# -*- coding: utf-8 -
# Copyright (c) 2008, Benoît Chesneau <benoitc@e-engura.com>
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


""" module that provide a Document object that allow you 
to map statically, dynamically or both a CouchDB
document in python """

import datetime
import decimal
import re

from simplecouchdb.client.database import Database
from simplecouchdb.schema import properties as p

__all__ = ['ReservedWordError', 'MAP_TYPES_PROPERTIES',
        'Document']

class ReservedWordError(Exception):
    """ exception raised when a reserved word
    is used in Document schema """

_RESERVED_WORDS = ['_id', '_rev', '$schema']

MAP_TYPES_PROPERTIES = {
        decimal.Decimal: p.DecimalProperty,
        datetime.datetime: p.DateTimeProperty,
        datetime.date: p.DateProperty,
        datetime.time: p.TimeProperty
}

_ALLOWED_PROPERTY_TYPES = set([
    basestring,
    str,
    unicode,
    bool,
    int,
    long,
    float,
    datetime.datetime,
    datetime.date,
    datetime.time,
    decimal.Decimal,
    list,
    tuple,
    type(None)
])

re_date = re.compile('^(\d{4})\D?(0[1-9]|1[0-2])\D?([12]\d|0[1-9]|3[01])$')
re_time = re.compile('^([01]\d|2[0-3])\D?([0-5]\d)\D?([0-5]\d)?\D?(\d{3})?$')
re_datetime = re.compile('^(\d{4})\D?(0[1-9]|1[0-2])\D?([12]\d|0[1-9]|3[01])(\D?([01]\d|2[0-3])\D?([0-5]\d)\D?([0-5]\d)?\D?(\d{3})?([zZ]|([\+-])([01]\d|2[0-3])\D?([0-5]\d)?)?)?$')
re_decimal = re.compile('^(\d+).(\d+)$')

def check_reserved_words(attr_name):
    if attr_name in _RESERVED_WORDS:
        raise ReservedWordError(
            "Cannot define property using reserved word '%(attr_name)s'." % 
            locals())

class DocumentBase(type):
    def __new__(cls, name, bases, attrs):
        properties = {}
        views = {}
        defined = set()
        for base in bases:
            if hasattr(base, '_properties'):
                property_keys = base._properties.keys()
                duplicate_properties = defined.intersection(property_keys)
                if duplicate_properties:
                    raise p.DuplicatePropertyError(
                        'Duplicate properties in base class %s already defined: %s' % (base.__name__, list(duplicate_properties)))
                defined.update(property_keys)
                properties.update(base._properties) 

        for attr_name, attr in attrs.items():
            if isinstance(attr, p.Property):
                check_reserved_words(attr_name)
                if attr_name in defined:
                    raise p.DuplicatePropertyError('Duplicate property: %s' % attr_name)
                properties[attr_name] = attr
                attr.__property_config__(cls, attr_name)
            elif isinstance(attr, p.ViewProperty):
                if attr_name in defined:
                    raise p.DuplicatePropertyError('Duplicate property: %s' % attr_name)
                views[attr_name] = attr
                attr.__view_config__(cls, attr_name)

        attrs['_properties'] = properties
        attrs['_views'] = views

        return type.__new__(cls, name, bases, attrs)        

class Document(object):
    """ Document object that map a CouchDB Document.
    It allow you to map statically a document by 
    providing fields like you do with any ORM or
    dynamically. Ie unknown fields are loaded as
    object property that you can edit, datetime in
    iso3339 format are automatically translated in
    python types (date, time & datetime) and decimal too.

    Example of document:

    .. code-block:: python
        
        from simplecouchdb.schema import *
        class MyDocument(Document):
            mystring = StringProperty()


    Fields of a documents can be accessed as property or
    key of dict. These are similar : ``value = instance.key or
    value = instance['key'].``

    To delete a property simply do ``del instance[key'] or 
    delattr(instance, key)``
    """

    __metaclass__ = DocumentBase
    
    _dynamic_properties = None
    _doc = None
    _doc_type = None
    
    def __init__(self, id=None, doc_type=None, **kwargs):
        self._dynamic_properties = {}
        self._doc = {}

        if id is not None:
            self._doc['_id'] = id

        if doc_type is not None:
            self._doc_type = doc_type
        else:
            self._doc_type = self.__class__.__name__
           
        for prop in self._properties.values():
            if prop.name in kwargs:
                value = kwargs.pop(prop.name)
            else:
                value = prop.default_value()
            prop.__set__(self, value)

        for attr_name, value in kwargs.iteritems():
            if attr_name not in self._properties and value is not None:
                setattr(self, attr_name, value)

    def __setattr__(self, key, value):
        check_reserved_words(key)
        if not key.startswith('_') and \
                key not in self._properties and \
                key not in dir(Document) and key not in self._views: 
            if type(value) not in _ALLOWED_PROPERTY_TYPES:
                raise TypeError("Document cannot accept values of type '%s'." %
                        type(value).__name__)
            if self._dynamic_properties is None:
                self._dynamic_properties = {}
            self._dynamic_properties[key] = value 
        else:
            object.__setattr__(self, key, value)

    def dynamic_properties():
        if self._dynamic_properties is None:
            return {}
        return self._dynamic_properties.keys()

    def properties():
        return self._properties

    def _get_type(self):
        """ Get/Set type of document by instance. 
        By default it is set to its name.
        """
        return self._doc_type
    
    def _set_type(self, doc_type):
        self._doc_type = doc_type
    doc_type = property(_get_type, _set_type)

    def _set_id(self, docid):
        self._doc['_id'] = docid
    def _get_id(self):
        """ get or set id of document"""
        return self._doc.get('_id')
    id = property(_get_id, _set_id)

    rev = property(lambda self: self._doc.get('_rev'))

    def __delattr__(self, key):
        """ delete property
        """

        if key in self._doc:
            del self._doc[key]

        if self._dynamic_properties and key in self._dynamic_properties:
            del self._dynamic_properties[key]
        else: 
            object.__delattr__(self, key)
        
    def __getattr__(self, key):
        """ get property value 
        """

        if self._dynamic_properties and key in self._dynamic_properties:
            return self._dynamic_properties[key]
        else:
            return getattr(super(Document, self), key)

    def __getitem__(self, key):
        """ get property value
        """
        return getattr(self, key)

    def __setitem__(self, key, value):
        """ add a property
        """
        setattr(self, key, value)

    def __delitem__(self, key):
        """ delete a property
        """
        try:
            delattr(self, key)
        except AttributeError, e:
            raise KeyError(e)

    remove = __delitem__

    def __contains__(self, key):
        """ does object contain this propery ?

        :param key: name of property
        
        :return: True if key exist.
        """
    
        if key in self._properties or key in self._dynamic_properties:
            return True
        return False

    def __iter__(self):
        """ iter document instance properties
        """

        all_properties = self._properties.copy()
        if self._dynamic_properties is not None:
            all_properties.update(self._dynamic_properties)

        for prop, value in all_properties.iteritems():
            if value is not None:
                yield (prop, value)
    iteritems = __iter__

    def items(self):
        """ return list of items
        """
        return list(self)

    def __len__(self):
        """ get number of properties
        """
        length = len(self._doc or ())
        if self._dynamic_properties:
            length += len(self._dynamic_properties or ())
        return length

    @classmethod
    def wrap(cls, data):
        instance = cls()
        
        if '_id' in data:
            instance._doc.update({'_id': data['_id']})
            del data['_id']

        if '_rev' in data:
            instance._doc.update({'_rev': data['_rev']})
            del data['_rev']

        doc_type = data.get('doc_type')
        instance._doc_type = doc_type or instance.__class__.__name__

        for prop in instance._properties.values():
            if prop.name in data:
                value = data.pop(prop.name)
                instance._doc[prop.name] = value
            else:
                value = prop.default_value()
                prop.__set__(instance, value)

        for attr_name, value in data.iteritems():
            if attr_name not in instance._properties and value is not None:
                setattr(instance, attr_name, value)

        if instance._dynamic_properties:
            for attr_name, value in instance._dynamic_properties.items():
                data_type = None
                if isinstance(value, basestring):
                    if re_date.match(value):
                        data_type = datetime.date
                    elif re_time.match(value):
                        data_type = datetime.time
                    elif re_datetime.match(value):
                        data_type = datetime.datetime
                    elif re_decimal.match(value):
                        data_type = decimal.Decimal

                if data_type is not None:
                    prop = MAP_TYPES_PROPERTIES[data_type]()
                    value = prop._to_python(value)
                    instance._dynamic_properties[attr_name] = value

        return instance


    def convert_property(self, value):
        if type(value) in MAP_TYPES_PROPERTIES:
            prop = MAP_TYPES_PROPERTIES[type(value)]()
            value = prop._to_json(value)
        return value

    def validate(self):
        """ validate a document """
        for attr_name, value in self._doc.iteritems():
            if attr_name in self._properties:
                self._properties[attr_name].validate(
                        getattr(self, attr_name))

    def save(self, db):
        """ Save document in database.
            
        :params db: simplecouchdb.client.Database instance
        """

        self.validate()

        doc = self._doc.copy()

        if self._dynamic_properties and self._dynamic_properties is not None:
            for key, value in self._dynamic_properties.iteritems():
                doc.update({key: self.convert_property(value)})
        if self._doc_type is None:
            self._doc_type = self.__class__.__name__
        self._doc['doc_type'] = doc['doc_type'] = self._doc_type
        db.save(doc)
        self._doc.update({'_id': doc['_id'], '_rev': doc['_rev']})
    store = save

    @classmethod
    def get(cls, db, docid):
        """ Get document from a database
    
        :params db: simplecouchdb.client.Database instance
        :params docid: str, id of document
        """

        doc = db.get(docid)
        if doc is None:
            return None
        return cls.wrap(doc)
    load = get

    def delete(self, db):
        if self.id is not None:
            del db[self.id]
            self._data = {}
            return True
        return False
    
    @classmethod
    def view(cls, db, view_name, **params):
        """ Get documents associated to a view.
        Results of view are automatically wrapped
        to Document object.

        
        :params db: simplecouchdb.client.Database instance
        :params view_name: str, name of view
        :params params:  params of view

        :return: :class:`simplecouchdb.client.ViewResults` instance. All
        results are wrapped to current document instance.
        """
        def _wrapper(row):
            data = row['value']
            data['_id'] = row['id']
            return cls.wrap(data)
        return db.view.get(view_name, wrapper=_wrapper, **params)

    @classmethod
    def temp_view(cls, db, design, **params):
        """ Temporary view. Like in view method,
        results are automatically wrapped to 
        Document object.

        :params db: simplecouchdb.client.Database instance
        :params design: design object, See `simplecouchd.client.Database`
        :params params:  params of view

        :return: Like view, return a :class:`simplecouchdb.client.ViewResults` instance. All
        results are wrapped to current document instance.
        """

        def _wrapper(row):
            data = row['value']
            data['_id'] = row['id']
            return cls.wrap(data)
        return db.temp_view.get(design, wrapper=_wrapper, **params)

