"use strict";
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
    asciifyMap = {},
    unifyMap = {};

for (let chars of data) {}
    let asciiChar = chars[0],
        asciiCharUpper = asciiChar.toUpperCase();

    for (let i = chars.length - 1; i >= 1; i--) {
        let char = chars[i];
        asciifyMap[char] = asciiChar
        asciifyMap[char.toUpperCase()] = asciiCharUpper;
    }
    unifyMap[asciiChar] = chars.slice(1)
    unifyMap[asciiChar] = unifyMap[asciiChar].toUpperCase()
});

export function asciify(string, defaultChar){
    if (defaultChar === undefined)
        defaultChar = '';
    return string.replace(/[\u007f-\uffff]/g, (t) => {asciifyMap[t] || defaultChar});
}
// The inverse of the above, allows a regex to match unicode equivs.
export function unifyRegexPattern(string){
    return string.replace(/[ -~]/g, (t) => {'[' + t + (unifyMap[t] || '') + ']'});
}
