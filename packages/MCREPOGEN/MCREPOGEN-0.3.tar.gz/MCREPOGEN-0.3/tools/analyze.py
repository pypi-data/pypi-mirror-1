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

from optparse import OptionParser
import logging
from logging import info, debug, warning, DEBUG, INFO
from pprint import pprint

from bzrlib.branch import Branch
from bzrlib.errors import NotBranchError

from mcrepogen.version_info import version_str

def _data_from_delta(delta):
    """Return a dictionary with interesting data from this delta."""
    data = {}
    added = delta.added
    data['files_added'] = [f[0] for f in added if f[2] == 'file']
    data['directories_added'] = [f[0] for f in added if f[2] == 'directory']
    
    data['files_modified'] = [f[0] for f in delta.modified if f[2] == 'file' \
                                                          and f[3]]
    removed = delta.removed
    data['files_removed'] = [f[0] for f in removed if f[2] == 'file']
    data['directories_removed'] = [f[0] for f in removed \
                                   if f[2] == 'directory']
    renamed = delta.renamed
    data['files_moved'] = [f[1] for f in renamed if f[3] == 'file']
    data['directories_moved'] = [f[1] for f in renamed if f[3] == 'directory']

    # handle kind changes as deletes and adds
    for f in delta.kind_changed:
        if f[2] == 'file' and f[3] == 'directory':
            data['files_removed'].append(f[0])
            data['directories_added'].append(f[0])
        elif f[2] == 'directory' and f[3] == 'file':
            data['files_added'].append(f[0])
            data['directories_removed'].append(f[0])
    return data


def analyze_branch(location):
    """Analyze the history of the branch at location.
    
    Yield a single dictionary for each revision.
    """
    info('Opening branch at %s', location)
    try:
        branch,_ = Branch.open_containing(location)
    except NotBranchError:
        raise ValueError("%s is not part of a Bazaar branch", location)
    debug('got branch %s', branch)
    debug('locking branch %s', branch)
    branch.lock_read()
    branch._merge_sorted_revisions_cache = None

    for revision_id,_,revno_tuple,__ in branch.iter_merge_sorted_revisions():
        this_result = {}
        this_result['revision_id'] = revision_id
        this_result['revno'] = revno_tuple
        revision = branch.repository.get_revision(revision_id)
        delta = branch.repository.get_deltas_for_revisions([revision]).next()
        this_result.update(_data_from_delta(delta))
        debug('result: %s', this_result)
        yield this_result
    branch.unlock()


if __name__ == "__main__":
    parser = OptionParser(usage="%prog [-v] LOCATION",
                          version="%prog " + version_str)
    parser.add_option('-v', '--verbose', dest='verbose',
                      default=False, action='store_true',
                      help='Show more information during the analysis')
    options, args = parser.parse_args()
    FORMAT = '%(levelname)s: %(message)s'
    if options.verbose:
        logging.basicConfig(level=DEBUG, format=FORMAT)
    else:
        logging.basicConfig(level=INFO, format=FORMAT)
    if len(args) > 1 or len(args) == 0:
        parser.error("Wrong arguments.  "
                     "Please specify the path to a Bazaar branch.")
    pprint(list(analyze_branch(args[0])))
