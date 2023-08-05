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

kukit.ar = {};

/*
*  class ActionRegistry
* 
*  The local event actions need to be registered here.
*/
kukit.ar.ActionRegistry = function () {
    this.content = {};
};

kukit.ar.ActionRegistry.prototype.register = function(name, func) {
    ;;; if (typeof(func) == 'undefined') {
    ;;;     throw 'func argument is mandatory when registering an action (ActionRegistry.register).';
    ;;; }
    if (this.content[name]) {
        // Do not allow redefinition
        ;;; kukit.logError('Error : action "' + name + '" already registered.');
        return;
        }
    this.content[name] = func;
};

kukit.ar.ActionRegistry.prototype.exists = function(name) {
    var entry = this.content[name];
    return (typeof(entry) != 'undefined');
};

kukit.ar.ActionRegistry.prototype.get = function(name) {
    var func = this.content[name];
    if (! func) {
        // not found
        ;;; kukit.E = 'Error : undefined local action "' + name + '"';
        throw kukit.E;
        //kukit.logError(kukit.E);
        }
    return func;
};

kukit.actionsGlobalRegistry = new kukit.ar.ActionRegistry();


/* XXX deprecated methods, to be removed asap */

kukit.ar.actionRegistry = {};
kukit.ar.actionRegistry.register = function(name, func) {
    ;;; kukit.logWarning('Deprecated kukit.ar.actionRegistry.register, use kukit.actionsGlobalRegistry.register instead! (' + name + ')');
    kukit.actionsGlobalRegistry.register(name, func);
};

