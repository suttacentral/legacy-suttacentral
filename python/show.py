#!/usr/bin/env python3.3

import regex, scdb, cherrypy, os, os.path

from jinja2 import Environment, FileSystemLoader

from views import *
import suttasearch, classes

import logging
logger = logging.getLogger(__name__)

STATIC_PAGES = ['about', 'abbreviations', 'bibliography', 'contacts', 'help',
                'methodology', 'sutta_numbering']

def sanitize(string):
    string = string.replace('<', '&lt;')
    string = string.replace('>', '&gt;')
    return string

def dispatch(*args, **kwargs):
    """ Call the correct view function.

    Because of SC's virtually flat url structure, we need to use a
    heavily customized dispatch function. We COULD do this formally though
    CP's framework, but laziness rules.

    """
    
    dbr = scdb.getDBR()
    if args[0] in STATIC_PAGES:
        # Static page (i.e. help) view!
        return static_view(args[0])
    try:
        uid = next(a for a in args if dbr(a))
    except StopIteration:
        uid = None
    try:
        lang = next(a for a in args if a in dbr.lang_codes)
    except StopIteration:
        lang = None
    logger.debug("Display uid={}, lang={}".format(uid, lang))

    if uid is None and lang is None:
        raise cherrypy.HTTPError(404, "No collection, division, subdivision, sutta or language group by that id exists.")

    if uid and lang:
        # Text view!
        return text_view( uid, lang)

    # Some urls don't contain a valid uid - these contain a number range.
    if lang and regex.search(r'\d-\d', args[0]):
        return text_view(args[0], lang)

    if lang is not None:
        # Language view!
        raise cherrypy.HTTPError(501, "You might see displayed here a list of texts and/or translations in the requested language. But don't hold your breath.")

    if uid is not None:
        # Collection, Division, Subdivision, or Sutta (Parallels) view
        if uid in dbr.collections:
            return collection_view(dbr.collections[uid])
        elif uid in dbr.divisions:
            full = len(args) > 1 and args[1] == 'full'
            return division_view(dbr.divisions[uid], full)
        elif uid in dbr.subdivisions:
            return subdivision_view(dbr.subdivisions[uid])
        elif uid in dbr.suttas:
            return parallels_view(dbr.suttas[uid])

def static_view(page):
    view = InfoView(page)
    return view.render()

def text_view(uid, lang):
    return TextView(uid, lang).render()

def collection_view(collection):
    return sanitize(str(collection))

def division_view(division, full):
    # HACK: This is just to do "What the old site did". 
    # Can we do this with some sort of sane logic?
    if division.uid in ["sn", "an", "kn", "ea", "t", "sht", "sa", "oa"] and not full:
        return SubdivisionHeadingsView(division).render()
    else:
        return DivisionView(division).render()

def subdivision_view(subdivision, captiondata=None):
    return SubdivisionView(subdivision).render()

def parallels_view(sutta):
    view = ParallelView(sutta)
    return view.render()

def search(query, target=None, limit=-1, offset=0, ajax=0):
    qdict = {'query':query, 'target':'all', 'limit':limit, 'offset':offset, 'ajax':ajax}

    search_result = classes.SearchResults(query=qdict)
    if not query:
        return search_result

    if not target or target == 'all' or target == 'suttas':
        slimit = limit
        if slimit == -1:
            slimit = 10 if ajax else 25
        search_result.add(suttasearch.search(query=query, limit=slimit, offset=offset))

    return SearchResultView(search_result).render()
