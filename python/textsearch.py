import os, threading, sqlite3, regex, lxml.html, shutil, functools, collections
from array import array
from contextlib import contextmanager
import declensions, config
from classes import FulltextResultsCategory, HTMLRow

from textfunctions import *

class PrettyRow(sqlite3.Row):
    def __repr__(self):
        out = []
        out.append("<PrettyRow:")
        for key in self.keys():
            out.append("['{}']={}".format(key, self[key]))
        out[-1] += ' >\n'
        return "\n".join(out)

tlocals = threading.local()
tlocals.con = {}

textroot = config.app['text_root']
searchroot = config.textsearch['dbpath']

def rank(data):
    "Taken from SQLite3 fts3/4 documentation c -> python"
    aMatchInfo = array('i', data)
    nPhrase = aMatchInfo[0]
    nCol = aMatchInfo[1]

    score = 0.0
    
    for iPhrase in range(0, nPhrase):
        aPhraseInfo = aMatchInfo[2 + iPhrase * nCol * 3:]
        for iCol in range(0, nCol):
            nHitCount = aPhraseInfo[3*iCol]
            nGlobalHitCount = aPhraseInfo[3*iCol+1]
            if nHitCount > 0:
                score += nHitCount / nGlobalHitCount
    return score

def fileiter(path, ext=None, rex=None):
    """Iterate over files starting at src.

    ext can be a string of space-seperated extensions. Or it can be an
    empty string. The empty string only matches files with no extension.

    rex should be a regular expression object or pattern. Only files which
    produce a match will be returned.
    """
    if ext is not None and ext != '':
        ext = regex.split(r'[, ]+', ext)
    if rex is not None and type(rex) is str:
        rex = regex.compile(rex)
    extmatch = regex.compile(r'.*\.(.*)').match
    for f in os.listdir(path):
        if ext:
            m = extmatch(f)
            if not m or m[1] not in ext:
                continue
        if not rex or rex.search(f):
            yield os.path.join(path, f)
        
def find_best_id(tag):
    while True:
        for a in tag.iter():
            if 'id' in a.attrib:
                if len(a.attrib['id']) > 0:
                    return a.attrib['id']
        tag = tag.getprevious()
        if tag is None:
            return '#'

class SectionSearch:
    """ Full text search class based on SQLite fts4 extension.

    SQL lite has some limitations around non-ascii characters and of course
    is limited in it's support for pali.

    A hack is used to workaround two limitations:
    1) Unicode punctuation/spaces aren't recognized as puncuation/space:
        To workaround this, unicode puncuations are replaced with unused
        ascii non-word-character subtitutes. On display, the substitutes
        are replaced with the unicode characters.
        It should be noted that ascii control characters can be used just
        fine since the the simple tokenizer treats anything which isn't
        [a-zA-Z0-9] as a seperator (porter additionally includes underscore)
        meaning that around 40 unicode characters can be given ascii
        placeholders.

    2) Non-ascii characters are case-sensitive, stemming:
        To work around this, an external content fts4 table is used, the
        real text is inserted into the real table, and the text inserted
        into the fts4 table is massaged in python, with the same massaging
        being applied to the query.
        The snippet function draws it's snippets from the real table, the
        only requirement for this sleight of hand to work is that the real
        and massaged texts tokenize into the 'same' tokens using the fts4
        simple tokenizer. This is why hack #1 and #2 must be combined. For
        example "then the bar—actually a baz—went foo" would be tokenized as
        'then, the, bar—actually, a, baz—went, foo'
        A hack#1 version would tokenize as:
        'then, the, bar, actually, a, baz, went, foo'
        And the snippet function would completely break down.

    In an ideal world we would implemented a custom fts3 tokenizer, but
    these hacks are not particulary ardious and are less work.

    This search implementation is reasonably fast, and as a near
    approximation uses no memory at all.

    """

    fts_tokenizer = 'porter'
    rex_tokenizer = regex.compile(r'([\p{ascii}--[A-Za-z0-9_]]+)', flags=regex.V1)
    #fts_tokenizer = 'simple'
    #rex_tokenizer = regex.compile(r'[A-Za-z0-9]+')
    aliases = []

    def __init__(self, lang_code, extensions='html', tags='h1, h2, p'):
        self.lang_code = lang_code
        self.extensions = extensions
        self.tags = tags
        self.path = os.path.join(textroot, lang_code)
        if not os.path.exists(self.path):
            raise Exception("Path {} does not exist".format(self.path))
        self.dbname = os.path.join(searchroot,
            'search_{}.sqlite'.format(lang_code))
        self.alias_map = {}
        for group in self.aliases:
            stemmed = [self.stemmer(t) for t in group]
            alias_text = '(' + " OR ".join(stemmed) + ')'
            self.alias_map.update((alias, alias_text) for alias in stemmed)

    @contextmanager
    def getcon(self):
        """ Reuse connections

        While SQLite connections are cheap to create, they do take a little
        time, and registering functions also adds to creation time.
        Recycling the connection reduces search execution time by ~20%.

        """

        try:
            tlocals.con
        except AttributeError:
            tlocals.con = {}
        try:
            con = tlocals.con[self.dbname]
        except KeyError:
            con = sqlite3.connect(self.dbname)
            con.row_factory=PrettyRow
            con.create_function('rank', 1, rank)
            con.create_function('demangle', 1, demangle)
            tlocals.con[self.dbname] = con
        try:
            yield con
        except:
            del tlocals.con[self.dbname]
            raise
        finally:
            pass

    def execute(self, sql, args=()):
        with self.getcon() as con:
            return con.execute(sql, args)
    def executemany(self, sql, args=()):
        with self.getcon() as con:
            return con.executemany(sql, args)

    def files(self):
        "Returns a sorted list of all files to be indexed"
        return sorted(fileiter(self.path, self.extensions), key=numsortkey)

    def checksum(self):
        "Returns an integer which can be compared to see if the files have changed"
        return sum(os.stat(f).st_mtime_ns & 4294967295 for f in self.files())

    def sanitize(self, string):
        return regex.sub(r'[\u200b]', '', string)
    
    def parse_entries(self):
        uidfind = regex.compile(r'.*/([\w-]+(?:\.[\d-]+)?)').findall
        entries = []
        stemmed_entries = []
        original_entries = []
        entry_id = 0
        for filename in self.files():

            file_uid = uidfind(filename)[0]

            dom = lxml.html.fromstring(open(filename, 'r', encoding='utf-8').read())
            self.dom = dom
            for e in dom.cssselect('#metaarea, .hidden'):
                e.drop_tree()
                
            elements = dom.cssselect(self.tags)
            elements.append(dom.makeelement('SENTINEL'))
            lasttag = 'p'
            text_l = []
            best_id = title = sutta_uid = None

            for i, e in enumerate(elements):
                if e.tag != 'p' and lasttag == 'p':
                    if text_l:
                        # Add this entry.

                        entry_id += 1
                        mang_text = " «br» ".join(text_l)
                        orig_text = mang_text.casefold().replace('\xad','')
                        stem_text = self.stemmer(mang_text)

                        entries.append( (entry_id, file_uid, sutta_uid, title, best_id, mang_text) )
                        stemmed_entries.append( (entry_id, stem_text) )
                        original_entries.append( (entry_id, orig_text) )

                        text_l = []
                        best_id = title = sutta_uid = None
                if e.tag == 'SENTINEL':
                    continue
                if sutta_uid is None:
                    # Attempt to discover true sutta_uid
                    # This really needs improvement in the source texts
                    # but the below bodge works in practise.
                    try:
                        
                        section = next(e.iterancestors('section'))
                        if 'id' in section.attrib:
                            t_uid = section.attrib['id']
                            if t_uid[0].isalpha():
                                sutta_uid = t_uid
                        if sutta_uid is None:
                            hgroup = next(section.iter('hgroup'))
                            sutta_uid = hgroup.cssselect('[id]')[0].attrib['id']
                    except (StopIteration, IndexError):
                        sutta_uid = file_uid

                if e.tag.startswith('h'):
                    # Choose the best title (prefer shorter, no numbers)
                    htext = e.text_content()
                    if not title:
                        title = htext
                    else:
                        if not regex.search(r'\d', htext) and regex.search(r'\d', title):
                            title = htext
                        elif len(title) > len(htext):
                                title = htext
                    if not best_id:
                        node = e
                        if e.getparent() is not None and e.getparent().tag in ('a', 'hgroup'):
                            node = e.getparent()
                        for a in node.iter():
                            try:
                                best_id = a.attrib['id']
                                break
                            except KeyError:
                                pass

                for a in e.iter('a'):
                    if a.text is None or regex.search('\d', a.text):
                        a.drop_tree()
                text = e.text_content()
                text = self.sanitize(text)
                text = mangle(text)
                text_l.append(text)
                lasttag = e.tag
        return (entries, original_entries, stemmed_entries)
    
    def generate_search_db(self):
        tmpfile = self.dbname + '.tmp'
        try:
            os.remove(tmpfile)
        except OSError:
            pass
        con = sqlite3.connect(tmpfile)
        con.execute('PRAGMA foreign_keys = ON')
        con.execute('PRAGMA synchronous = 0')
        con.execute('''CREATE TABLE entries (
            entry_id INTEGER PRIMARY KEY,
            file TEXT,
            uid TEXT,
            heading TEXT,
            bookmark TEXT,
            text TEXT)''')
        con.execute('''CREATE VIRTUAL TABLE stemmed
            USING fts4(content=entries, tokenize={}, file, uid, heading, bookmark, text)'''.format(self.fts_tokenizer))
        con.execute('''CREATE VIRTUAL TABLE original
            USING fts4(content=entries, tokenize=simple, file, uid, heading, bookmark, text)''')

        entries, original_entries, stemmed_entries = self.parse_entries()

        self.last = (entries, original_entries, stemmed_entries)

        con.executemany('INSERT INTO entries values(?, ?, ?, ?, ?, ?)',
            entries)
        con.executemany('INSERT INTO stemmed (docid, text) values (?, ?)',
            stemmed_entries)
        con.executemany('INSERT INTO original (docid, text) values (?, ?)',
            original_entries)

        con.commit() # Optimize requires commit beforehand.
        
        con.execute("INSERT INTO stemmed(stemmed) VALUES('optimize')")
        con.execute("INSERT INTO original(original) VALUES('optimize')")

        con.execute("CREATE VIRTUAL TABLE ft_terms USING fts4aux(original)")
        # We create a real table which can be indexed.
        terms = con.execute('SELECT term, occurrences FROM ft_terms WHERE col="*"').fetchall()

        con.execute('CREATE TABLE terms(ascii TEXT, simplified TEXT, phonetic TEXT, original TEXT, freq INT)')
        con.execute('DROP TABLE ft_terms')

        terms2 = [
            (asciify(term)[:24],
            simplify(term, self.lang_code, None) if len(term) < 24 else None,
            phonhash(term) if len(term) < 24 else None,
            term,
            occurrences) for term, occurrences in terms if not regex.search(r'\d', term) and term[0].isalpha()]

        con.executemany('INSERT INTO terms VALUES (?,?,?,?,?)', terms2)
        con.execute('CREATE INDEX terms_ascii_x ON terms(ascii)')
        con.execute('CREATE INDEX terms_simp_x ON terms(simplified)')
        con.execute('CREATE INDEX terms_phon_x ON terms(phonetic)')
        con.execute('CREATE UNIQUE INDEX terms_orig_x ON terms(original)')
        
        con.commit()
        os.replace(tmpfile, self.dbname)

    def stemmer(self, string, query=False):
        """stemmer should pre-stem text before passing it to fts4

        It is important to use the right python tokenizer which matches
        the chosen fts4 tokenizer.

        if query is true, that means a query is being processed. doing
        something special with queries is optional.

        stemmer need only casefold if a built-in fts3 stemmer is used.

        """

        stem = string.casefold()

    def vel_term_correction(self, term):
        return vel_to_uni(term)

    def expand_term(self, term):
        return [term]

    def ascii_term_correction(self, term, prune_ratio=50):
        """Converts an ascii form to probably intended true form.

        This works for any language/script based on ascii. It obviously
        wont work for Thai, Sinhala script etc.

        """
    
        wildcard = term.endswith('*')
        negated = term.startswith('-')
        o_term = term
        if wildcard:
            term = term[:-1]
        if negated:
            term = term[1:]
        s_term = simplify(term, self.lang_code)
        
        if wildcard:
            rows = self.execute('''SELECT original, freq FROM terms
            WHERE ascii >= ? AND ascii <= ?
            ORDER BY freq DESC''', (term, term+'~')).fetchall()
            if not rows and s_term is not None:
                rows = self.execute('''SELECT original, freq FROM terms
                WHERE simplified >= ? AND simplified <= ?
                ORDER BY freq DESC''',
                    (s_term, s_term+'~')).fetchall()
        else:
            forms = self.expand_term(term)
            sql = ('SELECT original, freq FROM terms '
                'WHERE ascii=? {}'.format('OR ascii=? ' * (len(forms)-1))+
                'ORDER BY freq DESC')

            rows = self.execute(sql, forms).fetchall()

            if not rows and s_term is not None:
                rows = self.execute('''SELECT original, freq FROM terms
                    WHERE simplified=? ORDER BY freq DESC''',
                        (s_term,)).fetchall()
        if not rows:
            return (None,None)

        best = rows[0][1]
        # Prune terms with low occurences
        terms = [row[0] for row in rows if best / row[1] <= prune_ratio]
        stemmed_terms = set(self.stemmer(term) for term in terms)
        stemmed_terms -= {None}
        
        prefix ='-' if negated else ''
        joiner = ' ' if negated else ' OR ' 

        if wildcard:
            # Return in stem + '*' form - using '*' is much more effecient
            # than OR'ing all full-length possibilities.
            exact_query = joiner.join(set(prefix + t[:len(term)] + '*' for t in terms))
            stemmed_query = joiner.join(set(prefix + t[:len(term)] + '*' for t in stemmed_terms))
        else:
            exact_query = joiner.join(prefix + t for t in terms[:3])
            stemmed_query = joiner.join(prefix + t for t in stemmed_terms)

        return (exact_query, stemmed_query)

    @functools.lru_cache(50)
    def prepare_query(self, query):
        "Prepare the query in a way which preserves control words"
        terms = regex.split(r'((?:\s+(?:OR|NEAR(?:/\d+)?)\s+|[,\s]+|"[^"]*")+)', query)
        exact_out = []
        stemmed_out = []
        is_near = query.find('NEAR') != -1

        exact_bad = False
        stemmed_bad = False

        for i, term in enumerate(terms):
            if i % 2 == 1:
                exact_out.append(term)
                stemmed_out.append(term)
                continue
            if term == '':
                continue
            term = term.casefold()
            term = self.vel_term_correction(term)
            
            if max(term) <= '~':
                exact, stemmed = self.ascii_term_correction(term, 1 if is_near else 50)
                if not exact:
                    exact_bad = True
                if not stemmed:
                    stemmed_bad = True
                    
            else:
                exact = term
                stemmed = self.stemmer(term)
                if not stemmed:
                    stemmed_bad = True
                
                try:
                    stemmed = self.alias_map(stemmed)
                except:
                    pass
            
            exact_out.append(exact)
            if stemmed:
                stemmed_out.append(stemmed)

        exact_query = "".join(exact_out) if not exact_bad else ''
        stemmed_query = "".join(stemmed_out) if not stemmed_bad else ''
                
        return (exact_query, stemmed_query)

    @functools.lru_cache(50)
    def get_match_count(self, e_query, s_query):
        exacts = set(t[0] for t in self.execute('SELECT docid FROM original WHERE original MATCH ?', (e_query,)).fetchall()) if e_query else set()
        stemmed = set(t[0] for t in self.execute('SELECT docid FROM stemmed WHERE stemmed MATCH ?', (s_query,))) if s_query else frozenset()
        #assert not stemmed or stemmed.issuperset(exacts), "Exact results not contained within stemmed results"
        stemmed -= exacts
        
        return (len(exacts), len(stemmed))

    def search_stemmed(self, e_query, s_query, limit=10, offset=0):

        rows = self.execute('''
            SELECT file, uid, heading, bookmark, demangle(snippet(stemmed, "<b>", "</b> ", " … ", -1, 40)) as snippet FROM stemmed JOIN (
                SELECT docid, rank(matchinfo(stemmed)) AS rank
                FROM stemmed
                WHERE docid NOT IN (SELECT docid FROM original WHERE
                    original MATCH :query)
                AND stemmed MATCH :squery
                ORDER BY rank DESC
                LIMIT :limit OFFSET :offset
            ) AS ranktable USING (docid)
            WHERE stemmed MATCH :squery
            ORDER BY ranktable.rank DESC''',
                        {'query':e_query, 'squery':s_query, 'limit':limit, 'offset':offset}).fetchall()

        return rows
    
    def search_exact(self, query, limit=10, offset=0):
        rows = self.execute('''
            SELECT file, uid, heading, bookmark, demangle(snippet(original, "<b>", "</b>", " … ", -1, 40)) as snippet FROM original JOIN (
                SELECT docid, rank(matchinfo(original)) AS rank
                FROM original
                WHERE original MATCH :query
                ORDER BY rank DESC
                LIMIT :limit OFFSET :offset
            ) AS ranktable USING (docid)
            WHERE original MATCH :query
            ORDER BY ranktable.rank DESC''',
            {'query':query, 'limit':limit, 'offset':offset}).fetchall()

        return rows

    def search(self, query, limit=10, offset=0):
        if limit == 0:
            return None
        e_query, s_query = self.prepare_query(query)

        e_total, s_total = self.get_match_count(e_query, s_query)
        if (e_total + s_total) < offset:
            return None
            
        exacts, stemmed = [], []
        # How many exact results to fetch?
        tofetch = limit
        if offset < e_total and e_total > 0:
            exacts = self.search_exact(e_query, limit=tofetch, offset=offset)

        tofetch -= len(exacts)
        
        if tofetch > 0 and s_total > 0:
            stemmed = self.search_stemmed(e_query, s_query, limit=tofetch, offset=offset - e_total)

        return (exacts, stemmed)

    #def search(self, query, limit=10, offset=0):
        #exact_count = self.count_exact(query)
        #stemmed_count = self.count_stemmed(query) - exact_count
        #to_fetch = exact_count - offset
        #exact_results = []
        #stemmed_results = []
        #if to_fetch > 0:
            #exact_results = self.search_exact(query, limit, offset)
            #if len(exact_results) == limit:
                #return (exact_results, [])

        ## We already have len(exact_results) results
        #offset -= exact_count
        #limit -= len(exact_results)

        #if stemmed_count - offset > 0:
            #stemmed_results = self.search_stemmed(query, limit, offset)
        #return (exact_results, stemmed_results)

class PaliStemFilter:
    " A stemmer for pali. "
    
    # Nirvana, karma
    sanskrit_to_pali = ( ('rv', 'bb'), ('rm', 'mm') )
    suffixes = set(declensions.endings)
    indeclineables = set(declensions.indeclineables)

    qsuffixes = set()
    qindeclineables = set()

    def __init__(self):
        if len(self.qsuffixes) == 0:
            self.qsuffixes.update(self.suffixes)
            self.qsuffixes.update(asciify(t) for t in self.suffixes)

            self.qindeclineables.update(self.indeclineables)
            self.qindeclineables.update(asciify(t) for t in self.indeclineables)

    def __call__(self, text, query=False):
        if query:
            indeclineables = self.qindeclineables
            suffixes = self.qsuffixes
        else:
            indeclineables = self.indeclineables
            suffixes = self.suffixes
        # Simplify the pali
        
        pieces = self.tokenizer.split(text)
        for place, token in enumerate(pieces):
            if place % 2 == 1 or not token or not token[0].isalpha():
                continue
            if token not in indeclineables:
                for skt, pli in self.sanskrit_to_pali:
                    token = token.replace(skt, pli)
                if token[:-1] == 'n':
                    token = token[:-1] + 'ṃ'
                for i in range(min(7, int(len(token)/2 - 0.5)), 0, -1):
                    sfx = token[-i:]
                    if sfx in suffixes:
                        token = token[:-i]
                        break
            
            #token = asciify(token)
            pieces[place] = token
        return "".join(pieces)
    
class PaliTextSearch(SectionSearch):
    fts_tokenizer = 'simple'
    rex_tokenizer = regex.compile(r'([\p{ascii}--[A-Za-z0-9]]+)', flags=regex.V1)
    stemmer = PaliStemFilter()
    stemmer.tokenizer = rex_tokenizer
    def expand_term(self, term):
        # 'a stem' also attempts to match o/aṁ for pali only.
        if term.endswith('a'):
            forms = [term, term[:-1] + 'o', term[:-1] + 'am']
        else:
            forms = [term]
        return forms

class EnglishTextSearch(SectionSearch):
    aliases =[('bhikkhu', 'monk', 'biksu'), ('bhikkhuni', 'nun', 'biksuni')]
    
    @staticmethod
    def repl(m):
        " Normalize common sanskrit terms into pali "
        string = m[0]
        string = string.replace('dharm', 'dhamm')
        string = string.replace('karm', 'kamm')
        string = string.replace('karm', 'kamm')
        string = string.replace('nirv', 'nibb')
        string = string.replace('ttva', 'tta')
        string = string.replace('bhiks', 'bhikkh')
        string = string.replace('bhikkhuni', 'nun')
        string = string.replace('bhikkhu', 'monk')
        return string

    rex_tokenizer = regex.compile(r'[\P{ascii}A-Za-z0-9_]+', flags=regex.V1)
    def stemmer(self, string, query=False):
        string = asciify(string)
        string = self.rex_tokenizer.sub(EnglishTextSearch.repl, string)
        return string

class VietnameseTextSearch(SectionSearch):
    fts_tokenizer = 'simple'
    rex_tokenizer = regex.compile(r'([\p{ascii}--[A-Za-z0-9]]+)', flags=regex.V1)

    # Todo: stemmer? Perhaps not needed for VN.
    
pi = PaliTextSearch('pi')
en = EnglishTextSearch('en')
vn = VietnameseTextSearch('vn')

all_searchers = {pi.lang_code:pi, en.lang_code:en, vn.lang_code:vn}

def build(all_searchers=all_searchers):
    for lang in sorted(all_searchers):
        all_searchers[lang].generate_search_db()

def count_all(query):
    out = {}
    for lang, searcher in all_searchers.items():
        # Note: Both below functions are cached.
        out[lang] = sum(searcher.get_match_count(*searcher.prepare_query(query)))
    return out

def search(query, target="texts", limit=25, offset=0, lang='en'):
    result = FulltextResultsCategory()
    counts = count_all(query)
    if target=='all':
        urls = []
        for lang_code in sorted(counts):
            if counts[lang_code] > 0:
                urls.append('<a href=/search/?query={query}&target=texts&lang={lang}&limit=25&offset=0>{lang}: {count}</a>'.format(
                    query=query,
                    lang=lang_code,
                    count=counts[lang_code]))
        if urls:
            result.add("", [HTMLRow(" | ".join(urls))])
        else:
            return None
    
    elif 'texts' in target:
        if lang in counts and counts[lang] > 0:
            total = counts[lang]
            results = all_searchers[lang].search(query, limit, offset)
            search.last = results
            results = results[0] + results[1]
            search.results = results
            result.add("", results)
            links = []
            if offset > 0:
                # Prev link
                start = max(0, offset - limit)
                end = min(start + limit, total)
                href = "/search/?query={}&target=texts&lang={}&limit={}&offset={}".format(query, lang, limit, start)
                links.append('<a href="{}">« Results {}–{}</a>'.format(
                    href, start + 1, end))
            if total > offset + len(results):
                # Next link
                start = offset + limit
                end = min(start + limit, total)
                href = "/search/?query={}&target=texts&lang={}&limit={}&offset={}".format(query, lang, limit, start)
                links.append('<a href="{}">Results {}–{} (of {}) »</a>'.format(
                    href, start + 1, end, total))
            if links:
                result.add_row(HTMLRow(" ".join(links)))
        else:
            return None

    return result