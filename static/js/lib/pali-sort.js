/* Based on code from Digital Pali Reader */
/* Made slightly less nutty */
(function(){

var reorder = [
'#','0','1','2','3','4','5','6','7','8','9',
'a','ā','i','ī','u','ū','e','o','ṃ','k','kh','g','gh','ṅ','c','ch','j',
'jh','ñ','ṭ','ṭh','ḍ','ḍh','ṇ','t','th','d','dh','n','p','ph','b','bh',
'm','y','r','l','ḷ','v','s','h'
]

var oldorder = [
'#','0','1','2','3','4','5','6','7','8','9',
'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R',
'S','T','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p',
'q','r','s','t','u','v','w','x','y','z'
]

var neworder = []
var roo = '';
for(var w = 0; w < reorder.length; w++) {
    roo = reorder[w];
    neworder[roo] = oldorder[w];
}

function sortaz(mydata){  // sort pali array

    mydata = mydata.sort(comparePaliAlphabet);
    for (i in mydata) {
        mydata[i] = mydata[i].replace(/^.*###/,''); // remove sorted words, return the rest
    } 
    return mydata;
}

function sortStrip(word) {
    if(DPR_prefs['nigahita']) {
        word = word.replace(/ṁ/g, 'ṃ');
        word = word.replace(/Ṁ/g, 'Ṃ');
    }
    word = toUni(word.toLowerCase()).replace(/[^a-zāīūṃṅñṭḍṇḷ#]/g,'');
    return word;
}

function comparePaliAlphabet(a,b) {
    
    if (a.length == 0 || b.length == 0) return;

    var two = [sortStrip(a),sortStrip(b)];
    var nwo = [];
    for(i = 0; i < two.length; i++) {
        var wordval = '';
        for (var c = 0; c < two[i].length; c++) {
            
            var onechar = two[i].charAt(c);
            if(onechar == '#') break;
            
            var twochar = onechar + two[i].charAt(c+1);
            
            if (neworder[twochar]) {
                wordval+=neworder[twochar];
                c++;
            }
            else if (neworder[onechar]) {
                wordval+=neworder[onechar];
            }
            else {
                wordval+=onechar;
            }
        }
        two[i] = wordval;
        nwo[i] = wordval;
    }
    nwo.sort();
    //dalert(a+' '+nwo+' '+b+' ' + two+' '+(nwo[0] == two[0]));
    if(nwo[0] != two[0]) return 1;
    else return -1;
    
}

window.comparePaliAlphabet = comparePaliAlphabet;

});
