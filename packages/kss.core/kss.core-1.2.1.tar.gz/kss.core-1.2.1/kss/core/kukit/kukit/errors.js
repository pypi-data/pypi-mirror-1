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

kukit.err = {};

/* 
* Exception factory 
*
* Create exception types:
*
* myError = kukit.err.exceptionFactory("myError", "My special error: ");
*
* Throwing:
*
* throw new myError("There was an error in my program.");
*
* Catching example:
*
*   ...
*    } catch(e) {
*        if (e.name == 'JSONRPCError') {
*            ...
*        } else {
*            throw(e);
*        }
*    }
*
* XXX TODO what about IE or other browsers?
* - on IE6, the error text is not printed.
*/


kukit.err.exceptionFactory = function(name) {
    var exc = function (arg1, arg2, arg3, arg4, arg5) {
        var kw = this.__init__(name, arg1, arg2, arg3, arg4, arg5);
        var err = new Error(kw.message);
        for (var key in kw) {
            err[key] = kw[key];
        }
        // number is an IE-only property
        if (typeof err.number == 'number') {
            // show sensible error on IE
            err.toString = function () {
                return this.name + ': ' + this.message;
            };
        }
        return err;
    };
    exc.prototype.__init__ = function(name, message) {
        var kw = {};
        kw.name = name;
        kw.message = message;
        return kw;
    };
    return exc;
};

;;; // this should be thrown with the error command as parameter
;;; kukit.err.ExplicitError = kukit.err.exceptionFactory('ExplicitError');
;;; kukit.err.ee = kukit.err.ExplicitError;
;;; kukit.err.ee.prototype.__superinit__ = kukit.err.ee.prototype.__init__;
;;; kukit.err.ee.prototype.__init__ = function(name, errorcommand) {
;;;     var message = 'Explicit error';
;;;     var kw = this.__superinit__(name, message);
;;;     kw.errorcommand = errorcommand;
;;;     return kw;
;;; };

;;; var name = 'ResponseParsingError';
;;; kukit.err.ResponseParsingError = kukit.err.exceptionFactory(name);

;;; var name = 'CommandExecutionError';
;;; kukit.err.CommandExecutionError = kukit.err.exceptionFactory(name);
;;; kukit.err.cex = kukit.err.CommandExecutionError;
;;; kukit.err.cex.prototype.__superinit__ = kukit.err.cex.prototype.__init__; 
;;; kukit.err.cex.prototype.__init__ = function(name, e, command) {
;;;     var kw = this.__superinit__(name, '');
;;;     kw.message = 'Command [' + command.name + '] ' + e.toString();
;;;     return kw;
;;; };

kukit.err.rd = {};
;;; kukit.err.rd.RuleMergeError = kukit.err.exceptionFactory('RuleMergeError');

;;; var name = 'KssSelectorError';
;;; kukit.err.rd.KssSelectorError = kukit.err.exceptionFactory(name);

;;; var name = 'EventBindError';
;;; kukit.err.rd.EventBindError = kukit.err.exceptionFactory(name);
;;; kukit.err.rd.ebe = kukit.err.rd.EventBindError;
;;; kukit.err.rd.ebe.prototype.__superinit__ = kukit.err.rd.ebe.prototype.__init__; 
;;; kukit.err.rd.ebe.prototype.__init__ = function(name, message, eventName, eventNamespace) {
;;;     var kw = this.__superinit__(name, message);
;;;     kw.eventName = eventName;
;;;     kw.eventNamespace = eventNamespace;
;;;     kw.message += ' When binding event name [' + eventName;
;;;     kw.message += '] in namespace [' + eventNamespace + '].';
;;;     return kw;
;;; };

kukit.err.tk = {};
;;; kukit.err.tk.ParsingError = kukit.err.exceptionFactory('ParsingError');
;;; kukit.err.tk.pe = kukit.err.tk.ParsingError; 
;;; kukit.err.tk.pe.prototype.__superinit__ = kukit.err.tk.pe.prototype.__init__; 
;;; kukit.err.tk.pe.prototype.__init__ = function(name, message, cursor) {
;;;     var kw = this.__superinit__(name, message);
;;;     if (cursor) {
;;;         kw.errpos = cursor.pos;
;;;         kw.errrow = cursor.row;
;;;         kw.errcol = cursor.col;
;;;         kw.message += ' at row ' + kw.errrow + ', column ' + kw.errcol;
;;;     } else {
;;;         kw.errpos = null;
;;;         kw.errrow = null;
;;;         kw.errcol = null;
;;;     }
;;;     return kw;
;;; };

