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
        ignoreSelector = '.text-popup *',
        link;
    
    function nodeFilter() {
        if ($(this).is(ignoreSelector)) {
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
        var ignoreClasses = ','.join(a);
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

            var m = /(\d+)(?:(?:\.(\d+))?-(\d+)?(?:\.(\d+))?)?/.exec(target),
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
    var lastString = null;
    function updateLink(force) {
        
        var selection = window.getSelection();
        var thisString = selection.toString().trim();
        if (!force && thisString == lastString) {
            return
        }
        lastString = thisString;
        
        closeQuotePopup();
        
        if (!force && window.getSelection().type != 'Range') {
            return
        }
        
        
        
        var target = null;

        var result = createReferenceChrome(selection);
        if ('error' in result) {
            return
        }
        
        var start = result.slice(0, 1)[0],
            end = result.slice(-1)[0];

        if (end.char_end == 1) {
            end.index -= 1;
            end.char_end = null;
        }
        if (start.char_start <= 1 && end.char_end == null) {
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
            } else {
                targetEnd = '';
            }
            //console.log(targetStart, targetEnd)
            target = '{}-{}'.format(targetStart, targetEnd);
        }

        var lang_uid = $('#text').attr('lang'),
            uid = $('.sutta').attr('id'),
            shortLink = '{}/{}/{}'.format(lang_uid, uid, target),
            link = '{}/{}'.format(window.location.origin,
                                 shortLink);
            
        
        var clientRects = result[0].range.getClientRects()
        var quoteControls = $(
            '<div id="quote-controls" data-clipboard-text="{}" title="Link to selected text">'.format(link) +
            '<input id="quote-link" value="{}" readonly>'.format(link) +
            '<input id="quote-copied" value="URL Copied" disabled>' +
            '</div>'),
            quoteLink = quoteControls.find('#quote-link'),
            quoteCopied = quoteControls.find('#quote-copied');
            
            quoteControls.appendTo(document.body)
                     .css({'position': 'fixed',
                            'top': clientRects[0].top,
                            'left': clientRects[0].left});
            quoteLink.on('click', function(){
                quoteLink.select();
            });
            var client = new ZeroClipboard(quoteControls);
            
            client.on('ready', function(readyEvent) {
                quoteLink.val('…/' + shortLink);
                client.on('copy', function(event) {
                    $('#quote-controls').addClass('copied').delay(1100).removeClass('copied');
                    $('#quote-copied').fadeIn(500).delay(100).fadeOut(500);
                    $('#quote-link').fadeTo(0, 0.0).delay(1100).fadeTo(100, 1.0);
                })
            })
        
        $(window).one('scroll', function(){
            updateLink(true);
        });
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
    

};
