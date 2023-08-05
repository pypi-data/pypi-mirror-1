/**
 * NewPost
 * ~~~~~~~
 *
 * JS for the NewPostPage
 *
 * :copyright: 2006 by Benjamin Wiegand.
 * :license: GNU GPL, see LICENSE for more details.
 */

// XXX: i18n
var str_no_users = "No other users are currently writing a post in this thread.";
var str_guest = "Guest";
var str_new_post = "Another user wrote a new post in this thread.";


function start_check(post_id) {
    if (typeof checker.timeout == "undefined") {
        checker.root_post_id = post_id;
        checker.last_post_id = "";
        checker.timeout = window.setTimeout(checker.check, '2000');
    }
}

checker = {};

checker.check = function() {
    var call = new pocoo.lib.async.RPC('core.newpost.check');
    call.send([checker.root_post_id, checker.last_post_id], {}, function(result) {
        var box = AJS.$('box_lposts');
        AJS.removeClass(box, 'indicator');
        // XXX: Imform the user if a new post was written
        if (result) {
            box.innerHTML = result['html'] + box.innerHTML;
            checker.last_post_id = result['latestpost'];
        }
        checker.timeout = window.setTimeout(checker.check, '45000');
    });
}

function add_attachment() {
    var cont = AJS.$('att_list');
    var file = AJS.$('att_file');
    var desc = AJS.$('att_desc');
    var f = file.value.split((file.value[0] == "/") ? "/" : "\\");
    var d = (desc.value != "") ? " - " + desc.value : "";

    file.removeAttribute("id");
    desc.removeAttribute("id");
    file.parentNode.replaceChild(AJS.INPUT({type: "file", id: "att_file"}), file);
    desc.parentNode.replaceChild(AJS.INPUT({type: "text", id: "att_desc"}), desc);
    AJS.hideElement(file, desc);
    AJS.appendChildNodes(cont, file, desc);
    cont.appendChild(AJS.DIV({}, AJS.B({}, document.createTextNode(f.last())), AJS.SPAN(d)));
    AJS.showElement(cont);
}