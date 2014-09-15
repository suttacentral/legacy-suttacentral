//This file is designed to be customized by users familiar with css and html.
//The meat and potato functions are found in sc.functions.js, they should not be
//edited except by someone who knows javascript, also, "use strict"

//The id of the page element which gets populated with the textual control elements.

var sc = window.sc || {}

sc.classes = {
    margin: {
        "as": "Page numbers in Yamada, 1972.",
        "bl": "(Not defined in GRETIL source.)",
        "bps": "",
        "eno89": "Paragraph numbers in Enomoto, 1989.",
        "fuk03": "Page numbers in Fukita, 2003",
        "fol": "Folio number in the manuscript.",
        "gatha-number": "Verse number.",
        "gatn": "",
        "gbm": "Section numbers in Gilgit Buddhist Manscripts.",
        "gno78": "Paragraph numbers in Gnoli, 1978.",
        "har04": "Paragraph number in Hartmann, 2004.",
        "hoe16": "Verse numbers in Hoernle, 1916.",
        "hos89a": "Paragraph numbers in Hosoda, 1989, “Sanskrit Fragments from the Parivrājakasaṃyukta of the Saṃyuktāgama I.”",
        "hos89b": "Paragraph numbers in Hosoda, 1989, “Sanskrit Fragments from the Parivrājakasaṃyukta of the Saṃyuktāgama II.”",
        "hos91": "Paragraph numbers in Hosoda, 1991.",
        "hs": "(Not defined in GRETIL source.)",
        "kel": "Paragraph numbers in Kelly, Sawyer, and Yareham.",
        "mat85": "Paragraph numbers in Matsumura, 1985.",
        "mat88": "Paragraph numbers for Mahāsudarśanasūtra in Matsumura, 1988.",
        "mit57": "Paragraph numbers in Mittal, 1957.",
        "ms": "Mahāsaṅgīti paragraph number.",
        "ms-pa": "",
        "of": "Paragraph numbers in Otto Franke, 1913.",
        "pts": "Pali Text Society vol/page number.",
        "pts1": "Page number of Pali Text Society, 1st edition (1881–1992).",
        "pts2": "Page number of Pali Text Society, 2nd edition (1974–1998).",
        "pts-cs": "Chapter and section of Pali Text Society editions.",
        "pts-vp-en": "Vol/page of the Pali Text Society translation.",
        "pts-vp-pi": "Vol/page of the Pali Text Society Pali edition.",
        "pts_pn": "Pali Text Society vol/page number.",
         "pts-p-pi": "Pali Text Society page number for the Pali text.",
        "roth": "Paragraph numbers in Roth, 1970.",
        "san87": "Paragraph numbers in Sander, 1987.",
        "san89": "Paragraph numbers in Sander, 1987.",
        "sc": "Sutta Central paragraph number.",
        "sen82": "Section and paragraph numbers in Senart, 1882.",
        "sht": "References for SHT fragments.",
        "snp-vagga-section-verse": "Chapter, section, and verse number within the section.",
        "snp-vagga-verse": "Chapter, and verse number within the chapter.",
        "t": "",
        "titus": "",
        "t-linehead": "",
        "ud-sutta": "Sutta number.",
        "ud-vagga-sutta": "Chapter/sutta number.",
        "tri62": "Sūtra and paragraph number in Tripāṭhī, 1962.",
        "tri95": "Section and paragraph number in Tripāṭhī, 1995.",
        "tu": "",
        "uv": "Chapter and verse numbers for the Udānavarga.",
        "vai58": "Page numbers in Vaidya, 1958.",
        "vai59": "Page and line numbers in Vaidya, 1959.",
        "vai61": "Page and line numbers in Vaidya, 1961.",
        "verse-num-pts": "Verse number in the Pali Text Society edition.",
        "vimula": "",
        "vn": "Vietnamese translation paragraph number.",
        "wal48": "Paragraph numbers for sondertext in Waldschmidt, 1948 (ST.ii).",
        "wal50": "Paragraph numbers in Waldschmidt, 1950 (etc.).",
        "wal52": "Paragraph numbers in Waldschmidt, 1952, 1956, 1960.",
        "wal55b": "Paragraph numbers in Waldschmidt, 1955b, “Die Einleitung des Saṅgītisūtra.”",
        "wal57c": "Paragraph numbers in Waldschmidt, 1957c, “Das Upasenasūtra.”",
        "wal58": "Paragraph numbers in Waldschmidt, 1958.",
        "wal59a": "Paragraph numbers in Waldschmidt, 1959a, “Kleine Brahmi-Schriftrolle.”",
        "wal60": "Paragraph numbers in Waldschmidt, 1960/1.",
        "wal61": "Paragraph numbers for sondertext in Waldschmidt, 1961 (ST.i).",
        "wal68a": "Paragraph numbers in Waldschmidt, 1958a, “Drei Fragmente buddhistischer Sūtras aus den Turfanhandschriften.”",
        "wal70a": "Paragraph numbers in Waldschmidt, 1970a, Buddha frees the disc of the moon.",
        "wal70b": "Paragraph numbers in Waldschmidt, 1970b, “Fragment of a Buddhist Sanskrit text on cosmogony.”",
        "wal76": "Paragraph numbers in Waldschmidt, 1976.",
        "wal78": "Paragraph numbers in Waldschmidt, 1978.",
        "wal80c": "Paragraph numbers in Waldschmidt, 1980c, “On a Sanskrit version of the Verahaccāni Sutta.”",
        "wp": "Wisdom Publications paragraph number.",
        "yam72": "Paragraph numbers in Yamada, 1972."
    },
    popup: {
        "pub": "",
        "var": "",
        "rdg": "",
        "cross": "",
        "end": ""
    },
    content: {
        "add": "Text added by the editor or translator for clarification.",
        "altAcronym": "PTS 1998 (Somaratne) edition of SN Vol I.",
        "altVolPage": "Alternative PTS or Taisho numbering.",
        "corr": "Reading corrected by the editor.",
        "dp": "Verse numbers for Dhammapada.",
        "gap": "Gap in the manuscript.",
        "gloss": "Definition of term",
        "precision": "Estimated precision of this location (1 = known, 6 = unknowable)",
        "sic": "Apparently incorrect reading determined by the editor.",
        "skt-mg-bu-pm": "Rule numbers in the Sanskrit Mahāsaṅghika Bhikhhu Pātimokkha.",
        "supplied": "Text hypothetically reconstructed by the editor or translator.",
        "suppliedmetre": "Metre reconstructed by the editor.",
        "surplus": "Surplus text.",
        "term": "Defined term",
        "unclear": "Unclear reading."
    }
}

sc.mode = {}
sc.data = {}
sc.jsBaseUrl = $('script[src*="js/"]').last().attr('src').match(/((.*\/|^)js\/)/)[0];

function onMainLoad() {
    sc.mode = {}
    var images = $("img");
    images.unveil(50);
    //polyfill details if needed
    $("details").details()
    if (!$.fn.details.support){
        // For css
        $("details").addClass('no-details').on('open.details', function(){
            $(this).attr('open', true);}).on('close.details', function(){
                $(this).attr('open', false);});
    }
    
    if ($('.sutta').length > 0){
        sc.mode.pali = ($('#text').attr('lang') == 'pi');
        sc.sidebar.init();
        sc.init();
    }
    var parallelCitationLabel = $('#parallel-citation .label');
    var parallelCitationTextField = $('#parallel-citation > input');
    var parallelCitationButton = $('#parallel-citation > button');
    if (parallelCitationButton.length) {
        parallelCitationTextField.on('click', function() {
            parallelCitationTextField.select();
        });
        var clip = new ZeroClipboard(parallelCitationButton, {
            moviePath: "/js/vendor/ZeroClipboard-1.2.3.swf",
            hoverClass: "hover",
            activeClass: "active"
        });
        clip.on('load', function(client) {
            parallelCitationLabel.hide();
            parallelCitationButton.show();
            client.on('complete', function(client, args) {
            });
        });
        clip.on('dataRequested', function(client, args) {
            var text = parallelCitationTextField.val();
            client.setText(text);
        });
    }
}

$(document).ready(onMainLoad);

function kindAdviceToIEusers(version){
    if (version > 8) return; //Works well enough on IE 9/10
    //Tell the user to upgrade
    $("#toc").append('<div style="border: 2px solid red; font-size:11px">You appear to be using an obsolete version of Internet Explorer. Advanced site features are not supported for old browsers and will not work. Please install and use a modern browser such as Google Chrome, Firefox, Internet Explorer 9 or 10 - or install the Google Chrome Frame plugin. <small>Or you know, keep using an antique broswer, and missing out on half the internet.</small></div>');
}
if (m = navigator.appVersion.match(/MSIE ([0-9]+)/))
    kindAdviceToIEusers(m[1]);

//The code below here is quite disorganized and messy
//Rewriting it is on the to-do.

// These are respectively, the id's of the buttons which peform transliteration,
// and the name of the function responsible for transliterating raw text
var transFuncs = {
    // id       function   label, title (optional)
    'toRoman':[toRoman, 'kā'],
    'toSinhala':[toSinhala, 'කා'],
    'toThai':[toThai, 'กา'],
    'toMyanmar':[toMyanmar, 'ကာ'],
    'toDevar':[toDevar,'का'],
    'toSyllables':[toSyllables, 'k-ā', "Breaks words into syllables and distinguishes between short and long syllables."]
};


var syllSpacer = '‧'; //Seperates syllables when that mode is activated. (\u2027)

sc.init = function(reset)
{
    if (reset) scState.restore("clean");
    
    buildTextualInformation();
    if (sc.userPrefs.getPref("textInfo") === true) {
        toggleTextualInfo(true);
    }
    
    if (sc.mode.pali === true) {
        var lookupToLang = sc.userPrefs.getPref('lookupToLang'),
            translitFunc = null;
            prefscript = sc.userPrefs.getPref("script");

        if (lookupToLang) {
            $('#lookup-to-lang').val(lookupToLang);
        }
        if (prefscript){
            sc.mode.translitFunc = transFuncs[prefscript][0];
        } else {
            sc.mode.translitFunc = transFuncs['toRoman'][0];
        }
        
        for (f in transFuncs) 
            if (wordMap[f] == undefined)
                wordMap[f] = {};
        
        if (!sc.mode.translitFunc) sc.mode.translitFunc = transFuncs[0][0];
        if (sc.userPrefs.getPref("paliLookup") === true)
        {
            if (sc.mode.translitFunc.name == 'toSyllables')
            {
                toSyllablesInit();
            }
            enablePaliLookup(true);
        } else {
            transliterate(sc.mode.translitFunc);
        }
    }
}

//"use strict"//

//Note: These preferences are not shared with the server. If session storage is available,
//it will be used. Otherwise settings will be forgotten on page refresh.
sc.userPrefs = {
    storage: getStorage(),
    setRemember: function(value) {
        value = !!value;
        if (value == false) this.storage.clear();
        this.storage["remember"] = value;
    },
    isRemember: function(){
        return this.storage["remember"];
    },
    setPref: function(pref, value, re_init) {
        this.storage[pref] = value;
        if (re_init) sc.init(true); //be more refined here perhaps.
    },
    getPref: function(pref) {
        
        var value = this.storage[pref];
        if (value === 'false') return false;
        if (value === 'true') return true;
        if (Number(value).toString() === value) return Number(value);
        return value;
    },
    togglePref: function(pref) {
        this.storage[pref] = !this.storage[pref];
    },
    clearPref: function(pref){
        this.storage.removeItem(pref);
    },
    clearAll: function(){
        this.storage.clear();
    }
}

function getStorage(){
    try {
        if('sessionStorage' in window && window['sessionStorage'] != null)
        {
            return sessionStorage;
        }
    } catch (e) {

    }
    //No session storage, return an ordinary object.
    return {};
}

function ohInternetExplorerLetMeCountTheWaysILoveYou(){
    function userFunc(){}
    var count = 0;
    if (!('name' in userFunc)){
        //#1 Not defining 'name' on functions
        for (var f in transFuncs) {
            transFuncs[f][0].name = f;
            count += 1;
        }
    }
};

ohInternetExplorerLetMeCountTheWaysILoveYou();
