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
__author__ = 'benoitc@e-engura.com (Benoît Chesneau)'

import unittest

from restclient import ResourceNotFound

from simplecouchdb.resource import CouchdbResource
from simplecouchdb.core import Server, Database
from simplecouchdb.core import document
from simplecouchdb.core.design import Design
from simplecouchdb.core.view import View

class ClientServerTestCase(unittest.TestCase):
    def setUp(self):
        self.couchdb = CouchdbResource()
        self.server = Server()

    def testGetInfo(self):
        info = self.server.info()
        self.assert_(info.has_key('version'))
        
    def testCreateDb(self):
        res = self.server.create_db('simplecouchdb_test')
        self.assert_(isinstance(res, Database) == True)
        all_dbs = self.server.all_dbs()
        self.assert_('simplecouchdb_test' in all_dbs)
        self.server.delete_db('simplecouchdb_test')
        
    def testBadResourceClassType(self):
        self.assertRaises(TypeError, Server, resource_class=None)
        
    def testServerLen(self):
        res = self.server.create_db('simplecouchdb_test')
        self.assert_(len(self.server) >= 1)
        self.assert_(bool(self.server))
        self.server.delete_db('simplecouchdb_test')
        
    def testServerContain(self):
        res = self.server.create_db('simplecouchdb_test')
        self.assert_('simplecouchdb_test' in self.server)
        self.server.delete_db('simplecouchdb_test')
        
        
class ClientDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.couchdb = CouchdbResource()
        self.server = Server()

    def tearDown(self):
        try:
            self.server.delete_db('simplecouchdb_test')
        except:
            pass
        
    def testCreateDatabase(self):
        db = self.server.create_db('simplecouchdb_test')
        self.assert_(isinstance(db, Database) == True)
        info = db.info()
        self.assert_(info['db_name'] == 'simplecouchdb_test')
        self.server.delete_db('simplecouchdb_test')

    def testCreateEmptyDoc(self):
        db = self.server.create_db('simplecouchdb_test')
        doc = {}
        db.save(doc)
        self.server.delete_db('simplecouchdb_test')
        self.assert_('_id' in doc)
        
        
    def testCreateDoc(self):
        db = self.server.create_db('simplecouchdb_test')
        # create doc without id
        doc = { 'string': 'test', 'number': 4 }
        db.save(doc)
        self.assert_(db.doc_exist(doc['_id']))
        # create doc with id
        doc1 = { '_id': 'test', 'string': 'test', 'number': 4 }
        db.save(doc1)
        self.assert_(db.doc_exist('test'))
        doc2 = { 'string': 'test', 'number': 4 }
        db['test2'] = doc2
        self.assert_(db.doc_exist('test2'))
        self.server.delete_db('simplecouchdb_test')

            
    def testUpdateDoc(self):
        db = self.server.create_db('simplecouchdb_test')
        doc = { 'string': 'test', 'number': 4 }
        db.save(doc)
        doc.update({'number': 6})
        db.save(doc)
        doc = db.get(doc['_id'])
        self.assert_(doc['number'] == 6)
        self.server.delete_db('simplecouchdb_test')
        
    def testDbLen(self):
        db = self.server.create_db('simplecouchdb_test')
        doc1 = { 'string': 'test', 'number': 4 }
        db.save(doc1)
        doc2 = { 'string': 'test2', 'number': 4 }
        db.save(doc2)

        self.assert_(len(db) == 2)
        self.server.delete_db('simplecouchdb_test')
        
    def testDeleteDoc(self):
        db = self.server.create_db('simplecouchdb_test')
        doc = { 'string': 'test', 'number': 4 }
        db.save(doc)
        docid=doc['_id']
        db.delete(docid)
        self.assert_(db.doc_exist(docid) == False)
        doc = { 'string': 'test', 'number': 4 }
        db.save(doc)
        docid=doc['_id']
        db.delete(doc)
        self.assert_(db.doc_exist(docid) == False)
        self.server.delete_db('simplecouchdb_test')

    def testStatus404(self):
        db = self.server.create_db('simplecouchdb_test')

        def no_doc():
            doc = db.get('t')

        self.assertRaises(ResourceNotFound, no_doc)
        
        self.server.delete_db('simplecouchdb_test')
        
    def testAttachments(self):
        db = self.server.create_db('simplecouchdb_test')
        doc = { 'string': 'test', 'number': 4 }
        db.save(doc)        
        text_attachment = u"un texte attaché"
        old_rev = doc['_rev']
        db.put_attachment(doc, text_attachment, "test", "text/plain")
        self.assert_(old_rev != doc['_rev'])
        fetch_attachment = db.fetch_attachment(doc, "test")
        self.assert_(text_attachment == fetch_attachment)
        self.server.delete_db('simplecouchdb_test')
   
    def testEmptyAttachment(self):
        db = self.server.create_db('simplecouchdb_test')
        doc = {}
        db.save(doc)
        db.put_attachment(doc, "", name="test")
        doc1 = db.get(doc['_id'])
        attachment = doc1['_attachments']['test']
        self.assertEqual(0, attachment['length'])
        self.server.delete_db('simplecouchdb_test')

    def testDeleteAttachment(self):
        db = self.server.create_db('simplecouchdb_test')
        doc = { 'string': 'test', 'number': 4 }
        db.save(doc)
        
        text_attachment = "un texte attaché"
        old_rev = doc['_rev']
        db.put_attachment(doc, text_attachment, "test", "text/plain")
        db.delete_attachment(doc, 'test')
        attachment = db.fetch_attachment(doc, 'test')
        self.assert_(attachment == None)
        self.server.delete_db('simplecouchdb_test')

    def testSaveMultipleDocs(self):
        db = self.server.create_db('simplecouchdb_test')
        docs = [
                { 'string': 'test', 'number': 4 },
                { 'string': 'test', 'number': 5 },
                { 'string': 'test', 'number': 4 },
                { 'string': 'test', 'number': 6 }
        ]
        db.save(docs)
        self.assert_(len(db) == 4)
        self.assert_('_id' in docs[0])
        self.assert_('_rev' in docs[0])
        doc = db.get(docs[2]['_id'])
        self.assert_(doc['number'] == 4)
        docs[3]['number'] = 6
        old_rev = docs[3]['_rev']
        db.save(docs)
        self.assert_(docs[3]['_rev'] != old_rev)
        doc = db.get(docs[3]['_id'])
        self.assert_(doc['number'] == 6)
        docs = [
                { '_id': 'test', 'string': 'test', 'number': 4 },
                { 'string': 'test', 'number': 5 },
                { '_id': 'test2', 'string': 'test', 'number': 42 },
                { 'string': 'test', 'number': 6 }
        ]
        db.save(docs)
        doc = db.get('test2')
        self.assert_(doc['number'] == 42) 
        self.server.delete_db('simplecouchdb_test')
   
    def testDeleteMultipleDocs(self):
        db = self.server.create_db('simplecouchdb_test')
        docs = [
                { 'string': 'test', 'number': 4 },
                { 'string': 'test', 'number': 5 },
                { 'string': 'test', 'number': 4 },
                { 'string': 'test', 'number': 6 }
        ]
        db.save(docs)
        self.assert_(len(db) == 4)
        db.delete(docs)
        self.assert_(len(db) == 0)
        self.assert_(db.info()['doc_del_count'] == 4)

        self.server.delete_db('simplecouchdb_test')


    def testCoreDocument(self):
        db = self.server.create_db('simplecouchdb_test')
        
        d = { 's': 'test' }
        
        db.save(d)
        self.assert_(isinstance(d, document.Document) == False)
        self.assert_(hasattr(d, 'id') == False)
       
        d2 = db.get(d['_id'])
        self.assert_(hasattr(d2, 'id') == True)

        d3 = document.Document({ 's': 'test' }, db)

        self.assert_(d3.new_document == True)

        d3.save()
        self.assert_(d3.rev is not None)

        old_rev = d3.rev
        db.save(d3)
        self.assert_(isinstance(d3, document.Document) == True)
        self.assert_(d3.rev is not None)
        self.assert_(d3.rev != old_rev)

        d4 = document.Document({'_id': 'test', 's': 'test'}, db)
        d4.save()
        self.assert_(d4.id == "test")
        self.assert_(d4.new_document == False)
        
        self.server.delete_db('simplecouchdb_test')

class ClientViewTestCase(unittest.TestCase):
    def setUp(self):
        self.couchdb = CouchdbResource()
        self.server = Server()

    def tearDown(self):
        try:
            self.server.delete_db('simplecouchdb_test')
        except:
            pass

        try:
            self.server.delete_db('simplecouchdb_test2')
        except:
            pass

    def testView(self):
        db = self.server.create_db('simplecouchdb_test')
        # save 2 docs 
        doc1 = { '_id': 'test', 'string': 'test', 'number': 4, 
                'docType': 'test' }
        db.save(doc1)
        doc2 = { '_id': 'test2', 'string': 'test', 'number': 2,
                    'docType': 'test'}
        db.save(doc2)

        design_doc = {
            '_id': '_design/test',
            'language': 'javascript',
            'views': {
                'all': {
                    "map": """function(doc) { if (doc.docType == "test") { emit(doc._id, doc);
}}"""
                }
            }
        }
        db.save(design_doc)
        
        doc3 = db.get('_design/test')
        self.assert_(doc3 is not None) 
        results = db.view('test/all')
        self.assert_(len(results) == 2)
        self.server.delete_db('simplecouchdb_test')

    def testCount(self):
        db = self.server.create_db('simplecouchdb_test')
        # save 2 docs 
        doc1 = { '_id': 'test', 'string': 'test', 'number': 4, 
                'docType': 'test' }
        db.save(doc1)
        doc2 = { '_id': 'test2', 'string': 'test', 'number': 2,
                    'docType': 'test'}
        db.save(doc2)

        design_doc = {
            '_id': '_design/test',
            'language': 'javascript',
            'views': {
                'all': {
                    "map": """function(doc) { if (doc.docType == "test") { emit(doc._id, doc); }}"""
                }
            }
        }
        db.save(design_doc)
        count = db.view('/test/all').count()
        self.assert_(count == 2)
        self.server.delete_db('simplecouchdb_test')

    def testTemporaryView(self):
        db = self.server.create_db('simplecouchdb_test')
        # save 2 docs 
        doc1 = { '_id': 'test', 'string': 'test', 'number': 4, 
                'docType': 'test' }
        db.save(doc1)
        doc2 = { '_id': 'test2', 'string': 'test', 'number': 2,
                    'docType': 'test'}
        db.save(doc2)

        design_doc = {
            "map": """function(doc) { if (doc.docType == "test") { emit(doc._id, doc);
}}"""
        }
         
        results = db.temp_view(design_doc)
        self.assert_(len(results) == 2)
        self.server.delete_db('simplecouchdb_test')


    def testView2(self):
        db = self.server.create_db('simplecouchdb_test')
        # save 2 docs 
        doc1 = { '_id': 'test1', 'string': 'test', 'number': 4, 
                'docType': 'test' }
        db.save(doc1)
        doc2 = { '_id': 'test2', 'string': 'test', 'number': 2,
                    'docType': 'test'}
        db.save(doc2)
        doc3 = { '_id': 'test3', 'string': 'test', 'number': 2,
                    'docType': 'test2'}
        db.save(doc3)
        design_doc = {
            '_id': '_design/test',
            'language': 'javascript',
            'views': {
                'with_test': {
                    "map": """function(doc) { if (doc.docType == "test") { emit(doc._id, doc);
}}"""
                },
                'with_test2': {
                    "map": """function(doc) { if (doc.docType == "test2") { emit(doc._id, doc);
}}"""
                }   

            }
        }
        db.save(design_doc)

        # yo view is callable !
        results = db.view('test/with_test')
        self.assert_(len(results) == 2)
        results = db.view('test/with_test2')
        self.assert_(len(results) == 1)
        self.server.delete_db('simplecouchdb_test')

    def testViewWithParams(self):
        db = self.server.create_db('simplecouchdb_test')
        # save 2 docs 
        doc1 = { '_id': 'test1', 'string': 'test', 'number': 4, 
                'docType': 'test', 'date': '20081107' }
        db.save(doc1)
        doc2 = { '_id': 'test2', 'string': 'test', 'number': 2,
                'docType': 'test', 'date': '20081107'}
        db.save(doc2)
        doc3 = { '_id': 'test3', 'string': 'machin', 'number': 2,
                    'docType': 'test', 'date': '20081007'}
        db.save(doc3)
        doc4 = { '_id': 'test4', 'string': 'test2', 'number': 2,
                'docType': 'test', 'date': '20081108'}
        db.save(doc4)
        doc5 = { '_id': 'test5', 'string': 'test2', 'number': 2,
                'docType': 'test', 'date': '20081109'}
        db.save(doc5)
        doc6 = { '_id': 'test6', 'string': 'test2', 'number': 2,
                'docType': 'test', 'date': '20081109'}
        db.save(doc6)

        design_doc = {
            '_id': '_design/test',
            'language': 'javascript',
            'views': {
                'test1': {
                    "map": """function(doc) { if (doc.docType == "test")
                    { emit(doc.string, doc);
}}"""
                },
                'test2': {
                    "map": """function(doc) { if (doc.docType == "test") { emit(doc.date, doc);
}}"""
                },
                'test3': {
                    "map": """function(doc) { if (doc.docType == "test")
                    { emit(doc.string, doc);
}}"""
                }


            }
        }
        db.save(design_doc)

        results = db.view('test/test1')
        self.assert_(len(results) == 6)

        results = db.view('test/test3', key="test")
        self.assert_(len(results) == 2)

       

        results = db.view('test/test3', key="test2")
        self.assert_(len(results) == 3)

        results = db.view('test/test2', startkey="200811")
        self.assert_(len(results) == 5)

        results = db.view('test/test2', startkey="20081107",
                endkey="20081108")
        self.assert_(len(results) == 3)

        self.server.delete_db('simplecouchdb_test')


    def testDesign(self):
        
        db = self.server.create_db('simplecouchdb_test')
        d = Design()
        d.database = db

        v = d.view_by('key1', 'key2')
        self.assert_(isinstance(v, View) == True)
       

        o = {'map': 'function(doc) {\n    if (doc.key1 && doc.key2) {\n        emit([doc.key1, doc.key2], doc);\n    }\n}'}

        self.assert_(d['views']['by_key1_and_key2'] == o)

        d.name = 'view1'
        self.assert_(d['_id'] == '_design/view1')


        d.name = '_design/view2'
        self.assert_(d['_id'] == '_design/view2')
        self.assert_(d.name == 'view2')

        self.server.delete_db('simplecouchdb_test')

    def testDesign2(self):
        db = self.server.create_db('simplecouchdb_test')

        d = Design()
        d.database = db

        v = d.view_by('key1', 'key2', 
                { 'map': "function(doc) { emit(null, doc); }", "method_name":"n1"})
       
        self.assert_('n1' in d['views'])

        self.assert_(d['views']['n1'] == {'map': 'function(doc) { emit(null, doc); }'})

        self.server.delete_db('simplecouchdb_test')

        

if __name__ == '__main__':
    unittest.main()

