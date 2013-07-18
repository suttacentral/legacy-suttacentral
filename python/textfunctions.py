import regex as _regex, unicodedata as _unicodedata, math as  _math
import itertools as _itertools

def numsortkey(input, index=0):
    """ Numerical sort. Handles identifiers well.

    Variable length ranges (i.e. 1.2 vs 1.11.111) are not handled gracefully.
    """
    if type(input) is str:
        string = input
    else:
        string = input[index]
        if string is None:
            return []
    return ( [int(a) if a.isnumeric() else a
                   for a in _regex.split(r'(\d+)', string)] )

def simplify_pali(string):
    rules = (
        (r'\P{alpha}', r''), #Non-alphabetical characters
        (r'nny', 'nn'), # nny (ññ) -> n
        (r'(.)(?=\1)', r''), #Remove duplicates
        (r'[mṁṃṅ](?=[gk])', r'n'), # 'n' before a 'g' or 'k'
        (r'by', 'vy'), # vy always, never by
    )

    out = string.casefold()
    for rule in rules:
        out = _regex.sub(rule[0], rule[1], out)
    out = _unicodedata.normalize('NFD', out)
    out = _regex.sub(r'\p{dia}', '', out)
    if len(out) > 5:
        out = _regex.sub(r'm\b', '', out) # Remove trailing m
    out = _regex.sub(r'(?<=[kgcjtdbp])h', r'', out) # Remove aspiration
    return out
    return ''

def simplify_english(string):
    rules = (
        (r'(.)(?=\1)', r''),
        (r'(?<=\w)[sc]', r'c'),
        (r'(?<=\w)[aou]+', r'a'),
        (r'(?<=\w)[ie]+', r'i'),
        (r'ia', 'ai'),
        )
    out = string
    for rule in rules:
        out = _regex.sub(rule[0], rule[1], out)
    return out

def simplify(string, langcode, default=None):
    if langcode == 'pi':
        return simplify_pali(string)
    elif langcode == 'en':
        return simplify_english(string)
    else:
        return default

def normalize(string):
    return _unicodedata.normalize('NFC', string)

def asciify(string):
    out = _unicodedata.normalize('NFD', string)
    out = _regex.sub(r'\p{dia}', '', out)
    out = out.replace('\xad', '')
    #out = _regex.sub(r'\p{dash}', '-', out)
    return out

def vel_to_uni(string):
    # Note: In python, literals/constants (such as tuples) in a function
    # are compiled into the function - the tuple is not re-created on each
    # call. Python is basically awesome :).
    rules = (
        ('aa', 'ā'),
        ('ii', 'ī'),
        ('uu', 'ū'),
        ('.t', 'ṭ'),
        ('.d', 'ḍ'),
        ('~n', 'ñ'),
        ('.n', 'ṇ'),
        ('"n', 'ṅ'),
        ('.l', 'ḷ'),
        ('.m', 'ṃ'),
        )

    for rule, repl in rules:
        string = string.replace(rule, repl)
    return string

def _build_phonhashdata():
    # Generate Phonetic Hash Data
    start = (('A', 'AEIOU'),
            ('B', 'BFPVW'),
            ('C', 'CGJKQSXZ'),
            ('D', 'DT'),
            ('H', 'H'),
            ('R', 'RL'),
            ('M', 'MN'),
            ('Y', 'Y'))

    middle =(
            ('A', 'AEIOUYRL'),
            ('B', 'BFPVW'),
            ('C', 'CGJKQSXZH'),
            ('D', 'DT'),
            ('M', 'MN'))

    phonhashdata = ({}, [])
    for value, keys in start:
            phonhashdata[0].update((key, value) for key in keys)

    # Remove aspiration.
    phonhashdata[1].append((_regex.compile(r'(?<=[KGCJDT])H', _regex.I), ''))
    # Reduce consonant clusters
    phonhashdata[1].append((_regex.compile(r'[HYLRS]+(?![AEIOU])|(?<![^AEIOU])[HYLRS]+', _regex.I), ''))
    for value, keys in start:
        phonhashdata[1].append((_regex.compile(r'['+keys+r']+', _regex.I), value))
    
    return phonhashdata

_phonhashdata = _build_phonhashdata()
_syllabalize = _regex.compile(r'([^aiueoāīū\s]*)([aiueoāīū])((?!br|[kgcjdt]h)[^aiueoāīū\s](?=[^aiueoāīū\s]))?').findall

def phonhash(word, length=4):
    " Generate a phonetic hash for word "
    if not word:
        return word
    word = asciify(word)
    start = _phonhashdata[0].get(word[0].upper(), '')
    if len(word) == 1:
        return start
    rest = word
    for reg, repl in _phonhashdata[1]:
        rest = reg.sub(repl, rest, pos=1)
    if len(rest) == 1:
        return start
    if start == 'A' == rest[1]:
        return rest[1:1+length]
    else:
        return start + rest[1:length]

def _build_transform_cost():
    vowel_costs_table = {
        ('a', 'ā'): 10,
        ('i', 'ī'): 10,
        ('u', 'ū'): 10,
        ('a', 'e'): 30,
        ('a', 'o'): 30,
        ('i', 'e'): 25,
        ('u', 'o'): 25,
        }

    vowel_costs_map = {tuple(sorted(key)): value for key, value in vowel_costs_table.items()}

    # This is a Counter of all naturally occuring consonant clusters in the pali canon
    nat_cons = {'t', 's', 'n', 'ṃ', 'v', 'p', 'm', 'r', 'y', 'k', 'bh', 'd', 'h', 'ss', 'c', 'kkh', 'tt', 'g', 'nt', 'dh', 'l', 'kh', 'ṇ', 'mm', 'j', 'th', 'ññ', 'tth', 'bb', 'pp', 'ṭ', 'cc', 'ṭṭh', 'nn', 'yy', 'ñc', 'tv', 'cch', 'jj', 'ddh', 'gg', 'mp', 'kk', 'sm', 'b', 'nd', 'br', 'hm', 'ṃs', 'jjh', 'ṅk', 'ṃgh', 'ṅg', 'ṇḍ', 'dd', 'ṇṇ', 'ṭh', 'ṃv', 'ch', 'gh', 'll', 'ṅkh', 'mb', 'ph', 'by', 'ndh', 'mh', 'ḷ', 'ṇh', 'dv', 'ñj', 'bbh', 'mbh', 'tr', 'ñ', 'ñh', 'ṃy', 'jh', 'ndr', 'yh', 'sv', 'ḍḍh', 'ly', 'ḷh', 'ṭṭ', 'mph', 'ṃk', 'pph', 'vh', 'ṇṭh', 'ṃh', 'ky', 'nth', 'ṅgh', 'ntv', 'ggh', 'khv', 'nv', 'ṃkh', 'nh', 'ṃp', 'dr', 'ḍḍ', 'ṃd', 'ḍ', 'yv', 'gr', 'ṃm', 'ñch', 'ṃn', 'ty', 'ṇṭ', 'ṃg', 'gy', 'my', 'kl', 'ṅkhy', 'sn', 'ṃr', 'ṃj', 'ṃbh', 'kv', 'ṃdh', 'st', 'ñjh', 'ṃc', 'ṃnh', 'ṃt', 'pl', 'nty', 'ṃb', 'hv', 'ṃph', 'ṇy', 'sy', 'kr', 'ṃch', 'ṃsv', 'ṃsm', 'ṃl', 'ṃtv', 'ṃdv', 'hy', 'tthy', 'dm', 'ny', 'tn', 'ṅkhv', 'khy', 'ṃṭh', 'dhv', 'kkhy', 'pv', 'ḍh', 'ṃth'}

    transform_cost = dict()
    
    # Transform from double to single (20)
    for key in nat_cons:
        if len(key) > 1 and key[0] == key[1]:
            akey = asciify(key[1:])
            transform_cost[ tuple(sorted((asciify(key[1:]), key))) ] = 35 # Some will get replaced later.
            transform_cost[ tuple(sorted((key[1:], key))) ] = 20

    # Allow cheap transformations from ascii -> diacritical
    for key in nat_cons:
        akey = asciify(key)
        if akey != key:
            transform_cost[(akey, key)] = 10

    transform_cost.update( (tuple(sorted(key)), value) for key, value in vowel_costs_table.items() )

    # Self-transformation is free.
    transform_cost.update( {(key[0], key[0]) : 0 for key in transform_cost} )
    transform_cost.update( {(key, key) : 0 for key in nat_cons} )

    # Sanskrit -> Pali (cheap because they don't exist in pali)
    transform_cost[ ('mm', 'rm') ] = 5
    transform_cost[ ('bb', 'rv') ] = 5

    # Special cases
    transform_cost[ ('ṃ', 'ṅ') ] = 5
    transform_cost[ ('m', 'ṅ') ] = 5
    transform_cost[ ('c', 'j') ] = 20
    transform_cost[ ('b', 'p') ] = 30
    transform_cost[ ('by', 'vy') ] = 10

    for key in transform_cost:
        if tuple(sorted(key)) != key:
            print(key)
            raise
    return transform_cost
_transform_cost = _build_transform_cost()

def _trans_cost(cc1, cc2, _cache={}):
    "Cost of transforming one consonant cluster into another"
    if cc1 == cc2:
        return 0

    opair = pair = tuple(sorted( [cc1, cc2] ))
    try:
        return _cache[ pair ]
    except KeyError:
        pass

    cost = 0

    if pair[0][-1] != 'h' and pair[1][-1] == 'h':
        cost += 15
        pair = tuple(sorted( [pair[0], pair[1][:-1]] ))
    try:
        cost += transform_cost[pair]
    except KeyError:
        print(opair, end="  ")
        cost += 80
    _cache[opair] = cost
    return cost

_vowelsplitrex = _regex.compile(r'([aeiouāīū]+)').split
def mc4(word1, word2):
    pieces1 = _vowelsplitrex(word1.lower())
    pieces2 = _vowelsplitrex(word2.lower())
    pairs = [tuple(sorted(t)) for t in _itertools.zip_longest(pieces1, pieces2, fillvalue='')]
    cost = 0
    # Vowels

    for i, pair in enumerate(pairs):
        if pair[0] == pair[1]:
            continue
        if pair[0] == '' or pair[1] == '':
            cost += 800 / (5 + i)
        if i % 2 == 1:
            mod = 1
            if i <= len(pairs) - 1:
                mod = 0.66
            cost += _transform_cost.get(pair, 50) * mod
        else:
            try:
                cost += transform_cost[pair]
            except KeyError:
                try:
                    if pair[0][-1] != 'h' and pair[1][-1] == 'h':
                        cost += 15
                        pair = tuple(sorted((pair[0], pair[1][:-1])))
                except IndexError:
                    pass
                try:
                    cost += _transform_cost[pair]
                except KeyError:
                    if phonhash(pair[0]) == phonhash(pair[1]):
                        cost += 50
                    else:
                        cost += 80

    return cost

def mc4_boost(freq, factor=100):
    return _math.log(factor) / _math.log(factor + freq)

_unused = set(range(1, 31))
_unused.remove(1)
_unused = sorted(_unused)
_uni   = '–—‘’“”… '
_ascii = "".join(chr(_unused[i]) for i in range(1, 1+len(_uni)))

def mangle(string, _trans=str.maketrans(_uni, _ascii)):
    "Mangle unicode puncuation into unused ascii characters"
    return string.translate(_trans)

def demangle(string, _trans=str.maketrans(_ascii, _uni)):
    "Demangle unused ascii characters into unicode puncuation"
    out = string.translate(_trans)
    out = string[:36].replace('«br»', ' ')+string[36:]
    return out.replace('«br»', '<br>')

del _ascii, _uni, _unused