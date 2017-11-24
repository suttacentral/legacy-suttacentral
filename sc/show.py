import cherrypy
import json
import logging

from sc import classes, data_repo, dictsearch, scimm, suttasearch, textsearch
import sc.data
from sc.scm import data_scm
from sc.util import filelock
from sc.views import *
from sc.language import LanguageView
import sc.donations

logger = logging.getLogger(__name__)

STATIC_PAGES = {file.stem + (file.suffix if file.suffix != '.html' else '') 
                for file 
                in (sc.templates_dir / 'static').glob('*.html')}

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
    
    if args[0] == 'panel':
        max_age = 86400 * 7
        cherrypy.response.headers['cache-control'] = 'public, max-age={}'.format(max_age)
        return GenericView('panel', {}).render()

    full = len(args) == 2 and args[1] == 'full'
    
    if args[0] == 'll':
        uid = args[1]
        return RelationshipsView(uid).render()
    
    if args[-1] == 'discussion':
        uid = args[-2]
        lang_code = None if len(args) == 2 else args[-3]
        
        result = TextDiscussionView(uid, lang_code, embed=kwargs.get('embed')).render()
        if result:
            # Permit these to be cached for 1 hour (note, we make
            # sure we have a valid result first!)
            cherrypy.response.headers['cache-control'] = 'public, max-age=3600'
            return result
    if len(args) <= 2:
        if args[0] in imm.languages:
            div_uid = None if len(args) == 1 else args[1]
            if div_uid is None or (div_uid in imm.divisions or div_uid in imm.subdivisions) and not imm.tim.get(lang_uid=args[0], uid=div_uid):
                return LanguageView(lang=args[0], div_uid=div_uid).render()
    
    if len(args) == 1 or full:
        uid = args[0]

        # Static Pages
        if uid in STATIC_PAGES:
            return InfoView('static/{}'.format(uid)).render()

        if uid in imm.pitakas:
            return PitakaView(imm.pitakas[uid]).render()

        if uid == 'uids':
            return UidsView().render()

        uid = uid.replace('_', '#')
        
        if regex.match(r'it\d+', uid):
            new_url = '/{}'.format(uid.replace('it', 'iti'))
            raise cherrypy.HTTPRedirect(new_url, 301)

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
        
        
        
        redirect = False
        bookmark = None

        if not imm.text_exists(uid, lang_code):
            if imm.text_exists(lang_code, uid):
                redirect = True
                uid, lang_code = lang_code, uid
            elif lang_code == 'zh' and imm.text_exists(uid, 'lzh'):
                redirect = True
                lang_code = 'lzh'
            elif uid.startswith('it') and imm.text_exists(uid.replace('it', 'iti'), lang_code):
                redirect = True
                uid = uid.replace('it', 'iti')
            else:
                raise cherrypy.NotFound()

        textinfo = imm.tim.get(uid, lang_code)
        if textinfo.file_uid != textinfo.uid:
            redirect = True
            uid = textinfo.file_uid
            if textinfo.bookmark:
                bookmark = textinfo.bookmark
            else:
                bookmark = textinfo.uid
                
        if redirect:
            # This is an old-style url, redirect to new-style url.
            if len(args) == 2:
                new_url = '/{}/{}'.format(lang_code, uid)
            else:
                new_url =  '/{}/{}/{}'.format(lang_code, uid, args[2])
            
            if bookmark:
                new_url += '#' + bookmark
            
            # Don't be transparent, we want to keep things canonical
            # and also, use 301. This is a permament change.
            raise cherrypy.HTTPRedirect(new_url, 301)
        
        
        sutta = imm.suttas.get(uid)
        lang = imm.languages[lang_code]
        if len(args) == 3 and 'embed' in cherrypy.request.params:
            return TextSelectionView(uid, lang_code, args[2]).render()
        canonical = False if len(args) == 3 else True
        if 'raw' in kwargs:
            return TextRawView(uid, lang_code).render()
        if 'edit' in kwargs:
            if sc.config.app['editor']:
                return EditView(sutta, lang_code, canonical).render()
            
        if sutta:
            return SuttaView(sutta, lang, canonical).render()
        else:
            return TextView(uid, lang_code, canonical).render()

    raise cherrypy.NotFound()

def advanced_search(target=None, **kwargs):
    if not target:
        return AdvancedSearchView(None, **kwargs).render()
    if not 'limit' in kwargs:
        kwargs['limit'] = 50
    if not 'offset' in kwargs:
        kwargs['offset'] = 0
    try:
        if target == 'suttas':
            results = sc.search.adv_search.sutta_search(**kwargs)
            return AdvancedSearchView(results, **kwargs).render()
        else:
            raise cherrypy.HTTPError(502, "Invalid Search Target")
    except sc.search.ConnectionError:
        raise cherrypy.HTTPError(503, 'Elasticsearch Not Available')

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

def donate(page, **kwargs):
    try:
        if page == 'plan':
            return DonationsPlanView(**kwargs).render()
        elif page == 'payment':
            kwargs["amount"] = sc.donations.calc_amount(kwargs["dollar_amount"])
            return DonationsPaymentView(**kwargs).render()
        elif page == 'confirm':
            result = sc.donations.donate(**kwargs)
            if result is None:
                return DonationsErrorView().render()
            result.update(kwargs)
            return DonationsConfirmView(**result).render()
        raise cherrypy.NotFound()
    except sc.donations.stripe.error.InvalidRequestError:
        raise

def sutta_info(uid, lang='en'):
    try:
        return SuttaInfoView(uid, lang).render()
    except KeyError:
        raise cherrypy.HTTPError(404, 'Sutta does not exist')

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

def build_maitenance_page():
    html = GenericView('errors/maintenance', {}).render()
    with (sc.static_dir / 'maintenance.html').open('w', encoding='utf8') as f:
        f.write(html)

try:
    build_maitenance_page()
except Exception as e:
    logger.exception("Could not build maitenance page")
    raise SystemExit("Failed to build the maitenace page, this indicates critical problems, exiting")
