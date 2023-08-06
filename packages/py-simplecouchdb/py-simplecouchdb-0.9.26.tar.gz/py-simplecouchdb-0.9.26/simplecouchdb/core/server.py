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

"""module to access and manage a CouchDB host. 
"""

from simplecouchdb.core.database import Database
from simplecouchdb.core.utils import validate_dbname
from simplecouchdb.resource import CouchdbResource
from simplecouchdb.schema.session import DBSession

__all__ = ['Server']

class Server(object):
    """ Server object that allow you to acces and manage
    a CouchDB host.
    A Server object could be used like any `dict` object.
    """

    def __init__(self, uri='http://127.0.0.1:5984', transport=None):
        """Constructor for Server object.

        Args: 
            uri: uri of CouchDb host
            http: an http instance from httplib2. Could be used
                to manage authentification to your server or
                proxy.
        """
        if not uri or uri is None:
            raise ValueError("Server uri is missing")

        self.uri = uri
        self.res = CouchdbResource(uri, transport=transport)
        
    def info(self):
        """ info of server

        :return: dict
        """
        result = self.res.get()
        return result
        
    def all_dbs(self):
        """ get list of databases in CouchDb host """
        result = self.res.get('/_all_dbs')
        return result
        
    def create_db(self, dbname):
        """ Create a database on CouchDb host

        :param dname: str, name of db

        :return: Database instance if it's ok
        """
        res = self.res.put('/%s/' % validate_dbname(dbname))
        if res['ok']:
            return Database(self, dbname)
        return res['ok']

    def delete_db(self, dbname):
        """ delete a database in CouchDB host

        :param dbname: str, name of database
        """
        result = self.res.delete('/%s/' % validate_dbname(dbname))
        return result
        
    def get_db(self, dbname):
        """ get database

        :param dbname: str, name of database

        :return: Database instance if dbname in server, None 
        if it don't exist.
        """
            
        if dbname in self:
            return Database(self, dbname)
        return None
        
    def db_exist(self, dbname):
        """ test if database exist in CouchDB host.

        :param dbname: str, name of database

        :return: bool, True if it exist
        """
        
        if dbname in self.all_dbs():
            return True
        return False

    def create_session(self, dbname, scoped_func=None):
        """ Provide a thread-local management of database

        :param dbname: str, name of database
        :param scopefunc: optional, 

        :return: DBSession object

        Usage::
        
        To create a initiate a db session

        .. code-block:: python 
            
            from simplecouchdb import Server
            s = Server()
            s.create_db('mydb')
            dbsession = s.create_session('mydb')

        
        """
        if not dbname in self:
            raise ValueError("%s don't exist at %s" % (dbname, 
                self.uri))
        return DBSession(self, dbname, scoped_func)
        
    def compact_db(self, dbname):
        """ compact database """
        if dbname in self:
            res = self.res.post('/%s/_compact' % dbname)
            return res['ok']
        return False
        
    def replicate(self, source, target):
        """ replicate database. source and target are uri """
        res = self.res.get('/_replicate', source=source, target=target)
        return res['ok']
        
    def __contains__(self, dbname):
        return self.db_exist(dbname)
        
    def __iter__(self):
        all_dbs = self.all_dbs()
        for db in all_dbs:
            yield Database(self, db)
            
    def __len__(self):
        all_dbs = self.all_dbs()
        return len(all_dbs)
        
    def __nonzero__(self):
        if len(self) > 0:
            return True
        return False
            
    def __delitem__(self, dbname):
        self.delete_db(dbname)

    def __getitem__(self, dbname):
        db = self.get_db(dbname)
        if db is None:
            raise KeyError("%s not in %s" % (dbname, self.uri))
        return self.get_db(dbname)
