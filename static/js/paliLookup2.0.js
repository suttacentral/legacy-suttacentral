sc = window.sc || {};

/* PaliLookup2.0
 * 
 * This is a fully async module, i.e. caching and such is all assumed
 * to by async.
 * 
 * Depends on jQuery, underscore and elasticsearch.jquery.js
 * 
 * Note that altough the API is able to make PUSH and DELETE requests
 * and so on, all requests made to https://elastic.suttacentral.net
 * are converted to GET before being received by the elasticsearch
 * server. As such only the public API is readonly.
 *
 */

sc.paliLookup = {
    _cache: {},
    _handlers: [],
    index: 'en-dict',
    sources: {
        cped: {
            'brief': 'CPD',
            'name': 'Concise Pali English Dictionary'
        },
        pts_ped: {
            'brief': 'PTS',
            'name': 'PTS Pali English Dictionary'
        },
        dhammika_ff: {
            'brief': 'N&E',
            'name': "Nature and the Environment in Early Buddhism by S. Dhammika"
        },
        sc_dppn: {
            'brief': 'PPN',
            'name': 'Pali Proper Names'
        }
    },
    isReady: false,
    init: function(args) {
        var self = this;
        if (self.isReady) return
        
        self.elasticUrl = args.elasticUrl;
        self.targetSelector = args.target;
        // Ensure that elasticsearch library is available.
        if ($.es === undefined) {
            $.getScript('https://cdnjs.cloudflare.com/ajax/libs/elasticsearch/5.0.0/elasticsearch.jquery.min.js')
             .success(function(){self.init1(args)})
        } else {
            self.init1(args);
        }
    },
    init1: function(args) {
        var self = this;
        
        self.client = $.es.Client({
            hosts: self.elasticUrl
        });
        self.isReady = true
    },
    addHandlers: function() {
        var self = this;
        $('main').on('mouseover.lookup', self.targetSelector, function(e){
            if ($(e.target).parents('.text-popup').length > 0) {
                return
            }
            sc.popup.clear(true);
            self.lookup(e.target, null, _.bind(self.buildQuery, self));
        });
        $('main').on('click.lookup', self.targetSelector, function(e) {
            sc.popup.clear(true);
            self.decomposeMode(e.target);
        });
    },
    removeHandlers: function() {
        sc.popup.clear(true);
        $('main').off('.lookup')
    },
    deTiTerm: function(term) {
        return term.replace(/n[”’]+ti$/, 'ṃ').replace(/[”’]+ti$/, '');
    },
    getTerm: function(node) {
        var term = node.childNodes[1].nodeValue;
        
        term = term.replace(/ṁ/g, 'ṃ')
                   .replace('\xad', '')
                   .toLowerCase()
                   .replace(/^([^”’]+)/, '$1');
        term = this.deTiTerm(term);
        if (!term || term.match(/^\s+$/)) return null
        return term
    },
    buildPopup: function(results) {
        var body = $('<div class="popup-wrap"/>'),
            leftCol = $('<div class="left-col"/>').appendTo(body),
            rightCol = $('<div class="right-col"/>').appendTo(body);
    },
    lookup: function(node, term, queryFn) {
        var self = this;
        
        var term = term || self.getTerm(node);
        if (!term) return

        self.search(term, queryFn, function(results) {
            if (results.hits.total == 0) return
            var table = $('<table/>');
            
            results.hits.hits.slice(0, 4).forEach(function(hit) {
                var tr = $('<tr/>').appendTo(table);
                if (hit._score < 2) {
                    tr.addClass('poor-match')
                }
                $('<td class="term"/>').text(hit._source.term).appendTo(tr);
                $('<td class="score"/>').text(hit._score).appendTo(tr);
                var meaning = $('<td class="meaning"/>').appendTo(tr);
                var ul = $('<ul/>').appendTo(meaning);
                hit._source.entries.forEach(function(entry) {
                    var li = $('<li/>').appendTo(ul);
                    $('<a class="source"/>').text(self.sources[entry.source].brief)
                                            .attr('title', self.sources[entry.source].name)
                                            .appendTo(li);
                    
                    var content = $('<div class="content"/>').append(entry.html_content)
                                               .appendTo(li);
                    content.find('dt').remove();
                    content.find('dd > p:first-child').contents().unwrap();
                });
            });
            popup = sc.popup.popup(node, table);
            if (popup) {
                popup.on('click', 'li', function(e) {
                    popup.find('.clicked').removeClass('clicked');
                    $(this).addClass('clicked');
                    return false
                });
            }
        });
    },
    decomposeMode: function(node) {
        var self = this,
            term = self.getTerm(node),
            popup = $('<div class="decomposed"/>');
        if (!term) return

        _(term).each(function(char) {
            popup.append($('<span class="letter"/>').text(char))
        });
        var em = Number(getComputedStyle(node, "").fontSize.match(/(\d*(\.\d*)?)px/)[1])
        var pos = $(node).offset();
        
        sc.popup.popup($(node).offset(), popup, true);
        var offset = popup.parent().offset();
        offset.top -= em / 3;
        offset.left -= em / 2;
        popup.parent().offset(offset);
        popup.on('mouseover click', '.letter', function(e) {
            $('.letter.selected').removeClass('selected');
            var letters = $(e.target).add($(e.target).nextAll());
            letters.addClass('selected');
            var out = letters.map(function(i, e) {return $(e).text()})
                             .get()
                             .join('');
            sc.popup.clear();
            console.log('Looking up: ', out);
            self.lookup(e.target, out, _.bind(self.buildQueryDecomposed, self));
            return false
        })
    },
    decomposeVowels: function(term) {
        var table = {
                'a': ['a'],
                'ā': ['ā', 'a'],
                'i': ['i'],
                'ī': ['ī', 'i'],
                'u': ['u'],
                'ū': ['ū', 'u'],            
                'e': ['e', 'a', 'i'],
                'o': ['o', 'a', 'u']
            },
            firstChar = term[0],
            lastChar = term.slice(-1),
            terms = [];
        if (table[firstChar]) {
            table[firstChar].forEach(function(char) {
                terms.push(char + term.slice(1));
            })
        } else {
            terms.push(term);
        }
        terms2 = [];
        if (table[lastChar]) {
            terms.forEach(function(term) {
                table[lastChar].forEach(function(char) {
                    terms2.push(term.slice(0, -1) + char);
                });
            });
        } else {
            terms2 = terms;
        }
        return terms2;
    },
    decompose: function(term, callback) {
        term = this.deTiTerm(term)
        var out = this.conjugate(term);
        for (var j = term.length - 1; j > 0; j--) {
            subTerm = term.slice(0, j);
            if (subTerm.length <= 2) continue
            out = out.concat(this.decomposeVowels(subTerm));
        }
        console.log('Decomposed: ', out);
        return out;
    },
    storeInCache: function(term, resp) {
        this._cache[term] = resp;
    },
    retrieveFromCache: function(term, success, failure) {
        if (false || this._cache[term]) {
            success(this._cache[term])
        } else {
            failure()
        }
    },
    search: function(term, queryFn, callback) {
        var self = this;
        
        var query = queryFn(term),
            key = JSON.stringify(term);
        
        //self.retrieveFromCache(key, callback, function() {
            self.esSearch(query, function(resp) {
                
                //self.storeInCache(key, resp);
                callback(resp);
            });
        //});
    },
    buildQuery: function(term) {
        console.log(this);
        if (term.match(/ṃ$/)) {
            var fuzzyQuery = {
                "bool": {
                    "should": [
                        {
                            "fuzzy": {
                                "term": {
                                    "max_expansions": 5,
                                    "prefix_length": 3,
                                    "value": term
                                }
                            }
                        },
                        {
                            "fuzzy": {
                                "term": {
                                    "max_expansions": 5,
                                    "prefix_length": 2,
                                    "value": term.replace(/ṃ$/, '')
                            }
                          }
                        }
                    ]
                }
            }
        } else {
            fuzzyQuery = {
                "fuzzy": {
                    "term": {
                        "max_expansions": 5,
                        "prefix_length": 3,
                        "value": term
                    }
                }
            }
        }
        var body = {
            _source: ['gloss', 'entries', 'term'],
            query: {
                bool: {
                    should: [
                        {
                            constant_score: {
                                filter: {
                                    term: {
                                        term: term
                                    }
                                },
                                boost: 10
                            }
                        },
                        {
                            constant_score: {
                                filter: {
                                    terms: {
                                      term: this.conjugate(term)
                                    }
                                },
                                boost: 10
                            }
                        },
                        fuzzyQuery
                    ]
                }
            }
        }
        return body
    },
    buildQueryDecomposed: function(term) {
        var body = {
            _source: ['gloss', 'entries', 'term'],
            query: {
                constant_score: {
                    filter: {
                        terms: {
                          term: this.decompose(term)
                        }
                    }
                }
            }
        }
        return body
    },
    esSearch: function(query, callback) {
        var self = this;
        console.log(JSON.stringify(query, null, 2));
        self.client.search({
            index: self.index,
            type: 'definition',
            body: query
        }).then(function(resp) {
            console.log(resp.hits.total);
            callback(resp);
        }, function(err) {
            console.trace(err.message);
        });
    },
    conjugate: function(word){
        var end = this.endings;
        var results = [word];
        
            results.push(word.slice(0, -1));
        for (var pass = 0; pass < 2; pass++) {
            if (pass == 1) {
                if (word.slice(-1) == 'ṃ') {
                    word = word.slice(0, -1)
                } else {
                    break
                }
            }
            for(var i = 0; i < end.length; i++) {
                if(word.length > end[i][2] && word.substring(word.length - end[i][0].length, word.length) === end[i][0]) {
                    var orig = word.substring(0,word.length - end[i][0].length + end[i][1]) + end[i][3];
                    if (orig.length >= 2) {
                        results.push(orig);
                    }
                }
            }
        }
        return _.uniq(results);
    }
}

sc.paliLookup.endings = [
['i',1,0,''],
['u',1,0,''],
['ati',1,0,''],
['āti',1,0,''],
['eti',1,0,''],
['oti',1,0,''],
['o',0,0,'a'],
['ā',0,0,'a'],
['aṁ',1,0,''],
['ṁ',0,0,''],
['e',0,0,'a'],
['ena',0,0,'a'],
['ehi',0,0,'a'],
['ebhi',0,0,'a'],
['āya',0,0,'a'],
['ssa',0,0,''],
['ānaṁ',0,0,'a'],
['smā',0,0,''],
['mhā',0,0,''],
['smiṁ',0,0,''],
['mhi',0,1,''],
['esu',0,0,'a'],
['ayo',0,1,'i'],
['ī',1,1,''],
['inā',1,1,''],
['īhi',1,1,''],
['hi',0,2,''],
['ībhi',1,1,''],
['bhi',0,1,''],
['ino',1,1,''],
['īnaṁ',1,1,''],
['īsu',1,1,''],
['i',1,2,'i'],
['inaṁ',1,0,''],
['avo',0,1,'u'],
['ave',0,1,'u'],
['ū',1,1,''],
['unā',1,1,''],
['ūhi',1,1,''],
['ūbhi',1,1,''],
['uno',1,1,''],
['ūnaṁ',1,1,''],
['ūsu',1,1,''],
['u',1,2,'u'],
['āni',0,2,'a'],
['īni',1,2,''],
['ūni',1,2,''],
['a',1,2,'a'],
['āyo',0,0,'a'],
['āhi',0,0,'a'],
['ābhi',0,0,'a'],
['āyaṁ',0,0,'a'],
['āsu',0,0,'a'],
['iyo',1,0,''],
['iyā',1,0,''],
['iyaṁ',1,0,''],
['iyā',0,0,'ī'],
['iyaṁ',0,0,'ī'],
['iyaṁ',0,0,'i'],
['āya',0,0,'ī'],
['ī',0,0,'a'],
['inī',0,0,'a'],
['uyo',1,0,''],
['uyā',1,0,''],
['uyaṁ',1,0,''],
['ā',0,3,'ant'],
['a',1,3,'nt'],
['ataṁ',1,3,'nt'],
['antaṁ',1,3,'nt'],
['anto',1,3,'nt'],
['antā',1,3,'nt'],
['ante',1,3,'nt'],
['atā',1,3,'nt'],
['antehi',1,3,'nt'],
['ato',1,3,'nt'],
['antānaṁ',1,3,'nt'],
['ati',1,3,'nt'],
['antesu',1,3,'nt'],
['ā',0,3,'anta'],
['a',1,3,'nta'],
['ataṁ',1,3,'nta'],
['ataṁ',1,3,'ti'],
['antaṁ',1,3,'nta'],
['anto',1,3,'nta'],
['antā',1,3,'nta'],
['ante',1,3,'nta'],
['atā',1,3,'nta'],
['antehi',1,3,'nta'],
['ato',1,3,'nta'],
['antānaṁ',1,3,'nta'],
['ati',1,3,'nta'],
['antesu',1,3,'nta'],
['ā',0,2,'ar'],
['āraṁ',0,2,'ar'],
['ārā',0,2,'ar'],
['u',0,2,'ar'],
['uno',0,2,'ar'],
['ari',0,2,'ar'],
['āro',0,2,'ar'],
['ūhi',0,2,'ar'],
['ūbhi',0,2,'ar'],
['ūnaṁ',0,2,'ar'],
['ārānaṁ',0,2,'ar'],
['ūsu',0,2,'ar'],
['ā',0,2,'ar'],
['a',0,2,'ar'],
['araṁ',0,2,'ar'],
['arā',0,2,'ar'],
['aro',0,2,'ar'],
['unā',0,2,'ar'],
['arehi',0,2,'ar'],
['arebhi',0,2,'ar'],
['ānaṁ',0,2,'ar'],
['arānaṁ',0,2,'ar'],
['unnaṁ',0,2,'ar'],
['ito',0,2,'ar'],
['uyā',0,2,'ar'],
['yā',0,2,'ar'],
['yaṁ',0,2,'ar'],
['uyaṁ',0,2,'ar'],
['aṁ',0,0,'ā'],
['āya',0,0,'ā'],
['asā',0,0,'o'],
['aso',0,0,'o'],
['asi',0,0,'o'],
['ā',0,0,'o'],
['aṁ',0,0,'o'],
['e',0,0,'o'],
['ena',0,0,'o'],
['ehi',0,0,'o'],
['ebhi',0,0,'o'],
['āya',0,0,'o'],
['assa',0,0,'o'],
['ānaṁ',0,0,'o'],
['asmā',0,0,'o'],
['amhā',0,0,'o'],
['asmiṁ',0,0,'o'],
['amhi',0,0,'o'],
['esu',0,0,'o'],
['ato',1,2,'ti'],
['atā',1,2,'ti'],
['ato',1,2,'ati'],
['atā',1,2,'ati'],
['eto',1,2,'ti'],
['etā',1,2,'ti'],
['oto',1,2,'ti'],
['otā',1,2,'ti'],
['ahi',1,1,''],
['to',0,2,''],
['annaṁ',1,1,''],
['unnaṁ',1,1,''],
['innaṁ',1,1,''],
['atā',2,1,'i'],
['iya',0,2,'a'],
['uyaṁ',0,0,''],
['ati',3,0,''],
['āti',3,0,''],
['eti',3,0,''],
['oti',3,0,''],
['anti',1,0,'ti'],
['si',0,3,'ti'],
['asi',1,0,'ti'],
['atha',1,0,'ati'],
['āmi',0,0,'ati'],
['āma',0,0,'ati'],
['āmi',1,0,'ti'],
['āma',1,0,'ti'],
['onti',1,0,'ti'],
['osi',1,0,'ti'],
['otha',1,0,'ti'],
['omi',1,0,'ti'],
['oma',1,0,'ti'],
['enti',1,0,'ti'],
['esi',1,0,'ti'],
['etha',1,0,'ti'],
['emi',1,0,'ti'],
['ema',1,0,'ti'],
['hi',0,3,'ti'],
['atu',1,2,'ti'],
['antu',1,1,'ti'],
['ohi',1,0,'ti'],
['otu',1,0,'ti'],
['ontu',1,0,'ti'],
['etu',1,0,'ti'],
['entu',1,0,'ti'],
['ehi',1,0,'ti'],
['eti',0,2,'ati'],
['enti',0,2,'ati'],
['esi',0,2,'ati'],
['etha',0,2,'ati'],
['emi',0,2,'ati'],
['ema',0,2,'ati'],
['eti',0,2,'āti'],
['enti',0,2,'āti'],
['esi',0,2,'āti'],
['etha',0,2,'āti'],
['emi',0,2,'āti'],
['ema',0,2,'āti'],
['entu',0,2,'ati'],
['ayitvā',0,2,'eti'],
['ayitvāna',0,2,'eti'],
['vāna',0,2,'i'],
['āpetvā',0,0,'ati'],
['itvāna',0,0,'ati'],
['itvāna',0,0,'āti'],
['itvāna',0,0,'eti'],
['etvāna',0,0,'ati'],
['tvāna',0,0,'ti'],
['itvā',0,0,'ati'],
['itvā',0,0,'āti'],
['itvā',0,0,'eti'],
['etvā',0,0,'ati'],
['tvā',0,0,'ti'],
['āya',0,0,'ati'],
['āya',0,0,'ati'],
['āya',0,0,'āti'],
['āya',0,0,'eti'],
['tuṁ',0,0,'ti'],
['ituṁ',0,0,'ati'],
['ituṁ',0,0,'āti'],
['a',0,3,'ati'],
['i',0,3,'ati'],
['imha',0,0,'ati'],
['imhā',0,0,'ati'],
['iṁsu',0,1,'ati'],
['ittha',0,0,'ati'],
['uṁ',0,0,'ati'],
['suṁ',0,0,'ti'],
['siṁ',0,0,'ti'],
['iṁ',0,0,'ati'],
['a',0,3,'āti'],
['i',0,3,'āti'],
['imha',0,0,'āti'],
['imhā',0,0,'āti'],
['iṁsu',0,1,'āti'],
['ittha',0,0,'āti'],
['uṁ',0,0,'āti'],
['iṁ',0,0,'āti'],
['a',0,3,'eti'],
['i',0,3,'eti'],
['imha',0,0,'eti'],
['imhā',0,0,'eti'],
['iṁsu',0,1,'eti'],
['ayiṁsu',0,1,'eti'],
['ittha',0,0,'eti'],
['uṁ',0,0,'eti'],
['iṁ',0,0,'eti'],
['iyaṁ',0,0,'eti'],
['eyya',0,0,'ati'],
['eyyaṁ',0,0,'ati'],
['eyyuṁ',0,0,'ati'],
['eyyati',0,0,'ati'],
['eyyasi',0,0,'ati'],
['eyyātha',0,0,'ati'],
['eyyāmi',0,0,'ati'],
['eyyāsi',0,0,'ati'],
['eyyāma',0,0,'ati'],
['eyyanti',0,0,'ati'],
['eyya',0,0,'āti'],
['eyyaṁ',0,0,'āti'],
['eyyuṁ',0,0,'āti'],
['eyyati',0,0,'āti'],
['eyyasi',0,0,'āti'],
['eyyātha',0,0,'āti'],
['eyyāmi',0,0,'āti'],
['eyyāsi',0,0,'āti'],
['eyyāma',0,0,'āti'],
['eyyanti',0,0,'āti'],
['eyya',1,0,'ti'],
['eyyaṁ',1,0,'ti'],
['eyyuṁ',1,0,'ti'],
['eyyati',1,0,'ti'],
['eyyasi',1,0,'ti'],
['eyyātha',1,0,'ti'],
['eyyāmi',1,0,'ti'],
['eyyāsi',1,0,'ti'],
['eyyāma',1,0,'ti'],
['eyyanti',1,0,'ti'],
['eyya',0,0,'oti'],
['eyyaṁ',0,0,'oti'],
['eyyuṁ',0,0,'oti'],
['eyyati',0,0,'oti'],
['eyyasi',0,0,'oti'],
['eyyātha',0,0,'oti'],
['eyyāmi',0,0,'oti'],
['eyyāsi',0,0,'oti'],
['eyyāma',0,0,'oti'],
['eyyanti',0,0,'oti'],
['issa',0,2,'ati'],
['issā',0,2,'ati'],
['issaṁsu',0,2,'ati'],
['issatha',0,2,'ati'],
['issaṁ',0,2,'ati'],
['issāmi',0,2,'ati'],
['issati',0,3,'ati'],
['issāma',0,2,'ati'],
['issa',0,2,'āti'],
['issā',0,2,'āti'],
['issaṁsu',0,2,'āti'],
['issa',0,2,'āti'],
['issatha',0,2,'āti'],
['issaṁ',0,2,'āti'],
['issāma',0,2,'āti'],
['essa',1,2,'ti'],
['essā',1,2,'ti'],
['essaṁsu',1,2,'ti'],
['essa',1,2,'ti'],
['essatha',1,2,'ti'],
['essaṁ',1,2,'ti'],
['essāma',1,2,'ti'],
['issanti',0,3,'ati'],
]


sc.markupGenerator = {
    paliAlphaRex: /([aiueokgcjtdnpbmyrlvshāīūṭḍṅṇṃñḷ])/i,
    paliRex: /([aiueokgcjtdnpbmyrlvshāīūṭḍṅṇṃñḷ’­”]+)/ig,
    splitRex: /([^  \n,.– —:;?!"'“‘-]+)/,
    defaultExcludeFn: function(node) {
        if (node.parentNode.nodeName == 'A') {
            if ($(node.parentNode).parents('h1,h2,h3,h4,h5').length == 0) {
                return false
            }
            return true
        }
        return false
    },
    wrapWords: function(node, markupOpen, markupClose, excludeFn) {
        var self = this,
            contents = $(node).contents();
        if (excludeFn === undefined) {
            excludeFn = self.defaultExcludeFn;
        }
        $(node).textNodes().each(function(i, node){
            if (excludeFn && excludeFn(node)) {
                return
            }
            var text = node.nodeValue;
            if (text.search(self.paliAlphaRex) == -1) {
                return
            }
            var newHtml = text.replace(self.paliRex, function(m, word) {
                return markupOpen + word + markupClose;
            });
            var proxy = $('<span/>')[0];
            node.parentNode.replaceChild(proxy, node);
            proxy.outerHTML = newHtml;
        });
            
            
        //contents.each(function(i, childNode) {
            //if (childNode.nodeType == document.ELEMENT_NODE) {
                //if (excludeFn && excludeFn(childNode)) {
                    //return
                //}
                //self.wrapWords(childNode, markupOpen, markupClose, excludeFn);
            //} else if (childNode.nodeType == document.TEXT_NODE) {
                //var text = childNode.nodeValue;
                //if (text.search(self.paliAlphaRex) == -1) {
                    //return
                //}
                //var newHtml = text.replace(self.paliRex, function(m, word) {
                    //return markupOpen + word + markupClose;
                //});
                //var proxy = $('<span/>')[0];
                //node.replaceChild(proxy, childNode);
                //proxy.outerHTML = newHtml;
            //}
        //});
    }
}

sc.paliLookup.targets = 'p, h1, h2, h3, h4, h5'
sc.paliLookup.activate = function() {
    var self = this;
    $('#text').on('mouseover.lookupMarkup', self.targets , function(e) {
        
        var target = $(e.target);
        if (!target.is(self.targets)) {
            return true
        }
        if (target.hasClass('lookup-marked-up')) {
            return
        }
        console.log(target);
        
        sc.markupGenerator.wrapWords(target, '<span class="lookup"><span class="lookup-word-marker"></span>', '</span>')
        target.addClass('lookup-marked-up');
    })
    sc.paliLookup.init({elasticUrl: sc.exports.elasticsearch_api_url, target: '.lookup'});
    sc.paliLookup.addHandlers();    
}

sc.paliLookup.deactivate = function() {
    $('#text').off('mouseover.lookupMarkup')
    sc.paliLookup.removeHandlers();
}

sc.paliLookup.toggleOn = false;
sc.paliLookup.toggle = function() {
    var state = !this.toggleOn;
    if (state) {
        this.activate()
    } else {
        this.deactivate()
    }
}
