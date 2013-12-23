/* This file contains useful javascript 'utilities', not specifically
 * related to sutta central.
 */


/* Pythonic format function.
 * I wrote this when I didn't have net access. Later I checked on-line
 * and there were a couple of existing versions. I didn't observe them
 * to be particulary more featureful, however.
 */

"use strict"
String.prototype.format = function(){
    var args = arguments, fs = this, i=0, j=-1;
    fs = fs.replace('{{', '\x01\x02').replace('}}', '\x03\x04');
    fs = fs.replace(/\{[^}]*\}/g, function(m){
        j++;
        var m = /\{(\w*)([^}]*)\}/.exec(m),
            key = m[1], attrs = m[2],
            obj, k, a;
        if (!key && !attrs) {
            if (j != i) throw new Error("Cannot switch from automatic field numbering to manual field specification");
            return args[i++];
        } else if (!isNaN(key)) {
            if (key >= args.length) throw new Error("Index out of range");
            obj = args[key];
        } else {
            if (!(key in args[0]))
                throw new Error('Key Error: ' + key);
            obj = args[0][key];
        }

        if (!attrs) return obj;
        a = attrs.split(/([.\[])/);
        for (k = 0; k < a.length; k += 2) {
            key = a[k]
            if (key == '' && k == 0) continue;
            if (a[k-1] == '['){
                if (key.slice(-1) != ']')
                    throw new Error("Format Syntax Error, unmatched [");
                key = key.slice(0, -1);
            }
            obj = obj[key]
        }
        return obj;
    });
    fs = fs.replace('\x01\x02', '{').replace('\x03\x04', '}');
    return fs
}

String.prototype.toTitleCase = function() {
    var skip = this.toTitleCase.skip;
    var string = this.replace(/(\S)(\S+)/g, function(m, m1, m2){
        if (m in skip) return m
            else
        return m1.toUpperCase() + m2});
    // Uppercase first letter regardless.
    return string[0].toUpperCase() + string.slice(1);
}
String.prototype.toTitleCase.skip = {"the":0, "on":0, "of":0, "and":0, 
                                     "in":0, "by":0}

// Python style 'join' where the string joins the elements of an array
// Note: The python logic is extremely good. Making 'join' a string method
// means it works on any array-like-object. Making 'join' an array method
// means it needs to be defined seperately for every array-like-object.
String.prototype.join = function(a){
    return Array.prototype.join.call(a, this)
}

var sc = window.sc || {}

sc.util = {
    // The most usual way to use the asciifyMap is provided here.
    asciify: function(string, defaultChar){
        var mapping = sc.util.getAsciifyMap();
        if (defaultChar === undefined)
            defaultChar = '';
        return string.replace(/[\u007f-\uffff]/g, function(t){return mapping[t] || defaultChar})
    },
    // The inverse of the above, allows a regex to match unicode equivs.
    unifyRegexPattern: function(string){
        var mapping = sc.util.getUnifyMap();

        return string.replace(/[ -~]/g, function(t){
            return '[' + t + (mapping[t] || '') + ']'
        });
    },
    getAsciifyMap: function(){
        if (!sc.util._asciifyMap)
            sc.util._generateMaps()
        return sc.util._asciifyMap;
    },
    getUnifyMap: function(){
        if (!sc.util._unifyMap)
            sc.util._generateMaps()
        return sc.util._unifyMap;
    },
    _generateMaps: function(){
        var data = [
            ';;',
            '<≮',
            '=≠',
            '>≯',
            '``',
            'aàáâãäåāăąǎǟǡǻȁȃȧḁạảấầẩẫậắằẳẵặ',
            'bḃḅḇ',
            'cçćĉċčḉ',
            'dďḋḍḏḑḓ',
            'eèéêëēĕėęěȅȇȩḕḗḙḛḝẹẻẽếềểễệ',
            'fḟ',
            'gĝğġģǧǵḡ',
            'hĥȟḣḥḧḩḫẖ',
            'iìíîïĩīĭįǐȉȋḭḯỉị',
            'jĵǰ',
            'kķǩḱḳḵ',
            'lĺļľḷḹḻḽ',
            'mḿṁṃ',
            'nñńņňǹṅṇṉṋ',
            'oòóôõöōŏőơǒǫǭȍȏȫȭȯȱṍṏṑṓọỏốồổỗộớờởỡợ',
            'pṕṗ',
            'rŕŗřȑȓṙṛṝṟ',
            'sśŝşšșṡṣṥṧṩ',
            'tţťțṫṭṯṱẗ',
            'uùúûüũūŭůűųưǔǖǘǚǜȕȗṳṵṷṹṻụủứừửữự',
            'vṽṿ',
            'wŵẁẃẅẇẉẘ',
            'xẋẍ',
            'yýÿŷȳẏẙỳỵỷỹ',
            'zźżžẑẓẕ',
            //The below were added manually.
            '-–—',
            '"“”',
            '\'‘’'],
            ascmap = {},
            unimap = {}
        data.forEach(function(s){
            var o = s[0], i, c, oupper = o.toUpperCase();
            for (i = s.length - 1; i >= 1; i--) {
                c = s[i]
                ascmap[c] = o
                ascmap[c.toUpperCase()] = oupper;
            }
            unimap[o] = s.slice(1)
            unimap[oupper] = unimap[o].toUpperCase()
        });
        sc.util._asciifyMap = ascmap;
        sc.util._unifyMap = unimap;
    }
}

