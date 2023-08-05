/**
 * Basic Editor
 * ~~~~~~~~~~~~
 *
 * The default editor just adds support for tabulators to the
 * textarea and doesn't create any toolbars.
 *
 * :copyright: 2006 by Armin Ronacher.
 * :license: GNU GPL, see LICENSE for more details.
 */

editor = {};

editor.init = function(textarea_id, toolbar_id, options) {
    var textarea = document.getElementById(textarea_id);
    var onKeyDown = function(e) {
        var e = (e) ? e : window.event;
        if (((e.keyCode) ? e.keyCode : e.which) == 9) {
            // For Internet Explorer
            if (document.selection && !textarea.selectionStart &&
                textarea.selectionStart != 0) {
                var range = document.selection.createRange();
                range.text = '\t';
                range.select();
            }
            // Mozilla Browsers
            else if (textarea.selectionStart || textarea.selectionStart == 0) {
                var startVal = textarea.value.substring(0, textarea.selectionStart);
                var endVal = textarea.value.substring(textarea.selectionStart);
                textarea.value = startVal + '\t' + endVal;
                textarea.selectionStart = startVal.length + 1;
                textarea.selectionEnd = startVal.length + 1;
                textarea.focus();
            }
            // others won't work, continue with default behaviour
            else {
                return true;
            }
            return false;
        }
        return true;
    }
    textarea.onkeydown = onKeyDown;
    textarea.onkeypress = onKeyDown;
}
