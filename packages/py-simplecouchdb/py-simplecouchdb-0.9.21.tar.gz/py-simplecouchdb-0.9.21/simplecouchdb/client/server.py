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

"""module to access and manage a CouchDB host. 
"""

from simplecouchdb.client.database import Database
from simplecouchdb.client.utils import validate_dbname
from simplecouchdb.resource import CouchdbResource
from simplecouchdb.url import make_uri


class Server(object):
    """ Server object that allow you to acces and manage
    a CouchDB host.
    A Server object could be used like any `dict` object.
    """

    def __init__(self, uri='http://localhost:5984', http=None, 
                 headers=None):
        """Constructor for Server object.

        Args: 
            uri: uri of CouchDb host
            http: an http instance from httplib2. Could be used
                to manage authentification to your server or
                proxy.
            headers: dict, optionnal HTTP headers that you need 
                to pass
        """

        self.res = CouchdbResource(uri, http=http, headers=headers)
        
    def info(self):
        """ info of server

        :return: dict
        """
        result, resp = self.res.get()
        return result
        
    def all_dbs(self):
        """ get list of databases in CouchDb host """
        result, resp = self.res.get('/_all_dbs')
        return result
        
    def create_db(self, dbname):
        """ Create a database on CouchDb host

        :param dname: str, name of db

        :return: Database instance if it's ok
        """
        res, resp = self.res.put('/%s/' % validate_dbname(dbname))
        if res['ok']:
            return Database(self, dbname)
        return res['ok']

    def delete_db(self, dbname):
        """ delete a database in CouchDB host

        :param dbname: str, name of database
        """
        result, resp = self.res.delete('/%s/' % validate_dbname(dbname))
        return result
        
    def get_db(self, dbname):
        """ get database

        :param dbname: str, name of database

        :return: Database instance if dbnam in server, None 
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
        
    def compact_db(self, dbname):
        """ compact database """
        if dbname in self:
            res, resp = self.res.post('/%s/_compact' % dbname)
            return res['ok']
        return False
        
    def replicate(self, source, target):
        """ replicate database. source and target are uri """
        res, resp = self.res.get('/_replicate', source=source, target=target)
        return res['ok']
        
    def __contains__(self, dbname):
        return self.db_exist(dbname)
        
    def __iter__(self):
        all_dbs = self.all_dbs()
        for db in all_dbs.iteritems():
            yield Database(db)
            
    def __len__(self):
        all_dbs = self.all_dbs()
        return len(all_dbs)
        
    def __nonzero__(self):
        if len(self) > 0:
            return True
        return False
            
    def __delitem__(self, dbname):
        self.delete(dbname)

    def __getitem__(self, dbname):
        return self.get_db(dbname)
