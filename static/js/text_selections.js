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
        $linkElement = $('[name=text-selection-url]')
    
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
        var a = [];
        for (var k in (sc.classes.margin))  {
            a.push('.' + k);
        }
        ignoreClasses = ','.join(a);
        highlightSelection();

        $(document.body).on('mouseup', updateLink);
        var clip = new ZeroClipboard($linkElement.parent().find('button')[0], {
            moviePath: "/js/vendor/ZeroClipboard-1.2.3.swf",
            hoverClass: "hover",
            activeClass: "active"
        });
        clip.on('load', function(client) {
            client.on('complete', function(client, args) {
            });
        });
        clip.on('dataRequested', function(client, args) {
            var text = $linkElement.val();
            client.setText(text);
            console.log('Set text');
        });
        
        $linkElement.on('click', function() {
            $linkElement.select();
        });
        
        $linkElement.parent().find('button, input').attr('disabled', 'disabled');
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


            console.log(startId, endId, startOffset, endOffset);
            
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

    function createReferenceChrome() {
        var selection = window.getSelection(),
            range = selection.getRangeAt(),
            startNode = range.startContainer,
            endNode = range.endContainer,
            startParent = $(startNode).parents(elementSelector),
            endParent = $(endNode).parents(elementSelector),
            startOffset = range.startOffset,
            endOffset = range.endOffset;

        var range = selection.getRangeAt();

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
                    valid_char_count += text.match(valid_char_rex).length;
                }
            });
            result.push({index: index,
                         char_start: char_start,
                         char_end: char_end})
        }
        return result;
    }

    function createReference(chars) {
        var selection = window.getSelection(),
            startNode = selection.anchorNode,
            endNode = selection.focusNode,
            startParent = $(startNode).parents(elementSelector),
            endParent = $(endNode).parents(elementSelector),
            startOffset = selection.anchorOffset,
            endOffset = selection.focusOffset;

        var range = selection.getRangeAt();

        if ($(range.commonAncestorContainer).parents('#text').length == 0) {
            return {error: 'A reference could not be created as ' +
                            'the selection is not a part of the text'}
        }
            
        if (startParent.length == 0 || endParent.length == 0) {
            return {'error':'A reference could not be created as ' +
                            'the selection is not a part of the text'}
        }
        var result = [],
            start_id = $elements.index(startParent),
            end_id = $elements.index(endParent);

        // A selection respects the users choice of direction (forwards
        // or backwards), we don't care, so if the user went backwards
        // swap all the values.

        // First we swap the parents if we need to.
        if (start_id >= end_id) {
            var diff = null;
            if (start_id > end_id) {
                var tmp = end_id;
                end_id = start_id;
                start_id = tmp;

                tmp = startParent;
                startParent = endParent;
                endParent = tmp;
                diff = -1;
            } else {
                // If there are two parents, then the text nodes will
                // definitely be out of order. But if there is only one
                // parent then we need to check.
                var nodes = $($elements.toArray()
                                      .slice(start_id, end_id + 1)
                              ).textNodes();
                diff = nodes.index(endNode) - nodes.index(startNode);
            }
            if (diff > 0) {
                // If the diff is > 0 we are cool, but it might
                // still be the case that there is only one textNode
                // involved, and the user went in reverse.
                
            } else if ((diff < 0) || (startOffset > endOffset)) {
                tmp = startNode;
                startNode = endNode
                endNode = tmp;

                tmp = startOffset;
                startOffset = endOffset;
                endOffset = tmp;
            }
        }
        
        for (var index = start_id; index <= end_id; ++index) {
            if (index > start_id && index < end_id) {
                result.append({index: index})
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

            $(parent).textNodes().each(function(i, node){
                var text = node.nodeValue;
                if (node == startNode || node == endNode) {
                    if (char_end !== null && char_start !== null) return
                    var all_char_count = 0;
                    
                    Array.prototype.forEach.call(text, function(char){
                        if (char_end !== null && char_start !== null) return
                        if (char.search(valid_char_rex) == 0) {
                            valid_char_count += 1;
                            console.log(char, valid_char_count, all_char_count);
                            if (node == startNode) {
                                if (all_char_count == startOffset) {
                                    char_start = valid_char_count;
                                    console.log('Start: ', char, char_start);
                                }
                            }
                            if (node == endNode) {
                                if (all_char_count >= endOffset) {
                                    char_end = valid_char_count - 1;
                                    console.log('End: ', char, char_end);
                                }
                            }
                        }
                        all_char_count += 1;
                    });
                } else {
                    valid_char_count += text.match(valid_char_rex).length;
                }
            });
            result.push({index: index,
                         char_start: char_start,
                         char_end: char_end})
        }
        return result;
    }
    
    function updateLink() {
        if (window.getSelection().type != 'Range') return
        var target = null;

        var result = createReferenceChrome();
        if ('error' in result) {
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
            console.log(targetStart, targetEnd)
            target = '{}-{}'.format(targetStart, targetEnd);
        }

        var lang_uid = $('#text').attr('lang'),
            uid = $('.sutta').attr('id');
        
        $linkElement.val('{}/{}/{}/{}'.format(window.location.origin,
                                   lang_uid,
                                   uid,
                                   target));
        $linkElement.parent().find('button, input').removeAttr('disabled');
    }
    
    $(document).one('ready', onReady);

    return {highlightSelection: highlightSelection,
            createReference: createReferenceChrome,
            nodeFilter: nodeFilter}
})();
