/* Standalone chinese to english lookup
 * Note that this requires:
 *   zh2en_data.js
 *   zh2en.css
 *
 * These do NOT need to be included in the html file,
 * since zh2en.js will automagically inject them, but both
 * files must be present in the same folder as zh2en.js.
 * (If you do include them manually, no harm will be done)
 *
 * zh2en lookup also requires jQuery, but will also attempt to inject
 * jQuery - since it (obviously) can't use jQuery to do this, browser
 * compatibility is much less guaranteed.
 * 
 * To use:
 * Simply include '<script src="zh2en/zh2en.js"></script>' somewhere in the
 * file you want to use the lookup dictionary in (modify the src accordinging
 * to relative location).
 */

"use strict";

if (!window.jQuery) (function(){
    //Attempt to inject jQuery
    var i, baseUrl,
        scripts = document.getElementsByTagName('script')
    for (var i = 0; i < scripts.length; i++) {
        var src = scripts[i].src
            baseUrl = src.replace('zh2en.js', '')
        document.write('<script src="'+baseUrl + 'jquery-1.9.1.min.js"></script>')
        console.log("Injected jquery");
        //We now need to reload this file, since it depends heavily
        //on jQuery to do anything more.
        document.write('<script src="' + src + '"></script>')
        return
    }
})();

$(document).ready(function(){
    $.ajaxSetup({'crossDomain':true});
    //Inject stylesheet url
    if ($('link[href*="zh2en.css"]').length == 0)
        $('body').append('<link rel="stylesheet" href="' + zh2en.baseUrl + 'zh2en.css">')
    //Insert the button.
    zh2en.init()
    //zh2en.insertButton('body')
    zh2en.activate()
});

var scMessage = {
    messageBox: $('<div id="message_box"></div>').insertAfter("header").hide(),
    show: function(html, delay){
        this.messageBox.clearQueue();
        this.messageBox.html(html).show().delay(delay).fadeOut();
    },
    clear: function(){
        this.messageBox.clearQueue();
        this.messageBox.fadeOut();
    }
}

//Cache Everything.
$.ajaxSetup({
    cache: true
});

var zh2en = {
    buttonId: "zh2en",
    chineseClasses: "P, H1, H2, H3",
    active: false,
    dictRequested: false,
    chineseIdeographs: /([\u4E00-\u9FCC])/g, //CFK Unified Ideographs
    chineseSplitRex: /[\u4E00-\u9FCC]{1,15}|[^\u4E00-\u9FCC]+|./g,
    loading: false,
    queue: [],
    markupTarget: null,
    originalHTML: null,
    mouseIn: 0,
    currentLookup: null,
    lastCurrentLookup: null,
    baseUrl: $('script[src*="zh2en"]').attr('src').replace('zh2en.js', ''),
    init: function(insert_where){
        this.markupTarget = document.body
    },
    insertButton: function(insert_where){
        this.button = $('<button id="'+this.buttonId+'">Chinese→English Dictionary</button>')
        $(insert_where).prepend(this.button);
        $(document).on('click', '#' + this.buttonId, function(){zh2en.toggle()});
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
            jQuery.getScript(this.baseUrl + 'zh2en_data.js', self.ready());
            jQuery.getScript(this.baseUrl + 'zh2en_fallback.js');
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
        $(document).on('mouseenter', 'span.lookup', zh2en.lookupHandler);
    },
    markupGenerator: {
        //Applies markup incrementally to avoid a 'browser stall'
        start: function(){
            this.node = zh2en.markupTarget;
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
            setTimeout('zh2en.markupGenerator.step.call(zh2en.markupGenerator)', 5);
        },
        andfinally: function(){
            if (this.button)
                zh2en.button.removeAttr('disabled');
            
        },
        textNodeToMarkup: function(node) {
            if (node === undefined) return;
            var text = node.nodeValue;
            if (/^[^\u4E00-\u9FCC]*$/.test(text)) return; //No chinese
            var proxy = document.createElement("span");
            node.parentNode.replaceChild(proxy, node);
            proxy.outerHTML = this.toLookupMarkup(text);
        },
        toLookupMarkup: function(input)
        {
            var self = this,
                out = "",
                parts = input.match(zh2en.chineseSplitRex);
            parts.push("")
            for (var i = 0; i < parts.length; i++) {
                if (!zh2en.chineseIdeographs.test(parts[i])){//tag or puncuation
                    out += parts[i];
                } else {
                    out += parts[i].replace(/[\u4E00-\u9FCC]/g, function(ideograph){
                        return '<span class="lookup">' + ideograph + '</span>'
                    });
                }
            }
            return out;
        }
    },
    toggle: function(){
        this.active = !this.active;
        if (this.active) this.activate()
        else this.deactivate();
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
        zh2en.setCurrent(e.target);
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
            
        $(document.body).append(dupe)
        var popupWidth = dupe.innerWidth(),
            popupHeight = dupe.innerHeight();
        dupe.remove()
        //The reason for the duplicity is because if you realize the
        //actual popup and measure that, then any transition effects
        //cause it to zip from it's original position...
        if (!isAbsolute) {
            offset.top += parent.innerHeight() - 4;
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
        $(document.body).append(popup)
        popup.offset(offset)

        popup.mouseleave(function(e){$(this).remove()});
        
        return popup;
    }
}



function _IterPermissions(permissables){
    if (!permissables)
        return undefined;
    var tmp = [];
    if (permissables.indexOf('element') != -1)
        tmp.push(1);
    if (permissables.indexOf('text') != -1)
        tmp.push(3);
    if (permissables.indexOf('comment') != -1)
        tmp.push(8);
    if (permissables.indexOf('document') != -1)
        tmp.push(9);
    if (tmp.length > 0)
        return tmp;
}

function Iter(node, permissables){
    //Iterates in-order over the subtree headed by 'node'
    //permissables should be a string containing one or more of
    //"element, text, comment, document"
    //This iter is suitable for inserting/appending content to the
    //current node - the inserted content will not be iterated over.
    this.permissables = _IterPermissions(permissables);
    this.next_node = node;
}
Iter.prototype = {
    next_node: undefined,
    stack: [],
    permissables: null,
    next: function(){
        var current = this.next_node;
        if (current === undefined) return undefined;
        if (current.firstChild) {
            this.stack.push(this.next_node);
            this.next_node = this.next_node.firstChild;
        }
        else if (this.next_node.nextSibling) {
            this.next_node = this.next_node.nextSibling;
        }
        else {
            while (this.stack.length > 0)
            {
                var back = this.stack.pop();
                if (back.nextSibling)
                {
                    this.next_node = back.nextSibling;
                    break;
                }
            }
            if (this.stack.length == 0) this.next_node = undefined;
        }
        if (!this.permissables)
            return current;
        if (this.permissables.indexOf(current.nodeType) != -1)
            return current;
        
        return this.next()
    }
}

function nextInOrder(node, permissables) {
    //Get the next node in 'natural order'
    if (node.firstChild) {
        node = node.firstChild;
    }
    else if (node.nextSibling) {
        node = node.nextSibling;
    }
    else {
        while (true){
            node = node.parentNode;
            if (!node) {
                return undefined;
            }
            if (node.nextSibling) {
                node = node.nextSibling;
                break;
            }
        }
    }

    if (typeof permissables == 'string') {
        if (node.nodeType == 1 && $(node).is(permissables))
            return node;
    } else if (typeof permissables == 'number') {
        if (node.nodeType == permissables)
            return node;
    } else if (permissables.indexOf(node.nodeType) != -1)
        return node;
    return nextInOrder(node, permissables);
}

function previousInOrder(node, permissables) {
    //Get previous node in 'natural order'
    if (node.previousSibling) {
        node = node.previousSibling;
        while (node.lastChild)
            node = node.lastChild;
    } else if (node.parentNode) {
        node = node.parentNode;
    } else {
        return undefined;
    }
    if (!permissables)
        return node;
    if (typeof permissables == 'string') {
        if (node.nodeType == 1 && $(node).is(permissables))
            return node;
    } else if (typeof permissables == 'number') {
        if (node.nodeType == permissables)
            return node;
    } else if (permissables.indexOf(node.nodeType) != -1)
        return node;
    return previousInOrder(node, permissables);
}
