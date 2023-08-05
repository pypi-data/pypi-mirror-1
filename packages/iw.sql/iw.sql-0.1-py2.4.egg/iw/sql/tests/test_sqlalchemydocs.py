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
Generic Test case for 'iw.sqlalchemy' doctest
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest
import sys
import os

from zope.testing import doctest

current_dir = os.path.dirname(__file__)

def add_mapper(session):
    from sqlalchemy import *
    meta = session.bind
    my_table = Table('sample', meta,
                     Column('id', Integer, primary_key=True))
    class MyTable(object):
        pass

    my_table.create()
    my_table.insert().execute(id=1)
    orm.mapper(MyTable, my_table)
    return MyTable

def get_session():
    """adds a sample database"""
    from sqlalchemy import *
    db = create_engine('sqlite:///:memory:')
    session = create_session(bind=db)
    meta = MetaData(bind=db)
    my_table = Table('sample', meta,
                     Column('id', Integer, primary_key=True))
    class MyTable(object):
         pass

    my_table.create()
    my_table.insert().execute(id=1)
    orm.mapper(MyTable, my_table)
    return MyTable, session

def restart_server():
    """simulates a server that has restarted"""
    from sqlalchemy.orm.query import Query
    from sqlalchemy.exceptions import SQLAlchemyError

    old = Query.first

    def failure_execute(*args, **kw):
        try:
            raise SQLAlchemyError('the server said: pouf!')
        finally:
            Query.first = old
    Query.first = failure_execute

def doc_suite(test_dir, setUp=None, tearDown=None, globs=None):
    """Returns a test suite, based on doctests found in /doctest."""
    suite = []
    if globs is None:
        globs = globals()

    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)

    package_dir = os.path.split(test_dir)[0]
    if package_dir not in sys.path:
        sys.path.append(package_dir)

    doctest_dir = os.path.join(package_dir, 'doctests')

    # filtering files on extension
    docs = [os.path.join(doctest_dir, doc) for doc in
            os.listdir(doctest_dir) if doc.endswith('.txt')]

    globs['restart_server'] = restart_server
    klass, session = get_session()
    globs['session'] = session
    globs['MyTable'] = klass
    globs['add_mapper'] = add_mapper

    for test in docs:
        suite.append(doctest.DocFileSuite(test, optionflags=flags,
                                          globs=globs, setUp=setUp,
                                          tearDown=tearDown,
                                          module_relative=False))

    return unittest.TestSuite(suite)

def test_suite():
    """returns the test suite"""
    return doc_suite(current_dir)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

