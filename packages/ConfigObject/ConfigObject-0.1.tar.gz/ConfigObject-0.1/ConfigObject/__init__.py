# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser

__doc__ = """
:class:`~ConfigObject.ConfigObject` is a wrapper to the python ConfigParser_ to
allow to access sections/options with attribute names::

    >>> from ConfigObject import ConfigObject
    >>> config = ConfigObject()

    >>> config.default.value = 1

Values are stored as string::

    >>> config.default.value
    '1'

Values are returned as :class:`~ConfigObject.ConfigValue` to convert result to
other types::

    >>> config.default.value.as_int()
    1

Here is how list are stored::

    >>> config.default.value1 = range(2)
    >>> print config.default.value1
    0
    1
    >>> config.default.value1.as_list()
    ['0', '1']

You can use keys::

    >>> config['set']['value'] = 1
    >>> config['set']['value'].as_int()
    1

You can set a section as dict::

    >>> config.dict = dict(value=1)
    >>> config.dict.value.as_int()
    1

See what your section look like::

    >>> config['set']
    {'value': '1'}

Delete options::

    >>> del config['set'].value
    >>> config['set']
    {}
"""

__all__ = ('ConfigObject', 'config_module', 'Object')

class ConfigValue(str):

    def as_int(self):
        """convert value to int"""
        try:
            return int(self)
        except TypeError:
            raise TypeError('%s is not a valid int' % self)

    def as_float(self):
        """convert value to float"""
        try:
            return float(self)
        except TypeError:
            raise TypeError('%s is not a valid float' % self)

    def as_list(self, sep=None):
        """convert value to list"""
        if sep is None and '\n' in self:
                sep = '\n'
        return [ConfigValue(v) for v in self.split(sep) if v]

    def as_bool(self):
        """convert value to bool"""
        if self.lower() in ('1', 'y', 'true', 'yes'):
            return True
        elif self.lower() in ('0', 'f', 'false', 'no'):
            return False
        elif not self:
            return False
        else:
            raise TypeError('%s is not a valid bool' % self)


def _ConfigValue(value=''):
    """
        >>> _ConfigValue(1)
        '1'
        >>> _ConfigValue(.1)
        '0.1'
        >>> _ConfigValue(True)
        'true'
        >>> print _ConfigValue(range(2))
        0
        1
    """
    if value is True or value is False:
        value = value and 'true' or 'false'
    elif isinstance(value, set) or \
         isinstance(value, list) or \
         isinstance(value, tuple):
        value = '\n'.join([str(v) for v in value])
    return ConfigValue(value)

class ConfigDict(object):

    def __init__(self, parent, section):
        self.__parent = parent
        self.__section = section

    def __getattr__(self, attr, default=None):
        return self.get(attr, None)

    def __getitem__(self, attr):
        return self.get(attr, None)

    def get(self, attr, default=None):
        config = self.__parent
        section = self.__section
        if config.has_section(section):
            value = config.get(section, attr)
        else:
            value = default
        if value is None:
            value = _ConfigValue()
        elif not isinstance(value, ConfigValue):
            value = _ConfigValue(value)
        return value

    def __setattr__(self, attr, value):
        if attr.startswith('_ConfigDict__'):
            object.__setattr__(self, attr, value)
        else:
            self.__setitem__(attr, value)

    def __setitem__(self, attr, value):
        config = self.__parent
        if not config.has_section(self.__section):
            config.add_section(self.__section)
        if value is not None and not isinstance(value, ConfigValue):
            value = _ConfigValue(value)
        config.set(self.__section, attr, value)

    def __delattr__(self, attr):
        config = self.__parent
        if config.has_section(self.__section):
            if config.has_option(self.__section, attr):
                config.remove_option(self.__section, attr)

    __delitem__ = __delattr__

    def items(self):
        if self.__parent.has_section(self.__section):
            items = self.__parent.items(self.__section)
            return [(k, _ConfigValue(v)) for k, v in items]
        return []

    def keys(self):
        if self.__parent.has_section(self.__section):
            return self.__parent.options(self.__section)
        return []

    def __repr__(self):
        return repr(dict(self.items()))

class Object(dict):
    def __getattr__(self, attr):
        return self.get(attr)
    def __setattr__(self, attr, value):
        self[attr] = value


class ConfigObject(ConfigParser, object):
    """ConfigParser_ wrapper
    """

    def __init__(self, *args, **kwargs):
        self.__config = Object()
        for k in ('autoreload', 'autosave'):
            if k in kwargs:
                kwargs.pop(k)
                self.__config[k] = True
            else:
                self.__config[k] = False
        ConfigParser.__init__(self, *args, **kwargs)

    def __getattr__(self, attr):
        return ConfigDict(self, attr)

    __getitem__ = __getattr__

    def __setattr__(self, attr, value):
        if attr.startswith('_') or isinstance(value, Object):
            object.__setattr__(self, attr, value)
        elif value:
            self.__setitem__(attr, value)

    def __setitem__(self, attr, value):
        if isinstance(value, dict):
            if not self.has_section(attr):
                self.add_section(attr)
            for k, v in value.items():
                self.set(attr, k, ConfigValue(v))
        else:
            raise TypeError('Value must be a dict')

    def __delattr__(self, attr):
        if self.has_section(attr):
            self.remove_section(attr)

    __delitem__ = __delattr__

def config_module(name, file, *filenames):
    """Allow to set a :class:`~ConfigObject.ConfigObject` as module. You have
    to add this to ``yourproject/config.py``:

    .. literalinclude:: ../ConfigObject/tests/config.py

    Then you are able to use ``from yourproject import config`` where
    ``config`` is the :class:`~ConfigObject.ConfigObject` itself.
    """
    config = ConfigObject()
    config.__name__ = name
    config.__file__ = file
    config.__path__ = file
    config.read(filenames)
    import sys
    sys.modules[name] = config
    return config


