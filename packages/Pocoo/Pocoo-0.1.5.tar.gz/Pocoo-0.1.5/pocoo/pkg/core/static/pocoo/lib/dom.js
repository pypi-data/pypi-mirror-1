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

pocoo.lib.dom.delete_empty_textnodes = function(elem) {
    var childs = AJS.$(elem).childNodes;
    for (var z = 0; z < childs.length; z++) {
        var child = childs[z];
        if (child.nodeType == 3 && !/\S/.test(child.nodeValue))
            child.parentNode.removeChild(child);
    }
}