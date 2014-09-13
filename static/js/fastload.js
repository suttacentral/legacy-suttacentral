sc.fastload = {
    cache: {
        store: (window.sessionStorage !== undefined) ? sessionStorage : {
            object: {},
            setItem: function(key, value) {
                this.object[key] = value;
            },
            getItem: function(key, value) {
                return this.object[key];
            }
        },
        has: function(key) {
            try {
                return 'sc:' + key in this.store;
            } catch (err) {
                return !!this.object.getItem('sc:' + key);
            }
        },
        add: function(key, data) {
            this.store.setItem('sc:' + key, data);
        },            
        retrive: function(key) {
            return this.store.getItem('sc:' + key);
        }
    },
    supports_history_api: function() {
        return !!(window.history && history.pushState);
    },
    valid_link: 'a[href]:not([href^="http://"]):not([href^="#"])',
    init: function init() {
        var self = this;
        if (!this.supports_history_api())
            return

        if (!window.location.origin.match(/https?:\/\//))
            return
        
        $(document.body).on('click',
            self.valid_link,
            this.hrefclick);
        window.addEventListener("popstate", self.goback);
        self.update_cache();
        self.preload();
    },
    hrefclick: function(e){
        console.log('Link clicked');
        e.preventDefault();
        sc.fastload.loadpage($(this).attr('href'), true);        
    },
    update_cache: function() {
        if (!this.cache.has(location.pathname)) {
            this.cache.add(location.pathname, $('#page-main')[0].outerHTML);
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
        if (self.cache.has(href)) {
            // Already in cache, don't bother with ajax request
            update_page(self.cache.retrive(href));
        } else {
            self.do_ajax(href)
                .done(function(data, status, xhr){update_page(data)})
                .fail(function(xhr, status, errorThrown){self.redirect(href)});
        }
    },
    do_ajax: function(href) {
        var qs = '?ajax=';
        if (href.search(/\?/) != -1) {
            qs = '&ajax=';
        }
        return $.ajax(href + qs, {dataType: 'html'})
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
    },
    
    preload: function(e) {
        var self = this;
        self.toLoad = $('[data-preload=1] a, a[data-preload=1]').toArray().reverse();

        function doload(){
            while (true) {
                var e = self.toLoad.pop();
                if (e == undefined) return;
                var href = $(e).attr('href')
                if (!self.cache.has(href))
                    break
            }
            self.do_ajax(href).done(function(data, status, xhr)
            {
                self.cache.add(href, data);
            })
            setTimeout(doload, 1);
        }

        setTimeout(doload, 500);

    } 
}

sc.fastload.init();
