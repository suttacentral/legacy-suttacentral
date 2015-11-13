#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
functions used in conversion of html suttas to latex and epub
''' 
import re
import os
import csv

base_dir = os.environ['HOME']+'/suttalatex/jinjatex/' #where language and conversion files are stored

class Sutta:
    """
    Creates a class which can determine the author and section title of the sutta.
    """
    def __init__(self, path):
        self._path = path
        self._suttaOpen = open(self._path,'r')
        self._readSutta = self._suttaOpen.read()
        self._author = ''
        self._division = ''
        self._section_title = ''

    def get_author(self):
        self._author = re.findall(r'author="(.*?)">' , self._readSutta, re.M)[0]
        return self._author

    def get_division(self):
        self._division = re.findall(r'class="division">(.*?)<' , self._readSutta, re.M)[0]
        return self._division

    def get_section_title(self):
        self._section_title = re.findall(r'<h1.*?>(.*?)</h1>', self._readSutta)[0]
        #If the suttasection starts with a digit, this is thrown out.
        if self._section_title[0].isdigit():
            self._section_title = re.findall(r'\d{1,5}(.*?)', self._section_title)[0]
            self._section_title = self._section_title.strip()
        if self._section_title.startswith('.'):
            self._section_title = re.findall(r'\. (.*?)', self._section_title)[0]
        return self._section_title


def get_globals():
    '''
    user input of globals
    '''
    suttanrs = []
    startsutta = -1
    endsutta = -1
    globals_dict = {}
    sutta_path = os.environ['HOME']+'/suttacentral/data/text/'

    while True:
        suttadir_answer = input('Enter the directory: ')
        suttadir = sutta_path+suttadir_answer
        try:
            os.listdir(suttadir)
            break
        except:
            print('Not a valid directory, please try again')

    # browses through the directory and finds all sutta numbers in there, 
    # which will later be used as chapter headings and to order the texts.
    for name in os.listdir(suttadir):
        namelist = re.split(r'(\d{1,4})',name)
        if len(namelist) > 3:
           suttanrs.append((int(namelist[1]),int(namelist[3])))
        else:
           suttanrs.append(int(namelist[1]))
    suttanrs.sort()

    print ('There are ' + str(len(suttanrs)) + ' files in this directory.')

    while startsutta < 0 or startsutta > len(suttanrs):
        print('Please enter a number between 1 and ' + str(len(suttanrs)) + '.')
        startsuttatext = input('Enter the number of the first sutta to be printed: ')
        try:
            startsutta = int(startsuttatext)-1
        except:
            print ('This is not a valid number.')

    while endsutta <= startsutta or endsutta > len(suttanrs):
        print('Please enter a number between ' + str(startsutta + 1) +' and ' + str(len(suttanrs)) + '.')
        endsuttatext = input('Enter the number of the last sutta to be printed: ')
        try: 
            endsutta = int(endsuttatext)
        except:
            print ('This is not a valid number.')

    versionnumber = input("Enter the version number or name: ")
    try:
        os.listdir(namelist[0]+versionnumber+'/')
    except:
        os.mkdir(namelist[0]+versionnumber+'/')

    while True:
        language = input("Enter the directory name where your translation files are stored: ")
        try:
            language = 'templates/'+language
            os.listdir(language)
            break
        except:
            print('Not a valid directory, please try again.')

    pars = input("Do you want paragraph numbers? (Y/n) ")
    if pars == 'Y':
        paragraph_id = input("Enter the paragraph id (i.e. sc, wp): ")
    else: paragraph_id = 'x'

    globals_dict['language'] = language
    globals_dict['versionnumber'] = versionnumber
    globals_dict['suttadir'] = suttadir
    globals_dict['startsutta'] = startsutta
    globals_dict['endsutta'] = endsutta
    globals_dict['suttanrs'] = suttanrs
    globals_dict['namelist'] = namelist
    globals_dict['pars'] = pars
    globals_dict['paragraph_id'] = paragraph_id

    return globals_dict


def match_sutta_vagga(nikaya, language):
    '''
    Matches sutta numbers to the vagga dictionary to output a dictionary with suttas 
    before which a new vagga name is to be added as new chapter
    '''
    vagga_dict = dict()
    for rows in csv.reader(open(language+'/vagga.csv', mode='r')):
        if rows[0] == nikaya:
            vagga_dict[rows[1]] = rows[2]

    sutta_dict = dict()
    for rows in csv.reader(open(base_dir+'templates/sutta.csv', mode='r')):
        if rows[4] == '1' and rows[2] == nikaya:
            sutta_dict[rows[1]] = rows[3]

    sutta_vagga_dict = dict()
    for keys,values in sutta_dict.items():
        sutta_vagga_dict[keys] = vagga_dict[values]

    return sutta_vagga_dict