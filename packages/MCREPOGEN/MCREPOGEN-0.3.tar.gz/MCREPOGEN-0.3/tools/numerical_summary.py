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
from logging import DEBUG, INFO, debug, info
import numpy as np
from scipy import stats

from mcrepogen.version_info import version_str
from summary import data_keys


def outliers(data):
    q1 = stats.scoreatpercentile(data,25)
    q3 = stats.scoreatpercentile(data,75)
    upper_fence = np.median(data) + 1.5*(q3-q1)
    lower_fence = np.median(data) - 1.5*(q3-q1)
    too_high = data[data>upper_fence]
    too_low = data[data<lower_fence]
    return (len(too_high) > 0 or len(too_low) > 0, list(too_high) + list(too_low))


def five_num(data):
    return (data.min(), stats.scoreatpercentile(data, 25), np.median(data), stats.scoreatpercentile(data,75), data.max())


def summarize_column(col):
    col_nonzero = col[col.nonzero()]
    print "p_nonzero:", len(col_nonzero)/float(len(col))
    if len(col_nonzero) == 0:
        return
    print "Five number summary:", five_num(col_nonzero)
    out_yes, outs = outliers(col_nonzero)
    print "Mean:", col_nonzero.mean()
    print "St. Dev.:", col_nonzero.std()
    print "Outliers?", out_yes, len(outs)
    if out_yes and options.verbose:
        print outs


def numerical_summary(summary_array=None, summary_filename=None):
    """Compute numerical summaries of all of the data

    This function takes either an array of data as calculated by
    `summary.summarize_branch` or a filename with a .npy saved version
    of such an array.  If both are specified, the array is used.

    """
    if summary_array is None:
        if summary_filename is None:
            raise ValueError("One of summary_array or summary_filename"
                             " must be specified.")
        else:
            summary_array = np.load(summary_filename)
    debug("Summarizing %d rows", summary_array.shape[0])
    for key in data_keys:
        print key
        print '-'*len(key)
        summarize_column(summary_array[key])
        print



if __name__ == '__main__':
    parser = OptionParser(usage="%prog [-v] SUMMARY_FILE",
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
        parser.error("Wrong arguments.  Please specify the path"
                     "to a file with a saved summary array.")
    numerical_summary(summary_filename=args[0])


