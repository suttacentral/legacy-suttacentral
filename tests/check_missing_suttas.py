#!/usr/bin/env python

#
# This check is for Bug 48...
#

import env
from os.path import join
import glob, mysql.connector, regex, textwrap
import config

def clean(str):
    return textwrap.dedent(str).strip()

def get_sutta_id_from_path(path):
    global db
    cursor = db.cursor()
    cursor.execute("""
        SELECT sutta_id FROM sutta
        WHERE sutta_text_url_link LIKE '{}%'
        LIMIT 1;
    """.format(path))
    return (cursor.fetchone() or [None])[0]

def get_sutta_id_from_uid(sutta_uid):
    global db
    cursor = db.cursor()
    cursor.execute("""
        SELECT sutta_id FROM sutta
        WHERE sutta_uid = '{}'
        LIMIT 1;
    """.format(sutta_uid))
    return (cursor.fetchone() or [None])[0]

def each_pali_sutta_file():
    for f in glob.glob(join(config.text_root, 'pi', '*.html')):
        yield f

def make_update_sql(sutta_id, path):
    return clean("""
        UPDATE sutta
            SET sutta_text_url_link = '{path}'
            WHERE sutta_id={sutta_id};
    """.format(path=path, sutta_id=sutta_id)) + '\n'

if __name__ == '__main__':

    db = mysql.connector.connect(**config.mysql)
    output_sql_path = join(config.base_dir, 'tmp', 'missing_suttas.sql')
    output_sql_file = open(output_sql_path, 'w', encoding='utf-8')

    for f in each_pali_sutta_file():
        sutta_uid = regex.match('^.+/([^/]+)\.html$', f)[1]
        path = '/{}/pi'.format(sutta_uid)
        sutta_id = get_sutta_id_from_path(path)
        if sutta_id is None:
            # See if there is a sutta for this...
            sutta_id = get_sutta_id_from_uid(sutta_uid)
            if sutta_id:
                # We have a pali sutta, a sutta in the database but no URL
                # assigned...
                sql = make_update_sql(sutta_id, path)
                output_sql_file.write(sql)
                print(sutta_uid)

    print('SQL fixes are here: {}'.format(output_sql_path))
