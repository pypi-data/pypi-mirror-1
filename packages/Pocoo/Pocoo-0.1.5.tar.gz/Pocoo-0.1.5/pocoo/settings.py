# -*- coding: utf-8 -*-
r"""
    pocoo.settings
    ~~~~~~~~~~~~~~

    A custom config file format and a class to represent a config file.


    The config file format
    ======================

    Configs consist of

    * includes
    * sections, which can contain subsections and values
    * values, which can be simple values or complex values (lists, dicts,
      multiline strings).

    An example config file::

        # -*- coding: utf-8 -*-
        # This is a unix style comment
        ; this is an ini style comment

        include "../other.conf"

        section general:
            key = value
            bool_key = true
            other_key = "value with whitespaces and\tspecial chars\n"

            list_entry = list:
                a
                list
                "of\n"
                items

            multiline_string = string:
                some lines of text, indented on the same level.
                All indentation will be stripped from the text while
                parsing. You can include leading or trailing whitespace
                "      using quotes. "

            # a comment
            section subsect:
                key = value

                dict_entry = dict:
                    key = value
                    anotherkey = anothervalue

    * As you can see, whitespace is significant as in Python. A tab is worth 8 spaces.
    * Comments always use their own line and can be indented as you like.
    * You can use quotes around values. The strings will then be parsed like Python
      strings, using the same escape rules.
    * All keys and simple values are strings. You can convert them to integers or
      booleans using the config object.
    * It's possible to define the encoding using a python coding declaration (PEP 263).
    * You can include other config files. This is helpful if you want to have a common
      config for several boards, but want to customize little details.

    Structure
    ---------

    The above config results in the following internal structure::

        {'general':
            {'key': 'value',
             'other_key': 'value with whitespaces and\tspecial chars\n',
             'list_entry': ['a', 'list', 'of\n', 'items'], 'bool_key': 'true',
             'multiline_string': 'some lines of text, indented on the same level.\nAll'
                                 'indentation will be stripped from the text while\n'
                                 'parsing. You can include leading or trailing'
                                 'whitespace\n      using quotes. ',

             'subsect':
                {'key': 'value',
                 'dict_entry': {'key': 'value', 'anotherkey': 'anothervalue'},
                }
            }
        }

    All strings are actually Unicode strings, having been decoded from the byte
    strings using the encoding specified in the file, defaulting to ascii.


    Example Queries
    ---------------

    You can query the object using these commands:

    >>> from pocoo.settings import Configuration
    >>> config = Configuration("/some/config/file")
    >>> config.get('general', 'list_entry')
    ['a', 'list', 'of\n', 'items']
    >>> config.get('general', 'key')
    'value'
    >>> config.get_bool('general', 'bool_key')
    True
    >>> config.get('nonexisting.section', 'key', 'foobar')
    'foobar'


    Updating the Configuration
    --------------------------

    You can also update the configuration:

    >>> config.set('my_section', 'mykey', 'myvalue')
    >>> config.get('my_section', 'mykey')
    'myvalue'
    >>> config.save()


    :copyright: 2006 by Georg Brandl, Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import sys, os, new, re
import cPickle as pickle
from UserString import MutableString
from itertools import chain

from pocoo.exceptions import InvalidConfigFile, MissingConfigValue
from pocoo.utils.debug import dtk

coding_re = re.compile(r'coding[:=]\s*([-\w.]+)')

missing = object()


def load_config(iterable, filename, root, initial_state='root'):
    """
    Load and parse a configuration file from ``iterable``.
    ``filename`` is used for error messages and for handling
    relative include paths.

    ``root`` is the dictionary into which the values are stored.
    ``initial_state`` is the initial state (can be "root" or "section").
    In initial state "root" there can only be sections and includes
    (this is used for pocoo.conf), in state "section" there can be
    sections and values, but no includes (used for package.conf).

    Raise InvalidConfigFile for syntax errors.
    """
    encoding = 'ascii'

    def parse_value(val):
        val = val.strip()
        if len(val) > 1 and val[0] == val[-1] and val[0] in '"\'':
            val = val[1:-1].decode('string-escape')
        return val.decode(encoding)

    def parse_key(key):
        return key.strip().decode(encoding)

    section = root
    raw = []

    indentlevels = [0]
    states = [initial_state]
    new_state = ""
    opts = thingtofill = None
    for lno, rline in enumerate(chain(iterable, [''])):
        rline = rline.rstrip().expandtabs()
        line  = rline.lstrip()
        indent = len(rline) - len(line)

        # comment
        if not line or line[0] in '#;':
            if lno < 2:
                m = coding_re.search(line)
                if m is not None:
                    encoding = m.group(1)
            raw.append((len(indentlevels), 'comment', line))
            continue

        if indent > indentlevels[-1]:
            if not new_state:
                raise InvalidConfigFile(filename, lno+1,
                                        "Unexpected indent")
            states.append(new_state)
            indentlevels.append(indent)
            new_state = ""
        elif indent < indentlevels[-1]:
            for ilevel in indentlevels:
                if indent == ilevel:
                    while indentlevels[-1] != ilevel:
                        if states[-1] == "section":
                            section = section['__parent__']
                            raw.append((len(indentlevels), 'endsection', ''))
                        del indentlevels[-1]
                        del states[-1]
                    break
            else:
                raise InvalidConfigFile(filename, lno+1, "Invalid dedent level")
        elif new_state:
            # TODO: until the "empty dict" problem is solved, this
            #       must be allowed
            #raise InvalidConfigFile(filename, lno+1, "Missing indent")
            if new_state == "section":
                section = section['__parent__']
                raw.append((len(indentlevels), 'endsection', ''))
            new_state = ""

        curstate = states[-1]
        if curstate == "root":
            if line.startswith("section ") and line.endswith(":"):
                sname = parse_key(line[7:-1])
                if not sname:
                    raise InvalidConfigFile(filename, lno+1,
                                            "Section name is empty")
                new_state = "section"
                new_sect = {'__parent__': section}
                section = section.setdefault(sname, new_sect)
                raw.append((len(indentlevels), 'section', sname))
            elif line.startswith("include "):
                iname = parse_value(line[7:])
                try:
                    if os.path.isfile(filename):
                        # we got a real filename
                        iname = os.path.join(os.path.dirname(filename), iname)
                    load_config(file(iname), iname, root)
                except IOError:
                    raise InvalidConfigFile(filename, lno+1,
                                            "Included file not found")
                root.setdefault('__includes__', []).append(iname)
                raw.append((len(indentlevels), 'include', iname))
            else:
                raise InvalidConfigFile(filename, lno+1,
                        "Only include and section allowed on top level")

        elif curstate == "section":
            if line.startswith("section ") and line.endswith(":"):
                sname = parse_key(line[7:-1])
                if not sname:
                    raise InvalidConfigFile(filename, lno+1,
                                            "Section name is empty")
                new_state = "section"
                new_sect = {'__parent__': section}
                section = section.setdefault(sname, new_sect)
                raw.append((len(indentlevels), 'section', sname))
                continue

            splitted = line.split("=", 1)
            name = parse_key(splitted[0])
            if not name:
                raise InvalidConfigFile(filename, lno+1, "Value without a name")
            if len(splitted) == 1:
                raise InvalidConfigFile(filename, lno+1,
                                        "Bare values only allowed in a list or string")
            else:
                value = splitted[1].lstrip()
            # complex data type
            if value.endswith(":"):
                if value.startswith("list"):
                    new_state = "list"
                    thingtofill = []
                elif value.startswith("dict"):
                    new_state = "dict"
                    thingtofill = {}
                elif value.startswith("string"):
                    new_state = "string"
                    thingtofill = MutableString()
                else:
                    raise InvalidConfigFile(filename, lno+1,
                                            "Invalid value type")
                opts = value[len(new_state):-1].strip()
                if opts and (opts[0] != "[" or opts[-1] != "]"):
                    raise InvalidConfigFile(filename, lno+1,
                                        "Options must be enclosed in [brackets]")
                opts = opts[1:-1].lower().split(",")
                if "extend" in opts:
                    # extend thing
                    if name in section:
                        thingtofill = section[name]
                    else:
                        section[name] = thingtofill
                else:
                    # replace thing
                    section[name] = thingtofill
                raw.append((len(indentlevels), new_state, name))
                continue
            else:
                val = parse_value(value)
                section[name] = val
                raw.append((len(indentlevels), 'value', name))

        elif curstate == "list":
            # pylint: disable-msg=E1101
            thingtofill.append(parse_value(line))

        elif curstate == "dict":
            splitted = line.split("=", 1)
            if len(splitted) == 1:
                raise InvalidConfigFile(filename, lno+1,
                                    "Invalid dict entry (must be separated by =)")
            thingtofill[parse_value(splitted[0])] = parse_value(splitted[1])

        elif curstate == "string":
            thingtofill += parse_value(line) + "\n"

        else:
            raise InvalidConfigFile(filename, lno+1,
                "You'll shoot me for this error message, but something went wrong")

    return (encoding, raw)


class Configuration(object):

    def __init__(self, root, filename='pocoo.conf'):
        self.root = os.path.realpath(root)
        self.filename = os.path.join(self.root, filename)

        self._data = {'__parent__': None, '__includes__': []}
        self._raw = []
        self._new_keys = {}
        self.encoding = 'ascii'
        self.last_change = 0
        self.installed = False

        self.load()


    def load(self):
        """
        Load and parse the configuration file.
        Raise `InvalidConfigFile` for syntax errors.
        """
        getmtime = os.path.getmtime
        cached = os.path.join(self.root, 'cache', os.path.basename(self.filename))

        # try to load the pickled version
        try:
            mtime = getmtime(cached)
            if mtime < getmtime(self.filename):
                raise IOError
            pfile = file(cached)
            self._data, self._raw = pickle.load(pfile)
            pfile.close()
            for ifile in self._data['__includes__']:
                if mtime < getmtime(ifile):
                    raise IOError
            dtk.log("config", "successfully loaded cached config " + cached)
            self.installed = True
            self.last_change = getmtime(self.filename)
            return
        except Exception:
            dtk.log("config", "cached version not current or original not found")
            if os.path.isfile(cached):
                os.unlink(cached)

        try:
            self.encoding, self._raw = load_config(file(self.filename),
                                                   self.filename, self._data)
        except IOError:
            dtk.log("config", "could not find " + self.filename)
            self.last_change = -1
            return
        dtk.log("config", "successfully loaded config " + self.filename)
        self.installed = True
        self.last_change = getmtime(self.filename)

        # try to write a pickled version to disk
        try:
            pfile = file(cached, 'w')
            pickle.dump((self._data, self._raw), pfile, pickle.HIGHEST_PROTOCOL)
            pfile.close()
        except Exception:
            pass

    def __getitem__(self, item):
        try:
            return self.get(*item.rsplit('.', 1))
        except (IndexError, ValueError, MissingConfigValue):
            raise KeyError(repr(item))

    def __repr__(self):
        return '<%s in %r>' % (
            self.__class__.__name__,
            self.root
        )

    def get(self, section, key, default=missing):
        """
        Get the value associated with ``section.key``.
        If the key is not set, return ``default`` if given, else
        raise MissingConfigValue.
        """
        node = self._data
        try:
            for bit in section.split('.'):
                node = node[bit]
            return node[key]
        except KeyError:
            if default is not missing:
                return default
            else:
                raise MissingConfigValue('mandatory value %s.%s not set' %
                                         (section, key))

    def get_bool(self, section, key, default=missing):
        """
        Get the value, and convert to boolean.
        """
        # pylint: disable-msg=E1101
        rv = self.get(section, key, default)
        if isinstance(rv, basestring):
            return rv.lower() in ('1', 'yes', 'on', 'true')
        else:
            return bool(rv)

    def get_int(self, section, key, default=missing):
        """
        Get the value, and convert to integer.
        """
        rv = self.get(section, key, default)
        try:
            return int(rv)
        except ValueError:
            raise MissingConfigValue('config value %s.%s should be '
                                     'an integer but cannot be converted '
                                     'to one' % (section, key))

    def get_float(self, section, key, default=missing):
        """
        Get the value, and convert to float.
        """
        rv = self.get(section, key, default)
        try:
            return float(rv)
        except ValueError:
            raise MissingConfigValue('config value %s.%s should be '
                                     'a float but cannot be converted '
                                     'to one' % (section, key))

    def get_list(self, section, key, default=missing):
        """
        Get the value, and convert to list.
        """
        rv = self.get(section, key, default)
        if not isinstance(rv, list):
            raise MissingConfigValue('config value %s.%s should be '
                                     'a list' % (section, key))
        return rv

    def get_dict(self, section, key, default=missing):
        """
        Get the value, and convert to list.
        """
        rv = self.get(section, key, default)
        if not isinstance(rv, dict):
            raise MissingConfigValue('config value %s.%s should be '
                                     'a dict' % (section, key))
        return rv

    def set(self, section, key, value):
        """
        Set ``section.key`` to ``value``.
        """
        # convert to string for ini representation
        if isinstance(value, bool):
            value = value and 'true' or 'false'

        node = self._data
        for bit in section.split('.'):
            if bit not in node:
                node[bit] = {'__parent__': node}
            node = node[bit]

        # FIXME: There are quite a few problems here, especially new
        #        sections are not written to the config file.

        if key not in node:
            # for raw writing
            self._new_keys.setdefault(section, []).append(key)
        node[key] = value

    def delete(self, section, key):
        """
        Delete ``section.key``.
        """
        node = self._data
        for bit in section.split('.'):
            if bit not in node:
                return
            node = node[bit]
        if key in node:
            del node[key]

    def to_dict(self):
        return self._data

    def to_string(self):
        """
        Return the formatted config file as a string.
        """
        from cStringIO import StringIO
        out = StringIO()
        self.save(out)
        return out.getvalue().rstrip()

    def save(self, output=None):
        """
        Save the formatted config file to the stream ``output``,
        if given, else to ``self.filename``.
        """
        close = False
        if output is None:
            output = file(self.filename, 'w')
            close = True

        def encode_val(val):
            if val.lower() in [u'true', u'yes', u'on', u'1', u'0',
                               u'off', u'false']:
                val = val.lower()
            else:
                val = "'%s'" % val.encode(self.encoding).encode('string-escape')
            return val

        def write_value(indent, name, val):
            output.write(indent + name.encode(self.encoding) + ' = ' +
                         encode_val(val) + '\n')

        def write_list(indent, name, val):
            output.write(indent + name.encode(self.encoding) + ' = list:\n')
            indent += "    "
            for item in val:
                output.write(indent + encode_val(item) + '\n')

        def write_dict(indent, name, val):
            output.write(indent + name.encode(self.encoding) + ' = dict:\n')
            indent += "    "
            for k, v in val.items():
                output.write(indent + k.encode(self.encoding) + ' = ' +
                             encode_val(v) + '\n')

        write = dict(value=write_value, list=write_list, dict=write_dict)

        sects = []
        sname = ''
        for level, typ, name in self._raw:
            indent = (level-1)*"    "
            if typ == 'comment':
                output.write(len(sects)*"    " + name + '\n')
            elif typ == 'section':
                output.write(indent + 'section ' + name.encode(self.encoding) + ':\n')
                sects.append(name)
                sname = '.'.join(sects)
            elif typ == 'endsection':
                # write new values
                for key in self._new_keys.get(sname, ()):
                    val = self.get(sname, key, missing)
                    if val is missing: continue
                    typ = {list: 'list', dict: 'dict'}.get(type(val), 'value')
                    write[typ](indent, key, val)

                del sects[-1]
                sname = '.'.join(sects)
            elif typ == 'include':
                output.write(indent + 'include ' + name.encode(self.encoding) + '\n')
            else:
                val = self.get(sname, name, missing)
                # deleted?
                if val is missing: continue
                write[typ](indent, name, val)
        if close:
            self.last_change = os.path.getmtime(self.filename)
            output.close()


class ConfigValue(object):
    """
    This class ensures that components can cache configuration values
    but receive always the up-to-date version of the configuration entry.

    The configuration object itself holds a value representing the time
    of the last update. Every ConfigValue object also holds a timestamp
    with the time of its own value.

    When the timestamp of the configuration is newer than the timestamp
    of the ConfigValue object it calls get() to fetch the new version from
    the config.

    You can also inherit from this class to allow more complex caching.
    See `pocoo.pkg.core.auth`.`AuthSettings` for an example.

    Usage::

        from pocoo.settings import cfg

        class MyComponent(...):
            key = cfg.int('section', 'key', 42)
            other_key = cfg.str('section', 'other_key', 'default')

            def do_something(self):
                return '%d :: %s' % (self.key, self.other_key)

    You can access those attributes like any other property since they
    use the Python descriptor protocol.
    """

    def __init__(self, section, key, default=missing):
        self.section = section
        self.key = key
        self.default = default
        self._cached = missing
        self._last_change = 0

    def get(self, ctx, section, key, default):
        raise NotImplementedError

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self._cached is missing or self._last_change < obj.ctx.cfg.last_change:
            self._cached = self.get(obj.ctx, self.section, self.key, self.default)
        return self._cached

    def __repr__(self):
        return '<%s: %r>' % (
            self.__class__.__name__,
            '%s.%s' % (self.section, self.key)
        )


class StringValue(ConfigValue):

    def get(self, ctx, section, key, default):
        return ctx.cfg.get(section, key, default)


class IntegerValue(ConfigValue):

    def get(self, ctx, section, key, default):
        return ctx.cfg.get_int(section, key, default)


class FloatValue(ConfigValue):

    def get(self, ctx, section, key, default):
        return ctx.cfg.get_float(section, key, default)


class BooleanValue(ConfigValue):

    def get(self, ctx, section, key, default):
        return ctx.cfg.get_bool(section, key, default)


cfg = new.module('pocoo.settings.cfg')
cfg.str = StringValue
cfg.int = IntegerValue
cfg.float = FloatValue
cfg.bool = BooleanValue
sys.modules['pocoo.settings.cfg'] = cfg
