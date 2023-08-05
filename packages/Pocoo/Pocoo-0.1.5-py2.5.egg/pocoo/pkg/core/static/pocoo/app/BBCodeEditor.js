/**
 * Basic Editor
 * ~~~~~~~~~~~~
 *
 * The BBCode editor adds support for all BBCodes
 *
 * :copyright: 2006 by Benjamin Wiegand.
 * :license: GNU GPL, see LICENSE for more details.
 */

var editors = {};

Editor = function() {
    for (var z = 0; z < arguments.length; z++) {
        var arg = arguments[z];
        var val = arg[1];
        eval('this.' + arg[0] + ' = val');
    }
};

function initEditor(textarea, toolbar, preview, prev_text, options) {
    var editor = new Editor(
        ['textarea', AJS.$(textarea)], ['toolbar', AJS.$(toolbar)], ['smileybar', AJS.DIV({id: 'smileybar'})], ['buttonbar', AJS.DIV({id: 'buttonbar'})], ['selectbar', AJS.DIV({id: 'selectbar'})], ['accesskeys', []], ['formats', options['buttons']], ['buttoninfo', AJS.DIV()], ['smilies', options['smilies']], ['preview', AJS.$(preview)], ['prev_text', AJS.$(prev_text)]
    );
    editor.buttoninfo.className = "buttoninfo";
    editor.toolbar.appendChild(editor.buttoninfo);
    editor.toolbar.appendChild(editor.smileybar);
    editor.toolbar.appendChild(editor.buttonbar);
    editor.toolbar.appendChild(editor.selectbar);

    editors[textarea] = editor;

    for (var z = 0; z < editor.formats.length; z++) {
        var format = editor.formats[z];

        if (format["values"] == null) { // if button
            var a = AJS.A();
            var key = _find_accesskey(a, format["name"], editor);
            var alt = format["description"] + ((key) ? " (Alt + " + key + ")" : "");
            var img = AJS.IMG({alt: alt, title: alt, src: format["icon"]});
            img.textarea = a.textarea = textarea;
            a.number = z;
            img.onmouseover = function() {
                var editor = editors[this.textarea];
                editor.buttoninfo.innerHTML = this.alt;
            };
            img.onmouseout = function() {
                var editor = editors[this.textarea];
                editor.buttoninfo.innerHTML = "";
            };
            a.onclick = function() {
                _do_format(editors[this.textarea], this.number);
            };
            a.appendChild(img);
            editor.buttonbar.appendChild(a);
        } else { // if select
            var select = AJS.SELECT();
            var title = AJS.OPTION();
            title.innerHTML = format["name"];
            select.appendChild(title);
            select.textarea = textarea;
            select.number = z;

            for (var y = 0; y < format["values"].length; y++) {
                var option = AJS.OPTION();
                option.innerHTML = format["labels"][y];
                option.value = format["values"][y];
                select.appendChild(option);
            }

            select.onchange = function() {
                _do_format(editors[this.textarea], this.number, this.value);
                this.selectedIndex = 0;
            };
            editor.selectbar.appendChild(select);
        }
    }
    for (var y = 0; y < editor.smilies.length; y++) {
        /* smiley: (text, img, dir) */
        var smiley = editor.smilies[y];
        var alt = smiley[0];
        var img = AJS.IMG({src: smiley[2] + smiley[1], alt: alt, title: alt});
        img.textarea = textarea;
        img.code = smiley[0];
        img.onmouseover = function() {
            editors[this.textarea].buttoninfo.innerHTML = this.alt;
        };
        img.onmouseout = function() {
            editors[this.textarea].buttoninfo.innerHTML = "";
        };
        img.onclick = function() {
            _insert_smiley(editors[this.textarea], this.code);
        };
        editor.smileybar.appendChild(img);
    }
}

_do_format = function(editor, id, attr) {
    var area = editor.textarea;
    var format = editor.formats[id];
    var insert = format["insert"];
    if (typeof(attr) != "undefined") { // if an additional attribute is given
        if (attr == format["name"]) {
            return false;
        }
        insert = insert.replace("{attr}", attr);
    }
    insert = insert.split("{text}");

    if (typeof(area.selectionStart) != "undefined" && typeof(area.selectionEnd) != "undefined") { // for good browsers
        var start = area.selectionStart;
        var end = area.selectionEnd;
        var first = area.value.substring(0, start);
        var middle = area.value.substring(start, end);
        var last = area.value.substring(end, area.value.length);
        if (end != start) { // if something is marked
            middle = insert[0] + middle + insert[1];
            new_start = start + insert[0].length;
            new_end = end + insert[0].length;
        } else { // if nothing is marked
            middle = insert[0] + format["name"] + insert[1];
            new_start = start + insert[0].length;
            new_end = new_start + format["name"].length;
        }
        area.value = first + middle + last;
        area.focus();
        area.selectionStart = new_start;
        area.selectionEnd = new_end;

    } else if (typeof(document.selection) != "undefined") { // for IE...
        area.focus();
        var s = document.selection;
        var rng = s.createRange();
        var text = rng.text;
        if (text.length > 0) {
            rng.text = format[0] + text + format[1];
        } else {
            rng.text = format[0] + format[2] + format[1]
        }
    }
}

function _insert_smiley(editor, smiley) {
    var smiley = ' ' + smiley + ' ';
    var area = editor.textarea;
    if (typeof(area.selectionStart) != "undefined" && typeof(area.selectionEnd) != "undefined") { // for good browsers
        var start = area.selectionStart;
        var end = area.selectionEnd;
        var first = area.value.substring(0, start);
        var middle = area.value.substring(start, end);
        var last = area.value.substring(end, area.value.length);
        middle = smiley;
        var new_start = start + smiley.length;
        area.value = first + middle + last;
        area.focus();
        area.selectionStart = new_start;
        area.selectionEnd = new_start;
    } else if (typeof(document.selection) != "undefined") { // for IE...
        area.focus();
        var s = document.selection;
        var rng = s.createRange();
        var text = rng.text;
        rng.text = smiley;
    }
}

function _find_accesskey(elem, str, editor) {
    for (var x = 0; x < str.length; x++) {
        char = str[x].toLowerCase();
        if (char != " ") {
            if (!AJS.isIn(char, editor.accesskeys)) {
                editor.accesskeys.push(char);
                elem.accessKey = char;
                return char;
            }
        }
    }
    return false;
}

function preview(area) {
    var editor = editors[area];
    text = editor.textarea.value;
    var rpc = new pocoo.lib.async.RPC('!jsonrpc');
    var method = rpc.getMethod('core.newpost.preview');
    method([text], {}, function (result) {
        editor.prev_text.innerHTML = result;
        AJS.showElement(editor.preview);
    });
}