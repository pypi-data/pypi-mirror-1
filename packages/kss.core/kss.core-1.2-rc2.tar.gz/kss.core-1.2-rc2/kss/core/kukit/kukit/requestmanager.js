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

/* Request manager */

kukit.rm = {};

/* Generation of an integer uid on request objects
*/

kukit.rm._rid = 0;

/*
* class RequestItem
*
* Request item. Encapsulates the sendout function and data.
*/
kukit.rm.RequestItem = function(sendHook, url, timeoutHook, timeout, now) {
    if (typeof(now) == 'undefined') {
        now = (new Date()).valueOf();
    }
    this.sent = now;
    this.expire = now + timeout;
    this.handled = false;
    this.sendHook = sendHook;
    this.url = url;
    this.timeoutHook = timeoutHook;
    // Generate a RID. Due to timeouting, we have enough
    // of these for not to overlap ever.
    this.rid = kukit.rm._rid;
    kukit.rm._rid ++;
    if (kukit.rm._rid >= 10000000000) {
        kukit.rm._rid = 0;
    }
};

kukit.rm.RequestItem.prototype.callTimeoutHook = function() {
    // Calls the timeout hook for this item
    if (this.timeoutHook) {
        this.timeoutHook(this);
    }
};

kukit.rm.RequestItem.prototype.setReceivedCallback = function(func) {
    // Sets the received callback function. It will be
    // called with the item as first parameter.
    this._receivedCallback = func;
};

kukit.rm.RequestItem.prototype.receivedResult = function(now) {
    // This is called when the result response has arrived. It
    // returns a booolean value, if this is false, the caller
    // must give up processing the result that has been timed
    // out earlier.
    var result = this._receivedCallback(this, now);
    this._receivedCallback = null;
    return result;
}; 

/* 
* class TimerQueue
*
* the send queue. This handles timeouts, and executes
* a callback for timed out items.
* Callback is called with the request item as parameter.
*/

kukit.rm.TimerQueue = function(callback) {
    this.callback = callback;
    this.queue = new kukit.ut.SortedQueue(this._sentSort);
    this.nr = 0;
};

kukit.rm.TimerQueue.prototype._sentSort = function(a, b) {
    // sorting of the sent queue, by expiration
    if (a.expire < b.expire) return -1;
    else if (a.expire > b.expire) return +1;
    else return 0;
};

kukit.rm.TimerQueue.prototype.push = function(item) {
    // push a given slot
    this.queue.push(item);
    this.nr += 1;
};

kukit.rm.TimerQueue.prototype.pop = function(item) {
    // pop a given slot, return true if it was valid,
    // return false if it was already handled by timeout.
    // An object can be popped more times!
    if (typeof(item) == 'undefined' || item.handled) {
        return false;
    } else {
        item.handled = true;
        this.nr -= 1;
        return true;
    }
};

kukit.rm.TimerQueue.prototype.handleExpiration = function(now) {
    if (typeof(now) == 'undefined') {
        now = (new Date()).valueOf();
    }
    var to;
    for (to=0; to<this.queue.size(); to++) {
        var item = this.queue.get(to);
        if (! item.handled) {
            if (item.expire > now) {
                break;
            } else {
                // call the callback for this element
                item.handled = true;
                this.nr -= 1;
                this.callback(item);
            }
        }
    }
    // remove the elements from the queue
    this.queue.popn(to);
    // Returns when the next element will expire.
    var front = this.queue.front();
    var next_expire = null;
    if (front) {
        next_expire = front.expire;
    }
    return next_expire;
};

/* 
* class RequestManager
*/
kukit.rm.RequestManager = function (name, maxNr, schedulerClass) {
    // schedulerClass is mainly provided for debugging...
    this.waitingQueue = new kukit.ut.FifoQueue();
    this.sentNr = 0;
    var self = this;
    var timeoutItem = function(item) {
       self.timeoutItem(item);
    };
    this.timerQueue = new kukit.rm.TimerQueue(timeoutItem);
    if (typeof(name) == 'undefined') {
        name = null;
    }
    this.name = name;
    var namestr = '';
    if (name != null) {
        namestr = '[' + name + '] ';
        }
    this.namestr = namestr;
    if (typeof(maxNr) != 'undefined' && maxNr != null) {
        this.maxNr = maxNr;
    }
    // sets the timeout scheduler
    var checkTimeout = function() {
       self.checkTimeout();
    };
    if (typeof(schedulerClass) == 'undefined') {
        schedulerClass = kukit.ut.Scheduler;
    }
    this.timeoutScheduler = new schedulerClass(checkTimeout);
    this.spinnerEvents = {'off': [], 'on': []};
    this.spinnerState = false;
};

// sending timeout in millisecs
kukit.rm.RequestManager.prototype.sendingTimeout = 8000;

// max request number
kukit.rm.RequestManager.prototype.maxNr = 4;

;;; kukit.rm.RequestManager.prototype.getInfo = function() {
;;;     return '(RQ: ' + this.sentNr + ' OUT, ' + this.waitingQueue.size() + ' WAI)';
;;; };

;;; kukit.rm.RequestManager.prototype.log = function(txt) {
;;;     kukit.logDebug('RequestManager ' + this.namestr + txt + ' ' + this.getInfo());
;;; };

kukit.rm.RequestManager.prototype.setSpinnerState = function(newState) {
    if (this.spinnerState != newState) {
        this.spinnerState = newState;
        // Call the registered spinner events for this state
        var events = this.spinnerEvents[newState ? 'on' : 'off'];
        for (var i=0; i<events.length; i++) {
            events[i]();
        }
    }
};

kukit.rm.RequestManager.prototype.pushWaitingRequest = function(item, now) {
    this.waitingQueue.push(item);
    // Set the timeout
    this.checkTimeout(now);
};

kukit.rm.RequestManager.prototype.popWaitingRequest = function() {
    var q = this.waitingQueue;
    // pop handled elements, we don't send them out at all
    while (! q.empty() && q.front().handled) {
        q.pop();
    }
    // return the element, or null if no more waiting!
    if (! q.empty()) {
        return q.pop();
    } else {
        return null;
    }
};

kukit.rm.RequestManager.prototype.pushSentRequest = function(item, now) {
    this.sentNr += 1;
    ;;; this.log('Notify server ' + item.url + ', rid=' + item.rid);
    // Set the spinner state
    this.setSpinnerState(true);
    // Set the timeout
    this.checkTimeout(now);
    // Wrap up the callback func. It will be called
    // with the item as first parameter.
    var self = this;
    var func = function(item, now) {
        return self.receiveItem(item, now);
    };
    item.setReceivedCallback(func);
    // Call the function
    item.sendHook(item);
};

kukit.rm.RequestManager.prototype.checkTimeout = function(now) {
    var nextWake = this.timerQueue.handleExpiration(now);
    if (nextWake) {
        // To make sure, add 50ms to the nextwake
        nextWake += 50;
        // do the logging
        //var now = (new Date()).valueOf();
        //this.log('Next timeout check in: ' + (nextWake - now));
    } else {
        ;;; this.log('Timeout checking suspended until the next requests');
        // Set the spinner state
        this.setSpinnerState(false);
    }
    // do the scheduling
    this.timeoutScheduler.setNextWakeAtLeast(nextWake);
};

kukit.rm.RequestManager.prototype.popSentRequest = function(item) {
    var success = this.timerQueue.pop(item);
    // We remove both to be processed, and timed out requests from the queue.
    // This means: possibly more physical requests are out, but this
    // is a better strategy in order not to hog the queue infinitely.
    this.sentNr -= 1;
    return success;
};

kukit.rm.RequestManager.prototype.isSentRequestQueueFull = function() {
    return (this.sentNr >= this.maxNr);
};

kukit.rm.RequestManager.prototype.receivedResult = function(item, now) {
    // called automatically when the result gets processed.
    // Mark that we have one less request out.
    var success = this.popSentRequest(item);
    // Independently of the success, this is the moment when we may
    // want to send out another item.
    var waiting = this.popWaitingRequest();
    if (waiting != null) {
        // see if we can send another request in place of the received one
        // request is waiting, send it.
        ;;; this.log('Dequeue server notification at ' + waiting.url + ', rid=' + waiting.rid);
        this.pushSentRequest(waiting, now);
    } else {
    //    this.log("Request queue empty.");
        // Set the spinner state
        this.setSpinnerState(false);
    }
    return success;
};


kukit.rm.RequestManager.prototype.receiveItem = function(item, now) {
    // calls result processing
    var success = this.receivedResult(item, now);
    ;;; if (success) {
    ;;;     this.log('Received result with rid=' + item.rid);
    ;;; } else {
    ;;;     this.log('Received timed out result rid=' + item.rid + ', to be ignored');
    ;;; }
    return success;
};

kukit.rm.RequestManager.prototype.timeoutItem = function(item) {
    /* Time out this item. */
    ;;; this.log('Timed out request rid=' + item.rid);
    // Call the timeout hook on the item
    item.callTimeoutHook();
};

/* request manager notification API */

kukit.rm.RequestManager.prototype.notifyServer = function(sendHook, url, timeoutHook, timeout, now) {
    // url is only for the logging
    // sendHook is the function that actually sends out the request.
    // sendHook will be called with one parameter: the 'item' array.
    // The sender mechanism must make sure to call item.receivedResult()
    // when it received the response.
    // Based on the return value of receivedResult(), the result processing
    // may go on or must be broken. If the return value is false, the
    // results must NOT be processed: this means that we have already
    // timed out the request by that time.
    // timeoutHook: can specify the timeouthook for this request. Setting it to null
    // disables it. This will be called with the 'item' as a parameter as well.
    if (typeof(timeout) == 'undefined') {
        // Default value of timeout
        timeout = this.sendingTimeout;
    }
    var item = new kukit.rm.RequestItem(sendHook, url, timeoutHook, timeout, now);
    // Start timing the item immediately
    this.timerQueue.push(item);
    if (! this.isSentRequestQueueFull()) {
        // can be sent if we are not over the limit.
        this.pushSentRequest(item, now);
    } else {
        this.pushWaitingRequest(item, now);
        ;;; this.log('Queue server notification at ' + item.url + ', rid=' + item.rid);
    }
};

kukit.rm.RequestManager.prototype.registerSpinnerEvent = function(func, state) {
    this.spinnerEvents[state ? 'on' : 'off'].push(func);
};

