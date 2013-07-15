# in the following: 0=to be found, 1=cut offset, 2=length of stem must be greater than this, 3=whattoadd, 4= noun, verb, participle, 5=type&declension

# original endings, for stem recog.

# Courtesy of Yuttadhammo
endings_data = (

('a'       ,'','n'),
('i'       ,'','n'),
('u'       ,'','n'),

('ati'     ,'','v'),
('āti'     ,'','v'),
('eti'     ,'','v'),
('oti'     ,'','v'),

# masc a
('o'       ,'a','n'),
('ā'       ,'a','n'),
('aṃ'      ,'a','n'),
('aṃ'       ,'a','n'),
('e'       ,'a','n'),
('ena'     ,'a','n'),
('ehi'     ,'a','n'),
('ebhi'    ,'a','n'),
('āya'     ,'a','n'),
('assa'     ,'a','n'),
('ānaṃ'    ,'a','n'),
('asmā'     ,'a','n'),
('amhā'     ,'a','n'),
('asmiṃ'    ,'a','n'),
('amhi'     ,'a','n'),
('esu'     ,'a','n'),

# masc i
('ayo'     ,'i','n'),
('ī'       ,'i','n'),
('inā'     ,'i','n'),
('īhi'     ,'i','n'),
('ihi'     ,'i','n'),
('ībhi'    ,'i','n'),
('ibhi'     ,'i','n'),
('ino'     ,'i','n'),
('īnaṃ'    ,'i','n'),
('īsu'     ,'i','n'),

# masc ī

('i'       ,'i','n'),
('inaṃ'    ,'i','n'),

# masc u

('avo'     ,'u','n'),
('ave'     ,'u','n'),
('ū'       ,'u','n'),
('unā'     ,'u','n'),
('ūhi'     ,'u','n'),
('ūbhi'    ,'u','n'),
('uno'     ,'u','n'),
('ūnaṃ'    ,'u','n'),
('ūsu'     ,'u','n'),

# masc ū

('u'       ,'u','n'),

# nt. a
('āni'     ,'','n'),
# nt. i
('īni'     ,'','n'),
# nt. u
('ūni'     ,'','n'),

# f. ā
('a'       ,'a','n'),
('āyo'     ,'','n'),
('āhi'     ,'','n'),
('ābhi'    ,'','n'),
('āyaṃ'    ,'','n'),
('āsu'     ,'','n'),
# f. i
('iyo'     ,'','n'),
('iyā'     ,'','n'),
('iyaṃ'    ,'','n'),
# f. ī
('ī'       ,'a','n'),
('inī'     ,'a','n'),
# f. u
('uyo'     ,'','n'),
('uyā'     ,'','n'),
('uyaṃ'    ,'','n'),
# f. ū


#   # irreg nouns

# vant, mant
('ā'       ,'nt','n'),
('a'       ,'nt','n'),
('ataṃ'    ,'nt','n'),
('antaṃ'   ,'nt','n'),
('anto'    ,'nt','n'),
('antā'    ,'nt','n'),
('ante'    ,'nt','n'),
('atā'     ,'nt','n'),
('antehi'  ,'nt','n'),
('ato'     ,'nt','n'),
('antānaṃ' ,'nt','n'),
('ati'     ,'nt','n'),
('antesu'  ,'nt','n'),

# anta (CPED)
('ā'       ,'nta','n'),
('a'       ,'nta','n'),
('ataṃ'    ,'nta','n'),
('ataṃ'    ,'ti','n'),
('antaṃ'   ,'nta','n'),
('anto'    ,'nta','n'),
('antā'    ,'nta','n'),
('ante'    ,'nta','n'),
('atā'     ,'nta','n'),
('antehi'  ,'nta','n'),
('ato'     ,'nta','n'),
('antānaṃ' ,'nta','n'),
('ati'     ,'nta','n'),
('antesu'  ,'nta','n'),


# kattar

('ā'       ,'ar','n'),
('āraṃ'    ,'ar','n'),
('ārā'     ,'ar','n'),
('u'       ,'ar','n'),
('uno'     ,'ar','n'),
('ari'     ,'ar','n'),
('āro'     ,'ar','n'),
('ūhi'     ,'ar','n'),
('ūbhi'    ,'ar','n'),
('ūnaṃ'    ,'ar','n'),
('ārānaṃ'  ,'ar','n'),
('ūsu'     ,'ar','n'),
('ā'       ,'ar','n'),
('a'       ,'ar','n'),
('araṃ'    ,'ar','n'),
('arā'     ,'ar','n'),

# pitar

('aro'     ,'ar','n'),
('unā'     ,'ar','n'),
('arehi'   ,'ar','n'),
('arebhi'  ,'ar','n'),
('ānaṃ'    ,'ar','n'),
('arānaṃ'  ,'ar','n'),
('unnaṃ'   ,'ar','n'),
('ito'     ,'ar','n'),

# matar

('uyā'     ,'ar','n'),
('ūyā'      ,'ar','n'),
('ūyaṃ'     ,'ar','n'),
('uyaṃ'    ,'ar','n'),


# mano

('asā'     ,'o','n'),
('aso'     ,'o','n'),
('asā'     ,'o','n'),
('aso'     ,'o','n'),
('asi'     ,'o','n'),

('ā'       ,'o','n'),
('aṃ'      ,'o','n'),
('e'       ,'o','n'),
('ena'     ,'o','n'),
('ehi'     ,'o','n'),
('ebhi'    ,'o','n'),
('āya'     ,'o','n'),
('assa'    ,'o','n'),
('ānaṃ'    ,'o','n'),
('asmā'    ,'o','n'),
('amhā'    ,'o','n'),
('asmiṃ'   ,'o','n'),
('amhi'    ,'o','n'),
('esu'     ,'o','n'),

# a verb participles

('ato'     ,'ti','n'),
('atā'     ,'ti','n'),


# ā verb participles

('ato'     ,'ati','n'),
('atā'     ,'ati','n'),


# e verb participles

('eto'     ,'ti','n'),
('etā'     ,'ti','n'),


# o verb participles

('oto'     ,'ti','n'),
('otā'     ,'ti','n'),


# unsorted

('ahi'     ,'','n'),
('ato'      ,'','n'),
('annaṃ'   ,'','n'),
('unnaṃ'   ,'','n'),
('innaṃ'   ,'','n'),
('atā'     ,'i','n'),
('iya'     ,'a','n'),
('uyaṃ'    ,'','n'),

#('abbaṃ'  ,''),



# verbs

('ati'     ,'','v'),
('āti'     ,'','v'),
('eti'     ,'','v'),
('oti'     ,'','v'),

     # a stem pres.

('anti'    ,'ti','v'),
('āsi'      ,'ti','v'),
('asi'     ,'ti','v'),
('atha'    ,'ti','v'),
('āmi'     ,'ti','v'),
('āma'     ,'ti','v'),

     # ā stem pres.

('āmi'     ,'ti','v'),
('āma'     ,'ti','v'),

     # o stem pres.

('onti'    ,'ti','v'),
('osi'     ,'ti','v'),
('otha'    ,'ti','v'),
('omi'     ,'ti','v'),
('oma'     ,'ti','v'),

     # e stem pres.

('enti'    ,'ti','v'),
('esi'     ,'ti','v'),
('etha'    ,'ti','v'),
('emi'     ,'ti','v'),
('ema'     ,'ti','v'),


     # a stem impv.

('ahi'      ,'ti','v'),
('atu'     ,'ti','v'),
('antu'    ,'ti','v'),

     # o stem impv.

('ohi'     ,'ti','v'),
('otu'     ,'ti','v'),
('ontu'    ,'ti','v'),


     # e stem impv.

('etu'     ,'ti','v'),
('entu'    ,'ti','v'),
('ehi'     ,'ti','v'),

     # a stem caus.

('eti'     ,'ati','v'),
('enti'    ,'ati','v'),
('esi'     ,'ati','v'),
('etha'    ,'ati','v'),
('emi'     ,'ati','v'),
('ema'     ,'ati','v'),

     # ā stem caus.

('eti'     ,'āti','v'),
('enti'    ,'āti','v'),
('esi'     ,'āti','v'),
('etha'    ,'āti','v'),
('emi'     ,'āti','v'),
('ema'     ,'āti','v'),

     # not sure...

('entu'    ,'ati','v'),


# verb participles

('ayitvā'  ,'eti','v'),
('ayitvāna','eti','v'),
('vāna'    ,'i','v'),
('āpetvā'  ,'ti','v'),
('itvāna'  ,'ati','v'),
('itvāna'  ,'āti','v'),
('itvāna'  ,'eti','v'),
('etvāna'  ,'ati','v'),
('tvāna'   ,'ti','v'),
('itvā'    ,'ati','v'),
('itvā'    ,'āti','v'),
('itvā'    ,'eti','v'),
('etvā'    ,'ati','v'),
('tvā'     ,'ti','v'),
('āya'     ,'ti','v'),
('āya'     ,'ati','v'),
('āya'     ,'āti','v'),
('āya'     ,'eti','v'),
('tuṃ'     ,'ti','v'),
('ituṃ'    ,'ati','v'),
('ituṃ'    ,'āti','v'),

# past a

('a'       ,'ati','v'),
('i'       ,'ati','v'),
('imha'    ,'ati','v'),
('imhā'    ,'ati','v'),
('iṃsu'    ,'ati','v'),
('ittha'   ,'ati','v'),
('uṃ'      ,'ati','v'),
('asuṃ'     ,'ati','v'),
('asiṃ'     ,'ati','v'),
('iṃ'      ,'ati','v'),

# past ā

('a'       ,'āti','v'),
('i'       ,'āti','v'),
('imha'    ,'āti','v'),
('imhā'    ,'āti','v'),
('iṃsu'    ,'āti','v'),
('ittha'   ,'āti','v'),
('uṃ'      ,'āti','v'),
('iṃ'      ,'āti','v'),

# past e

('a'       ,'eti','v'),
('i'       ,'eti','v'),
('imha'    ,'eti','v'),
('imhā'    ,'eti','v'),
('iṃsu'    ,'eti','v'),
('ayiṃsu'  ,'eti','v'),
('ittha'   ,'eti','v'),
('uṃ'      ,'eti','v'),
('iṃ'      ,'eti','v'),

# optative a

('eyya'    ,'ati','v'),
('eyyaṃ'   ,'ati','v'),
('eyyuṃ'   ,'ati','v'),
('eyyati'  ,'ati','v'),
('eyyasi'  ,'ati','v'),
('eyyātha' ,'ati','v'),
('eyyāmi'  ,'ati','v'),
('eyyāsi'  ,'ati','v'),
('eyyāma'  ,'ati','v'),
('eyyanti' ,'ati','v'),

# optative ā

('eyya'    ,'āti','v'),
('eyyaṃ'   ,'āti','v'),
('eyyuṃ'   ,'āti','v'),
('eyyati'  ,'āti','v'),
('eyyasi'  ,'āti','v'),
('eyyātha' ,'āti','v'),
('eyyāmi'  ,'āti','v'),
('eyyāsi'  ,'āti','v'),
('eyyāma'  ,'āti','v'),
('eyyanti' ,'āti','v'),

# optative e

('eyya'    ,'ti','v'),
('eyyaṃ'   ,'ti','v'),
('eyyuṃ'   ,'ti','v'),
('eyyati'  ,'ti','v'),
('eyyasi'  ,'ti','v'),
('eyyātha' ,'ti','v'),
('eyyāmi'  ,'ti','v'),
('eyyāsi'  ,'ti','v'),
('eyyāma'  ,'ti','v'),
('eyyanti' ,'ti','v'),

# optative o

('eyya'    ,'oti','v'),
('eyyaṃ'   ,'oti','v'),
('eyyuṃ'   ,'oti','v'),
('eyyati'  ,'oti','v'),
('eyyasi'  ,'oti','v'),
('eyyātha' ,'oti','v'),
('eyyāmi'  ,'oti','v'),
('eyyāsi'  ,'oti','v'),
('eyyāma'  ,'oti','v'),
('eyyanti' ,'oti','v'),


# conditional

('issa'    ,'ati','v'),
('issā'    ,'ati','v'),
('issaṃsu' ,'ati','v'),
('issatha' ,'ati','v'),
('issaṃ'   ,'ati','v'),
('issāma'  ,'ati','v'),

('issa'    ,'āti','v'),
('issā'    ,'āti','v'),
('issaṃsu' ,'āti','v'),
('issa'    ,'āti','v'),
('issatha' ,'āti','v'),
('issaṃ'   ,'āti','v'),
('issāma'  ,'āti','v'),

('essa'    ,'ti','v'),
('essā'    ,'ti','v'),
('essaṃsu' ,'ti','v'),
('essa'    ,'ti','v'),
('essatha' ,'ti','v'),
('essaṃ'   ,'ti','v'),
('essāma'  ,'ti','v'),
)

indeclineables = {'evaṃ', 'kho', 'taṃ', 'tena', 'yena', 'hi', 'ti', 'idaṃ', 'tatrā', 'sutaṃ'}


def _build_endings():
    import collections
    endmap = collections.defaultdict(set)
    for ending, what, nv in endings_data:
        endmap[ending].update(nv)
    
    return dict( (ending, "".join(sorted(nv))) for ending, nv in endmap.items())

endings = _build_endings()