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
import numpy as np
from scipy import stats

from analyze import _data_from_delta
from summary import _summary_from_data
from fit import fit, fit_poisson, fit_geometric, fit_zero_geometric, check_fit

class DummyDelta:

    def __init__(self, added=[], removed=[], renamed=[], 
                       modified=[], kind_changed=[]):
        self.added = added
        self.removed = removed
        self.renamed = renamed
        self.modified = modified
        self.kind_changed = kind_changed


class TestAnalyzeDelta:

    def setUp(self):
        # create a Delta member for testing
        self.delta = DummyDelta(added=[('file1', '1', 'file'),
                                       ('dir1', '2', 'directory')],
                                removed=[('file2', '3', 'file'),
                                         ('dir2', '4', 'directory')],
                                renamed=[('filea', 'fileb', '5', 'file'),
                                         ('dira', 'dirb', '6', 'directory')],
                                modified=[('filez', 'z', 'file', True)],
                                kind_changed=[('z', '7', 'file', 'directory')],
                               )

    def testDataFromDelta(self):
        """Make sure that the data dictionary has the right size values"""
        data = _data_from_delta(self.delta)
        assert_equal(len(data['files_added']), 1)
        assert_equal(len(data['directories_added']), 2)
        assert_equal(len(data['files_removed']), 2)
        assert_equal(len(data['directories_removed']), 1)
        assert_equal(len(data['files_moved']), 1)
        assert_equal(len(data['directories_moved']), 1)
        assert_equal(len(data['files_modified']), 1)

class TestSummary(TestAnalyzeDelta):

    def setUp(self):
        """Set up a data attribute"""
        TestAnalyzeDelta.setUp(self)
        self.data = _data_from_delta(self.delta)
        self.data['revno'] = (1,)

    def testTooLongRevno(self):
        """Revnos can be at most 100 characters"""
        self.data['revno'] = (1,)*51 # Equivalent to 1.1.1. and so on
        summary = _summary_from_data(self.data)
        assert_not_equal(summary[0], self.data['revno'])

    def testSumaryFromData(self):
        """Summary should have the right data"""
        summary = _summary_from_data(self.data)
        assert_equal(summary['files_added'], 1)
        assert_equal(summary['directories_added'], 2)
        assert_equal(summary['files_removed'], 2)
        assert_equal(summary['directories_removed'], 1)
        assert_equal(summary['files_moved'], 1)
        assert_equal(summary['directories_moved'], 1)
        assert_equal(summary['files_modified'], 1)

class TestFit:

    def testDegenerateFit(self):
        """Test a trivial distribution"""
        data = np.zeros((100,))
        def point_mass(x, p):
            return (x==0).astype(np.int)
        ans = fit(data, point_mass, [0.5])
        assert_equal(ans, 0.5)

    def testPoisson(self):
        """Test the Poisson fitter"""
        np.random.seed(12345)
        lam = np.random.uniform(.1, 10)
        data = np.random.poisson(lam, size=10000)
        ans1 = fit(data, stats.poisson.pmf, [1])
        ans2 = fit_poisson(data, lambda_guess=1)
        assert_equal(ans1, ans2)
        assert_almost_equal(ans2, lam, places=1)

    def testGeometric(self):
        """Test the Geometric fitter"""
        np.random.seed(1234)
        p = np.random.uniform()
        data = np.random.geometric(p, size=10000)
        ans1 = fit(data, stats.geom.pmf, [0.5])
        ans2 = fit_geometric(data, p_guess=0.5)
        assert_equal(ans1, ans2)
        assert_almost_equal(ans2, p, places=2)
        
    def testZeroGeometric(self):
        """Test fitting a geometric with a point mass at zero"""
        np.random.seed(12345678)
        p = np.random.uniform()
        data = np.random.geometric(p, size=10000)
        data = np.hstack((data, np.zeros(10000,)))
        p_fit, p_zero_fit = fit_zero_geometric(data, .5, .5)
        assert_almost_equal(p_fit, p, places=2)
        assert_almost_equal(p_zero_fit, 0.5, places=5)

    def testCheck(self):
        """Test the fit checker"""
        pmf = stats.rv_discrete(name='test', values=([0, 1], [.5, .5])).pmf
        data = np.array([0]*10 + [1]*11)
        chi2, p = check_fit(data, pmf, [])
        assert p > 0.5


if __name__ == '__main__':
    nose.main()
