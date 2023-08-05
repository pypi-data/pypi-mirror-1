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
*  kukit.eventsGlobalRegistry.register(namespace, eventname, func, 
*    bindmethodname, defaultactionmethodname);
*  
*     namespace = null: means global namespace
*     defaultactionmethodname = null: if there is no default action implemented
*     func must be a class (constructor) function, this is the class that
*           implements the binder.
*/
kukit.er.EventRegistry = function () {
    this.content = {};
    this.classes = {};
    this.eventsets = [];
};

/* binder registration */

kukit.er.EventRegistry.prototype.registerBinder = function(classname, func) {
    if (typeof(func) == 'undefined') {
        throw 'func argument is mandatory when registering an event binder (EventRegistry.registerBinder).';
    }
    if (this.classes[classname]) {
        // Do not allow redefinition
        kukit.logError('Error : event class "' + classname + '" already registered.');
        return;
    
    }
    // Decorate and store the class
    kukit.er.decorateEventBinderClass(func);
    this.classes[classname] = func;
};

kukit.er.EventRegistry.prototype.existsBinder = function(classname) {
    var func = this.classes[classname];
    return (typeof(func) != 'undefined');
};

kukit.er.EventRegistry.prototype.getBinder = function(classname) {
    var func = this.classes[classname];
    if (! func) {
        // not found
        throw 'Error : undefined event setup type ' + classname;
        }
    return func;
};

/* events (methods) registration  helpers (not to be called directly) */

kukit.er.EventRegistry.prototype._register = function(namespace, eventname, klass,
        bindmethodname, defaultactionmethodname, bindmethodapi) {
    if (typeof(defaultactionmethodname) == 'undefined') {
        throw 'some arguments are not passed when calling EventRegistry.register';
    }
    // Find out the class name. (Not specified now.)
    var classname = klass.prototype.__classname__;
    if (typeof(classname) == 'undefined') {
        // Create a classname, and register it too.
        classname = '' + kukit.er.eventClassCounter;
        kukit.er.eventClassCounter += 1;
        this.registerBinder(classname, klass);
        klass.prototype.__classname__ = classname;
    }
    if (!eventname) {
        throw 'eventname argument cannot be empty when registering an event (EventRegistry.register)';
    }
    var key = this._getKey(namespace, eventname);
    var entry = this.content[key];
    if (typeof(entry) != 'undefined') {
        if (key[0] == '-') {
            key = key.substring(1);
        }
        throw 'In EventRegistry.register double registration of key "' + key + '"';
    }
    // register it
    this.content[key] = {
        'classname': classname,
        'bindmethodname': bindmethodname,
        'defaultactionmethodname': defaultactionmethodname,
        'bindmethodapi': bindmethodapi
        };
};

/* events (methods) binding "ForAll" registration */

kukit.er.EventRegistry.prototype._registerEventSet = function(namespace, names) {
    // At this name the class and event should be checked already. so this should
    // be called _after_ _register.
    this.eventsets.push({'namespace': namespace, 'names': names});
};


/* there are the actual registration methods, to be called from plugins */

kukit.er.EventRegistry.prototype.register = function(namespace, eventname, klass,
        bindmethodname, defaultactionmethodname) {
    this._register(namespace, eventname, klass, bindmethodname, defaultactionmethodname, 'old');
    this._registerEventSet(namespace, [eventname]);
};

kukit.er.EventRegistry.prototype.registerForAllEvents = function(namespace, eventnames, klass,
        bindmethodname, defaultactionmethodname) {
    if (typeof(eventnames) == 'string') {
        eventnames = [eventnames];
        }
    for (var i=0; i<eventnames.length; i++) {
        var eventname = eventnames[i];
        this._register(namespace, eventname, klass, bindmethodname, defaultactionmethodname, 'new');
    }
    this._registerEventSet(namespace, eventnames);
};

kukit.er.EventRegistry.prototype._getKey = function(namespace, eventname) {
    if (namespace == null) {
        namespace = '';
    } else if (namespace.split('-') > 1) {
        throw 'In EventRegistry.register namespace cannot contain -';
    }
    return namespace + '-' + eventname;
};

kukit.er.EventRegistry.prototype.exists = function(namespace, eventname) {
    var key = this._getKey(namespace, eventname);
    var entry = this.content[key];
    return (typeof(entry) != 'undefined');
};

kukit.er.EventRegistry.prototype.get = function(namespace, eventname) {
    var key = this._getKey(namespace, eventname);
    var entry = this.content[key];
    if (typeof(entry) == 'undefined') {
        if (key[0] == '-') {
            key = key.substring(1);
            throw 'Error : undefined global event key ' + key + ' (or maybe namespace is missing?)';
        } else {
            throw 'Error : undefined event key ' + key;
        }
    } 
    return entry;
};

kukit.eventsGlobalRegistry = new kukit.er.EventRegistry();


/* XXX deprecated methods, to be removed asap */

kukit.er.eventRegistry = {};
kukit.er.eventRegistry.register = function(namespace, eventname, klass,
        bindmethodname, defaultactionmethodname) {
    kukit.logWarning('Deprecated kukit.er.eventRegistry.register, use kukit.eventsGlobalRegistry.register instead! (' + namespace + '-' + eventname + ')');
    kukit.eventsGlobalRegistry.register(namespace, eventname, klass,
        bindmethodname, defaultactionmethodname);
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
*  be accessed with the "pass" kss parameter provider.)
*
* Call examples: 
*
* trigger an event bound to a given state instance, same node
*
*     binderinstance.__continue_event__('doit', oper.node, {'extravalue': '5'});
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
*     binderinstance.__continue_event__('doit', null, {'extravalue': '5'});
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
*     binderinstance.__continue_event_allnodes__('doit', {'extravalue': '5'});
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

kukit.er.EventBinder__continue_event__ = function(name, node, parms) {
    // Trigger a continuation event bound to a given state instance, given node
    // (or on document, if node = null)
    //
    var oper = new kukit.op.Oper();
    oper.node = node;
    if (node) {
        // if we found the binding, just use that
        var info = kukit.engine.binderInfoRegistry.getBinderInfoById(this.__binder_id__);
        var newoper = info.bound.getBoundOperForNode(name, node);
        if (newoper) {
            oper = newoper;
        }
    } else {
        oper.eventrule =  kukit.engine.documentRules.getMergedRule('document', name, this);
    }
    // Look up the behaviour rule, if any.
    var behav_eventrule =  kukit.engine.documentRules.getMergedRule('behaviour', name, this);
    if (behav_eventrule) {
        if (! oper.eventrule) {
            // There was no node matching for the rule, use behaviour rule
            // this allows to set up parametrized actions in general.
            oper.eventrule = behav_eventrule;
        } else {
            // XXX this case should go away, as we should check this already from binding time
            // and signal the appropriate error.
            // Also note that behaviour roles will only be allowed for "non-binding" events.
            kukit.logError('Behaviour rule for continuation event "' + name + '" will be ignored, because we found an explicit rule.');
        }
    }
    // If parameters are specified in the call, use them.
    if (typeof(parms) != 'undefined') {
        oper.parms = parms;
    } else {
        oper.parms = {};
    }
    // (if eventrule is null here, we can yet have the default method, so go on.)
    this._EventBinder_triggerevent(name, oper);
    kukit.logDebug('Continuation event "' + name + '" executed on same node.');
};

kukit.er.EventBinder__continue_event_allnodes__ = function(name, parms) {
    // Trigger an event bound to a given state instance, on all nodes.
    // (or on document, if node = null)
    // if no other nodes execute.
    var executed = 0;
    // Normal rules. If any of those match, execute them too
    // each on the node that it selects - not on the original node.
    var oper = new kukit.op.Oper();
    var info = kukit.engine.binderInfoRegistry.getBinderInfoById(this.__binder_id__);
    var opers = info.getBoundOpers(name);
    for (var i=0; i<opers.length; i++) {
        var oper = opers[i];
        var newoper = oper.clone();
        if (typeof(parms) != 'undefined') {
            newoper.parms = parms;
        } else {
            newoper.parms = {};
        }
        this._EventBinder_triggerevent(name, newoper);
        executed += 1;
    }
    kukit.logDebug('Event "' + name + '" executed on ' + executed + ' nodes.');
};

kukit.er.EventBinder_makeFuncToBind = function(name, node) {
   var executor = new kukit.er.LateBinder(this, name, node);
   return function() {
       executor.executeActions();
   };
};

kukit.er.LateBinder = function(binderinstance, name, node) {
    this.binderinstance = binderinstance;
    this.name = name;
    this.node = node;
    this.bound = null;
};

kukit.er.LateBinder.prototype.executeActions = function() {
    if (! this.bound) {
        kukit.log('Attempt of late binding for event ' + this.name + ', node ' + this.node.nodeName);
        if (kukit.hasFirebug) {
            kukit.log(this.node);
        }
        var info = kukit.engine.binderInfoRegistry.getBinderInfoById(this.binderinstance.__binder_id__);
        var oper = info.bound.getBoundOperForNode(this.name, this.node);
        if (oper) {
            // (if eventrule is null here, we can yet have the default method, so go on.)
            oper.parms = {};
            this.bound = function() {
                this.binderinstance._EventBinder_triggerevent(this.name, oper);
            };
            kukit.log('node bound');
        } else {
            kukit.logWarning('no node bound');
            this.bound = function() {};
        }
    }
    this.bound();
};        

kukit.er.EventBinder_triggerevent = function(name, oper) {
    // Private. Called from __continue_event__ or from main event execution.
    oper.binderinstance = this;
    if (oper.eventrule) {
        // Call the actions, if we had an event rule.
        // This includes calling the default action.
        oper.eventrule.actions.execute(oper);
    } else {
        // In case there is no event rule, just call the default event action.
        var namespace = this.__event_namespace__;
        kukit.logDebug('Calling implicit event "' + name + '" on namespace "' + namespace + '"');
        var success = oper.executeDefaultAction(name, true);
        if (! success) {
            // instead of the standard message give more specific reason:
            // either way we should have executed something...
            throw 'Could not trigger event name "' + name + '" on namespace "' + namespace + '", because there is neither an explicit kss rule, nor a default method';
        }
    }
};

/* (default) method call handling */

kukit.er.EventBinder_callmethod = function(namespace, name, oper, methodname) {
    // hidden method for calling just a method and checking that is exists.
    // (called from oper)
    var method = this[methodname];
    if (! method) {
        throw 'Could not trigger event name "' + name + '" on namespace "' + namespace + '", because the method "' + methodname + '" does not exist.';
    }
    // call it
    oper.binderinstance = this;
    method.call(this, name, oper);
};

kukit.er.decorateEventBinderClass = function(cls) {
    cls.prototype.__continue_event__ = kukit.er.EventBinder__continue_event__;
    cls.prototype.__continue_event_allnodes__ = kukit.er.EventBinder__continue_event_allnodes__;
    cls.prototype._EventBinder_triggerevent = kukit.er.EventBinder_triggerevent;
    cls.prototype._EventBinder_callmethod = kukit.er.EventBinder_callmethod;
    cls.prototype.__make_func_to_bind__ = kukit.er.EventBinder_makeFuncToBind;
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

kukit.er.BinderInfoRegistry.prototype.getOrCreateBinderInfo = function (id, classname, namespace) {
    // Get or create the event.
    var binderinfo = this.info[id];
    if (typeof(binderinfo) == 'undefined') {
        // Create a new event.
        kukit.logDebug('instantiating event id=' + id + ', classname=' + classname + ', namespace=' + namespace);
        binderinstance = new (kukit.eventsGlobalRegistry.getBinder(classname))();
        
        binderinfo = this.info[id] = new kukit.er.BinderInfo(binderinstance);

        // decorate it with id and class
        binderinstance.__binder_id__ = id;
        binderinstance.__binder_classname__ = classname;
        binderinstance.__event_namespace__ = namespace;
        // store the bound rules
        //binderinstance.__bound_rules__ = [];
    } else if (binderinfo.getBinderInstance().__binder_classname__ != classname) {
        // just paranoia
        throw 'Conflicting class for event id "' + id + '", "' + binderinfo.getBinderInstance().__binder_classname__
                + '" != "' + classname + '"';
    }
    return binderinfo;
};

kukit.er.BinderInfoRegistry.prototype.getBinderInfoById = function (id) {
    // Get an event.
    var binderinfo = this.info[id];
    if (typeof(binderinfo) == 'undefined') {
        throw 'Event with id "' + id + '" not found.';
    }
    return binderinfo;
};

kukit.er.BinderInfoRegistry.prototype.getSingletonBinderInfoByName = function (namespace, name) {
    //Get classname
    var classname = kukit.eventsGlobalRegistry.get(namespace, name).classname;
    // Get an event.
    var id = kukit.rd.makeId(namespace, classname);
    var binderinfo = this.info[id];
    if (typeof(binderinfo) == 'undefined') {
        throw 'Singleton event with namespace "' + namespace + '" and (event) name "' + name + '" not found.';
    }
    return binderinfo;
};

kukit.er.BinderInfoRegistry.prototype.startBindingPhase = function () {
    // At the end of the binding phase, we want to process our events. This
    // must include all the binder instances we bound in this phase.
    for (var id in this.info) {
        var binderinfo = this.info[id];
        // process binding on this instance.
        binderinfo.startBindingPhase();
    }
};

kukit.er.BinderInfoRegistry.prototype.processBindingEvents = function () {
    // At the end of the binding phase, we want to process our events. This
    // must include all the binder instances we bound in this phase.
    for (var id in this.info) {
        var binderinfo = this.info[id];
        // process binding on this instance.
        binderinfo.processBindingEvents();
    }
};

/*
* class BinderInfo
*
* Information about the given binder instance. This contains the instance and
* various binding info. Follows the workflow of the binding in different stages.
*
*/

kukit.er.BinderInfo = function (binderinstance) {
    this.binderinstance = binderinstance;
    this.bound = new kukit.er.OperRegistry();
    this.startBindingPhase();
};

kukit.er.BinderInfo.prototype.getBinderInstance = function () {
    return this.binderinstance;
};

kukit.er.BinderInfo.prototype.startBindingPhase = function () {
    // The bindind phase starts and it has the information for
    // the currently on-bound events.
    this.binding = new kukit.er.OperRegistry();
};

kukit.er.BinderInfo.prototype.bindOper = function (oper) {
    // We mark a given oper. This means a binding on the binderinstance 
    // for given event, node and eventrule (containing event namespace,
    // name, and evt- parms.)

    // first see if it can go to already bound ones
    this.bound.checkOperBindable(oper);
    // then register it properly to the binding events
    this.binding.bindOper(oper);
};

kukit.er.BinderInfo.prototype.processBindingEvents = function () {
    // We came to the end of the binding phase. Now we process all our binding
    // events, This will do the actual binding on the browser side.
    var eventRegistry = kukit.eventsGlobalRegistry;
    for (var i=0; i < eventRegistry.eventsets.length; i++) {
        var eventset = eventRegistry.eventsets[i];
        if (this.binderinstance.__event_namespace__ == eventset.namespace) {
            this._processBindingEventSet(eventset.names);
        }
    }
    // Now we to add these to the new ones.
    this.binding.propagateTo(this.bound);
    // Delete them from the registry, to protect against accidents.
    this.binding = null;
};

kukit.er.BinderInfo.prototype._processBindingEventSet = function (names) {
    // Bind finally for all the opers collected
    var opers = this.binding.getBoundOpersForEventSet(names);
    if (opers.length == 0) {
        return;
    }
    // find the bind method
    // (We use the name and namespace from the first oper, as the bindmethod
    // should be identical anyway.
    var kss_selector = opers[0].eventrule.kss_selector;
    var namespace = kss_selector.namespace;
    var name = kss_selector.name;
    var reg = kukit.eventsGlobalRegistry.get(namespace, name);
    var methodname = reg.bindmethodname;
    // XXX this is now disabled. We want to allow these events to "bind" on different nodes,
    // however there is no actual event bound. 
    if (! methodname) {
        return;
        //throw new kukit.err.rd.EventBindError('Method is not defined as bindable', name, namespace);
    }
    var method = this.binderinstance[methodname];
    if (typeof(method) == 'undefined' ) {
        throw new kukit.err.rd.EventBindError('Method "' + methodname + '" does not exist', name, namespace);
    }
    // Ok. Now decide if we go with the new or the old api.
    if (reg.bindmethodapi == 'new') {
        // Protect the binding for better logging
        try {
            method.call(binderinstance, opers);
        } catch(e) {
            throw new kukit.err.rd.EventBindError('Error during binding, reason: [' + e + ']', name, namespace);
        }
    } else { // old
        for (var i=0; i<opers.length; i++) {
            var oper = opers[i];
            var func_to_bind = oper.makeExecuteActionsHook();
            if (this.binderinstance != oper.binderinstance) {
                throw new kukit.err.rd.EventBindError('fatal: wrong binder instance');
            }
            var binderinstance = oper.binderinstance;
            var eventname = oper.getEventName();
            // Protect the binding for better logging
            try {
                method.call(binderinstance, eventname, func_to_bind, oper);
            } catch(e) {
                throw new kukit.err.rd.EventBindError('Error during binding, reason: [' + e + ']', eventname, oper.getEventNamespace());
            }
        }
    }
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
    this.info = {};
};

kukit.er.OperRegistry.prototype.propagateTo = function (newreg) {
    for (var key in this.info) {
        var rules_per_name = this.info[key];
        for (var name in rules_per_name) {
            var oper = rules_per_name[name];
            newreg.bindOper(oper);
        }
    }
};

kukit.er.OperRegistry.prototype.checkOperBindable = function (oper) {
    // Check if the binding with this oper could be done.
    // Throw exception otherwise.
    var info = this.info;
    var name = oper.eventrule.kss_selector.name;
    var nodehash = kukit.rd.hashnode(oper.node);
    var rules_per_name = info[name];
    if (typeof(rules_per_name) == 'undefined') {
        // Create an empty list.
        rules_per_name = info[name] = {};
    } else if (typeof(rules_per_name[nodehash]) != 'undefined') {
        throw 'Mismatch in bind registry, ' + name + ' already bound to node in this instance.'; 
    }
    return rules_per_name;
};
    
kukit.er.OperRegistry.prototype.bindOper = function (oper) {
    // Marks binding between binderinstance, eventname, node.
    var nodehash = kukit.rd.hashnode(oper.node);
    var rules_per_name = this.checkOperBindable(oper);
    rules_per_name[nodehash] = oper;
};

kukit.er.OperRegistry.prototype.getBoundOperForNode = function (name, node) {
    // Get the oper that is bound to a given eventname to a node in this binderinstance
    // returns null, if there is no such oper.
    var rules_per_name = this.info[name];
    if (typeof(rules_per_name) == 'undefined') {
        return null;
    }
    var nodehash = kukit.rd.hashnode(node);
    var oper = rules_per_name[nodehash];
    if (typeof(oper) == 'undefined') {
        return null;
    }
    // Return it
    return oper;
};

kukit.er.OperRegistry.prototype.getBoundOpers = function (name) {
    // Get the opers bound to a given eventname (to any node) in this binderinstance
    var opers = [];
    var rules_per_name = this.info[name];
    if (typeof(rules_per_name) != 'undefined') {
        // take the values as a list
        for (var nodehash in rules_per_name) {
            opers.push(rules_per_name[nodehash]);
        }
    }
    // Return it
    return opers;
};

kukit.er.OperRegistry.prototype.getBoundOpersForEventSet = function (names) {
    // Returns all opers for a given eventset.
    var opers = [];
    for (var i=0; i<names.length; i++) {
        var name = names[i];
        opers = opers.concat(this.getBoundOpers(name));
    }
    return opers;
};
