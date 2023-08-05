# -*- coding: utf-8 -*-
"""
    pocoo.utils.tabbox
    ~~~~~~~~~~~~~~~~~~

    This file helps creating a TabBox.

    TabBox Implementation
    ===================

    Creating a new TabBox instance works like this::

        from pocoo.utils.tabbox import TabBox, Tab

        box = TabBox(request, call_function, is_inside_form,
            #tabs
        )

    ``call_function`` is executed to get the content for a tab.
    It's called with the following arguments:

        1: The id of the requested tab
        2 - n: Values of other text fields (see later)

    The ``call_function`` must return a string containing the HTML code for the
    tab content.

    If ``is_inside_form`` is set to ``True``, Pocoo uses <input>s instead of
    <a>s.  This has the advantage that the content of other text fields will
    still exist if a user without JS/AJAX has to reload the page for selecting a
    new tab.

    The final arguments are the tabs. The creation of a tab looks like this::

        Tab(tab_title, static [True], send [[]])

    ``tab_title`` is the name of the tab.

    ``static`` defines whether the tab content should be loaded only on request.
    If ``static`` is set to ``True``, the content of the tab is provided by the
    html source; else the content will be loaded later when the user selects the
    tab.

    ``send`` contains a list of other text fields whose contents are sent as
    additional arguments to the ``call_function`` (see above).

    Every `TabBox` instance has an attribute ``html`` containing the HTML source
    for the TabBox.

    A working example of a box would look like this::

        # inside the Python file

        from pocoo.utils.tabbox import TabBox, Tab
        import time

        def get_content(req, page):
            page = int(page)
            if page == 0:
                return "Good morning"
            elif page == 1:
                return "Good night"
            elif page == 2:
                return time.asctime()

        box = TabBox(req, get_content, False,
            Tab(_("7 pm")),
            Tab(_("11 am")),
            Tab(_("Clock"), static=False)
        )

        return TemplateResponse('test.html',
            box = box
        )

        # inside test.html

        {{ box.html }}

    :copyright: 2006 by Benjamin Wiegand.
    :license: GNU GPL, see LICENSE for more details.
"""

class TabBox(object):

    def __init__(self, req, func, is_form, *tabs):
        self.req = req
        self.func = func
        self.is_form = is_form
        self.selected = int(req.args.get('partial') or req.form.get('partial') or 0)
        self.tabs = tabs
        self.indexes = {}
        for tab in self.tabs:
            if tab.short_name:
                self.indexes[tab.short_name] = list(self.tabs).index(tab)

    @property
    def html(self):
        html = ['<ul class="tabs">']
        boxes = []

        for i, tab in enumerate(self.tabs):
            selected = self.selected == i
            html.append(tab.get_html(i, '%s.%s' % (self.func.__module__.split('.')[2],
                    self.func.rpc_name),
                self.is_form, selected))
            if tab.static or selected and not tab.lazy:
                args = [self.req.form.get(send) for send in tab.send]
                content = self.func(self.req, i, *args)

            boxes.append('<div class="tabbox%s" id="box_%s"%s>%s</div>' % \
                        (tab.lazy and ' indicator' or '', tab.short_name or i,
                        selected and ' style="display: block"' or "",
                        (tab.static or selected) and content or "")),

        boxes.append('<div class="tabbox" id="tabbox"></div>')

        return u"\n".join(html + ['</ul>', '<div>'] + boxes + ['</div>'])


class Tab(object):

    def __init__(self, name, short_name=None, static=True, send=[], lazy=False):
        self.name = name
        self.short_name = short_name
        self.static = static
        self.send = send
        self.lazy = lazy

    def get_html(self, index, method, is_form, selected):
        if self.static:
            onclick = "loadTab('box_%s', this.parentNode); return false;" % \
                (self.short_name or index)
        else:
            onclick = ("return ajax(AJS.partial(loadTab, 'box_%s', this.parentNode, "
                       "'%s', [%s], [%s]))" % (self.short_name or index, method,
                       index, ",".join(self.send)))

        if is_form:
            id = "tab%s" % index
            elem = ('<input type="submit" name="partial" value="%s" onclick="%s"'
                    'id="%s" /><label for="%s">%s</label>' % (index, onclick, id,
                                                              id, self.name))
        else:
            elem = '<a href="?partial=%s" onclick="%s">%s</a>' % (index, onclick,
                                                                  self.name)

        return '<li class="tab%s">%s</li>' % (selected and " active_tab" or "", elem)
