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
;;; if (name.indexOf('@') != -1) {
;;;     var msg = 'Kss selector name must not contain @: [' + name + '].';
;;;     throw new kukit.err.rd.KssSelectorError(msg);
;;;     }
;;; if (id && id.indexOf('@') != -1) {
;;;     var msg = 'Kss selector id must not contain @: [' + id + '].';
;;;     throw new kukit.err.rd.KssSelectorError(msg);
;;;     }
;;; if (namespace && namespace.indexOf('@') != -1) {
;;;     var msg = 'Kss selector namespace must not contain @: [' + namespace;
;;;     msg = msg + '].';
;;;     throw new kukit.err.rd.KssSelectorError(msg);
;;;    }
;;; if (! isEvent) {
;;;     // method rule
;;;     if (css != 'document' && css != 'behaviour') {
;;;         var msg = 'KssSpecialSelector [' + name;
;;;         msg = msg + '] must have one of the allowed names';
;;;         throw new kukit.err.rd.KssSelectorError(msg);
;;;    }
;;; }
    this.css = css;
    this.name = name;
    this.namespace = namespace;
    this.className = null;
    this.id = id;
};

kukit.rd.KssSelector.prototype.setIdAndClass = function() {
    // Sets up id and class on the selector, based on registration info
    this.className = kukit.eventsGlobalRegistry.get(
        this.namespace, this.name).className;
    if (this.id == null) {
        // singleton for class
        this.id = kukit.rd.makeId(this.namespace, this.className);
    }
    // Also set the merge id. The rules with the same merge
    // id should be merged on the same node.
    this.mergeId = kukit.rd.makeMergeId(this.id, this.namespace, this.name);
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

kukit.rd.KssTextValue.prototype.evaluate =
    function(parms, key, node, defaultParameters) {

    // For normal string parms, this would return the string itself.
    // In other execution contexts (like kssSelector, for example) this can
    // do something else.
    parms[key] = this.pprovider.eval([this.txt], node, defaultParameters);
};

/*
*  class KssTextValue
*/
kukit.rd.KssMethodValue = function(methodName, args) {
    // A method parameter in the format 
    //      key: methodName(v1, v2, ... vn);
    this.methodName = methodName;
    this.args = args;
};

kukit.rd.KssMethodValue.prototype.isMethod = true;

kukit.rd.KssMethodValue.prototype.check = function(registry) {
    // Check syntax
    var f = registry.get(this.methodName);
    this.pprovider = new f();
;;; this.pprovider.check(this.args);
};

kukit.rd.KssMethodValue.prototype.evaluate =
    function(parms, key, node, defaultParameters) {

    // Evaluate into parms.
    parms[key] = this.pprovider.eval(this.args, node, defaultParameters);
};

/*
*  class KssPseudoValue
*/
kukit.rd.KssPseudoValue = function(methodName, args) {
    // A method parameter in the format 
    //      methodName(v1)
    this.methodName = methodName;
    this.args = args;
};

kukit.rd.KssPseudoValue.prototype.isMethod = true;

kukit.rd.KssPseudoValue.prototype.check = function() {
};

kukit.rd.EventRuleNr = 0;            // just a counter

/*
*  class EventRule
*/
kukit.rd.EventRule = function(kssSelector, parms, actions) {
    if (typeof(parms) == 'undefined') {
        // called for merging clone
        this.kssSelector = kssSelector;
    } else {
        this.index = kukit.rd.EventRuleNr;
        this.mergedIndex = null;
        kukit.rd.EventRuleNr = this.index + 1;
;;;     var namestr;
;;;     if (kssSelector.namespace) {
;;;         namestr = kssSelector.namespace + '-' + kssSelector.name;
;;;     } else {
;;;         namestr = kssSelector.name;
;;;     }
;;;     var msg = 'EventRule #' + this.getIndex() + ': ';
;;;     msg = msg + kssSelector.css + ' EVENT=' + namestr;
;;;     kukit.logDebug(msg);
        this.kssSelector = kssSelector;
        this.parms = parms;
        this.actions = actions;
    }
};

kukit.rd.EventRule.prototype.getIndex = function() {
    if (this.mergedIndex) {
        return this.mergedIndex;
    } else {
        return this.index;
    }
};

kukit.rd.EventRule.prototype.mergeForSelectedNodes = 
    function(ruletable, phase, inNodes) {

    // Select all nodes within the inNodes for phase==2.
    // (or undefined on initial node, phase==1)
    // Merge itself to the selected nodes.
    if (this.kssSelector.isEventSelector) {
        var nodes = kukit.dom.cssQuery(this.kssSelector.css, inNodes);
        var counter = 0;
        for (var y=0; y < nodes.length; y++)
        {
            var node = nodes[y];
            // XXX never rebind to any node again!
            // this compensates that cssQuery is returning
            // results out of the subtree
            if (typeof(node._kukitmark) == 'undefined') {
                ruletable.add(node, this);
                counter += 1;
                }
        }
;;;     if (counter > 0) {
;;;         var msg = 'EventRule [#' + this.getIndex();
;;;         msg = msg + '-' + this.kssSelector.mergeId;
;;;         msg = msg + '] selected ' + counter + ' nodes.';
;;;         kukit.logDebug(msg);
;;;     }
    } else if (typeof(inNodes) == 'undefined') {
        // Method selector. They only need to be handled on the initial
        // pageload, when the inNodes parameter is ommitted.
        kukit.engine.documentRules.add(this);
    }
};

kukit.rd.EventRule.prototype.getBinderInfo = function() {
    // Gets the event instance for the rule.
    return kukit.engine.binderInfoRegistry.getOrCreateBinderInfo(
        this.kssSelector.id, this.kssSelector.className, 
        this.kssSelector.namespace);
};

/*
* bind(node) : calls binder hook on event instance.
*  These hooks are tried in order, if succeeds it must return true:
*
* __bind__(name, parms, func_to_bind, node, eventRule)
* __bind_<name>__(parms, func_to_bind, node, eventRule)
*
* If none succeeds is an error.
*
*/

kukit.rd.EventRule.prototype.bind = function(node) {
    // Creation of the binding oper
    var oper = new kukit.op.Oper();
    var binderInfo = this.getBinderInfo();
    oper.node = node;
    oper.eventRule = this;
    oper.binderInstance = binderInfo.binderInstance;
    oper.parms = this.parms;
    // mark on the instance as bound
    binderInfo.bindOper(oper); 
};


/*
* Merging event rules
*/

kukit.rd.EventRule.prototype.isMerged = function() {
    return (this.mergedIndex != null);
};

kukit.rd.EventRule.prototype.cloneForMerge = function() {
    // Do not touch ourselves, make a new copy for the merge.
    var merged = new kukit.rd.EventRule(this.kssSelector);
    merged.actions = new kukit.rd.ActionSet();
    merged.parms = {};
    merged.mergedIndex = 'X';
    merged.merge(this);
    merged.mergedIndex = this.getIndex();
    return merged;
};

kukit.rd.EventRule.prototype.merge = function(other) {
;;; if (! this.isMerged()) {
;;;     throw 'Cannot merge into a genuine event rule';
;;; }
;;; if (this.kssSelector.isEventSelector) {
;;;     if (this.kssSelector.id != other.kssSelector.id) {
;;;         throw 'Differing kss selector ids in event rule merge';
;;;     }
;;;     if (this.kssSelector.className != other.kssSelector.className) {
;;;         throw 'Differing kss selector classes in event rule merge';
;;;     }
;;; }
;;; if (this.kssSelector.name != other.kssSelector.name) {
;;;     throw 'Differing kss selector names in event rule merge';
;;; }
    this.mergedIndex = this.mergedIndex + ',' + other.getIndex();
    for (var key in other.parms) {
        this.parms[key] = other.parms[key];
    }
    this.actions.merge(other.actions);
;;; if (this.mergedIndex.substr(0, 1) != 'X') {
;;;     // ignore initial clone-merge
;;;     var msg = 'Merged rule [' + this.mergedIndex;
;;;     msg = msg + '-' + this.kssSelector.mergeId + '].';
;;;     kukit.logDebug(msg);
;;; }
};

kukit.rd.EventRule.prototype.mergeIntoDict = function(dict, key, eventRule) {
    // Merge into the given dictionary by given key.
    // If possible, store the genuine rule first - if not,
    // clone it and do a merge. Never destroy the genuine
    // rules, clone first. This is for efficiency.
    var mergedRule = dict[key];
    if (typeof(mergedRule) == 'undefined') {
        // there was no rule
        dict[key] = eventRule;
    } else {
        // we have to merge the rule
        if (! mergedRule.isMerged()) {
            // Make sure genuine instances are replaced
            mergedRule = mergedRule.cloneForMerge();
            dict[key] = mergedRule;
        }
        mergedRule.merge(eventRule);
    }
};

/*
*  class ActionSet
*/
kukit.rd.ActionSet = function() {
    this.content = {};
};

kukit.rd.ActionSet.prototype.hasActions = function() {
    for (var name in this.content) {
        return true;
    }
    return false;
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
;;;             var msg = 'Cannot action-delete unexisting action, [';
;;;             msg = msg + key + '].';
;;;             kukit.E = new kukit.err.rd.RuleMergeError(msg);
                throw kukit.E;
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
    // parms so it was actually not entered as an action object
    // otherwise, it would have been executed from action.execute already
    if (typeof(this.content['default']) == 'undefined') {
        // this is conditional: if there is no default method, it's skipped.
        var name = oper.eventRule.kssSelector.name;
        // Execution with no parms. (XXX ?)
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
;;; if (typeof(action) == 'undefined') {
;;;     throw('Action [' + name + '] does not exist and cannot be deleted.');
;;; }
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
;;; if (this.name != null && this.name != name) {
;;;     var msg = 'Error overriding action name [' + this.name;
;;;     msg = msg + '] to [' + name + '] (Unmatching action names at merge?)';
;;;     throw new kukit.err.rd.RuleMergeError(msg);
;;; }
    this.name = name;
    if (name == 'default') {
;;;     if (this.type != null && this.type != 'D') {
;;;         var msg = 'Error setting action to default on action [' + this.name;
;;;         msg = msg + '], current type [' + this.type + '].';
;;;         throw new kukit.err.rd.RuleMergeError(msg);
;;;     }
        this.setType('D');
    }
};

kukit.rd.Action.prototype.setType = function(type) {
    // Allowed types:
    //
    // S = server
    // C = client
    // E = error / client
    // D = default (unsettable)
    // X = cancel action
;;; var checkType = function(type) {
;;;     var isNotServer = type != 'S';
;;;     var isNotClient = type != 'C';
;;;     var isNotError = type != 'E';
;;;     var isNotCancel = type != 'X';
;;;     return isNotServer && isNotClient && isNotError && isNotCancel;
;;; };
;;; if (checkType(type) || (this.type != null && this.type != type)) {
;;;     var msg = 'Error setting action type on action [' + this.name;
;;;     msg = msg + '] from [' + this.type + '] to [' + type;
;;;     msg = msg + '] (Attempt to merge client, server or error actions ?)';
;;;     throw new kukit.err.rd.RuleMergeError(msg);
;;; }
;;; if (this.error != null && this.type != 'S') {
;;;     var msg = 'Error setting action error handler on action [' + this.name;
;;;     msg = msg + '], this is only allowed on server actions.';
;;;     throw new kukit.err.rd.RuleMergeError(msg);
;;; }
    this.type = type;  
};

kukit.rd.Action.prototype.setError = function(error) {
;;; if (this.type != null && this.type != 'S') {
;;;     var msg = 'Error setting action error handler on action [' + this.name;
;;;     msg =  msg + '], this is only allowed on server actions.';
;;;     throw new kukit.err.rd.RuleMergeError(msg);
;;; }
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

kukit.rd.Action.prototype.makeActionOper = function(oper) {
    // Fill the completed action parms, based on the node
    // The kssXxx parms, reserved for the action, are 
    // handled as appropriate.
    // A cloned oper is returned.
    var parms = {};
    var kssParms = {};
    // Make sure we have defaultParameters on oper
    if (typeof(oper.defaultParameters) == 'undefined') {
        oper.defaultParameters = {};
    }
    for (var key in this.parms) {
        var kssvalue = this.parms[key]; 
        if (key.match(/^kss/)) {
            // kssXxx parms are separated to kssParms.
            kssvalue.evaluate(kssParms, key, oper.node,
                oper.defaultParameters); 
        } else {
            // evaluate the method parms into parms
            kssvalue.evaluate(parms, key, oper.node,
                oper.defaultParameters); 
        }
    }
    var anOper = oper.clone({
            'parms': parms,
            'kssParms': kssParms,
            'action': this
        });
    return anOper;
};

kukit.rd.Action.prototype.execute = function(oper) {
    oper = this.makeActionOper(oper);
    switch (this.type) {
        case 'D': {
            // Default action.
            var name = oper.eventRule.kssSelector.name;
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
*   To summarize the procedure, each eventRule is added with
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

kukit.rd.RuleTable.prototype.add = function(node, eventRule) {
    // look up node
    var nodehash = kukit.rd.hashNode(node);
    var nodeval = this.nodes[nodehash];
    if (typeof(nodeval) == 'undefined') {
        nodeval = {'node': node, 'val': {}};
        this.nodes[nodehash] = nodeval;
    }
    // Merge into the dict
    eventRule.mergeIntoDict(
        nodeval.val, eventRule.kssSelector.mergeId, eventRule);
};

kukit.rd.RuleTable.prototype.bindall = function(phase) {
    // Bind all nodes
    var counter = 0;
    for (var nodehash in this.nodes) {
        var nodeval = this.nodes[nodehash];
        // XXX Mark the node, disabling rebinding in a second round
        nodeval.node._kukitmark = phase;
        for (var id in nodeval.val) {
            var eventRule = nodeval.val[id];
            eventRule.bind(nodeval.node);            
        }
        counter += 1;
    }
;;; kukit.logDebug(counter + ' nodes bound in grand total.');
    // Execute the load actions in a deferred manner
    var loadactions = this.loadScheduler;
    if (! loadactions.empty()) {
;;;     kukit.logDebug('Delayed load actions execution starts.');
        var count = loadactions.executeAll();
;;;     kukit.logDebug(count + ' load actions executed.');
    }
};

kukit.rd.uid = 0;

kukit.rd.hashNode = function(node) {
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

kukit.rd.MethodTable.prototype.add = function(eventRule) {
    // Get the entry by the type which is now at css
    var category = eventRule.kssSelector.css;
    var dict = this.content[category];
;;; if (typeof(dict) == 'undefined') {
;;;     throw 'Unknown method rule category [' + category + '].';
;;; }
    // Merge into the corresponding category
    eventRule.mergeIntoDict(dict, eventRule.kssSelector.mergeId, eventRule);
};

kukit.rd.MethodTable.prototype.getMergedRule =
    function(category, name, binderInstance) {

    // Returns the rule for a given event instance, 
    // Get the entry by category (= document or behaviour)
    var dict = this.content[category];
;;; if (typeof(dict) == 'undefined') {
;;;     throw 'Unknown method rule category [' + category + '].';
;;; }
    // look up the rule
    var namespace = binderInstance.__eventNamespace__;
    var id = binderInstance.__binderId__;
    var mergeId = kukit.rd.makeMergeId(id, namespace, name);
    var mergedRule = dict[mergeId];
    if (typeof(mergedRule) == 'undefined') {
        // no error, just return null.
        mergedRule = null;
    }
    return mergedRule;
};

kukit.rd.MethodTable.prototype.bindall = function() {
    // bind document events
    var documentRules = this.content['document'];
    var counter = 0;
    for (var mergeId in documentRules) {
        // bind to null as a node
        documentRules[mergeId].bind(null);
        counter += 1;
    }
;;; kukit.logDebug(counter + ' special rules bound in grand total.');
};
