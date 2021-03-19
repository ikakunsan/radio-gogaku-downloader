#!/usr/bin/env python3
# encoding: utf-8
#
# NHK radio gogaku downloader
#
# Memo:
#   (2021/03/12) Program source format was changed to JSON from XML (XML will be no longer used from Apr 2021)
#
# 2019/05/02    v1.0    Initial
# 2021/03/18    v2.0    Change program info source from XML to JSON (prep for April)
#
from os import makedirs, path
import sys
import json
import argparse
import requests
import npyscreen
import ffmpeg
#import xml.etree.ElementTree as ET

class SelectApp(npyscreen.StandardApp):
    def onStart(self):
        self.addForm('MAIN', SelectForm, name='Course Selection')

class SelectForm(npyscreen.ActionForm):
    def create(self):
        self.multiselect = self.add(npyscreen.TitleMultiSelect, \
                relx=3, rely=2, value=prog_sel_num, name="講座選択", \
                values=prog_all_title, scroll_exit=True)

    def on_ok(self):
        self.parentApp.setNextForm(None)
        selects = self.multiselect.value
        lall = []
        with open(path_prog_all, mode='r') as fs:
            for sline in fs:
                lall.append(sline)
        with open(path_prog_sel, mode='w') as fd:
            for i in range(6):      # Just copy line 1 through line 6 in the source file
                fd.write(lall[i])
            for i in range(len(selects)):   # Copy lines of selected courses
                l = lall[selects[i] + 6]
                if i == len(selects) - 1:
                    l = l[:l.rfind(',')] + '\n'
                fd.write(l)
            for i in range(2):
                fd.write(lall[len(lall) - 2 + i])   # Copy last 2 lines in the source file

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
    parser.add_argument('-d', '--dir', help='Specify directory to store audio files.')
    parser.add_argument('-o', '--output', default = '1', \
                help='Output style. OUTPUT should be 1~3 (Default is 1). Please refer to readme for detail.')
    parser.add_argument('-f', '--force',  action='store_true', \
                help='Force overwrite existing files.')
    args = parser.parse_args()

    # Try to read courses-selected.json file
    # Try to extract JSON file
    currentdir = path.dirname(path.abspath(__file__))
    path_prog_all = currentdir + '/' + path_prog_all
    path_prog_sel = currentdir + '/' + path_prog_sel
    if path.exists(path_prog_sel):
        file_prog_sel = open(path_prog_sel, 'r')
        json_prog_sel = json.load(file_prog_sel)
        prog_sel = json_prog_sel['programs']
        prog_sel_num = []
        for i in range(len(prog_sel)):
            prog_sel_num.append(int(prog_sel[i]['num']))
    else:
        prog_sel_num = []

    # If selected json not exist or course select option then open selection menu
    if  args.select or len(prog_sel_num) == 0:
        print(path_prog_all)
        try:
            fileall = open(path_prog_all, 'r', encoding='utf-8')
        except:
            print('[ERROR] Cannot open {}.'.format(path_prog_all))
            exit(1)
        json_prog_all = json.load(fileall)
        prog_all = json_prog_all['programs']
        prog_all_title = []
        for i in range(len(prog_all)):
            prog_all_title.append(prog_all[i]['title'])
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
                print('[ERROR] Cannot connect to site: {}'.format(url_prog_this_week))
                exit(1)
            if file_prog_this_week.status_code != 200:
                print('[ERROR] Cannot open program JSON fiie: {}'.format(prog_sel_title[i]))
                exit(1)

            # Set file output directory
            try:
                save_dir_base = path.abspath(args.dir)
            except:
                print('\n[OPTION ERROR] Please specify target directory with option "-d"\n')
                exit(1)

            json_prog_this_week = json.loads(file_prog_this_week.text)
            for i in range(len(json_prog_this_week['main']['detail_list'])):  # Process for each date
                prog_title = json_prog_this_week['main']['program_name']
                onair_date = json_prog_this_week['main']['detail_list'][i]['file_list'][0]['aa_vinfo3']
                onair_date = onair_date[0:4] + '年' + onair_date[4:6] + '月' + onair_date[6:8] + '日放送分'

                url_music_source = json_prog_this_week['main']['detail_list'][i]['file_list'][0]['file_name']
                nendo = get_nendo(json_prog_this_week['main']['detail_list'][i]['file_list'][0]['aa_vinfo3'][:8])

                # Default output format
                #       ({DIR}/{year}/{course title}/{date}.mp3)
                if args.output == '1':
                    save_dir = save_dir_base + '/' + nendo + '/' + prog_title
                    save_path = save_dir + '/' + onair_date + '.mp3'
                # Output format option-1
                #       ({DIR}/{year}/{course title}/{course title}_{date}.mp3)
                elif args.output == '2':
                    save_dir = save_dir_base + '/' + nendo + '/' + prog_title
                    save_path = save_dir + '/' + prog_title + '_' + onair_date + '.mp3'
                # Output format option-2
                #       ({DIR}/{year}/{course title}_{date}.mp3)
                elif args.output == '3':
                    save_dir = save_dir_base + '/' + nendo
                    save_path = save_dir + '/' + prog_title + '_' + onair_date + '.mp3'
                else:
                    print('\n[OPTION ERROR] Please specify 1~3 for option "-o". \
                            (Default is same as "-o 1")\n')
                    exit(1)

                # Try to create a directory to store music files
                try:
                    makedirs(save_dir)
                except:
                    pass

                if  args.force or path.exists(save_path) == False:
                    output_options = {'ab':'64k', 'id3v2_version':'3', \
                        'metadata:g:0':'artist=NHK', \
                        'metadata:g:1':'album='+prog_title, \
                        'metadata:g:2':'date='+nendo}
                    (
                        ffmpeg
                        .input(url_music_source)
                        .output(save_path, **output_options)
                        .overwrite_output()
                        .run()
                    )
