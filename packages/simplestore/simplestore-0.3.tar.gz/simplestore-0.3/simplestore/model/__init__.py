# Copyright 2009 David Reynolds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import zlib
import datetime

try:
    import cPickle as pickle
except ImportError:
    import pickle

from simplestore.datastore import __entities_table__

entities_table = """
CREATE TABLE IF NOT EXISTS %s (
    added_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id CHAR(32) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    fields MEDIUMBLOB,
    UNIQUE KEY (id),
    KEY (created_at)
) ENGINE=InnoDB;
""" % __entities_table__

def _initialize_properties(cls, name, bases, dct):
    cls._properties = {}
    defined = set()

    # add properties from base classes and make sure
    # there are no duplicates.
    for base in bases:
        if hasattr(base, '_properties'):
            property_keys = base._properties.keys()
            dupes = defined.intersection(property_keys)
            if dupes:
                raise Exception("Duplicate properties in base class %s "
                                "already defined: %s" %
                                (base.__name__, list(dupes)))
            defined.update(property_keys)
            cls._properties.update(base._properties)

    for name, attr in dct.iteritems():
        if isinstance(attr, Property):
            if name in defined:
                raise Exception("Duplicate property: %s" % name)
            defined.add(name)
            cls._properties[name] = attr
            attr._configure(cls, name)

class MetaModel(type):

    def __init__(cls, name, bases, dct):
        super(MetaModel, cls).__init__(name, bases, dct)
        _initialize_properties(cls, name, bases, dct)

class Property(object):

    def __init__(self,
                 name=None,
                 default=None,
                 required=False,
                 validator=None,
                 choices=None):
        self.name = name
        self.default = default
        self.required = required
        self.validator = validator

        # choices is used to assert a property's
        # value is one of the choices.
        self.choices = choices
        self.model_class = None

    def _configure(self, model_class, property_name):
        self.model_class = model_class
        if self.name is None:
            self.name = property_name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        try:
            return getattr(instance, self._attr_name())
        except AttributeError:
            return None

    def __set__(self, instance, value):
        value = self.validate(value)
        setattr(instance, self._attr_name(), value)

        if hasattr(instance, '_has_changed'):
            if not instance._has_changed:
                instance._has_changed = True

    def default_value(self):
        return self.default

    def _attr_name(self):
        return '_' + self.name

    def empty(self, value):
        return not value

    def validate(self, value):
        if self.empty(value):
            if self.required:
                raise Exception('Property %s is required' % self.name)
        else:
            if self.choices:
                match = False
                for choice in self.choices:
                    if choice == value:
                        match = True
                if not match:
                    raise Exception('Property %s is %r; must be one of %r' %
                                    (self.name, value, self.choices))

        if self.validator is not None:
            self.validator(value)
        return value

    def get_value_for_datastore(self, instance):
        return self.__get__(instance, instance.__class__)

    data_type = str

class StringProperty(Property):

    def validate(self, value):
        value = super(StringProperty, self).validate(value)
        if value is not None and not isinstance(value, basestring):
            raise Exception('Property %s must be a str or unicode instance, not a %s' %
                            (self.name, type(value).__name__))
        return value

    data_type = basestring

class KeyProperty(Property):

    def validate(self, value):
        value = super(KeyProperty, self).validate(value)
        if value is not None and not isinstance(value, str):
            raise Exception('Property %s must be a str, not a %s' %
                            (self.name, type(value).__name))

        if value and len(value) != 32:
            raise Exception('Property %s must be a 32-byte string' % self.name)

        return value

    data_type = str

class BooleanProperty(Property):

    def validate(self, value):
        value = super(BooleanProperty, self).validate(value)
        if value is not None:
            if isinstance(value, int):
                value = bool(value)
            if not isinstance(value, bool):
                raise Exception('Property %s must be a bool' % self.name)

        return value

    def get_value_for_datastore(self, instance):
        val = super(BooleanProperty, self).get_value_for_datastore(instance)
        return bool(val)

    data_type = bool

    def empty(self, value):
        return value is None

class IntegerProperty(Property):

    def validate(self, value):
        value = super(IntegerProperty, self).validate(value)
        if value is None:
            return value

        if not isinstance(value, (int, long)) or isinstance(value, bool):
            raise Exception('Property %s must be an int or long, not a %s' %
                            (self.name, type(value).__name__))

        if value < -0x8000000000000000 or value > 0x7fffffffffffffff:
            raise Exception('Property %s must fit in 64 bits' % self.name)

        return value

    def get_value_for_datastore(self, instance):
        val = super(IntegerProperty, self).get_value_for_datastore(instance)
        if val is None:
            return ''
        return int(val)

    data_type = int

class DateTimeProperty(Property):

    def __init__(self, auto_now=False, auto_now_add=False, **kwargs):
        """
        auto_now: datetime property is updated every time it's saved.
        auto_add_now: datetime property is set when the instance is created."""
        super(DateTimeProperty, self).__init__(**kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add

    def validate(self, value):
        value = super(DateTimeProperty, self).validate(value)
        if value and not isinstance(value, self.data_type):
            raise Exception('Property %s must be a %s' %
                            (self.name, self.data_type.__name__))
        return value

    def default_value(self):
        if self.auto_now or self.auto_now_add:
            return self.now()
        return super(DateTimeProperty, self).default_value()

    def get_value_for_datastore(self, instance):
        if self.auto_now:
            val = self.now()
        else:
            val = super(DateTimeProperty, self).get_value_for_datastore(instance)
        #if val is None:
        #    return val
        #return str(val)
        return val

    data_type = datetime.datetime

    @staticmethod
    def now():
        return datetime.datetime.utcnow()

class DateProperty(Property):

    def __init__(self, **kwargs):
        super(DateProperty, self).__init__(**kwargs)

    def validate(self, value):
        value = super(DateProperty, self).validate(value)
        if value and not isinstance(value, self.data_type):
            raise Exception('Property %s must be a %s' %
                            (self.name, self.data_type.__name__))
        return value

    def default_value(self):
        return super(DateProperty, self).default_value()

    def get_value_for_datastore(self, instance):
        val = super(DateProperty, self).get_value_for_datastore(instance)
        #if val is None:
        #    return val
        #return str(val)
        return val

    data_type = datetime.date

class ListProperty(Property):

    def __init__(self, item_type=str, default=None, **kwargs):
        if item_type is str:
            item_type = basestring
        self.item_type = item_type

        if default is None:
            default = []

        super(ListProperty, self).__init__(default=default, **kwargs)

    def validate(self, value):
        value = super(ListProperty, self).validate(value)
        if value is not None:
            if not isinstance(value, list):
                raise Exception('Property %s must be a list' % self.name)
            value = self.validate_list_contents(value)
        return value

    def validate_list_contents(self, value):
        if self.item_type in (int, long):
            item_type = (int, long)
        else:
            item_type = self.item_type

        for item in value:
            if not isinstance(item, item_type):
                if item_type == (int, long):
                    raise Exception('Items in the %s list must all be integers' % self.name)
                else:
                    raise Exception('Items in the %s list must all be %s instances' %
                        (self.name, self.item_type.__name__))
        return value

    def empty(self, value):
        return value is None

    data_type = list

    def default_value(self):
        return list(super(ListProperty, self).default_value())

class Model(object):

    __metaclass__ = MetaModel

    def __init__(self, **kwargs):
        self._original_attrs = {}

        for prop in self._properties.values():
            if prop.name in kwargs:
                value = kwargs[prop.name]
            else:
                value = prop.default_value()

            prop.__set__(self, value)
            self._original_attrs[prop.name] = value

        # set this variable after initialization,
        # otherwise the prop.__set__ above sets this
        # to True once per property
        self._has_changed = False

    def fields(self):
        _fields = {}
        for name, attr in self._properties.iteritems():
            _fields[name] = attr.get_value_for_datastore(self)
        return _fields

    def compressed_fields(self):
        _fields = self.fields()
        _fields = pickle.dumps(_fields)
        _fields = zlib.compress(_fields)
        return _fields
