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

kukit.kssp.openComment = kukit.tk.mkToken('openComment', "\/\*");
kukit.kssp.closeComment = kukit.tk.mkToken('closeComment', "\*\/");
kukit.kssp.openBrace = kukit.tk.mkToken('openBrace', "{");
kukit.kssp.closeBrace = kukit.tk.mkToken('closeBrace', "}");
kukit.kssp.openBracket = kukit.tk.mkToken('openBracket', "[");
kukit.kssp.closeBracket = kukit.tk.mkToken('closeBracket', "]");
kukit.kssp.openParent = kukit.tk.mkToken('openParent', "(");
kukit.kssp.closeParent = kukit.tk.mkToken('closeParent', ")");
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
    "\/\*": 'new kukit.kssp.Comment(this.cursor, kukit.kssp.openComment)',
    "{": 'new kukit.kssp.Block(this.cursor, kukit.kssp.openBrace)'
    });
kukit.kssp.Document.prototype.process = function() {
    this.eventRules = [];
    // Parse all tokens (including first and last)
    var context = {'nextTokenIndex': 0};
    while (context.nextTokenIndex < this.result.length) {
        this.digestTxt(context, kukit.tk.Fraction, kukit.kssp.Comment);
        var key = context.txt;
        if (! key) {
            break;
        }
        this.expectToken(context, kukit.kssp.Block);
        var block = context.token;
        var rules = block.parseSelectors(key);
        this.addRules(rules);
    }
    this.result = [];
    this.txt = '';
};

kukit.kssp.Document.prototype.addRules = function(rules) {
    // Create the event rules.
    for(var i=0; i<rules.length; i++) {
        this.eventRules.push(rules[i]);
    };
};

/*
* class Comment 
*/
kukit.kssp.Comment = kukit.tk.mkParser('comment', {
    // it's not 100% good, but will do
    "\*\/": 'this.emitAndReturn(new kukit.kssp.closeComment(this.cursor))'
    });
kukit.kssp.Comment.prototype.process = function() {
    this.result = [];
    this.txt = ' ';
};

/*
* class Block 
*/
kukit.kssp.Block = kukit.tk.mkParser('block', {
    ";": 'new kukit.kssp.semicolon(this.cursor)',
    ":": '[new kukit.kssp.colon(this.cursor), new kukit.kssp.PropValue(this.cursor)]',
    "}": 'this.emitAndReturn(new kukit.kssp.closeBrace(this.cursor))'
    });
kukit.kssp.Block.prototype.process = function() {
    //this.parms = {};
    this.eventFullNames = {};
    this.actions = new kukit.rd.ActionSet();
    // Parse all tokens (except first and last)
    var context = {'nextTokenIndex': 1};
    while (context.nextTokenIndex < this.result.length-1) {
        this.digestTxt(context, kukit.tk.Fraction, kukit.kssp.Comment);
        var key = context.txt;
        if (! key) {
            break;
        }
        this.expectToken(context, kukit.kssp.colon);
        this.expectToken(context, kukit.kssp.PropValue);
        // store the wrapped prop
        this.addDeclaration(key, context.token.value);
        if (context.nextTokenIndex == this.result.length-1) break;
        this.expectToken(context, kukit.kssp.semicolon);
    }
    this.result = [];
    this.txt = '';
};

kukit.kssp.Block.prototype.parseSelectors = function(key) {
    // Parse the part in an embedded parser
    var cursor = new kukit.tk.Cursor(key + ' ');
    var parser = new kukit.kssp.KssSelectors(cursor, null, true);
    var results = [];
    var hasFullNames = false;
    for(var eventFullName in this.eventFullNames) {
        var hasFullNames = true;
        var found = false;
        for(var i=0; i< parser.selectors.length; ++i) {
            var fullName = '';
            var kssSelector = parser.selectors[i];
            if (kssSelector.namespace) {
                fullName = kssSelector.namespace + '-';
            }
            fullName += kssSelector.name;
            if (fullName == eventFullName) {
                var eventParameters = this.eventFullNames[fullName];
                var eventRule;
                if (typeof(eventParameters)!='undefined') {
                    eventRule = new kukit.rd.EventRule(kssSelector,
                                                eventParameters, this.actions);
                }
                else{
                    eventRule = new kukit.rd.EventRule(kssSelector,
                                                {}, this.actions);
                }
                results.push(eventRule);
                found = true;
            }
        }
        if (! found){
;;;         kukit.E = 'Wrong value for evt-[<NAMESPACE>-]<EVENTNAME> [' + eventFullName + '] : ';
;;;         kukit.E += '<NAMESPACE>-<EVENTNAME> should exist in the event of the selectors.';
            this.emitError(kukit.E);
        }
    }
    if (! hasFullNames){
        for(var i=0; i< parser.selectors.length; ++i) {
            var kssSelector = parser.selectors[i];
            eventRule = new kukit.rd.EventRule(kssSelector,
                                               {}, this.actions);
            results.push(eventRule);
        }
    }
    return results;
}

kukit.kssp.Block.prototype.addEventDeclaration = function(key, splitkey, value) {

    // evt-<EVTNAME>-<PARAMETER>: <VALUE>
    // evt-<NAMESPACE>-<EVTNAME>-<PARAMETER>: <VALUE>
;;; if (splitkey.length < 3) {
;;;     kukit.E = 'Wrong rule key : "' + key + '". ';
;;;     kukit.E += 'KSS rule key must be "<ACTIONNAME>-<PARAMETER>"';
;;;     kukit.E += ' or "<NAMESPACE>-<ACTIONNAME>-<PARAMETER>" or ';
;;;     kukit.E += '"evt-<EVENTNAME>-<PARAMETER>" or ';
;;;     kukit.E += '"evt-<NAMESPACE>-<EVENTNAME>-<PARAMETER>".';
;;;     this.emitError(kukit.E);
;;; }
    var eventNamespace;
    var eventName;
    var eventKey;
    var eventFullName;
    if (splitkey.length == 3) {
        // evt-<EVENTNAME>-<PARAMETER>: <VALUE>
        eventName =  splitkey[1];
        eventKey = splitkey[2];
        eventFullName = eventName;
    } else {
        // evt-<NAMESPACE>-<EVENTNAME>-<PARAMETER>: <VALUE>
        eventNamespace = splitkey[1];
        eventName = splitkey[2];
        eventKey = splitkey[3];
        eventFullName = eventNamespace + '-' + eventName;
    }
;;; if (value.isMethod != false) {
;;;     kukit.E = 'Wrong value for key [' + key + '] : ';
;;;     kukit.E += 'value providers are not ';
;;;     kukit.E += 'allowed as value for ';
;;;     kukit.E += 'evt-[<NAMESPACE>-]<EVENTNAME>-<PARAMETER> keys.';
;;;     this.emitError(kukit.E);
;;; }
    var eventParameters = this.eventFullNames[eventFullName];
    if (typeof(eventParameters) == 'undefined') {
        this.eventFullNames[eventFullName] = {};
        eventParameters = this.eventFullNames[eventFullName];
    }
    eventParameters[eventKey] = value.txt;
}

kukit.kssp.Block.prototype.addActionDeclaration = function(key, splitkey, value) {
    // action-server: <ACTIONNAME>
    // action-client: <ACTIONNAME>
    // action-client: <NAMESPACE>-<ACTIONNAME>
    // action-cancel: <ACTIONNAME>
    // action-cancel: <NAMESPACE>-<ACTIONNAME>
;;; if (splitkey.length != 2) {
;;;     kukit.E = 'Wrong key [' + key + '] : ';
;;;     kukit.E += 'action-<QUALIFIER> keys can have only one dash.';
;;;     this.emitError(kukit.E);
;;;     }
;;; if (value.isMethod != false) {
;;;     kukit.E = 'Wrong value for key [' + key + '] : ';
;;;     kukit.E += 'value providers are not ';
;;;     kukit.E += 'allowed for action-<QUALIFIER> keys.';
;;;     this.emitError(kukit.E);
;;;     }
    var atab = {'server': 'S', 'client': 'C', 'cancel': 'X'};
    var actionType = atab[splitkey[1]];
;;; if (! actionType) {
;;;     kukit.E = 'Wrong key [' + key + '] : ';
;;;     kukit.E += 'qualifier in action-<QUALIFIER> keys must be ';
;;;     kukit.E += '"server" or "client" or "cancel".'; 
;;;     this.emitError(kukit.E);
;;;     }    
;;; // force value to be <ACTIONNAME> or <NAMESPACE>-<ACTIONNAME>
;;; var splitvalue = value.txt.split('-');
;;; if (splitvalue.length > 2) {
;;;     kukit.E = 'Wrong value for key [' + key + '] : ';
;;;     kukit.E += 'value must be <ACTIONNAME> or <NAMESPACE>';
;;;     kukit.E += '-<ACTIONNAME> for action-<QUALIFIER> keys.';
;;;     this.emitError(kukit.E);
;;;     }
    // set it
    var action = this.actions.getOrCreateAction(value.txt);
    if (actionType != 'X' || action.type == null) {
        action.setType(actionType);
    } else {
        this.actions.deleteAction(value.txt);
    }
}

kukit.kssp.Block.prototype.addActionError = function(action, key, value) {
    // <ACTIONNAME>-error: <VALUE>
    // default-error: <VALUE>
;;; if (value.isMethod == true) {
;;;     kukit.E = 'Wrong value for key [' + key + '] : ';
;;;     kukit.E += 'value providers are not ';
;;;     kukit.E += 'allowed for <ACTIONNAME>-error keys.';
;;;     this.emitError(kukit.E);
;;; }
    action.setError(value.txt);
    // also create the action for the error itself.
    var err_action = this.actions.getOrCreateAction(value.txt);
    err_action.setType('E');
}

kukit.kssp.Block.prototype.addActionParameter = function(action, key, value) {
    var ppRegistries = {
        '': kukit.pprovidersGlobalRegistry,
        'kssSelector': kukit.sr.pproviderSelRegistry,
        'kssSubmitForm': kukit.fo.pproviderFormRegistry
    };

    // <ACTIONNAME>-<KEY>: <VALUE>
    // default-<KEY>: <VALUE>
    // 
    // value may be either txt or method parms, 
    // and they get stored with the wrapper.
    // 
    // Check the syntax of the value at this point.
    // This will also set the value providers on the value
    // (from check).
    //
    // Figure out which registry to use.
    var registry = ppRegistries[key];
    if (typeof(registry) == 'undefined') {
        // use default pproviders
        registry = ppRegistries[''];
    }
    //
    try {
        // Check also sets the value provider on the value.
        value.check(registry);
    } catch(e) {
;;;     kukit.E = 'Error in value : ' + e + '.';
        this.emitError(kukit.E);
    }
    action.parms[key] = value;
}

kukit.kssp.Block.prototype.addDeclaration = function(key, value) {
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
        this.addEventDeclaration(key, splitkey, value);
    } else if (name == 'action') {
        this.addActionDeclaration(key, splitkey, value);
    } else {
        // <ACTIONNAME>-<KEY>: <VALUE>
        // <NAMESPACE>-<ACTIONNAME>-<KEY>: <VALUE>
        // <ACTIONNAME>-error: <VALUE>
        // <NAMESPACE>-<ACTIONNAME>-error: <VALUE>
        // default-<KEY>: <VALUE>
        // default-error: <VALUE>
        var actionName;
        var actionKey;
        if (splitkey.length == 2) {
            // <ACTIONNAME>-<KEY>: <VALUE>
            // <ACTIONNAME>-error: <VALUE>
            // default-<KEY>: <VALUE>
            // default-error: <VALUE>
            actionName =  splitkey[0];
            actionKey = splitkey[1];
        } else {
            // <NAMESPACE>-<ACTIONNAME>-<KEY>: <VALUE>
            // <NAMESPACE>-<ACTIONNAME>-error: <VALUE>
            actionName = splitkey[0] + '-' + splitkey[1];
            actionKey = splitkey[2];
        }
        var action = this.actions.getOrCreateAction(actionName);
        if (actionKey == 'error') {
            this.addActionError(action, key, value);
        } else {
            this.addActionParameter(action, actionKey, value);
        }
    }
};

/*
* class PropValue
*/
kukit.kssp.PropValue = kukit.tk.mkParser('propValue', {
    ";": 'this.emitAndReturn()',
    "}": 'this.emitAndReturn()',
    ")": 'this.emitAndReturn()',
    ",": 'this.emitAndReturn()',
    "'": 'new kukit.kssp.String(this.cursor, kukit.kssp.quote)',
    '"': 'new kukit.kssp.String2(this.cursor, kukit.kssp.dquote)',
    "\/\*": 'new kukit.kssp.Comment(this.cursor, kukit.kssp.openComment)',
    "(": 'new kukit.kssp.MethodArgs(this.cursor, kukit.kssp.openParent)'
    });
kukit.kssp.PropValue.prototype.process = function() {
    // Parse all tokens (including first and last)
    var context = {'nextTokenIndex': 0};
    this.digestTxt(context, kukit.tk.Fraction, kukit.kssp.Comment);
    this.txt = '';
    var txt = context.txt;
    if (this.notInTokens(context, kukit.kssp.String)) {
        // The previous txt must be all whitespace.
        if (txt) {
;;;         kukit.E = 'Wrong value : unallowed characters [' + txt + ']';
;;;         kukit.E += ' before a string.';
            this.emitError(kukit.E);
        }
        // the next one must be a string.
        this.expectToken(context, kukit.kssp.String);
        this.produceTxt(context.token.txt);
    } else if (this.notInTokens(context, kukit.kssp.MethodArgs)) {
        // see if not empty and has no spaces in it 
        if (! txt || txt.indexOf(' ') != -1) {
;;;         kukit.E = 'Wrong value : method name [' + txt + '] cannot ';
;;;         kukit.E += 'have spaces.';
            this.emitError(kukit.E);
        }
        // the next one must be the rules
        this.expectToken(context, kukit.kssp.MethodArgs);
        this.value = new this.valueClass(txt, context.token.args);
    } else {
        // not a string or method: check if we allowed multiword.
        if (! this.multiword_allowed && txt.indexOf(' ') != -1) {
;;;         kukit.E = 'Wrong value : [' + txt + '] cannot have spaces.';
            this.emitError(kukit.E);
        }
        this.produceTxt(txt);
    }
    // see what's after
    if (context.nextTokenIndex < this.result.length) {
        this.digestTxt(context, kukit.tk.Fraction, kukit.kssp.Comment);
        // we have to be at the end and have no text after
        if (context.nextTokenIndex < this.result.length || context.txt) {
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
kukit.kssp.PropValueInMethod = kukit.tk.mkParser('propValue', {
    ";": 'this.emitAndReturn()',
    "}": 'this.emitAndReturn()',
    ")": 'this.emitAndReturn()',
    "]": 'this.emitAndReturn()',
    ",": 'this.emitAndReturn()',
    "'": 'new kukit.kssp.String(this.cursor, kukit.kssp.quote)',
    '"': 'new kukit.kssp.String2(this.cursor, kukit.kssp.dquote)',
    "\/\*": 'new kukit.kssp.Comment(this.cursor, kukit.kssp.openComment)'
    });
kukit.kssp.PropValueInMethod.prototype.multiword_allowed = false;
kukit.kssp.PropValueInMethod.prototype.process =
    kukit.kssp.PropValue.prototype.process;
kukit.kssp.PropValueInMethod.prototype.produceTxt = function(txt) {
    // txt parms are returned unwrapped
    this.txt = txt;
};

/*
* class EventValue
*
* PropValue in pseudo must be single word with no spaces around.
*/
kukit.kssp.EventValue = kukit.tk.mkParser('propValue', {
    "{": 'this.emitAndReturn()',
    " ": 'this.emitAndReturn()',
    "\t": 'this.emitAndReturn()',
    "\n": 'this.emitAndReturn()',
    "\r": 'this.emitAndReturn()',
    "\/\*": 'this.emitAndReturn()',
    ":": 'this.emitAndReturn()',
    "(": '[new kukit.kssp.openParent(this.cursor), new kukit.kssp.PropValue(this.cursor)]',
    ")": 'this.emitAndReturn(new kukit.kssp.closeParent(this.cursor))'
    });
kukit.kssp.EventValue.prototype.multiword_allowed = false;
kukit.kssp.EventValue.prototype.process = function() {
    // Parse all tokens (including first and last)
    var context = {'nextTokenIndex': 0};
    this.digestTxt(context, kukit.tk.Fraction, kukit.kssp.Comment);
    this.txt = '';
    var txt = context.txt;
    if (this.notInTokens(context, kukit.kssp.String)) {
        // The previous txt must be all whitespace.
        if (txt) {
;;;         kukit.E = 'Wrong value : unallowed characters [' + txt + ']';
;;;         kukit.E += ' before a string.';
            this.emitError(kukit.E);
        }
        // the next one must be a string.
        this.expectToken(context, kukit.kssp.String);
        this.produceTxt(context.token.txt);
    } else if (this.notInTokens(context, kukit.kssp.openParent)) {
        this.expectToken(context, kukit.kssp.openParent);
        this.expectToken(context, kukit.kssp.PropValue);
        this.value = new kukit.rd.KssEventValue(txt, context.token.value);
        this.digestTxt(context, kukit.tk.Fraction, kukit.kssp.Comment);
        // we have to be at the end and have no text after
        if (context.txt) {
;;;         kukit.E = 'Wrong event selector : [' + context.txt; 
;;;         kukit.E += '] is not expected before the closing';
;;;         kukit.E += ' parenthesis. :<EVENTNAME>(<ID>) can have';
;;;         kukit.E += ' only one parameter.';
            this.emitError(kukit.E);
        }
        // eat up everything before the closing parent
        this.expectToken(context, kukit.kssp.closeParent);
    } else {
        // not a string or method: check if we allowed multiword.
        if (! this.multiword_allowed && txt.indexOf(' ') != -1) {
;;;         kukit.E = 'Wrong value : [' + txt + '] cannot have spaces.';
            this.emitError(kukit.E);
        }
        this.produceTxt(txt);
    }
    // see what's after
    if (context.nextTokenIndex < this.result.length) {
        this.digestTxt(context, kukit.tk.Fraction, kukit.kssp.Comment);
        // we have to be at the end and have no text after
        if (context.nextTokenIndex < this.result.length || context.txt) {
;;;         kukit.E = 'Excess characters after the property value';
            this.emitError(kukit.E);
        }
    }
    this.result = [];
};

kukit.kssp.EventValue.prototype.produceTxt = function(txt) {
    // txt parms are returned embedded
    this.value = new kukit.rd.KssEventValue(txt, null);
};

/*
* class String
*/
kukit.kssp.String = kukit.tk.mkParser('string', {
    "'": 'this.emitAndReturn(new kukit.kssp.quote(this.cursor))',
    '\x5c': 'new kukit.kssp.Backslashed(this.cursor, kukit.kssp.backslash)'
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
    '"': 'this.emitAndReturn(new kukit.kssp.dquote(this.cursor))',
    '\x5c': 'new kukit.kssp.Backslashed(this.cursor, kukit.kssp.backslash)'
    });
kukit.kssp.String2.prototype.process = kukit.kssp.String.prototype.process; 

/*
* class StringInSelector
*/
kukit.kssp.StringInSelector = kukit.tk.mkParser('string', {
    "'": 'this.emitAndReturn(new kukit.kssp.quote(this.cursor))',
    '\x5c': 'new kukit.kssp.Backslashed(this.cursor, kukit.kssp.backslash)'
    });
kukit.kssp.StringInSelector.prototype.process = function() {
    // collect up the value of the string, including the quotes
    this.txt = '';
    for (var i=0; i<this.result.length; i++) {
        this.txt += this.result[i].txt;
    }
};

/*
* class String2InSelector
*/
kukit.kssp.String2InSelector = kukit.tk.mkParser('string', {
    '"': 'this.emitAndReturn(new kukit.kssp.dquote(this.cursor))',
    '\x5c': 'new kukit.kssp.Backslashed(this.cursor, kukit.kssp.backslash)'
    });
kukit.kssp.String2InSelector.prototype.process = kukit.kssp.StringInSelector.prototype.process; 

/*
* class Backslashed
*/
kukit.kssp.Backslashed = kukit.tk.mkParser('backslashed', {});
kukit.kssp.Backslashed.prototype.nextStep = function(table) {
    // digest the next character and store it as txt
    var cursor = this.cursor;
    var length = cursor.text.length;
    if (length < cursor.pos + 1) {
;;;     kukit.E = 'Missing character after backslash.';
        this.emitError(kukit.E);
    } else { 
        this.result.push(new kukit.tk.Fraction(cursor, cursor.pos+1));
        this.cursor.pos += 1;
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
    "'": 'new kukit.kssp.String(this.cursor, kukit.kssp.quote)',
    '"': 'new kukit.kssp.String2(this.cursor, kukit.kssp.dquote)',
    ",": 'new kukit.kssp.comma(this.cursor)',
    ")": 'this.emitAndReturn(new kukit.kssp.closeParent(this.cursor))',
    "(": 'new kukit.kssp.MethodArgs(this.cursor, kukit.kssp.openParent)',
    "\/\*": 'new kukit.kssp.Comment(this.cursor, kukit.kssp.openComment)'
    });
kukit.kssp.MethodArgs.prototype.process = function() {
    this.args = [];
    // Parse all tokens (except first and last)
    var context = {'nextTokenIndex': 1};
    while (context.nextTokenIndex < this.result.length-1) {
        this.digestTxt(context, kukit.tk.Fraction, kukit.kssp.Comment);
        var value = context.txt;
        if (! value) {
            // allow to bail out after widow ,
            if (context.nextTokenIndex == this.result.length-1) break;
            // here be a string then.
            this.expectToken(context, kukit.kssp.String);
            value = context.token.txt;
        } else {
            // Just a value, must be one word then.
            if (value.indexOf(' ') != -1) {
;;;             kukit.E = 'Wrong method argument [' + value;
;;;             kukit.E += '] : value cannot have spaces (if needed,';
;;;             kukit.E += ' quote it as a string).';
                this.emitError(kukit.E);
            }
        }
        var valueClass;
        var args;
        var providedValue;
        if (this.notInTokens(context, kukit.kssp.MethodArgs)){
            this.expectToken(context, kukit.kssp.MethodArgs);
             valueClass = kukit.rd.KssMethodValue;
             args = context.token.args;
             providedValue = new valueClass(value, args);
        } else {
             // XXX This should be wrapped too !
             //valueClass = kukit.rd.KssTextValue;
             //providedValue = new valueClass(value);
             providedValue = value;
        }
        this.args.push(providedValue);
        if (context.nextTokenIndex == this.result.length-1) break;
        this.expectToken(context, kukit.kssp.comma);
    }
    this.result = [];
    this.txt = '';
};

/*
* class KssSelectors
*
* embedded parser to parse the block of selectors
* KSS event selector: (has spaces in it)
*      <css selector> selector:name(id)
* KSS method selector: (has no spaces in it)
*      document:name(id) or behaviour:name(id)
*/
kukit.kssp.KssSelectors = kukit.tk.mkParser('kssselectors', {
    "'": 'new kukit.kssp.StringInSelector(this.cursor, kukit.kssp.quote)',
    '"': 'new kukit.kssp.String2InSelector(this.cursor, kukit.kssp.dquote)',
    ",": 'new kukit.kssp.comma(this.cursor)',
    "{": 'this.emitAndReturn()',
    "\/\*": 'new kukit.kssp.Comment(this.cursor, kukit.kssp.openComment)'
    });
kukit.kssp.KssSelectors.prototype.process = function() {
    this.selectors = [];
    // Parse all tokens (including first and last)
    var context = {'nextTokenIndex': 0};
    while (context.nextTokenIndex < this.result.length) {
        this.digestTxt(context, kukit.tk.Fraction, kukit.kssp.Comment,
            kukit.kssp.String, kukit.kssp.String2);
        var cursor = new kukit.tk.Cursor(context.txt + ' ')
        var parser = new kukit.kssp.KssSelector(cursor, null, true);
        this.selectors.push(parser.kssSelector);
        if (context.nextTokenIndex == this.result.length) break;
        this.expectToken(context, kukit.kssp.comma);
        if (context.nextTokenIndex == this.result.length) {
;;;        kukit.E = 'Wrong event selector : trailing comma';
           this.emitError(kukit.E); 
        }
    };
    this.result = [];
    this.txt = '';
};

/*
* class KssSelector
*
* embedded parser to parse the selector
* KSS event selector: (has spaces in it)
*      <css selector> selector:name(id)
*      <css selector> selector:name(pprov(id))
* kss method selector: (has no spaces in it)
*      document:name(id) or behaviour:name(id)
*      document:name(pprov(id)) or behaviour:name(pprov(id))
*/
kukit.kssp.KssSelector = kukit.tk.mkParser('kssselector', {
    ":": '[new kukit.kssp.colon(this.cursor), new ' + 
        'kukit.kssp.EventValue(this.cursor)]',
    "{": 'this.emitAndReturn()',
    "\/\*": 'new kukit.kssp.Comment(this.cursor, kukit.kssp.openComment)'
    });
kukit.kssp.KssSelector.prototype.process = function() {
    var name;
    var namespace = null;
    var id = null;
    var tokenIndex = this.result.length - 1;
    // Find the method parms and calculate the end of css parms. (RL)
    var cycle = true;
    while (cycle && tokenIndex >= 0) {
        var token = this.result[tokenIndex];
        switch (token.symbol) {
            case kukit.tk.Fraction.prototype.symbol: {
                // if all spaces, go to previous one
                if (token.txt.match(/^[\r\n\t ]*$/) != null) {
                    tokenIndex -= 1;
                } else {
;;;                 kukit.E = 'Wrong event selector : missing event ';
;;;                 kukit.E += 'qualifier :<EVENTNAME> ';
;;;                 kukit.E += 'or :<EVENTNAME>(<ID>).';
                    this.emitError(kukit.E);
                }
            } break;
            case kukit.kssp.Comment.prototype.symbol: {
                tokenIndex -= 1;
            } break;
            default: {
                cycle = false;
            } break;
        }
    }
    // Now we found the token that must be <fraction> <colon> <propValue>.
    tokenIndex -= 2;
    if (tokenIndex < 0
         || (this.result[tokenIndex+2].symbol !=
                kukit.kssp.EventValue.prototype.symbol)
         || (this.result[tokenIndex+1].symbol != 
                kukit.kssp.colon.prototype.symbol)
         || (this.result[tokenIndex].symbol !=
                kukit.tk.Fraction.prototype.symbol)) {
;;;     kukit.E = 'Wrong event selector : missing event qualifier ';
;;;     kukit.E += ':<EVENTNAME> or :<EVENTNAME>(<ID>).';
        this.emitError(kukit.E);
    }
    // See that the last fraction does not end with space.
    var lasttoken = this.result[tokenIndex];
    var commatoken = this.result[tokenIndex+1];
    var pseudotoken = this.result[tokenIndex+2];
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
    css = this.cursor.text.substring(this.startpos, commatoken.startpos);
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
    var ppid = null;
    if (pseudotoken.value.arg) {
        // We have something in the parentheses after the event name.
        if (pseudotoken.value.arg.isMethod) {
            // we have a param provider here. Just store.
            ppid = pseudotoken.value.arg;
            // Check its syntax too.
            ppid.check(kukit.pprovidersGlobalRegistry);
        } else {
            // just an id. Express in txt.
            id = pseudotoken.value.arg.txt;
        }
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
            namespace, id, ppid);
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
        var cursor = new kukit.tk.Cursor(this.txt);
        var parser = new kukit.kssp.Document(cursor, null, true);
        // Store event rules in the common list
        for (var i=0; i<parser.eventRules.length; i++) {
            var rule = parser.eventRules[i];
            rule.kssSelector.prepareId();
            this.rules.push(rule);
        }
;;; } catch(e) {
;;;    // ParsingError are logged.
;;;    if (e.name == 'ParsingError' || e.name == 'UndefinedEventError') {
;;;        throw kukit.err.kssParsingError(e, this.href);
;;;    } else {
;;;        throw e;
;;;    }
;;; }
};

