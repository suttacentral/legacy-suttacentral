//This file is designed to be customized by users familiar with css and html.
//The meat and potato functions are found in sc_functions.js, they should not be
//edited except by someone who knows javascript, also, "use strict"

//The id of the page element which gets populated with the textual control elements.
textualControls = {
    id: "textual_controls",
    marginClasses: "a.bps, a.eno89, a.fol, a.gatha-number, a.gatn, a.gbm, a.gno78, a.har04, a.hoe16, a.hos89a, a.hos89b, a.hos91, a.hs, a.kel, a.mat85, a.mat88, a.mit57, a.ms, a.san87, a.sc, a.sen82, a.snp-vagga-section-verse, a.snp-vagga-verse, a.t, a.titus-random, a.tlinehead, a.tri62, a.tri95, a.tu, a.uv, a.vai59, a.verse-num-pts, a.vimula, a.vn, a.vnS, a.wal48, a.wal50, a.wal52, a.wal58, a.wal59a, a.wal60, a.wal61, a.wal68a, a.wal70a, a.wal70b, a.wal76, a.wal78, a.wal80c, a.wp, a.yam72",
    popupClasses: ".pub, .var, .rdg, .cross, .end",
    contentClasses: ".supplied, .supplied2, .add, .corr, .del, .end, .lem, .sic, .surplus",
    metaarea: "#metaarea"
}

var sc = {
    'zh2en_dict_url' : '/js/zh2en_dict_0.04s.js',
    'pi2en_dict_url' : '/js/pi2en_dict_0.03.js'
}

// Used for different 'modes', such as interface language (defaults to 'en')
// Also partly to save on transfer and ease of updating titles.
scMode = {
    'lang':'en',
    'en':{
        'strings':{
            'add': "Text added by the editor or translator for clarification.",
            'altAcronym': "PTS 1998 (Somaratne) edition of SN Vol I.",
            'altVolPage': "Alternative PTS or Taisho numbering.",
            'as': "Page numbers in Yamada, 1972.",
            'bl': "(Not defined in GRETIL source.)",
            'eno89': "Paragraph numbers in Enomoto, 1989.",
            'fol': "Folio number in the manuscript.",
            'fuk03': "Page numbers in Fukita, 2003",
            'gbm': "Section numbers in Gilgit Buddhist Manscripts.",
            'gno78': "Paragraph numbers in Gnoli, 1978.",
            'har04': "Paragraph number in Hartmann, 2004.",
            'hoe16': "Verse numbers in Hoernle, 1916.",
            'hos89a': "Paragraph numbers in Hosoda, 1989, “Sanskrit Fragments from the Parivrājakasaṃyukta of the Saṃyuktāgama I.”",
            'hos89b': "Paragraph numbers in Hosoda, 1989, “Sanskrit Fragments from the Parivrājakasaṃyukta of the Saṃyuktāgama II.”",
            'hos91': "Paragraph numbers in Hosoda, 1991.",
            'hs': "(Not defined in GRETIL source.)",
            'kel': "Paragraph numbers in Kelly, Sawyer, and Yareham.",
            'mat85': "Paragraph numbers in Matsumura, 1985.",
            'mat88': "Paragraph numbers for Mahāsudarśanasūtra in Matsumura, 1988.",
            'mit57': "Paragraph numbers in Mittal, 1957.",
            'ms': "Mahāsaṅgīti paragraph number.",
            'precision': "Estimated precision of this location (1 = known, 6 = unknowable)",
            'roth': "Paragraph numbers in Roth, 1970.",
            'san87': "Paragraph numbers in Sander, 1987.",
            'san89': "Paragraph numbers in Sander, 1987.",
            'sc': "Sutta Central paragraph number.",
            'sen82': "Section and paragraph numbers in Senart, 1882.",
            'sht': "References for SHT fragments.",
            'skt-mg-bu-pm': "Rule numbers in the Sanskrit Mahāsaṅghika Bhikhhu Pātimokkha.",
            'snp-vagga-section-verse': "Chapter, section, and verse number within the section.",
            'snp-vagga-verse': "Chapter, and verse number within the chapter.",
            'supplied': "Text hypothetically reconstructed by the editor or translator.",
            'surplus': "Surplus text.",
            'tri62': "Sūtra and paragraph number in Tripāṭhī, 1962.",
            'tri95': "Section and paragraph number in Tripāṭhī, 1995.",
            'ud-sutta': "Sutta number.",
            'ud-vagga-sutta': "Chapter/sutta number.",
            'uv': "Chapter and verse numbers for the Udānavarga.",
            'dp': "Verse numbers for Dhammapada.",
            'vai58': "Page numbers in Vaidya, 1958.",
            'vai59': "Page and line numbers in Vaidya, 1959.",
            'verse-num-pts': "Verse number in the Pali Text Society edition.",
            'vn': "Vietnamese translation paragraph number.",
            'wal48': "Paragraph numbers for sondertext in Waldschmidt, 1948 (ST.ii).",
            'wal50': "Paragraph numbers in Waldschmidt, 1950 (etc.).",
            'wal52': "Paragraph numbers in Waldschmidt, 1952, 1956, 1960.",
            'wal55b': "Paragraph numbers in Waldschmidt, 1955b, “Die Einleitung des Saṅgītisūtra.”",
            'wal57c': "Paragraph numbers in Waldschmidt, 1957c, “Das Upasenasūtra.”",
            'wal58': "Paragraph numbers in Waldschmidt, 1958.",
            'wal59a': "Paragraph numbers in Waldschmidt, 1959a, “Kleine Brahmi-Schriftrolle.”",
            'wal60': "Paragraph numbers in Waldschmidt, 1960/1.",
            'wal61': "Paragraph numbers for sondertext in Waldschmidt, 1961 (ST.i).",
            'wal68a': "Paragraph numbers in Waldschmidt, 1958a, “Drei Fragmente buddhistischer Sūtras aus den Turfanhandschriften.”",
            'wal70a': "Paragraph numbers in Waldschmidt, 1970a, Buddha frees the disc of the moon.",
            'wal70b': "Paragraph numbers in Waldschmidt, 1970b, “Fragment of a Buddhist Sanskrit text on cosmogony.”",
            'wal76': "Paragraph numbers in Waldschmidt, 1976.",
            'wal78': "Paragraph numbers in Waldschmidt, 1978.",
            'wal80c': "Paragraph numbers in Waldschmidt, 1980c, “On a Sanskrit version of the Verahaccāni Sutta.”",
            'wp': "Wisdom Publications paragraph number.",
            'yam72': "Paragraph numbers in Yamada, 1972."
        }
    }
}

$(document).ready(function() {
    $('#home').easyTabs({defaultContent:1});
    if ($('.sutta').length > 0){
        textualControls.init();
    }
});

function kindAdviceToIEusers(version){
    if (version > 8) return; //Works well enough on IE 9/10
    //Tell the user to upgrade
    $("#toc").append('<div style="border: 2px solid red; font-size:11px">You appear to be using an obsolete version of Internet Explorer. Advanced site features are not supported for old browsers and will not work. Please install and use a modern browser such as Google Chrome, Firefox, Internet Explorer 9 or 10 - or install the Google Chrome Frame plugin. <small>Or you know, keep using an antique broswer, and missing out on half the internet.</small></div>');
}
if (m = navigator.appVersion.match(/MSIE ([0-9]+)/))
    kindAdviceToIEusers(m[1]);

textualControls.init = function(){
    this.allInfoClasses = this.textInfoClasses + ", " + this.textmarginInfoClasses;
    if (document.getElementById(this.id)){
        document.getElementById(this.id).innerHTML = "";
    } else { //Create at the best position.
        controls = '<div id="' + this.id + '"></div>';
        if ($("#toc").append(controls).length) {}//Bottom of the #toc
        else if ($("#menu, menu").last().after(controls).length){}//Below the menu
        else if ($("#onecol").prepend(controls).length) {}//Start of the #onecol
        else if ($("header").last().after(controls).length) {}//Below the header
        else if ($("body").prepend(controls).length) {}//Start of the body
        else {
            alert("Something seriously weird has happened! Failed to find anywhere to insert the textual controls. No #toc, no (#)menu, no header, not even a body! What kind of weird html document is this?");
        }
    }
    initChineseLookup();
    initPaliFunctions();
    $("#metaarea").detach().appendTo("#toc")
    scState.save("clean");
    sc_init();
}

textualControls.disable = function() {
    $('#' + this.id + ' button').attr('disabled', 'disabled');
}
textualControls.enable = function() {
    $('#' + this.id + ' button').removeAttr('disabled');
}

function initChineseLookup()
{
    //Logic for deciding whether to install chinese lookup
    if ($('div[lang*=zh]').length == 0) return;//no elements declared to be chinese

    //Where to attach the chinese lookup control button.
    chineseLookup.init('#' + textualControls.id)
}

function initPaliFunctions()
{
    //Logic for deciding whether to install pali lookup
    if ($('div').filter($('[lang*="pi"]')).length > 0) scMode.pali = true

    //Create elements
    addButtons(document.getElementById(textualControls.id));
}

//The code below here is quite disorganized and messy
//Rewriting it is on the to-do.


//The dictionary of pali to english glosses.
var paliDictSrc = "lookup_data.js"//"lookup_data.js"
var paliLookupLogId = "pali_lookup_log"

//The id of the button which generates text info (for styling in css)
var textInfoButtonId = "text_info_button"
var paliLookupButtonId = "pali_lookup_button"


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

function sc_init(reset)
{
    if (reset) scState.restore("clean");
    //Bind elements
    bindButtons();
    
    buildTextualInformation();
    if (scUserPrefs.getPref("textInfo") === true)
    {
        toggleTextualInfo(true);
    }
    
    if (scMode.pali === true) {
        translitFunc = null;
        prefscript = scUserPrefs.getPref("script");
        if (prefscript){
            scMode.translitFunc = transFuncs[prefscript][0];
        } else {
            scMode.translitFunc = transFuncs['toRoman'][0];
        }
        
        for (f in transFuncs) 
            if (wordMap[f] == undefined)
                wordMap[f] = {};
        
        if (!scMode.translitFunc) scMode.translitFunc = transFuncs[0][0];
        if (scUserPrefs.getPref("paliLookup") === true)
        {
            if (scMode.translitFunc.name == 'toSyllables')
            {
                toSyllablesInit();
            }
            enablePaliLookup(true);
        } else {
            transliterate(scMode.translitFunc);
        }
    }
}

function addButtons(target){
    if (!target) return;
    var out = '<button id="' + textInfoButtonId + '">Textual Information</button>';
    if (scMode.pali === true){
        out += '<button id="' + paliLookupButtonId + '">Pali→English Dictionary</button>' + '<div id="' + paliLookupLogId + '"></div>';

        out += '<div id="translitButtons">';
        for (f in transFuncs) {
            out += '<button id="' + f + '">' + transFuncs[f][1] + '</button>'
        }
        out += '</div>';
    }

    $(target).append(out);
};

//"use strict"//


//Note: These preferences are not shared with the server. If session storage is available,
//it will be used. Otherwise settings will be forgotten on page refresh.
scUserPrefs = {
    sc_storage: getStorage(),
    setRemember: function(value) {
        value = !!value;
        if (value == false) this.sc_storage.clear();
        this.sc_storage["remember"] = value;
    },
    isRemember: function(){
        return this.sc_storage["remember"];
    },
    setPref: function(pref, value, re_init) {
        this.sc_storage[pref] = value;
        if (re_init) sc_init(true); //be more refined here perhaps.
    },
    getPref: function(pref) {
        
        var value = this.sc_storage[pref];
        if (value === 'false') return false;
        if (value === 'true') return true;
        if (Number(value).toString() === value) return Number(value);
        return value;
    },
    togglePref: function(pref) {
        this.sc_storage[pref] = !this.sc_storage[pref];
    },
    clearPref: function(pref){
        this.sc_storage.removeItem(pref);
    },
    clearAll: function(){
        this.sc_storage.clear();
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
    //if (count > 0) console.log("Oh Internet Explorer, I love you in " + count + " ways.");
};

ohInternetExplorerLetMeCountTheWaysILoveYou();

$('#search_box_input').select().focus();
