#!/usr/bin/env python

import sys, lxml.html, os, regex

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

def make_insert_sql(id, uid, href, brief):
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    return clean("""
        INSERT INTO reference
          (sutta_id, reference_type_id, reference_language_id,
           reference_seq_nbr, abstract_text, reference_url_link,
           update_login_id, update_timestamp)
        VALUES
          ({id}, 1, 1, 1, '{brief}', '{href}', 'admin', '{time}')
        ;
    """).format(id=id, uid=uid, time=now, href=href, brief=brief) + "\n"

db = mysql.connector.connect(**config.mysql)
sql_f = open('translations.sql', 'w', encoding='utf-8')

files = sys.argv[1:]
if not files:
    print("This utility requires a list of files to produce database entries for.")

entries = []

for filename in files:
    text = open(filename, encoding='utf-8').read()
    lang, fileuid = regex.match(r'.*/(.*)/(.*)\.html', filename)[1:]

    uids = [uid for uid in regex.findall(r'<section[^>]+id="([^"]+)"', text) if uid not in ('vagga',)]

    if not uids:
        uids = [fileuid]
    dom = lxml.html.fromstring(text)

    metaarea = dom.get_element_by_id('metaarea')

    if metaarea is not None:
        meta = metaarea.text_content()
        brief = regex.match(r'[^.]+\.', meta)[0].strip()
    else:
        print("No metadata for {} :(".format(filename))
        metaarea = None

    if len(uids) <= 1:
        entries.extend( (uid, "/{}/{}".format(fileuid, lang), brief) for uid in uids)
    else:
        entries.extend( (uid, "/{}/{}/#{}".format(fileuid, lang, uid), brief) for uid in uids)

ids = []
for uid, href, brief in entries:
    try:
        id = get_sutta_id(uid)
        ids.append(id)
        sql_f.write(make_insert_sql(id, uid, href, brief))
    except TypeError:
        print("No database entry found for uid {}".format(uid))

ids = tuple(ids)

open('destroy_old_translations.sql', 'w').write('''
DELETE FROM reference WHERE sutta_id IN {} AND reference_language_id=1 AND reference_url_link LIKE '/%';'''.format(ids))



    