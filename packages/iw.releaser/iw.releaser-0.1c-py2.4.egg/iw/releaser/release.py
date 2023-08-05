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
import os
import re
import subprocess
import tempfile

re_version = re.compile(r"^version = '(.*?)'", re.MULTILINE|re.DOTALL)  

def _get_setup():
    """returns setup content"""
    setup_py = os.path.join(os.getcwd(), 'setup.py')
    return open(setup_py).read()

def get_version():
    """extract the version of the current package"""
    version = re_version.findall(_get_setup())
    if len(version) == 0:
        return None
    return version[0]

def raise_version(version):
    """raises the version"""
    new_setup = re_version.sub("version = '%s'" % version, _get_setup())
    setup_py = os.path.join(os.getcwd(), 'setup.py') 
    f = open(setup_py, 'w')
    try:
        f.write(new_setup)
    finally:
        f.close()

def check_tests():
    """runs the tests over the package"""
    try:
        # XXX get the env python
        subprocess.check_call('python setup.py ztest', shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def increment_changes():
    """increment changes"""
    version = get_version()
    CHANGES = os.path.join(os.getcwd(), 'CHANGES')
    if not os.path.exists(CHANGES):
        # no CHANGES file, let's create it
        content = ['* trunk',
                   '  - ',
                   '',
                   '* %s' % version,
                   '  - initial revision']
    else:
        # raising the version
        content = open(CHANGES).read()
        if '* %s' % version not in content:
            content = content.replace('* trunk', '* %s' % version)
            content = ['* trunk',  '  -'] + content.split('\n')
        else:
            content = content.split('\n')
    f = open(CHANGES, 'w')
    try:
        f.write('\n'.join(content))
    finally:
        f.close()

class ReleaseError(Exception):
    pass

def _command(cmd):
    """returns a command result"""
    return subprocess.Popen(cmd, shell=True, 
                            stdout=subprocess.PIPE).stdout

def _check_command(cmd):
    """sends a command and check the result"""
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def _get_svn_paths():
    """return paths"""
    version = get_version()
    svn_info = _command('svn info')
    url = None
    for element in svn_info:
        if element.startswith('URL:'):
            url = element.split('URL: ')[-1].strip()
            break
    if url is None:
        raise ReleaseError('could not find svn info')

    
    trunk = url
    if not url.endswith('/trunk'):
        raise ReleaseError('we are not in a trunk folder ! (%s)' % url) 

    paths = {}
    paths['trunk'] = trunk
    paths['root'] = trunk.replace('/trunk', '/')
    paths['tag_root'] = '%stags' % paths['root']
    paths['branch_root'] = '%sbranches' % paths['root']
    paths['tag'] = '%stags/%s' % (paths['root'], version)
    paths['branch'] = '%sbranches/%s' % (paths['root'], version)
    return paths

def create_branches():
    """creates a tag an a branch for the current version"""
    version = get_version()
    paths = _get_svn_paths()
    root = paths['root']
    tag_root = paths['tag_root']
    branch_root = paths['branch_root']
    tag = paths['tag']
    branch = paths['branch']
    trunk = paths['trunk']

    # commiting trunk
    if not _check_command('svn ci -m "preparing release %s"' % version):
        raise ReleaseError('could not commit the trunk')
   
    # checking if tag_root and branch_root exists 
    for branch_ in (tag_root, branch_root):
        if not _check_command('svn ls %s' % branch_):
            # creating the 
            if not _check_command('svn mkdir %s -m "creating folder"' \
                                  % branch_):
                raise ReleaseError('could not create the directory %s'\
                                    % branch_) 
    
    # checking if the branch exists, if so, override it
    if _check_command('svn ls %s' % branch):    
        # removing it
        if not _check_command('svn rm %s -m "removing branch"' \
                               % branch):
            raise ReleaseError("could not remove the existing branch")
        else:
            print 'branch was existing, removed'

    if not _check_command('svn cp %s %s -m "branch for %s release"' \
                          % (trunk, branch, version)):
        
        raise ReleaseError('could not copy the branch')
    else:
        print 'branch created for releasing'

    # now let's work on the branch: removing setup.cfg if it exists
    if _check_command('svn ls %s/setup.cfg' % branch):
        if not  _check_command(('svn rm %s/setup.cfg -m '
                                '"not needed for release"') % branch):
            raise ReleaseError('could not remove setup.cfg')
        else:
            print 'setup.cfg removed in the branch'

    # lets tag
    if _check_command('svn ls %s' % tag):    
        # removing it
        if not _check_command('svn rm %s -m "removing tag"' \
                               % tag):
            raise ReleaseError("could not remove the existing tag")
        else:
            print 'existing tag removed'
            
    if not _check_command('svn cp %s %s -m "tag for %s release"' \
                          % (trunk, tag, version)):
        
        raise ReleaseError('could not create the tag')
    else:
        print 'trunk tagged'

def pypi_upload():
    """upload into pypi"""
    version = get_version()
    paths = _get_svn_paths()
    rep = tempfile.mkdtemp()
    if not _check_command('svn co %s %s' % (paths['tag_root'], rep)):
        raise ReleaseError('could not get the version')

    # let's upload
    os.chdir(rep)
    _check_command('python setup.py register bdist_egg upload')

