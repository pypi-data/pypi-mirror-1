/**
 * Pocoo effects library
 * ~~~~~~~~~~~~~~~~~~~~~
 *
 * This library contains some special effects.
 *
 * :copyright: 2006 by the Pocoo team.
 * :license: GNU GPL, see LICENSE for more details.
 */

if (typeof(pocoo) == "undefined") {
    pocoo = {};
    pocoo.lib = {};
}

pocoo.lib.effects = {};

/**
 * Pocoo DialogBox
 * ===============
 * This shows a centered dialog box and fades out the background
 * === Usage ===:
 *      var box = new pocoo.lib.effects.DialogBox();
 *      box.setTitle(abc);
 *      box.loadContentFromJson("core.my.json.rpc", ['abc'], {'test':'Hello world'}, true)
 *      box.setDimension(500, 250);
 *      pocoo.lib.effects.DialogBox.show(box)
 */

pocoo.lib.effects.DialogBox = function() {
    this.id = pocoo.lib.effects.DialogBox.id;
    pocoo.lib.effects.DialogBox.id = this.id + 1;
    this.loaded = true;
    this.wait = false;
    this.width = 400;
    this.height = 200;

    this.setTitle = function(title) {
        this.title = title;
    }

    this.loadContentFromJson = function(id, args, kwargs, /* optional */ wait) {
        /* wait defines whether the box should stay hidden until the rpc call is finished */
        if (typeof(wait) == "undefined") {
            wait = true;
        }
        this.wait = wait;
        this.loaded = false;
        var rpc = new pocoo.lib.async.RPC('!jsonrpc');
        var method = rpc.getMethod(id);
        method(args, kwargs, eval('function(content) { pocoo.lib.effects.DialogBox.show(' + this.id + ', content); }'));
    }

    this.setDimension = function(x, y) {
        this.width = x;
        this.height = y;
    }
}

pocoo.lib.effects.DialogBox.id = 0;
pocoo.lib.effects.DialogBox.queue = [];
pocoo.lib.effects.DialogBox.locked = false;

pocoo.lib.effects.DialogBox.show = function(obj, content) {
    function _iterate_objects(elem) {
        try {
            var handler = elem.getAttribute("pocoo:handler");
            if (handler != null) {
                if (handler == "closeDialog") {
                    elem.onclick = function() {
                        pocoo.lib.effects.DialogBox.close();
                    }
                }
            }
        } catch(e) {}
        if (elem.hasChildNodes()) {
            for (var z = 0; z < elem.childNodes.length; z++) {
                _iterate_objects(elem.childNodes[z]);
            }
        }
    }

    var get = pocoo.lib.dom.get_or_create;
    this.bg = get("dialogbg", "div");
    this.box = get("dialogbox", "div");
    this.title = get("dialogtitle", "h2", this.box);
    this.content = get("dialogcontent", "div", this.box);

    if (typeof obj == "number") { // if obj is an id
        for (var z = 0; z < this.queue.length; z++) {
            inst = this.queue[z];
            if (inst.id == obj) {
                obj = inst;
                obj.content = content;
                obj.loaded = true;
                this.queue.splice(0,1);
                break;
            }
        }
        // if obj is still an id --> no object with this id in queue
        if (typeof obj == "number") { return false; }
    }

    // if no obj in arguments get the first one in queue
    if (arguments.length == 0) {
        if (this.queue.length > 0) {
            var obj = this.queue[0];
            this.queue.splice(0,1);
        } else {
            return false;
        }
    }

    if (this.locked) {
        this.queue.push(obj);
        return;
    }

    AJS.setOpacity(this.bg, 0);
    AJS.setOpacity(this.box, 0);

    if (!obj.wait || (obj.wait && obj.loaded)) {
        this.locked = true;
        this.content.innerHTML = obj.content;
        _iterate_objects(this.content);
        this.title.innerHTML = obj.title;
        this.box.style.width = obj.width + "px";
        this.box.style.height = obj.height + "px";
        var margin = "-" + 0.5 * (obj.height + 15) + "px 0 0 -" + (0.5 * obj.width) + "px";

        this.box.style.margin = margin;
        this.box.style.display = "none";
        var callback = eval('function() { pocoo.lib.effects.fade("' + this.box.id + '", 0, 100); }');
        pocoo.lib.effects.fade(this.bg.id, 0, 50, callback);
    } else {
        this.queue.push(obj);
        window.setTimeout('pocoo.lib.effects.DialogBox.show()', 5000);
    }
}

pocoo.lib.effects.DialogBox.close = function() {
    // XXX: effect library
    this.bg.style.display = "none";
    this.box.style.display = "none";
    this.locked = false;
    // show the next dialog in queue
    this.show();
}

/* fades an object in or out */

pocoo.lib.effects.fade = function(obj, from, to, callback) {
    AJS.$(obj).style.display = "block";
    AJS.setOpacity(AJS.$(obj), (from / 100));
    if (from != to) {
        window.setTimeout('pocoo.lib.effects.fade("' + obj + '",' + (from + 10) +', ' + to + ', ' + callback + ')', 100);
    } else {
        if (typeof callback != "undefined") {
            window.setTimeout(callback, 100);
        }
    }
}

/**
 * An info box
 * ===========
 * This info box scrolls up from the bottom of the page
 * === Usage ===
 * pocoo.lib.effects.hint.show("Hello World!")
 */

pocoo.lib.effects.hint = {};

pocoo.lib.effects.hint.queue = new Array();

pocoo.lib.effects.hint.speed = 4;

pocoo.lib.effects.hint.height = 40;

pocoo.lib.effects.hint.show = function(text) {
    if (this.locked == true) {
        this.queue.push(text);
        return;
    }
    this.locked = true;
    this.elem = pocoo.lib.dom.get_or_create("hint", "div");
    this.h2 = pocoo.lib.dom.get_or_create("hint-h2", "h2", this.elem);
    this.text = pocoo.lib.dom.get_or_create("hint-text", "div", this.elem);
    this.text.innerHTML = text;
    this.h2.innerHTML = "Hint";
    this.elem.style.display = "block";
    this.elem.style.height = "0px";
    this._move_updown(this.height, this.speed);
}

pocoo.lib.effects.hint._move_updown = function(count, move) {
    if (count > 0) {
        this.elem.style.height = (parseInt(this.elem.style.height) + move) + "px";
        window.setTimeout('pocoo.lib.effects.hint._move_updown(' + (count-1) + ', ' + move + ');', 30);
    } else  {
        this._done(move);
    }
}

pocoo.lib.effects.hint._done = function(move) {
    if (move > 0) {
        // move back down in 8 seconds
        window.setTimeout('pocoo.lib.effects.hint._move_updown(' + this.height + ', -' + this.speed + ');', 8000);
    } else {
        if (this.queue.length > 0) {
            this.text.innerHTML = this.queue.shift();
            this._move_updown(this.height, this.speed);
        } else {
            this.elem.style.display = "none";
            this.locked = false;
        }
    }
}
