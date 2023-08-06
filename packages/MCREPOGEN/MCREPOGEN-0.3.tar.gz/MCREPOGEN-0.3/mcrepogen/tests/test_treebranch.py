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

"""Test the abstract and concrete branch and tree objects"""

import nose
from nose.tools import *
import shutil, os

from .. import treebranch
from .. import bzrtreebranch

class TreeTester:

    def assert_exists(self, item):
        """Assert that an item exists in the directory tree"""
        abspath = self.tree._tree.abspath(item)
        assert_true(os.path.exists(abspath))
    
    def assert_doesnt_exist(self, item):
        """Assert that an item does not exist in the directory tree"""
        abspath = self.tree._tree.abspath(item)
        assert_false(os.path.exists(abspath))


class TestABCs:

    def test_branch(self):
        """Branch should raise NotImplementedError for every method"""
        branch = treebranch.Branch()
        assert_raises(NotImplementedError, branch.checkpoint)
        assert_raises(NotImplementedError, branch.get_checkpoint,0)
        assert_raises(NotImplementedError, branch.serialize)

    def test_directory_tree(self):
        """DirectoryTree should raise NotImplementedError for every method"""
        tree = treebranch.DirectoryTree(None)
        assert_raises(NotImplementedError, tree.iter_files)
        assert_raises(NotImplementedError, tree.iter_subdirs)
        assert_raises(NotImplementedError, tree.iter_all_files)
        assert_raises(NotImplementedError, tree.iter_all_subdirs)
        assert_raises(NotImplementedError, tree.add_file,'path')
        assert_raises(NotImplementedError, tree.add_directory,'path')
        assert_raises(NotImplementedError, tree.remove_file,'path')
        assert_raises(NotImplementedError, tree.remove_directory,'path')
        assert_raises(NotImplementedError, tree.move,'path','newpath')
        assert_raises(NotImplementedError, tree.open_file,'path')
        assert_raises(NotImplementedError, tree.open_file_by_id,0)
        assert_raises(NotImplementedError, tree.path2id,'path')
        assert_raises(NotImplementedError, tree.id2path,0)


class TestBzrTree(TreeTester):

    def setup(self):
        self.tree = bzrtreebranch.BzrTree(None)

    def teardown(self):
        shutil.rmtree(self.tree._tree.basedir)

    def test_add(self):
        """Add a file"""
        id = self.tree.add_file('file1')
        contents = self.tree.open_file_by_id(id).read()
        assert_equal(contents, '')
        file_contents = open(self.tree._tree.abspath('file1'),'r').read()
        assert_equal(file_contents, '')

    def test_add_with_text(self):
        """Add a file with some initial content"""
        text = 'text of file1'
        id = self.tree.add_file('file1', text)
        contents = self.tree.open_file_by_id(id).read()
        assert_equal(contents, text)
        file_contents = open(self.tree._tree.abspath('file1'),'r').read()
        assert_equal(file_contents, text)

    def test_add_dir(self):
        """Add a directory"""
        self.tree.add_directory('dir1')
        # How do we know it got added?
        assert_equal(list(self.tree.iter_subdirs()), ['dir1'])

    def test_remove_file(self):
        """Remove a file"""
        self.tree.add_file('file1','contents')
        self.tree.remove_file('file1')
        assert_false(os.path.exists(self.tree._tree.abspath('file1')))

    def test_remove_dir(self):
        """Remove a directory"""
        self.tree.add_directory('dir1')
        self.tree.add_directory('dir1/subdir1')
        self.tree.add_file('dir1/file1')
        self.tree.remove_directory('dir1')
        print list(self.tree.iter_all_subdirs())
        for item in ['dir1', 'dir1/subdir1', 'dir1/file1']:
            self.assert_doesnt_exist(item)

    def test_move_file(self):
        """Move a file"""
        self.tree.add_directory('dir1')
        self.tree.add_directory('dir1/subdir1')
        self.tree.add_file('dir1/file1')
        self.tree.move('dir1/file1', 'dir1/subdir1/file1')
        self.assert_exists('dir1/subdir1/file1')

    def test_move_dir(self):
        """Move a directory"""
        self.tree.add_directory('dir1')
        self.tree.add_directory('dir2')
        self.tree.add_directory('dir1/subdir1')
        self.tree.add_file('dir1/file1')
        self.tree.move('dir1', 'dir2/dir1')
        self.assert_exists('dir2/dir1/file1')
        self.assert_exists('dir2/dir1/subdir1')

    def test_iter_subdirs(self):
        """Iterate over subdirectories"""
        self.tree.add_directory('dir1')
        self.tree.add_directory('dir2')
        assert_equal(set(self.tree.iter_subdirs()), set(['dir1', 'dir2']))

    def test_iter_subdirs_not_at_root(self):
        """Iterate over subdirectories of another directory"""
        self.tree.add_directory('dir1')
        self.tree.add_directory('dir2')
        self.tree.add_directory('dir1/subdir1')
        self.tree.add_directory('dir1/subdir2')
        assert_equal(set(self.tree.iter_subdirs('dir1')), 
                     set([u'dir1/subdir1', u'dir1/subdir2']))
        assert_false('dir2' in set(self.tree.iter_subdirs('dir1')))

    def test_iter_files(self):
        """Iterate over files"""
        self.tree.add_file('file1')
        self.tree.add_file('file2')
        assert_equal(set(self.tree.iter_files()),
                     set([u'file1', u'file2']))

    def test_iter_files_not_at_root(self):
        """Iterate over files in some directory"""
        self.tree.add_directory('dir1')
        self.tree.add_file('top_file')
        self.tree.add_file('dir1/file1')
        self.tree.add_file('dir1/file2')
        assert_equal(set(self.tree.iter_files('dir1')),
                     set([u'dir1/file1', u'dir1/file2']))
        assert_false('top_file' in set(self.tree.iter_files('dir1')))

    def test_iter_all(self):
        """Iterate recursively for files and subdirectories"""
        self.tree.add_directory('dir1')
        self.tree.add_file('file1')
        self.tree.add_file('dir1/subfile1')
        self.tree.add_directory('dir2')
        self.tree.add_directory('dir2/subdir1')
        assert_equal(set(self.tree.iter_all_files()),
                     set([u'file1', u'dir1/subfile1']))
        assert_equal(set(self.tree.iter_all_subdirs()),
                     set([u'', u'dir1', u'dir2', u'dir2/subdir1']))

    def test_path2id(self):
        """Convert pathnames to ids"""
        id = self.tree.add_file('file1')
        assert_equal(self.tree.path2id('file1'), id)

    def test_id2path(self):
        """Convert ids to pathnames"""
        id = self.tree.add_file('file1')
        assert_equal(self.tree.id2path(id), 'file1')


if __name__ == '__main__':
    nose.main()
