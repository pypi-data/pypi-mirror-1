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

"""Fit discrete probability distributions to measured frequency data."""

import logging
import numpy as np
try:
    from scipy.optimize import leastsq
    from scipy import stats
except ImportError:
    logging.error('fit.py requires SciPy for fitting')

try:
    from matplotlib import pyplot as plt
except ImportError:
    logging.error('fit.py requires matplotlib for plotting')

def fit(data, pmf_fcn, guesses, nbins=None):
    """Fit the distribution specified by pmf_fcn to the data.

    :param data: A list of measurements.
    :param pmf_fcn: A function to compute the probability mass function of
      the desired distribution.  It should accept additional parameters with
      pmf_fcn(x, *parameters) where the list parameters is of the same
      size as `guesses`.
    :param guesses: A list of initial guesses for the parameters of pmf_fcn.

    This does a least-squares fit of the differences between the relative
    frequency of each value in the data and the value of the pmf for that
    value.  This is a generic fitting process whose quality should be 
    checked a posteriori.  It is *not* the same as a maximum likelihood
    estimate for the parameters in the case of a particular distribution.

    """
    if nbins is None:
        nbins = 1 + data.max()
    hist_edges = np.arange(nbins+1)
    data_freq = np.histogram(data, hist_edges, normed=True)[0] 
    values = hist_edges[:-1]

    def residuals(parameters):
        res = data_freq - pmf_fcn(values, *list(parameters))
        return res

    return leastsq(residuals, guesses)[0]

def fit_poisson(data, lambda_guess=1, nbins=None):
    return fit(data, stats.poisson.pmf, [lambda_guess], nbins)

def fit_geometric(data, p_guess=0.5, nbins=None):
    return fit(data, stats.geom.pmf, [p_guess], nbins)

def _geom_zero_pmf(x, p, p_zero):
    g = stats.geom.pmf(x, p)
    zero = np.where(x==0, np.ones_like(x), np.zeros_like(x))
    return p_zero * zero + (1 - p_zero) * g

def fit_zero_geometric(data, 
                       p_guess=0.5, p_zero_guess=0.5,
                       nbins=None):
    """Fit a geometric distribution plus a point mass at zero"""

    return fit(data, _geom_zero_pmf, [p_guess, p_zero_guess], nbins)

def fit_zero_geometric2(data,
                        p_guess=0.5,
                        nbins=None):
    """Fit a geometric distribution plus a point mass at zero

    This version fits the probability of the point mass exactly and 
    then does a least-squares fit for the rest
    """
    data_nonzero = data[data.nonzero()]
    p_zero = 1 - len(data_nonzero)/float(len(data))
    p = fit_geometric(data_nonzero, p_guess=p_guess, nbins=nbins)
    return [p, p_zero]

def plot_fit(data, pmf_fcn, parameters, nbins=None):
    """Plot the histogram of the data along with the specified distribution
    
    :param parameters: a list of parameters for the pmf so that 
      pmf_fcn(x, *parameters) works
    """
    plt.figure()
    if nbins is None:
        nbins = data.max() + 1
    plt.hist(data, np.arange(nbins+1), normed=True)
    plt.plot(np.arange(nbins), pmf_fcn(np.arange(nbins), *parameters),
             color='black', linewidth=2,
             hold=True)

def check_fit(data, pmf_fcn, parameters, nbins=None):
    """Test if the data were drawn from the specified distribution.
    
    Returns the test statistic and p-value for the goodness of fit test.  If p
    is small, then it is likely that the data were *not* drawn from that
    distribution.
    
    """
    if nbins is None:
        nbins = data.max() + 1
    observed = np.histogram(data, np.arange(nbins+1))[0]
    expected = len(data)*pmf_fcn(np.arange(nbins), *parameters)
    return stats.chisquare(observed, expected)
