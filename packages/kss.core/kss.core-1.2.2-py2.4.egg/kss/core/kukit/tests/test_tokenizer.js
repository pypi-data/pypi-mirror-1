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

kukit.TokenizerTestCaseBase = function() {
   
    this.printDebug = function(parser, prefix) {
        if (typeof(prefix) == "undefined") {
            prefix = '';
            print('########################');
        }
        for (var i=0; i<parser.result.length; i++) {
            var txt = '';
            if (parser.result[i].txt) {
                txt = ' "' + parser.result[i].txt + '"';
            }
            print (prefix + '#' + i + ': [' + parser.result[i].symbol + ']' + txt);
            if (parser.result[i].result) {
                this.printDebug(parser.result[i],  prefix + '#' + i);
            }
        }
        if (!prefix) {
            print('');
        }
    };

    this.assertParsingError = function(pclass, src, tokenClass, eofOk, errtxt, errpos) {
        var exc = null;
        try {
            new pclass(src, tokenClass, eofOk);
        } catch(e) {
            exc = e;
            if (e.name != 'ParsingError') {
                throw e;
            }
        }
        this.assertNotEquals(exc, null, 'Should have thrown a ParsingError exception.');
        //this.assertEquals(exc.name, 'ParsingError');
        if (typeof(errtxt) != 'undefined') {
            this.assertEquals(exc.message.substr(0, errtxt.length), errtxt);
        }
        if (typeof(errpos) != 'undefined') {
        // XXX Do not check the error position now. This should be fixed however
        // it's not priority - it should be put back after the error position
        // reporting has been rationalized overall.
        //    this.assertEquals(exc.errpos, errpos);
        }
    };
};

kukit.TokenizerTestCaseBase.prototype = new kukit.UtilsTestCaseBase;

kukit.TokenizerTestCase = function() {
    this.name = 'kukit.TokenizerTestCase';

    this.setUp = function() {
    };

    this.testException = function() {
        var exc = null;
        try {
            throw new kukit.err.tk.ParsingError('Error happened');
        } catch(e) {
            exc = e;
        }
        this.assertNotEquals(exc, null);
        this.assertEquals(exc.name, 'ParsingError');
        // see if toString is overwritten on IE:
        this.assertEquals(exc.toString(), 'ParsingError: Error happened');
        this.assertEquals(exc.message, 'Error happened');
        this.assertEquals(exc.errpos, null);
        this.assertEquals(exc.errrow, null);
        this.assertEquals(exc.errcol, null);
    };

    this.testExceptionWithRowCol = function() {
        var exc = null;
        var cursor = new kukit.tk.Cursor('1234\n1234\n1234\n1234\n');
        var marker = cursor.makeMarker(13);
        try {
            throw new kukit.err.tk.ParsingError('Error happened', marker);
        } catch(e) {
            exc = e;
        }
        this.assertNotEquals(exc, null);
        this.assertEquals(exc.name, 'ParsingError');
        // see if toString is overwritten on IE:
        this.assertEquals(exc.toString(), 'ParsingError: Error happened at row 3, column 4');
        this.assertEquals(exc.message, 'Error happened at row 3, column 4');
        this.assertEquals(exc.errpos, 13);
        this.assertEquals(exc.errrow, 3);
        this.assertEquals(exc.errcol, 4);
    };

    this.testBasic = function() {
        // Basic parser creation
        var txt="abc def";
        var src = new kukit.tk.Cursor(txt);

        kukit.tk.openbrace = kukit.tk.mkToken('openbrace', '{');
        kukit.tk.openbracket = kukit.tk.mkToken('openbracket', '[');

        var pf = kukit.tk.mkParser('block', {
            '[': 'this.emitAndReturn(new kukit.tk.openbracket(this.src))',
            '{': 'new kukit.tk.openbrace(this.src)'
            });

        var parser = new pf(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 1);
        this.assertEquals(parser.result[0].symbol, 'fraction');
        this.assertEquals(parser.result[0].txt, 'abc def');
        
        this.assertParsingError(pf, src, null, false, 'Unexpected EOF');
        
        var txt="abc{def";
        var src = new kukit.tk.Cursor(txt);
        var parser = new pf(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 3);
        
        var txt="abc[def";
        var src = new kukit.tk.Cursor(txt);
        var parser = new pf(src, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 2);
        this.assertEquals(src.pos, 4);
    };
    
    this.testRecursive = function() {
        // Recursive parser creation
        var txt="a[bc{de[f}ghi";
        var src = new kukit.tk.Cursor(txt);

        kukit.tk.openbrace = kukit.tk.mkToken('openbrace', '{');
        kukit.tk.openbracket = kukit.tk.mkToken('openbracket', '[');
        kukit.tk.closebrace = kukit.tk.mkToken('closebrace', '}');
        kukit.tk.wrappedbracket = kukit.tk.mkToken('wrappedbracket', '[');

        kukit.tk.global = kukit.tk.mkParser('global', {
            '[': 'new kukit.tk.openbracket(this.src)',
            '{': 'new kukit.tk.inside(this.src, kukit.tk.openbrace)'
            });
            
        kukit.tk.inside = kukit.tk.mkParser('inside', {
            '[': 'new kukit.tk.wrappedbracket(this.src)',
            '}': 'this.emitAndReturn(new kukit.tk.closebrace(this.src))'
            });

        var parser = new kukit.tk.global(src, null, true);
        //this.printDebug(parser);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 5);
        this.assertEquals(parser.result[0].symbol, 'fraction');
        this.assertEquals(parser.result[0].txt, 'a');
        this.assertEquals(parser.result[1].symbol, 'openbracket');
        this.assertEquals(parser.result[1].txt, '[');
        this.assertEquals(parser.result[2].symbol, 'fraction');
        this.assertEquals(parser.result[2].txt, 'bc');
        this.assertEquals(parser.result[3].symbol, 'inside');
        
        var itoken = parser.result[3]
        this.assertEquals(itoken.result.length, 5);
        this.assertEquals(itoken.result[0].symbol, 'openbrace');
        this.assertEquals(itoken.result[0].txt, '{');
        this.assertEquals(itoken.result[1].symbol, 'fraction');
        this.assertEquals(itoken.result[1].txt, 'de');
        this.assertEquals(itoken.result[2].symbol, 'wrappedbracket');
        this.assertEquals(itoken.result[2].txt, '[');
        this.assertEquals(itoken.result[3].symbol, 'fraction');
        this.assertEquals(itoken.result[3].txt, 'f');
        this.assertEquals(itoken.result[4].symbol, 'closebrace');
        this.assertEquals(itoken.result[4].txt, '}');

        this.assertEquals(parser.result[4].symbol, 'fraction');
        this.assertEquals(parser.result[4].txt, 'ghi');

        //
        // Testing for unexpected eof handling
        //

        var txt="";
        var src = new kukit.tk.Cursor(txt);
        parser = new kukit.tk.global(src, null, true);
        //this.printDebug(parser);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 0);

        // In particular, the next one should not raise unexpected eof.
        var txt="{}";
        var src = new kukit.tk.Cursor(txt);
        parser = new kukit.tk.global(src, null, true);
        //this.printDebug(parser);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 1);

    };
    
    this.testProcessing = function() {
        // Processing parser creation
        var txt="abc'de\\'f'ghi";
        var src = new kukit.tk.Cursor(txt);

        kukit.tk.quote = kukit.tk.mkToken('quote', "'");
        kukit.tk.backslash = kukit.tk.mkToken('backslash', "\\");

        kukit.tk.global = kukit.tk.mkParser('global', {
            "'": 'new kukit.tk.string(this.src, kukit.tk.quote)'
            });
            
        kukit.tk.string = kukit.tk.mkParser('string', {
            "'": 'this.emitAndReturn(new kukit.tk.quote(this.src))',
            "\\": 'new kukit.tk.backslashed(this.src, kukit.tk.backslash)'
            });
        kukit.tk.string.prototype.process = function() {
            // collect up the value of the string, omitting the quotes
            this.txt = '';
            for (var i=1; i<this.result.length-1; i++) {
                this.txt += this.result[i].txt;
            }
        }

        kukit.tk.backslashed = kukit.tk.mkParser('backslashed', {});
        kukit.tk.backslashed.prototype.nextStep = function(table) {
            // digest the next character and store it as txt
            var src = this.src;
            var length = src.text.length;
            if (length < src.pos + 1) {
                this.emitError('Missing character after backslash');
            } else { 
                this.result.push(new kukit.tk.Fraction(src, src.pos+1));
                this.src.pos += 1;
                this.finished = true;
            }
        }
        kukit.tk.backslashed.prototype.process = function() {
            this.txt = this.result[1].txt;
        }

        var parser = new kukit.tk.global(src, null, true);
        //this.printDebug(parser);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 3);
        this.assertEquals(parser.result[0].symbol, 'fraction');
        this.assertEquals(parser.result[0].txt, 'abc');
        this.assertEquals(parser.result[1].symbol, 'string');
        this.assertEquals(parser.result[1].txt, "de'f");

        this.assertEquals(parser.result[1].result.length, 5);
        this.assertEquals(parser.result[1].result[0].symbol, 'quote');
        this.assertEquals(parser.result[1].result[0].txt, "'");
        this.assertEquals(parser.result[1].result[1].symbol, 'fraction');
        this.assertEquals(parser.result[1].result[1].txt, 'de');
        this.assertEquals(parser.result[1].result[2].symbol, 'backslashed');
        this.assertEquals(parser.result[1].result[2].txt, "'");

        this.assertEquals(parser.result[1].result[2].result.length, 2);
        this.assertEquals(parser.result[1].result[2].result[0].symbol, 'backslash');
        this.assertEquals(parser.result[1].result[2].result[0].txt, "\\");
        this.assertEquals(parser.result[1].result[2].result[1].symbol, 'fraction');
        this.assertEquals(parser.result[1].result[2].result[1].txt, "'");
        
        this.assertEquals(parser.result[1].result[3].symbol, 'fraction');
        this.assertEquals(parser.result[1].result[3].txt, 'f');
        this.assertEquals(parser.result[1].result[4].symbol, 'quote');
        this.assertEquals(parser.result[1].result[4].txt, "'");


        this.assertEquals(parser.result[2].symbol, 'fraction');
        this.assertEquals(parser.result[2].txt, 'ghi');
    };
    
    this.testEmbedded = function() {
        // Embedded parser creation
        // this means make independend parsing of separate tokens
        // only makes sense if we don't want LR parse inside a token.
        var txt="a[bc{de fg[h] ij[kl]mn}opq";
        var src = new kukit.tk.Cursor(txt);

        kukit.tk.openbrace = kukit.tk.mkToken('openbrace', '{');
        kukit.tk.openbracket = kukit.tk.mkToken('openbracket', '[');
        kukit.tk.closebrace = kukit.tk.mkToken('closebrace', '}');
        kukit.tk.closebracket = kukit.tk.mkToken('closebracket', ']');

        kukit.tk.global = kukit.tk.mkParser('global', {
            '[': 'new kukit.tk.openbracket(this.src)',
            '{': 'new kukit.tk.inside(this.src, kukit.tk.openbrace)'
            });
            
        kukit.tk.inside = kukit.tk.mkParser('inside', {
            '}': 'this.emitAndReturn(new kukit.tk.closebrace(this.src))'
            });
        kukit.tk.inside.prototype.process = function() {
            // collect up the value of the string, omitting the quotes
            this.txt = '';
            for (var i=1; i<this.result.length-1; i++) {
                this.txt += this.result[i].txt;
            }
            // Take all what is in the braces, and parse only the third part.
            var parts = this.txt.split(' ');
            var last_part = parts[parts.length - 1];
            // make embedded parsing
            var embedded_src =new kukit.tk.Cursor(last_part);
            this.embedded_parser = new kukit.tk.embedded(embedded_src, null, true);
            if (this.embedded_parser == 2) {
                this.emitError('Error in embedded parser: ' + embedded_src.errtxt);
                }
        }
            
        kukit.tk.embedded = kukit.tk.mkParser('embedded', {
            '[': 'new kukit.tk.embedded_inside(this.src, kukit.tk.openbracket)'
            });
 
        kukit.tk.embedded_inside = kukit.tk.mkParser('embedded_inside', {
            ']': 'this.emitAndReturn(new kukit.tk.closebracket(this.src))'
            });
            
        var parser = new kukit.tk.global(src, null, true);
        //this.printDebug(parser);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 5);
        this.assertEquals(parser.result[0].symbol, 'fraction');
        this.assertEquals(parser.result[0].txt, 'a');
        this.assertEquals(parser.result[1].symbol, 'openbracket');
        this.assertEquals(parser.result[1].txt, '[');
        this.assertEquals(parser.result[2].symbol, 'fraction');
        this.assertEquals(parser.result[2].txt, 'bc');
        this.assertEquals(parser.result[3].symbol, 'inside');
        this.assertEquals(parser.result[3].txt, "de fg[h] ij[kl]mn");

        var iparser = parser.result[3].embedded_parser;
        //this.printDebug(iparser);
        this.assertEquals(iparser.result.length, 3);
        this.assertEquals(iparser.result[0].symbol, 'fraction');
        this.assertEquals(iparser.result[0].txt, 'ij');
        this.assertEquals(iparser.result[1].symbol, 'embedded_inside');
        this.assertEquals(iparser.result[1].txt, '[kl]');
        this.assertEquals(iparser.result[2].symbol, 'fraction');
        this.assertEquals(iparser.result[2].txt, 'mn');

        this.assertEquals(parser.result[4].symbol, 'fraction');
        this.assertEquals(parser.result[4].txt, 'opq');
    };
    
    this.testMoreTokens = function() {
        // More tokens, empty entries
        var txt="a[bc{de[f}ghi";
        var src = new kukit.tk.Cursor(txt);

        kukit.tk.openbrace = kukit.tk.mkToken('openbrace', '{');
        kukit.tk.openbracket = kukit.tk.mkToken('openbracket', '[');
        kukit.tk.closebrace = kukit.tk.mkToken('closebrace', '}');
        kukit.tk.wrappedbracket = kukit.tk.mkToken('wrappedbracket', '[');

        kukit.tk.global = kukit.tk.mkParser('global', {
            '[': 'new kukit.tk.openbracket(this.src)',
            '{': '[new kukit.tk.openbrace(this.src), new kukit.tk.inside(this.src)]',
            '}': 'new kukit.tk.closebrace(this.src)'
            });
            
        kukit.tk.inside = kukit.tk.mkParser('inside', {
            '[': 'new kukit.tk.wrappedbracket(this.src)',
            '}': 'this.emitAndReturn()'
            });

        var parser = new kukit.tk.global(src, null, true);
        //this.printDebug(parser);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 7);
        this.assertEquals(parser.result[0].symbol, 'fraction');
        this.assertEquals(parser.result[0].txt, 'a');
        this.assertEquals(parser.result[1].symbol, 'openbracket');
        this.assertEquals(parser.result[1].txt, '[');
        this.assertEquals(parser.result[2].symbol, 'fraction');
        this.assertEquals(parser.result[2].txt, 'bc');
        this.assertEquals(parser.result[3].symbol, 'openbrace');
        this.assertEquals(parser.result[3].txt, '{');
        this.assertEquals(parser.result[4].symbol, 'inside');
        
        var itoken = parser.result[4];
        this.assertEquals(itoken.result.length, 3);
        this.assertEquals(itoken.result[0].symbol, 'fraction');
        this.assertEquals(itoken.result[0].txt, 'de');
        this.assertEquals(itoken.result[1].symbol, 'wrappedbracket');
        this.assertEquals(itoken.result[1].txt, '[');
        this.assertEquals(itoken.result[2].symbol, 'fraction');
        this.assertEquals(itoken.result[2].txt, 'f');
        
        this.assertEquals(parser.result[5].symbol, 'closebrace');
        this.assertEquals(parser.result[5].txt, '}');
        this.assertEquals(parser.result[6].symbol, 'fraction');
        this.assertEquals(parser.result[6].txt, 'ghi');
    };
 
};
    
kukit.TokenizerTestCase.prototype = new kukit.TokenizerTestCaseBase;

if (typeof(testcase_registry) != 'undefined') {
    testcase_registry.registerTestCase(kukit.TokenizerTestCase, 'kukit.TokenizerTestCase');
}
