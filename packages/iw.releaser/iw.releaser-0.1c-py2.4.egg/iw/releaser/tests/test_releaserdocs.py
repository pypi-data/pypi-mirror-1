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
"""
Generic Test case for iw.releaser doctest
"""
__docformat__ = 'restructuredtext'

import subprocess
import unittest
import doctest
import sys
import os

from zope.testing import doctest

try:
    from subprocess import CalledProcessError
except ImportError:
    CalledProcessError = Exception

current_dir = os.path.dirname(__file__)

def cmd(cmd):
    if cmd == 'svn info':
        return ['Path: .', 'URL: http://xxx/my.package/trunk', '...']
    raise NotImplementedError

def check_cmd(cmd):
    for starter in ('svn ', 'python ', 'bin/buildout', 'bin\\buildout'):
        if cmd.startswith(starter):
            return True
    raise CalledProcessError(cmd, 'ok')

def  _checkout_tag(*args, **kw):
    pass

def setUp(self):
    import iw.releaser.base
    import iw.releaser.packet
    iw.releaser.base.command = cmd
    iw.releaser.base.check_command = check_cmd 
    iw.releaser.packet._checkout_tag = _checkout_tag
    iw.releaser.packet._run_setup = _checkout_tag
    import base
    import packet
    base.command = cmd
    base.check_command = check_cmd 
    packet._checkout_tag = _checkout_tag
    packet._run_setup = _checkout_tag

def doc_suite(test_dir, setUp=setUp, tearDown=None, globs=None):
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

    globs['test_dir'] = os.path.dirname(__file__)

    # filtering files on extension
    docs = [os.path.join(doctest_dir, doc) for doc in
            os.listdir(doctest_dir) if doc.endswith('.txt')]

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

