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
