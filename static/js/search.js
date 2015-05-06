// AJAX search results.

sc.search = {
    search_element: $('#page-header-search > input'),
    lastXHR: null,
    oldMain: null,
    dropDown: $(),
    latestSearchTimeoutId: null,
    init: function() {
        sc.search.search_element.on('keyup focus', sc.search.handleSearch);

/* DS START Local Debug - remove when working */
// self.dropDown = $('<div id="autocomplete-dropdown"><ul><li><a class="suggestion" title="it" href="/search?query=testimone+fisico&amp;lang=en%2Cpi%2Cit&amp;define=1&amp;details=1">Testimone fisico</a></li><li><a class="suggestion" title="es" href="/search?query=testigo+ocular+del+cuerpo&amp;lang=en%2Cpi%2Ces&amp;define=1&amp;details=1">Testigo ocular del cuerpo</a></li><li><a class="suggestion" title="de" href="/search?query=geistestr%C3%BCbungen&amp;lang=en%2Cpi%2Cde&amp;define=1&amp;details=1">Geistestrübungen</a></li><li><a class="suggestion" title="sr" href="/search?query=pore%C4%91enje+sa+testerom&amp;lang=en%2Cpi%2Csr&amp;define=1&amp;details=1">Poređenje sa testerom</a></li><li><a class="suggestion" title="cs" href="/search?query=rozprava+o+%C5%A1t%C4%9Bst%C3%AD&amp;lang=en%2Cpi%2Ccs&amp;define=1&amp;details=1">Rozprava o štěstí</a></li><li><a class="suggestion" title="en" href="/search?query=the+greatest+good+fortune&amp;lang=en%2Cpi&amp;define=1&amp;details=1">The Greatest Good Fortune</a></li><li><a class="suggestion" title="hu" href="/search?query=besz%C3%A9d+a+test+tudatos%C3%ADt%C3%A1s%C3%A1r%C3%B3l&amp;lang=en%2Cpi%2Chu&amp;define=1&amp;details=1">Beszéd a test tudatosításáról</a></li><li><a class="suggestion" title="fr" href="/search?query=le+r%C3%A9cit+de+l%E2%80%99incontestable&amp;lang=en%2Cpi%2Cfr&amp;define=1&amp;details=1">Le récit de l’incontestable</a></li><li><a class="suggestion" title="no" href="/search?query=helvetestrusler+er+ikke+veien+%C3%A5+g%C3%A5&amp;lang=en%2Cpi%2Cno&amp;define=1&amp;details=1">Helvetestrusler er ikke veien å gå</a></li><li><a class="suggestion" title="es" href="/search?query=discurso+sobre+los+test%C3%ADculos+como+olla&amp;lang=en%2Cpi%2Ces&amp;define=1&amp;details=1">Discurso sobre los testículos como olla</a></li></ul></div>')
//                 .hide()
//                 .appendTo('header');
/* DS END Local Debug - remove when working */

    },
    clear: function() {
        this.dropDown.empty();
    },
    handleSearch: function(e) {

/* DS START Local Debug - remove when working */
// $('#panel-screen-wrap').addClass('active');
// dropDown.show();
/* DS END Local Debug - remove when working */

        var self = sc.search,
            query = e.target.value;
        //console.log(query);
        if (sc.search.lastXHR) {
            sc.search.lastXHR.abort();
        }
        if (query.length < 3) {
            self.clear();
        } else {
            var params = {'query': query,
                          'lang': sc.intr.lang,
                          'autocomplete': 1 }
            var url = "/search?" + $.param(params),
                ajax = jQuery.ajax(url, { "cache": false});
            ajax.done(self.done);
            ajax.error(self.error);
            sc.search.lastXHR = ajax;
        }
    },
    done: function(data, code, jqXHR) {
        var self = sc.search,
            url = this.url;

        results = JSON.parse(data);
        console.log(results);
        
/* DS START Local Debug - comment this out when testing */
        if (self.dropDown.length == 0) {
            self.dropDown = $('<div id="autocomplete-dropdown"></div>')
                            .appendTo('header')
                            .hide()
                            .on('click', '.suggestion', function(e){
                                self.search_element.val($(e.target).text().toLowerCase())
                                                   .focus();
                            });
            self.search_element.on('blur', function(){self.dropDown.delay(50).slideUp(); return false});
        }
        self.dropDown.empty();
/* DS END Local Debug - comment this out when testing */

        
        if (results.total == 0) {
            self.dropDown.slideUp()
            return
        }
        var ul = $('<ul></ul>').appendTo(self.dropDown);
        $(results.hits).each(function(i, hit) {
            var langs = ['en', 'pi'];
            if (hit.lang != 'en' && hit.lang != 'pi') {
                langs.push(hit.lang);
            }
            
            $('<a class="suggestion"/>')
                .appendTo($('<li/>').appendTo(ul))
                .text(hit.value)
                .attr('title', hit.lang)
                .attr('href', '/search?' + $.param({query: hit.value.toLowerCase(),
                                                    lang: langs.join(','),
                                                    define: 1,
                                                    details: 1}))
        });
        self.dropDown.show();
    },
    error: function(query, data, code, jqXHR) {
        return
    },
    addCloseButton: function(e){
        var close = $('<div class="close-button">×</div>');
        close.click(sc.search.restoreMain);
        e.prepend(close);
    }
};

sc.search.init();
