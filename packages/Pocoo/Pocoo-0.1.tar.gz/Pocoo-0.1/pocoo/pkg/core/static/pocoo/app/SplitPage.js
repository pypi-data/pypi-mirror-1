/**
 * SplitPage
 * ~~~~~~~~~
 *
 * JavaScript for splitting threads.
 *
 * :copyright: 2006 by Benjamin Wiegand.
 * :license: GNU GPL, see LICENSE for more details.
 */

split = {};

split.changes = {};

split.posts = {};

split.threads = [];

Post = function(data) {
    this.post_id = data["post_id"];
    this.parent_id = data["parent_id"];
    this.title = data["title"];
}

Thread = function(data) {
    this.root_post_id = data["root_post_id"];
    this.forum_id = data["forum_id"];
}

split.get_post_list = function(root_post_id, container) {
    this.container = AJS.$(container);
    var rpc = new pocoo.lib.async.RPC('!jsonrpc');
    var method = rpc.getMethod('core.split.get_post_tree');
    method([root_post_id], {}, split._write_posts);
}

split._write_posts = function(data) {
    var tmp = split.threads.length;
    var thread = new Thread(data["thread"]);
    thread["position"] = tmp;
    split.threads.push(thread);
    split.container.parentNode.onmousedown = eval('function() { return split.threads[' + (tmp) +']; }');

    var li = split._render_posts(data["posts"])[0];
    split.container.appendChild(li);
    // make the containers sortable
    var s = MochiKit.Sortable.Sortable;
    s.create(split.container, {'tree':true, containment:['thread-1','thread-2'], constraint:false});
    s.create("thread-2", {'tree':true, containment:['thread-2','thread-1'], constraint:false});
}

split._render_posts = function(posts) {
    var lis = [];
    for (var a = 0; a < posts.length; a++) {
        var children = [];
        var post = posts[a];
        var li = document.createElement("li");
        var ul = document.createElement("ul");

        li.id = "post-" + post["post_id"];
        li.innerHTML = post["title"];
        li.onmouseup = eval('function() { split.after_move(this, split.posts[' + post["post_id"] +']); }');
        li.onmousedown = eval('function() { return split.posts[' + post["post_id"] +']; }');

        if (typeof(post["children"]) != "undefined") {
            children = this._render_posts(post["children"]);
        }
        for (var b = 0; b < children.length; b++) {
            child = children[b];
            ul.appendChild(child);
        }

        li.appendChild(ul);
        lis.push(li);
        this.posts[post["post_id"]] = new Post(post);
    }
    return lis
}

split.after_move = function(obj, post) {
    parent_obj = obj.parentNode.parentNode;
    parent_data = parent_obj.onmousedown(); // get post data
    if (parent_data instanceof Post) {
        if (post.parent_id != parent_data.post_id) { // if parent of post changed
            this._new_change(post, parent_data);
        }
    } else if (parent_data instanceof Thread) {
        if (parent_data.root_post_id != post.post_id) { // if post is a new root_post
            this._new_change(post, parent_data);
        }
    }
}

split._new_change = function(post, moved_to) {
    if (moved_to instanceof Post) {
        this.changes[post.post_id] = {
            'moved_to_post':moved_to.post_id
        };
    } else {
        this.changes[post.post_id] = {
            'moved_to_thread':moved_to.position
        };
        this.id2obj(post.post_id).appendChild(this.id2obj(moved_to.root_post_id));
        this.threads[moved_to["position"]].root_post_id = post.post_id;
    }
}

split.id2obj = function(post_id) {
    return AJS.$("post-" + post_id);
}

split.commit = function() {
    var d = this.rpc.call('core.split.commit', this.changes);
    d.addCallback(function(result) {
        alert(result);
    });
    d.addErrback(function(result) {
        alert(result);
    });
}
