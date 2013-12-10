import bisect, math, functools
import scimm, classes, textfunctions
from html import escape

class Ranker:
    def __init__(self, query, lang):
        self.query_cased = query
        self.query = query.casefold()
        self.query_whole = ' ' + self.query + ' '
        self.query_starts = ' ' + self.query
        self.query_simple = textfunctions.simplify_pali(self.query)
        self.lang = lang

    def __call__(self, input):
        query = self.query
        sutta = input[0]
        lang = self.lang
        query_simple = self.query_simple
        if self.query:
            if self.query_whole in input[1]:
                rank = 100
            elif self.query_starts in input[1]:
                rank = 200
            elif self.query in input[1]:
                rank = 300
            elif ' ' + self.query_simple + ' ' in input[3]:
                rank = 1000
            elif ' ' + self.query_simple in input[3]:
                rank = 1100
            elif self.query_simple in input[3]:
                rank = 1200
            else:
                rank = 10000
        else:
            rank = 200

        if lang:
            if lang == sutta.lang.code or any(
                lang == t.lang.code and t.url.startswith('/')
                    for t in sutta.translations):
                rank -= 100
            else:
                rank += 1200

        # Add bonus rank for suttas with more parallels.
        pbonus = sum(3 - 2 * t.partial for t in sutta.parallels)
        pbonus += len(sutta.translations)
        bonus = 200 * math.log(2) / math.log(2 + pbonus)

        # Penalize suttas from a subdivision with very many suttas.
        if pbonus < 4:
            bonus += 5 * int(10 / max(1, 25 - sutta.number))

        # Give a boost to suttas from a division with few suttas
        if len(sutta.subdivision.division.subdivisions) == 1:
            bonus -= 50 * math.log(32) / math.log(1 + len(sutta.subdivision.suttas))

        #if self.query_cased in input[2]:
            #bonus -= 25

        rank += bonus

        rank += sutta.subdivision.division.id

        return 10 * int(rank / 10) 

# This is a good place for a cache, since it is quite likely that
# the same results will be requested again, with only the offset changed.
# Results are not large, so there's little harm in caching a lot of them.

def get_and_rank_results(query, lang=None):
    results = search_imm(query, lang)
    if len(results) == 0:
        return ((),())
    ranker = Ranker(query, lang)
    ranks, suttas = zip(*sorted((ranker(s), s[0]) for s in results))
    return (ranks, suttas)

def search(query=None, limit=25, offset=0):
    out = classes.SuttaResultsCategory()
    searchlang = None
    quoted = '"' in query
    query = query.replace('"', '')
    if len(query) <= 3:
        imm = scimm.imm()
        if query in imm.lang_codes:
            searchlang = query
        if not searchlang and len(query) <= 2:
            out.total = 0
            out.add("Search term too short.", [])
            return out
    if searchlang:
        ranks, suttas = get_and_rank_results(query='', lang=searchlang)
    else:
        ranks, suttas = get_and_rank_results(query)
    


    ranks = ranks[offset:offset+limit]
    suttas = suttas[offset:offset+limit]
    
    breakpoint = bisect.bisect(ranks, 700)
    e_results = suttas[:breakpoint]
    s_results = suttas[breakpoint:]
    if quoted:
        s_results = []
    
    count = len(e_results) + len(s_results)
    out.total = count
    if count == 0:
        out.add("No results", [])
        return out

    if count > offset+limit:
        start = limit + offset
        href = '/search/?query={}&target=suttas&limit={}&offset={}'.format(
            query, limit, start)
        out.footurl = '<a href="{}">Results {}–{}</a>'.format(
            escape(href), start + 1, min(count, start + limit))
    
    if e_results:
        out.add("Exact results", e_results)
    if s_results and not quoted:
        out.add("Similiar results", s_results)
    return out
        
def search_imm(query, lang):
    imm = scimm.imm()
    # The structure of imm.searchstrings is :
    # ( sutta, searchstring, searchstring_cased, suttaname simplified)

    # First try matching query as a whole
    if lang:
        cf_query = " " + lang + " "
        sm_query = None
    else:
        cf_query = query.casefold()
        sm_query = textfunctions.simplify_pali(query)
    results = set(s for s in imm.searchstrings if cf_query in s[1])
    if sm_query and cf_query != sm_query:
        results_s = set(s for s in imm.searchstrings if sm_query in s[3])
        results.update(results_s)

    return results

def stress(count=1000):
    import time, concurrent.futures, random
    imm = scimm.imm()
    terms = [s.name[:4] for s in imm.suttas.values()]
    random.shuffle(terms)
    terms = terms[:1000] * int(1 + count / 1000)
    queries = random.sample(terms, count)

    getter = concurrent.futures.ThreadPoolExecutor(4)

    start = time.time()
    for r in getter.map(search, queries):
        pass
    done = time.time()

    print("Performed {} queries in {} seconds.".format(len(queries), done-start))
    print("{} queries per second.".format(len(queries) / (done-start)))
    