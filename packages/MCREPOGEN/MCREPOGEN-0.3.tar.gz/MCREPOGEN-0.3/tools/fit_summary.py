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
from matplotlib import pyplot as plt

from mcrepogen.version_info import version_str
from summary import data_keys
from graphical_summary import _key_to_title
from fit import fit_geometric


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


def plot_column(col, p, title='Column Fit', axes=None, nbins=None):
    if axes is None:
        axes = plt.Axes(plt.figure(), [0,1,0,1])
    if nbins is None:
        nbins = col.max() + 1
    axes.hist(col, np.arange(1, nbins+1), normed=True)
    axes.set_title(title)
    axes.set_ylim([0,1])
    
    points = np.arange(1, nbins+1)
    values = stats.geom.pmf(points, p)
    axes.plot(points, values, 'k-', linewidth=3)
    return axes


def fit_column(col, nbins=None):
    """Fit a distribution to one column.

    Return None if the fit cannot be done.
    """
    col_nonzero = col[col.nonzero()]
    print "p_nonzero:", len(col_nonzero)/float(len(col))
    if len(col_nonzero) == 0:
        return None
    p = fit_geometric(col_nonzero, nbins=nbins)
    print 'p:', p
    return p
    

def fit_summary(summary_array=None, summary_filename=None, nbins=None):
    """Fit distributions and plot the best fits.

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
    plt.figure(figsize=(11,6));
    for i, key in enumerate(data_keys):
        print key
        print '-'*len(key)
        p = fit_column(summary_array[key], nbins=nbins)
        if p is not None:
            ax = plot_column(summary_array[key], p, title=_key_to_title(key),
                                                    axes=plt.subplot(2,4,i+1),
                                                    nbins=nbins)
        if i % 4 != 0:
            ax.set_yticklabels([])
        print
    plt.show()



if __name__ == '__main__':
    parser = OptionParser(usage="%prog [-v] [-n NBINS] SUMMARY_FILE",
                          version="%prog " + version_str)
    parser.add_option('-v', '--verbose', dest='verbose',
                      default=False, action='store_true',
                      help='Show more information during the analysis')
    parser.add_option('-n', '--num-bins', dest='nbins',
                      default=None, action='store', type=int,
                      help='Number of bins to use for the fit')
    options, args = parser.parse_args()
    FORMAT = '%(levelname)s: %(message)s'
    if options.verbose:
        logging.basicConfig(level=DEBUG, format=FORMAT)
    else:
        logging.basicConfig(level=INFO, format=FORMAT)
    if len(args) > 1 or len(args) == 0:
        parser.error("Wrong arguments.  Please specify the path"
                     "to a file with a saved summary array.")
    fit_summary(summary_filename=args[0], nbins=options.nbins)


