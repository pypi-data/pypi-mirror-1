# Copyright (C) 2007-2008 by Barry A. Warsaw
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

"""setuptools plugin for projects maintained under Bazaar."""

__version__ = '1.1'
__all__ = [
    'find_files_for_bzr',
    ]


import os
import subprocess

try:
    from bzrlib.branch import Branch
    from bzrlib.errors import NotBranchError
except ImportError:
    Branch = None


def bzrlib_get_children(path):
    """Use direct bzrlib calls to get child information."""
    # Open an existing branch which contains the url.
    branch, inpath = Branch.open_containing(path)
    # Get the inventory of the branch's last revision.
    inv = branch.repository.get_revision_inventory(branch.last_revision())
    # Get the inventory entry for the path.
    entry = inv[inv.path2id(path)]
    # Return the names of the children.
    return [os.path.join(path, child) for child in entry.children.keys()]


def bzrlib_find_files_for_bzr(dirname):
    """Use direct bzrlib calls to recursively find versioned files."""
    bzrfiles = []
    search = [dirname]
    while search:
        current = search.pop(0)
        try:
            children = bzrlib_get_children(current)
        except NotBranchError:
            # Ignore this directory, it's not under bzr
            pass
        else:
            bzrfiles.extend(children)
            search.extend([child for child in children
                           if os.path.isdir(child)])
    return bzrfiles


def bzr_find_files_for_bzr(dirname):
    """Use the program bzr(1) to recursively find versioned files."""
    cmd = 'bzr ls --versioned ' + dirname
    proc = subprocess.Popen(cmd.split(),
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    # XXX check for errors and log stderr
    return stdout.splitlines()


def find_files_for_bzr(dirname):
    """Return the files found that are under bzr version control."""
    if Branch is None:
        paths = bzr_find_files_for_bzr(dirname)
    else:
        paths = bzrlib_find_files_for_bzr(dirname)
    return [path for path in paths if os.path.isfile(path)]
