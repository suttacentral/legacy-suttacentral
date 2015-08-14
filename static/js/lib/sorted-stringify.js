/* This code was taken from this question on stackoverflow:
 * http://stackoverflow.com/a/23124958/4092906
 * 
 */

var sortByKeys = function(obj) {
  if (!_.isObject(obj)) {
    return obj;
  }
  var sorted = {};
  _.each(_.keys(obj).sort(), function(key) {
    sorted[key] = sortByKeys(obj[key]);
  });
  return sorted;
};

var sortedStringify = function() {
    arguments[0] = sortByKeys(arguments[0]);
    return JSON.stringify.apply(this, arguments);
};

var orderedStringify = function(obj) {
    if (_.isArray(obj)) {
        var parts = [];
        obj.forEach(function(child) {
            parts.push(orderedStringify(child));
        });
        return '[' + parts.join(',') + ']'
    } else if (_.isObject(obj)) {
        var parts = [],
            keys = _.keys(obj).sort();
        
        keys.forEach(function(key) {
            var value = obj[key];
            if (value === undefined) return
            parts.push(JSON.stringify(key));
            parts.push(':')
            parts.push(orderedStringify(value));
            parts.push(',');
        });
        parts.splice(-1);
        return '{' + parts.join('') + '}';
    }
    if (obj === undefined) {
        return "null"
    }
    return JSON.stringify(obj);
}
