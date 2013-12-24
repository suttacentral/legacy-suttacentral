#!/usr/bin/env python

""" ANALYTICS:

Displays information about each sutta.
The colors mean as follow:
white/blue is purely informative.
green means there is probably no problem, and the basis for that assumption is printed.
yellow means there is a problem but the program knows how to and has the information available to fix it.
red means human intervention is required.

"""

import sys, regex, os, shutil, collections, itertools
import pathlib
from copy import copy

import sc

def get_existing_uids(_cache=[]):
    try:
        return _cache[0]
    except IndexError:
        pass
    imm = sc.scimm.imm()
    existing_uids = set(imm.suttas.keys())
    for value in imm.text_paths.values():
        existing_uids.update(value.keys())
    _cache.append(existing_uids)
    return existing_uids

def get_tag_data(_cache=[]):
    try:
        return _cache[0]
    except IndexError:
        pass
    import json
    jsonfile = sc.base_dir / 'utility' / 'tag_data.json'
    with jsonfile.open('r') as f:
        tag_data = json.load(f)
    _cache.append(tag_data)
    return tag_data


def has_ascii_punct(root):
    badpuncts = ('"', '--', "'s")
    for e in root.iter():
        for punct in badpuncts:
            if (e.text and punct in e.text) or (e.tail and punct in e.tail):
                return True
            return False

def finalize(root, entry, lang=None, metadata=None, options={}):
    pnums = set()
    filename = entry.filename
    existing_uids = get_existing_uids()
    tag_data = get_tag_data()
    # Analytics.
    print("Analyzing {}:".format(filename))
    # Does this file have a menu?
    multisutta = len(root.select('article, h1')) > 2
    needsarticle = len(root.select('article')) == 0
    try:
        metadata = root.select_or_throw('#metaarea')[0]
        hasmeta = True
    except:
        hasmeta = False
        if not metadata:
            entry.error('No metadata found. Metadata should either be in a \
            <div id="metaarea"> tag, or a seperate file "meta.html".')
            # No metadata is an error (i.e. absolutely invalidates text)
            # But we will continue to find more errors.
        
    hasmenu = len(root.select('#menu')) > 0
    needsmenu = not hasmenu and len(root.select('h1, h2, h3')) > 3 or len(root.select('h1')) > 2

    try:
        lang = root.select('div[lang], html[lang], section[lang], article[lang]')[0].attrib['lang']
    except (IndexError, KeyError):
        if not lang:
            entry.error('No language code found. Either use <div id="en">, or include \
            in a subfolder en/filename.html')
            # No language is an error, but we will forge ahead!
    
    uid = pathlib.Path(entry.filename).stem
    if uid not in existing_uids:
        entry.warning("The filename does not match the uid or filename of an \
        existing text, this is okay if you are adding something completely \
        new but is more likely an error.")
        
    # Does this this file have numbering?
    pnumbers = False
    pnumbers_need_id = False
    scnumbers_misplaced = False
    scnumbers_insane = False
    scn = root.select('a.sc')
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
            global root, pnumbers_need_id, scnumbers_insane
            for article in root.select('article.sutta'):
                
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

        anchors = root.select('p a')
        c.update(a.attrib['class'] if 'class' in a.attrib else None for a in anchors)
        m = c.most_common(1)
        pcount = len(list(root.iter('p')))
        if m and m[0][1] >= max(3, pcount / 4):
            pnumbers = m[0]
            pnumbers_no_id = ('id' not in root.select('a.'+pnumbers[0])[0].attrib) if pnumbers[0] is not None else False
            pnums.add(m[0])

    h1notinhgroup = False
    supplied_misused = False
    for h1 in root.iter('h1'):
        if h1.getparent().tag != 'hgroup':
            h1notinhgroup = True
    for h in root.select('h1,h2,h3,h4,h5,h6,h7'):
        if 'class' in h.attrib and 'supplied' in h.attrib['class']:
            supplied_misused = True
    
    all_ids = ','.join(tag_data['pnum_classes'].keys())
    for e in root.select(all_ids):
        if 'id' not in e.attrib:
            pnumbers_need_id = True
            break
    items = []

    # Does this file need emdashing?
    if has_ascii_punct(root):
        entry.warning("Contains ascii puncuation, consider applying emdashar or manually fix")
    
    try:
        divtext = root.get_element_by_id('text')
    except KeyError:
        divtext = root.makeelement('div', {'id':'text'})
        divtext.extend(root.body)
        root.body.append(divtext)

    for e in root.select('#metaarea'):
        divtext.append(e)

    divtext.attrib['lang'] = lang or base_lang
    # Now do stuff.
    if needsarticle:
        if multisutta:
            raise sc.tools.webtools.ProcessingError("Multiple Suttas per file not implemented yet, sorry.")
        else:
            try:
                section = root.select('section')[0]
            except IndexError:
                section = root.makeelement('section', {'class':'sutta'})
            article = root.makeelement('article')
            # Move everything inside divtext into the article
            article.extend(divtext)
            divtext.append(section)
            section.append(article)
            section.attrib['id'] = uid

    try:
        toc = root.get_element_by_id('toc')
    except KeyError:
        toc = root.makeelement('div', {'id':'toc'})
        divtext.insert(0, toc)

    if h1notinhgroup:
        for h1 in root.iter('h1'):
            hgroup = root.makeelement('hgroup')
            h1.addnext(hgroup)
            hgroup.append(h1)
    if supplied_misused:
        for h in root.select('h1,h2,h3,h4,h5,h6,h7'):
            if 'class' in h.attrib and 'supplied' in h.attrib['class']:
                if h.attrib['class'] == 'supplied':
                    del h.attrib['class']
                else:
                    h.attrib['class'] = regex.sub('supplied,?', '', h.attrib['class'])
                span = root.makeelement('span', {'class':'add'})
                span.text = h.text; h.text = None
                for child in h:
                    span.append(child)
                h.append(span)
                
    if scnumbers_misplaced:
        for a in scn:
            p = a.getparent()
            a.tail = p.text
            p.text = None
        for a in root.select('#metaarea p a.sc'):
            a.drop_tree()

    used_ids = set()
    
    if scnumbers_insane or not pnumbers or options.get('force_sc_nums'):
        for a in root.select('a.sc'):
            a.drop_tree()
        for section in root.select('section.sutta'):
            pcount = itertools.count(1)
            uid = section.attrib['id']
            assert uid[0].isalpha()
            for p in section.select('p'):
                if len(p.text_content()) > 50:
                    id = str(next(pcount))
                    used_ids.add(id)
                    a = p.makeelement('a', {'class':'sc', 'id':id})
                    a.tail = p.text
                    p.text = None
                    p.insert(0, a)

    if pnumbers_need_id:
        c = collections.Counter(used_ids)
        for i, e in enumerate(root.select(all_ids)):
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
        # We have JavaScript menu generation.
        pass
        #try:
            #menu_list = []
            #if not multisutta:
                #headings = root.select('h2, h3, h4, h5, h6')
                #hcount = itertools.count(1)
                #for h in headings:

                    #if list(h.iterancestors('hgroup')):
                        #continue # skip initial heading.
                    ##try:
                        ##if h.getnext().tag in 'h2, h3, h4, h5, h6':
                            ##continue # Skip all but last heading in group
                    ##except AttributeError:
                        ##continue
                    #id = 'm{}'.format(next(hcount))
                    ## Wrangle the heading.
                    #a = copy(h)
                    #a.tag = 'a'
                    #a.attrib.update({'href':'#toc', 'id':id})
                    #h.clear()
                    #h.append(a)

                    ## Create the menu item
                    #li = '<li><a href="#{}">{}</a></li>'.format(id, h.text_content())
                    #depth = int(h.tag[1])
                    #menu_list.append( (depth, li) )
                #max_d = max(t[0] for t in menu_list)
                #min_d = min(t[0] for t in menu_list)
                #menu_list = [ (1 + t[0] - min_d, t[1]) for t in menu_list]

                ## Build the menu
                #menu = root.makeelement('div', {'id':'menu'})
                #ul = root.makeelement('ul')
                #menu.append(ul)
                #last_d = 1
                #last_e = ul
                #for depth, li in menu_list:
                    ## Create a new ul if the menu is getting deeper.
                    #while depth > last_d:
                        #ul = root.makeelement('ul')
                        #last_e[-1].append(ul)
                        #last_e = ul
                        #last_d += 1
                    #while depth < last_d:
                        #last_e = last_e.getparent().getparent()
                        #last_d -= 1
                    #last_e.append(lxml.html.fromstring(li))
                #toc.insert(0, menu)
        #except (AttributeError, IndexError):
            #menu = '<ul>{}</ul>'.format("\n".join(t[1] for t in menu_list))
            #toc.insert(0, lxml.html.fragment_fromstring(menu))
            
    if not hasmeta:
        if metadata is not None:
            divtext.append(copy(metadata))
    