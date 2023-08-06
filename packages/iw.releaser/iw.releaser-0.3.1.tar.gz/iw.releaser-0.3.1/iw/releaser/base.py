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
from tarfile import TarFile
import subprocess
import os
import sys

join = os.path.join

try:
    # python 2.5
    from subprocess import CalledProcessError
    from subprocess import check_call
except ImportError:
    # python 2.4
    CalledProcessError = Exception
    from subprocess import call

    def check_call(*args, **kw):
        return call(*args, **kw)

class ReleaseError(Exception):
    pass

def system(command, input=''):
    i, o, e = os.popen3(command)
    if input:
        i.write(input)
    i.close()
    result = o.read()+e.read()
    o.close()
    e.close()
    return result

def command(cmd):
    """returns a command result"""
    return subprocess.Popen(cmd, shell=True, 
                            stdout=subprocess.PIPE).stdout

def check_command(cmd):
    """sends a command and check the result"""
    try:
        return check_call(cmd, shell=True) == 0
    except CalledProcessError:
        return False

def get_svn_url():
    """returns current folder's url"""
    svn_info = command('svn info')
    for element in svn_info:
        if element.startswith('URL'):
            return element.split(':', 1)[-1].strip()
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

def svn_cat(url):
    """checkouts"""
    return system('svn cat %s' % url)

def svn_checkout(url, folder):
    """checkouts"""
    if not check_command('svn co %s %s' % (url, folder)):
        raise ReleaseError('could not get %s' % url)

def svn_add(*files):
    """adding files"""
    for file_ in files:
        if not check_command('svn add %s' % file_):
            raise ReleaseError('could not add %s' % file_)

def safe_input(message, default=None):
    if default is None:
        sdefault = ''
    else:
        sdefault = default
    value = raw_input('%s [%s]: ' % (message, sdefault)) 
    value = value.strip()
    if value == '':
        return default
    return value

def yes_no_input(message, default='n'):
    show_default = default == 'n' and 'y/N' or 'Y/n'
    value = raw_input('%s [%s]: ' % (message, show_default))
    value = value.strip().lower()
    if not value:
        return default == 'y' and True or False
    if value in ('y', 'yes'):
        return True
    return False

def display(msg):
    print msg

if sys.version_info[0:2] < (2, 5):
    # this come from python 2.5

    def extractall(self, path=".", members=None):
        """Extract all members from the archive to the current working
        directory and set owner, modification time and permissions on
        directories afterwards. `path' specifies a different directory
        to extract to. `members' is optional and must be a subset of the
        list returned by getmembers().
        """
        directories = []
        if members is None:
            members = self
        for tarinfo in members:
            if tarinfo.isdir():
                # Extract directory with a safe mode, so that
                # all files below can be extracted as well.
                try:
                    os.makedirs(os.path.join(path, tarinfo.name), 0700)
                except EnvironmentError:
                    pass
                directories.append(tarinfo)
            else:
                self.extract(tarinfo, path)

        # Reverse sort directories.
        directories.sort(lambda a, b: cmp(a.name, b.name))
        directories.reverse()

        # Set correct owner, mtime and filemode on directories.
        for tarinfo in directories:
            path = os.path.join(path, tarinfo.name)
            try:
                self.chown(tarinfo, path)
                self.utime(tarinfo, path)
                self.chmod(tarinfo, path)
            except ExtractError, e:
                if self.errorlevel > 1:
                    raise
                else:
                    self._dbg(1, "tarfile: %s" % e)
    TarFile.extractall = extractall
