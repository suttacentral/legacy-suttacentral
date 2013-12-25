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

def get_existing_file_uids(_cache=sc.util.TimedCache(lifetime=15 * 60)):
    try:
        return _cache[0]
    except KeyError:
        pass
    
    imm = sc.scimm.imm()
    existing_file_uids = set()
    for value in imm.text_paths.values():
        existing_file_uids.update(value.keys())
    
    _cache[0] = existing_file_uids
    return existing_file_uids

def get_tag_data(_cache=sc.util.TimedCache(lifetime=15 * 60)):
    try:
        return _cache[0]
    except KeyError:
        pass
    import json
    jsonfile = sc.base_dir / 'utility' / 'tag_data.json'
    with jsonfile.open('r') as f:
        tag_data = json.load(f)
    _cache[0] = tag_data
    return tag_data

def process_metadata(root):
    metaarea = root.select('div#metaarea')
    if metaarea:
        return metaarea[0]
    pes = root.select('p')
    if pes:
        parent = pes[0].getparent()
        if parent.tag == 'blockquote':
            parent = parent.getparent()
        parent.tag = 'div'
        parent.attrib['id'] = 'metaarea'
        return parent
    if root.text and root.tag == 'div':
        root.attrib['id'] = 'metaarea'
        root.wrap_inner(root.makeelement('p'))
        return root
    raise tools.webtools.ProcessingError("Couldn't make sense of metadata")

def normalize_id(string):
    # Remove spaces between alpha char and digit
    string = regex.sub(r'(?<=\p{alpha})\s+(?=\d)', '', string)
    # Replace space between alpha with hyphen
    string = regex.sub(r'(?<=\p{alpha})\s+(?=\p{alpha})', '-', string)
    # Replace space between digits with period
    string = regex.sub(r'(?<=\d)\s+(?=\d)', '.', string)
    
    # WARNING this can still return invalid ids, need to check
    # the HTML5 standard. This is an area where not being restricted
    # to the HTML4 standard would be very ideall. From memory
    # in HTML5 is might be defined as a list of forbidden characters,
    # with unicode characters in general being okay.
    
    return string

def normalize_tags(root, entry):
    tag_data = get_tag_data()
    validtags = sc.tools.html.defs.tags
    warned = set()
    for e in root.iter():
        if not isinstance(e.tag, str):
            continue
        if e.tag not in validtags:
            if tag_data['pnum_classes'].get(e.tag):
                # Certainly a paragraph number
                
                e.attrib['class'] = e.tag
                e.tag = 'a'
                id = e.attrib.get('id')
                text = e.text
                
                if id and text:
                    if id == text:
                        e.text = None
                
                elif text:
                    e.attrib['id'] = normalize_id(text)
                    e.text = None
            else:
                tags = tag_data['by_class'].get(e.tag)
                if tags:
                    tags = sorted(tags.items(), key=lambda t: t[1], reverse=True)
                    e.attrib['class'] = e.tag
                    e.tag = tags[0][0]
                else:
                    if e.tag not in warned:
                        entry.warning("Don't know what to do with tag: {}".format(e.tag), lineno=e.sourceline)
                        warned.add(e.tag)

def inspect_classes(root, entry):
    tag_data = get_tag_data()
    warned = set()
    for e in self.iter():
        if 'class' in e.attrib:
            for class_ in e.attrib['class'].split():
                if class_ not in tag_data['by_class']:
                    if class_ not in warned:
                        entry.warning("CSS class {} not recognized, this may be an error.".format(_class), lineno=e.sourceline)
                        warned.add(class_)

    
def has_ascii_punct(root):
    badpuncts = ('"', '--', "'s")
    for e in root.iter():
        for punct in badpuncts:
            if (e.text and punct in e.text) or (e.tail and punct in e.tail):
                return (punct, e.sourceline)
            return False

def finalize(root, entry, languid=None, metadata=None, options={}):
    pnums = set()
    filename = entry.filename
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
        doclang = root.select('div[lang], section[lang], article[lang]')[0].attrib['lang']
        if not lang:
            lang = doclang
        else:
            if lang != doclang:
                entry.warning("Document language '{0}' does not match path language '{1}', defaulting to '{1}'".format(doclang, lang))
    except (IndexError, KeyError):
        if not lang:
            entry.error('No language code found. Either use <div lang="en">, or include in a subfolder en/filename.html')
            # No language is an error, but we will forge ahead!
    
    uid = pathlib.Path(entry.filename).stem
        
    imm = sc.scimm.imm()
    
    if lang in imm.languages:
        language_name = imm.languages[lang].name
    else:
        language_name = "Unknown Language"
    
    for ipass in range(0, 2):
        if ipass == 0:
            uid_ = uid
        else:
            # Try pruning the end of the uid.
            m = regex.match(r'(.*?).?\d+-\d+$', uid)
            if m:
                uid_ = m[1]
        if uid_ in imm.suttas:
            entry.info("Looks like sutta text {0.acronym}: {0.name} ({1})".format(imm.suttas[uid_], language_name))
            break
        
        elif uid_ in imm.divisions:
            entry.info("Looks like division text {0.uid}: {0.name} ({1})".format(imm.divisions[uid_], language_name))
            break
            
        elif uid_ in imm.subdivisions:
            entry.info("Looks like subdivision text {0.uid}: {0.name} ({1})".format(imm.subdivisions[uid_], language_name))
            break
    else:
        entry.warning("Don't know what {} is ({})".format(uid, 
            language_name))
        if uid not in get_existing_file_uids():
            entry.warning("It also doesn't match any existing file.")
    
    # Examine for over-nesting
    pes = []
    for p in root.select('p'):
        if p.getparent() == metadata:
            continue
        pes.append(p)
    if not pes:
        entry.warning("Document contains no paragraphs. This is okay only under exceptional circumstances. <div> tags containing text should be changed to <p>")
    else:
        midp = pes[int(len(pes)/2)]
        ancestors = [e.tag for e in midp.iterancestors()]
        anccount = len(ancestors) - 2 # html and body
        if 'article' in ancestors:
            anccount -= 1
        if 'section' in ancestors:
            anccount -= 1
        if 'div' in ancestors:
            anccount -= 1
        if 'blockquote' in ancestors:
            anccount -= 1
        if anccount > 0:
            entry.warning("Document content appears to be excessively nested, by {} levels.".format(anccount))
    
    rubbish = root.cssselect('body script, body link, body style')
    if rubbish:
        entry.warning("Document contains rubbish such as script or style tags. Has this document been cleaned up?")
    for e in rubbish:
        e.drop_tree()
    
    #Convert non-HTML tags to classes
    normalize_tags(root, entry)
    
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
    
    for e in root.select('div, article, section'):
        if 'lang' in e.attrib:
            del e.attrib['lang']
    if lang:
        divtext.attrib['lang'] = lang
        
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
        # Old code deleted because it was crappy. If we want
        # static menus, convert code from sc_formatter.js
        pass
            
    if not hasmeta:
        if metadata is not None:
            divtext.append(copy(metadata))
    