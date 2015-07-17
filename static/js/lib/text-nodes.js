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
};
