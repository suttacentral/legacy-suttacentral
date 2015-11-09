#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
See readme file for instructions on how to use this module
This converts a number of suttas in a directory to epub. Use Calibre to convert it further.
pi/su/mn/
''' 
import re
import os
import jinja2
import csv
import shutil
from base_input import get_globals, match_sutta_vagga, Sutta

navnum = 3

def ReadWritePage(inputname,titletext):
    """
    Helper function to read a text file and write the output xhtml file
    """
    linenr = 1
    inputOpen = open(language+'/'+inputname+'.txt','r')
    outputWrite = open(namelist[0]+versionnumber+'/'+inputname+'.xhtml','w')
    outputWrite.write(open('templates/header_epub_template.xhtml').read())
    outputWrite.write('<article>\n<h1'+titletext+'</h1>\n')
    for line in inputOpen:
        line = re.sub(r' https://(.*?) ',r' <a href="https://\1">\1</a> ',line)
        line = re.sub(r' https://(.*?)\.\n',r' <a href="https://\1">\1</a>.\n',line)
        if len(line) > 2:
            if linenr == 1:
                outputWrite.write('<p class="firstline">'+line+'</p>\n')
                linenr += 1
            else:
                outputWrite.write('<p>'+line+'</p>\n')
    outputWrite.write('\n</article>\n</body>\n</html>')
    outputWrite.close()


def writeExtraPages():
    """
    Writes the Preface, Biography, Metadata and About sections as well as 
    makes a copy of the css and png file in the current directory
    """

    #Preface
    ReadWritePage('preface','>'+transl_dict['preface_transl'])

    #Biography
    ReadWritePage('bio',' class="endtext">'+transl_dict['bio_transl']+": "+transl_dict['author'])

    #About SuttaCentral
    ReadWritePage('about',' class="endtext">'+transl_dict['about_transl']+' SuttaCentral')

    #Metadata
    outputWrite = open(namelist[0]+versionnumber+'/metaarea.xhtml','w')
    outputWrite.write(open('templates/header_epub_template.xhtml').read())
    outputWrite.write('<p>'+transl_dict['edition_notice']+'</p>\n')
    outputWrite.write('<p>'+transl_dict['meta_area']+'</p>\n')
    outputWrite.write('<p>'+transl_dict['copyright_notice']+'</p>\n')
    outputWrite.write('\n</body>\n</html>')
    outputWrite.close()

    #CSS file
    shutil.copy('templates/main.css',namelist[0]+versionnumber+'/main.css')

    #PNG cover
    shutil.copy(language+'/'+namelist[0]+'_epub.png',namelist[0]+versionnumber+'/'+namelist[0]+'_epub.png')

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
    changes span texts to footnotes at the bottom for EPub2
    '''
    footnotetitles = re.findall(r'<span class=".*?" title="(.*?)" id="note(\d{1,5})">.*?</span>',line)
    for nn in range(len(footnotetitles)):
        fileFoots.write('<p><a epub:type="footnote" id="n'+footnotetitles[nn][1]+'">'+footnotetitles[nn][1]+': '+footnotetitles[nn][0].strip()+'</a></p>\n')
        #fileFoots.write('<p><a id="note'+footnotetitles[nn][1]+'">'+footnotetitles[nn][1]+': '+footnotetitles[nn][0].strip()+'</a></p>\n')

    line = re.sub(r'<span class="var" title="(.*?)" id="note(\d{1,5})">(.*?)</span>',
                r'\3<a class="note" epub:type="noteref" href="#n\2">\2</a>',line)
        #r'\3<sup><a class="footnote" href="#note\2">\2</a></sup>',line)
    line = re.sub(r'<span class="cross" title="(.*?)" id="note(\d{1,5})">(.*?)</span>',
                r'\3<a class="note" epub:type="noteref" href="#n\2">\2</a>',line)
        #r'\3<sup><a class="footnote" href="#note\2">\2</a></sup>',line)
    return line

def writeSutta(each_sutta):
    """
    Takes the sutta information for each sutta and writes it to file
    """
    global navnum


    fileFoots = open('footnotes.xhtml','w')
    fileFoots.write('<hr>\n<aside>\n')

    if len(namelist) > 3:
        suttaname = namelist[0]+str(suttanrs[each_sutta][0])+'.'+str(suttanrs[each_sutta][1])
    else:
        suttaname = namelist[0]+str(suttanrs[each_sutta])
    suttapath = os.path.join(suttadir,suttaname+'.html')

    fileOpen = open(suttapath,'r')
    fileWrite = open(namelist[0]+'_temp/'+namelist[0]+str(suttanrs[each_sutta])+'.xhtml','w')

    #If the suttasections starts with a digit, this is thrown out.
    if not Sutta(suttapath).get_section_title()[0].isdigit():
        sectionname = Sutta(suttapath).get_section_title()
    else:
        sectionname = re.findall(r'\d{1,5}(.*?)', Sutta(suttapath).get_section_title())[0]
        sectionname = sectionname.strip()
        if sectionname.startswith('.'):
            sectionname = re.findall(r'\. (.*?)', Sutta(suttapath).get_section_title())[0]

    if suttaname in sutta_vagga_dict.keys():
        fileWrite.write('<h1 class="vagga">'+sutta_vagga_dict[suttaname]+'</h1>\n')
        TOCWrite.write('</p>\n<p class="pref"><a href="'+namelist[0]+str(suttanrs[each_sutta])+'.xhtml">'+sutta_vagga_dict[suttaname]+'</a><br>\n')
        if navnum != 3:
            TOC_ncxWrite.write('</navpoint>\n')
        TOC_ncxWrite.write('<navPoint id="num_'+str(navnum)+'" playOrder="'+str(navnum)+
            '">\n<navLabel>\n<text>'+sutta_vagga_dict[suttaname]+'</text>\n</navLabel>\n<content src="'
            +namelist[0]+str(suttanrs[each_sutta])+'.xhtml"/>\n')
        navnum += 1

    fileWrite.write('<h1><a id="'+namelist[0]+str(suttanrs[each_sutta])+'"></a>'+str(suttanrs[each_sutta])+' '+sectionname+'</h1>')
    TOCWrite.write('<a href="'+namelist[0]+str(suttanrs[each_sutta])+'.xhtml#'+namelist[0]+str(suttanrs[each_sutta])+'" class="sutta">'
        +str(suttanrs[each_sutta])+' '+re.sub(r'<span .*?>(.*?)</span>',r'\1',sectionname)+'</a><br>\n')
    TOC_ncxWrite.write('<navPoint id="num_'+str(navnum)+'" playOrder="'+str(navnum)+
        '">\n<navLabel>\n<text>'+str(suttanrs[each_sutta])+' '+sectionname+
        '</text>\n</navLabel>\n<content src="'+namelist[0]+str(suttanrs[each_sutta])+'.xhtml#'+namelist[0]+str(suttanrs[each_sutta])+'"/>\n</navPoint>')
    navnum += 1

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
    fileWrite = open(namelist[0]+versionnumber+'/'+namelist[0]+str(suttanrs[each_sutta])+'.xhtml','w')

    fileWrite.write(open('templates/header_epub_template.xhtml').read())
    fileWrite.write('<article>\n')

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

    fileFoots.write('\n</aside>')
    fileFoots.close()
    fileWrite.write(open('footnotes.xhtml','r').read())

    fileWrite.write('\n</article>\n</body>\n</html>')
    fileWrite.close()

    os.remove(namelist[0]+'_temp/'+namelist[0]+str(suttanrs[each_sutta])+'.xhtml')
    os.remove('footnotes.xhtml')


# loads all user input as data in dictionary
globals_dict = get_globals()
locals().update(globals_dict)

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
TOCWrite = open(namelist[0]+versionnumber+'/toc.xhtml','w')
TOC_ncxWrite = open(namelist[0]+versionnumber+'/toc.ncx','w')
TOCWrite.write(open('templates/header_epub_template.xhtml').read())
TOC_ncxWrite.write(open('templates/toc_header.ncx').read())
TOCWrite.write('<h1>'+transl_dict['contents']+'</h1>\n<p class="pref"><a href="metaarea.xhtml"></a></p>\n<p class="pref"><a href="preface.xhtml">'
    +transl_dict['preface_transl']+'</a>')

for each_sutta in range(startsutta, endsutta):
    writeSutta(each_sutta)

writeExtraPages()

os.rmdir(namelist[0]+'_temp/')

TOCWrite.write('</p>\n<p class="pref"><a href="bio.xhtml">'+transl_dict['bio_transl']+': '+transl_dict['author']+
    '</a></p>\n<p class="pref"><a href="about.xhtml">'+transl_dict['about_transl']+
    ' SuttaCentral</a></p>\n</body>\n</html>')
TOC_ncxWrite.write('</navpoint>\n<navPoint id="num_'+str(navnum)+'" playOrder="'+str(navnum)+
    '">\n<navLabel>\n<text>'+transl_dict['bio_transl']+': '+transl_dict['author']+
    '</text>\n</navLabel>\n<content src="bio.xhtml"/>\n</navPoint>\n<navPoint id="num_'
    +str(navnum+1)+'" playOrder="'+str(navnum+1)+'">\n<navLabel>\n<text>'
    +transl_dict['about_transl']+' SuttaCentral</text>\n</navLabel>\n<content src="about.xhtml"/>\n</navPoint>\n</navMap>\n</ncx>')
TOCWrite.close()
TOC_ncxWrite.close()