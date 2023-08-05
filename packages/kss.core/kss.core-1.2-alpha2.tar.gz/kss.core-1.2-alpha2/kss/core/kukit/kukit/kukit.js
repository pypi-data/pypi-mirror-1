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
    this.rules = new Array();
    this.bindScheduler = new kukit.ut.SerializeScheduler();
    // State vars storage. This can be used from kss via a method.
    this.statevars = {};
    // instantiate request manager
    this.requestManager = new kukit.rm.RequestManager();
    this.binderInfoRegistry = new kukit.er.BinderInfoRegistry();
    // instantiate a load scheduler
    this.loadScheduler = new kukit.rd.LoadActions();
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
    var nodes = document.getElementsByTagName("base");
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
        if (nodes[i].rel=="kukit" || nodes[i].rel=="k-stylesheet" ) {
            var res_type = null;
            // Resource syntax is decided on type attribute.
            if((nodes[i].type == 'text/css') || (nodes[i].type == 'text/kss')) {
                res_type = 'kss';
            }
            results[results.length] = new kukit.RuleSheetLink(nodes[i].href, res_type);
        }
    }
    return results;
};

kukit.Engine.prototype.setupEvents = function(in_nodes) {
    var self = this;
    var f = function() {
        self._setupEvents(in_nodes);
    };
    var targetmsg;
    var found = false;
    if ( ! in_nodes) {
        targetmsg = 'document';
        found = true;
    } else {
        targetmsg = 'node subtrees ';
        for (var i=0; i<in_nodes.length; i++) {
            var node = in_nodes[i];
            if (node.nodeType == 1) {
                if (! found) {
                    found = true;
                } else {
                    targetmsg += ', '; 
                }
                targetmsg += node.tagName.toLowerCase();
            }
        }
    }
    if (found) {
        this.bindScheduler.addPre(f, 'setting up events for ' + targetmsg);
    }
};

kukit.Engine.prototype._setupEvents = function(in_nodes) {
    // Decide phase. 1=initial, 2=insertion.
    var phase;
    if (typeof(in_nodes) == 'undefined') {
        phase = 1;
    } else {
        phase = 2;
    }
    this.binderInfoRegistry.startBindingPhase();
    var rules = this.rules;
    var ruletable = new kukit.rd.RuleTable(this.loadScheduler);
    for (var y=0; y < rules.length; y++) {
        rules[y].mergeForSelectedNodes(ruletable, phase, in_nodes);
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
        kukit.log('Subsequent call to initializeRules is ignored');
        return;
    }
    // Succesful initialization. At the moment the engine is kept
    // as a global variable, but this needs refinement in the future.
    kukit.engine = this;
    window.kukitRulesInitializing = true;
    // load the rulesheets
    var rulelinks = this.getRuleSheetLinks();
    kukit.log("Count of KSS links: " + rulelinks.length);
    for (var i=0; i<rulelinks.length; i++) {
        var rulelink = rulelinks[i];
        var ruleProcessorClass = this._ruleProcessorClasses[rulelink.res_type];
        if (ruleProcessorClass) {
            kukit.log("Start loading and processing " + rulelink.href + " resource type " + rulelink.res_type);
            var ruleprocessor = new ruleProcessorClass(rulelink.href);
            var ts_start = (new Date()).valueOf();
            ruleprocessor.load();
            var ts_loaded = (new Date()).valueOf();
            try {
                ruleprocessor.parse();
            } catch(e) {
                // ParsingError are logged.
                if (e.name == 'ParsingError') {
                    var msg = 'Error parsing ' + rulelink.res_type + ' at ' + rulelink.href + ' : ' + e.toString();
                    // Log the message
                    kukit.logFatal(msg);
                    // and throw it...
                    throw msg;
                } else {
                    throw e;
                }
            }
            var ts_end = (new Date()).valueOf();
            kukit.log("Finished loading and processing " + rulelink.href + " resource type " + rulelink.res_type + ' in ' + (ts_loaded - ts_start) + ' + ' + (ts_end - ts_loaded) + ' ms');
            this._ruleProcessors[this._ruleProcessors.length] = ruleprocessor;
        } else {
            kukit.logError("Ignoring rulesheet " + rulelink.href + ' of type ' + rulelink.res_type);
        }
    }
    try {
        this.setupEvents();
    } catch(e) {
        // Event setup errors are logged.
        if (e.name == 'RuleMergeError' || e.name == 'EventBindError') {
            var msg = 'Error setting up events: ' + e.toString();
            // Log the message
            kukit.logFatal(msg);
            // and throw it...
            throw msg;
        } else {
            throw e;
        }
    }
    window.kukitRulesInitializing = false;
    window.kukitRulesInitialized = true;
};


/* XXX deprecated methods, to be removed asap 
 * (this was used from the plone plugin only, 
 * to allow the event-registration.js hook)
 */

kukit.initializeRules = function() {
    kukit.logWarning('Deprecated kukit.initializeRules, use kukit.bootstrap instead!');
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
    var engine = new kukit.Engine();
    // Successful initializeRules will store the engine as kukit.engine. 
    // Subsequent activations will not delete the already set up engine.
    // Subsequent activations may happen, if more event handlers are set up,
    // and the first one will do the job, the later ones are ignored.
    engine.initializeRules();
};

if (typeof(window) != 'undefined') {
    kukit.ut.registerEventListener(window, "load", kukit.bootstrap);
}

