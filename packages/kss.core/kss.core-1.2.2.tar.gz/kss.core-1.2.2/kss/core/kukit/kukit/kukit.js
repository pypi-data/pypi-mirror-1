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



/*
* class Engine
*/
kukit.Engine = function() {
    this.baseUrl = this.calculateBase();
    this.documentRules = new kukit.rd.MethodTable();
    // table from res_type to rule processor
    this._ruleProcessorClasses = {};
    // register processor for type kss
    this._ruleProcessorClasses['kss'] = kukit.kssp.KssRuleProcessor;
    this._ruleProcessors = new Array();
    this.bindScheduler = new kukit.ut.SerializeScheduler();
    // State vars storage. This can be used from kss via a method.
    this.stateVariables = {};
    // instantiate request manager
    this.requestManager = new kukit.rm.RequestManager();
    this.binderInfoRegistry = new kukit.er.BinderInfoRegistry();
    // instantiate a load scheduler
    this.loadScheduler = new kukit.rd.LoadActions();
    this.initializedOnDOMLoad = false;
    // setup events queuing, collect them at the end of commands
    this.setupEventsQueue = [];
    this.setupEventsInProgress = false;

};

kukit.Engine.prototype.calculateBase = function() {
    var base = '';
    try {
        var _dummy = document;
        _dummy = window;
    } catch (e) {
        // testing or what
        return base;
    }
    var nodes = document.getElementsByTagName("link");
    if (nodes.length > 0) {
        for (var i=0; i<nodes.length; i++) {
            var link = nodes[i];
            if (link.rel == 'kss-base-url') {
                return link.href;
            }
        }
    }
    nodes = document.getElementsByTagName("base");
    if (nodes.length == 0) {
        var base = window.location.href;
        var pieces = base.split('/');
        pieces.pop();
        base = pieces.join('/');
    } else {
        base = nodes[0].href;
        // take off trailing slash
        var baselen = base.length;
        if (baselen > 0 && base.substring(baselen - 1) == '/') {
            base = base.substring(0, baselen - 1);
        }
    }
    return base;
};

kukit.Engine.prototype.getRuleSheetLinks = function() {
    var nodes = document.getElementsByTagName("link");
    var results = [];
    for (var i=0; i<nodes.length; i++) {
        if (kukit.isKineticStylesheet(nodes[i])) {
            var res_type = null;
            // Resource syntax is decided on type attribute.
            if((nodes[i].type == 'text/css') || (nodes[i].type == 'text/kss')) {
                res_type = 'kss';
            }
            var newRuleLink = new kukit.RuleSheetLink(nodes[i].href, res_type);
            results[results.length] = newRuleLink;
        }
    }
    return results;
};

kukit.Engine.prototype.createRuleProcessor = function(rulelink) {
    var ruleProcessorClass = this._ruleProcessorClasses[rulelink.res_type];
    if (ruleProcessorClass) {
;;;     var msg = "Start loading and processing " + rulelink.href;
;;;     msg = msg + " of type " + rulelink.res_type;
;;;     kukit.log(msg);
        var ruleprocessor = new ruleProcessorClass(rulelink.href);
        this._ruleProcessors[this._ruleProcessors.length] = ruleprocessor;
        return ruleprocessor;
;;; } else {
;;;     var msg = "Ignore rulesheet " + rulelink.href;
;;;     msg = msg + " of type " + rulelink.res_type;
;;;     kukit.log(msg);
    }
    return null;
};


kukit.Engine.prototype.getRules = function() {
    var rules = new Array();
    var ruleProcessors = this._ruleProcessors
    for (var j=0; j<ruleProcessors.length; j++) {
        var ruleProcessor = ruleProcessors[j];
        for (var i=0; i<ruleProcessor.rules.length; i++) {
            rules.push(ruleProcessor.rules[i]);
        }
    }
    return rules;
}

kukit.Engine.prototype.getRuleProcessors = function() {
    return this._ruleProcessors
}

kukit.isKineticStylesheet = function(node) {
    var rel = node.rel;
    if (rel=="kinetic-stylesheet") {
        return true;
    }
    // BBB to be removed after 2008-02-17
    if (rel=="kukit" || rel=="k-stylesheet") {
;;;     var msg = node.href + ': rel "' + rel +'" is deprecated;';
;;;     msg = msg + ' use "kinetic-stylesheet" instead.';
;;;     kukit.logWarning(msg);
        return true;
    }
    return false;
};

kukit.Engine.prototype.setupEvents = function(inNodes) {
    if (this.setupEventsInProgress) {
        // remember them
        this.setupEventsQueue = this.setupEventsQueue.concat(inNodes);
    } else {
        // do it
        this.doSetupEvents(inNodes);
    }
};

kukit.Engine.prototype.beginSetupEventsCollection = function() {
    this.setupEventsInProgress = true;
};

kukit.Engine.prototype.finishSetupEventsCollection = function() {
    this.setupEventsInProgress = false;
    var setupEventsQueue = this.setupEventsQueue;
    this.setupEventsQueue = [];
    this.doSetupEvents(setupEventsQueue);
};

kukit.Engine.prototype.doSetupEvents = function(inNodes) {
    var self = this;
    var deferredEventsSetup = function() {
        self._setupEvents(inNodes);
    };
;;; var targetMsg;
    var found = false;
    if ( ! inNodes) {
;;;     targetMsg = 'document';
        found = true;
    } else {
;;;     targetMsg = 'nodes subtrees ';
        for (var i=0; i<inNodes.length; i++) {
            var node = inNodes[i];
            if (node.nodeType == 1) {
                if (! found) {
                    found = true;
;;;             } else {
;;;                 targetMsg += ', '; 
                }
;;;             targetMsg += '[' + node.tagName.toLowerCase() + ']';
            }
        }
    }
    if (found) {
        var remark = '';
;;;     remark += 'Setup of events for ' + targetMsg;
        this.bindScheduler.addPre(deferredEventsSetup, remark);
    }
};

kukit.Engine.prototype._setupEvents = function(inNodes) {
    // Decide phase. 1=initial, 2=insertion.
    var phase;
    if (typeof(inNodes) == 'undefined') {
        phase = 1;
    } else {
        phase = 2;
    }
    this.binderInfoRegistry.startBindingPhase();
    var rules = this.getRules();
    var ruletable = new kukit.rd.RuleTable(this.loadScheduler);
    for (var y=0; y < rules.length; y++) {
        rules[y].mergeForSelectedNodes(ruletable, phase, inNodes);
    }
    // bind special selectors first
    if (phase == 1) {
        this.documentRules.bindall(phase);
    }
    // finally bind the merged events
    ruletable.bindall(phase);

    // ... and do the actual binding. 
    this.binderInfoRegistry.processBindingEvents();
};




kukit.Engine.prototype.initializeRules = function() {
    if (window.kukitRulesInitializing || window.kukitRulesInitialized) {
        // Refuse to initialize a second time.
;;;     kukit.log('[initializeRules] is called twice.');
        return;
    }
;;; kukit.log('Initializing rule sheets.');
    // Succesful initialization. At the moment the engine is kept
    // as a global variable, but this needs refinement in the future.
    kukit.engine = this;
    window.kukitRulesInitializing = true;
    // load the rulesheets
    var rulelinks = this.getRuleSheetLinks();
;;; kukit.log("Count of KSS links: " + rulelinks.length);
    for (var i=0; i<rulelinks.length; i++) {
        var rulelink = rulelinks[i];
        var ruleprocessor = this.createRuleProcessor(rulelink);
        if (ruleprocessor) {
;;;         var ts_start = (new Date()).valueOf();
            ruleprocessor.load();
;;;         var ts_loaded = (new Date()).valueOf();
            ruleprocessor.parse();
;;;         var ts_end = (new Date()).valueOf();
;;;         var msg = "Finished loading and processing " + rulelink.href;
;;;         msg += " resource type " + rulelink.res_type;
;;;         msg += ' in ' + (ts_loaded - ts_start) + ' + ';
;;;         msg += (ts_end - ts_loaded) + ' ms.';
;;;         kukit.log(msg);
        }
    }
;;; try {
        this.setupEvents();
;;; } catch(e) {
;;;     // Event setup errors are logged.
;;;     if (e.name == 'RuleMergeError' || e.name == 'EventBindError') {
;;;        var msg = 'Events setup - ' + e.toString();
;;;         // Log the message
;;;         kukit.logFatal(msg);
;;;         // and throw it...
;;;         throw msg;
;;;     } else {
;;;         throw e;
;;;     }
;;; }
    window.kukitRulesInitializing = false;
    window.kukitRulesInitialized = true;
};


/* XXX deprecated methods, to be removed asap 
 * (this was used from the plone plugin only, 
 * to allow the event-registration.js hook)
 */

kukit.initializeRules = function() {
;;; var msg = '[kukit.initializeRules] is deprecated,';
;;; msg += 'use [kukit.bootstrap] instead !';
;;; kukit.logWarning(msg);
    kukit.bootstrap();
};

/*
* class RuleSheetLink
*/
kukit.RuleSheetLink = function(href, res_type) {
    this.href = href;
    this.res_type = res_type;
};

kukit.bootstrap = function() {
;;; kukit.log('Engine instantiated.');
    var engine = new kukit.Engine();
    // Successful initializeRules will store the engine as kukit.engine. 
    // Subsequent activations will not delete the already set up engine.
    // Subsequent activations may happen, if more event handlers are set up,
    // and the first one will do the job, the later ones are ignored.
    engine.initializeRules();
};

kukit.bootstrapFromDOMLoad = function() {
;;; kukit.log('Engine instantiated in [DOMLoad].');
    var engine = new kukit.Engine();
    // Successful initializeRules will store the engine as kukit.engine. 
    // Subsequent activations will not delete the already set up engine.
    // Subsequent activations may happen, if more event handlers are set up,
    // and the first one will do the job, the later ones are ignored.
    engine.initializedOnDOMLoad = true;
    engine.initializeRules();
};

if (typeof(window) != 'undefined') {
    kukit.ut.registerEventListener(window, "load", kukit.bootstrap);
}

