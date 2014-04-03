import sys, regex, os, shutil, collections, itertools
import pathlib
from copy import copy

import sc, sc.scimm, sc.util

def normalize_anchor(string):
    string = regex.sub(r'(?<=\d) (?=\d)', '.', string)
    string = regex.sub(r'(?<=\p{alpha}) (?=\p{alpha})', '_', string)
    string = regex.sub(r'(\p{lower})(\p{upper})', r'\1_\2', string)
    string = string.casefold()
    return string

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
    metaarea = root.select_one('div#metaarea')
    if metaarea:
        return metaarea
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

def discover_author(root, entry, num_in_file):
    author = root.select_one('meta[author]')
    if not author:
        author = root.select_one('meta[data-author]')
        if author:
            author.attrib['author'] = author.attrib['data-author']
            del author.attrib['data-author']
    if author:
        return author
    
    metaarea = root.select_one('div#metaarea')
    if metaarea:
        metatext = metaarea.text_content()
        transby = None
        m = regex.search('Transl(?:ated|ion) (?:by|from) ((?:(?<!\p{alpha})\p{alpha}\.\s|[^.:,])+(?: and ((?:(?<!\p{alpha})\p{alpha}\.\s|[^.:,])+)))', metatext)
        if m:
            transby = m[0]
        else:
            # Match two words at front if possible commas are allowed, after that
            # match everything up to the first sentence ender, but permit periods
            # as abbreviation indicators.
            m = regex.match(r'(?:\p{alpha}+,? \p{alpha}+,?\s)?(?:(?<!\p{alpha})(?:\bed|\b\p{alpha})\.\s*|[^.:,])+', metatext)
            if m:
                transby = m[0]
            if transby:
                if num_in_file <= 0:
                    entry.warning('No explicit author/origin blurb provided, using "{}", if this is not sensible, please add an element \'<meta author="Translated by So-and-so">\' to the metadata'.format(transby))
                return root.makeelement('meta', author=transby)
    if num_in_file <= 0:
        entry.error('Could not determine author(translator/editor) blurb, please add an element \'<meta author="Translated by So-and-so">\' to the metadata')
    return None
    
def normalize_id(string):
    # Remove spaces between alpha char and digit
    string = regex.sub(r'(?<=\p{alpha})\s+(?=\d)', '', string)
    # Replace space between alpha with hyphen
    string = regex.sub(r'(?<=\p{alpha})\s+(?=\p{alpha})', '-', string)
    # Replace space between digits with period
    string = regex.sub(r'(?<=\d)\s+(?=\d)', '.', string)
    
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

def inspect_for_rubbish(root, entry):
    # Examine for over-nesting
    pes = []
    for p in root.select('p'):
        if p.getparent().attrib.get('id') == 'metaarea':
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

def discover_language(root, entry):
    imm = sc.scimm.imm()
    language = None
    if entry.filename:
        for part in entry.filename.parts:
            language = imm.languages.get(part)
            if language:
                break
    
    element = root.select_one('div[lang], section[lang], article[lang]')
    if element:
        lang_iso_code = element.attrib['lang']
        langs = imm.isocode_to_language.get(lang_iso_code, [])
        if len(langs) == 1 and not language:
            language = langs[0]
        elif len(langs) > 1 and not language:
            possibilities = ", ".join("{}/{}".format(l.uid, l.name) for l in langs)
            entry.error("Ambigious language, could be ({}), please implicitly specify language uid by enclosing in a sub folder i.e. zh/filename.html".format(possibilities))
            return
        elif language and language.iso_code != lang_iso_code:
            entry.error("Language mismatch, according to path structure language is {}, but according to lang tag language is {}".format(language.iso_code, lang_iso_code))
            return
    else:
        # Language does not exist.
        if language:
            lang_iso_code = language.iso_code
        else:
            entry.error('No language uid found. Please enclose file(s) in a subfolder en/filename.html')
            return
    
    if not language:
        if entry.filename:
            possible_code = entry.filename.parts[0]
            if 2 <= len(possible_code) <= 3:
                entry.error("Language could not be determined. If '{}' is a new language, it will need to be added to the database.".format(possible_code))
                return
        entry.error("Language could not be determined.")
    
    return language

def generate_canonical_path(uid, language):
    imm = sc.scimm.imm()
    
    if isinstance(language, str):
        language = imm.languages[language]
    
    path = pathlib.Path(language.uid)
    
    subdivision = imm.subdivisions.get(uid)
    if not subdivision:
        sutta = imm.suttas.get(uid)
        if sutta:
            subdivision = sutta.subdivision

    
    division = imm.divisions.get(uid)
    
    if not (subdivision or division):
        m = regex.match(r'(.*?)\.?\d+(?:-\d+)?$', uid)
        if m:
            subdivision = imm.subdivisions.get(m[1])
    
    if subdivision:
        division = subdivision.division
    
    if division:
        collection = division.collection
    else:
        return path
    
    if collection.pitaka.uid != 'su':
        path /= collection.pitaka.uid
    
    if language != collection.lang:
        path /= pathlib.Path(collection.lang.uid)
    m = regex.match(r'.*\.(.*)', collection.uid)
    if m:
        path /= m[1]

    if division.uid != uid:
        path /= division.uid
    
    if subdivision and uid != subdivision.uid != None:
        if division.collection.pitaka == 'su':
            path /= subdivision.uid
    
    return path

def discover_uid(root, entry):
    section = root.select_one('section[id]')
    if section:
        uid = section.attrib['id']
        if not regex.fullmatch(r'\P{alpha}+', uid):
            entry._lineno = section.sourceline
            return uid
    hgroup = root.select_one('hgroup[id]')
    if hgroup:
        uid = hgroup.attrib['id']
        if not regex.fullmatch(r'\P{alpha}+', uid):
            entry._lineno = hgroup.sourceline
            return uid
    return None

def generate_next_prev_links(root, language):
    # Note there is a fallback next/prev link generator
    # applied at time of serving a file.
    # This assumes the order in the file provides a betterer
    # indication of relationships than the automated generator
    # can determine.
    if isinstance(language, str):
        lang_uid = language
    else:
        lang_uid = language.uid
    sections = root.select('section.sutta')
    if len(sections) <= 1:
        return
    imm = sc.scimm.imm()
    def get_text(uid):
        sutta = imm.suttas.get(uid)
        if sutta:
            if hasattr(sutta, 'brief_name'):
                text = sutta.brief_name
            else:
                text = sutta.name
        else:
            text = imm.uid_to_acro(uid)
        return text
    link_count = 0
    for i, section in enumerate(sections):
        links = []
        if section != sections[0]:
            # Prev link
            prev_uid = sections[i - 1].attrib['id']
            href = sc.classes.Sutta.canon_url(uid=prev_uid,
                                              lang_code=lang_uid)
            prev = root.makeelement('a', {'href':href, 'class':'previous'})
            prev.text = '◀ {}'.format(get_text(prev_uid))
            links.append(prev)
        # Top link
        top = root.makeelement('a', {'class':'top', 'href':'#'})
        top.text = ' ▲ TOP '
        links.append(top)
        if section != sections[-1]:
            # Next link
            next_uid = sections[i + 1].attrib['id']
            href = sc.classes.Sutta.canon_url(uid=next_uid,
                                              lang_code=language)
            prev = root.makeelement('a', {'href':href, 'class':'next'})
            prev.text = '{} ▶'.format(get_text(next_uid))
            links.append(prev)
        section.extend(links)
        link_count += len(links) - 1
    return link_count

def finalize(root, entry, language=None, metadata=None, 
             num_in_file=-1, options={}):
    if root.tag != 'html':
        raise ValueError('Root element should be <html> not <{}>'.format(root.tag))
    pnums = set()
    filename = entry.filename
    tag_data = get_tag_data()
    
    imm = sc.scimm.imm()
    
    if not language:
        language = discover_language(root, entry if num_in_file == -1 else 
            sc.tools.webtools.Report.Entry())
    
    multisutta = len(root.select('article, h1')) > 2
    
    if metadata:
        # Allow specific metadata.
        metadata = root.select_one('#metaarea') or metadata
    else:
        metadata = root.select_one('#metaarea')
        if not metadata and num_in_file <= 0:
            entry.error('No metadata found. Metadata should either be in a \
        <div id="metaarea"> tag, or a seperate file "meta.html".')
    
    if metadata:
        root.body.append(metadata)
    
    uid1 = discover_uid(root, entry)
    uid2 = pathlib.Path(entry.filename).stem
    
    inspect_for_rubbish(root, entry)
    
    if len(root.select('section')) > 1:
        raise ValueError('Should not be called with multiple sections')
    
    if language:
        language_name = language.name
    else:
        language_name = 'Unknown'
    
    def uid_makes_sense(uid):
        if not uid:
            return False
        for ipass in range(0, 2):
            if ipass == 1:
                # Try pruning the end off the uid.
                m = regex.match(r'(.*?)\.?\d+[a-z]?(?:-\d+[a-z]?)?$', uid)
                if m:
                    uid = m[1]
            
            if uid in imm.suttas:
                return "Looks like sutta text {0.acronym}: {0.name} ({1})".format(imm.suttas[uid], language_name)
                
            
            elif uid in imm.divisions:
                return "Looks like belongs to division {0.uid}: {0.name} ({1})".format(imm.divisions[uid], language_name)
                
                
            elif uid in imm.subdivisions:
                return "Looks like belongs to subdivision {0.uid}: {0.name} ({1})".format(imm.subdivisions[uid], language_name)
            
        return False
    
    uid1_sense = uid_makes_sense(uid1)
    uid2_sense = uid_makes_sense(uid2)
    if uid1_sense and (not uid2_sense or uid1.startswith(uid2)):
        entry.info(uid1_sense)
        uid = uid1
    elif uid2_sense and not uid1_sense:
        entry.info(uid2_sense)
        uid = uid2
    elif uid1_sense and uid2_sense:
        entry.warning(uid1_sense)
        entry.warning('(also) ' + uid2_sense)
        if len(uid1) > len(uid2):
            uid = uid1
        else:
            uid = uid2
        entry.warning('Using {}'.format(uid))
    if not uid1_sense and not uid2_sense:
        if uid1 == uid2:
            entry.error('{} not recognized as a valid uid, a database entry may be required'.format(uid1))
            uid = uid1
        else:
            entry.error('{} or {} not recognized as valid uids, a database entry may be required'.format(uid1, uid2))
            uid = uid1
    else:
        entry.info('uid looks like {}'.format(uid))
    
    #Convert non-HTML tags to classes
    normalize_tags(root, entry)
    
    all_ids = ','.join(tag_data['pnum_classes'].keys())
    for e in root.select(all_ids):
        if 'id' not in e.attrib:
            pnumbers_need_id = True
            break
    items = []

    # Does this file need emdashing?
    if has_ascii_punct(root):
        entry.warning("Contains ascii puncuation, consider applying emdashar or manually fix")
    
    # tear down
    for e in root.select('div#text, section, article'):
        e.drop_tag()
        
    # rebuild document structure
    article = root.makeelement('article')
    section = root.makeelement('section', 
                                {'class':'sutta', 'id': uid})
    divtext = root.makeelement('div', id="text")
    
    for e in root.select('hgroup'):
        if 'id' in e.attrib:
            del e.attrib['id']
    
    if language:
        divtext.attrib['lang'] = language.iso_code
    
    article.extend(root.body)
    root.body.append(divtext)
    divtext.append(section)
    section.append(article)
    
    try:
        toc = root.get_element_by_id('toc')
    except KeyError:
        toc = root.makeelement('div', {'id':'toc'})
    
    divtext.insert(0, toc)

    # Convert old-style hgroups
    for hgroup in root.iter('hgroup'):
        hgroup.tag = 'div'
        hgroup.add_class('hgroup')
        if hgroup[0].tag != 'h1':
            hgroup[0].tag = 'p'
            hgroup[0].attrib['class'] = 'division'

        for e in hgroup.select('h4'):
            e.tag = 'p'
            
        for e in hgroup[1:-1]:
            if e.tag not in {'h2','h3','h4','h5','h6', 'p'}:
                continue
            e.tag = 'p'
        del hgroup
    
    h1notinhgroup = False
    for h1 in root.iter('h1'):
        if 'hgroup' not in h1.getparent().get('class', ''):
            h1notinhgroup = True

    if h1notinhgroup:
        entry.error('<h1> not in hgroup, please enclose the <h1> in a <div class="hgroup>, the division or subdivision heading should be <p class="division">, other subheadings (such as chapters) should be simple <p> but included inside the hgroup.')

    for e in root.select('.hgroup > h2:last-child'):
        e.getparent().addnext(e)

    for e in root.select('.hgroup > *'):
        if e.tag not in {'h1', 'p'}:
            entry.warning('Inappropriate tag in div.hgroup: <{}>. Only <h1> and <p> are permissible.'.format(e.tag))
    
    supplied_misused = False
    for h in root.select('h1,h2,h3,h4,h5,h6,h7'):
        if 'class' in h.attrib and 'supplied' in h.attrib['class']:
            supplied_misused = True
    if supplied_misused:
        for h in root.select('h1,h2,h3,h4,h5,h6,h7'):
            if 'supplied' in h.attrib.get('class',''):
                if h.attrib['class'] == 'supplied':
                    del h.attrib['class']
                else:
                    h.attrib['class'] = regex.sub(r'supplied\s*,?', '', h.attrib['class']).strip()
                span = root.makeelement('span', {'class':'add'})
                span.text = h.text; h.text = None
                for child in h:
                    span.append(child)
                h.append(span)
    
    for e in root.select('#metaarea'):
        e.drop_tree()
        e.tail = '\n'
    
    if metadata:
        section.append(metadata)

    scn_problem = False
    scn = root.select('a.sc')
    if root.select('meta a.sc'):
        scn_problem = True

    used_ids = collections.Counter()

    if not scn or scn_problem or options.get('force-sc-nums'):
        for e in scn:
            e.drop_tree()
        sections = root.select('section.sutta')
        if len(sections) > 1:
            comprefix = os.path.commonprefix(s.attrib['id'] for s in sections)

        for section in sections:
            if len(sections) == 1:
                base_uid = ''
            else:
                base_uid = section.attrib['id'][len(comprefix):]
                if base_uid[-1].isdigit():
                    base_uid += '.'
            pnum = 0

            for p in section.select('article p'):
                if len(p.text_content()) > 50:
                    pnum += 1
                    
                    id = base_uid + str(pnum)
                    if id in used_ids:
                        id += '_' + str(used_ids[id] + 1)
                    used_ids.update([id])
                    a = p.makeelement('a', {'class':'sc', 'id':id})
                    p.prepend(a)

    for i, e in enumerate(root.select(all_ids)):
        if e.text and not e.text.isspace():
            if e.attrib['id'] == 'sc':
                id = normalize_anchor(e.text)
            else:
                id = normalize_anchor(e.attrib['class'] + ' ' + e.text)
            e.attrib['id'] = id
            e.text = None

    # Merge blockquotes
    blockquotes = root.select('blockquote')
    if blockquotes:
        e = blockquotes[0]
        i = 1
        while i < len(blockquotes):
            if e.tail and not e.tail.isspace():
                continue
            nextbq = e.getnext()
            if nextbq == blockquotes[i]:
                e.append(nextbq)
                nextbq.drop_tag()
            else:
                e = blockquotes[i]

            i += 1
                
                
                
    
        
        
        
        

    for e in root.select('a.previous, a.top, a.next'):
        divtext.append(e)
    
    author_blurb = discover_author(root, entry, num_in_file)
    
    if author_blurb:
        root.headsure.append(author_blurb)
    
    
