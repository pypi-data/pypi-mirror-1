/* 
 * This file is part of kss.plugin.jsmath.
 * Copyright (c) 2007 KissBooth Collective, see CREDITS.txt.
 *
 * kss.plugin.jsmath is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 ONLY of the License.
 *
 * Foobar is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with kss.plugin.jsmath.  If not, see <http://www.gnu.org/licenses/>.
 */


/* 
 * jsload support for KSS (jsload)
 *
 */

/* XXX At the moment this comes in this plugin, but this should have
 * XXX its own separate nest, in fact. This is why name is Xjsload.
 */

kukit.Xjsload = new function() {

     /* Makes absolute site url
     * - if starts with http:// https:// : no change
     * - if starts with /: interprets absolute from domain
     * - othrwise: relative to current context
     */
    var _absoluteUrl = this.absoluteUrl = function(url) {
        // XXX packer breaks on following regexp constant, so it must be quoted
        // XXX (not needed in javascript syntax)
        //if (url.match(RegExp(/^https?:\/\//))) {
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
        // (paranoia: add an / to the path *only* if it is *not* there)
        // XXX packer breaks on following regexp constant, so it must be quoted
        // XXX (not needed in javascript syntax)
        //if (! path.match(RegExp(/\/$/))) {
        if (! path.match(RegExp("/\/$/"))) {
            // this really always happens...
            path += '/';
        }
        url = path + url;
        return url;
    };

    /* 
     * Javascript loader can be used to load a javascript on demand.
     *
     * Usage:
     *
     *     var loader = kukit.jsload.Loader(src, continuationHandler, extra_info);
     *     loader.load();
     *
     * src: the url of the javascript-
     * continuationHandler: this will be called if the javascript is loaded and evaluated
     *                      succesfully. (optional)
     * extra_info: extra text given in the logs (optional).
     *
     * If the loading has an error or timeout or the javascript evaluation throws 
     * an exception, the process will stop and the continuation will not be called.
     *
     */
    var _Loader = this.Loader = function(src, continuationHandler, extra_info, auto_eval) {

;;;     // Format extra info (if supplied)
;;;     if (extra_info) {
;;;         extra_info = ' [' + extra_info + ']';
;;;     } else {
;;;         extra_info = '';
;;;     }
        // auto_eval is by default on
        if (typeof(auto_eval) == 'undefined') {
            auto_eval = true;
        }
        this.src = _absoluteUrl(src);
        this.continuationHandler = continuationHandler;
        this.extra_info = extra_info;
        this.auto_eval = auto_eval
        // give a little bigger timeout here then the default.
        this.timeout = 8000; 

        this._startNotify = function(queueItem) {
;;;         // Do the start logging
;;;         var msg = "Starting on-demand loading of " + src;
;;;         msg += this.extra_info;
;;;         kukit.log(msg);
            // make a deferred callback
            var request = new XMLHttpRequest();
            var self = this;
            var notifyDone = function() {
                self._notifyDone(request, queueItem);
            }
            request.open("GET", this.src, true);
            request.onreadystatechange = notifyDone;
            request.send(null);
        };

        this._notifyDone = function(request, queueItem) {
            if (request.readyState == 4) {
                // notify the queue that we are done
                var success = queueItem.receivedResult();
                // We only process if the response has not been timed
                // out by the queue in the meantime.
                if (success) {
;;;                 // record the time of loading
;;;                 var ts_loaded = (new Date()).valueOf();
                    // store the result
                    this.code = request.responseText
                    // If we only load one file, we normally evaluate
                    // the results here.
                    // If we have a group of files, we will want to do it
                    // somewhere else, when all the files have arrived.
                    if (this.auto_eval) {
                        // process the results
                        this.evaluateCode();
                    }
;;;                 // Do the finish logging
;;;                 var ts_end = (new Date()).valueOf();
;;;                 var msg = "Finished on-demand loading"
;;;                 if (this.auto_eval) {
;;;                     msg += ' and evaluation'
;;;                 }
;;;                 msg += ' of ' + this.src
;;;                 msg += this.extra_info
;;;                 msg += ' in ' + (ts_end - queueItem.sent)
;;;                 if (this.auto_eval) {
;;;                     msg += ' (' + (ts_loaded - queueItem.sent) + ' + ';
;;;                     msg +=  (ts_end - ts_loaded) + ')'
;;;                 }
;;;                 msg += ' ms.';
;;;                 kukit.log(msg);
                    // Call the continuation
                    if (this.continuationHandler) {
                        this.continuationHandler();
                    }
                }
            }
        };

        this._processError = function(queueItem) {
;;;         // Show the user that something went wrong.
;;;         var msg = "Error (timeout) during on-demand loading of " + this.src;
;;;         msg += this.extra_info;
;;;         kukit.logError(msg);
        };

        this.load = function() {
            var self = this;
            var startNotify = function(queueItem) {
                self._startNotify(queueItem);
            };
            var processError = function(queueItem) {
                self._processError(queueItem);
            };
            kukit.engine.requestManager.notifyServer(startNotify, 
                    this.src, processError, this.timeout);
        };

        this.evaluateCode = function() {
            window.eval(this.code);
        };

    }; // end Loader
 
    /* 
     * Javascript loader can be used to load a group of javascript on demand.
     *
     * Usage:
     *
     *     var loader = kukit.jsload.Loader(continuationHandler, extra_info);
     *     loader.addSource(src1);
     *     loader.addSource(src2);
     *     loader.addSource(src3);
     *     loader.load();
     *
     * continuationHandler: this will be called if the javascript is loaded and evaluated
     *                      succesfully. (optional)
     * extra_info: extra text given in the logs (optional).
     *
     * src: the url of the javascript-
     *
     * The javascript of the sources will be evaluated in exact order, in case all loading
     * is finished.
     *
     * If one of the loadings has an error or timeout or the javascript evaluation throws 
     * an exception, the process will stop and the continuation will not be called.
     *
     */
    this.GroupLoader = function(continuationHandler, extra_info) {

;;;     // Format extra info (if supplied)
;;;     if (extra_info) {
;;;         extra_info = ' [' + extra_info + ']';
;;;     } else {
;;;         extra_info = '';
;;;     }
        this.continuationHandler = continuationHandler;
        this.extra_info = extra_info;
        this.loaders = [];
        this.sources = {};

        this.add = function(src) {
            if (typeof(this.sources[src]) != 'undefined') {
                // This source is already added. Let's ignore.
                return;
            }
            var self = this;
            var continuation = this._groupContinuations.makeContinuation(src);
            // create a loader with no evaluation intended, since we do it
            // when all files got back.
            var loader = new _Loader(src, continuation, this.extra_info, false);
            this.loaders.push(loader);
            this.sources[src] = true;
        };

        this.empty = function() {
            return (this.loaders.length == 0);
        };

        this.getSources = function() {
            result = []
            for (var i = 0; i < this.loaders.length; i++) {
                result.push(this.loaders[i].src);
            }
            return result;
        };

        this.load = function() {
            for (var i = 0; i < this.loaders.length; i++) {
                this.loaders[i].load();
            }
        };

        this._loadFinish = function() {
            var nrLoaders = this.loaders.length;
;;;         // Do the start logging
;;;         var ts_start = (new Date()).valueOf();
;;;         var msg = "Start evaluation";
;;;         msg += ' of ' + nrLoaders + ' javascript sources.';
;;;         kukit.log(msg);
            for (var i = 0; i < nrLoaders; i++) {
                this.loaders[i].evaluateCode();
            }
;;;         // Do the finish logging
;;;         var ts_end = (new Date()).valueOf();
;;;         var msg = "Finished evaluation"
;;;         msg += ' of ' + nrLoaders + ' javascript sources'
;;;         msg += ' in ' + (ts_end - ts_start) + ' ms.'
;;;         kukit.log(msg);
            // Call the continuation
            if (this.continuationHandler) {
                this.continuationHandler();
            }
        };

        /* This singleton manages a final continuation when all individual
         * contuations have arrived. */
        var _GroupContinuations = function(groupContinuationHandler) {
            var waitingNr = 0;

            var _handleContinue = function(src) {
                // We don't really care for src... only count them.
                // but it could be used for better error logging,
                // once it's needed.
                waitingNr -= 1;
                // All the files arrived?
                if (waitingNr == 0) {
                    // If yes, call the group continuation.
                    groupContinuationHandler();
                }
            }

            this.makeContinuation = function(src) {
                waitingNr += 1;
                var self = this;
                var f = function() {
                    return _handleContinue(src);
                };
                return f;
            };

        };

        // Set up the group continuations handler
        var self = this;
        var loadfinish = function() {
            self._loadFinish()
        };
        this._groupContinuations = new _GroupContinuations(loadfinish);

    };          // end GroupLoader

}();


/* 
 * jsMath support for KSS (jsmath)
 *
 */

new function() {
    
    // The javascript file that we must load
    var sources = ["/++resource++jsmath/jsMath.js",
                   "/++resource++jsmath/plugins/tex2math.js"];

    var do_activate = function(oper) {
        //
        // Set some parameters
        //
        var parms = oper.parms;

        // Disable double clicks
        if (!jsMath.Click) {jsMath.Click = {};}
        jsMath.Click.CheckDblClick = function () {};

        // Scale up a bit
        // XXX this will change size globally in the page though!
        jsMath.Controls.cookie.scale = parms.scale;
        jsMath.Setup.Styles();

        // get rid of any jsMath Process... messages
        jsMath.Message.Set = function() {};
        
        // Remove the warnings that are on the screen already
        // This is justa fallback, we should have taken care of
        // this already before the loading.
        jsMath.Font.HideMessage();

        // tag elements with "math" class, that contain markup
        jsMath.tex2math.Convert(oper.node, {
                processSingleDollars: parms.processSingleDollars, 
                processDoubleDollars: parms.processDoubleDollars,
                processSlashParens: parms.processSlashParens, 
                processSlashBrackets: parms.processSlashBrackets,
                processLaTeXenvironments: parms.processLaTeXenvironments,
                custom: parms.custom,
                fixEscapedDollars: parms.fixEscapedDollars});

        // process markup
        jsMath.Process(oper.node);

        // get rid of jsMath button
        document.getElementById('jsMath_button').style.display = 'none';

    };
    
    var _friendlyLog = function(message) {
;;;         kukit.log('JsMath says: ' + message);
    };

    var activate = function(oper) {
        ;;; oper.componentName = '[jsmath-activate] action';
        oper.evaluateParameters([], {
            // scaling factor
            scale: '120',
            // parameters for conversion cueing
            processSingleDollars: '', 
            processDoubleDollars: '',
            processSlashParens: 'true', 
            processSlashBrackets: 'true',
            processLaTeXenvironments: 'true',
            custom: '',
            fixEscapedDollars: ''});
        oper.evalInt('scale');
        oper.evalBool('processSingleDollars');
        oper.evalBool('processDoubleDollars');
        oper.evalBool('processSlashParens');
        oper.evalBool('processSlashBrackets');
        oper.evalBool('processLaTeXenvironments');
        oper.evalBool('custom');
        oper.evalBool('fixEscapedDollars');
        // Check if the javascript is loaded?
        var is_loaded = (typeof(window.jsMath) != 'undefined');
        if (is_loaded) {
            // do activation
            do_activate(oper);
        } else {
            // Before loading, we need to set the root url thet jsMath
            // will use for loading its extras.
            // We really *must* give it a full url. If we just give a
            // traverse path within the site, jsMath will chuckle on it
            // if there is a port number. (will blit the warning, and so on).
            var baseurl = kukit.Xjsload.absoluteUrl('/++resource++jsmath/');
            window.jsMath = {Autoload: {root:          baseurl},
                             Font:     {Message:       _friendlyLog,
                                        PrintMessage:  _friendlyLog}};
            // load javascripts, and set its continuation
            var f = function() {
                do_activate(oper);
            };
            var loader = new kukit.Xjsload.GroupLoader(f);
            for (var i = 0; i < sources.length; i++) {
                // Fortunately, loader sanitizes url-s so we need not
                // worry about that.
                loader.add(sources[i]);
            }
            loader.load();
        }
    };
    kukit.actionsGlobalRegistry.register('jsmath-activate', activate);
    kukit.commandsGlobalRegistry.registerFromAction('jsmath-activate',  kukit.cr.makeGlobalCommand);
    
}();

