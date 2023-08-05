/*
* Copyright (c) 2005-2006
* Authors:
*   Martin Heidegger <mastakaneda@gmail.com>
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

/* Simple but effective tokenizing parser engine */

kukit.tk = {};

/*
* class _TokenBase
*/
kukit.tk._TokenBase = function() {
};

kukit.tk._TokenBase.prototype.emitError = function(txt) {
    // Use the start position of the token for the error report.
    throw new kukit.err.tk.ParsingError(txt, this.src.makeMarker(this.startpos));
};

kukit.tk._TokenBase.prototype.setSrcStatus = function(eofOk) {
    if (! this.finished && this.src.text.length == this.src.pos) {
        if (eofOk) {
            this.finished = true;
        } else {
            this.emitError('Unexpected EOF');
        }
    }
};


/*
* class _ParserBase
*/
kukit.tk._ParserBase = function() {
};

kukit.tk._ParserBase.prototype = new kukit.tk._TokenBase;

kukit.tk._ParserBase.prototype.emitAndReturn = function(token) {
    // handle return to the next level
    this.finished = true;
    return token;
};

kukit.tk._ParserBase.prototype.nextStep = function(table) {
    var src = this.src;
    // Search for symbol according to table.
    var best_pos = src.text.length;
    var best_symbol = null;
    for (var symbol in table) {
        var pos = src.text.indexOf(symbol, src.pos);
        if (pos != -1 && pos < best_pos) {
            best_pos = pos;
            best_symbol = symbol;
        }
    }
    // eat up till the symbol found (of EOF)
    if (best_pos > src.pos) {
        this.result.push(new kukit.tk.Fraction(src, best_pos));
        src.pos = best_pos;
    }
    // handle cursor point
    if (best_symbol) {
        // found a symbol, handle that
        // make the token and push it
        var tokens = eval(table[best_symbol]);
        if (typeof(tokens) != 'undefined') {
            if (typeof(tokens.length) == 'undefined') {
                tokens = [tokens];
            }
            for (var i=0; i<tokens.length; i++) {
                this.result.push(tokens[i]);
            }
        }
    }
};

/* token postprocess support */

kukit.tk._ParserBase.prototype.process = function() {
    // default process after tokenization
    this.txt = '';
    for (var i=0; i<this.result.length; i++) {
        this.txt += this.result[i].txt;
    }
};

kukit.tk._ParserBase.prototype.expectToken = function(cursor, token) {
    var i = cursor.next;
    if (token) {
        var symbol = token.prototype.symbol;
        if (i >= this.result.length) {
            this.emitError('Expected [' + symbol + ']');
        } else if (this.result[i].symbol != symbol) {
            this.emitError('Expected [' + symbol + '], found [' + this.result[i].symbol + ']');
        }
    } else {
        if (i >= this.result.length) {
            this.emitError('Expected token');
        }
    }
    cursor.token = this.result[i];
    cursor.next += 1;
};

kukit.tk._ParserBase.prototype.ifToken = function(cursor, token1, token2, token3, token4) {
    var i = cursor.next;
    return (! (i >= this.result.length || this.result[i].symbol != token1.prototype.symbol
                && (!token2 || this.result[i].symbol != token2.prototype.symbol
                && (!token3 || this.result[i].symbol != token3.prototype.symbol
                && (!token4 || this.result[i].symbol != token4.prototype.symbol)))));
};

kukit.tk._ParserBase.prototype.digestTxt = function(cursor, token1, token2, token3, token4) {
    // digests the txt from the tokens, ignores given token
    // plus whitespace removal
    this.digestExactTxt(cursor, token1, token2, token3, token4);
    cursor.txt = this.dewhitespaceAndTrim(cursor.txt);
};

kukit.tk._ParserBase.prototype.digestExactTxt = function(cursor, token1, token2, token3, token4) {
    // digests the txt from the tokens, ignores given token
    // exact value: no whitespace removal
    var result = '';
    while (this.ifToken(cursor, token1, token2, token3, token4)) {
        result += this.result[cursor.next].txt;
        cursor.next ++;
        }
    cursor.txt = result;
};


kukit.tk._ParserBase.prototype.dewhitespace = function(txt) {
    // removes ws but leaves leading and trailing one
    if (txt != ' ') { //speedup only
        txt = txt.replace(/[\r\n\t ]+/g, ' ');
    }
    return txt;
};
    
kukit.tk._ParserBase.prototype.dewhitespaceAndTrim = function(txt) {
    txt = this.dewhitespace(txt);
    // XXX Strange thing is: following replace works from
    // tests and the original demo, but with kukitportlet demo
    // it breaks. Someone stinks!
    //txt = txt.replace(/^ /, '');
    if (txt && txt.charAt(0) == ' ') {
        txt = txt.substr(1);
    }
    txt = txt.replace(/ $/, '');
    return txt;
};

/*
* class Fraction
*/
kukit.tk.Fraction = function(src, endpos) {
    this.txt = src.text.substring(src.pos, endpos);
    this.startpos = src.pos;
    this.endpos = src.pos;
    this.finished = true;
};
kukit.tk.Fraction.prototype.symbol = 'fraction';


/* Factories to make tokens and parsers */

kukit.tk.mkToken = function(symbol, txt) {
    // Poor man's subclassing.
    f = function(src) {
        this.src = src;
        this.startpos = src.pos;
        if (src.text.substr(src.pos, txt.length) != txt) {
            this.emitError('Expected "' + txt + '", found "' + src.text.substr(src.pos, txt.length) + '"');
        } else {
            src.pos += txt.length;
            this.finished = true;
        }
        this.endpos = src.pos;
        //this.src = null;
    };
    f.prototype = new kukit.tk._TokenBase;
    f.prototype.symbol = symbol;
    f.prototype.txt = txt;
    return f;
};

kukit.tk.mkParser = function(symbol, table) {
    // Poor man's subclassing.
    f = function(src, tokenClass, eofOk) {
        this.src = src;
        this.startpos = src.pos;
        this.finished = false;
        this.result = [];
        if (tokenClass) {
            // Reentry with starting token propagated.
            this.result.push(new tokenClass(this.src));
        }
        this.setSrcStatus(eofOk);
        while (!this.finished) {
            this.nextStep(table);
            this.setSrcStatus(eofOk);
        }
        this.endpos = src.pos;
        // post processing
        this.process();
        
        //this.src = null;
    };
    f.prototype = new kukit.tk._ParserBase;
    f.prototype.symbol = symbol;
    return f;
};

kukit.tk.Cursor = function(txt) {
    this.text = txt;
    this.pos = 0;
};

kukit.tk.Cursor.prototype.makeMarker = function(pos) {
    // create a cursor to mark this position
    var cursor = new kukit.tk.Cursor();
    cursor.text = this.text;
    cursor.pos = pos;
    // Calculate the row and column information on the cursor
    cursor.calcRowCol();
    return cursor;
};

kukit.tk.Cursor.prototype.getRowCol = function(pos) {
    // Gets the row, col information for the position.
    if (typeof(pos) == 'undefined') {
        pos = this.pos;
    }
    var index = 0;
    var row = 1;
    var next = 0;
    while (true) {
        next = this.text.indexOf('\n', index);
        if (next == -1 || next >= pos) {
            break;
        }
        index = next + 1;
        row += 1;
    }
    var col = pos - index + 1;
    return {'row': row, 'col': col};
};

kukit.tk.Cursor.prototype.calcRowCol = function(pos) {
    // Calculates row and column information on the cursor.
    var rowcol = this.getRowCol();
    this.row = rowcol.row;
    this.col = rowcol.col;
};
