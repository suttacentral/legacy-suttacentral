import collections
import lxml.html
import regex
import sqlite3
import sys
from pathlib import Path

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
from sc import config, textfunctions

sys.path.insert(1, str(config.dict_sources_dir))
import cped_data

class PrettyRow(sqlite3.Row):
    def __repr__(self):
        out = []
        out.append("<PrettyRow:")
        for key in self.keys():
            out.append("['{}']={}".format(key, self[key]))
        out[-1] += ' >'
        return "\n".join(out)

def create_brief(string, max_length=150):
    # Filter out references. 'remove any string of alphanumerical and periods
    # which doesn't consist soley of alphabetical characters.
    #string = regex.sub(r'[\w.]+', lambda m: m[0] if m[0].isalpha() else '', string)
    string = regex.sub(r'\b[\w.]+\b(?<!\b\p{alpha}+\b)', '', string)
    
    if len(string) <= max_length:
        return string
    
    string = string[:max_length + 1]
    # 'r' flag causes the regex to search in reverse
    m = regex.search(r'(?r)(.*)[^,—.]*', string)
    if m and m[1]:
        return m[1]
    else:
        return regex.sub(r'\S+$', '', string)

# Create the database.
db_path = config.dict_db_path
tmp_db_path = db_path.with_suffix('.sqlite.tmp')
try:
    tmp_db_path.unlink()
except OSError:
    pass
con = sqlite3.connect(str(tmp_db_path))
#con.execute('PRAGMA foreign_keys = ON')
con.execute('PRAGMA synchronous = 0') # Much faster and we don't want a partial database.
con.row_factory = PrettyRow

# html is what should be delivered to the web browser. text is what
# should be used to generate snippets. Only text is searched.
con.execute('''CREATE TABLE entries_base (
    entry_id INTEGER PRIMARY KEY,
    term_id INTEGER,
    alt_terms TEXT,
    html HTMLTEXT, --recognized as 'TEXT' by sqlite
    text TEXT,
    info TEXT,
    dict_id INTEGER)''')

# Create an external content fts4 table which mirrors entries.
# We will use this table for all actual queries.
# The reason for this sleight of hand is that you can insert lowercase
# entries into an external content fts4 table, but it will return the
# properly-cased results from the content table. This even works with
# snippets! This handily works around sqlite3's case-sensitivity for
# codepoints > 127 and there is virtually no overhead.
# The other benefit is that only those fields which actually need to be
# indexed by fts4 get indexed.
con.execute('''CREATE VIRTUAL TABLE entries USING fts4(
    content="entries_base",
    tokenize=porter,
    entry_id,
    term_id,
    alt_terms,
    html,
    text,
    info,
    dict_id)
    ''')

# Note that more than one term may reference an entry. Every entry
# must be linked with at least one term.
con.execute('''CREATE TABLE terms_base (
    term_id INTEGER PRIMARY KEY,
    base_id INTEGER,
    term TEXT,
    number INTEGER,
    phon_hash TEXT,
    boost REAL,
    entry_id INTEGER)''')

con.execute('''CREATE VIRTUAL TABLE terms USING fts4(
    content="terms_base",
    tokenize=simple,
    term_id,
    base_id,
    term,
    number,
    phon_hash,
    boost,
    entry_id)''')

# References are optional.
con.execute('''CREATE TABLE refs (
    entry_id INTEGER,
    collection TEXT,
    vol INTEGER,
    page_start INTEGER,
    page_end INTEGER)''')


con.execute('''CREATE TABLE dicts (
    dict_id INTEGER PRIMARY KEY,
    abbrev TEXT,
    name TEXT,
    author TEXT,
    about TEXT,
    details TEXT
    )''')

class Ref:
        def __init__(self, vol, book, page, page_end):
            self.div = vol
            self.book = book
            self.page = int(page) if page else None
            self.page_end = int(page_end) if page_end else self.page
        def __iter__(self):
            return [self.vol, self.book, self.page, self.page_end]

dict_id = 0
entry_id = 0
term_id = 0

def build_dppn():
    global dict_id, entry_id, term_id, con

    dict_path = config.dict_sources_dir / 'sc_dppn.html'
    with dict_path.open('r', encoding='utf-8') as f:
        dom = lxml.html.fromstring(f.read())

    # Perform sanity-correction
    items = list(dom.cssselect('meta, person, place, thing'))
    for e in items:
        if e.getparent() != dom:
            dom.append(e)

    # Populate dictionary information.
    dict_id += 1
    metas = dom.cssselect('meta')
    author = metas[1].attrib['content']
    about = metas[0].attrib['content']
    details = metas[2].attrib['content']
    con.execute('INSERT INTO dicts VALUES(?, ?, ?, ?, ?, ?)',
        (dict_id, 'EBPN', 'Early Buddhism Proper Names',
        author, about, details))

    # Used to process references in DPPN
    refrex = regex.compile(r'(\w+)(?:[.]([ivxml]+|p))?[.](\d+)(?:–(\d+))?')

    count = collections.Counter()

    def loc(e):
        e.attrib['class'] = 'location'
        ll = e.text
        if ll and ll[0].isdigit():
            e.tag = 'a'
            ll = ll.replace(' ', '')
            e.attrib['href'] = 'http://maps.google.com.au/maps?ll={}'.format(ll)
            e.text = '^ see location '
        else:
            if ll:
                e.tag = 'span'
            else:
                if e.getnext().tag == "precision":
                    e.getnext().drop_tree()
                e.drop_tree()
        
    tfn = {'ref': ('a', 'ref'),
            'description': None,
            'place': ('div', 'place'),
            'person': ('div', 'person'),
            'thing': ('div', 'thing'),
            'location': loc,
            'precision': ('span', 'precision'),
            'type': ('span', 'type'),}            

    for entry in dom.cssselect('person, place, thing'):
        entry_id += 1

        html = lxml.html.tostring(entry, encoding='utf8').decode()
        
        name_rows = []
        for i, e in enumerate(entry.iter('name')):
            name = e.text_content().strip()
            try:
                html_id = e.attrib['id']
            except KeyError:
                html_id = None
            count.update([name])
            boost = textfunctions.mc4_boost(len(html), 1000)
            if i > 0:
                boost = (1 + i + boost) / (2 + i)
            term_id += 1
            name_rows.append([
                            term_id,
                            0,
                            name,
                            count[name],
                            textfunctions.phonhash(name) if name else None,
                            boost,
                            entry_id])
            e.drop_tree()
        alt_names = ", ".join(r[2] for r in name_rows[1:])

        for e in entry.iter():
            if e.tag in tfn:
                value = tfn[e.tag]
                if value is None:
                    e.drop_tag()
                elif callable(value):
                    value(e)
                elif len(value) == 2:
                    e.tag = value[0]
                    e.attrib['class'] = value[1]
                else:
                    raise NotImplementedError
                
        html = lxml.html.tostring(entry, encoding='utf8').decode()
        html = html.replace('</a>', '</a> ').replace('<a', ' <a').replace('  ', ' ')
        
        # Destructively modify the element
        refstrs = list(t.text.strip() for t in entry.iter('ref'))
        for ref in entry.iter('ref'):
            ref.text = " " + ref.text + " "
            ref.drop_tag()

        paras = [p.text_content() for p in entry.iter('p')]
        text = " ".join(paras)
        text = regex.sub(" {2,}", " ", text)
        if paras:
            brief = create_brief(paras[0])
        else:
            brief = None

        # terms:
        # term_id, base_id, term, number, phon_hash, boost, entry_id

        con.executemany('INSERT INTO terms_base VALUES(?, ?, ?, ?, ?, ?, ?)',
            name_rows)

        # entries:
        # entry_id, term_id, html, text, brief, info, dict_id
        con.execute('INSERT INTO entries_base VALUES (?, ?, ?, ?, ?, ?, ?)',
            (entry_id, name_rows[0][0], alt_names, html, textfunctions.mangle(text), entry.tag, dict_id))

        # Populate references.
        for refstr in refstrs:
            m = refrex.match(refstr)
            try:
                values = [entry_id]
                values.extend(m[1:])
                con.execute('INSERT INTO refs VALUES (?, ?, ?, ?, ?)', values)
            except TypeError:
                print("Malformed ref: {}, ignoring.".format(refstr))
            except:
                print(values)
                raise

def build_cped():
    global dict_id, entry_id, term_id, con
    entries = cped_data.entries

    # Perform corrections and stuff on the entries data.
    # -> utf8

    for entry in entries:
        # Generate phonetic hash, and boost factor. Boost is ignored for CPED.
        entry[0] = textfunctions.vel_to_uni(entry[0])
        entry[1:1] = [textfunctions.phonhash(entry[0]), 1]
        
    CPEDRow = collections.namedtuple('CPEDRow', 'pali phonhash boost defn grammar meaning source inflectgroup inflectinfo baseword basedefn funcstem regular')
    rows = tuple(CPEDRow._make(entry) for entry in entries)

    # Populate dictionary information.
    dict_id += 1
    author = "A.P.Buddhadatta Mahāthera"
    about = ""
    details = ""
    con.execute('INSERT INTO dicts VALUES(?, ?, ?, ?, ?, ?)',
        (dict_id, 'CPED', 'Concise Pali-English Dictionary',
        author, about, details))
    terms = []
    entries = []
    search_entries = []
    for row in rows:
        term_id += 1
        entry_id += 1
        terms.append((term_id, None, row.pali, 1, row.phonhash, row.boost, entry_id))
        entries.append((entry_id, term_id, None, textfunctions.mangle(row.meaning), row.meaning, row.grammar, dict_id))
        search_entries.append((entry_id, row.meaning))
    print(len(terms), len(entries))
    # term_id, base_id, term, number, phon_hash, boost, entry_id
    con.executemany('INSERT INTO terms_base VALUES(?, ?, ?, ?, ?, ?, ?)', terms)

    # entry_id, term_id, html, text, brief, info, dict_id
    con.executemany('INSERT INTO entries_base VALUES (?, ?, ?, ?, ?, ?, ?)', entries)

build_dppn()
# Generate aliases
entries = con.execute('SELECT * FROM terms ORDER BY boost').fetchall()
names = [t['term'] for t in entries]
allterms = [t[0] for t in con.execute('SELECT term FROM terms')]
allterms = set(allterms)

for entry in entries:
    aname = textfunctions.asciify(entry['term'])
    if aname != entry['term']:
        term_id += 1
        con.execute('INSERT INTO terms_base VALUES(?, ?, ?, ?, ?, ?, ?)',
            (term_id,
            0,
            aname,
            None,
            entry['phon_hash'],
            entry['boost'] * 1.01,
            entry['entry_id']))

build_cped()

# Populate the fts4 tables with lowercased text using python str.lower
con.create_function('ulower', 1, str.casefold) # Python love :).

con.execute('INSERT INTO terms(docid, term) SELECT rowid, ulower(term) FROM terms_base')

con.execute('INSERT INTO entries(docid, text) SELECT rowid, ulower(text) FROM entries_base')

con.execute('CREATE INDEX phon_x ON terms_base(phon_hash)')
con.execute('CREATE INDEX term_id_x ON entries_base(term_id)')
con.execute('CREATE INDEX entry_id_x ON terms_base(entry_id)')
con.execute('CREATE INDEX ref_entry_id_x ON refs(entry_id)')

con.execute('ANALYZE')

con.commit()
tmp_db_path.replace(db_path)
