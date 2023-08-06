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

"""Module to manage access to databases in couchdb"""


from mimetypes import guess_type

from simplecouchdb.client.utils import validate_dbname
from simplecouchdb.client.view import View, TempView, AllDocumentsView, view_cache, register_view, ViewDefinition
from simplecouchdb.resource import ResourceNotFound

class InvalidAttachment(Exception):
    """ raised when an attachment is invalid """

class Database(object):
    """ Object that abstract access to a CouchDB database
    A Database object could act as a Dict object.
    """

    def __init__(self, server, dbname):
        """Constructor for Database

        :param server: simplecouchdb.client.Server instance
        :param dbname: str, name of database on this server
        """

        if not hasattr(server, 'compact_db'):
            raise TypeError('%s is not a simplecouchdb.Server instance' % 
                            server.__class__.__name__)
                            
        self.dbname = validate_dbname(dbname)
        self.server = server
        self.res = server.res.clone()
        self.res.update_uri('/%s' % dbname)
        self._view = View(self)
        self._temp_view = TempView(self)
        self._all_documents_view = AllDocumentsView(self)

    def info(self):
        """
        Get infos of database
            
        :return: dict
        """
        data, resp = self.res.get()
        return data
        
    def doc_exist(self, docid):
        """Test if document exist in database

        :param docid: str, document id
        :return: boolean, True if document exist
        """

        try:
            data, resp = self.res.head(docid)
        except ResourceNotFound:
            return False
        return True
        
    def get(self, docid, default=None, rev=None):
        """Get document from database
        
        Args:
        :param docid: str, document id to retrieve default: 
        default result
        :param rev: if specified, allow you to retrieve
        a specifiec revision of document
        
        :return: dict, representation of CouchDB document as
         a dict.
        """

        try:
            if rev is not None:
                doc, resp = self.res.get(docid, rev=rev)
            else:
                doc, resp = self.res.get(docid)
        except ResourceNotFound:
            return default
        return doc
        
    def revisions(self, docid, with_doc=True):
        """ retrieve revisions of a doc
            
        :param docid: str, id of document
        :param with_doc: bool, if True return document
        dict with revisions as member, if false return 
        only revisions
        
        :return: dict: '_rev_infos' member if you have set with_doc
        to True :

        .. code-block:: python

                {
                    "_revs_info": [
                        {"rev": "123456", "status": "disk"},
                            {"rev": "234567", "status": "missing"},
                            {"rev": "345678", "status": "deleted"},
                    ]
                }
            
        If False, return current revision of the document, but with
        an additional field, _revs, the value being a list of 
        the available revision IDs. 
        """

        try:
            if with_doc:
                doc_with_revs, resp = self.res.get(docid, revs=True)
            else:
                doc_with_revs, resp = self.res.get(docid, revs_info=True)
        except ResourceNotFound:
            return None
        return doc_with_revs           
        
    def save(self, doc):
        """ Save one documents or multiple documents.

        :param doc: dict or list/tuple of dict.

        :return: dict or list of dict: dict or list are updated 
        with doc '_id' and '_rev' properties returned 
        by CouchDB server.

        """
        if doc is None:
            doc = {}
        if isinstance(doc, (list, tuple,)):
            results, resp = self.res.post('_bulk_docs',
                    data={ "docs": doc })

            docs = [d for d in doc]
            for idx, res in enumerate(results['new_revs']):
                docs[idx].update({ '_id': res['id'],
                    '_rev': res['rev']})
        else: 
            if '_id' in doc:
                res, resp = self.res.put(doc['_id'], data=doc)
            else:
                res, resp = self.res.post(data=doc)
            doc.update({ '_id': res['id'], '_rev': res['rev']})
        return doc
                
    def delete(self, doc_or_docs):
        """ delete a document or a list of document

        :param doc_or_docs: list or str: doment id or list
        of documents or list with _id and _rev, optionnaly 
        _deleted member set to true. See _bulk_docs document
        on couchdb wiki.
        
        :return: list of doc or dict like:
       
        .. code-block:: python

            {"ok":true,"rev":"2839830636"}
        """
        result = { 'ok': False }
        if isinstance(doc_or_docs, (list, tuple,)):
            docs = []
            for doc in doc_or_docs:
                doc.update({'_deleted': True})
                docs.append(doc)
            result, resp = self.res.post('_bulk_docs', data={
                "docs": docs
            })
            
        elif isinstance(doc_or_docs, dict) and '_id' in doc_or_docs:
            result, resp = self.res.delete(doc_or_docs['_id'], 
                    rev=doc_or_docs['_rev'])
        elif isinstance(doc_or_docs, basestring):
            data, resp = self.res.head(doc_or_docs)
            result, resp2 = self.res.delete(doc_or_docs, 
                    rev=resp['etag'].strip('"'))
        return result

    @property
    def documents(self):
        """ Get all documents in a database. It correspond
        to ``somedatabase/all_docs`` call 
        
        :return: `AllDocumentsView` instance.
        
        
        """
        return self._all_documents_view 
        
    def iterdocuments(self, **params):
        """ iter documents of a db 
        
        :param params: dict or strings, 
        """
        return self.documents.get(**params)

    @property
    def view(self):
        """ 
        See :ref:`view-ref` documentation

        :return: View instance. """
        return self._view

    @property
    def temp_view(self):
        """ 
        See :ref:`view-ref` documentation

        :return: TemporaryView instance """
        return self._temp_view

    def add_attachment(self, doc, content, name=None, content_type=None):
        """ Add attachement to a document.

        :param doc: dict, document object
        :param content: string or :obj:`File` object.
        :param name: name or attachment (file name).
        :param content_type: string, mimetype of attachment.
        If you don't set it, it will be autodetected.

        :return: bool, True if everything was ok.


        Example:

            >>> db = self.server.create_db('simplecouchdb_test')
            >>> doc = { 'string': 'test', 'number': 4 }
            >>> db.save(doc)
            >>> text_attachment = "un texte attaché"
            >>> db.add_attachment(doc, text_attachment, "test", "text/plain")
            True
            >>> db.get_attachment(doc, "test")
            u'un texte attaché'
            >>> db.delete_attachment(doc, 'test')
            >>> db.get_attachment(doc, 'test')
            None
            >>> self.server.delete_db('simplecouchdb_test')

        """

        if hasattr(content, 'read'):
            data = content.read()
        else:
            data = content

        if name is None:
            if hasattr('content', name):
                name = content.name
            else:
                raise InvalidAttachment('You should provid a valid attachment name')

        if content_type is None:
            content_type = ';'.join(filter(None, guess_type(name)))

        res, resp = self.res(doc['_id']).put(
                name,
                data=data,
                headers={'Content-Type': content_type },
                rev=doc['_rev']
        )

        if res['ok']:
            doc.update({ '_rev': res['rev']})
        return res['ok']

    def delete_attachment(self, doc, name):
        """ delete attachement of documen

        :param doc: dict, document object in python
        :param name: name of attachement
    
        :return: dict, withm member ok setto True if delete was ok.
        """

        result, resp = self.res(doc['_id']).delete(name, rev=doc['_rev'])

    def get_attachment(self, id_or_doc, name, default=None):
        """ get attachment in document
        
        :param id_or_doc: str or dict, doc id or document dict
        :param name: name of attachment default: default result

        :return: str, attachment
        """

        if isinstance(id_or_doc, basestring):
            docid = id_or_doc
        else:
            docid = id_or_doc['_id']
        
        try:
            data, resp = self.res(docid).get(name)
        except ResourceNotFound:
            return default
        return data

    def sync(self, verbose_level=None):
        """ sync all views definition stored
        in cache.
        
        see :ref:`view-ref` for more info.
        """
        views = view_cache.get_views(self.dbname)
        if views is not None:
            for view_def in views.itervalues():
                view_def.sync(self, verbose_level)

    def add_viewdef(self, view_def):
        """ add a view defintion to db """
        register_view(self.dbname, view_def)

    def add_view(self, design_name, view_name, map_fun,
            reduce_fun=None, language='javascript', 
            **params):
        """ create a view definition and add it to db """
        view_def = ViewDefiniton(design_name, view_name,
                map_fun, reduce_fun=reduce_fun, 
                language=language, **params)
        register_view(self.db_name, view_def)
        
    def __len__(self):
        return self.info()['doc_count'] 
        
    def __contains__(self, docid):
        return self.doc_exist(docid)
        
    def __getitem__(self, id):
        return self.get(id)
        
    def __setitem__(self, docid, doc):
        res, resp = self.res.put(docid, data=doc)
        doc.update({ '_id': res['id'], '_rev': res['rev']})
        
    def __delitem__(self, docid):
       data, resp = self.res.head(docid)
       result, resp2 = self.res.delete(docid, 
               rev=resp['etag'].strip('"'))

    def __iter__(self):
        return self.iterdocuments()
        
    def __nonzero__(self):
        return (len(self) > 0)

