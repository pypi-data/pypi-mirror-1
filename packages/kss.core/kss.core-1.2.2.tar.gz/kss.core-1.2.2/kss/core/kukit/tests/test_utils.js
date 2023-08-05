/*
* Copyright (c) 2005-2006
* Authors:
*   Balazs Ree <ree@greenfinity.hu>
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

if (typeof(kukit) == "undefined") {
    var kukit = {};
}

kukit.UtilsTestCaseBase = function() {
   
    this.assertDictEquals = function(a, b, reason) {
        if (typeof(reason) == 'undefined') {
            reason = '';
        } else {
            reason += ', ';
        }
        for (var key in a) {
            this.assertNotEquals(typeof(b[key]), 'undefined', reason + 'key ' + key + ' missing from dict 2');
            this.assertEquals(a[key], b[key], reason + 'mismatch at key ' + key);
        }
        for (var key in b) {
            this.assertNotEquals(typeof(a[key]), 'undefined', reason + 'key ' + key + ' missing from dict 1');
            this.assertEquals(a[key], b[key], reason + 'mismatch at key ' + key);
        }
    };

    this.assertListEquals = function(a, b, reason) {
        if (typeof(reason) == 'undefined') {
            reason = '';
        } else {
            reason += ', ';
        }
        this.assertEquals(a.length, b.length, reason + 'lists of different length');
        for (var i=0; i<a.length; i++) {
            this.assertEquals('"' + a[i] + '"', '"' + b[i] + '"', reason + 'list values differ in position ' + i);
        }
    };
    
};

kukit.UtilsTestCaseBase.prototype = new TestCase;

kukit.UtilsTestCase = function() {
    this.name = 'kukit.UtilsTestCase';

    this.setUp = function() {
    };

    this.testFifoQueue = function() {
        // Test the fifo queue
        var q;

        q = new kukit.ut.FifoQueue();
        this.assertEquals(q.empty(), true);
        this.assertEquals(q.size(), 0);
        q.push(1);
        q.push(3);
        q.push(2);
        q.push(4);
        this.assertEquals(q.empty(), false);
        this.assertEquals(q.size(), 4);
        this.assertEquals(q.front(), 1);
        this.assertListEquals(q.elements, [1, 3, 2, 4]);
        this.assertEquals(q.pop(), 1);
        this.assertEquals(q.pop(), 3);
        this.assertEquals(q.pop(), 2);
        this.assertEquals(q.pop(), 4);
        this.assertEquals(q.empty(), true);
        this.assertEquals(q.size(), 0);
    };

    this.testSortedQueue = function() {
        // Test the sorted queue
        var q;

        q = new kukit.ut.SortedQueue();
        this.assertEquals(q.empty(), true);
        this.assertEquals(q.size(), 0);
        q.push(1);
        q.push(3);
        q.push(2);
        q.push(4);
        this.assertEquals(q.empty(), false);
        this.assertEquals(q.size(), 4);
        this.assertEquals(q.front(), 1);
        this.assertListEquals(q.elements, [1, 2, 3, 4]);
        this.assertEquals(q.pop(), 1);
        this.assertEquals(q.pop(), 2);
        this.assertEquals(q.pop(), 3);
        this.assertEquals(q.pop(), 4);
        this.assertEquals(q.empty(), true);
        this.assertEquals(q.size(), 0);

        // reverse order
        var comparefunc = function(a, b) {
            if (a < b) return +1;
            else if (a > b) return -1;
            else return 0;
        };
        q = new kukit.ut.SortedQueue(comparefunc);
        this.assertEquals(q.empty(), true);
        this.assertEquals(q.size(), 0);
        q.push(1);
        q.push(3);
        q.push(2);
        q.push(4);
        this.assertEquals(q.empty(), false);
        this.assertEquals(q.size(), 4);
        this.assertEquals(q.front(), 4);
        this.assertListEquals(q.elements, [4, 3, 2, 1]);
        this.assertEquals(q.pop(), 4);
        this.assertEquals(q.pop(), 3);
        this.assertEquals(q.pop(), 2);
        this.assertEquals(q.pop(), 1);
        this.assertEquals(q.empty(), true);
        this.assertEquals(q.size(), 0);

    };

    this.testEvalList = function() {
        var value = kukit.ut.evalList('');
        this.assertListEquals(value, ['']);
        value = kukit.ut.evalList('1');
        this.assertListEquals(value, ['1']);
        value = kukit.ut.evalList('1,2');
        this.assertListEquals(value, ['1', '2']);
        value = kukit.ut.evalList('1, 2');
        this.assertListEquals(value, ['1', '2']);
        value = kukit.ut.evalList('1, 2 ');
        this.assertListEquals(value, ['1', '2']);
        value = kukit.ut.evalList(' 1, 2');
        this.assertListEquals(value, ['1', '2']);
        value = kukit.ut.evalList('  1  ,  2  ');
        this.assertListEquals(value, ['1', '2']);
    }

};
    
kukit.UtilsTestCase.prototype = new kukit.UtilsTestCaseBase;

if (typeof(testcase_registry) != 'undefined') {
    testcase_registry.registerTestCase(kukit.UtilsTestCase, 'kukit.UtilsTestCase');
}
