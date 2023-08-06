# -*- coding: utf-8 -
# Copyright (c) 2008, 2009, Benoît Chesneau <benoitc@e-engura.com>.
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


""" 
simplecouchdb.resource
~~~~~~~~~~~~~~~~~~~~~~

This module provide a common interface for all CouchDB request. This
module make HTTP request using :mod:`httplib2` module.

Example: 
    
    >>> resource = CouchdbResource()
    >>> info = resource.get()
    >>> info['couchdb']
    u'Welcome'

"""

import httplib2
import socket
# First we try to use simplejson if installed
# then json from python 2.6
try:
    import simplejson as json
except ImportError:
    import json
    
from simplecouchdb import __version__


from simplecouchdb.url import make_uri

USER_AGENT = 'py-simplecouchdb/%s' % __version__


class ResourceNotFound(Exception):
    """ Exception raised when a resource is not found """

class ResourceConflict(Exception):
    """ Exception raised when there is conflict while updating"""

class RequestFailed(Exception):
    """ Exception raised when request failed """

class PreconditionFailed(Exception):
    """ Exception raised when 412 HTTP error is received in response
    to a request """


class CouchdbResource(object):

    debug = False

    def __init__(self, uri="http://127.0.0.1:5984", http=None, 
            headers=None):
        """Constructor for a `CouchdbResource` object.

        CouchdbResource represent an HTTP resource to CouchDB.

        :param uri: str, full uri to the server.
        :param http: an http instance from httplib2. Could be used
                to manage authentification to your server or
                proxy.
        :param headers: dict, optionnal HTTP headers that you need 
                to pass
        """     

        self.uri = uri
        if http is None:
            http = httplib2.Http()
            http.force_exception_to_status_code = False
        self.http = http
        self.headers = headers or {}
        
    def clone(self):
        """if you want to add a path to resource uri, you can do:
        
"""
        obj = self.__class__(self.uri, http=self.http, 
                headers=self.headers)
        return obj
   
    def __call__(self, path):
        """if you want to add a path to resource uri, you can do:
        
            Resource("/path").request("GET")"""

        return type(self)(make_uri(self.uri, path), http=self.http, 
               headers=self.headers)
 
    def request(self, method, path=None, data=None, headers=None, **params):
        """ Perform HTTP call to the couchdb server and manage 
        JSON conversions, support GET, POST, PUT and DELETE.
        
        Usage example, get infos of a couchdb server on 
        http://127.0.0.1:5984 :

        .. code-block:: python

            import simplecouchdb.CouchdbResource
            resource = simplecouchdb.CouchdbResource()
            infos = resource.request('GET'))

        :param method: str, the HTTP action to be performed: 
            'GET', 'HEAD', 'POST', 'PUT', or 'DELETE'
        :param path: str or list, path to add to the uri
        :param data: str or string or any object that could be
            converted to JSON.
        :param headers: dict, optionnal headers that will
            be added to HTTP request.
        :param params: Optionnal parameterss added to the request. 
        Parameterss are for example the parameters for a view. See 
        `CouchDB View API reference 
        <http://wiki.apache.org/couchdb/HTTP_view_API>`_ for example.
        
        :return: tuple (data, resp), where resp is an `httplib2.Response` object and data a python object (often a dict).
        """
        
        headers = headers or {}
        headers.setdefault('Accept', 'application/json')
        headers.setdefault('User-Agent', USER_AGENT)
        
        body = None
        if data is not None:
            if not isinstance(data, basestring):
                body = json.dumps(data, ensure_ascii=False).encode('utf-8')
                headers.setdefault('Content-Type', 'application/json')
            else:
                body = data
                
            if method in ['POST', 'PUT']:
                headers.setdefault('Content-Length', str(len(body))) 

        params = self.encode_params(params)
        
        def _make_request(retry=1):
            try:
                return self.http.request(make_uri(self.uri, path, **params), method, body=body, headers=headers)
            except socket.error, e:
                if retry > 0 and e.args[0] == 54: # reset by peer
                    return _make_request(retry - 1)
                raise RequestFailed("Error happened while connecting to")   
        resp, resp_data = _make_request()

        status_code = int(resp.status)
        if resp_data and resp.get('content-type') == 'application/json':
            try:
                resp_data = json.loads(resp_data)
            except:
                pass
        
        if status_code >= 400:
            if type(resp_data) is dict:
                error = (resp_data.get('error'), resp_data.get('reason'))
            else:
                error = resp_data
                
            if status_code == 404:
                raise ResourceNotFound(error)
            elif status_code == 409:
                raise ResourceConflict(error)
            elif status_code == 412:
                raise PreconditionFailed(error)
            else:
                raise RequestFailed((status_code, error))
                
        return resp_data, resp

    def encode_params(self, params):
        _params = {}
        if params:
            for name, value in params.items():
                if name in ('key', 'startkey', 'endkey') \
                        or not isinstance(value, basestring):
                    value = json.dumps(value, allow_nan=False,
                            ensure_ascii=False)
                _params[name] = value
        return _params
        
    def update_uri(self, path):
        """
        to set a new uri absolute path
        """
        self.uri = make_uri(self.uri, path)
        

    def head(self, path=None, headers=None, **params):
        return self.request('HEAD', path, headers=headers, **params)

    def get(self, path=None, headers=None, **params):
        return self.request('GET', path, headers=headers, **params)

    def post(self, path=None, data=None, headers=None, **params):
        return self.request('POST', path, data=data, headers=headers, **params)

    def put(self, path=None, data=None, headers=None, **params):
        return self.request('PUT', path, data=data, headers=headers, **params)

    def delete(self, path=None, headers=None, **params):
        return self.request('DELETE', path, headers=headers, **params)


