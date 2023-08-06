FBL.ns(function dynamicUpdate() { with (FBL) {

const iosvc = CCSV("@mozilla.org/network/io-service;1", "nsIIOService");
const chromeReg = CCSV("@mozilla.org/chrome/chrome-registry;1", "nsIToolkitChromeRegistry");

/*
 * http://developer-stage.mozilla.org/en/docs/XMLHttpRequest
 */

function XMLHttpRequest() {}

XMLHttpRequest.prototype.open = function(method, uri, async)
{
    this.request = Components.
              classes["@mozilla.org/xmlextras/xmlhttprequest;1"].
              createInstance();
       this.request.QueryInterface(Components.interfaces.nsIDOMEventTarget);
       this.request.QueryInterface(Components.interfaces.nsIXMLHttpRequest);
    this.request.open(method, uri, async);
    if (this.onprogress)
        this.request.addEventListener("progress", this.onprogress, false);
    if (this.onload)
        this.request.addEventListener("load", this.onload, false);
    if (this.onerror)
        this.request.addEventListener("error", this.onerror, false);
    this.request.requestURI = uri;
}

XMLHttpRequest.prototype.send = function(body)
{
    this.request.send(body);
}

function UpdateRequest(){}


UpdateRequest.prototype = extend(XMLHttpRequest.prototype,  // probably should contain the req not be one.
{
    initialize: function()
    {
        var self = this;

        this.onload = function(event)
        {
            var req = event.target;
             if (FBTrace.DBG_DYNUP) FBTrace.sysout("UpdateRequest onload status:"+req.status+" readyState:"+req.readyState+" "+req.requestURI+"\n");
             if (FBTrace.DBG_DYNUP) FBTrace.sysout("UpdateRequest onload responseText: "+req.responseText+"\n");

            self.listenForUpdates();
            self.onupdate(self.updateSourceURI, req.responseText);
        }
    },

    listenForUpdates: function(uri)
    {
        if (uri)
        {
            this.initialize();
            this.updateSourceURI = uri;
        }

        this.open("GET", this.updateSourceURI, true);
        this.send(null);
    },

    onerror: function(event)
    {
        var req = event.target;
        if (FBTrace.DBG_DYNUP) FBTrace.sysout("UpdateRequest onerror status:"+req.status+" readyState:"+req.readyState+" "+req.requestURI+"\n");
    }
});


/*--------------------------------------------------------------------------*/

Firebug.DynamicUpdate = extend(Firebug.Module, {

    debug: true,

    contexts: [],

    loadedContext: function(context)
    {
        if (!this.active)  // todo initialize pref
            return;
        if (this.contexts.length == 0)
        {
            var updateSourceURL = "http://localhost:63636/updates/";  // TODO config
            this.updater = this.getSelfSustainingUpdater(updateSourceURL);
            this.contexts.push(context);
             if (FBTrace.DBG_DYNUP) FBTrace.sysout("Firebug.DynamicUpdate loadedContext new location:"+context.window.location+"\n");
        }
        else
        {
            for (var i = 0; i < this.contexts.length; i++)
            {
                if (this.contexts[i] === context)
                    return;  // already got it
            }
            this.contexts.push(context);
            if (FBTrace.DBG_DYNUP) FBTrace.sysout("Firebug.DynamicUpdate loadedContext location:"+context.window.location+"\n");
        }
    },

    getSelfSustainingUpdater: function(uri)
    {
        var updater = new UpdateRequest();
        updater.onupdate = 	function updateDocument(that_uri, responseText)
        {
            Firebug.DynamicUpdate.applyUpdate(that_uri, responseText, ChromeBug);
        };

        updater.listenForUpdates(uri);
        return updater;
    },

    applyUpdate: function(updaterURI, responseText, ChromeBug)
    {
        try
        {
            var updatedResourceLocator = Firebug.DynamicUpdate.getUpdatedResourceLocator(responseText);
            if (updatedResourceLocator)
            {
                for (var i = 0; i < this.contexts.length; i++)
                {
                    var context = this.contexts[i];
                     if (FBTrace.DBG_DYNUP) FBTrace.sysout("applyUpdate URI:"+updaterURI+" context.window.location:"+context.window.location+"\n");
                     if (FBTrace.DBG_DYNUP) FBTrace.dumpProperties("onupdate ChromeBug.extensions:", ChromeBug.extensions);
                    var sourceFile = Firebug.DynamicUpdate.getSourceFileByLocalURI(ChromeBug.extensions, updatedResourceLocator);
                    if (sourceFile)
                    {
                         if (FBTrace.DBG_DYNUP) FBTrace.sysout("onupdate for url:"+sourceFile.href+"\n");
                        return Firebug.DynamicUpdate.updateWindow(sourceFile, context.window);
                    }
                }
            }
        }
        catch(exc)
        {
            FBTrace.dumpProperties("updater FAILS", exc);
        }
    },

    updateWindow: function(updateSourceFile, window)
    {
        var updateURL = updateSourceFile.href;
        FBL.iterateWindows(window, FBL.bind(function(win)
        {
            if (!win.document.documentElement)
                return;

            var scripts = win.document.documentElement.getElementsByTagName("script");
            for (var i = 0; i < scripts.length; ++i)
            {
                var scriptSrc = scripts[i].getAttribute('src'); // for XUL use attribute
                var url = scriptSrc ? FBL.absoluteURL(scriptSrc, win.location.href) : win.location.href;
                url = FBL.normalizeURL(url ? url : win.location.href);
                if (url == updateURL)
                    return this.reloadScript(scriptSrc, win);
                 if (FBTrace.DBG_DYNUP)                                                                           /*@explore*/
                    FBTrace.sysout("updateWindow "+(scriptSrc?"inclusion":"inline   ")+" script #"+i+" | "+url+" vs "+updateURL+"\n");  /*@explore*/
            }
        }, this));
    },

    reloadScript: function(scriptURL, win)
    {
        var context = (win ? TabWatcher.getContextByWindow(win) : null);
        if (context)
        {
            context.sourceCache.invalidate(scriptURL);  // TODO check normalize
            var src = context.soureceCache.load(scriptURL);
            try
            {
                eval(src, win);
            }
            catch(exc)
            {
                FBTrace.dumpProperties("reloadScript eval FAILS", exc);  // TODO something reasonable with errors
                return false;
            }
            return true;
        }
        FBTrace.sysout("reloadScript fails to getContextByWindow for win.location="+win?win.location:"undefined window"+"\n");
    },

    getUpdatedResourceLocator: function(responseText)
    {
        var update = eval('( ' + responseText + ')');
         if (FBTrace.DBG_DYNUP) FBTrace.dumpProperties("getSelfSustainingUpdater update:", update);
        return update.URL;
    },

    getSourceFileByLocalURI: function(extensions, localURI)
    {
        if (!this.sourceFilesByLocalURI)
            this.sourceFilesByLocalURI = this.buildSourceFilesByLocalURI(extensions);

        if ( this.sourceFilesByLocalURI.hasOwnProperty(localURI) )
            return this.sourceFilesByLocalURI[localURI];
        else
            FBTrace.dumpProperties("getSourceFileByLocalURI no find localURI:"+localURI, this.sourceFilesByLocalURI)
    },

    buildSourceFilesByLocalURI: function(extensions)
    {
        this.sourceFilesByLocalURI = {};
        for (extension in extensions)
        {
            var sourceFiles = extensions[extension];  // TODO pref to pick one or more
            if (FBTrace.DBG_DYNUP)
                FBTrace.sysout("buildSourceFilesByLocalURI extension "+extension+" "+sourceFiles.length+" sourceFiles"+"\n");
            for (var i = 0; i < sourceFiles.length; i++)
            {
                var sourceFile = sourceFiles[i];
                if (sourceFile.href)
                {
                    if (FBTrace.DBG_DYNUP)
                        FBTrace.sysout("buildSourceFilesByLocalURI trying "+sourceFile.href+"\n");
                    var chromeURI = iosvc.newURI(sourceFile.href, null, null);
                    var localURI = chromeReg.convertChromeURL(chromeURI);
                    var oneSlashForm = localURI.spec.replace("file:///", "file:/");
                    this.sourceFilesByLocalURI[oneSlashForm] = sourceFile;
                }
                else
                    FBTrace.dumpProperties("buildSourceFilesByLocalURI sourceFile", sourceFile);
            }
        }
         if (FBTrace.DBG_DYNUP) FBTrace.dumpProperties("buildSourceFilesByLocalURI ", this.sourceFilesByLocalURI);
        return this.sourceFilesByLocalURI;
    },
});

Firebug.registerModule(Firebug.DynamicUpdate);
}});
