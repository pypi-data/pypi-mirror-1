# Copyright 2008 Neil Martinsen-Burrell

# This file is part of mcrepogen
#
# mcrepogen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, tempfile, sys

from bzrlib.workingtree import WorkingTree
from bzrlib.bzrdir import BzrDir
from bzrlib.revisionspec import RevisionSpec
from bzrlib.status import show_tree_status
from bzrlib.errors import InvalidRevisionSpec, BzrError
from bzrlib.plugin import load_plugins
from bzrlib.urlutils import unescape

from treebranch import Branch, DirectoryTree

class FastImportNotInstalled(BzrError):

    _fmt = ('To serialize trees, you must install bzr-fastimport.\n'
            'See https://launchpad.net/bzr-fastimport for more information.')


class BzrBranch(Branch):

    """Concrete implementation using Bazaar's branch structure"""

    def __init__(self, path=None, outf=sys.stderr):
        if path is None:
            location = tempfile.mkdtemp()
        else:
            location = path
        
        try:
            self._branch = BzrDir.open(location).open_branch()
        except:
            self._branch = BzrDir.create_branch_convenience(location)

        self.outf = outf

    def checkpoint(self, print_output=True):
        """Commit the current state of the working tree.
        
        :param print_output: bool
            If true, print the differences for each commit.  Otherwise, 
            dont print anything.  The stream used for printing is
            accessible as self.outf.
        """
        wt = self._branch.bzrdir.open_workingtree()
        if print_output:
            try:
                show_tree_status(wt, to_file=self.outf,
                    revision=[RevisionSpec.from_string('revno:-1')])
            except InvalidRevisionSpec:
                pass

        id = wt.commit('')
        if print_output:
            print >> self.outf, "Committed revision %s" % self._branch.last_revision_info()[0]
        return id

    def get_checkpoint(self, identifier):
        """Return a tree representing the state specified by the identifier."""
        pass

    def serialize(self, out_stream=sys.stdout):
        """Return a serialized version of the branch's history.
        
        :param out_stream: A stream for output.  It defaults to stdout.
        
        """
        load_plugins()
        try:
            from bzrlib.plugins.fastimport.bzr_exporter import BzrFastExporter
        except ImportError:
            raise FastImportNotInstalled
        exporter = BzrFastExporter(unescape(self._branch.base),
                                   None)
        exporter.outf = out_stream
        exporter.run()

    def is_changed(self):
        """Has the associated tree has changed from the last checkpoint?"""
        wt = self._branch.bzrdir.open_workingtree()
        delta = wt.changes_from(wt.basis_tree())
        return delta.has_changed()


class BzrTree(DirectoryTree):

    """Concrete implementation using Bazaar's working tree."""

    def __init__(self, branch, path=None):
        """Create a bazaar tree.  Pass arguments on to WorkingTree"""
        self.branch=branch

        if path is None: # create the tree in a temporary location
            location = tempfile.mkdtemp()
        else:
            location = path
        
        try:
            self._tree = WorkingTree.open(location)
        except:
            BzrDir.create_standalone_workingtree(location)
            self._tree = WorkingTree.open(location)

    def _absolute_path(self, relative_path):
        """Return the file system absolute path of a tree-relative path"""
        return self._tree.abspath(relative_path)

    def _safe_add(self, path):
        """Add a file or directory, returning the ID"""
        self._tree.lock_write()
        self._tree.add(path)
        self._tree.unlock()
        return self._tree.path2id(path)

    def id2path(self, id):
        """Return the full path for a specified entry"""
        return self._tree.id2path(id)

    def path2id(self, path):
        """Return the id for a specified full path"""
        return self._tree.path2id(path)

    def iter_files(self, directory=''):
        """Iterate over the files in a directory."""
        self._tree.lock_read()
        for child_entry in self._tree.walkdirs(directory).next()[1]:
            if child_entry[2] == 'file':
                yield child_entry[0]
        self._tree.unlock()

    def iter_subdirs(self, directory=''):
        """Iterate over the files in a directory."""
        self._tree.lock_read()
        for child_entry in self._tree.walkdirs(directory).next()[1]:
            if child_entry[2] == 'directory':
                yield child_entry[0]
        self._tree.unlock()

    def iter_all_files(self, directory=''):
        """Iterate recursively over all files in start"""
        self._tree.lock_read()
        for directory_entry in self._tree.walkdirs(directory):
            children = directory_entry[1]
            for child in children:
                if child[2] == 'file':
                    yield child[0]
        self._tree.unlock()

    def iter_all_subdirs(self, directory=''):
        """Iterate recursively over all directories under start"""
        self._tree.lock_read()
        for directory_entry in self._tree.walkdirs(directory):
            yield directory_entry[0][0]
        self._tree.unlock()

    def add_file(self, filepath, contents=''):
        """Add a file to the tree, returning its ID.

        To change the file after it is added, use get_file_by_id.
        """
        absolute_filepath = self._absolute_path(filepath)
        f = open(absolute_filepath,'w')
        f.write(contents)
        f.close()
        return self._safe_add(filepath)

    def add_directory(self, directory):
        """Add a directory to the tree, returning its ID."""
        absolute_directory = self._absolute_path(directory)
        os.mkdir(absolute_directory)
        return self._safe_add(directory)

    def _hard_remove(self, path):
        """Really remove a file from the tree and filesystem."""
        self._tree.lock_write()
        self._tree.remove(path, keep_files=False, force=True)
        self._tree.unlock()

    def remove_file(self, filepath):
        """Remove a file or directory from the tree."""
        self._hard_remove(filepath)

    def remove_directory(self, directory):
        """Remove a directory and its children from the tree."""
        children = list(self.iter_all_files(directory))
        children += list(self.iter_all_subdirs(directory))
        self._hard_remove(children)

    def move(self, path, destination):
        """Move the item at path to destination"""
        self._tree.lock_write()
        try:
            self._tree.rename_one(path, destination)
        finally:
            self._tree.unlock()

    def open_file(self, path, mode='r'):
        """Return a file handle to the given file.

        The file will be opened with the specified mode.
        """
        return open(self._absolute_path(path), mode)

    def open_file_by_id(self, id, mode='r'):
        """Return a file handle for the file specified by the id.

        The file may be opened in any of the allowed modes.
        """
        return open(self._tree.id2abspath(id), mode)
    

def create_branch_and_tree(path=None, *args, **kwargs):
    """Convenience function to create a Branch and Tree.

    Returns a tuple of (branch, tree).
    """
    if path is None:
        location = tempfile.mkdtemp()
    else:
        location = path
    BzrDir.create_standalone_workingtree(location)
    branch = BzrBranch(path=location, *args, **kwargs)
    tree = BzrTree(branch, path=location)
    return branch, tree

