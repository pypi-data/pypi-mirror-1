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

import sys

from bzrtreebranch import create_branch_and_tree
from mutators import *
from editors import *

def get_default_mutators():
    return  [FileCreator(),
             DirectoryCreator(),
             FileRemover(),
             DirectoryRemover(),
             FileMover(),
             DirectoryMover(),
            ]

def get_default_editors():
    return [Patcher()]

def evolve(iterations=100, mutators=None, editors=None):
    """Evolve a tree forward in time, snapshotting its progress.

    Create a tree and track its progress over time when changed by the
    specified mutators and editors.
    """

    if mutators is None:
        raise ValueError('You must specify a list of mutators')
    if editors is None:
        raise ValueError('You must specify a list of editors')

    transition = TransitionKernel(mutators, editors)
    branch, tree = create_branch_and_tree(outf=sys.stderr)

    ids = []
    for i in xrange(iterations):
        tree = transition.step(tree)
        new_id = branch.checkpoint()
        ids.append(new_id)
    return branch, tree


class TransitionKernel(object):

    """Transition object for a Markov Chain on directory trees."""

    def __init__(self, mutators, editors):
        """A TransitionKernel object with lists of mutators and editors.

        """
        self.mutators = mutators
        self.editors = editors

    def step(self, tree):
        """Take a forward time-step of the Markov Chain on the tree."""
        not_changed = True
        while not_changed:
            for mutator in self.mutators:
                tree = mutator.mutate(tree)
            for editor in self.editors:
                tree = editor.edit(tree)
            not_changed = not tree.branch.is_changed()
        return tree
