import sys
sys.path.insert(0, '../..')

import regex


import json

from collections import OrderedDict

from sc.classes import *

import pathlib

import sc.scimm
imm = sc.scimm.imm()

base_types = (str, int, float, bool, type(None))

keywords={'name', 'uid', 'type', 'volpage', 'alt_volpage',
              'alt_acronym', 'biblio_entry', 'text_ref', 'url', 'abstract',
              'lang', 'translations', 'order', 'sect', 'pitika', 'text'}

def add_properties(to, obj, *attrs):
    for attr in attrs:
        value = getattr(obj, attr, None)
        if value:
            if isinstance(value, base_types):
                to[attr] = value
            else:
                to[attr] = to_json(value)
    type_name = type(obj).__name__.lower()
    if type_name != 'sutta':
        to['type'] = type_name

def add_children(to, children):
    
    if isinstance(children, dict):
        children = children.values()

    order = []
    for child in children:
        to[child.uid] = to_json(child)
        order.append(child.uid)
    if order:
        if all(regex.search('[0-9]', uid) for uid in order):
            # We don't need order if there are numbers in the uids
            pass
        else:
            to['order'] = order


def sect_to_json(sect):
    return sect.uid

def pitika_to_json(pitika):
    return pitika.uid

def biblio_entry_to_json(biblio_entry):
    return biblio_entry._asdict()

def language_to_json(language):
    out = OrderedDict()

    add_properties(out, language, 'name')
    add_children(out, language.collections)
    return out

def collection_to_json(collection):
    out = OrderedDict()
    add_properties(out, collection, 'name', 'pitika', 'sect')
    add_children(out, collection.divisions)
    return out

def division_to_json(division):
    out = OrderedDict()
    add_properties(out, division, 'uid', 'name')
    if len(division.subdivisions) == 1 and division.subdivisions[0].uid == division.uid:
        subout = subdivision_to_json(division.subdivisions[0])
        for k, v in subout.items():
            if k not in keywords:
                out[k] = v
    else:
        add_children(out, division.subdivisions)
    return out

def subdivision_to_json(subdivision):
    out = OrderedDict()
    add_properties(out, subdivision, 'uid', 'name')
    if len(subdivision.vaggas) == 1 and not subdivision.vaggas[0].name:
        add_children(out, subdivision.suttas)
    else:
        for vagga in subdivision.vaggas:
            vagga_uid = '{}-vagga-{}'.format(vagga.subdivision.uid,
                                      vagga.number)
            out[vagga_uid] = to_json(vagga)
            
    return out

def vagga_to_json(vagga):
    out = OrderedDict()
    add_properties(out, vagga, 'name')
    add_children(out, vagga.suttas)
    
    return out

def sutta_to_json(sutta):
    out = OrderedDict()
    add_properties(out, sutta, 'name', 'alt_acronym',
                    'biblio_entry', 'volpage')
    textinfo = imm.tim.get(lang_uid=sutta.lang.uid, uid=sutta.uid)
    if textinfo and 'volpage' in out:
        if textinfo.volpage == out.get('volpage'):
            del out['volpage']
    if sutta.alt_volpage_info:
        out['alt_volpage'] = sutta.alt_volpage_info
    return out

def grouped_sutta_to_json(sutta):
    out = OrderedDict()
    add_properties(out, sutta, 'name', 'alt_acronym',
                    'biblio_entry', 'volpage')
    if sutta.alt_volpage_info:
        out['alt_volpage'] = sutta.alt_volpage_info

    if sutta.text_ref and sutta.text_ref.url.startswith('http://'):
        out['text_ref'] = to_json(sutta.text_ref)
    translations = []
    for textref in sutta.translations:
        if textref.url.startswith('http://'):
            translations.append(to_json(textref))
    if translations:
        out['translations'] = translations
    return out

def textref_to_json(textref):
    return None
    out = OrderedDict()
    out['lang'] = textref.lang.uid
    add_properties(out, textref, 'name', 'url', 'abstract')
    return out

to_json_fns = {
    Language: language_to_json,
    Collection: collection_to_json,
    Division: division_to_json,
    Subdivision: subdivision_to_json,
    Vagga: vagga_to_json,
    Sutta: sutta_to_json,
    GroupedSutta: grouped_sutta_to_json,
    TextRef: textref_to_json,
    Sect: sect_to_json,
    Pitaka: pitika_to_json,
    BiblioEntry: biblio_entry_to_json
}


def to_json(obj):
    return to_json_fns[type(obj)](obj)
    


out = OrderedDict()

languages = [l for l in imm.languages.values() if l.isroot]
languages.sort()
languages.sort(key=lambda l: -1 if l.uid == 'pi' else l.priority)
add_children(out, languages)



def scan(tree):
    
    seen = {}
    def inner_scan(subtree, _stack=[]):
        for key, value in subtree.items():
            if key not in keywords:
                if key in seen:
                    print('Oops! {} already seen! {} / {}'.format(key, seen[key], _stack))
                seen[key] = list(_stack)
            if isinstance(value, list):
                for value in value:
                    if isinstance(value, dict):
                        inner_scan(value, _stack=_stack + [key])
            elif isinstance(value, dict):
                inner_scan(value, _stack=_stack + [key])
    inner_scan(tree, _stack=['root'])


scan(out)

def redict(tree):
    if isinstance(tree, dict):
        return {key: redict(value) for key, value in tree.items()}
    elif isinstance(tree, list):
        return [redict(value) for value in tree]
    return tree

with open('root.json', 'w') as f:
    f.write(json.dumps(out, ensure_ascii=0, indent=4))


import pickle
with open('root.pickle', 'wb') as f:
    pickle.dump(out, f)

base_dir = pathlib.Path('sectioned')

def section_json(obj, depth, stack=None):
    target_file = pathlib.Path(base_dir, *stack)
    if not target_file.parent.exists():
        target_file.parent.mkdir(parents=True)
    if depth == 0:
        with target_file.with_suffix('.json').open('w') as f:
            json.dump(obj, f, ensure_ascii=0, indent=4)
    else:
        properties = {k: v for k, v in obj.items() if k in keywords}
        children = {k: v for k, v in obj.items() if k not in keywords}
        if properties:
            with target_file.with_suffix('.json').open('w') as f:
                json.dump(properties, f, ensure_ascii=0, indent=4)
        if children:
            for key, value in children.items():
                section_json(value, depth - 1, stack + [key])

section_json(obj=out, depth=3, stack=['root'])
    
    

## Sanitize
#bad = []
#for d in list(root.iter('division')):
    #if len(d.attrib) == 1 or d.get('uid', False) == d.getparent().get('uid', True):
        #if len(d.getparent()) == 1:
            #d.tag = 'OMGKILLME'

#for d in root.iter('textref'):
    #if d.get('url').startswith('/'):
        #d.tag = 'OMGKILLME'

#etree.strip_tags(root, 'OMGKILLME')


## Rearrange
#canon = root.find('pitakas')
#canon.tag = 'canon'

#for pitaka in canon:
    #pitaka.extend(root.findall('*//collection[@pitaka="{}"]'.format(pitaka.get('uid'))))
#root.append(canon)
#languages = {}
#sects = {}
#for collection in root.iter('collection'):
    ## We need to create language elements inside the pitakas
    #lang_uid = collection.get('lang')
    #pitaka_uid = collection.get('pitaka')
    #sect_uid = collection.get('sect')

    #pitaka = canon.find('pitaka[@uid="{}"]'.format(pitaka_uid))

    #language = languages.get((pitaka_uid, lang_uid))
    #if language is None:
        #languages[(pitaka_uid, lang_uid)] = language = SubElement(pitaka, 'language', uid=lang_uid)

    #sect = sects.get((pitaka_uid, lang_uid, sect_uid))
    #if sect is None:
        #sects[(pitaka_uid, lang_uid, sect_uid)] = sect = SubElement(language, 'sect')
        #if sect_uid:
            #sect.set('uid', sect_uid)
    #sect.append(collection)


#etree.strip_tags(root, 'collection', 'collections')

    
#to_utf8_file(root, str(outdir / 'all.json'))

## Now break it up!
#for division in root.findall('*//sect/division'):
    #uid = division.get('uid')
    #divfile = outdir / (uid + '.json')
    #include = etree.Element('include')
    #include.extend(division)
    #to_utf8_file(include, str(divfile))
    #division.append(etree.Element(XI + 'include', href=uid+'.json'))
    ##division.getparent().remove(division)

#to_utf8_file(root, str(outdir / 'root.json'))

## (lang, uid, path, bookmark, name, author, volpage)

## Now generate external textual references
#textrefs = etree.Element('textrefs')
#findnums = regex.compile(r'\d+(\.\d+)?(-\d+)?').findall

#for sutta in imm.suttas.values():
    #e = textrefs.makeelement('textref', sutta=sutta.uid)
    #if sutta.text_ref and not sutta.text_ref.url.startswith('/'):
        #tr = sutta.text_ref
        #SubElement(e, 'extref', lang=sutta.lang.uid, url=tr.url, abstract=tr.abstract)
    #if sutta.volpage:
        #by_tim = imm.tim.get(sutta.uid, sutta.lang.uid)
        #if not by_tim or not by_tim.volpage or findnums(by_tim.volpage) != findnums(sutta.volpage):
            #SubElement(e, 'volpage', lang=sutta.lang.uid, value=sutta.volpage)
        #if sutta.alt_volpage_info:
            #if not by_tim or not by_tim.volpage or findnums(by_tim.volpage) != findnums(sutta.alt_volpage_info):
                #SubElement(e, 'volpage', lang=sutta.lang.uid, value=sutta.alt_volpage_info)
    #if len(e):
        #textrefs.append(e)

#to_utf8_file(textrefs, str(outdir / 'textrefs.json'))
