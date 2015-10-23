#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
Split files at <split> command without throwing out any html text. 
The <split> should be on a new line.
Create all files complete with header and footer, seperated by <split> 
and put them in a folder "toconvert" on the Desktop.
Only use the <split>-tag (and not </split>)
Make sure that in the headers in the section (class="sutta") the id is mentioned, 
which will be the name of the output file.
"""

import re
import os

base_dir = os.environ['HOME']+'/Desktop/'
suttadir = base_dir+'toconvert/'
suttanr = 1

os.mkdir(base_dir+'temp/')
os.mkdir(base_dir+'converted/')

for name in os.listdir(suttadir):
    fileRead = open(suttadir+name,'r')
    fileWrite = open(base_dir+'temp/'+str(suttanr)+name, 'w')
    for line in fileRead:
        if line.startswith('<split>'):
            fileWrite.close()
            suttanr += 1
            fileWrite = open(base_dir+'temp/'+str(suttanr)+name, 'w')
        else:
            fileWrite.write(line)
    fileWrite.close()

suttadir = base_dir+'temp/'

for name in os.listdir(suttadir):
    fileReadNr = open(suttadir+name,'r')
    suttanr = ''
    for line in fileReadNr:
            if line.find('<section class="sutta') != -1:
                suttanr = re.findall(r'id="(.*?)">' , line, re.M)[0]
    fileWrite = open(base_dir+'converted/'+suttanr+'.html', 'w')
    fileReadwhole = open(suttadir+name).read()
    fileWrite.write(fileReadwhole)
    fileWrite.close()
    os.remove(base_dir+'temp/'+name)

os.rmdir(base_dir+'temp/')