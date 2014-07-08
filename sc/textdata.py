import time
import regex
import pickle
import pathlib
import sqlite3
import threading
from itertools import chain

import sc
from sc.tools import html
import logging
logger = logging.getLogger(__name__)

""" A tool responsible for collating information from the texts

"""

def text_dir_md5(extra_files=[__file__]):
    """ Generates an md5 hash based on text modification times

    This can be used to detect if the database is up to date.

    By default uses all directories (not files) in the text_dir,
    plus this module file since changes to this module are quite
    likely to result in a different final database.

    """
    files = chain(sc.text_dir.glob('**/*.html'), (pathlib.Path(f) for f in extra_files))
    mtimes = (file.stat().st_mtime_ns for file in files)
    
    from hashlib import md5
    from array import array
    
    return md5(array('Q', mtimes)).hexdigest()

class TextInfo:
    __slots__ = ('uid', 'lang', 'path', 'bookmark', 'name', 'author', 'volpage', 'prev_uid', 'next_uid')
    def __init__(self, **kwargs):
        for key in self.__slots__:
            setattr(self, key, kwargs.get(key, None))
    def __repr__(self):
        return 'TextInfo({})'.format(', '.join('{}={}'.format(attr, getattr(self, attr)) for attr in self.__slots__))

    @property
    def url(self):
        out = '/{}/{}'.format(self.uid, self.lang)
        if self.bookmark:
            out = out + '#{}'.format(self.bookmark)
        return out

class TextInfoModel:
    """ The TextInfoModel is responsible for scanning the entire contents
    of the text folders and building a model containing information not
    easily gleaned at a glance of the filesystem, which is required for
    purposes other than delivering the HTML of the text itself.

    It is required to delve quite deeply into the structure of the documents
    to discover all that is needed to be known, hence the scanning is
    quite time-consuming.

    This is the python-dict based TIM, it generates a structure
    consisting entirely of python dicts which can be pickled.

    """
    FILES_N = 200
    def __init__(self):
        self._by_lang = {}
        self._by_uid = {}
    
    def get(self, uid=None, lang_uid=None):
        """ Returns TextInfo entries which match arguments

        If both uid and lang_uid are defined, a single entry is returned
        if uid is set a dictionary of entries keyed by lang_uid is returned
        if lang_uid is set a dict of entries keyed by uid is returned
        if neither is set a ValueError is raised

        This method returns None or an empty dict if there are no matching entries.
        """
        
        try:
            if uid and lang_uid:
                try:
                    return self._by_uid[uid][lang_uid]
                except KeyError:
                    return None
            elif uid:
                return self._by_uid.get(uid, {})
            elif lang_uid:
                return self._by_lang.get(lang_uid, {})
            else:
                raise ValueError('At least one of uid or lang_uid must be set')
        except KeyError:
            return None

    def exists(self, uid, lang_uid):
        try:
            self._by_uid[uid][lang_uid]
            return True
        except KeyError:
            return False

    def add_text_info(self, lang_uid, uid, textinfo):
        if lang_uid not in self._by_lang:
            self._by_lang[lang_uid] = {}
        self._by_lang[lang_uid][uid] = textinfo
        if uid not in self._by_uid:
            self._by_uid[uid] = {}
        self._by_uid[uid][lang_uid] = textinfo

    def get_palipagenumbinator(self):
        if not self._ppn:
            self._ppn = PaliPageNumbinator()
        return self._ppn

    @staticmethod
    def uids_are_related(uid1, uid2, _rex=regex.compile(r'\p{alpha}*(?:-\d+)?')):
        # We will perform a simple uid comparison
        # We could be more sophisticated! For example we could
        # inspect whether they belong to the same division
        if uid1 is None or uid2 is None:
            return False
        
        m1 = _rex.match(uid1)[0]
        m2 = _rex.match(uid2)[0]
        if m1 and m2 and m1 == m2:
            return True
    
    def build(self, force=False):
        # The pagenumbinator should be scoped because it uses
        # a large chunk of memory which should be gc'd.
        # But it shouldn't be created at all if we don't need it.
        # So we use a getter, and delete it when we are done.
        self._ppn = None
        file_i = 0
        for lang_dir in sc.text_dir.glob('*'):
            lang_uid = lang_dir.stem
            files = sorted(lang_dir.glob('**/*.html'), key=lambda f: sc.util.numericsortkey(f.stem))
            for i, htmlfile in enumerate(files):
             try:
                if not self._should_process_file(htmlfile, force):
                    continue
                logger.info('Adding file: {!s}'.format(htmlfile))
                uid = htmlfile.stem
                root = html.parse(str(htmlfile)).getroot()

                # Set the previous and next uids, using explicit data
                # if available, otherwise making a safe guess.
                # The safe guess relies on comparing uids, and will not
                # capture relationships such as the order of patimokha
                # rules.
                prev_uid = root.get('data-prev')
                next_uid = root.get('data-next')
                if not (prev_uid or next_uid):
                    if i > 0:
                        prev_uid = files[i - 1].stem
                        if not self.uids_are_related(uid, prev_uid):
                            prev_uid = None
                    if i + 1 < len(files):
                        next_uid = files[i + 1].stem
                        if not self.uids_are_related(uid, next_uid):
                            next_uid = None
                
                path = htmlfile.relative_to(sc.text_dir)
                author = self._get_author(root, lang_uid, uid)
                name = self._get_name(root, lang_uid, uid)
                volpage = self._get_volpage(root, lang_uid, uid)
                embedded = self._get_embedded_uids(root, lang_uid, uid)

                textinfo = TextInfo(uid=uid, lang=lang_uid, path=path, name=name, author=author, volpage=volpage, prev_uid=prev_uid, next_uid=next_uid)
                self.add_text_info(lang_uid, uid, textinfo)

                for child in embedded:
                    child.path = path
                    child.author = author
                    self.add_text_info(lang_uid, child.uid, child)

                m = regex.match(r'(.*?)(\d+)-(\d+)$', uid)
                if m:
                    range_textinfo = TextInfo(uid=uid+'#', lang=lang_uid, path=path, name=name, author=author, volpage=volpage)
                    start = int(m[2])
                    end = int(m[3]) + 1
                    for i in (range(start, end) if end - start < 20 else [0]):
                        iuid = m[1] + str(i)
                        if self.exists(iuid, lang_uid):
                            continue

                        self.add_text_info(lang_uid, iuid, range_textinfo)
                file_i += 1
                if (file_i % self.FILES_N) == 0:
                    self._on_n_files()
             except Exception as e:
                 print('An exception occured: {!s}'.format(htmlfile))
                 raise
        if (file_i % self.FILES_N) != 0:
            self._on_n_files()
        
        del self._ppn

    def _on_n_files(self):
        return
    def _should_process_file(self, file, force):
        return True
    
    # Class Variables
    _build_lock = threading.Lock()
    _build_ready = threading.Event()
    _instance = None
    
    def _get_author(self, root, lang_uid, uid):
        try:
            e = root.select_one('meta[author]')
            if e:
                return e.attrib['author']
            else:
                e = root.select_one('meta[data-author]')
                return e.attrib['data-author']
        except Exception as e:
            logger.warn('Could not determine author for {}/{}'.format(lang_uid, uid))
            return ''
    
    def _get_name(self, root, lang_uid, uid):
        try:
            hgroup = root.select_one('.hgroup')
            h1 = hgroup.select_one('h1')
            return h1.text_content()
        except Exception as e:
            logger.warn('Could not determine name for {}/{}'.format(lang_uid, uid))
            return ''
    
    def _get_volpage(self, element, lang_uid, uid):
        if lang_uid == 'zh':
            e = element.next_in_order()
            while e is not None:
                if e.tag =='a' and e.select_one('.t, .t-linehead'):
                    break
                e = e.next_in_order()
            else:
                return
            return 'T {}'.format(e.attrib['id'])
        elif lang_uid == 'pi':
            ppn = self.get_palipagenumbinator()
            e = element.next_in_order()
            while e:
                if e.tag == 'a' and e.select_one('.ms'):
                    return ppn.get_pts_ref_from_pid(e.attrib['id'])
                e = e.next_in_order()

        return None
    
    def _get_embedded_uids(self, root, lang_uid, uid):
        # Generates possible uids that might be contained
        # within this text.
        out = []
        
        if '-pm' in uid:
            # This is a patimokkha text
            for h4 in root.select('h4'):
                a = h4.select_one('a[id]')
                if not a:
                    continue
                
                volpage = self._get_volpage(h4, lang_uid, uid)
                out.append(TextInfo(
                    uid='{}#{}'.format(uid, a.attrib['id']),
                    bookmark=a.attrib['id'],
                    name=None,
                    volpage=volpage))

        data_uid_seen = set()
        for e in root.select('[data-uid]'):
            if e.tag in {'h1','h2','h3','h4','h5','h6'}:
                heading = e.text_content()
                add = e.select_one('.add')
                if add and add.text_content() == heading:
                    heading = '[' + heading + ']'
            else:
                heading = None
            out.append(TextInfo(uid=e.get('data-uid'), name=heading, bookmark=e.get('id')))
            data_uid_seen.add(e)
        
        for e in root.select('.embeddedparallel'):
            if 'data-uid' in e.attrib:
                if e in data_uid_seen:
                    continue
                # Explicit
                new_uid = e.attrib['data-uid']
            else:
                # Implicit
                new_uid = '{}#{}'.format(uid, e.attrib['id'])
            out.append(TextInfo(
                uid=new_uid,
                bookmark = e.attrib['id']))

        sections = root.select('section.sutta')
        if len(sections) > 1:
            for section in sections:
                data_uid = section.attrib.get('data-uid')
                id = section.attrib.get('id')
                if data_uid:
                    out.append(TextInfo(
                        uid=data_uid,
                        bookmark=id))
        return out

    @classmethod
    def build_once(cls, force_build):
        if cls._build_lock.acquire(blocking=False):
            try:
                tim_base_filename = 'text_info_model_'
                textmd5 = text_dir_md5()
                timfile = sc.db_dir / (tim_base_filename + textmd5 + '.pickle')
                if not force_build and timfile.exists():
                    with timfile.open('rb') as f:
                        newtim = pickle.load(f)
                else:
                    newtim = TextInfoModel()
                    newtim.build()
                    for file in sc.db_dir.glob(tim_base_filename + '*'):
                        file.unlink()

                    with timfile.open('wb') as f:
                        pickle.dump(newtim, f)

                TextInfoModel._instance = newtim
                TextInfoModel._build_ready.set()
            finally:
                TextInfoModel._build_lock.release()

class SqliteBackedTIM(TextInfoModel):
    """ A memory-saving version of the TIM

    Sqlite is generally very, very fast and this is not noticably
    slower than the python dict based TextInfoModel, not more than
    5% slower to build, and while requests are about
    20x slower it's still about 30,000 'gets' per second, and the SQL
    overhead accounts for no more than 20% of the total process time
    for building a division view. (April 2014)
    
    """
    def __init__(self, filename):
        self._filename = filename
        self._local = threading.local()

    @property
    def _con(self):
        try:
            return self._local.con
        except AttributeError:
            self.reconnect()
            return self._local.con

    def reconnect(self):
        self._local.con = sqlite3.connect(self._filename)

    def _init_table(self):
        try:
            pathlib.Path(self._filename).unlink()
        except FileNotFoundError:
            pass
        self.reconnect()
        self._con.execute('CREATE TABLE data(lang, uid, path, bookmark, name, author, volpage, prev_uid, next_uid)')
        self._con.execute('CREATE TABLE mtimes(path UNIQUE, mtime)')
        # Presently we build the whole lot in one go and disabling
        # journaling dramatically improves bulk insert performance.
        self._con.execute('PRAGMA journal_mode = OFF')

    def _finally_table(self):
        self._con.execute('CREATE INDEX lang_x ON data(lang)')
        self._con.execute('CREATE INDEX uid_x ON data(uid)')
        self._con.execute('CREATE INDEX path_x ON data(path)')
        self._con.execute('CREATE INDEX mtimes_path_x on mtimes(path)')
        self._con.execute('PRAGMA journal_mode = wal')
        
    def build(self, force=False):
        happy = self.is_happy()
        if happy:
            self._mtimes = {path:mtime for path, mtime in self._con.execute('SELECT * FROM mtimes')}
            self._check_for_deleted()
        else:
            self._init_table()
            self.set_happy()
            self._mtimes = {}
        super().build(force)
        if not happy:
            self._finally_table()
            
        self._con.commit()
        del self._mtimes

    def _check_for_deleted(self):
        sc_dir = str(sc.text_dir) + '/'
        existing = {str(file).replace(sc_dir, '') for file in sc.text_dir.glob('**/*.html')}
        for path in self._mtimes.keys():
            if path not in existing:
                logger.info('File removed: {!s}.'.format(path))
                self._delete_entries(pathlib.Path(path))
        
    def _should_process_file(self, file, force):
        
        mtime = file.stat().st_mtime_ns
        path = file.relative_to(sc.text_dir)
        
        if not force and self._mtimes.get(str(path)) == mtime:
            return False

        self._delete_entries(path)
        self._con.execute('INSERT INTO mtimes VALUES(?, ?)', (str(path), mtime))
        return True

    def _delete_entries(self, path):
        con = self._con
        con.execute('DELETE FROM data WHERE path=?', (str(path),))
        con.execute('DELETE FROM mtimes WHERE path=?', (str(path),))

    def _on_n_files(self):
        self._con.commit()
    
    def set_happy(self):
        self._con.execute('CREATE TABLE happy(yes)')

    def is_happy(self):
        try:
            self._con.execute('SELECT 1 FROM happy')
            return True
        except:
            return False
    
    def get(self, uid=None, lang_uid=None):
        con = self._con
        
        def text_info_from_row(row):
            return TextInfo(lang = row[0], uid=row[1],
                            path=pathlib.Path(row[2]), bookmark=row[3],
                            name=row[4], author=row[5], volpage=row[6], prev_uid=row[7], next_uid=row[8])
        
        if uid and lang_uid:
            cur = con.execute('''SELECT lang, uid, path, bookmark, name, author, volpage, prev_uid, next_uid
                                FROM data
                                WHERE lang=?
                                AND uid=?''',
                                (lang_uid, uid))
            result = cur.fetchone()
            if not result:
                return None
            return text_info_from_row(result)
        else:
            sql_fmtstr = '''SELECT lang, uid, path, bookmark, name, author, volpage, prev_uid, next_uid
                                FROM data
                                WHERE {field}=?'''
            if uid:
                cur = con.execute(sql_fmtstr.format(field='uid'), (uid,))
                return {row[0]: text_info_from_row(row) for row in cur}
            elif lang_uid:
                cur = con.execute(sql_fmtstr.format(field='lang'), (lang_uid,))
                return {row[1]: text_info_from_row(row) for row in cur}
            else:
                raise ValueError('At least one of uid or lang_uid must be set')

    def exists(self, uid, lang_uid):
        cur = self._con.execute('SELECT 1 FROM data WHERE lang=? and uid=?',
                        (lang_uid, uid))
        return cur.fetchone() != None

    def add_text_info(self, lang_uid, uid, textinfo):
        self._con.execute('INSERT INTO data VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (lang_uid, uid, str(textinfo.path), textinfo.bookmark,
            textinfo.name, textinfo.author, textinfo.volpage, textinfo.prev_uid, textinfo.next_uid))

    filename = str(sc.db_dir / 'text_info_model.db')
    
    @classmethod
    def build_once(cls, force_build):
        if cls._build_lock.acquire(blocking=False):
            try:
                start=time.time()
                logger.info('Acquiring SQLite Backed Text Info Model')
                cls._instance = cls(cls.filename)
                cls._instance.build(force_build)
                cls._build_ready.set()
                build_time = time.time()-start
                logger.info('Text Info Model ready in {:.4f}s'.format(build_time))
            finally:
                cls._build_lock.release()

    @classmethod
    def parallel_rebuild(cls):
        """ Rebuild the Model from stratch

        Leaves the existing database intact so that the server can
        continue to use it while the build is in progress. Once the build
        is finished, the database file is overwitten, existing connections
        will continue to use the old (now unlinked) database, the server
        will need to be restarted to re-create the connections.

        This method is useful because a complete rebuild can take upwards
        of 10 minutes, hence it is better that such a task be delegated
        to a background thread or process.

        """
        
        import os
        logger.info('Rebuilding SQLite Backed Text Info Model in background')
        timfile = cls.filename + '.working'
        tim = cls(timfile)
        tim.build()
        logger.info('Rebuild complete')
        os.replace(timfile, cls.filename)
        return True
        
        
        

def tim(force_build=False, Model=SqliteBackedTIM):
    """ Returns an instance of the TIM

    When this is called for the first time, it will check if the cached
    TIM is up to date. If it is, the cached copy will be loaded and
    returned. If it's not, it will rebuild.

    The TIM can take some time to build, perhaps a couple of minutes.
    For this reason, it's a reasonable idea to load it in a seperate
    process before restarting the server, thus ensuring it is fresh.

    i.e.
    import sc.textdata
    sc.textdata.tim()
    
     """

    if not force_build and Model._build_ready.set():
        return Model._instance
    Model.build_once(force_build)
    Model._build_ready.wait()
    return Model._instance

def rebuild_tim(Model=SqliteBackedTIM):
    Model.parallel_rebuild()

class PaliPageNumbinator:
    msbook_to_ptsbook_mapping = {
        'a': 'AN',
        'ap': 'Ap',
        'bu': 'Bv',
        'cn': 'Cnd',
        'cp': 'Cp',
        'd': 'DN',
        'dh': 'Dhp',
        'dhs': 'Ds',
        'dht': 'Dt',
        'it': 'It',
        'j': 'Ja',
        'kh': 'Kp',
        'kv': 'Kv',
        'm': 'MN',
        'mi': 'Mil',
        'mn': 'Mnd',
        'ne': 'Ne',
        'p': 'Pt',
        'pe': 'Pe',
        'ps': 'Ps',
        'pu': 'Pp',
        'pv': 'Pv',
        's': 'SN',
        'sn': 'Snp',
        'th1': 'Thag',
        'th2': 'Thig',
        'ud': 'Ud',
        'v': 'Vin',
        'vbh': 'Vb',
        'vv': 'Vv',
        'y': 'Ya'}

    default_attempts = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9,-10,-11,-12,-13,-14,-15,1,2,3,4,5]
    def __init__(self):
        self.load()

    def load(self):
        from sc.scimm import table_reader

        reader = table_reader('pali_concord')

        mapping = {(msbook, int(msnum), edition): (book, page)
                for msbook, msnum, edition, book, page in reader}
        self.mapping = mapping

    def msbook_to_ptsbook(self, msbook):
        m = regex.match(r'\d+([A-Za-z]+(?:(?<=th)[12])?)', msbook)
        return self.msbook_to_ptsbook_mapping[m[1]]

    def get_pts_ref_from_pid(self, pid):
        m = regex.match(r'p_(\w+)_(\d+)', pid)

        msbook = m[1].lower()
        msnum = int(m[2])
        return self.get_pts_ref(msbook, msnum)
        
        
    def get_pts_ref(self, msbook, msnum, attempts=None):
        if not attempts:
            attempts = self.default_attempts
        for i in attempts:
            n = msnum + i
            if n < 1:
                continue
            key1 = (msbook, n, 'pts1')
            key2 = (msbook, n, 'pts2')
            key = None
            if key1 in self.mapping:
                key = key1
            elif key2 in self.mapping:
                key = key2
            if key:
                book, num = self.mapping[key]
                ptsbook = self.msbook_to_ptsbook(msbook)
                return self.format_book(ptsbook, book, num)

    def format_book(self, ptsbook, book, num):
        if not book:
            return '{} {}'.format(ptsbook, num)
        
        book = {'1':'i', '2':'ii', '3':'iii', '4':'iv', '5':'v', '6':'vi'
                }.get(book, book)
        return '{} {} {}'.format(ptsbook, book, num)

