# setuptools plugin for bzr
# Barry Warsaw <barry@python.org>

__version__ = '1.0'
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


if Branch is None:
    find_files_for_bzr = bzr_find_files_for_bzr
else:
    find_files_for_bzr = bzrlib_find_files_for_bzr
