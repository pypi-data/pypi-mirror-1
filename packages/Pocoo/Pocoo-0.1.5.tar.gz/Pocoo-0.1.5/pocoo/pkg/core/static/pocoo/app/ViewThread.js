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
    var call = new pocoo.lib.async.RPC('core.thread.get_post');
    call.send([post_id], {}, function(post) {
        var el = AJS.$('post');
        el.innerHTML = post;
        var tree = AJS.$('post_tree');
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
}

function initAutoUpdate(tree_id, post_id) {
    var last_change = new Date();
    var doCheck = new pocoo.lib.async.RPC('core.thread.tree_requires_update');
    var doUpdate = new pocoo.lib.async.RPC('core.thread.get_tree');
    var check = function() {
        doCheck.send([post_id, last_change.toGMTString()], {}, function(result) {
            if (result) {
                last_change = new Date();
                doUpdate.send([current_post], {}, function(result) {
                    AJS.$(tree_id).innerHTML = result;
                });
            }
        });
        window.setTimeout(check, 45000);
    }
    window.setTimeout(check, 45000);
}
