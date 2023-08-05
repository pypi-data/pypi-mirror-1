# -*- coding: utf-8 -*-
"""
    pocoo.utils.form
    ~~~~~~~~~~~~~~~~

    Pocoo form validation helpers.


    Form Validation
    ===============

    Validating forms sucks. To simplify it, Pocoo provides some classes
    for form validation.


    Application Side
    ----------------

    Real-world usage example::

        from pocoo.application import RequestHandler
        from pocoo.template import TemplateResponse
        from pocoo.utils.form import Form, TextField, TextArea
        from pocoo.utils import validators as V

        class NewThread(RequestHandler):

            def get_handler_regexes(self):
                yield r'forum/(?P<id>\d+)/new$'

            def handle_request(self, req, forum_id):
                form = Form(req, 'forum/%d/new' % forum.forum_id, 'POST',
                    TextField('title', validator=V.checkTextLength(3, 60)),
                    TextArea('text', validator=V.checkTextLength(4, 3000))
                )
                if 'sent' in req.form:
                    form.update(req.form, prefix='f_')
                    if not form.has_errors:
                        d = form.to_dict()
                        # do something with the form data dict "d"
                return TemplateResponse('posting',
                    forum=forum,
                    form=form.generate(prefix='f_')
                )

    **Note:** Validators are either classes or functions. In the module
    definition, they must have a pep8 conform name, but get a ``smallCaps``
    name after having been assigned to the ``Form`` class.

    Manipulators
    ------------

    The data returned from ``form.to_dict()`` normally is just a string.
    But if the form contains no errors the manipulators are called. A
    manipulator is a callable that returns something. You can use the builtin
    python types ``str``, ``int``, ``unicode``, ``float`` or ``bool``::

        form = Form(req, 'test', 'POST',
           TextField('a_number', validator=v.isInteger(), manipulator=int)
        )
        form.update(req.form)
        if not form.has_errors:
            d = form.to_dict()
            n = d['a_number']
            print '%d + 4 = %d' % (n, n + 4)
        else:
            print 'wrong data'

    Template Usage
    --------------

    ::

        <form action="{{ form.action }}" method="{{ form.method }}">
          {% if form.errors %}
          <div class="error">
            {% trans "There are some errors in your form" %}
          </div>
          {% endif %}

          <input type="text" name="{{ form.title.name }}"
                 value="{{ form.title.value|e }}" />
          {% if form.title.errors %}
          <ul class="error">
            {% for error in form.title.errors %}
            <li>{{ error|e }}</li>
            {% endfor %}
          </ul>
          {% endif %}

          <textarea name="{{ form.text.name }}">{{ form.text.value|e }}</textarea>
          {% if form.text.errors %}
          <ul class="error">
            {% for error in form.text.errors %}
            <li>{{ error|e }}</li>
            {% endfor %}
          </ul>
          {% endif %}
        </form>

    Each `FormField` returns a different template context. `TextField` and
    `TextArea` provide ``name`` and ``value``. `SelectBox` provides ``name``,
    ``values`` where ``values`` is a list of dicts in the form
    ``{'active': bool, 'value': str, 'caption': str}``::

        <select name="{{ form.timezone }}">
        {% for item in form.timezone.values %}
          <option value="{{ item.value|e }}"
              {% if item.active %} selected="selected"{% endif %}>
            {{ item.caption|e }}</option>
        {% endfor %}
        </select>

    A `CheckBox` works like a `TextField` or `TextArea` but also provides
    a checked key in the context.

    Validators
    ----------

    Core validators are defined in `pocoo.utils.validators` and
    `pocoo.pkg.core.validators`.


    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""

from pocoo.utils.validators import ValidationError, isInChoiceList, \
     isNotMultiline, doMultiCheck


class Form(object):

    def __init__(self, req, url, method, *fields):
        assert method in ('POST', 'GET'), 'method must be either POST or GET'
        self.req = req
        self.method = method
        if hasattr(url, 'url'):
            self.url = url.url
        else:
            self.url = req.ctx.make_url(url)
        self.fields = {}
        for field in fields:
            self.fields[field.name] = field
        self.has_errors = False

    def __getitem__(self, key):
        return self.fields[key]

    def update(self, d, prefix=''):
        for name, field in self.fields.iteritems():
            key = prefix + name
            if key in d:
                field.set_value(self, d[key])
            # quite ugly hack to solve the problem that unchecked checkboxes
            # aren't send with the form data
            elif isinstance(field, CheckBox):
                field.set_value(self, False)
        for field in self.fields.itervalues():
            field.validate(self)
            if field.errors:
                self.has_errors = True

    def reset(self):
        self.has_errors = False

    def to_dict(self):
        return dict((name, field.get_value(self)) for name, field in
                    self.fields.iteritems())

    def generate(self, prefix=u''):
        result = {}
        for name, field in self.fields.iteritems():
            if name in ('action', 'method'):
                name += '_'
            result[name] = field.get_template_context(self, prefix)
        result['action'] = self.url
        result['method'] = self.method.lower()
        return result



class FormField(object):

    def __init__(self, name, default=u'', validator=None, manipulator=None):
        self.name = name
        self.value = default
        if validator is None:
            validator = lambda x, y: None
        self.validator = validator
        if manipulator is None:
            manipulator = unicode
        self.manipulator = manipulator
        self.errors = []

    def set_value(self, form, data):
        self.value = data

    def validate(self, form):
        try:
            self.validator(self, form)
        except ValidationError, e:
            self.errors[:] = e.args
        else:
            self.errors[:] = ()

    def get_template_context(self, form, prefix):
        raise NotImplementedError()

    def get_value(self, form):
        if self.errors:
            return self.manipulator()
        return self.manipulator(self.value)

    def __repr__(self):
        return '<%s %s: %r>' % (
            self.__class__.__name__,
            self.name,
            self.value
        )


class TextField(FormField):

    def __init__(self, name, default=u'', validator=None, manipulator=None):
        if validator is None:
            validator = isNotMultiline()
        else:
            validator = doMultiCheck(isNotMultiline(), validator)
        super(TextField, self).__init__(name, default, validator,
                                        manipulator)

    def get_template_context(self, form, prefix):
        return {
            'name':     prefix + self.name,
            'value':    self.value,
            'errors':   self.errors
        }


class TextArea(FormField):

    def get_template_context(self, form, prefix):
        return {
            'name':     prefix + self.name,
            'value':    self.value,
            'errors':   self.errors
        }


class FileField(FormField):

    def get_template_context(self, form, prefix):
        return {
            'name':     prefix + self.name,
            'errors':   self.errors
        }


class CheckBox(FormField):

    def __init__(self, name, default=False, validator=None, manipulator=None):
        def checkbox_manipulator(x):
            if isinstance(x, unicode):
                return True
            else:
                return False

        if manipulator is None:
            manipulator = checkbox_manipulator
        super(CheckBox, self).__init__(name, default, validator, manipulator)

    def get_value(self, form):
        return self.manipulator(self.value)

    def get_template_context(self, form, prefix):
        return {
            'name':         prefix + self.name,
            'checked':      bool(self.value),
            'value':        self.value
        }


class SelectBox(FormField):

    def __init__(self, name, choices, default=u'', validator=None,
                 manipulator=None):
        if isinstance(choices, dict):
            self.choices = sorted(choices.items())
        else:
            self.choices = choices
        choices = [item for item, _ in self.choices]
        if validator is None:
            validator = isInChoiceList(choices)
        else:
            validator = doMultiCheck(isInChoiceList(choices),
                                     validator)
        super(SelectBox, self).__init__(name, default, validator,
                                        manipulator)

    def get_template_context(self, form, prefix):
        values = []
        for item in self.choices:
            if isinstance(item, (tuple, list)):
                values.append({
                    'value':        item[0],
                    'caption':      item[1],
                    'selected':     item[0] == self.value
                })
            else:
                values.append({
                    'value':        item,
                    'caption':      item,
                    'selected':     item == self.value
                })
        return {
            'name':     prefix + self.name,
            'values':   values,
            'errors':   self.errors
        }
