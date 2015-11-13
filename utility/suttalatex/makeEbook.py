#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Changes output of convertepub.py to epub3 format. This module for use in the terminal only.
'''
import re
from ebooklib import epub

original_get_template = epub.EpubBook.get_template
def new_get_template(*args, **kwargs):
    return original_get_template(*args, **kwargs).encode(encoding='utf8')

def makeEpub(path, nikaya, language, isbn, title, author):
    book = epub.EpubBook()
    tocncx = []

    # set metadata
    book.set_identifier(isbn)
    book.set_title(title)
    book.set_language(language)
    book.add_author(author)
    im = open(path+nikaya+'_epub.jpg','rb').read()
    book.set_cover(file_name=nikaya+'_epub.jpg', content=im, create_page=True)

    chapterslist = ['titlepage', 'metaarea', 'toc']

    titlepage = epub.EpubHtml(uid='titlepage', title='Cover', file_name='titlepage.xhtml')
    titlepage.content = '<section style="text-align:center;" epub:type="cover"><img src="mn_epub.jpg"/></section>'
    book.add_item(titlepage)
    metaarea = epub.EpubHtml(uid='metaarea', title='Meta Data', file_name='metaarea.xhtml')
    metaarea.content = open(path+'metaarea.xhtml').read()
    book.add_item(metaarea)
    
    #read toc.xhtml and create ncx file out of this
    tocfile = open(path+'toc.xhtml','r')
    for line in tocfile:
        if line.startswith('<h1'):
            contenttext = re.findall(r'<h1>(.*?)</h1>',line)[0]
            chapter = epub.EpubHtml(uid='toc', title=contenttext, file_name='toc.xhtml')
            chapter.content=open(path+'toc.xhtml').read()
            book.add_item(chapter)
            tocncx.append(epub.Link('toc.xhtml', contenttext, 'toc'))
        elif line.startswith('<p class="pref"><a href="'+nikaya):
            vagga = []
            suttalst = []
            contenttext = re.findall(r'<p class="pref"><a href="(.*?)\.xhtml">(.*?)</a>',line)
            suttatext = re.findall(r'<a class="sutta" href="(.*?)\.xhtml">(.*?)</a>',line)
            vagga.append(epub.Section(contenttext[0][1]))
            for nr in range(len(suttatext)):
                chapter = epub.EpubHtml(uid=suttatext[nr][0], title=suttatext[nr][1], file_name=suttatext[nr][0]+'.xhtml')
                chapter.content=open(path+suttatext[nr][0]+'.xhtml').read()
                book.add_item(chapter)
                chapterslist.append(suttatext[nr][0])
                suttalst.append(chapter)
            vagga.append(tuple(suttalst))
            tocncx.append(tuple(vagga))
        elif line.startswith('<p class="pref">'):
            contenttext = re.findall(r'<p class="pref"><a href="(.*?)\.xhtml">(.*?)</a>',line)
            chapter = epub.EpubHtml(uid=contenttext[0][0], title=contenttext[0][1], file_name=contenttext[0][0]+'.xhtml')
            chapter.content=open(path+contenttext[0][0]+'.xhtml').read()
            book.add_item(chapter)
            tocncx.append(epub.Link(contenttext[0][0]+'.xhtml', contenttext[0][1], contenttext[0][0]))
            chapterslist.append(contenttext[0][0])

    book.toc = tuple(tocncx)
    book.add_item(epub.EpubNcx())

    # define CSS style
    nav_css = epub.EpubItem(uid="style_nav", file_name="main.css", media_type="text/css", content=open(path+'main.css').read())
    book.add_item(nav_css)

    # basic spine
    book.spine = chapterslist

    # write to the file
    epub.EpubBook.get_template = new_get_template
    epub.write_epub(path+nikaya+'_epub.epub', book, {})
