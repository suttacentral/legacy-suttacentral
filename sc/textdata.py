import time
import regex
import pickle
import pathlib
import threading
from itertools import chain

import sc
from sc.tools import html
import logging
logger = logging.Logger(__name__)


""" A tool responsible for collating information from the texts

"""

def text_dir_md5(extra_files=[__file__]):
    """ Generates an md5 hash based on text modification times

    This can be used to detect if the database is up to date.

    By default uses all directories (not files) in the text_dir,
    plus this module file since changes to this module are quite
    likely to result in a different final database.

    """
    files = chain(sc.text_dir.glob('**/.'), (pathlib.Path(f) for f in extra_files))
    mtimes = (file.stat().st_mtime_ns for file in files)
    
    from hashlib import md5
    from array import array
    
    return md5(array('Q', mtimes)).hexdigest()

class TextInfo:
    __slots__ = ('uid', 'path', 'bookmark', 'name', 'author', 'volpage')
    def __init__(self, **kwargs):
        for key in self.__slots__:
            setattr(self, key, kwargs.get(key, None))
    def __repr__(self):
        return 'TextInfo({})'.format(', '.join('{}={}'.format(attr, getattr(self, attr)) for attr in self.__slots__))

class TextInfoModel:
    """ The TextInfoModel is responsible for scanning the entire contents
    of the text folders and building a model containing information not
    easily gleaned at a glance of the filesystem, which is required for
    purposes other than delivering the HTML of the text itself.

    It is required to delve quite deeply into the structure of the documents
    to discover all that is needed to be known.

    """
    
    def get(self, uid=None, lang_uid=None):
        """ Returns TextInfo entries which match arguments

        If both uid and lang_uid are defined, a single entry is returned
        if only one is defined, a dictionary of entries is returned
        If neither is defined it is a ValueError

        This method returns None if there are no matching entries.
        """
        
        try:
            if uid and lang_uid:
                try:
                    return self.by_uid[uid][lang_uid]
                except KeyError:
                    return None
            elif uid:
                return self.by_uid.get(uid, {})
            elif lang_uid:
                return self.by_lang.get(lang_uid, {})
            else:
                raise ValueError('At least one of uid or lang_uid must be set')
        except KeyError:
            return None

    def exists(self, uid, lang_uid):
        try:
            self.by_uid[uid][lang_uid]
            return True
        except KeyError:
            return False
    
    def __init__(self):
        self.by_lang = {}
        self.by_uid = {}

    def build(self):
        start=time.time()
        # The pagenumbinator should be scoped because it uses
        # a large chunk of memory which should be gc'd.
        
        p = PaliPageNumbinator() 
        for lang_dir in sc.text_dir.glob('*'):
            lang_uid = lang_dir.stem
            self.by_lang[lang_uid] = {}
            
            for htmlfile in lang_dir.glob('**/*.html'):
                uid = htmlfile.stem
                root = html.parse(str(htmlfile)).getroot()
                
                path = htmlfile.relative_to(sc.text_dir)
                author = _get_author(root, lang_uid, uid)
                name = _get_name(root, lang_uid, uid)
                volpage = _get_volpage(root, lang_uid, uid, p)
                embedded = _get_embedded_uids(root, lang_uid, uid, p)

                textinfo = TextInfo(uid=uid, path=path, name=name, author=author, volpage=volpage)
                self.by_lang[lang_uid][uid] = textinfo
                if uid not in self.by_uid:
                    self.by_uid[uid] = {}
                self.by_uid[uid][lang_uid] = textinfo

                for child in embedded:
                    child.path = path
                    child.author = author
                    self.by_lang[lang_uid][child.uid] = child
                    if child.uid not in self.by_uid:
                        self.by_uid[child.uid] = {}
                    self.by_uid[child.uid][lang_uid] = child

                m = regex.match(r'(.*?)(\d+)-(\d+)$', uid)
                if m:
                    range_textinfo = TextInfo(uid=uid+'#', path=path, name=name, author=author, volpage=volpage)
                    for i in range(int(m[2]), int(m[3]) + 1):
                        iuid = m[1] + str(i)
                        if iuid in self.by_uid:
                            if lang_uid in self.by_uid[iuid]:
                                continue
                        
                        self.by_lang[lang_uid][iuid] = range_textinfo
                        if iuid not in self.by_uid:
                            self.by_uid[iuid] = {}
                        self.by_uid[iuid][lang_uid] = range_textinfo
                        
                        
                        
        self.build_time = time.time()-start
        logger.info('Text Info Model built in {}s'.format(self.build_time))

    # Class Variables
    _build_lock = threading.Lock()
    _build_ready = threading.Event()
    _instance = None

def _get_author(root, lang_uid, uid):
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

def _get_name(root, lang_uid, uid):
    try:
        hgroup = root.select_one('.hgroup')
        h1 = hgroup.select_one('h1')
        return h1.text_content()
    except Exception as e:
        logger.warn('Could not determine name for {}/{}'.format(lang_uid, uid))
        return ''

def _get_volpage(element, lang_uid, uid, ppn):
    if lang_uid == 'zh':
        e = element.next_in_order()
        while e:
            if e.tag =='a' and e.select_one('.t, .t-linehead'):
                break
            e = e.next_in_order()
        else:
            return
        return 'T {}'.format(e.attrib['id'])
    elif lang_uid == 'pi':
        e = element.next_in_order()
        while e:
            if e.tag == 'a' and e.select_one('.ms'):
                return ppn.get_pts_ref_from_pid(e.attrib['id'])
            e = e.next_in_order()        

    return None

def _get_embedded_uids(root, lang_uid, uid, ppn):
    # Generates possible uids that might be contained
    # within this text.
    out = []
    
    if uid.endswith('-pm'):
        # This is a patimokkha text
        for h4 in root.select('h4'):
            a = h4.select_one('a[id]')
            if not a:
                continue
            
            volpage = _get_volpage(h4, lang_uid, uid, ppn)
            out.append(TextInfo(
                uid='{}#{}'.format(uid, a.attrib['id']),
                bookmark=a.attrib['id'],
                name=None,
                volpage=volpage))
    
    for e in root.select('.embeddedparallel'):
        if 'data-uid' in e.attrib:
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

def tim(force_build=False):
    """ Returns an instance of the TIM

    Will rebuild if and only if needed.

    Note that while this will happily build on demand, ideally it should
    be called in advance from a seperate process before restarting the server,
    thus preparing the cached copy.

    i.e.
    import sc.textdata
    sc.textdata.tim()

    It takes a considerable time to return
    
     """

    if not force_build and TextInfoModel._build_ready.set():
        return TextInfoModel._instance
        
    if TextInfoModel._build_lock.acquire(blocking=False):
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
        
    
    TextInfoModel._build_ready.wait()
    return TextInfoModel._instance
    

class PaliPageNumbinator:
    msbook_to_ptsbook_mapping = {
        'a': 'A',
        'ap': 'Ap',
        'bu': 'Bv',
        'cn': 'Nid II',
        'cp': 'Cp',
        'd': 'D',
        'dh': 'Dhp',
        'dhs': 'Dhs',
        'dht': 'Dhātuk',
        'it': 'It',
        'j': 'Ja',
        'kh': 'Khp',
        'kv': 'Kv',
        'm': 'M',
        'mi': 'Mil',
        'mn': 'Nidd I',
        'ne': 'Nett',
        'p': 'Paṭṭh',
        'pe': 'Peṭ',
        'ps': 'Paṭis',
        'pu': 'Pp',
        'pv': 'Pv',
        's': 'S',
        'sn': 'Sn',
        'th1': 'Th',
        'th2': 'Thī',
        'ud': 'Ud',
        'v': 'V',
        'vbh': 'Vibh',
        'vv': 'Vv',
        'y': 'Yam'}

    default_attempts = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9,-10,1,2,3,4,5,6,7,8,9,10]
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

        
        
        
        
