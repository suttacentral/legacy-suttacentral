import regex

# Some basic shims for translating js to python

rex = regex.compile

# javascript String.charAt returns a falsey value for out-of-bounds
def char_at(string, index):
    if index < 0 or index >= len(string):
        return None
    return string[index]

# Instead of long replace chains...
# also in js String.replace can take a string or RegExp
def replace(string, repls):
    for src, repl in repls:
        if isinstance(src, string):
            string = string.replace(src, repl)
        else:
            string = src.sub(repl, string)
    return string

def toUni(input):
    if not input or input == '':
        return input
    nigahita = 'ṃ'
    Nigahita = 'Ṃ'
    repls = [
        ('aa', 'ā'),
        ('ii', 'ī'),
        ('uu', 'ū'),
        (rex(r'\.t'), 'ṭ'),
        (rex(r'\.d'), 'ḍ'),
        (rex(r'\"nk'), 'ṅk'),
        (rex(r'\"ng'), 'ṅg'),
        (rex(r'\.n'), 'ṇ'),
        (rex(r'\.m'), nigahita),
        ('\u1E41', nigahita),
        (rex(r'\~n'), 'ñ'),
        (rex(r'\.l'), 'ḷ'),
        ('AA', 'Ā'),
        ('II', 'Ī'),
        ('UU', 'Ū'),
        (rex(r'\.T'), 'Ṭ'),
        (rex(r'\.D'), 'Ḍ'),
        (rex(r'\"N'), 'Ṅ'),
        (rex(r'\.N'), 'Ṇ'),
        (rex(r'\.M'), Nigahita),
        (rex(r'\~N'), 'Ñ'),
        (rex(r'\.L'), 'Ḷ'),
        (rex(r'\.ll'), 'ḹ'),
        (rex(r'\.r'), 'ṛ'),
        (rex(r'\.rr'), 'ṝ'),
        (rex(r'\.s'), 'ṣ'),
        (rex(r'"s'), 'ś'),
        (rex(r'\,h'), 'ḥ')
    ]
    return replace(input, repls)

def toUniRegEx(input):
    if not input or input == '':
     return input
    nigahita = if DPR_prefs['nigahita'] then 'ṁ' else 'ṃ'::
    Nigahita = if DPR_prefs['nigahita'] then 'Ṁ' else 'Ṃ'::
    repls = (
        ('aa', 'ā'),
        ('ii', 'ī'),
        ('uu', 'ū'),
        (rex(r'\\\.t'), 'ṭ'),
        (rex(r'\\\.d'), 'ḍ'),
        (rex(r'\"nk'), 'ṅk'),
        (rex(r'\"ng'), 'ṅg'),
        (rex(r'\\\.n'), 'ṇ'),
        (rex(r'\\\.m'), nigahita),
        ('\u1E41', nigahita),
        (rex(r'\~n'), 'ñ'),
        (rex(r'\\\.l'), 'ḷ'),
        ('AA', 'Ā'),
        ('II', 'Ī'),
        ('UU', 'Ū'),
        (rex(r'\\\.T'), 'Ṭ'),
        (rex(r'\\\.D'), 'Ḍ'),
        (rex(r'\"N'), 'Ṅ'),
        (rex(r'\\\.N'), 'Ṇ'),
        (rex(r'\\\.M'), Nigahita),
        (rex(r'\~N'), 'Ñ'),
        (rex(r'\\\,L'), 'Ḷ')
    )
    return replace(input, repls)

def toVel(input):
    if not input or input == '':
        return input
    repls = (
        ('\u0101', 'aa'),
        ('\u012B', 'ii'),
        ('\u016B', 'uu'),
        ('\u1E6D', '.t'),
        ('\u1E0D', '.d'),
        ('\u1E45', '"n'),
        ('\u1E47', '.n'),
        ('\u1E43', '.m'),
        ('\u1E41', '.m'),
        ('\u00F1', '~n'),
        ('\u1E37', '.l'),
        ('\u0100', 'AA'),
        ('\u012A', 'II'),
        ('\u016A', 'UU'),
        ('\u1E6C', '.T'),
        ('\u1E0C', '.D'),
        ('\u1E44', '"N'),
        ('\u1E46', '.N'),
        ('\u1E42', '.M'),
        ('\u00D1', '~N'),
        ('\u1E36', '.L'),
        ('ḹ', '.ll'),
        ('ṛ', '.r'),
        ('ṝ', '.rr'),
        ('ṣ', '.s'),
        ('ś', '"s'),
        ('ḥ', ',h')
    )
    return replace(input, repls)

def toVelRegEx(input):
    if not input or input == '':
        return input
    repls = (
        ('\u0101', 'aa'),
        ('\u012B', 'ii'),
        ('\u016B', 'uu'),
        ('\u1E6D', '\\.t'),
        ('\u1E0D', '\\.d'),
        ('\u1E45', '"n'),
        ('\u1E47', '\\.n'),
        ('\u1E43', '\\.m'),
        ('\u1E41', '\\.m'),
        ('\u00F1', '~n'),
        ('\u1E37', '\\.l'),
        ('\u0100', 'AA'),
        ('\u012A', 'II'),
        ('\u016A', 'UU'),
        ('\u1E6C', '\\.T'),
        ('\u1E0C', '\\.D'),
        ('\u1E44', '"N'),
        ('\u1E46', '\\.N'),
        ('\u1E42', '\\.M'),
        ('\u00D1', '~N'),
        ('\u1E36', '\\,L')
    )
    return replace(input, repls)

def toFuzzy(input):
    if not input:
        return
    input = toVel(input)
    repls = (
        (rex(r'\.([tdnlmTDNLM])'), r'\1'),
        (rex(r'~([nN])'), r'\1'),
        (rex(r'"([nN])'), r'\1'),
        ('aa', 'a'),
        ('ii', 'i'),
        ('uu', 'u'),
        ('nn', 'n'),
        ('mm', 'm'),
        ('yy', 'y'),
        ('ll', 'l'),
        ('ss', 's'),
        (rex(r'([kgcjtdpb])[kgcjtdpb]{0,1}h*'), r'\1')
    )
    return replace(input, repls)

def toSkt(input, rv):
    if not input or input == '':
        return input
    if rv:
        repls = (
            ('A', 'aa'),
            ('I', 'ii'),
            ('U', 'uu'),
            ('f', '.r'),
            ('F', '.rr'),
            ('x', '.l'),
            ('X', '.ll'),
            ('E', 'ai'),
            ('O', 'au'),
            ('K', 'kh'),
            ('G', 'gh'),
            ('N', '"n'),
            ('C', 'ch'),
            ('J', 'jh'),
            ('Y', '~n'),
            ('w', '.t'),
            ('q', '.d'),
            ('W', '.th'),
            ('Q', '.dh'),
            ('R', '.n'),
            ('T', 'th'),
            ('D', 'dh'),
            ('P', 'ph'),
            ('B', 'bh'),
            ('S', '"s'),
            ('z', '.s'),
            ('M', '.m'),
            ('H', ',h')
        )
    else:
        repls = (
            ('aa', 'A'),
            ('ii', 'I'),
            ('uu', 'U'),
            (rex(r'\.r'), 'f'),
            (rex(r'\.rr'), 'F'),
            (rex(r'\.l'), 'x'),
            (rex(r'\.ll'), 'X'),
            ('ai', 'E'),
            ('au', 'O'),
            ('kh', 'K'),
            ('gh', 'G'),
            (rex(r'\"nk'), 'Nk'),
            (rex(r'\"ng'), 'Ng'),
            ('ch', 'C'),
            ('jh', 'J'),
            (rex(r'~n'), 'Y'),
            (rex(r'\.t'), 'w'),
            (rex(r'\.d'), 'q'),
            (rex(r'\.th'), 'W'),
            (rex(r'\.dh'), 'Q'),
            (rex(r'\.n'), 'R'),
            ('th', 'T'),
            ('dh', 'D'),
            ('ph', 'P'),
            ('bh', 'B'),
            (rex(r'"s'), 'S'),
            (rex(r'\.s'), 'z'),
            (rex(r'\.m'), 'M'),
            (rex(r'\,h'), 'H')
        )
    return replace(input, repls)

def toSin(input, type):
    input = input.lower().replace('ṁ', 'ṃ')
    vowel = {}
    vowel['a'] = 'අ'
    vowel['ā'] = 'ආ'
    vowel['i'] = 'ඉ'
    vowel['ī'] = 'ඊ'
    vowel['u'] = 'උ'
    vowel['ū'] = 'ඌ'
    vowel['e'] = 'එ'
    vowel['o'] = 'ඔ'
    sinhala = {}
    sinhala['ā'] = 'ා'
    sinhala['i'] = 'ි'
    sinhala['ī'] = 'ී'
    sinhala['u'] = 'ු'
    sinhala['ū'] = 'ූ'
    sinhala['e'] = 'ෙ'
    sinhala['o'] = 'ො'
    sinhala['ṃ'] = 'ං'
    sinhala['k'] = 'ක'
    sinhala['g'] = 'ග'
    sinhala['ṅ'] = 'ඞ'
    sinhala['c'] = 'ච'
    sinhala['j'] = 'ජ'
    sinhala['ñ'] = 'ඤ'
    sinhala['ṭ'] = 'ට'
    sinhala['ḍ'] = 'ඩ'
    sinhala['ṇ'] = 'ණ'
    sinhala['t'] = 'ත'
    sinhala['d'] = 'ද'
    sinhala['n'] = 'න'
    sinhala['p'] = 'ප'
    sinhala['b'] = 'බ'
    sinhala['m'] = 'ම'
    sinhala['y'] = 'ය'
    sinhala['r'] = 'ර'
    sinhala['l'] = 'ල'
    sinhala['ḷ'] = 'ළ'
    sinhala['v'] = 'ව'
    sinhala['s'] = 'ස'
    sinhala['h'] = 'හ'
    conj = {}
    conj['kh'] = 'ඛ'
    conj['gh'] = 'ඝ'
    conj['ch'] = 'ඡ'
    conj['jh'] = 'ඣ'
    conj['ṭh'] = 'ඨ'
    conj['ḍh'] = 'ඪ'
    conj['th'] = 'ථ'
    conj['dh'] = 'ධ'
    conj['ph'] = 'ඵ'
    conj['bh'] = 'භ'
    conj['jñ'] = 'ඥ'
    conj['ṇḍ'] = 'ඬ'
    conj['nd'] = 'ඳ'
    conj['mb'] = 'ඹ'
    conj['rg'] = 'ඟ'
    cons = {}
    cons['k'] = 'ක'
    cons['g'] = 'ග'
    cons['ṅ'] = 'ඞ'
    cons['c'] = 'ච'
    cons['j'] = 'ජ'
    cons['ñ'] = 'ඤ'
    cons['ṭ'] = 'ට'
    cons['ḍ'] = 'ඩ'
    cons['ṇ'] = 'ණ'
    cons['t'] = 'ත'
    cons['d'] = 'ද'
    cons['n'] = 'න'
    cons['p'] = 'ප'
    cons['b'] = 'බ'
    cons['m'] = 'ම'
    cons['y'] = 'ය'
    cons['r'] = 'ර'
    cons['l'] = 'ල'
    cons['ḷ'] = 'ළ'
    cons['v'] = 'ව'
    cons['s'] = 'ස'
    cons['h'] = 'හ'
    im = None
    i0 = None
    i1 = None
    i2 = None
    i3 = None
    output = ''
    i = 0
    input = input.replace('"', '`')
    
    while i < input.length:
        im = char_at(input, i - 2)
        i0 = char_at(input, i - 1)
        i1 = char_at(input, i)
        i2 = char_at(input, i + 1)
        i3 = char_at(input, i + 2)
        if vowel[i1]:
            if i == 0 or i0 == 'a':
                output += vowel[i1]
            elif i1 != 'a':
                output += sinhala[i1]
            i += 1
        elif conj[i1 + i2]:
            # two character match
            output += conj[i1 + i2]
            i += 2
            if cons[i3]:
                output += '්'
        elif sinhala[i1] and i1 != 'a':
            # one character match except a
            output += sinhala[i1]
            i += 1
            if cons[i2] and i1 != 'ṃ':
                output += '්'
        elif not sinhala[i1]:
            if cons[i0] or i0 == 'h' and cons[im]:
                output += '්'
            # end word consonant
            output += i1
            i += 1
            if vowel[i2]:
                # word-beginning vowel marker
                output += vowel[i2]
                i += 1
        else:
            i += 1
    if cons[i1]:
        output += '්'
    # fudges
    # "‍" zero-width joiner inside of quotes
    output = output.replace('ඤ්ජ', 'ඦ')
    output = output.replace('ණ්ඩ', 'ඬ')
    output = output.replace('න්ද', 'ඳ')
    output = output.replace('ම්බ', 'ඹ')
    output = output.replace('්ර', '්‍ර')
    output = output.replace(rex(r'\`+'), '"')
    return output

def fromSin(input, type):
    vowel = {}
    vowel['අ'] = 'a'
    vowel['ආ'] = 'ā'
    vowel['ඉ'] = 'i'
    vowel['ඊ'] = 'ī'
    vowel['උ'] = 'u'
    vowel['ඌ'] = 'ū'
    vowel['එ'] = 'e'
    vowel['ඔ'] = 'o'
    vowel['ඒ'] = 'ē'
    vowel['ඇ'] = 'ai'
    vowel['ඈ'] = 'āi'
    vowel['ඕ'] = 'ō'
    vowel['ඖ'] = 'au'
    vowel['ා'] = 'ā'
    vowel['ි'] = 'i'
    vowel['ී'] = 'ī'
    vowel['ු'] = 'u'
    vowel['ූ'] = 'ū'
    vowel['ෙ'] = 'e'
    vowel['ො'] = 'o'
    vowel['ෘ'] = 'ṛ'
    vowel['ෟ'] = 'ḷ'
    vowel['ෲ'] = 'ṝ'
    vowel['ෳ'] = 'ḹ'
    vowel['ේ'] = 'ē'
    vowel['ැ'] = 'ae'
    vowel['ෑ'] = 'āe'
    vowel['ෛ'] = 'ai'
    vowel['ෝ'] = 'ō'
    vowel['ෞ'] = 'au'
    sinhala = {}
    sinhala['ං'] = 'ṃ'
    sinhala['ක'] = 'k'
    sinhala['ඛ'] = 'kh'
    sinhala['ග'] = 'g'
    sinhala['ඝ'] = 'gh'
    sinhala['ඞ'] = 'ṅ'
    sinhala['ච'] = 'c'
    sinhala['ඡ'] = 'ch'
    sinhala['ජ'] = 'j'
    sinhala['ඣ'] = 'jh'
    sinhala['ඤ'] = 'ñ'
    sinhala['ට'] = 'ṭ'
    sinhala['ඨ'] = 'ṭh'
    sinhala['ඩ'] = 'ḍ'
    sinhala['ඪ'] = 'ḍh'
    sinhala['ණ'] = 'ṇ'
    sinhala['ත'] = 't'
    sinhala['ථ'] = 'th'
    sinhala['ද'] = 'd'
    sinhala['ධ'] = 'dh'
    sinhala['න'] = 'n'
    sinhala['ප'] = 'p'
    sinhala['ඵ'] = 'ph'
    sinhala['බ'] = 'b'
    sinhala['භ'] = 'bh'
    sinhala['ම'] = 'm'
    sinhala['ය'] = 'y'
    sinhala['ර'] = 'r'
    sinhala['ල'] = 'l'
    sinhala['ළ'] = 'ḷ'
    sinhala['ව'] = 'v'
    sinhala['ස'] = 's'
    sinhala['හ'] = 'h'
    sinhala['ෂ'] = 'ṣ'
    sinhala['ශ'] = 'ś'
    sinhala['ඥ'] = 'jñ'
    sinhala['ඬ'] = 'ṇḍ'
    sinhala['ඳ'] = 'nd'
    sinhala['ඹ'] = 'mb'
    sinhala['ඟ'] = 'rg'
    im = None
    i0 = None
    i1 = None
    i2 = None
    i3 = None
    output = ''
    i = 0
    input = input.replace('"', '`')
    while i < input.length:
        i1 = char_at(input, i)
        if vowel[i1]:
            if char_at(output, output.length - 1) == 'a':
                output = output.substring(0, output.length - 1)
            output += vowel[i1]
        elif sinhala[i1]:
            output += sinhala[i1] + 'a'
        else:
            output += i1
        i += 1
    # fudges
    # "‍" zero-width joiner inside of quotes
    output = output.replace('a්', '')
    return output

def toMyanmar(input, type):
    input = input.lower().replace('ṁ', 'ṃ')
    vowel = {}
    vowel['a'] = 'အ'
    vowel['i'] = 'ဣ'
    vowel['u'] = 'ဥ'
    vowel['ā'] = 'အာ'
    vowel['ī'] = 'ဤ'
    vowel['ū'] = 'ဦ'
    vowel['e'] = 'ဧ'
    vowel['o'] = 'ဩ'
    myanr = {}
    #	myanr['ā'] = 'ā'; // later
    myanr['i'] = 'ိ'
    myanr['ī'] = 'ီ'
    myanr['u'] = 'ု'
    myanr['ū'] = 'ူ'
    myanr['e'] = 'ေ'
    #	myanr['o'] = 'ေā'; // later
    myanr['ṃ'] = 'ံ'
    myanr['k'] = 'က'
    myanr['kh'] = 'ခ'
    myanr['g'] = 'ဂ'
    myanr['gh'] = 'ဃ'
    myanr['ṅ'] = 'င'
    myanr['c'] = 'စ'
    myanr['ch'] = 'ဆ'
    myanr['j'] = 'ဇ'
    myanr['jh'] = 'ဈ'
    myanr['ñ'] = 'ဉ'
    myanr['ṭ'] = 'ဋ'
    myanr['ṭh'] = 'ဌ'
    myanr['ḍ'] = 'ဍ'
    myanr['ḍh'] = 'ဎ'
    myanr['ṇ'] = 'ဏ'
    myanr['t'] = 'တ'
    myanr['th'] = 'ထ'
    myanr['d'] = 'ဒ'
    myanr['dh'] = 'ဓ'
    myanr['n'] = 'န'
    myanr['p'] = 'ပ'
    myanr['ph'] = 'ဖ'
    myanr['b'] = 'ဗ'
    myanr['bh'] = 'ဘ'
    myanr['m'] = 'မ'
    myanr['y'] = 'ယ'
    myanr['r'] = 'ရ'
    myanr['l'] = 'လ'
    myanr['ḷ'] = 'ဠ'
    myanr['v'] = 'ဝ'
    myanr['s'] = 'သ'
    myanr['h'] = 'ဟ'
    cons = {}
    cons['k'] = 'က'
    cons['g'] = 'ဂ'
    cons['ṅ'] = 'င'
    cons['c'] = 'စ'
    cons['j'] = 'ဇ'
    cons['ñ'] = 'ဉ'
    cons['ṭ'] = 'ဋ'
    cons['ḍ'] = 'ဍ'
    cons['ṇ'] = 'ဏ'
    cons['t'] = 'တ'
    cons['d'] = 'ဒ'
    cons['n'] = 'န'
    cons['p'] = 'ပ'
    cons['b'] = 'ဗ'
    cons['m'] = 'မ'
    cons['y'] = 'ယ'
    cons['r'] = 'ရ'
    cons['l'] = 'လ'
    cons['ḷ'] = 'ဠ'
    cons['v'] = 'ဝ'
    cons['s'] = 'သ'
    cons['h'] = 'ဟ'
    spec = {}
    # takes special aa
    spec['kh'] = 1
    spec['g'] = 1
    spec['d'] = 1
    spec['dh'] = 1
    spec['p'] = 1
    spec['v'] = 1
    im = None
    i0 = None
    i1 = None
    i2 = None
    i3 = None
    output = ''
    i = 0
    input = input.replace('"', '`')
    longa = false
    # special character for long a
    while i < input.length:
        im = char_at(input, i - 2)
        i0 = char_at(input, i - 1)
        i1 = char_at(input, i)
        i2 = char_at(input, i + 1)
        i3 = char_at(input, i + 2)
        if vowel[i1]:
            if i == 0 or i0 == 'a':
                output += vowel[i1]
            elif i1 == 'ā':
                if spec[longa]:
                    output += 'ါ'
                else:
                    output += 'ာ'
            elif i1 == 'o':
                if spec[longa]:
                    output += 'ေါ'
                else:
                    output += 'ော'
            elif i1 != 'a':
                output += myanr[i1]
            i += 1
            longa = false
        elif myanr[i1 + i2] and i2 == 'h':
            # two character match
            output += myanr[i1 + i2]
            if i3 != 'y' and not longa:
                longa = i1 + i2
            # gets first letter in conjunct for special long a check
            if cons[i3]:
                output += '္'
            i += 2
        elif myanr[i1] and i1 != 'a':
            # one character match except a
            output += myanr[i1]
            i += 1
            if i2 != 'y' and not longa:
                longa = i1
            # gets first letter in conjunct for special long a check
            if cons[i2] and i1 != 'ṃ':
                output += '္'
        elif not myanr[i1]:
            output += i1
            i += 1
            if vowel[i2]:
                # word-beginning vowel marker
                if vowel[i2 + i3]:
                    output += vowel[i2 + i3]
                    i += 2
                else:
                    output += vowel[i2]
                    i += 1
            longa = false
        else:
            longa = false
            i += 1
    # fudges
    output = output.replace('ဉ္ဉ', 'ည')
    output = output.replace('္ယ', 'ျ')
    output = output.replace('္ရ', 'ြ')
    output = output.replace('္ဝ', 'ွ')
    output = output.replace('္ဟ', 'ှ')
    output = output.replace('သ္သ', 'ဿ')
    output = output.replace('င္', 'င်္')
    output = output.replace(rex(r'\`+'), '"')
    return output

def toDeva(input, type):
    input = input.lower().replace('ṁ', 'ṃ')
    vowel = {}
    vowel['a'] = ' अ'
    vowel['i'] = ' इ'
    vowel['u'] = ' उ'
    vowel['ā'] = ' आ'
    vowel['ī'] = ' ई'
    vowel['ū'] = ' ऊ'
    vowel['e'] = ' ए'
    vowel['o'] = ' ओ'
    devar = {}
    devar['ā'] = 'ा'
    devar['i'] = 'ि'
    devar['ī'] = 'ी'
    devar['u'] = 'ु'
    devar['ū'] = 'ू'
    devar['e'] = 'े'
    devar['o'] = 'ो'
    devar['ṃ'] = 'ं'
    devar['k'] = 'क'
    devar['kh'] = 'ख'
    devar['g'] = 'ग'
    devar['gh'] = 'घ'
    devar['ṅ'] = 'ङ'
    devar['c'] = 'च'
    devar['ch'] = 'छ'
    devar['j'] = 'ज'
    devar['jh'] = 'झ'
    devar['ñ'] = 'ञ'
    devar['ṭ'] = 'ट'
    devar['ṭh'] = 'ठ'
    devar['ḍ'] = 'ड'
    devar['ḍh'] = 'ढ'
    devar['ṇ'] = 'ण'
    devar['t'] = 'त'
    devar['th'] = 'थ'
    devar['d'] = 'द'
    devar['dh'] = 'ध'
    devar['n'] = 'न'
    devar['p'] = 'प'
    devar['ph'] = 'फ'
    devar['b'] = 'ब'
    devar['bh'] = 'भ'
    devar['m'] = 'म'
    devar['y'] = 'य'
    devar['r'] = 'र'
    devar['l'] = 'ल'
    devar['ḷ'] = 'ळ'
    devar['v'] = 'व'
    devar['s'] = 'स'
    devar['h'] = 'ह'
    i0 = ''
    i1 = ''
    i2 = ''
    i3 = ''
    i4 = ''
    i5 = ''
    output = ''
    cons = 0
    i = 0
    input = input.replace('"', '`')
    while i < input.length:
        i0 = char_at(input, i - 1)
        i1 = char_at(input, i)
        i2 = char_at(input, i + 1)
        i3 = char_at(input, i + 2)
        i4 = char_at(input, i + 3)
        i5 = char_at(input, i + 4)
        if i == 0 and vowel[i1]:
            # first letter vowel
            output += vowel[i1]
            i += 1
        elif i2 == 'h' and devar[i1 + i2]:
            # two character match
            output += devar[i1 + i2]
            if i3 and not vowel[i3] and i2 != 'ṃ':
                output += '्'
            i += 2
        elif devar[i1]:
            # one character match except a
            output += devar[i1]
            if i2 and not vowel[i2] and not vowel[i1] and i1 != 'ṃ':
                output += '्'
            i += 1
        elif i1 != 'a':
            if cons[i0] or i0 == 'h' and cons[im]:
                output += '्'
            # end word consonant
            output += i1
            i += 1
            if vowel[i2]:
                output += vowel[i2]
                i += 1
        else:
            i += 1
        # a
    if cons[i1]:
        output += '्'
    output = regex.sub(r'`+', '"', output)
    return output

def toThai(input):
    input = input.lower().replace('ṁ', 'ṃ')
    vowel = {}
    vowel['a'] = '1'
    vowel['ā'] = '1'
    vowel['i'] = '1'
    vowel['ī'] = '1'
    vowel['iṃ'] = '1'
    vowel['u'] = '1'
    vowel['ū'] = '1'
    vowel['e'] = '2'
    vowel['o'] = '2'
    thair = {}
    thair['a'] = 'อ'
    thair['ā'] = 'า'
    thair['i'] = 'ิ'
    thair['ī'] = 'ี'
    thair['iṃ'] = 'ึ'
    thair['u'] = 'ุ'
    thair['ū'] = 'ู'
    thair['e'] = 'เ'
    thair['o'] = 'โ'
    thair['ṃ'] = 'ํ'
    thair['k'] = 'ก'
    thair['kh'] = 'ข'
    thair['g'] = 'ค'
    thair['gh'] = 'ฆ'
    thair['ṅ'] = 'ง'
    thair['c'] = 'จ'
    thair['ch'] = 'ฉ'
    thair['j'] = 'ช'
    thair['jh'] = 'ฌ'
    thair['ñ'] = ''
    thair['ṭ'] = 'ฏ'
    thair['ṭh'] = ''
    thair['ḍ'] = 'ฑ'
    thair['ḍh'] = 'ฒ'
    thair['ṇ'] = 'ณ'
    thair['t'] = 'ต'
    thair['th'] = 'ถ'
    thair['d'] = 'ท'
    thair['dh'] = 'ธ'
    thair['n'] = 'น'
    thair['p'] = 'ป'
    thair['ph'] = 'ผ'
    thair['b'] = 'พ'
    thair['bh'] = 'ภ'
    thair['m'] = 'ม'
    thair['y'] = 'ย'
    thair['r'] = 'ร'
    thair['l'] = 'ล'
    thair['ḷ'] = 'ฬ'
    thair['v'] = 'ว'
    thair['s'] = 'ส'
    thair['h'] = 'ห'
    cons = {}
    cons['k'] = '1'
    cons['g'] = '1'
    cons['ṅ'] = '1'
    cons['c'] = '1'
    cons['j'] = '1'
    cons['ñ'] = '1'
    cons['ṭ'] = '1'
    cons['ḍ'] = '1'
    cons['ṇ'] = '1'
    cons['t'] = '1'
    cons['d'] = '1'
    cons['n'] = '1'
    cons['p'] = '1'
    cons['b'] = '1'
    cons['m'] = '1'
    cons['y'] = '1'
    cons['r'] = '1'
    cons['l'] = '1'
    cons['ḷ'] = '1'
    cons['v'] = '1'
    cons['s'] = '1'
    cons['h'] = '1'
    i0 = ''
    i1 = ''
    i2 = ''
    i3 = ''
    i4 = ''
    i5 = ''
    output = ''
    i = 0
    input = input.replace('"', '`')
    while i < input.length:
        im = char_at(input, i - 2)
        i0 = char_at(input, i - 1)
        i1 = char_at(input, i)
        i2 = char_at(input, i + 1)
        i3 = char_at(input, i + 2)
        i4 = char_at(input, i + 3)
        i5 = char_at(input, i + 4)
        if vowel[i1]:
            if i1 == 'o' or i1 == 'e':
                output += thair[i1] + thair['a']
                i += 1
            else:
                if i == 0:
                    output += thair['a']
                if i1 == 'i' and i2 == 'ṃ':
                    # special i.m character
                    output += thair[i1 + i2]
                    i += 1
                elif i1 != 'a':
                    output += thair[i1]
                i += 1
        elif thair[i1 + i2] and i2 == 'h':
            # two character match
            if i3 == 'o' or i3 == 'e':
                output += thair[i3]
                i += 1
            output += thair[i1 + i2]
            if cons[i3]:
                output += 'ฺ'
            i = i + 2
        elif thair[i1] and i1 != 'a':
            # one character match except a
            if i2 == 'o' or i2 == 'e':
                output += thair[i2]
                i += 1
            output += thair[i1]
            if cons[i2] and i1 != 'ṃ':
                output += 'ฺ'
            i += 1
        elif not thair[i1]:
            output += i1
            if cons[i0] or i0 == 'h' and cons[im]:
                output += 'ฺ'
            i += 1
            if i2 == 'o' or i2 == 'e':
                # long vowel first
                output += thair[i2]
                i += 1
            if vowel[i2]:
                # word-beginning vowel marker
                output += thair['a']
        else:
            # a
            i += 1
    if cons[i1]:
        output += 'ฺ'
    output = regex.sub(r'`+', '"', output)
    return output

def fromThai(input):
    repls = (
        (rex(r'([อกขคฆงจฉชฌญฏฐฑฒณตถทธนปผพภมยรลฬวสห])(?!ฺ)'), r'\1a'),
        (rex(r'([เโ])([อกขคฆงจฉชฌญฏฐฑฒณตถทธนปผพภมยรลฬวสหฺฺ]+a)'), r'$2\1'),
        (rex(r'[a]([าิีึุูเโ])'), r'\1'),
        ('ฺ', '')
        ('อ', ''),
        ('า', 'ā'),
        ('ิ', 'i'),
        ('ี', 'ī'),
        ('ึ', 'iṃ'),
        ('ุ', 'u'),
        ('ู', 'ū'),
        ('เ', 'e'),
        ('โ', 'o'),
        ('ํ', 'ṃ'),
        ('ก', 'k'),
        ('ข', 'kh'),
        ('ค', 'g'),
        ('ฆ', 'gh'),
        ('ง', 'ṅ'),
        ('จ', 'c'),
        ('ฉ', 'ch'),
        ('ช', 'j'),
        ('ฌ', 'jh'),
        ('', 'ñ'),
        ('ญ', 'ñ'),
        ('ฏ', 'ṭ'),
        ('', 'ṭh'),
        ('ฐ', 'ṭh'),
        ('ฑ', 'ḍ'),
        ('ฒ', 'ḍh'),
        ('ณ', 'ṇ'),
        ('ต', 't'),
        ('ถ', 'th'),
        ('ท', 'd'),
        ('ธ', 'dh'),
        ('น', 'n'),
        ('ป', 'p'),
        ('ผ', 'ph'),
        ('พ', 'b'),
        ('ภ', 'bh'),
        ('ม', 'm'),
        ('ย', 'y'),
        ('ร', 'r'),
        ('ล', 'l'),
        ('ฬ', 'ḷ'),
        ('ว', 'v'),
        ('ส', 's'),
        ('ห', 'h'),
        ('๐', '0'),
        ('๑', '1'),
        ('๒', '2'),
        ('๓', '3'),
        ('๔', '4'),
        ('๕', '5'),
        ('๖', '6'),
        ('๗', '7'),
        ('๘', '8'),
        ('๙', '9'),
        ('ฯ', '..,'),
        ('', '')
    )
    return replace(input, repls)
