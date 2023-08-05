/**
 * Pocoo utils library
 * ~~~~~~~~~~~~~~~~~~~~~
 *
 * This library contains some usefull utilities
 * Also implements a fake javascript console for developers with
 * disabled / not available firebug.
 *
 * :copyright: 2006 by the Pocoo team.
 * :license: GNU GPL, see LICENSE for more details.
 */

Array.prototype.last = function() {
    return this[this.length-1];
}

pocoo.lib.compare_arrays = function(arr1, arr2) {
    if (!AJS.isArray(arr1) || !AJS.isArray(arr2)) { return false };
    if (arr1.length != arr2.length) { return false };
    for (var z = 0; z < arr1.length; z++) {
        if (!AJS.isIn(arr1[z], arr2)) {
            return false;
        }
    }
    return true;
}

function list(obj) {
    return (AJS.isArray(obj)) ? obj : [obj];
}

/* <debug> */
if (typeof console == 'undefined') {
    (function() {
        var f = function() {};
        console = {
            assert: f, count: f, debug: f, dir: f,
            dirxml: f, error: f, group: f, info: f,
            log: f, profile: f, profileEnd: f,
            time: f, timeEnd: f, trace: f, warn: f,
            firebug: 'Fake Firebug Console'
        }
    })();
}
/* </debug> */
