#!/usr/bin/env python
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

"""
Create history of a random directory tree

MCREPOGEN creates random histories of directory trees using a Markov
Chain approach.
"""

import sys

import mcrepogen.transition as transition
from mcrepogen.version_info import version_info

def generate(output_file=None, revisions=100):
    b,t = transition.evolve(revisions)
    if output_file is None:
        out_stream = sys.stdout
    else:
        out_stream = file(output_file, 'w')
    b.serialize(out_stream)


if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [-r REVISIONS] [-o FILE]", 
                          version="%prog "+ "%d.%d" % version_info)
    parser.add_option('-o', '--output', dest='output', default=None,
                      help='Write output to FILE', metavar='FILE')
    parser.add_option('-r', '--revisions', dest='revisions', default=100,
                      type='int',
                      help='Number of revisions to create')

    (options, args) = parser.parse_args()
    generate(options.output, options.revisions)
