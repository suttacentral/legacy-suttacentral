import cherrypy
import json
import logging

from sc import classes, data_repo, dictsearch, scimm, suttasearch, textsearch
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
        
    elif len(args) == 2:
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
            if imm.text_exists(lang_code, uid):
                # This is an old-style url, redirect to new-style url.
                # (Don't be transparent, we want to keep things canonical)
                # (Also, use 301. This is a permament change)
                raise cherrypy.HTTPRedirect('/{}/{}'.format(uid, lang_code), 301)
            else:
                raise cherrypy.NotFound()
        
        sutta = imm.suttas.get(uid)
        lang = imm.languages[lang_code]
        if sutta:
            return SuttaView(sutta, lang).render()
        else:
            return TextView(uid, lang_code).render()

    raise cherrypy.NotFound()

def search(query, target=None, limit=0, offset=0, ajax=0, **kwargs):
    limit = int(limit)
    offset = int(offset)
    if not target:
        target = 'all'
    ajax = not ajax in (None, 0, '0')
    if not limit:
        limit = 10 if ajax else 25
    qdict = {'query':query, 'target':target, 'limit':limit, 'offset':offset, 'ajax':ajax}
    qdict.update(kwargs)

    search_result = classes.SearchResults(query=qdict)
    if not query:
        return search_view(query, search_result)

    if target=='all' or 'terms' in target or 'entries' in target:
        dict_results = dictsearch.search(query=query, target=target, limit=limit, offset=offset, ajax=ajax, **kwargs)
        if dict_results:
            search_result.add(dict_results)

    if target == 'all' or 'texts' in target:
        text_results = textsearch.search(query=query, target=target, limit=limit, offset=offset, **kwargs)
        if text_results:
            search_result.add(text_results)

    if target in ('all', 'suttas'):
        slimit = limit
        if slimit == -1:
            slimit = 10 if ajax else 25
        search_result.add(suttasearch.search(query=query, limit=slimit, offset=offset))

    return search_view(query, search_result)

def search_view(search_query, search_result):
    if not search_result.query['ajax']:
        return SearchResultView(search_query, search_result).render()
    else:
        return AjaxSearchResultView(search_query, search_result).render()

def downloads():
    return DownloadsView().render()

def sht_lookup(query):
    return ShtLookupView(query).render()

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
