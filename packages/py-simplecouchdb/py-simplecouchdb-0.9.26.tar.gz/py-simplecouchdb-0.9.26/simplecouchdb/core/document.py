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


class Document(dict):

    def __init__(self, d=None, db=None):
        self._db = db or None
        dict.__init__(self, d or {})

    def get_id(self):
        return self.get('_id', None)

    def set_id(self, docid):
        if not isinstance(docid, basestring):
            raise TypeError('doc id should be a string')
        self['_id'] = docid
    id = property(get_id, set_id)

    @property
    def rev(self):
        return self.get('_rev')

    def set_database(self, db):
        self._db = db

    def get_database(self):
        if not hasattr(self, '_db'):
            return None
        return self._db
    database = property(get_database, set_database)
 
    new_document = property(lambda self: self.get('_rev') is None) 
    
    def save(self):
        if not hasattr(self, '_db'):
            raise TypeError("doc database required to save document")
        self._db.save(self)

    def put_attachment(self, content, name=None,
        content_type=None, content_length=None):
        """ Add attachement to a document.
 
        :param content: string or :obj:`File` object.
        :param name: name or attachment (file name).
        :param content_type: string, mimetype of attachment.
        If you don't set it, it will be autodetected.
        :param content_lenght: int, size of attachment.

        :return: bool, True if everything was ok.
        """
        if not hasattr(self, '_db'):
            raise TypeError("doc database required to save document")
        return self._db.put_attachment(self, content, name=name,
            content_type=content_type, content_length=content_length)

    def delete_attachment(self, name):
        """ delete attachement of documen
        
        :param name: name of attachement
    
        :return: dict, withm member ok setto True if delete was ok.
        """
        if not hasattr(self, '_db'):
            raise TypeError("doc database required to save document")
        return self._db.delete_attachment(self, name)

    def fetch_attachment(self, name):
        """ get attachment in document
        
        :param name: name of attachment default: default result

        :return: str or unicode, attachment
        """
        if not hasattr(self, '_db'):
            raise TypeError("doc database required to save document")
        return self._db.fetch_attachment(self, name)


    def has_changed(self):
        if self.new_document:
            return True
        else:
            if not hasattr(self, '_db'):
                raise TypeError("doc database required.")
            data = self._db.res.head(self.id)
            resp = self._db.res.get_response()
            if self.rev != resp['etag'].strip('"'):
                return True
        return False
