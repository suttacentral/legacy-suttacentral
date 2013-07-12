import cherrypy, os, regex
import classes, scdb, suttasearch
from views import *
import classes, suttasearch, dictsearch

import logging
logger = logging.getLogger(__name__)

STATIC_PAGES = ['about', 'abbreviations', 'bibliography', 'contacts', 'help',
                'methodology', 'sutta_numbering']

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
        # Sutta or Translation Texts
        lang = args[1]
        path = '%s/%s' % (uid, lang)
        suttas = dbr.sutta_texts.get(path)
        if suttas:
            return TextView(uid, lang).render()
        translations = dbr.translation_texts.get(path)
        if translations:
            return TextView(uid, lang).render()

    raise cherrypy.HTTPError(404, 'Unknown path {}'.format(' '.join(args)))

def search(query, target='all', limit=10, offset=0, ajax=0):
    limit = int(limit)
    offset = int(offset)
    ajax = not ajax in (None, 0, '0')
    qdict = {'query':query, 'target':target, 'limit':limit, 'offset':offset, 'ajax':ajax}

    search_result = classes.SearchResults(query=qdict)
    if not query:
        return search_result

    if target=='all' or 'terms' in target or 'entries' in target:
        dict_results = dictsearch.search(query=query, target=target, limit=limit, offset=offset, ajax=ajax)
        if dict_results:
            search_result.add(dict_results)

    if target in ('all', 'suttas'):
        slimit = limit
        if slimit == -1:
            slimit = 10 if ajax else 25
        search_result.add(suttasearch.search(query=query, limit=slimit, offset=offset))

    return search_view(search_result)

def search_view(search_result):
    if not search_result.query['ajax']:
        return SearchResultView(search_result).render()
    else:
        return AjaxSearchResultView(search_result).render()
