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
import subprocess

try:
    # python 2.5
    from subprocess import CalledProcessError
    from subprocess import check_call
except ImportError:
    # python 2.4
    CalledProcessError = Exception
    from subprocess import call

    def check_call(*args, **kw):
        return call(*args, **kw) == 0

class ReleaseError(Exception):
    pass

def command(cmd):
    """returns a command result"""
    return subprocess.Popen(cmd, shell=True, 
                            stdout=subprocess.PIPE).stdout

def check_command(cmd):
    """sends a command and check the result"""
    try:
        check_call(cmd, shell=True)
        return True
    except CalledProcessError:
        return False

def get_svn_url():
    """returns current folder's url"""
    svn_info = command('svn info')
    for element in svn_info:
        if element.startswith('URL:'):
            return element.split('URL: ')[-1].strip()
    raise ReleaseError('could not find svn info')

def svn_remove(url):
    """checking if the branch exists, if so, override it"""
    if check_command('svn ls %s' % url):    
        # removing it
        if not check_command('svn rm %s -m "removing branch"' \
                               % url):
            raise ReleaseError("could not remove the existing branch")
        else:
            print 'branch was existing, removed'

def svn_copy(source, target, comment):
    """copy a branch"""
    if not check_command('svn cp %s %s -m "%s"' \
                          % (source, target, comment)):
        raise ReleaseError('could not copy %s to %s' % (source, target))
    else:
        print 'copied %s to %s' % (source, target)

def svn_mkdir(url): 
    """make a dir if not existing"""
    if not check_command('svn ls %s' % url):
        # creating the folder 
        if not check_command('svn mkdir %s -m "creating folder"' % url):
            raise ReleaseError('could not create the directory %s' % url)

def svn_commit(comment):
    """commits the current directory"""
    if not check_command('svn ci -m "%s"' % comment):
        raise ReleaseError('could not commit the trunk')

def svn_rm(url, comment):
    """removes the url, if exists"""
    if check_command('svn ls %s' % url):
        if not check_command('svn rm %s -m "%s"' % (url, comment)):
            raise ReleaseError('could not remove %s' % url)
        else:
            print '%s removed' % url

def svn_checkout(url, folder):
    """checkouts"""
    if not check_command('svn co %s %s' % (url, folder)):
        raise ReleaseError('could not get %s' % url)

