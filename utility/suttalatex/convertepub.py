#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
See readme file for instructions on how to use this module
This converts a number of suttas in a directory to epub.
''' 
import re
import os
import jinja2
import csv
import shutil
from base_input import get_globals, match_sutta_vagga, Sutta
from makeEbook import makeEpub

def ReadWritePage(inputname,titletext):
    """
    Helper function to read a text file and write the output xhtml file
    """
    linenr = 1
    inputOpen = open(language+'/'+inputname+'.txt','r')
    outputWrite = open(writepath+inputname+'.xhtml','w')
    outputWrite.write('<div>\n<link rel="stylesheet" href="main.css">\n<article>\n<h1'+titletext+'</h1>\n')
    for line in inputOpen:
        line = re.sub(r' https://(.*?) ',r' <a href="https://\1">\1</a> ',line)
        line = re.sub(r' https://(.*?)\.\n',r' <a href="https://\1">\1</a>.\n',line)
        if len(line) > 2:
            if linenr == 1:
                outputWrite.write('<p class="firstline">'+line+'</p>\n')
                linenr += 1
            else:
                outputWrite.write('<p>'+line+'</p>\n')
    outputWrite.write('\n</article>\n</div>\n')
    outputWrite.close()


def writeExtraPages():
    """
    Writes the Preface, Biography, Metadata and About sections as well as 
    makes a copy of the css and jpg file in the current directory
    """

    #Preface
    ReadWritePage('preface','>'+transl_dict['preface_transl'])

    #Biography
    ReadWritePage('bio',' class="endtext">'+transl_dict['bio_transl']+": "+transl_dict['author'])

    #About SuttaCentral
    ReadWritePage('about',' class="endtext">'+transl_dict['about_transl']+' SuttaCentral')

    #Metadata
    outputWrite = open(writepath+'metaarea.xhtml','w')
    outputWrite.write('<div>\n<link rel="stylesheet" href="main.css">\n<p>'+transl_dict['edition_notice']+'</p>\n<p>'
        +transl_dict['meta_area']+'</p>\n<p>'+transl_dict['copyright_notice']+'</p>\n</div>')
    outputWrite.close()

    #CSS file
    shutil.copy('templates/main.css',writepath+'main.css')

    #PNG cover
    shutil.copy(language+'/'+namelist[0]+'_epub.jpg',writepath+namelist[0]+'_epub.jpg')

def paragraphNumbers(line):
    '''
    Deletes all paragraph references that do not match the paragraph_id.
    creates new paragraphs before floating paragraph references
    moves the paragraph reference to the end of the paragraph
    '''

    parnrs = re.findall(r'<a.*?class="(.*?)"',line)
    for pn in range(len(parnrs)):
        if parnrs[pn] != paragraph_id:
            line = re.sub('<a class="'+parnrs[pn]+r'" id=".*?"></a>','',line)
            line = re.sub(r'<a id=".*?" class="'+parnrs[pn]+'"></a>','',line)

    paragraph_nr = re.findall(r'(..)<a class="'+paragraph_id+r'" id="(.*?)"></a>',line)
    for nn in range(len(paragraph_nr)):
        if paragraph_nr[nn][0] != 'p>':
            line = line.replace('<a class="'+paragraph_id+'" id="'+paragraph_nr[nn][1]+'"></a>', '</p><p><a class="'+paragraph_id+'" id="'+paragraph_nr[nn][1]+'"></a>')

    #moves a paragraph reference to the end of the paragraph:
    line = re.sub(r'<p><a (.*?)"></a>(.*?)</p>', r'<p>\2<a \1"></a></p>',line)

    return line

def footNotes(line,fileFoots):
    '''
    changes span texts to footnotes at the bottom for EPub3
    '''
    footnotetitles = re.findall(r'<span class=".*?" title="(.*?)" id="note(\d{1,5})">.*?</span>',line)
    for nn in range(len(footnotetitles)):
        fileFoots.write('<aside epub:type"footnote" id="n'+footnotetitles[nn][1]+'"><p>'+footnotetitles[nn][1]+': '+footnotetitles[nn][0].strip()+'</p></aside>\n')

    line = re.sub(r'<span class="var" title="(.*?)" id="note(\d{1,5})">(.*?)</span>',
                r'\3<a class="note" epub:type="noteref" href="#n\2"><sup>\2</sup></a>',line)
    line = re.sub(r'<span class="cross" title="(.*?)" id="note(\d{1,5})">(.*?)</span>',
                r'\3<a class="note" epub:type="noteref" href="#n\2"><sup>\2</sup></a>',line)
    return line

def writeSutta(each_sutta):
    """
    Takes the sutta information for each sutta and writes it to file
    """
    fileFoots = open('footnotes.xhtml','w')
    fileFoots.write('<hr>\n')

    if len(namelist) > 3:
        suttaname = namelist[0]+str(suttanrs[each_sutta][0])+'.'+str(suttanrs[each_sutta][1])
    else:
        suttaname = namelist[0]+str(suttanrs[each_sutta])
    suttapath = os.path.join(suttadir,suttaname+'.html')

    fileOpen = open(suttapath,'r')
    fileWrite = open(namelist[0]+'_temp/'+namelist[0]+str(suttanrs[each_sutta])+'.xhtml','w')

    sectionname = Sutta(suttapath).get_section_title()

    if suttaname in sutta_vagga_dict.keys():
        fileWrite.write('<h1 class="vagga">'+sutta_vagga_dict[suttaname]+'</h1>\n')
        TOCWrite.write('</p>\n<p class="pref"><a href="'+namelist[0]+str(suttanrs[each_sutta])+'.xhtml">'+sutta_vagga_dict[suttaname]+'</a><br>')

    fileWrite.write('<h1>'+str(suttanrs[each_sutta])+' '+sectionname+'</h1>')
    sectionname = re.sub(r'<span .*?>(.*?)</span>',r'\1',sectionname)
    TOCWrite.write('<a class="sutta" href="'+namelist[0]+str(suttanrs[each_sutta])+'.xhtml">'
        +str(suttanrs[each_sutta])+' '+sectionname+'</a><br>')

    for line in fileOpen:
        if line.startswith('</div>'):
            break

    for line in fileOpen:
        line = line.strip()
        if not re.search('</article>', line):
            line = paragraphNumbers(line)
            line = re.sub(r'<ul.*?>','',line)
            line = re.sub('</ul>','',line)
            line = re.sub(r'<li.*?>','<p>',line)
            line = re.sub('</li>','</p>',line)
            line = re.sub(r'<a.*?href=.*?>(.*?)</a>',r'\1',line)
            line = re.sub(r'<h(\d{1,4})',r'\n<h\1',line)
            line = line.replace('<bl','\n<bl')
            line = line.replace('</blockquote>','</blockquote>\n')
            fileWrite.write(line)
        else: 
            break

    fileWrite.close()

    fileOpen = open(namelist[0]+'_temp/'+namelist[0]+str(suttanrs[each_sutta])+'.xhtml','r')
    fileWrite = open(writepath+namelist[0]+str(suttanrs[each_sutta])+'.xhtml','w')

    fileWrite.write('<div>\n<link rel="stylesheet" href="main.css">\n<article>\n')

    for line in fileOpen:
        #moves a paragraph reference to the end of the paragraph:
        line = re.sub(r'<p><a (.*?)"></a>(.*?)</p>', r'<p>\2<a \1"></a></p>',line)
        line = footNotes(line,fileFoots)
        line = re.sub(r'</h(\d{1,4})><p>“‘',r'</h\1><p class="fltwicequote">“‘',line)
        line = re.sub(r'</h(\d{1,4})><p>“',r'</h\1><p class="fldoublequote">“',line)
        line = re.sub(r'</h(\d{1,4})><p>‘',r'</h\1><p class="flquote">‘',line)
        line = re.sub(r'</h(\d{1,4})><p>',r'</h\1><p class="firstline">',line)
        if line.startswith('<blockquote'):
            line = line.replace('<p>“‘','<p class="fltwicequote">“‘')
            line = line.replace('<p>“','<p class="fldoublequote">“')
            line = line.replace('<p>‘','<p class="flquote">‘')
            line = line.replace('<p>','<p class="firstline">')
        else:
            line = line.replace('<p>“‘','<p class="twicequote">“‘')
            line = line.replace('<p>“','<p class="doublequote">“')
            line = line.replace('<p>‘','<p class="quote">‘')
        line = line.replace('<p','\n<p')
        line = line.replace('<p></p>\n','')
        if pars == 'Y':
        #creates a paragraph div block before the paragraph:
            line = re.sub(r'<p(.*?)>(.*?)<a class="'+paragraph_id+'" id="'+paragraph_id+r'(.*?)"></a></p>', r'<div class="par">\3</div><p\1>\2</p>',line)
            line = re.sub(r'<p(.*?)>(.*?)<a class="'+paragraph_id+r'" id="(.*?)"></a></p>', r'<div class="par">\3</div><p\1>\2</p>',line)

        fileWrite.write(line)

    fileFoots.close()
    fileWrite.write(open('footnotes.xhtml','r').read())

    fileWrite.write('\n</article>\n</div>\n')
    fileWrite.close()

    os.remove(namelist[0]+'_temp/'+namelist[0]+str(suttanrs[each_sutta])+'.xhtml')
    os.remove('footnotes.xhtml')


# loads all user input as data in dictionary
globals_dict = get_globals()
locals().update(globals_dict)
writepath = namelist[0]+versionnumber+'/'

try:
    os.listdir(namelist[0]+'_temp/')
except:
    os.mkdir(namelist[0]+'_temp/')

# loads translation dictionary
transl_dict = dict()
for rows in csv.reader(open(language+'/trans.txt', mode='r'),delimiter='='):
    transl_dict[rows[0]] = rows[1]

sutta_vagga_dict = match_sutta_vagga(namelist[0],language)

#TOC
TOCWrite = open(writepath+'toc.xhtml','w')
TOCWrite.write('<div>\n<link rel="stylesheet" href="main.css">\n<h1>'+transl_dict['contents']+'</h1>\n<p class="pref"><a href="preface.xhtml">'
    +transl_dict['preface_transl']+'</a>')

for each_sutta in range(startsutta, endsutta):
    writeSutta(each_sutta)

writeExtraPages()

os.rmdir(namelist[0]+'_temp/')

TOCWrite.write('</p>\n<p class="pref"><a href="bio.xhtml">'+transl_dict['bio_transl']+': '+transl_dict['author']+
    '</a></p>\n<p class="pref"><a href="about.xhtml">'+transl_dict['about_transl']+
    ' SuttaCentral</a></p>\n</div>\n')
TOCWrite.close()

makeEpub(writepath, namelist[0], language, transl_dict['isbn_paperback'], transl_dict['title_transl'], transl_dict['author'])
