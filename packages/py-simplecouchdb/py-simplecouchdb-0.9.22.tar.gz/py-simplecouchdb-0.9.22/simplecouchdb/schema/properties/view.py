# -*- coding: utf-8 -
# Copyright (c) 2008, Benoît Chesneau <benoitc@e-engura.com>
# Copyright (C) 2007-2008 Christopher Lenz
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

from simplecouchdb.client.view import ViewDefinition

class ViewProperty(object):
    """ view property. It allow you add a view as 
    a member of a Document object. It return a
    :class:`simplecouchdb.client.ViewDefinition` object.

    .. code-block:: python

        class DocTest(Document):
            field = StringProperty()
            view_all = ViewProperty("test", map_fun=\"\"\"function(doc) {
            if (doc.doc_type == "DocTest")
                    { emit(doc._id, doc);}}\"\"\")
        
        results = DocTest.view_all.get(db)
        
    
    All results are DocTest instance.
    """
        

    def __init__(self, design_name, name=None, map_fun=None,
            reduce_fun=None, language='javascript',
            wrapper=None, **params):
        """Constructor for ViewProperty.
        
        Args:
            design_name: str, name of view
            name: name of view. It is set when Document
                object is created.
            map_fun: file object or str, map function
            reduce_fun: file object or str, reduce function
            language: language of view. by default javascript
            wrapper: allow you to provide a customised wrapper,
                by default results are wrap around object. 
            params: params of view
        """


        self.design_name = design_name
        self.name = name
        self.map_fun = map_fun
        self.reduce_fun = reduce_fun
        self.wrapper = wrapper
        self.language = language
        self.params = params

    def __view_config__(self, document_class, name):
        self.name = name
        self.document_class = document_class

    def __get__(self, document_instance, document_class):
        if self.wrapper is None:
            def wrapper(row):
                data = row['value']
                data['_id'] = row['id']
                return document_class.wrap(data)
        else:
            wrapper = self.wrapper

        return ViewDefinition(self.design_name, self.name,
                map_fun=self.map_fun, reduce_fun=self.reduce_fun,
                language=self.language, wrapper=wrapper,
                **self.params)


