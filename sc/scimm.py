"""SuttaCentral In-Memory Module.

Example:
    >>> from sc import scimm
    >>> imm = scimm.imm()
    >>> imm.suttas.get('dn1')
    < Sutta: "Brahmajāla"
        uid=dn1,
        ... >
"""

import time
import math
import regex
import hashlib
import logging
import threading
from bisect import bisect
from datetime import datetime
from itertools import chain
from collections import OrderedDict, defaultdict, namedtuple

import sc
import sc.fonts
from sc import config, textfunctions, textdata
from sc.classes import *
from sc.uid_expansion import uid_to_acro, uid_to_name

from sc.csv_loader import table_reader

import sc.init

logger = logging.getLogger(__name__)

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


class _Imm:
    _uidlangcache = {}
    _cache = None
    _instance = None
    _ready = threading.Event()
    def __init__(self, timestamp):
        self._cache = {}
        self.tim = textdata.tim()
        self.build()
        self.build_parallels_data()
        self.build_parallels()
        self.build_grouped_suttas()
        self.build_parallel_sutta_group('vinaya_pm')
        self.build_parallel_sutta_group('vinaya_kd')
        self.load_epigraphs()
        self.verify_uid_uniqueness()
        self.font_data = sc.fonts.get_fonts_data()
        self.timestamp = timestamp
        self.build_time = datetime.now()
    
    def __call__(self, uid):
        if uid in self.collections:
            return self.collections[uid]
        elif uid in self.divisions:
            return self.divisions[uid]
        elif uid in self.subdivisions:
            return self.subdivisions[uid]
        elif uid in self.suttas:
            return self.suttas[uid]
    
    def verify_uid_uniqueness(self):
        mappings = [self.pitakas, self.sects, self.languages, self.collections, self.divisions, self.subdivisions, self.suttas]
        
        used_uids = dict()
        
        for mapping in mappings:
            for uid, thing in mapping.items():
                if uid in used_uids:
                    if isinstance(thing, Subdivision) and isinstance(used_uids[uid], Division):
                        continue
                    logger.error('UID: {thing.uid} is used for <{thing.__class__.__name__}>: "{thing.name}" and <{other.__class__.__name__}>: "{other.name}"'.format(thing=mapping[uid], other=used_uids[uid]))
                used_uids[uid] = mapping[uid]
        
    def build(self):
        """ Build the sutta central In Memory Model

        This starts from the highest level (i.e. collection) and works to
        the lowest level (i.e. parallels - the relationship between suttas)
        Since it is fully navigitable both up and down this means some
        elements can't be populated initially. This means that suttas
        insert themselves into the subdivision where they belong.

        Some tables are indexed as dicts, with the key being the uid.
        These include:
        collection, division, subdivision, sutta, language
        
        When classes are contained within a class, for example, suttas in
        a subdivision, this is always represented by a list. That list will
        be sorted appropriately and can be directly outputted, generally
        without any need for filtering or sorting.

        When an attribute is a list or dict, the name always end in an 's'
        for example:
        imm.suttas['sn1.1'].subdivision.division.subdivisions[0].suttas[0]

        Some things, such as parallels, are not indexed at all, and are
        only accessable as attributes of the relevant suttas.
        
        The imm also examines the file system. The fully qualified path to a 
        text can be acquired using:
        imm.text_paths[lang][uid]

        """
        
        # Build Pitakas
        self.pitakas = OrderedDict()
        for row in table_reader('pitaka'):
            self.pitakas[row.uid] = Pitaka(uid=row.uid, name=row.name, always_full=row.always_full)

        # Build Sects
        self.sects = OrderedDict()
        for row in table_reader('sect'):
            self.sects[row.uid] = Sect(uid=row.uid, name=row.name)

        # Build Languages (indexed by id)
        self.languages = OrderedDict()
        for row in table_reader('language'):
            self.languages[row.uid] = Language(
                uid=row.uid,
                name=row.name,
                iso_code=row.iso_code,
                isroot=row.isroot,
                priority=int(row.priority),
                search_priority=float(row.search_priority),
                collections=[],
                )
        
        # Note that one isocode can map to multiple languages
        # for example zh modern/ancient
        self.isocode_to_language = {}
        for language in self.languages.values():
            if language.iso_code not in self.isocode_to_language:
                self.isocode_to_language[language.iso_code] = []
            self.isocode_to_language[language.iso_code].append(language)
        
        # From external_text table
        text_refs = defaultdict(list)
        for row in table_reader('external_text'):
            text_refs[row.sutta_uid].append( TextRef(lang=self.languages[row.language], name=None, abstract=row.abstract, url=row.url, priority=row.priority) )

        self._external_text_refs = text_refs.copy()
        
        collections = []
        for i, row in enumerate(table_reader('collection')):
            if row.sect_uid:
                sect = self.sects[row.sect_uid]
            else:
                sect = None
            collection = Collection(
                uid=row.uid,
                name=row.name,
                abbrev_name=row.abbrev_name,
                lang=self.languages[row.language],
                sect=sect,
                pitaka=self.pitakas[row.pitaka_uid],
                menu_seq=i,
                divisions=[] # Populate later
                )
            collections.append(collection)

        # Sort collections by menu_seq
        collections.sort(key=Collection.sort_key)

        self.collections = OrderedDict()
        for collection in collections:
            self.collections[collection.uid] = collection
            self.languages[collection.lang.uid].collections.append(collection)

        # Build divisions (indexed by uid)
        self.divisions = OrderedDict()
        for i, row in enumerate(table_reader('division')):
            collection = self.collections[row.collection_uid]
            
            text_ref = self.get_text_ref(uid=row.uid, lang_uid=collection.lang.uid);
            
            division = Division(
                uid=row.uid,
                name=row.name,
                alt_name=row.alt_name,
                text_ref=text_ref,
                acronym=row.acronym or uid_to_acro(row.uid),
                subdiv_ind=row.subdiv_ind,
                menu_seq=i,
                menu_gwn_ind=bool(row.menu_gwn_ind),
                collection=collection,
                subdivisions=[], # Populate later
            )
            self.divisions[row.uid] = division
            # Populate collections
            collection.divisions.append(division)

        # Sort divisions within collections by menu_seq
        for collection in self.collections.values():
            collection.divisions.sort(key=Division.sort_key)

        # Build subdivisions (indexed by uid)
        self.subdivisions = OrderedDict()
        self.nosubs = set()
        for i, row in enumerate(table_reader('subdivision')):
            subdivision = Subdivision(
                uid=row.uid,
                acronym=row.acronym,
                division=self.divisions[row.division_uid],
                name=row.name,
                vagga_numbering_ind=row.vagga_numbering_ind,
                order=i,
                vaggas=[], # Populate later
                suttas=[] # Populate later
            )
            self.subdivisions[row.uid] = subdivision
            if row.uid.endswith('-nosub'):
                self.nosubs.add(row.uid[:-6])
            # populate divisions.subdivisions
            self.divisions[row.division_uid].subdivisions.append(subdivision)
        
        for division in self.divisions.values():
            if not division.subdivisions:
                subdivision = Subdivision(
                                uid=division.uid,
                                acronym=None,
                                division=division,
                                name=None,
                                vagga_numbering_ind=False,
                                order=9000,
                                vaggas=[],
                                suttas=[])
                division.subdivisions.append(subdivision)
                self.subdivisions[division.uid] = subdivision
        
        # Build vaggas
        self.vaggas = OrderedDict()
        for row in table_reader('vagga'):
            vagga = Vagga(
                subdivision=self.subdivisions[row.subdivision_uid],
                number=row.number,
                name=row.name,
                suttas=[], # Populate later
            )
            self.vaggas[(row.subdivision_uid, row.number)] = vagga
            # Populate subdivision.vaggas
            vagga.subdivision.vaggas.append(vagga)
        
        for subdivision in self.subdivisions.values():
            if not subdivision.vaggas:
                subdivision.vaggas.append(Vagga(
                    subdivision=subdivision,
                    number=0,
                    name=None,
                    suttas=[]))
        
        # Load biblio entries (Not into an instance variable)
        biblios = {}
        for row in table_reader('biblio'):
            biblios[row.uid] = BiblioEntry(
                uid=row.uid,
                name=row.name,
                text=row.text)
        
        # Build suttas (indexed by uid)
        suttas = []
        for row in table_reader('sutta'):
            uid = row.uid
            volpage = row.volpage.split('//')
            acro = row.acronym.split('//')
            if not acro[0]:
                acro[0] = uid_to_acro(uid)
            
            lang = self.languages[row.language]
            
            subdivision = self.subdivisions[row.subdivision_uid]
            
            if row.vagga_number:
                vagga_number = int(row.vagga_number)
                vagga = subdivision.vaggas[vagga_number - 1]
            else:
                vagga_number = 0
                vagga = subdivision.vaggas[0]
            
            m = regex.search(r'(?r)\d+', row.uid)
            if m:
                number = int(m[0])
            else:
                number = 9999
            
            biblio_entry = None
            if row.biblio_uid:
                biblio_entry = biblios.get(row.biblio_uid)
            
            sutta = Sutta(
                uid=row.uid,
                acronym=acro[0],
                alt_acronym=acro[1] if len(acro) > 1 else None,
                name=row.name,
                vagga_number=vagga_number,
                lang=lang,
                subdivision=subdivision,
                vagga=vagga,
                number=number,
                number_in_vagga=row.number_in_vagga,
                volpage=volpage[0],
                alt_volpage_info=volpage[1] if len(volpage) > 1 else None,
                biblio_entry=biblio_entry,
                parallels=[],
                imm=self,
            )
            suttas.append( (uid, sutta) )
        
        suttas = sorted(suttas, key=numsortkey)
        
        self.suttas = OrderedDict(suttas)
        
        # Populate subdivisions.suttas
        for sutta in self.suttas.values():
            sutta.subdivision.suttas.append(sutta)
            sutta.vagga.suttas.append(sutta)
        
    def build_parallels_data(self):
        
        fulls = defaultdict(set)
        partials = defaultdict(set)
        indirects = defaultdict(set)
        # initially we operate purely on ids using id, footnote tuples

        #Populate partial and full parallels
        for row in table_reader('correspondence'):
            if row.partial:
                partials[row.sutta_uid].add( (row.other_sutta_uid, row.footnote) )
                partials[row.other_sutta_uid].add( (row.sutta_uid, row.footnote) )
            else:
                fulls[row.sutta_uid].add( (row.other_sutta_uid, row.footnote) )
                fulls[row.other_sutta_uid].add( (row.sutta_uid, row.footnote) )

        # Populate indirect full parallels
        for id, parallels in fulls.items():
            for pid, footnote in parallels:
                if pid in fulls:
                    indirects[id].update(fulls[pid])

        for id, parallels in indirects.items():
            # Remove self and fulls
            indirects[id] -= set(a for a in indirects[id] if a[0] == id)

        return {
            'fulls': fulls.items(),
            'indirects': indirects.items(),
            'partials': partials.items(),
            }
    
    def build_parallels(self):
        parallels_data = self.build_parallels_data()
        fulls = parallels_data['fulls']
        indirects = parallels_data['indirects']
        partials = parallels_data['partials']
        
        for sutta_uid, parallels in fulls:
            sutta = self.suttas[sutta_uid]
            for p_uid, note in parallels:
                p_sutta = self.suttas[p_uid]
                sutta.parallels.append(Parallel(p_sutta, False, False, note))
                
        for sutta_uid, parallels in indirects:
            sutta = self.suttas[sutta_uid]
            for p_uid, note in parallels:
                p_sutta = self.suttas[p_uid]
                sutta.parallels.append(Parallel(p_sutta, False, True, note))

        for sutta_uid, parallels in partials:
            sutta = self.suttas[sutta_uid]
            for p_uid, note in parallels:
                p_sutta = self.suttas[p_uid]
                sutta.parallels.append(Parallel(p_sutta, True, False, note))

        for sutta in self.suttas.values():
            sutta.parallels.sort(key=Parallel.sort_key)
    
    def build_grouped_suttas(self):
        vinaya_rules = {}
        for i, row in enumerate(table_reader('vinaya_rules')):
            uid = row.uid
            
            rule = GroupedSutta(
                uid=uid,
                volpage=row.volpage_info,
                imm=self,
            )
            
            subdivision = rule.subdivision
            subdivision.suttas.append(rule)
            
            subdivision.vaggas[0].suttas.append(rule)
            
            self.suttas[uid] = rule

    def build_parallel_sutta_group(self, table_name):
        """ Generate a cleaned up form of the table data
        
        A parallel group is a different way of defining parallels, in essence
        it is a group of suttas (in the broader sense) from different
        traditions, all of which are the same 'thing', this is for example
        particulary relevant in the Patimokkha which is extremely similar
        across the traditions.

        All suttas within a sutta group share the same name (title) this is
        done mainly because many manuscripts lack titles (these being added
        by redactors). Also their uids are consistently derived from their
        division/subdivision uid.

        Some of this code is pretty messy but that can't really be helped
        because it's really the underlying logic that is pretty messy.
        
        """
        
        def normalize_uid(uid):
            return uid.replace('#', '-').replace('*', '')
        
        org_by_rule = list(table_reader(table_name))
        
        by_column = []
        for i, column in enumerate(zip(*org_by_rule)): #rotate
            if i == 0:
                by_column.append(column)
            else:
                division_uid = column[0]
                try:
                    division = self.divisions[division_uid]
                except KeyError:
                    raise Exception('Bad column data `{}`'.format(column))
                division_negated_parallel = NegatedParallel(
                    division=division)
                division_maybe_parallel = MaybeParallel(
                    division=division)
                new_column = []
                by_column.append(new_column)
                for j, uid in enumerate(column):
                    if j <= 1:
                        new_column.append(uid)
                    else:
                        if not uid or uid == '-':
                            new_column.append(division_negated_parallel)
                        elif uid == '?':
                            new_column.append(division_maybe_parallel)
                        else:
                            try:
                                sutta = self.suttas[uid.rstrip('*')]
                            except KeyError:
                                sutta = self.suttas[normalize_uid(uid)]
                                
                            new_column.append(sutta)
        
        by_row = list(zip(*by_column))
        #self.by_column = by_column
        #self.by_row = by_row
        
        for row in by_row[2:]:
            group = ParallelSuttaGroup(row[0], row[1:])
            for rule in row[1:]:
                if isinstance(rule, GroupedSutta):
                    if hasattr(rule, 'parallel_group'):
                        if not isinstance(rule.parallel_group, MultiParallelSuttaGroup):
                            rule.parallel_group = MultiParallelSuttaGroup(rule.parallel_group)
                        rule.parallel_group.add_group(group)
                    else:
                        rule.parallel_group = group

    def build_search_data(self):
        """ Build useful search data.

        Note that the size of the data is somewhat less than 2mb """
        
        suttastringsU = []
        seen = set()
        for sutta in self.suttas.values():
            if isinstance(sutta, GroupedSutta):
                if sutta.name in seen:
                    continue
                seen.add(sutta.name)
            name = sutta.name.lower()
            suttastringsU.append("  {}  ".format("  ".join(
                                [sutta.uid,
                                sutta.lang.iso_code,
                                sutta.acronym,
                                sutta.alt_acronym or '',
                                name,
                                textfunctions.codely(name),
                                textfunctions.plainly(name),
                                sutta.volpage_info,
                                sutta.alt_volpage_info or '',
                                "  ".join( t.lang.iso_code
                                    for t in sutta.translations,) or '',]))
                                )
        suttastrings = [s.lower() for s in suttastringsU]
        # Only simplify the name.
        suttanamesimplified = (["  {}  ".format(
            textfunctions.simplify(sutta.name, sutta.lang.iso_code))
            for sutta in self.suttas.values()])

        self.searchstrings = list(zip(self.suttas.values(), suttastrings, suttastringsU, suttanamesimplified))

    def generate_search_data(self):
        seen = set()
        out = []
        for sutta in self.suttas.values():
            if isinstance(sutta, GroupedSutta):
                if sutta.name in seen:
                    continue
                seen.add(sutta.name)
            name = sutta.name
            plain_name = textfunctions.codely(name)
            coded_name = textfunctions.plainly(name)
            simple_name = textfunctions.simplify(sutta.name, sutta.lang.iso_code)

            searchdata = {'uid': sutta.uid,
                'lang_code': sutta.lang.iso_code,
                'acronym': sutta.acronym,
                'name': name,
                'plain_name': plain_name,
                'coded_name': coded_name,
                'simple_name': simple_name,
                'volpage': sutta.volpage,
                'languages': " ".join(t.lang.iso_code for t in sutta.translations)}

            if sutta.alt_volpage_info:
                searchdata['volpage'] += '  ' + sutta.alt_volpage_info

            if sutta.alt_acronym:
                searchdata['acronym'] += '  ' + sutta.alt_acronym

            for k in list(searchdata.keys()):
                if searchdata[k] is None:
                    del searchdata[k]
            searchdata['md5'] = hashlib.md5(str(searchdata).encode()).hexdigest()[0:5]
            yield searchdata
    
    def get_text_ref(self, uid, lang_uid):
        textinfo = self.tim.get(uid=uid, lang_uid=lang_uid)
        if textinfo:
            return TextRef.from_textinfo(textinfo, self.languages[lang_uid])
        
        for textref in self._external_text_refs.get(uid, []):
            if textref.lang.uid == lang_uid:
                return textref

        m = regex.match(r'(.*?)(\d+)-(\d+)', uid)
        if m:
            textinfo = self.tim.get(uid=m[1]+m[2], lang_uid=lang_uid)
            if textinfo:
                return TextRef.from_textinfo(textinfo, self.languages[lang_uid])

    def get_root_lang_from_uid(self, uid):
        if uid in self.suttas:
            return self.suttas[uid].lang.uid
        else:
            div_uid = uid
            while div_uid:
                if div_uid in self.divisions:
                    return self.divisions[div_uid].collection.lang.uid
                if div_uid in self.subdivisions:
                    return self.subdivisions[div_uid].division.collection.lang.uid
                div_uid = div_uid[:-1]
        if uid[0] == 't':
            return 'lzh'
        if uid[:3] == 'skt':
            return 'skt'
        raise ValueError("No root lang could be determined for uid: {}".format(uid))
            
    def get_translations(self, uid, root_lang_uid):
        out = []
        for textref in self._external_text_refs.get(uid, []):
            if textref.lang.uid == root_lang_uid:
                continue
            out.append(textref)
        
        textinfos = self.tim.get(uid=uid)
        seen = set()
        for lang_uid, textinfo in textinfos.items():
            if lang_uid == root_lang_uid:
                continue
            out.append(TextRef.from_textinfo(textinfo, self.languages[lang_uid]))
            seen.add(lang_uid)
        
        m = regex.match(r'(.*?)(\d+)-(\d+)', uid)
        if m:
            textinfos = self.tim.get(uid=m[1]+m[2])
            for lang_uid, textinfo in textinfos.items():
                if lang_uid == root_lang_uid:
                    continue
                if lang_uid in seen:
                    continue
                out.append(TextRef.from_textinfo(textinfo, self.languages[lang_uid]))
                
        out.sort(key=TextRef.sort_key)
        
        
        return out

    def get_text_refs(self, uid):
        out = []
        for textref in self._external_text_refs.get(uid, []):
            out.append(textref)
        def fuzzy_attempts(uid):
            yield uid
            m = regex.match(r'(.*?)(\d+)(-\d+)?', uid)
            if m:
                # Dedash
                if m[3]:
                    yield m[1] + m[2]
                # Remove number
                yield m[1].rstrip('.')
        textinfos = None
        for fuid in fuzzy_attempts(uid):
            textinfos = self.tim.get(uid=fuid)
            if textinfos:
                for lang_uid, textinfo in textinfos:
                    out.append(TextRef.from_textinfo(textinfo, self.languages[lang_uid]))
                break
        
        out.sort(key=TextRef.sort_key)
        return out
        
    def get_fuzzy(self, uid):
        uid = uid.lstrip('~')
        uid = uid.split('#')[0]
        obj = self(uid)
        
        if not obj:
            if '-' in uid:
                obj = self(uid.split('-')[0])
        
        if obj:
            return obj
        
        while uid:
            uid = uid[:-1]
            obj = self(uid)
            if obj:
                return obj
        return None

    def text_path(self, uid, lang_uid):
        try:
            textinfo = self.tim.get(uid, lang_uid)
        except TypeError:
            logger.error('Not valid uid: "{}" or lang: "{}"'.format(uid, lang_uid))
            raise
        if not textinfo:
            return None
        return textinfo.path
        
    def text_exists(self, uid, lang_uid):
        return self.tim.exists(uid, lang_uid)
    
    def get_text_data(self, uid, language_code=None):
        return self.tim.get(uid, language_code)
        
    def guess_subdiv_uid(self, uid):
        # Just keep slicing it until we find something that
        # matches. It's good enough.
        while len(uid) > 0:
            if uid in self.subdivisions:
                return uid
            uid = uid[:-1]

    def guess_div_uid(self, uid):
        while len(uid) > 0:
            if uid in self.divisions:
                return uid
            uid = uid[:-1]
    
    def guess_lang(self, uid):
        if not uid:
            return None
        obj = self.get_fuzzy(uid)
        if obj is None:
            return None
        
        while True:
            try:
                return obj.lang
            except AttributeError:
                pass
            if 'collection' in obj:
                obj = obj.collection
            elif 'division' in obj:
                obj = obj.division
            elif 'subdivision' in obj:
                obj = obj.subdivision
            else:
                return None                
            
    
    @staticmethod
    def get_text_author(filepath):
        """ Examines the file to discover the author
        
        This requires that a tag appears
        <meta author="Translated by Bhikkhu Bodhi">
        
        This must be in head and occur in the first 5 lines.
        The attribute must be quoted and should be fully qualified.
        <meta author='Edited by Bhante Sujato'>
        
        <meta author="Pali text from the Mahāsaṅgīti Tipiṭaka">
        
        """
        
        with filepath.open('r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i > 6:
                    break
                m = _Imm._author_search(line)
                if m:
                    return m[1]
        return None

    def load_epigraphs(self):
        import lxml.etree
        file = sc.data_dir / 'table' / 'epigraphs.xml'
        self.epigraphs = []
        
        doc = lxml.etree.parse(str(file))
        valid = 0
        for count, element in enumerate(doc.findall('//epigraph')):
            id = element.get('id')
            uid = element.find('uid').text
            content = regex.match(r'(?s)<content>\n?(.*)</content>',
                lxml.etree.tostring(element.find('content'),
                encoding='unicode'))[1]
            
            if uid not in self.suttas:
                logger.warning('{}:{} - "{}" does not match any known sutta uid'.format(file.name, element.sourceline, uid))
            else:
                sutta = self.suttas[uid]
                href = None
                if element.find('href').text:
                    href = element.find('href').text
                else:
                    for tr in sutta.translations:
                        if tr.url.startswith('/en'):
                            href = tr.url
                if href is None:
                    logger.warning('{}:{} - Sutta "{}" has no english translation. Using details page instead.'.format(file.name, element.sourceline, uid))
                    href = '/{}'.format(uid)
                else:
                    self.epigraphs.append({'sutta': self.suttas[uid], 'content': content, 'href': href})
                    valid += 1
        logger.info('Loaded {} epigraphs, {} are valid, {} are invalid'.format(count + 1, valid, count - valid))

    def get_random_epigraph(self):
        import random
        return random.choice(self.epigraphs)

    def get_next_prev(self, uid, lang_uid):
        if not hasattr(self, 'sutta_order_cache'):
            self.sutta_order_cache = soc = defaultdict(dict)
            for division in self.divisions.values():
                suttas = list(chain(*(sd.suttas for sd in division.subdivisions)))
                
                prev = None
                for sutta in suttas:
                    if prev:
                        soc[sutta.uid]['prev'] = prev.uid
                        soc[prev.uid]['next'] = sutta.uid
                    prev = sutta
        soc = self.sutta_order_cache
        tim = self.tim
        
        nextdata = None
        prevdata = None
        
        textdata = tim.get(uid=uid, lang_uid=lang_uid)
        
        nextprev = soc.get(uid)
        if nextprev:
            # if the sutta data says that a sutta is the start/end of a 
            # division, we will trust it, hence we use 'False', for there
            # is no next/prev sutta, rather than 'None' for unknown.
            if 'next' in nextprev:
                nextdata = tim.get(uid=nextprev.get('next'), lang_uid=lang_uid)
                if nextdata and textdata and nextdata.path == textdata.path:
                    nextdata = None
            else:
                nextdata = False
            if 'prev' in nextprev:
                prevdata = tim.get(uid=nextprev.get('prev'), lang_uid=lang_uid)
                if prevdata and textdata and prevdata.path == textdata.path:
                    prevdata = None
            else:
                prevdata = False
    
        
        if textdata:
            if nextdata is None and textdata.next_uid:
                nextdata = tim.get(uid=textdata.next_uid, lang_uid=lang_uid)
            if prevdata is None and textdata.prev_uid:
                prevdata = tim.get(uid=textdata.prev_uid, lang_uid=lang_uid)
        return {'next': nextdata,
                'prev': prevdata}
        
def imm(wait=True):
    """ Get an instance of the DBR.

    Use only this function to get an instance of the DBR. For most intents
    and purposes the DBR should be considered a singleton. However it can
    be regenerated, and while being regenerated, a 'stale' copy can be be
    served, hence multiple versions can exist for a short time. (The stale
    copies will be garbage collected when they fall out of scope)
    
    If the imm is being generated, this function will block until it is
    ready. If the imm has already been generated, it is virtually free to
    call.

    """

    if wait:
        if not _Imm._instance:
            _Imm._ready.wait()
            if not _Imm._instance:
                raise SystemExit("IMM Build Failed, unable to proceed")
    return _Imm._instance

def build():
    timestamp = max(int(file.stat().st_mtime) for file in sc.table_dir.glob('**/*'))
    if not _Imm._instance or _Imm._instance.timestamp != timestamp:
        logger.info('Building IMM')
        try:
            start = time.time()
            _Imm._instance = _Imm(timestamp)
            logger.info('imm build took {} seconds'.format(time.time() - start))
            _Imm._ready.set()
        except Exception as e:
            logger.error("Critical Error: IMM buid failed.", e)
            _Imm._ready.set()
