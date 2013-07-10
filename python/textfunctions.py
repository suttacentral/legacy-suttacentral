import regex, unicodedata

def simplify(string, langcode):
    if langcode == 'pi':
        return simplify_pali(string)
    else:
        return string

def simplify_pali(string):
    rules = (
        (r'\P{alpha}', r''), #Non-alphabetical characters
        (r'nny', 'nn'), # nny (ññ) -> n
        (r'(.)(?=\1)', r''), #Remove duplicates
        (r'[ṁṃṅ](?=[gk])', r'n'), # 'n' before a 'g' or 'k'
        (r'by', 'vy'), # vy always, never by

    )

    out = string.casefold()
    for rule in rules:
        out = regex.sub(rule[0], rule[1], out)
    out = unicodedata.normalize('NFD', out)
    out = regex.sub(r'\p{dia}', '', out)
    if len(out) > 5:
        out = regex.sub(r'm\b', '', out) # Remove trailing m
    out = regex.sub(r'(?<=[kgcjtdbp])h', r'', out) # Remove aspiration
    return out
    return ''

import regex, unicodedata, math, itertools

def numsortkey(input, index=0):
    """ Numerical sort. Handles identifiers well.

    If variable lengths ranges are involved (i.e. 1.2 vs 1.11.111) see
    'natsortkey', which is about 20x slower but handles such cases
    gracefully.
    """
    if type(input) is str:
        string = input
    else:
        string = input[index]
        if string is None:
            return []
    return ( [int(a) if a.isnumeric() else a
                   for a in regex.split(r'(\d+)', string)] )

def normalize(string):
    return unicodedata.normalize('NFC', string)

def asciify(string):
    out = unicodedata.normalize('NFD', string)
    out = regex.sub(r'\p{dia}', '', out)
    #out = regex.sub(r'\p{dash}', '-', out)
    return out



def simple_stem_pali(string):
    " Doesn't do proper stemming. Just simplifies the form. "
    if not string:
        return string
    out = simplify_pali(string)
    if out[-1] in 'aeiou':
        return out[:-1]
    else:
        return out


def simplify(string, lang):
    if lang == 'pi':
        return simplify_pali(string)
    else:
        return ''

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

_phonhashdata = ({}, [])
for value, keys in start:
        _phonhashdata[0].update((key, value) for key in keys)


# Remove aspiration.
_phonhashdata[1].append((regex.compile(r'(?<=[KGCJDT])H', regex.I), ''))
# Reduce consonant clusters
_phonhashdata[1].append((regex.compile(r'[HYLRS]+(?![AEIOU])|(?<![^AEIOU])[HYLRS]+', regex.I), ''))
for value, keys in start:
    _phonhashdata[1].append((regex.compile(r'['+keys+r']+', regex.I), value))
del start, middle

costs = {
    # The costs dictionary is a 'pseduo mapping' of how costly it is to
    # convert one character into another. To simplfy things
    # Very cheap transformations.
    ('a', 'ā'): 2,
    ('i', 'ī'): 2,
    ('u', 'ū'): 2,
    ('by', 'vy'): 2,
    ('t', 'ṭ'): 2,
    ('d', 'ḍ'): 2,
    ('l', 'ḷ'): 2,
    ('ṁ', 'ṅ'): 1,
    ('m', 'ṁ'): 2,

    # Moderately cheap transformations.
    ('c', 'j'): 4,
    ('b', 'p'): 4,
    ('c', 'k'): 4,
    ('a', 'e'): 4,
    ('a', 'o'): 4,
    ('e', 'i'): 4,
    ('o', 'u'): 4,

    }

costs.update( ((c, c+'h'), 2) for c in 'kgcjḍṭdt')
costs.update( (('n', c), 2) for c in 'ñṁṅṇ')
costs.update( (('a', c), 4) for c in 'eo')
# Everything else '7'

assert all(list(key) == sorted(key) for key in costs), 'Out of order.'

_syllabalize = regex.compile(r'([^aiueoāīū\s]*)([aiueoāīū])((?!br|[kgcjdt]h)[^aiueoāīū\s](?=[^aiueoāīū\s]))?').findall

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
    if start == 'A' == rest[1]:
        return rest[1:1+length]
    else:
        return start + rest[1:length]

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
nat_cons = {'t', 's', 'n', 'ṁ', 'v', 'p', 'm', 'r', 'y', 'k', 'bh', 'd', 'h', 'ss', 'c', 'kkh', 'tt', 'g', 'nt', 'dh', 'l', 'kh', 'ṇ', 'mm', 'j', 'th', 'ññ', 'tth', 'bb', 'pp', 'ṭ', 'cc', 'ṭṭh', 'nn', 'yy', 'ñc', 'tv', 'cch', 'jj', 'ddh', 'gg', 'mp', 'kk', 'sm', 'b', 'nd', 'br', 'hm', 'ṁs', 'jjh', 'ṅk', 'ṁgh', 'ṅg', 'ṇḍ', 'dd', 'ṇṇ', 'ṭh', 'ṁv', 'ch', 'gh', 'll', 'ṅkh', 'mb', 'ph', 'by', 'ndh', 'mh', 'ḷ', 'ṇh', 'dv', 'ñj', 'bbh', 'mbh', 'tr', 'ñ', 'ñh', 'ṁy', 'jh', 'ndr', 'yh', 'sv', 'ḍḍh', 'ly', 'ḷh', 'ṭṭ', 'mph', 'ṁk', 'pph', 'vh', 'ṇṭh', 'ṁh', 'ky', 'nth', 'ṅgh', 'ntv', 'ggh', 'khv', 'nv', 'ṁkh', 'nh', 'ṁp', 'dr', 'ḍḍ', 'ṁd', 'ḍ', 'yv', 'gr', 'ṁm', 'ñch', 'ṁn', 'ty', 'ṇṭ', 'ṁg', 'gy', 'my', 'kl', 'ṅkhy', 'sn', 'ṁr', 'ṁj', 'ṁbh', 'kv', 'ṁdh', 'st', 'ñjh', 'ṁc', 'ṁnh', 'ṁt', 'pl', 'nty', 'ṁb', 'hv', 'ṁph', 'ṇy', 'sy', 'kr', 'ṁch', 'ṁsv', 'ṁsm', 'ṁl', 'ṁtv', 'ṁdv', 'hy', 'tthy', 'dm', 'ny', 'tn', 'ṅkhv', 'khy', 'ṁṭh', 'dhv', 'kkhy', 'pv', 'ḍh', 'ṁth'}

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
transform_cost[ ('ṁ', 'ṅ') ] = 5
transform_cost[ ('m', 'ṅ') ] = 5
transform_cost[ ('c', 'j') ] = 20
transform_cost[ ('b', 'p') ] = 30
transform_cost[ ('by', 'vy') ] = 10

for key in transform_cost:
    if tuple(sorted(key)) != key:
        print(key)
        raise

def trans_cost(cc1, cc2, _cache={}):
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

vowelsplitrex = regex.compile(r'([aeiouāīū]+)').split
def mc4(word1, word2):
    pieces1 = vowelsplitrex(word1.lower())
    pieces2 = vowelsplitrex(word2.lower())
    pairs = [tuple(sorted(t)) for t in itertools.zip_longest(pieces1, pieces2, fillvalue='')]
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
            cost += transform_cost.get(pair, 50) * mod
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
                    cost += transform_cost[pair]
                except KeyError:
                    if phonhash(pair[0]) == phonhash(pair[1]):
                        cost += 50
                    else:
                        cost += 80

    return cost

def mc4_boost(freq, factor=100):
    return math.log(factor) / math.log(factor + freq)

_unused = set(range(1, 31))
_unused.remove(1)
_unused = sorted(_unused)
_uni   = '–—‘’“”…'
_ascii = "".join(chr(_unused[i]) for i in range(1, 1+len(_uni)))

def mangle(string, _trans=str.maketrans(_uni, _ascii)):
    "Mangle unicode puncuation into unused ascii characters"
    return string.translate(_trans)

def demangle(string, _trans=str.maketrans(_ascii, _uni)):
    "Demangle unused ascii characters into unicode puncuation"
    return string.translate(_trans)

del _ascii, _uni, _unused