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

/* Tokens of the KSS parser */

kukit.kssp = {};

/* Tokens */

kukit.kssp.commentbegin = kukit.tk.mkToken('commentbegin', "\/\*");
kukit.kssp.commentend = kukit.tk.mkToken('commentend', "\*\/");
kukit.kssp.openbrace = kukit.tk.mkToken('openbrace', "{");
kukit.kssp.closebrace = kukit.tk.mkToken('closebrace', "}");
kukit.kssp.openbracket = kukit.tk.mkToken('openbracket', "[");
kukit.kssp.closebracket = kukit.tk.mkToken('closebracket', "]");
kukit.kssp.openparent = kukit.tk.mkToken('openparent', "(");
kukit.kssp.closeparent = kukit.tk.mkToken('closeparent', ")");
kukit.kssp.semicolon = kukit.tk.mkToken('semicolon', ";");
kukit.kssp.colon = kukit.tk.mkToken('colon', ":");
kukit.kssp.quote = kukit.tk.mkToken('quote', "'");
kukit.kssp.dquote = kukit.tk.mkToken('dquote', '"');
kukit.kssp.backslash = kukit.tk.mkToken('backslash', '\x5c'); 
kukit.kssp.comma = kukit.tk.mkToken('comma', ",");
kukit.kssp.equals = kukit.tk.mkToken('equals', "=");

/* Parsers */

/*
* class Document 
*/
kukit.kssp.Document = kukit.tk.mkParser('document', {
    "\/\*": 'new kukit.kssp.Comment(this.src, kukit.kssp.commentbegin)',
    "{": 'new kukit.kssp.Block(this.src, kukit.kssp.openbrace)'
    });
kukit.kssp.Document.prototype.process = function() {
    this.eventRules = [];
    var cursor = {'next': 0};
    while (cursor.next < this.result.length) {
        this.digestTxt(cursor, kukit.tk.Fraction, kukit.kssp.Comment);
        var key = cursor.txt;
        if (! key) {
            break;
        }
        this.expectToken(cursor, kukit.kssp.Block);
        this.addBlock(key, cursor.token);
    }
    this.result = [];
    this.txt = '';
}; 
kukit.kssp.Document.prototype.addBlock = function(key, block) {
    // Parse the part in an embedded parser
    var src = new kukit.tk.Cursor(key + ' ');
    var parser = new kukit.kssp.KssSelector(src, null, true);
    // check the event name and namespace use in evt- rules
    // equals the event name and namespace set in the KSS selector.
    if (block.evt_name != null) {
        // We have evt- parms in the rule.
        if (block.evt_name != parser.kssSelector.name
            || block.evt_namespace != parser.kssSelector.namespace) {
            // XXX this should be done in another way,
            //so that we can see where the error happened.
;;;         kukit.E = 'Wrong prefix : we have "' + block.evt_namespace;
;;;         kukit.E += '-' + block.evt_name + '" instead of "' + key;
;;;         kukit.E += '". KSS prefix ';
;;;         kukit.E += '"evt-[<NAMESPACE>-]<EVENTNAME>-<NAME>" ';
;;;         kukit.E += 'must not have different [namespace and] ';
;;;         kukit.E += 'name than the KSS selector at the top of the ';
;;;         kukit.E += 'rule.';
            block.emitError(kukit.E);
        }
    }
    // Create the event rule. (one action only)
    var eventRule = new kukit.rd.EventRule(parser.kssSelector,
        block.eventParameters, block.actions);
    // Store the rule
    this.eventRules.push(eventRule);
};

/*
* class Comment 
*/
kukit.kssp.Comment = kukit.tk.mkParser('comment', {
    // it's not 100% good, but will do
    "\*\/": 'this.emitAndReturn(new kukit.kssp.commentend(this.src))'
    });
kukit.kssp.Comment.prototype.process = function() {
    this.result = [];
    this.txt = ' ';
};

/*
* class Block 
*/
kukit.kssp.Block = kukit.tk.mkParser('block', {
    ";": 'new kukit.kssp.semicolon(this.src)',
    ":": '[new kukit.kssp.colon(this.src), new kukit.kssp.PropValue(this.src)]',
    "}": 'this.emitAndReturn(new kukit.kssp.closebrace(this.src))'
    });
kukit.kssp.Block.prototype.process = function() {
    //this.parms = {};
    this.eventParameters = {};
    this.evt_name = null; // we don't know at this point
    this.evt_namespace = null; // we don't know at this point
    this.actions = new kukit.rd.ActionSet();
    var cursor = {'next': 1};
    while (cursor.next < this.result.length-1) {
        this.digestTxt(cursor, kukit.tk.Fraction, kukit.kssp.Comment);
        var key = cursor.txt;
        if (! key) {
            break;
        }
        this.expectToken(cursor, kukit.kssp.colon);
        this.expectToken(cursor, kukit.kssp.PropValue);
        // store the wrapped prop
        this.addDeclaration(key, cursor.token.value);
        if (cursor.next == this.result.length-1) break;
        this.expectToken(cursor, kukit.kssp.semicolon);
    }
    this.result = [];
    this.txt = '';
};
kukit.kssp.Block.prototype.addDeclaration = function(key, value) {

    var ppRegistries = {
        '': kukit.pprovidersGlobalRegistry,
        'kssSelector': kukit.sr.pproviderSelRegistry,
        'kssSubmitForm': kukit.fo.pproviderFormRegistry
    };

    // p.s. value is here a KssXxParm. In most cases we check and unwrap it.
    // the keys look like this:
    //
    // evt-<EVTNAME>-<KEY>: <VALUE>
    // evt-<NAMESPACE>-<EVTNAME>-<KEY>: <VALUE>
    //
    // action-server: <ACTIONNAME>
    // action-client: <ACTIONNAME>
    // action-client: <NAMESPACE>-<ACTIONNAME>
    // action-cancel: <ACTIONNAME>
    // action-cancel: <NAMESPACE>-<ACTIONNAME>
    //
    // <ACTIONNAME>-<KEY>: <VALUE>
    // <NAMESPACE>-<ACTIONNAME>-<KEY>: <VALUE>
    // <ACTIONNAME>-error: <VALUE>
    // <NAMESPACE>-<ACTIONNAME>-error: <VALUE>
    //
    // default-<KEY>: <VALUE>
    // default-error: <VALUE>
    //
    var splitkey = key.split('-');
;;; if (splitkey.length < 2 || splitkey.length > 4) {
;;;     kukit.E = 'Wrong rule key : "' + key + '". ';
;;;     kukit.E += 'KSS rule key must be "<ACTIONNAME>-<PARAMETER>" or ';
;;;     kukit.E += '"<NAMESPACE>-<ACTIONNAME>-<PARAMETER>" or ';
;;;     kukit.E += '"evt-<EVENTNAME>-<PARAMETER>" or ';
;;;     kukit.E += '"evt-<NAMESPACE>-<EVENTNAME>-<PARAMETER>".';
;;;     this.emitError(kukit.E);
;;; }
    var name = splitkey[0];
    if (name == 'evt') {
        // evt-<EVTNAME>-<PARAMETER>: <VALUE>
        // evt-<NAMESPACE>-<EVTNAME>-<PARAMETER>: <VALUE>
;;;     if (splitkey.length < 3) {
;;;         kukit.E = 'Wrong rule key : "' + key + '". ';
;;;         kukit.E += 'KSS rule key must be "<ACTIONNAME>-<PARAMETER>"';
;;;         kukit.E += ' or "<NAMESPACE>-<ACTIONNAME>-<PARAMETER>" or ';
;;;         kukit.E += '"evt-<EVENTNAME>-<PARAMETER>" or ';
;;;         kukit.E += '"evt-<NAMESPACE>-<EVENTNAME>-<PARAMETER>".';
;;;         this.emitError(kukit.E);
;;;     }
        var enamespace;
        var ename;
        var ekey;
        if (splitkey.length == 3) {
            // evt-<EVENTNAME>-<PARAMETER>: <VALUE>
            ename =  splitkey[1];
            ekey = splitkey[2];
        } else {
            // evt-<NAMESPACE>-<EVENTNAME>-<PARAMETER>: <VALUE>
            enamespace = splitkey[1];
            ename = splitkey[2];
            ekey = splitkey[3];
        }
        if (this.evt_name == null) {
            // This is the first evt- rule, so we set it up
            // so that we can check it stays the same within the block.
            this.evt_name = ename;
            this.evt_namespace = enamespace;
;;;     } else {
;;;         if (ename != this.evt_name || enamespace != this.evt_namespace) {
;;;             // Do not allow deviation from the previous event names.
;;;             kukit.E = 'Wrong key [' + key + '] : ';
;;;             kukit.E += 'evt-[<NAMESPACE>-]<EVENTNAME>-<PARAMETER> ';
;;;             kukit.E += 'keys cannot have different [namespace and] ';
;;;             kukit.E += 'event name than in the event selector, ';
;;;             kukit.E += 'it should have been [' + this.evt_namespace;
;;;             kukit.E += '-' + this.evt_name + '].';
;;;             this.emitError(kukit.E);
;;;         }
;;;     }
;;;     if (value.isMethod != false) {
;;;         kukit.E = 'Wrong value for key [' + key + '] : ';
;;;         kukit.E += 'value providers are not ';
;;;         kukit.E += 'allowed as value for ';
;;;         kukit.E += 'evt-[<NAMESPACE>-]<EVENTNAME>-<PARAMETER> keys.';
;;;         this.emitError(kukit.E);
        }
        // set it
        this.eventParameters[ekey] = value.txt;
    } else if (name == 'action') {
        // action-server: <ACTIONNAME>
        // action-client: <ACTIONNAME>
        // action-client: <NAMESPACE>-<ACTIONNAME>
        // action-cancel: <ACTIONNAME>
        // action-cancel: <NAMESPACE>-<ACTIONNAME>
;;;     if (splitkey.length != 2) {
;;;         kukit.E = 'Wrong key [' + key + '] : ';
;;;         kukit.E += 'action-<QUALIFIER> keys can have only one dash.';
;;;         this.emitError(kukit.E);
;;;         }
;;;     if (value.isMethod != false) {
;;;         kukit.E = 'Wrong value for key [' + key + '] : ';
;;;         kukit.E += 'value providers are not ';
;;;         kukit.E += 'allowed for action-<QUALIFIER> keys.';
;;;         this.emitError(kukit.E);
;;;         }
        var atab = {'server': 'S', 'client': 'C', 'cancel': 'X'};
        var actionType = atab[splitkey[1]];
;;;     if (! actionType) {
;;;         kukit.E = 'Wrong key [' + key + '] : ';
;;;         kukit.E += 'qualifier in action-<QUALIFIER> keys must be ';
;;;         kukit.E += '"server" or "client" or "cancel".'; 
;;;         this.emitError(kukit.E);
;;;         }    
;;;     // force value to be <ACTIONNAME> or <NAMESPACE>-<ACTIONNAME>
;;;     var splitvalue = value.txt.split('-');
;;;     if (splitvalue.length > 2) {
;;;         kukit.E = 'Wrong value for key [' + key + '] : ';
;;;         kukit.E += 'value must be <ACTIONNAME> or <NAMESPACE>';
;;;         kukit.E += '-<ACTIONNAME> for action-<QUALIFIER> keys.';
;;;         this.emitError(kukit.E);
;;;         }
        // set it
        var action = this.actions.getOrCreateAction(value.txt);
        if (actionType != 'X' || action.type == null) {
            action.setType(actionType);
        } else {
            this.actions.deleteAction(value.txt);
        }
    } else {
        // <ACTIONNAME>-<KEY>: <VALUE>
        // <NAMESPACE>-<ACTIONNAME>-<KEY>: <VALUE>
        // <ACTIONNAME>-error: <VALUE>
        // <NAMESPACE>-<ACTIONNAME>-error: <VALUE>
        // default-<KEY>: <VALUE>
        // default-error: <VALUE>
        var aname;
        var akey;
        if (splitkey.length == 2) {
            // <ACTIONNAME>-<KEY>: <VALUE>
            // <ACTIONNAME>-error: <VALUE>
            // default-<KEY>: <VALUE>
            // default-error: <VALUE>
            aname =  splitkey[0];
            akey = splitkey[1];
        } else {
            // <NAMESPACE>-<ACTIONNAME>-<KEY>: <VALUE>
            // <NAMESPACE>-<ACTIONNAME>-error: <VALUE>
            aname = splitkey[0] + '-' + splitkey[1];
            akey = splitkey[2];
        }
        // set it
        var action = this.actions.getOrCreateAction(aname);
        switch (akey) {
            case 'error': {
                    // <ACTIONNAME>-error: <VALUE>
                    // default-error: <VALUE>
;;;                 if (value.isMethod != false) {
;;;                     kukit.E = 'Wrong value for key [' + key + '] : ';
;;;                     kukit.E += 'value providers are not ';
;;;                     kukit.E += 'allowed for <ACTIONNAME>-error keys.';
;;;                     this.emitError(kukit.E);
;;;                     }
                    action.setError(value.txt);
                    // also create the action for the error itself.
                    var err_action = this.actions.getOrCreateAction(value.txt);
                    err_action.setType('E');
                } break;
            default: {
                    // <ACTIONNAME>-<KEY>: <VALUE>
                    // default-<KEY>: <VALUE>
                    // 
                    // value may be either txt or method parms, 
                    // and they get stored with the wrapper.
                    action.parms[akey] = value;
                    // 
                    // Check the syntax of the value at this point.
                    // This will also set the value providers on the value
                    // (from check).
                    //
                    // Figure out which registry to use.
                    var registry = ppRegistries[akey];
                    if (typeof(registry) == 'undefined') {
                        // use default pproviders
                        registry = ppRegistries[''];
                    }
                    //
                    try {
                        // Check also sets the value provider on the value.
                        value.check(registry);
                    } catch(e) {
;;;                     kukit.E = 'Error in value : ' + e + '.';
                        this.emitError(kukit.E);
                    }
                } break;
        }
    }
};

/*
* class PropValue
*/
kukit.kssp.PropValue = kukit.tk.mkParser('propvalue', {
    ";": 'this.emitAndReturn()',
    "}": 'this.emitAndReturn()',
    ")": 'this.emitAndReturn()',
    ",": 'this.emitAndReturn()',
    "'": 'new kukit.kssp.String(this.src, kukit.kssp.quote)',
    '"': 'new kukit.kssp.String2(this.src, kukit.kssp.dquote)',
    "\/\*": 'new kukit.kssp.Comment(this.src, kukit.kssp.commentbegin)',
    "(": 'new kukit.kssp.MethodArgs(this.src, kukit.kssp.openparent)'
    });
kukit.kssp.PropValue.prototype.process = function() {
    var cursor = {'next': 0};
    this.digestTxt(cursor, kukit.tk.Fraction, kukit.kssp.Comment);
    this.txt = '';
    var txt = cursor.txt;
    if (this.ifToken(cursor, kukit.kssp.String)) {
        // The previous txt must be all whitespace.
        if (txt) {
;;;         kukit.E = 'Wrong value : unallowed characters [' + txt + ']';
;;;         kukit.E += ' before a string.';
            this.emitError(kukit.E);
        }
        // the next one must be a string.
        this.expectToken(cursor, kukit.kssp.String);
        this.produceTxt(cursor.token.txt);
    } else if (this.ifToken(cursor, kukit.kssp.MethodArgs)) {
        // see if not empty and has no spaces in it 
        if (! txt || txt.indexOf(' ') != -1) {
;;;         kukit.E = 'Wrong value : method name [' + txt + '] cannot ';
;;;         kukit.E += 'have spaces.';
            this.emitError(kukit.E);
        }
        // the next one must be the rules
        this.expectToken(cursor, kukit.kssp.MethodArgs);
        this.value = new this.valueClass(txt, cursor.token.args);
    } else {
        // not a string or method: check if we allowed multiword.
        if (! this.multiword_allowed && txt.indexOf(' ') != -1) {
;;;         kukit.E = 'Wrong value : [' + txt + '] cannot have spaces.';
            this.emitError(kukit.E);
        }
        this.produceTxt(txt);
    }
    // see what's after
    if (cursor.next < this.result.length) {
        this.digestTxt(cursor, kukit.tk.Fraction, kukit.kssp.Comment);
        // we have to be at the end and have no text after
        if (cursor.next < this.result.length || cursor.txt) {
;;;         kukit.E = 'Wrong value : unallowed characters after ';
;;;         kukit.E += 'the property.';
            this.emitError(kukit.E);
        }
    }
    this.result = [];
};
kukit.kssp.PropValue.prototype.multiword_allowed = true;
kukit.kssp.PropValue.prototype.valueClass = kukit.rd.KssMethodValue;
kukit.kssp.PropValue.prototype.produceTxt = function(txt) {
    // txt parms are returned embedded
    this.value = new kukit.rd.KssTextValue(txt);
};

/*
* class PropValueInMethod
*
* PropValue in method cannot have method-style vars.
*/
kukit.kssp.PropValueInMethod = kukit.tk.mkParser('propvalue', {
    ";": 'this.emitAndReturn()',
    "}": 'this.emitAndReturn()',
    ")": 'this.emitAndReturn()',
    "]": 'this.emitAndReturn()',
    ",": 'this.emitAndReturn()',
    "'": 'new kukit.kssp.String(this.src, kukit.kssp.quote)',
    '"': 'new kukit.kssp.String2(this.src, kukit.kssp.dquote)',
    "\/\*": 'new kukit.kssp.Comment(this.src, kukit.kssp.commentbegin)'
    });
kukit.kssp.PropValueInMethod.prototype.multiword_allowed = false;
kukit.kssp.PropValueInMethod.prototype.process =
    kukit.kssp.PropValue.prototype.process;
kukit.kssp.PropValueInMethod.prototype.produceTxt = function(txt) {
    // txt parms are returned unwrapped
    this.txt = txt;
};

/*
* class PropValueInPseudo
*
* PropValue in pseudo must ba single word with no spaces around.
*/
kukit.kssp.PropValueInPseudo = kukit.tk.mkParser('propvalue', {
    "{": 'this.emitAndReturn()',
    " ": 'this.emitAndReturn()',
    "\t": 'this.emitAndReturn()',
    "\n": 'this.emitAndReturn()',
    "\r": 'this.emitAndReturn()',
    "\/\*": 'this.emitAndReturn()',
    ":": 'this.emitAndReturn()',
    "(": 'this.emitAndReturn(new kukit.kssp.MethodArgs(this.src,' +
        'kukit.kssp.openparent))'
    });
kukit.kssp.PropValueInPseudo.prototype.multiword_allowed = false;
kukit.kssp.PropValueInPseudo.prototype.process = 
    kukit.kssp.PropValue.prototype.process;
kukit.kssp.PropValueInPseudo.prototype.valueClass = kukit.rd.KssPseudoValue;
kukit.kssp.PropValueInPseudo.prototype.produceTxt = function(txt) {
    // txt parms are returned embedded
    this.value = new kukit.rd.KssPseudoValue(txt, []);
};

/*
* class String
*/
kukit.kssp.String = kukit.tk.mkParser('string', {
    "'": 'this.emitAndReturn(new kukit.kssp.quote(this.src))',
    '\x5c': 'new kukit.kssp.Backslashed(this.src, kukit.kssp.backslash)'
    });
kukit.kssp.String.prototype.process = function() {
    // collect up the value of the string, omitting the quotes
    this.txt = '';
    for (var i=1; i<this.result.length-1; i++) {
        this.txt += this.result[i].txt;
    }
};

/*
* class String2
*/
kukit.kssp.String2 = kukit.tk.mkParser('string', {
    '"': 'this.emitAndReturn(new kukit.kssp.dquote(this.src))',
    '\x5c': 'new kukit.kssp.Backslashed(this.src, kukit.kssp.backslash)'
    });
kukit.kssp.String2.prototype.process = kukit.kssp.String.prototype.process; 


/*
* class Backslashed
*/
kukit.kssp.Backslashed = kukit.tk.mkParser('backslashed', {});
kukit.kssp.Backslashed.prototype.nextStep = function(table) {
    // digest the next character and store it as txt
    var src = this.src;
    var length = src.text.length;
    if (length < src.pos + 1) {
;;;     kukit.E = 'Missing character after backslash.';
        this.emitError(kukit.E);
    } else { 
        this.result.push(new kukit.tk.Fraction(src, src.pos+1));
        this.src.pos += 1;
        this.finished = true;
    }
};
kukit.kssp.Backslashed.prototype.process = function() {
    this.txt = this.result[1].txt;
};

/*
* class MethodArgs
*
* methodargs are (a, b, c) lists.
*/
kukit.kssp.MethodArgs = kukit.tk.mkParser('methodargs', {
    "'": 'new kukit.kssp.String(this.src, kukit.kssp.quote)',
    '"': 'new kukit.kssp.String2(this.src, kukit.kssp.dquote)',
    ",": 'new kukit.kssp.comma(this.src)',
    ")": 'this.emitAndReturn(new kukit.kssp.closeparent(this.src))',
    "\/\*": 'new kukit.kssp.Comment(this.src, kukit.kssp.commentbegin)'
    });
kukit.kssp.MethodArgs.prototype.process = function() {
    this.args = [];
    var cursor = {'next': 1};
    while (cursor.next < this.result.length-1) {
        this.digestTxt(cursor, kukit.tk.Fraction, kukit.kssp.Comment);
        var value = cursor.txt;
        if (! value) {
            // allow to bail out after widow ,
            if (cursor.next == this.result.length-1) break;
            // here be a string then.
            this.expectToken(cursor, kukit.kssp.String);
            value = cursor.token.txt;
        } else {
            // Just a value, must be one word then.
            if (value.indexOf(' ') != -1) {
;;;             kukit.E = 'Wrong method argument [' + value;
;;;             kukit.E += '] : value cannot have spaces (if needed,';
;;;             kukit.E += ' quote it as a string).';
                this.emitError(kukit.E);
            }
        }
        this.args.push(value);
        if (cursor.next == this.result.length-1) break;
        this.expectToken(cursor, kukit.kssp.comma);
    }
    this.result = [];
    this.txt = '';
};

/*
* class KssSelector
*
* embedded parser to parse the selector
* KSS event selector: (has spaces in it)
*      <css selector> selector:name(id)
* KSS method selector: (has no spaces in it)
*      document:name(id) or behaviour:name(id)
*/
kukit.kssp.KssSelector = kukit.tk.mkParser('kssselector', {
    ":": '[new kukit.kssp.colon(this.src), new ' + 
        'kukit.kssp.PropValueInPseudo(this.src)]',
    "{": 'this.emitAndReturn()',
    "\/\*": 'new kukit.kssp.Comment(this.src, kukit.kssp.commentbegin)'
    });
kukit.kssp.KssSelector.prototype.process = function() {
    var name;
    var namespace = null;
    var id = null;
    var tokenindex = this.result.length - 1;
    // Find the method parms and calculate the end of css parms. (RL)
    var cycle = true;
    while (cycle && tokenindex >= 0) {
        var token = this.result[tokenindex];
        switch (token.symbol) {
            case kukit.tk.Fraction.prototype.symbol: {
                // if all spaces, go to previous one
                if (token.txt.match(/^[\r\n\t ]*$/) != null) {
                    tokenindex -= 1;
                } else {
;;;                 kukit.E = 'Wrong event selector : missing event ';
;;;                 kukit.E += 'qualifier :<EVENTNAME> ';
;;;                 kukit.E += 'or :<EVENTNAME>(<ID>).';
                    this.emitError(kukit.E);
                }
            } break;
            case kukit.kssp.Comment.prototype.symbol: {
                tokenindex -= 1;
            } break;
            default: {
                cycle = false;
            } break;
        }
    }
    // Now we found the token that must be <fraction> <colon> <propvalue>.
    tokenindex -= 2;
    if (tokenindex < 0
         || (this.result[tokenindex+2].symbol !=
                kukit.kssp.PropValueInPseudo.prototype.symbol)
         || (this.result[tokenindex+1].symbol != 
                kukit.kssp.colon.prototype.symbol)
         || (this.result[tokenindex].symbol !=
                kukit.tk.Fraction.prototype.symbol)) {
;;;     kukit.E = 'Wrong event selector : missing event qualifier ';
;;;     kukit.E += ':<EVENTNAME> or :<EVENTNAME>(<ID>).';
        this.emitError(kukit.E);
    }
    // See that the last fraction does not end with space.
    var lasttoken = this.result[tokenindex];
    var commatoken = this.result[tokenindex+1];
    var pseudotoken = this.result[tokenindex+2];
    var txt = lasttoken.txt;
    if (txt.match(/[\r\n\t ]$/) != null) {
;;;     kukit.E = 'Wrong event selector :';
;;;     kukit.E += ' space before the colon.';
        this.emitError(kukit.E);
    }
    if (! pseudotoken.value.methodName) {
;;;     kukit.E = 'Wrong event selector :';
;;;     kukit.E += ' event name cannot have spaces.';
        this.emitError(kukit.E);
    }
    if (pseudotoken.value.args.length > 1) {
;;;     kukit.E = 'Wrong event selector :';
;;;     kukit.E += ':<EVENTNAME>(<ID>) can have only one parameter.';
        this.emitError(kukit.E);
    }
    css = this.src.text.substring(this.startpos, commatoken.startpos);
    // Decide if we have an event or a method selector.
    // We have a method selector if a single word "document" or "behaviour".
    var singleword = css.replace(/[\r\n\t ]/g, ' ');
    if (singleword && singleword.charAt(0) == ' ') {
        singleword = singleword.substring(1);
    }
    var isEvent = (singleword != 'document' && singleword != 'behaviour');
    if (! isEvent) {
        // just store the single word, in case of event selectors
        css = singleword;
    }
    // create the selector.
    var id = null;
    if (pseudotoken.value.args.length == 1) {
        id = pseudotoken.value.args[0];
    }
    var name = pseudotoken.value.methodName;
    var splitname = name.split('-');
    var namespace = null;
    if (splitname.length > 2) {
;;;     kukit.E = 'Wrong event selector [' + name + '] : ';
;;;     kukit.E += 'qualifier should be :<EVENTNAME> or ';
;;;     kukit.E += ':<NAMESPACE>-<EVENTNAME>.';
        this.emitError(kukit.E);
    } else if (splitname.length == 2) { 
        name = splitname[1];
        namespace = splitname[0];
    }
    // Protect the error for better logging
;;; try {
        this.kssSelector = new kukit.rd.KssSelector(isEvent, css, name,
            namespace, id);
;;; } catch(e) {
;;;     if (e.name == 'KssSelectorError') {
;;;         // Log the message
;;;         this.emitError(e.toString());
;;;     } else {
;;;         throw e;
;;;     }
;;; }
    this.txt = '';
    this.result = [];
};

/*
* class KssRuleProcessor
*
* Rule processor that interfaces with kukit core
*/
kukit.kssp.KssRuleProcessor = function(href) {
    this.href = href;
    this.loaded = false;
    this.rules = [];
};

kukit.kssp.KssRuleProcessor.prototype.load = function() {
      // Opera does not support getDomDocument.load, so we use XMLHttpRequest
      var domDoc = new XMLHttpRequest();
      domDoc.open("GET", this.href, false);
      domDoc.send(null);
      this.txt = domDoc.responseText;
      this.loaded = true;
};

kukit.kssp.KssRuleProcessor.prototype.parse = function() {
;;; try {
        //Build a parser and parse the text into it
        var src = new kukit.tk.Cursor(this.txt);
        var parser = new kukit.kssp.Document(src, null, true);
        // Store event rules in the common list
        for (var i=0; i<parser.eventRules.length; i++) {
            var rule = parser.eventRules[i];
            // finish up the KSS on it
;;;         try {
            rule.kssSelector.setIdAndClass();
;;;         } catch(e) {
;;;             // foolishly, we don't know the position at this point
;;;             kukit.E = 'Undefined event : [';
;;;             kukit.E += rule.kssSelector.namespace;
;;;             kukit.E += ':' + rule.kssSelector.name + '].';
;;;             throw new kukit.err.tk.ParsingError(kukit.E);
;;;         }
            this.rules.push(rule);
        }
;;; } catch(e) {
;;;    // ParsingError are logged.
;;;    if (e.name == 'ParsingError') {
;;;        var msg = 'Error parsing KSS at ' + this.href;
;;;        msg += ' : ' + e.toString();
;;;        kukit.logFatal(msg);
;;;        throw msg;
;;;    } else {
;;;        throw e;
;;;    }
;;; }
};

