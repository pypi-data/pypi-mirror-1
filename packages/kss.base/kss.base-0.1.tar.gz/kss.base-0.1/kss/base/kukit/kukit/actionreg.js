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

kukit.ar = new function() {   /// MODULE START

var ar = this;
 
/*
*  class ActionRegistry
* 
*  The local event actions need to be registered here.
*/
var ActionRegistry = function () {
    this.content = {};
};

ActionRegistry.prototype.register = function(name, func) {
;;;if (typeof(func) == 'undefined') {
;;;    kukit.E = '[func] argument is mandatory when registering an action';
;;;    kukit.E += ' [ActionRegistry.register].';
;;;    throw new Error(kukit.E);
;;;}
    if (this.content[name]) {
        // Do not allow redefinition
;;;    kukit.logError('Error : action [' + name + '] already registered.');
        return;
        }
    this.content[name] = func;
};

ActionRegistry.prototype.exists = function(name) {
    var entry = this.content[name];
    return (typeof(entry) != 'undefined');
};

ActionRegistry.prototype.get = function(name) {
    var func = this.content[name];
    if (! func) {
        // not found
;;;    kukit.E = 'Error : undefined local action [' + name + '].';
        throw Error(kukit.E);
        }
    return func;
};

kukit.actionsGlobalRegistry = new ActionRegistry();

/* XXX deprecated methods, to be removed asap */

ar.actionRegistry = {};
ar.actionRegistry.register = function(name, func) {
;;;var msg='Deprecated kukit.ar.actionRegistry.register, use ';
;;;msg += 'kukit.actionsGlobalRegistry.register instead !';
;;;kukit.logWarning(msg);
    kukit.actionsGlobalRegistry.register(name, func);
};

}();                              /// MODULE END

