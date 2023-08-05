/*
* Copyright (c) 2005-2006
* Authors:
*   Martin Heidegger <mastakaneda@gmail.com>
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

kukit.KssParserTestCase = function() {
    this.name = 'kukit.KssParserTestCase';

    this.setUp = function() {
    };
    
    this.assertKssParmValueEquals = function(a, b, reason) {
        if (typeof(reason) == 'undefined') {
            reason = '';
        } else {
            reason += ', ';
        }
        this.assertEquals(a.isMethod, b.isMethod, reason + 'different types');
        if (! a.isMethod) {
            this.assertEquals(a.txt, b.txt, reason + 'text mismatch' );
        } else {
            this.assertEquals(a.methodname, b.methodname, reason + 'methodname mismatch');
            this.assertListEquals(a.args, b.args, reason + 'args mismatch');
        }
    };

    this.assertKssParmEquals = function(a, b, reason) {
        if (typeof(reason) == 'undefined') {
            reason = '';
        } else {
            reason += ', ';
        }
        for (var key in a) {
            this.assertNotEquals(typeof(b[key]), 'undefined', reason + 'key ' + key + ' missing from parms 2');
            this.assertKssParmValueEquals(a[key], b[key], 'mismatch at parm key ' + key);
        }
        for (var key in b) {
            this.assertNotEquals(typeof(a[key]), 'undefined', reason + 'key ' + key + ' missing from parms 1');
            this.assertKssParmValueEquals(a[key], b[key], reason + 'mismatch at parm key ' + key);
        }
    };
 
    this.testPropvalueInMethod = function() {
        // Parsing prop values (no methods allowed)
        var txt= "apple;";
        var src = new kukit.tk.Cursor(txt);
        var parser = new kukit.kssp.PropValueInMethod(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.txt, 'apple');

        txt= "'a  string';";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.PropValueInMethod(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.txt, 'a  string');

        txt= '"a  string";';
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.PropValueInMethod(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.txt, 'a  string');

        txt= '"a  \\"string";';
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.PropValueInMethod(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.txt, 'a  "string');

        txt= " /* valid */ 'a  string' /* here*/ /*and*/ /*there*/;";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.PropValueInMethod(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.txt, 'a  string');

        txt= " in /* valid */ 'a  string';";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.PropValueInMethod, src, null, true, 'Excess characters before the string in property value');

        txt= " 'a  string' trashy;";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.PropValueInMethod, src, null, true, 'Excess characters after the property value');

        txt= " 'a  string' trashy \"trishy\";";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.PropValueInMethod, src, null, true, 'Excess characters after the property value');

        // multiword not ok
        txt= "b   c";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.PropValueInMethod, src, null, true,
            'Property value must be one word', 5);

        txt= "  apples and   oranges   ;";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.PropValueInMethod, src, null, true,
            'Property value must be one word', 25);

        txt= " /* comments; */ apples and  /* more comments and*/ oranges   ;";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.PropValueInMethod, src, null, true,
            'Property value must be one word', 62);

        // in string, multiword ok even in method
        txt= "'b   c' ";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.PropValueInMethod(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.txt, 'b   c');
        this.assertEquals(parser.parms, null);

        // Not ok
        txt= "a'b c'";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.PropValueInMethod, src, null, true,
            'Excess characters before the string in property value', 6);

        // Not ok
        txt= "'a''b c'";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.PropValueInMethod, src, null, true,
            'Excess characters after the property value', 8);

    };

    this.testPropValue = function() {
        // Parsing property values 

        var txt= "b";
        var src = new kukit.tk.Cursor(txt);
        var parser = new kukit.kssp.PropValue(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.value.isMethod, false);
        this.assertEquals(parser.value.txt, 'b');

        // multiword ok
        txt= "b   c";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.PropValue(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.value.isMethod, false);
        this.assertEquals(parser.value.txt, 'b c');

        txt= "  apples and   oranges   ;";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.PropValue(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.value.isMethod, false);
        this.assertEquals(parser.value.txt, 'apples and oranges');

        txt= " /* comments; */ apples and  /* more comments and*/ oranges   ;";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.PropValue(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.value.isMethod, false);
        this.assertEquals(parser.value.txt, 'apples and oranges');

        // params ok
        txt= "formVar(x, y) ";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.PropValue(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.value.isMethod, true);
        this.assertEquals(parser.value.methodname, 'formVar');
        this.assertListEquals(parser.value.args, ['x', 'y']);

        // params ok
        txt= "formVar(x, y)";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.PropValue(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.value.isMethod, true);
        this.assertEquals(parser.value.methodname, 'formVar');
        this.assertListEquals(parser.value.args, ['x', 'y']);

        //ok
        txt= "   formVar   (x, y)";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.PropValue(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.value.isMethod, true);
        this.assertEquals(parser.value.methodname, 'formVar');
        this.assertListEquals(parser.value.args, ['x', 'y']);

        txt= " a formVar(x, y)";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.PropValue, src, null, true,
            'Method property value must have a one-word method name', 16);

        txt= " 'formVar'(x, y)";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.PropValue, src, null, true,
            'Excess characters after the property value', 16);

        txt= "formVar(x, y) xxx";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.PropValue, src, null, true,
            'Excess characters after the property value', 17);
    };
    
    this.testPropValueInPseudo = function() {
        // Parsing prop values in pseudo (no methods allowed)

        var txt= "b";
        var src = new kukit.tk.Cursor(txt);
        var parser = new kukit.kssp.PropValueInPseudo(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.value.methodname, 'b');

        // multiword ok but does not finish
        txt= "b   c";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.PropValueInPseudo(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(src.pos, 1);
        this.assertEquals(parser.value.methodname, 'b');

        // space ok but does not finish
        txt= " b";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.PropValueInPseudo(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(src.pos, 0);
        this.assertEquals(parser.value.methodname, '');

        // ok, does not finish
        txt= "apples/* more comments and*/";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.PropValueInPseudo(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(src.pos, 6);
        this.assertEquals(parser.value.methodname, 'apples');

        // params ok
        txt= "click(x)";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.PropValueInPseudo(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.value.methodname, 'click');
        this.assertListEquals(parser.value.args, ['x']);

        // more then 1 args not ok (but we check it only from kss selector)
        //txt= "drag(x, y)";
        //src = new kukit.tk.Cursor(txt);

        // not ok but we don't parse an error
        //txt= "'drag'(x)";
        //src = new kukit.tk.Cursor(txt);
        //this.assertParsingError(kukit.kssp.PropValueInPseudo, src, null, true,
        //    'Excess characters after the property value', 16);

    };

    this.testMethodArgs = function() {
        // Parsing method args
        var txt= "(a, b)";
        var src = new kukit.tk.Cursor(txt);
        var parser = new kukit.kssp.MethodArgs(src, kukit.kssp.openparent, true);
        this.assertEquals(parser.finished, true);
        this.assertListEquals(parser.args, ['a', 'b']);
    
        txt= "('a',  /* to annoy you */ \"b\")";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.MethodArgs(src, kukit.kssp.openparent, true);
        this.assertEquals(parser.finished, true);
        this.assertListEquals(parser.args, ['a', 'b']);

        txt= "(' a    multi', /* to annoy you */ \"b    multi \")";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.MethodArgs(src, kukit.kssp.openparent, true);
        this.assertEquals(parser.finished, true);
        this.assertListEquals(parser.args, [' a    multi','b    multi ']);

        txt= "('a', /*comment*/  /* to annoy you */ \"b\")";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.MethodArgs(src, kukit.kssp.openparent, true);
        this.assertEquals(parser.finished, true);
        this.assertListEquals(parser.args, ['a', 'b']);

        txt= "(a, b, )";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.MethodArgs(src, kukit.kssp.openparent, true);
        this.assertEquals(parser.finished, true);
        this.assertListEquals(parser.args, ['a', 'b']);

        txt= "(a, b c )";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.MethodArgs, src, kukit.kssp.openparent, true,
            'Argument value must be one word', 9);

        txt= "(a, b 'x' )";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.MethodArgs, src, kukit.kssp.openparent, true,
            'Expected [comma], found [string]', 11);

    };

    this.testKssSelector = function() {
        // Parsing event selector params
        var txt= "a:drag(hello)";
        var src = new kukit.tk.Cursor(txt);
        var parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.kssSelector.isEventSelector, true);
        this.assertEquals(parser.kssSelector.css, 'a');
        this.assertEquals(parser.kssSelector.name, 'drag');
        this.assertEquals(parser.kssSelector.namespace, null);
        this.assertEquals(parser.kssSelector.id, 'hello');

        var txt= "a:dnd-drag(hello)";
        var src = new kukit.tk.Cursor(txt);
        var parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.kssSelector.isEventSelector, true);
        this.assertEquals(parser.kssSelector.css, 'a');
        this.assertEquals(parser.kssSelector.name, 'drag');
        this.assertEquals(parser.kssSelector.namespace, 'dnd');
        this.assertEquals(parser.kssSelector.id, 'hello');

        var txt= "a:dnd-drag-toomuch(hello)";
        var src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'Kss event selector must be name or namespace-name but no more dashes, "dnd-drag-toomuch"', 25);

        // maybe in std css space is not allowed in the parents,
        // but we tolerate it
        txt= "  a div#id:drag( hello)";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.kssSelector.isEventSelector, true);
        this.assertEquals(parser.kssSelector.css, '  a div#id');
        this.assertEquals(parser.kssSelector.name, 'drag');
        this.assertEquals(parser.kssSelector.namespace, null);
        this.assertEquals(parser.kssSelector.id, 'hello');

        // We do not allow space here 
        txt= "  a div#id:drag   (hello)";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'Kss event selector must end with an event qualifier :event or :event(id)', 25);

        // We do not allow space here
        txt= "  a div#id: drag(hello)";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'Kss event selector must end with an event qualifier :event or :event(id)', 23);

        txt= "a div#id:drop ";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.kssSelector.isEventSelector, true);
        this.assertEquals(parser.kssSelector.css, 'a div#id');
        this.assertEquals(parser.kssSelector.name, 'drop');
        this.assertEquals(parser.kssSelector.namespace, null);
        this.assertEquals(parser.kssSelector.id, null);

        txt= "a div.class:drop ";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.kssSelector.isEventSelector, true);
        this.assertEquals(parser.kssSelector.css, 'a div.class');
        this.assertEquals(parser.kssSelector.name, 'drop');
        this.assertEquals(parser.kssSelector.namespace, null);
        this.assertEquals(parser.kssSelector.id, null);

        txt= "a:click ";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.kssSelector.isEventSelector, true);
        this.assertEquals(parser.kssSelector.css, 'a');
        this.assertEquals(parser.kssSelector.name, 'click');
        this.assertEquals(parser.kssSelector.namespace, null);
        this.assertEquals(parser.kssSelector.id, null);

        // two params: not allowed
        txt= "a:drop('hello', bello)";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'Kss pseudo value must not have more then one parameters', 22);

        // zero params: not std css but tolerated 
        txt= "a:drop()";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'Kss event selector must end with an event qualifier :event or :event(id)', 8);

        txt= "   (hello)";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'Kss event selector must end with an event qualifier :event or :event(id)', 10);

        txt= "hello  ('bello')";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'Kss event selector must end with an event qualifier :event or :event(id)', 16);

        txt= "a:lang(hu)  (hello)";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'Kss event selector must end with an event qualifier :event or :event(id)', 19);

        txt= "a:lang(hu) b (hello)";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'Kss event selector must end with an event qualifier :event or :event(id)', 20);

        // A valid attr selector in the css selector part.
        txt= "a[href=hello].class:lang(hu) div#id:click ";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.kssSelector.isEventSelector, true);
        this.assertEquals(parser.kssSelector.css, "a[href=hello].class:lang(hu) div#id");
        this.assertEquals(parser.kssSelector.name, 'click');
        this.assertEquals(parser.kssSelector.namespace, null);
        this.assertEquals(parser.kssSelector.id, null);

        txt= "a[href=hello].class:lang(hu) div#id:drop(hello) ";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.kssSelector.isEventSelector, true);
        this.assertEquals(parser.kssSelector.css, "a[href=hello].class:lang(hu) div#id");
        this.assertEquals(parser.kssSelector.name, 'drop');
        this.assertEquals(parser.kssSelector.namespace, null);
        this.assertEquals(parser.kssSelector.id, 'hello');

        txt= "   a:lang(hu) click ";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'Kss event selector must end with an event qualifier :event or :event(id)', 20);

        // Spaces in the end
        txt= "   a:lang(hu, uh) b:click    ";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.kssSelector.isEventSelector, true);
        this.assertEquals(parser.kssSelector.css, "   a:lang(hu, uh) b");
        this.assertEquals(parser.kssSelector.name, 'click');
        this.assertEquals(parser.kssSelector.namespace, null);
        this.assertEquals(parser.kssSelector.id, null);

        // Comment in the end
        txt= "   a:lang(hu, uh) b:click/*comment here*/";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.kssSelector.isEventSelector, true);
        this.assertEquals(parser.kssSelector.css, "   a:lang(hu, uh) b");
        this.assertEquals(parser.kssSelector.name, 'click');
        this.assertEquals(parser.kssSelector.namespace, null);
        this.assertEquals(parser.kssSelector.id, null);

        // Should be ok.
        txt= "a:lang(hu)/*comment here*/b:click ";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.kssSelector.isEventSelector, true);
        this.assertEquals(parser.kssSelector.css, "a:lang(hu)/*comment here*/b");
        this.assertEquals(parser.kssSelector.name, 'click');
        this.assertEquals(parser.kssSelector.namespace, null);
        this.assertEquals(parser.kssSelector.id, null);
  
        // Should be ok.
        txt= "a:lang(hu) click/*comment here*/b:clack ";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.kssSelector.isEventSelector, true);
        this.assertEquals(parser.kssSelector.css, "a:lang(hu) click/*comment here*/b");
        this.assertEquals(parser.kssSelector.name, 'clack');
        this.assertEquals(parser.kssSelector.namespace, null);
        this.assertEquals(parser.kssSelector.id, null);

        txt= "a:click:clack ";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'Kss event selector must end with an event qualifier :event or :event(id)', 14);

        txt= "a:click    :clack ";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'In kss event selector no space can be before the colon', 18);

        txt= "a:click/*comment */:clack ";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'Kss event selector must end with an event qualifier :event or :event(id)', 26);

        txt= "click/*comment here*/:clack ";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'Kss event selector must end with an event qualifier :event or :event(id)', 28);

        txt= "/*comment here*/click:clack ";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);

        txt= " no-document:click(hello)";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.kssSelector.isEventSelector, true);
        this.assertEquals(parser.kssSelector.css, " no-document");
        this.assertEquals(parser.kssSelector.name, 'click');
        this.assertEquals(parser.kssSelector.namespace, null);
        this.assertEquals(parser.kssSelector.id, "hello");

            
        // Event method selectors

        txt= " document:click(hello)  ";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.kssSelector.isMethodSelector, true);
        this.assertEquals(parser.kssSelector.css, 'document');
        this.assertEquals(parser.kssSelector.name, 'click');
        this.assertEquals(parser.kssSelector.namespace, null);
        this.assertEquals(parser.kssSelector.id, 'hello');

        txt= " document:native-click(hello)  ";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.kssSelector.isMethodSelector, true);
        this.assertEquals(parser.kssSelector.css, 'document');
        this.assertEquals(parser.kssSelector.name, 'click');
        this.assertEquals(parser.kssSelector.namespace, 'native');
        this.assertEquals(parser.kssSelector.id, 'hello');
 
        txt= "document";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'Kss event selector must end with an event qualifier :event or :event(id)', 8);

        txt= "document: ";
        src = new kukit.tk.Cursor(txt);
        this.assertParsingError(kukit.kssp.KssSelector, src, null, true,
            'Kss event selector must have a one-word name after the colon', 10);

        // also, "behaviour:" works
        txt= " behaviour:click(hello)  ";
        src = new kukit.tk.Cursor(txt);
        parser = new kukit.kssp.KssSelector(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.kssSelector.isMethodSelector, true);
        this.assertEquals(parser.kssSelector.css, 'behaviour');
        this.assertEquals(parser.kssSelector.name, 'click');
        this.assertEquals(parser.kssSelector.namespace, null);
        this.assertEquals(parser.kssSelector.id, 'hello');

    }
 
    this.testEmptyDoc = function() {
        // unexpected eof handling 

        var txt= "";
        var src = new kukit.tk.Cursor(txt);
        var parser = new kukit.kssp.Document(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.eventRules.length, 0);

        // In particular, this should not raise unexpected eof.
        var txt= "/*xxx*/";
        var src = new kukit.tk.Cursor(txt);
        var parser = new kukit.kssp.Document(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.eventRules.length, 0);
    };

    this.testFull = function() {
        // Basic parsing test
        var txt= ""
            +"/* a long\n"
            +"** comment\n"
            +"*/\n"
            +"\n"
            +"#calendar-previous a:click {\n"
            +"   action-server : kukitresponse/kukitGetPreviousMonth;\n"
            +"}\n"
            +"div#update-area:timeout {\n"
            +"   evt-timeout-delay: 2000; \n"
            +"   action-server: getCurrentTime;\n"
            +"   getCurrentTime-effect: fade; \n"
            +"}\n"
            +"#calendar-previous a:click {\n"
            +"   action-server: 'kukitresponse/kukitGetPreviousMonth' /* place comment here*/;\n"
            +"}\n"
            +"#calendar-previous a:click {\n"
            +"   action-server : kukitGetPreviousMonth /* place comment here*/;\n"
            +"   kukitGetPreviousMonth-member: formVar(edit, 'f_member');\n"
            +"}\n"
            +"#calendar-previous a:dnd-drag(shelve) {\n"
            +"   action-server : whatever\n"
            +"}\n"
            +"#button-one:annoyClicker-click(annoy-me) {\n"
            +"   action-server:     clickedButton;\n"
            +"   clickedButton-id:  nodeAttr(id);\n"
            +"}\n"
            +"document:annoy(annoyMe) {\n"
            +"   action-client:    alert;\n"
            +'   alert-message:    "You are an idiot! Ha ha ha. (But just keep on trying...)";\n'
            +"}\n"
            +"document:annoyClicker-annoy(annoyMe) {\n"
            +"   action-client:    alert;\n"
            +'   alert-message:       "You are an idiot! Ha ha ha. (But just keep on trying...)";\n'
            +"}\n"
            +"div#update-area:timeout {\n"
            +"   evt-timeout-delay: 2000; \n"
            +"   action-server: getCurrentTime;\n"
            +"   getCurrentTime-effect: fade; \n"
            +"   action-client:    log;\n"
            +'   log-message:    "Logging";\n'
            +"}\n"
            +"document:annoyClicker-annoy(annoyMe) {\n"
            +"   evt-annoyClicker-annoy-preventdefault:   true;\n"
            +"   action-client:    namespaced-alert;\n"
            +'   namespaced-alert-message:       "You are an idiot! Ha ha ha. (But just keep on trying...)";\n'
            +"}\n";

        var src = new kukit.tk.Cursor(txt);

        // XXX TODO change comments
        
        var parser = new kukit.kssp.Document(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.eventRules.length, 10);
        var rule;
        var action;

        // rule 0
            // #calendar-previous a:click {
            //   kss-action : kukitresponse/kukitGetPreviousMonth;
            // }
        rule = parser.eventRules[0];
        this.assertDictEquals(rule.parms, {});
        this.assertEquals(rule.kss_selector.isEventSelector, true);
        this.assertEquals(rule.kss_selector.css,  '#calendar-previous a');
        this.assertEquals(rule.kss_selector.name,  'click');
        this.assertEquals(rule.kss_selector.namespace,  null);
        this.assertEquals(rule.kss_selector.id,  null);
        action = rule.actions.content['kukitresponse/kukitGetPreviousMonth'];
        this.assertEquals(action.type, 'S');
        this.assertEquals(action.name, 'kukitresponse/kukitGetPreviousMonth');
        this.assertEquals(action.error, null);
        this.assertKssParmEquals(action.parms, {});

        // rule 1
            // div#update-area:timeout {
            //   evt-timeout-delay: 2000;
            //   effect: fade;
            //   kss-action: getCurrentTime;
            // }
        rule = parser.eventRules[1];
        this.assertDictEquals(rule.parms, {'delay': '2000'});
        this.assertEquals(rule.kss_selector.isEventSelector, true);
        this.assertEquals(rule.kss_selector.css,  'div#update-area');
        this.assertEquals(rule.kss_selector.name,  'timeout');
        this.assertEquals(rule.kss_selector.namespace,  null);
        this.assertEquals(rule.kss_selector.id,  null);
        action = rule.actions.content['getCurrentTime'];
        this.assertEquals(action.type, 'S');
        this.assertEquals(action.name, 'getCurrentTime');
        this.assertEquals(action.error, null);
        this.assertKssParmEquals(action.parms, {
                'effect': new kukit.rd.KssTextValue('fade')
            });
        
        // rule 2
            // #calendar-previous a:click {
            //   kss-action : 'kukitresponse/kukitGetPreviousMonth' /* place comment here*/;
            // }
        rule = parser.eventRules[2];
        this.assertDictEquals(rule.parms, {});
        this.assertEquals(rule.kss_selector.css,  '#calendar-previous a');
        this.assertEquals(rule.kss_selector.isEventSelector, true);
        this.assertEquals(rule.kss_selector.name,  'click');
        this.assertEquals(rule.kss_selector.namespace,  null);
        this.assertEquals(rule.kss_selector.id,  null);
        action = rule.actions.content['kukitresponse/kukitGetPreviousMonth'];
        this.assertEquals(action.type, 'S');
        this.assertEquals(action.name, 'kukitresponse/kukitGetPreviousMonth');
        this.assertEquals(action.error, null);
        this.assertKssParmEquals(action.parms, {});

        // rule 3
            // #calendar-previous a:click {
            //   kss-action : 'kukitresponse/kukitGetPreviousMonth' /* place comment here*/;
            //   member: formVar(edit, 'f_member');
            // }
        rule = parser.eventRules[3];
        this.assertDictEquals(rule.parms, {});
        this.assertEquals(rule.kss_selector.css,  '#calendar-previous a');
        this.assertEquals(rule.kss_selector.isEventSelector, true);
        this.assertEquals(rule.kss_selector.name,  'click');
        this.assertEquals(rule.kss_selector.namespace,  null);
        this.assertEquals(rule.kss_selector.id,  null);
        action = rule.actions.content['kukitGetPreviousMonth'];
        this.assertEquals(action.type, 'S');
        this.assertEquals(action.name, 'kukitGetPreviousMonth');
        this.assertEquals(action.error, null);
        this.assertKssParmEquals(action.parms, {
                'member': new kukit.rd.KssMethodValue('formVar', ['edit', 'f_member'])
            });
         
        // rule 4
            // #calendar-previous a:dnd-drag(shelve) {
            //   kss-action : whatever
            // }
        rule = parser.eventRules[4];
        this.assertDictEquals(rule.parms, {});
        this.assertEquals(rule.kss_selector.css,  '#calendar-previous a');
        this.assertEquals(rule.kss_selector.isEventSelector, true);
        this.assertEquals(rule.kss_selector.name,  'drag');
        this.assertEquals(rule.kss_selector.namespace,  'dnd');
        this.assertEquals(rule.kss_selector.id,  'shelve');
        action = rule.actions.content['whatever'];
        this.assertEquals(action.type, 'S');
        this.assertEquals(action.name, 'whatever');
        this.assertEquals(action.error, null);
        this.assertKssParmEquals(action.parms, {
            });
 
        // rule 5
            //#button-one:annoyClicker-click(annoyMe) {
            //   kss-action:     clickedButton;
            //   id:             nodeAttr(id);
            //}
        rule = parser.eventRules[5];
        this.assertDictEquals(rule.parms, {});
        this.assertEquals(rule.kss_selector.css,  '#button-one');
        this.assertEquals(rule.kss_selector.isEventSelector, true);
        this.assertEquals(rule.kss_selector.name,  'click');
        this.assertEquals(rule.kss_selector.namespace,  'annoyClicker');
        this.assertEquals(rule.kss_selector.id,  'annoy-me');
        action = rule.actions.content['clickedButton'];
        this.assertEquals(action.type, 'S');
        this.assertEquals(action.name, 'clickedButton');
        this.assertEquals(action.error, null);
        this.assertKssParmEquals(action.parms, {
                'id': new kukit.rd.KssMethodValue('nodeAttr', ['id'])
            });

        // rule 6
            // document:annoy(annoyMe) {
            //   kss-action:    alert;
            //   message:       "You are an idiot! Ha ha ha. (But just keep on trying...)";
            //}
        rule = parser.eventRules[6];
        this.assertDictEquals(rule.parms, {});
        this.assertEquals(rule.kss_selector.css, 'document');
        this.assertEquals(rule.kss_selector.isMethodSelector, true);
        this.assertEquals(rule.kss_selector.name, 'annoy');
        this.assertEquals(rule.kss_selector.namespace, null);
        this.assertEquals(rule.kss_selector.id, 'annoyMe');
        action = rule.actions.content['alert'];
        this.assertEquals(action.type, 'C');
        this.assertEquals(action.name, 'alert');
        this.assertEquals(action.error, null);
        this.assertKssParmEquals(action.parms, {
                'message': new kukit.rd.KssTextValue( "You are an idiot! Ha ha ha. (But just keep on trying...)")
            });

        // rule 7
            // document:annoyClicker-annoy(annoyMe) {
            // annoy#annoy-me {
            //   kss-action:    alert;
            //   message:       "You are an idiot! Ha ha ha. (But just keep on trying...)";
            //}
        rule = parser.eventRules[7];
        this.assertDictEquals(rule.parms, {});
        this.assertEquals(rule.kss_selector.css, 'document');
        this.assertEquals(rule.kss_selector.isMethodSelector, true);
        this.assertEquals(rule.kss_selector.name, 'annoy');
        this.assertEquals(rule.kss_selector.namespace, 'annoyClicker');
        this.assertEquals(rule.kss_selector.id, 'annoyMe');
        action = rule.actions.content['alert'];
        this.assertEquals(action.type, 'C');
        this.assertEquals(action.name, 'alert');
        this.assertEquals(action.error, null);
        this.assertKssParmEquals(action.parms, {
                'message': new kukit.rd.KssTextValue( "You are an idiot! Ha ha ha. (But just keep on trying...)")
            });

        // rule 8
        rule = parser.eventRules[8];
        this.assertDictEquals(rule.parms, {'delay': '2000'});
        this.assertEquals(rule.kss_selector.isEventSelector, true);
        this.assertEquals(rule.kss_selector.css,  'div#update-area');
        this.assertEquals(rule.kss_selector.name,  'timeout');
        this.assertEquals(rule.kss_selector.namespace,  null);
        this.assertEquals(rule.kss_selector.id,  null);
        action = rule.actions.content['getCurrentTime'];
        this.assertEquals(action.type, 'S');
        this.assertEquals(action.name, 'getCurrentTime');
        this.assertEquals(action.error, null);
        this.assertKssParmEquals(action.parms, {
                'effect': new kukit.rd.KssTextValue('fade')
            });
        action = rule.actions.content['log'];
        this.assertEquals(action.type, 'C');
        this.assertEquals(action.name, 'log');
        this.assertEquals(action.error, null);
        this.assertKssParmEquals(action.parms, {
                'message': new kukit.rd.KssTextValue('Logging')
            });

        // rule 9
            //document:annoyClicker-annoy(annoyMe) {\n"
            //   evt-annoyClicker-annoy-preventdefault:   true;\n"
            //   action-client:    namespaced-alert;\n"
            //   namespaced-alert-message:       "You are an idiot! Ha ha ha. (But just keep on trying...)";\n'
            //}
        rule = parser.eventRules[9];
        this.assertDictEquals(rule.parms, {'preventdefault': 'true'});
        this.assertEquals(rule.kss_selector.css, 'document');
        this.assertEquals(rule.kss_selector.isMethodSelector, true);
        this.assertEquals(rule.kss_selector.name, 'annoy');
        this.assertEquals(rule.kss_selector.namespace, 'annoyClicker');
        this.assertEquals(rule.kss_selector.id, 'annoyMe');
        action = rule.actions.content['namespaced-alert'];
        this.assertEquals(action.type, 'C');
        this.assertEquals(action.name, 'namespaced-alert');
        this.assertEquals(action.error, null);
        this.assertKssParmEquals(action.parms, {
                'message': new kukit.rd.KssTextValue( "You are an idiot! Ha ha ha. (But just keep on trying...)")
            });

        
    };
};
    
kukit.KssParserTestCase.prototype = new kukit.TokenizerTestCaseBase;

if (typeof(testcase_registry) != 'undefined') {
    testcase_registry.registerTestCase(kukit.KssParserTestCase, 'kukit.KssParserTestCase');
}
