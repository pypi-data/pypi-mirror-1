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
from wrapper import DynamicDecorator

class TestWrapper(unittest.TestCase):

    def test_ddecorator(self):

        class A(object):

            def func(self):
                return 1

        def dec(func):
            def func_plus_one(*args, **kw):
                return func(*args, **kw) + 1
            return func_plus_one

        a = DynamicDecorator(A, dec)
        self.assertEquals(a.func(), 2)

def test_suite():
    tests = [unittest.makeSuite(TestWrapper)]
    return unittest.TestSuite(tests)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

