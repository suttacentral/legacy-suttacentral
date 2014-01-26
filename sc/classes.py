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

class Slotted:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        for key in self.__slots__:
            if not hasattr(self, key):
                raise ValueError('required keyword arg {} missing'.format(
                    key))
    def __repr__(self):
        from numbers import Number
        details = []
        
        for attr in sorted(self.__slots__, key=lambda s: '' if s == 'uid' else s):
            details.append('{}='.format(attr))
            value = getattr(self, attr)
            if isinstance(value, str):
                details[-1] += value
            elif isinstance(value, Number):
                details[-1] += str(value)
            else:
                try:
                    details[-1] += self._repr_len(value)
                except AttributeError:
                    details[-1] += repr(value)
        
        return '<{} {}>'.format(self.__qualname__,
            '    \n'.join(details))
    
    def _repr_len(self, value):
        if isinstance(value, list):
            return '[{} values]'.format(len(value))
        elif isinstance(value, tuple):
            return '({} values)'.format(len(value))
        elif isinstance(value, set):
            return '{{{} values}}'.format(len(value))
        elif isinstance(value, dict):
            return '{{{} items}}'.format(len(value))
        else:
            return '<{} {} items>'.format(value.__qualname__, len(value))

class VinayaRule(Slotted):
    __slots__ = {'uid', 'name', 'division', 'text_ref', 'translations', 'parallels'}
    def __repr__(self):
        return "<VinayaRule(uid='{}', division=<{}>, text_ref=<{}>, translations=[{}], parallels=[{}])".format(
            self.uid, self.division.uid, self.text_ref, 
            len(self.translations), len(self.parallels))

class VinayaRuleSet(Slotted):
    __slots__ = {'uid', 'name', 'rules'}

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
class Sutta(SuttaBase):
    __slots__ = ()
    def __repr__(self):
        return """< Sutta: "{self.name}"
    uid={self.uid},
    subdivision=<{self.subdivision.uid}>,
    number={self.number},
    lang=<{self.lang.uid}>,
    acronym={self.acronym},
    alt_acronym={self.alt_acronym},
    name={self.name},
    vagga=vagga,
    number_in_vagga={self.number_in_vagga},
    volpage_info={self.volpage_info}, alt_volpage_info={self.alt_volpage_info},
    biblio_entry={self.biblio_entry},
    text_ref={self.text_ref},
    translations={translations},
    parallels={parallels} >\n""".format(
        self=self,
        vagga="<{}>".format(self.vagga.name) if self.vagga else '',
        translations="[{}]".format(", ".join(
        "<{}>".format(a.lang.uid) for a in self.translations)),
        parallels="[{}]".format(", ".join(
            "<{}{}>".format(a.sutta.uid, '*' if a.partial else '')
                for a in self.parallels)),
        )
    
    no_show_parallels = False
    
    def __hash__(self):
        return hash(self.uid)
    
    @staticmethod
    def canon_url(uid, lang_code):
        return '/{uid}/{lang}'.format(uid=uid, lang=lang_code)

class VinayaRule(Sutta):
    __slots__ = ()
    
    no_show_parallels = True

class Vagga(VaggaBase):
    __slots__ = ()
    def __repr__(self):
        return """<Vagga: "{self.name}"
    uid={self.uid},
    subdivision=<{self.subdivision.uid}>,
    name={self.name},
    suttas=[{suttas}]\n""".format(self=self,
        suttas=", ".join("<{}>".format(sutta.uid) for sutta in self.suttas))
    

class Parallel(ParallelBase):
    __slots__ = ()
    def __repr__(self):
        return ("<Parallel: sutta={self.sutta.uid}, "
        "partial={self.partial}, "
        "footnote={self.footnote}>").format(self=self)

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

class TextRef(TextRefBase):
    __slots__ = ()
    
    def __repr__(self):
        return '<TextRef: lang=<{self.lang.uid}>, url="{self.url}">'.format(self=self)

    @staticmethod
    def sort_key(t):
        """The canonical ordering as follows:
            1) language id
            2) sequence number
        To be used with sort() or sorted()."""
        return (not t.url.startswith('/'), t.lang.priority, t.lang.iso_code, t.priority)

class Collection(CollectionBase):
    __slots__ = ()
    def __repr__(self):
        return """<Collection: "{self.name}",
    uid={self.uid},
    name={self.name},
    lang=<{self.lang.uid}>,
    sect=<{sect}>,
    pitaka=<{self.pitaka.uid}>,
    menu_seq=<{self.menu_seq}>,
    divisions={divisions}\n""".format(
        self=self,
        sect=getattr(self.sect, 'uid', None),
        divisions="[{}]".format(", ".join(
            "<{}>".format(a.name) for a in self.divisions)))

    @staticmethod
    def sort_key(collection):
        """Return the canonical sort key."""
        return collection.menu_seq

class Division(DivisionBase):
    __slots__ = ()
    def __repr__(self):
        return """<Division: "{self.name}"
    uid={self.uid},
    collection={collection},
    name={self.name},
    alt_name={self.alt_name},
    acronym={self.acronym},
    subdiv_ind={self.subdiv_ind},
    text_ref={self.text_ref},
    menu_seq={self.menu_seq},
    menu_gwt_ind={self.menu_gwt_ind},
    subdivisions={subdivisions}\n""".format(self=self,
        collection="<Collection>",
        subdivisions="[{}]".format(
            ", ".join("<{}>".format(a.uid)
                for a in self.subdivisions)),
        )

    @staticmethod
    def sort_key(division):
        """Return the canonical sort key."""
        return division.menu_seq

    def has_subdivisions(self):
        return len(self.subdivisions) > 1

class Subdivision(SubdivisionBase):
    __slots__ = ()
    def __repr__(self):
        return """<Subdivision: "{self.name}"
    uid={self.uid}
    division=<{self.division.uid}>
    name={self.name}
    acronym={self.acronym}
    vagga_numbering_ind={self.vagga_numbering_ind},
    vaggas=[{vaggas}],
    suttas=[{suttas}]\n""".format(
        self=self,
        vaggas=", ".join(str(len(a)) for a in self.vaggas),
        suttas=", ".join("<{}>".format(a.uid) for a in self.suttas),
        )



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