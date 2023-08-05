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
* function registerBrowserEvent
*
* This can be used to register native events in a way that
* they handle allowbubbling, preventdefault and preventbubbling as needed.
* (THe handling of these parms are optional, it is allowed not to have them
* in the oper.parms.)
*
* THe register function can also take a filter function as parameter. 
* This function needs to receive oper as a parameter,
* where 'browserevent' will be set on oper too as the native browser event.
* The function must return true if it wants the event to execure, false otherwise.
* If it returns false, the event will not be prevented and counts as if
* were not called.
* This allows for certain event binder like key handlers, to put an extra condition
* on the triggering of event.
*
* The eventname parameter is entirely optional and can be used to set up a different
* event from the desired one.
*/

kukit.pl.registerBrowserEvent = function(oper, filter, eventname) {
    var func_to_bind = oper.makeExecuteActionsHook(filter);
    if (! eventname)
        eventname = oper.getEventName();
    var func = function(e) {
        target = kukit.pl.getTargetForBrowserEvent(e);
        if (oper.parms.allowbubbling || target == oper.node) {
            // Execute the action, provide browserevent on oper
            // ... however, do it protected. We want the preventdefault
            // in any case!
            var exc;
            var success;
            try {
                success = func_to_bind({'browserevent': e});
            } catch(exc1) {
                exc = exc1;    
            }
            if (success || exc) {
                // This should only be skipped, if the filter told
                // us that we don't need this event to be executed.
                // If an exception happened during the event execution,
                // we do yet want to proceed with the prevents.
                //
                // Cancel default event ?
                if (oper.parms.preventdefault) {
                    // W3C style
                    if (e.preventDefault)
                        e.preventDefault();
                    // MS style
                    try { e.returnValue = false; } catch (exc2) {}
                }
                // Prevent bubbling to other kss events ?
                if (oper.parms.preventbubbling) {
                    if (!e) var e = window.event;
                    e.cancelBubble = true;
                    if (e.stopPropagation) e.stopPropagation();
                }
            }
            //
            if (exc != null) {
                // throw the original exception
                throw exc;
            }
        ;;; } else {
        ;;;    kukit.log('Ignored bubbling event for event "' + eventname + '" (target =' + target.tagName + '), EventRule #' + oper.eventrule.getNr() + ' mergeid ' + oper.eventrule.kss_selector.mergeid); 
        }
    };
    kukit.ut.registerEventListener(oper.node, eventname, func);
};

/*
* class NativeEventBinder
*/
kukit.pl.NativeEventBinder = function() {
};

kukit.pl.NativeEventBinder.prototype.__bind__node = function(name, func_to_bind, oper) {
    ;;; if (oper.node == null) {
    ;;;     throw 'Native event "' + name + '"must be bound to a node.';
    ;;; }
    this.__bind__(name, func_to_bind, oper);
};

kukit.pl.NativeEventBinder.prototype.__bind__nodeorwindow = function(name, func_to_bind, oper) {
    if (oper.node == null) {
        oper.node = window;
    }
    this.__bind__(name, func_to_bind, oper);
};

kukit.pl.NativeEventBinder.prototype.__bind__window = function(name, func_to_bind, oper) {
    ;;; if (oper.node != null) {
    ;;;     throw 'Native event "' + name + '"must not be bound to a node.';
    ;;; }
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
    ;;; oper.componentname = 'native event binding';
    oper.completeParms([], {'preventdefault': '', 'allowbubbling': '', 'preventbubbling': ''});
    oper.evalBool('preventdefault');
    oper.evalBool('allowbubbling');
    oper.evalBool('preventbubbling');
    if (oper.parms.preventdefault) {
        if (name != 'click') {
            throw 'In native events only the click event can have preventdefault.';
        }
    }
    kukit.pl.registerBrowserEvent(oper);
    //
    // XXX Safari hack
    // necessary since Safari does not prevent the <a href...> following
    // (in case of allowbubbling we have to apply it to all clicks, as there
    // might be a link inside that we cannot detect on the current node)
    //
    // XXX not needed since we have the legacy name parameter:
    // var name = oper.getEventName();
    if (oper.parms.preventdefault && kukit.HAVE_SAFARI 
            && (oper.parms.allowbubbling || name == 'click' && oper.node.tagName.toLowerCase() == 'a')) {
        oper.node.onclick = function cancelClickSafari() {
            return false;
        };
    }
};

kukit.pl.NativeEventBinder.prototype.__bind_key__ = function(name, func_to_bind, oper) {
    ;;; oper.componentname = 'native key event binding';
    oper.completeParms([], {'preventdefault': 'true', 'allowbubbling': '', 'preventbubbling': '', 'keycodes': ''});
    oper.evalList('keycodes');
    oper.evalBool('preventdefault');
    oper.evalBool('allowbubbling');
    var filter;
    if (oper.parms.keycodes.length >= 0) {
        // Convert keyCode to dict
        var keycodes = {};
        for (var i=0; i<oper.parms.keycodes.length; i++) {
            keyCode = oper.parms.keycodes[i];
            keycodes[keyCode] = true;
        }
        // Set filter so that only the specified keys should trigger.
        filter = function(oper) {
            var keyCode = oper.browserevent.keyCode.toString();
            return keycodes[keyCode];
        };
    }
    kukit.pl.registerBrowserEvent(oper, filter);
};

/*
*  Registration of all the native events that can bound to a node or to document 
*  (= document or window, depending on the event specs)
*  Unsupported are those with absolute no hope to work in a cross browser way
*  Preventdefault is only allowed for click and key events, currently
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
    ;;; oper.componentname = 'timeout event binding';
    oper.completeParms(['delay'], {'repeat': 'true'});
    oper.evalBool('repeat');
    var key = oper.eventrule.getNr();
    if (! (oper.parms.repeat && this.counters[key])) {
        ;;; kukit.logDebug('timer event key entered for actionEvent #' + key + ' '  + oper.eventrule.kss_selector.css);
        var f = function() {
            // check if the node has been deleted
            // and weed it out if so
            if (oper.node != null && ! oper.node.parentNode) {
                ;;; kukit.logDebug('timer deleted for actionEvent #' + key + ' ' + oper.eventrule.kss_selector.css);
                this.clear();
            } else {
                func_to_bind();
            }
        };
        var counter = new kukit.ut.TimerCounter(oper.parms.delay, f, oper.parms.repeat); 
        this.counters[key] = counter;
        // Start the counter
        counter.start();
    ;;; } else {   
    ;;;     // Don't bind the counter if we matched this eventrule already
    ;;;     // (this is only checked if this event is repeating)
    ;;;     kukit.logDebug('timer event key ignored for actionEvent #' + key + ' ' + oper.eventrule.kss_selector.css);
    }
};

kukit.eventsGlobalRegistry.register(null, 'timeout', kukit.pl.TimeoutEventBinder, '__bind__', null);

/*
* class LoadEventBinder
*/
kukit.pl.LoadEventBinder = function() {
};

kukit.pl.LoadEventBinder.prototype.process_parms = function(oper, iload) {
    if (! oper) {
        return;
    }
    if (iload) {
        ;;; oper.componentname = 'iload event binding';
        oper.completeParms(['autodetect'], {'initial': 'true', 'insert': 'true'});
        // autodetect=false changes the iload autosense method to one that requires the iframe set
        // the _kssReadyForLoadEvent attribute on the document. Setting this attribute is explicitely required 
        // if autodetect is off, since otherwise in this case we would never notice if the document has arrived.
        oper.evalBool('autodetect');
    } else {
        ;;; oper.componentname = 'load event binding';
        oper.completeParms([], {'initial': 'true', 'insert': 'true'});
    }
    oper.evalBool('initial');
    oper.evalBool('insert');
    var phase = oper.node._kukitmark;
    if (phase == 1 && ! oper.parms.initial) {
        ;;; kukit.logDebug('EventRule #' + oper.eventrule.getNr() + ' mergeid ' + oper.eventrule.kss_selector.mergeid + ' event ignored, oninitial=false.');
        return;
    }
    if (phase == 2 && ! oper.parms.insert) {
        ;;; kukit.logDebug('EventRule #' + oper.eventrule.getNr() + ' mergeid ' + oper.eventrule.kss_selector.mergeid + ' event ignored, oninsert=false.');
        return;
    }
    return oper;
};

kukit.pl.LoadEventBinder.prototype.__bind__ = function(opers_by_eventname) {
    // This bind method handles load and iload events together, and opers_by_eventname is
    // a dictionary of opers which can contain a load and an iload key, either one or both.
    var loadoper = opers_by_eventname.load;
    var iloadoper = opers_by_eventname.iload;
    loadoper = this.process_parms(loadoper);
    iloadoper = this.process_parms(iloadoper, true);
    var anyoper = loadoper || iloadoper;
    if (! anyoper) {
        return;
    }
    if (anyoper.node != null && anyoper.node.tagName.toLowerCase() == 'iframe') {
        // In an iframe.
        //
        // BBB If there is only a load (and no iload) event bound to this node, 
        // we interpret it as an iload event, but issue deprecation warning.
        // This conserves legacy behaviour when the load event was actually doing an iload,
        // when it was bound to an iframe node.
        // The deprecation tells that the event should be changed from load to iload.
        if (loadoper && ! iloadoper) {
            iloadoper = loadoper;
            loadoper = null;
            // with the legacy loads we suppose autodetect=false
            iloadoper.parms.autodetect = false;
            ;;; kukit.E = 'Deprecated the use of "load" event for iframes. It will behave differently in the future. ';
            ;;; kukit.E += 'Use the "iload" event (maybe with evt-iload-autodetect: false) instead!';
            ;;; kukit.logWarning(kukit.E);
        } 
    } else {
        // Not an iframe. So iload is not usable.
        if (iloadoper) {
            ;;; kukit.E = 'iload event can only be bound on an iframe node.';
            throw kukit.E;
        }
    }
    // Now, bind the events.
    if (loadoper) {
        ;;; kukit.E = 'EventRule #' + loadoper.eventrule.getNr() + ' mergeid ';
        ;;; kukit.E += loadoper.eventrule.kss_selector.mergeid;
        ;;; kukit.E += ' event selected normal postponed execution.';
        ;;; kukit.logDebug(kukit.E);
        // for any other node than iframe, or even for iframe in phase1, we need to execute immediately.
        var func_to_bind = loadoper.makeExecuteActionsHook();
        ;;; kukit.E = 'Execute load event for node ' + loadoper.node.tagName.toLowerCase();
        kukit.engine.bindScheduler.addPost(func_to_bind, kukit.E);
    }
    if (iloadoper) {
        var phase = iloadoper.node._kukitmark;
        // For phase 2 we need to execute posponed, for phase1 immediately.
        // XXX it would be better not need this and do always postponed.
        if (phase == 2 || (phase == 1 && kukit.engine.initializedOnDOMLoad)) {
            ;;; kukit.E = 'EventRule #' + iloadoper.eventrule.getNr() + ' mergeid ';
            ;;; kukit.E += iloadoper.eventrule.kss_selector.mergeid;
            ;;; kukit.E += ' event selected delayed execution (when iframe loaded)';
            ;;; kukit.logDebug(kukit.E);
            // We want the event execute once the iframe is loaded.
            // In a somewhat tricky way, we start the scheduler only from the normal delayed execution. This will enable that in
            // case we had a load event on the same node, it could modify the name and id parameters and we only start
            // the autosense loop (which is based on name and id) after the load event's action executed. 
            // (Note, oper.node.id may lie in the log then and show the original, unchanged id but we ignore this for the time.)
            var g = function() {
                var f = function() {
                    var func_to_bind = iloadoper.makeExecuteActionsHook();
                    ;;; kukit.E = 'Execute iload event for iframe ' + iloadoper.node.name;
                    kukit.engine.bindScheduler.addPost(func_to_bind, kukit.E);
                };
                new kukit.dom.EmbeddedContentLoadedScheduler(iloadoper.node.id, f, iloadoper.parms.autodetect);
            };
            ;;; kukit.E = 'Schedule iload event for iframe ' + iloadoper.node.name;
            kukit.engine.bindScheduler.addPost(g, kukit.E);
        } else {
            ;;; kukit.E = 'EventRule #' + iloadoper.eventrule.getNr() + ' mergeid ';
            ;;; kukit.E += iloadoper.eventrule.kss_selector.mergeid;
            ;;; kukit.E += ' event selected normal postponed execution.';
            ;;; kukit.logDebug(kukit.E);
            var func_to_bind = iloadoper.makeExecuteActionsHook();
            ;;; kukit.E = 'Execute iload event for iframe ' + iloadoper.node.name;
            kukit.engine.bindScheduler.addPost(func_to_bind, kukit.E);
        }
    }
};

// Use the "node" iterator to provide expected invocation and call signature of the bind method.
kukit.eventsGlobalRegistry.registerForAllEvents(null, ['load', 'iload'], kukit.pl.LoadEventBinder, '__bind__', null, 'node');


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
    ;;; oper.componentname = 'spinner event binding';
    oper.completeParms([], {'laziness': 0});
    oper.evalInt('laziness');
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
;;;     oper.completeParms([], {'message': 'LogDebug action'}, 'logDebug action');
;;;     var node = oper.node;
;;;     var nodeName = '<DOCUMENT>';
;;;     if (node != null) {
;;;         nodeName = node.nodeName;
;;;     }
;;;     var message = oper.parms.message;
;;;     if (oper.eventrule) {
;;;         message = message + ', event=' + oper.eventrule.kss_selector.name + ', rule=#' + oper.eventrule.getNr() + ', node=' + nodeName; 
;;;     }
;;;     kukit.logDebug(message); 
;;;     if (kukit.hasFirebug) {
;;;         kukit.logDebug(oper.node);
;;;     }
});
kukit.commandsGlobalRegistry.registerFromAction('logDebug', kukit.cr.makeGlobalCommand);

kukit.actionsGlobalRegistry.register("log", function (oper) {
;;;     oper.completeParms([], {'message': 'Log action'}, 'log action');
;;;     var node = oper.node;
;;;     var nodeName = '<DOCUMENT>';
;;;     if (node != null) {
;;;         nodeName = node.nodeName;
;;;     }
;;;     var message = oper.parms.message;
;;;     if (oper.eventrule) {
;;;         message = message + ', event=' + oper.eventrule.kss_selector.name + ', rule=#' + oper.eventrule.getNr() + ', node=' + nodeName; 
;;;     }
;;;     kukit.log(message);
});
kukit.commandsGlobalRegistry.registerFromAction('log', kukit.cr.makeGlobalCommand);

kukit.actionsGlobalRegistry.register("alert", function (oper) {
;;;     oper.completeParms([], {'message': 'Alert action'}, 'alert action');
;;;     var node = oper.node;
;;;     var nodeName = '<DOCUMENT>';
;;;     if (node != null) {
;;;         nodeName = node.nodeName;
;;;     }
;;;     var message = oper.parms.message;
;;;     if (oper.eventrule) {
;;;         message = message + ', rule=#' + oper.eventrule.getNr() + ', node=' + nodeName; 
;;;     }
;;;     alert(message);
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
    ;;; oper.componentname = 'replaceInnerHTML action';
    oper.completeParms(['html'], {'withKssSetup': true});
    oper.evalBool('withKssSetup');
    var node = oper.node;
    var insertedNodes;
    if (typeof(oper.parms.html) == 'string') {
        node.innerHTML = oper.parms.html;
        insertedNodes = node.childNodes; 
    } else {
        oper.parms.html = kukit.dom.forceToDom(oper.parms.html);
        kukit.dom.clearChildNodes(node);
        insertedNodes = kukit.dom.appendChildren(oper.parms.html.childNodes, node);
    }
    if (oper.parms.withKssSetup) {
        kukit.engine.setupEvents(insertedNodes);
    }
});
kukit.commandsGlobalRegistry.registerFromAction('replaceInnerHTML', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('replaceHTML', function(oper) {
/*
*  accepts both string and dom.
*/
    ;;; oper.componentname = 'replaceHTML action';
    oper.completeParms(['html'], {'withKssSetup':true});
    oper.evalBool('withKssSetup');
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
        if (oper.parms.withKssSetup) {
            kukit.engine.setupEvents(insertedNodes);
        }
    }
});
kukit.commandsGlobalRegistry.registerFromAction('replaceHTML', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('setAttribute', function(oper) {
    ;;; oper.componentname = 'setAttribute action';
    oper.completeParms(['name', 'value'], {});
    if (oper.parms.name.toLowerCase() == 'style') {
        ;;; kukit.E = 'Style attribute is not allowed with setAttribute';
        throw kukit.E;
    }
    kukit.dom.setAttribute(oper.node, oper.parms.name, oper.parms.value);
});
kukit.commandsGlobalRegistry.registerFromAction('setAttribute', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('setKssAttribute', function(oper) {
    ;;; oper.componentname = 'setKssAttribute action';
    oper.completeParms(['name', 'value'], {});
    kukit.dom.setKssAttribute(oper.node, oper.parms.name, oper.parms.value);
});
kukit.commandsGlobalRegistry.registerFromAction('setKssAttribute', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('setStyle', function(oper) {
    ;;; oper.componentname = 'setStyle action';
    oper.completeParms(['name', 'value'], {});
    oper.node.style[oper.parms.name] = oper.parms.value;
});
kukit.commandsGlobalRegistry.registerFromAction('setStyle', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('addClass', function(oper) {
    ;;; oper.componentname = 'addClass action';
    oper.completeParms(['value'], {});
    addClassName(oper.node, oper.parms.value);
});
kukit.commandsGlobalRegistry.registerFromAction('addClass', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('removeClass', function(oper) {
    ;;; oper.componentname = 'removeClass action';
    oper.completeParms(['value'], {});
    removeClassName(oper.node, oper.parms.value);
});
kukit.commandsGlobalRegistry.registerFromAction('removeClass', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('insertHTMLAfter', function(oper) {
    ;;; oper.componentname = 'insertHTMLAfter action';
    oper.completeParms(['html'], {'withKssSetup':true});
    oper.evalBool('withKssSetup');
    oper.parms.html = kukit.dom.forceToDom(oper.parms.html);
    var content = oper.parms.html;
    var parentNode = oper.node.parentNode;
    var toNode = kukit.dom.getNextSiblingTag(oper.node);
    var insertedNodes;
    if (toNode == null) {
        insertedNodes = kukit.dom.appendChildren(content.childNodes, parentNode);
    } else {
        insertedNodes = kukit.dom.insertBefore(content, parentNode, toNode);
    }
    // update the events for the new nodes
    ;;; kukit.logDebug("Inserted nodes length: "+insertedNodes.length);
    if (oper.parms.withKssSetup) {
        kukit.engine.setupEvents(insertedNodes);
    }
});
kukit.commandsGlobalRegistry.registerFromAction('insertHTMLAfter', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('insertHTMLBefore', function(oper) {
    ;;; oper.componentname = 'insertHTMLBefore action';
    oper.completeParms(['html'], {'withKssSetup':true});
    oper.evalBool('withKssSetup');
    oper.parms.html = kukit.dom.forceToDom(oper.parms.html);
    var content = oper.parms.html;
    var toNode = oper.node;
    var parentNode = toNode.parentNode;
    var insertedNodes = kukit.dom.insertBefore(content, parentNode, toNode);
    // update the events for the new nodes
    ;;; kukit.logDebug("Inserted nodes length: "+insertedNodes.length);
    if (oper.parms.withKssSetup) {
        kukit.engine.setupEvents(insertedNodes);
    }
});
kukit.commandsGlobalRegistry.registerFromAction('insertHTMLBefore', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('insertHTMLAsLastChild', function(oper) {
    ;;; oper.componentname = 'insertHTMLAsLastChild action';
    oper.completeParms(['html'], {'withKssSetup':true});
    oper.evalBool('withKssSetup');
    oper.parms.html = kukit.dom.forceToDom(oper.parms.html);
    var insertedNodes = kukit.dom.appendChildren(oper.parms.html, oper.node);
    insertedNodes = kukit.dom.appendChildren(oper.parms.html.childNodes, oper.node);
    // update the events for the new nodes
    ;;; kukit.logDebug("Inserted nodes length: "+insertedNodes.length);
    if (oper.parms.withKssSetup) {
        kukit.engine.setupEvents(insertedNodes);
    }
});
kukit.commandsGlobalRegistry.registerFromAction('insertHTMLAsLastChild', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('insertHTMLAsFirstChild', function(oper) {
    ;;; oper.componentname = 'insertHTMLAsFirstChild action';
    oper.completeParms(['html'], {'withKssSetup':true});
    oper.evalBool('withKssSetup');
    oper.parms.html = kukit.dom.forceToDom(oper.parms.html);
    var content = oper.parms.html;
    var parentNode = oper.node;
    var toNode = parentNode.firstChild;
    var insertedNodes;
    if (toNode == null) {
        insertedNodes = kukit.dom.appendChildren(content.childNodes, parentNode);
    } else {
        insertedNodes = kukit.dom.insertBefore(content, parentNode, toNode);
    }
    // update the events for the new nodes
    ;;; kukit.logDebug("Inserted nodes length: "+insertedNodes.length);
    if (oper.parms.withKssSetup) {
        kukit.engine.setupEvents(insertedNodes);
    }
});
kukit.commandsGlobalRegistry.registerFromAction('insertHTMLAsFirstChild', kukit.cr.makeSelectorCommand);


kukit.actionsGlobalRegistry.register('deleteNodeAfter', function(oper) {
    ;;; oper.componentname = 'deleteNodeAfter action';
    ;;; oper.completeParms([], {});
    var parentNode = oper.node.parentNode;
    var toNode = kukit.dom.getNextSiblingTag(oper.node);
    if (toNode != null) {
        parentNode.removeChild(toNode);
    }  
});
kukit.commandsGlobalRegistry.registerFromAction('deleteNodeAfter', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('deleteNodeBefore', function(oper) {
    ;;; oper.componentname = 'deleteNodeBefore action';
    ;;; oper.completeParms([], {});
    var parentNode = oper.node.parentNode;
    var toNode = kukit.dom.getPreviousSiblingTag(oper.node);
    parentNode.removeChild(toNode);
});
kukit.commandsGlobalRegistry.registerFromAction('deleteNodeBefore', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('deleteNode', function(oper) {
    ;;; oper.componentname = 'deleteNode action';
    ;;; oper.completeParms([], {});
    var parentNode = oper.node.parentNode;
    parentNode.removeChild(oper.node);
});
kukit.commandsGlobalRegistry.registerFromAction('deleteNode', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('clearChildNodes', function(oper) {
    // TODO get rid of none
    ;;; oper.componentname = 'clearChildNodes action';
    oper.completeParms([], {'none': false});
    kukit.dom.clearChildNodes(oper.node);
});
kukit.commandsGlobalRegistry.registerFromAction('clearChildNodes', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('focus', function(oper) {
    // TODO get rid of none
    ;;; oper.componentname = 'focus action';
    oper.completeParms([], {'none': false});
    kukit.dom.focus(oper.node);
});
kukit.commandsGlobalRegistry.registerFromAction('focus', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('moveNodeAfter', function(oper) {
    ;;; oper.componentname = 'moveNodeAfter action';
    ;;; oper.completeParms(['html_id'], {});
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

kukit.actionsGlobalRegistry.register('moveNodeBefore', function(oper) {
    ;;; oper.componentname = 'moveNodeBefore action';
    ;;; oper.completeParms(['html_id'], {});
    var node = oper.node;
    // no need to remove it, as insertNode does it anyway
    // var parentNode = node.parentNode;
    // parentNode.removeChild(node);
    var toNode = document.getElementById(oper.parms.html_id);
    var parentNode = toNode.parentNode;
    parentNode.insertBefore(node, toNode);
});
kukit.commandsGlobalRegistry.registerFromAction('moveNodeBefore', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('moveNodeAsLastChild', function(oper) {
    ;;; oper.componentname = 'moveNodeAsLastChild action';
    ;;; oper.completeParms(['html_id'], {});
    var node = oper.node;
    // no need to remove it, as insertNode does it anyway
    // var parentNode = node.parentNode;
    // parentNode.removeChild(node);
    var parentNode = document.getElementById(oper.parms.html_id);
    parentNode.appendChild(node);
});
kukit.commandsGlobalRegistry.registerFromAction('moveNodeAsLastChild', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('copyChildNodesFrom', function(oper) {
    ;;; oper.componentname = 'copyChildNodesFrom action';
    ;;; oper.completeParms(['html_id'], {});
    var fromNode = document.getElementById(oper.parms.html_id);
    Sarissa.copyChildNodes(fromNode, oper.node);
});
kukit.commandsGlobalRegistry.registerFromAction('copyChildNodesFrom', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('copyChildNodesTo', function(oper) {
    ;;; oper.componentname = 'copyChildNodesTo action';
    ;;; oper.completeParms(['html_id'], {});
    toNode = document.getElementById(oper.parms.html_id);
    Sarissa.copyChildNodes(oper.node, toNode);
});
kukit.commandsGlobalRegistry.registerFromAction('copyChildNodesTo', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register('setStateVar', function(oper) {
    ;;; oper.componentname = 'setStateVar action';
    ;;; oper.completeParms(['varname', 'value'], {});
    kukit.engine.statevars[oper.parms.varname] = oper.parms.value;
});
kukit.commandsGlobalRegistry.registerFromAction('setStateVar', kukit.cr.makeGlobalCommand);

kukit.actionsGlobalRegistry.register('continueEvent', function(oper) {
    // Trigger continuation event. Event will be triggered on the same node or
    // on all the nodes bound for the current event state.
    // allows excess parms in the following check.
    ;;; oper.componentname = 'continue action';
    oper.completeParms(['name'], {'allnodes': 'false'}, '', true);
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
        // execution happens on the orignode
        binderinstance.__continue_event__(parms.name, oper.orignode, actionparms);
    }
});
kukit.commandsGlobalRegistry.registerFromAction('continueEvent', kukit.cr.makeGlobalCommand);

kukit.actionsGlobalRegistry.register('executeCommand', function(oper) {
    // Allows executing a local action on a different selection.
    //
    // allows excess parms in the following check
    ;;; oper.componentname = 'executeCommand action';
    oper.completeParms(['name', 'selector'],
                       {'selectorType': null},
                       '', true);
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
    ;;; oper.componentname = 'toggleClass action';
    // BBB 4 month, until 2007-10-18
    // oper.completeParms(['value'], {});
    kukit.actionsGlobalRegistry.BBB_classParms(oper);

    var node = oper.node;
    var classname = oper.parms.value;

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
kukit.commandsGlobalRegistry.registerFromAction('toggleClass', kukit.cr.makeSelectorCommand);

/*
*  XXX Compatibility settings for old command names.
*  These will be removed as soon as all current use cases are changed.
*  Do not use these as your code will break!
* 
*/
// BBB remove at 2007-10-18
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
// BBB 4 month, until 2007-10-18
kukit.actionsGlobalRegistry.register('addClassName', function(oper) {
    ;;; kukit.logWarning('Deprecated the "addClassName"  action, use "addClass" instead!');
    ;;; oper.componentname = 'addClassName action';
    kukit.actionsGlobalRegistry.BBB_classParms(oper);
    kukit.actionsGlobalRegistry.get('addClass')(oper);
});
kukit.commandsGlobalRegistry.registerFromAction('addClassName', kukit.cr.makeSelectorCommand);
// BBB 4 month, until 2007-10-18
kukit.actionsGlobalRegistry.register('removeClassName', function(oper) {
    ;;; kukit.logWarning('Deprecated the "removeClassName"  action, use "removeClass" instead!');
    ;;; oper.componentname = 'removeClassName action';
    kukit.actionsGlobalRegistry.BBB_classParms(oper);
    kukit.actionsGlobalRegistry.get('removeClass')(oper);
});
kukit.commandsGlobalRegistry.registerFromAction('removeClassName', kukit.cr.makeSelectorCommand);

// BBB 4 month, until 2007-10-18
kukit.actionsGlobalRegistry.BBB_classParms = function(oper) {
    var old;
    var has_old;
    if (typeof(oper.parms.classname) != 'undefined') {
        old = oper.parms.classname;
        has_old = true;
        ;;; kukit.logWarning('Deprecated the "classname" parameter in ' + oper.componentname + ', use "value" instead!');
    }
    if (typeof(oper.parms.name) != 'undefined') {
        old = oper.parms.name;
        has_old = true;
        ;;; kukit.logWarning('Deprecated the "name" parameter in ' + oper.componentname + ', use "value" instead!');
    }
    if (has_old) {
        if (typeof(oper.parms.value) == 'undefined') {
            oper.parms = {value: old};
        } else {
            oper.parms = {};
        }
    }
};
// end BBB

