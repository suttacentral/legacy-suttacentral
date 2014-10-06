sc.fastload = {
    cache: {
        store: sessionStorage,
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
        return !!(window.sessionStorage && window.history && history.pushState);
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
        e.preventDefault();
        sc.fastload.loadpage($(this).attr('href'), true);        
    },
    update_cache: function() {
        if (!this.cache.has(location.pathname)) {
            this.cache.add(location.pathname, $('main')[0].outerHTML);
        }
    },
    loadpage: function(href, change_state, state) {
        var self = this;
        // For closure
        function update_page(data) {
            var title = $('meta[name=title]').attr('content');
            $('main')[0].outerHTML = data;
            $('title').text(title);
            if (change_state) {
                history.pushState({scrollY: document.body.scrollY, scrollX: document.body.scrollX}, null, href);
            }
            
            // If Google Universal Analytics is activated, we better
            // send a pageview
            if ('ga' in window) {
                ga('send', 'pageview', {'page': href, 'title': title + ' -- ajax load'});
            }
            self.update_cache();
            self.preload();
            document.body.scrollX = state ? state.scrollX : 0;
            document.body.scrollY = state ? state.scrollY : 0;
            sc.headerMenu.deactivate();
            
            onMainLoad();
        }
        if (self.cache.has(href)) {
            // Already in cache, don't bother with ajax request
            update_page(self.cache.retrive(href));
        } else {
            self.do_ajax(href)
                .done(function(data, status, xhr){update_page(data)})
                .fail(function(xhr, status, errorThrown){console.log('Fail: ' + status); return;self.redirect(href)});
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
        window.location.replace(href);
    },
    goback: function(e) {
        var self = sc.fastload;
        self.loadpage(location.pathname, false, e.state)
    },
    preload_timeout_id: null,
    preload: function(toLoad) {
        var self = this;
        self.toLoad = $('[data-prefetch] a, a[data-prefetch]').toArray().reverse();

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
                $(data).preload
            })
            self.preload_timeout_id = setTimeout(doload, 1);
        }
        clearTimeout(self.preload_timeout_id)
        self.preload_timeout_id = setTimeout(doload, 100);

    } 
}

sc.fastload.init();
