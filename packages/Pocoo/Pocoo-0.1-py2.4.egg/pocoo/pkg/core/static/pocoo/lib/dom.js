/**
 * Pocoo DOM library
 * ~~~~~~~~~~~~~~~~~
 *
 * A library for manipulating DOM elements.
 *
 * :copyright: 2006 by the Pocoo team.
 * :license: GNU GPL, see LICENSE for more details.
 */

if (typeof(pocoo) == "undefined") {
    pocoo = {};
    pocoo.lib = {};
}

pocoo.lib.dom = {};

pocoo.lib.dom.get_or_create = function(obj, type, container) {
    // if obj exists return it, else create it
    if (AJS.$(obj) != null) {
        return AJS.$(obj);
    } else {
        var elem = document.createElement(type);
        elem.id = obj;
        (container) ? container.appendChild(elem) : AJS.getBody().appendChild(elem);
        return elem;
    }
}
