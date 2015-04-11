import cherrypy
import json
import logging

from sc import classes, data_repo, dictsearch, scimm, suttasearch, textsearch
import sc.data
from sc.scm import data_scm
from sc.util import filelock
from sc.views import *

logger = logging.getLogger(__name__)

STATIC_PAGES = ['about', 'abbreviations', 'bibliography', 'contacts', 'help',
                'methodology', 'sutta_numbering', 'copyright', 'colors',
                'fonts']

def home():
    return InfoView('home').render()

def default(*args, **kwargs):
    """Parse the path arguments and call the correct view function.

    We use the following (fairly flat) URL structure:

        <static_page>                 : static page, e.g., help
        <division_uid>                : division view or subdivision headings
                                        view (depending on if the division
                                        supports full division view)
        <division_uid>/full           : full division view (for those
                                        divisions that support it)
        <subdivision_uid>             : subdivision view
        <sutta_uid>                   : sutta parallel view
        <text_sutta_uid>/<lang>       : sutta text view
        <text_translation_uid>/<lang> : translation text view

    TODO: Collections?
    """

    imm = scimm.imm()

    full = len(args) == 2 and args[1] == 'full'
    
    if len(args) == 1 or full:
        uid = args[0]

        # Static Pages
        if uid in STATIC_PAGES:
            return InfoView(uid).render()

        if uid in imm.pitakas:
            return PitakaView(imm.pitakas[uid]).render()

        if uid == 'uids':
            return UidsView().render()

        uid = uid.replace('_', '#')

        # Divisions
        division = imm.divisions.get(uid)
        if division:
            if division.collection.pitaka.always_full:
                if len(division.subdivisions) > 1:
                    if division.collection.pitaka.always_full:
                        full = True
            if division.has_subdivisions():
                if full:
                    return DivisionView(division).render()
                else:
                    return SubdivisionHeadingsView(division).render()
            elif not full:
                return DivisionView(division).render()

        # Subdivisions
        subdivision = imm.subdivisions.get(uid)
        if subdivision:
            return SubdivisionView(subdivision).render()

        # Sutta Parallels
        sutta = imm.suttas.get(uid)
        if sutta:
            return ParallelView(sutta).render()
        
    elif len(args) >= 2:
        
        if args[1] == 'citation.txt':
            # Citation
            cherrypy.response.headers['Content-Type'] = "text/plain"
            sutta = imm.suttas.get(args[0])
            if sutta:
                return SuttaCitationView(sutta).render()
            else:
                raise cherrypy.NotFound()
        # Sutta or Translation Texts

        # New style urls have the language code first then the uid
        lang_code = args[0]
        uid = args[1]

        if not imm.text_exists(uid, lang_code):
            redirect = False
            if imm.text_exists(lang_code, uid):
                redirect = True
                uid, lang_code = lang_code, uid
            elif lang_code == 'zh' and imm.text_exists(uid, 'lzh'):
                redirect = True
                lang_code = 'lzh'
            if redirect:
                # This is an old-style url, redirect to new-style url.
                if len(args) == 2:
                    new_url = '/{}/{}'.format(lang_code, uid)
                else:
                    new_url =  '/{}/{}/{}'.format(lang_code, uid, args[2])
                # Don't be transparent, we want to keep things canonical
                # and also, use 301. This is a permament change.
                raise cherrypy.HTTPRedirect(new_url, 301)
            else:
                raise cherrypy.NotFound()
        
        sutta = imm.suttas.get(uid)
        lang = imm.languages[lang_code]
        if len(args) == 3 and 'embed' in cherrypy.request.params:
            return TextSelectionView(uid, lang_code, args[2]).render()
        canonical = False if len(args) == 3 else True
        if sutta:
            return SuttaView(sutta, lang, canonical).render()
        else:
            return TextView(uid, lang_code, canonical).render()

    raise cherrypy.NotFound()

def search(query, **kwargs):
    if not 'limit' in kwargs:
        kwargs['limit'] = 10
    if not 'offset' in kwargs:
        kwargs['offset'] = 0
    try:
        if 'autocomplete' in kwargs:
            results = sc.search.autocomplete.search(query, **kwargs)
            return json.dumps(results, ensure_ascii=False, sort_keys=True)
        else:
            results = sc.search.query.search(query, **kwargs)
            return ElasticSearchResultsView(query, results, **kwargs).render()
    except sc.search.ConnectionError:
        raise cherrypy.HTTPError(503, 'Elasticsearch Not Available')

def sutta_info(uid, lang='en'):
    return SuttaInfoView(uid, lang).render()

def data(**kwargs):
    valid_names = {'langs', 'translation_count', 'suttas', 'parallels',
					'text_images'}

    out = {}
    for name in kwargs:
        if name in valid_names:
            out[name] = getattr(sc.data.data, name)(**kwargs)
    return out

def downloads():
    return DownloadsView().render()

def sht_lookup(query):
    return ShtLookupView(query).render()

def define(term):
    return DefinitionView(term).render()

def admin_index():
    return AdminIndexView().render()

def admin_data_notify(json_payload):
    if json_payload:
        logger.info('Data update request')
        try:
            payload = json.loads(json_payload)
        except ValueError:
            payload = None
        if isinstance(payload, dict):
            logger.info('Payload: {}'.format(repr(payload)))
            payload_branch = str(payload.get('ref')).replace('refs/heads/', '')
            update_data = data_scm.branch == payload_branch
        else:
            logger.warning('Invalid payload: {}'.format(repr(json_payload)))
            update_data = False
    else:
        logger.info('Data update request (manually-triggered)')
        update_data = True
    if update_data:
        logger.info('Data update started')
        data_repo.update(bg=True)
    else:
        logger.info('Data update request ignored')
    raise cherrypy.HTTPRedirect('/admin', 303)

def error(status, message, traceback, version):
    return ErrorView(status=status, message=message, traceback=traceback, version=version).render()

def profile(locals_dict, globals_dict, *args, **kwargs):
    """ Generates a profile

    You can request a profile anytime by appending ?profile to the url.

    If config.profile_passhash is set, then you must use ?profile=password
    where sha1(password.encode() + b'foobarusrex') == profile_passhash

    If the password is required and not correct, raises a value error.

    """
    
    from tempfile import NamedTemporaryFile
    from hashlib import sha1
    from io import StringIO
    import cProfile
    from pstats import Stats
    import regex
    key = kwargs['profile'].encode() + b'spambarusrex'
    if sc.config.app['profile_passhash'] and (sha1(key).hexdigest() !=
        sc.config.app['profile_passhash']):
            raise ValueError('Invalid Password')
    with NamedTemporaryFile(prefix='profile') as tmpfile:
        cProfile.runctx("show.default(*args, **kwargs)",
            globals=globals_dict,
            locals=locals_dict,
            filename=tmpfile.name)
        stats = Stats(tmpfile.name)
    stats.sort_stats('tottime')
    stats.stream = StringIO()
    stats.print_stats()
    out = stats.stream.getvalue()
    splitpoint = out.find('ncalls')
    preamble = out[:splitpoint]
    table = out[splitpoint:]
    def splitdict(d):
        return ['{}: {}'.format(k, d[k]) for k in sorted(d)]
            
    m = regex.search(r'(?<= )(/home/.*)(/site-packages)(?=/)', table)
    site_packages = m[1] + m[2] if m else 'Unknown'
    table = table.replace(site_packages, '…')
            
    return '''<!DOCTYPE html><html><head><meta charset="utf8">
<title>{}</title>\
<body style="font-family: monospace;">
<h1> {} : Debug and Profile information</h1>
<h2> Request Info: </h2>

<pre>cherrypy.request.config = {{\n{}\n}}</pre>
<pre>cherrypy.request.headers = {{\n{}\n}}</pre>

<h2> Profile </h2>
<pre>{}\nsite-packages (…) = {}</pre>
<table><tbody>{}</tbody></table>
<script src="/js/vendor/jquery-1.10.2.min.js"></script>
<script src="/js/tablesort.js"></script>'''.format(
        'Profile',
        ''.join('/' + a for a in args),
        '\n'.join('    ' + e for e in splitdict(cherrypy.request.config)),
        '\n'.join('    ' + e for e in splitdict(cherrypy.request.headers)),
        preamble,
        site_packages,
        '\n'.join('<tr>' + ''.join(
            '<td>{}'.format(s) for s in line.split(maxsplit=5)) for line in table.split('\n'))
    )
