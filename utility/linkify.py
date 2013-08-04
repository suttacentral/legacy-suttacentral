#!/usr/bin/env python

import sys, lxml.html, os, regex, collections, gzip

from os.path import dirname, join, realpath
import sys

sys.path.insert(1, join(dirname(dirname(realpath(__file__))), 'python'))

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

textroot = config['app']['text_root']

for dirpath, dirnames, filenames in os.walk(textroot):
    lang = os.path.basename(dirpath)
    for filename in filenames:
        if not filename.endswith('.html'):
            continue
        #dom = lxml.html.fromstring(open(filename).read())
        fileuid = filename.replace('.html', '')
        print (dirpath, fileuid)
        try:
            prefix, start, end = regex.match(r'(sa-[23]\.|\p{alpha}+(?:\d+\.)?)(\d+)-?(\d*)', fileuid)[1:]
        except TypeError:
            print("FAIL!")
            continue
        start = int(start)
        if end:
            end = int(end)
        else:
            end = start
        for i in range(start, end + 1):
            mapping[(lang, prefix + str(i))] = (lang, fileuid)

files = os.walk(textroot)
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
        #print("{} not found ({})".format((lang,uid), base_uid))

    for rlang in langs:
        if lang == rlang:
            continue
        try:
            target = mapping[(rlang, base_uid)]
        except KeyError:
            continue
        print("Translation for {} in {}.".format(uid, rlang))
        href = '/{}/{}/'.format(target[1], target[0])
        brief = ''
        type_id = 1
        lang_id = ref_lang[rlang]
        entries.append(make_ref_sql(id, href, brief, lang_id))
        destroy_ids[lang_id].add(id)

destroyers = []

for lang_id, sutta_ids in destroy_ids.items():
    if len(sutta_ids) == 1:
        sutta_ids = list(sutta_ids) * 2
    destroyers.append('''
DELETE FROM reference WHERE sutta_id IN {} AND reference_language_id={} AND reference_url_link LIKE '/%';'''.format(tuple(sorted(sutta_ids)), lang_id))
    
sql_f = gzip.open('auto_urls.sql.gz', 'wb')
sql_f.write('\n'.join(destroyers + entries).encode(encoding='utf-8'))

    