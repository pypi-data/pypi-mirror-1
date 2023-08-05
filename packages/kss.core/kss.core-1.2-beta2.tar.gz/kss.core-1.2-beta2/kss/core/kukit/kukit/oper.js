/*
* Copyright (c) 2006-2007
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
*  parms: a dictionary that holds the parameters to the function.
*      All parameters are named ones.
*
*  eventrule: The eventrule associated by the trigger.
*
*  binderinstance: The event binder instance that holds the event state
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
    this.eventrule = null;
    this.binderinstance = null;
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
        if (restricted && (key == 'node' || key == 'parms' || key == 'eventrule' 
                || key == 'binderinstance' || key == 'orignode')) {
            throw 'Illegal update on oper object, protected attribute "' + key + '"';
        }
        var value = dict[key];
        if (typeof(value) != 'function') {
            this[key] = value;
        }
    }
};

kukit.op.Oper.prototype.logDebug = function() {
    var result = [];
    for (var key in this){
        if (key == 'parms') {
            var res2 = [];
            for (var k2 in this.parms){
                res2.push(k2 + '="' + this.parms[k2] + '"');
            }
            result.push('parms={' + res2.join(',') + '}');
        } else if (typeof(kukit.op.Oper.prototype[key]) == 'undefined') {
            result.push(key + '=' + this[key]);
        }
    }
    kukit.logDebug('Oper contents: ' + result.join(', '));
};

kukit.op.Oper.prototype.executeClientAction = function(name) {
    // Check kss action parameters
    var nodes = null;
    // XXX TODO this should be refactored with parms constraint checking
    for (key in this.aparms) {
        switch (key) {
            case 'kssSelector': {
                // The value already contains the results
                nodes = this.aparms[key];
            } break;
            default: {
                throw 'No kss parameter "' + key + '" allowed in action-client. (Normal parameters cannot start with kss.)';
            } break;
        }
    }
    //
    // XXX TODO refactor this with commands execution (or the other way)
    var nodetext = function(node) {
        if (node) {
            return node.tagName.toLowerCase();
        } else {
            return 'DOCUMENT';
        }
    };
    var executeActions = kukit.actionsGlobalRegistry.get(name);
    if (nodes != null) { 
        kukit.logDebug('action Selector type selected nodes:' + nodes.length);
        if (!nodes || nodes.length == 0) {
            kukit.logWarning('action Selector found no nodes');
        }
        for (var i=0; i < nodes.length; i++) {
            this.node = nodes[i];
            //XXX error handling for wrong command name
            //kukit.logDebug('action Name: ' + this.name);
            kukit.logDebug('action Name: ' + name + ' executing on target (' + (i+1) +  '/' + nodes.length +  '): ' + nodetext(this.node));
            executeActions(this);
        }
    } else {
        // single node
        kukit.logDebug('action Name: ' + name + ' executing on single target ' + nodetext(this.node));
        executeActions(this);
    }
};

kukit.op.Oper.prototype.executeDefaultAction = function(name, optional) {
    // Check kss action parameters
    for (key in this.aparms) {
        throw 'No kss parameter "' + key + '" allowed in action-default. (Normal parameters cannot start with kss.)';
    }
    //
    var namespace = this.binderinstance.__event_namespace__;
    var methodname = kukit.eventsGlobalRegistry.get(namespace, name).defaultactionmethodname;
    var success = false;
    if (! methodname) {
        if (! optional) {
            throw 'Could not trigger event name "' + name + '" on namespace "' + namespace + '", because this event has no default method.';
        }
    } else {
        this.binderinstance._EventBinder_callmethod(namespace, name, this, methodname);
        success = true;
    }
    return success;
};

kukit.op.Oper.prototype.executeServerAction = function(name) {
    for (key in this.aparms) {
        switch (key) {
            case 'kssUrl': {
                // Value will be evaluated.
            } break;
            case 'kssSubmitForm': {
                // Value will be evaluated.
            } break;
            default: {
                throw 'No kss parameter "' + key + '" allowed in action-server. (Normal parameters cannot start with kss.)';
            } break;
        }
    }

    // oper will be accessible to some commands that execute in return
    var sa = new kukit.sa.ServerAction(name, this);
};

/* Helpers the serve binding */

kukit.op.Oper.prototype.getEventName = function () {
    // Gets event name
    return this.eventrule.kss_selector.name;
};

kukit.op.Oper.prototype.getEventNamespace = function () {
    // Gets event name
    return this.eventrule.kss_selector.namespace;
};

kukit.op.Oper.prototype.makeExecuteActionsHook = function () {
    // Factory that creates the function that executes the actions.
    // The function may take a dict that is updated on the oper 
    var eventname = this.getEventName();
    var self = this;
    var func_to_bind = function(dict) {
        var newoper = self.clone(dict, true);
        newoper.binderinstance._EventBinder_triggerevent(eventname, newoper);
    };
    return func_to_bind;
};

/* Utility for parameter checking */

kukit.op.Oper.prototype.completeParms = function(mandatory, defaults, errname, allow_excess) {
    // Checks if mandatory params are supplied and there are no excess params
    // also fill up default values
    // Parms are cloned and returned.
    // Call example: oper.completeParms(['mand1', 'mand2'], {'key1': 'defval'}, 'event X');
    if (typeof(allow_excess) == 'undefined') {
        allow_excess = false;
    }
    var newparms = {};
    for (var i=0; i<mandatory.length; i++) {
        var next = mandatory[i];
        if (typeof(this.parms[next]) == 'undefined') {
            throw 'Missing mandatory parameter "' + next + '" in ' + errname;
        }
        newparms[next] = this.parms[next];
    }
    for (var key in defaults){
        var val = this.parms[key];
        if (typeof(val) == 'undefined') {
            newparms[key] = defaults[key];
        } else {
            newparms[key] = val;
        }
    }
    for (var key in this.parms){
        if (typeof(newparms[key]) == 'undefined') {
            if (allow_excess) {
                newparms[key] = this.parms[key];
            } else {
                throw 'Excess parameter "' + key + '" in ' + errname;
            }
        }
    }
    this.parms = newparms;
};

kukit.op.Oper.prototype.evalBool = function(key, errname) {
    var value = this.parms[key];
    this.parms[key] = kukit.ut.evalBool(value, 'for key "' + key + '" in ' + errname);
};

kukit.op.Oper.prototype.evalInt = function(key, errname) {
    var value = this.parms[key];
    this.parms[key] = kukit.ut.evalInt(value, 'for key "' + key + '" in ' + errname);
};

kukit.op.Oper.prototype.evalList = function(key, errname) {
    var value = this.parms[key];
    this.parms[key] = kukit.ut.evalList(value, 'for key "' + key + '" in ' + errname);
};

