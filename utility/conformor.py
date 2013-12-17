#!/usr/bin/env python

""" ANALYTICS:

Displays information about each sutta.
The colors mean as follow:
white/blue is purely informative.
green means there is probably no problem, and the basis for that assumption is printed.
yellow means there is a problem but the program knows how to and has the information available to fix it.
red means human intervention is required.

"""

import sys, regex, lxml.html, os, shutil, collections, itertools, glob
from copy import copy
from subprocess import Popen, PIPE
from nandar.termcolor import colored

path_to = "sktout"
path_from = "skt"
base_lang = 'en'

force_sc_nums = True

all_ids = "a.bl, a.bps, a.eno89, a.fol, a.fuk03, a.gatha-number, a.gatn, a.gbm, a.gno78, a.har04, a.hoe16, a.hos89a, a.hos89b, a.hos91, a.hs, a.kel, a.mat85, a.mat88, a.mit57, a.ms, a.pts, a.pts_pn, a.san87, a.san89, a.sc, a.sen82, a.sht, a.snp-vagga-section-verse, a.snp-vagga-verse, a.t, a.titus-random, a.tlinehead, a.tri62, a.tri95, a.ud-sutta, a.ud-vagga-sutta, a.tu, a.uv, a.vai59, a.vai61, a.verse-num-pts, a.vimula, a.vn, a.wal48, a.wal50, a.wal52, a.wal57c, a.wal58, a.wal59a, a.wal60, a.wal61, a.wal68a, a.wal70a, a.wal70b, a.wal76, a.wal78, a.wal80c, a.wp, a.yam72"

problems = collections.defaultdict(list)

metas = {}
class TidyError(Exception):
    pass

def numsortkey(input, index=0):
    """ Numerical sort. Handles identifiers well.

    Variable length ranges (i.e. 1.2 vs 1.11.111) are not handled gracefully.
    """
    if type(input) is str:
        string = input
    else:
        string = input[index]
        if string is None:
            return []
    return ( [int(a) if a.isnumeric() else a
                   for a in regex.split(r'(\d+)', string)] )

files = sorted((f for f in glob.glob(os.path.join(path_from, '*.html')) if 'meta' not in f), key=numsortkey)

def inject_filename_info(dom, filename):
    m = regex.match('sf[0-9]+(?:_(?<puid>[A-Z]+[0-9.?]+(?=_|\.)))*_?(?<name>[\w_]*\p{lower}\w*)?', filename)
    if not m:
        return
    name = m['name'] or ''
    puids = m.captures('puid') 
    print(", ".join(puids) + '  ' + name)

pnums = set()

for filename in files:
    info = {}
    inpath = os.path.dirname(filename)
    if path_from:
        if path_from not in inpath:
            raise ValueError("Value to replace not found")
        outpath = inpath.replace(path_from, path_to)
    else:
        outpath = os.path.join(path_to, filename)
    if not os.path.exists(outpath):
        os.mkdir(outpath)
    outfile = os.path.join(outpath, os.path.basename(filename))

    with open(filename) as f:
        text = f.read()
        text = text.replace('ṁ', 'ṃ').replace('Ṁ', 'Ṃ')
        text = regex.sub('.*</head>', '', text, flags=regex.DOTALL)
        text = '<html><head><meta charset="utf-8"><title></title></head><body>' + text
        print(filename)
        dom = lxml.html.document_fromstring(text)
    try:
        meta = metas[inpath]
    except KeyError:
        try:
            metas[inpath] = lxml.html.fromstring(open(os.path.join(inpath, 'meta.html')).read()).cssselect('#metaarea')[0]
        except OSError:
            metas[inpath] = None
        meta = metas[inpath]
    
    # Analytics.
    print("Analyzing {}:".format(filename))
    # Does this file have a menu?
    multisutta = len(dom.cssselect('article, h1')) > 2
    needsarticle = len(dom.cssselect('article')) == 0
    hasmeta = len(dom.cssselect('#metaarea')) == 1
    
    hasmenu = len(dom.cssselect('#menu')) > 0
    needsmenu = not hasmenu and len(dom.cssselect('h1, h2, h3')) > 3 or len(dom.cssselect('h1')) > 2

    try:
        lang = dom.cssselect('div[lang], html[lang]')[0].attrib['lang']
    except (IndexError, KeyError):
        lang = None

    # Does this this file have numbering?
    pnumbers = False
    pnumbers_need_id = False
    scnumbers_misplaced = False
    scnumbers_insane = False
    scn = dom.cssselect('a.sc')
    for a in scn:
        try:
            if a.getparent().text or a.getparent().attrib['id'] == 'metaarea':
                scnumbers_misplaced = True
                scnumbers_insane = True
                break
        except KeyError:
            pass
    if scn:
        pnumbers = "sc"
        def checksanity():
            global dom, pnumbers_need_id, scnumbers_insane
            for article in dom.cssselect('article.sutta'):
                
                seen = set()
                last = 0
                for a in scn:
                    try:
                        num = int(a.attrib['id'].split('.')[-1])
                    except KeyError:
                        return
                    if num - last < 1:
                        scnumbers_insane = True
                        return
                    parent = a.getparent()
                    if parent in seen:
                        scnumbers_insane = True
                        return
                    seen.add(parent)
        checksanity()
    else:
        c = collections.Counter()

        anchors = dom.cssselect('p a')
        c.update(a.attrib['class'] if 'class' in a.attrib else None for a in anchors)
        m = c.most_common(1)
        pcount = len(list(dom.iter('p')))
        if m and m[0][1] >= max(3, pcount / 4):
            pnumbers = m[0]
            pnumbers_no_id = ('id' not in dom.cssselect('a.'+pnumbers[0])[0].attrib) if pnumbers[0] is not None else False
            pnums.add(m[0])

    h1notinhgroup = False
    supplied_misused = False
    for h1 in dom.iter('h1'):
        if h1.getparent().tag != 'hgroup':
            h1notinhgroup = True
    for h in dom.cssselect('h1,h2,h3,h4,h5,h6,h7'):
        if 'class' in h.attrib and 'supplied' in h.attrib['class']:
            supplied_misused = True

    for e in dom.cssselect(all_ids):
        if 'id' not in e.attrib:
            pnumbers_need_id = True
            break
    items = []

    # Does this file need emdashing?

    tc = dom.text_content()
    if '"' in tc or '--' in tc or "'s" in tc:
        items.append(colored("emdash!", 'red'))

    if multisutta:
        items.append(colored("multi", 'blue'))
    else:
        items.append("single")
    try:
        dom.get_element_by_id('text')
    except KeyError:
        items.append(colored("no_div.text", 'yellow'))
    if needsarticle:
        items.append(colored("needsarticle", 'yellow'))
    if not hasmeta:
        items.append(colored("needsmeta", 'red' if meta is None else 'yellow'))
    if hasmenu:
        items.append(colored("hasmenu", 'green'))
    elif needsmenu:
        items.append(colored("needsmenu", 'yellow'))
    if pnumbers:
        color = 'green'
        if not pnumbers[0]:
            color = 'red'
        items.append(colored("p: {}".format(pnumbers), color))
    else:
        items.append(colored("needspnum", 'yellow'))
    
    if pnumbers_need_id:
        items.append(colored("pn_need_id", 'yellow'))
    if scnumbers_misplaced:
        items.append(colored("scnumbers_misplaced", 'yellow'))
    if scnumbers_insane:
        items.append(colored("scnumbers_insane", 'yellow'))
        
    items.append(colored('lang: '+str(lang), 'white' if lang else 'red'))

    if h1notinhgroup:
        items.append(colored('h1 not in hgroup', 'yellow'))
    if supplied_misused:
        items.append(colored('supplied misued', 'yellow'))
        
    print(", ".join(items))
    try:
        divtext = dom.get_element_by_id('text')
    except KeyError:
        divtext = dom.makeelement('div', {'id':'text'})
        divtext.extend(dom.body)
        dom.body.append(divtext)

    for e in dom.cssselect('#metaarea'):
        divtext.append(e)

    divtext.attrib['lang'] = lang or base_lang
    # Now do stuff.
    if needsarticle:
        if multisutta:
            raise NotImplementedError
        else:
            try:
                section = dom.cssselect('section')[0]
            except IndexError:
                section = dom.makeelement('section', {'class':'sutta'})
            article = dom.makeelement('article')
            # Move everything inside divtext into the article
            article.extend(divtext)
            divtext.append(section)
            section.append(article)
            # Guess the uid
            uid = regex.match(r'.*/(.*)\.html', filename)[1]
            info['uid'] = uid
            section.attrib['id'] = uid

    try:
        toc = dom.get_element_by_id('toc')
    except KeyError:
        toc = dom.makeelement('div', {'id':'toc'})
        divtext.insert(0, toc)

    if h1notinhgroup:
        for h1 in dom.iter('h1'):
            hgroup = dom.makeelement('hgroup')
            h1.addnext(hgroup)
            hgroup.append(h1)
    if supplied_misused:
        for h in dom.cssselect('h1,h2,h3,h4,h5,h6,h7'):
            if 'class' in h.attrib and 'supplied' in h.attrib['class']:
                if h.attrib['class'] == 'supplied':
                    del h.attrib['class']
                else:
                    h.attrib['class'] = regex.sub('supplied,?', '', h.attrib['class'])
                span = dom.makeelement('span', {'class':'add'})
                span.text = h.text; h.text = None
                for child in h:
                    span.append(child)
                h.append(span)
                
    if scnumbers_misplaced:
        for a in scn:
            p = a.getparent()
            a.tail = p.text
            p.text = None
        for a in dom.cssselect('#metaarea p a.sc'):
            a.drop_tree()

    used_ids = set()
    
    if scnumbers_insane or not pnumbers or force_sc_nums:
        for a in dom.cssselect('a.sc'):
            a.drop_tree()
        for section in dom.cssselect('section.sutta'):
            pcount = itertools.count(1)
            uid = section.attrib['id']
            assert uid[0].isalpha()
            for p in section.cssselect('p'):
                if len(p.text_content()) > 50:
                    id = str(next(pcount))
                    used_ids.add(id)
                    a = p.makeelement('a', {'class':'sc', 'id':id})
                    a.tail = p.text
                    p.text = None
                    p.insert(0, a)

    if pnumbers_need_id:
        c = collections.Counter(used_ids)
        for i, e in enumerate(dom.cssselect(all_ids)):
            if 'id' not in e.attrib:
                if e.text:
                    c[e.text] += 1
                    pid = e.text
                    if c[e.text] > 1:
                        pid = str(c[e.text]) + '_' + pid
                    e.text = None
                else:
                    pid = 'p' + str(i)
                e.attrib['id'] = pid
    
    if needsmenu and not hasmenu:
        try:
            menu_list = []
            if not multisutta:
                headings = dom.cssselect('h2, h3, h4, h5, h6')
                hcount = itertools.count(1)
                for h in headings:

                    if list(h.iterancestors('hgroup')):
                        continue # skip initial heading.
                    #try:
                        #if h.getnext().tag in 'h2, h3, h4, h5, h6':
                            #continue # Skip all but last heading in group
                    #except AttributeError:
                        #continue
                    id = 'm{}'.format(next(hcount))
                    # Wrangle the heading.
                    a = copy(h)
                    a.tag = 'a'
                    a.attrib.update({'href':'#toc', 'id':id})
                    h.clear()
                    h.append(a)

                    # Create the menu item
                    li = '<li><a href="#{}">{}</a></li>'.format(id, h.text_content())
                    depth = int(h.tag[1])
                    menu_list.append( (depth, li) )
                max_d = max(t[0] for t in menu_list)
                min_d = min(t[0] for t in menu_list)
                menu_list = [ (1 + t[0] - min_d, t[1]) for t in menu_list]

                # Build the menu
                menu = dom.makeelement('div', {'id':'menu'})
                ul = dom.makeelement('ul')
                menu.append(ul)
                last_d = 1
                last_e = ul
                for depth, li in menu_list:
                    # Create a new ul if the menu is getting deeper.
                    while depth > last_d:
                        ul = dom.makeelement('ul')
                        last_e[-1].append(ul)
                        last_e = ul
                        last_d += 1
                    while depth < last_d:
                        last_e = last_e.getparent().getparent()
                        last_d -= 1
                    last_e.append(lxml.html.fromstring(li))
                toc.insert(0, menu)
        except (AttributeError, IndexError):
            print("Menu generation failed, falling back.")
            menu = '<ul>{}</ul>'.format("\n".join(t[1] for t in menu_list))
            toc.insert(0, lxml.html.fragment_fromstring(menu))
            
    if not hasmeta:
        if meta is not None:
            divtext.append(copy(meta))
    for e in dom.cssselect('meta')[:-1]:
        e.drop_tree()
    
    # Closing Analytics
    try:
        dom.cssselect('#metaarea')[0]
    except IndexError:
        problems[filename].append("No metadata")
    out_text = '<!DOCTYPE html>'+lxml.html.tostring(dom, encoding='utf8').decode()#.replace('</head>', '<meta charset="utf-8></head>')
    tidy_text, tidy_err = Popen("tidy -w 0 --tidy-mark no --show-info no", shell=True, universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(out_text)
    if 'Error:' in tidy_err:
        raise TidyError(tidy_err)
    print("\n".join(regex.findall('Warning:.*', tidy_err)))
    with open(outfile, 'w') as f:
        f.write(tidy_text)

pc = collections.Counter()
for c, n in pnums:
    pc[c] += n
print("All pnum classes seen: {}".format(pc))