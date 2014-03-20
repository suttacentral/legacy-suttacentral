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
        'volpage_info alt_volpage_info biblio_entry '
        'parallels, imm')):
    __slots__ = ()
    
    group_parallels = None
    
    def __hash__(self):
        return hash(self.uid)

    @property
    def details_uid(self):
        return self.uid.replace('#', '_')
    
    @staticmethod
    def canon_url(uid, lang_code, bookmark=''):
        if not isinstance(lang_code, str):
            lang_code = lang_code.uid
        url = '/{lang}/{uid}'.format(uid=uid, lang=lang_code)
        if bookmark:
            url += '#' + bookmark
        return url

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
        

class GroupedSutta:
    """The GroupedSutta is like a Sutta, except it belongs to a group of
    related suttas and most of the information is generated on the fly from
    it's group data.
    
    """
    
    __slots__ = {'uid', 'ref_uid', 'volpage_info', 'imm', '_textinfo',
                'parallel_group'}
    
    no_show_parallels = True
    
    alt_volpage_info = None
    biblio_entry = None
    alt_acronym = None
    
    def __init__(self, uid, volpage_info, imm):
        self.uid = uid
        self.volpage_info = volpage_info
        self.imm = imm
        self._textinfo = imm.tim.get(uid, self.lang.uid)
    
    @property
    def name(self):
        if self._textinfo:
            name = self._textinfo.name
            if name:
                return name
        try:
            return self.parallel_group.name
        except AttributeError as e:
            e.args = list(e.args) + ['No group found for {}'.format(self.uid)]
            raise e

    @property
    def details_uid(self):
        return self.uid.replace('#', '_')
    
    @property
    def acronym(self):
        return self.imm.uid_to_acro(self.uid)
    
    @property
    def _subdivision_uid(self, _rex=regex.compile(r'(.*?)\d+[a-g]?$')):
        uid = self.uid.split('#')[0]
        m = _rex.match(uid)
        if m:
            return m[1]
        else:
            raise TypeError('`{}` could not be reduced to a subdivision_uid.'.format(self.uid))
    
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
    
    @property
    def text_ref(self):
        return self.imm.get_text_ref(self.uid, self.lang.uid)
        
    @property
    def translations(self):
        return self.imm.get_translations(self.uid, self.lang.uid)
    
    parallels = []

    @property
    def parallels_count(self):
        return len(self.parallels) + max(0, self.parallel_group.real_count() - 1)
    
    @property
    def brief_uid(self):
        return ' '.join(self.uid.split('-')[-1:])
    
    @property
    def brief_acronym(self):
        return self.imm.uid_to_acronym(self.brief_uid)
    
    @property
    def brief_name(self):
        return self.imm.uid_to_name(self.brief_uid)

class ParallelSuttaGroup:
    """ A class which acts a lot like a list of parallels """
    def __init__(self, name, entries):
        self.name = name
        self.entries = entries

    def real_count(self):
        return len([e for e in self.entries if isinstance(e, GroupedSutta)])
    
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

class MultiParallelSuttaGroup(ParallelSuttaGroup):
    def __init__(self, initial):
        self.groups = [initial]
        self.name = initial.name

    def add_group(self, group):
        self.groups.append(group)

    def real_count(self):
        return len(list(self.parallels()))

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

    @classmethod
    def from_textinfo(cls, textinfo, lang):
        return cls(lang=lang,
                        abstract=textinfo.author or lang.name,
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
