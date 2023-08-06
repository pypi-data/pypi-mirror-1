# -*- coding: utf-8 -*-
# Copyright (C) 2007-2008 Christopher Lenz

__all__ = ['validate_dbname']

import re


VALID_DB_NAME = re.compile(r'^[a-z0-9_$()+-/]+$')
def validate_dbname(name):
    """ validate dbname """
    if not VALID_DB_NAME.match(name):
        raise ValueError('Invalid database name')
    return name
