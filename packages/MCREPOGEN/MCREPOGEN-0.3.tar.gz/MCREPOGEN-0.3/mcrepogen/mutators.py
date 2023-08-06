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

"""Objects that mutate the structure of the tree"""

from random import random, choice, sample
import string, os, gzip
from string import whitespace

import numpy.random as mtrand

from bzrlib.errors import BzrMoveFailedError

word_list_location = os.path.join(os.path.dirname(__file__), '6of12.txt.gz')
WORD_LIST = [line.strip(whitespace+':&#<^=+') for line in
             gzip.GzipFile(word_list_location).readlines()]

def _random_filename():
    """Generate a random filename of specified length"""
    return choice(WORD_LIST)

def _random_content(length):
    """Returns a random line of content with at least length characters"""
    line = ''
    while len(line) < length:
        line += ' '+choice(WORD_LIST)
    return line


class Mutator(object):

    """This changes the contents of a tree in some probabilistic way."""

    def __init__(self, parameters=None):
        """Create an object with fixed probabilities.

        parameters should be a dictionary with the specified keys.  A
        missing key will result in the default value being
        used.
        """
        if parameters is None:
            self.parameters = self.default_parameters
        else: # parameters should be a dictionary
            self.parameters = parameters
            for k,v in self.default_parameters.items():
                if k not in self.parameters:
                    self.parameters[k] = v
            # make sure all of the values are numbers
            for k,v in self.parameters.items():
                self.parameters[k] = eval(str(v))

    def mutate(self, input_tree):
        """Return a changed version of the input_tree."""
        raise NotImplementedError


class FileCreator(Mutator):

    """A number of new files are created at random.

    At least one new file is created with probability p_happens.

    If at least one file is created, then the number of files created is 
    a geometric random variable where the mean is 1/p

    Their initial content is a collection of a random number of lines
    with a random number of characters between 0 and max_line_length.
    The expected number of characters per line is max_line_length/2.
    
    The number of lines has a geometric distribution (how many lines do
    we have to write to get to the last one where the probability of
    each line being the last one is given).  The expected number of
    lines in a file is 1/p_last_line.
    
    """

    default_parameters = {'p_happens': 0.123,
                          'p': 0.428,
                          'max_line_length': 72,
                          'p_last_line': 0.025 # no data on this yet
                         }

    def __init__(self, parameters=None):
        """Create an object with fixed probabilities.

        parameters should be a dictionary with the following keys.  A
        value of None for any key will result in the default value being
        used.
    
        key                 default value
        ---                 -------------
        'p_happens'             0.123
        'p'                     0.428
        'max_line_length'       72
        'p_last_line'           0.025
        """
        Mutator.__init__(self, parameters)

    def _random_content(self, num_lines):
        """Generate random content"""
        line_lengths = mtrand.randint(self.parameters['max_line_length'],
                                      size=num_lines)
        return '\n'.join(_random_content(length)
                         for length in line_lengths)

    def mutate(self, input_tree):
        """Add files with random initial content"""
        if mtrand.random() > self.parameters['p_happens']:
            return input_tree
        p_last_line = self.parameters['p_last_line']
        p = self.parameters['p']
        all_dirs = list(input_tree.iter_all_subdirs())
        _geometric = mtrand.geometric
        for i in xrange(_geometric(p)):
            dir = choice(all_dirs)
            if dir == '':
                full_path = _random_filename()
            else:
                full_path = dir + '/' + _random_filename()
            input_tree.add_file(full_path, 
                                self._random_content(_geometric(p_last_line)))
        return input_tree


class DirectoryCreator(Mutator):

    """Create subdirectories at random.

    A nonzero number of directories is created with probability p_happens.

    The number of new directories created has a geometric distribution with
    mean 1/p.

    """

    default_parameters = {'p_happens' : 0.028,
                          'p': 0.53 }

    def __init__(self, parameters=None):
        """Create an object with fixed probabilities.

        parameters should be a dictionary with the following keys.  A
        value of None for any key will result in the default value being
        used.
    
        key                 default value
        ---                 -------------
        'p_happens'         0.028
        'p'                 0.53
        """
        Mutator.__init__(self, parameters)

    def mutate(self, input_tree):
        """Add random subdirectories"""
        if mtrand.random() > self.parameters['p_happens']:
            return input_tree
        subdirs = list(input_tree.iter_all_subdirs())
        num_to_add = mtrand.geometric(self.parameters['p'])
        for i in xrange(num_to_add):
            dir = choice(subdirs)
            if dir == '':
                new_path = _random_filename()
            else:
                new_path = dir + '/' + _random_filename()
            input_tree.add_directory(new_path)
        return input_tree


class FileRemover(Mutator):

    """Remove files at random.

    A nonzero number of files is removed with probability p_happens.

    The number of files removed is a geometric random variable with mean
    1/p.
    """

    default_parameters = {'p_happens' : 0.026,
                          'p': 0.62 }

    def __init__(self, parameters=None):
        """Create an object with fixed probabilities.

        parameters should be a dictionary with the following keys.  A
        value of None for any key will result in the default value being
        used.
    
        key                 default value
        ---                 -------------
        'p_happens'         0.026
        'p'                 0.62
        """
        Mutator.__init__(self, parameters)

    def mutate(self, input_tree):
        """Remove files at random"""
        if mtrand.random() > self.parameters['p_happens']:
            return input_tree
        all_files = list(input_tree.iter_all_files())
        num_removed = min(len(all_files),
                          mtrand.geometric(self.parameters['p']))
        to_be_removed = sample(all_files, num_removed)
        for filename in to_be_removed:
            input_tree.remove_file(filename)
        return input_tree

    
class FileMover(Mutator):

    """Move files to new names at random.
    
    A non-zero number of files are moved with probability p_happens.

    The number of files moved is a geometric random variable with mean 1/p.
    
    """

    default_parameters = {'p_happens': 0.035,
                          'p': 0.59}

    def __init__(self, parameters=None):
        """Create an object with fixed probabilities.

        parameters should be a dictionary with the following keys.  A
        value of None for any key will result in the default value being
        used.
    
        key                 default value
        ---                 -------------
        'p_happens'             0.035
        'p'                     0.59
        """
        Mutator.__init__(self, parameters)

    def mutate(self, input_tree):
        """Move files around at random"""
        if mtrand.random() > self.parameters['p_happens']:
            return input_tree

        def _move(fromfile, to_dir):
            if os.path.dirname(fromfile) == to_dir:
                return
            to_path = os.path.join(to_dir,os.path.basename(fromfile))
            input_tree.move(fromfile, to_path)
        
        directories = list(input_tree.iter_all_subdirs())
        files = list(input_tree.iter_all_files())
        files_to_move = sample(files, mtrand.geometric(self.parameters['p']))
        for f in files_to_move:
            _move(f, choice(directories))
        return input_tree


class DirectoryRemover(Mutator):

    """Remove entire directories at random.

    A non-zero number of directories are removed with probability p_happens

    The number of directories removed is a geometric random variable with
    mean 1/p.

    """

    default_parameters = {'p_happens': .0065,
                          'p': 0.73}

    def __init__(self, parameters=None):
        """Create an object with fixed probabilitiezos.

        parameters should be a dictionary with the following keys.  A
        value of None for any key will result in the default value being
        used.
    
        key                 default value
        ---                 -------------
        'p_happens'             0.0065
        'p'                     0.73    
        """
        Mutator.__init__(self, parameters)

    def mutate(self, input_tree):
        """Remove directories at random"""
        if mtrand.random() > self.parameters['p_happens']:
            return input_tree
        num_removed = mtrand.geometric(self.parameters['p'])
        for d in sample(list(input_tree.iter_all_subdirs()), num_removed):
            if d == '':  #don't remove the root directory
                continue
            input_tree.remove_directory(d)
        return input_tree


class DirectoryMover(Mutator):

    """Move directories to new names at random.
    
    A non-zero number of directories is moved with probability p_happens.

    The number of directories moved is a geometric random variable with
    mean 1/p.
    
    """

    default_parameters = {'p_happens': 0.0044,
                          'p': 0.75}

    def __init__(self, parameters=None):
        """Create an object with fixed probabilities.

        parameters should be a dictionary with the following keys.  A
        value of None for any key will result in the default value being
        used.
    
        key                 default value
        ---                 -------------
        'p_happens'             0.0044
        'p'                     0.75
        """
        Mutator.__init__(self, parameters)

    def mutate(self, input_tree):
        """Move directories around at random"""
        if mtrand.random() > self.parameters['p_happens']:
            return input_tree

        directories = list(input_tree.iter_all_subdirs())
        # Make two passes.  Choose the directories to move. Then choose
        # where to move them to for each directory.
        to_move = []
        to_move = sample(directories,
                         mtrand.geometric(self.parameters['p']))
        while to_move:
            d = to_move.pop()
            new_home = choice(directories)
            try:
                input_tree.move(d, new_home)
            except (BzrMoveFailedError, IndexError):
                continue
            # rename everything involved with d
            new_path = os.path.join(new_home, os.basename(d))
            def _replacer(path):
                return string.replace(path, d, new_path)
            map(_replacer, directories)
            map(_replacer, to_move)
        return input_tree
