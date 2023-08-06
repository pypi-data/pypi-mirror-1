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
from calendar import timegm
import datetime
import decimal
import time
import re

try:
    import simplejson
except ImportError:
    try:
        import json
    except ImportError:
        print >> sys.stderr, "Simplejson module is required to use simplecouchdb on python < 2.6."
        raise


__all__ = ['SimplecouchdbJSONEncoder']

class SimplecouchdbJSONEncoder(simplejson.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types. 
    """
    
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return  o.replace(microsecond=0).isoformat() + 'Z'
        
        if isinstance(o, datetime.date):
            return o.isoformat()
        
        if isinstance(o, datetime.time):
            
            return o.replace(microsecond=0).isoformat()
        
        if isinstance(o, decimal.Decimal):
            return  unicode(o)
        
        return super(SimplecouchdbJSONEncoder, self).default(o)
