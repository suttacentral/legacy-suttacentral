sc = sc || {};

sc.zh2enLookup = {
    buttonId: "zh2en",
    chineseClasses: "P, H1, H2, H3",
    active: false,
    dictRequested: false,
    chineseIdeographs: /[\u4E00-\u9FCC　。]/g, //CFK Unified Ideographs
    chinesePunctuation: /[　、。]/g,
    loading: false,
    queue: [],
    markupTarget: null,
    originalHTML: null,
    mouseIn: 0,
    currentLookup: null,
    lastCurrentLookup: null,
    baseUrl: $('script[src*="sc_zh2en_lookup.js"]').attr('src').replace('sc_zh2en_lookup.js', ''),
    init: function(insert_button_where, markup_target){
        this.markupTarget = $(markup_target).addClass('zh2enLookup')[0];
        this.markupTarget
        this.insertButton(insert_button_where);
    },
    insertButton: function(insert_where){
        this.button = $('<button id="'+this.buttonId+'">Chinese→English Dictionary</button>')
        $(insert_where).append(this.button);
        $(document).on('click', '#' + this.buttonId, sc.zh2enLookup.toggle);
    },
    ready: function(){
        self = this
        var popup = '<table class="popup"><tr><td><center>Chinese to english lookup activated.</center><tr><td>Use the mouse or left, right arrow keys to navigate the text (shift-right to advance more). <tr><td>A red border indicates modern usage, possibly unrelated to early Buddhist usage.</table>'
        setTimeout(function(){
            popup = self.popup({left:12, top: $(document).scrollTop()+12}, popup);
            popup.select('table').addClass('info')
            }, 250)
        self.currentLookup = $('span.lookup:first')[0];
        self.lastCurrentLookup = self.currentLookup;
            
        console.log('Ready')
    },
    activate: function(){
        var self = this;
        if (!this.originalHTML)
            this.originalHTML = this.markupTarget.innerHTML;
        
        if (!this.dictRequested && !window.zh2en_dict)
        {
            this.dictRequested = true;
            jQuery.getScript(this.baseUrl + 'zh2en_data_0.05.js', self.ready());
            jQuery.getScript(this.baseUrl + 'zh2en_fallback_0.05.js');
        }
        this.generateMarkup();
        $(document).on('mouseenter', 'span.lookup', function(){
            self.mouseIn ++;
        })
        $(document).on('mouseleave', 'span.lookup', function(){
            self.mouseIn --;
        })
        $(document).on('keyup', '', function(e){
            if (!self.mouseIn)
                return
            if (e.keyCode == 39 || e.keyCode == 37)
                e.preventDefault();
            if (e.keyCode == 39) {
                var next = nextInOrder(e.shiftKey ? self.lastCurrentLookup : self.currentLookup, 'span.lookup');
                if (!next)
                    return
                self.setCurrent(next)
            } else if (e.keyCode == 37){
                var prev = previousInOrder(self.currentLookup, 'span.lookup');
                if (!prev)
                    return
                self.setCurrent(prev);
            }
        });
    },
    deactivate: function(){
        this.markupTarget.innerHTML = this.originalHTML;
    },
    generateMarkup: function() {
        if (this.button)
            this.button.attr('disabled', 'disabled');
        this.markupGenerator.start();
        $(document).on('mouseenter', 'span.lookup', sc.zh2enLookup.lookupHandler);
    },
    markupGenerator: {
        //Applies markup incrementally to avoid a 'browser stall'
        start: function(){
            this.node = sc.zh2enLookup.markupTarget;
            this.startTime = Date.now();
            this.step();
        },
        step: function(){
            for (var i = 0; i < 10; i++){
                if (this.node === undefined) {
                    this.andfinally();
                    return;
                }
                var nextNode = nextInOrder(this.node, document.TEXT_NODE)
                this.textNodeToMarkup(this.node);
                this.node = nextNode;
            }
            setTimeout('sc.zh2enLookup.markupGenerator.step.call(sc.zh2enLookup.markupGenerator)', 5);
        },
        andfinally: function(){
            self = sc.zh2enLookup;
            console.log('Done');
            if (self.button)
                self.button.removeAttr('disabled');
            
        },
        textNodeToMarkup: function(node) {
            if (node === undefined) return;
            var text = node.nodeValue;
            if (!text || text.search(sc.zh2enLookup.chineseIdeographs) == -1){
                return
            }
            var proxy = document.createElement("span");
            node.parentNode.replaceChild(proxy, node);
            proxy.outerHTML = this.toLookupMarkup(text);
        },
        toLookupMarkup: function(input)
        {
            var self = sc.zh2enLookup,
                chinesePunctuation = self.chinesePunctuation;
            
            return input.replace(self.chineseIdeographs, function(ideograph){
                var eclass = 'lookup';
                if (chinesePunctuation.test(ideograph))
                    eclass += ' punctuation';
                return '<span class="' + eclass +'">' + ideograph + '</span>'
            });
        }
    },
    toggle: function(){
        self = sc.zh2enLookup;
        self.active = !self.active;
        if (self.active) self.activate()
        else self.deactivate();
    },
    setCurrent: function(node) {
        var self=this,
            graphs = '',
            nodes = $(),
            iter = new Iter(node),
            i
        $('.popup').remove()
        $('.current_lookup').removeClass('current_lookup fallback')
        this.currentLookup = node
        while (graphs.length < 10) {
            if ($(node).is('span.lookup')) {
                graphs += $(node).text();
                nodes.push(node)
            }
            node = nextInOrder(node, document.ELEMENT_NODE)
            if (!node) {
                break
            }
        }
        
        if (!graphs)
            return

        var popup = ['<table class="popup">'],
            first = true,
            fallback = false;
        for (i = graphs.length; i > 0; i--) {
            var snip = graphs.slice(0, i)
            if (snip in zh2en_dict) {
                popup.push(self.lookupWord(snip))
                if (first) {
                    first = false;
                    nodes.slice(0, i).addClass('current_lookup')
                    this.lastCurrentLookup = nodes[i-1];
                }
            } else if (i == 1 && snip in zh2en_fallback) {
                popup.push(self.lookupWord(snip))
                popup[0] = '<table class="popup fallback">'
                fallback = true
                if (first) {
                    first = false;
                    nodes.slice(0, i).addClass('current_lookup fallback')
                    this.lastCurrentLookup = nodes[i-1];
                }
            }
        }
        if (first)
            return

        popup.push('</table>')

        popup = self.popup(nodes[0], popup.join('\n'))
    },
    lookupHandler: function(e){
        sc.zh2enLookup.setCurrent(e.target);
    },
    lookupWord: function(graph){
        //Check if word exists and return HTML which represents the meaning.
        var out = "";
        graph = graph.replace(/\u2060/, '');
        if (zh2en_dict[graph])
        {
            var href = "http://www.buddhism-dict.net/cgi-bin/xpr-ddb.pl?q=" + encodeURI(graph);
            return ('<tr><td class="ideograph"><a href="' + href + '">' + graph + '</a></td> <td class="meaning"> ' + zh2en_dict[graph][0] + ': ' + zh2en_dict[graph][1] + '</td></tr>');
        } else if (zh2en_fallback[graph]) {
            return ('<tr class="fallback"><td class="ideograph"><a>' + graph + '</a></td> <td class="meaning"> ' + zh2en_fallback[graph][0] + ': ' + zh2en_fallback[graph][1] + '</td></tr>')

        }
        return "";
    },
    popup: function(parent, popup) {
        var offset, docWith, dupe, docWidth, isAbsolute = false
        if ('left' in parent || 'top' in parent) {
            offset = parent
            offset.left = offset.left || 0
            offset.top = offset.top || 0
            parent = document.body
            isAbsolute = true

        } else {
            parent = $(parent)
            offset = parent.offset()
        }
        popup = $(popup)

        //We need to measure the doc width now.
        docWidth = $(document).width()
        // We need to create a dupe to measure it.
        dupe = $(popup).clone()
            
        $(this.markupTarget).append(dupe)
        var popupWidth = dupe.innerWidth(),
            popupHeight = dupe.innerHeight();
        dupe.remove()
        //The reason for the duplicity is because if you realize the
        //actual popup and measure that, then any transition effects
        //cause it to zip from it's original position...
        if (!isAbsolute) {
            offset.top += parent.innerHeight() - popupHeight - parent.outerHeight();
            offset.left -= popupWidth / 2;
        }

        if (offset.left < 1) {
            offset.left = 1;
            popup.innerWidth(popupWidth + 5);
        }
        
        if (offset.left + popupWidth + 5 > docWidth)
        {
            offset.left = docWidth - (popupWidth + 5);
        }
        popup.offset(offset)
        $(this.markupTarget).append(popup)
        popup.offset(offset)

        popup.mouseleave(function(e){$(this).remove()});
        
        return popup;
    }
}