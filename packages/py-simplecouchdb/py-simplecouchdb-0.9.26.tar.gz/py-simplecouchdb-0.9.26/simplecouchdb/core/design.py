# -*- coding: utf-8 -*-
#
# Copyright (c) 2008-2009 Benoit Chesneau <benoitc@e-engura.com> 
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
# Some code taken from ruby couchrest under the following license:
# Copyright 2008 J. Chris Anderson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import uuid

from simplecouchdb.resource import ResourceConflict
from simplecouchdb.core import document

__all__ = ['Design']

class Design(document.Document):
    """ design is a Design document object. 
    It allow you to create an save a  document it is inherited
    from :class::`simplecouchdb.core.document.Document`

    simple usage :

    .. code-block:: python
        
        from simplecouchdb.core.design import Design
        d = Design()
        myview = d.view_by('key1', 'key2')
        for row in view_results:
            ....

    """

    def fetch_view(self, view_name, wrapper=None, **params):
        if self._db is None:
            raise TypeError("database required to fetch view")
        
        view_path = "%s/%s" % (self.name, view_name)
        return self._db.view(view_path, wrapper=wrapper, **params)

    def view_by(self, *args, **kwargs):
        if not 'views' in self:
            self['views'] = {}

        args = args or ()

        options = {}
        args = list(args)
        if args and isinstance(args[len(args)-1], dict):
            options = args.pop()
        if kwargs:
            options.update(kwargs)

        if 'method_name' in options:
            method_name = options.pop('method_name')
        elif args:
            method_name = "by_%s" % ('_and_'.join(args))
        else:
            raise TypeError('method_name or key name'+ 
                    'is missing in kwargs')

        _wrapper = options.pop('wrapper', None)

        view = {}
        if 'map' in options:
            view['map'] = options.pop('map')
            if 'reduce' in options:
                view['reduce'] = options.pop('reduce')

            for k in ('guards', 'doctype'):
                try:
                    del options[k]
                except:
                    continue
        elif args:
            doc_keys = ['doc.%s' % key for key in args]
            if len(doc_keys) == 1:
                emit_keys = doc_keys[0]
            else:
                emit_keys = "[%s]" % ', '.join(doc_keys)
            guards = options.pop('guards', [])
            guards.extend(doc_keys)
            map_func = """function(doc) {
    if (%(guards)s) {
        emit(%(key_emit)s, doc);
    }
}""" % { 'guards': " && ".join(guards), 'key_emit': emit_keys }

            view['map'] = map_func

        else:
            for k in ('guards', 'doctype'):
                try:
                    del options[k]
                except:
                    continue

            return self.fetch_view(method_name, wrapper=_wrapper, **options)

        if method_name in self['views']:
            if self['views'][method_name] != view:
                self['views'][method_name] = view
                self.save()
        else:
            self['views'][method_name] = view
            self.save()

        return self.fetch_view(method_name, wrapper=_wrapper, **options)

    ##################################
    # Functions specific to design   #
    ##################################
            
    def get_name(self):
        if not '_id' in self:
            return None
        return self['_id'].replace('_design/', '')

    def set_name(self, name):
        if name.startswith('/'):
            name = name[1:]
        if not name.startswith('_design/'):
            name = "_design/%s" % name
        if not self.new_document and name != self.id:
            del self['_rev']
        self['_id'] = name
    
    name = property(get_name, set_name)

    def has_view(self, view):
        if 'views' in self:
            return self['views'].get(view)
        return None

    def save(self, force_update=False):
        if self._db is None:
            raise TypeError("doc database required to save document")

        if not '_id' in self:
            self['_id'] = '_design/%s' % uuid.uuid4().hex
                    
        try:
            self._db.save(self)
        except ResourceConflict:
            current = self._db.get(self.id)
            if force_update or not 'views' in current:
                self['_rev'] = current['_rev']
                self._db.save(self)
            else:
                should_save = False
                for method_name, view in self['views'].iteritems():
                    if current['views'].get('method_name') != view:
                        should_save = True
                        break
                if should_save:
                    self['_rev'] = current['_rev']
                    self._db.save(self)

