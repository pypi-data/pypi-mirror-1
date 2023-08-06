# Copyright 2009 Neil Martinsen-Burrell

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

import nose
from nose.tools import *

from .. import transition

class TestTransition:

    @raises(ValueError)
    def testNoMutators(self):
        """Call evolve with no mutators"""
        transition.evolve(0, None, [])

    @raises(ValueError)
    def testNoEditors(self):
        """Call evolve with no editors"""
        transition.evolve(0, [], None)

    def testNoRevisions(self):
        "Call evolve with 0 revisions"""
        transition.evolve(0, [], [])


if __name__ == '__main__':
    nose.main()
