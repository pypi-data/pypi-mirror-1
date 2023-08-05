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

kukit.sa = {};

kukit.sa.ServerAction = function(name, oper) {
    this.url = oper.aparms.kssUrl;
    if (typeof(this.url) == 'undefined') {
        this.url = name;
    }
    this.url = this.calculateAbsoluteURL(this.url);
    this.oper = oper;
    this.notifyServer();
};

kukit.sa.ServerAction.prototype.calculateAbsoluteURL = function(url) {
    //
    // If the url is an absolute path, it is used
    //
    // If the url is not an absolute path, it is put at the end of the context
    // url.
    //
    // example: url='@theview/getName',
    //          context='http://your.site.com/portal/folder/object'
    //
    //     result='http://your.site.com/portal/folder/object/@@theview/getName'
    //
    if (url.match(RegExp('/^https?:\/\//'))) {
        return url;
    } else {
        var result = kukit.engine.baseUrl + '/' + url;
        return result;
    }
};

// Backparms can be used on command execution.
kukit.sa.ServerAction.prototype.notifyServer = function() {
    var self = this;
    var sendHook = function(queueItem) {
        // store the queue reception on the oper
        self.oper.queueItem = queueItem;
        self.reallyNotifyServer();
    };
    var timeoutHook = function(queueItem) {
        // store the queue reception on the oper
        self.oper.queueItem = queueItem;
        self.processError('timeout');
    };
    kukit.engine.requestManager.notifyServer(sendHook, this.url, timeoutHook);
};

kukit.sa.ServerAction.prototype.reallyNotifyServer = function() {
    // make a deferred callback
    var domDoc = new XMLHttpRequest();
    var self = this;
    var notifyServer_done  = function() {
        self.notifyServer_done(domDoc);
    };
    // convert params
    var query = new kukit.fo.FormQuery();
    for (var key in this.oper.parms) {
        query.appendElem(key, this.oper.parms[key]);
    }
    var encoded = query.encode();
    // sending form
    var ts = new Date().getTime();
    //kukit.logDebug('TS: '+ts);
    var tsurl = this.url + "?kukitTimeStamp=" + ts;
    domDoc.open("POST", tsurl, true);
    domDoc.onreadystatechange = notifyServer_done;
    domDoc.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    domDoc.send(encoded);
};

kukit.sa.ServerAction.prototype.notifyServer_done = function(domDoc) {
    if (domDoc.readyState == 4) {
        // notify the queue that we are done
        var success = this.oper.queueItem.receivedResult();
        // We only process if the response has not been timed
        // out by the queue in the meantime.
        if (success) {
            // catch the errors otherwise won't get logged.
            // In FF they seem to get swallowed silently.
            try {
                // process the results
                this.processResult(domDoc);
            } catch(e) {
                if (e.name == 'RuleMergeError' || e.name == 'EventBindError') {
                    // Log the message
                    var msg = 'Error setting up events: ' + e.toString();
                    kukit.logFatal(msg);
                    // just throw it too...
                    throw msg;
                } else if (e.name == 'ResponseParsingError') {
                    this.processError('Response parsing error: ' + e);
                } else if (e.name == 'ExplicitError') {
                    this.processError(e.errorcommand);
                } else {
                    kukit.logError('Unhandled error during command execution: ' + e);
                    // also IE acts foul on thrown errors
                    // but at least mumbles something
                    throw e;
                }
            }
        }
/*  } else {
        kukit.logDebug('Request arrived with readyState = ' + domDoc.readyState); */
    }
};

kukit.sa.ServerAction.prototype.processResult = function(domDoc) {
    // checking various dom process errors, and get the commands part
    var dom;
    var commandstags = [];
    // Let's process xml payload first:
    if (domDoc.responseXML) {
        dom = domDoc.responseXML;
        commandstags = kukit.dom.getNsTags(dom, 'commands');
        if (commandstags.length != 1) {
            // no good, maybe better luck with it as html payload
            dom = null;
        }
    }
    // Check for html too, this enables setting the kss error command on the 
    // error response.
    if (dom == null) {
        // Read the header and load it as xml, if defined.
        var payload = domDoc.getResponseHeader('X-KSSCOMMANDS');
        if (payload) {
            try {
                dom = (new DOMParser()).parseFromString(payload, "text/xml");
            } catch(e) {
                throw new kukit.err.ResponseParsingError('Error parsing X-KSSCOMMANDS header.');
            }
            commandstags = kukit.dom.getNsTags(dom, 'commands');
            if (commandstags.length != 1) {
                // no good
                dom = null;
            }
        } else {
            // Ok. we have not found it either in the headers.
            // Check if there was a parsing error in the xml, and log it as reported from the dom
            // Opera <= 8.5 does not have the parseError attribute, so check for it first
            dom = domDoc.responseXML;
            if (dom && dom.parseError && (dom.parseError != 0)) {
                throw new kukit.err.ResponseParsingError('KSS payload not found: ' + Sarissa.getParseErrorText(dom));
            } else {
                throw new kukit.err.ResponseParsingError('KSS payload not found');
            }
        }
    }
    if (dom == null) {
        // this should not happen
        throw new kukit.err.ResponseParsingError('Neither xml nor html payload.');
    }
    // find the commands (atm we don't limit ourselves inside the commandstag)
    var commands = kukit.dom.getNsTags(dom, 'command');
    // Warning, if there is a valid response containing 0 commands.
    if (commands.length == 0) {
        kukit.logWarning('No commands in kukit response');
        return;
    }
    // One or more valid commands to parse
    var command_processor = new kukit.cp.CommandProcessor();
    command_processor.parseCommands(commands, domDoc);
    command_processor.executeCommands(this.oper);
};

kukit.sa.ServerAction.prototype.processError = function(errorcommand) {
    var error_action = null;
    if (this.oper.eventrule) {
        var error_action = this.oper.eventrule.actions.getErrorActionFor(this.oper.action);
        }
    var reason = '';
    if (typeof(errorcommand) == 'string') {
        // not a command, just a string
        reason = ', client_reason="' + errorcommand + '" ';
    } else if (typeof(errorcommand) != 'undefined') {
        // a real error command, sent by the server
        reason = ', server_reason="' + errorcommand.parms.message + '" ';
    }
    if (error_action) {
        kukit.logWarning('Request failed at url ' + this.oper.queueItem.url +
        ', rid=' + this.oper.queueItem.rid + reason + ', will be handled by action "' + error_action.name + '"');
        // Individual error handler was defined. Execute it!
        error_action.execute(this.oper);
    } else {
        // Unhandled: just log it...
        kukit.logError('Request failed at url ' + this.oper.queueItem.url
            + ', rid=' + this.oper.queueItem.rid + reason);
    }
};

