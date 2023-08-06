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

"""Objects that edit the content of files"""

import numpy.random as mtrand
import numpy as np
import random, string
from itertools import imap

from mutators import Mutator, _random_content

class Editor(Mutator):

    def edit(self, input_tree):
        raise NotImplmentedError

class Patcher(Editor):
    
    """Apply a randomly generated patch to randomly selected files.

    The number of files changed is a Poisson distribution with parameter lambda
    that gives the average number of files changed in a single revision.  

    The number of lines changed in the file is one plus a binomial with the
    number of lines is the file as n and a (small) probability p of each line
    being changed.  The changed lines are determined by a Bernoulli trial for
    each line and then split up into hunks based on their proximity.

    The number of lines replacing those in a hunk is Poisson with average
    equal to the number of lines in a hunk.

    The replacement lines have length uniformly distributed between 0 and
    max_line_length
    """

    default_parameters = {'lambda': 2,
                          'p_line_changed': .01,
                          'max_line_length': 72,
                         }

    def __init__(self, parameters=None):
        """Create an object with fixed probabilities.

        parameters should be a dictionary with the following keys.  A
        value of None for any key will result in the default value being
        used.
    
        key                 default value
        ---                 -------------
        'lambda'                2
        'p_line_changed'        .01
        'max_line_length'       72
        """
        Editor.__init__(self, parameters)


    def _patch_file(self, f):
        """Change the given file (opened for reading and writing)"""
        lines = f.readlines()
        length = len(lines)
        if length <= 1:
            changed_line_nums = [0]
        else:
            num_changed_lines = 1 + mtrand.binomial(length-1,
                self.parameters['p_line_changed'])
            changed_line_nums = random.sample(range(length), num_changed_lines)
        # make hunks
        changed_line_nums.sort()
        hunks = [[changed_line_nums[0]]]; hunk_num = 0
        for num in changed_line_nums[1:]:
            if num - hunks[hunk_num][-1] == 1:
                hunks[hunk_num].append(num)
            else: # start a new hunk
                hunks.append([num])
                hunk_num += 1
        # Change each hunk
        new_hunks = []
        for line_nums in hunks:
            new_hunk_length = mtrand.poisson(len(line_nums))
            line_lengths = mtrand.randint(self.parameters['max_line_length'],
                                          size=new_hunk_length)
            new_hunks.append([_random_content(length) + '\n'
                              for length in line_lengths])
        # Compose the new file
        f.seek(0); f.truncate()
        orig_file_pos = 0
        for i, line_nums in enumerate(hunks):
            f.writelines(lines[orig_file_pos:line_nums[0]])
            f.writelines(new_hunks[i])
            orig_file_pos = line_nums[-1] + 1
        f.writelines(lines[orig_file_pos:])

        f.close()


    def edit(self, input_tree):
        """Change lines in randomly selected files."""
        # select files that have changed
        n_changed = mtrand.poisson(self.parameters['lambda'], 1)[0]
        all_files = list(input_tree.iter_all_files())
        n_changed = min(n_changed, len(all_files))
        changed_files = random.sample(all_files, n_changed)
        for filename in changed_files:
            self._patch_file(input_tree.open_file(filename,'r+'))    
        return input_tree

