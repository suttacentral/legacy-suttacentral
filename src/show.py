import cherrypy, os, regex
import classes, scdb, suttasearch
from views import *
import classes, suttasearch, dictsearch, textsearch

import logging
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

    uid = args[0]

    # Static Pages
    if uid in STATIC_PAGES:
        return InfoView(uid).render()

    dbr = scdb.getDBR()

    # Divisions
    full = len(args) == 2 and args[1] == 'full'
    if len(args) == 1 or full:
        division = dbr.divisions.get(uid)
        if division:
            if division.has_subdivisions():
                if full:
                    return DivisionView(division).render()
                else:
                    return SubdivisionHeadingsView(division).render()
            elif not full:
                return DivisionView(division).render()

    # Subdivisions
    if len(args) == 1:
        subdivision = dbr.subdivisions.get(uid)
        if subdivision:
            return SubdivisionView(subdivision).render()

    if len(args) == 1:
        # Sutta Parallels
        sutta = dbr.suttas.get(uid)
        if sutta:
            return ParallelView(sutta).render()
    elif len(args) == 2:
        if args[1] == 'citation.txt':
            # Citation
            cherrypy.response.headers['Content-Type'] = "text/plain"
            sutta = dbr.suttas.get(args[0])
            if sutta:
                return SuttaCitationView(sutta).render()
            else:
                raise cherrypy.NotFound()
        # Sutta or Translation Texts
        lang_code = args[1]
        path = '%s/%s' % (uid, lang_code)
        suttas = dbr.sutta_texts.get(path)
        if suttas and suttas[0]:
            sutta = suttas[0]
            return SuttaView(sutta, sutta.lang, uid, lang_code).render()
        translations = dbr.translation_texts.get(path)
        if translations and translations[0]:
            translation = translations[0]
            return SuttaView(translation.sutta, translation.lang, uid, lang_code).render()
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

def fallback_disp_handler(id, collection):
    try:
        id = int(id)
    except (TypeError, ValueError) as e:
        id = None
    if id:
        objects = getattr(scdb.getDBR(), collection).values()
        # Looping is awful but it's all we have for now...
        for object in objects:
            if object.id == id:
                path = '/{}'.format(object.uid)
                raise cherrypy.HTTPRedirect(path, 301)
    raise cherrypy.NotFound()

def fallback_disp_correspondence(sutta_id=None, **kwargs):
    fallback_disp_handler(sutta_id, 'suttas')

def fallback_disp_subdivision(division_id=None, **kwargs):
    fallback_disp_handler(division_id, 'divisions')

def fallback_disp_sutta(division_id=None, subdivision_id=None, **kwargs):
    if subdivision_id:
        fallback_disp_handler(subdivision_id, 'subdivisions')
    else:
        fallback_disp_handler(division_id, 'divisions')
