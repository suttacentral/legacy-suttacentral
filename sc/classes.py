import regex
from collections import namedtuple
from sc.util import ConciseRepr

Language = namedtuple('Language', 
    'uid name isroot iso_code priority collections')


Sect = namedtuple('Sect', 'uid name')


Pitaka = namedtuple('Pitaka', 'uid name always_full')


class Collection(ConciseRepr, namedtuple('Collection',
        'uid name abbrev_name lang sect pitaka menu_seq divisions')):
    __slots__ = ()
    
    @staticmethod
    def sort_key(collection):
        """Return the canonical sort key."""
        return collection.menu_seq


class Division(ConciseRepr, namedtuple('Division', 
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


class Subdivision(ConciseRepr, namedtuple('Subdivision',
        'uid division name acronym vagga_numbering_ind vaggas suttas order')):
    __slots__ = ()


class Vagga(ConciseRepr, namedtuple('Vagga', 
        'subdivision number name suttas')):
    __slots__ = ()


class Sutta(ConciseRepr, namedtuple('Sutta',
        'uid acronym alt_acronym name vagga_number '
        'number_in_vagga number lang subdivision vagga '
        'volpage_info alt_volpage_info biblio_entry text_ref '
        'translations parallels')):
    __slots__ = ()
    
    no_show_parallels = False
    
    def __hash__(self):
        return hash(self.uid)
    
    @staticmethod
    def canon_url(uid, lang_code):
        return '/{uid}/{lang}'.format(uid=uid, lang=lang_code)


class VinayaRule:
    """The VinayaRule is like a Sutta, except most of the 
    information is generated on the fly. This involves a bit
    more CPU but the Vinaya is unlikely to be accessed much,
    and it requires a huge amount of memory to 'unfold' it
    in full. So we only 'unfold' data from the master table
    as required.
    
    This is useful because when I did 'unfold' the whole vinaya
    data the memory requirements for the server tripled. It's not
    a trivial memoy optimization.
    
    """
    
    __slots__ = {'uid', 'ref_uid', 'volpage_info', 'imm', '_rule_row'}
    
    no_show_parallels = True
    
    alt_volpage_info = None
    biblio_entry = None
    alt_acronym = None
    
    def __init__(self, uid, volpage_info, imm):
        self.uid = uid
        self.volpage_info = volpage_info
        self.imm = imm
    
    @property
    def name(self):
        return self._rule_row[0]
    
    @property
    def acronym(self):
        return self.imm.uid_to_acro(self.uid)
    
    @property
    def _subdivision_uid(self, _rex=regex.compile(r'(.*?)\d+$')):
        return _rex.match(self.uid)[1]
    
    @property
    def subdivision(self):
        return self.imm.subdivisions[self._subdivision_uid]
    
    @property
    def lang(self):
        return self.subdivision.division.collection.lang
    
    @property
    def vagga(self):
        return self.subdivision.vaggas[0]
    
    @property
    def text_ref(self):
        return []
    
    @property
    def translations(self):
        return []
    
    @property
    def parallels(self):
        out = []
        for i, e in enumerate(self._rule_row):
            if e == self or i == 0:
                continue
            if isinstance(e, VinayaRule):
                out.append(Parallel(sutta=e, partial=False,
                    indirect=False, footnote=None))
            else:
                out.append(e)
        return out
    
    @property
    def brief_acronym(self):
        return ' '.join(self.acronym.split(' ')[-2:])

class Parallel(ConciseRepr, namedtuple('Parallel',
        'sutta partial indirect footnote')):
    __slots__ = ()

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

class TextRef(ConciseRepr, namedtuple('TextRef', 
        'lang abstract url priority')):
    __slots__ = ()

    @staticmethod
    def sort_key(t):
        """The canonical ordering as follows:
            1) language id
            2) sequence number
        To be used with sort() or sorted()."""
        return (not t.url.startswith('/'), t.lang.priority, t.lang.iso_code, t.priority)


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