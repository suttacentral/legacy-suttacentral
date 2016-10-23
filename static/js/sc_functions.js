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

//Rewriting it is on the to-do.

sc.piLookup = {
    scripts: [
        {
            lang: 'en',
            name: 'English',
            scriptUrl: 'data/pi2en-maindata-v1.js'
        }, 
        {
            lang: 'de',
            name: 'Deutsch',
            scriptUrl: 'data/pi2de-maindata-v1.2.js'
        }, 
        {
            
            lang: 'es',
            name: 'Español',
            scriptUrl: 'data/pi2es-maindata-v1.js'
        }, 
        {
            lang: 'pt',
            name: 'Português',
            scriptUrl: 'data/pi2pt-maindata-v1.2.js'
        },
        {
            lang: 'id',
            name: 'Bahasa Indonesia',
            scriptUrl: 'data/pi2id-maindata-v1.js'
        }, 
        {
            lang: 'nl',
            name: 'Nederlands',
            scriptUrl: 'data/pi2nl-maindata-v1.js'
        }
    ],
    dataByName: {},
    data: null,     
    register: function(json) {
        this.dataByName[json.script] = json.data;
    },
    init: function(){
        self = this;
        var lang = self.lang || window.localStorage.getItem('sc.piLookup.lang');
        if (!lang) {
            lang = sc.intr.lang;
            if (!lang || _.indexOf(_.pluck(self.scripts, 'lang')) == -1) {
                lang = self.scripts[0].lang;
            }
        }
        self.lang = lang;
        self.makeControls();
        
        $('#pali-lookup-controls').on('click', '[data-lang]', _.bind(this.buttonHandler, this));
    },
    makeButton: function(script) {
        return $('<a class="dropdown-button">')
                    .attr('data-lang', script.lang)
                    .text('Pāli → ' + script.name)
                    .addClass('lookup-inactive');
    },
    makeButtons: function() {
        self.buttons = [];
        _.each(self.scripts, function(script) {
            var button = self.makeButton(script);
            script.button = button;
            self.buttons[script.lang] = button;
        })
    },
    makeControls: function() {
        var self = this,
            selectorId = 'pali-lookup-selector',
            $controls = $('#pali-lookup-controls');
        
        $controls.addClass("x2 button-row");
        $controls.empty();
        
        self.makeButtons();
        
        var $prime = $('<div class="button prime"/>').append(self.buttons[self.lang]),
            $selector = $('<a class="button">Lookup Language ▼</a>'),
            $dropdown = $('<div class="dropdown dropdown-relative"/>').attr('id', selectorId),
            $dropdownPanel = $('<div class="dropdown-panel">').appendTo($dropdown);
        
        _.each(self.scripts, function(script) {
            if (script.lang != self.lang) {
                $dropdownPanel.append(script.button);
            }
        });
        
        $controls.append($selector);
        $controls.append($prime);
        $controls.append($dropdown);
        $selector.attr('data-dropdown', '#' + selectorId)
                 .dropdown('attach', '#' + selectorId);
    },
    setLang: function(lang) {
        this.lang = lang;
        window.localStorage.setItem('sc.piLookup.lang', lang);
    },
    buttonHandler: function(e) {
        var $button = $(e.target),
            lang = $button.attr('data-lang'),
            self = sc.piLookup;
        if (lang != self.lang) {
            self.setLang($button.attr('data-lang'));
            self.makeControls();
            self.togglePaliLookup(true);
        } else {
            self.togglePaliLookup();
        }
    },
    enablePaliLookup: function() {
        var self = this;
        $(document).on('mouseenter', 'span.lookup', lookupWordHandler);

        /* Contains language-neutral information on declensions and
         * conjugations */
        if (!sc.piLookup.endings) {
            jQuery.ajax({
                url: sc.jsBaseUrl + 'data/pi-endings-v1.js',
                dataType: "script",
                success: function() {
                    self.endings = self.dataByName['endings'];                    
                },
                crossDomain: true,
                cache: true
            });
        }
        
        if (!self.dataByName[self.lang]) {
            
            sc.sidebar.messageBox.clear();
            sc.sidebar.messageBox.show("Requesting Pali Dictionary…", {id: "msg-request-dict", timeout: null});
        
            jQuery.ajax({
                url: sc.jsBaseUrl + self.scriptsByName[self.lang].scriptUrl,
                dataType: "script",
                success: function() {
                    self.ready();
                    sc.sidebar.messageBox.remove("msg-request-dict");
                },
                crossDomain: true,
                cache: true
            });
        } else {
            self.ready();
        }
    },
    ready: function() {
        var self = sc.piLookup;
        self.data = self.dataByName[self.lang];
        generateLookupMarkup();
        sc.sidebar.messageBox.show("The lookup dictionary is now enabled. Hover with the mouse to display the meaning.", {id: "msg-lookup-success"});
        $('.lookup-active').removeClass('lookup-active').addClass('lookup-inactive');
        $('.prime .dropdown-button').removeClass('lookup-inactive').addClass('lookup-active');
    },
    togglePaliLookup: function(force) {
        var toggleLookupOn;
        if (force === undefined) {
            toggleLookupOn = !sc.userPrefs.getPref("paliLookup");
        } else {
            toggleLookupOn = force
        }
        sc.sidebar.messageBox.clear();
        sc.userPrefs.setPref("paliLookup", toggleLookupOn, true);
        if (toggleLookupOn == false) {
            sc.sidebar.messageBox.show('The lookup dictionary is now disabled.', {timeout: 5000});
            $('.prime .lookup-active').removeClass('lookup-active').addClass('lookup-inactive');
        }
    }
}
sc.piLookup.scriptsByName = _.object(_.map(sc.piLookup.scripts, function(o){return [o.lang, o]}));
$(document).ready(function(){
    sc.piLookup.init();
});



function transliterateHandler()
{
    sc.userPrefs.setPref("script", this.id, true);
}

function toggleTextualInfo() {
    var showTextInfo = sc.userPrefs.getPref("textInfo");
    showTextInfo = !showTextInfo;
    if ($('body').hasClass('infomode')) {
        showTextInfo = false;
    } else {
        showTextInfo = true;
    }

    // if (force === true) {showTextInfo = true;}
    // else if (force === false) {showTextInfo = false;}

    if (showTextInfo)
    {
        $(document.body).addClass("infomode");
        localStorage.setItem('infomode.on', true);
    } else {
        $(document.body).removeClass("infomode");
        localStorage.removeItem('infomode.on');
    }
    sc.userPrefs.setPref("textInfo", showTextInfo, false);
    sc.text_image.init();
}

function buildTextualInformation() {
    var marginClasses = sc.classes.margin,
        idRex,
        idRepl;
    for (var marginClass in sc.classes.margin) {
        var elements = $('.' + marginClass);
        if (elements.length == 0) {
            continue
        }
        var title = sc.classes.margin[marginClass];
        if (title) {
            elements.attr("title", title);
        }
        if (marginClass == 'ms') {
            idRex = /p_([0-9A-Z]+)_([0-9]+)/;
            idRepl = "$1:$2";
        } else if (marginClass == 'vnS') {
            idRex = /S.([iv]+),([0-9])/;
            idRepl = "S $1 $2";
        }
        else if (marginClass == 'pts1' || marginClass == 'pts2') {
            idRex = RegExp('^pts', 'i');
            idRepl = '';
        } else {
            idRex = RegExp('^' + marginClass, 'i');
            idRepl = '';
        }
        elements.each(function(){
            var id = $(this).attr('id');
            if (!id) {
                return
            }
            if ($(this).text() == '') {
                $(this).text(id.replace(/^\d+_/, '')
                               .replace(idRex, idRepl)
                               .replace(/(\d)-(\d)/, '$1\u2060–\u2060$2'));
            }
        });

    }

    var tes = $('.t, .t-linehead');
    if (tes.length) {
        var uid = $('section.sutta').attr('id'),
            volPrefix = null;

        var prefixes = Object.keys(sc.volPrefixMap).sort(function(a,b){return a.length < b.length});
        for (var i = 0; i < prefixes.length; i++) {
            var prefix = prefixes[i];
            // Rewrite rex
            var m = RegExp('^' + prefix + '(?![a-z])\\.?(\\d*)').exec(uid);
            if (m) {
                
                var number = m[1],
                    volData = sc.volPrefixMap[prefix];
                if (typeof(volData) == 'string') {
                    volPrefix = volData;
                } else {
                    for (j = 0; j < volData.length; j++) {
                        var from = volData[i][0],
                            to = volData[i][1],
                            value = volData[i][2]
                        if (from <= number && number <= to) {
                            volPrefix = value;
                            break
                        }
                    }
                }
                if (volPrefix) {
                    break
                }
            }

        }

        if (volPrefix !== null) {
            tes.each(function(){
                $(this).text(volPrefix + ' ' + $(this).text());
            });
        }
    }

    $('#text a[id]:not([href])').each(function(){
        $(this).attr('href', '#' + $(this).attr('id'));
    });

    for (var contentClass in sc.classes.content) {
        $('.' + contentClass).attr('title', sc.classes.content[contentClass]);
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
    if (!wordMap[func.name]) wordMap[func.name] = {};

    
    if (func == toMyanmar) {
        $('#text').attr('lang', 'pi-Mymr');
    }
    else if (func == toThai) {
        $('#text').attr('lang', 'pi-Thai');
    }
    else if (func == toSinhala) {
        $('#text').attr('lang', 'pi-Sinh');
    }
    else if (func == toDevar) {
        $('#text').attr('lang', 'pi-Deva');
    }
    else {
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

var anychar = /[aiueokgcjtdnpbmyrlvshāīūṭḍṅṇṃṃñḷ]/i;
var syllabousRex = (function(){
    //Construct an enourmous regular expression which devours an entire paragraph and poops it out as syllables
    //In english, a pali syllable may be described as 'Zero or more consonants, a single vowel (no dipthongs in pali),
    //then optionally a consonant which ends the word, or a consonant which starts a cluster.
    //The complexity is mainly dealing with aspiration (am-ha is correct, a-bha is correct)
    //Mk2
    var cons = "(?:br|[kgcjtṭdḍbp]h|[kgcjtṭdḍp](?!h)|[mnyrlvshṅṇṃṃñḷ]|b(?![rh]))";
    var vowel = "(?:[aiueoāīū])";
    var other = "[^aiueokgcjtdnpbmyrlvshāīūṭḍṅṇṃṃñḷ]";
    return RegExp(cons + '*' + vowel + '(?:' + cons + '(?!' + vowel + '))?' + '|' + other, 'gi')

    var other = "[^aiueokgcjtdnpbmyrlvshāīūṭḍṅṇṃṃñḷ]";
    var cons = "[kgcjtdnpbmyrlvshṭḍṅṇṃṃñḷ]"
    return RegExp('('+cons+'*[aiueoāīū]('+cons+'(?='+other+')|[yrlvshṅṃñ](?=h)|' + cons + '(?!h)' + '(?='+cons+'))?'+')|('+other+'+)', 'gi');})();

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
    }
}

function transliterateWord(word, func) {
    var script = func.name
    //Caching makes no performance difference for Chrome, but Firefox is faster.
    //However the reverse cache is very useful because it enables word lookup in roman.
    if (func.name == 'toSyllables')
        return func(word);
    
    word = word.toLowerCase().replace(/ṁ/g, 'ṃ');
    if (!wordMap[script][word]) {
        wordMap[script][word] = func(word)
        reverseMap[wordMap[script][word]] = word
    }
    return wordMap[script][word];
}

function transliterateString(input, func) {
    var splitRex = RegExp('[^aiueokgcjtdnpbmyrlvshāīūṭḍṅṇṃñḷ]+|[aiueokgcjtdnpbmyrlvshāīūṭḍṅṇṃñḷ]+', 'gi');
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
var b={"ā":"ා",i:"ි","ī":"ී",u:"ු","ū":"ූ",e:"ෙ",o:"ො","ṃ":"ං",k:"ක",g:"ග","ṅ":"ඞ",c:"ච",j:"ජ","ñ":"ඤ","ṭ":"ට","ḍ":"ඩ","ṇ":"ණ",t:"ත",d:"ද",n:"න",p:"ප",b:"බ",m:"ම",y:"ය",r:"ර",l:"ල","ḷ":"ළ",v:"ව",s:"ස",h:"හ"};
var j={kh:"ඛ",gh:"ඝ",ch:"ඡ",jh:"ඣ","ṭh":"ඨ","ḍh":"ඪ",th:"ථ",dh:"ධ",ph:"ඵ",bh:"භ","jñ":"ඥ","ṇḍ":"ඬ",nd:"ඳ",mb:"ඹ",rg:"ඟ"};
var a={k:"ක",g:"ග","ṅ":"ඞ",c:"ච",j:"ජ","ñ":"ඤ","ṭ":"ට","ḍ":"ඩ","ṇ":"ණ",t:"ත",d:"ද",n:"න",p:"ප",b:"බ",m:"ම",y:"ය",r:"ර",l:"ල","ḷ":"ළ",v:"ව",s:"ස",h:"හ"};
var k,g,f,e,d;var c="";var h=0;while(h<l.length){k=l.charAt(h-2);g=l.charAt(h-1);
f=l.charAt(h);e=l.charAt(h+1);d=l.charAt(h+2);if(m[f]){if(h==0||g=="a"){c+=m[f]}else{if(f!="a"){c+=b[f]
}}h++}else{if(j[f+e]){c+=j[f+e];h+=2;if(a[d]){c+="්"}}else{if(b[f]&&f!="a"){c+=b[f];
h++;if(a[e]&&f!="ṃ"){c+="්"}}else{if(!b[f]){if(a[g]||(g=="h"&&a[k])){c+="්"}c+=f;
h++;if(m[e]){c+=m[e];h++}}else{h++}}}}}if(a[f]){c+="්"}c=c.replace(/ඤ්ජ/g,"ඦ");c=c.replace(/ණ්ඩ/g,"ඬ");
c=c.replace(/න්ද/g,"ඳ");c=c.replace(/ම්බ/g,"ඹ");c=c.replace(/්ර/g,"්ර");c=c.replace(/\`+/g,'"');
return c.slice(0, -1)}
function toMyanmar(k){k=k.toLowerCase() + " ";var m={a:"အ",i:"ဣ",u:"ဥ","ā":"အာ","ī":"ဤ","ū":"ဦ",e:"ဧ",o:"ဩ"};
var l={i:"ိ","ī":"ီ",u:"ု","ū":"ူ",e:"ေ","ṃ":"ံ",k:"က",kh:"ခ",g:"ဂ",gh:"ဃ","ṅ":"င",c:"စ",ch:"ဆ",j:"ဇ",jh:"ဈ","ñ":"ဉ","ṭ":"ဋ","ṭh":"ဌ","ḍ":"ဍ","ḍh":"ဎ","ṇ":"ဏ",t:"တ",th:"ထ",d:"ဒ",dh:"ဓ",n:"န",p:"ပ",ph:"ဖ",b:"ဗ",bh:"ဘ",m:"မ",y:"ယ",r:"ရ",l:"လ","ḷ":"ဠ",v:"ဝ",s:"သ",h:"ဟ"};
var a={k:"က",g:"ဂ","ṅ":"င",c:"စ",j:"ဇ","ñ":"ဉ","ṭ":"ဋ","ḍ":"ဍ","ṇ":"ဏ",t:"တ",d:"ဒ",n:"န",p:"ပ",b:"ဗ",m:"မ",y:"ယ",r:"ရ",l:"လ","ḷ":"ဠ",v:"ဝ",s:"သ",h:"ဟ"};
var n={kh:"1",g:"1",d:"1",dh:"1",p:"1",v:"1"};var j,f,e,d,c;var b="";var g=0;k=k.replace(/\&quot;/g,"`");
var h=false;while(g<k.length){j=k.charAt(g-2);f=k.charAt(g-1);e=k.charAt(g);d=k.charAt(g+1);
c=k.charAt(g+2);if(m[e]){if(g==0||f=="a"){b+=m[e]}else{if(e=="ā"){if(n[h]){b+="ါ"
}else{b+="ာ"}}else{if(e=="o"){if(n[h]){b+="ေါ"}else{b+="ော"}}else{if(e!="a"){b+=l[e]
}}}}g++;h=false}else{if(l[e+d]&&d=="h"){b+=l[e+d];if(c!="y"&&!h){h=e+d}if(a[c]){b+="္"
}g+=2}else{if(l[e]&&e!="a"){b+=l[e];g++;if(d!="y"&&!h){h=e}if(a[d]&&e!="ṃ"){b+="္"
}}else{if(!l[e]){b+=e;g++;if(m[d]){if(m[d+c]){b+=m[d+c];g+=2}else{b+=m[d];g++}}h=false
}else{h=false;g++}}}}}b=b.replace(/ဉ္ဉ/g,"ည");b=b.replace(/္ယ/g,"ျ");b=b.replace(/္ရ/g,"ြ");
b=b.replace(/္ဝ/g,"ွ");b=b.replace(/္ဟ/g,"ှ");b=b.replace(/သ္သ/g,"ဿ");b=b.replace(/င္/g,"င်္");
return b.slice(0, -1)}
function toDevar(l){l=l.toLowerCase() + " ";var m={a:" अ",i:" इ",u:" उ","ā":" आ","ī":" ई","ū":" ऊ",e:" ए",o:" ओ"};
var n={"ā":"ा",i:"ि","ī":"ी",u:"ु","ū":"ू",e:"े",o:"ो","ṃ":"ं",k:"क",kh:"ख",g:"ग",gh:"घ","ṅ":"ङ",c:"च",ch:"छ",j:"ज",jh:"झ","ñ":"ञ","ṭ":"ट","ṭh":"ठ","ḍ":"ड","ḍh":"ढ","ṇ":"ण",t:"त",th:"थ",d:"द",dh:"ध",n:"न",p:"प",ph:"फ",b:"ब",bh:"भ",m:"म",y:"य",r:"र",l:"ल","ḷ":"ळ",v:"व",s:"स",h:"ह"};
var k,h,g,f,e,d,b;var c="";var a=0;var j=0;l=l.replace(/\&quot;/g,"`");while(j<l.length){k=l.charAt(j-2);
h=l.charAt(j-1);g=l.charAt(j);f=l.charAt(j+1);e=l.charAt(j+2);d=l.charAt(j+3);b=l.charAt(j+4);
if(j==0&&m[g]){c+=m[g];j+=1}else{if(f=="h"&&n[g+f]){c+=n[g+f];if(e&&!m[e]&&f!="ṃ"){c+="्"
}j+=2}else{if(n[g]){c+=n[g];if(f&&!m[f]&&!m[g]&&g!="ṃ"){c+="्"}j++}else{if(g!="a"){if(a[h]||(h=="h"&&a[k])){c+="्"
}c+=g;j++;if(m[f]){c+=m[f];j++}}else{j++}}}}}if(a[g]){c+="्"}c=c.replace(/\`+/g,'"');
return c.slice(0, -1)}
function toThai(m){m=m.toLowerCase() + " ";var n={a:"1","ā":"1",i:"1","ī":"1","iṃ":"1",u:"1","ū":"1",e:"2",o:"2"};
var j={a:"อ","ā":"า",i:"ิ","ī":"ี","iṃ":"ึ",u:"ุ","ū":"ู",e:"เ",o:"โ","ṃ":"ํ",k:"ก",kh:"ข",g:"ค",gh:"ฆ","ṅ":"ง",c:"จ",ch:"ฉ",j:"ช",jh:"ฌ","ñ":"","ṭ":"ฏ","ṭh":"","ḍ":"ฑ","ḍh":"ฒ","ṇ":"ณ",t:"ต",th:"ถ",d:"ท",dh:"ธ",n:"น",p:"ป",ph:"ผ",b:"พ",bh:"ภ",m:"ม",y:"ย",r:"ร",l:"ล","ḷ":"ฬ",v:"ว",s:"ส",h:"ห"};
var a={k:"1",g:"1","ṅ":"1",c:"1",j:"1","ñ":"1","ṭ":"1","ḍ":"1","ṇ":"1",t:"1",d:"1",n:"1",p:"1",b:"1",m:"1",y:"1",r:"1",l:"1","ḷ":"1",v:"1",s:"1",h:"1"};
var l,h,g,f,e,d,b;var c="";var k=0;m=m.replace(/\&quot;/g,"`");while(k<m.length){l=m.charAt(k-2);
h=m.charAt(k-1);g=m.charAt(k);f=m.charAt(k+1);e=m.charAt(k+2);d=m.charAt(k+3);b=m.charAt(k+4);
if(n[g]){if(g=="o"||g=="e"){c+=j[g]+j.a;k++}else{if(k==0){c+=j.a}if(g=="i"&&f=="ṃ"){c+=j[g+f];
k++}else{if(g!="a"){c+=j[g]}}k++}}else{if(j[g+f]&&f=="h"){if(e=="o"||e=="e"){c+=j[e];
k++}c+=j[g+f];if(a[e]){c+="ฺ"}k=k+2}else{if(j[g]&&g!="a"){if(f=="o"||f=="e"){c+=j[f];
k++}c+=j[g];if(a[f]&&g!="ṃ"){c+="ฺ"}k++}else{if(!j[g]){c+=g;if(a[h]||(h=="h"&&a[l])){c+="ฺ"
}k++;if(f=="o"||f=="e"){c+=j[f];k++}if(n[f]){c+=j.a}}else{k++}}}}}if(a[g]){c+="ฺ"
}c=c.replace(/\`+/g,'"');return c.slice(0, -1);};

//Pali lookup functions//
function generateLookupMarkup(){
    //We want to wrap every word in a tag.
    var classes = ".sutta P, .sutta H1, .sutta H2, .sutta H3"
    generateMarkupCallback.nodes = $(classes).toArray();
    generateMarkupCallback.start = Date.now();
    sc.sidebar.disableControls()
    generateMarkupCallback();
    return;
}

function generateMarkupCallback() {
    var node = generateMarkupCallback.nodes.shift();
    if (!node) {
        sc.sidebar.enableControls();
        return}
    toLookupMarkup(node);
    setTimeout(generateMarkupCallback, 5);
}

var paliRex = /([aiueokgcjtdnpbmyrlvshāīūṭḍṅṇṃñḷ’­”]+)/i;
var splitRex = /([^  \n,.– —:;?!"'“‘-]+)/;
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
    word = word.replace(/ṃg/g, 'ṅg').replace(/ṃk/g, 'ṅk').replace(/ṃ/g, 'ṃ').replace(/Ṃ/g, 'ṃ');
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
                var base = firstchar + leftover;
                if (base != 'ṃ') {
                    allMatches.push({"base": base, "meaning":"?"});
                }
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
        var href = "http://suttacentral.net/define/" + allMatches[i].base;
        
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

            wordp = wordp.replace(/ī$/, "i").replace(/ā$/, "i").replace(/ū$/, "i").replace(/n$/, "").replace(/n$/, "ṃ");
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
            var target = sc.piLookup.data[part]
            if (typeof(target) == 'object') {
                var meaning = target[1];
                if (meaning === undefined) {
                    meaning = target[0];
                }
                
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
    var target = sc.piLookup.data[word];
    if(typeof(target) == 'object') {
        if (target[1] === undefined) {
            var meaning = target[0];
        } else {
            var meaning = target[1] + ' ('+target[0]+')';
        }
        return {"base": word, "meaning": meaning};
    }
    return null;
}

function fuzzyMatch(word){
    var end = sc.piLookup.endings;
    for(var i = 0; i < end.length; i++) {
        if(word.length > end[i][2] && word.substring(word.length - end[i][0].length, word.length) === end[i][0]) {
            var orig = word.substring(0,word.length - end[i][0].length + end[i][1]) + end[i][3];
            var target = sc.piLookup.data[orig];
            if(typeof(target) == 'object') {
                if (target[1] === undefined) {
                    var meaning = target[0];
                } else {
                    var meaning = target[1] + ' ('+target[0]+')';
                }
                return {"base": orig, "meaning": meaning};
            }
        }
    }
    return null;
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

function nextInOrderByType(node, nodeType) {
    while (true) {
        var node = nextInOrder(node);
        if (node === undefined) return
        if (node.nodeType == nodeType) {
                return node
        }
    }
}

function nextInOrderBySelector(node, selector) {
    while (true) {
        var node = nextInOrder(node);
        if (node === undefined) return
        if ($(node).is(selector)) return node;
    }
}

function nextInOrder(node) {
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
    return node
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
    else if (typeof permissables == 'string') {
        if ($(node).is(permissables)) return node;
    }
    else if (permissables.indexOf(node.nodeType) != -1)
        return node;
    return previousInOrder(node, permissables);
}
