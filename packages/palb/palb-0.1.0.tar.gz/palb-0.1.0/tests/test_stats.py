from __future__ import division
import time
import math
from nose.tools import *

from palb.core import Result
from palb.stats import *

canned_results = [Result(t, 1500, 200) for t in [10, 13, 15, 20, 17]]

class TestResultStats(object):
    def setup(self):
        self.rs = ResultStats()
        for r in canned_results:
            self.rs.add(r)
        self.rs.stop()
    def test_failed_requests(self):
        self.rs.add(Result(100, 0, 400))
        eq_(len(self.rs.results), 6)
        eq_(self.rs.failed_requests, 1)
    
    def test_total_req_time(self):
        eq_(self.rs.total_req_time, 75)
    
    def test_avg_req_time(self):
        assert_almost_equal(self.rs.avg_req_time, 15)
    
    def test_total_req_length(self):
        eq_(self.rs.total_req_length, 1500*5)
    
    def test_avg_req_length(self):
        eq_(self.rs.avg_req_length, 1500)
    
    def test_distribution(self):
        dist = self.rs.distribution()
        eq_(dist, [(50, 15), (66, 17), (75, 17),
                   (80, 17), (90, 20), (95, 20), (98, 20), (99, 20), (100, 20)])
    def test_connection_times(self):
        assert self.rs.connection_times() is None
    def test_total_wall_time(self):
        s = ResultStats()
        time.sleep(0.2)
        s.stop()
        assert_almost_equal(s.total_wall_time, 0.2, 2)


def test_square_sum():
    eq_(square_sum([2, 3]), 4+9)

def test_mean():
    eq_(mean([1, 2, 3, 4, 5]), 3)
    eq_(mean([10, 20]), 15)

def test_median():
    eq_(median([1, 2, 3, 4, 5]), 3)
    eq_(median([0, 19, 2, 7, 6]), 6)

def test_deviations():
    eq_(deviations([1, 2, 3, 4, 5], 3), [-2, -1, 0, 1, 2])

def test_std_deviation():
    eq_(std_deviation([1, 2, 3, 4, 5]), math.sqrt(10/4))
    eq_(std_deviation([2]), 0)
    