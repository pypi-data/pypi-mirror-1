/*
* Copyright (c) 2005-2007
* Authors: KSS Project Contributors (see docs/CREDITS.txt)
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

/* Create kukit namespace */

if (typeof(kukit) == 'undefined') {
    var kukit = {};
}

;;; /*  ----------------------------------------------------------------
;;;  *  Lines starting with the ;;; are only cooked in development mode.
;;;  *  ----------------------------------------------------------------
;;;  */

/*
 * kukit.E is a proxy variable used globally for error and info messages.
 * This assure the following code can be used:
 *    
 *     ;;; kukit.E = 'This is the error message';
 *     throw kukit.E;
 *
 * or:
 *
 *     ;;; kukit.E = 'The event' + event + ' caused problems';
 *     method_with_info(x, kukit.E);
 *
 * or even:
 *
 *     ;;; kukit.E = 'The event' + event + ' caused problems ';
 *     ;;; kukit.E += 'and this is a very long line ';
 *     ;;; kukit.E += 'so we split it to parts for better readibility';
 *     ;;; kukit.logWarning(kukit.E);
 *
 */
kukit.E = 'Unknown message (kss optimized for production mode)';

// Browser identification. We need these switches only at the moment.
try {
    kukit.HAVE_SAFARI = navigator.vendor && navigator.vendor.indexOf('Apple') != -1;
    kukit.HAVE_IE =  eval("_SARISSA_IS_IE");
} catch (e) {}

;;; // Activation of extra logging panel: if necessary
;;; // this allows to start the logging panel from the browser with
;;; //    javascript:kukit.showlog();
;;; kukit.showlog = function() {
;;;     kukit.logWarning('Logging is on the console: request to show logging pane ignored');
;;; };

// We want a way of knowing if Firebug is available :
// it is very convenient to log a node in Firebug;
// you get a clickable result that brings you to Firebug inspector.
// The pattern is the following :
//  if (kukit.hasFirebug) {
//     kukit.log(node);
//  }
kukit.hasFirebug = false;

;;; // check whether the logging stuff of Firebug is available
;;; if (typeof kukit.log == 'undefined' && typeof console != 'undefined' && typeof console.log != 'undefined' && typeof console.debug != 'undefined' && typeof console.error != 'undefined' && typeof console.warn != 'undefined') {
;;;         kukit.log = console.log;
;;;         kukit.logDebug = console.debug;
;;;         kukit.logFatal = console.error;
;;;         kukit.logError = console.error;
;;;         kukit.logWarning = console.warn;
;;;         kukit.hasFirebug = true;
;;; }

;;; // check whether the logging stuff of MochiKit is available
;;; if (typeof kukit.log == 'undefined' && typeof MochiKit != 'undefined' && typeof MochiKit.Logging != 'undefined' && typeof MochiKit.Logging.log != 'undefined') {
;;;         kukit.log = MochiKit.Logging.log;
;;;         kukit.logError = MochiKit.Logging.logError;
;;;         kukit.logDebug = MochiKit.Logging.logDebug;
;;;         kukit.logFatal = MochiKit.Logging.logFatal;
;;;         kukit.logWarning = MochiKit.Logging.logWarning;
;;;         // make convenience url
;;;         //    javascript:kukit.showlog();
;;;         // instead of the need to say
;;;         //    javascript:void(createLoggingPane(true));
;;;         kukit.showlog = function() {
;;;             createLoggingPane(true);
;;;         };
;;; }

;;; // check whether the logging stuff of Safari is available
;;; if (typeof kukit.log == 'undefined' && typeof console != 'undefined' && typeof console.log != 'undefined') {
;;;         kukit.log = function(str) { console.log('INFO: '+str); };
;;;         kukit.logError = function(str) { console.log('ERROR: '+str); };
;;;         kukit.logDebug = function(str) { console.log('DEBUG: '+str); };
;;;         kukit.logFatal = function(str) { console.log('FATAL: '+str); };
;;;         kukit.logWarning = function(str) { console.log('WARNING: '+str); };
;;; }

/* no logging solution available */
;;; if (typeof kukit.log == 'undefined') {
        kukit.log = function(str){};
        kukit.logError = kukit.log;
        kukit.logDebug = kukit.log;
        kukit.logFatal = kukit.log;
        kukit.logWarning = kukit.log;
;;; }

// log a startup message
;;; kukit.log('Initializing kss');

/* utilities */

kukit.ut = {};


/* 
* class FifoQueue
*/
kukit.ut.FifoQueue = function () {
    this.reset();
};

kukit.ut.FifoQueue.prototype.reset = function() {
    this.elements = new Array();
};

kukit.ut.FifoQueue.prototype.push = function(obj) {
    this.elements.push(obj);
};

kukit.ut.FifoQueue.prototype.pop = function() {
    return this.elements.shift();
};

kukit.ut.FifoQueue.prototype.empty = function() {
    return ! this.elements.length;
};

kukit.ut.FifoQueue.prototype.size = function() {
    return this.elements.length;
};

kukit.ut.FifoQueue.prototype.front = function() {
    return this.elements[0];
};

/*
* class SortedQueue
*/
kukit.ut.SortedQueue = function (comparefunc) {
    // comparefunc(left, right) determines the order by returning -1 if left should 
    // occur before right, +1 if left should occur after right or 
    // 0 if left and right  have no preference as to order.
    // If comparefunc is not specified or is undefined, the default order specified by < used.
    if (comparefunc) {
        this.comparefunc = comparefunc;
    }
    this.reset();
};

kukit.ut.SortedQueue.prototype.comparefunc = function(a, b) {
    if (a < b) {
        return -1;
    } else if (a > b) {
        return +1;
    } else {
        return 0;
    }
};

kukit.ut.SortedQueue.prototype.reset = function() {
    this.elements = new Array();
};

kukit.ut.SortedQueue.prototype.push = function(obj) {
    // Find the position of the object.
    var i = 0;
    while (i < this.elements.length && this.comparefunc(this.elements[i], obj) == -1) {
        i ++;
    }
    // and insert it there
    this.elements.splice(i, 0, obj);
};

kukit.ut.SortedQueue.prototype.pop = function() {
    // takes minimal element
    return this.elements.shift();
};

kukit.ut.SortedQueue.prototype.popn = function(n) {
    // takes first n minimal element
    return this.elements.splice(0, n);
};

kukit.ut.SortedQueue.prototype.empty = function() {
    return ! this.elements.length;
};

kukit.ut.SortedQueue.prototype.size = function() {
    return this.elements.length;
};

kukit.ut.SortedQueue.prototype.get = function(n) {
    return this.elements[n];
};

kukit.ut.SortedQueue.prototype.front = function() {
    return this.elements[0];
};

kukit.ut.evalBool = function(value, errname) {
    if (value == 'true' || value == 'True' || value == '1') {
        value = true;
    } else if (value == 'false' || value == 'False' || value == '0' || value == '') {
        value = false;
;;;     } else {
;;;         throw 'Bad boolean value "' + value + '" ' + errname;
    }
    return value;
};

kukit.ut.evalInt = function(value, errname) {
;;;     try {
        value = parseInt(value);
;;;     } catch(e) {
;;;         throw 'Bad integer value "' + value + '" ' + errname;
;;;     }
    return value;
};

kukit.ut.evalList = function(value, errname) {
;;;     try {
        // remove whitespace from beginning, end
        value = value.replace(/^ +/, '');
        //while (value && value.charAt(0) == ' ') {
        //    value = value.substr(1);
        //}
        value = value.replace(/ +$/, '');
        // do the splitting
        value = value.split(/ *, */);
;;;     } catch(e) {
;;;         throw 'Bad list value "' + value + '" ' + errname;
;;;     }
    return value;
};



/* 
* class TimerCounter
*
* for repeating or one time timing
*/
kukit.ut.TimerCounter = function(delay, func, restart) {
    this.delay = delay;
    this.func = func;
    if (typeof(restart) == 'undefined') {
        restart = false;
    }
    this.restart = restart;
    this.timer = null;
};

kukit.ut.TimerCounter.prototype.start = function() {
    if (this.timer) {
        ;;; kukit.E = 'Timer already started.';
        throw kukit.E;
    }
    var self = this;
    var func = function() {
        self.timeout();
    };
    this.timer = setTimeout(func, this.delay);
};

kukit.ut.TimerCounter.prototype.timeout = function() {
    // Call the event action
    this.func();
    // Restart the timer
    if (this.restart) {
        this.timer = null;
        this.start();
    }
};

kukit.ut.TimerCounter.prototype.clear = function() {
    if (this.timer) {
        window.clearTimeout(this.timer);
        this.timer = null;
    }
    this.restart = false;
};

/*
* class Scheduler
*/
kukit.ut.Scheduler = function(func) {
    this.func = func;
    this.timer = null;
    this.nextWake = null;
};

kukit.ut.Scheduler.prototype.setNextWake = function(ts) {
    // Sets wakeup time, null clears
    if (this.nextWake) {
        this.clear();
    }
    if (! ts) {
        return;
    }
    var now = (new Date()).valueOf();
    if (ts > now) {
        this.nextWake = ts;
        var self = this;
        var func = function() {
            self.timeout();
        };
        this.timer = setTimeout(func, ts - now);
    } else {
        // if in the past, run immediately
        this.func();
    }
};

kukit.ut.Scheduler.prototype.setNextWakeAtLeast = function(ts) {
    // Sets wakeup time, unless it would wake up later than the
    // currently set timeout. Null clears the timer.
    if (! ts || ! this.nextWake || ts < this.nextWake) {
        this.setNextWake(ts);
    } else {
        var now = (new Date()).valueOf();
        // XXX why compute now and not use it ?
    }
};

kukit.ut.Scheduler.prototype.timeout = function() {
    // clear the timer
    this.timer = null;
    this.nextWake = null;
    // Call the event action
    this.func();
};


kukit.ut.Scheduler.prototype.clear = function() {
    if (this.nextWake) {
        window.clearTimeout(this.timer);
        this.timer = null;
        this.nextWake = null;
    }
};

/* 
* class SerializeScheduler
*
* Scheduler for serializing bind and load procedures
*/
kukit.ut.SerializeScheduler = function() {
    this.items = [];
    this.lock = false;
};

kukit.ut.SerializeScheduler.prototype.addPre = function(func, remark) {
    this.items.push({func: func, remark: remark});
    this.execute();
};

kukit.ut.SerializeScheduler.prototype.addPost = function(func, remark) {
    this.items.unshift({func: func, remark: remark});
    this.execute();
};

kukit.ut.SerializeScheduler.prototype.execute = function() {
    if (! this.lock) {
        this.lock = true;
        while (true) {
            var item = this.items.pop();
            if (! item) {
                break;
            }
            ;;; kukit.log('Starting ' + item.remark);
            ;;; var ts_start = (new Date()).valueOf();
            try {
                item.func();
            } catch(e) {
                this.lock = false;
                throw e;
            }
            ;;; var ts_end = (new Date()).valueOf();
            ;;; kukit.log('Finished ' + item.remark + ' in ' + (ts_end - ts_start) + ' ms');
        }
        this.lock = false;
    }
};

/* Browser event binding */

/* extracted from Plone */
// cross browser function for registering event handlers
kukit.ut.registerEventListener = function(elem, event, func) {
    if (elem.addEventListener) {
        elem.addEventListener(event, func, false);
        return true;
    } else if (elem.attachEvent) {
        var result = elem.attachEvent("on"+event, func);
        return result;
    }
    // maybe we could implement something with an array
    return false;
};


/* collecting keys-values into a dict or into a tuple list */

kukit.ut.DictCollector = function() {
    this.result = {};
};

kukit.ut.DictCollector.prototype.add = function(key, value) {
    this.result[key] = value;
};

kukit.ut.TupleCollector = function() {
    this.result = [];
};

kukit.ut.TupleCollector.prototype.add = function(key, value) {
    this.result.push([key, value]);
};

