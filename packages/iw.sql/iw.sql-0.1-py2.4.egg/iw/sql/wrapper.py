# -*- coding: utf-8 -*-
# Copyright (C)2007 'Ingeniweb'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
This module contains a base wrapper for SQL connections
"""
from z3c.sqlalchemy.base import BaseWrapper
import sqlalchemy

def retry_on_failure(func):
    """retry-on-failure decorator"""
    def _w_retry_on_failure(*args, **kw):
        try:
            return func(*args, **kw)
        except:
            return func(*args, **kw)
    return _w_retry_on_failure

def _secured_query(query):
    """returned a query object which methods are decorated"""
    def _w_secured_query(*args, **kw):
        query_object = query(*args, **kw)
        return DynamicDecorator(query_object, retry_on_failure)
    return _w_secured_query

class DynamicDecorator(object):
    """will dynamically decorate a class"""
    def __init__(self, instance, decorator, method_name=None):
        self.__instance = instance
        self.__method = method_name
        self.__decorator = decorator

    def __getattr__(self, name):
        if hasattr(self.__instance, name):
            attr = getattr(self.__instance, name)
            if type(attr).__name__ == 'instancemethod':
                if (self.__method is None or
                    attr.im_func.func_name == self.__method):
                    return self.__decorator(attr)
            return attr
        raise AttributeError(name)


def _secured_session(engine):
    """returns a decorated session object
    when `query` is invoqued, it's done through `_secured_query`
    """
    return  DynamicDecorator(sqlalchemy.create_session(engine),
                             _secured_query, 'query')

class SecuredBaseWrapper(BaseWrapper):
    """overrides the base wrapper to provide retry-on-failure
    pattern"""

    @property
    def session(self):
        return _secured_session(self._engine)


