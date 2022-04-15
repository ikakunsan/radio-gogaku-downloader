#!/usr/bin/env python3
#
# NHK radio gogaku downloader
#
# 2021,2022 ikakunsan
# https://github.com/ikakunsan/radio-gogaku-downloader
#
#
import sys
import os
import time
import datetime as dt
import json
from pathlib import Path
import argparse
import requests
import npyscreen
import ffmpeg
from distutils.util import strtobool
from sys import exit

# from logging import getLogger, StreamHandler, DEBUG
import logging as lgg

FILE_SIZE_PER_SEC = {
    "64k": 64000,
    "128k": 128000,
    "256k": 256000,
}
RETRY_MAX = 5  # retry count in HTTP 404 error

logging_filename = "radio-gogaku-downloader.log"
logging_path = os.path.dirname(os.path.abspath(__file__))  # Current directory
logger = lgg.getLogger(__name__)
handler = lgg.FileHandler(f"{logging_path}/{logging_filename}", encoding="utf-8")
# handler = lgg.StreamHandler()
log_format = lgg.Formatter("%(asctime)s : %(levelname)s : %(message)s")
handler.setFormatter(log_format)
log_level = lgg.ERROR
handler.setLevel(log_level)
logger.setLevel(log_level)
logger.addHandler(handler)
logger.propagate = False


class SelectApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", SelectForm, name="Course Selection")


class SelectForm(npyscreen.ActionForm):
    def create(self):
        prog_sel_num = []
        for ix_sel in range(len(prog_sel_title)):
            for ix_all in range(len(prog_all_title)):
                if prog_sel_title[ix_sel] == prog_all_title[ix_all]:
                    prog_sel_num.append(ix_all)
                    break
        self.multiselect = self.add(
            npyscreen.TitleMultiSelect,
            relx=3,
            rely=2,
            value=prog_sel_num,
            name="講 座 選 択 ",
            values=prog_all_title,
            scroll_exit=True,
        )

    def on_ok(self):
        self.parentApp.setNextForm(None)
        selects = self.multiselect.value
        lall = []
        with open(path_prog_all, mode="r", encoding="utf-8") as fs:
            for sline in fs:
                lall.append(sline)
        with open(path_prog_sel, mode="w", encoding="utf-8") as fd:
            for i in range(6):  # Just copy line 1 through line 6 in the source file
                fd.write(lall[i])
            for i in range(len(selects)):  # Copy lines of selected courses
                json_prog_one = json_prog_all["programs"][selects[i]]
                s = "        " + json.dumps(json_prog_one, ensure_ascii=False)
                s += ",\n"
                fd.write(s)
            for i in range(3):
                fd.write(
                    lall[len(lall) - 3 + i]
                )  # Copy last 3 lines in the source file

    def on_cancel(self):
        self.parentApp.setNextForm(None)


class NetworkProtocolError(Exception):
    pass


def get_nendo(ymd):
    nendo = int(ymd[:4])
    if int(ymd[4:6]) < 4:
        nendo -= 1
    return f"{nendo:04}"  # No need to format actually....


def log_print(loglevel, message):
    msg_str = " ".join(message)
    if loglevel == "DEBUG":
        logger.debug(msg_str)
    elif loglevel == "INFO":
        logger.info(msg_str)
    elif loglevel == "WARNING":
        logger.warning(msg_str)
    elif loglevel == "ERROR":
        logger.error(msg_str)
        print("\n", msg_str, "\n")
    elif loglevel == "CRITICAL":
        logger.critical(msg_str)
        print("\n", msg_str, "\n")
    elif loglevel == "EXCEPTION":
        logger.exception(msg_str)
        print("\n", msg_str, "\n")
    else:
        logger.error("[PARAM ERROR]", msg_str)


if __name__ == "__main__":
    ################################
    path_prog_all = "courses-all.json"
    path_prog_sel = "courses-selected.json"
    ################################

    parser = argparse.ArgumentParser(
        description="NHK radio gogaku streaming downloader"
    )
    parser.add_argument(
        "-s", "--select", action="store_true", help="Display a menu to select courses."
    )
    parser.add_argument("-d", "--dir", help="Specify directory to store audio files.")
    parser.add_argument(
        "-o",
        "--output",
        default=1,
        type=int,
        help="Output style. OUTPUT should be 1~4 (Default is 1). "
        + "Please refer to README for detail.",
    )
    parser.add_argument(
        "-q",
        "--quality",
        default=1,
        type=int,
        help="Sound quality. 0:basic (64kbps), " + "1:high (128kbps), 2:best (256kbps)",
    )
    parser.add_argument(
        "-p",
        "--sample",
        default=0,
        type=int,
        help="Sample rate. 0:48kHz (default), 1:44.1kHz",
    )
    parser.add_argument(
        "-y",
        "--year",
        default="1",
        type=strtobool,
        help="Switch to add Year in output file name. "
        + "0:without year, 1:with year (Default is 1)",
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="Force overwrite existing files."
    )
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    args = parser.parse_args()

    # Try to read courses-selected.json file
    # Try to extract JSON file
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        dir_current = Path(sys.argv[0]).resolve().parent
    else:
        dir_current = Path(__file__).resolve().parent
    path_prog_all = dir_current / path_prog_all
    path_prog_sel = dir_current / path_prog_sel

    # Set log level to debug
    if args.debug:
        log_level = lgg.DEBUG
        handler.setLevel(log_level)
        logger.setLevel(log_level)
        logger.addHandler(handler)

    log_message = ("---------",)
    log_print("INFO", log_message)
    log_message = ("Program Started",)
    log_print("INFO", log_message)

    ## Check option parameters
    # Output Style
    if args.output < 1 or args.output > 4:
        log_message = (
            "[OPTION ERROR]",
            'Please specify 1~4 for option "-o".',
            '(Without this option is same as "-o 1")',
        )
        log_print("ERROR", log_message)
        exit(1)

    # Audio Quality
    mp3_bitrate = "128k"  # Default
    if args.quality == 0:
        mp3_bitrate = "64k"
    elif args.quality == 1:  # Default value
        mp3_bitrate = "128k"
    elif args.quality == 2:
        mp3_bitrate = "256k"
    else:
        log_message = (
            "[OPTION ERROR]",
            'Please specify 0~2 for option "-q".'
            '(Without this option is same as "-q 1")',
        )
        log_print("ERROR", log_message)
        exit(1)

    # Audio Sample Rate
    mp3_samplerate = "48k"
    if args.sample == 0:
        mp3_samplerate = "48k"
    elif args.sample == 1:
        mp3_samplerate = "44.1k"
    else:
        log_message = (
            "[OPTION ERROR]",
            'Please specify 0~1 for option "-p".'
            '(Without this option is same as "-p 0")',
        )
        log_print("ERROR", log_message)
        exit(1)

    # If courses-selected.json exists, put selected program list (dir numbers)
    # to prog_sel_num[]
    if path_prog_sel.exists():
        file_prog_sel = open(path_prog_sel, "r", encoding="utf-8")
        try:
            json_prog_sel = json.load(file_prog_sel)
        except:
            log_message = (
                "[ERROR]",
                '"courses-selected.json" is broken.',
                "Try to delete it and select courses again.",
            )
            log_print("ERROR", log_message)
            exit(1)

        prog_sel = json_prog_sel["programs"]
        if len(prog_sel) > 0:
            for i in range(len(prog_sel)):
                if prog_sel[i]["dir"] == "EEEE":
                    prog_sel.pop(i)
    else:
        prog_sel = []

    # If selected json not exist or course select option then
    # open selection menu
    if args.select or len(prog_sel) == 0:
        try:
            file_prog_all = open(path_prog_all, "r", encoding="utf-8")
        except:
            log_message = (
                "[ERROR]",
                "Cannot open {}.".format(path_prog_all),
            )
            log_print("ERROR", log_message)
            exit(1)
        json_prog_all = json.load(file_prog_all)
        prog_all = json_prog_all["programs"]
        prog_all_title = []
        prog_sel_title = []
        for i in range(len(prog_all)):
            if prog_all[i]["dir"] != "EEEE":
                prog_all_title.append(prog_all[i]["title"])
        if len(prog_sel) != 0:
            for i in range(len(prog_sel)):
                if prog_sel[i]["dir"] != "EEEE":
                    prog_sel_title.append(prog_sel[i]["title"])
        # Open TUI menu to create JSON file
        SelApp = SelectApp()
        SelApp.run()
        exit(0)

    # Else Download and convert streaming files
    else:
        year = json_prog_sel["year"]
        # url = url1 + '/' + dir + '/' + url2 + dir + '_' + sub + url3
        url1 = json_prog_sel["url1"]
        url2 = json_prog_sel["url2"]
        url3 = json_prog_sel["url3"]
        prog_sel = json_prog_sel["programs"]
        prog_sel_len = len(prog_sel)
        prog_sel_title = []
        prog_sel_dir = []
        prog_sel_sub = []
        for i in range(prog_sel_len):
            prog_sel_title.append(prog_sel[i]["title"])
            prog_sel_dir.append(prog_sel[i]["dir"])
            prog_sel_sub.append(prog_sel[i]["sub"])
            url_prog_this_week = (
                url1
                + "/"
                + prog_sel_dir[i]
                + "/"
                + url2
                + prog_sel_dir[i]
                + "_"
                + prog_sel_sub[i]
                + url3
            )

            # Get json file of the program for this week
            try:
                file_prog_this_week = requests.get(url_prog_this_week)
            except:
                log_message = (
                    "[ERROR]",
                    "Cannot connect to site: {}".format(url_prog_this_week),
                )
                log_print("ERROR", log_message)
                exit(1)
            if file_prog_this_week.status_code != 200:
                log_message = (
                    "[ERROR]",
                    "Cannot open program JSON fiie: {}".format(prog_sel_title[i]),
                )
                log_print("ERROR", log_message)
                exit(1)

            # Set file output directory
            try:
                dir_output_base = Path(args.dir).resolve()
            except:
                log_message = (
                    "[OPTION ERROR]",
                    'Please specify target directory with option "-d"',
                )
                log_print("ERROR", log_message)
                exit(1)

            json_prog_this_week = json.loads(file_prog_this_week.text)

            for i in range(
                len(json_prog_this_week["main"]["detail_list"])
            ):  # Process for each date
                try:
                    prog_title = json_prog_this_week["main"]["program_name"]
                    onair_datetime = json_prog_this_week["main"]["detail_list"][i][
                        "file_list"
                    ][0]["aa_vinfo4"]
                    onair_date_mmdd = (
                        onair_datetime[5:7] + "月" + onair_datetime[8:10] + "日放送分"
                    )
                    onair_date = onair_datetime[0:4] + "年" + onair_date_mmdd
                    onair_start = dt.datetime.strptime(
                        onair_datetime[0:19], "%Y-%m-%dT%H:%M:%S"
                    )
                    onair_end = dt.datetime.strptime(
                        onair_datetime[26:45], "%Y-%m-%dT%H:%M:%S"
                    )
                    onair_time = onair_end - onair_start
                    expected_file_size = (
                        FILE_SIZE_PER_SEC[mp3_bitrate] * int(onair_time.seconds) / 8
                    )
                except:
                    log_message = (
                        "[ERROR]",
                        "This program does not exist",
                        prog_title,
                    )
                    log_print("ERROR", log_message)
                    break

                if args.year == 0:
                    onair_date = onair_date_mmdd

                url_music_source = json_prog_this_week["main"]["detail_list"][i][
                    "file_list"
                ][0]["file_name"]
                nendo = get_nendo(
                    json_prog_this_week["main"]["dev"][:4]
                    + json_prog_this_week["main"]["dev"][5:7]
                    + json_prog_this_week["main"]["dev"][8:10]
                )
                log_message = (
                    "Processing:",
                    nendo,
                    prog_title,
                    onair_date,
                )
                log_print("INFO", log_message)

                # Default output format
                #       ({DIR}/{year}/{course title}/{date}.mp3)
                if args.output == 1:
                    dir_output = dir_output_base / nendo / prog_title
                    path_output = dir_output / f"{onair_date}.mp3"
                # Output format option-1
                #       ({DIR}/{year}/{course title}/{course title}_{date}.mp3)
                elif args.output == 2:
                    dir_output = dir_output_base / nendo / prog_title
                    path_output = dir_output / f"{prog_title}_{onair_date}.mp3"
                # Output format option-2
                #       ({DIR}/{year}/{course title}_{date}.mp3)
                elif args.output == 3:
                    dir_output = dir_output_base / nendo
                    path_output = dir_output / f"{prog_title}_{onair_date}.mp3"
                # Output format option-3
                #       ({DIR}/{course title}/{year}/{date}.mp3)
                elif args.output == 4:
                    dir_output = dir_output_base / prog_title / nendo
                    path_output = dir_output / f"{onair_date}.mp3"
                else:
                    log_message = (
                        "[OPTION ERROR]",
                        'Please specify 1~4 for option "-o".',
                        '(Default is same as "-o1")',
                    )
                    log_print("ERROR", log_message)
                    exit(1)

                # Try to create a directory to store music files
                try:
                    dir_output.mkdir(parents=True, exist_ok=True)
                except:
                    log_message = (
                        "[ERROR]",
                        "Cannot create target directory: {}".format(dir_output),
                    )
                    log_print("ERROR", log_message)
                    exit(1)

                if args.force or not path_output.exists():
                    output_options = {
                        "id3v2_version": "3",
                        "ab": mp3_bitrate,
                        "ar": mp3_samplerate,
                        "metadata:g:0": "artist=NHK",
                        "metadata:g:1": "album=" + prog_title,
                        "metadata:g:2": "date=" + nendo,
                    }
                    http_error = False
                    retry = 1
                    while True:
                        try:
                            (
                                ffmpeg.input(url_music_source)
                                .output(str(path_output.resolve()), **output_options)
                                .overwrite_output()
                                .run()
                            )
                            actual_file_size = os.path.getsize(path_output)
                            log_print(
                                "DEBUG",
                                ("Expected File Size:", str(int(expected_file_size))),
                            )
                            log_print(
                                "DEBUG",
                                ("Actual File Size:  ", str(int(actual_file_size))),
                            )

                            if actual_file_size < expected_file_size:
                                log_print(
                                    "ERROR",
                                    ("Expected Size:", str(int(expected_file_size))),
                                )
                                log_print(
                                    "ERROR",
                                    ("Actual Size:  ", str(int(actual_file_size))),
                                )
                                raise NetworkProtocolError

                        except FileNotFoundError:
                            log_message = (
                                "[ERROR]",
                                "ffmpeg is not installed.",
                            )
                            log_print("ERROR", log_message)

                        except ffmpeg._run.Error:
                            http_error = True
                            log_message = (
                                "[ERROR]",
                                "ffmpeg error. Maybe source file does not exist.",
                                prog_title,
                                onair_date,
                                "will retry",
                                str(retry),
                            )
                            log_print("ERROR", log_message)

                        except NetworkProtocolError:
                            http_error = True
                            log_message = (
                                "[ERROR]",
                                "Network protocol error, possibly HTTP 404 error on some segments.",
                                prog_title,
                                onair_date,
                                "will retry",
                                str(retry),
                            )
                            log_print("ERROR", log_message)
                            time.sleep(15)  # Wait for 15 seconds for retry

                        except:
                            log_message = (
                                "[ERROR]",
                                "Other error. See log file for detail.",
                            )
                            log_print("EXCEPTION", log_message)

                        retry += 1
                        if retry > RETRY_MAX or not http_error:
                            http_error = False
                            if retry > RETRY_MAX:
                                s = str(path_output)
                                s = "{0}(incomplete){1}".format(
                                    s[:-4], s[-4:]
                                )
                                path_output_incomp = Path(s).resolve()
                                os.rename(path_output, path_output_incomp)
                            break

        log_message = ("Program finished",)
        log_print("INFO", log_message)
