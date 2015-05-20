// # Plugins
// `eachText` will call `callback` for the text value of every text node
// within the collection. The text value will be set to the return value
// of the callback, unless that value is `undefined`. eachText calls
// *callback* on text in document order.
$.fn.eachText = function(callback) {
    function iterNodes(node) {
        if (node.nodeType == 3) {
            var result = callback(node.nodeValue, node);
            if (result !== undefined) {
                node.nodeValue = result;
            }
        } else {
            Array.prototype.forEach.call(node.childNodes, iterNodes);
        }
    }
    this.each(function(){iterNodes(this)});
    return this
}

// Returns a flattened array of descendent textNodes
// optionally filtered by *filter*, which should return
// true to include an element.
$.fn.textNodes = function(filter) {
    var result = [];
    function iterNodes(node) {
        if (filter && $.proxy(filter, node)(node) == false) return
        
        if (node.nodeType == 3) {
            result.push(node);
        } else {
            Array.prototype.forEach.call(node.childNodes, iterNodes);
        }
    }
    this.each(function(){iterNodes(this)});
    return $(result)
}

sc.text_selection = (function() {
    "use strict";

    // Module is available only for texts.
    if ($('#text').length == 0) return

    // Only text within these $elements are valid selection targets
    var elementSelector = 'article > *:not(div),\
                           article > div.hgroup,\
                           article > div:not(.hgroup) > *',

        $elements = $(elementSelector),
        valid_char_rex = /[^ \n “”‘’.,?!—]/g,
        ignoreClasses,
        link;
    
    function nodeFilter() {
        //return !$(this).is(ignoreClasses);
        if ($(this).is(ignoreClasses)) {
            return false
        }
        if (this.nodeType == 3 && /^\s*[“”‘’]+\s*$/.test(this.nodeValue)) {
            return false
        }
        return true
    }

    function onReady() {
        var a = ['.deets'];
        for (var k in (sc.classes.margin))  {
            a.push('.' + k);
        }
        ignoreClasses = ','.join(a);
        highlightSelection();

        $(document.body).on('mouseup', function(){_.delay(updateLink, 1)});

    }
    
    function highlightSelection() {
        var parts = window.location.pathname.split('/');
        if (parts.length < 4) return
        var targets = parts[3],
            firstTarget = null;
        
        targets.split('+').forEach(function(target) {
            // Form 1

            var m = /(\d+)(?:(?:\.(\d+))?-(\d+)(?:\.(\d+))?)?/.exec(target),
                startId = +m[1],
                endId = +m[3],
                startOffset = +m[2],
                endOffset = +m[4],
                startedHl = false,
                wasStartedHl = false,
                doneHl = false;
            if (isNaN(endId)) { endId = startId }
            if (isNaN(startOffset) || startOffset == 0) { startOffset = 1 }
            if (isNaN(endOffset)) { endOffset = 9001 }


            //console.log(startId, endId, startOffset, endOffset);
            
            for (var index = startId; index <= endId; ++index) {
                var targetElement = $elements[index];
                firstTarget = firstTarget || targetElement;
                if (index != startId && index != endId)
                {
                    $(targetElement)
                        .textNodes(nodeFilter)
                        .wrap('<span class="marked">');
                    continue
                }
                var pos = 0;
                $(targetElement).textNodes(nodeFilter)
                                .each(function(i, node) {
                    var text = node.nodeValue;
                    if (index == endId && pos >= endOffset) {
                        return
                    }
                    wasStartedHl = startedHl;
                    var startedAdded = false;
                    var newText = text.replace(valid_char_rex, function (m) {
                        var result = m[0];
                        pos += 1;
                        if (index == endId && pos == endOffset) {
                            result = result + '__HLEND__';
                            doneHl = true;
                        }
                        if (index == startId && pos == startOffset) {
                            result = '__HLSTART__' + result;
                            startedAdded = true;
                            startedHl = true;
                        }
                        return result
                    });

                    if (startedHl) {
                        if (!startedAdded) {
                            newText = '__HLSTART__' + newText;
                        }
                        if (!doneHl) {
                            newText = newText + '__HLEND__';
                        }
                    }
                    node.nodeValue = newText
                    
                });
                var html = targetElement.innerHTML;
                html = html.replace(/__HLSTART__/g, '<span class="marked">')
                           .replace(/__HLEND__/g, '</span>');
                targetElement.innerHTML = html;
                var marked = $(targetElement).find('.marked');
                marked.first().addClass('first-marked');
                marked.last().addClass('last-marked');
                
            }

            for (var index = startId; index <= endId; ++index) {
                var marked = $($elements[index]).find('.marked');
                marked.first().addClass('first-marked');
                marked.last().addClass('last-marked');
            }
        });
        
        if (firstTarget) {
            document.body.scrollTop = $(firstTarget).offset().top - 40;
        }
    }
    
    function getSelectionCoords(range) {
        return
    }

    function createReferenceChrome(selection) {
        var range = selection.getRangeAt(0),
            startNode = range.startContainer,
            endNode = range.endContainer,
            startParent = $(startNode).parents(elementSelector),
            endParent = $(endNode).parents(elementSelector),
            startOffset = range.startOffset,
            endOffset = range.endOffset;

        if ($(range.commonAncestorContainer).parents('#text').length == 0) {
            return {error: 'A reference could not be created as ' +
                            'the selection is not a part of the text'}
        }

        var result = [],
            start_id = $elements.index(startParent),
            end_id = $elements.index(endParent);

        for (var index = start_id; index <= end_id; ++index) {
            if (index > start_id && index < end_id) {
                result.push({index: index})
                continue
            }
            var parent = $elements[index],
                char_start = null,
                char_end = null,
                valid_char_count = 0;
            
            if (index > start_id) {
                char_start = 0;
            }
            if (index < end_id) {
                char_end = $(parent).text().match(valid_char_rex).length;
            }

            $(parent).textNodes(nodeFilter).each(function(i, node){
                var text = node.nodeValue;
                if (node == startNode || node == endNode) {
                    if (char_end !== null && char_start !== null) return
                    var all_char_count = 0;
                    
                    Array.prototype.forEach.call(text, function(char){
                        if (char_end !== null && char_start !== null) return
                        if (char.search(valid_char_rex) == 0) {
                            valid_char_count += 1;
                            if (node == startNode) {
                                if (all_char_count == startOffset) {
                                    char_start = valid_char_count;
                                }
                            }
                            if (node == endNode) {
                                if (all_char_count >= endOffset) {
                                    char_end = valid_char_count - 1;
                                }
                            }
                        }
                        all_char_count += 1;
                    });
                } else {
                    var m = text.match(valid_char_rex);
                    if (m) {
                        valid_char_count += m.length;
                    } // else += 0
                }
            });
            result.push({index: index,
                         char_start: char_start,
                         char_end: char_end,
                         range: range})
        }
        return result;
    }
    
    function updateLink() {
        closeQuotePopup();
        var selection = window.getSelection();
        if (window.getSelection().type != 'Range') {
            return
        } 
        
        var target = null;

        var result = createReferenceChrome(selection);
        if ('error' in result) {
            closeQuotePopup();
            return
        }
        
        var start = result.slice(0, 1)[0],
            end = result.slice(-1)[0];

        if (end.char_end == 1) {
            end.index -= 1;
            end.char_end = null;
        }
        if (start.char_start == 1 && end.char_end == null) {
            if (start.index == end.index) {
                target = start.index;
            }
        }
        if (target == null) {
            var targetStart = start.index;
            if (start.char_start > 1 || end.char_end != null) {
                targetStart += '.' + start.char_start;
            }
            var targetEnd = end.index;
            if (end.char_end != null) {
                targetEnd += '.' + end.char_end;
            }
            //console.log(targetStart, targetEnd)
            target = '{}-{}'.format(targetStart, targetEnd);
        }

        var lang_uid = $('#text').attr('lang'),
            uid = $('.sutta').attr('id');
        
        link = '{}/{}/{}/{}'.format(window.location.origin,
                                   lang_uid,
                                   uid,
                                   target);
        
        var clientRects = result[0].range.getClientRects()
        console.log(clientRects[0]);
        var quoteControls = $('\
<div id="quote-controls" class="closed">\
<div id="quote-inner-wrap">\
<button id="quote-button">Quote</button>\
<input id="quote-link"/>\
<button id="quote-copy-link">Copy URL</button>\
</div>\
</div>');
        
        var quoteButton = quoteControls.find('#quote-button'),
            quoteLink = quoteControls.find('#quote-link'),
            quoteCopyButton = quoteControls.find('#quote-copy-link');
        
        quoteControls.appendTo(document.body)
                     .css({'position': 'fixed',
                            'top': clientRects[0].top,
                            'left': clientRects[0].left});
        
        quoteButton.on('click', function(e){
            quoteControls.toggleClass('closed');
            e.preventDefault();
            quoteLink.select();
            return false
        });
        quoteControls.on('mouseup', function(e){ return false });
        quoteLink.val(link);
        
        var clip = new ZeroClipboard(quoteCopyButton[0], {
                moviePath: "/js/vendor/ZeroClipboard-1.2.3.swf",
                hoverClass: "hover",
                activeClass: "active"
            });

            clip.on('load', function(client) {
                client.on('complete', function(client, args) {
                });
            });
            clip.on('dataRequested', function(client, args) {
                var text = quoteLink.val();
                client.setText(text);
                console.log('Set text');
            });
    
        $(window).one('scroll', closeQuotePopup);
        
    }
    
    function closeQuotePopup(){
        $('#quote-controls').remove();
    }
    
    $(document).one('ready', onReady);

    return {highlightSelection: highlightSelection,
            createReference: createReferenceChrome,
            nodeFilter: nodeFilter}
})();

function paint(){
    var selection = window.getSelection(),
        range = selection.getRangeAt(0),
        startNode = range.startContainer,
        endNode = range.endContainer,
        startOffset = range.startOffset,
        endOffset = range.endOffset;
    

}
