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
""" project.py low-level tests
"""
import unittest
import os
import sys
import shutil

from zc.buildout.testing import rmdir

from iw.releaser.project import (archive_contents, _python, 
                                 diff_releases, _set_dynlibs, 
                                 _extract_url,  _make_python)
from iw.releaser import testing
from iw.releaser import base

from os.path import join
curdir = os.path.dirname(__file__)

class ProjectTest(unittest.TestCase):
  
    globs = {}
 
    def setUp(self):
        testing.releaserSetUp(self)
        testing.clearRepository(self)

        # adding a 'previous' snap
        svn_root = '%s/sample-buildout/trunk' % self.globs['svn_url']
        previous_snap = ['eggs/file', 'eggs/stuff.egg',
                         'downloads/dist/file', 'downloads/dist/file2']
        self.svn_root = svn_root

    def tearDown(self):
        testing.releaserTearDown(self)
     
    def test_light_archiving(self):
        
        location = join(os.path.dirname(__file__), 'tarball')
        tarfile_ = join(os.path.dirname(__file__), 'pack.tgz')

        # light archiving
        archive_contents('pack.tgz', location, source=True) 
        import tarfile
        tar = tarfile.open(tarfile_, "r:gz")
        try:
            elements = [tarinfo.name for tarinfo in tar
                        if not os.path.split(tarinfo.name)[-1].startswith('.')]
        finally:
            tar.close()

        for el in ['downloads/file.pyc', 'file2.pyc', 'file3.pyo']:
            self.assert_(el not in elements)

        os.remove(tarfile_)

        # complete archiving
        archive_contents('pack.tgz', location, source=False) 
        import tarfile
        tar = tarfile.open(tarfile_, "r:gz")
        try:
            elements = [tarinfo.name for tarinfo in tar
                        if not os.path.split(tarinfo.name)[-1].startswith('.')]
        finally:
            tar.close()

        for el in ['downloads/file.pyc', 'file2.pyc', 'file3.pyo']:
            self.assert_(el in elements)

        os.remove(tarfile_)
    
    def test_archiving(self): 
        location = join(os.path.dirname(__file__), 'tarball')
        #previous = self.svn_root
        tarfile_ = join(os.path.dirname(__file__), 'pack.tgz')
        archive_contents('pack.tgz', location) 
    
        # checking the result
        import tarfile
        tar = tarfile.open(tarfile_, "r:gz")
        try:
            elements = [tarinfo.name for tarinfo in tar
                        if not os.path.split(tarinfo.name)[-1].startswith('.')]
        finally:
            tar.close()

        for el in ['downloads/file2', 'file']:
            self.assert_(el in elements)

        os.remove(tarfile_)

    def test_python(self):
        # virtualenv generates python either python2.4
        test_bin = join(os.path.dirname(__file__), 
                                'test_bin')
        os.mkdir(test_bin)
        os.chdir(test_bin)
        try:
            os.mkdir(join(test_bin, 'bin'))
            os.mkdir(join(test_bin, 'Scripts'))
            linux =  (('bin', 'python'), 
                      ('bin', 'python2.4'),
                      ('bin', 'python2.4.3'))
            windows = (('Scripts', 'python.exe'),)
            if sys.platform == 'win32': 
                places = windows
            else:
                places = linux

            for place in places:
                f = open(join(test_bin, place[0], place[1]), 'w')
                f.write('#')
                f.close()
                python = _python()    
                self.assertEquals(python, join(place[0], place[1]))
                os.remove(python)
        finally:
            shutil.rmtree(test_bin)

    def test_diff_releases(self):
        # making a new tarball diff
        diff_dir = join(os.path.dirname(__file__), 'diff')
        old = join(diff_dir, 'old.tgz')
        new = join(diff_dir, 'new.tgz')
        res = join(diff_dir, 'res.tgz') 
        wanted = join(diff_dir, 'diff.tgz')
        try:
            diff_releases(old, new, res)

            # let's compare
            self.assert_(open(res, 'wb'), open(wanted, 'wb'))
        finally:
            if os.path.exists(res):
                os.remove(res)
    
    def test_diff_releases2(self):
        # make sure we get the tarball named autoamtically
        # in the right place
        diff_dir = join(os.path.dirname(__file__), 'diff')
        old = join(diff_dir, 'old.tgz')
        new = join(diff_dir, 'new.tgz')
        res = join(diff_dir, 'old-to-new.tgz') 
        wanted = join(diff_dir, 'diff.tgz')
        try:
            diff_releases(old, new)
            # let's compare
            self.assert_(open(res, 'wb'), open(wanted, 'wb'))
        finally:
            if os.path.exists(res):
                os.remove(res)

    def test_set_dynlibs(self):
        old = sys.executable
        sys.executable = os.path.join(curdir, 'python', 'python.exe')
        try:
            root = os.path.join(curdir, 'root')
            _set_dynlibs(root)
            self.assert_(os.path.exists(os.path.join(root, 'libs', 
                                                      'libpython24.a')))
        finally:
            shutil.rmtree(os.path.join(root, 'libs'))
            sys.executable = old

    def test_extract_url(self):
    
        prot, path = _extract_url('http://svn.ingeniweb.com/pack')
        self.assertEquals(prot, 'http://')
        self.assertEquals(path, ['svn.ingeniweb.com', 'pack'])

        prot, path = _extract_url('https://svn.ingeniweb.com/pack')
        self.assertEquals(prot, 'https://')
        self.assertEquals(path, ['svn.ingeniweb.com', 'pack'])

        prot, path = _extract_url('svn://svn.ingeniweb.com/pack')
        self.assertEquals(prot, 'svn://')
        self.assertEquals(path, ['svn.ingeniweb.com', 'pack'])
    
    def test_make_python(self):
        python = _make_python(curdir)
        try:
            self.assert_(os.path.exists(python)) 
        finally:
            if os.path.exists(python):
                dir_ = os.path.dirname(python)
                shutil.rmtree(dir_)

def test_suite():
    """returns the test suite"""
    return unittest.makeSuite(ProjectTest)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


