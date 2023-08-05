/**
 * Pocoo async library
 * ~~~~~~~~~~~~~~~~~~~
 *
 * This library is for creating of asynchronous XMLHttpRequests.
 *
 * :copyright: 2006 by the Pocoo team.
 * :license: GNU GPL, see LICENSE for more details.
 */

var msg_no_connection = "When requesting data, the server didn't send a response. May you lost your connection to the internet or the server crashed.";
var msg_not_allowed = "The action you tried to execute is not allowed.";
var msg_error = "When requesting data, the server caused the following error error:";
var msg_inform_admin = "Please inform the administrator about this problem.";

if (typeof(pocoo) == "undefined") {
    pocoo = {};
    pocoo.lib = {};
}

pocoo.lib.async = {};

function loadTab(obj, caller, method, args, send) {
    obj = AJS.$(obj);
    if (arguments.length > 2) {
        AJS.addClass(AJS.setHTML(obj, ""), "indicator");
        AJS.map(send, function(e) {
            args.push(AJS.$(e).value);
        })
        var call = new pocoo.lib.async.RPC(method);
        call.send(args, {}, function(res) {
            AJS.removeClass(AJS.setHTML(obj, res), "indicator");
        });
    }
    AJS.setClass(AJS.forceArray(caller.parentNode.childNodes), "tab");
    AJS.hideElement(AJS.forceArray(AJS.filter(obj.parentNode.childNodes, function(e) { return e.nodeType == 1 })));
    caller.className = "tab active_tab";
    obj.style.display = "block";
    caller.style.display = "block";
}

pocoo.lib.async.RPC = function(method) {
    this.method = method;
}

pocoo.lib.async.RPC.prototype.send = function(args, kwargs, callback) {
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
        method:         this.method,
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
    req.open('POST', base_url + '!jsonrpc', true);
    req.setRequestHeader('Content-Type', 'application/json');
    req.setRequestHeader('Accept', 'application/json');
    req.send(data);
    return req;
}

function ajax(func) {
    try {
        if (pocoo.no_ajax) {
            throw new Exception();
        }
        AJS.getXMLHttpRequest()();
        return true;
    } catch(e) {
        (func) ? func() : "";
        return false;
    };
}