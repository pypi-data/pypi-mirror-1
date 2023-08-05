/*
* Copyright (c) 2005-2006
# Authors: KSS Project Contributors (see docs/CREDITS.txt)
*
* This program is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License version 2 as published
* by the Free Software Foundation.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
* 02111-1307, USA.
*/

kukit.sr = {};

// Registry of the pprovider functions for selecting

kukit.sr.pproviderSelRegistry = new kukit.pr.ParamProviderRegistry();


// this will provide an arbitrary selector, and is designed to
// be used with the makeAnyPP factory function.
kukit.sr.AnyPP = function() {};
kukit.sr.AnyPP.prototype = {
    /*
    ;;; */
    check: function(args) {
        // check does not need to be used here actually.
        if (args.length != 1) {
            throw 'internal error, xxxselector() needs 1 argument';
        }
    },
    /*
    */
    eval: function(args, node, defaultparms) {
        var f = kukit.selectorTypesGlobalRegistry.get(this.selector_type);
        // We don't have orignode if we evaluate from here, consequently
        // the orignode parameter cannot be used from selectors. We pass
        // node just to be sure...
        return f(args[0], node, defaultparms, node);
    }
};

kukit.sr.pproviderSelRegistry.register('', kukit.sr.AnyPP);

kukit.sr.makeAnyPP = function(selector_type) {
    var pp = function () {};
    pp.prototype.eval = kukit.sr.AnyPP.prototype.eval;
    ;;; pp.prototype.check = kukit.sr.AnyPP.prototype.check;
    pp.prototype.selector_type = selector_type;
    return pp;
};

// this can be used to pass a node programmatically
kukit.sr.PassnodePP = function() {};
kukit.sr.PassnodePP.prototype = {
    /*
    ;;; */
    check: function(args) {
        if (args.length != 1) {
            throw 'passnode selector method needs 1 argument';
        }
    },
    /*
    */
    eval: function(args, node, defaultparms) {
        var value = defaultparms[args[0]];
        if (typeof(value) == 'undefined') {
            // notfound arguments will get null
            ;;; kukit.E = 'Nonexistent default parm "'+ key +'"';
            throw kukit.E;
        }
        nodes = [value];
        return nodes;
    }
};
kukit.sr.pproviderSelRegistry.register('passnode', kukit.sr.PassnodePP);


/* 
* class SelectorTypeRegistry 
*
*  available for plugin registration
*
*  usage:
*
*  kukit.selectorTypesGlobalRegistry.register(name, func);
*
*/
kukit.sr.SelectorTypeRegistry = function () {
    this.mapping = {};
};

kukit.sr.SelectorTypeRegistry.prototype.defaultSelectorType = 'css';

kukit.sr.SelectorTypeRegistry.prototype.register = function(name, func) {
    if (typeof(func) == 'undefined') {
        throw 'Func is mandatory.';
    }
    ;;; if (this.mapping[name]) {
    ;;;    // Do not allow redefinition
    ;;;    kukit.logError('Error : redefinition attempt of selector ' + name);
    ;;;    return;
    ;;; }
    this.mapping[name] = func;
    // Also register the selector param provider
    var pp = kukit.sr.makeAnyPP(name);
    kukit.sr.pproviderSelRegistry.register(name, pp);
};

kukit.sr.SelectorTypeRegistry.prototype.get = function(name) {
    if (! name) {
        // if name is null or undefined or '',
        // we use the default type.
        name = this.defaultSelectorType;
    }
    var result = this.mapping[name];
    ;;; if (typeof(result) == 'undefined') {
    ;;;    throw 'Unknown selector type "' + name + '"';
    ;;; }
    return result;
};

kukit.selectorTypesGlobalRegistry = new kukit.sr.SelectorTypeRegistry();

kukit.selectorTypesGlobalRegistry.register('htmlid', function(expr, node) {
    var nodes = [];
    var node = document.getElementById(expr);
    if (node) {
        nodes.push(node);
        }
    return nodes;
});

kukit.selectorTypesGlobalRegistry.register('css', function(expr, node) {
    // Always search globally
    var nodes = kukit.dom.cssQuery(expr);
    return nodes;
});

kukit.selectorTypesGlobalRegistry.register('samenode', function(expr, node) {
    nodes = [node];
    return nodes;
});

// Return a list of all nodes that match the css expression in the parent chain
kukit.selectorTypesGlobalRegistry.register('parentnode', function(expr, node) {
    var selectednodes = kukit.dom.cssQuery(expr);
    var parentnodes = [];
    var parentnode = node.parentNode;
    while(parentnode.parentNode) {
        parentnodes.push(parentnode);
        parentnode = parentnode.parentNode;
    }

    // Filter the nodes so that only the ones in the parent chain remain
    var results = [];
    for(var i=0; i<selectednodes.length; i++){
        var inchain = false;
        for(var j=0; j<parentnodes.length; j++){
            if(selectednodes[i] === parentnodes[j]){
                inchain = true;
            }
        }
        if(inchain){
            results.push(selectednodes[i]);
        }
    }
    return results;
});
