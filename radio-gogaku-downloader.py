#!/usr/bin/env python3
# encoding: utf-8
#
# NHK radio gogaku downloader
#
from os import makedirs, path
import sys
import json
import argparse
import requests
import npyscreen
import ffmpeg
import xml.etree.ElementTree as ET

class SelectApp(npyscreen.StandardApp):
    def onStart(self):
        self.addForm('MAIN', SelectForm, name='Course Selection')

class SelectForm(npyscreen.ActionForm):
    def create(self):
        self.multiselect = self.add(npyscreen.TitleMultiSelect, \
                relx=3, rely=2, value=crsselnum, name="講座選択", \
                values=crsalltitle, scroll_exit=True)

    def on_ok(self):
        self.parentApp.setNextForm(None)
        selects = self.multiselect.value
        lall = []
        with open('courses-all.json', mode='r') as fs:
            for sline in fs:
                lall.append(sline)
        with open('courses-selected.json', mode='w') as fd:
            for i in range(5):
                fd.write(lall[i])
            for i in range(len(selects)):
                l = lall[selects[i] + 5]
                if i == len(selects) - 1:
                    l = l[:l.rfind(',')] + '\n'
                fd.write(l)
            for i in range(2):
                fd.write(lall[len(lall) - 2 + i])

    def on_cancel(self):
        self.parentApp.setNextForm(None)

if __name__ == '__main__':
    ################################
    urlmusicbase = 'https://nhk-vh.akamaihd.net/i/gogaku-stream/mp4/{}/master.m3u8'
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
    if path.exists('courses-selected.json'):
        filesel = open('courses-selected.json', 'r')
        jsonsel = json.load(filesel)
        crssel = jsonsel['course']
        crsselnum = []
        for i in range(len(crssel)):
            crsselnum.append(int(crssel[i]['num']))
    else:
        crsselnum = []

    # If selected json not exist or course select option then open selection menu
    if  args.select or len(crsselnum) == 0:
        try:
            fileall = open('courses-all.json', 'r', encoding='utf-8')
        except:
            print('[ERROR] courses-all.json not found.')
            exit(1)
        jsonall = json.load(fileall)
        crsall = jsonall['course']
        crsalltitle = []
        for i in range(len(crsall)):
            crsalltitle.append(crsall[i]['title'])
        # Open TUI menu to create JSON file
        SelApp = SelectApp()
        SelApp.run()
        exit(0)

    # Else Download and convert streaming files
    else:
        year = jsonsel['year']
        # url = url1 + lang + '/' + dir + url2
        url1 = jsonsel['url1']
        url2 = jsonsel['url2']
        crssel = jsonsel['course']
        crssellen = len(crssel)
        crsseltitle = []
        crssellang = []
        crsseldir = []
        for i in range(crssellen):
            crsseltitle.append(crssel[i]['title'])
            crssellang.append(crssel[i]['lang'])
            crsseldir.append(crssel[i]['dir'])
            urlxml = requests.get('{}{}/{}{}'.format(url1, crssellang[i], \
                    crsseldir[i], url2))

            # print(r.text)
            root = ET.fromstring(urlxml.text)
            savedirbase = path.abspath(args.dir)
            for music in root.findall('music'):
                course_title = music.get('title')
                hdate = music.get('hdate')
                hdate = hdate[0:hdate.find('月')].zfill(2) + '月' + \
                    hdate[hdate.find('月')+1:hdate.find('日')].zfill(2) + \
                    '日放送分'
                musicfile = music.get('file')
                nendo = music.get('nendo')
                urlmusic = urlmusicbase.format(musicfile)

                # Default output format
                #       ({DIR}/{year}/{course title}/{date}.mp3)
                if args.output == '1':
                    savedir = savedirbase + '/' + nendo + '/' + course_title
                    savepath = savedir + '/' + hdate + '.mp3'
                # Output format option-1
                #       ({DIR}/{year}/{course title}/{course title}_{date}.mp3)
                elif args.output == '2':
                    savedir = savedirbase + '/' + nendo + '/' + course_title
                    savepath = savedir + '/' + course_title + '_' + hdate + '.mp3'
                # Output format option-2
                #       ({DIR}/{year}/{course title}_{date}.mp3)
                elif args.output == '3':
                    savedir = savedirbase + '/' + nendo
                    savepath = savedir + '/' + course_title + '_' + hdate + '.mp3'
                else:
                    print('[OPTION ERROR] Please specify 1~3 for option "-o". \
                            (Default is same as "-o 1")')
                    exit(1)

                # Try to create a directory to store music files
                try:
                    makedirs(savedir)
                except:
                    pass

                if  args.force or path.exists(savepath) == False:
                    output_options = {'ab':'64k', 'id3v2_version':'3', \
                        'metadata:g:0':'artist=NHK', \
                        'metadata:g:1':'album='+course_title, \
                        'metadata:g:2':'date='+nendo}
                    (
                        ffmpeg
                        .input(urlmusic)
                        .output(savepath, **output_options)
                        .overwrite_output()
                        .run()
                    )
