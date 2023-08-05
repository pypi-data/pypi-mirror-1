/**
 * Display Thread
 * ~~~~~~~~~~~~~~
 *
 * :copyright: 2006 by Armin Ronacher.
 * :license: GNU GPL, see LICENSE for more details.
 */

// Get the current post from the url
var href = document.location.href + '';
current_post = parseInt(href.match(/\/post\/(\d+)/)[1]);


function showPost(this_link, post_id) {
    current_post = post_id;
    var rpc = new pocoo.lib.async.RPC('!jsonrpc');
    var method = rpc.getMethod('core.thread.get_post');
    method([post_id], {}, function(post) {
        var el = document.getElementById('post');
        el.innerHTML = post;
        var tree = document.getElementById('post_tree');
        var links = tree.getElementsByTagName('A');
        for (var i = 0; i < links.length; i++) {
            var link = links[i];
            if (link.className == 'active') {
                link.className = '';
                break;
            }
        }
        this_link.className = 'active';
    });
    return false;
}

function initAutoUpdate(tree_id, post_id) {
    var last_change = new Date();
    var rpc = new pocoo.lib.async.RPC('!jsonrpc');
    var doCheck = rpc.getMethod('core.thread.tree_requires_update');
    var doUpdate = rpc.getMethod('core.thread.get_tree');
    var check = function() {
        doCheck([post_id, last_change.toGMTString()], {}, function(result) {
            if (result) {
                last_change = new Date();
                doUpdate([current_post], {}, function(result) {
                    var el = document.getElementById(tree_id);
                    el.innerHTML = result;
                });
            }
        });
        window.setTimeout(check, 15000);
    }
    window.setTimeout(check, 15000);
}
