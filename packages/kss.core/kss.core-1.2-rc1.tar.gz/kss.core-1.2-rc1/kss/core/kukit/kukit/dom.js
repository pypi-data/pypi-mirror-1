/*
* Copyright (c) 2005-2007
* Authors: KSS Project Contributors (see docs/CREDITS.txt)
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

/* Generic dom helpers */

kukit.dom = {};

kukit.dom.getPreviousSiblingTag = function(node) {
    var toNode = node.previousSibling;
    while ((toNode != null) && (toNode.nodeType != 1)) {
        toNode = toNode.previousSibling;
    }
    return toNode;
};

kukit.dom.getNextSiblingTag = function(node) {
    var toNode = node.nextSibling;
    while ((toNode != null) && (toNode.nodeType != 1)) {
        toNode = toNode.nextSibling;
    }
    return toNode;
};

kukit.dom.insertBefore = function(nodeFrom, parentNode, nodeTo) {
    var ownerDoc = nodeTo.nodeType == Node.DOCUMENT_NODE ? nodeTo : nodeTo.ownerDocument;
    var nodes = nodeFrom.childNodes;
    var result = new Array();
    if(ownerDoc.importNode && (!kukit.HAVE_IE)) {
        for(var i=0;i < nodes.length;i++) {
            result[i] = parentNode.insertBefore(ownerDoc.importNode(nodes[i], true), nodeTo);
        }
    } else {
        for(var i=0;i < nodes.length;i++) {
            result[i] = parentNode.insertBefore(nodes[i].cloneNode(true), nodeTo);
        }
    }
    return result;
};

kukit.dom.appendChildren = function(nodes, toNode) {
    var ownerDoc = toNode.nodeType == Node.DOCUMENT_NODE ? toNode : toNode.ownerDocument;
    var result = new Array();
    if(ownerDoc.importNode && (!kukit.HAVE_IE)) {
        for(var i=0;i < nodes.length;i++) {
            result[i] = toNode.appendChild(ownerDoc.importNode(nodes[i], true));
        }
    }else{
        for(var i=0;i < nodes.length;i++) {
            result[i] = toNode.appendChild(nodes[i].cloneNode(true));
        }
    }
    return result;
};

kukit.dom.clearChildNodes = function(node) {
    //Maybe we want to get rid of sarissa once?
    Sarissa.clearChildNodes(node);
};

kukit.dom.forceToDom = function(param) {
    // This is a dirty helper to avoid rewriting existing stuff.
    // If param is not a dom, it converts to it.
    // This is to assure that all methods that accept a dom can accept a string
    // instead.
    if (typeof(param) == 'string') {
        //
        // now convert to dom
        //
        
        //param = "<option>test_xmlentity</option><option>tic</option><option>tac&#32;toe</option>";
        // ***BROKEN*** param = "<option>test_htmlentity</option><option>tic</option><option>tac&nbsp;toe</option>";
        //param = "<option>test_utf8</option><option>tic</option><option>tacűtoe</option>";

        // This is a good solution since it does not do magic to
        // our html - BUT html is parsed as xml
        // so we currently preprocess it on the server
        // and remove html named entities from it.
        //
        var root_txt = '<html xmlns="http://www.w3.org/1999/xhtml"><div>' + param + '</div></html>';
        var doc = (new DOMParser()).parseFromString(root_txt, "text/xml");
        var root = doc.getElementsByTagName('div')[0];

        // XXX Sarissa bug; html docs would not have a
        // working serialize, and so importNodes would fail on them.
        // XXX Fixed in: Revision 1.23  - Sun Jul 10 18:53:53 2005 UTC
        // use at least 0.9.6.1
        
        param = root;
    }
    // Need to do this or else IE fails miserably.
    // importNode acts strangely.
    // on FF, you can execute it several times but the next condition
    //        always evaluated to False.
    // on IE, it is a big problem to execute this for the second time
    //        but it needs to be executed once, thus the condition
    if (param.ownerDocument != document) {
        param = document.importNode(param, true);
    }
    //alert(Sarissa.serialize(param));
    return param;
};

/*
*  really the query should start from the document root, but
*  limited to in_nodes subtrees!
*/


kukit.dom.cssQuery = function(selector, in_nodes) {
    // to eliminate possible errors
    if (typeof(in_nodes) != 'undefined' && in_nodes == null) {
        ;;; kukit.E = 'Selection error in kukit.dom.cssQuery';
        throw kukit.E;
    }
    return kukit.dom._cssQuery(selector, in_nodes);
};

/*
 * Decide which query to use
 */

kukit.dom._cssQuery = function(selector, in_nodes) {
    var USE_BASE2 = (typeof(base2) != 'undefined');
    if (USE_BASE2) {
        ;;; kukit.log('Using cssQuery from base2');
        kukit.dom._cssQuery = kukit.dom._cssQuery_base2
    } else {
        ;;; kukit.log('Using original cssQuery');
        kukit.dom._cssQuery = kukit.dom._cssQuery_orig
    }
    return kukit.dom._cssQuery(selector, in_nodes);
};

kukit.dom._cssQuery_base2 = function(selector, in_nodes) {
    // global scope, always.
    // This is very bad. However the binding makes sure that
    // nodes once bound will never be bound again
    // (also, noticed the following issue: cssQuery, when called
    // on an element, does not check the element itself.)
    var results = base2.DOM.Document.matchAll(document, selector);
    var nodes = [];
    for(var i = 0; i < results.length; i++) {
        nodes.push(results.item(i));
    }
    return nodes;
};

kukit.dom._cssQuery_orig = function(selector, in_nodes) {
    // global scope, always.
    // This is very bad. However the binding makes sure that
    // nodes once bound will never be bound again
    // (also, noticed the following issue: cssQuery, when called
    // on an element, does not check the element itself.)
    var results = cssQuery(selector);
    return results;
};

kukit.dom.focus = function(node) {
    tagName = node.tagName.toLowerCase();
    if ((tagName == 'input') || (tagName == 'select') || (tagName == 'textarea')) {
        node.focus();
    ;;; } else {
    ;;;     kukit.logWarning('Focus on node that cannot have focus !');
    }
};

/*
*  Gets the textual content of the node
*  if recursive=false (default), does not descend into sub nodes
*/
kukit.dom.textContent = function(node, recursive) {
    var value = kukit.dom._textContent(node, recursive);
    // replace newline with spaces
    value = value.replace(/\r\n/g, ' ');
    value = value.replace(/[\r\n]/g, ' ');
    return value;
};

kukit.dom._textContent = function(node, recursive) {
    if (typeof(recursive) == 'undefined') {
        recursive = false;
    }
    var value = '';
    var childnodes = node.childNodes;
    for (var i=0; i<childnodes.length; i++) {
        var child = childnodes[i];
        if (child.nodeType == 3) {
            // Only process text nodes
            value += child.nodeValue;
        } else if (recursive && child.nodeType == 1) {
            // recurr into element nodes
            value += kukit.dom.textContent(child, true);
        }
    }
    return value;
};

/* Getting and setting node attibutes 
   We need to provide workarounds for IE.
*/

kukit.dom.getAttribute = function(node, attrname) {
    if (attrname.toLowerCase() == 'style') {
        throw 'Style attribute is not allowed with getAttribute';
    }
    // Try first, there is chance that it works
    // XXX this works but not for kukit:xxx args
    //var value = node[argname];
    var value = node.getAttribute(attrname);
    if (! value) {
        // Workarounds, in case we have not found above
        if (attrname.toLowerCase() == 'class') {
            // for IE
            value = node.className;
        } else if (attrname.toLowerCase() == 'for') {
            // for IE
            value = node.htmlFor;
        }
    }
    return value;
    // XXX We cannot distinguish between notfound and '', unfortunately
};

kukit.dom.setAttribute = function(node, attrname, value) {
    if (attrname.toLowerCase() == 'style') {
        throw 'Style attribute is not allowed with setAttribute';
    }
    else if (attrname.toLowerCase() == 'class') {
        // The class attribute cannot be set on IE, instead
        // className must be used. However node.className = x
        // works on both IE and FF.
        node.className = value;
    } else if (attrname.toLowerCase() == 'for') {
        // On IE, workaround is needed. Since I am not sure, I use both methods.
        node.htmlFor = value;
        node.setAttribute(attrname, value);
    } else if (attrname.toLowerCase() == 'checked') {
        // we need to convert this to boolean.
        value = ! (value == '' || value == 'false' || value == 'False');
        node.checked = value;
    } else {
        node.setAttribute(attrname, value);
    }
};


/* KSS attributes: a workaround to provide attributes
   in our own namespace.
   Since namespaced attributes (kss:name="value") are not allowed
   even in transitional XHTML, we must provide a way to
   substitute them. This is achieved by putting kssattr-name-value
   identifiers in the class attribute, separated by spaces.
   We only read these attributes, writing happens
   always in the kss namespace.
   XXX at the moment, deletion can be achieved with setting with
   a value ''. This is consistent with DOM behaviour as we seem to
   be getting '' for nonexistent values anyway.
*/

kukit.dom.kssAttrNamespace = 'kssattr';

kukit.dom.getKssClassAttribute = function(node, attrname) {
    // Gets a given kss attribute from the class
    var klass = kukit.dom.getAttribute(node, 'class');
    var result = null;
    if (klass) {
        var splitclass = klass.split(/ +/);
        for (var i=0; i<splitclass.length; i++) {
            var elem = splitclass[i];
            var splitelem = elem.split('-', 3);
            if (splitelem.length == 3 && splitelem[0] == kukit.dom.kssAttrNamespace
                    && splitelem[1] == attrname) {
                // Found it. (The last one will be valid, in case of duplication)
                var index = splitelem[0].length + splitelem[1].length + 2;
                result = elem.substr(index);
            }

        }
    }
    return result;
};

kukit.dom.getKssAttribute = function(node, attrname) {
    // Gets a given kss attribute 
    // first from the namespace, then from the class
    var result = kukit.dom.getAttribute(node, kukit.dom.kssAttrNamespace + ':' + attrname);
    // XXX if this was '' it is the same as notfound, so it shadows the class attribute!
    // This means setting an attribute to '' is the same as deleting it - at the moment
    if (! result) {
        result = kukit.dom.getKssClassAttribute(node, attrname);
    }
    return result;
};

kukit.dom.setKssAttribute = function(node, attrname, value) {
    // Sets a given kss attribute on the namespace
    kukit.dom.setAttribute(node, kukit.dom.kssAttrNamespace + ':' + attrname, value);
};

/* Recursive getting of node attributes
   getter is a function that gets the value from the node.
*/

kukit.dom.getRecursiveAttribute = function(node, attrname, recurseParents, getter) {
    var value = getter(node, attrname);
    if (recurseParents) {
        var element = node;
        // need to recurse even if value="" ! We cannot figure out if there exists
        // and attribute in a crossbrowser way, or it is set to "".
        while (! value) {
            element = element.parentNode;
            if (! element || ! element.getAttribute) {
                break;
            }
            value = getter(element, attrname);
        }
    } 
    if (typeof(value) == 'undefined') {
        // notfound arguments will get null
        value = null;
    }
    return value;
};



/*
*  class EmbeddedContentLoadedScheduler
*
*  Scheduler for embedded window content loaded
*/
kukit.dom.EmbeddedContentLoadedScheduler = function(framename, func, autodetect) {
    this.framename = framename;
    this.func = func;
    this.autodetect = autodetect;
    var self = this;
    var f = function() {
        self.check();
    };
    this.counter = new kukit.ut.TimerCounter(250, f, true);
    // check immediately.
    //this.counter.timeout();
    // XXX can't execute immediately, it fails on IE.
    this.counter.start();
};

/*
* From http://xkr.us/articles/dom/iframe-document/
* Note it's not necessary for the iframe to have the name
* attribute since we don't access it from window.frames by name.
*/
kukit.dom.getIframeDocument = function(framename) {
    var iframe = document.getElementById(framename);
    var doc = iframe.contentWindow || iframe.contentDocument;
    if (doc.document) {
        doc = doc.document;
    }
    return doc;
};

kukit.dom.EmbeddedContentLoadedScheduler.prototype.check = function() {
    
    ;;; kukit.logDebug('Is iframe loaded ?');
    
    var doc = kukit.dom.getIframeDocument(this.framename);

    // quit if the init function has already been called
    // XXX I believe we want to call the function too, then
    // XXX attribute access starting with _ breaks full compression, even in strings
    //if (doc._embeddedContentLoadedInitDone) {
    if (doc['_' + 'embeddedContentLoadedInitDone']) {
        ;;; kukit.logWarning('Iframe already initialized, but we execute the action anyway, as requested.');
        this.counter.restart = false;
    }

    // autodetect=false implements a more reliable detection method
    // that involves cooperation from the internal document. In this
    // case the internal document sets the _kssReadyForLoadEvent attribute
    // on the document, when loaded. It is safe to check for this in any 
    // case, however if this option is selected, we rely only on this, 
    // and skip the otherwise problematic default checking.
    // XXX attribute access starting with _ breaks full compression, even in strings
    //if (typeof doc._kssReadyForLoadEvent != 'undefined') {
    if (typeof doc['_' + 'kssReadyForLoadEvent'] != 'undefined') {
        this.counter.restart = false;
    } 

    if (this.autodetect && this.counter.restart) {

        // obviously we are not there... this happens on FF
        if (doc.location.href == 'about:blank') {
            return;
        } /* */
        
        // First check for Safari or
        //if DOM methods are supported, and the body element exists
        //(using a double-check including document.body, for the benefit of older moz builds [eg ns7.1] 
        //in which getElementsByTagName('body')[0] is undefined, unless this script is in the body section)
        
        if(/KHTML|WebKit/i.test(navigator.userAgent)) {
            if(/loaded|complete/.test(doc.readyState)) {
                this.counter.restart = false;
            }
        } else if(typeof doc.getElementsByTagName != 'undefined' && (doc.getElementsByTagName('body')[0] != null || doc.body != null)) {
            this.counter.restart = false;
        } /* */

    }

    if ( ! this.counter.restart) {
        ;;; kukit.logDebug('Yes, iframe is loaded.');
        // XXX attribute access starting with _ breaks full compression, even in strings
        // doc._embeddedContentLoadedInitDone = true;
        doc['_' + 'embeddedContentLoadedInitDone'] = true;
        this.func();
    }
};

kukit.dom.getNsTags = function(dom, tagName) {
    if (dom.getElementsByTagNameNS) { 
        tags = dom.getElementsByTagNameNS('http://www.kukit.org/commands/1.0',
            tagName);
    } else {
        //IE does not know DOM2
        tags = dom.getElementsByTagName('kukit:' + tagName);
    }
    return tags;
};

