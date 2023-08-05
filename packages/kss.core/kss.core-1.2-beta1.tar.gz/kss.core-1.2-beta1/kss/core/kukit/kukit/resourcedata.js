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

/* Supplemental data that the parser builds up */

kukit.rd = {};

kukit.rd.makeId = function(namespace, name) {
    if (namespace == null) {
        namespace = '';
    }
    return '@' + namespace + '@' + name;
};

kukit.rd.makeMergeId = function(id, namespace, name) {
    if (namespace == null) {
        namespace = '';
    }
    return id + '@' + namespace + '@' + name;
};

/*
*  class KssSelector
*/
kukit.rd.KssSelector = function(isEvent, css, name, namespace, id) {
    this.isEventSelector = isEvent;
    this.isMethodSelector = ! isEvent;
    if (! name) {
        throw 'KssSelector must have name';
    }
    if (name.indexOf('@') != -1)
        throw new kukit.err.rd.KssSelectorError('Kss selector name must not contain @: "' + name + '"');
    if (id && id.indexOf('@') != -1)
        throw new kukit.err.rd.KssSelectorError('Kss selector id must not contain @: "' + id + '"');
    if (namespace && namespace.indexOf('@') != -1)
        throw new kukit.err.rd.KssSelectorError('Kss selector namespace must not contain @: "' + namespace + '"');
    if (! isEvent) {
        // method rule
        if (css != 'document' && css != 'behaviour') {
            throw new kukit.err.rd.KssSelectorError('KssSpecialSelector "' + name + '" must have one of the allowed names');
        }
    }
    this.css = css;
    this.name = name;
    this.namespace = namespace;
    this.classname = null;
    this.id = id;
};

kukit.rd.KssSelector.prototype.setIdAndClass = function() {
    // Sets up id and class on the selector, based on registration info
    this.classname = kukit.eventsGlobalRegistry.get(this.namespace, this.name).classname;
    if (this.id == null) {
        // singleton for class
        this.id = kukit.rd.makeId(this.namespace, this.classname);
    }
    // Also set the merge id. The rules with the same merge
    // id should be merged on the same node.
    this.mergeid = kukit.rd.makeMergeId(this.id, this.namespace, this.name);
};

/*
* Kss parameter values. There are two kinds: text and method.
*
* They are evaluated in two phases: check is invoked at parsing,
* allowing the early detection of errors. Evaluate is called
* when the action is to be called. This allows a kss method
* to add any parameter to the action.
*/

/*
*  class KssTextValue
*/
kukit.rd.KssTextValue = function(txt) {
    // A text parameter in the format 
    //      key: value;
    this.txt = txt;
};
kukit.rd.KssTextValue.prototype.isMethod = false;
kukit.rd.KssTextValue.prototype.check = function(registry) {
    // use the IdentityPP provider.
    this.pprovider = new (registry.get(''))();
};
kukit.rd.KssTextValue.prototype.evaluate = function(parms, key, node, defaultparms) {
    // For normal string parameters, this would return the string itself.
    // In other execution contexts (like kssSelector, for example) this can
    // do something else.
    parms[key] = this.pprovider.eval([this.txt], node, defaultparms);
};

/*
*  class KssTextValue
*/
kukit.rd.KssMethodValue = function(methodname, args) {
    // A method parameter in the format 
    //      key: methodname(v1, v2, ... vn);
    this.methodname = methodname;
    this.args = args;
};
kukit.rd.KssMethodValue.prototype.isMethod = true;
kukit.rd.KssMethodValue.prototype.check = function(registry) {
    // Check syntax
    var f = registry.get(this.methodname);
    this.pprovider = new f();
    this.pprovider.check(this.args);
};

kukit.rd.KssMethodValue.prototype.evaluate = function(parms, key, node, defaultparms) {
    // Evaluate into parms.
    parms[key] = this.pprovider.eval(this.args, node, defaultparms);
};

/*
*  class KssPseudoValue
*/
kukit.rd.KssPseudoValue = function(methodname, args) {
    // A method parameter in the format 
    //      methodname(v1)
    this.methodname = methodname;
    this.args = args;
};
kukit.rd.KssPseudoValue.prototype.isMethod = true;
kukit.rd.KssPseudoValue.prototype.check = function() {
};

kukit.rd.EventRuleNr = 0;            // just a counter

/*
*  class EventRule
*/
kukit.rd.EventRule = function(kss_selector, parms, actions) {
    if (typeof(parms) == 'undefined') {
        // called for merging clone
        this.kss_selector = kss_selector;
    } else {
        this.nr = kukit.rd.EventRuleNr;
        this.mergednr = null;
        kukit.rd.EventRuleNr = this.nr + 1;
        var namestr;
        if (kss_selector.namespace) {
            namestr = kss_selector.namespace + '-' + kss_selector.name;
        } else {
            namestr = kss_selector.name;
        }
        kukit.logDebug("EventRule #" + this.getNr() + ": " + kss_selector.css + ' EVENT=' + namestr);
        this.kss_selector = kss_selector;
        this.parms = parms;
        this.actions = actions;
    }
};

kukit.rd.EventRule.prototype.getNr = function() {
    if (this.mergednr) {
        return this.mergednr;
    } else {
        return this.nr;
    }
};

kukit.rd.EventRule.prototype.mergeForSelectedNodes = function(ruletable, phase, in_nodes) {
    // Select all nodes within the in_nodes for phase==2. (or undefined on initial node, phase==1)
    // Merge itself to the selected nodes.
    if (this.kss_selector.isEventSelector) {
        var nodes = kukit.dom.cssQuery(this.kss_selector.css, in_nodes);
        var counter = 0;
        for (var y=0; y < nodes.length; y++)
        {
            var node = nodes[y];
            // XXX never rebind to any node again!
            // this compensates that cssQuery is returning results out of the subtree
            if (typeof(node._kukitmark) == 'undefined') {
                ruletable.add(node, this);
                counter += 1;
                }
        }
        if (counter > 0) {
            kukit.logDebug('EventRule #' + this.getNr() + ' mergeid ' + this.kss_selector.mergeid + ' selected ' + counter + ' nodes');
        }
    } else if (typeof(in_nodes) == 'undefined') {
        // Method selector. They only need to be handled on the initial
        // pageload, when the in_nodes parameter is ommitted.
        kukit.engine.documentRules.add(this);
    }
};

kukit.rd.EventRule.prototype.getBinderInfo = function() {
    // Gets the event instance for the rule.
    return kukit.engine.binderInfoRegistry.getOrCreateBinderInfo(this.kss_selector.id, this.kss_selector.classname, 
        this.kss_selector.namespace);
};

/*
* bind(node) : calls binder hook on event instance.
*  These hooks are tried in order, if succeeds it must return true:
*
* __bind__(name, parms, func_to_bind, node, eventrule)
* __bind_<name>__(parms, func_to_bind, node, eventrule)
*
* If none succeeds is an error.
*
*/

kukit.rd.EventRule.prototype.bind = function(node) {
    // Creation of the binding oper
    var oper = new kukit.op.Oper();
    var binderinfo = this.getBinderInfo();
    oper.node = node;
    oper.eventrule = this;
    oper.binderinstance = binderinfo.binderinstance;
    oper.parms = this.parms;
    // mark on the instance as bound
    binderinfo.bindOper(oper); 
};


/*
* Merging event rules
*/

kukit.rd.EventRule.prototype.isMerged = function() {
    return (this.mergednr != null);
};

kukit.rd.EventRule.prototype.cloneForMerge = function() {
    // Do not touch ourselves, make a new copy for the merge.
    var merged = new kukit.rd.EventRule(this.kss_selector);
    merged.actions = new kukit.rd.ActionSet();
    merged.parms = {};
    merged.mergednr = 'X';
    merged.merge(this);
    merged.mergednr = this.getNr();
    return merged;
};

kukit.rd.EventRule.prototype.merge = function(other) {
    if (! this.isMerged()) {
        throw "Cannot merge into a genuine event rule";
    }
    if (this.kss_selector.isEventSelector) {
        if (this.kss_selector.id != other.kss_selector.id) {
            throw "Differing kss selector ids in event rule merge";
        }
        if (this.kss_selector.classname != other.kss_selector.classname) {
            throw "Differing kss selector classes in event rule merge";
        }
    }
    if (this.kss_selector.name != other.kss_selector.name) {
        throw "Differing kss selector names in event rule merge";
    }
    this.mergednr = this.mergednr + ',' + other.getNr();
    for (var key in other.parms) {
        this.parms[key] = other.parms[key];
    }
    this.actions.merge(other.actions);
    if (this.mergednr.substr(0, 1) != 'X')
        // ignore initial clone-merge
        kukit.logDebug('Merged rule ' + this.mergednr + ' mergeid ' + this.kss_selector.mergeid);
};

kukit.rd.EventRule.prototype.mergeIntoDict = function(dict, key, eventrule) {
    // Merge into the given dictionary by given key.
    // If possible, store the genuine rule first - if not,
    // clone it and do a merge. Never destroy the genuine
    // rules, clone first. This is for efficiency.
    var mergedrule = dict[key];
    if (typeof(mergedrule) == 'undefined') {
        // there was no rule
        dict[key] = eventrule;
    } else {
        // we have to merge the rule
        if (! mergedrule.isMerged()) {
            // Make sure genuine instances are replaced
            mergedrule = mergedrule.cloneForMerge();
            dict[key] = mergedrule;
        }
        mergedrule.merge(eventrule);
    }
};

/*
*  class ActionSet
*/
kukit.rd.ActionSet = function() {
    this.content = {};
};

kukit.rd.ActionSet.prototype.merge = function(other) {
    for (var key in other.content) {
        var action = this.content[key];
        var action2 = other.content[key];
        if (typeof(action) == 'undefined') {
            if (action2.type != 'X') {
                // new action
                action = new kukit.rd.Action();
                this.content[key] = action;
            } else {
                throw new kukit.err.rd.RuleMergeError('Cannot action-delete unexisting action, "' + key + '"');
            }
        }
        if (action2.type != 'X') {
            // merge the action
            action.merge(action2);
        } else {
            // Delete the action
            this.deleteAction(key);
        }
    }
};

kukit.rd.ActionSet.prototype.execute = function(oper) {
    for (var key in this.content) {
        var action = this.content[key];
        // do not execute error actions!
        if (action.type != 'E') {
            action.execute(oper);
        }
    }
    // Execute the default action in case of there is one but there were no
    // parameters so it was actually not entered as an action object
    // otherwise, it would have been executed from action.execute already
    if (typeof(this.content['default']) == 'undefined') {
        // this is conditional: if there is no default method, it's skipped.
        var name = oper.eventrule.kss_selector.name;
        // Execution with no parameters. (XXX ?)
        oper = oper.clone({'parms': {}});
        oper.executeDefaultAction(name, true);
    }
};

kukit.rd.ActionSet.prototype.getOrCreateAction = function(name) {
    var action = this.content[name];
    if (typeof(action) == 'undefined') {
        action = new kukit.rd.Action();
        action.setName(name);
        this.content[name] = action;
    }
    return action;
};

kukit.rd.ActionSet.prototype.getActionOrNull = function(name) {
    var action = this.content[name];
    if (typeof(action) == 'undefined') {
        action = null;
    }
    return action;
};

kukit.rd.ActionSet.prototype.deleteAction = function(name) {
    var action = this.content[name];
    if (typeof(action) == 'undefined') {
        throw('Action "' + name + '" does not exist and cannot be deleted.');
    }
    delete this.content[name];

};

kukit.rd.ActionSet.prototype.getDefaultAction = function() {
    return this.getActionOrNull('default');
};

kukit.rd.ActionSet.prototype.getErrorActionFor = function(action) {
    // Get the error action of a given action: or null,
    // if the action does not define an error handler.
    return this.getActionOrNull(action.error);
};

/*
*  class Action
*/
kukit.rd.Action = function() {
    this.name = null;
    this.error = null;
    this.parms = {};
    this.type = null;
};

kukit.rd.Action.prototype.setName = function(name) {
    if (this.name != null && this.name != name) {
        throw new kukit.err.rd.RuleMergeError('Error overriding action name "' + this.name + '" to "' + name + '" (Unmatching action names at merge?)');
    }
    this.name = name;
    if (name == 'default') {
        if (this.type != null && this.type != 'D') {
            throw new kukit.err.rd.RuleMergeError('Error setting action to default on action "' + this.name + '", current type "' + this.type + '"');
        }
        this.setType('D');
    }
};

kukit.rd.Action.prototype.setType = function(type) {
    // Possible types:
    //  S = server
    //  C = client
    //  E = error / client
    //  D = default (unsettable)
    //  X = cancel action
    if ((type != 'S' && type != 'C' && type != 'E' && type != 'X') ||
            (this.type != null && this.type != type)) {
        throw new kukit.err.rd.RuleMergeError('Error setting action type on action "' + this.name + '" from "' + this.type + '" to "' + type + '" (Attempt to merge client, server or error actions?)');
    }
    if (this.error != null && this.type != 'S') {
        throw new kukit.err.rd.RuleMergeError('Error setting action error handler on action "' + this.name + '", this is only allowed on server actions.');
    }
    this.type = type;  
};

kukit.rd.Action.prototype.setError = function(error) {
    if (this.type != null && this.type != 'S') {
        throw new kukit.err.rd.RuleMergeError('Error setting action error handler on action "' + this.name + '", this is only allowed on server actions.');
    }
    this.error = error;  
};

kukit.rd.Action.prototype.merge = function(other) {
    // Merge to the instance.
    if (other.name != null) { 
        this.setName(other.name);
    }
    if (other.type != null) { 
        this.setType(other.type);
    }
    if (other.error != null) { 
        this.setError(other.error);
    }
    // These are simply overwritten.
    for (var key in other.parms) {
        this.parms[key] = other.parms[key];
    }
};

kukit.rd.Action.prototype.makeActionOper = function(oper, defaultparms) {
    // Fill the completed action parameters, based on the node
    // if defaultparms is given, its values can be used with the 
    // pass() function.
    // The kssXxx parameters, reserved for the action, are put into
    // aparms.
    // A cloned oper is returned.
    var parms = {};
    var aparms = {};
    if (typeof(defaultparms) == 'undefined') {
        defaultparms = {};
    }
    for (var key in this.parms) {
        var kssvalue = this.parms[key]; 
        if (key.match(/^kss/)) {
            // kssXxx parameters are separated to aparms.
            kssvalue.evaluate(aparms, key, oper.node, defaultparms); 
        } else {
            // evaluate the method parameters into parms
            kssvalue.evaluate(parms, key, oper.node, defaultparms); 
        }
    }
    var aoper = oper.clone({
            'parms': parms,
            'aparms': aparms,
            'action': this
        });
    return aoper;
};

kukit.rd.Action.prototype.execute = function(oper) {
    oper = this.makeActionOper(oper, oper.parms);
    switch (this.type) {
        case 'D': {
            // Default action.
            var name = oper.eventrule.kss_selector.name;
            oper.executeDefaultAction(name);
        } break;
        case 'S': {
            // Server action.
            oper.executeServerAction(this.name);
        } break;
        case 'C': {
            // Client action.
            oper.executeClientAction(this.name);
        } break;
        case 'E': {
            // Error action (= client action)
            oper.executeClientAction(this.name);
        } break;
    }
};


/*
*  class LoadActions
*/
kukit.rd.LoadActions = function() {
    this.items = [];
};

kukit.rd.LoadActions.prototype.empty = function() {
    return (this.size() == 0);
};

kukit.rd.LoadActions.prototype.size = function() {
    return this.items.length;
};

kukit.rd.LoadActions.prototype.push = function(f) {
    if (this.items.length >= 100) {
        throw ('Infinite recursion, stack full');
    }
    this.items.push(f);
};

kukit.rd.LoadActions.prototype.execute = function() {
    var f = this.items.shift();
    if (f) {
        f();
        return true;
    } else {
        return false;
    }
};

kukit.rd.LoadActions.prototype.executeAll = function() {
    var i = 0;
    while(true) {
        var success = this.execute();
        if (! success) {
            break;
        }
        i++;
    }
    return i;
};


/*
*  class RuleTable
*
*   Used for binding rules to nodes, and handling the merges.
*   It is a two level dictionary.
*
*   There are more rules that match a given node and event id. 
*   They will be merged appropriately. The event id is also
*   important. The event class must be the same with merge
*   rules (within the id).
*
*   To summarize the procedure, each eventrule is added with
*   all the nodes that are selected by it. Nothing is executed,
*   only merges are done at this time. Finally, all binds are
*   done in the second path.
*
*   Event with the same merge id are merged. The merge id is
*   a concatenation of the event id and the event name.
* 
*   XXX TODO this has to be refactored, since it's all global now
*
*/

kukit.rd.RuleTable = function(loadScheduler) {
    this.loadScheduler = loadScheduler;
    this.nodes = {};
};

kukit.rd.RuleTable.prototype.add = function(node, eventrule) {
    // look up node
    var nodehash = kukit.rd.hashnode(node);
    var nodeval = this.nodes[nodehash];
    if (typeof(nodeval) == 'undefined') {
        nodeval = {'node': node, 'val': {}};
        this.nodes[nodehash] = nodeval;
    }
    // Merge into the dict
    eventrule.mergeIntoDict(nodeval.val, eventrule.kss_selector.mergeid, eventrule);
};

kukit.rd.RuleTable.prototype.bindall = function(phase) {
    // Bind all nodes
    var counter = 0;
    for (var nodehash in this.nodes) {
        var nodeval = this.nodes[nodehash];
        // XXX Mark the node, disabling rebinding in a second round
        nodeval.node._kukitmark = phase;
        for (var id in nodeval.val) {
            var eventrule = nodeval.val[id];
            eventrule.bind(nodeval.node);            
        }
        counter += 1;
    }
    kukit.logDebug('Binding to ' + counter + ' nodes in grand total');
    // Execute the load actions in a deferred manner
    var loadactions = this.loadScheduler;
    if (! loadactions.empty()) {
        kukit.logDebug('Start executing delayed load actions');
        var nr = loadactions.executeAll();
        kukit.logDebug('Executed ' + nr + ' load actions');
    }
};

kukit.rd.uid = 0;

kukit.rd.hashnode = function(node) {
    // It is, generally, not possible to use a node as a key.
    // However we try to set this right.
    // We generate an uniqueID on the node. This does not work
    // on MSIE but it already has an uniqueID.
    if (node == null) {
        // null represents the document
        return '<<DOCUMENT>>';
    }
    var id = node.uniqueID;
    if (typeof(id) == 'undefined') {
        id = kukit.rd.uid;
        node.uniqueID = id;
        kukit.rd.uid ++;
    }
    return id;
};

/*
*  class MethodTable
*
* stores the method rules.
*
* Unlike the rule table that is specific for each binding,
* this is unique to the page.
*/
kukit.rd.MethodTable = function() {
    this.content = {};
    this.content['document'] = {};
    this.content['behaviour'] = {};
};

kukit.rd.MethodTable.prototype.add = function(eventrule) {
    // Get the entry by the type which is now at css
    var category = eventrule.kss_selector.css;
    var dict = this.content[category];
    if (typeof(dict) == 'undefined') {
        throw 'Unknown method rule category "' + category + '"';
    }
    // Merge into the corresponding category
    eventrule.mergeIntoDict(dict, eventrule.kss_selector.mergeid, eventrule);
};

kukit.rd.MethodTable.prototype.getMergedRule = function(category, name, binderinstance) {
    // Returns the rule for a given event instance, 
    // Get the entry by category (= document or behaviour)
    var dict = this.content[category];
    if (typeof(dict) == 'undefined') {
        throw 'Unknown method rule category "' + category + '"';
    }
    // look up the rule
    var namespace = binderinstance.__event_namespace__;
    var id = binderinstance.__binder_id__;
    var mergeid = kukit.rd.makeMergeId(id, namespace, name);
    var mergedrule = dict[mergeid];
    if (typeof(mergedrule) == 'undefined') {
        // no error, just return null.
        mergedrule = null;
    }
    return mergedrule;
};

kukit.rd.MethodTable.prototype.bindall = function() {
    // bind document events
    var documentrules = this.content['document'];
    var counter = 0;
    for (var mergeid in documentrules) {
        // bind to null as a node
        documentrules[mergeid].bind(null);
        counter += 1;
    }
    kukit.logDebug('Binding ' + counter + ' special rules in grand total');
};
