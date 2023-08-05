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

kukit.cp = {};

/*
* class CommandProcessor
*/
kukit.cp.CommandProcessor = function() {
      this.commands = new Array();
};

kukit.cp.CommandProcessor.prototype.parseCommands = function(commands, transport) {
    kukit.log('Parse commands');
    kukit.logDebug('Number of commands: ' + commands.length);
    for (var y=0;y < commands.length;y++) {
        var command = commands[y];
        this.parseCommand(command, transport);
        // If we receive an error command, we handle that separately.
        // We abort immediately and let the processError handler do its job.
        // This means that although no other commands should be in commands,
        // we make sure we execute none of them.
        var lastcommand = this.commands[this.commands.length-1];
        if (lastcommand.name == 'error') {
            throw new kukit.err.ExplicitError(lastcommand);
        }
    }
};

kukit.cp.CommandProcessor.prototype.parseCommand = function(command, transport) {
    var selector = "";
    var params = {};
    var name = "";

    selector = command.getAttribute("selector");
    name = command.getAttribute("name");
    type = command.getAttribute("selectorType");
    if (name == null)
        name = "";
    var childNodes = command.childNodes;
    for (var n=0;n < childNodes.length;n++) {
        var childNode = childNodes[n];
        if (childNode.nodeType != 1) 
            continue;
        if (childNode.localName) {
            // (here tolerate both cases)
            if (childNode.localName.toLowerCase() != "param" && childNode.nodeName.toLowerCase() != "kukit:param") {
                throw 'Bad payload, expected param';
            }
        } else {
            //IE does not know DOM2
            if (childNode.nodeName.toLowerCase() != "kukit:param") {
                throw 'Bad payload, expected kukit:param';
            }
        }        
        data = childNode.getAttribute('name');
        if (data != null) { 
            // Decide if we have a string or a dom parameter
            var childCount = childNode.childNodes.length;
            var result;
            if (childCount == 0) {
                // We take this a string (although this could be dom)
                result = '';
            } else if (childCount == 1 && childNode.firstChild.nodeType == 3) {
                // we have a single text node
                result = childNode.firstChild.nodeValue;
            } else {
                // dom
                result = childNode;
            }
            params[data] = result;
        } else {
            throw 'Bad payload, expected attribute "name"';
        }
    }
    var command = new kukit.cr.makeCommand(selector, name, type, params, transport);
    this.addCommand(command);
}; 

kukit.cp.CommandProcessor.prototype.addCommand = function(command) {
    this.commands[this.commands.length] = command;
};

kukit.cp.CommandProcessor.prototype.executeCommands = function(oper) {
    // node, eventrule, binderinstance are given on oper, in case
    // the command was called up from an event
    if (typeof(oper) == 'undefined' || oper == null) {
        oper = new kukit.op.Oper();
    }
    var commands = this.commands;
    for (var y=0;y < commands.length;y++) {
        var command = commands[y];
        try {
            command.execute(oper); 
        } catch (e) {
            if (e.name == 'RuleMergeError' || e.name == 'EventBindError') {
                throw(e);
            } else {
                // augment the error message
                throw new kukit.err.CommandExecutionError(e, command); 
            }
        }
    }
};

