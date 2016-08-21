//This file is designed to be customized by users familiar with css and html.
//The meat and potato functions are found in sc.functions.js, they should not be
//edited except by someone who knows javascript, also, "use strict"

//The id of the page element which gets populated with the textual control elements.

var sc = window.sc || {}

sc.classes = {
    margin: {
        "as": "Page numbers in Yamada, 1972.",
        "adh-v": "Paragraph numbers in Adhikaraṇavastu, Gnoli 1978",
        "apz": "Paragraph numbers in A.P. de Zoysa",
        "cps": "Paragraph numbers in Catuṣpariṣatsūtra, E. Waldschmidt, 1952-62",
        "ba": "paragraph number in The Book of Analysis, Thittila 1969",
        "bhaisv": "Paragraph numbers in Bhaiṣajyavastu, J. Chung und K. Wille",
        "bi": "Paragraph numbers in Bhikkhu Indacanda.",
        "bjt": "Paragraph numbers in Buddha Jayanthi.",
        "bl": "(Not defined in GRETIL source.)",
	"bm": "Paragraph numbers in Bhikkhu Mettiko.",
	"bn": "Paragraph numbers in Bhikkhu Ñāṇadassana.",
        "bps": "Buddhist Publication Society",
        "bjt": "Buddha Jayanthi Tipitaka",
        "d-vp": "Vol/page of the Derge edition",
        "divy": "Paragraph numbers in Divyāvadāna, ed. E.B. Cowell, R.A. Neil, Cambridge 1886",
        "eno89": "Paragraph numbers in Enomoto, 1989.",
	"es": "Paragraph numbers in Ekkehard Saß.",
	"fa": "Verse numbers in Falk 2015.",
        "fuk03": "Page numbers in Fukita, 2003",
        "fol": "Folio number in the manuscript.",
        "gatha-number": "Verse number.",
        "gatn": "",
        "gbm": "Section numbers in Gilgit Buddhist Manscripts.",
        "gno78": "Paragraph numbers in Gnoli, 1978.",
        "har04": "Paragraph number in Hartmann, 2004.",
	"hh": "Paragraph numbers in Hellmuth Hecker.",
        "hoe16": "Verse numbers in Hoernle, 1916.",
        "hos89a": "Paragraph numbers in Hosoda, 1989, “Sanskrit Fragments from the Parivrājakasaṃyukta of the Saṃyuktāgama I.”",
        "hos89b": "Paragraph numbers in Hosoda, 1989, “Sanskrit Fragments from the Parivrājakasaṃyukta of the Saṃyuktāgama II.”",
        "hos91": "Paragraph numbers in Hosoda, 1991.",
        "hs": "(Not defined in GRETIL source.)",
        "ia": "Paragraph numbers in Indra Anggara",
        "jb": "Verse numbers in Gāndhārī Dharmapada, John Brough, London 1962",
	"jd": "Paragraph numbers in Dr. Julius Dutoit.",
	"jsk": "Paragraph numbers in J.S. Krüger.",
        "kat": "Paragraph numbers in Kaṭhinavastu, Matsumura, 1996.",
        "kel": "Paragraph numbers in Kelly, Sawyer, and Yareham.",
        "kl": "Paragraph numbers in Kåre A. Lie.",
	"ks": "Paragraph numbers in Karl Seidenstücker.",
	"lh": "Verse numbers in Lenz 2003, Hinüber 2004.",
        "mat85": "Paragraph numbers in Matsumura, 1985.",
        "mat88": "Paragraph numbers for Mahāsudarśanasūtra in Matsumura, 1988.",
        "mat96": "Paragraph numbers in Matsumura, 1996.",
        "mc": "Verse numbes in Patna Dharmapada, Margaret Cone",
        "mkv" : "Page numbers in Mahākarmavibhaṅga",
        "mit57": "Paragraph numbers in Mittal, 1957.",
        "ms": "Mahāsaṅgīti paragraph number.",
        "msdiv": "Msdiv paragraph numbers.",
        "msvi": "Vol/page in Gilgit Manuscript, ed. N. Dutt, vol. III.1",
        "msvii": "Vol/page in Gilgit Manuscript, ed. N. Dutt, vol. III, part 2, Srinagar 1942.",
        "msviii": "Vol/page in Gilgit Manuscript, ed. N. Dutt, vol. III, part 3, Srinagar 1943.",
        "msviv": "Vol/page in Gilgit Manuscript N. Dutt vollIII part IV",
        "msvwi": "Vol/page in Wille",
        "mt": "Paragraph numbers in Maitrimurti / Trätow.",
        "ms-pa": "",
	"nm": "Paragraph numbers in Nyānatiloka Mahāthera.",
	"np": "Paragraph numbers in Nyānaponika Mahāthera.",
        "nst": "Paragraph numbers in Ven. Nilwakke Somananda Thera.",
        "of": "Paragraph numbers in Otto Franke, 1913.",
        "pand-v": "Paragraph numbers in Pāṇḍulohitakavastu Nobuyuki Yamagiwa",
	"pl": "Paragraph numbers in Peter van Loosbroek.",
        "pos-v": "Paragraph numbers in Posadhavastu von Hinüber",
        "prava-v": "Paragraph numbers in Pravaranavastu Jin-il Chung",
        "pravr-v-i": "Paragraph numbers in Pravrajyāvastu vol I Vogel/Wille",
        "pravr-v-ii": "Paragraph numbers in Pravrajyāvastu vol II Vogel/Wille",
        "pravr-v-iii": "Paragraph numbers in Pravrajyāvastu vol III Vogel/Wille",
        "pravr-v-iv": "Paragraph numbers in Pravrajyāvastu vol IV Vogel/Wille",
        "pts": "Pali Text Society vol/page number.",
        "pts-s": "Pali Text Society section number.",
        "pts1ed": "Page number of Pali Text Society, 1st edition.",
        "pts2ed": "Page number of Pali Text Society, 2nd edition.",
        "pts-cs": "Chapter and section of Pali Text Society editions.",
        "pts-vp-en": "Vol/page of the Pali Text Society translation.",
        "pts-vp-pi": "Vol/page of the Pali Text Society Pali edition.",
        "pts_pn": "Pali Text Society vol/page number.",
        "pts-p-pi": "Pali Text Society page number for the Pali text.",
        "roth": "Paragraph numbers in Roth, 1970.",
        "rs-vp": "Volume and page numbers in Rahula Sankriytayana translation.",
        "san87": "Paragraph numbers in Sander, 1987.",
        "san89": "Paragraph numbers in Sander, 1989.",
        "say-v": "Paragraph numbers in Śayanāsanavastu, Gnoli 1978",
        "sb": "Paragraph numbers in Fritz Schaefer / Raimund Beyerlein.",
        "sbvi": "Paragraph numbers in Saṅghabhedavastu, Gnoli / Venkatacharya, 1977-78",
        "sbvii": "Paragraph numbers in Saṅghabhedavastu, Gnoli / Venkatacharya, 1977-78",
        "sc": "SuttaCentral paragraph number.",
        "sen": "Section and paragraph numbers in Senart, 1882.",
        "sht": "References for SHT fragments.",
        "snp-vagga-section-verse": "Chapter, section, and verse number within the section.",
        "snp-vagga-verse": "Chapter, and verse number within the chapter.",
        "ss": "Paragraph numbers in Shai Schwartz",
        "t": "Sutra number and page, column, and line in the Taishō canon.",
        "titus": "",
        "t-linehead": "Sutra number and page, column, and line in the Taishō canon.",
        "tb": "Paragraph numbers in Thanissaro Bhikkhu.",
        "ttc": "Paragraph numbers in Thích Thiện Châu.",
        "ud-sutta": "Sutta number.",
        "ud-vagga-sutta": "Chapter/sutta number.",
        "tri62": "Sūtra and paragraph number in Tripāṭhī, 1962.",
        "tri95": "Section and paragraph number in Tripāṭhī, 1995.",
        "tu": "",
        "uv": "Chapter and verse numbers for the Udānavarga.",
        "vagga-gatha-num-sc": "SuttaCentral vagga and verse number",
        "vai58": "Page numbers in Vaidya, 1958.",
        "vai59": "Page and line numbers in Vaidya, 1959.",
        "vai61": "Page and line numbers in Vaidya, 1961.",
        "var-v": "Paragraph numbers in Varsavastu Masanori Shono",
        "verse-num-sc": "SuttaCentral verse number",
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
	"wg": "Paragraph numbers in Wilhelm Geiger.",
        "wp": "Wisdom Publications paragraph number.",
        "wr": "Paragraph numbers in Walpola Rahula.",
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
        "gloss": "Definition of term.",
        "jataka":"An embedded Jātaka story.",
        "precision": "Estimated precision of this location (1 = known, 6 = unknowable)",
        "pe":"Instructions for expanding text supplied by the editor or translator.",
        "expanded":"Text expanded by editor or translator although elided in original.",
        "sic": "Apparently incorrect reading determined by the editor.",
        "skt-mg-bu-pm": "Rule numbers in the Sanskrit Mahāsaṅghika Bhikhhu Pātimokkha.",
        "supplied": "Text hypothetically reconstructed by the editor or translator.",
        "suppliedmetre": "Metre reconstructed by the editor.",
        "surplus": "Surplus text.",
        "sutta-parallel":"Passage also found in the Sutta Pitaka.",
        "term": "Defined term.",
        "unclear": "Unclear reading."
    }
}
sc.classes.marginSelector = _.map(_.keys(sc.classes.margin),
                                  function(e){return '.' + e})
                            .join(',')

/*
 * Prefix To Volume mapping used for adding volume information
 * to paragraph/line numbers.
 *
 * The uid MUST be defined <section class="sutta" id="uid"> and it
 * must be lowercase.
 *
 * The code uses a 'longest first match' approach, so for example
 * sa-2.1 would match both sa and sa-2, but sa-2 will always be matched
 * first as it is longest. This means a more specific match will always
 * override a less specific one.
 *
 * It wont match parts of words, for example 't' will not match 'thag'.
 * It is required that after the match comes a non-alphabetical
 * character. 'zh-mg' will match 'zh-mg-bu-pm' as it is followed by
 * a hyphen. 'zh-mg-' would not as it is followed by 'b'.
 *
 * If the volume is a string it is simply used. If it is arrays, then
 * the numbers are 'to' : 'from' ranges. If the uid matches the division
 * but fails to match any number range, it counts as failed and the code
 * will attempt to match against other untried division codes.
 */

sc.volPrefixMap = {
    'da': 'i',
    'ma': 'i',
    'ea': 'ii',
    'ea-2': 'ii',
    'sa': 'ii',
    'sa-2': 'ii',
    'sa-3': 'ii',
    'zh-mg': 'xxii',
    'zh-mi': 'xxii',
    'zh-dg': 'xxii',
    'zh-mi': 'xxii',
    'zh-sarv': 'xxiii',
    'zh-ka': 'xxiv',
    't': [
        [0, 98, 'i'],
        [102, 151, 'ii'],
        [152, 154, 'iii'],
        [197, 212, 'iv'],
        [499, 515, 'xiv'],
        [605, 605, 'xv'],
        [713, 715, 'xvi'],
        [741, 802, 'xvii'],
        [1245, 1362, 'xxi'],
        [1421, 1428, 'xxii'],
        [1435, 1444, 'xxii'],
        [1448, 1451, 'xxiv'],
        [1507, 1509, 'xxv'],
        [1521, 1537, 'xxvi'],
        [1545, 1545, 'xxvii'],
        [1548, 1548, 'xxviii']
        ]
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
    
    
    $('.acro:not([title])').each(function(){
        var e = $(this);
        e.attr('title', sc.util.acro_to_name(e.text()));
    })
    
    var parallelCitationLabel = $('#parallel-citation .label');
    var parallelCitationTextField = $('#parallel-citation > input');
    var parallelCitationButton = $('#parallel-citation > button');
    if (parallelCitationButton.length) {
        parallelCitationTextField.on('click', function() {
            parallelCitationTextField.select();
        });
        parallelCitationTextField.attr('id', 'parallel-citation-field')
        parallelCitationButton.attr('data-clipboard-target', '#parallel-citation-field');
        var clipboard = new Clipboard('#parallel-citation > button');
        clipboard.on('success', function(e) {
            parallelCitationButton.addClass('copied');
            setTimeout(function(){parallelCitationButton.removeClass('copied')}, 250);
        })
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
        var translitFunc = null;
            prefscript = sc.userPrefs.getPref("script");

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
            sc.piLookup.enablePaliLookup(true);
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
