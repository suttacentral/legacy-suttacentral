""" Convert a mysql database to sqlite3

If dbname is memory, then a reference to the created database will be
returned. If dbname is a filename, then a sqlite3 database of that name
will be created. If the file already exists, it will be replaced with the
new database when it is fully-formed, this replacement is an atomic
operation.

"""

import subprocess as _subprocess, regex as _regex, sqlite3 as _lite, time as _time, os as _os, shutil as _shutil

def dump_mysql(mysql_settings):
    """ Produce a clean dump of a mysql database """
    command = "mysqldump --compact -u {0[user]} --password={0[password]} {0[db]}".format(mysql_settings)
    script = _subprocess.check_output(command.split()).decode()
    script = _regex.sub(r'/\*.*?\*/;?', '', script, _regex.DOTALL)
    script = script.replace('`', '')
    return script

def build_sqlite3_db(script, dbname=':memory:', cull=None, no_index=False):
    if dbname == ':memory:':
        con = _lite.connect(dbname)
    else:
        dbname_tmp = dbname + '.tmp' + str(int(_time.time()))[:5]
        con = _lite.connect(dbname_tmp)
    
    con.execute('PRAGMA synchronous = 0')

    rules = (
        (r'AUTO_INCREMENT|COLLATE \w+|CHARACTER SET \w+|ON UPDATE CURRENT_TIMESTAMP', ''),
        (r'[,\s]+\)\Z', ')'),
        (r' int\(\d+\)( unsigned)?', ' INTEGER'),
        (' varchar\(\d+\)', ' TEXT'),
        (' char\(\d+\)', ' TEXT'),
        (' enum\(.*?\)', ' TEXT'),
        )
    
    table_kills = {}
    indexes = []
    creates = _regex.findall(r'(CREATE .*?\)) ENGINE.*?;', script, _regex.DOTALL)
    for i in range(0, len(creates)):
        # Apply rules
        
        index_strings = _regex.findall(r'(?m)^\s*.*?(?<!PRIMARY) KEY.*', creates[i])
        creates[i] = _regex.sub(r'(?m)^\s*.*?(?<!PRIMARY) KEY.*', '', creates[i])
        
        for rule, repl in rules:
            creates[i] = _regex.sub(rule, repl, creates[i])
            
        m = _regex.match(r"CREATE TABLE (?<table>\w+) \((?:(?<column>\s*(?<field>\w++).*))*\)", creates[i])
        table = m['table']
        columns = m.captures('column')
        fields = m.captures('field')
        assert len(columns) == len(fields)
        if cull is None:
            new_columns = columns
        else:
            new_columns = [columns[i] for i, f in enumerate(fields) if not cull(f)]
            table_kills[table] = (
            [i for (i, f) in enumerate(m.captures('field')) if cull(f)])

        new_sql = "CREATE TABLE {} ({})".format(table, "".join(new_columns))

        if new_sql[-2:] == ',)':
            new_sql = "".join((new_sql[:-2],  ')'))

        con.execute(new_sql)
        
        # Create indexes
        for ix in index_strings:
            ixm = _regex.match('\s*(?<unique>UNIQUE |)?KEY (?<name>\w+) \((?<columns>.*)\)', ix)
            index_sql = 'CREATE {m[unique]}INDEX {table}_{m[name]} ON {table} ({m[columns]});'.format(m=ixm, table=table)
            indexes.append(index_sql)

    insertPattern = r"(INSERT INTO (?<table>\w+) VALUES )"
    valuesPattern = r"\(((?:(?<value>\d++[\d.]*|NULL)|'(?<value>(?:[^']|\\')*)')[,\)])*[,;\)]"


    for insert in _regex.findall('INSERT .*', script, flags=_regex.MULTILINE):
        m = _regex.match(insertPattern + valuesPattern, insert)
        cullem = set(table_kills[m['table']]) if table_kills else set()

        row = m.captures('value')
        cmd = "{}({})".format(m[1], ", ".join("?" * (len(row) - len(cullem))))

        rows = [row.captures('value') for row in _regex.finditer(valuesPattern, insert, start=m.end())]
        if table_kills:
            rows2 = [ [(f if f != 'NULL' else None) for i, f in enumerate(row) if i not in cullem] for row in rows]
        else:
            rows2 = rows
        con.executemany(cmd, rows2)
    if not no_index:
        for index_sql in indexes:
            try:
                con.execute(index_sql)
                con.commit()
            except _lite.IntegrityError as e:
                print('Problem executing: "{}"'.format(index_sql))
                print(e)
                if 'UNIQUE' in index_sql:
                    print("Attempting to create non-unique index... ", end='')
                    try:
                        con.execute(index_sql.replace('UNIQUE', ''))
                        con.commit()
                        print(" success.")
                    except:
                        print(" failure.")
                        raise

    con.commit()
    if dbname != ":memory:":
        try:
            con.close()
            _os.replace(dbname_tmp, dbname)
        except OSError:
            raise
    else:
        return con

def cull(column_defn, cull_list):
    if any(k in column_defn for k in cull_list):
        return True
    else:
        return False

def convert(mysql_settings, lite_db=':memory:', cull_list=None, no_index=False):
    script = dump_mysql(mysql_settings)
    con = build_sqlite3_db(script, lite_db, cull=(lambda s: cull(s, cull_list)) if cull_list else None, no_index=no_index)
    return con

#convert(mysql_settings, lite_db=':memory:', cull_list=('timestamp', 'login'))

#convert(mysql_settings, lite_db='scdb.sqlite', cull_list=('timestamp', 'login'),no_index=True)
    