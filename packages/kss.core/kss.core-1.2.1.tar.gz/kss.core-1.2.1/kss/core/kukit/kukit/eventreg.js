/*
* Copyright (c) 2005-2007
* Authors: KSS Project Contributors (see doc/CREDITS.txt)
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

kukit.er = {};


kukit.er.eventClassCounter = 0;

/*
*
* class CommandRegistry
*
* available for plugin registration
*
* usage:
*
*  kukit.eventsGlobalRegistry.register(namespace, eventName, func, 
*    bindMethodName, defaultActionMethodName);
*  
*     namespace = null: means global namespace
*     defaultActionMethodName = null: if there is no default action implemented
*     func must be a class (constructor) function, this is the class that
*           implements the binder.
*/
kukit.er.EventRegistry = function () {
    this.content = {};
    this.classes = {};
    this.eventSets = [];
};

/* binder registration */

kukit.er.EventRegistry.prototype.registerBinder = function(className, func) {
    if (typeof(func) == 'undefined') {
;;;     kukit.E = 'func argument is mandatory when registering an event';
;;;     kukit.E += ' binder (EventRegistry.registerBinder).';
        throw kukit.E;
    }
    if (this.classes[className]) {
        // Do not allow redefinition
;;;     var msg = 'Error : event class [' + className + '] already registered.';
;;;     kukit.logError(msg);
        return;
    
    }
    // Decorate and store the class
    kukit.er.decorateEventBinderClass(func);
    this.classes[className] = func;
};

kukit.er.EventRegistry.prototype.existsBinder = function(className) {
    var func = this.classes[className];
    return (typeof(func) != 'undefined');
};

kukit.er.EventRegistry.prototype.getBinder = function(className) {
    var func = this.classes[className];
    if (! func) {
        // not found
;;;     kukit.E = 'Error : undefined event setup type [' + className + '].';
        throw kukit.E;
        }
    return func;
};

/* events (methods) registration  helpers (not to be called directly) */

kukit.er.EventRegistry.prototype._register = 
    function(namespace, eventName, klass,
        bindMethodName, defaultActionMethodName, iterName) {
    if (typeof(defaultActionMethodName) == 'undefined') {
;;;     kukit.E = 'Missing arguments when calling [EventRegistry.register].';
        throw kukit.E;
    }
    // Find out the class name. (Not specified now.)
    var className = klass.prototype.__className__;
    if (typeof(className) == 'undefined') {
        // Create a className, and register it too.
        className = '' + kukit.er.eventClassCounter;
        kukit.er.eventClassCounter += 1;
        this.registerBinder(className, klass);
        klass.prototype.__className__ = className;
    }
    if (!eventName) {
;;;     kukit.E = '[eventName] argument cannot be empty when registering';
;;;     kukit.E += ' an event with [EventRegistry.register].';
        throw kukit.E;
    }
    var key = this._getKey(namespace, eventName);
    var entry = this.content[key];
    if (typeof(entry) != 'undefined') {
        if (key[0] == '-') {
            key = key.substring(1);
        }
;;;     kukit.E = 'Attempt to register key [' + key;
;;;     kukit.E += '] twice when registering';
;;;     kukit.E += ' an event with [EventRegistry.register].';
        throw kukit.E;
    }
    // check bindMethodName and defaultActionMethodName
    if (bindMethodName && ! klass.prototype[bindMethodName]) {
;;;     kukit.E = 'In EventRegistry.register bind method [' + bindMethodName;
;;;     kukit.E += '] is undefined for event [' + eventName;
;;;     kukit.E += '] namespace [' + namespace + '].';
        throw kukit.E;
    }
    if (defaultActionMethodName && ! klass.prototype[defaultActionMethodName]) {
;;;     kukit.E = 'In EventRegistry.register default action method [';
;;;     kukit.E += defaultActionMethodName + '] is undefined for event [';
;;;     kukit.E += eventName + '] namespace [' + namespace + '].';
        throw kukit.E;
    }
    // check the iterator.
    if  (! kukit.er.getBindIterator(iterName)) {
;;;     kukit.E = 'In EventRegistry.register unknown bind iterator [';
;;;     kukit.E += iterName + '].';
        throw kukit.E;
    }
    // register it
    this.content[key] = {
        'className': className,
        'bindMethodName': bindMethodName,
        'defaultActionMethodName': defaultActionMethodName,
        'iterName': iterName
        };
};

/* events (methods) binding [ForAll] registration */

kukit.er.EventRegistry.prototype._registerEventSet =
    function(namespace, names, iterName, bindMethodName) {
    // At this name the values should be checked already. so this should
    // be called _after_ _register.
    this.eventSets.push({
        'namespace': namespace, 
        'names': names,
        'iterName': iterName,
        'bindMethodName': bindMethodName
        });
};

/* there are the actual registration methods, to be called from plugins */

kukit.er.EventRegistry.prototype.register =
    function(namespace, eventName, klass, bindMethodName,
        defaultActionMethodName) {
    this._register(namespace, eventName, klass, bindMethodName,
        defaultActionMethodName, 'EachLegacy');
    this._registerEventSet(namespace, [eventName], 'EachLegacy',
        bindMethodName);
};

kukit.er.EventRegistry.prototype.registerForAllEvents =
    function(namespace, eventNames, klass,
        bindMethodName, defaultActionMethodName, iterName) {
    if (typeof(eventNames) == 'string') {
        eventNames = [eventNames];
        }
    for (var i=0; i<eventNames.length; i++) {
        var eventName = eventNames[i];
        this._register(namespace, eventName, klass, bindMethodName, 
            defaultActionMethodName, iterName);
    }
    this._registerEventSet(namespace, eventNames, iterName, bindMethodName);
};

kukit.er.EventRegistry.prototype._getKey = function(namespace, eventName) {
    if (namespace == null) {
        namespace = '';
    } else if (namespace.split('-') > 1) {
;;;     kukit.E = 'In [EventRegistry.register], [namespace] cannot have';
;;;     kukit.E += 'dashes.';
        throw kukit.E;
    }
    return namespace + '-' + eventName;
};

kukit.er.EventRegistry.prototype.exists = function(namespace, eventName) {
    var key = this._getKey(namespace, eventName);
    var entry = this.content[key];
    return (typeof(entry) != 'undefined');
};

kukit.er.EventRegistry.prototype.get = function(namespace, eventName) {
    var key = this._getKey(namespace, eventName);
    var entry = this.content[key];
    if (typeof(entry) == 'undefined') {
;;;     if (key.substr(0, 1) == '-') {
;;;         key = key.substring(1);
;;;         kukit.E = 'Error : undefined global event key ';
;;;         kukit.E += key + ' (or maybe namespace is missing ?).';
;;;     } else {
;;;         kukit.E = 'Error : undefined event key [' + key + '].';
;;;     }
        throw kukit.E;
    } 
    return entry;
};

kukit.eventsGlobalRegistry = new kukit.er.EventRegistry();


/* XXX deprecated methods, to be removed asap */

kukit.er.eventRegistry = {};
kukit.er.eventRegistry.register = function(namespace, eventName, klass,
        bindMethodName, defaultActionMethodName) {
;;; var msg = 'Deprecated kukit.er.eventRegistry.register,';
;;; msg += ' use kukit.eventsGlobalRegistry.register instead ! [';
;;; msg += namespace + '-' + eventName + '].';
;;; kukit.logWarning(msg);
    kukit.eventsGlobalRegistry.register(namespace, eventName, klass,
        bindMethodName, defaultActionMethodName);
};

/* Event class decoration 
*
* poor man's subclassing
* This is called automatically on registration, to dress
* up the event class with the necessary methods
*
*/

/* Provide callins on the state instance that execute a given
*  continuation event.
*  Parameters will be the ones specified in the call + 
*  those defined in the rule will be added too. (Parameters can
*  be accessed with the [pass] kss parameter provider.)
*
* Call examples: 
*
* trigger an event bound to a given state instance, same node
*
*     binderInstance.__continueEvent__('doit', oper.node, {'extravalue': '5'});
*
*   with kss rule:
*
*     node.selector:doit {
*         action-client: log;
*         log-message: pass(extravalue);
*     }
*
*  or
*
*     behaviour.selector:doit {
*         action-client: log;
*         log-message: pass(extravalue);
*     }
*
* trigger an event bound to a given state instance, and the document
* (different from current scope)
*
*     binderInstance.__continueEvent__('doit', null, {'extravalue': '5'});
*
*   with kss rule:
*
*     document:doit {
*         action-client: log;
*         log-message: pass(extravalue);
*     }
*
*  or
*
*     behaviour.selector:doit {
*         action-client: log;
*         log-message: pass(extravalue);
*     }
*
* trigger an event on all the nodes + document bound to a given state instance
*
*     binderInstance.__continueEvent_allNodes__('doit', {'extravalue': '5'});
*
*   with kss rule:
*
*     node.selector:doit {
*         action-client: log;
*         log-message: pass(extravalue);
*     }
*
* p.s. oper is not required to make it easy to adapt existing code
* so we create a new oper below
*/

kukit.er.EventBinder__continueEvent__ =
    function(name, node, defaultParameters) {
    // Trigger a continuation event bound to a given state instance, given node
    // (or on document, if node = null)
    //
    var oper = new kukit.op.Oper();
    oper.node = node;
    if (node) {
        // if we found the binding, just use that
        var info = kukit.engine.binderInfoRegistry.getBinderInfoById(
            this.__binderId__);
        var newOper = info.bound.getBoundOperForNode(name, node);
        if (newOper) {
            oper = newOper;
        }
    } else {
        oper.eventRule =  kukit.engine.documentRules.getMergedRule(
            'document', name, this);
    }
    // Look up the behaviour rule, if any.
    var behav_eventRule =  kukit.engine.documentRules.getMergedRule(
        'behaviour', name, this);
    if (behav_eventRule) {
        if (! oper.eventRule) {
            // There was no node matching for the rule, use behaviour rule
            // this allows to set up parametrized actions in general.
            oper.eventRule = behav_eventRule;
        } else {
            // XXX this case should go away, as we should check
            // this already from binding time
            // and signal the appropriate error.
            // Also note that behaviour roles will only be allowed
            // for "non-binding" events.
;;;         var msg = 'Behaviour rule for continuation event [' + name;
;;;         msg += '] will be ignored, because we found an explicit rule.';
;;;         kukit.logError(msg);
        }
    }
    // If parms are specified in the call, use them.
    if (typeof(defaultParameters) != 'undefined') {
        oper.defaultParameters = defaultParameters;
    } else {
        oper.defaultParameters = {};
    }
    // if eventRule is null here, we can yet have the default method, so go on.
    this._EventBinder_triggerEvent(name, oper);
;;; kukit.logDebug('Continuation event [' + name + '] executed on same node.');
};

kukit.er.EventBinder__continueEvent_allNodes__ =
    function(name, defaultParameters) {
    // Trigger an event bound to a given state instance, on all nodes.
    // (or on document, if node = null)
    // if no other nodes execute.
    var executed = 0;
    // Normal rules. If any of those match, execute them too
    // each on the node that it selects - not on the original node.
    var oper = new kukit.op.Oper();
    var info = kukit.engine.binderInfoRegistry.getBinderInfoById(
        this.__binderId__);
    var opers = info.bound.getBoundOpers(name);
    for (var i=0; i<opers.length; i++) {
        var oper = opers[i];
        var newOper = oper.clone();
        if (typeof(defaultParameters) != 'undefined') {
            newOper.defaultParameters = defaultParameters;
        } else {
            newOper.defaultParameters = {};
        }
        this._EventBinder_triggerEvent(name, newOper);
        executed += 1;
    }
;;; kukit.logDebug('Event [' + name + '] executed on ' + executed + ' nodes.');
};

kukit.er.EventBinder_makeFuncToBind = function(name, node) {
   var executor = new kukit.er.LateBinder(this, name, node);
   return function() {
       executor.executeActions();
   };
};

kukit.er.LateBinder = function(binderInstance, name, node) {
    this.binderInstance = binderInstance;
    this.name = name;
    this.node = node;
    this.bound = null;
};

kukit.er.LateBinder.prototype.executeActions = function() {
    if (! this.bound) {
;;;        var msg = 'Attempt of late binding for event [' + this.name;
;;;        msg += '], node [' + this.node.nodeName + '].';
;;;        kukit.log(msg);
        if (kukit.hasFirebug) {
            kukit.log(this.node);
        }
        var info = kukit.engine.binderInfoRegistry.getBinderInfoById(
            this.binderInstance.__binderId__);
        var oper = info.bound.getBoundOperForNode(this.name, this.node);
        if (oper) {
            // (if eventRule is null here, we could still have the default
            // method, so go on.)
            oper.parms = {};
            this.bound = function() {
                this.binderInstance._EventBinder_triggerEvent(this.name, oper);
            };
;;;         kukit.log('Node bound.');
        } else {
;;;         kukit.logWarning('No node bound.');
            this.bound = function() {};
        }
    }
    this.bound();
};        

kukit.er.EventBinder_triggerEvent = function(name, oper) {
    // Private. Called from __continueEvent__ or from main event execution.
    oper.binderInstance = this;
    if (oper.eventRule) {
        // Call the actions, if we had an event rule.
        // This includes calling the default action.
        oper.eventRule.actions.execute(oper);
    } else {
        // In case there is no event rule, just call the default event action.
        var namespace = this.__eventNamespace__;
;;;     var msg = 'Calling implicit event [' + name + '] on namespace [';
;;;     msg += namespace + '].';
;;;     kukit.logDebug(msg);
        var success = oper.executeDefaultAction(name, true);
        if (! success) {
            // instead of the standard message give more specific reason:
            // either way we should have executed something...
;;;         kukit.E = 'Could not trigger event name [' + name;
;;;         kukit.E += '] on namespace [' + namespace;
;;;         kukit.E += '], because there is neither an explicit KSS rule,';
;;;         kukit.E += ' nor a default method';
            throw kukit.E;
        }
    }
};

/* (default) method call handling */

kukit.er.EventBinder_callMethod = function(namespace, name, oper, methodName) {
    // hidden method for calling just a method and checking that is exists.
    // (called from oper)
    var method = this[methodName];
    if (! method) {
;;;     kukit.E = 'Could not trigger event name [' + name;
;;;     kukit.E += '] on namespace [' + namespace;
;;;     kukit.E += '], because the method [' + methodName + '] does not exist.';
        throw kukit.E;
    }
    // call it
    oper.binderInstance = this;
    method.call(this, name, oper);
};

kukit.er.decorateEventBinderClass = function(cls) {
    cls.prototype.__continueEvent__ = kukit.er.EventBinder__continueEvent__;
    cls.prototype.__continueEvent_allNodes__ =
        kukit.er.EventBinder__continueEvent_allNodes__;
    cls.prototype._EventBinder_triggerEvent = kukit.er.EventBinder_triggerEvent;
    cls.prototype._EventBinder_callMethod = kukit.er.EventBinder_callMethod;
    cls.prototype.__makeFuncToBind__ = kukit.er.EventBinder_makeFuncToBind;
};

/* Event instance registry 
*
* class BinderInfoRegistry
*
*  used in run-time to keep track of the event instances
*
*/

kukit.er.BinderInfoRegistry = function () {
    this.info = {};
};

kukit.er.BinderInfoRegistry.prototype.getOrCreateBinderInfo =
    function (id, className, namespace) {
    // Get or create the event.
    var binderInfo = this.info[id];
    if (typeof(binderInfo) == 'undefined') {
        // Create a new event.
;;;     var msg = 'Instantiating event id [' + id + '], className [';
;;;     msg += className + '], namespace [' + namespace + '].';
;;;     kukit.logDebug(msg);
        var binder = kukit.eventsGlobalRegistry.getBinder(className);
        var binderInstance = new binder();
        
        binderInfo = this.info[id] = new kukit.er.BinderInfo(binderInstance);

        // decorate it with id and class
        binderInstance.__binderId__ = id;
        binderInstance.__binderClassName__ = className;
        binderInstance.__eventNamespace__ = namespace;
        // store the bound rules
        //binderInstance.__bound_rules__ = [];
    } else if (binderInfo.getBinderInstance().__binderClassName__ != 
        className) {
        // just paranoia
;;;     kukit.E = 'Conflicting class for event id [' + id + '], [';
;;;     kukit.E += binderInfo.getBinderInstance().__binderClassName__;
;;;     kukit.E += '] != [' + className + '].';
        throw kukit.E;
    }
    return binderInfo;
};

kukit.er.BinderInfoRegistry.prototype.getBinderInfoById = function (id) {
    // Get an event.
    var binderInfo = this.info[id];
    if (typeof(binderInfo) == 'undefined') {
;;;     kukit.E = 'Event with id [' + id + '] not found.';
        throw kukit.E;
    }
    return binderInfo;
};

kukit.er.BinderInfoRegistry.prototype.getSingletonBinderInfoByName =
    function (namespace, name) {
    //Get className
    var className = kukit.eventsGlobalRegistry.get(namespace, name).className;
    // Get an event.
    var id = kukit.rd.makeId(namespace, className);
    var binderInfo = this.info[id];
    if (typeof(binderInfo) == 'undefined') {
;;;     kukit.E = 'Singleton event with namespace [' + namespace;
;;;     kukit.E += '] and (event) name [' + name + '] not found.';
        throw kukit.E;
    }
    return binderInfo;
};

kukit.er.BinderInfoRegistry.prototype.startBindingPhase = function () {
    // At the end of the binding phase, we want to process our events. This
    // must include all the binder instances we bound in this phase.
    for (var id in this.info) {
        var binderInfo = this.info[id];
        // process binding on this instance.
        binderInfo.startBindingPhase();
    }
};

kukit.er.BinderInfoRegistry.prototype.processBindingEvents = function () {
    // At the end of the binding phase, we want to process our events. This
    // must include all the binder instances we bound in this phase.
    for (var id in this.info) {
        var binderInfo = this.info[id];
        // process binding on this instance.
        binderInfo.processBindingEvents();
    }
};

/*
* class BinderInfo
*
* Information about the given binder instance. This contains the instance and
* various binding info. Follows the workflow of the binding in different stages.
*
*/

kukit.er.BinderInfo = function (binderInstance) {
    this.binderInstance = binderInstance;
    this.bound = new kukit.er.OperRegistry();
    this.startBindingPhase();
};

kukit.er.BinderInfo.prototype.getBinderInstance = function () {
    return this.binderInstance;
};

kukit.er.BinderInfo.prototype.startBindingPhase = function () {
    // The bindind phase starts and it has the information for
    // the currently on-bound events.
    this.binding = new kukit.er.OperRegistry();
};

kukit.er.BinderInfo.prototype.bindOper = function (oper) {
    // We mark a given oper. This means a binding on the binderInstance 
    // for given event, node and eventRule (containing event namespace,
    // name, and evt- parms.)
    //
    // first see if it can go to already bound ones
    this.bound.checkOperBindable(oper);
    // then register it properly to the binding events
    this.binding.bindOper(oper);
};

kukit.er.BinderInfo.prototype.processBindingEvents = function () {
    // We came to the end of the binding phase. Now we process all our binding
    // events, This will do the actual binding on the browser side.
    this.binding.processBindingEvents(this.binderInstance);
    // Now we to add these to the new ones.
    this.binding.propagateTo(this.bound);
    // Delete them from the registry, to protect against accidents.
    this.binding = null;
};


/*
*  class OperRegistry
*
*  OperRegistry is associated with a binder instance in the 
*  BinderInfoRegistry, and remembers bounding information.
*  This is used both to remember all the bindings for a given
*  instance, but also just to remember the bindings done during
*  a given event setup phase.
*/

kukit.er.OperRegistry = function () {
    this.infoPerName = {};
    this.infoPerNode = {};
};

// XXX XXX XXX we can do this without full cloning, more efficiently.
kukit.er.OperRegistry.prototype.propagateTo = function (newreg) {
    for (var key in this.infoPerName) {
        var rulesPerName = this.infoPerName[key];
        for (var name in rulesPerName) {
            var oper = rulesPerName[name];
            newreg.bindOper(oper);
        }
    }
};

kukit.er.OperRegistry.prototype.checkOperBindable =
    function (oper, name, nodeHash) {
    // Check if the binding with this oper could be done.
    // Throw exception otherwise.
    //
    // Remark. We need  different check and bind method,
    // because we need to bind to the currently
    // processed nodes, but we need to check duplication 
    // in all the previously bound nodes.
    var info = this.infoPerName;
    // name and nodeHash are for speedup.
    if (typeof(nodeHash) == 'undefined') {
        name = oper.eventRule.kssSelector.name;
        nodeHash = kukit.rd.hashNode(oper.node);
    }
    var rulesPerName = info[name];
    if (typeof(rulesPerName) == 'undefined') {
        // Create an empty list.
        rulesPerName = info[name] = {};
    } else if (typeof(rulesPerName[nodeHash]) != 'undefined') {
;;;     kukit.E = 'Mismatch in bind registry,[ ' + name;
;;;     kukit.E += '] already bound to node in this instance.'; 
        throw kukit.E;
    }
    return rulesPerName;
};
    
kukit.er.OperRegistry.prototype.bindOper = function (oper) {
    // Marks binding between binderInstance, eventName, node.
    var name = oper.eventRule.kssSelector.name;
    var nodeHash = kukit.rd.hashNode(oper.node);
    var rulesPerName = this.checkOperBindable(oper, name, nodeHash);
    rulesPerName[nodeHash] = oper;
    // also store per node info
    var rulesPerNode = this.infoPerNode[nodeHash];
    if (typeof(rulesPerNode) == 'undefined') {
        // Create an empty list.
        rulesPerNode = this.infoPerNode[nodeHash] = {};
    }
    rulesPerNode[name] = oper;
};

// XXX This will need refactoring.
/// We would only want to lookup from our registry and not the other way around.
kukit.er.OperRegistry.prototype.processBindingEvents = 
    function (binderInstance) {
    var eventRegistry = kukit.eventsGlobalRegistry;
    for (var i=0; i < eventRegistry.eventSets.length; i++) {
        var eventSet = eventRegistry.eventSets[i];
        // Only process binding events (and ignore non-binding ones)
        if (eventSet.bindMethodName) {
            if (binderInstance.__eventNamespace__ == eventSet.namespace) {
                // Process the binding event set.
                // This will call the actual bindmethods
                // according to the specified iterator.
                var iterator = kukit.er.getBindIterator(eventSet.iterName);
                iterator.call(this, eventSet, binderInstance);
            }
        }
    }
};

// XXX The following methods will probably disappear as iterators 
// replace their functionality.

kukit.er.OperRegistry.prototype.getBoundOperForNode = function (name, node) {
    // Get the oper that is bound to a given eventName
    // to a node in this binderInstance
    // returns null, if there is no such oper.
    var rulesPerName = this.infoPerName[name];
    if (typeof(rulesPerName) == 'undefined') {
        return null;
    }
    var nodeHash = kukit.rd.hashNode(node);
    var oper = rulesPerName[nodeHash];
    if (typeof(oper) == 'undefined') {
        return null;
    }
    // Return it
    return oper;
};

kukit.er.OperRegistry.prototype.getBoundOpers = function (name) {
    // Get the opers bound to a given eventName (to any node)
    // in this binderInstance
    var opers = [];
    var rulesPerName = this.infoPerName[name];
    if (typeof(rulesPerName) != 'undefined') {
        // take the values as a list
        for (var nodeHash in rulesPerName) {
            opers.push(rulesPerName[nodeHash]);
        }
    }
    // Return it
    return opers;
};

// Iterators
// The getBindIterator returns a function that gets executed on
// the oper registry.
//
// Iterators receive the eventSet as a parameter
// plus a binderInstance and a method. They need to iterate by calling this
// as method.call(binderInstance, ...); where ... can be any parms this
// given iteration specifies.
//

kukit.er.getBindIterator = function(iterName) {
    // attempt to find canonical version of string
    // and shout if it does not match.
    // String must start uppercase.
    var canonical = iterName.substring(0, 1).toUpperCase() + 
            iterName.substring(1);
    if (iterName != canonical) {
        // BBB 2007.12.31, this will turn into an exception.
;;;     var msg = 'Deprecated the lowercase iterator names in last ';
;;;     msg += 'parameters of ';
;;;     msg += 'kukit.eventsGlobalRegistry.registerForAllEvents, use [';
;;;     msg += canonical + '] instead of [' + iterName + '] (2007-12-31)';
;;;     kukit.logWarning(msg);
        iterName = canonical;
        }
    return kukit.er.OperRegistry.prototype['_iterate' + iterName];
};

kukit.er.OperRegistry.prototype.callBindMethod = 
    function (eventSet, binderInstance, p1, p2, p3, p4, p5, p6) {
    var method = binderInstance[eventSet.bindMethodName];
    // Protect the binding for better logging
;;; try {
        method.call(binderInstance, p1, p2, p3, p4, p5, p6);
;;; } catch(e) {
;;;     var msg = e;
;;;     var names = eventSet.names;
;;;     var namespace = eventSet.namespace;
;;;     kukit.E = new kukit.err.rd.EventBindError(msg, names, namespace);
;;;     throw kukit.E;
;;; }
};

// This calls the bind method by each bound oper one by one.
// Eventname and funcToBind are passed too.
// this is the legacy ([EachLegacy]) way
kukit.er.OperRegistry.prototype._iterateEachLegacy =
    function (eventSet, binderInstance) {
    for (var i=0; i<eventSet.names.length; i++) {
        var rulesPerName = this.infoPerName[eventSet.names[i]];
        if (typeof(rulesPerName) != 'undefined') {
            for (var nodeHash in rulesPerName) {
                var oper = rulesPerName[nodeHash];
                var eventName = oper.getEventName();
                var funcToBind = oper.makeExecuteActionsHook();
                this.callBindMethod(eventSet, binderInstance, eventName,
                    funcToBind, oper);
            }
        }
    }
};


// This calls the bind method by each bound oper one by one.
// Eventname and funcToBind are passed too.
// this is the preferred ([Each]) way. Parameters are different from EachLegacy.
kukit.er.OperRegistry.prototype._iterateEach =
    function (eventSet, binderInstance) {
    for (var i=0; i<eventSet.names.length; i++) {
        var rulesPerName = this.infoPerName[eventSet.names[i]];
        if (typeof(rulesPerName) != 'undefined') {
            for (var nodeHash in rulesPerName) {
                var oper = rulesPerName[nodeHash];
                this.callBindMethod(eventSet, binderInstance, oper);
            }
        }
    }
};

// This calls the bind method by the list of bound opers
kukit.er.OperRegistry.prototype._iterateOpers =
    function (eventSet, binderInstance) {
    var opers = [];
    for (var i=0; i<eventSet.names.length; i++) {
        var rulesPerName = this.infoPerName[eventSet.names[i]];
        if (typeof(rulesPerName) != 'undefined') {
            for (var nodeHash in rulesPerName) {
                opers.push(rulesPerName[nodeHash]);
            }
        }
    }
    this.callBindMethod(eventSet, binderInstance, opers);
};

// This calls the bind method by a mapping eventName:oper
// per each bound node individually
kukit.er.OperRegistry.prototype._iterateNode =
    function (eventSet, binderInstance) {
    for (var nodeHash in this.infoPerNode) {
        var rulesPerNode = this.infoPerNode[nodeHash];
        // filter only the events we are interested in
        var filteredRules = {};
        var operFound = false;
        for (var i=0; i<eventSet.names.length; i++) {
            var name = eventSet.names[i];
            var oper = rulesPerNode[name];
            if (typeof(oper) != 'undefined') {
                filteredRules[name] = oper;
                operFound = oper;
            }
        }
        // call it
        // All opers have the same node, the last one is yet in operFound, so
        // we use it as a second parameter to the call.
        // The method may or may not want to use this.
        if (operFound) {
            this.callBindMethod(eventSet, binderInstance, filteredRules,
                operFound.node);
        }
    }
};

// This calls the bind method once per instance, by a list of
// items, where item.node is the node and item.opersByEventName nodeHash:item
// in item there is item.node and item.opersByEventName
kukit.er.OperRegistry.prototype._iterateAllNodes = 
    function (eventSet, binderInstance) {
    var items = [];
    var hasResult = false;
    for (var nodeHash in this.infoPerNode) {
        var rulesPerNode = this.infoPerNode[nodeHash];
        // filter only the events we are interested in
        var filteredRules = {};
        var operFound = false;
        for (var i=0; i<eventSet.names.length; i++) {
            var name = eventSet.names[i];
            var oper = rulesPerNode[name];
            if (typeof(oper) != 'undefined') {
                filteredRules[name] = oper;
                operFound = oper;
            }
        }
        if (operFound) {
            var item = {node: operFound.node, 
                opersByEventName: filteredRules};
            items.push(item);
            hasResult = true;
        }
    }
    // call the binder method
    if (hasResult) {
        this.callBindMethod(eventSet, binderInstance, items);
    }
};

