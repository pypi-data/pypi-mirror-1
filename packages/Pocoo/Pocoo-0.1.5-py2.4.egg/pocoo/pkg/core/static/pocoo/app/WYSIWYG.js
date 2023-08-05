/**
 * Pocoo WYSIWYG library
 * ~~~~~~~~~~~~~~~~~~~
 *
 * :copyright: 2006 by Benjamin Wiegand
 * :license: GNU GPL, see LICENSE for more details.
 */


function create_editor(elem, toolbar, opts) {
    elem = AJS.$(elem);
    var ifr = AJS.IFRAME({id: elem.id, className: "textarea"});
    AJS.swapDOM(elem, ifr);
    ifr.data = [AJS.$(toolbar), opts];
    ifr.onload = function(evt) {
        new Editor(this, this.data[0], this.data[1]);
        var func = function(evt) {
            this.editor.handle_key(new Key(evt));
        }
        if (document.addEventListener) ifr.contentDocument.addEventListener("keypress", func, true)
        else ifr.contentDocument.onkeypress = func;
    }
}

function Editor(ifr, toolbar, opts) {
    ifr.contentDocument.editor = this;
    ifr.contentDocument.designMode = "On";
    this.area = ifr;
    this.toolbar = toolbar;
    this.col = this.row = 0;
    this.opts = opts;
    this.active_tags = [];
    this.codes = opts["codes"];

    for (var z = 0; z < this.codes.length; z++) {
        var code = this.codes[z];
        switch(code["t"]) {
            case 1:
                var a = AJS.A(AJS.IMG({src: opts["img_folder"] + code["img"], alt: code["name"], title: code["name"]}))
                a.onclick = function() { this.editor.do_format(this.com); }
                break;
            case 2:
                var a = AJS.SELECT();
                for (var y = 0; y < code["options"].length; y++) {
                    var opt = code["options"][y];
                    a.appendChild(AJS.OPTION({value: opt[0]}, opt[1]));
                }
                a.onchange = function() { this.editor.do_format(this.com); }
        }
        a.com = code["exec"];
        a.editor = this;
        this.toolbar.appendChild(a);
    }


    this.do_format = function(com) {
        if (this.selection) {
            // XXX
        } else {
            this.area.contentDocument.execCommand(com, false, "");
        }
        this.area.contentWindow.focus();
    }

    this.add_obj = function(id) {
        obj = this.codes[id];
        var box = new pocoo.lib.effects.DialogBox();
        box.title = "Insert " + obj["name"];
        // XXX move this to json or somewhere else
        box.content = '<form><input type="hidden" name="id" value="'+id+'" /><fieldset><legend>Get image</legend><input type="radio" name="source" checked="checked" /> URL <input type="radio" name="source"> Attachment<input Type="radio" name="source"> Local file</fieldset><fieldset><legend>URL</legend>URL: <input name="src" type="text" /></fieldset><fieldset><legend>Size</legend>Width: <select><option>Normal</option><option>Pixels</option></select><br />Height: <select><option>Normal</option><option>Pixels</option></select></fieldset><input type="button" value="Abort" pocoo:handler="abort" /><input type="button" value="Insert" pocoo:handler="submit" /></form>';
        box.callbacks.push([this, "handle_obj"]);
        box.setDimension(500, 250);
        pocoo.lib.effects.DialogBox.show(box)
    }

    this.handle_obj = function(args) {
        var code = this.codes[args["id"]];
        var attrs = [];
        for (var z = 0; z < code["attrs"].length; z++) {
            var attr = code["attrs"][z];
            if (attr in args) {
                attrs.push([attr, args[attr]]);
            }
        }
        var obj = new Obj(code["name"], code["tag"], attrs);
        this.col++;
    }

    this.handle_key = function(key) {
        // Place for special functions
    }
}

function Key(evt) {
    this.alt = evt.altKey;
    this.shift = evt.shiftKey;
    this.ctrl = evt.ctrlKey;
}