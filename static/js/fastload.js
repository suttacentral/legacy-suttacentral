sc.fastload = {
    cache: (window.sessionStorage !== undefined) ? sessionStorage : {
        store = {},
        getItem: function(key) {
            return key in this.store
        },
        setItem: function(key, value) {
            this.store[key] = value
        }
    }
    supports_history_api: function() {
        return !!(window.history && history.pushState);
    },
    init: function init() {
        var self = this;
        if (!this.supports_history_api())
            return

        if (!window.location.origin.match(/https?:\/\//))
            return
        
        $(document.body).on('click',
            'a[href]:not([href^="http://"]):not([href^="#"])',
            this.hrefclick);
        window.addEventListener("popstate", self.goback);
        self.update_cache();
    },
    hrefclick: function(e){
        console.log('Link clicked');
        e.preventDefault();
        sc.fastload.loadpage($(this).attr('href'), true);        
    },
    update_cache: function() {
        if (!this.store.has(location.pathname)) {
            this.store.add(location.pathname, $('#page-main')[0].outerHTML);
        }
    },
    loadpage: function(href, change_state) {
        var self = this;
        // For closure
        function update_page(data) {
            console.log('Updating page');
            
            $('#page-main').replaceWith(data);
            $('title').text($('meta[name=title]').attr('content'));
            if (change_state) {
                history.pushState(null, null, href);
            }
            
            // If Google Universal Analytics is activated, we better
            // send a pageview
            if ('ga' in window) {
                ga('send', 'pageview', {'page': href});
            }
            self.update_cache();
        }
        console.log('Loading page');
        if ('sc:' + href in self._state_cache) {
            // Already in cache, don't bother with ajax request
            update_page(self._state_cache['sc:' + href]);
        } else {
            var qs = '?ajax=';
            if (href.search(/\?/) != -1) {
                qs = '&ajax=';
            }
            $.ajax(href + qs, {dataType: 'html'})
                .done(function(data, status, xhr){update_page(data)})
                .fail(function(xhr, status, errorThrown){self.redirect(href)});
        }
    },
    redirect: function redirect(href) {
        alert('Redirecting!')
        return
        window.location.replace(href);
    },
    goback: function(e) {
        var self = sc.fastload;
        console.log('Going back to ' + location.pathname);
        console.log('Location in cache? ' + (location.pathname in self._state_cache))
        console.log(e);
        self.loadpage(location.pathname)
    }
}

sc.fastload.init();
