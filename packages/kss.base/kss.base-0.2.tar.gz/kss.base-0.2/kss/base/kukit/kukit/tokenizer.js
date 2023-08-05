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

/* Simple but effective tokenizing parser engine */

kukit.tk = {};

/*
* class _TokenBase
*/
kukit.tk._TokenBase = function() {
};

kukit.tk._TokenBase.prototype.emitError = function(msg) {
    // Use the start position of the token for the error report.
;;; var marker = this.cursor.makeMarker(this.startpos);
;;; throw kukit.err.parsingError(msg, marker);
    throw new Error(kukit.E);
};

kukit.tk._TokenBase.prototype.updateFinished = function() {
    if (! this.finished && this.cursor.text.length == this.cursor.pos) {
        if (this.isTopLevelParser) {
            this.finished = true;
        } else {
;;;         kukit.E = 'Unexpected EOF.';
            this.emitError(kukit.E);
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
    var cursor = this.cursor;
    // Search for symbol according to table.
    var best_pos = cursor.text.length;
    var best_symbol = null;
    for (var symbol in table) {
        var pos = cursor.text.indexOf(symbol, cursor.pos);
        if (pos != -1 && pos < best_pos) {
            best_pos = pos;
            best_symbol = symbol;
        }
    }
    // eat up till the symbol found (of EOF)
    if (best_pos > cursor.pos) {
        this.result.push(new kukit.tk.Fraction(cursor, best_pos));
        cursor.pos = best_pos;
    }
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

kukit.tk._ParserBase.prototype.expectToken = function(context, token) {
    var i = context.nextTokenIndex;
    if (token) {
        var symbol = token.prototype.symbol;
        if (i >= this.result.length) {
;;;         kukit.E = 'Missing token : [' + symbol + '].';
            this.emitError(kukit.E);
        } else if (this.result[i].symbol != symbol) {
;;;         kukit.E = 'Unexpected token : [' + this.result[i].symbol;
;;;         kukit.E += '] found, [' + symbol + '] was expected.';
            this.emitError(kukit.E);
        }
    } else {
        if (i >= this.result.length) {
;;;         kukit.E = 'Missing token.';
            this.emitError(kukit.E);
        }
    }
    context.token = this.result[i];
    context.nextTokenIndex += 1;
};

kukit.tk._ParserBase.prototype.resultIsNullOrNotToken = 
    function(token, currentValue) {
    return (!token || currentValue.symbol != token.prototype.symbol);
};

kukit.tk._ParserBase.prototype.notInTokens = 
    function(context, token1, token2, token3, token4) {
    var i = context.nextTokenIndex;
    var currentValue = this.result[i];
    return !(
        (i >= this.result.length) ||
        (this.resultIsNullOrNotToken(token1, currentValue) &&
        this.resultIsNullOrNotToken(token2, currentValue) &&
        this.resultIsNullOrNotToken(token3, currentValue) &&
        this.resultIsNullOrNotToken(token4, currentValue))
        );
};

kukit.tk._ParserBase.prototype.digestTxt =
    function(context, token1, token2, token3, token4) {
    // digests the txt from the tokens, ignores given token
    // plus whitespace removal
    this.digestExactTxt(context, token1, token2, token3, token4);
    context.txt = this.removeWhitespacesAndTrim(context.txt);
};

kukit.tk._ParserBase.prototype.digestExactTxt =
    function(context, token1, token2, token3, token4) {
    // digests the txt from the tokens, ignores given token
    // exact value: no whitespace removal
    var result = '';
    while (this.notInTokens(context, token1, token2, token3, token4)) {
        result += this.result[context.nextTokenIndex].txt;
        context.nextTokenIndex ++;
        }
    context.txt = result;
};


kukit.tk._ParserBase.prototype.removeWhitespaces = function(txt) {
    // removes ws but leaves leading and trailing one
    if (txt != ' ') { //speedup only
        txt = txt.replace(/[\r\n\t ]+/g, ' ');
    }
    return txt;
};
    
kukit.tk._ParserBase.prototype.removeWhitespacesAndTrim = function(txt) {
    txt = this.removeWhitespaces(txt);
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
kukit.tk.Fraction = function(cursor, endpos) {
    this.txt = cursor.text.substring(cursor.pos, endpos);
    this.startpos = cursor.pos;
    this.endpos = cursor.pos;
    this.finished = true;
};
kukit.tk.Fraction.prototype.symbol = 'fraction';


/* Factories to make tokens and parsers */

kukit.tk.mkToken = function(symbol, txt) {
    // Poor man's subclassing.
    f = function(cursor) {
        this.cursor = cursor;
        this.startpos = cursor.pos;
        if (cursor.text.substr(cursor.pos, txt.length) != txt) {
;;;         kukit.E = 'Unexpected token : [';
;;;         kukit.E += cursor.text.substr(cursor.pos, txt.length) + '] found,';
;;;         kukit.E += ' [' + txt + '] was expected.';
            this.emitError(kukit.E);
        } else {
            cursor.pos += txt.length;
            this.finished = true;
        }
        this.endpos = cursor.pos;
        //this.cursor = null;
    };
    f.prototype = new kukit.tk._TokenBase;
    f.prototype.symbol = symbol;
    f.prototype.txt = txt;
    return f;
};

kukit.tk.mkParser = function(symbol, table) {
    // Poor man's subclassing.
    f = function(cursor, tokenClass, isTopLevelParser) {
        this.cursor = cursor;
        this.startpos = cursor.pos;
        this.finished = false;
        this.isTopLevelParser = isTopLevelParser;
        this.result = [];
        if (tokenClass) {
            // Reentry with starting token propagated.
            this.result.push(new tokenClass(this.cursor));
        }
        this.updateFinished();
        while (!this.finished) {
            this.nextStep(table);
            this.updateFinished();
        }
        this.endpos = cursor.pos;
        // post processing
        this.process();
        
        //this.cursor = null;
    };
    f.prototype = new kukit.tk._ParserBase;
    f.prototype.symbol = symbol;
    return f;
};

/*
* class Cursor
*/
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
