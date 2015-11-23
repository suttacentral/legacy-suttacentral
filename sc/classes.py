import regex
from collections import namedtuple, Counter
from sc.util import ConciseRepr
from sc.uid_expansion import uid_to_acro, uid_to_name

class Serializable:
    """ Serialize the class to JSON

    A subclass should either define _serialize_attrs or override
    _to_json.

    """
    
    __slots__ = ()
    _serialize_attrs = ('uid', 'name')
    def _to_json(self, depth=0):
        def smart_convert(obj, depth=depth):
            if type(obj) in {str, int, float, bool} or obj is None:
                return obj
            
            if depth == 0:
                if hasattr(obj, 'uid'):
                    return obj.uid
                else:
                    return str(obj)
            else:
                if isinstance(obj, Serializable):
                    return obj._to_json(depth - 1)
                else:
                    return str(obj)
        
        result = {}
        for attr in self._serialize_attrs:
            value = getattr(self, attr)
            if isinstance(value, list):
                value = [smart_convert(e) for e in value]
            else:
                value = smart_convert(value)
            result[attr] = value
        return result

class Language(Serializable, namedtuple('Language', 
        'uid name isroot iso_code priority search_priority collections')):
    __slots__ = ()


class Sect(Serializable, namedtuple('Sect', 'uid name')):
    __slots__ = ()

class Pitaka(Serializable, namedtuple('Pitaka', 'uid name always_full')):
    __slots__ = ()

class Collection(ConciseRepr, Serializable, namedtuple('Collection',
        'uid name abbrev_name lang sect pitaka menu_seq divisions')):
    __slots__ = ()
    
    @staticmethod
    def sort_key(collection):
        """Return the canonical sort key."""
        return collection.menu_seq

class Division(ConciseRepr, Serializable, namedtuple('Division', 
        'uid collection name alt_name acronym subdiv_ind '
        'menu_seq menu_gwn_ind text_ref subdivisions')):
    __slots__ = ()

    @staticmethod
    def sort_key(division):
        """Return the canonical sort key."""
        return division.menu_seq

    def has_subdivisions(self):
        return len(self.subdivisions) > 1
    
    @property
    def has_suttas(self):
        return len(self.subdivisions[0].suttas)


class Subdivision(ConciseRepr, Serializable, namedtuple('Subdivision',
        'uid division name acronym vagga_numbering_ind vaggas suttas order')):
    __slots__ = ()


class Vagga(ConciseRepr, Serializable, namedtuple('Vagga', 
        'subdivision number name suttas')):
    __slots__ = ()
    _serialize_attrs = ('name', )


class SuttaCommon(Serializable):
    __slots__ = ()
    _serialize_attrs = ['uid', 'acronym', 'name', 'vagga', 'volpage',
                'parallels', 'translations', 'text_ref', 'subdivision']
    
    @property
    def details_uid(self):
        return self.uid.replace('#', '_')

    @property
    def parallels_count(self):
        return len(self.parallels)

    @property
    def url_uid(self):
        return self.uid

    @property
    def text_ref(self):
        return self.imm.get_text_ref(self.uid, self.lang.uid)

    @property
    def translations(self):
        return self.imm.get_translations(self.uid, self.lang.uid)

    @property
    def local_text_refs(self):
        allrefs = []
        if self.text_ref and self.text_ref.url.startswith('/'):
            allrefs.append(self.text_ref)
        allrefs.extend(self.translations)
        return [tref for tref in allrefs if tref.url.startswith('/')]
    
    def __hash__(self):
        return hash(self.uid)

    group_parallels = None

    @property
    def volpage_info(self):
        if self.volpage:
            return self.volpage
        
        textinfo = self._textinfo
        if textinfo and textinfo.volpage:
            return textinfo.volpage
        return ''

    @staticmethod
    def canon_url(uid, lang_code, bookmark=''):
        if not isinstance(lang_code, str):
            lang_code = lang_code.uid
        url = '/{lang}/{uid}'.format(uid=uid, lang=lang_code)
        if bookmark:
            url += '#' + bookmark
        return url

    def get_translation(self, lang):
        for tr in self.translations:
            if tr.url.startswith('http'):
                continue
            if tr.lang == lang:
                return tr

    @property
    def _textinfo(self):
        return self.imm.tim.get(self.uid, self.lang.uid)

    def _fixname(self, name):
        if name:
            m = regex.match(r'(\d+(?:\.\d+)?(?:–\d+)?)?\s*(.*)', name)
            if m[2]:
                return m[2]
            else:
                return m[1]
        else:
            return ''

class Sutta(ConciseRepr, namedtuple('Sutta',
        'uid acronym alt_acronym name vagga_number '
        'number_in_vagga number lang subdivision vagga '
        'volpage alt_volpage_info biblio_entry '
        'parallels, imm'), SuttaCommon):
    __slots__ = ()

    @property
    def name(self):
        supname = super().name
        if supname:
            return supname
        ti = self._textinfo
        return self._fixname(ti.name if ti else '')
    
    def __hash__(self):
        return hash(self.uid)
    

class GroupedSutta(SuttaCommon):
    """The GroupedSutta is like a Sutta, except it belongs to a group of
    related suttas and most of the information is generated on the fly from
    it's group data.
    
    """
    
    __slots__ = {'uid', 'ref_uid', 'volpage', '_textinfo',
                'parallel_group', 'imm'}
    
    no_show_parallels = True
    
    alt_volpage_info = None
    biblio_entry = None
    alt_acronym = None
    
    def __init__(self, uid, volpage, imm):
        self.uid = uid
        self.volpage = volpage
        self.imm = imm
        self._textinfo = imm.tim.get(uid, self.lang.uid)
    
    @property
    def name(self):
        if self._textinfo and '-pm' not in self.uid and '-vb' not in self.uid:
            ti = self._textinfo
            return self._fixname(ti.name if ti else '')
        try:
            return self.parallel_group.name
        except AttributeError as e:
            e.args = list(e.args) + ['No group found for {}'.format(self.uid)]
            raise e
    
    @property
    def acronym(self):
        return uid_to_acro(self.uid)
    
    @property
    def _subdivision_uid(self):
        imm = self.imm
        uid = self.uid
        uid = uid.replace('#', '-')
        # Just keep slicing it until we find something that
        # matches. It's good enough.
        while len(uid) > 0:
            if uid in imm.subdivisions:
                return uid
            uid = uid[:-1]

    @property
    def number(self):
        try:
            return int(regex.search(r'(\d+)(-\d+)?[a-g]?$', self.uid)[1])
        except:
            print(self.uid)
            raise
        
    @property
    def subdivision(self):
        return self.imm.subdivisions[self._subdivision_uid]
    
    @property
    def lang(self):
        return self.subdivision.division.collection.lang
    
    @property
    def vagga(self):
        return self.subdivision.vaggas[0]
    
    _subdiv_match = regex.compile(r'(.*?)(\d+)$').match
    _div_match = regex.compile(r'(.*)-(.*)$').match
    
    parallels = []

    @property
    def parallels_count(self):
        return len(self.parallels) + max(0, self.parallel_group.real_count() - 1)
    
    @property
    def brief_uid(self):
        return ' '.join(self.uid.split('-')[-1:])
    
    @property
    def brief_acronym(self):
        return uid_to_acronym(self.brief_uid)
    
    @property
    def brief_name(self):
        return uid_to_name(self.brief_uid)
    
class ParallelSuttaGroup:
    """ A class which acts a lot like a list of parallels """
    def __init__(self, name, entries):
        self.name = name
        self.entries = entries

    def real_count(self):
        return len(set(e.sutta.subdivision.uid for e in self.parallels() if hasattr(e, 'sutta')))
    
    def parallels(self, sutta=None):
        "yields a series of Parallel objects"
        for e in self.entries:
            if e == sutta:
                continue
            if isinstance(e, GroupedSutta):
                yield Parallel(sutta=e, partial=False,
                    indirect=False, footnote=None)
            else:
                yield e

    def groupees(self):
        c = Counter()
        c.update(e.sutta.subdivision.uid for e in self.parallels() if hasattr(e, 'sutta'))
        return {uid: count for uid, count in c.items() if count > 1}

class MultiParallelSuttaGroup(ParallelSuttaGroup):
    def __init__(self, initial):
        self.groups = [initial]
        self.name = initial.name

    def add_group(self, group):
        self.groups.append(group)
    
    def parallels(self, sutta=None):
        for col in zip(*(g.entries for g in self.groups)):
            if col[0] == sutta:
                continue
            if len(set(col)) == 1:
                if isinstance(col[0], GroupedSutta):
                    yield Parallel(sutta=col[0], partial=False,
                        indirect=False, footnote=None)
                else:
                    yield col[0]
            else:
                seen = set()
                for entry in col:
                    if entry in seen:
                        continue
                    if isinstance(entry, GroupedSutta):
                        yield Parallel(sutta=entry,partial=False,
                            indirect=False,footnote=None)
                    else:
                        yield entry

class Parallel(ConciseRepr, Serializable, namedtuple('Parallel',
        'sutta partial indirect footnote')):
    __slots__ = ()
    _serialize_attrs = ()
    
    @staticmethod
    def sort_key(p):
        """The canonical ordering as follows:
            1) full, then partial
            2) sutta language id,
            3) sutta subdivision id,
            4) sutta number.
        To be used with sort() or sorted()."""
        s = p.sutta
        return (s.lang.priority,
                p.partial,
                s.subdivision.order,
                s.number_in_vagga)
    
    negated = False

    def _to_json(self, depth):
        if depth == 0:
            return self.sutta.uid
        else:
            return {"uid": self.sutta.uid,
                    "partial": self.partial,
                    "footnote": self.footnote}

class NegatedParallel:
    __slots__ = ('division')
    negated = '---'
    maybe = False
    def __init__(self, division):
        self.division = division

class MaybeParallel:
    __slots__ = ('division')
    negated = '???'
    maybe = True
    def __init__(self, division):
        self.division = division

class TextRef(ConciseRepr, Serializable, namedtuple('TextRef', 
        'lang name author abstract url priority')):
    __slots__ = ()
    _serialize_attrs = ['lang', 'name', 'author', 'abstract', 'url']

    @staticmethod
    def sort_key(t):
        """The canonical ordering as follows:
            1) language id
            2) sequence number
        To be used with sort() or sorted()."""
        return (not t.url.startswith('/'), t.lang.priority, t.lang.iso_code, t.priority)

    @classmethod
    def from_textinfo(cls, textinfo, lang):
        return cls(lang=lang,
                        name=textinfo.name,
                        abstract=textinfo.author or lang.name,
                        author=textinfo.author,
                        url=Sutta.canon_url(uid=textinfo.path.stem,
                                            lang_code=lang.uid,
                                            bookmark=textinfo.bookmark),
                        priority=0)
        


BiblioEntry = namedtuple('BiblioEntry', 'uid name text')


class SearchString(str):
    __slots__ = ('target')
    def __new__(cls, value, target, **kwargs):
        obj = str.__new__(cls, value, **kwargs)
        obj.target = target
        return obj

class SearchResults:
    def __init__(self, query, categories=None):
        self.query = query
        self.categories = categories or []
    def add(self, category):
        self.categories.append(category)
    error = False

ResultSection = namedtuple('ResultSection', 'title results')
class ResultsCategory:
    type = None # Stringly typing :).
    caption = None
    def __init__(self, sections=None, total=None):
        self.sections = sections or []
        self.total = total
    def add(self, title, entries):
        self.sections.append( ResultSection(title, entries) )
    def add_row(self, row):
        "Add a row to the most recently added section"
        self.sections[-1][1].append(row)
        
SuttaSection = namedtuple('SuttaSection', 'title suttas')
class SuttaResultsCategory(ResultsCategory):
    type = 'sutta'
    caption = 'Suttas:'
    def add(self, title, suttas):
        self.sections.append( SuttaSection(title, suttas) )

class DictionaryResultsCategory(ResultsCategory):
    type = 'dict'
    caption = 'Dictionaries:'

class FulltextResultsCategory(ResultsCategory):
    type = 'fulltext'
    caption = 'Texts:'

class HTMLRow:
    """Insert a row of arbitary HTML code into a results listing.

    It is the responsibility of the template to put it in the correct
    containing element (i.e. a <li>, or a <tr><td>...)

    """
    def __init__(self, html):
        self.html=html
