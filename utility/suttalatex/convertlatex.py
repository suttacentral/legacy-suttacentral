#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
See readme file for instructions on how to use this module
This converts a number of suttas in a directory to tex.
pi/su/mn/
''' 
import re
import os
import jinja2
import csv
from base_input import get_globals, match_sutta_vagga, Sutta

# Ordered dictionary to run through regex commands in order.
#The item: '­':'\\ -' is an invisible hyphernation character.

html_to_latex = ([('</h\d{1,3}>','}\n\n'), ('\[','{[}'), ('\]','{]}'),
                 ('<p>“','\\ vleftofline{“}'), ('<p>‘','\\ vleftofline{‘}'), ('</p>',"\n\n"),
                 ('</a>',''), ('<a .*?>',''), ('#','\\ #'), ('\^','\\ ^\\  '),
                 ('</div>',''), ('<div .*?>',''),
                 ('<span .*?>',''), ('</span>',''), ('­','\\ -'),
                 ('<h2>','\\subsection*{'), ('<h3>','\\subsubsection*{'), ('<h4>','\\hfour{'),
                 ('<h5>','\\hfive{'), ('<h6>','\\hsix{'),
                 ('<i.*?>','\\emph{'), ('</i>','}'), ('<em.*?>','\\emph{'), ('</em>','}'),
                 ('<ol.*?>','\\ begin{enumerate}\n'), ('</ol>','\\ end{enumerate}\n'), ('<ul>',''), ('</ul>','\n'),
                 ('<li>',''),('</li>','\n\n'),('<p.*?>',''),
                 ('<br>','\\ \\\n'), ('<blockquote.*?>','\\ begin{verse} [\\ versewidth]\n'),
                 ('</blockquote>','\\ end{verse}\n\n'),
                 ('<strong>',' \\ textbf{'), ('<b>',' \\ textbf{'), ('</strong>','}'), ('</b>','}'),
                 ('}“','}\\ vleftofline{“}'), ('}‘','}\\ vleftofline{‘}')
                  ])

def cleanHTML(line):
    """
    cleans a line of text and replaces it with appropriate latex coding
    """
    clean_line = line
    if line.startswith('<h'):
    #Takes care of long headers due to pali behind it - only in translations
        clean_line = re.sub(r" \(<i.*?>(.*?)</i>\)",r"\\ \\  \\small{(\\emph{\1})}",clean_line)
        clean_line = re.sub(r" \(<em.*?>(.*?)</em>\)",r"\\ \\  \\small{(\\emph{\1})}",clean_line)
    # adds the "thus have I heard" part
    clean_line = re.sub(r'<span class="evam">(.*?)</span>',r'\\ textsc{\1}',clean_line)
    # adds the add-span class
    addtext = re.findall(r'<span class="add">(.*?)</span>', clean_line)
    for nr in range(0,len(addtext)):
        if addtext[nr] and addtext[nr].startswith('('):
            clean_line = re.sub(r'<span class="add">(.*?)</span>',addtext[nr], clean_line)
        elif addtext[nr]:
            clean_line = re.sub(r'<span class="add">(.*?)</span>','('+addtext[nr]+')',clean_line)
    # changes endsection to finsection
    clean_line = re.sub(r'<p class="endsection">(.*?)</p>',r'\n\\ finsection{\1}\n\n',clean_line)
    # cleans the line as per dictionary entries in order
    for x in range(len(html_to_latex)):
        clean_line = re.sub(html_to_latex[x][0],html_to_latex[x][1],clean_line)
    #adds vleftofline in paragraphs that are not marked with a paragraph number
    if clean_line.startswith('‘'):
        clean_line = re.sub('‘', '\\ vleftofline{‘}', clean_line, count=1)
    elif clean_line.startswith('“'):
        clean_line = re.sub('“', '\\ vleftofline{“}', clean_line, count=1)
        clean_line = clean_line.replace('\\ vleftofline{“}\\ vleftofline{‘}','\\ vleftofline{“}‘')

    clean_line = clean_line.replace("\\ ","\\") # counteract a bug in re module
    clean_line = clean_line.replace("  "," ")
    if clean_line.startswith(' '):
        clean_line = re.sub(' ', '', clean_line, count=1)
    return clean_line

def addParagraph(line):
    """
    Searches the document for paragraph numbers and replaces them with latex coding
    """
    if paragraph_id == 'sc':
        paragraph_nr = re.findall(r'<a class="'+paragraph_id+'" id="(.*?)">', line)
    else:
        paragraph_nr = re.findall(r'<a class="'+paragraph_id+'" id="'+paragraph_id+'(.*?)">', line)

    if paragraph_nr:
        for nn in range(len(paragraph_nr)):
            if nn == 0:
                line = re.sub(r'<a class="'+paragraph_id+'" id=".*?">','\\ paragraph{'+paragraph_nr[nn]+'}', line, count=1)
            else:
                line = re.sub(r'<a class="'+paragraph_id+'" id=".*?">','\n\n\\ paragraph{'+paragraph_nr[nn]+'}', line, count=1)
    return line

def addFootnotes(line):
    """
    Changes notes in pali texts to footnotes
    <span class="var" title="anubaddhā (bj, pts1)" id="note1">anubandhā</span>
    """
    line = re.sub(r'<span class=".*?" title="(.*?)" id="note.*?">(.*?)</span>',r'\2\\ footnote{\1}', line)
    return line

def writeHeader():
    """
    Writes the header information to the file
    """
    jinja2_environment = jinja2.Environment(autoescape = True, loader = jinja2.FileSystemLoader(os.getcwd()))
    template = jinja2_environment.get_template('templates/header_template.tex')
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
    template = jinja2_environment.get_template('templates/footer_template.tex')
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

    # add footnote if the section title has one
    section_title = addFootnotes(Sutta(suttapath).get_section_title())
    for x in range(len(html_to_latex)):
        section_title = re.sub(html_to_latex[x][0],html_to_latex[x][1],section_title)
    section_title = section_title.replace("\\ ","\\") # counteract a bug in re module

    #If the suttasections starts with a digit, this is thrown out.
    if not section_title[0].isdigit():
        sectionname = section_title
    else:
        sectionname = re.findall(r'\d{1,5}(.*?)', section_title)[0]
        sectionname = sectionname.strip()
        if sectionname.startswith('.'):
            sectionname = re.findall(r'\. (.*?)', section_title)[0]

    if suttaname in sutta_vagga_dict.keys():
        fileWrite.write('\n\chapter*{'+sutta_vagga_dict[suttaname]+'}\\thispagestyle{empty}\n')

    #if there is a footnote in the section, it needs a different format in order not to mess up the toc
    sectiontxt = re.findall(r'(.*?)\\footnote',sectionname)
    if sectiontxt:
        fileWrite.write('\n\\section['+sectiontxt[0]+']{'+sectionname+'}\n\n')
    else:
        fileWrite.write('\n\\section{'+sectionname+'}\n\n')
        
    for line in fileOpen:
        if line.startswith('<h1'):
            break

    for line in fileOpen:
        line = line.strip()
        if not (re.search('<p class="endsutta">', line) or re.search('</article>', line)):
            if pars == 'Y':
                line = addParagraph(line)
            line = addFootnotes(line)
            line = cleanHTML(line)
            fileWrite.write(line)
        elif re.search('<p class="endsutta">', line):
            line = re.sub(r'<p class="endsutta">(.*?)</p>',r'\n\\finsutta{\1}\n\n', line)
            fileWrite.write(line)
            break
        elif line.startswith('</p>'):
            fileWrite.write('\n\n')
            break
        else: 
            break


# loads all user input as data in dictionary
globals_dict = get_globals()
locals().update(globals_dict)

# loads translation dictionary
transl_dict = dict()
for rows in csv.reader(open(language+'/trans.txt', mode='r'),delimiter='='):
    transl_dict[rows[0]] = rows[1]

sutta_vagga_dict = match_sutta_vagga(namelist[0],language)

# create file handlers
fileWrite = open(namelist[0]+versionnumber+'/'+namelist[0]+versionnumber+'.tex', 'w') 

# write header, suttas and footer to file
writeHeader()
for each_sutta in range(startsutta, endsutta):
    writeSutta(each_sutta)

writeFooter()
fileWrite.close()

