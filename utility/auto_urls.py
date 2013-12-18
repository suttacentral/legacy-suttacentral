#!/usr/bin/env python

import env
import sys, lxml.html, os, regex, collections, gzip

from os.path import dirname, join, realpath
import sys
import glob, mysql.connector, os, regex, textwrap, time
import config

def clean(str):
    return textwrap.dedent(str).strip()

def get_sutta_id(uid):
    global db
    cursor = db.cursor()
    cursor.execute("""
        SELECT sutta_id FROM sutta WHERE sutta_uid = '%s';
    """ % uid)
    
    return cursor.fetchone()[0]

def make_ref_sql(id, href, brief, lang_id):
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    return clean("""
        INSERT INTO reference
          (sutta_id, reference_type_id, reference_language_id,
           reference_seq_nbr, abstract_text, reference_url_link,
           update_login_id, update_timestamp)
        VALUES
          ({id}, 1, {lang_id}, 1, '{brief}', '{href}', 'auto', '{time}')
        ;
    """).format(id=id, time=now, href=href, brief=brief, lang_id=lang_id) + "\n"

def make_url_sql(id, href, info=""):
    return """
UPDATE sutta SET sutta_text_url_link = '{}', url_extra_info_text= '{}'
WHERE sutta_id = '{}';""".format(href, info, id)

db = mysql.connector.connect(**config.mysql)


entries = []

mapping = {}
transby = {}

textroot = config.text_dir

def dedup(item):
    out = []
    for i in item:
        if i not in out:
            out.append(i)
    return out
            
embedded_parallels = {}

for dirpath, dirnames, filenames in os.walk(textroot):
    lang = os.path.basename(dirpath)
    for filename in filenames:
        if not filename.endswith('.html'):
            continue
        fileuid = filename.replace('.html', '')
        try:
            prefix, start, end = regex.match(r'(sa-[23]\.|\p{alpha}+(?:\d+\.)?)(\d+)-?(\d*)', fileuid)[1:]
        except TypeError:
            print("Uid form not recognized: " + filename)
            continue
        if end:
            start = int(start)
            for i in range(start, int(end) + 1):
                mapping[(lang, prefix + str(i))] = (lang, fileuid)
        else:
            mapping[(lang, prefix + start)] = (lang, fileuid)

        text = open(os.path.join(dirpath, filename), encoding='utf8').read()

        # Discover embedded parallels
        for m in regex.finditer(r'<div[^>]+embeddedparallel[^>]+>', text):
            frag = lxml.html.fragment_fromstring(m[0])
            uid = frag.attrib['data-uid'];
            bookmark = frag.attrib['id'];
            embedded_parallels[(lang, uid)] = (fileuid, bookmark)
        
        m = dedup(regex.findall(r'<span class="author">([^>]+)</span>', text))
        if m:
            if lang == 'en':
                transby[(lang, fileuid)] = "Translated by: {}.".format(", ".join(m))
            else:
                #Localize!
                transby[(lang, fileuid)] = "Translated by: {}.".format(", ".join(m))
        else:
            if lang == 'vn':
                m = regex.search('Hòa thượng[^.<]+', text)
                if m:
                    transby[(lang,fileuid)] = m[0] + '.'
        
cur = db.cursor()

cur.execute('SELECT iso_code_2, reference_language_id FROM reference_language')
ref_lang = dict(cur.fetchall())
ref_lang['skt'] = ref_lang['sa']
langs = sorted(ref_lang)

destroy_ids = collections.defaultdict(set)

# Create URL's for root text
cur.execute('SELECT sutta_id, sutta_uid, language_code FROM sutta INNER JOIN collection_language USING(collection_language_id)')
for id, uid, lang in cur.fetchall():
    base_uid = regex.match(r'(?r)(.*)(-\d+)?', uid)[1]
    try:
        target = mapping[(lang, base_uid)]
        href = '/{}/{}/'.format(target[1], target[0])
        entries.append(make_url_sql(id, href))
    except KeyError:
        pass
    try:
        target = embedded_parallels[(lang, uid)]
        href = '/{}/{}/#{}'.format(target[0], lang, target[1])
        entries.append(make_url_sql(id, href))
        print(lang, uid, href)
    except KeyError:
        pass

    for rlang in langs:
        if lang == rlang:
            continue
        try:
            target = mapping[(rlang, base_uid)]
        except KeyError:
            continue
        trans = transby.get(target, None)
        href = '/{}/{}/'.format(target[1], target[0])
        type_id = 1
        lang_id = ref_lang[rlang]
        entries.append(make_ref_sql(id, href, trans, lang_id))
        destroy_ids[lang_id].add(id)

destroyers = []

for lang_id, sutta_ids in destroy_ids.items():
    if len(sutta_ids) == 1:
        sutta_ids = list(sutta_ids) * 2
    destroyers.append('''
DELETE FROM reference WHERE sutta_id IN {} AND reference_language_id={} AND reference_url_link LIKE '/%';'''.format(tuple(sorted(sutta_ids)), lang_id))
    
sql_f = gzip.open('auto_urls.sql.gz', 'wb')
sql_f.write('\n'.join(destroyers + entries).encode(encoding='utf-8'))

    