import sqlite3, threading, time, collections, functools, concurrent.futures, unicodedata, time, regex, jinja2
from contextlib import contextmanager

import textfunctions, config, classes

class PrettyRow(sqlite3.Row):
    def __repr__(self):
        out = []
        out.append("<PrettyRow:")
        for key in self.keys():
            out.append("['{}']={}".format(key, self[key]))
        out[-1] += ' >\n'
        return "\n".join(out)

# Use threadlocals for sqlite3 connections, since they can't be shared.
tlocals = threading.local()
if not hasattr(tlocals, 'con'):
    tlocals.con = {}

def uni_in(substr, string):
    return substr.casefold() in string.casefold()

class OmniDictSearcher:
    """ Dictionary searcher based on an SQLite database.

    Blazingly fast. Can perform 5000 lookups per second. Term lookup can be
    made twice as fast by avoiding fts4 extension, but why bother?
    Note that queries must be lowercase.

    Also note that the count functions generally execute no faster than
    actually pulling the results. The time is consumed nearly entirely in
    discovering what matches. However, if ranking is added, then the count
    function might be a lot faster so it should be preferred when only a
    count is needed.

    Rolling the count into the search incurs very little overhead,
    particulary when nothing matches, so all queries return total as the
    total number of matches.
    
    """
    def __init__(self, dbname):
        self.dbname = dbname
    
    @contextmanager
    def getcon(self):
        """Get a properly set up connection object.

        This function recycles the connections. This is for performance
        reasons, allowing the '5000+' queries per second!

        """
        try:
            tlocals.con
        except AttributeError:
            tlocals.con = {}
        try:
            con = tlocals.con[self.dbname]
        except KeyError:
            con = sqlite3.connect(self.dbname)
            con.create_function('py_in', 2, uni_in)
            con.create_function('mc4', 2, textfunctions.mc4)
            con.create_function('demangle', 1, textfunctions.demangle)
            con.row_factory = PrettyRow
            tlocals.con[self.dbname] = con
        try:
            yield con
        except:
            # Make a new connection in case it helps solve the problem.
            del tlocals.con[self.dbname]
            raise
        finally:
            pass

    def fix_match_query(self, query):
        " Performs case-correction on a query for use in MATCH clause"
        def repl(m):
            return m[0] + ' OR ' + m[0][0].upper() + m[0][1:].lower()
        return regex.sub(r'\b[[\p{lower}]&&[\P{ascii}]]\w+', repl, query,
            flags=regex.V1)
    def execute(self, sql, args=()):
        with self.getcon() as con:
            return con.execute(sql, args)

    def get_matching_terms(self, query):
        return self.execute('''
            SELECT terms_base.term as term, dicts.name, dicts.abbrev, terms_base.number, coalesce(html, demangle(text)) AS full, coalesce(brief, text) AS brief
                FROM terms INNER JOIN
                entries_base USING(entry_id)
                JOIN dicts ON entries_base.dict_id = dicts.dict_id
                JOIN terms_base ON entries_base.term_id=terms_base.term_id
                WHERE terms.term MATCH ?
                GROUP BY terms.entry_id
                ORDER BY terms.boost''',
                (query.casefold(), )).fetchall()
                
    def get_matching_entries(self, query):
        return self.execute('''
            SELECT entries.entry_id, dicts.name, dicts.abbrev, term, number, coalesce(brief, demangle(text)) AS brief, coalesce(html, demangle(text)) AS full, snippet(entries) AS snip
                FROM entries INNER JOIN terms_base USING(term_id)
                JOIN dicts ON entries.dict_id = dicts.dict_id
                WHERE entries MATCH :query
                AND entries.entry_id NOT IN (SELECT entry_id FROM terms WHERE terms MATCH :query)
                ''', {'query':query.casefold(), 'cquery': query}).fetchall()
    
    @functools.lru_cache(50)
    def get_terms_and_entries(self, query):
        terms = self.get_matching_terms(query)
        entries = self.get_matching_entries(query)
        lquery = query.casefold()
        terms.sort(key=lambda r: r['term'].casefold() == lquery, reverse=True)
        entries.sort(key=lambda r: r['full'].lower().count(lquery), reverse=True)

        return terms, entries

    def entry_search_count(self, query):
        "This is (generally) no faster than the above."
        return self.execute('SELECT count(*) FROM entries WHERE entries MATCH ?', (query.casefold(),)).fetchone()[0]

omni = OmniDictSearcher(dbname=config['dict']['db'])

def search(query, target='dict', limit=10, offset=0, ajax=0):
    dictResults = classes.DictionaryResultsCategory()
    terms, entries = omni.get_terms_and_entries(query)
    total = len(terms) + len(entries)
    if target == 'all' and ajax:
        if len(terms) > 0:
            href = "/search/?query={}&target=dict&limit=25&offset=0".format(query)
            strings = []
            if terms:
                strings.append('{} terms'.format(len(terms)))
            if entries:
                strings.append('{} entries'.format(len(entries)))
            dictResults.footurl = '<a href="{}">{} match {}</a>'.format(
                href, " and ".join(strings),
                query)
            dictResults.add("", terms[0:1])
        else:
            return None

    elif target == 'all':
        footurl = None
        total = len(entries) + len(terms)
        if total > 0:
            href = '/search/?query={}&target=dict&limit=10&offset=0'.format(query)
            footurl = '<a href="{}">Show full dictionary results ({} total)</a>'.format(href, total)

        dictResults.footurl = footurl
        if terms:
            dictResults.add("Terms", terms[:5])
        if entries:
            dictResults.add("Entries", entries[:5])
            
    elif target == "dict":
        footurl = ""
        r_terms = terms[offset:offset+limit]
        if r_terms:
            dictResults.add("Terms", r_terms)
        if len(r_terms) < limit:
            e_limit = limit - len(r_terms)
            e_offset = max(0, offset - len(terms))
            r_entries = entries[e_offset: e_offset + e_limit]
            if r_entries:
                dictResults.add("Entries", r_entries)
        if offset > 0:
            #Prev link
            start = max(0, offset - limit)
            href ='/search/?query={}&target=dict&limit={}&offset={}'.format(
                query, limit, start)
            footurl += '<a href="{}"> « Results {}–{}</a>'.format(
                href, start + 1, min(total, start + limit))
        if limit + offset < total:
            start = offset + limit
            href ='/search/?query={}&target=dict&limit={}&offset={}'.format(
                query, limit, start)
            footurl += '<a href="{}">Results {}—{} »</a>'.format(
                href, start, min(total, start + limit))
        dictResults.footurl = footurl

    return dictResults

def stress():
    "Search all terms. Helps expose problems."
    import random, concurrent.futures as futures, time
    terms = [t[0] for t in omni.execute('SELECT term FROM terms')]
    queries = (random.sample(terms, 50) * 50)[:25000]
    
    getter = futures.ThreadPoolExecutor(4)
    start=time.time()
    results = list(getter.map(omni.get_matching_terms, queries))
    done = time.time()
    print("{} queries executed in {} seconds.".format(len(terms), done-start))
    print("{} queries per second.".format(len(terms) / (done-start)))
    return results
    