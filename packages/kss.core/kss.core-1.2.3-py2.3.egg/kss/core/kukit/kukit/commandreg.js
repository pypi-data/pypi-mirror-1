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

/* Command registration */

kukit.cr = {};

/*
*  class CommandRegistry
*/
kukit.cr.CommandRegistry = function () {
    this.commands = {};
};

/* 
* This is the proposed way of registration, as we like all commands to be
*  client actions first.
* 
*  Examples:
* 
*  kukit.actionsGlobalRegistry.register('log', f1);
*  kukit.commandsGlobalRegistry.registerFromAction('log',
*       kukit.cr.makeGlobalCommand);
* 
*  kukit.actionsGlobalRegistry.register('replaceInnerHTML', f2);
*  kukit.commandsGlobalRegistry.registerFromAction('replaceInnerHTML',
*       kukit.cr.makeSelectorCommand);
*/
kukit.cr.CommandRegistry.prototype.registerFromAction =
    function(srcname, factory, name) {
    if (typeof(name) == 'undefined') {
        // allows to set a different name as the action name,
        // usable for backward
        // compatibility setups
        name = srcname;
    }
    // register a given action as a command, using the given vactor
    var f = kukit.actionsGlobalRegistry.get(srcname);
    factory(name, f);
};

kukit.cr.CommandRegistry.prototype.register = function(name, klass) {
    if (this.commands[name]) {
        // Do not allow redefinition
;;;     var msg = 'ValueError : command [' + name + '] is already registered.';
;;;     kukit.logError(msg);
        return;
        }
    this.commands[name] = klass;
};

kukit.cr.CommandRegistry.prototype.get = function(name) {
    var klass = this.commands[name];
;;; if (! klass) {
;;;     // not found
;;;     var msg = 'ValueError : no command registered under [' + name + '].';
;;;     kukit.logError(msg);
;;;    }
    return klass;
};

kukit.commandsGlobalRegistry = new kukit.cr.CommandRegistry();


/* XXX deprecated methods, to be removed asap */

kukit.cr.commandRegistry = {};
kukit.cr.commandRegistry.registerFromAction = function(srcname, factory, name) {
;;; var msg = 'Deprecated kukit.cr.commandRegistry.registerFromAction,';
;;; msg += ' use kukit.commandsGlobalRegistry.registerFromAction instead! (';
;;; msg += srcname + ')';
;;; kukit.logWarning(msg);
    kukit.commandsGlobalRegistry.registerFromAction(srcname, factory, name);
};

/* Command factories */

kukit.cr.makeCommand = function(selector, name, type, parms, transport) {
    var commandClass = kukit.commandsGlobalRegistry.get(name);
    var command = new commandClass();
    command.selector = selector;
    command.name = name;
    command.selectorType = type;
    command.parms = parms;
    command.transport = transport;
    return command;
};

kukit.cr._Command_execute = function(oper) {
    var newoper = oper.clone({
        'parms': this.parms,
        'orignode': oper.node,
        'node': null
        });
    this.executeOnScope(newoper);
};

kukit.cr._Command_execute_selector = function(oper) {
    var selfunc = kukit.selectorTypesGlobalRegistry.get(this.selectorType);
    // When applying the selection, the original event target will be used
    // as a starting point for the selection.
    var nodes = selfunc(this.selector, oper.orignode, {});
;;; var printType;
;;; if (this.selectorType) {
;;;     printType = this.selectorType;
;;; } else {
;;;     printType = 'default (';
;;;     printType += kukit.selectorTypesGlobalRegistry.defaultSelectorType;
;;;     printType += ')';
;;; }
;;; var msg = 'Selector type [' + printType + '], selector [';
;;; msg += this.selector + '], selected nodes [' + nodes.length + '].';
;;; kukit.logDebug(msg);
;;; if (!nodes || nodes.length == 0) {
;;;     kukit.logWarning('Selector found no nodes.');
;;; }
    for (var i=0;i < nodes.length;i++) {
        oper.node = nodes[i];
        //XXX error handling for wrong command name
;;;     kukit.logDebug('[' + this.name + '] execution.');
        this.executeOnSingleNode(oper);
    }
};

kukit.cr.makeSelectorCommand = function(name, executeOnSingleNode) {
    var commandClass = function() {};
    commandClass.prototype = {
        execute: kukit.cr._Command_execute,
        executeOnScope: kukit.cr._Command_execute_selector,
        executeOnSingleNode: executeOnSingleNode
    };
    kukit.commandsGlobalRegistry.register(name, commandClass); 
};

kukit.cr.makeGlobalCommand = function(name, executeOnce) {
    var commandClass = function() {};
    commandClass.prototype = {
        execute: kukit.cr._Command_execute,
        executeOnScope: executeOnce,
        executeOnSingleNode: executeOnce
    };
    kukit.commandsGlobalRegistry.register(name, commandClass); 
};

