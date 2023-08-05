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

kukit.sr = {};

/* 
* class SelectorTypeRegistry 
*
*  available for plugin registration
*
*  usage:
*
*  kukit.selectorTypesGlobalRegistry.register(name, func);
*
*/
kukit.sr.SelectorTypeRegistry = function () {
    this.mapping = {};
};

kukit.sr.SelectorTypeRegistry.prototype.defaultSelectorType = 'css';

kukit.sr.SelectorTypeRegistry.prototype.register = function(name, func) {
    if (typeof(func) == 'undefined') {
        throw 'Func is mandatory.';
    }
    if (this.mapping[name]) {
        // Do not allow redefinition
        kukit.logError('Error : redefinition attempt of selector ' + name);
        return;
    }
    this.mapping[name] = func;
};

kukit.sr.SelectorTypeRegistry.prototype.get = function(name) {
    if (! name) {
        // if name is null or undefined or '',
        // we use the default type.
        name = this.defaultSelectorType;
    }
    var result = this.mapping[name];
    if (typeof(result) == 'undefined') {
        throw 'Unknown selector type "' + name + '"';
    }
    return result;
};

kukit.selectorTypesGlobalRegistry = new kukit.sr.SelectorTypeRegistry();

kukit.selectorTypesGlobalRegistry.register('htmlid', function(expr, node) {
    var nodes = [];
    var node = document.getElementById(expr);
    if (node) {
        nodes.push(node);
        }
    return nodes;
});

kukit.selectorTypesGlobalRegistry.register('css', function(expr, node) {
    // Always search globally
    var nodes = kukit.dom.cssQuery(expr);
    return nodes;
});

kukit.selectorTypesGlobalRegistry.register('samenode', function(expr, node, orignode) {
    nodes = [orignode];
    return nodes;
});

