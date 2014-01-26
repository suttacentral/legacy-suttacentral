import regex
from collections import namedtuple

TextRefBase = namedtuple('TextRef', 'lang, abstract, url, priority')

ParallelBase = namedtuple('ParallelBase',
                                  'sutta, partial, indirect, footnote')

BiblioEntry = namedtuple('BiblioEntry', 'uid, name, text')

DivisionBase = namedtuple('DivisionBase', '''
    uid, collection, name, alt_name, acronym,
    subdiv_ind, menu_seq, menu_gwn_ind, text_ref, subdivisions''')

SubdivisionBase = namedtuple('SubdivisionBase',
    'uid, division, name, acronym, vagga_numbering_ind, vaggas, suttas, order')

VaggaBase = namedtuple('VaggaBase', ('subdivision', 'number', 'name', 'suttas') )

CollectionBase = namedtuple('CollectionBase',
    ('uid', 'name', 'abbrev_name', 'lang', 'sect', 'pitaka', 'menu_seq',
     'divisions'))

SuttaBase = namedtuple('SuttaBase', (
        'uid', 'acronym', 'alt_acronym', 'name', 'vagga_number', 'number_in_vagga', 'number',
        'lang', 'subdivision', 'vagga', 'volpage_info', 'alt_volpage_info',
        'biblio_entry', 'text_ref', 'translations', 'parallels') )

VinayaDivision = namedtuple('VinayaDivision', ['uid', 'name', 'rules'])

class NamedTupleBriefRepr:
    __slots__ = ()
    def __repr__(self):
        from numbers import Number
        details = []
        
        for attr in sorted(self._fields, key=lambda s: '' if s == 'uid' else s):
            details.append('{}='.format(attr))
            value = getattr(self, attr)
            if isinstance(value, str):
                details[-1] += repr(value)
            elif isinstance(value, Number):
                details[-1] += str(value)
            elif isinstance(value, NamedTupleBriefRepr):
                if hasattr(value, 'uid'):
                    details[-1] += '<{} {}>'.format(value.__qualname__, value.uid)
                else:
                    details[-1] += '<{}>'.format(value.__qualname__)
            else:
                try:
                    details[-1] += self._repr_len(value)
                except TypeError:
                    details[-1] += repr(value)
        
        return '<{} {}>'.format(self.__qualname__,
            '    \n'.join(details))
    
    def _repr_len(self, value):

        if len(value) == 0:
            return "{}()".format(type(value).__qualname__)
        
        if isinstance(value, dict):
            content = value.values()
        else:
            content = value
        
        types = {type(e) for e in content}
        
        if len(types) == 1:
            typestring = 'of type <{}>'.format(
                type(next(iter(content))).__qualname__)
        else:
            typestring = 'of mixed type'
        
        return '{}({} {})'.format(
            type(value).__qualname__, len(value), typestring)

Language = namedtuple('Language', 'uid, name, isroot, iso_code, priority, collections')

Sect = namedtuple('Sect', ('uid', 'name'))

Pitaka = namedtuple('Pitaka', ('uid', 'name'))

class SearchString(str):
    __slots__ = ('target')
    def __new__(cls, value, target, **kwargs):
        obj = str.__new__(cls, value, **kwargs)
        obj.target = target
        return obj


# Because a Sutta contains references to other complete objects which
# each have their own verbose default __repr__, it is necessary to make
# a custom __repr__ which summarises the enclosed objects.
class Sutta(NamedTupleBriefRepr, SuttaBase):
    __slots__ = ()
    
    no_show_parallels = False
    
    def __hash__(self):
        return hash(self.uid)
    
    @staticmethod
    def canon_url(uid, lang_code):
        return '/{uid}/{lang}'.format(uid=uid, lang=lang_code)

class VinayaRule(Sutta):
    __slots__ = ()
    
    no_show_parallels = True

class Vagga(NamedTupleBriefRepr, VaggaBase):
    __slots__ = ()

class Parallel(NamedTupleBriefRepr, ParallelBase):
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

class TextRef(NamedTupleBriefRepr, TextRefBase):
    __slots__ = ()

    @staticmethod
    def sort_key(t):
        """The canonical ordering as follows:
            1) language id
            2) sequence number
        To be used with sort() or sorted()."""
        return (not t.url.startswith('/'), t.lang.priority, t.lang.iso_code, t.priority)

class Collection(NamedTupleBriefRepr, CollectionBase):
    __slots__ = ()
    
    @staticmethod
    def sort_key(collection):
        """Return the canonical sort key."""
        return collection.menu_seq

class Division(NamedTupleBriefRepr, DivisionBase):
    __slots__ = ()

    @staticmethod
    def sort_key(division):
        """Return the canonical sort key."""
        return division.menu_seq

    def has_subdivisions(self):
        return len(self.subdivisions) > 1

class Subdivision(NamedTupleBriefRepr, SubdivisionBase):
    __slots__ = ()

class SearchResults:
    def __init__(self, query, categories=None):
        self.query = query
        self.categories = categories or []
    def add(self, category):
        self.categories.append(category)

ResultSection = namedtuple('ResultSection', 'title, results')
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
        
SuttaSection = namedtuple('SuttaSection', 'title, suttas')
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