import bisect
import scdb, classes, textfunctions

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

        if self.query_cased in input[2]:
            rank -= 50

        rank += input[0].subdivision.division.id

        return rank

def search(query=None, limit=-1, offset=0):
    
    results = search_dbr(query)

    ranker = Ranker(query)

    ranks, suttas = zip(*sorted((ranker(s), s[0]) for s in results))
    count = len(suttas)
    ranks = ranks[offset:limit]
    suttas = suttas[offset:limit]
    
    breakpoint = bisect.bisect(ranks, 399)
    out = classes.SuttaResultsCategory(total=count)
    e_results = suttas[:breakpoint]
    s_results = suttas[breakpoint:]
    if e_results:
        out.add("Exact results", e_results)
    if s_results:
        out.add("Similiar results", s_results)
    return out
        
def search_dbr(query):
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