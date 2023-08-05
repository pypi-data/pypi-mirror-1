"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_range.py $
$Id: utest_range.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea.physical_value import PhysicalValue
from dulcinea.range_value import RangeValue
from sancho.utest import UTest, raises

class RangeTest (UTest):

    def check_init(self):
        r1 = RangeValue(1, 3)
        assert r1.get_tuple() == (1,3)
        assert r1.get_min() == 1
        assert r1.get_max() == 3
        assert r1.get_type() == int
        r = RangeValue(1.0, 3.0)
        assert r.get_tuple() == (1.0,3.0)
        assert map(type, r.get_tuple()) == [float,float]


    def check_init_err(self):
        raises(TypeError, RangeValue)
        raises(TypeError, RangeValue, 1)
        raises(TypeError, RangeValue, 1, 2, 3)
        raises(TypeError, RangeValue, 'foo')
        raises(TypeError, RangeValue, (1, 'foo'))
        raises(TypeError, RangeValue, (1, 3.0))
        raises(TypeError, RangeValue, (3L, 5.0))
        raises(TypeError, RangeValue, (-6.66, 10))
        # range values CANNOT contain PhysicalValues!
        pv1 = PhysicalValue(1.0)
        pv2 = PhysicalValue(2.0)
        raises(TypeError, RangeValue, pv1, pv2)
        raises(ValueError, RangeValue, 1, 0)
        raises(ValueError, RangeValue, 1.5, -5.0)

    def check_format(self):
        r1 = RangeValue(1, 3)
        r2 = RangeValue(2.0, 5.6)
        r3 = RangeValue(0, 0)

        assert str(r1) == "1 .. 3"
        assert r1.format() == "1 .. 3"
        assert str(r2) == "2.0 .. 5.6"
        assert r2.format() == "2 .. 5.6"
        assert r3.format() == "0"


    def check_convert(self):
        r1 = RangeValue(1, 10)
        r2 = RangeValue(1, 10)
        assert r1 == r2
        assert r1.get_type() == int
        assert r2.get_type() == int

        r3 = r2.to_float()
        assert r2.get_type() == int
        assert r3.get_type() == float

        assert r2 == r3
        assert not r2 is r3


    def check_eq(self):
        irange = RangeValue(1, 4)
        frange = RangeValue(2.5, 3.5)
        assert irange == irange
        assert irange == RangeValue(1, 4)
        assert frange == frange
        assert frange == RangeValue(2.5, 3.5)
        assert irange != frange
        assert frange != irange
        assert irange != 37
        assert irange != 'foo'
        assert frange != 37
        assert frange != 'foo'

    def check_addsub(self):
        r1 = RangeValue(1, 4)
        r2 = RangeValue(2, 3)
        assert (r1 + 2).get_tuple() == (3, 6)
        assert (2 + r1).get_tuple() == (3, 6)
        assert (r1 - 2).get_tuple() == (-1, 2)
        assert (2 - r1).get_tuple() == (-2, 1)
        assert (r1 + 2.0).get_tuple() == (3, 6)
        assert (r1 - 2.0).get_tuple() == (-1, 2)
        try:
            r1 + r2
            assert 0
        except TypeError: pass
        try:
            r1 - r2
            assert 0
        except TypeError: pass

    def check_muldiv(self):
        r1 = RangeValue(1, 4)
        r2 = RangeValue(2, 3)
        # Multiplication and division: range with scalar
        assert (r1 * 2).get_tuple() == (2, 8)
        assert (2 * r1).get_tuple() == (2, 8)
        assert (r1 / 2).get_tuple() == (0, 2)

        fr1 = RangeValue(*map(float, r1.get_tuple()))
        assert fr1 == r1
        assert (fr1 / 2).get_tuple() == (0.5, 2.0)

        # Multiplication and division of ranges
        try:
            r1 * r2
            assert 0
        except TypeError: pass
        try:
            r1 / r2
            assert 0
        except TypeError: pass

        # Try dividing float range
        r1 = r1.to_float()
        assert (r1 / 2.0).get_tuple() == (0.50, 2.0)


    def check_compare(self):
        r1 = RangeValue(1, 4)
        r1a = RangeValue(1.0, 4.0)
        r2 = RangeValue(-2.5, 3.25)

        # ranges can only be compared for equality -- relations
        # don't make sense because of Python's weak comparison
        # semantics ;-(
        assert r1 == RangeValue(1, 4)
        assert r1 == r1a
        assert r1 != r2

        # test the 'in_range()' method
        assert r1.in_range(2)
        assert r1.in_range(1)
        assert r1.in_range(4)
        assert r1.in_range(1.001)
        assert not r1.in_range(0)
        assert not r1.in_range(4.1)

        assert r2.in_range(-2.5)
        assert r2.in_range(3.25)
        assert not r2.in_range(-2.6)
        assert not r2.in_range(3.26)


if __name__ == "__main__":
    RangeTest()
