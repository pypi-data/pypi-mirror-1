# -*- coding: utf-8 -
# Copyright (c) 2008, 2009, Benoît Chesneau <benoitc@e-engura.com>
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

""" Module that allow you to manage, access to view
in a couchdb database.

    ViewResults: A ViewResults instance is constructed 
        by View, TemporaryView, AllDocumentView and Viewdefinition
        objects. Results are only retrieved when you use one method
        of ViewResults instance.

    View: Object that allow you to retrieve resulys of a view
        in db.

    TemporaryView: same as view but for temporary view

    AllDocumentView: use by Database.documents method

    ViewDefinition: A ViewDefiniton object allow you to easyly
        create a view and add it to a database. You could sync
        a database to add allo cached ViewDefintion's object.

    Sample usage of a view :

    >>> from simplecouchdb import Server, Database, Views
    >>> server = Server()
    >>> db = Database(name="test", server=server)
    >>> results = db.view.get("test/all")

    at this step, ou have only set an instance of
    ViewResults.

    On only retrieved results when you for example iter
    results :

    >>> list_of_results = list(iter(results))
"""
        
import sys
import weakref

from simplecouchdb.resource import ResourceNotFound
from simplecouchdb import url


class InvalidView(Exception):
    """ Exception raised when a _design doc is invalid """

class ViewResults(object):
    """ ViewResults object. It act as a list.
    you could use iter, list and empty function """

    def __init__(self, view, wrapper=None, **params):
        self._view = view
        self._wrapper = wrapper
        self.params = params
        self._result_cache = {}
   
    def __repr__(self):
        return repr(list(self))

    def __len__(self):
        self._fetch_if_needed()
        total_rows = 0
        if self._result_cache:
            if 'rows' in self._result_cache and self._result_cache['rows']:
                total_rows = len(self._result_cache['rows'])
            elif 'total_rows' in self._result_cache:
                total_rows = self._result_cache['total_rows']
        return total_rows

    def __iter__(self):
        self._fetch_if_needed()
        rows = []
       
        if self._result_cache:
            rows = self._result_cache['rows']
        
        if self._wrapper is not None:
            for row in rows:
                yield self._wrapper(row)
        else:
            for row in rows:
                yield row

    def __nonzero__(self):
        if self._result_cache is not None:
            return bool(self._result_cache['rows'])
        try:
            iter(self).next()
        except StopIteration:
            return False
        return True
   
    def items():
        return list(self)

    @property
    def offset(self):
        if bool(self):
            return self._result_cache.get('offset', 0)
    
    @property
    def total_rows(self):
        total_rows  = 0
        self._fetch_if_needed()
        if self.result_cache:
            total_rows = self.result_cache['total_rows']
        return total_rows


    def fetch(self):
        result = {}
        try:
            result = self._view._make_request()
        except ResourceNotFound:
            pass
        self._result_cache = result
        
    def _fetch_if_needed(self):
        if not self._result_cache:
            self.fetch()
 

class View(object):
    """ View object. Object to access to a view. All
    other Views object (except ViewDefintion) inherit this.
    """
    def __init__(self, database):
        self.database = database     
        self.res = self.database.res.clone()
        self.params = {}

    def __call__(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get(self, view_name, wrapper=None, **params):
        """ get results of a view

        Args:
            view_name: name of view
            wrapper: callable to wrap results 
            params: params of a view

        Return:
            ViewResults instance
        """

        self.params = params or {}
        self.wrapper = wrapper
        self.view_path = "_view/%s" % view_name
        uri = url.make_uri(
                self.database.res.uri, 
                *self.view_path.split('/'))
        self.res.uri = uri
        return ViewResults(self, wrapper=wrapper, **params)

    def count(self, view_name):
        """ get max number of resuls of a view

        Args:
            view_name: name of view
        Return:
            int
        """
        results = self.get(view_name, limit=0)
        return len(results)

    def _make_request(self): 
        results, resp =  self.res.get(**self.params)
        return results

class TempView(View):
    """ Temp view representation
    """
    
    def get(self, design, wrapper=None, **params):
        """ get results 

        Args:
        design: dict or string of a slow view:
            design_doc = {
                "map": \"\"\"function(doc) { 
                    if (doc.docType == "test") { 
                        emit(doc._id, doc);
                }}\"\"\"
            }
            wrapper: callable to wrap results 
            params: params of a view

        Return:
            ViewResults instance
        """

        self.params = params or params
        if hasattr(design, 'read'):
            self.design = design.read()
        else:
            self.design = design
        return ViewResults(self, wrapper=wrapper, **params)

    def _make_request(self):
        results, resp = self.res.post('_temp_view', data=self.design,
                **self.params)
        return results

class AllDocumentsView(View):
    def get(self, **params):
        self.params = params or {}
        return ViewResults(self, **params)

    def _make_request(self):
        results, resp = self.res.get('_all_docs', **self.params)
        return results

class ViewCache(object):
    """
    A cache that store view installed in db
    """
    # Use the Borg pattern to share state between all instances. Details at
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531.
    __shared_state__ = dict (
            databases = [],
            db_views = {}
    )

    def __init__(self):
        self.__dict__ = self.__shared_state__

    def add_view(self, dbname, view_def):
        """Add a view definition to the cache. View are only created
        When you sync a database (see :meth:`simplecouchdb.client.Database.sync` method)

        :param dbname: name of database
        :param view_def: :class:`simplecouchdb.client.ViewDefinition` instance
        """

        if dbname not in self.databases:
            self.databases.append(dbname)

        design_path = "%s/%s" %  (
                view_def.design_name,
                view_def.view_name
        )
        if dbname not in self.db_views:
            self.db_views[dbname] = weakref.WeakValueDictionary()
        self.db_views[dbname][design_path] = view_def

    def get_views(self, dbname):
        """ get all views of a database registered in the cache

        :param dbname: name of database
        """

        if dbname not in self.db_views:
            return None
        return self.db_views[dbname]

    def get_view(self, dbname, design_name, view_name):
        """ Get view registered in the cache for a database.

        :param dbname: name of database
        :param design_name: name of design document
        :param view_name: name of view

        :return: :class:`simplecouchdb.client.ViewDefinition` instance
        registered in the cache.
        """

        if dbname in self.db_views:
            return None

        design_path = "%s/%s" %  (
                view_def.design_name,
                view_def.view_name
        )
        return self.db_views[dbname].get(design_path)

view_cache = ViewCache()

class ViewDefinition(object):
    """ class to maintain/ register a '_design'
    document.
    Idee borrowed to couchdb-python
    """

    def __init__(self, design_name, view_name, map_fun=None,
        reduce_fun=None, language='javascript', wrapper=None,
        **params):
        """Constructor to ViewDefinition

            :param design_name: name of design document
            :param view_nane: name of view
            :param map_fun: str of file object, string for map function
            :param reduce_fun: str of file object, string for reduce 
                function
            :param language: language of view, default is javascript
            :param wrapper: default wrapper of view
            :param params: default params of view
        """

        if design_name.startswith('_design/'):
            design_name = design_name[8:]
        if design_name.startswith('/'):
            design_name = design_name[1:]
        self.design_name = design_name
        self.view_name = view_name
        self.map_fun = map_fun
        self.reduce_fun = reduce_fun
        self.language = language or 'javascript'
        self.params = params or {}
        self.wrapper = wrapper

    def register(self, db_name):
        """ register view in db
        
        Args:
            db_name: name of db
        """

        register_view(db_name, self)

    def sync(self, db, verbose_level=None):
        """ sync view in db. If it don't exist,
        create it. """

        if self.map_fun is None:
            if verbose_level == 2:
                print >> sys.stderr, "Not synced: no map"
            return 
        design_path = '_design/%s' % self.design_name
        design_doc = db.get(design_path)
        view = { "map": self.map_fun }
        if self.reduce_fun:
            view["reduce"] = self.reduce_fun

        if design_doc is None:            
            db.save({
                '_id': design_path,
                'language': self.language,
                'views': { self.view_name: view }
            })
            if verbose_level == 2:
                print >> sys.stderr, "%s/%s created" % (
                        design_path, self.view_name)
        else:
            if self.language != design_doc['language']:
                raise ValueError("View definition language is different from the _design doc already stored in db")
            design_doc['views'][self.view_name] = view
            db.save(design_doc)

    def get(self, db, wrapper=None, sync=True, **params):
        """ get result of view like View object. If sync is true
        try ro create or update the view. """

        params = params or {}
        self.params.update(params)
        if callable(wrapper):
            self.wrapper = wrapper
        self.view_path = "_view/%s/%s" % (
                self.design_name, self.view_name)

        # sync view definition if it don't exist
        if sync and self.map_fun:
            try:
                views = db['_design/%s'] % self.design_name
                if self.view_name in views:
                    v = views[self.view_name]

                    all_funcs = { "map": self.map_fun }
                    if self.reduce_fun:
                        all_funcs['reduce'] = self.reduce_fun
                
                    for func_type, func in all_funcs:
                        if func_type in v:
                            if v[func_type] != func:
                                self.sync(db)
                                break
                        else:
                            self.sync(db)
                            break
                else:
                    self.sync(db)
            except:
                self.sync(db)

        self.res = db.res.clone()
        uri = url.make_uri(
                db.res.uri, 
                *self.view_path.split('/'))
        self.res.uri = uri
        return ViewResults(self, wrapper=wrapper, **self.params)

    def _make_request(self):
        results, resp = self.res.get(**self.params)
        return results


def register_view(dbname, view_def):
    """ register a ViewDefintion instance 
    for db_name
        
    :param dbname: name of database
    :param view_def: ViewDefinition object
    """
    view_cache.add_view(dbname, view_def)

