"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_numeric.py $
$Id: utest_numeric.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea.numeric import near_cmp
from sancho.utest import UTest

class CompareTest (UTest):

    def check_nonfloat (self):
        assert near_cmp(1, 2) == -1
        assert near_cmp(2, 1) == +1
        assert near_cmp(2, 2) == 0

        assert near_cmp('foo', 'bar') > 0
        assert near_cmp('bar', 'foo') < 0
        assert not near_cmp('foo', 'foo')

    def check_float (self):
        assert near_cmp(1.0, 1.0) == 0
        assert near_cmp(1.0, 1.00001) == -1
        assert near_cmp(1.000001, 1.0) == +1

        assert near_cmp(1.0e-9, 1.0e-9) == 0
        assert near_cmp(1.0e-9, 1.00001e-9) == -1
        assert near_cmp(1.000001e-9, 1.0e-9) == +1

        assert near_cmp(10.0, -10.0) == +1
        assert near_cmp(-10.0, 10.0) == -1
        assert near_cmp(-10.0, -10.0) == 0
        assert near_cmp(-10.0, -20.0) == +1
        assert near_cmp(-20.0, -10.0) == -1

        # provoke some round-off error
        v1 = 1000.0
        v2 = 1.0e-3 / 1.0e-6
        assert abs(v1 - v2) > 0
        assert v1 != v2
        assert near_cmp(v1, v2) == 0
        assert near_cmp(v2, v1) == 0

    def check_zero (self):
        small = 1e-6
        very_small = 1e-18

        assert near_cmp(0.0, 0.0) == 0
        assert near_cmp(0.0, small) == -1
        assert near_cmp(0.0,-small) == +1
        assert near_cmp(0.0, very_small) == 0
        assert near_cmp(0.0, -very_small) == 0

    def check_mixed (self):
        assert near_cmp(1, 1.0) == 0
        assert near_cmp(1.0, 1) == 0
        assert near_cmp(1, 1.00001) == -1
        assert near_cmp(1.000001, 1) == +1

        v1 = 1000
        v2 = 1.0e-3 / 1.0e-6
        assert near_cmp(v1, v2) == 0
        assert near_cmp(v2, v1) == 0


if __name__ == "__main__":
    CompareTest()
