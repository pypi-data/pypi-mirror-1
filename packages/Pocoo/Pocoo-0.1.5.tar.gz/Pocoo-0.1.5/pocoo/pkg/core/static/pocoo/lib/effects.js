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
 *      box.title = "abc";
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
    this.callbacks = [];

    this.loadContentFromJson = function(id, args, kwargs, /* optional */ wait) {
        /* wait defines whether the box should stay hidden until the rpc call is finished */
        if (typeof(wait) == "undefined") wait = true;
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

    this.submit = function(form) {
        var args = {};
        for (var z = 0; z < form.elements.length; z++) {
            var elem = form.elements[z];
            args[elem.name] = elem.value;
        }
        for (var z = 0; z < this.callbacks.length; z++) {
            /* XXX: This is a dirty sollution, find a better one!
            I made this to don't have this == document inside "this.testfunction"
            >>> box.callbacks.push(this, "testfunction")
            */
            this.callbacks[z][0][this.callbacks[z][1]](args);
        }
        pocoo.lib.effects.DialogBox.close();
    }
}

pocoo.lib.effects.DialogBox.id = 0;
pocoo.lib.effects.DialogBox.queue = [];
pocoo.lib.effects.DialogBox.locked = false;

pocoo.lib.effects.DialogBox.show = function(obj, content) {
    function _iterate_objects(elem) {
        try {
            switch (elem.getAttribute("pocoo:handler")) {
                case "abort":
                    elem.onclick = function() { pocoo.lib.effects.DialogBox.close(); };
                    break;
                case "submit":
                    elem.form.box = obj;
                    elem.onclick = function() { this.form.box.submit(this.form) };
                    break;
            }
        } catch(e) {}
        AJS.map(elem.childNodes, function(elm) {
            _iterate_objects(elm);
        });
    }

    var get = pocoo.lib.dom.get_or_create;
    this.bg = get("dialogbg", "div");
    this.box = get("dialogbox", "div");
    this.title = get("dialogtitle", "h2", this.box);
    this.content = get("dialogcontent", "div", this.box);

    if (AJS.isNumber(obj)) { // if obj is an id
        obj = AJS.filter(this.queue, function(n) {
            return n.id == obj
        })[0];
        obj.content = content;
        obj.loaded = true;
        this.queue.splice(0,1);
    }

    // if no obj in arguments get the first one in queue
    if (arguments.length == 0) {
        if (this.queue.length > 0) {
            var obj = this.queue.splice(0,1)[0]
        } else return false;
    }

    if (this.locked) return this.queue.push(obj);

    AJS.setOpacity(this.bg, 0);
    AJS.setOpacity(this.box, 0);

    if (!obj.wait || (obj.wait && obj.loaded)) {
        this.locked = true;
        this.content.innerHTML = obj.content;
        _iterate_objects(this.content);
        this.title.innerHTML = obj.title;
        AJS.setWidth(this.box, obj.width);
        AJS.setHeight(this.box, obj.height);

        var margin = "-" + 0.5 * (obj.height + 15) + "px 0 0 -" + (0.5 * obj.width) + "px";

        this.box.style.margin = margin;
        AJS.hideElement(this.box);
        pocoo.lib.effects.fade(this.bg.id, 0, 50, eval('function() { pocoo.lib.effects.fade("' + this.box.id + '", 0, 100); }'));
    } else {
        this.queue.push(obj);
        window.setTimeout('pocoo.lib.effects.DialogBox.show()', 5000);
    }
}

pocoo.lib.effects.DialogBox.close = function() {
    AJS.hideElement(this.bg, this.box);
    this.locked = false;
    // show the next dialog in queue
    this.show();
}

pocoo.lib.effects.fade = function(obj, from, to, callback) {
    AJS.showElement(AJS.$(obj));
    AJS.setOpacity(AJS.$(obj), (from / 100));
    if (from != to) {
        window.setTimeout('pocoo.lib.effects.fade("' + obj + '",' + (from + 25) +', ' + to + ', ' + callback + ')', 1);
    } else {
        if (typeof callback != "undefined") window.setTimeout(callback, 100);
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

pocoo.lib.effects.hint.queue = [];

pocoo.lib.effects.hint.speed = 4;

pocoo.lib.effects.hint.height = 40;

pocoo.lib.effects.hint.show = function(text) {
    if (this.locked == true) return this.queue.push(text);
    this.locked = true;
    var get = pocoo.lib.dom.get_or_create;
    this.elem = get("hint", "div");
    this.h2 = get("hint-h2", "h2", this.elem);
    this.text = get("hint-text", "div", this.elem);
    this.text.innerHTML = text;
    this.h2.innerHTML = "Hint";
    AJS.showElement(this.elem);
    AJS.setHeight(this.elem, 0);
    this._move_updown(this.height, this.speed);
}

pocoo.lib.effects.hint._move_updown = function(count, move) {
    if (count > 0) {
        AJS.setHeight(this.elem, parseInt(this.elem.style.height) + move);
        window.setTimeout('pocoo.lib.effects.hint._move_updown(' + (count-1) + ', ' + move + ');', 30);
    } else this._done(move);
}

pocoo.lib.effects.hint._done = function(move) {
    if (move > 0) return window.setTimeout('pocoo.lib.effects.hint._move_updown(' + this.height + ', -' + this.speed + ');', 8000);

    if (this.queue.length > 0) {
        this.text.innerHTML = this.queue.shift();
        this._move_updown(this.height, this.speed);
    } else {
        AJS.hideElement(this.elem);
        this.locked = false;
    }
}