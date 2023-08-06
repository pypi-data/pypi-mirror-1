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

""" some utilities to manage urls """

from urlparse import urlparse
from urllib import quote, urlencode, unquote_plus

DEFAULT_PROTOCOL = "http"
DEFAULT_PORT = 5984

class InvalidUrl(Exception):
    pass

def make_uri(base, *path, **query):
    """Assemble a uri based on a base, any number of path segments, and query
    string parameters.

    >>> make_uri('http://example.org/', '/_all_dbs')
    'http://example.org/_all_dbs'
    """

    if base and base.endswith("/"):
        base = base[:-1]
    retval = [base]

    # build the path
    path = '/'.join([''] +
                    [unicode_quote(s.strip('/')) for s in path 
                    if s is not None])

    if path:
        retval.append(path)

    params = []
    for k, v in query.items():
        if type(v) in (list, tuple):
            params.extend([(name, i) for i in v if i is not None])
        elif v is not None:
            params.append((k,v))
    if params:
        retval.extend(['?', unicode_urlencode(params)])
    return ''.join(retval)

def unicode_quote(string, safe=''):
    """Like urllib.quote but return unicode """
    if isinstance(string, unicode):
        string = string.encode('utf-8')
    elif not isinstance(string, str):
        s = str(s)
    return quote(string, safe)

def unicode_urlencode(data):
    """ like urllib.urlencode but return unicode """
    if isinstance(data, dict):
        data = data.items()
    params = []
    for name, value in data:
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        params.append((name, value))
    return urlencode(params)
