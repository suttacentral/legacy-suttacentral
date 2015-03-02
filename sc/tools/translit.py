# Code adapted from Digital Pali Reader translit.js */

from collections import defaultdict

def toUni(input, overdot=False):
    if not input:
        return input
    nigahita = (("ṁ" if overdot else "ṃ"))
    Nigahita = (("Ṁ" if overdot else "Ṃ"))
    input = input.replace("aa", "ā").replace("ii", "ī").replace("uu", "ū").replace(".t", "ṭ").replace(".d", "ḍ").replace("\"n", "ṅ").replace(".n", "ṇ").replace(".m", nigahita).replace("ṁ", nigahita).replace("~n", "ñ").replace(".l", "ḷ").replace("AA", "Ā").replace("II", "Ī").replace("UU", "Ū").replace(".T", "Ṭ").replace(".D", "Ḍ").replace("\"N", "Ṅ").replace(".N", "Ṇ").replace(".M", Nigahita).replace("~N", "Ñ").replace(".L", "Ḷ").replace(".ll", "ḹ").replace(".r", "ṛ").replace(".rr", "ṝ").replace(".s", "ṣ").replace("\"s", "ś").replace(".h", "ḥ")
    return input

def toUniRegEx(input):
    if not input:
        return input
    nigahita = (("ṁ" if DPR_prefs.get("nigahita") else "ṃ"))
    Nigahita = (("Ṁ" if DPR_prefs.get("nigahita") else "Ṃ"))
    input = input.replace("aa", "ā").replace("ii", "ī").replace("uu", "ū").replace(".t", "ṭ").replace(".d", "ḍ").replace("\"n", "ṅ").replace(".n", "ṇ").replace(".m", nigahita).replace("ṁ", nigahita).replace("~n", "ñ").replace(".l", "ḷ").replace("AA", "Ā").replace("II", "Ī").replace("UU", "Ū").replace(".T", "Ṭ").replace(".D", "Ḍ").replace("\"N", "Ṅ").replace(".N", "Ṇ").replace(".M", Nigahita).replace("~N", "Ñ").replace(".L", "Ḷ")
    return input

def toVel(input):
    if not input:
        return input
    input = input.replace("ā", "aa").replace("ī", "ii").replace("ū", "uu").replace("ṭ", ".t").replace("ḍ", ".d").replace("ṅ", "\"n").replace("ṇ", ".n").replace("ṃ", ".m").replace("ṁ", ".m").replace("ñ", "~n").replace("ḷ", ".l").replace("Ā", "AA").replace("Ī", "II").replace("Ū", "UU").replace("Ṭ", ".T").replace("Ḍ", ".D").replace("Ṅ", "\"N").replace("Ṇ", ".N").replace("Ṃ", ".M").replace("Ñ", "~N").replace("Ḷ", ".L").replace("ḹ", ".ll").replace("ṛ", ".r").replace("ṝ", ".rr").replace("ṣ", ".s").replace("ś", "\"s").replace("ḥ", ".h")
    return input

def toVelRegEx(input):
    if not input:
        return input
    input = input.replace("ā", "aa").replace("ī", "ii").replace("ū", "uu").replace("ṭ", ".t").replace("ḍ", ".d").replace("ṅ", "\"n").replace("ṇ", ".n").replace("ṃ", ".m").replace("ṁ", ".m").replace("ñ", "~n").replace("ḷ", ".l").replace("Ā", "AA").replace("Ī", "II").replace("Ū", "UU").replace("Ṭ", ".T").replace("Ḍ", ".D").replace("Ṅ", "\"N").replace("Ṇ", ".N").replace("Ṃ", ".M").replace("Ñ", "~N").replace("Ḷ", ".L")
    return input

def toFuzzy(input):
    if not input:
        return input
    input = toVel(input).replace(".([tdnlmTDNLM])", "$1").replace("~([nN])", "$1").replace("\"([nN])", "$1").replace("aa", "a").replace("ii", "i").replace("uu", "u").replace("nn", "n").replace("mm", "m").replace("yy", "y").replace("ll", "l").replace("ss", "s").replace("([kgcjtdpb])[kgcjtdpb]{0,1}h*", "$1")
    return input

def toSkt(input, rv):
    if not input:
        return input
    if rv:
        input = input.replace("A", "aa").replace("I", "ii").replace("U", "uu").replace("f", ".r").replace("F", ".rr").replace("x", ".l").replace("X", ".ll").replace("E", "ai").replace("O", "au").replace("K", "kh").replace("G", "gh").replace("N", "\"n").replace("C", "ch").replace("J", "jh").replace("Y", "~n").replace("w", ".t").replace("q", ".d").replace("W", ".th").replace("Q", ".dh").replace("R", ".n").replace("T", "th").replace("D", "dh").replace("P", "ph").replace("B", "bh").replace("S", "\"s").replace("z", ".s").replace("M", ".m").replace("H", ".h")
    else:
        input = input.replace("aa", "A").replace("ii", "I").replace("uu", "U").replace(".r", "f").replace(".rr", "F").replace(".l", "x").replace(".ll", "X").replace("ai", "E").replace("au", "O").replace("kh", "K").replace("gh", "G").replace("\"n", "N").replace("ch", "C").replace("jh", "J").replace("~n", "Y").replace(".t", "w").replace(".d", "q").replace(".th", "W").replace(".dh", "Q").replace(".n", "R").replace("th", "T").replace("dh", "D").replace("ph", "P").replace("bh", "B").replace("\"s", "S").replace(".s", "z").replace(".m", "M").replace(".h", "H")
    return input

def toSin(input):
    input = input.lower().replace("ṁ", "ṃ")
    vowel = {}
    vowel["a"] = "අ"
    vowel["ā"] = "ආ"
    vowel["i"] = "ඉ"
    vowel["ī"] = "ඊ"
    vowel["u"] = "උ"
    vowel["ū"] = "ඌ"
    vowel["e"] = "එ"
    vowel["o"] = "ඔ"
    sinhala = {}
    sinhala["ā"] = "ා"
    sinhala["i"] = "ි"
    sinhala["ī"] = "ී"
    sinhala["u"] = "ු"
    sinhala["ū"] = "ූ"
    sinhala["e"] = "ෙ"
    sinhala["o"] = "ො"
    sinhala["ṃ"] = "ං"
    sinhala["k"] = "ක"
    sinhala["g"] = "ග"
    sinhala["ṅ"] = "ඞ"
    sinhala["c"] = "ච"
    sinhala["j"] = "ජ"
    sinhala["ñ"] = "ඤ"
    sinhala["ṭ"] = "ට"
    sinhala["ḍ"] = "ඩ"
    sinhala["ṇ"] = "ණ"
    sinhala["t"] = "ත"
    sinhala["d"] = "ද"
    sinhala["n"] = "න"
    sinhala["p"] = "ප"
    sinhala["b"] = "බ"
    sinhala["m"] = "ම"
    sinhala["y"] = "ය"
    sinhala["r"] = "ර"
    sinhala["l"] = "ල"
    sinhala["ḷ"] = "ළ"
    sinhala["v"] = "ව"
    sinhala["s"] = "ස"
    sinhala["h"] = "හ"
    conj = {}
    conj["kh"] = "ඛ"
    conj["gh"] = "ඝ"
    conj["ch"] = "ඡ"
    conj["jh"] = "ඣ"
    conj["ṭh"] = "ඨ"
    conj["ḍh"] = "ඪ"
    conj["th"] = "ථ"
    conj["dh"] = "ධ"
    conj["ph"] = "ඵ"
    conj["bh"] = "භ"
    conj["jñ"] = "ඥ"
    conj["ṇḍ"] = "ඬ"
    conj["nd"] = "ඳ"
    conj["mb"] = "ඹ"
    conj["rg"] = "ඟ"
    cons = {}
    cons["k"] = "ක"
    cons["g"] = "ග"
    cons["ṅ"] = "ඞ"
    cons["c"] = "ච"
    cons["j"] = "ජ"
    cons["ñ"] = "ඤ"
    cons["ṭ"] = "ට"
    cons["ḍ"] = "ඩ"
    cons["ṇ"] = "ණ"
    cons["t"] = "ත"
    cons["d"] = "ද"
    cons["n"] = "න"
    cons["p"] = "ප"
    cons["b"] = "බ"
    cons["m"] = "ම"
    cons["y"] = "ය"
    cons["r"] = "ර"
    cons["l"] = "ල"
    cons["ḷ"] = "ළ"
    cons["v"] = "ව"
    cons["s"] = "ස"
    cons["h"] = "හ"
    im = None
    i0 = None
    i1 = None
    i2 = None
    i3 = None
    output = ""
    i = 0
    input = input.replace("\&quot;", "`")
    while i < len(input):
        im = input[i - 2: i - 2 + 1]
        i0 = input[i - 1: i - 1 + 1]
        i1 = input[i: i + 1]
        i2 = input[i + 1: i + 1 + 1]
        i3 = input[i + 2: i + 2 + 1]
        if vowel.get(i1):
            if i == 0 or i0 == "a":
                output += vowel.get(i1)
            elif i1 != "a":
                output += sinhala.get(i1)
            i+= 1
        elif conj.get(i1 + i2): # two character match
            output += conj.get(i1 + i2)
            i += 2
            if cons.get(i3):
                output += "්"
        elif sinhala.get(i1) and i1 != "a": # one character match except a
            output += sinhala.get(i1)
            i+= 1
            if cons.get(i2) and i1 != "ṃ":
                    output += "්"
        elif not sinhala.get(i1):
            if cons.get(i0) or (i0 == "h" and cons.get(im)):
                output += "්"     # end word consonant
            output += i1
            i+= 1
            if vowel.get(i2): # word-beginning vowel marker
                output += vowel.get(i2)
                i+= 1
        else:
            i+= 1
    if cons.get(i1):
        output += "්"
    
    # fudges
    
    # "‍" zero-width joiner inside of quotes
    output = output.replace("ඤ්ජ", "ඦ")
    output = output.replace("ණ්ඩ", "ඬ")
    output = output.replace("න්ද", "ඳ")
    output = output.replace("ම්බ", "ඹ")
    output = output.replace("්ර", "්‍ර")
    output = output.replace("\`+", "\"")
    return output

def fromSin(input):
    vowel = {}
    vowel["අ"] = "a"
    vowel["ආ"] = "ā"
    vowel["ඉ"] = "i"
    vowel["ඊ"] = "ī"
    vowel["උ"] = "u"
    vowel["ඌ"] = "ū"
    vowel["එ"] = "e"
    vowel["ඔ"] = "o"
    vowel["ඒ"] = "ē"
    vowel["ඇ"] = "ai"
    vowel["ඈ"] = "āi"
    vowel["ඕ"] = "ō"
    vowel["ඖ"] = "au"
    vowel["ා"] = "ā"
    vowel["ි"] = "i"
    vowel["ී"] = "ī"
    vowel["ු"] = "u"
    vowel["ූ"] = "ū"
    vowel["ෙ"] = "e"
    vowel["ො"] = "o"
    vowel["ෘ"] = "ṛ"
    vowel["ෟ"] = "ḷ"
    vowel["ෲ"] = "ṝ"
    vowel["ෳ"] = "ḹ"
    vowel["ේ"] = "ē"
    vowel["ැ"] = "ae"
    vowel["ෑ"] = "āe"
    vowel["ෛ"] = "ai"
    vowel["ෝ"] = "ō"
    vowel["ෞ"] = "au"
    sinhala = {}
    sinhala["ං"] = "ṃ"
    sinhala["ක"] = "k"
    sinhala["ඛ"] = "kh"
    sinhala["ග"] = "g"
    sinhala["ඝ"] = "gh"
    sinhala["ඞ"] = "ṅ"
    sinhala["ච"] = "c"
    sinhala["ඡ"] = "ch"
    sinhala["ජ"] = "j"
    sinhala["ඣ"] = "jh"
    sinhala["ඤ"] = "ñ"
    sinhala["ට"] = "ṭ"
    sinhala["ඨ"] = "ṭh"
    sinhala["ඩ"] = "ḍ"
    sinhala["ඪ"] = "ḍh"
    sinhala["ණ"] = "ṇ"
    sinhala["ත"] = "t"
    sinhala["ථ"] = "th"
    sinhala["ද"] = "d"
    sinhala["ධ"] = "dh"
    sinhala["න"] = "n"
    sinhala["ප"] = "p"
    sinhala["ඵ"] = "ph"
    sinhala["බ"] = "b"
    sinhala["භ"] = "bh"
    sinhala["ම"] = "m"
    sinhala["ය"] = "y"
    sinhala["ර"] = "r"
    sinhala["ල"] = "l"
    sinhala["ළ"] = "ḷ"
    sinhala["ව"] = "v"
    sinhala["ස"] = "s"
    sinhala["හ"] = "h"
    sinhala["ෂ"] = "ṣ"
    sinhala["ශ"] = "ś"
    sinhala["ඥ"] = "jñ"
    sinhala["ඬ"] = "ṇḍ"
    sinhala["ඳ"] = "nd"
    sinhala["ඹ"] = "mb"
    sinhala["ඟ"] = "rg"
    im = None
    i0 = None
    i1 = None
    i2 = None
    i3 = None
    output = ""
    i = 0
    input = input.replace("\&quot;", "`")
    while i < len(input):
        i1 = input[i: i + 1]
        if vowel.get(i1):
            if output.get(len(output) - 1) == "a":
                output = output.substring(0, len(output) - 1)
            output += vowel.get(i1)
        elif sinhala.get(i1):
            output += sinhala.get(i1) + "a"
        else:
            output += i1
        i+= 1
    
    # fudges
    
    # "‍" zero-width joiner inside of quotes
    output = output.replace("a්", "")
    return output

def toMyanmar(input):
    input = input.lower().replace("ṁ", "ṃ")
    vowel = {}
    vowel["a"] = "အ"
    vowel["i"] = "ဣ"
    vowel["u"] = "ဥ"
    vowel["ā"] = "အာ"
    vowel["ī"] = "ဤ"
    vowel["ū"] = "ဦ"
    vowel["e"] = "ဧ"
    vowel["o"] = "ဩ"
    myanr = {}
    
    #	myanr['ā'] = 'ā'; // later
    myanr["i"] = "ိ"
    myanr["ī"] = "ီ"
    myanr["u"] = "ု"
    myanr["ū"] = "ူ"
    myanr["e"] = "ေ"
    
    #	myanr['o'] = 'ေā'; // later
    myanr["ṃ"] = "ံ"
    myanr["k"] = "က"
    myanr["kh"] = "ခ"
    myanr["g"] = "ဂ"
    myanr["gh"] = "ဃ"
    myanr["ṅ"] = "င"
    myanr["c"] = "စ"
    myanr["ch"] = "ဆ"
    myanr["j"] = "ဇ"
    myanr["jh"] = "ဈ"
    myanr["ñ"] = "ဉ"
    myanr["ṭ"] = "ဋ"
    myanr["ṭh"] = "ဌ"
    myanr["ḍ"] = "ဍ"
    myanr["ḍh"] = "ဎ"
    myanr["ṇ"] = "ဏ"
    myanr["t"] = "တ"
    myanr["th"] = "ထ"
    myanr["d"] = "ဒ"
    myanr["dh"] = "ဓ"
    myanr["n"] = "န"
    myanr["p"] = "ပ"
    myanr["ph"] = "ဖ"
    myanr["b"] = "ဗ"
    myanr["bh"] = "ဘ"
    myanr["m"] = "မ"
    myanr["y"] = "ယ"
    myanr["r"] = "ရ"
    myanr["l"] = "လ"
    myanr["ḷ"] = "ဠ"
    myanr["v"] = "ဝ"
    myanr["s"] = "သ"
    myanr["h"] = "ဟ"
    cons = {}
    cons["k"] = "က"
    cons["g"] = "ဂ"
    cons["ṅ"] = "င"
    cons["c"] = "စ"
    cons["j"] = "ဇ"
    cons["ñ"] = "ဉ"
    cons["ṭ"] = "ဋ"
    cons["ḍ"] = "ဍ"
    cons["ṇ"] = "ဏ"
    cons["t"] = "တ"
    cons["d"] = "ဒ"
    cons["n"] = "န"
    cons["p"] = "ပ"
    cons["b"] = "ဗ"
    cons["m"] = "မ"
    cons["y"] = "ယ"
    cons["r"] = "ရ"
    cons["l"] = "လ"
    cons["ḷ"] = "ဠ"
    cons["v"] = "ဝ"
    cons["s"] = "သ"
    cons["h"] = "ဟ"
    spec = {} # takes special aa
    spec["kh"] = 1
    spec["g"] = 1
    spec["d"] = 1
    spec["dh"] = 1
    spec["p"] = 1
    spec["v"] = 1
    im = None
    i0 = None
    i1 = None
    i2 = None
    i3 = None
    output = ""
    i = 0
    input = input.replace("\&quot;", "`")
    longa = False # special character for long a
    while i < len(input):
        im = input[i - 2: i - 2 + 1]
        i0 = input[i - 1: i - 1 + 1]
        i1 = input[i: i + 1]
        i2 = input[i + 1: i + 1 + 1]
        i3 = input[i + 2: i + 2 + 1]
        if vowel.get(i1):
            if i == 0 or i0 == "a":
                output += vowel.get(i1)
            elif i1 == "ā":
                if spec.get(longa):
                    output += "ါ"
                else:
                    output += "ာ"
            elif i1 == "o":
                if spec.get(longa):
                    output += "ေါ"
                else:
                    output += "ော"
            elif i1 != "a":
                output += myanr.get(i1)
            i+= 1
            longa = False
        elif myanr.get(i1 + i2) and i2 == "h": # two character match
            output += myanr.get(i1 + i2)
            if i3 != "y" and not longa:
                longa = i1 + i2 # gets first letter in conjunct for special long a check
            if cons.get(i3):
                output += "္"
            i += 2
        elif myanr.get(i1) and i1 != "a": # one character match except a
            output += myanr.get(i1)
            i+= 1
            if i2 != "y" and not longa:
                longa = i1    # gets first letter in conjunct for special long a check
            if cons.get(i2) and i1 != "ṃ":
                output += "္"
        elif not myanr.get(i1):
            output += i1
            i+= 1
            if vowel.get(i2): # word-beginning vowel marker
                if vowel.get(i2 + i3):
                    output += vowel.get(i2 + i3)
                    i += 2
                else:
                    output += vowel.get(i2)
                    i+= 1
            longa = False
        else:
            longa = False
            i+= 1
    
    # fudges
    output = output.replace("ဉ္ဉ", "ည")
    output = output.replace("္ယ", "ျ")
    output = output.replace("္ရ", "ြ")
    output = output.replace("္ဝ", "ွ")
    output = output.replace("္ဟ", "ှ")
    output = output.replace("သ္သ", "ဿ")
    output = output.replace("င္", "င်္")
    output = output.replace("\`+", "\"")
    return output

def toDeva(input):
    input = input.lower().replace("ṁ", "ṃ")
    vowel = {}
    vowel["a"] = " अ"
    vowel["i"] = " इ"
    vowel["u"] = " उ"
    vowel["ā"] = " आ"
    vowel["ī"] = " ई"
    vowel["ū"] = " ऊ"
    vowel["e"] = " ए"
    vowel["o"] = " ओ"
    devar = {}
    devar["ā"] = "ा"
    devar["i"] = "ि"
    devar["ī"] = "ी"
    devar["u"] = "ु"
    devar["ū"] = "ू"
    devar["e"] = "े"
    devar["o"] = "ो"
    devar["ṃ"] = "ं"
    devar["k"] = "क"
    devar["kh"] = "ख"
    devar["g"] = "ग"
    devar["gh"] = "घ"
    devar["ṅ"] = "ङ"
    devar["c"] = "च"
    devar["ch"] = "छ"
    devar["j"] = "ज"
    devar["jh"] = "झ"
    devar["ñ"] = "ञ"
    devar["ṭ"] = "ट"
    devar["ṭh"] = "ठ"
    devar["ḍ"] = "ड"
    devar["ḍh"] = "ढ"
    devar["ṇ"] = "ण"
    devar["t"] = "त"
    devar["th"] = "थ"
    devar["d"] = "द"
    devar["dh"] = "ध"
    devar["n"] = "न"
    devar["p"] = "प"
    devar["ph"] = "फ"
    devar["b"] = "ब"
    devar["bh"] = "भ"
    devar["m"] = "म"
    devar["y"] = "य"
    devar["r"] = "र"
    devar["l"] = "ल"
    devar["ḷ"] = "ळ"
    devar["v"] = "व"
    devar["s"] = "स"
    devar["h"] = "ह"
    i0 = ""
    i1 = ""
    i2 = ""
    i3 = ""
    i4 = ""
    i5 = ""
    output = ""
    cons = {}
    i = 0
    input = input.replace("&quot;", "`")
    while i < len(input):
        i0 = input[i - 1: i - 1 + 1]
        i1 = input[i: i + 1]
        i2 = input[i + 1: i + 1 + 1]
        i3 = input[i + 2: i + 2 + 1]
        i4 = input[i + 3: i + 3 + 1]
        i5 = input[i + 4: i + 4 + 1]
        if i == 0 and vowel.get(i1): # first letter vowel
            output += vowel.get(i1)
            i += 1
        elif i2 == "h" and devar.get(i1 + i2): # two character match
            output += devar.get(i1 + i2)
            if i3 and not vowel.get(i3) and i2 != "ṃ":
                output += "्"
            i += 2
        elif devar.get(i1): # one character match except a
            output += devar.get(i1)
            if i2 and not vowel.get(i2) and not vowel.get(i1) and i1 != "ṃ":
                output += "्"    
            i+= 1
        elif not i1 == "a":
            if cons.get(i0) or (i0 == "h" and cons.get(im)): # end word consonant
                output += "्" 
            output += i1
            i+= 1
            if vowel.get(i2):
                output += vowel.get(i2)
                i+= 1
        else: # a
            i+= 1
    if cons.get(i1):
        output += "्"
    output = output.replace("`+", "\"")
    return output

def toThai(input):
    input = input.lower().replace("ṁ", "ṃ")
    vowel = {}
    vowel["a"] = "1"
    vowel["ā"] = "1"
    vowel["i"] = "1"
    vowel["ī"] = "1"
    vowel["iṃ"] = "1"
    vowel["u"] = "1"
    vowel["ū"] = "1"
    vowel["e"] = "2"
    vowel["o"] = "2"
    thair = {}
    thair["a"] = "อ"
    thair["ā"] = "า"
    thair["i"] = "ิ"
    thair["ī"] = "ี"
    thair["iṃ"] = "ึ"
    thair["u"] = "ุ"
    thair["ū"] = "ู"
    thair["e"] = "เ"
    thair["o"] = "โ"
    thair["ṃ"] = "ํ"
    thair["k"] = "ก"
    thair["kh"] = "ข"
    thair["g"] = "ค"
    thair["gh"] = "ฆ"
    thair["ṅ"] = "ง"
    thair["c"] = "จ"
    thair["ch"] = "ฉ"
    thair["j"] = "ช"
    thair["jh"] = "ฌ"
    thair["ñ"] = ""
    thair["ṭ"] = "ฏ"
    thair["ṭh"] = ""
    thair["ḍ"] = "ฑ"
    thair["ḍh"] = "ฒ"
    thair["ṇ"] = "ณ"
    thair["t"] = "ต"
    thair["th"] = "ถ"
    thair["d"] = "ท"
    thair["dh"] = "ธ"
    thair["n"] = "น"
    thair["p"] = "ป"
    thair["ph"] = "ผ"
    thair["b"] = "พ"
    thair["bh"] = "ภ"
    thair["m"] = "ม"
    thair["y"] = "ย"
    thair["r"] = "ร"
    thair["l"] = "ล"
    thair["ḷ"] = "ฬ"
    thair["v"] = "ว"
    thair["s"] = "ส"
    thair["h"] = "ห"
    cons = {}
    cons["k"] = "1"
    cons["g"] = "1"
    cons["ṅ"] = "1"
    cons["c"] = "1"
    cons["j"] = "1"
    cons["ñ"] = "1"
    cons["ṭ"] = "1"
    cons["ḍ"] = "1"
    cons["ṇ"] = "1"
    cons["t"] = "1"
    cons["d"] = "1"
    cons["n"] = "1"
    cons["p"] = "1"
    cons["b"] = "1"
    cons["m"] = "1"
    cons["y"] = "1"
    cons["r"] = "1"
    cons["l"] = "1"
    cons["ḷ"] = "1"
    cons["v"] = "1"
    cons["s"] = "1"
    cons["h"] = "1"
    i0 = ""
    i1 = ""
    i2 = ""
    i3 = ""
    i4 = ""
    i5 = ""
    output = ""
    i = 0
    input = input.replace("&quot;", "`")
    while i < len(input):
        im = input[i - 2: i - 2 + 1]
        i0 = input[i - 1: i - 1 + 1]
        i1 = input[i: i + 1]
        i2 = input[i + 1: i + 1 + 1]
        i3 = input[i + 2: i + 2 + 1]
        i4 = input[i + 3: i + 3 + 1]
        i5 = input[i + 4: i + 4 + 1]
        if vowel.get(i1):
            if i1 == "o" or i1 == "e":
                output += thair.get(i1) + thair.get("a")
                i+= 1
            else:
                if i == 0:
                    output += thair.get("a")
                if i1 == "i" and i2 == "ṃ": # special i.m character
                    output += thair.get(i1 + i2)
                    i+= 1
                elif i1 != "a":
                    output += thair.get(i1)
                i+= 1
        elif thair.get(i1 + i2) and i2 == "h": # two character match
            if i3 == "o" or i3 == "e":
                output += thair.get(i3)
                i+= 1
            output += thair.get(i1 + i2)
            if cons.get(i3):
                output += "ฺ"
            i = i + 2
        elif thair.get(i1) and i1 != "a": # one character match except a
            if i2 == "o" or i2 == "e":
                output += thair.get(i2)
                i+= 1
            output += thair.get(i1)
            if cons.get(i2) and i1 != "ṃ":
                output += "ฺ"
            i+= 1
        elif not thair.get(i1):
            output += i1
            if cons.get(i0) or (i0 == "h" and cons.get(im)):
                output += "ฺ"
            i+= 1
            if i2 == "o" or i2 == "e": # long vowel first
                output += thair.get(i2)
                i+= 1
            # word-beginning vowel marker
            if vowel.get(i2):
                output += thair.get("a")
        else: # a
            i+= 1
    if cons.get(i1):
        output += "ฺ"
    output = output.replace("`+", "\"")
    return output

def fromThai(input):
    output = regex.sub(r"([อกขคฆงจฉชฌญฏฐฑฒณตถทธนปผพภมยรลฬวสห])(?!ฺ)", r"\1a", input)
    output = regex.sub(r"([เโ])([อกขคฆงจฉชฌญฏฐฑฒณตถทธนปผพภมยรลฬวสหฺฺ]+a)", r"\2\1", output)
    ouput = regex.sub(r"[a]([าิีึุูเโ])", r"\1", output)
    output = output.replace("ฺ", "")
    output = output.replace("อ", "").replace("า", "ā").replace("ิ", "i").replace("ี", "ī").replace("ึ", "iṃ").replace("ุ", "u").replace("ู", "ū").replace("เ", "e").replace("โ", "o").replace("ํ", "ṃ").replace("ก", "k").replace("ข", "kh").replace("ค", "g").replace("ฆ", "gh").replace("ง", "ṅ").replace("จ", "c").replace("ฉ", "ch").replace("ช", "j").replace("ฌ", "jh").replace("", "ñ").replace("ญ", "ñ").replace("ฏ", "ṭ").replace("", "ṭh").replace("ฐ", "ṭh").replace("ฑ", "ḍ").replace("ฒ", "ḍh").replace("ณ", "ṇ").replace("ต", "t").replace("ถ", "th").replace("ท", "d").replace("ธ", "dh").replace("น", "n").replace("ป", "p").replace("ผ", "ph").replace("พ", "b").replace("ภ", "bh").replace("ม", "m").replace("ย", "y").replace("ร", "r").replace("ล", "l").replace("ฬ", "ḷ").replace("ว", "v").replace("ส", "s").replace("ห", "h").replace("๐", "0").replace("๑", "1").replace("๒", "2").replace("๓", "3").replace("๔", "4").replace("๕", "5").replace("๖", "6").replace("๗", "7").replace("๘", "8").replace("๙", "9").replace("ฯ", "...")
    output = output.replace("", "")
    return output
