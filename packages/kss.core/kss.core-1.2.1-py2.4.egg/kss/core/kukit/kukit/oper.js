/*
* Copyright (c) 2006-2007
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



kukit.op = {};

/*
* class Oper
*
*  This is a single parameter that contains a collection
*  of operation objects to pass by, at various
*  operations.
*
*  Node and parms are the one to be accessed really, but the rest
*  is also accessible to read for special event implementations.
*
*
*  The members are:
*
*  node: the node in focus, to which the event triggered
*
*  parms: a dictionary that holds the parms to the function.
*      All parms are named ones.
*
*  eventRule: The eventRule associated by the trigger.
*
*  binderInstance: The event binder instance that holds the event state
*       and on which all events are executed.
*
*  orignode: in case when a command has returned from a server action, 
*      this holds the original node that triggered the event first.
*
*  browserevent: the original browser event.
*/
kukit.op.Oper = function (dict) {
    this.node = null;
    this.parms = {};
    this.eventRule = null;
    this.binderInstance = null;
    this.orignode = null;
    this.action = null;
    this.browserevent = null;
    // update from the dict
    this.unrestrictedUpdate(dict);
};

kukit.op.Oper.prototype.clone = function(dict, restricted) {
    var newoper = new kukit.op.Oper(this);
    newoper.unrestrictedUpdate(dict, restricted);
    return newoper;
};

kukit.op.Oper.prototype.update = function(dict) {
    // restricted attrs must not be changed on existing oper.
    this.unrestrictedUpdate(dict, true);
};

kukit.op.Oper.prototype.unrestrictedUpdate = function(dict, restricted) {
    if (typeof(dict) == 'undefined') {
        return;
    }
    for (var key in dict) {
;;;     if (typeof(checkKey) == 'undefined') {
;;;         var checkKey = function(key) {
;;;             var isNode = key == 'node';
;;;             var isParameters = key == 'parms';
;;;             var isEventRule = key == 'eventRule';
;;;             var isBinder = key == 'binderInstance';
;;;             var isOrig = key == 'orignode';
;;;         return isNode || isParameters || isEventRule || isBinder || isOrig;
;;;         };
;;;     }
;;;     if (restricted && checkKey(key)) {
;;;         kukit.E = 'Illegal update on oper object, protected attribute [';
;;;         kukit.E += key + '].';
;;;         throw kukit.E;
;;;     }
        var value = dict[key];
        if (typeof(value) != 'function') {
            this[key] = value;
        }
    }
};

kukit.op.Oper.prototype.logDebug = function() {
;;;     var result = [];
;;;     for (var key in this){
;;;         if (key == 'parms') {
;;;             var res2 = [];
;;;             for (var k2 in this.parms){
;;;                 res2.push(k2 + '="' + this.parms[k2] + '"');
;;;             }
;;;             result.push('parms={' + res2.join(',') + '}');
;;;         } else if (typeof(kukit.op.Oper.prototype[key]) == 'undefined') {
;;;             result.push(key + '=' + this[key]);
;;;         }
;;;     }
;;;     kukit.logDebug('Oper values: ' + result.join(', '));
};

kukit.op.Oper.prototype.executeClientAction = function(name) {
    // Check kss action parms
    var nodes = null;
    // XXX TODO this should be refactored with parms constraint checking
    for (key in this.kssParms) {
        switch (key) {
            case 'kssSelector': {
                // The value already contains the results
                nodes = this.kssParms[key];
            } break;
            default: {
;;;            kukit.E = 'Wrong parameter : [' + key + '] starts with ';
;;;            kukit.E += '"kss"; normal parms (that do not start with';
;;;            kukit.E += ' "kss") only are allowed in action-client keys.';
               throw kukit.E;
            } break;
        }
    }
    // XXX TODO refactor this with commands execution (or the other way)
;;; var nodetext = function(node) {
;;;     if (node) {
;;;         return node.tagName.toLowerCase();
;;;     } else {
;;;         return 'DOCUMENT';
;;;     }
;;; };
    var executeActions = kukit.actionsGlobalRegistry.get(name);
    if (nodes != null) { 
;;;     var msg = nodes.length + ' nodes found for action [' + name + '].';
;;;     kukit.logDebug(msg);
;;;     if (!nodes || nodes.length == 0) {
;;;         kukit.logWarning('Action selector found no nodes.');
;;;     }
        for (var i=0; i < nodes.length; i++) {
            this.node = nodes[i];
            //XXX error handling for wrong command name
;;;         var msg = '[' + name + '] action executes on target (' + (i+1);
;;;         msg += '/' + nodes.length +  ') ';
;;;         msg += '[' + nodetext(this.node) + '].';
;;;         kukit.logDebug(msg);
            executeActions(this);
        }
    } else {
        // single node
;;;     var msg = '[' + name + '] action executes on single node ';
;;;     msg += '[' + nodetext(this.node) + '].';
;;;     kukit.logDebug(msg);
        executeActions(this);
    }
};

kukit.op.Oper.prototype.executeDefaultAction = function(name, optional) {
    // Check kss action parms
;;; for (key in this.kssParms) {
;;;     kukit.E = 'Wrong parameter : [' + key + '] starts with "kss";';
;;;     kukit.E += ' normal parms (that do not start with kss)';
;;;     kukit.E += ' only are allowed in action-default keys.';
;;;     throw kukit.E;
;;; }
    //
    var namespace = this.binderInstance.__eventNamespace__;
    var kssevent = kukit.eventsGlobalRegistry.get(namespace, name);
    var methodName = kssevent.defaultActionMethodName;
    var success = false;
    if (! methodName) {
;;;     if (! optional) {
;;;         kukit.E = 'Could not trigger event [' + name;
;;;         kukit.E += '] from namespace [' + namespace + '], because this';
;;;         kukit.E += ' event has no default method registered.';
;;;         throw kukit.E;
;;;     }
    } else {
        // Put defaultParameters to parms!
        // This makes sure, that for implicit events 
        // you do need not to specify pass(xxx)
        // for making the parms arrive to the action.
        this.parms = this.defaultParameters;
        this.binderInstance._EventBinder_callMethod(
            namespace, name, this, methodName);
        success = true;
    }
    return success;
};

kukit.op.Oper.prototype.executeServerAction = function(name) {
;;; for (key in this.kssParms) {
;;;     if (key == 'kssUrl') {
;;;         // Value will be evaluated.
;;;     } else if (key == 'kssSubmitForm') {
;;;         // Value will be evaluated.
;;;     } else {
;;;        kukit.E = 'Wrong parameter : [' + key + '] starts with "kss";';
;;;         kukit.E += ' normal parms (that do not start with kss)';
;;;         kukit.E += ' only are allowed in action-server keys.';
;;;         throw kukit.E;
;;;     }
;;; }
    // oper will be accessible to some commands that execute in return
    var sa = new kukit.sa.ServerAction(name, this);
};

/* Helpers the serve binding */

kukit.op.Oper.prototype.getEventName = function () {
    // Gets event name
    return this.eventRule.kssSelector.name;
};

kukit.op.Oper.prototype.getEventNamespace = function () {
    // Gets event name
    return this.eventRule.kssSelector.namespace;
};

kukit.op.Oper.prototype.hasExecuteActions = function () {
    // Decide if there are any actions (or a default action)
    // to execute. This can speed up execution if in case
    // we have nothing to do, there is no reason to bind
    // the actions hook.
    if (this.eventRule) {  
        // if it has actions, the answer is yes
        if (this.eventRule.actions.hasActions())
            return true
        // if we have a default action, we will return true in any case
        // because we may want to call it.
        // The reason for this check is, that a default action is also
        // valid, even if it received no parms in the eventRule,
        // in which case it is not present as an action.
        var kssevent = kukit.eventsGlobalRegistry.get(
            this.getEventNamespace(), this.getEventName())
        var methodName = kssevent.defaultActionMethodName;
        return (typeof methodName != 'undefined');
    } else
        return false;
};

kukit.op.Oper.prototype.makeExecuteActionsHook = function (filter) {
    // Factory that creates the function that executes the actions.
    // The function may take a dict that is updated on the oper 
    // If filter is specified, it will we called with a function and
    // the event will only be triggered if the filter returned true.
    // THe return value of func_to_bind will show if the event
    // has executed or not.
    //
    // Speedup.
    if (! this.hasExecuteActions()) {
        return function() {};
    }
    var eventName = this.getEventName();
    var self = this;
    var func_to_bind = function(dict) {
        // (XXX XXX TODO it should happen here, that we change to a different
        // oper class. This is for the future when we separate the BindOper
        // from the ActionOper.)

        var newoper = self.clone(dict, true);
        // call the filter and if it says skip it, we are done
        if (filter && ! filter(newoper)) return false;
        // execute the event's actions
        newoper.binderInstance._EventBinder_triggerEvent(eventName, newoper);
        // show that the event's actions have been executed
        return true;
    };
    return func_to_bind;
};

/* Utility for parameter checking */

kukit.op.Oper.prototype.evaluateParameters =
    function(mandatory, defaults, errname, allow_excess) {
    // Checks if mandatory params are supplied and there are no excess params
    // also fill up default values
    // Parms are cloned and returned.
    // Example: 
    // oper.evaluateParameters(['mand1', 'mand2'], {'key1': 'defval'},
    //      'event X');
;;; if (typeof(allow_excess) == 'undefined') {
;;;     allow_excess = false;
;;;}
    var newParameters = {};
    for (var i=0; i<mandatory.length; i++) {
        var next = mandatory[i];
;;;     if (typeof(this.parms[next]) == 'undefined') {
;;;         kukit.E = 'Missing mandatory parameter [' + next;
;;;         kukit.E += '] in [' + errname + '].';
;;;         throw kukit.E;
;;;     }
        newParameters[next] = this.parms[next];
    }
    for (var key in defaults){
        var val = this.parms[key];
        if (typeof(val) == 'undefined') {
            newParameters[key] = defaults[key];
        } else {
            newParameters[key] = val;
        }
    }
    for (var key in this.parms){
        if (typeof(newParameters[key]) == 'undefined') {
;;;         if (allow_excess) {
                newParameters[key] = this.parms[key];
;;;         } else {
;;;             throw 'Excess parameter [' + key + '] in [' + errname + '].';
;;;         }
        }
    }
    this.parms = newParameters;
};

kukit.op.Oper.prototype.completeParms =
    function(mandatory, defaults, errname, allow_excess) {
;;; var msg = 'Deprecated [Oper.completeParms],';
;;; msg += 'use [Oper.evaluateParameters] instead !';
;;; kukit.logWarning(msg);
    this.evaluateParameters(mandatory, defaults, errname, allow_excess);
};

kukit.op.Oper.prototype.evalBool = function(key, errname) {
    var value = this.parms[key];
;;; kukit.E = 'for key [' + key + '] in [' + errname + '].';
    this.parms[key] = kukit.ut.evalBool(value, kukit.E);
};

kukit.op.Oper.prototype.evalInt = function(key, errname) {
    var value = this.parms[key];
;;; kukit.E = 'for key [' + key + '] in [';
;;; kukit.E += errname || this.componentName + '].';
    this.parms[key] = kukit.ut.evalInt(value, kukit.E);
};

kukit.op.Oper.prototype.evalList = function(key, errname) {
    var value = this.parms[key];
;;; kukit.E = 'for key [' + key + '] in [';
;;; kukit.E += errname || this.componentName + '].';
    this.parms[key] = kukit.ut.evalList(value, kukit.E);
};

;;; kukit.op.Oper.prototype.debugInformation = function() {
;;; if (this.eventRule) {
;;;     var eventRule = this.eventRule;
;;;     var node = this.node;
;;;     var nodeName = '<DOCUMENT>';
;;;     if (node != null) {
;;;         nodeName = node.nodeName;
;;;     }
;;;     var message = ', event [' + eventRule.kssSelector.name;
;;;     message += '], rule #' + eventRule.getIndex() + ', node [';
;;;     message += nodeName + '].'; 
;;;     return message;
;;; }
;;; return '';
;;; };
