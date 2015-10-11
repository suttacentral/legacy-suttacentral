#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
See readme file for instructions on how to use this module
This converts a number of suttas in a directory to tex.
''' 
import re
import os
import jinja2
import csv


def get_globals():
    '''
    user input of globals
    '''

    suttanrs = []
    startsutta = -1
    endsutta = -1
    versionnumber = ''
    language = ''
    globals_dict = {}

    while True:
        suttadir = input('Enter the directory: ')
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
    while True:
        language = input("Enter the directory name where your translation files are stored: ")
        try:
            os.listdir(language)
            break
        except:
            print('Not a valid directory, please try again.')
 
    globals_dict['language'] = language
    globals_dict['versionnumber'] = versionnumber
    globals_dict['suttadir'] = suttadir
    globals_dict['startsutta'] = startsutta
    globals_dict['endsutta'] = endsutta
    globals_dict['suttanrs'] = suttanrs
    globals_dict['namelist'] = namelist

    return globals_dict


html_to_latex2 = {'<h2>':'\\subsection*{', '<h3>':'\\subsubsection*{', '<h4>':'\\hfour{',
                 '<h5>':'\\hfive{', '<h6>':'\\hsix{',
                 '<i.*?>':'\\emph{', '</i>':'}', '<em.*?>':'\\emph{', '</em>':'}',
                 '<ol.*?>':'\\ begin{enumerate}\n',  '</ol>':'\\ end{enumerate}\n','<ul>':'',  '</ul>':'\n',
                 '<li>':'','</li>':'\n\n','<p.*?>':'',
                 '<br>':'\\ \\\n','<blockquote.*?>':'\\ begin{verse} [\\ versewidth]\n',
                 '</blockquote>':'\\ end{verse}\n\n',
                 '<strong>':' \\ textbf{', '<b>':' \\ textbf{', '</strong>':'}', '</b>':'}'
                  }

html_to_latex1 = {'</h\d{1,3}>':'}\n\n', '\[':'{[}', '\]':'{]}',
                 '<p>“':'\\ vleftofline{“}', '<p>‘':'\\ vleftofline{‘}', '</p>':"\n\n",
                 '</a>':'', '<a .*?>':'',
                 '</div>':'', '<div .*?>':'',
                 '<span .*?>':'', '</span>':''
                  }

html_to_latex3 = {'}“':'}\\ vleftofline{“}', '}‘':'}\\ vleftofline{‘}',
                  }               


def match_sutta_vagga(nikaya):
    '''
    Matches sutta numbers to the vagga dictionary to output a dictionary with suttas 
    before which a new vagga name is to be added as  new chapter
    '''
    vagga_dict = dict()
    for rows in csv.reader(open(language+'/vagga.csv', mode='r')):
        if rows[0] == nikaya:
            vagga_dict[rows[1]] = rows[2]

    sutta_dict = dict()
    for rows in csv.reader(open('sutta.csv', mode='r')):
        if rows[4] == '1' and rows[2] == nikaya:
            sutta_dict[rows[1]] = rows[3]

    sutta_vagga_dict = dict()
    for keys,values in sutta_dict.items():
        sutta_vagga_dict[keys] = vagga_dict[values]

    return sutta_vagga_dict

def cleanHTML(line):
    """
    cleans a line of text and replaces it with appropriate latex coding
    """
    clean_line = line
    if line.startswith('<h'):
        #Takes care of long headers due to pali behind it
        clean_line = re.sub(" \(<i.*?>","\\ \\  \\small{(\\emph{",clean_line)
        clean_line = re.sub(" \(<em.*?>","\\ \\  \\small{(\\emph{",clean_line)
        clean_line = re.sub("</i>\)","})}",clean_line)
        clean_line = re.sub("</em>\)","})}",clean_line)
    evamtext = re.findall(r'<span class="evam">(.*?)</span>', clean_line)
    if evamtext:
        clean_line = re.sub('<span class="evam">(.*?)</span>','\\ caps{'+evamtext[0]+'}',clean_line)
    addtext = re.findall(r'<span class="add">(.*?)</span>', clean_line)
    for nr in range(0,len(addtext)):
        if addtext[nr] and addtext[nr].startswith('('):
            clean_line = re.sub('<span class="add">(.*?)</span>',addtext[nr],clean_line)
        elif addtext[nr]:
            clean_line = re.sub('<span class="add">(.*?)</span>','('+addtext[nr]+')',clean_line)
    for x,y in html_to_latex1.items():
        clean_line = re.sub(x,y,clean_line)
    for x,y in html_to_latex2.items():
        clean_line = re.sub(x,y,clean_line)
    for x,y in html_to_latex3.items():
        clean_line = clean_line.replace(x,y)
    if clean_line.startswith('‘'):
        clean_line = re.sub('‘', '\\ vleftofline{‘}', clean_line, count=1)
    elif clean_line.startswith('“'):
        clean_line = re.sub('“', '\\ vleftofline{“}', clean_line, count=1)
    clean_line = clean_line.replace('\\ vleftofline{“}\\ vleftofline{‘}','\\ vleftofline{“}‘')
    clean_line = clean_line.replace("\\ ","\\") # counteract a bug in re module
    clean_line = clean_line.replace("  "," ")
    return clean_line

def addParagraph(line):
    """
    Searches the document for paragraph numbers and replaces them with latex coding
    """
    paragraph_nr = re.findall(r'<a class="\w+" id="..(.*?)">', line)
    if paragraph_nr:
        line = re.sub('<a class=".*?" id=".*?(\d{1,5})">','\\ paragraph{'+paragraph_nr[0]+'}',line)
    return line

def writeHeader():
    """
    Writes the header information to the file
    """
    jinja2_environment = jinja2.Environment(autoescape = True, loader = jinja2.FileSystemLoader(os.getcwd()))
    template = jinja2_environment.get_template('header_template.tex')
    fileWrite.write(template.render(titleabr=namelist[0].upper(),transl_dict=transl_dict,
        sectioncounter=startsutta,prefacefile=language+'/preface.txt'))

def writeFooter():
    """
    Writes footer info to the file
    """
    #abouttmp is a temp. file i.e. the conversion of the about.txt file to latex and is inserted into the footer
    aboutfh = open(language+'/about.txt','r')
    abouttmp = open('about.tmp','w')
    linecount = 0

    for line in aboutfh:
        if len(line) > 2:
            urls = re.findall(r'https://(.*?) ' , line, re.M)
            urls2 = re.findall(r'https://(.*?)\.\n' , line, re.M)
            for url in urls: line = re.sub("https://"+url,"\\href{https://"+url+"}{"+url+"}",line)
            for url in urls2: line = re.sub("https://"+url,"\\href{https://"+url+"}{"+url+"}",line)
            if linecount == 0:
                abouttmp.write('{\\small\\noindent '+line+'}\n\n')
                linecount += 1
            else:
                abouttmp.write('{\\small '+line+'}\n\n')

    abouttmp.close()

    jinja2_environment = jinja2.Environment(autoescape = True, loader = jinja2.FileSystemLoader(os.getcwd()))
    template = jinja2_environment.get_template('footer_template.tex')
    fileWrite.write(template.render(transl_dict=transl_dict,biofile=language+'/bio.txt',aboutfile='about.tmp'))

    os.remove('about.tmp')

def writeSutta(each_sutta):
    """
    Takes the sutta information for each sutta and writes it to file
    """
    if len(namelist) > 3:
        suttaname = namelist[0]+str(suttanrs[each_sutta][0])+'.'+str(suttanrs[each_sutta][1])
    else:
        suttaname = namelist[0]+str(suttanrs[each_sutta])
    suttapath = os.path.join(suttadir,suttaname+'.html')

    fileOpen = open(suttapath,'r')

    #If the suttasections starts with a digit, this is thrown out.
    if not Sutta(suttapath).get_section_title()[0].isdigit():
        sectionname = Sutta(suttapath).get_section_title()
    else:
        sectionname = re.findall(r'\d{1,5}(.*?)', Sutta(suttapath).get_section_title())[0]
        sectionname = sectionname.strip()
        if sectionname.startswith('.'):
            sectionname = re.findall(r'\. (.*?)', Sutta(suttapath).get_section_title())[0]

    if suttaname in sutta_vagga_dict.keys():
        fileWrite.write('\n\chapter*{'+sutta_vagga_dict[suttaname]+'}\\thispagestyle{empty}\n')
    fileWrite.write('\n\\section{'+sectionname+'}\n\n')
        
    for line in fileOpen:
        if line.startswith('<h1'):
            break

    for line in fileOpen:
        line = line.strip()
        if not (re.search('<p class="endsutta">', line) or re.search('</article>', line)):
            line = addParagraph(line)
            line = cleanHTML(line)
            fileWrite.write(line)
        elif re.search('<p class="endsutta">', line):
            line = line.replace('<p class="endsutta">','\n\\finsutta{')
            line = line.replace('</p>','}\n\n')
            fileWrite.write(line)
            break
        elif line.startswith('</p>'):
            fileWrite.write('\n\n')
            break
        else: 
            break

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
        self._section_title = re.findall(r'<h1>(.*?)</h1>', self._readSutta)[0]
        return self._section_title


# loads all user input as data in dictionary
globals_dict = get_globals()
locals().update(globals_dict)

# loads translation dictionary
transl_dict = dict()
for rows in csv.reader(open(language+'/trans.txt', mode='r'),delimiter='='):
    transl_dict[rows[0]] = rows[1]

sutta_vagga_dict = match_sutta_vagga(namelist[0])

# create file handlers
fileWrite = open(namelist[0]+versionnumber+'.tex', 'w') 

# write header, suttas and footer to file
writeHeader()
for each_sutta in range(startsutta, endsutta):
    writeSutta(each_sutta)

writeFooter()
fileWrite.close()

