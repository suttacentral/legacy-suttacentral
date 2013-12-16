
import regex, os, hashlib, collections, unicodedata

def naivesortkey(string):
    """Naive human sort. Much faster than natsortkey, but not as robust.

    Useful in cases where input strings are uniform. Where ranges with a
    variable number of entries exist (for example: 1, 1.1, 1.1.1) it is
    nessecary to use natsortkey instead.

    """
    #      paranthesis to allow linebreak in list comprehension
    return ( [int(a) if a.isnumeric() else a 
                    for a in regex.split(r'(\d+)', string)] )

def natsortkey(string):
    r"""Natural (human) sort.

    This version of natural sort is indifferent to hyphens, periods and
    endashes (–) seperating numbers. One difference between this and the
    naive algorithm is it compares number clusters as discrete units.

    naive natural sort:
    >>> print(naivesortkey('foo1:2'), naivesortkey('foo1.1:2.1'), sep='\n')
    ['foo', 1, ':', 2, '']
    ['foo', 1, '.', 1, ':', 2, '.', 1, '']
    
    natsortkey:
    >>> print(natsortkey('foo1:2'), natsortkey('foo1.1:2.1'), sep='\n')
    ['foo', (1,), ':', (2,), '']
    ['foo', (1, 1), ':', (2, 1), '']
    
    >>> naivesortkey('foo1:2') < naivesortkey('foo1.1:2.1')
    False
    
    >>> natsortkey('foo1:2') < natsortkey('foo1.1:2.1')
    True
    
    Note that periods are NOT treated as decimal points.
    This is for the sake of sorting dates and other 'dotted' series which
    would be sorted wrongly if treated as decimal numbers.
    >>> sorted(['1.3.1', '1.10.1', '10.1.2', '1.2.1'], key=natsortkey)
    ['1.2.1', '1.3.1', '1.10.1', '10.1.2']
    
    As per above, leading zeros are ignored.
    >>> natsortkey('007') == natsortkey('7')
    True
    
    >>> natsortkey('1.1') == natsortkey('1.001')
    True
    
    Strings which cannot be meaningfully compared will still be ordered.
    >>> sorted(['foo', '42', '41', 'h4.1', 'halp!'], key=natsortkey)
    ['41', '42', 'foo', 'h4.1', 'halp!']
    
    """

    # This code is perhaps 5x slower than naivesortkey. 
    
    string = regex.sub(r'(?<=\d)[–-](?=\d)', '.', string)
    key = regex.split(r'(\d++(?:[\d.]*(?<!\.)))', string)
    for i, piece in enumerate(key):
        if i % 2 == 1:
            key[i] = tuple(int(a) for a in regex.findall(r'\d+', piece))
    return key


def palisortkey(input, _charvalue = {}):
    """sorts strings into pali alphabetical order"""
    if len(_charvalue) == 0:
        charInorder = [
            '#', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'ā',
            'i', 'ī', 'u', 'ū', 'e', 'o', 'ṃ', 'k', 'kh', 'g', 'gh', 'ṅ', 'c',
            'ch', 'j', 'jh', 'ñ', 'ṭ', 'ṭh', 'ḍ', 'ḍh', 'ṇ', 't', 'th', 'd',
            'dh', 'n', 'p', 'ph', 'b', 'bh', 'm', 'y', 'r', 'l', 'ḷ', 'v', 's', 'h',
        ]
        for i in range(0, len(charInorder)):
            c = charInorder[i]
            _charvalue[c] = i * 2
            if c != c.upper():
                _charvalue[c.upper()] = i * 2 - 1
        del charInorder
    mult = len(_charvalue)
    vals = []
    for i in range(0, len(input)):
        val = 0
        c1 = input[i]
        c2 = input[i:i+2]
        if c2 in _charvalue:
            val = _charvalue[c2]
            i += 1
        elif c1 in _charvalue:
            val = _charvalue[c1]
        vals.append(val)
    return tuple(vals)

def simple_to_pali(pattern):
    r"""Convert a simple pattern into a pattern which will match pali

    >>> simple_to_pali('buda')
    'bh?[uū][dḍ]{1,2}h?[aā]'

    >>> regex.search("(?i)" + simple_to_pali('buda'), 'The Buddha')[0]
    'Buddha'

    >>> regex.search("(?i)" + simple_to_pali('sammaditthi'),
    ...     '—sammādiṭṭhi sammāsaṅkappo …')[0]
    'sammādiṭṭhi'

    >>> simple_to_pali('sammaditthi')
    's[aā][mṁṃ][mṁṃ][aā][dḍ]{1,2}h?[iī][tṭ][tṭ]h[iī]'

    >>> simple_to_pali('sammādiṭṭhi')
    's[aā][mṁṃ][mṁṃ]ā[dḍ]{1,2}h?[iī]ṭṭh[iī]'

    """
    rexrules = (
            (r'([kgcjtdbp])(?!h)(?=[aāiīuūoe])', r'\1h?'),
            (r'(?<!\b|[kgcjtdnpbmyls])([kgcjtdnpbmyls])(?![kgcjtdnpbmyls])', r'\1{1,2}'),
            (r'n(?=[kg])', r'[ṅṁṃ]'),
        )
    reprules = (
            (r't', r'[tṭ]'),
            (r'd', r'[dḍ]'),
            (r'n', r'[nṇṅñ]'),
            (r'm', r'[mṁṃ]'),
            (r'a', r'[aā]'),
            (r'i', r'[iī]'),
            (r'u', r'[uū]'),
            (r'vy', r'[vb]y'),
            (r'by', r'[vb]y'),
        )
    for rule in rexrules:
        pattern = regex.sub(rule[0], rule[1], pattern, regex.I)
    for rule in reprules:
        pattern = pattern.replace(rule[0], rule[1])
    return pattern

de_diacritical = str.maketrans('ṭḍṇṅñṁṃḷāīū“”‘’', 'tdnnnmmlaiu""\'\'')

def pali_to_simple(string, _rules = (
        (r'(.)(?=\1)', r''), #Remove duplicates
        (r'(?<=[kgcjtdbp])h', r''), # Remove aspiration
        (r'[ṁṃṅ](?=[gk])', r'n'), # 'n' before a 'g' or 'k'
        (r'by', 'vy'), # vy always, never by
    )):

    pattern = string
    for rule in _rules:
        pattern = regex.sub(rule[0], rule[1], pattern)
    pattern = unicodedata.normalize('NFD', pattern)
    pattern = regex.sub(r'\p{dia}', '', pattern)
    pattern = regex.sub(r'(?<=\w{3})m\b', '', pattern)
    return pattern

def AdvancableCounter(value):
    """A counter which can be advanced but cannot be rewound
    
    >>> ad = AdvancableCounter(1)
    >>> print(next(ad), next(ad), next(ad), next(ad), next(ad))
    1 2 3 4 5

    >>> ad.send(10)
    10

    >>> next(ad)
    11

    >>> ad.send(10)
    Traceback (most recent call last):
    ValueError: Counter may be advanced, but may not be rewound.
    """
    while True:
        value += 1
        tmp = (yield value - 1)
        if tmp is not None:
            if tmp < value:
                raise ValueError('Counter may be advanced, but may not be rewound.')
            value = tmp

def fileiter(src, ext=None, rex=None):
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
    extrex = regex.compile(r'.*\.(.*)')
    for dirpath, dirnames, filenames in os.walk(src):
        for infile in (os.path.join(dirpath, a) for a in filenames):
            if ext is not None:
                m = extrex.search(infile)
                if m is None:
                    if ext != '':
                        continue
                else:
                    if m[1] not in ext:
                        continue
            if rex is not None:
                if rex.search(m) is None:
                    continue
            yield infile

def generate_name(*args):
    result = []
    for arg in args:
        if type(arg) is str:
            result.append(arg)
            
        else:
            result.extend(arg)
    return hashlib.md5("".join(result).encode()).hexdigest()


    

"""
A persistent (sqlite3) python dictionary

Based on:
http://erezsh.wordpress.com/2009/05/31/filedict-bug-fixes-and-updates/
Author: Erez Shinan
Date: 31-May-2009

Copyright 2010 Matteo Bertini <matteo@naufraghi.net>
Python Software Foundation License (PSFL)
"""

import pickle
import sqlite3

sqlite3.register_converter("PICKLE", pickle.loads)
sqlite3.register_adapter(set, pickle.dumps)
sqlite3.register_adapter(frozenset, pickle.dumps)


class PList(collections.abc.Sequence):
    """A persistent list built on SQLite

    PList has only limited mutability and no search capability.
    By default it uses the pickle module to store values. This means
    that only things which can be pickled can be stored.

    >>> p = PList(":memory:", sqltype="STRING")
    >>> p.extend( ("foo", "bar", "baz") )
    >>> list(p)
    ['foo', 'bar', 'baz']

    >>> p[0]
    'foo'

    >>> len(p)
    3

    >>> q = PList(":memory:")
    >>> q.extend( [1, (4, 2), "Python"] )
    >>> q[1]
    (4, 2)

    """
    
    def __init__(self, filename, sqltype="PICKLE"):
        self.filename = filename
        self.sqltype = sqltype
        sqlite3.register_converter
        self._conn = sqlite3.connect(filename,
                            detect_types=sqlite3.PARSE_DECLTYPES)
        self._conn.execute("CREATE TABLE IF NOT EXISTS list(idx INTEGER PRIMARY KEY, value {})".format(self.sqltype))
        self._conn.commit()
        
    def __getitem__(self, index):
        try:
            return self._conn.execute("SELECT value FROM list WHERE idx=?", (index + 1,)).fetchone()[0]
        except TypeError:
            raise IndexError("{} not in PList".format(index))
    
    def __iter__(self):
        return (a for (a,) in self._conn.execute("SELECT value FROM list"))

    def __len__(self):
        return self._conn.execute("SELECT COUNT(*) FROM list;").fetchone()[0]
    
    def append(self, value):
        self.extend( (value,) )
    
    def extend(self, values):
        if self.sqltype == "PICKLE":
            # Note we use a list comprehension rather than a generator
            # to ensure everything pickles before anything is entered.
            self._conn.executemany("INSERT OR REPLACE INTO list (value) values (?);", [(pickle.dumps(a),) for a in values])
        else:
            self._conn.executemany("INSERT OR REPLACE INTO list (value) values (?);", ((a,) for a in values))
        self._conn.commit()
    
    def clear(self):
        self._conn.execute("DELETE FROM list")

class SqliteDict(collections.abc.MutableMapping):
    "A dictionary that stores its data persistently in a database"

    def __init__(self, filename, keytype="STRING", valuetype="PICKLE", flag='c', protocol=-1, writeback=False):
        self.filename = filename
        self.flag = flag
        self.protocol = protocol
        self.writeback = writeback
        self.types = (keytype, valuetype)
        # flag as in http://docs.python.org/library/anydbm.html#anydbm.open
        if flag in ('r', 'w'):
            if not os.path.exists(filename):
                raise IOError("File {0!r} missing!".format(filename))

        sqlite3.register_converter("PICKLE", self._loads)
        self._conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES)
        if flag == 'n':
            self._dbdrop()
        if flag in ('n', 'c'):
            self._dbcreate()

    def _dbdrop(self):
        self._conn.execute("DROP TABLE IF EXISTS dict;")
        self._conn.commit()

    def _dbcreate(self):
        self._conn.execute("""CREATE TABLE IF NOT EXISTS dict (idx INTEGER PRIMARY KEY, key {} UNIQUE, value {});""".format(*self.types))
        
        self._conn.execute("CREATE INDEX IF NOT EXISTS dict_index ON dict(key);")
        self._conn.commit()

    def _commit(self):
        if self.writeback:
            self._conn.commit()

    def _dumps(self, value):
        return pickle.dumps(value, self.protocol)
    def _loads(self, blob):
        return pickle.loads(blob)

    def __getitem__(self, key):
        cursor = self._conn.execute("SELECT value FROM dict WHERE key=?;", (key,))
        for (value,) in cursor:
            return value
        raise KeyError(key)

    def _setitems(self, items):
        parameters = ((key, self._dumps(value)) for key, value in items)
        self._conn.executemany("INSERT OR REPLACE INTO dict (key, value) values (?, ?);", parameters)
        self._commit()

    def __setitem__(self, key, value):
        self._setitems([(key, value)])

    def __delitem__(self, key):
        cursor = self._conn.execute("DELETE FROM dict WHERE key=?;", (key,))
        if cursor.rowcount <= 0:
            raise KeyError(key)
        self._commit()

    def update(self, d):
        self._setitems(d.items())

    def iterkeys(self):
        return (a[0] for a in self._conn.execute("SELECT key FROM dict;"))
    def itervalues(self):
        return (a[0] for a in self._conn.execute("SELECT value FROM dict;"))
    def iteritems(self):
        return ((k[0], v[0]) for (k, v) in self._conn.execute("SELECT key, value FROM dict;"))

    def __iter__(self):
        return self.iterkeys()
    def keys(self):
        return list(self.iterkeys())
    def values(self):
        return list(self.itervalues())
    def items(self):
        return list(self.iteritems())

    def __contains__(self, key):
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

    def __len__(self):
        return self._conn.execute("SELECT COUNT(*) FROM dict;").fetchone()[0]

    def close(self):
        self.sync()
        self._conn.close()

    def sync(self):
        self._conn.commit()

    def __del__(self):
        self.close()