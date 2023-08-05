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
        ;;; kukit.E = 'func argument is mandatory when registering an event binder (EventRegistry.registerBinder).';
        throw kukit.E;
    }
    if (this.classes[classname]) {
        // Do not allow redefinition
        ;;; kukit.logError('Error : event class "' + classname + '" already registered.');
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
        ;;; kukit.E = 'Error : undefined event setup type ' + classname;
        throw kukit.E;
        }
    return func;
};

/* events (methods) registration  helpers (not to be called directly) */

kukit.er.EventRegistry.prototype._register = function(namespace, eventname, klass,
        bindmethodname, defaultactionmethodname, itername) {
    if (typeof(defaultactionmethodname) == 'undefined') {
        ;;; kukit.E = 'some arguments are not passed when calling EventRegistry.register';
        throw kukit.E;
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
        ;;; kukit.E = 'eventname argument cannot be empty when registering an event (EventRegistry.register)';
        throw kukit.E;
    }
    var key = this._getKey(namespace, eventname);
    var entry = this.content[key];
    if (typeof(entry) != 'undefined') {
        if (key[0] == '-') {
            key = key.substring(1);
        }
        ;;; kukit.E = 'In EventRegistry.register double registration of key "' + key + '"';
        throw kukit.E;
    }
    // check bindmethodname and defaultactionmethodname
    if (bindmethodname && ! klass.prototype[bindmethodname]) {
        ;;; kukit.E = 'In EventRegistry.register bind method "' + bindmethodname;
        ;;; kukit.E += '" is undefined for event "' + eventname + '" namespace "' + namespace + '"';
        throw kukit.E;
    }
    if (defaultactionmethodname && ! klass.prototype[defaultactionmethodname]) {
        ;;; kukit.E = 'In EventRegistry.register default action method "' + defaultactionmethodname;
        ;;; kukit.E += '" is undefined for event "' + eventname + '" namespace "' + namespace + '"';
        throw kukit.E;
    }
    // check the iterator.
    if  (! kukit.er.getBindIterator(itername)) {
        ;;; kukit.E = 'In EventRegistry.register unknown bind iterator "' + itername + '"';
        throw kukit.E;
    }
    // register it
    this.content[key] = {
        'classname': classname,
        'bindmethodname': bindmethodname,
        'defaultactionmethodname': defaultactionmethodname,
        'itername': itername
        };
};

/* events (methods) binding "ForAll" registration */

kukit.er.EventRegistry.prototype._registerEventSet = function(namespace, names, itername, bindmethodname) {
    // At this name the values should be checked already. so this should
    // be called _after_ _register.
    this.eventsets.push({
        'namespace': namespace, 
        'names': names,
        'itername': itername,
        'bindmethodname': bindmethodname
        });
};

/* there are the actual registration methods, to be called from plugins */

kukit.er.EventRegistry.prototype.register = function(namespace, eventname, klass,
        bindmethodname, defaultactionmethodname) {
    this._register(namespace, eventname, klass, bindmethodname, defaultactionmethodname, 'each_legacy');
    this._registerEventSet(namespace, [eventname], 'each_legacy', bindmethodname);
};

kukit.er.EventRegistry.prototype.registerForAllEvents = function(namespace, eventnames, klass,
        bindmethodname, defaultactionmethodname, itername) {
    if (typeof(eventnames) == 'string') {
        eventnames = [eventnames];
        }
    for (var i=0; i<eventnames.length; i++) {
        var eventname = eventnames[i];
        this._register(namespace, eventname, klass, bindmethodname, defaultactionmethodname, itername);
    }
    this._registerEventSet(namespace, eventnames, itername, bindmethodname);
};

kukit.er.EventRegistry.prototype._getKey = function(namespace, eventname) {
    if (namespace == null) {
        namespace = '';
    } else if (namespace.split('-') > 1) {
        ;;; kukit.E = 'In EventRegistry.register namespace cannot contain -';
        throw kukit.E;
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
        if (key.substr(0, 1) == '-') {
            ;;; key = key.substring(1);
            ;;; kukit.E = 'Error : undefined global event key ';
            ;;; kukit.E += key + ' (or maybe namespace is missing?)';
            throw kukit.E;
        } else {
            ;;; kukit.E = 'Error : undefined event key ' + key;
            throw kukit.E;
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

kukit.er.EventBinder__continue_event__ = function(name, node, defaultparms) {
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
            ;;; kukit.logError('Behaviour rule for continuation event "' + name + '" will be ignored, because we found an explicit rule.');
        }
    }
    // If parameters are specified in the call, use them.
    if (typeof(defaultparms) != 'undefined') {
        oper.defaultparms = defaultparms;
    } else {
        oper.defaultparms = {};
    }
    // (if eventrule is null here, we can yet have the default method, so go on.)
    this._EventBinder_triggerevent(name, oper);
    ;;; kukit.logDebug('Continuation event "' + name + '" executed on same node.');
};

kukit.er.EventBinder__continue_event_allnodes__ = function(name, defaultparms) {
    // Trigger an event bound to a given state instance, on all nodes.
    // (or on document, if node = null)
    // if no other nodes execute.
    var executed = 0;
    // Normal rules. If any of those match, execute them too
    // each on the node that it selects - not on the original node.
    var oper = new kukit.op.Oper();
    var info = kukit.engine.binderInfoRegistry.getBinderInfoById(this.__binder_id__);
    var opers = info.bound.getBoundOpers(name);
    for (var i=0; i<opers.length; i++) {
        var oper = opers[i];
        var newoper = oper.clone();
        if (typeof(defaultparms) != 'undefined') {
            newoper.defaultparms = defaultparms;
        } else {
            newoper.defaultparms = {};
        }
        this._EventBinder_triggerevent(name, newoper);
        executed += 1;
    }
    ;;; kukit.logDebug('Event "' + name + '" executed on ' + executed + ' nodes.');
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
        ;;; kukit.log('Attempt of late binding for event ' + this.name + ', node ' + this.node.nodeName);
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
            ;;; kukit.log('node bound');
        } else {
            ;;; kukit.logWarning('no node bound');
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
        ;;; kukit.logDebug('Calling implicit event "' + name + '" on namespace "' + namespace + '"');
        var success = oper.executeDefaultAction(name, true);
        if (! success) {
            // instead of the standard message give more specific reason:
            // either way we should have executed something...
            ;;; kukit.E = 'Could not trigger event name "' + name;
            ;;; kukit.E += '" on namespace "' + namespace;
            ;;; kukit.E += '", because there is neither an explicit kss rule, nor a default method';
            throw kukit.E;
        }
    }
};

/* (default) method call handling */

kukit.er.EventBinder_callmethod = function(namespace, name, oper, methodname) {
    // hidden method for calling just a method and checking that is exists.
    // (called from oper)
    var method = this[methodname];
    if (! method) {
        ;;; kukit.E = 'Could not trigger event name "' + name;
        ;;; kukit.E += '" on namespace "' + namespace;
        ;;; kukit.E += '", because the method "' + methodname + '" does not exist.';
        throw kukit.E;
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
        ;;; kukit.logDebug('instantiating event id=' + id + ', classname=' + classname + ', namespace=' + namespace);
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
        ;;; kukit.E = 'Conflicting class for event id "' + id + '", "';
        ;;; kukit.E += binderinfo.getBinderInstance().__binder_classname__ + '" != "' + classname + '"';
        throw kukit.E;
    }
    return binderinfo;
};

kukit.er.BinderInfoRegistry.prototype.getBinderInfoById = function (id) {
    // Get an event.
    var binderinfo = this.info[id];
    if (typeof(binderinfo) == 'undefined') {
        ;;; kukit.E = 'Event with id "' + id + '" not found.';
        throw kukit.E;
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
        ;;; kukit.E = 'Singleton event with namespace "' + namespace;
        ;;; kukit.E += '" and (event) name "' + name + '" not found.';
        throw kukit.E;
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
    //
    // first see if it can go to already bound ones
    this.bound.checkOperBindable(oper);
    // then register it properly to the binding events
    this.binding.bindOper(oper);
};

kukit.er.BinderInfo.prototype.processBindingEvents = function () {
    // We came to the end of the binding phase. Now we process all our binding
    // events, This will do the actual binding on the browser side.
    this.binding.processBindingEvents(this.binderinstance);
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
    this.infopername = {};
    this.infopernode = {};
};

// XXX XXX XXX we can do this without full cloning, more efficiently.
kukit.er.OperRegistry.prototype.propagateTo = function (newreg) {
    for (var key in this.infopername) {
        var rules_per_name = this.infopername[key];
        for (var name in rules_per_name) {
            var oper = rules_per_name[name];
            newreg.bindOper(oper);
        }
    }
};

kukit.er.OperRegistry.prototype.checkOperBindable = function (oper, name, nodehash) {
    // Check if the binding with this oper could be done.
    // Throw exception otherwise.
    //
    // Remark. We need  different check and bind method, because we need to bind to the currently
    // processed nodes, but we need to check duplication in all the previously bound nodes.
    var info = this.infopername;
    // name and nodehash are for speedup.
    if (typeof(nodehash) == 'undefined') {
        name = oper.eventrule.kss_selector.name;
        nodehash = kukit.rd.hashnode(oper.node);
    }
    var rules_per_name = info[name];
    if (typeof(rules_per_name) == 'undefined') {
        // Create an empty list.
        rules_per_name = info[name] = {};
    } else if (typeof(rules_per_name[nodehash]) != 'undefined') {
        ;;; kukit.E = 'Mismatch in bind registry, ' + name + ' already bound to node in this instance.'; 
        throw kukit.E;
    }
    return rules_per_name;
};
    
kukit.er.OperRegistry.prototype.bindOper = function (oper) {
    // Marks binding between binderinstance, eventname, node.
    var name = oper.eventrule.kss_selector.name;
    var nodehash = kukit.rd.hashnode(oper.node);
    var rules_per_name = this.checkOperBindable(oper, name, nodehash);
    rules_per_name[nodehash] = oper;
    // also store per node info
    var rules_per_node = this.infopernode[nodehash];
    if (typeof(rules_per_node) == 'undefined') {
        // Create an empty list.
        rules_per_node = this.infopernode[nodehash] = {};
    }
    rules_per_node[name] = oper;
};

// XXX This will need refactoring.
/// We would only want to lookup from our registry and not the other way around.
kukit.er.OperRegistry.prototype.processBindingEvents = function (binderinstance) {
    var eventRegistry = kukit.eventsGlobalRegistry;
    for (var i=0; i < eventRegistry.eventsets.length; i++) {
        var eventset = eventRegistry.eventsets[i];
        // Only process binding events (and ignore non-binding ones)
        if (eventset.bindmethodname) {
            if (binderinstance.__event_namespace__ == eventset.namespace) {
                // Process the binding event set. This will call the actual bindmethods
                // according to the specified iterator.
                var iterator = kukit.er.getBindIterator(eventset.itername);
                iterator.call(this, eventset, binderinstance);
            }
        }
    }
};

// XXX The following methods will probably disappear as iterators replace their functionality.

kukit.er.OperRegistry.prototype.getBoundOperForNode = function (name, node) {
    // Get the oper that is bound to a given eventname to a node in this binderinstance
    // returns null, if there is no such oper.
    var rules_per_name = this.infopername[name];
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
    var rules_per_name = this.infopername[name];
    if (typeof(rules_per_name) != 'undefined') {
        // take the values as a list
        for (var nodehash in rules_per_name) {
            opers.push(rules_per_name[nodehash]);
        }
    }
    // Return it
    return opers;
};

// Iterators
// The getBindIterator returns a function that gets executed on
// the oper registry.
//
// Iterators receive the eventset as a parameter
// plus a binderinstance and a method. They need to iterate by calling this
// as method.call(binderinstance, ...); where ... can be any parameters this
// given iteration specifies.
//

kukit.er.getBindIterator = function(itername) {
    return kukit.er.OperRegistry.prototype['iter_' + itername];
};

kukit.er.OperRegistry.prototype.call_bind_method = function (eventset, binderinstance, p1, p2, p3, p4, p5, p6) {
    var method = binderinstance[eventset.bindmethodname];
    // Protect the binding for better logging
    ;;; try {
        method.call(binderinstance, p1, p2, p3, p4, p5, p6);
    ;;; } catch(e) {
    ;;;     throw new kukit.err.rd.EventBindError('Error during binding, reason: [' + e + ']',  eventset.names, eventset.namespace);
    ;;; }
};

// This calls the bind method by each bound oper one by one. Eventname and func_to_bind are passed too.
// this is the legacy ("each_legacy") way
kukit.er.OperRegistry.prototype.iter_each_legacy = function (eventset, binderinstance) {
    for (var i=0; i<eventset.names.length; i++) {
        var rules_per_name = this.infopername[eventset.names[i]];
        if (typeof(rules_per_name) != 'undefined') {
            for (var nodehash in rules_per_name) {
                var oper = rules_per_name[nodehash];
                var eventname = oper.getEventName();
                var func_to_bind = oper.makeExecuteActionsHook();
                this.call_bind_method(eventset, binderinstance, eventname, func_to_bind, oper);
            }
        }
    }
};


// This calls the bind method by each bound oper one by one. Eventname and func_to_bind are passed too.
// this is the preferred ("each") way. Parameters are different from each_legacy.
kukit.er.OperRegistry.prototype.iter_each = function (eventset, binderinstance) {
    for (var i=0; i<eventset.names.length; i++) {
        var rules_per_name = this.infopername[eventset.names[i]];
        if (typeof(rules_per_name) != 'undefined') {
            for (var nodehash in rules_per_name) {
                var oper = rules_per_name[nodehash];
                this.call_bind_method(eventset, binderinstance, oper);
            }
        }
    }
};

// This calls the bind method by the list of bound opers
kukit.er.OperRegistry.prototype.iter_opers = function (eventset, binderinstance) {
    var opers = [];
    for (var i=0; i<eventset.names.length; i++) {
        var rules_per_name = this.infopername[eventset.names[i]];
        if (typeof(rules_per_name) != 'undefined') {
            for (var nodehash in rules_per_name) {
                opers.push(rules_per_name[nodehash]);
            }
        }
    }
    this.call_bind_method(eventset, binderinstance, opers);
};

// This calls the bind method by a mapping eventname:oper per each bound node individually
kukit.er.OperRegistry.prototype.iter_node = function (eventset, binderinstance) {
    for (var nodehash in this.infopernode) {
        var rules_per_node = this.infopernode[nodehash];
        // filter only the events we are interested in
        var filtered_rules = {};
        var foundoper = false;
        for (var i=0; i<eventset.names.length; i++) {
            var name = eventset.names[i];
            var oper = rules_per_node[name];
            if (typeof(oper) != 'undefined') {
                filtered_rules[name] = oper;
                foundoper = oper;
            }
        }
        // call it
        // All opers have the same node, the last one is yet in foundoper, so
        // we use it as a second parameter to the call.
        // The method may or may not want to use this.
        if (foundoper) {
            this.call_bind_method(eventset, binderinstance, filtered_rules, foundoper.node);
        }
    }
};

// This calls the bind method once per instance, by a list of
// items, where item.node is the node and item.opers_by_eventname nodehash:item
// in item there is item.node and item.opers_by_eventname
kukit.er.OperRegistry.prototype.iter_allnodes = function (eventset, binderinstance) {
    var items = [];
    var has_result = false;
    for (var nodehash in this.infopernode) {
        var rules_per_node = this.infopernode[nodehash];
        // filter only the events we are interested in
        var filtered_rules = {};
        var foundoper = false;
        for (var i=0; i<eventset.names.length; i++) {
            var name = eventset.names[i];
            var oper = rules_per_node[name];
            if (typeof(oper) != 'undefined') {
                filtered_rules[name] = oper;
                foundoper = oper;
            }
        }
        if (foundoper) {
            items.push({node: foundoper.node, opers_by_eventname: filtered_rules});
            has_result = true;
        }
    }
    // call the binder method
    if (has_result) {
        this.call_bind_method(eventset, binderinstance, items);
    }
};

