#!/usr/bin/env python

from os.path import dirname, join, realpath
import sys

sys.path.insert(1, join(dirname(dirname(dirname(realpath(__file__)))), 'src'))

import glob, jinja2, mysql.connector, os, regex, textwrap, time
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

def get_title(html):
    title = regex.findall(r'<h1>(.+)</h1>', html)[0]
    return regex.sub(r'<[^>]+>', '', title)

def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def get_sutta_html(path):
    html = read(f)
    return regex.sub(r'</?(body|html)>', '', html).strip()

def get_meta_html():
    html = read('in/Dhp/DhammapadaEnglishMetadata.txt')
    return '<div id="metaarea">\n' + html + '</div>\n'

def get_template():
    loader = jinja2.PackageLoader('conv', '.')
    env = jinja2.Environment(loader=loader)
    return env.get_template('template.html')

def each_input_file():
    for f in glob.glob('in/Dhp/dhp*.html'):
        yield f

def make_insert_sql(id, uid):
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    return clean("""
        INSERT INTO reference
          (sutta_id, reference_type_id, reference_language_id,
           reference_seq_nbr, abstract_text, reference_url_link,
           update_login_id, update_timestamp)
        VALUES
          ({id}, 1, 1,
           1, 'English translation of {uid} by Ācāriya Buddharakkhita', '/{uid}/en',
           'admin', '{time}')
        ;
    """).format(id=id, uid=uid, time=now) + "\n"

if __name__ == '__main__':

    db = mysql.connector.connect(**config.mysql)
    template = get_template()
    meta_html = get_meta_html()
    try:
        os.mkdir('out')
    except OSError:
        pass
    sql_f = open('out/dhammapada.sql', 'w', encoding='utf-8')

    for f in each_input_file():
        sutta_html = get_sutta_html(f)
        title = get_title(sutta_html)
        uid = regex.match('^.*(dhp.*)\.html$', f)[1]
        id = get_sutta_id(uid)

        out_file = 'out/{}.html'.format(uid)
        html = template.render(title=title,
            sutta_html=sutta_html, meta_html=meta_html)
        open(out_file, 'w', encoding='utf-8').write(html)

        sql_f.write(make_insert_sql(id, uid))
