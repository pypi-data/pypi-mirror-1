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

class Branch(object):

    """Abstract Base Class for a branch (history of directory trees)"""

    def __init__(self, tree=None):
        """Create a branch whose current state is the given tree."""
        self.tree = tree

    def checkpoint(self):
        """Record the current state of the tree.

        Returns an identifier that can be used to retrieve the state of
        the tree at the time this method is called.
        """
        raise NotImplementedError

    def get_checkpoint(self, identifier):
        """Get a directory tree corresponding to the give identifier."""
        raise NotImplementedError

    def serialize(self):
        """A file-like object representing the history of the tree.
        
        Use the read() method to get the history.  The preferred format
        is the stream format used by git's fast-import.
        """
        raise NotImplementedError


class DirectoryTree(object):

    """Abstract Base Class for a directory tree."""

    def __init__(self):
        """Create a new DirectoryTree"""
        pass

    def id2path(self, id):
        """Return the full path for a specified entry"""
        raise NotImplementedError

    def path2id(self, path):
        """Return the id for a specified full path"""
        raise NotImplementedError

    def iter_files(self, directory=''):
        """Iterate over the paths of the files in a directory"""
        raise NotImplementedError

    def iter_subdirs(self, directory=''):
        """Iterate over the paths of the subdirectories in a directory"""
        raise NotImplementedError

    def iter_all_files(self, directory=''):
        """Iterate recursively over all files in directory"""
        raise NotImplementedError

    def iter_all_subdirs(self, directory=''):
        """Iterate recursively over all subdirectories of directory
        
        Note that this method yields an entry for the starting directory, in
        contrast to iter_subdirs.

        """
        raise NotImplementedError

    def add_file(self, filepath, contents=''):
        """Add a file to the tree, returning its ID.

        To change the file after it is added, use open_file_by_id.
        """
        raise NotImplementedError

    def add_directory(self, directory):
        """Add a directory to the tree, returning its ID"""
        raise NotImplementedError

    def remove_file(self, filepath):
        """Remove the file from the tree."""
        raise NotImplementedError

    def remove_directory(self, directory):
        """Remove a directory and its children from the tree."""
        raise NotImplementedError

    def move(self, from_path, to_path):
        """Move an item in the tree.

        Move the item that is currently at from_path to the new location
        to_path.  Thus renames and moving files around and moving
        directories around are all handled in the same way 

        """
        raise NotImplementedError

    def open_file(self, filepath, mode='r'):
        """Return a file object for the given file.

        The file will be opened with the specified mode.
        """
        raise NotImplementedError

    def open_file_by_id(self, id, mode='r'):
        """Return a file obect for the file specified by the id.

        The file may be opened in any of the allowed modes.
        """
        raise NotImplementedError


