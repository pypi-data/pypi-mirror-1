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

"""Test the functions for changing the files in the tree"""

import nose
from nose.tools import *
# import shutil, os

from .. import bzrtreebranch
from .. import editors

def _sizeof(iterable):
    """Find the size of an iterator by consuming it"""
    return len(list(iterable))

class TestEditors:
    def setUp(self):
        """Create a simple tree to test with"""
        _, self.tree = bzrtreebranch.create_branch_and_tree()
        self.tree.add_file('a','contents of a')
        self.tree.add_directory('adir')
        self.tree.add_file('adir/b','contents of b')
        self.tree.add_file('adir/c','This is file c')

        self.repetitions = 10

    def testEditorLeavesFiles(self):
        """Check that the editor doesn't change the tree"""
        editor = editors.Patcher()
        orig_size = _sizeof(self.tree.iter_all_files())
        for i in xrange(self.repetitions):
            self.tree = editor.edit(self.tree)
            assert _sizeof(self.tree.iter_all_files()) == orig_size


if __name__ == '__main__':
    nose.main()

