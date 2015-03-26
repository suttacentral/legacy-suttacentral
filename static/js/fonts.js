sc = sc || {};

sc.fonts = {
    makeFontName: function(e) {
        return '{},{},{}'.format(
            e.css('font-family').split(',')[0],
            e.css('font-weight'),
            e.css('font-style'))
    },
    analyzeFontsRecursive: function(element, result) {
        if (result === undefined) result = {};
        var fontName = this.makeFontName($(element)),
            chars = [];
        $(element).contents().each(function() {
            if (this.nodeType === 3) {
                chars = _.union(chars, this.nodeValue.split(''));
            } else if (this.nodeType === 1) {
                sc.fonts.analyzeFontsRecursive(this, result);
            }
        });
        
        
        result[fontName] = _.union(result[fontName] || [], chars)
        return result
    },
    massageResults: function(results) {
        for (fontName in results) {
            results[fontName].sort();
            results[fontName] = results[fontName].join('');
        }
        
        return results
    },
    getHtmlDump: function(results) {
        var results = this.analyzeFontsRecursive(document.body);
        this.massageResults(results)
        
        out = '<table style="margin:0; padding: 0">'
        _.sortBy(_.pairs(results), function(t){
            return 1 / (1 + t[1].length);
        }).forEach(function(t, i){
            var style = 'font-name: {0[0]}; font-weight: {0[1]}; font-style: {0[2]}'.format(t[0].split(','));
            out += '<tr style="font-family: {0}"><td style="white-space: nowrap">{0}</td><td style="{2}">{1}</td></tr>'.format(t[0].replace(/,/g, '<br>'), t[1], style);
        });
        return out
    }
}

$(document).on('ready', function() {
    if (window.location.search == '?fonts') {
        var html = sc.fonts.getHtmlDump();
        var e = $('<div id="fonts-dump"/>').css(
            {position: "fixed",
             right: 0, 
             'z-index': 9001,
             bottom: 0,
             top: 0,
             width: "50em",
             background: "white",
             border: "1px solid black",
             'font-family': "mono",
             'font-size': "80%",
             'word-break': 'break-all',
             'overflow-x': 'visible',
             'overflow-y': 'auto'
            });
             
        e.html(html).appendTo(document.body);
        console.log(html);
        
    }
});
