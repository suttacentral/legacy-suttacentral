#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import asciicodes

'''
convert ascii codes to utf.
Make sure the source files are in UTF-8 first!
'''
base_dir = os.environ['HOME']+'/Desktop/'
suttadir = base_dir+'toconvert/'
os.mkdir(base_dir+'converted/')

def convert_codes(line):
    asciinumbers = re.findall(r'(&#.*?;)' , line, re.M)
    for x in range(len(asciinumbers)):      
        line = re.sub(asciinumbers[x], asciicodes.codes_dict.get(asciinumbers[x],asciinumbers[x]), line)
    return line

for name in os.listdir(suttadir):
    print (name)
    fileOpen = open(suttadir+name,'r')
    fileWrite = open(base_dir+'converted/'+name, 'w')
    for line in fileOpen:
       line = convert_codes(line)
       fileWrite.write(line)
    fileWrite.close()
