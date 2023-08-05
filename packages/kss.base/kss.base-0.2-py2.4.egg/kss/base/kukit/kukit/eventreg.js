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

kukit.er = new function() {   /// MODULE START

var er = this;

var _eventClassCounter = 0;

/*
*
* class _EventRegistry
*
* available for plugin registration
*
* usage:
*
*  kukit.eventsGlobalRegistry.register(namespace, eventName, func, 
*    bindMethodName, defaultActionMethodName);
*  
*     namespace = null: means global namespace
*     defaultActionMethodName = null: if there is no default action implemented
*     func must be a class (constructor) function, this is the class that
*           implements the binder.
*/
var _EventRegistry = function () {
    this.content = {};
    this.classes = {};
    this.eventSets = [];
};

/* binder registration */

_EventRegistry.prototype.registerBinder = function(className, func) {
    if (typeof(func) == 'undefined') {
;;;     kukit.E = 'func argument is mandatory when registering an event';
;;;     kukit.E += ' binder (_EventRegistry.registerBinder).';
        throw new Error(kukit.E);
    }
    if (this.classes[className]) {
        // Do not allow redefinition
;;;     var msg = 'Error : event class [' + className + '] already registered.';
;;;     kukit.logError(msg);
        return;
    
    }
    // Decorate and store the class
    decorateEventBinderClass(func);
    this.classes[className] = func;
};

_EventRegistry.prototype.existsBinder = function(className) {
    var func = this.classes[className];
    return (typeof(func) != 'undefined');
};

_EventRegistry.prototype.getBinderClass = function(className) {
    var func = this.classes[className];
    if (! func) {
        // not found
;;;     kukit.E = 'Error : undefined event setup type [' + className + '].';
        throw new Error(kukit.E);
        }
    return func;
};

/* events (methods) registration  helpers (not to be called directly) */

_EventRegistry.prototype._register = 
    function(namespace, eventName, klass,
        bindMethodName, defaultActionMethodName, iterName) {
    if (typeof(defaultActionMethodName) == 'undefined') {
;;;     kukit.E = 'Missing arguments when calling [_EventRegistry.register].';
        throw new Error(kukit.E);
    }
    // Find out the class name. (Not specified now.)
    var className = klass.prototype.__className__;
    if (typeof(className) == 'undefined') {
        // Create a className, and register it too.
        className = '' + _eventClassCounter;
        _eventClassCounter += 1;
        this.registerBinder(className, klass);
        klass.prototype.__className__ = className;
    }
    if (!eventName) {
;;;     kukit.E = '[eventName] argument cannot be empty when registering';
;;;     kukit.E += ' an event with [_EventRegistry.register].';
        throw new Error(kukit.E);
    }
    var key = this._getKey(namespace, eventName);
    var entry = this.content[key];
    if (typeof(entry) != 'undefined') {
        if (key[0] == '-') {
            key = key.substring(1);
        }
;;;     kukit.E = 'Attempt to register key [' + key;
;;;     kukit.E += '] twice when registering';
;;;     kukit.E += ' an event with [_EventRegistry.register].';
        throw new Error(kukit.E);
    }
    // check bindMethodName and defaultActionMethodName
    if (bindMethodName && ! klass.prototype[bindMethodName]) {
;;;     kukit.E = 'In _EventRegistry.register bind method [' + bindMethodName;
;;;     kukit.E += '] is undefined for event [' + eventName;
;;;     kukit.E += '] namespace [' + namespace + '].';
        throw new Error(kukit.E);
    }
    if (defaultActionMethodName && ! klass.prototype[defaultActionMethodName]) {
;;;     kukit.E = 'In _EventRegistry.register default action method [';
;;;     kukit.E += defaultActionMethodName + '] is undefined for event [';
;;;     kukit.E += eventName + '] namespace [' + namespace + '].';
        throw new Error(kukit.E);
    }
    // check the iterator.
    if  (! er.getBindIterator(iterName)) {
;;;     kukit.E = 'In _EventRegistry.register unknown bind iterator [';
;;;     kukit.E += iterName + '].';
        throw new Error(kukit.E);
    }
    // register it
    this.content[key] = {
        'className': className,
        'bindMethodName': bindMethodName,
        'defaultActionMethodName': defaultActionMethodName,
        'iterName': iterName
        };
};

/* events (methods) binding [ForAll] registration */

_EventRegistry.prototype._registerEventSet =
    function(namespace, names, iterName, bindMethodName) {
    // At this name the values should be checked already. so this should
    // be called _after_ _register.
    this.eventSets.push({
        'namespace': namespace, 
        'names': names,
        'iterName': iterName,
        'bindMethodName': bindMethodName
        });
};

/* there are the actual registration methods, to be called from plugins */

_EventRegistry.prototype.register =
    function(namespace, eventName, klass, bindMethodName,
        defaultActionMethodName) {
    this._register(namespace, eventName, klass, bindMethodName,
        defaultActionMethodName, 'EachLegacy');
    this._registerEventSet(namespace, [eventName], 'EachLegacy',
        bindMethodName);
};

_EventRegistry.prototype.unregister =
    function(namespace, eventName) {
    var key = this._getKey(namespace, eventName);
    delete this.content[key];
    var found = null;
    for (var i=0; i < this.eventSets.length; i++) {
        var eventSet = this.eventSets[i];
        if (eventSet['namespace'] == namespace) {
            found = i;
            break;
        }
    }
    if (found != null) {
        this.eventSets.splice(found, 1);
    }
};

_EventRegistry.prototype.registerForAllEvents =
    function(namespace, eventNames, klass,
        bindMethodName, defaultActionMethodName, iterName) {
    if (typeof(eventNames) == 'string') {
        eventNames = [eventNames];
        }
    for (var i=0; i<eventNames.length; i++) {
        var eventName = eventNames[i];
        this._register(namespace, eventName, klass, bindMethodName, 
            defaultActionMethodName, iterName);
    }
    this._registerEventSet(namespace, eventNames, iterName, bindMethodName);
};

_EventRegistry.prototype._getKey = function(namespace, eventName) {
    if (namespace == null) {
        namespace = '';
    } else if (namespace.split('-') > 1) {
;;;     kukit.E = 'In [_EventRegistry.register], [namespace] cannot have';
;;;     kukit.E += 'dashes.';
        throw new Error(kukit.E);
    }
    return namespace + '-' + eventName;
};

_EventRegistry.prototype.exists = function(namespace, eventName) {
    var key = this._getKey(namespace, eventName);
    var entry = this.content[key];
    return (typeof(entry) != 'undefined');
};

_EventRegistry.prototype.get = function(namespace, eventName) {
    var key = this._getKey(namespace, eventName);
    var entry = this.content[key];
    if (typeof(entry) == 'undefined') {
;;;     if (key.substr(0, 1) == '-') {
;;;         key = key.substring(1);
;;;         kukit.E = 'Error : undefined global event [';
;;;         kukit.E += key + '] (or maybe namespace is missing ?).';
;;;     } else {
;;;         kukit.E = 'Error : undefined namespace or event in [' + key + '].';
;;;     }
        throw new Error(kukit.E);
    } 
    return entry;
};

kukit.eventsGlobalRegistry = new _EventRegistry();

/* XXX deprecated methods, to be removed asap */

var _eventRegistry = {};
_eventRegistry.register = function(namespace, eventName, klass,
        bindMethodName, defaultActionMethodName) {
;;; var msg = 'Deprecated _eventRegistry.register,';
;;; msg += ' use kukit.eventsGlobalRegistry.register instead ! [';
;;; msg += namespace + '-' + eventName + '].';
;;; kukit.logWarning(msg);
    kukit.eventsGlobalRegistry.register(namespace, eventName, klass,
        bindMethodName, defaultActionMethodName);
};

/* Event class decoration 
*
* poor man's subclassing
* This is called automatically on registration, to dress
* up the event class with the necessary methods
*
*/

/* Provide callins on the state instance that execute a given
*  continuation event.
*  Parameters will be the ones specified in the call + 
*  those defined in the rule will be added too. (Parameters can
*  be accessed with the [pass] kss parameter provider.)
*
* Call examples: 
*
* trigger an event bound to a given state instance, same node
*
*     binder.__continueEvent__('doit', oper.node, {'extravalue': '5'});
*
*   with kss rule:
*
*     node.selector:doit {
*         action-client: log;
*         log-message: pass(extravalue);
*     }
*
*  or
*
*     behaviour.selector:doit {
*         action-client: log;
*         log-message: pass(extravalue);
*     }
*
* trigger an event bound to a given state instance, and the document
* (different from current scope)
*
*     binder.__continueEvent__('doit', null, {'extravalue': '5'});
*
*   with kss rule:
*
*     document:doit {
*         action-client: log;
*         log-message: pass(extravalue);
*     }
*
*  or
*
*     behaviour.selector:doit {
*         action-client: log;
*         log-message: pass(extravalue);
*     }
*
* trigger an event on all the nodes + document bound to a given state instance
*
*     binder.__continueEvent_allNodes__('doit', {'extravalue': '5'});
*
*   with kss rule:
*
*     node.selector:doit {
*         action-client: log;
*         log-message: pass(extravalue);
*     }
*
* p.s. oper is not required to make it easy to adapt existing code
* so we create a new oper below
*/

var _EventBinder__continueEvent__ =
    function(name, node, defaultParameters) {
    // Trigger a continuation event bound to a given state instance, given node
    // (or on document, if node = null)
    //
    var oper = new kukit.op.Oper();
    oper.node = node;
    if (node) {
        // if we found the binding, just use that
        var info = kukit.engine.binderInfoRegistry.getBinderInfoById(
            this.__binderId__);
        var newOper = info.bound.getBoundOperForNode(name, node);
        if (newOper) {
            oper = newOper;
        }
    } else {
        oper.eventRule =  kukit.engine.documentRules.getMergedRule(
            'document', name, this);
    }
    // Look up the behaviour rule, if any.
    var behav_eventRule =  kukit.engine.documentRules.getMergedRule(
        'behaviour', name, this);
    if (behav_eventRule) {
        if (! oper.eventRule) {
            // There was no node matching for the rule, use behaviour rule
            // this allows to set up parametrized actions in general.
            oper.eventRule = behav_eventRule;
        } else {
            // XXX this case should go away, as we should check
            // this already from binding time
            // and signal the appropriate error.
            // Also note that behaviour roles will only be allowed
            // for "non-binding" events.
;;;         var msg = 'Behaviour rule for continuation event [' + name;
;;;         msg += '] will be ignored, because we found an explicit rule.';
;;;         kukit.logError(msg);
        }
    }
    // If parms are specified in the call, use them.
    if (typeof(defaultParameters) != 'undefined') {
        oper.defaultParameters = defaultParameters;
    } else {
        oper.defaultParameters = {};
    }
    // if eventRule is null here, we can yet have the default method, so go on.
    this._EventBinder_triggerEvent(name, oper);
;;; kukit.logDebug('Continuation event [' + name + '] executed on same node.');
};

var _EventBinder__continueEvent_allNodes__ =
    function(name, defaultParameters) {
    // Trigger an event bound to a given state instance, on all nodes.
    // (or on document, if node = null)
    // if no other nodes execute.
    var executed = 0;
    // Normal rules. If any of those match, execute them too
    // each on the node that it selects - not on the original node.
    var oper = new kukit.op.Oper();
    var info = kukit.engine.binderInfoRegistry.getBinderInfoById(
        this.__binderId__);
    var opers = info.bound.getBoundOpers(name);
    for (var i=0; i<opers.length; i++) {
        var oper = opers[i];
        var newOper = oper.clone();
        if (typeof(defaultParameters) != 'undefined') {
            newOper.defaultParameters = defaultParameters;
        } else {
            newOper.defaultParameters = {};
        }
        this._EventBinder_triggerEvent(name, newOper);
        executed += 1;
    }
;;; kukit.logDebug('Event [' + name + '] executed on ' + executed + ' nodes.');
};

var _EventBinder_makeFuncToBind = function(name, node) {
   var executor = new er._LateBinder(this, name, node);
   return function() {
       executor.executeActions();
   };
};

/*
*
* class _LateBinder
*
* postpone binding of actions until called first time
*
*/
var _LateBinder = function(binder, name, node) {
    this.binder = binder;
    this.name = name;
    this.node = node;
    this.boundEvent = null;
};

_LateBinder.prototype.executeActions = function() {
    if (! this.boundEvent) {
;;;        var msg = 'Attempt of late binding for event [' + this.name;
;;;        msg += '], node [' + this.node.nodeName + '].';
;;;        kukit.log(msg);
        if (kukit.hasFirebug) {
            kukit.log(this.node);
        }
        var info = kukit.engine.binderInfoRegistry.getBinderInfoById(
            this.binder.__binderId__);
        var oper = info.bound.getBoundOperForNode(this.name, this.node);
        if (oper) {
            // (if eventRule is null here, we could still have the default
            // method, so go on.)
            oper.parms = {};
            this.boundEvent = function() {
                this.binder._EventBinder_triggerEvent(this.name, oper);
            };
;;;         kukit.log('Node bound.');
        } else {
;;;         kukit.logWarning('No node bound.');
            this.boundEvent = function() {};
        }
    }
    this.boundEvent();
};        

var _EventBinder_triggerEvent = function(name, oper) {
    // Private. Called from __continueEvent__ or from main event execution.
    oper.binder = this;
    if (oper.eventRule) {
        // Call the actions, if we had an event rule.
        // This includes calling the default action.
        oper.eventRule.actions.execute(oper);
    } else {
        // In case there is no event rule, just call the default event action.
        var namespace = this.__eventNamespace__;
;;;     var msg = 'Calling implicit event [' + name + '] on namespace [';
;;;     msg += namespace + '].';
;;;     kukit.logDebug(msg);
        var success = oper.executeDefaultAction(name, true);
        if (! success) {
            // instead of the standard message give more specific reason:
            // either way we should have executed something...
;;;         kukit.E = 'Could not trigger event name [' + name;
;;;         kukit.E += '] on namespace [' + namespace;
;;;         kukit.E += '], because there is neither an explicit KSS rule,';
;;;         kukit.E += ' nor a default method';
            throw new Error(kukit.E);
        }
    }
};

/* (default) method call handling */

var _EventBinder_callMethod = function(namespace, name, oper, methodName) {
    // hidden method for calling just a method and checking that is exists.
    // (called from oper)
    var method = this[methodName];
    if (! method) {
;;;     kukit.E = 'Could not trigger event name [' + name;
;;;     kukit.E += '] on namespace [' + namespace;
;;;     kukit.E += '], because the method [' + methodName + '] does not exist.';
        throw new Error(kukit.E);
    }
    // call it
    oper.binder = this;
    method.call(this, name, oper);
};

var decorateEventBinderClass = function(cls) {
    cls.prototype.__continueEvent__ = _EventBinder__continueEvent__;
    cls.prototype.__continueEvent_allNodes__ =
        _EventBinder__continueEvent_allNodes__;
    cls.prototype._EventBinder_triggerEvent = _EventBinder_triggerEvent;
    cls.prototype._EventBinder_callMethod = _EventBinder_callMethod;
    cls.prototype.__makeFuncToBind__ = _EventBinder_makeFuncToBind;
};

/* Event instance registry 
*
* class BinderInfoRegistry
*
*  used in run-time to keep track of the event instances
*
*/

er.BinderInfoRegistry = function () {
    this.info = {};
};

er.BinderInfoRegistry.prototype.getOrCreateBinderInfo =
    function (id, className, namespace) {
    // Get or create the event.
    var binderInfo = this.info[id];
    if (typeof(binderInfo) == 'undefined') {
        // Create a new event.
;;;     var msg = 'Instantiating event id [' + id + '], className [';
;;;     msg += className + '], namespace [' + namespace + '].';
;;;     kukit.logDebug(msg);
        var binderClass = kukit.eventsGlobalRegistry.getBinderClass(className);
        var binder = new binderClass();
        
        binderInfo = this.info[id] = new _BinderInfo(binder);

        // decorate it with id and class
        binder.__binderId__ = id;
        binder.__binderClassName__ = className;
        binder.__eventNamespace__ = namespace;
        // store the bound rules
        //binder.__bound_rules__ = [];
    } else if (binderInfo.getBinder().__binderClassName__ != 
        className) {
        // just paranoia
;;;     kukit.E = 'Conflicting class for event id [' + id + '], [';
;;;     kukit.E += binderInfo.getBinder().__binderClassName__;
;;;     kukit.E += '] != [' + className + '].';
        throw new Error(kukit.E);
    }
    return binderInfo;
};

er.BinderInfoRegistry.prototype.getBinderInfoById = function (id) {
    // Get an event.
    var binderInfo = this.info[id];
    if (typeof(binderInfo) == 'undefined') {
;;;     kukit.E = 'Event with id [' + id + '] not found.';
        throw new Error(kukit.E);
    }
    return binderInfo;
};

er.BinderInfoRegistry.prototype.getSingletonBinderInfoByName =
    function (namespace, name) {
    //Get className
    var className = kukit.eventsGlobalRegistry.get(namespace, name).className;
    // Get an event.
    var id = er.makeId(namespace, className);
    var binderInfo = this.info[id];
    if (typeof(binderInfo) == 'undefined') {
;;;     kukit.E = 'Singleton event with namespace [' + namespace;
;;;     kukit.E += '] and (event) name [' + name + '] not found.';
        throw new Error(kukit.E);
    }
    return binderInfo;
};

er.BinderInfoRegistry.prototype.startBindingPhase = function () {
    // At the end of the binding phase, we want to process our events. This
    // must include all the binder instances we bound in this phase.
    for (var id in this.info) {
        var binderInfo = this.info[id];
        // process binding on this instance.
        binderInfo.startBindingPhase();
    }
};

er.BinderInfoRegistry.prototype.processBindingEvents = function () {
    // At the end of the binding phase, we want to process our events. This
    // must include all the binder instances we bound in this phase.
    for (var id in this.info) {
        var binderInfo = this.info[id];
        // process binding on this instance.
        binderInfo.processBindingEvents();
    }
};

/*
* class _BinderInfo
*
* Information about the given binder instance. This contains the instance and
* various binding info. Follows the workflow of the binding in different stages.
*
*/

var _BinderInfo = function (binder) {
    this.binder = binder;
    this.bound = new _OperRegistry();
    this.startBindingPhase();
};

_BinderInfo.prototype.getBinder = function () {
    return this.binder;
};

_BinderInfo.prototype.startBindingPhase = function () {
    // The binding phase starts and it has the information for
    // the currently on-bound events.
    this.binding = new _OperRegistry();
};

_BinderInfo.prototype.bindOper = function (oper) {
    // We mark a given oper. This means a binding on the binder 
    // for given event, node and eventRule (containing event namespace,
    // name, and evt- parms.)
    //
    // first see if it can go to already bound ones
    this.bound.checkOperBindable(oper);
    // then register it properly to the binding events
    this.binding.bindOper(oper);
};

_BinderInfo.prototype.processBindingEvents = function () {
    // We came to the end of the binding phase. Now we process all our binding
    // events, This will do the actual binding on the browser side.
    this.binding.processBindingEvents(this.binder);
    // Now we to add these to the new ones.
    this.binding.propagateTo(this.bound);
    // Delete them from the registry, to protect against accidents.
    this.binding = null;
};


/*
*  class _OperRegistry
*
*  OperRegistry is associated with a binder instance in the 
*  BinderInfoRegistry, and remembers bounding information.
*  This is used both to remember all the bindings for a given
*  instance, but also just to remember the bindings done during
*  a given event setup phase.
*/

var _OperRegistry = function () {
    this.infoPerName = {};
    this.infoPerNode = {};
};

// XXX we can do this without full cloning, more efficiently.
_OperRegistry.prototype.propagateTo = function (newreg) {
    for (var key in this.infoPerName) {
        var rulesPerName = this.infoPerName[key];
        for (var name in rulesPerName) {
            var oper = rulesPerName[name];
            newreg.bindOper(oper);
        }
    }
};

_OperRegistry.prototype.checkOperBindable =
    function (oper, name, nodeHash) {
    // Check if the binding with this oper could be done.
    // Throw exception otherwise.
    //
    // Remark. We need  different check and bind method,
    // because we need to bind to the currently
    // processed nodes, but we need to check duplication 
    // in all the previously bound nodes.
    var info = this.infoPerName;
    // name and nodeHash are for speedup.
    if (typeof(nodeHash) == 'undefined') {
        name = oper.eventRule.kssSelector.name;
        nodeHash = kukit.rd.hashNode(oper.node);
    }
    var rulesPerName = info[name];
    if (typeof(rulesPerName) == 'undefined') {
        // Create an empty list.
        rulesPerName = info[name] = {};
    } else if (typeof(rulesPerName[nodeHash]) != 'undefined') {
;;;     kukit.E = 'Mismatch in bind registry,[ ' + name;
;;;     kukit.E += '] already bound to node in this instance.'; 
        throw new Error(kukit.E);
    }
    return rulesPerName;
};
    
_OperRegistry.prototype.bindOper = function (oper) {
    // Marks binding between binder, eventName, node.
    var name = oper.eventRule.kssSelector.name;
    var nodeHash = kukit.rd.hashNode(oper.node);
    var rulesPerName = this.checkOperBindable(oper, name, nodeHash);
    rulesPerName[nodeHash] = oper;
    // also store per node info
    var rulesPerNode = this.infoPerNode[nodeHash];
    if (typeof(rulesPerNode) == 'undefined') {
        // Create an empty list.
        rulesPerNode = this.infoPerNode[nodeHash] = {};
    }
    rulesPerNode[name] = oper;
};

// XXX This will need refactoring.
/// We would only want to lookup from our registry and not the other way around.
_OperRegistry.prototype.processBindingEvents = 
    function (binder) {
    var eventRegistry = kukit.eventsGlobalRegistry;
    for (var i=0; i < eventRegistry.eventSets.length; i++) {
        var eventSet = eventRegistry.eventSets[i];
        // Only process binding events (and ignore non-binding ones)
        if (eventSet.bindMethodName) {
            if (binder.__eventNamespace__ == eventSet.namespace) {
                // Process the binding event set.
                // This will call the actual bindmethods
                // according to the specified iterator.
                var iterator = er.getBindIterator(eventSet.iterName);
                iterator.call(this, eventSet, binder);
            }
        }
    }
};

// XXX The following methods will probably disappear as iterators 
// replace their functionality.

_OperRegistry.prototype.getBoundOperForNode = function (name, node) {
    // Get the oper that is bound to a given eventName
    // to a node in this binder
    // returns null, if there is no such oper.
    var rulesPerName = this.infoPerName[name];
    if (typeof(rulesPerName) == 'undefined') {
        return null;
    }
    var nodeHash = kukit.rd.hashNode(node);
    var oper = rulesPerName[nodeHash];
    if (typeof(oper) == 'undefined') {
        return null;
    }
    // Return it
    return oper;
};

_OperRegistry.prototype.getBoundOpers = function (name) {
    // Get the opers bound to a given eventName (to any node)
    // in this binder
    var opers = [];
    var rulesPerName = this.infoPerName[name];
    if (typeof(rulesPerName) != 'undefined') {
        // take the values as a list
        for (var nodeHash in rulesPerName) {
            opers.push(rulesPerName[nodeHash]);
        }
    }
    // Return it
    return opers;
};

// Iterators
// The getBindIterator returns a function that gets executed on
// the oper registry.
//
// Iterators receive the eventSet as a parameter
// plus a binder and a method. They need to iterate by calling this
// as method.call(binder, ...); where ... can be any parms this
// given iteration specifies.
//

er.getBindIterator = function(iterName) {
    // attempt to find canonical version of string
    // and shout if it does not match.
    // String must start uppercase.
    var canonical = iterName.substring(0, 1).toUpperCase() + 
            iterName.substring(1);
    // Special case: allnodes -> AllNodes, not handled by
    // the previous line
    if (canonical == 'Allnodes') {
        canonical = 'AllNodes';
    }
    if (iterName != canonical) {
        // BBB 2007.12.31, this will turn into an exception.
;;;     var msg = 'Deprecated the lowercase iterator names in last ';
;;;     msg += 'parameters of ';
;;;     msg += 'kukit.eventsGlobalRegistry.registerForAllEvents, use [';
;;;     msg += canonical + '] instead of [' + iterName + '] (2007-12-31)';
;;;     kukit.logWarning(msg);
        iterName = canonical;
        }
    return _OperRegistry.prototype['_iterate' + iterName];
};

_OperRegistry.prototype.callBindMethod = 
    function (eventSet, binder, p1, p2, p3, p4, p5, p6) {
    var method = binder[eventSet.bindMethodName];
    // Protect the binding for better logging
;;; try {
        method.call(binder, p1, p2, p3, p4, p5, p6);
;;; } catch(e) {
;;;     var names = eventSet.names;
;;;     var namespace = eventSet.namespace;
;;;     kukit.E = kukit.err.eventBindError(e, names, namespace);
;;;     throw new Error(kukit.E);
;;; }
};

// This calls the bind method by each bound oper one by one.
// Eventname and funcToBind are passed too.
// this is the legacy ([EachLegacy]) way
_OperRegistry.prototype._iterateEachLegacy =
    function (eventSet, binder) {
    for (var i=0; i<eventSet.names.length; i++) {
        var rulesPerName = this.infoPerName[eventSet.names[i]];
        if (typeof(rulesPerName) != 'undefined') {
            for (var nodeHash in rulesPerName) {
                var oper = rulesPerName[nodeHash];
                var eventName = oper.getEventName();
                var funcToBind = oper.makeExecuteActionsHook();
                this.callBindMethod(eventSet, binder, eventName,
                    funcToBind, oper);
            }
        }
    }
};


// This calls the bind method by each bound oper one by one.
// Eventname and funcToBind are passed too.
// this is the preferred ([Each]) way. Parameters are different from EachLegacy.
_OperRegistry.prototype._iterateEach =
    function (eventSet, binder) {
    for (var i=0; i<eventSet.names.length; i++) {
        var rulesPerName = this.infoPerName[eventSet.names[i]];
        if (typeof(rulesPerName) != 'undefined') {
            for (var nodeHash in rulesPerName) {
                var oper = rulesPerName[nodeHash];
                this.callBindMethod(eventSet, binder, oper);
            }
        }
    }
};

// This calls the bind method by the list of bound opers
_OperRegistry.prototype._iterateOpers =
    function (eventSet, binder) {
    var opers = [];
    for (var i=0; i<eventSet.names.length; i++) {
        var rulesPerName = this.infoPerName[eventSet.names[i]];
        if (typeof(rulesPerName) != 'undefined') {
            for (var nodeHash in rulesPerName) {
                opers.push(rulesPerName[nodeHash]);
            }
        }
    }
    this.callBindMethod(eventSet, binder, opers);
};

// This calls the bind method by a mapping eventName:oper
// per each bound node individually
_OperRegistry.prototype._iterateNode =
    function (eventSet, binder) {
    for (var nodeHash in this.infoPerNode) {
        var rulesPerNode = this.infoPerNode[nodeHash];
        // filter only the events we are interested in
        var filteredRules = {};
        var operFound = false;
        for (var i=0; i<eventSet.names.length; i++) {
            var name = eventSet.names[i];
            var oper = rulesPerNode[name];
            if (typeof(oper) != 'undefined') {
                filteredRules[name] = oper;
                operFound = oper;
            }
        }
        // call it
        // All opers have the same node, the last one is yet in operFound, so
        // we use it as a second parameter to the call.
        // The method may or may not want to use this.
        if (operFound) {
            this.callBindMethod(eventSet, binder, filteredRules,
                operFound.node);
        }
    }
};

// This calls the bind method once per instance, by a list of
// items, where item.node is the node and item.opersByEventName nodeHash:item
// in item there is item.node and item.opersByEventName
_OperRegistry.prototype._iterateAllNodes = 
    function (eventSet, binder) {
    var items = [];
    var hasResult = false;
    for (var nodeHash in this.infoPerNode) {
        var rulesPerNode = this.infoPerNode[nodeHash];
        // filter only the events we are interested in
        var filteredRules = {};
        var operFound = false;
        for (var i=0; i<eventSet.names.length; i++) {
            var name = eventSet.names[i];
            var oper = rulesPerNode[name];
            if (typeof(oper) != 'undefined') {
                filteredRules[name] = oper;
                operFound = oper;
            }
        }
        if (operFound) {
            var item = {node: operFound.node, 
                opersByEventName: filteredRules};
            items.push(item);
            hasResult = true;
        }
    }
    // call the binder method
    if (hasResult) {
        this.callBindMethod(eventSet, binder, items);
    }
};

er.makeId = function(namespace, name) {
    if (namespace == null) {
        namespace = '';
    }
    return '@' + namespace + '@' + name;
};

er.makeMergeId = function(id, namespace, name) {
    if (namespace == null) {
        namespace = '';
    }
    return id + '@' + namespace + '@' + name;
};

}();                              /// MODULE END
