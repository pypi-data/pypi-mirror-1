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

"""Test the functions for changing the tree structure"""

import nose
from nose.tools import *
# import shutil, os

from .. import bzrtreebranch
from .. import mutators

def _sizeof(iterable):
    """Find the size of an iterator by consuming it"""
    return len(list(iterable))

class TestMutators:
    def setUp(self):
        """Create a simple tree to test with"""
        _, self.tree = bzrtreebranch.create_branch_and_tree()
        self.tree.add_file('a','contents of a')
        self.tree.add_directory('adir')
        self.tree.add_file('adir/b','contents of b')
        self.tree.add_file('adir/c','This is file c')

        self.repetitions = 10

    def testFileCreator(self):
        """Check that the file creator doesn't remove files"""
        creator = mutators.FileCreator()
        old_size = _sizeof(self.tree.iter_all_files())
        num_directories = _sizeof(self.tree.iter_all_subdirs())
        for i in xrange(self.repetitions):
            self.tree = creator.mutate(self.tree)
            new_size = _sizeof(self.tree.iter_all_files())
            assert new_size >= old_size
            old_size = new_size
            assert _sizeof(self.tree.iter_all_subdirs()) == num_directories

    def testDirectoryCreator(self):
        """Check that the directory creator only creates directories"""
        creator = mutators.DirectoryCreator()
        old_size = _sizeof(self.tree.iter_all_subdirs())
        for i in xrange(self.repetitions):
            self.tree = creator.mutate(self.tree)
            new_size = _sizeof(self.tree.iter_all_subdirs())
            assert new_size >= old_size
            old_size = new_size

    def testFileRemover(self):
        """Removers should only reduce the size"""
        remover = mutators.FileRemover()
        old_size = _sizeof(self.tree.iter_all_files())
        num_directories = _sizeof(self.tree.iter_all_subdirs())
        for i in xrange(self.repetitions):
            self.tree = remover.mutate(self.tree)
            new_size = _sizeof(self.tree.iter_all_files())
            assert new_size <= old_size
            old_size = new_size
            assert _sizeof(self.tree.iter_all_subdirs()) == num_directories
        
    def testDirectoryRemover(self):
        """Removers should only reduce the size"""
        remover = mutators.DirectoryRemover()
        old_size = _sizeof(self.tree.iter_all_subdirs())
        for i in xrange(self.repetitions):
            self.tree = remover.mutate(self.tree)
            new_size = _sizeof(self.tree.iter_all_subdirs())
            assert new_size <= old_size
            old_size = new_size

    def testDirectoryMover(self):
        """The tree shouldn't change size when moving"""
        mover = mutators.DirectoryMover()
        old_file_size = _sizeof(self.tree.iter_all_files())
        old_directory_size = _sizeof(self.tree.iter_all_subdirs())
        for i in xrange(self.repetitions):
            self.tree = mover.mutate(self.tree)
            new_file_size = _sizeof(self.tree.iter_all_files())
            assert new_file_size == old_file_size
            new_directory_size = _sizeof(self.tree.iter_all_subdirs())
            assert new_directory_size == old_directory_size
            old_file_size, old_directory_size = new_file_size, new_directory_size

    def testFileMover(self):
        """The tree shouldn't change size when moving"""
        mover = mutators.FileMover()
        old_file_size = _sizeof(self.tree.iter_all_files())
        old_directory_size = _sizeof(self.tree.iter_all_subdirs())
        for i in xrange(self.repetitions):
            self.tree = mover.mutate(self.tree)
            new_file_size = _sizeof(self.tree.iter_all_files())
            assert new_file_size == old_file_size
            new_directory_size = _sizeof(self.tree.iter_all_subdirs())
            assert new_directory_size == old_directory_size
            old_file_size, old_directory_size = new_file_size, new_directory_size


if __name__ == '__main__':
    nose.main()
