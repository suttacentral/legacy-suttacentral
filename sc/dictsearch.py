import functools
import sqlite3
import threading
from contextlib import contextmanager
from html import escape

from sc import config, classes, textfunctions

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
            SELECT terms_base.term as term, alt_terms, dicts.name, dicts.abbrev, terms_base.number, html AS entry, terms_base.boost
                FROM terms INNER JOIN
                entries_base USING(entry_id)
                JOIN dicts ON entries_base.dict_id = dicts.dict_id
                JOIN terms_base ON entries_base.term_id=terms_base.term_id
                WHERE terms.term MATCH ?
                GROUP BY terms_base.entry_id
                ORDER BY terms_base.boost''',
                (query.casefold(), )).fetchall()
                
    def get_matching_entries(self, query):
        return self.execute('''
            SELECT entries.entry_id, dicts.name, dicts.abbrev, term, alt_terms, number, html AS entry
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

        tsk = TermSortKey(query)
        esk = EntrySortKey(query)
        terms.sort(key=tsk)
        entries.sort(key=esk)

        return terms, entries

    def entry_search_count(self, query):
        "This is (generally) no faster than the above."
        return self.execute('SELECT count(*) FROM entries WHERE entries MATCH ?', (query.casefold(),)).fetchone()[0]

class EntrySortKey:
    def __init__(self, query):
        self.query = query.casefold()
        self.terms = self.query.split()
    def __call__(self, row):
        score = 0
        entry = row['entry'].casefold()

        for term in self.terms:
            score -= 0.1 * (1 - min(10, entry.count(term))/10)
            try:
                score -= 0.7 * (1 - entry.index(term, 0, 50) / 50)
                score -= 0.3 * (1 - entry.index(term, 0, 300) / 300)
            except:
                pass

        return 1 + score / len(self.terms)

class TermSortKey:
    def __init__(self, query):
        self.query = query.casefold()
        self.terms = self.query.split()
    def __call__(self, row):
        score = row['boost']
        if self.query in row['term']:
            if row['boost'] == 1:
                score -= 0.1 / len(row['term'])
            else:
                score -= 0.1
        if self.query == row['term']:
            score -= 0.05
        return score
        
omni = OmniDictSearcher(dbname=str(config.dict_db_path))

def search(query, target='dict', limit=10, offset=0, ajax=0):
    dictResults = classes.DictionaryResultsCategory()
    terms, entries = omni.get_terms_and_entries(query)
    total = len(terms) + len(entries)
    if offset > total:
        offset = max(0, total - limit)
        
    navtarget = None

    see_all_terms = None
    see_all_entries = None
    see_all = None
    see_more = None
    if len(terms) > 0:
        href = '/search/?query={}&target=terms&limit=25&offset=0'.format(query)
        see_all_terms = '<a href={}>{} term{} match{}</a>'.format(
                href, len(terms), '' if len(terms)==1 else 's', 'es' if len(terms)==1 else '')
    if len(entries) > 0:
        href = '/search/?query={}&target=entries&limit=25&offset=0'.format(query)
        see_all_entries = '<a href={}>{} entr{} match{}</a>'.format(
            href, len(entries), 'y' if len(terms) == 1 else 'ies', 'es' if len(terms) == 1 else '')
    
    if see_all_entries and see_all_terms:
        href = 'search/?query={}&target=terms,entries&limit=25&offset=0'.format(query)
        see_all = '<a href={}>{} total</a>'.format(href, total)
    if terms and entries:
        see_more = '{} and {}, {}'.format(see_all_terms, see_all_entries, see_all)
    elif terms:
        see_more = see_all_terms
    elif entries:
        see_more = see_all_entries
    if see_more:            #alpha preceeded by >  :)
        see_more = regex.sub('(?<=>)\p{alpha}', lambda m: m[0].upper(), see_more, 1) + '.'
        
    if target == 'all' and ajax:
        if terms:
            terms_list = terms[0:1]
            if see_more:
                terms_list.append(classes.HTMLRow(see_more))
            dictResults.add("", terms_list)

    elif target == 'all':
        maxterms = 3
        maxentries = 0 if terms else 1

        if terms and maxterms > 0:
            terms_list = terms[:maxterms]
            dictResults.add("Terms", terms_list)
        if entries and maxentries > 0:
            entries_list = entries[:maxentries]
            dictResults.add("Entries", entries_list)
        if see_more:
            dictResults.add_row(classes.HTMLRow(see_more))

    elif 'terms' in target and 'entries' in target:
        r_terms = terms[offset:offset+limit]
        if r_terms:
            dictResults.add("Terms", r_terms)
        if len(r_terms) < limit:
            e_limit = limit - len(r_terms)
            e_offset = max(0, offset - len(terms))
            r_entries = entries[e_offset: e_offset + e_limit]
            if r_entries:
                dictResults.add("Entries", r_entries)
        navtarget = "terms,entries"
    elif 'terms' in target:
        dictResults.add("Terms", terms[offset:offset+limit])
        total = len(terms)
        navtarget="terms"

    elif 'entries' in target:
        dictResults.add("Entries", entries[offset:offset+limit])
        total = len(entries)
        navtarget="entries"

    footurl = ""
    if navtarget and offset > 0:
        #Prev link
        start = max(0, offset - limit)
        href ='/search/?query={}&target={}&limit={}&offset={}'.format(
            query, navtarget, limit, start)
        footurl += '<a href="{}"> « Results {}–{}</a>'.format(
            escape(href), start + 1, min(total, start + limit))
    if navtarget and limit + offset < total:
        start = offset + limit
        href ='/search/?query={}&target={}&limit={}&offset={}'.format(
            query, navtarget, limit, start)
        footurl += '<a href="{}">Results {}—{} of {} »</a>'.format(
            escape(href), start, min(total, start + limit), total)
    if footurl:
        dictResults.add_row(classes.HTMLRow(footurl))
    return dictResults