pref("extensions.chromebug.outerWidth", 0);
pref("extensions.chromebug.outerHeight", 0);
pref("extensions.chromebug.openalways", false);
pref("extensions.chromebug.extensions", "none");
pref("extensions.chromebug.DBG_CHROMEBUG", false); // /*@explore*/


// Global
pref("extensions.chromebug.disabledAlways", false);
pref("extensions.chromebug.allowSystemPages", false);
pref("extensions.chromebug.disabledFile", true);
pref("extensions.chromebug.defaultPanelName", "html");
pref("extensions.chromebug.throttleMessages", true);
pref("extensions.chromebug.textSize", 0);
pref("extensions.chromebug.showInfoTips", true);
pref("extensions.chromebug.largeCommandLine", false);
pref("extensions.chromebug.textWrapWidth", 100);
pref("extensions.chromebug.openInWindow", false);
pref("extensions.chromebug.showErrorCount", true);
pref("extensions.chromebug.showIntroduction", true);
pref("extensions.chromebug.viewPanelOrient", "horizontal");

// Console
pref("extensions.chromebug.showJSErrors", true);
pref("extensions.chromebug.showJSWarnings", false);
pref("extensions.chromebug.showCSSErrors", false);
pref("extensions.chromebug.showXMLErrors", false);
pref("extensions.chromebug.showChromeErrors", false);
pref("extensions.chromebug.showChromeMessages", false);
pref("extensions.chromebug.showExternalErrors", false);
pref("extensions.chromebug.showXMLHttpRequests", true);

pref("extensions.chromebug.console.enableLocalFiles", "default");
pref("extensions.chromebug.console.enableSystemPages", "default");

// HTML
pref("extensions.chromebug.showCommentNodes", false);
pref("extensions.chromebug.showWhitespaceNodes", false);
pref("extensions.chromebug.showFullTextNodes", true);
pref("extensions.chromebug.highlightMutations", true);
pref("extensions.chromebug.expandMutations", false);
pref("extensions.chromebug.scrollToMutations", false);
pref("extensions.chromebug.shadeBoxModel", true);

// CSS
pref("extensions.chromebug.showComputedStyle", false);

// Stack
pref("extensions.chromebug.omitObjectPathStack", false);

// DOM
pref("extensions.chromebug.showUserProps", true);
pref("extensions.chromebug.showUserFuncs", true);
pref("extensions.chromebug.showDOMProps", true);
pref("extensions.chromebug.showDOMFuncs", false);
pref("extensions.chromebug.showDOMConstants", false);

// Layout
pref("extensions.chromebug.showAdjacentLayout", false);
pref("extensions.chromebug.showRulers", true);

// Script
pref("extensions.chromebug.script.enableLocalFiles", "default");
pref("extensions.chromebug.script.enableSystemPages", "default");

// Net
pref("extensions.chromebug.netFilterCategory", "all");
pref("extensions.chromebug.disableNetMonitor", false);
pref("extensions.chromebug.collectHttpHeaders", true);
pref("extensions.chromebug.net.enableLocalFiles", "default");
pref("extensions.chromebug.net.enableSystemPages", "default");

// External Editors
pref("extensions.chromebug.externalEditors", "");

// Trace  /*@explore*/
pref("extensions.chromebug.DBG_BP", false); 			// debugger.js and firebug-services.js; lots of output   /*@explore*/
pref("extensions.chromebug.DBG_TOPLEVEL", false); 	// top level jsd scripts                     /*@explore*/
pref("extensions.chromebug.DBG_STACK", false);  		// call stack, mostly debugger.js            /*@explore*/
pref("extensions.chromebug.DBG_UI_LOOP", false); 		// debugger.js                               /*@explore*/
pref("extensions.chromebug.DBG_ERRORS", false);  		// error.js                                  /*@explore*/
pref("extensions.chromebug.DBG_EVENTS", false);  		// debugger.js for event handlers, need more /*@explore*/
pref("extensions.chromebug.DBG_FUNCTION_NAMES", false);  // heuristics for anon functions          /*@explore*/
pref("extensions.chromebug.DBG_EVAL", false);    		// debugger.js and firebug-service.js        /*@explore*/
pref("extensions.chromebug.DBG_PANELS", false);  		// panel selection                           /*@explore*/
pref("extensions.chromebug.DBG_DOM", false);  //                                             /*@explore*/
pref("extensions.chromebug.DBG_CACHE", false);   		// sourceCache                               /*@explore*/
pref("extensions.chromebug.DBG_SOURCEFILES", false); 	// debugger and sourceCache                  /*@explore*/
pref("extensions.chromebug.DBG_WINDOWS", false);    	// tabWatcher, dispatch events; very useful for understand modules/panels  /*@explore*/
pref("extensions.chromebug.DBG_NET", false);        	// net.js                                    /*@explore*/
pref("extensions.chromebug.DBG_INITIALIZE", false);   // registry (modules panels); initialize FB  /*@explore*/
pref("extensions.chromebug.DBG_OPTIONS", false);      // /*@explore*/
pref("extensions.chromebug.DBG_INSPECT", false);      // /*@explore*/
