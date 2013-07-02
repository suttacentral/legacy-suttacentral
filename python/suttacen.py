#!/usr/bin/env python3.3

import scdb, regex, textfunctions, cherrypy, show, bisect

def from_uid(uid):
    print("Looking up {}".format(uid))
    dbr = scdb.getDBR()
    string = str(dbr(uid))
    if string:
        string = string.replace('<', '&lt;')
        string = string.replace('>', '&gt;')
        
        print(string)
        return string
    return "<Not found>"

def debug(*args, **kwargs):
    out=[]
    if len(args) == 1:
        dbr = scdb.getDBR()
        uid = args[0]
        string = str(dbr(uid))
        print("String: {}".format(string))
        
        if string == 'None':
            if uid in (l.code for l in dbr.collection_languages.values()):
                string="<ul>{}</ul>".format('<li>'.join(
                '<a href="/debug/{0}">{0}</a> {1}'.format(v.uid, v.name)
                for v in dbr.suttas.values() if v.lang.code == uid))
                out.append(string)
                
        elif string != 'None':
            
            
            out.append(sanitize(string))
        else:
            out.append("« Not Found »")
    else:
        out.append("« No Guidance »")
        
    return "<p>" + "<p>".join(out)

def sanitize(string):
    string = regex.subf(r'<(?!br)([a-z0-9.-]+)>',
                r'«a href="/debug/{1}"»{1}«/a»', string)
    string = string.replace('<', '&lt;')
    string = string.replace('>', '&gt;')
    string = string.replace('«', '<')
    string = string.replace('»', '>')
    return string

class DummyObject:
    pass

class DummySubdivisions:
    def __init__(self, name, suttas):
        self.name = name
        self.suttas = suttas

class SuttaResults:
    name = ""
    acronym = ""
    def __init__(self, label=""):
        self.collection = DummyObject()
        self.subdivisions = []
        self.collection.name = "Search Results"
        self.name = label

    def add_suttas(self, label, suttas):
        self.subdivisions.append(DummySubdivisions(label, suttas))

class Ranker:
    def __init__(self, query):
        self.query_cased = query
        self.query = query.casefold()
        self.query_whole = ' ' + self.query.strip() + ' '
        self.query_starts = ' ' + self.query.strip()
        self.query_simple = textfunctions.simplify(self.query)

    def __call__(self, input):
        query = self.query
        query_simple = self.query_simple
        if self.query_whole in input[1]:
            rank = 100
        elif self.query_starts in input[1]:
            rank = 200
        elif self.query in input[1]:
            rank = 300
        elif ' ' + self.query_simple + ' ' in input[3]:
            rank = 400
        elif ' ' + self.query_simple in input[3]:
            rank = 500
        elif self.query_simple in input[3]:
            rank = 600
        else:
            rank = 10000

        #if self.query_cased in input[2]:
            #rank -= 50

        rank += input[0].subdivision.division.id

        return rank


class Find(object):
    @cherrypy.expose
    def index(self, **kwargs):
        query = list(kwargs.values())[0]
        return self.show_results(query)

    def show_results(self, query):
        results = self.search_dbr(query)
        
        ranker = Ranker(query)

        ranks, suttas = zip(*sorted((ranker(s), s[0]) for s in results))

        breakpoint = bisect.bisect(ranks, 399)

        results = SuttaResults("Results for {}".format(query))
        results.add_suttas("Exact results", suttas[:breakpoint])
        results.add_suttas("Similiar results", suttas[breakpoint:])

        return show.DivisionView(results).render()

    def search_dbr(self, query):
        dbr = scdb.getDBR()
        # The structure of dbr.searchstrings is :
        # ( sutta, searchstring, searchstring_cased, suttaname simplified)

        # First try matching query as a whole
        cf_query = query.casefold()
        sm_query = textfunctions.simplify(query)
        results = set(s for s in dbr.searchstrings if cf_query in s[1])
        results_s = set(s for s in dbr.searchstrings if sm_query in s[3])

        results.update(results_s)

        return results
        

#cherrypy.config.update({'error_page.default': error_page})