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



class View(object):

    def __init__(self, db, view_path, wrapper=None, **params):
        self._db = db
        self.view_path = view_path
        self._wrapper = wrapper
        self.params = params
        self._result_cache = None
        self._total_rows = None
        self._offset = 0

    def results_iterator(self):
        self._fetch_if_needed()
        rows = self._result_cache.get('rows')
        if not rows:
            yield {}
        else:
            for row in rows:
                if self._wrapper:
                    yield self._wrapper(row)
                else:
                    yield row

    def results(self):
        return list(self)

    def count(self):
        self._fetch_if_needed()
        return len(self._result_cache.get('rows', []))

    def fetch(self):
        if 'keys' in self.params:
            self._result_cache = self._db.res.post(self.view_path,
                    **self.params)
        else:
            self._result_cache = self._db.res.get(self.view_path, **self.params)

        self._total_rows = self._result_cache.get('total_rows')
        self._offset = self._result_cache.get('offset', 0)

    def _fetch_if_needed(self):
        if not self._result_cache:
            self.fetch()

    @property
    def total_rows(self):
        if self._total_rows is None:
            return self.count()
        return self._total_rows

    @property
    def offset(self):
        self._fetch_if_needed() 
        return self._offset

    def __iter__(self):
        return self.results_iterator()

    def __len__(self):
        return self.count()

    def __nonzero__(self):
        bool(len(self))

class TempView(View):
    def __init__(self, db, design, wrapper=None, **params):
        self._db = db
        self.design = design
        self._wrapper = wrapper
        self.params = params
        self._result_cache = None
        self._total_rows = None
        self._offset = 0


    def fetch(self):
        self._result_cache  = self._db.res.post('_temp_view', payload=self.design,
                **self.params)

        self._total_rows = self._result_cache.get('total_rows')
        self._offset = self._result_cache.get('offset', 0)
