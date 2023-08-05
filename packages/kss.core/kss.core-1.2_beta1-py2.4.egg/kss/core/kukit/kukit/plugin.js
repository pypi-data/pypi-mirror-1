/*
* Copyright (c) 2005-2006
* Authors:
*   Godefroid Chapelle <gotcha@bubblenet.be>
*   Florian Schulze <florian.schulze@gmx.net>
*   Balázs Reé <ree@greenfinity.hu>
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

/* Core plugins and utilities */

kukit.pl = {};

/* 
* Event plugins 
* 
* __trigger_event__(name, parms, node)
* is a method bound to each class, so methods can call
* it up to call an event action bound through kss.
*
* The event binder hooks
* __bind__(name, parms, func_to_bind)
* should be defined to make binding of event to the given function.
*
* The event action hooks
* __exec__(name, parms, node)
* can be defined to specify a default event action.
*/

kukit.pl.getTargetForBrowserEvent = function(e) {
    // this prevents the handler to be called on wrong elements, which
    // can happen because of propagation or bubbling
    // XXX this needs to be tested in all browsers
    if (!e) var e=window.event;
    var target = null;
    if (e.target) {
        target = e.target;
    } else if (e.srcElement) {
        target = e.srcElement;
    }
    /* ???
    if (e.currentTarget)
        if (target != e.currentTarget)
            target = null;*/
    return target;
};

/*
* class NativeEventBinder
*/
kukit.pl.NativeEventBinder = function() {
};

kukit.pl.NativeEventBinder.prototype.__bind__node = function(name, func_to_bind, oper) {
    if (oper.node == null) {
        throw 'Native event "' + name + '"must be bound to a node.';
    }
    this.__bind__(name, func_to_bind, oper);
};

kukit.pl.NativeEventBinder.prototype.__bind__nodeorwindow = function(name, func_to_bind, oper) {
    if (oper.node == null) {
        oper.node = window;
    }
    this.__bind__(name, func_to_bind, oper);
};

kukit.pl.NativeEventBinder.prototype.__bind__window = function(name, func_to_bind, oper) {
    if (oper.node != null) {
        throw 'Native event "' + name + '"must not be bound to a node.';
    }
    oper.node = window;
    this.__bind__(name, func_to_bind, oper);
};

kukit.pl.NativeEventBinder.prototype.__bind__nodeordocument = function(name, func_to_bind, oper) {
    if (oper.node == null) {
        oper.node = document;
    }
    this.__bind__(name, func_to_bind, oper);
};

kukit.pl.NativeEventBinder.prototype.__bind__ = function(name, func_to_bind, oper) {
    oper.completeParms([], {'preventdefault': '', 'allowbubbling': ''}, 'native event binding');
    oper.evalBool('preventdefault', 'native event binding');
    oper.evalBool('allowbubbling', 'native event binding');
    if (oper.parms.preventdefault) {
        if (name != 'click') {
            throw 'In native events only the click event can have preventdefault.';
        }
    }
    var allowbubbling = oper.parms.allowbubbling;
    var preventdefault = oper.parms.preventdefault;
    var node = oper.node;
    var func = function(e) {
        target = kukit.pl.getTargetForBrowserEvent(e);
        if (allowbubbling || target == node) {
            // Execute the action, provide browserevent on oper
            // ... however, do it protected. We want the preventdefault
            // in any case!
            var exc;
            try {
                func_to_bind({'browserevent': e});
            } catch(exc1) {
                exc = exc1;    
            }
            // Cancel default event ?
            if (preventdefault) {
                // W3C style
                if (e.preventDefault)
                    e.preventDefault();
                // MS style
                try { e.returnValue = false; } catch (exc2) {}
            }
            if (exc != null) {
                // throw the original exception
                throw exc;
            }
        } else {
            kukit.log('Ignored bubbling event for "' + name + '" (target =' + target.tagName + '), EventRule #' + oper.eventrule.getNr() + ' mergeid ' + oper.eventrule.kss_selector.mergeid); 
        }
    };
    kukit.ut.registerEventListener(node, name, func);
    // XXX Safari hack
    // necessary since Safari does not prevent the <a href...> following
    // (in case of allowbubbling we have to apply it to all clicks, as there
    // might be a link inside that we cannot detect on the current node)
    if (preventdefault && kukit.HAVE_SAFARI 
            && (allowbubbling || name == 'click' && node.tagName.toLowerCase() == 'a')) {
        function cancelClickSafari() {
            return false;
        }
        node.onclick = cancelClickSafari;
    }
};

kukit.pl.NativeEventBinder.prototype.__bind_key__ = function(name, func_to_bind, oper) {
    oper.completeParms([], {'preventdefault': 'true', 'allowbubbling': '', 'keycodes': ''},  'native key event binding');
    oper.evalList('keycodes', 'native key event binding');
    oper.evalBool('preventdefault', 'native key event binding');
    oper.evalBool('allowbubbling', 'native key event binding');
    var allowbubbling = oper.parms.allowbubbling;
    var preventdefault = oper.parms.preventdefault;
    var node = oper.node;
    // Convert keyCode to dict
    var keycodes = {};
    for (var i=0; i<oper.parms.keycodes.length; i++) {
        keyCode = oper.parms.keycodes[i];
        keycodes[keyCode] = true;
    }
    var func = function(e) {
        target = kukit.pl.getTargetForBrowserEvent(e);
        if (allowbubbling || target == node) {
            var keyCode = e.keyCode.toString();
            if (oper.parms.keycodes.length == 0 || keycodes[keyCode]) {         
                // Execute the action, provide browserevent on oper
                func_to_bind({'browserevent': e});
                // Cancel default event
                if (preventdefault) {
                    // W3C style
                    if (e.preventDefault)
                        e.preventDefault();
                    // MS style
                    try { e.returnValue = false; } catch (exc) {}
                }
            } else {
                kukit.log('Ignored event for "' + name + '", keycode ' + e.keyCode + ' not in ' + oper.parms.keycodes);
            }
        } else {
            kukit.log('Ignored bubbling event for "' + name + '" (target =' + target.tagName + '), EventRule #' + oper.eventrule.getNr() + ' mergeid ' + oper.eventrule.kss_selector.mergeid); 
        }
    };
    kukit.ut.registerEventListener(node, name, func);
};

/*
*  Registration of all the native events that can bound to a node or to document 
*  (= document or window, depending on the event specs)
*  Unsupported are those with absolute no hope to work in a cross browser way
*  Preventdefault is only allowed for click, currently
*/
kukit.eventsGlobalRegistry.register(null, 'blur', kukit.pl.NativeEventBinder, '__bind__nodeorwindow', null);
kukit.eventsGlobalRegistry.register(null, 'focus', kukit.pl.NativeEventBinder, '__bind__nodeorwindow', null);
kukit.eventsGlobalRegistry.register(null, 'resize', kukit.pl.NativeEventBinder, '__bind__nodeorwindow', null);
kukit.eventsGlobalRegistry.register(null, 'click', kukit.pl.NativeEventBinder, '__bind__nodeordocument', null);
kukit.eventsGlobalRegistry.register(null, 'dblclick', kukit.pl.NativeEventBinder, '__bind__node', null);
kukit.eventsGlobalRegistry.register(null, 'mousedown', kukit.pl.NativeEventBinder, '__bind__nodeordocument', null);
kukit.eventsGlobalRegistry.register(null, 'mouseup', kukit.pl.NativeEventBinder, '__bind__nodeordocument', null);
kukit.eventsGlobalRegistry.register(null, 'mousemove', kukit.pl.NativeEventBinder, '__bind__nodeordocument', null);
kukit.eventsGlobalRegistry.register(null, 'mouseover', kukit.pl.NativeEventBinder, '__bind__node', null);
kukit.eventsGlobalRegistry.register(null, 'mouseout', kukit.pl.NativeEventBinder, '__bind__node', null);
kukit.eventsGlobalRegistry.register(null, 'change', kukit.pl.NativeEventBinder, '__bind__node', null);
kukit.eventsGlobalRegistry.register(null, 'reset', kukit.pl.NativeEventBinder, '__bind__node', null);
kukit.eventsGlobalRegistry.register(null, 'select', kukit.pl.NativeEventBinder, '__bind__node', null);
kukit.eventsGlobalRegistry.register(null, 'submit', kukit.pl.NativeEventBinder, '__bind__node', null);
kukit.eventsGlobalRegistry.register(null, 'keydown', kukit.pl.NativeEventBinder, '__bind_key__', null);
kukit.eventsGlobalRegistry.register(null, 'keypress', kukit.pl.NativeEventBinder, '__bind_key__', null);
kukit.eventsGlobalRegistry.register(null, 'keyup', kukit.pl.NativeEventBinder, '__bind_key__', null);
//kukit.eventsGlobalRegistry.register(null, 'unload', kukit.pl.NativeEventBinder, '__bind__window', null);

/*
* class TimeoutEventBinder
*
*  Timer events. The binding of this event will start one counter
*  per event rule. No matter how many nodes matched it. 
*  The timer will tick for ever,
*  unless the binding node has been deleted, in which case it stops,
*  or it runs only once if repeat=false is given.
*/
kukit.pl.TimeoutEventBinder = function() {
    this.counters = {};
};

kukit.pl.TimeoutEventBinder.prototype.__bind__ = function(name, func_to_bind, oper) {
    oper.completeParms(['delay'], {'repeat': 'true'}, 'timeout event binding');
    oper.evalBool('repeat', 'timeout event binding');
    var key = oper.eventrule.getNr();
    if (oper.parms.repeat && this.counters[key]) {
        // Don't bind the counter if we matched this eventrule already
        // (this is only checked if this event is repeating)
        kukit.logDebug('timer event key ignored for actionEvent #' + key + ' ' 
            + oper.eventrule.kss_selector.css);
    } else {   
        kukit.logDebug('timer event key entered for actionEvent #' + key + ' ' 
            + oper.eventrule.kss_selector.css);
        var f = function() {
            // check if the node has been deleted
            // and weed it out if so
            if (oper.node != null && ! oper.node.parentNode) {
                kukit.logDebug('timer deleted for actionEvent #' + key + ' ' 
                    + oper.eventrule.kss_selector.css);
                this.clear();
            } else {
                func_to_bind();
            }
        };
        var counter = new kukit.ut.TimerCounter(oper.parms.delay, f, oper.parms.repeat); 
        this.counters[key] = counter;
        // Start the counter
        counter.start();
    }
};

kukit.eventsGlobalRegistry.register(null, 'timeout', kukit.pl.TimeoutEventBinder, '__bind__', null);

/*
* class LoadEventBinder
*/
kukit.pl.LoadEventBinder = function() {
};

kukit.pl.LoadEventBinder.prototype.__bind__ = function(name, func_to_bind, oper) {
    oper.completeParms([], {'initial': 'true', 'insert': 'true'}, 'load event binding');
    oper.evalBool('initial', 'load event binding');
    oper.evalBool('insert', 'load event binding');
    // Bind the function to the onload event of the node.
    // If this is an iframe node, we have the possibility
    // to wait until the execution totally finishes, so we load the real load event.
    // node._kukitmark contains the binding phase.
    var phase = oper.node._kukitmark;
    if (phase == 1 && ! oper.parms.initial) {
        kukit.logDebug('EventRule #' + oper.eventrule.getNr() + ' mergeid ' + oper.eventrule.kss_selector.mergeid + ' event ignored, oninitial=false.');
        return;
    }
    if (phase == 2 && ! oper.parms.insert) {
        kukit.logDebug('EventRule #' + oper.eventrule.getNr() + ' mergeid ' + oper.eventrule.kss_selector.mergeid + ' event ignored, oninsert=false.');
        return;
    }
    if (oper.node != null && oper.node.tagName.toLowerCase() == 'iframe' &&
              (phase == 2 || (phase == 1 && kukit.engine.initializedOnDOMLoad))) {
        kukit.logDebug('EventRule #' + oper.eventrule.getNr() + ' mergeid ' + oper.eventrule.kss_selector.mergeid + ' event selected delayed execution (when iframe loaded)');
        // We want the event execute once the iframe is loaded.
        var f = function() {
            kukit.engine.bindScheduler.addPost(func_to_bind, 'Execute load event for iframe ' + oper.node.name);
        };
        new kukit.dom.EmbeddedContentLoadedScheduler(oper.node.id, f);

    } else {
        kukit.logDebug('EventRule #' + oper.eventrule.getNr() + ' mergeid ' + oper.eventrule.kss_selector.mergeid + ' event selected normal postponed execution.');
        // for any other node than iframe, or even for iframe in phase1, we need to execute immediately.
        kukit.engine.bindScheduler.addPost(func_to_bind, 'Execute load event for node ' + oper.node.tagName.toLowerCase());
    }
};

kukit.eventsGlobalRegistry.register(null, 'load', kukit.pl.LoadEventBinder, '__bind__', null);

/*
* class SpinnerEventBinder
*
* Spinner support. Besides the event itself we use some utility
* classes to introduce lazyness (delay) for the spinner.
*/
kukit.pl.SpinnerEventBinder = function() {
    this.state = false;
    var self = this;
    var timeoutSetState = function(spinnerevent) {
       self.timeoutSetState(spinnerevent);
    };
    this.scheduler = new kukit.ut.Scheduler(timeoutSetState);
};

kukit.pl.SpinnerEventBinder.prototype.__bind__ = function(name, func_to_bind, oper) {
    oper.completeParms([], {'laziness': 0}, 'spinner event binding');
    oper.evalInt('laziness', 'spinner event binding');
    // Register the function with the global queue manager
    var state_to_bind = (name == 'spinneron');
    var self = this;
    var func = function() {
        self.setState(func_to_bind, state_to_bind, oper.parms.laziness);
    };
    kukit.engine.requestManager.registerSpinnerEvent(func, state_to_bind);
};

kukit.pl.SpinnerEventBinder.prototype.setState = function(func_to_bind, state, laziness) {
    // This is called when state changes. We introduce laziness
    // before calling the func.
    this.func_to_bind = func_to_bind;
    this.state = state;
    var now = (new Date()).valueOf();
    var wakeUp = now + laziness;
    this.scheduler.setNextWakeAtLeast(wakeUp);
};

kukit.pl.SpinnerEventBinder.prototype.timeoutSetState = function() {
    // really call the bound actions which should set the spinner
    this.func_to_bind();
};

kukit.eventsGlobalRegistry.register(null, 'spinneron', kukit.pl.SpinnerEventBinder, '__bind__', null);
kukit.eventsGlobalRegistry.register(null, 'spinneroff', kukit.pl.SpinnerEventBinder, '__bind__', null);


/* Core actions
*
* The core client actions that can be executed on the client
* side.
*
* They also get registered as commands
*/
kukit.actionsGlobalRegistry.register("error", function (oper) {
    throw 'The builtin error action should never execute.';
    }
);
kukit.commandsGlobalRegistry.registerFromAction('error', kukit.cr.makeGlobalCommand);

kukit.actionsGlobalRegistry.register("logDebug", function (oper) {
    oper.completeParms([], {'message': 'LogDebug action'}, 'logDebug action');
    var node = oper.node;
    var nodeName = '<DOCUMENT>';
    if (node != null) {
        nodeName = node.nodeName;
    }
    var message = oper.parms.message;
    if (oper.eventrule) {
        message = message + ', event=' + oper.eventrule.kss_selector.name + ', rule=#' + oper.eventrule.getNr() + ', node=' + nodeName; 
    }
    kukit.logDebug(message); 
    if (kukit.hasFirebug) {
        kukit.logDebug(oper.node);
    }
});
kukit.commandsGlobalRegistry.registerFromAction('logDebug', kukit.cr.makeGlobalCommand);

kukit.actionsGlobalRegistry.register("log", function (oper) {
    oper.completeParms([], {'message': 'Log action'}, 'log action');
    var node = oper.node;
    var nodeName = '<DOCUMENT>';
    if (node != null) {
        nodeName = node.nodeName;
    }
    var message = oper.parms.message;
    if (oper.eventrule) {
        message = message + ', event=' + oper.eventrule.kss_selector.name + ', rule=#' + oper.eventrule.getNr() + ', node=' + nodeName; 
    }
    kukit.log(message);
});
kukit.commandsGlobalRegistry.registerFromAction('log', kukit.cr.makeGlobalCommand);

kukit.actionsGlobalRegistry.register("alert", function (oper) {
    oper.completeParms([], {'message': 'Alert action'}, 'alert action');
    var node = oper.node;
    var nodeName = '<DOCUMENT>';
    if (node != null) {
        nodeName = node.nodeName;
    }
    var message = oper.parms.message;
    if (oper.eventrule) {
        message = message + ', rule=#' + oper.eventrule.getNr() + ', node=' + nodeName; 
    }
    alert(message);
});
kukit.commandsGlobalRegistry.registerFromAction('alert', kukit.cr.makeGlobalCommand);

/* Core commands 
*
* All the commands are also client actions.
*/

kukit.actionsGlobalRegistry.register('replaceInnerHTML', function(oper) {
/*
*  accepts both string and dom.
*/
    oper.completeParms(['html'], {},
                       'replaceInnerHTML action');
    var node = oper.node;
    var inserted;
    if (typeof(oper.parms.html) == 'string') {
        node.innerHTML = oper.parms.html;
        inserted = node.childNodes; 
    } else {
        oper.parms.html = kukit.dom.forceToDom(oper.parms.html);
        kukit.dom.clearChildNodes(node);
        inserted = kukit.dom.appendChildren(oper.parms.html.childNodes, node);
    }
    kukit.engine.setupEvents(inserted);
});
kukit.commandsGlobalRegistry.registerFromAction('replaceInnerHTML', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('replaceHTML', function(oper) {
/*
*  accepts both string and dom.
*/
    oper.completeParms(['html'], {}, 'replaceHTML action');
    var node = oper.node;
    oper.parms.html = kukit.dom.forceToDom(oper.parms.html);
    var elements = oper.parms.html.childNodes;
    var length = elements.length;
    if (length > 0) {
        var parentNode = node.parentNode;
        var insertedNodes = [];
        // insert the last node
        var next = elements[length-1];
        parentNode.replaceChild(next, node);
        insertedNodes.push(next);
        // then we go backwards with the rest of the nodes
        for (var i=length-2; i>=0; i--) {
            var inserted = parentNode.insertBefore(elements[i], next);
            insertedNodes.push(inserted);
            next = inserted;
        }
        kukit.engine.setupEvents(insertedNodes);
    }
});
kukit.commandsGlobalRegistry.registerFromAction('replaceHTML', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('setAttribute', function(oper) {
    oper.completeParms(['name', 'value'], {}, 'setAttribute action');
    if (oper.parms.name.toLowerCase() == 'style') {
        throw 'Style attribute is not allowed with setAttribute';
    }
    kukit.dom.setAttribute(oper.node, oper.parms.name, oper.parms.value);
});
kukit.commandsGlobalRegistry.registerFromAction('setAttribute', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('setKssAttribute', function(oper) {
    oper.completeParms(['name', 'value'], {}, 'setKssAttribute action');
    kukit.dom.setKssAttribute(oper.node, oper.parms.name, oper.parms.value);
});
kukit.commandsGlobalRegistry.registerFromAction('setKssAttribute', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('setStyle', function(oper) {
    oper.completeParms(['name', 'value'], {}, 'setStyle action');
    oper.node.style[oper.parms.name] = oper.parms.value;
});
kukit.commandsGlobalRegistry.registerFromAction('setStyle', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('insertHTMLAfter', function(oper) {
    oper.completeParms(['html'], {}, 'insertHTMLAfter action');
    oper.parms.html = kukit.dom.forceToDom(oper.parms.html);
    var content = oper.parms.html;
    var parentNode = oper.node.parentNode;
    var toNode = kukit.dom.getNextSiblingTag(oper.node);
    var inserted;
    if (toNode == null) {
        inserted = kukit.dom.appendChildren(content.childNodes, parentNode);
    } else {
        inserted = kukit.dom.insertBefore(content, parentNode, toNode);
    }
    // update the events for the new nodes
    kukit.logDebug("Inserted nodes length: "+inserted.length);
    kukit.engine.setupEvents(inserted);
});
kukit.commandsGlobalRegistry.registerFromAction('insertHTMLAfter', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('insertHTMLBefore', function(oper) {
    oper.completeParms(['html'], {}, 'insertHTMLBefore action');
    oper.parms.html = kukit.dom.forceToDom(oper.parms.html);
    var content = oper.parms.html;
    var toNode = oper.node;
    var parentNode = toNode.parentNode;
    var inserted = kukit.dom.insertBefore(content, parentNode, toNode);
    // update the events for the new nodes
    kukit.logDebug("Inserted nodes length: "+inserted.length);
    kukit.engine.setupEvents(inserted);
});
kukit.commandsGlobalRegistry.registerFromAction('insertHTMLBefore', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('insertHTMLAsLastChild', function(oper) {
    oper.completeParms(['html'], {}, 'insertHTMLAsLastChild action');
    oper.parms.html = kukit.dom.forceToDom(oper.parms.html);
    var inserted = kukit.dom.appendChildren(oper.parms.html, oper.node);
    inserted = kukit.dom.appendChildren(oper.parms.html.childNodes, oper.node);
    // update the events for the new nodes
    kukit.logDebug("Inserted nodes length: "+inserted.length);
    kukit.engine.setupEvents(inserted);
});
kukit.commandsGlobalRegistry.registerFromAction('insertHTMLAsLastChild', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('insertHTMLAsFirstChild', function(oper) {
    oper.completeParms(['html'], {}, 'insertHTMLAsFirstChild action');
    oper.parms.html = kukit.dom.forceToDom(oper.parms.html);
    var content = oper.parms.html;
    var parentNode = oper.node;
    var toNode = parentNode.firstChild;
    if (toNode == null) {
        inserted = kukit.dom.appendChildren(content.childNodes, parentNode);
    } else {
        inserted = kukit.dom.insertBefore(content, parentNode, toNode);
    }
    // update the events for the new nodes
    kukit.logDebug("Inserted nodes length: "+inserted.length);
    kukit.engine.setupEvents(inserted);
});
kukit.commandsGlobalRegistry.registerFromAction('insertHTMLAsFirstChild', kukit.cr.makeSelectorCommand);


kukit.actionsGlobalRegistry.register('deleteNodeAfter', function(oper) {
    oper.completeParms([], {}, 'deleteNodeAfter action');
    var parentNode = oper.node.parentNode;
    var toNode = kukit.dom.getNextSiblingTag(oper.node);
    if (toNode != null) {
        parentNode.removeChild(toNode);
    }  
});
kukit.commandsGlobalRegistry.registerFromAction('deleteNodeAfter', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('deleteNodeBefore', function(oper) {
    oper.completeParms([], {}, 'deleteNodeBefore action');
    var parentNode = oper.node.parentNode;
    var toNode = kukit.dom.getPreviousSiblingTag(oper.node);
    parentNode.removeChild(toNode);
});
kukit.commandsGlobalRegistry.registerFromAction('deleteNodeBefore', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('deleteNode', function(oper) {
    oper.completeParms([], {}, 'deleteNode action');
    var parentNode = oper.node.parentNode;
    parentNode.removeChild(oper.node);
});
kukit.commandsGlobalRegistry.registerFromAction('deleteNode', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('clearChildNodes', function(oper) {
    // TODO get rid of none
    oper.completeParms([], {'none': false}, 'clearChildNodes action');
    kukit.dom.clearChildNodes(oper.node);
});
kukit.commandsGlobalRegistry.registerFromAction('clearChildNodes', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('moveNodeAfter', function(oper) {
    oper.completeParms(['html_id'], {}, 'moveNodeAfter action');
    var node = oper.node;
    var parentNode = node.parentNode;
    parentNode.removeChild(node);
    var toNode = document.getElementById(oper.parms.html_id);
    var nextNode = kukit.dom.getNextSiblingTag(toNode);
    if (nextNode == null) {
        toNode.parentNode.appendChild(node);
    } else {
        parentNode.insertBefore(node, nextNode);
    }
});
kukit.commandsGlobalRegistry.registerFromAction('moveNodeAfter', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('copyChildNodesFrom', function(oper) {
    oper.completeParms(['html_id'], {}, 'copyChildNodesFrom action');
    var fromNode = document.getElementById(oper.parms.html_id);
    Sarissa.copyChildNodes(fromNode, oper.node);
});
kukit.commandsGlobalRegistry.registerFromAction('copyChildNodesFrom', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('copyChildNodesTo', function(oper) {
    oper.completeParms(['html_id'], {}, 'copyChildNodesTo action');
    toNode = document.getElementById(oper.parms.html_id);
    Sarissa.copyChildNodes(oper.node, toNode)
});
kukit.commandsGlobalRegistry.registerFromAction('copyChildNodesTo', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('setStateVar', function(oper) {
    oper.completeParms(['varname', 'value'], {}, 'setStateVar action');
    kukit.engine.statevars[oper.parms.varname] = oper.parms.value;
});
kukit.commandsGlobalRegistry.registerFromAction('setStateVar', kukit.cr.makeGlobalCommand);

kukit.actionsGlobalRegistry.register('continueEvent', function(oper) {
    // Trigger continuation event. Event will be triggered on the same node or
    // on all the nodes bound for the current event state.
    // allows excess parms in the following check.
    oper.completeParms(['name'], {'allnodes': 'false'}, 'continueEvent action', true);
    oper.evalBool('allnodes', 'continueEvent');
    var parms = oper.parms;
    var binderinstance = oper.binderinstance;
    var allnodes = parms.allnodes;
    // marshall it, the rest of the parms will be passed
    var actionparms = {};
    for (var key in parms) {
        if (key != 'name' && key != 'allnodes') {
            actionparms[key] = parms[key];
        }
    }
    if (parms.allnodes) {
        binderinstance.__continue_event_allnodes__(parms.name, actionparms);
    } else {
        binderinstance.__continue_event__(parms.name, oper.node, actionparms);
    }
});
kukit.commandsGlobalRegistry.registerFromAction('continueEvent', kukit.cr.makeGlobalCommand);

kukit.actionsGlobalRegistry.register('executeCommand', function(oper) {
    // Allows executing a local action on a different selection.
    //
    // allows excess parms in the following check
    oper.completeParms(['name', 'selector'],
                       {'selectorType': null},
                       'executeCommand action', true);
    var parms = oper.parms;
    // marshall it, the rest of the parms will be passed
    var actionparms = {};
    for (var key in parms) {
        if (key != 'name' && key != 'selector' && key != 'selectorType') {
            actionparms[key] = parms[key];
        }
    }
    var command = new kukit.cr.makeCommand(parms.selector,
            parms.name, parms.selectorType, actionparms);
    command.execute(oper);
});


// Add/remove a class to/from a node
kukit.actionsGlobalRegistry.register("toggleClass", function (oper) {
    oper.completeParms(['classname'], {}, 'toggleClass action');

    var node = oper.node;
    var classname = oper.parms.classname;

    var nodeclass = kukit.dom.getAttribute(node, 'class');
    var foundclassatindex = -1;
    var parts = nodeclass.split(' ');
    for(var i=0; i<parts.length; i++){
        if(parts[i]==classname){
            foundclassatindex = i;
        }
    }
    if(foundclassatindex==-1){
        parts.push(classname);
    } else {
        parts.splice(foundclassatindex, 1);
    }
    kukit.dom.setAttribute(node, 'class', parts.join(' '));
});
kukit.commandsGlobalRegistry.registerFromAction('toggleClass', kukit.cr.makeGlobalCommand);

/*
*  XXX Compatibility settings for old command names.
*  These will be removed as soon as all current use cases are changed.
*  Do not use these as your code will break!
* 
*/
kukit.commandsGlobalRegistry.registerFromAction('replaceInnerHTML', kukit.cr.makeSelectorCommand, 'setHtmlAsChild');
kukit.commandsGlobalRegistry.registerFromAction('replaceHTML', kukit.cr.makeSelectorCommand, 'replaceNode');
kukit.commandsGlobalRegistry.registerFromAction('insertHTMLAfter', kukit.cr.makeSelectorCommand, 'addAfter');
kukit.commandsGlobalRegistry.registerFromAction('deleteNodeAfter', kukit.cr.makeSelectorCommand, 'removeNextSibling');
kukit.commandsGlobalRegistry.registerFromAction('deleteNodeBefore', kukit.cr.makeSelectorCommand, 'removePreviousSibling');
kukit.commandsGlobalRegistry.registerFromAction('deleteNode', kukit.cr.makeSelectorCommand, 'removeNode');
kukit.commandsGlobalRegistry.registerFromAction('clearChildNodes', kukit.cr.makeSelectorCommand, 'clearChildren');
kukit.commandsGlobalRegistry.registerFromAction('copyChildNodesFrom', kukit.cr.makeSelectorCommand, 'copyChildrenFrom');
kukit.commandsGlobalRegistry.registerFromAction('copyChildNodesTo', kukit.cr.makeSelectorCommand, 'copyChildrenTo');
kukit.commandsGlobalRegistry.registerFromAction('setStateVar', kukit.cr.makeGlobalCommand, 'setStatevar');
   
