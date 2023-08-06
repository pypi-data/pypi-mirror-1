/* 
 * This file is part of kss.plugin.cacheability .
 * Copyright (c) 2008 KissBooth Collective, see CREDITS.txt.
 *
 * kss.plugin.cacheability is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 ONLY of the License.
 *
 * Foobar is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with kss.plugin.cacheability.  If not, see <http://www.gnu.org/licenses/>.
 */


/* 
 * cacheability support for KSS
 *
 * XXX XXX XXX
 * WARNING! This plugin accesses the old, unpublished
 * internal event lookup api of KSS. The code below should
 * be only considered as a temporary example. The next
 * version of KSS (1.5 ?) will provide a cleaner way of
 * achieving the same operations and may cause parts of the
 * unpublished api go away without deprecation.
 * XXX XXX XXX
 * 
 *
 * This plugin enables to use cacheable (GET) KSS reguests.
 * This feature will be supported in the future directly by
 * kss.
 *
 * Usage::
 * 
 *     css:event {
 *         action-client: cacheability-serverAction;
 *         cacheability-serverAction-url: actionName;
 *     }
 * 
 * The future syntax for this will be::
 *
 *     css:event {
 *          action-server: actionName method(GET);
 *     }
 *
 *
 * Limitations
 * -----------
 *
 * Because currently the action runs as a client action in
 * the eyes of KSS, entire forms cannot be marshalled to the
 * server action. (kssSubmitForm, etc. does not work.) This
 * will work out of the box if the new syntax is added to
 * KSS.
 *
 */

if (! kukit.plugin) {
    kukit.plugin = {};
}

kukit.plugin.cacheability = new function() {

var ca = this;


/* This is an extension of kukit.sa.ServerAction
 * with support of cacheability
 * by adding request methods (GET and POST)
 */

ca.ServerAction = function() {

    this.initialize = function initialize(name, oper, method) {
        this.oper = oper;
        this.url = oper.kssParms.kssUrl;
        if (typeof(this.url) == 'undefined') {
            this.url = name;
        }
        // set the method
        if (typeof(method) == 'undefined') {
            this.method = 'GET';
        } else {
            this.method = method
        }
    };

    /* XXX execute is added to the original ServerAction, to
     * decouple execution from initialize().
     */

    this.execute = function execute() {
      // absolutize the url
      this.url = this.calculateAbsoluteURL(this.url);
      this.notifyServer();
    };

    /* XXX calculateAbsoluteURL is fixed in the closure, and
     * also somewhat enhanced.
     *
     * Makes absolute site url
     * - if starts with http:// https:// : no change
     * - if starts with /: interprets absolute from domain
     * - otherwise: relative to current context
     */

    this.calculateAbsoluteURL = function(url) {
        // XXX packer breaks on following regexp constant,
        // XXX so it must be quoted (not needed in
        // javascript syntax)
        if (url.match(RegExp("/^https?:\/\//"))) {
            // absolute already
            return url;
        }
        var absoluteMatch = url.match(RegExp(/^(\/)(.*)/));
        var path = kukit.engine.baseUrl;
        if (absoluteMatch) {
            // relative to domain
            var base = path.match(RegExp(/^(.*:\/\/[^\/]*)(\/?)/))[1];
            // base is like: http://foo.bar without trailing /
            url = base + url;
            return url;
        }
        // final case: relative to current url
        // (paranoia: add an / to the path *only* if it is
        // *not* there) 
        // XXX packer breaks on following
        // regexp constant, so it must be quoted
        // XXX (not needed in javascript syntax)
        if (! path.match(RegExp("/\/$/"))) {
            // this really always happens...
            path += '/';
        }
        url = path + url;
        return url;
    };

    /* From the rest of the methods we only override
     * reallyNofifyServer, with the enhanced behaviour.
     */

    this.reallyNotifyServer = function() {
        // make a deferred callback
        var domDoc = new XMLHttpRequest();
        var self = this;
        var notifyServer_done  = function() {
            self.notifyServer_done(domDoc);
        };
        // convert params
        var query = new kukit.fo.FormQuery();
        for (var key in this.oper.parms) {
            query.appendElem(key, this.oper.parms[key]);
        }
        // XXX this will not happen currently (we are a
        // client-action really)
        //
        // also add the parms that result from submitting an
        // entire form.  This is, unlike the normal parms,
        // is a list. Keys and values are added at the end
        // of the query, without mangling names.
        var submitForm = this.oper.kssParms.kssSubmitForm;
        if (submitForm) {
            for (var i=0; i<submitForm.length; i++) {
                var item = submitForm[i];
                query.appendElem(item[0], item[1]);
            }
        }
        //
        // encode the query
        var encoded = query.encode();
        var url = this.url;
        if (this.method == 'POST') {
            // XXX kukitTimeStamp is not needed
            //var ts = new Date().getTime();
            //url = url + "?kukitTimeStamp=" + ts;
            // sending form
            domDoc.open("POST", url, true);
            domDoc.onreadystatechange = notifyServer_done;
            domDoc.setRequestHeader("Content-Type",
                    "application/x-www-form-urlencoded");
            domDoc.send(encoded);
        } else { // GET
            // sending form
            url = url + '?' + encoded;
            domDoc.open("GET", url, true);
            domDoc.onreadystatechange = notifyServer_done;
            domDoc.send(null);
        }
    };


// XXX XXX XXX The rest of the methods are just copypasted
// from the base class. This should not be needed at all,
// however the current way the initialize and closures are
// used, make it impossible to inherit from it.

// Backparameters can be used on command execution.
this.notifyServer = function() {
    var self = this;
    var sendHook = function(queueItem) {
        // store the queue reception on the oper
        self.oper.queueItem = queueItem;
        self.reallyNotifyServer();
    };
    var timeoutHook = function(queueItem) {
        // store the queue reception on the oper
        self.oper.queueItem = queueItem;
        self.processError('timeout');
    };
    kukit.engine.requestManager.notifyServer(sendHook, this.url, timeoutHook);
};

this.notifyServer_done = function(domDoc) {
;;; var msg = 'Request readyState = ' + domDoc.readyState + '.';
;;; kukit.logDebug(msg);
    if (domDoc.readyState == 4) {
        // notify the queue that we are done
        var success = this.oper.queueItem.receivedResult();
        // We only process if the response has not been timed
        // out by the queue in the meantime.
        if (success) {
            // catch the errors otherwise won't get logged.
            // In FF they seem to get swallowed silently.
            // We need these both in production and development mode,
            // since the erorr fallbacks are activated from processError.
            try {
                // process the results
                this.processResult(domDoc);
            } catch(e) {
;;;             if (e.name == 'RuleMergeError' || e.name == 'EventBindError') {
;;;                 throw kukit.err.eventSetupError(e);
;;;             } 
                if (e.name == 'ResponseParsingError') {
;;;                 kukit.E = 'Response parsing error: ' + e;
                    this.processError(kukit.E);
                } else if (e.name == 'ExplicitError') {
                    this.processError(e.info.kw.errorcommand);
                } else {
                    throw e;
                }
            }
        }
    };
};

this.processResult = function(domDoc) {
    // checking various dom process errors, and get the commands part
    var dom;
    var commandstags = [];
    // Let's process xml payload first:
    if (domDoc.responseXML) {
        dom = domDoc.responseXML;
        commandstags = kukit.dom.getNsTags(dom, 'commands');
        if (commandstags.length != 1) {
            // no good, maybe better luck with it as html payload
            dom = null;
        }
    }
    // Check for html too, this enables setting the kss error command on the 
    // error response.
    if (dom == null) {
        // Read the header and load it as xml, if defined.
        var payload = domDoc.getResponseHeader('X-KSSCOMMANDS');
        if (payload) {
            try {
                dom = (new DOMParser()).parseFromString(payload, "text/xml");
            } catch(e) {
;;;             kukit.E = 'Error parsing X-KSSCOMMANDS header.';
                throw kukit.err.responseParsingError(kukit.E);
            }
            commandstags = kukit.dom.getNsTags(dom, 'commands');
            if (commandstags.length != 1) {
                // no good, maybe better luck with it as html payload
                dom = null;
            }
        }
        // Check for html too, this enables setting the kss error command on the 
        // error response.
        if (dom == null) {
            // Read the header and load it as xml, if defined.
            var payload = domDoc.getResponseHeader('X-KSSCOMMANDS');
            if (payload) {
                try {
                    dom = (new DOMParser()).parseFromString(payload, "text/xml");
                } catch(e) {
;;;                 kukit.E = 'Error parsing X-KSSCOMMANDS header.';
                    throw kukit.err.responseParsingError(kukit.E);
                }
                commandstags = kukit.dom.getNsTags(dom, 'commands');
                if (commandstags.length != 1) {
                    // no good
                    dom = null;
                }
            } else {
                // Ok. we have not found it either in the headers.
                // Check if there was a parsing error in the xml, 
                // and log it as reported from the dom
                // Opera <= 8.5 does not have the parseError attribute,
                // so check for it first
;;;             dom = domDoc.responseXML;
;;;             kukit.E = 'Unknown server error (invalid KSS response, no error';
;;;             kukit.E += ' info received)';
;;;             if (dom && dom.parseError && (dom.parseError != 0)) {
;;;                 kukit.E += ' : ' + Sarissa.getParseErrorText(dom);
;;;                 }
                throw kukit.err.responseParsingError(kukit.E);
            }
        }
        if (dom == null) {
            // this should not happen
;;;         kukit.E = 'Neither xml nor html payload.';
            throw kukit.err.responseParsingError(msg);
        }
        // find the commands (atm we don't limit ourselves inside the commandstag)
        var commands = kukit.dom.getNsTags(dom, 'command');
        // Warning, if there is a valid response containing 0 commands.
        if (commands.length == 0) {
;;;         kukit.log('No commands in kukit response');
            return;
        }
        // One or more valid commands to parse
        var command_processor = new kukit.cp.CommandProcessor();
        command_processor.parseCommands(commands, domDoc);
        kukit.engine.beginSetupEventsCollection();
        command_processor.executeCommands(this.oper);
        kukit.engine.finishSetupEventsCollection();
    };

    this.processError = function(errorcommand) {
        var error_action = null;
        if (this.oper.eventRule) {
            var error_action = this.oper.eventRule.actions.getErrorActionFor(
                this.oper.action);
            }
;;;     var reason = '';
;;;     if (typeof(errorcommand) == 'string') {
;;;         // not a command, just a string
;;;         reason = ', client_reason="' + errorcommand + '" ';
;;;     } else if (typeof(errorcommand) != 'undefined') {
;;;         // a real error command, sent by the server
;;;         // as kukit payload.
;;;         // this way the server sends whatever message he wants as a parameter
;;;         // to the error command.
;;;         reason = ', server_reason="' + errorcommand.parms.message + '" ';
;;;     }
        if (error_action) {
;;;         kukit.E = 'Request failed at url ' + this.oper.queueItem.url;
;;;         kukit.E += ', rid=' + this.oper.queueItem.rid + reason;
;;;         kukit.E += ', will be handled by action "' + error_action.name + '"';
;;;         kukit.logWarning(kukit.E);
            // Individual error handler was defined. Execute it!
            error_action.execute(this.oper);
        } else {
            // Ok. we have not found it either in the headers.
            // Check if there was a parsing error in the xml, 
            // and log it as reported from the dom
            // Opera <= 8.5 does not have the parseError attribute,
            // so check for it first
;;;         dom = domDoc.responseXML;
;;;         kukit.E = 'Unknown server error (invalid KSS response, no error';
;;;         kukit.E += ' info received)';
;;;         if (dom && dom.parseError && (dom.parseError != 0)) {
;;;             kukit.E += ' : ' + Sarissa.getParseErrorText(dom);
;;;             }
            throw kukit.err.responseParsingError(kukit.E);
        }
    }
    if (dom == null) {
        // this should not happen
;;;     kukit.E = 'Neither xml nor html payload.';
        throw kukit.err.responseParsingError(msg);
    }
    // find the commands (atm we don't limit ourselves inside the commandstag)
    var commands = kukit.dom.getNsTags(dom, 'command');
    // Warning, if there is a valid response containing 0 commands.
    if (commands.length == 0) {
;;;     kukit.log('No commands in kukit response');
        return;
    }
    // One or more valid commands to parse
    var command_processor = new kukit.cp.CommandProcessor();
    command_processor.parseCommands(commands, domDoc);
    kukit.engine.beginSetupEventsCollection();
    command_processor.executeCommands(this.oper);
    kukit.engine.finishSetupEventsCollection();
};

this.processError = function(errorcommand) {
    var error_action = null;
    if (this.oper.eventRule) {
        var error_action = this.oper.eventRule.actions.getErrorActionFor(
            this.oper.action);
        }
;;; var reason = '';
;;; if (typeof(errorcommand) == 'string') {
;;;     // not a command, just a string
;;;     reason = ', client_reason="' + errorcommand + '" ';
;;; } else if (typeof(errorcommand) != 'undefined') {
;;;     // a real error command, sent by the server
;;;     // as kukit payload.
;;;     // this way the server sends whatever message he wants as a parameter
;;;     // to the error command.
;;;     reason = ', server_reason="' + errorcommand.parms.message + '" ';
;;; }
    if (error_action) {
;;;     kukit.E = 'Request failed at url ' + this.oper.queueItem.url;
;;;     kukit.E += ', rid=' + this.oper.queueItem.rid + reason;
;;;     kukit.E += ', will be handled by action "' + error_action.name + '"';
;;;     kukit.logWarning(kukit.E);
        // Individual error handler was defined. Execute it!
        error_action.execute(this.oper);
    } else {
        // Unhandled: just log it...
;;;     kukit.E = 'Request failed at url ' + this.oper.queueItem.url;
;;;     kukit.E += ', rid=' + this.oper.queueItem.rid + reason;
;;;     kukit.logError(kukit.E);
;;;     return;
        // in case of no logging, we would like to throw an error.
        // This means user will see something went wrong.
        // XXX But: throwing an error on Firefox
        // _seems to be ineffective__
        // and throwing the error from IE
        // _throws an ugly window, "Uncaught exception"
        // TODO figure out something?
    }
};

// XXX XXX XXX end of copypaste


    this.initialize.apply(this, arguments);
};
// XXX Wish we could inherit here.



/* The client action that executes the server request
*/

kukit.actionsGlobalRegistry.register('cacheability-serverAction', function (oper) {
;;; oper.componentName = '[cacheability-serverAction] action';
    // allow additional parameters unlimited, in the next line
    // GET method is the default.
    // POST makes a POST: as normally, but without the kukitTimeStamp.
    oper.evaluateParameters(['url'], {'method': 'GET'}, '', true);
    // further process method
    var method = oper.parms.method.toUpperCase();
;;; if (method != 'GET' && method != 'POST') {
;;;     kukit.E = 'Bad method [' + method;
;;;     kukit.E += '], only GET or POST are allowed.';
;;;     throw new Error(kukit.E);
;;; }
    // get all keys except the ones from our parms
    var newparms = {};
    for (var key in oper.parms) {
        if (key != 'url' && key != 'method') {
            newparms[key] = oper.parms[key];
        }
    }
    var newoper = oper.clone({parms: newparms});
    // Call the action
    var sa = new ca.ServerAction(oper.parms.url, newoper, method);
    sa.execute();
});

/* 
 * This is not part of the caching, but is something that is
 * needed in some of the use cases, and is missing from
 * core.
 *
 * A variant of continueEvent from the core plugin.  This
 * can take a binderid parameter. If this is specified, the
 * binder with the corresponding id is selected for the
 * continuation event.
 *
 */
kukit.actionsGlobalRegistry.register('cacheability-triggerEventInBinder', function(oper) {
    // Trigger continuation event. Event will be triggered
    // on the same node.  If binderid specifies an id, the
    // corresponding binder will be selected for the node.
    // If binderid is empty, the singleton binder will be
    // used.
    //
    // allows excess parms in the following check.
;;; oper.componentName = '[cacheability-triggerEventInBinder] action';
    oper.evaluateParameters(['name'], {'binderid': null}, '', true);
    var parms = oper.parms;
    // marshall it, the rest of the parms will be passed and
    // can be utilized with the pass() value provider.
    // XXX Note we need to rename pass() and defaultParameters.
    var defaultParameters = {};
    for (var key in parms) {
        if (key != 'name' && key != 'binderid') {
            defaultParameters[key] = parms[key];
        }
    }
    // XXX the namespace and name has to be separated by us
    // because the current api still supports separate
    // namespace and name. However we don't want to follow
    // this with the plugin.
    var splitname = parms.name.split('-', 2);
    var namespace;
    var name;
    if (splitname.length == 2) {
        namespace = splitname[0];
        name = splitname[1];
    } else {
        namespace = null;
        name = parms.name;
    }
    // Find the binder.
    var binderid = parms.binderid;
;;; var binderid_display = binderid;
    var is_singleton = (binderid == null);
    //Get className
    var className = kukit.eventsGlobalRegistry.get(namespace, name).className;
    if (is_singleton) {
        // Get the binderid for the singleton.
        binderid = kukit.er.makeId(namespace, className);
;;;     binderid_display = '<SINGLETON>';
    }
    // Get the binder depending if it's a singleton or not
    // XXX this section will need to be changed on kss 1.5
    // (?) to match the new api. Most of the stuff done here
    // will be a service of the api.
    //
    // Try to look up the binder info.
    var binderInfo = kukit.engine.binderInfoRegistry.info[binderid];
    if (typeof(binderInfo) == 'undefined') {
        // Binder info not found. Now, if there is a bahaviour
        // rule, then we may want need to instantiate the binder.
        // This is because the behaviour rules are not really bound
        // to any node, so their binder instances are not set up
        // by default.
        //
        // XXX we create it without condition.
        binderInfo = kukit.engine.binderInfoRegistry.getOrCreateBinderInfo(
            binderid, className, namespace);
        /*
        // Look up the behaviour rule, if any.
        var mergeId = kukit.er.makeMergeId(binderid, namespace, name);
        var behavEventRule =  kukit.engine.documentRules.content.behaviour[mergeId];
        if (behavEventRule) {
            // We have a behaviour rule so let's use it.
            binderInfo = kukit.engine.binderInfoRegistry.getOrCreateBinderInfo(
                    binderid, className, namespace);
        } else {
;;;         kukit.E = 'Failed to trigger event [' + parms.name;
;;;         kukit.E += '] because neither an explicit nor a behaviour rule found ';
;;;         kukit.E += 'for the binder instance [' + binderid_display + '].';
            throw new Error(kukit.E);
        }
        */
    }
    var binder = binderInfo.getBinder();
    // execution happens on the orignode
    // XXX in this version, the namespace is not needed to
    // be passed.
    binder.continueEvent(name, oper.node,
        defaultParameters);
});
kukit.commandsGlobalRegistry.registerFromAction('cacheability-triggerEventInBinder',
    kukit.cr.makeGlobalCommand);

}();               // END CLOSURE kukit.plugin.cacheability

