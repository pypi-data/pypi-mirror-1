/**
 * Pocoo async library
 * ~~~~~~~~~~~~~~~~~~~
 *
 * This library is for creating of asynchronous XMLHttpRequests.
 *
 * :copyright: 2006 by the Pocoo team.
 * :license: GNU GPL, see LICENSE for more details.
 */

if (typeof(pocoo) == "undefined") {
    pocoo = {};
    pocoo.lib = {};
}

pocoo.lib.async = {};

pocoo.lib.async.RPC = function(url) {
    this.url = base_url + url;
}

pocoo.lib.async.RPC.prototype.getMethod = function(method) {
    var url = this.url;
    return function(args, kwargs, callback) {
        var params = {};
        for (var idx in args) {
            params[idx] = args[idx];
        }
        for (var key in kwargs) {
            params[key] = args[key];
        }
        var emitError = function(data) {
            // XXX: How to i18n these strings?
            if (data instanceof XMLHttpRequest) {
                try {
                    var status = data.status;
                } catch(e) {
                    pocoo.lib.effects.hint.show("When requesting data, the server didn't send a response. May you lost your connection to the internet or the server crashed.");
                    return true;
                }
                if (status == 403) { // AccessDenied
                    pocoo.lib.effects.hint.show("The action you tried to execute is not allowed.");
                }
            } else if (typeof data.error != "undefined") {
                pocoo.lib.effects.hint.show("When requesting data, the server caused a "+ data.error.type +":<br /><pre>" + data.error.msg + ".</pre>Please inform the administrator about this problem.");
            } else {
                pocoo.lib.effects.hint.show("When requesting data, an unknown error occured.<br />Please inform the administrator about this problem.");
            }
        }
        var req = AJS.getXMLHttpRequest();
        var args = AJS.forceArray(arguments);
        var data = AJS.serializeJSON({
            version:        '1.1',
            method:         method,
            params:         params
        });
        req.onreadystatechange = function() {
            if (req.readyState == 4) {
                try {
                    if (typeof req.status != 'undefined' && (
                        req.status == 200 || req.status == 304)) {
                        var response = AJS.evalTxt(req.responseText);
                        if (typeof response.error != 'undefined') {
                            emitError(response.error);
                        } else {
                            callback(response.result);
                        }
                    } else {
                        emitError(req);
                    }
                }
                catch(e) {
                    emitError(req);
                }
            }
        };
        req.open('POST', url, true);
        req.setRequestHeader('Content-Type', 'application/json');
        req.setRequestHeader('Accept', 'application/json');
        req.send(data);
        return req;
    }
}
