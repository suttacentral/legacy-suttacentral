import os, threading, sqlite3, regex, lxml.html, shutil
from array import array
from contextlib import contextmanager
import textfunctions, declensions, config

tlocals = threading.local()
tlocals.con = {}

textroot = config.app['text_root']
searchroot = config.textsearch['dbpath']


def rank(data):
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

    def __init__(self, lang_code, extensions='html', tags='h1, h2, p'):
        self.lang_code = lang_code
        self.extensions = extensions
        self.tags = tags
        self.path = os.path.join(textroot, lang_code)
        if not os.path.exists(self.path):
            raise Exception("Path {} does not exist".format(self.path))
        self.dbname = os.path.join(searchroot,
            'search_{}.sqlite'.format(lang_code))

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
            con.create_function('rank', 1, rank)
            con.create_function('demangle', 1, textfunctions.demangle)
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

    def files(self):
        "Returns a sorted list of all files to be indexed"
        return sorted(fileiter(self.path, self.extensions), key=textfunctions.numsortkey)

    def checksum(self):
        "Returns an integer which can be compared to see if the files have changed"
        return sum(os.stat(f).st_mtime_ns & 4294967295 for f in self.files())

    def sanitize(self, string):
        return regex.sub(r'[\u200b]', '', string)

    def parse_entries(self):
        uidfind = regex.compile(r'.*/([\w-]+)').findall
        entries = []
        stemmed_entries = []
        original_entries = []
        entry_id = 0
        for filename in self.files():

            uid = uidfind(filename)[0]

            dom = lxml.html.fromstring(open(filename).read())
            self.dom = dom
            elements = dom.cssselect(self.tags)
            elements.append(dom.makeelement('SENTINEL'))
            lasttag = 'p'
            text_l = []
            best_id = None
            title = None

            for i, e in enumerate(elements):
                if e.tag != 'p' and lasttag == 'p':
                    if text_l:
                        # Add this entry.
                        entry_id += 1
                        mang_text = " «br» ".join(text_l)
                        orig_text = mang_text
                        stem_text = self.stemmer(mang_text)

                        entries.append( (entry_id, uid, title, best_id, mang_text) )
                        stemmed_entries.append( (entry_id, stem_text) )
                        original_entries.append( (entry_id, orig_text) )

                        text_l = []
                        best_id = None
                        title = None

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
                for a in e.iter('a'):
                    if not best_id and 'id' in a.attrib:
                    # Choose the best id (closest to start)
                        best_id = a.attrib['id']
                        if a.text is None or regex.search('\d', a.text):
                            a.text = None
                            a.drop_tag()
                text = e.text_content()
                text = self.sanitize(text)
                text = textfunctions.mangle(text)
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
            uid TEXT,
            heading TEXT,
            bookmark TEXT,
            text TEXT)''')
        con.execute('''CREATE VIRTUAL TABLE stemmed
            USING fts4(content=entries, tokenize={}, uid, heading, bookmark, text)'''.format(self.fts_tokenizer))
        con.execute('''CREATE VIRTUAL TABLE original
            USING fts4(content=entries, tokenize=simple, uid, heading, bookmark, text)''')

        entries, original_entries, stemmed_entries = self.parse_entries()

        print(len(entries))
        con.executemany('INSERT INTO entries values(?, ?, ?, ?, ?)',
            entries)
        con.executemany('INSERT INTO stemmed (docid, text) values (?, ?)',
            stemmed_entries)
        con.executemany('INSERT INTO original (docid, text) values (?, ?)',
            original_entries)
        
        con.execute("INSERT INTO stemmed(stemmed) VALUES('optimize')")
        con.execute("INSERT INTO original(original) VALUES('optimize')")
        
        con.commit()
        os.replace(tmpfile, self.dbname)

    def count_stemmed(self, query):
        return self.execute('SELECT count(*) FROM stemmed WHERE stemmed MATCH ?', (self.stemmer(query, True), )).fetchone()[0]

    def search_stemmed(self, query, limit=10, offset=0):
        query = query.lower()

        rows = self.execute('''
            SELECT uid, heading, bookmark, demangle(snippet(stemmed, "<b>", "</b> ", " … ", -1, -40)) as snippet FROM stemmed JOIN (
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
                        {'query':query, 'squery':self.stemmer(query, True), 'limit':limit, 'offset':offset}).fetchall()

        return rows

    def count_exact(self, query):
        return self.execute('SELECT count(*) FROM original WHERE original MATCH ?', (query,)).fetchone()[0]
    
    def search_exact(self, query, limit=10, offset=0):
        query = query.lower()
        rows = self.execute('''
            SELECT uid, heading, bookmark, demangle(snippet(original, "<b>", "</b> ", " … ", -1, -40)) as snippet FROM original JOIN (
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
        exact_count = self.count_exact(query)
        stemmed_count = self.count_stemmed(query) - exact_count
        to_fetch = exact_count - offset
        exact_results = []
        stemmed_results = []
        if to_fetch > 0:
            exact_results = self.search_exact(query, limit, offset)
            if len(exact_results) == limit:
                return (exact_results, [], exact_count, stemmed_count)

        # We already have len(exact_results) results
        offset -= exact_count
        limit -= len(exact_results)

        if stemmed_count - offset > 0:
            stemmed_results = self.search_stemmed(query, limit, offset)
        return (exact_results, stemmed_results, exact_count, stemmed_count)

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
            self.qsuffixes.update(textfunctions.asciify(t) for t in self.suffixes)

            self.qindeclineables.update(self.indeclineables)
            self.qindeclineables.update(textfunctions.asciify(t) for t in self.indeclineables)

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
                    token = token[:-1] + 'ṁ'
                for i in range(min(7, int(len(token)/2 - 0.5)), 0, -1):
                    sfx = token[-i:]
                    if sfx in suffixes:
                        token = token[:-i]
                        break
            
            token = textfunctions.asciify(token)
            token = regex.sub(r'(.)\1h?', r'\1', token)
            token = regex.sub(r'(?<=[kgcjtdbp])h', r'', token)
            pieces[place] = token
        return "".join(pieces)
    
class PaliTextSearch(SectionSearch):
    fts_tokenizer = 'simple'
    rex_tokenizer = regex.compile(r'([\p{ascii}--[A-Za-z0-9_]]+)', flags=regex.V1)
    stemmer = PaliStemFilter()
    stemmer.tokenizer = rex_tokenizer

p = PaliTextSearch('pi')

def stress_test(count):
    import random, time
    terms = 'buddha dhamma sangha ānanda sariputta moggallana kassapa anuruddha'.split()
    queries = [" ".join(random.sample(terms, 2)) for i in range(count)]

    requesters = concurrent.futures.ThreadPoolExecutor(10)
    def gimmie(query):
        res = p.search(query, 10, 0)
        return len(res[0])+len(res[1])
    start=time.time()
    results = list(requesters.map(gimmie, queries))
    return time.time() - start