# -*- coding: utf-8 -*-
# Copyright (C)2007 Ingeniweb

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
""" base.py low-level tests
"""
import unittest
import os

from iw.releaser.base import safe_input

class BaseTest(unittest.TestCase):

    def test_safe_input(self):
        def my_input(msg):
            return ''
        safe_input.func_globals['raw_input'] = my_input
        self.assertEquals(safe_input('value'), None)
        self.assertEquals(safe_input('value', 10), 10)
        

def test_suite():
    """returns the test suite"""
    return unittest.makeSuite(BaseTest)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


