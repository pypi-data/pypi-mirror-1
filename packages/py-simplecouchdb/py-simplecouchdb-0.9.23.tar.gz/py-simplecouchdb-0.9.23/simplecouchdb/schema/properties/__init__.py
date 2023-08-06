# -*- coding: utf-8 -
# Copyright (c) 2008, 2009 Benoît Chesneau <benoitc@e-engura.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from calendar import timegm
import decimal
import datetime
import time

from simplecouchdb.schema.properties.view import *

class DuplicatePropertyError(Exception):
    """ exception raised when there is a duplicate 
    property in a model """

class BadValueError(Exception):
    """ exception raised when a value can't be validated 
    or is required """

class Property(object):
    """ Propertu base which all other properties
    inherit."""
    creation_counter = 0

    def __init__(self, verbose_name=None, name=None, 
            default=None, required=False, validators=None,
            choices=None):
        """ Default constructor for a property. 

        :param verbose_name: str, verbose name of field, could
                be use for description
        :param name: str, name of field
        :param default: default value
        :param required: True if field is required, default is False
        :param validators: list of callable or callable, field validators 
        function that are executed when document is saved.
        """

        self.verbose_name = verbose_name
        self.name = name
        self.default = default
        self.required = required
        self.validators = validators
        self.choices = choices
        Property.creation_counter += 1

    def __property_config__(self, document_class, property_name):
        self.document_class = document_class
        if self.name is None:
            self.name = property_name

    def __get__(self, document_instance, document_class):
        if document_instance is None:
            return self

        value = document_instance._doc.get(self.name)
        if value is not None:
            value = self._to_python(value)
        return value

    def __set__(self, document_instance, value):
        if value is not None:
            value = self._to_json(self.validate(value))
        document_instance._doc[self.name] = value

    def __delete__(self, document_instance):
        pass

    def default_value(self):
        """ return default value """

        default = self.default
        if callable(default):
            default = default()
        return default

    def validate(self, value):
        """ validate value """
        if self.empty(value):
            if self.required:
                raise BadValueError('Property %s is required' 
                        % self.name)
        else:
            if self.choices:
                match = False
                for choice in self.choices:
                    if choice == value:
                        match = True
                    if not match:
                        raise BadValueError('Property %s is %r; must be one of %r' % (self.name, value, self.choices))
        if self.validators:
            if isinstance(self.validators, (list, tuple,)):
                for validator in self.validators:
                    if callable(validator):
                        validator(value)
            elif callable(self.validators):
                self.validators(value)
        return value

    def empty(self, value):
        """ test if value is empty """
        return not value or value is None

    def _to_python(self, value):
        """ convert to python type """
        return unicode(value)

    def _to_json(self, value):
        """ convert to json, These converetd value is saved in couchdb. """

        return self._to_python(value)

    data_type = None

class StringProperty(Property):
    """ string property str or unicode property 
    
    *Value type*: unicode
    """
    _to_python = unicode

    def validate(self, value):
        value = super(StringProperty, self).validate(value)
        if value is not None and not isinstance(value, basestring):
            raise BadValueError(
                'Property %s must be unicode or str instance, not a %s' % (self.name, type(value).__name__))

        return value

    data_type = unicode

class IntegerProperty(Property):
    """ Integer property. map to int 
    
    *Value type*: int
    """
    _to_python = int

    def validate(self, value):
        value = super(IntegerProperty, self).validate(value)
        if value is not None and not isinstance(value, int):
            raise BadValueError(
                'Property %s must be int or long instance, not a %s'
                % (self.name, type(value).__name__)) 
        return value

    data_type = int

class LongProperty(Property):
    """ Long property, map to python long.
    
    *Value type*: long
    """
    _to_python = long

    def validate(self, value):
        value = super(LongProperty, self).validate(value)
        if value is not None and not isinstance(value, long):
            raise BadValueError(
                'Property %s must be int or long instance, not a %s'
                % (self.name, type(value).__name__)) 
        return value

    data_type = long

class FloatProperty(Property):
    """ Float property, map to python float 
    
    *Value type*: float
    """
    _to_python = float
    data_type = float

    def validate(self, value):
        value = super(FloatProperty, self).validate(value)
        if value is not None and not isinstance(value, float):
            raise BadValueError(
                'Property %s must be float instance, not a %s'
                % (self.name, type(value).__name__))

        return value
Number = FloatProperty

class BooleanProperty(Property):
    """ Boolean property, map to python bool
    
    *ValueType*: bool
    """
    _to_python = bool
    data_type = bool

    def validate(self, value):
        value = super(BooleanProperty, self).validate(value)
        if value is not None and not isinstance(value, bool):
            raise BadValueError(
                'Property %s must be bool instance, not a %s'
                % (self.name, type(value).__name__))

        return value

class DecimalProperty(Property):
    """ Decimal property, map to Decimal python object
    
    *ValueType*: decimal.Decimal
    """
    data_type = decimal.Decimal

    def _to_python(self, value):
        return decimal.Decimal(value)

    def _to_json(self, value):
        return unicode(value)

class DateTimeProperty(Property):
    """DateTime property. It convert iso3339 string
    to python and vice-versa. Map to datetime.datetime
    object.
    
    *ValueType*: datetime.datetime
    """

    def __init__(self, verbose_name=None, auto_now=False, auto_now_add=False,
               **kwds):
        super(DateTimeProperty, self).__init__(verbose_name, **kwds)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add

    def validate(self, value):
        value = super(DateTimeProperty, self).validate(value)
        if value and not isinstance(value, self.data_type):
            raise BadValueError('Property %s must be a %s' %
                          (self.name, self.data_type.__name__))
        return value

    def default_value(self):
        if self.auto_now or self.auto_now_add:
            return self.now()
        return Property.default_value(self)

    def _to_python(self, value):
        if isinstance(value, basestring):
            try:
                value = value.split('.', 1)[0] # strip out microseconds
                value = value.rstrip('Z') # remove timezone separator
                timestamp = timegm(time.strptime(value, '%Y-%m-%dT%H:%M:%S'))
                value = datetime.datetime.utcfromtimestamp(timestamp)
            except ValueError, e:
                raise ValueError('Invalid ISO date/time %r' % value)
        return value

    def _to_json(self, value):
        if self.auto_now:
            value = self.now()
        return value.replace(microsecond=0).isoformat() + 'Z'

    data_type = datetime.datetime

    @staticmethod
    def now():
        return datetime.datetime.utcnow()

class DateProperty(DateTimeProperty):
    """ Date property, like DateTime property but only
    for Date. Map to datetime.date object
    
    *ValueType*: datetime.date
    """
    data_type = datetime.date

    @staticmethod
    def now():
        return datetime.datetime.now().date()

    def _to_python(self, value):
        if isinstance(value, basestring):
            try:
                value = datetime.date(*time.strptime(value, '%Y-%m-%d')[:3])
            except ValueError, e:
                raise ValueError('Invalid ISO date %r' % value)
        return value

    def _to_json(self, value):
        return value.isoformat()

class TimeProperty(DateTimeProperty):
    """ Date property, like DateTime property but only
    for time. Map to datetime.time object
    
    *ValueType*: datetime.time
    """

    data_type = datetime.time

    @staticmethod
    def now(self):
        return datetime.datetime.now().time()

    def _to_python(self, value):
        if isinstance(value, basestring):
            try:
                value = value.split('.', 1)[0] # strip out microseconds
                value = datetime.time(*time.strptime(value, '%H:%M:%S')[3:6])
            except ValueError, e:
                raise ValueError('Invalid ISO time %r' % value)
        return value

    def _to_json(self, value):
        return value.replace(microsecond=0).isoformat()

class ListProperty(Property):
    """List property. Map to python list
    
    *ValueType*: list
    """

    _to_python = list

    def validate(self, value):
        value = super(ListProperty, self).validate(value)

        if not isinstance(value, (list, tuple,)):
            raise BadValueError('Property %s must be a list' %
                    self.name)

        return value
