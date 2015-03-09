// AJAX search results.

sc.search = {
    search_element: $('#page-header-search > input'),
    lastXHR: null,
    oldMain: null,
    dropDown: $(),
    latestSearchTimeoutId: null,
    init: function() {
        sc.search.search_element.keyup(sc.search.handleSearch);
    },
    clear: function() {
        this.dropDown.empty();
    },
    handleSearch: function(e) {
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
        
        
        if (self.dropDown.length == 0) {
            self.dropDown = $('<div id="autocomplete-dropdown"></div>')
                            .appendTo('header')
                            .hide()
                            .on('click', 'span', function(){
                                self.search_element.val($(this).text().toLowerCase())
                                                   .focus();
                                self.dropDown.hide()
                            });
        }
        self.dropDown.empty();
        
        if (results.total == 0) {
            self.dropDown.hide()
            return
        }
        var ul = $('<ul></ul>').appendTo(self.dropDown);
        $(results.hits).each(function(i, hit) {
            var langs = ['en', 'pi', 'en-dict', 'suttas'];
            if (hit.lang != 'en' && hit.lang != 'pi') {
                langs.push(hit.lang);
            }
            
            $('<a class="suggestion"/>')
                .appendTo($('<li/>').appendTo(ul))
                .text(hit.value)
                .attr('title', hit.lang)
                .attr('href', '/search?' + $.param({query: hit.value,
                                                     lang: langs.join(',')}))
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
