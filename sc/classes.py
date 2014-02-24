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
    
    group_parallels = None
    
    def __hash__(self):
        return hash(self.uid)
    
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

class GroupedSutta:
    """The GroupedSutta is like a Sutta, except it belongs to a group of
    related suttas and most of the information is generated on the fly from
    it's group data.
    
    """
    
    __slots__ = {'uid', 'ref_uid', 'volpage_info', 'imm',
                'parallel_group'}
    
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
        try:
            return self.parallel_group.name
        except AttributeError as e:
            e.args = list(e.args) + ['No group found for {}'.format(self.uid)]
            raise e
    
    @property
    def acronym(self):
        return self.imm.uid_to_acro(self.uid)
    
    @property
    def _subdivision_uid(self, _rex=regex.compile(r'(.*?)\d+[a-g]?$')):
        m = _rex.match(self.uid)
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
    
    def _get_uid_bookmark_pairs(self):
        """ Provides uids which can be tried in turn """
        uid = self.uid
        yield (uid, '') # Direct match for rule
        m = self._subdiv_match(uid)
        if m: 
            yield (m[1], m[2])
        m = self._div_match(uid)
        if m:
            yield (m[1], m[2])
        raise StopIteration
    
    @property
    def text_ref(self):
        # We are not using external references for Vinaya
        imm = self.imm
        lang = self.lang
        uid = self.uid
        
        lang_uid_paths = imm.text_paths_by_lang.get(lang.uid)
        if not lang_uid_paths:
            return None
        
        for ref_uid, bookmark in self._get_uid_bookmark_pairs():
            path = lang_uid_paths.get(ref_uid)
            if path:
                break
        else:
            return None
        
        return TextRef(lang=lang,
                        abstract=None,
                        url=Sutta.canon_url(uid=ref_uid,
                                            lang_code=lang.uid,
                                            bookmark=bookmark),
                        priority=0)
    
    @property
    def translations(self):
        # We are not using external references for Vinaya
        imm = self.imm
        lang = self.lang
        uid = self.uid
        
        out = {}
        
        for ref_uid, bookmark in self._get_uid_bookmark_pairs():
            lang_paths = imm.text_paths_by_uid.get(ref_uid, {})
            for lang_uid, path in lang_paths.items():
                if lang_uid in out or lang_uid == lang.uid:
                    continue
                out[lang_uid] = (ref_uid, bookmark, path)
        
        def create_abstract(lang_uid):
            lang_name = imm.uid_to_name(lang_uid)
            if not lang_name or lang_name.lower() == lang_uid:
                return None
            return '{} translation'.format(lang_name.title())
        
        return tuple(sorted((TextRef(imm.languages[lang_uid],
                                abstract=create_abstract(lang_uid),
                                url=Sutta.canon_url(uid=ref_uid,
                                    lang_code=lang_uid,
                                    bookmark=bookmark),
                                priority=0)
                        for lang_uid, (ref_uid, bookmark, path)
                        in out.items()),
                    key=TextRef.sort_key))
    
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