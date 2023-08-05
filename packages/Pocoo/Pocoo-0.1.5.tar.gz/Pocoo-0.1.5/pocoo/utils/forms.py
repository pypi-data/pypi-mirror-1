# -*- coding: utf-8 -*-
"""
    pocoo.utils.forms
    ~~~~~~~~~~~~~~~~~

    Pocoo form validation helpers.


    Form Validation
    ===============

    Validating forms sucks. To simplify it, Pocoo provides some classes
    for form validation.


    Application Side
    ----------------

    Here an example form used in `pocoo.pkg.core.forms`::

        from pocoo.utils import forms
        from pocoo.utils.validators import isEmail, isSameValue
        from pocoo.pkg.core.validators import isAvailableUsername, \
             isStrongPassword

        def get_password_error(form, field):
            _ = form.req.gettext
            return _('The two passwords don\'t match.')

        class RegisterForm(forms.Form):
            username = forms.TextField(isAvailableUsername())
            email = forms.TextField(isEmail())
            password = forms.PasswordField(isStrongPassword())
            password2 = forms.PasswordField(isSameValue('password',
                                            get_password_error))

    As you can see a form definition is just a normal class defintion.
    Callbacks can be defined in both the class and the module, the
    latter is recommended if you want to use the callback function
    in more than one form.

    Note that there are in fact two base forms. `Form` and
    `OrderedForm`. The latter knows about the order of the form fields
    defined in it. Use this if you want to iterate over form fields
    in templates.

    You can use it inside of the controller like this::

        form = RegisterForm(req, self, 'POST')
        # fill with defaults
        form.fill(defaults)
        # fill with request data
        if req.method == 'POST':
            form.update(req.form, prefix='f_')
            if not form.has_errors:
                # get form data and do something:
                d = form.to_dict()
                ...
        return TemplateResponse('name_of_template.html',
            form = form.generate(prefix='f_')
        )

    Templates
    ---------

    The form templates are very clean and easy since the form fields
    are able to create the html code of the form fields theirselves.
    Most request handlers put a variable named ``'form'`` into the
    template context which includes at least the following keys:

    ``action``
        the target url of the form

    ``method``
        the method (either ``'post'`` or ``'get'``)

    If the form is a `OrderedForm` there will be also a key called
    ``fields`` which is a list of form field items in the correct
    order so that you can iterate over them.

    The form fields itself are also part of that dict. For example,
    if your form field is called ``'foo'`` you can get access to it
    by using ``form.foo`` in the template.

    What keys a form field acutally has depends on the type of form
    field. For a detailed description have a look at the docstrings of
    the form fields below.

    At least the following keys will be present:

    ``name``
        the name of the form field

    ``id``
        the id of the form field

    ``html``
        generated html markup for the formfield

    ``errors``
        the rendered partial template ``'partial/form_errors.html``.
        (this template is rendered for each form field, the list
        of errors is in the variable ``errors``)

    ``js``
        javascript sourcecode for the ajax validator call (already
        part of the ``html`` value)

    All fields except the `PasswordField` also have a ``value``
    variable that includes the current value)

    Example Template::

        <dl>
          <dt>{% trans "Username" %}</dt>
          <dd>{{ form.username.html }}
              {{ form.username.errors }}</dd>
          <dt>{% trans "E-Mail" %}</dt>
          <dd>{{ form.email.html }}
              {{ form.email.errors }}</dd>
          <dt>{% trans "Password" %}</dt>
          <dd>{{ form.password.html }}
              {{ form.password.errors }}</dd>
          <dt>{% trans "Password again" %}</dt>
          <dd>{{ form.password2.html }}
              {{ form.password2.errors }}</dd>
        </dl>

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""

from weakref import WeakValueDictionary
from pocoo.template import render_template
from pocoo.utils.html import escape_html
from pocoo.utils.validators import ValidationError, isInChoiceList, \
     isNotMultiline, doMultiCheck


#XXX: docstrings for the `get_template_context` methods below
#XXX: ajax functions missing for the form fields


#: id of the last created form field
_last_field_id = 0
_last_form_id = 0

#: form map
_forms = WeakValueDictionary()


JAVASCRIPT_TEMPLATE = '''
<script type="text/javascript">
  /* do_something_with('%(client_id)s') */
</script>\
'''


def get_javascript(client_id, form_id, field_id):
    """Return the javascript validator call for a form field."""
    return JAVASCRIPT_TEMPLATE % locals()


def get_form(form_id):
    """Return the form for a given id or `ValueError` if not found."""
    try:
        return _forms[form_id]
    except KeyError:
        raise ValueError('Form %r not found' % form_id)


class FormFieldMeta(type):

    def __call__(*args, **kwargs):
        global _last_field_id
        formfield = type.__call__(*args, **kwargs)
        formfield._internal_id = _last_field_id
        formfield.server_id = '%x' % _last_field_id
        _last_field_id += 1
        return formfield


class FormField(object):
    """
    Base class for all form fields. It's not possible to generate
    a template context of this abstract form field, so it's required
    to override the `get_template_context` method.
    """
    __metaclass__ = FormFieldMeta
    bound = False

    def __init__(self, validator=None, manipulator=None):
        self.name = None
        if validator is None:
            validator = lambda x, y: None
        self.validator = validator
        if manipulator is None:
            manipulator = unicode
        self.manipulator = manipulator

    def bind(self, form):
        """Return a bound FormField."""
        assert not self.bound, 'tried to bind a bound form field'
        # create a temporary mixin class constructed
        # out of the special BoundFormField and the
        # original class
        cls = type('Bound' + self.__class__.__name__,
                   (BoundFormField, self.__class__), {})
        result = object.__new__(cls)
        result.__dict__.update(self.__dict__)
        result.form = form
        result.req = form.req
        result.ctx = form.ctx
        result.reset()
        return result

    def reset(self):
        """Reset the form field to defaults."""
        assert self.bound, 'access to unbound form field'
        self.value = u''
        self.errors = []

    def set_value(self, form, data):
        """Set the field value to the data requested"""
        assert self.bound, 'access to unbound form field'
        if data is None:
            self.value = u''
        else:
            self.value = unicode(data)

    def validate(self, form):
        """Validate the formfield"""
        assert self.bound, 'access to unbound form field'
        try:
            self.validator(self, form)
        except ValidationError, e:
            self.errors[:] = e.args
        else:
            self.errors[:] = ()

    def get_template_context(self, form, prefix):
        """Return the template context for this field."""
        assert self.bound, 'access to unbound form field'
        raise NotImplementedError()

    def get_value(self, form):
        """Return the converted value of this field."""
        assert self.bound, 'access to unbound form field'
        if self.errors:
            return self.manipulator()
        return self.manipulator(self.value)

    def get_raw_value(self, form):
        """Return the current form value as unicode object
        so that you can insert it into html code again."""
        if self.value is None:
            return u''
        return unicode(self.value)

    def render_errors(self):
        """Render the partial error template."""
        assert self.bound, 'access to unbound form field'
        return render_template(self.req, 'partial/form_error.html', {
            'errors':       self.errors
        })

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.name,
        )


class BoundFormField(FormField):
    """
    Special Class representing bound form fields. This class is
    created by the `bind` method of a `FormField`. You can't
    create instances of this class yourself.
    """
    __metaclass__ = type
    bound = True

    def __init__(self):
        raise TypeError('cannot create %r instances' %
                        self.__class__.__name__)

    def __repr__(self):
        return '<%s %s: %r>' % (
            self.__class__.__name__,
            self.name,
            self.value
        )


class FormMeta(type):

    def __new__(cls, name, bases, d):
        global _last_form_id
        form = type.__new__(cls, name, bases, d)
        form._internal_id = _last_form_id
        form.server_id = '%x' % _last_form_id
        form.fields = fields = []
        form.field_id_map = id_map = {}
        for key, value in d.iteritems():
            if isinstance(value, FormField):
                if value.name is not None:
                    raise TypeError('you can\'t use a form field '
                                    'twice')
                value.form_class = form
                value.name = key
                fields.append(value)
                id_map[value.server_id] = value
        _last_form_id += 1
        _forms[form.server_id] = form
        return form


class OrderedFormMeta(FormMeta):

    def __new__(cls, name, bases, d):
        form = FormMeta.__new__(cls, name, bases, d)
        form.fields.sort(key=lambda x: x._internal_id)
        return form


class Form(object):
    """
    Basic Form. Allows you to define a bunch of form fields
    as class variables. Each form field must be defined only
    for one form at the same time. It's not possible to pass
    form fields from one from definition to another one.
    """
    __metaclass__ = FormMeta

    def __init__(self, req, url, method, defaults=None):
        assert method in ('POST', 'GET'), 'method must be either POST or GET'
        self.req = req
        self.ctx = req.ctx
        self.method = method
        if hasattr(url, 'url'):
            self.url = url.url
        else:
            self.url = req.ctx.make_url(url)
        self.has_errors = False

        # bind all form fields to this new form istance
        self.field_map = {}
        fielditer, self.fields = iter(self.fields), []
        for field in fielditer:
            bound_field = field.bind(self)
            self.fields.append(bound_field)
            self.field_map[field.name] = bound_field

        if defaults:
            self.fill(defaults)

    def fill(self, d):
        """
        Fills the form with defaults. The `has_error` value
        is left ontouched. It's also possible to fill the
        form with defaults by using the `defaults` parameter
        of the constructor.
        """
        for field in self.fields:
            if field.name in d:
                field.set_value(self, d[field.name])

    def update(self, d, prefix=''):
        """
        This method updates the form values of each field
        and calls the validators afterwards.
        """
        for field in self.fields:
            key = prefix + field.name
            if key in d:
                field.set_value(self, d[key])
            # XXX: ugly hack to solve the problem that unchecked checkboxes
            #      aren't send with the form data
            elif isinstance(field, CheckBox):
                field.set_value(self, False)
        for field in self.fields:
            field.validate(self)
            if field.errors:
                self.has_errors = True

    def reset(self):
        """Reset the form"""
        for field in self.fields:
            field.reset()
        self.has_errors = False

    def to_dict(self):
        """
        Collect all values from the fields and apply the manipulators.
        The return value is a dictionary.
        """
        return dict((field.name, field.get_value(self)) for field in
                    self.fields)

    def generate(self, prefix=u''):
        """
        This method generates a dict which is meant to be passed to the
        template context. The keys of this dict are the names of the
        form fields. Additionally the keys ``'action'`` and ``'method'``
        (which held the url and the transport method) exists. If those
        collide with names of the form fields, the form field names
        are renamed so that they have a trailing underscore in the name.
        """
        result = {}
        for field in self.fields:
            name = field.name
            if name in ('action', 'method'):
                name += '_'
            result[name] = field.get_template_context(self, prefix)
        result['action'] = self.url
        result['method'] = self.method.lower()
        return result


class OrderedForm(Form):
    """
    Works pretty much like the normal form, except that the
    form fields are stored on the form in the order they
    appear in the sourcecode. To get the correct field order
    in the template use the ``form.fields`` variable which is
    an iterable of form fields.
    """
    __metaclass__ = OrderedFormMeta

    def generate(self, prefix=u''):
        """
        Works like the `generate` method of the normal `Form` class
        except that the fields are in the dict twice. A second time
        in the ordered list ``'fields'`` so that a template designer
        can iterate over the list.
        """
        result = {}
        fields = []
        for field in self.fields:
            name = field.name
            if name in ('action', 'method', 'fields'):
                name += '_'
            result[name] = f = field.get_template_context(self, prefix)
            fields.append(f)
        result['fields'] = fields
        result['action'] = self.url
        result['method'] = self.method.lower()
        return result

    def to_list(self):
        """
        Works like `to_dict` but it returns an ordered list of
        ``(name, value)`` tuples.
        """
        return [(field.name, field.get_value(self)) for field in self.fields]


class TextField(FormField):

    def __init__(self, validator=None, manipulator=None):
        if validator is None:
            validator = isNotMultiline()
        else:
            validator = doMultiCheck(isNotMultiline(), validator)
        super(TextField, self).__init__(validator, manipulator)

    def get_template_context(self, form, prefix):
        assert self.bound, 'access to unbound form field'
        name = prefix + self.name
        js = get_javascript(name, form.server_id, self.server_id)
        return {
            'name':         name,
            'id':           name,
            'server_id':    self.server_id,
            'value':        self.value,
            'errors':       self.render_errors(),
            'js':           js,
            'html':         u'<input name="%s" id="%s" value="%s" />%s' % (
                name,
                name,
                escape_html(self.get_raw_value(form)),
                js
            )
        }


class PasswordField(TextField):

    def get_template_context(self, form, prefix):
        assert self.bound, 'access to unbound form field'
        name = prefix + self.name
        js = get_javascript(name, form.server_id, self.server_id)
        return {
            'name':         prefix + self.name,
            'id':           name,
            'server_id':    self.server_id,
            'errors':       self.render_errors(),
            'js':           js,
            'html':         u'<input type="password" name="%s" '
                            u'id="%s" />%s' % (
                name,
                name,
                js
            )
        }


class HiddenField(FormField):

    def __init__(self, manipulator=None):
        FormField.__init__(self, None, manipulator)

    def validate(self, form):
        """Validate the formfield"""
        assert self.bound, 'access to unbound form field'
        try:
            self.manipulator(self.value)
        except ValueError, e:
            self.errors[:] = (u'Hacking Attempt',)

    def get_template_context(self, form, prefix):
        assert self.bound, 'access to unbound form field'
        name = prefix + self.name
        return {
            'name':         name,
            'value':        self.value,
            'html':         u'<input type="hidden" name="%s" '
                            u'value="%s" />' % (
                name,
                escape_html(self.get_raw_value(form))
            )
        }


class TextArea(FormField):

    def get_template_context(self, form, prefix):
        assert self.bound, 'access to unbound form field'
        name = prefix + self.name
        js = get_javascript(name, form.server_id, self.server_id)
        return {
            'name':         name,
            'id':           name,
            'server_id':    self.server_id,
            'value':        self.value,
            'errors':       self.render_errors(),
            'js':           js,
            'html':         u'<textarea name="%s" id="%s">'
                            u'%s</textarea>%s' % (
                name,
                name,
                escape_html(self.get_raw_value(form)),
                js
            )
        }


class FileField(FormField):

    def get_template_context(self, form, prefix):
        assert self.bound, 'access to unbound form field'
        name = prefix + self.name
        js = get_javascript(name, form.server_id, self.server_id)
        return {
            'name':         name,
            'id':           name,
            'server_id':    self.server_id,
            'errors':       self.render_errors(),
            'js':           js,
            'html':         u'<input type="file" name="%s" '
                            u'id="%s" />%s' % (
                name,
                name,
                js
            )
        }


class CheckBox(FormField):

    def __init__(self, validator=None, manipulator=None):
        def checkbox_manipulator(x):
            if isinstance(x, unicode):
                return True
            else:
                return False

        if manipulator is None:
            manipulator = checkbox_manipulator
        super(CheckBox, self).__init__(validator, manipulator)

    def get_value(self, form):
        assert self.bound, 'access to unbound form field'
        return self.manipulator(self.value)

    def get_template_context(self, form, prefix):
        assert self.bound, 'access to unbound form field'
        name = prefix + self.name
        js = get_javascript(name, form.server_id, self.server_id)
        return {
            'name':         name,
            'id':           name,
            'server_id':    self.server_id,
            'checked':      bool(self.value),
            'errors':       self.render_errors(),
            'js':           js,
            'html':         u'<input type="checkbox" value="on"'
                            u'name="%s" id="%s"%s />%s' % (
                name,
                name,
                bool(self.value) and ' checked="checked"' or '',
                js
            )
        }


class SelectBox(FormField):

    def __init__(self, choices_callback, validator=None, manipulator=None):
        self.choices_callback = choices_callback
        super(SelectBox, self).__init__(validator, manipulator)

    def validate(self, form):
        assert self.bound, 'access to unbound form field'
        choices = self.choices_callback(self, form)
        if isinstance(choices, dict):
            choices = choices.keys()
        else:
            choices = [x[0] for x in choices]
        validator = doMultiCheck(isInChoiceList(choices),
                                 self.validator)
        try:
            validator(self, form)
        except ValidationError, e:
            self.errors[:] = e.args
        else:
            self.errors[:] = ()

    def get_template_context(self, form, prefix):
        assert self.bound, 'access to unbound form field'
        choices = self.choices_callback(self, form)
        if isinstance(choices, dict):
            choices = choices.items()
            choices.sort(key=lambda x: x[1].lower())
        values = []
        name = prefix + self.name
        js = get_javascript(name, form.server_id, self.server_id)
        for value, caption in choices:
            values.append({
                'value':        value,
                'caption':      caption,
                'selected':     value == self.value
            })
        return {
            'name':         name,
            'id':           name,
            'server_id':    self.server_id,
            'values':       values,
            'errors':       self.render_errors(),
            'js':           js,
            'html':         u'<select name="%s" id="%s">%s</select>%s' % (
                name,
                name,
                u'\n'.join(
                    u'<option value="%s"%s>%s</option>' % (
                        escape_html(item['value']),
                        item['selected'] and ' selected="selected"' or '',
                        escape_html(item['caption'])
                    ) for item in values
                ),
                js
            )
        }
