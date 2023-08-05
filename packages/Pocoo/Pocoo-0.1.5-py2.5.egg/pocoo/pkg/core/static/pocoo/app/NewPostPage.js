/**
 * NewPost
 * ~~~~~~~
 *
 * JS for the NewPostPage (preview etc.)
 *
 * :copyright: 2006 by Benjamin Wiegand.
 * :license: GNU GPL, see LICENSE for more details.
 */


function getLatestPosts(root_post_id, obj) {
    var rpc = new pocoo.lib.async.RPC('!jsonrpc');
    var method = rpc.getMethod('core.newpost.get_latest_posts');
    method([root_post_id], {}, function (result) {
        var cont = AJS.$("lastposts");
        cont.innerHTML = result["html"];
        cont.className = "loaded";
        AJS.showElement(cont, AJS.$("lposts2"));
        AJS.hideElement(obj);
        checker.root_post_id = root_post_id;
        checker.last_post_id = result["last_post"];
        checker.timeout = window.setTimeout(checker.checkNewPosts, '2000');
    });
}

// XXX: Does anybody know a better name? ^^
checker = {};

checker.checkNewPosts = function(post_id, last_post) {
    var rpc = new pocoo.lib.async.RPC('!jsonrpc');
    var method = rpc.getMethod('core.newpost.check_new_posts');
    method([checker.root_post_id, checker.last_post_id], {}, function(result) {
        if (result !== false) {
            var cont = AJS.$("lastposts");
            cont.innerHTML = result["html"] + cont.innerHTML;
            checker.last_post_id = result["last_post"];
        }
        checker.timeout = window.setTimeout(checker.checkNewPosts, '15000');
    });
}
