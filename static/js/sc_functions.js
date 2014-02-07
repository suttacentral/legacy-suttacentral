/* All code here is free to use any purpose. If you wish to make use
 * of it, please feel free to contact me at
 * bhante.nandiya@gmail.com
 * I would be happy to help if I am able.
 */

"use strict";

function E(nodeName, text) {
    var e = document.createElement(nodeName);
    if (text) e.appendChild(T(text));
    return e;
}
function T(arg) { return document.createTextNode(arg) }

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
/*
var chineseLookup = {
    buttonId: "zh2en",
    chineseClasses: "P, H1, H2, H3",
    activate: function(){
        textualControls.disable();
        if (!this.dictRequested)
        {
            this.dictRequested = true;
            if (scPersistantStorage.check('zh2en_dict', sc.zh2en_dict_url))
            {
                scMessage.show("Retrieving Chinese Dictionary from local storage …", 100000);
                window.zh2en_dict = scPersistantStorage.retrive('zh2en_dict', sc.zh2en_dict_url);
                chineseLookup.generateMarkup();
                scMessage.show("Hover with the mouse to display meaning.<br> Click a compound to break it up.", 10000);
                return
            }
            if (!window.zh2en_dict) {
                scMessage.show("Requesting Chinese Dictionary, this may take some time...", 1000000);
                jQuery.getScript(sc.zh2en_dict_url, function() {
                    scMessage.show("Analyzing Text...", 2000);
                    chineseLookup.generateMarkup();
                    scMessage.show("Hover with the mouse to display meaning.<br> Click a compound to break it up.", 10000);
                    scPersistantStorage.store('zh2en_dict', window.zh2en_dict, sc.zh2en_dict_url)
                    return
                });
            }
        }
        if (window.zh2en_dict) this.generateMarkup();
    }

}*/

sc.zh2enLookup = {
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
    baseUrl: $('script[src*="sc_functions"]').attr('src').replace('sc_functions.js', ''),
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
            if (/^[^\u4E00-\u9FCC]*$/.test(text)) return; //No chinese
            var proxy = document.createElement("span");
            node.parentNode.replaceChild(proxy, node);
            proxy.outerHTML = this.toLookupMarkup(text);
        },
        toLookupMarkup: function(input)
        {
            var self = this,
                out = "",
                parts = input.match(sc.zh2enLookup.chineseSplitRex);
            parts.push("")
            for (var i = 0; i < parts.length; i++) {
                if (!sc.zh2enLookup.chineseIdeographs.test(parts[i])){//tag or puncuation
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
        $(this.markupTarget).append(popup)
        popup.offset(offset)

        popup.mouseleave(function(e){$(this).remove()});
        
        return popup;
    }
}

//Used for rollback and caching.
var scState = {
    _target: (function(){
        if ($("#text").length) return $("#text")[0];
        if ($("#onecol").length) return $("#onecol")[0];
        if ($("#home").length) return $("#home")[0];
        if ($("body section").length) return $("body section")[0];
        throw "Error!";
    }) (),
    save: function(state) {
        if (typeof this[state] == "function") throw new Error("Invalid state name!");
        this[state] = this._target.innerHTML;
    },
    set: function(state, html) {
        if (typeof this[state] == "function") throw new Error("Invalid state name!");
        if (!html) throw new TypeError;
        this._target.innerHTML = html;
        this.save("state")
    },
    restore: function(state) {
        if (typeof this[state] == "function") throw new Error("Invalid state name!");
        if (!this[state]) throw new Error("State not saved!");
        this._target.innerHTML = this[state];
    },
    getHTML: function(state) {
        if (typeof this.state == "function") throw new Error("Invalid state name!");
        if (!this[state]) throw new Error("State not saved!");
        return this[state];
    },
    exists: function(state) {
        if (typeof this.state == "function") throw new Error("Invalid state name!");
        return !!this[state];
    }
}

var scPersistantStorage = {
    database: function() {
        //Database should define five methods:
        //add, get, check, remove and purge
        //If version is passed, the return will only be positive if the
        //passed version matches the stored version for that key.
        if (!('localStorage' in window)) return null;
        var lsdb = {
            add: function(key, data, version) {
                if (!version) version = "";
                localStorage[key] = data;
                localStorage[key + '.version'] = version;
            },
            get: function(key, version)
            {
                //Retrive an item from localstorage
                if (!version) version = "";
                if (localStorage[key + '.version'] == version)
                    return localStorage[key];
                else
                    this.clear(key);
            },
            check: function(key, version)
            {
                if (!version) version = "";
                return (key in localStorage && localStorage[key + '.version'] == version)
            },
            remove: function(key)
            {
                localStorage.removeItem(key);
                localStorage.removeItem(key + '.version');
            },
            purge: function()
            {
                localStorage.clear();
            }
        }
        return lsdb;
    } (),
    store: function(key, data, version){
        if (!this.database) return false;
        this.database.add(key, JSON.stringify(data), version);
    },
    retrive: function(key, version) {
        if (!this.database) return false;
        return JSON.parse(this.database.get(key, version));
    },
    check: function(key, version) {
        if (!this.database) return false;
        return this.database.check(key, version);
    }
}
        

//The code below here is quite disorganized and messy relative to the chineseLookup above.

//Rewriting it is on the to-do.

function togglePaliLookup(){
    toggleLookupOn = !sc.userPrefs.getPref("paliLookup");
    scMessage.clear();
    sc.userPrefs.setPref("paliLookup", toggleLookupOn, true);
}

function transliterateHandler()
{
    sc.userPrefs.setPref("script", this.id, true);
}

function toggleTextualInfo(force) {
    var showTextInfo = sc.userPrefs.getPref("textInfo");
    showTextInfo = !showTextInfo;

    if (force === true) {showTextInfo = true;}
    else if (force === false) {showTextInfo = false;}

    if (showTextInfo)
    {
        //The tlinehead thing is a nasty little bodge to cull the excessive
        //numbers of that type.
        $(textualControls.marginClasses).not('.tlinehead:odd').addClass("infomode");
        $(textualControls.popupClasses).addClass("infomode");
        $(textualControls.contentClasses).addClass("infomode");
        var meta = $(textualControls.metaarea)[0];
        if (meta.innerHTML) {
            var content = false;
            for (var i = 0; i < meta.childNodes.length; i++)
            {
                var child = meta.childNodes[i]
                if (child.nodeType == 3) {
                    if (child.nodeValue.trim()){
                        content = true;
                        break;
                    }
                } else if (child.nodeType == 1) {
                    //console.log(child);
                    if ($(child).not(".hidden").length > 0){
                        content = true;
                        break;
                    }
                }
            }
            if (content){
                //console.log('Content found');
                $(meta).addClass("infomode");
            }
        }
    } else {
        $(textualControls.marginClasses).removeClass("infomode")
        $(textualControls.popupClasses).removeClass("infomode")
        $(textualControls.contentClasses).removeClass("infomode")
        $(textualControls.metaarea).removeClass("infomode")
    }
    sc.userPrefs.setPref("textInfo", showTextInfo, false);
}

function bindButtons(){
     document.getElementById(textInfoButtonId).onclick = toggleTextualInfo;
     if (sc.mode.pali === true){
        document.getElementById(paliLookupButtonId).onclick = togglePaliLookup;

        for (f in transFuncs) {
            try {
                document.getElementById(f).onclick = transliterateHandler;
            } catch (e) {/*If button doesn't exist.*/}
        }
    }
}

function buildTextualInformation() {
    var anchors = $(textualControls.marginClasses);
    for (var i = 0; i < anchors.length; i++) {
        var a = anchors[i];
        var da = $(a);

        var aClass = a.className.split(' ')[0];
        var title = sc.mode[sc.mode.lang]["strings"][aClass];
        $(a).attr("title", title);
        var aid = da.attr('id');
        
        if (aClass == 'ms') {
            $(a).text( aid.replace(/p_([0-9A-Z]+)_([0-9]+)/, "$1:$2."))
        } else if (aClass == 'vnS') {
            $(a).text(aid.replace(/S.([iv]+),([0-9])/, "S $1 $2"))
        } else if (aClass == 'pts_pn'){
            var m = aid.split('.')
            m[0] = m[0].toUpperCase();
            $(a).text( m.join('.') )
        }
        
        if (da.text() == '') {
            da.text(aid.replace(/\d+_/, '').replace(aClass+'_', ''));
        }
        if (!da.attr('href') && aid) {
            da.attr('href', '#' + aid);
        }

        a.innerHTML = a.innerHTML.replace(/(\d)-(\d)/, '$1\u2060—\u2060$2')
    }
    var das = $('a.da');
    for (i = 0; i < das.length; i += 3)
        das[i].innerHTML = das[i].id;
    buildVariantNotes();
    $("#metaarea a").filter(textualControls.marginClasses).each(function(){this.className = ""; this.innerHTML = ""});
    $(textualControls.titleClasses).each(function(){
        var class_ = this.className.split(' ')[0];
        $(this).attr("title", sc.mode[sc.mode.lang]["strings"][class_])
    });


}

function buildVariantNotes(){
    var notes = $(textualControls.popupClasses);

    for (var i = 0; i < notes.length; i++)
    {
        var mula = notes[i].getAttribute("data-mula");
        var content = notes[i].getAttribute("data-content");
        if (!mula || !content) continue;
        $(notes[i]).append($('<span class="deets">'+content+'</span>'));
    }
}

//Transliteration functions//
/* Note that the object 'transFuncs' must be defined */

var wordMap = {};
var reverseMap = {};

function toSyllablesInit(){
    $(".sutta P, .sutta H1, .sutta H2, .sutta H3").addClass('syllables');
    return;
}
        

function transliterate(func){
    if (func == toMyanmar) {
        $('#text').attr('lang', 'my');
    } else {
        // TODO other languages
        $('#text').attr('lang', 'pi');
    }
    if (func == toSyllables) {
        toSyllablesInit();
        $('.syllables').each(function(){
            toSyllablesIteratively(this)
        });
        return;
    }
    var classes = $(".sutta P, .sutta H1, .sutta H2, .sutta H3")
    for (var i = 0; i < classes.length; i++) {
        convertIteratively(classes[i], func);
    }
    if (func == toMyanmar) {
        // This is to handle a strange artifact in Chrome.
        var evam = $('#text .evam')[0];
        if (evam) {
            var textNode = evam.nextSibling;
            if (textNode) {
                var text = textNode.textContent;
                text = text.replace(/^\s+/, '');
                textNode.textContent = text;
            }
        }
    }
}

function convertIteratively(startNode, func) {
    var node, it = new Iter(startNode, 'text'), type, name, text;
    while (node = it.next())
    {
        if (node.parentNode.nodeName == 'A')
            if (node.parentNode.parentNode.nodeName[0] != 'H')
                continue;
        text = node.nodeValue.replace(/\&nbsp;/g,' ');;
        if (!(/^\s*$/).test(text)){
            if (func != toRoman && func != toSyllables) {
                node.nodeValue = transliterateString(text, func);
            }
        }
    }
    return
}

function toRoman(input){return input}//Presently roman is default.

var anychar = /[aiueokgcjtdnpbmyrlvshāīūṭḍṅṇṃṁñḷ]/i;
var syllabousRex = (function(){
    //Construct an enourmous regular expression which devours an entire paragraph and poops it out as syllables
    //In english, a pali syllable may be described as 'Zero or more consonants, a single vowel (no dipthongs in pali),
    //then optionally a consonant which ends the word, or a consonant which starts a cluster.
    //The complexity is mainly dealing with aspiration (am-ha is correct, a-bha is correct)
    //Mk2
    var cons = "(?:br|[kgcjtṭdḍbp]h|[kgcjtṭdḍp](?!h)|[mnyrlvshṅṇṃṁñḷ]|b(?![rh]))";
    var vowel = "(?:[aiueoāīū])";
    var other = "[^aiueokgcjtdnpbmyrlvshāīūṭḍṅṇṃṁñḷ]";
    return RegExp(cons + '*' + vowel + '(?:' + cons + '(?!' + vowel + '))?' + '|' + other, 'gi')

    var other = "[^aiueokgcjtdnpbmyrlvshāīūṭḍṅṇṃṁñḷ]";
    var cons = "[kgcjtdnpbmyrlvshṭḍṅṇṃṁñḷ]"
    return RegExp('('+cons+'*[aiueoāīū]('+cons+'(?='+other+')|[yrlvshṅṁñ](?=h)|' + cons + '(?!h)' + '(?='+cons+'))?'+')|('+other+'+)', 'gi');})();

//(Defining this outside the function saves 10% runtime).


function toSyllables(input){
    var out = "";
    var parts = input.match(syllabousRex);
    if (parts)
        for (var i = 0; i < parts.length; i++)
        {
            //All valid syllables in pali must contain a vowel
            if (anychar.test(parts[i]))
            {
                if ((/[aiu]$/i).test(parts[i])) {out += parts[i]}
                else {out += "<u>" + parts[i] + "</u>"};
                if (parts[i+1] && (/[aiueoāīū]/i).test(parts[i+1]))
                    out += syllSpacer;
            } else
                out += parts[i];
        }
    return out
}
    
function toSyllablesIteratively(node){
    var it = new Iter(node, 'text'), input, i, parts, out, proxy;
    while (node = it.next())
    {
        parent = node.parentNode;
        if (parent.nodeName == 'A') continue;
        input = node.nodeValue.replace(/­/g, ''); //Optional Hyphen
        out = toSyllables(input)
        proxy = E('span')
        parent.insertBefore(proxy, node);
        node.nodeValue = '';
        proxy.outerHTML = out;
        //XHTML code - but it runs much slower on all browsers except Chrome
        /*parent = node.parentNode;
        if (parent.nodeName == 'A') continue;
        //node.parentNode.replaceChild(tmp, node);
        parts = node.nodeValue.replace(/­/g, '').match(syllabousRex);
        if (parts && parts.length)
        for (i = 0; i < parts.length; i++) {
            if (anychar.test(parts[i])) {
                if (/[aiu]$/i.test(parts[i])) {
                    text += parts[i];
                } else {
                    if (text) {
                        parent.insertBefore(T(text), node);
                        text = "";
                    }
                    parent.insertBefore(E('u', parts[i]), node);
                }
                if (parts[i+1] && (/[aiueoāīū]/i).test(parts[i+1]))
                    text += syllSpacer;
            } else {
                text += parts[i];
            }
        }
        if (text) {
            parent.insertBefore(T(text), node);
            text = "";
        }
        parent.removeChild(node)*/
    }
}

function transliterateWord(word, func) {
    var script = func.name
    //Caching makes no performance difference for Chrome, but Firefox is faster.
    //However the reverse cache is very useful because it enables word lookup in roman.
    if (func.name == 'toSyllables')
        return func(word);
    
    word = word.toLowerCase().replace(/ṃ/g, 'ṁ');
    if (!wordMap[script][word]) {
        wordMap[script][word] = func(word)
        reverseMap[wordMap[script][word]] = word
    }
    return wordMap[script][word];
}

function transliterateString(input, func) {
    var splitRex = RegExp('[^aiueokgcjtdnpbmyrlvshāīūṭḍṅṇṁñḷ]+|[aiueokgcjtdnpbmyrlvshāīūṭḍṅṇṁñḷ]+', 'gi');
    var output = "";
    input = input.replace(/\&quot;/g, '`').toLowerCase();
    var parts = input.match(splitRex);
    for (var i in parts) {
        var word = parts[i];
        if (anychar.test(word))
        {
            output += transliterateWord(word, func)
        }
        else {
            output += parts[i];
        }
    }
    output = output.replace(/\`+/g, '"');
    return output;
}
//Minified because these are lengthy functions.
function toSinhala(l){
    l = l.toLowerCase() + " ";
var m={a:"අ","ā":"ආ",i:"ඉ","ī":"ඊ",u:"උ","ū":"ඌ",e:"එ",o:"ඔ"};
var b={"ā":"ා",i:"ි","ī":"ී",u:"ු","ū":"ූ",e:"ෙ",o:"ො","ṁ":"ං",k:"ක",g:"ග","ṅ":"ඞ",c:"ච",j:"ජ","ñ":"ඤ","ṭ":"ට","ḍ":"ඩ","ṇ":"ණ",t:"ත",d:"ද",n:"න",p:"ප",b:"බ",m:"ම",y:"ය",r:"ර",l:"ල","ḷ":"ළ",v:"ව",s:"ස",h:"හ"};
var j={kh:"ඛ",gh:"ඝ",ch:"ඡ",jh:"ඣ","ṭh":"ඨ","ḍh":"ඪ",th:"ථ",dh:"ධ",ph:"ඵ",bh:"භ","jñ":"ඥ","ṇḍ":"ඬ",nd:"ඳ",mb:"ඹ",rg:"ඟ"};
var a={k:"ක",g:"ග","ṅ":"ඞ",c:"ච",j:"ජ","ñ":"ඤ","ṭ":"ට","ḍ":"ඩ","ṇ":"ණ",t:"ත",d:"ද",n:"න",p:"ප",b:"බ",m:"ම",y:"ය",r:"ර",l:"ල","ḷ":"ළ",v:"ව",s:"ස",h:"හ"};
var k,g,f,e,d;var c="";var h=0;while(h<l.length){k=l.charAt(h-2);g=l.charAt(h-1);
f=l.charAt(h);e=l.charAt(h+1);d=l.charAt(h+2);if(m[f]){if(h==0||g=="a"){c+=m[f]}else{if(f!="a"){c+=b[f]
}}h++}else{if(j[f+e]){c+=j[f+e];h+=2;if(a[d]){c+="්"}}else{if(b[f]&&f!="a"){c+=b[f];
h++;if(a[e]&&f!="ṁ"){c+="්"}}else{if(!b[f]){if(a[g]||(g=="h"&&a[k])){c+="්"}c+=f;
h++;if(m[e]){c+=m[e];h++}}else{h++}}}}}if(a[f]){c+="්"}c=c.replace(/ඤ්ජ/g,"ඦ");c=c.replace(/ණ්ඩ/g,"ඬ");
c=c.replace(/න්ද/g,"ඳ");c=c.replace(/ම්බ/g,"ඹ");c=c.replace(/්ර/g,"්ර");c=c.replace(/\`+/g,'"');
return c.slice(0, -1)}
function toMyanmar(k){k=k.toLowerCase() + " ";var m={a:"အ",i:"ဣ",u:"ဥ","ā":"အာ","ī":"ဤ","ū":"ဦ",e:"ဧ",o:"ဩ"};
var l={i:"ိ","ī":"ီ",u:"ု","ū":"ူ",e:"ေ","ṁ":"ံ",k:"က",kh:"ခ",g:"ဂ",gh:"ဃ","ṅ":"င",c:"စ",ch:"ဆ",j:"ဇ",jh:"ဈ","ñ":"ဉ","ṭ":"ဋ","ṭh":"ဌ","ḍ":"ဍ","ḍh":"ဎ","ṇ":"ဏ",t:"တ",th:"ထ",d:"ဒ",dh:"ဓ",n:"န",p:"ပ",ph:"ဖ",b:"ဗ",bh:"ဘ",m:"မ",y:"ယ",r:"ရ",l:"လ","ḷ":"ဠ",v:"ဝ",s:"သ",h:"ဟ"};
var a={k:"က",g:"ဂ","ṅ":"င",c:"စ",j:"ဇ","ñ":"ဉ","ṭ":"ဋ","ḍ":"ဍ","ṇ":"ဏ",t:"တ",d:"ဒ",n:"န",p:"ပ",b:"ဗ",m:"မ",y:"ယ",r:"ရ",l:"လ","ḷ":"ဠ",v:"ဝ",s:"သ",h:"ဟ"};
var n={kh:"1",g:"1",d:"1",dh:"1",p:"1",v:"1"};var j,f,e,d,c;var b="";var g=0;k=k.replace(/\&quot;/g,"`");
var h=false;while(g<k.length){j=k.charAt(g-2);f=k.charAt(g-1);e=k.charAt(g);d=k.charAt(g+1);
c=k.charAt(g+2);if(m[e]){if(g==0||f=="a"){b+=m[e]}else{if(e=="ā"){if(n[h]){b+="ါ"
}else{b+="ာ"}}else{if(e=="o"){if(n[h]){b+="ေါ"}else{b+="ော"}}else{if(e!="a"){b+=l[e]
}}}}g++;h=false}else{if(l[e+d]&&d=="h"){b+=l[e+d];if(c!="y"&&!h){h=e+d}if(a[c]){b+="္"
}g+=2}else{if(l[e]&&e!="a"){b+=l[e];g++;if(d!="y"&&!h){h=e}if(a[d]&&e!="ṁ"){b+="္"
}}else{if(!l[e]){b+=e;g++;if(m[d]){if(m[d+c]){b+=m[d+c];g+=2}else{b+=m[d];g++}}h=false
}else{h=false;g++}}}}}b=b.replace(/ဉ္ဉ/g,"ည");b=b.replace(/္ယ/g,"ျ");b=b.replace(/္ရ/g,"ြ");
b=b.replace(/္ဝ/g,"ွ");b=b.replace(/္ဟ/g,"ှ");b=b.replace(/သ္သ/g,"ဿ");b=b.replace(/င္/g,"င်္");
return b.slice(0, -1)}
function toDevar(l){l=l.toLowerCase() + " ";var m={a:" अ",i:" इ",u:" उ","ā":" आ","ī":" ई","ū":" ऊ",e:" ए",o:" ओ"};
var n={"ā":"ा",i:"ि","ī":"ी",u:"ु","ū":"ू",e:"े",o:"ो","ṁ":"ं",k:"क",kh:"ख",g:"ग",gh:"घ","ṅ":"ङ",c:"च",ch:"छ",j:"ज",jh:"झ","ñ":"ञ","ṭ":"ट","ṭh":"ठ","ḍ":"ड","ḍh":"ढ","ṇ":"ण",t:"त",th:"थ",d:"द",dh:"ध",n:"न",p:"प",ph:"फ",b:"ब",bh:"भ",m:"म",y:"य",r:"र",l:"ल","ḷ":"ळ",v:"व",s:"स",h:"ह"};
var k,h,g,f,e,d,b;var c="";var a=0;var j=0;l=l.replace(/\&quot;/g,"`");while(j<l.length){k=l.charAt(j-2);
h=l.charAt(j-1);g=l.charAt(j);f=l.charAt(j+1);e=l.charAt(j+2);d=l.charAt(j+3);b=l.charAt(j+4);
if(j==0&&m[g]){c+=m[g];j+=1}else{if(f=="h"&&n[g+f]){c+=n[g+f];if(e&&!m[e]&&f!="ṁ"){c+="्"
}j+=2}else{if(n[g]){c+=n[g];if(f&&!m[f]&&!m[g]&&g!="ṁ"){c+="्"}j++}else{if(g!="a"){if(a[h]||(h=="h"&&a[k])){c+="्"
}c+=g;j++;if(m[f]){c+=m[f];j++}}else{j++}}}}}if(a[g]){c+="्"}c=c.replace(/\`+/g,'"');
return c.slice(0, -1)}
function toThai(m){m=m.toLowerCase() + " ";var n={a:"1","ā":"1",i:"1","ī":"1","iṁ":"1",u:"1","ū":"1",e:"2",o:"2"};
var j={a:"อ","ā":"า",i:"ิ","ī":"ี","iṁ":"ึ",u:"ุ","ū":"ู",e:"เ",o:"โ","ṁ":"ํ",k:"ก",kh:"ข",g:"ค",gh:"ฆ","ṅ":"ง",c:"จ",ch:"ฉ",j:"ช",jh:"ฌ","ñ":"","ṭ":"ฏ","ṭh":"","ḍ":"ฑ","ḍh":"ฒ","ṇ":"ณ",t:"ต",th:"ถ",d:"ท",dh:"ธ",n:"น",p:"ป",ph:"ผ",b:"พ",bh:"ภ",m:"ม",y:"ย",r:"ร",l:"ล","ḷ":"ฬ",v:"ว",s:"ส",h:"ห"};
var a={k:"1",g:"1","ṅ":"1",c:"1",j:"1","ñ":"1","ṭ":"1","ḍ":"1","ṇ":"1",t:"1",d:"1",n:"1",p:"1",b:"1",m:"1",y:"1",r:"1",l:"1","ḷ":"1",v:"1",s:"1",h:"1"};
var l,h,g,f,e,d,b;var c="";var k=0;m=m.replace(/\&quot;/g,"`");while(k<m.length){l=m.charAt(k-2);
h=m.charAt(k-1);g=m.charAt(k);f=m.charAt(k+1);e=m.charAt(k+2);d=m.charAt(k+3);b=m.charAt(k+4);
if(n[g]){if(g=="o"||g=="e"){c+=j[g]+j.a;k++}else{if(k==0){c+=j.a}if(g=="i"&&f=="ṁ"){c+=j[g+f];
k++}else{if(g!="a"){c+=j[g]}}k++}}else{if(j[g+f]&&f=="h"){if(e=="o"||e=="e"){c+=j[e];
k++}c+=j[g+f];if(a[e]){c+="ฺ"}k=k+2}else{if(j[g]&&g!="a"){if(f=="o"||f=="e"){c+=j[f];
k++}c+=j[g];if(a[f]&&g!="ṁ"){c+="ฺ"}k++}else{if(!j[g]){c+=g;if(a[h]||(h=="h"&&a[l])){c+="ฺ"
}k++;if(f=="o"||f=="e"){c+=j[f];k++}if(n[f]){c+=j.a}}else{k++}}}}}if(a[g]){c+="ฺ"
}c=c.replace(/\`+/g,'"');return c.slice(0, -1);};

//Pali lookup functions//
function generateLookupMarkup(){
    //We want to wrap every word in a tag.
    var classes = ".sutta P, .sutta H1, .sutta H2, .sutta H3"
//     $(marginInfoClasses).html('');
//     $("span.deets").remove();
//     $(textInfoClasses).replaceWith(function(){$(this).text()});
    generateMarkupCallback.nodes = $(classes).toArray();
    generateMarkupCallback.start = Date.now();
    textualControls.disable()
    generateMarkupCallback();
//     buildTextualInformation();
    return;
}

function generateMarkupCallback() {
    var node = generateMarkupCallback.nodes.shift();
    if (!node) {
        textualControls.enable();
        return}
    toLookupMarkup(node);
    setTimeout(generateMarkupCallback, 5);
}

var paliRex = /([aiueokgcjtdnpbmyrlvshāīūṭḍṅṇṁñḷ’­”]+)/i;
var splitRex = /([^  ,.– —:;?!"'“‘-]+)/;
function toLookupMarkup(startNode)
{
    var parts, i, out = "", proxy, node;
    var it = new Iter(startNode, 'text');
    while (node = it.next()) if (node.nodeValue) {
        if (node.parentNode.nodeName == 'A')
            if (node.parentNode.parentNode.nodeName[0] != 'H')
                continue;
        out = "";
        parts = node.nodeValue.split(splitRex);
        for (i = 0; i < parts.length; i++) {
            if (i % 2 == 1) {// Word
                var word = parts[i]
                if (sc.mode.translitFunc.name != 'toRoman')
                    word = transliterateWord(word, sc.mode.translitFunc);
                if (node.parentNode.nodeName != 'A')
                    out += '<span class="lookup">' + word + '</span>'
                else
                    out += word
            } else { //Non-word
                out += parts[i];
            }
        }
        proxy = E('span');
        node.parentNode.replaceChild(proxy, node);
        proxy.outerHTML = out;
    }
}

var G_uniRegExpNSG = /[–   :;?!,.“‘]+/gi;
var toggleLookupOn = false;
var paliDictRequested = false;
var pi2en_dict = null;
function enablePaliLookup(){
    $(document).on('mouseenter', 'span.lookup', lookupWordHandler);
    if (!pi2en_dict)
    {
        if (scPersistantStorage.check('pi2en_dict', sc.pi2en_dict_url))
        {
            scMessage.show("Retrieving Pali Dictionary from local storage …", 100000);
            pi2en_dict = scPersistantStorage.retrive('pi2en_dict', sc.pi2en_dict_url);
            generateLookupMarkup();
            scMessage.show("Dictionary Enabled. Hover with the mouse to display meaning.", 10000);
            return
        } else {
            scMessage.show("Requesting Pali Dictionary...", 10000);
            jQuery.getScript(sc.pi2en_dict_url, function(){
                scPersistantStorage.store('pi2en_dict', pi2en_dict, sc.pi2en_dict_url);
                generateLookupMarkup();
                scMessage.show("Dictionary Enabled. Hover with the mouse to display meaning.", 10000);
                return
            });
        }
    } else
        generateLookupMarkup();
}

function lookupWordHandler(event){
    if (!sc.userPrefs.getPref("paliLookup")) return;
    if (! 'paliDictionary' in window) return;

    if ($(this).children().is("span.meaning")) return;

    var word = $(this).text().toLowerCase().trim();
    word = word.replace(/­/g, '').replace(RegExp(syllSpacer, 'g'), '');//optional hyphen, syllable-breaker

    if (reverseMap[word]) {
        meaning += word + " : ";
        word = reverseMap[word];
    }
    word = word.replace(/ṁg/g, 'ṅg').replace(/ṁk/g, 'ṅk').replace(/ṃ/g, 'ṁ').replace(/Ṃ/g, 'Ṁ');
    var meaning = lookupWord(word);
    if (meaning) {
        var textBox = $('<span class="meaning">'+meaning+'</span>');
        $(this).append(textBox);
        sc.formatter.rePosition(textBox);
    }
}

function lookupWord(word){

    var allMatches = [];

    var isTi = false;
    if (word.match(/[’”]ti$/)) {
        isTi=true;
        word = word.replace(/[’”]ti$/, "");
    }
    word = word.replace(/[’”]/g, "");
    var original = word;
    var unword = null; //The un-negated version.

    //First we try to match the word as-is
    var m = matchComplete(word, {"ti":isTi});
    if (!m || m.length == 0) {
        if (word.search(/^an|^a(.)\1/) != -1) unword = word.substring(2, word.length)
        else if (word.search(/^a/) != -1) unword = word.substring(1, word.length);
        if (unword) {
            m = matchComplete(unword, {"ti":isTi});
            if (m && m.length > 0)
            {
                allMatches.push({"base":"an", "meaning":"non/not"});
            }
        }
    }
    if (m && m.length > 0)
    {
        allMatches = allMatches.concat(m);
    }


    if (allMatches.length == 0)
    {
        //Now we attempt to break up the compound.
        //First is special case since 'an' is possibility.
        var m = matchPartial(word);
        if (unword)
        {
            var unm = matchPartial(unword);
            if ((unm && !m) || (unm && m && unm.base.length > m.base.length)) {
                m = unm;
                allMatches.push({"base":"an", "meaning":"non/not"});
            }
        }
        var foundComplete = false;
        while (m && !foundComplete)
        {
            allMatches = allMatches.concat(m);
            var leftover = m.leftover;
            var sandhi = m.base[m.base.length - 1];
            var firstchar = leftover[0];
            leftover = leftover.substring(1, leftover.length);
            var starts = [firstchar, "", sandhi + firstchar];
            var vowels = ['a', 'ā', 'i', 'ī', 'u', 'ū', 'o', 'e'];
            //As a rule sandhi doesn't shortern vowels
            if (sandhi == 'a' || sandhi == 'i' || sandhi == 'u') vowels = ['a', 'i', 'u'];
            for (i in vowels) starts.push(vowels[i] + firstchar);
            var foundComplete = false;
            for (i in starts)
            {
                m = matchComplete(starts[i] + leftover, {"ti":isTi});
                if (m && m.length > 0) {
                    allMatches =  allMatches.concat(m);
                    foundComplete = true;
                    break;
                }
                m = matchPartial(starts[i] + leftover);
                if (m) break;
            }
            if (!m)
            {
                allMatches.push({"base":firstchar + leftover, "meaning":"?"});
                break;
            }
        }
        //In the long run it would be nice to implement 'two ended candle' match.
    }

    var out = "";
    if (allMatches.length == 0)
    {
        allMatches.push({"base":original, "meaning":"?"});
    }
    if (isTi) allMatches.push({"base":"iti", "meaning":"endquote"});
    for (var i in allMatches) {
        var href = "http://dsal.uchicago.edu/cgi-bin/philologic/search3advanced?dbname=pali&searchdomain=headwords&matchtype=start&display=utf8&query=" + allMatches[i].base;
        
        out += '<a href="'+href+'">' + allMatches[i].base + '</a>: ' + allMatches[i].meaning;
        if (i != allMatches.length - 1)
        {
            out += " + ";
        }
    }
    return out;
}

function matchComplete(word, args){
    var matches = [];
    for (var pi = 0; pi < 2; pi++) // 'pi (list)
        for (var vy = 0; vy < 2; vy++) // vy / by (burmese)
                for (var ti = 0; ti < 2; ti++) // 'ti (end quote)
    {
        //On the first pass change nothing.
        var wordp = word;
        //On the second pass we change the last vowel if 'ti', otherwise skip.
        if (ti && args.ti == true)
        {

            wordp = wordp.replace(/ī$/, "i").replace(/ā$/, "i").replace(/ū$/, "i").replace(/n$/, "").replace(/n$/, "ṁ");
        }
        if (pi)
        {
            if (wordp.search(/pi$/) == -1) continue;
            wordp = wordp.replace(/pi$/, "");
        }
        if (vy)
        {
            if (wordp.match(/vy/)) wordp = wordp.replace(/vy/g, 'by')
            else if (wordp.match(/by/)) wordp = wordp.replace(/by/g, 'vy')
            else continue;
        }

        var m = exactMatch(wordp) || fuzzyMatch(wordp);
        if (m) {
            matches.push(m);
            if (pi) matches.push({"base":"pi", "meaning":"too"});
            return matches;
        }
    }

    return null;
}

function matchPartial(word, maxlength){
    //Matching partials is somewhat simpler, since all ending cases are clipped off.
    for (var vy = 0; vy < 2; vy++)
    {
        var wordp = word;
        if (vy)
        {
            if (wordp.match(/vy/)) wordp = wordp.replace(/vy/g, 'by')
            else if (wordp.match(/by/)) wordp = wordp.replace(/by/g, 'vy')
            else continue;
        }

        if (!maxlength) maxlength = 4;
        for (var i = 0; i < word.length; i++){
            var part = word.substring(0, word.length - i);
            if (part.length < maxlength) break;
            if(typeof(pi2en_dict[part]) == 'object') {
                var meaning = pi2en_dict[part][1];
                return {"base":part, "meaning": meaning, "leftover": word.substring(word.length - i, word.length)}
            }
        }
    }
}
//Every match function should return an object containing:
// "base": The base text being matched
// "meaning": The meaning of the matched text.
// "leftovers": Anything which wasn't matched by the function, should be empty string
//  or null if meaningless (such as a grammatical insertion ie. 'ti')

function exactMatch(word)
{
    if(typeof(pi2en_dict[word]) == 'object') {
        var meaning = pi2en_dict[word][1]+' ('+pi2en_dict[word][0]+')';
        return {"base": word, "meaning": meaning};
    }
    return null;
}

function fuzzyMatch(word){
    var end = pi2en_dict._end;
    for(var i = 0; i < end.length; i++) {
        if(word.length > end[i][2] && word.substring(word.length - end[i][0].length, word.length) === end[i][0]) {
            var orig = word.substring(0,word.length - end[i][0].length + end[i][1]) + end[i][3];
            if(typeof(pi2en_dict[orig]) == 'object') {
                var meaning = pi2en_dict[orig][1] + ' ('+pi2en_dict[orig][0]+')';
                return {"base": orig, "meaning": meaning};
            }
        }
    }
    return null;
}

function timeit(command, times){
    if (!times) times = 10000;
    var start = (new Date()).getTime();
    for (var i = 0; i < times; i++)
        command();
    return ((new Date()).getTime() - start)
}

function timeprecision(delay, times){
    if (!times) times = 1000;
    timeprecision.times = times;
    timeprecision.results = [];
    timeprecision.delay = delay;
    timeprecision.callback();
}
timeprecision.callback = function(){
    timeprecision.results.push(Date.now());
    if (timeprecision.times-- <= 0) {
        timeprecision.andfinally();
        return;
    }
    setTimeout(timeprecision.callback, timeprecision.delay);
}
timeprecision.andfinally = function(){
    var freq = {};
    var results = timeprecision.results;
    for (var i = results.length; i > 0; i--)
    {
        var diff = results[i] - results[i - 1]
        if (diff in freq) {freq[diff]++}
        else freq[diff] = 1;
    }
    //console.log(freq);
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

function FreeIter(node, permissables) {
    //FreeIter is an ultra lightweight iterator that traverses the entire
    //document, starting (not including) 'node', in forward or reverse.
    //next/previous ALWAYS use the live state of the node.
    this.permissables = _IterPermissions(permissables);
    this.current = node;
}

FreeIter.prototype = {
    current: undefined,
    next: function(node){
        var node = this.current;
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
        this.current = node;
        if (!this.permissables)
            return node;
        if (this.permissables.indexOf(node.nodeType) != -1)
            return node;
        return this.next();
    },
    previous: function(node){
        var node = this.current;
        if (node.previousSibling) {
            node = node.previousSibling;
            while (node.lastChild)
                node = node.lastChild;
        } else if (node.parentNode) {
            node = node.parentNode;
        } else {
            return undefined;
        }
        this.current = node;
        if (!this.permissables)
            return node;
        if (this.permissables.indexOf(current.nodeType) != -1)
            return node;
        return this.previous();
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
    if (typeof permissables == 'number') {
        if (node.nodeType == permissables)
            return node;
    }
    else if (permissables.indexOf(node.nodeType) != -1)
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
    if (typeof permissables == 'number') {
        if (node.nodeType == permissables)
            return node;
    }
    else if (permissables.indexOf(node.nodeType) != -1)
        return node;
    return previousInOrder(node, permissables);
}