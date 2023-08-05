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

    this.assertParsingError = function(pclass, cursor, tokenClass, eofOk, errtxt, errpos) {
        if (! kukit.isDevelMode) {
            return; }
        var exc = null;
        try {
            new pclass(cursor, tokenClass, eofOk);
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
        if (! kukit.isDevelMode) {
            return; }
        var exc = null;
        try {
            throw kukit.err.parsingError('Error happened');
        } catch(e) {
            exc = e;
        }
        this.assertNotEquals(exc, null);
        this.assertEquals(exc.name, 'ParsingError');
        // test here under tries to discriminate IE
        // it does work for IE 6.0.2900.2180.xpsp_sp2
        // it does not work at least for IE 6.0.2800.1106
        if (typeof(exc.number) == 'number') {
            // IE
            this.assertEquals(exc.description, 'Error happened');
        } else {
            // toString result is browser dependent.
            // colon in FF
            // dash in Safari
            // reason for the indexOf below
            var toString = exc.toString();
            this.assertTrue(toString.indexOf('ParsingError') != -1, '"ParsingError" not in toString() : ' + toString);
            this.assertTrue(toString.indexOf('Error happened') != -1, '"Error happened" not in toString() : ' + toString);
            this.assertEquals(exc.message, 'Error happened');
        };
        this.assertEquals(exc.errpos, null);
        this.assertEquals(exc.errrow, null);
        this.assertEquals(exc.errcol, null);
    };

    this.testExceptionWithRowCol = function() {
        if (! kukit.isDevelMode) {
            return; }
        var exc = null;
        var cursor = new kukit.tk.Cursor('1234\n1234\n1234\n1234\n');
        var marker = cursor.makeMarker(13);
        try {
            throw kukit.err.parsingError('Error happened', marker);
        } catch(e) {
            exc = e;
        }
        this.assertNotEquals(exc, null);
        this.assertEquals(exc.name, 'ParsingError');
        // test here under tries to discriminate IE
        // it does work for IE 6.0.2900.2180.xpsp_sp2
        // it does not work at least for IE 6.0.2800.1106
        if (typeof(exc.number) == 'number') {
            // IE
            this.assertEquals(exc.description, 'Error happened, at row 3, column 4');
        } else {
            // toString result is browser dependent.
            // colon in FF
            // dash in Safari
            // reason for the indexOf below
            var toString = exc.toString();
            this.assertTrue(toString.indexOf('ParsingError') != -1, '"ParsingError" not in toString() : ' + toString);
            this.assertTrue(toString.indexOf('Error happened, at row 3, column 4') != -1, '"Error happened, at row 3, column 4" not in toString() : ' + toString);
            this.assertEquals(exc.message, 'Error happened, at row 3, column 4');
        };
        this.assertEquals(exc.info.kw.errpos, 13);
        this.assertEquals(exc.info.kw.errrow, 3);
        this.assertEquals(exc.info.kw.errcol, 4);
    };

    this.testBasic = function() {
        // Basic parser creation
        var txt="abc def";
        var cursor = new kukit.tk.Cursor(txt);

        kukit.tk.openBrace = kukit.tk.mkToken('openBrace', '{');
        kukit.tk.openBracket = kukit.tk.mkToken('openBracket', '[');

        var pf = kukit.tk.mkParser('block', {
            '[': 'this.emitAndReturn(new kukit.tk.openBracket(this.cursor))',
            '{': 'new kukit.tk.openBrace(this.cursor)'
            });

        var parser = new pf(cursor, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 1);
        this.assertEquals(parser.result[0].symbol, 'fraction');
        this.assertEquals(parser.result[0].txt, 'abc def');
        
        this.assertParsingError(pf, cursor, null, false, 'Unexpected EOF');
        
        var txt="abc{def";
        var cursor = new kukit.tk.Cursor(txt);
        var parser = new pf(cursor, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 3);
        
        var txt="abc[def";
        var cursor = new kukit.tk.Cursor(txt);
        var parser = new pf(cursor, null, true);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 2);
        this.assertEquals(cursor.pos, 4);
    };
    
    this.testRecursive = function() {
        // Recursive parser creation
        var txt="a[bc{de[f}ghi";
        var cursor = new kukit.tk.Cursor(txt);

        kukit.tk.openBrace = kukit.tk.mkToken('openBrace', '{');
        kukit.tk.openBracket = kukit.tk.mkToken('openBracket', '[');
        kukit.tk.closeBrace = kukit.tk.mkToken('closeBrace', '}');
        kukit.tk.wrappedBracket = kukit.tk.mkToken('wrappedBracket', '[');

        kukit.tk.global = kukit.tk.mkParser('global', {
            '[': 'new kukit.tk.openBracket(this.cursor)',
            '{': 'new kukit.tk.inside(this.cursor, kukit.tk.openBrace)'
            });
            
        kukit.tk.inside = kukit.tk.mkParser('inside', {
            '[': 'new kukit.tk.wrappedBracket(this.cursor)',
            '}': 'this.emitAndReturn(new kukit.tk.closeBrace(this.cursor))'
            });

        var parser = new kukit.tk.global(cursor, null, true);
        //this.printDebug(parser);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 5);
        this.assertEquals(parser.result[0].symbol, 'fraction');
        this.assertEquals(parser.result[0].txt, 'a');
        this.assertEquals(parser.result[1].symbol, 'openBracket');
        this.assertEquals(parser.result[1].txt, '[');
        this.assertEquals(parser.result[2].symbol, 'fraction');
        this.assertEquals(parser.result[2].txt, 'bc');
        this.assertEquals(parser.result[3].symbol, 'inside');
        
        var itoken = parser.result[3]
        this.assertEquals(itoken.result.length, 5);
        this.assertEquals(itoken.result[0].symbol, 'openBrace');
        this.assertEquals(itoken.result[0].txt, '{');
        this.assertEquals(itoken.result[1].symbol, 'fraction');
        this.assertEquals(itoken.result[1].txt, 'de');
        this.assertEquals(itoken.result[2].symbol, 'wrappedBracket');
        this.assertEquals(itoken.result[2].txt, '[');
        this.assertEquals(itoken.result[3].symbol, 'fraction');
        this.assertEquals(itoken.result[3].txt, 'f');
        this.assertEquals(itoken.result[4].symbol, 'closeBrace');
        this.assertEquals(itoken.result[4].txt, '}');

        this.assertEquals(parser.result[4].symbol, 'fraction');
        this.assertEquals(parser.result[4].txt, 'ghi');

        //
        // Testing for unexpected eof handling
        //

        var txt="";
        var cursor = new kukit.tk.Cursor(txt);
        parser = new kukit.tk.global(cursor, null, true);
        //this.printDebug(parser);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 0);

        // In particular, the next one should not raise unexpected eof.
        var txt="{}";
        var cursor = new kukit.tk.Cursor(txt);
        parser = new kukit.tk.global(cursor, null, true);
        //this.printDebug(parser);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 1);

    };
    
    this.testProcessing = function() {
        // Processing parser creation
        var txt="abc'de\\'f'ghi";
        var cursor = new kukit.tk.Cursor(txt);

        kukit.tk.quote = kukit.tk.mkToken('quote', "'");
        kukit.tk.backslash = kukit.tk.mkToken('backslash', "\\");

        kukit.tk.global = kukit.tk.mkParser('global', {
            "'": 'new kukit.tk.string(this.cursor, kukit.tk.quote)'
            });
            
        kukit.tk.string = kukit.tk.mkParser('string', {
            "'": 'this.emitAndReturn(new kukit.tk.quote(this.cursor))',
            "\\": 'new kukit.tk.backslashed(this.cursor, kukit.tk.backslash)'
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
            var cursor = this.cursor;
            var length = cursor.text.length;
            if (length < cursor.pos + 1) {
                this.emitError('Missing character after backslash');
            } else { 
                this.result.push(new kukit.tk.Fraction(cursor, cursor.pos+1));
                this.cursor.pos += 1;
                this.finished = true;
            }
        }
        kukit.tk.backslashed.prototype.process = function() {
            this.txt = this.result[1].txt;
        }

        var parser = new kukit.tk.global(cursor, null, true);
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
        var cursor = new kukit.tk.Cursor(txt);

        kukit.tk.openBrace = kukit.tk.mkToken('openBrace', '{');
        kukit.tk.openBracket = kukit.tk.mkToken('openBracket', '[');
        kukit.tk.closeBrace = kukit.tk.mkToken('closeBrace', '}');
        kukit.tk.closeBracket = kukit.tk.mkToken('closeBracket', ']');

        kukit.tk.global = kukit.tk.mkParser('global', {
            '[': 'new kukit.tk.openBracket(this.cursor)',
            '{': 'new kukit.tk.inside(this.cursor, kukit.tk.openBrace)'
            });
            
        kukit.tk.inside = kukit.tk.mkParser('inside', {
            '}': 'this.emitAndReturn(new kukit.tk.closeBrace(this.cursor))'
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
            var embedded_cursor =new kukit.tk.Cursor(last_part);
            this.embedded_parser = new kukit.tk.embedded(embedded_cursor, null, true);
            if (this.embedded_parser == 2) {
                this.emitError('Error in embedded parser: ' + embedded_cursor.errtxt);
            }
        }

        kukit.tk.embedded = kukit.tk.mkParser('embedded', {
                '[': 'new kukit.tk.embeddedInside(this.cursor, kukit.tk.openBracket)'
            });
 
        kukit.tk.embeddedInside = kukit.tk.mkParser('embeddedInside', {
            ']': 'this.emitAndReturn(new kukit.tk.closeBracket(this.cursor))'
            });
            
        var parser = new kukit.tk.global(cursor, null, true);
        //this.printDebug(parser);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 5);
        this.assertEquals(parser.result[0].symbol, 'fraction');
        this.assertEquals(parser.result[0].txt, 'a');
        this.assertEquals(parser.result[1].symbol, 'openBracket');
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
        this.assertEquals(iparser.result[1].symbol, 'embeddedInside');
        this.assertEquals(iparser.result[1].txt, '[kl]');
        this.assertEquals(iparser.result[2].symbol, 'fraction');
        this.assertEquals(iparser.result[2].txt, 'mn');

        this.assertEquals(parser.result[4].symbol, 'fraction');
        this.assertEquals(parser.result[4].txt, 'opq');
    };
    
    this.testMoreTokens = function() {
        // More tokens, empty entries
        var txt="a[bc{de[f}ghi";
        var cursor = new kukit.tk.Cursor(txt);

        kukit.tk.openBrace = kukit.tk.mkToken('openBrace', '{');
        kukit.tk.openBracket = kukit.tk.mkToken('openBracket', '[');
        kukit.tk.closeBrace = kukit.tk.mkToken('closeBrace', '}');
        kukit.tk.wrappedBracket = kukit.tk.mkToken('wrappedBracket', '[');

        kukit.tk.global = kukit.tk.mkParser('global', {
            '[': 'new kukit.tk.openBracket(this.cursor)',
            '{': '[new kukit.tk.openBrace(this.cursor), new kukit.tk.inside(this.cursor)]',
            '}': 'new kukit.tk.closeBrace(this.cursor)'
            });
            
        kukit.tk.inside = kukit.tk.mkParser('inside', {
            '[': 'new kukit.tk.wrappedBracket(this.cursor)',
            '}': 'this.emitAndReturn()'
            });

        var parser = new kukit.tk.global(cursor, null, true);
        //this.printDebug(parser);
        this.assertEquals(parser.finished, true);
        this.assertEquals(parser.result.length, 7);
        this.assertEquals(parser.result[0].symbol, 'fraction');
        this.assertEquals(parser.result[0].txt, 'a');
        this.assertEquals(parser.result[1].symbol, 'openBracket');
        this.assertEquals(parser.result[1].txt, '[');
        this.assertEquals(parser.result[2].symbol, 'fraction');
        this.assertEquals(parser.result[2].txt, 'bc');
        this.assertEquals(parser.result[3].symbol, 'openBrace');
        this.assertEquals(parser.result[3].txt, '{');
        this.assertEquals(parser.result[4].symbol, 'inside');
        
        var itoken = parser.result[4];
        this.assertEquals(itoken.result.length, 3);
        this.assertEquals(itoken.result[0].symbol, 'fraction');
        this.assertEquals(itoken.result[0].txt, 'de');
        this.assertEquals(itoken.result[1].symbol, 'wrappedBracket');
        this.assertEquals(itoken.result[1].txt, '[');
        this.assertEquals(itoken.result[2].symbol, 'fraction');
        this.assertEquals(itoken.result[2].txt, 'f');
        
        this.assertEquals(parser.result[5].symbol, 'closeBrace');
        this.assertEquals(parser.result[5].txt, '}');
        this.assertEquals(parser.result[6].symbol, 'fraction');
        this.assertEquals(parser.result[6].txt, 'ghi');
    };
 
};
    
kukit.TokenizerTestCase.prototype = new kukit.TokenizerTestCaseBase;

if (typeof(testcase_registry) != 'undefined') {
    testcase_registry.registerTestCase(kukit.TokenizerTestCase, 'kukit.TokenizerTestCase');
}
