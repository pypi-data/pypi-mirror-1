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
import shutil

from zc.buildout.testing import rmdir

from iw.releaser.project import archive_contents, _python
from iw.releaser import testing
from iw.releaser import base

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
        testdir = os.path.dirname(__file__)
        checkout_dir = os.path.join(testdir, 'checkout')

        base.svn_checkout(svn_root, checkout_dir)
        snap = os.path.join(checkout_dir, '.snapshot')
        f = open(snap, 'w')
        f.write('\n'.join(previous_snap))
        f.close()
        curdir = os.getcwd()
        os.chdir(checkout_dir)
        base.svn_add(snap)
        base.svn_commit('added snapshot')
        rmdir(checkout_dir)
        os.chdir(curdir)        

    def tearDown(self):
        testing.releaserTearDown(self)
         
    def test_archiving(self):         
        
        location = os.path.join(os.path.dirname(__file__), 'tarball')
        previous = self.svn_root
        tarfile_ = os.path.join(os.path.dirname(__file__), 'pack.tgz')
        archive_contents('pack.tgz', location, previous)            
    
        # checking the result
        import tarfile
        tar = tarfile.open(tarfile_, "r:gz")
        try:
            elements = [tarinfo.name for tarinfo in tar
                        if not os.path.split(tarinfo.name)[-1].startswith('.')]
        finally:
            tar.close()
        
        self.assertEquals(elements, ['tarball/downloads/file2', 
                                     'tarball/file'])        

        os.remove(tarfile_)

    def test_python(self):
        # virtualenv generates python either python2.4
        test_bin = os.path.join(os.path.dirname(__file__), 
                                'test_bin')
        os.mkdir(test_bin)
        os.chdir(test_bin)
        try:
            os.mkdir(os.path.join(test_bin, 'bin'))
            os.mkdir(os.path.join(test_bin, 'Scripts'))
                
            f = open(os.path.join(test_bin, 'bin', 'python'), 'w')
            f.write('#')
            f.close()
            python = _python()    
            self.assertEquals(python, 'bin/python')
            os.remove(python)
            f = open(os.path.join(test_bin, 'bin', 'python2.4'), 'w')
            f.write('#')
            f.close()
            python = _python()    
            self.assertEquals(python, 'bin/python2.4')
            os.remove(python)
            f = open(os.path.join(test_bin, 'Scripts', 'python'), 'w')
            f.write('#')
            f.close()
            python = _python()    
            self.assertEquals(python, 'Scripts/python')

        finally:
            shutil.rmtree(test_bin)

def test_suite():
    """returns the test suite"""
    return unittest.makeSuite(ProjectTest)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


