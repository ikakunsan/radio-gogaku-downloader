#!/usr/bin/env python3
# encoding: utf-8
#
# NHK radio gogaku downloader
#
# 2021 ikakunsan
# https://github.com/ikakunsan/radio-gogaku-downloader
#
#
from pathlib import Path
import sys
import json
import argparse
import requests
import npyscreen
import ffmpeg
from distutils.util import strtobool
from sys import exit

class SelectApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', SelectForm, name='Course Selection')

class SelectForm(npyscreen.ActionForm):
    def create(self):
        prog_sel_num = []
        for ix_sel in range(len(prog_sel_title)):
            for ix_all in range(len(prog_all_title)):
                if prog_sel_title[ix_sel] == prog_all_title[ix_all]:
                    prog_sel_num.append(ix_all)
                    break
        self.multiselect = self.add(npyscreen.TitleMultiSelect, \
                relx=3, rely=2, value=prog_sel_num, name="講 座 選 択 ", \
                values=prog_all_title, scroll_exit=True)

    def on_ok(self):
        self.parentApp.setNextForm(None)
        selects = self.multiselect.value
        lall = []
        with open(path_prog_all, mode='r', encoding='utf-8') as fs:
            for sline in fs:
                lall.append(sline)
        with open(path_prog_sel, mode='w', encoding='utf-8') as fd:
            for i in range(6):      # Just copy line 1 through line 6 in the source file
                fd.write(lall[i])
            for i in range(len(selects)):   # Copy lines of selected courses
                json_prog_one = json_prog_all['programs'][selects[i]]
                s = '        ' + json.dumps(json_prog_one, ensure_ascii=False)
                s += ',\n'
                fd.write(s)
            for i in range(3):
                fd.write(lall[len(lall) - 3 + i])   # Copy last 3 lines in the source file

    def on_cancel(self):
        self.parentApp.setNextForm(None)

def get_nendo(ymd):
    nendo = int(ymd[:4])
    if int(ymd[4:6]) < 4:
        nendo -= 1
    return f'{nendo:04}'    # No need to format actually....

if __name__ == '__main__':
    ################################
    path_prog_all = 'courses-all.json'
    path_prog_sel = 'courses-selected.json'
    ################################

    parser = argparse.ArgumentParser(description='NHK radio gogaku streaming downloader')
    parser.add_argument('-s', '--select',  action='store_true', \
                help='Display a menu to select courses.')
    parser.add_argument('-d', '--dir', \
                help='Specify directory to store audio files.')
    parser.add_argument('-o', '--output', default = 1, type = int, \
                help='Output style. OUTPUT should be 1~4 (Default is 1). Please refer to README for detail.')
    parser.add_argument('-q', '--quality', default = 0, type = int, \
                help='Sound quality. 0:standard (64kbps), 1:high (128kbps), 2:best (256kbps)')
    parser.add_argument('-y', '--year', default = '1', type = strtobool, \
                help='Switch to add Year in output file name. 0:without year, 1:with year (Default is 1)')
    parser.add_argument('-f', '--force',  action='store_true', \
                help='Force overwrite existing files.')
    args = parser.parse_args()

    # Try to read courses-selected.json file
    # Try to extract JSON file
    dir_current = Path(__file__).resolve().parent
    path_prog_all = dir_current / path_prog_all
    path_prog_sel = dir_current / path_prog_sel

    # Check option parameters
    if args.output < 1 or args.output > 4:
        print('\n[OPTION ERROR] Please specify 1~4 for option "-o". \
            (Without this option is same as "-o 1")\n')
        exit(1)

    mp3_bitrate = '64k'         # Default
    if args.quality == 0:       # 0: Default value
        mp3_bitrate = '64k'
    elif args.quality == 1:
        mp3_bitrate = '128k'
    elif args.quality == 2:
        mp3_bitrate = '256k'
    else:
        print('\n[OPTION ERROR] Please specify 0~2 for option "-q". \
            (Without this option is same as "-q 0")\n')
        exit(1)

    # If courses-selected.json exists, put selected program list (dir numbers) to prog_sel_num[]
    if path_prog_sel.exists():
        file_prog_sel = open(path_prog_sel, 'r', encoding='utf-8')
        try:
            json_prog_sel = json.load(file_prog_sel)
        except:
            print('\n[ERROR] "courses-selected.json" is broken. Try to delete it and select courses again.')
            exit(1)
        prog_sel = json_prog_sel['programs']
        if len(prog_sel) > 0:
            for i in range(len(prog_sel)):
                if prog_sel[i]['dir'] == 'EEEE':
                    prog_sel.pop(i)
    else:
        prog_sel = []

    # If selected json not exist or course select option then open selection menu
    if  args.select or len(prog_sel) == 0:
        try:
            file_prog_all = open(path_prog_all, 'r', encoding='utf-8')
        except:
            print('\n[ERROR] Cannot open {}.'.format(path_prog_all))
            exit(1)
        json_prog_all = json.load(file_prog_all)
        prog_all = json_prog_all['programs']
        prog_all_title = []
        prog_sel_title = []
        for i in range(len(prog_all)):
            if prog_all[i]['dir'] != 'EEEE':
                prog_all_title.append(prog_all[i]['title'])
        if len(prog_sel) != 0:
            for i in range(len(prog_sel)):
                if prog_sel[i]['dir'] != 'EEEE':
                    prog_sel_title.append(prog_sel[i]['title'])
        # Open TUI menu to create JSON file
        SelApp = SelectApp()
        SelApp.run()
        exit(0)

    # Else Download and convert streaming files
    else:
        year = json_prog_sel['year']
        # url = url1 + '/' + dir + '/' + url2 + dir + '_' + sub + url3
        url1 = json_prog_sel['url1']
        url2 = json_prog_sel['url2']
        url3 = json_prog_sel['url3']
        prog_sel = json_prog_sel['programs']
        prog_sel_len = len(prog_sel)
        prog_sel_title = []
        prog_sel_dir = []
        prog_sel_sub = []
        for i in range(prog_sel_len):
            prog_sel_title.append(prog_sel[i]['title'])
            prog_sel_dir.append(prog_sel[i]['dir'])
            prog_sel_sub.append(prog_sel[i]['sub'])
            url_prog_this_week = url1 + "/" + prog_sel_dir[i] + "/" + url2 + prog_sel_dir[i] + \
                        "_" + prog_sel_sub[i] + url3

            # Get json file of the program for this week
            try:
                file_prog_this_week = requests.get(url_prog_this_week)
            except:
                print('\n[ERROR] Cannot connect to site: {}'.format(url_prog_this_week))
                exit(1)
            if file_prog_this_week.status_code != 200:
                print('\n[ERROR] Cannot open program JSON fiie: {}'.format(prog_sel_title[i]))
                exit(1)

            # Set file output directory
            try:
                dir_output_base = Path(args.dir).resolve()
            except:
                print('\n[OPTION ERROR] Please specify target directory with option "-d"\n')
                exit(1)

            json_prog_this_week = json.loads(file_prog_this_week.text)
            for i in range(len(json_prog_this_week['main']['detail_list'])):  # Process for each date
                prog_title = json_prog_this_week['main']['program_name']
                onair_date = json_prog_this_week['main']['detail_list'][i]['file_list'][0]['aa_vinfo3']
                onair_date_mmdd = onair_date[4:6] + '月' + onair_date[6:8] + '日放送分'
                onair_date = onair_date[0:4] + '年' + onair_date_mmdd
                if args.year == 0:
                    onair_date = onair_date_mmdd

                url_music_source = json_prog_this_week['main']['detail_list'][i]['file_list'][0]['file_name']
                nendo = get_nendo(json_prog_this_week['main']['dev'][:4]+json_prog_this_week['main']['dev'][5:7]+json_prog_this_week['main']['dev'][8:10])

                # Default output format
                #       ({DIR}/{year}/{course title}/{date}.mp3)
                if args.output == 1:
                    dir_output = dir_output_base / nendo / prog_title
                    path_output = dir_output / (onair_date + '.mp3')
                # Output format option-1
                #       ({DIR}/{year}/{course title}/{course title}_{date}.mp3)
                elif args.output == 2:
                    dir_output = dir_output_base / nendo / prog_title
                    path_output = dir_output / (prog_title + '_' + onair_date + '.mp3')
                # Output format option-2
                #       ({DIR}/{year}/{course title}_{date}.mp3)
                elif args.output == 3:
                    dir_output = dir_output_base / nendo
                    path_output = dir_output / (prog_title + '_' + onair_date + '.mp3')
                # Output format option-3
                #       ({DIR}/{course title}/{year}/{date}.mp3)
                elif args.output == 4:
                    dir_output = dir_output_base / prog_title / nendo
                    path_output = dir_output / (onair_date + '.mp3')
                else:
                    print('\n[OPTION ERROR] Please specify 1~4 for option "-o". \
                            (Default is same as "-o1")\n')
                    exit(1)

                # Try to create a directory to store music files
                try:
                    dir_output.mkdir(parents=True, exist_ok=True)
                except:
                    print('\n[ERROR] Cannot create target directory: {}\n'.format(dir_output))
                    exit(1)

                if args.force or path_output.exists() == False:
                    try:
                        output_options = {'id3v2_version':'3', \
                            'ab':mp3_bitrate,
                            'metadata:g:0':'artist=NHK', \
                            'metadata:g:1':'album='+prog_title, \
                            'metadata:g:2':'date='+nendo}
                        (
                            ffmpeg
                            .input(url_music_source)
                            .output(str(path_output.resolve()), **output_options)
                            .overwrite_output()
                            .run()
                        )
                    except FileNotFoundError:
                        print('\n[ERROR] ffmpeg is not installed.\n')
                    except ffmpeg._run.Error:
                        print('\n[ERROR] ffmpeg error. Maybe source file does not exist.\n')
                    except:
                        print('\n[ERROR] Unknown error.\n')
