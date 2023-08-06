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

import logging
from logging import DEBUG, INFO, debug, info
from optparse import OptionParser
from pprint import pprint

from mcrepogen.version_info import version_str
from analyze import analyze_branch
import numpy as np

data_keys = ['files_modified','files_added','files_moved',
             'directories_added', 'files_removed', 'directories_removed',
              'directories_moved']
DTYPE = np.dtype({'names':['revno']+data_keys,
                  'formats':['S100']+[np.int]*len(data_keys)})

def _summary_from_data(data):
    """Give one summary row from the dictionary representing a revision."""
    this_summary = np.empty((1,), DTYPE)
    debug('Got data dictionary %s', data)
    for key in data_keys:
        this_summary[key] = len(data[key])
    revno_str = ''
    for elt in data['revno']:
        revno_str += '.%d' % elt
    revno_str = revno_str[1:]  #strip of the leading dot
    this_summary['revno'] = revno_str
    debug('Got summary row: %s', str(this_summary))
    return this_summary


def summarize_branch(location=None, results=None, output_file=None,
                     feedback=True):
    """Summarize the changes on the branch at location.
    
    :param location: If given, summarize the branch at location
    :param results: If location is not given, this should be a generator
      such as would be produced by `analyze.analyze_branch`.
    :param output_file: If given, save the results array to this file
    """
    if location is not None:
        results = analyze_branch(location) #this should be a generator
    elif location is None and results is None:
        raise ValueError('You must specify either a branch location'
                         ' or a dictionary of analysis results.')
    summary = []
    for data in results:  # consume a generator
        summary.append(_summary_from_data(data))
        if feedback:
            y = len(summary)
            if y % 1000 == 0:
                info('Analyzed %d revisions', y) 
    answer = np.array(summary, DTYPE)
    
    if output_file is not None:
        np.save(output_file, answer)

    return answer


if __name__ == "__main__":
    parser = OptionParser(usage="%prog [-v] [-o OUTFILE] LOCATION",
                          version="%prog " + version_str)
    parser.add_option('-v', '--verbose', dest='verbose',
                      default=False, action='store_true',
                      help='Show more information during the analysis')
    parser.add_option('-o', '--output', dest='output',
                      default=None, action='store',
                      help='Save output to this file')
    options, args = parser.parse_args()
    FORMAT = '%(levelname)s: %(message)s'
    if options.verbose:
        logging.basicConfig(level=DEBUG, format=FORMAT)
    else:
        logging.basicConfig(level=INFO, format=FORMAT)
    if len(args) > 1 or len(args) == 0:
        parser.error("Wrong arguments.  "
                     "Please specify the path to a Bazaar branch.")
    pprint(summarize_branch(location=args[0], output_file=options.output))
