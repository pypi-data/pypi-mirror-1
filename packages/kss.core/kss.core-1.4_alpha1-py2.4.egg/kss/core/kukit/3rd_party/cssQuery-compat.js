
/* cssQuery drop-in replacement
 * 
 * You need to include this, when you use base2 and you don't
 * want to use cssQuery.
 *
 * When both cssQuery and base2 are present, this code does nothing.
 * When cssQuery is missing, this code defines a compatibility cssQuery
 * function that actually reuses base2 for querying.
 *
 */

if (typeof(window.cssQuery) == 'undefined') {
    // Define the compatibility layer.
    window.cssQuery = function(selector, element) {
        if (typeof(element) == 'undefined') {
            // if parameter is not given, we need to use document.
            element = document;
        }
        var results = base2.DOM.Document.matchAll(element, selector);
        var nodes = [];
        for(var i = 0; i < results.length; i++) {
            nodes.push(results.item(i));
        }
        return nodes;
    };
};

