#!/usr/bin/env python3.3

# Import user modules.
import setup, textfunctions
from classes import Sutta, Translation, Parallel, Vagga, BiblioEntry, Subdivision, Division, Collection, Language

from mysql import connector as mysql

import collections, functools, itertools, time, regex, hashlib, os, threading, math, datetime, cherrypy
from collections import OrderedDict, defaultdict, namedtuple

logger = setup.logging.getLogger(__name__)

def numsort(input, index=0):
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

def db_grab(conn):
    """Sucks an entire database from SQL.

    Conn should be a mysql database connection.

    The result is a namedtuple 'Database'. Tables can be accessed as
    attributes of the Database object. Each table is a dictionary indexed
    by Primary Key, if possible. If there is no Primary key, it is indexed
    numerically starting at 0. To iterate over a table in order:
    >>> for k in sorted(sutta):
    >>>     sutta[k]
    To get a list of all suttas in-order
    >>> [db.sutta[key] for key in sorted(db.sutta)]
    This is fully 50% as fast as iterating over the equivilant pre-sorted list."""

    #Here the byte input can be converted to the consumed type
    def conform(input, field_type):
        if field_type is int:
            if input is None:
                return 0
            return int(input)
        elif field_type is datetime:
            if input.startswith(b'0000'): return None
            return datetime(*(int(a) for a in regex.split(r'[- :]', input.decode())))
        if input is None or input == b'NULL':
            return None

        return input.decode()

    #Here special types can be declared
    def gettype(input):
        if input.startswith('int'):
            return int
        #elif input.endswith('timestamp'): return datetime
        return str

    start = time.time()
    curr = conn.cursor()

    def grab_table(table_name):
        "Return table as a dictionary, index by Primary Key, or ascending"
        curr = conn.cursor()
        curr.execute("SHOW fields in {}".format(table_name))
        fields = tuple(curr)
        field_names = tuple(f[0] for f in fields)
        field_types = tuple(gettype(f[1]) for f in fields)
        TableRow = namedtuple(table_name, field_names)
        curr = conn.cursor(buffered = True, raw = True)

        curr.execute("SELECT * FROM {}".format(table_name))
        try:
            key = next(i for i,f in enumerate(fields) if 'PRI' in f)
            for db_row in curr.fetchall():
                row = TableRow._make(conform(a, field_types[i]) for i, a in enumerate(db_row))
                yield(row[key], row)
        except StopIteration: #Meaning: Empty Iterator - No 'PRI' found.
            for key, row in enumerate(curr.fetchall()):
                yield (key, Table._make(conform(a, field_types[i]) for i, a in enumerate(row)))

    def grab_tables(tables):
        for table in tables:
            items = list(grab_table(table))
            keys = [i[0] for i in items]
            if len(keys) == len(set(keys)):
                yield dict(items)
            else:
                yield [i[1] for i in items]

    curr.execute("SHOW tables")
    table_names = tuple(t[0] for t in curr.fetchall())
    database = namedtuple('Database', table_names)(*tuple(grab_tables(table_names)));
    return database

def db_modified(conn):
    """ Return the timestamp of the last modification.

    This is a fast function, it only takes a few milliseconds"""

    curr = conn.cursor(raw=True)
    curr.execute('SHOW table status')
    return sorted((a[11] for a in curr.fetchall()), key=lambda m: tuple(int(a) for a in regex.findall(rb'\d+', m)), reverse=True)[0].decode()

class _DBR:
    errors = []
    warnings = []
    
    def __init__(self, db, timestamp):
        
        self.build_suttas(db)
        self.build_references(db)
        self.build_parallels(db)
        self.build_search_data()
        self.build_file_data()
        self.timestamp = timestamp
    
    def __call__(self, uid):
        if uid in self.collections:
            return self.collections[uid]
        elif uid in self.divisions:
            return self.divisions[uid]
        elif uid in self.subdivisions:
            return self.subdivisions[uid]
        elif uid in self.suttas:
            return self.suttas[uid]
    
    def build_suttas(self, db):
        """ Build the sutta central database representation

        This starts from the highest level (i.e. collection) and works to
        the lowest level (i.e. parallels - the relationship between suttas)
        Since it is fully navigitable both up and down this means some
        elements can't be populated initially. This means that suttas
        insert themselves into the subdivision where they belong.

        Some attribute names undergo transformation (DRY). For example:
        sutta.sutta_uid -> sutta.uid

        Some attributes are transformed from a name into an object
        correspondence.sutta_uid -> parallel.sutta.uid
        
        Some tables are indexed as dicts, with the key being id or uid.
        These include:
        collection, division, subdivision, vagga, sutta
        
        When classes are contained within a class, for example, suttas in
        a subdivision, this is always represented by a list. That list will
        be sorted appropriately and can be directly outputted, generally
        without any need for filtering or sorting.

        When an attribute is a list or dict, the name always end in an 's'
        for example:
        dbr.suttas['sn1.1'].subdivision.division.subdivisions[0].suttas[0]

        lists always use zero-based indexing, while dicts are generally
        based on the table data, generally starting at 1. This inconsitency
        is not a problem since for lists only the ordering is meaningful,
        they are intended to be printed out as a whole unit using "for in"

        Some things, such as parallels, are not indexed at all, and are
        only accessable as attributes of the relevant suttas.

        """

        # Build Languages (indexed by id)
        self.collection_languages = OrderedDict()
        for row in db.collection_language.values():
            self.collection_languages[row.collection_language_id] = Language(
                id=row.collection_language_id,
                name=row.collection_language_name,
                abbrev=row.collection_language_abbrev_name,
                code=row.language_code)

        self.reference_languages = OrderedDict()
        for row in db.reference_language.values():
            self.reference_languages[row.reference_language_id] = Language(
                id=row.reference_language_id,
                name=row.reference_language_name,
                abbrev=None,
                code=row.iso_code_2)

        self.lang_codes = frozenset(
            [l.code for l in self.collection_languages.values()] +
            [l.code for l in self.reference_languages.values()])

        #Build Collections (indexed by id)
        self.collections = OrderedDict()
        for row in db.collection.values():
            self.collections[row.collection_id] = Collection(
                id=row.collection_id,
                name=row.collection_name,
                abbrev_name=row.collection_abbrev_name,
                lang=self.collection_languages[row.collection_language_id],
                note_text=row.note_text,
                divisions=[] # Populate later
                )
        
        # Build divisions (indexed by uid)
        self.divisions = OrderedDict()
        for row in db.division.values():
            division = Division(
                id=row.division_id,
                uid=row.division_uid,
                name=row.division_name,
                coded_name=row.division_coded_name,
                plain_name=row.division_plain_name,
                acronym=row.division_acronym,
                subdiv_ind=row.subdiv_ind,
                note_text=row.note_text,
                collection=self.collections[row.collection_id],
                subdivisions=[], # Populate later
            )
            self.divisions[row.division_uid] = division
            # Populate collections.divisions
            self.collections[row.collection_id].divisions.append(division)

        # Build divisions (indexed by uid)
        self.subdivisions = OrderedDict()
        for row in db.subdivision.values():
            subdivision = Subdivision(
                id=row.subdivision_id,
                uid=row.subdivision_uid,
                name=row.subdivision_name,
                coded_name=row.subdivision_coded_name,
                plain_name=row.subdivision_plain_name,
                acronym=row.subdivision_acronym,
                vagga_numbering_ind=(row.vagga_numbering_ind=='Y'),
                division=self.divisions[db.division[row.division_id].division_uid],
                suttas=[], # Populate later
            )
            self.subdivisions[row.subdivision_uid] = subdivision
            # populate divisions.subdivisions
            self.divisions[db.division[row.division_id].division_uid].subdivisions.append(subdivision)

        # Build vaggas (indexed by id)
        self.vaggas = OrderedDict()
        for row in db.vagga.values():
            self.vaggas[row.vagga_id] = Vagga(
                id=row.vagga_id,
                subdivision=self.subdivisions[db.subdivision[row.subdivision_id].subdivision_uid],
                name=row.vagga_name,
                coded_name=row.vagga_coded_name,
                plain_name=row.vagga_plain_name,
            )
            # At present vaggas are not 'owned' by subdivisions and do not
            #'own' suttas. This is because the database data is incorrect.
        
        # Build suttas (indexed by uid)
        # Note that we re-sort rather than keeping database order. This is
        # because some suttas are improperly ordered.
        suttas = []
        for sutta in db.sutta.values():
            sutta_uid = sutta.sutta_uid
            subdivision = db.subdivision[sutta.subdivision_id]
            division_id = db.division[subdivision.division_id].division_id
            subdivision_uid = subdivision.subdivision_uid
            try:
                biblio_entry = BiblioEntry(
                    name=db.biblio_entry[sutta.biblio_entry_id].biblio_entry_name,
                    text=db.biblio_entry[sutta.biblio_entry_id].biblio_entry_text,)
            except KeyError:
                if sutta.biblio_entry_id > 0:
                    logger.error('Database: Invalid biblio id {} for sutta {}'.format(sutta.biblio_entry_id, sutta_uid))
                biblio_entry = None
            try:
                vagga = self.vaggas[sutta.vagga_id]
            except KeyError:
                if sutta.vagga_id > 0:
                    logger.error('Invalid vagga id {} for sutta {}'.format(sutta.vagga_id, sutta_uid))
                vagga = None
            try:
                lang = self.collection_languages[sutta.collection_language_id]
            except KeyError:
                logger.error('Invalid language id {} for sutta {}'.format(sutta.collection_language_id, sutta_uid))
                lang = Language(-1, 'Unknown', 'Unknown', 'Unknown')
            try:
                new_sutta = Sutta(
                    id=sutta.sutta_id,
                    uid=sutta_uid,
                    acronym=sutta.sutta_acronym,
                    alt_acronym=sutta.alt_sutta_acronym,
                    name=sutta.sutta_name,
                    coded_name=sutta.sutta_coded_name,
                    plain_name=sutta.sutta_plain_name,
                    number=sutta.sutta_number,
                    lang=lang,
                    subdivision=self.subdivisions[subdivision_uid],
                    vagga=vagga,
                    number_in_vagga=sutta.sutta_in_vagga_number,
                    volpage_info=sutta.volpage_info,
                    alt_volpage_info=sutta.alt_volpage_info,
                    biblio_entry=biblio_entry,
                    url=sutta.sutta_text_url_link,
                    url_info=sutta.url_extra_info_text,
                    translations=[],
                    parallels=[],
                )
                suttas.append( (sutta_uid, new_sutta) )
            except:
                print("Sutta: " + str(sutta))
                raise

        suttas = sorted(suttas, key=numsort)
        suttas = sorted(suttas, key=lambda t: t[1].subdivision.division.id)
        
        self.suttas = OrderedDict(suttas)
        # Populate subdivisions.suttas
        for sutta in self.suttas.values():
            sutta.subdivision.suttas.append(sutta)

    def build_references(self, db):
        for key, row in db.reference.items():
            try:
                uid = db.sutta[row.sutta_id].sutta_uid
            except KeyError:
                self.errors.append('{} missing in sutta ({})'.format(
                    row.sutta_id, key))
            lang = (self.reference_languages[                                    row.reference_language_id])
            seq_nbr = row.reference_seq_nbr
            url = row.reference_url_link
            abstract = row.abstract_text
            translation = Translation(seq_nbr, lang, url, abstract)
            self.suttas[uid].translations.append(translation)
        for sutta in self.suttas.values():
            sutta.translations.sort(key=lambda t: (t.lang.id, t.seq_nbr))

    def build_parallels(self, db):
        db = db
        fulls = defaultdict(set)
        partials = defaultdict(set)
        indirects = defaultdict(set)
        # initially we operate purely on ids using id, footnote tuples

        #Populate partial and full parallels
        for row in db.correspondence:
            if row.partial_corresp_ind == 'Y':
                partials[row.entry_id].add( (row.corresp_entry_id, row.footnote_text) )
                partials[row.corresp_entry_id].add( (row.entry_id, row.footnote_text) )
            else:
                fulls[row.entry_id].add( (row.corresp_entry_id, row.footnote_text) )
                fulls[row.corresp_entry_id].add( (row.entry_id, row.footnote_text) )

        # Populate indirect full parallels
        for id, parallels in fulls.items():
            for pid, footnote in parallels:
                if pid in fulls:
                    indirects[id].update(fulls[pid])

        for id, parallels in indirects.items():
            
            # Remove self and fulls
            indirects[id] -= set(a for a in indirects[id] if a[0] == id)
            #indirects[id] -= fulls[id]

        def test():
            class CaseSutta:
                def __init__(self, id, fulls, partials):
                    self.id = id
                    self.fulls = fulls
                    self.partials = partials

            case_suttas = (
                CaseSutta(id=16,
                        fulls={4155, 4187, 4188, 4189, 6036, 6099, 6100, 6105,
                            6106, 6156, 6205, 6283, 6289, 6291, 6297, 6301, 6312},
                        partials={2770, 3327, 3432, 4051, 6381, 6382,
                                6385, 6386, 6387, 8553, 8577, 8578, 2325}),
                CaseSutta(id=4218,
                        fulls={36, 3940, 4436, 5932, 6071},
                        partials=set()),
                )
            for case_sutta in case_suttas:
                id = case_sutta.id
                full_ids = set(a[0] for a in fulls[id].union(indirects[id]))
                part_ids = set(a[0] for a in partials[id])
            
                if full_ids == case_sutta.fulls and part_ids == case_sutta.partials:
                    logger.info("Parallels generation for id = {} passes test.".format(case_sutta.id))
                else:
                    logger.warning("Parallel generation anonomly id = {}:\n    missing: {}\n    extras: {}".format(
                        case_sutta.id,
                        (case_sutta.fulls - full_ids,
                         case_sutta.partials - part_ids),
                        (full_ids - case_sutta.fulls,
                         part_ids - case_sutta.partials)))
        test()
        
        for sutta_id, parallels in fulls.items():
            sutta = self.suttas[db.sutta[sutta_id].sutta_uid]
            for pid, note in parallels:
                psutta = self.suttas[db.sutta[pid].sutta_uid]
                sutta.parallels.append(Parallel(psutta, False, False, note))
                
        for sutta_id, parallels in indirects.items():
            sutta = self.suttas[db.sutta[sutta_id].sutta_uid]
            for pid, note in parallels:
                psutta = self.suttas[db.sutta[pid].sutta_uid]
                sutta.parallels.append(Parallel(psutta, False, True, note))

        for sutta_id, parallels in partials.items():
            sutta = self.suttas[db.sutta[sutta_id].sutta_uid]
            for pid, note in parallels:
                psutta = self.suttas[db.sutta[pid].sutta_uid]
                sutta.parallels.append(Parallel(psutta, True, False, note))

        def parallel_sort_key(p):
            # To do multisort in python, return a tuple, tuples are ordered
            # in the sanest way imaginable.
            return (p.partial, p.sutta.subdivision.id, numsort(p.sutta.uid))
        
        for sutta in self.suttas.values():
            sutta.parallels.sort(key=parallel_sort_key)

    def build_search_data(self):
        """ Build useful search data.

        Note that the size of the data is somewhat less than 2mb """

        suttastringsU = (["  {}  ".format("  ".join(
                                [sutta.uid,
                                sutta.lang.code,
                                sutta.acronym,
                                sutta.alt_acronym or '',
                                sutta.name,
                                sutta.coded_name,
                                sutta.plain_name,
                                sutta.volpage_info,
                                sutta.alt_volpage_info or '',
                                ", ".join( t.lang.code
                                    for t in sutta.translations,) or '',]))
                            for sutta in self.suttas.values()])
        suttastrings = [s.lower() for s in suttastringsU]
        # Only simplify the name.
        suttanamesimplified = (["  {}  ".format(
            textfunctions.simplify(sutta.name, sutta.lang.code))
            for sutta in self.suttas.values()])

        self.searchstrings = list(zip(self.suttas.values(), suttastrings, suttastringsU, suttanamesimplified))
        
    def build_file_data(self):
        self.static_pages = []
        return
        self.static_pages = ([a[:-5] for a in os.listdir(setup.static_root)
                                if a.endswith('.html')])

    def deep_md5(self, ids=False):
        """ Calculate a md5 for the data. Takes ~0.5s on a fast cpu.

        This will detect most inconsistencies in the contents of strings,
        ints, tuples, dicts and so on. As is always the case, carefully
        crafted different inputs could produce identical md5s, but this
        is highly unlikely to occur by chance.

        If ids is True, it additionally generates a md5 checksum on the
        id of every object encountered. The return value will be a tuple,
        (data_md5, id_md5). The data_md5 should be identical across
        different invocations of the program but the id_md5 will change.
        The id_md5 can detect some corruptions which the data_md5 won't,
        particularly when circular references are involved. For example
        data_md5 might not notice when the order of a list of parallels
        changes (if it has already seen each invidivudal parallel before),
        but id_md5 certainly will. On the other hand, at least in principle
        a change to an objects id need not invalidate the data - altough
        such things should not need to happen.
        
        """
        stack = []
        #md5 = hashlib.md5()
        #for b in atomicfy(self.collections, stack=stack):
            #md5.update(b)
        md5 = hashlib.md5(b"".join(atomicfy(self.collections, stack=stack)))
        if ids:
            md5ids = hashlib.md5(b"".join([str(id(a)).encode() for a in stack]))
            return (md5.hexdigest(), md5ids.hexdigest())
        return md5.hexdigest()

    def check_md5(self, exception=None):
        new_md5 = self.deep_md5(ids=True)
        if not hasattr(self, 'dbr_md5'):
            self.dbr_md5 = new_md5
            logger.info('Generating md5 {}.'.format(new_md5))
        else:
            if self.dbr_md5 == new_md5:
                logger.info('md5s match')
            else:
                logger.error('md5 mismatch')
                if exception:
                    raise exception

def atomicfy(start, stack=None):
    """ Slice a unit into 'atomic' units (strs, bytes and ints)

    The individuals 'atoms' are yielded as bytes objects, suitable for
    consumption by a hashlib md5, sha or other function.

    If called with the stack attribute, stack must be a list. After the
    function as run, it will be populated with every object the function
    has seen. This has two purposes, first a stack of starting points
    can be entered, secondly you can perform further manupulations on the
    contents of the passed in stack.

    """

    if stack is None:
        stack = [start]
    elif start is not None and start not in stack:
        stack.append(start)
    touched = set()

    # Iterating over an object which is getting longer is fine in python.
    for obj in stack:
        oid = id(obj)
        try:
            if oid in touched:
                continue
            touched.add(oid)
        except TypeError:
            touched = set([oid])

        try:
            length = len(obj)
            # Object has length
            if length == 0:
                #For empty container, yield the type
                yield b't' + str(type(obj)).encode()
                continue
            
            try:
                yield obj.encode() # String?
                continue
            except AttributeError:
                try:
                    yield b'b' + obj # Bytes or btye-like?
                    continue
                except TypeError:
                    pass
            
            # Yield the length as an additional check
            yield b'l' + str(length).encode()
            
            try:
                for pair in obj.items(): # Dict-like?
                    stack.extend(pair)
                continue
            except AttributeError:
                pass

            try:
                stack.extend(obj) # List-like?
                continue
            except AttributeError:
                pass

        except TypeError:
            # Atomic (length-less) object.
            pass

        try:
            test = int(obj)
            yield b'n' + str(obj).encode()
            #intobj = abs(int(obj))
            #yield 'n' + intobj.tobytes(math.ceil(math.log(intobj+1, 2) / 8), 'big')
            continue
        except TypeError:
            pass

        # Yield the type. Useful for user classes.
        yield b't' + str(type(obj)).encode()

def _buildDBR(timestamp):
    global _dbr
    # Note: It is vitally important the timestamp of the build is set
    # from the very start of the process, so if the database changes
    # while the build is happening, we will know to re-build.
    start=time.time()
    con = mysql.connect(**setup.mysql_settings)
    db = db_grab(con)
    bstart=time.time()
    _dbr = _DBR(db, timestamp)
    logger.info('Built DBR. Grab took {} seconds. Build took {} seconds'.format(bstart-start, time.time()-bstart))

def getDBR():
    """ Get an instance of the DBR.

    Use only this function to get an instance of the DBR. For most intents
    and purposes the DBR should be considered a singleton. However it can
    be regenerated, and while being regenerated, a 'stale' copy can be be
    served, hence multiple versions can exist for a short time. (The stale
    copies will be garbage collected when they fall out of scope)
    
    This function is cheap to call, but not quite free (~210 times per
    second on this laptop). It is also not guaranteed to always return the
    *same* instance of the dbr, so prefer to use it to get a reference,
    then use the reference.

    """
    
    con = mysql.connect(**setup.mysql_settings)
    timestamp = db_modified(con)
    con.close()

    try:
        if _dbr.timestamp == timestamp:
            dbr = _dbr
    except (NameError, AttributeError, ValueError):
        buildthreads = [t for t in threading.enumerate() if t.name == 'buildDBR' and t.is_alive()]
        if len(buildthreads) == 0:
            buildthread = threading.Thread(
                target=_buildDBR, name="buildDBR", args=(timestamp, ))
            buildthread.start()
        else:
            buildthread = buildthreads[0]
        try:
            dbr = _dbr # Return stale copy if we can.
        except (NameError, AttributeError):
            buildthread.join(timeout=30) # Wait if we can't.
            dbr = _dbr
    if setup.RUNTIME_TESTS:
        checkDBR()
    return dbr

def checkDBR():
    """ Checks if the DBR has been modified by user code.

    Only meaningful when called multiple times. Threaded to make non-
    blocking and ensure only ever one check happens at one time. Writes
    messages to log.
    
    """
    
    def check_dbr_helper():
        getDBR().check_md5()
    check_threads = [t for t in threading.enumerate() if t.name == 'checkDBR' and t.is_alive()]
    if len(check_threads) == 0:
        threading.Thread(target=check_dbr_helper, name="checkDBR").start()

checkDBR()