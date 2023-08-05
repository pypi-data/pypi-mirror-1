"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_set_utils.py $
$Id: utest_set_utils.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea.physical_unit import  UnitCollection
from dulcinea.physical_value import PhysicalValue
from dulcinea.range_value import RangeValue
from dulcinea.set_utils import _get_physical_value_intersection
from dulcinea.set_utils import get_set_intersection
from dulcinea.set_utils import in_set, get_range_intersection
from sancho.utest import UTest, raises

def split_comma (s):
    return s.split(', ')

class CompareTest (UTest):

    def _pre(self):
        self.units = units = UnitCollection()

    def _post(self):
        del self.units

    def check_simple_set(self):
        set1 = ['foo', 'bar']
        assert in_set('foo', set1)
        assert not in_set('', set1)
        assert not in_set(3, set1)
        set1.append(3)
        assert in_set(3, set1)
        raises(TypeError, in_set, 'foo', 'bar')
        raises(TypeError, in_set, 'f', 'bar')
        raises(TypeError, in_set, 'f', 3)

    def check_range_set(self):
        set2 = [3, 6, RangeValue(8, 10)]
        assert in_set(3, set2)
        assert not in_set(4, set2)
        assert not in_set('foo', set2)
        assert in_set(6.0, set2)
        assert in_set(6L, set2)
        assert in_set(8, set2)
        assert in_set(9, set2)
        assert in_set(10, set2)
        assert in_set(8.5, set2)
        assert not in_set(10.5, set2)

        # Put the range in the middle
        set2.append(12)
        assert in_set(10, set2)
        assert not in_set(10.5, set2)
        assert not in_set(11, set2)
        assert in_set(12, set2)

    def check_pv_set(self):
        get_unit = self.units.get_unit
        set3 = (PhysicalValue(3, get_unit("min")),
                PhysicalValue(4, get_unit("s")),
                PhysicalValue(1.5, get_unit("hour")))
        assert in_set(PhysicalValue(3, get_unit('min')), set3)
        assert not in_set(PhysicalValue(3.1, get_unit('min')), set3)
        assert in_set(PhysicalValue(180, get_unit('s')), set3)
        assert in_set(PhysicalValue(1.5, get_unit('hour')), set3)
        assert in_set(PhysicalValue(90, get_unit('min')), set3)
        assert not in_set(PhysicalValue(-90, get_unit('min')), set3)

    def check_pv_range_set(self):
        get_unit = self.units.get_unit
        set4 = (PhysicalValue(1.5, get_unit("m")),
                PhysicalValue(RangeValue(200, 300), get_unit("cm")),
                PhysicalValue(4, get_unit("m")))
        assert in_set(PhysicalValue(1.5, get_unit('m')), set4)
        assert not in_set(PhysicalValue(1.4, get_unit('m')), set4)
        assert in_set(PhysicalValue(2, get_unit('m')), set4)
        assert in_set(PhysicalValue(2.9, get_unit('m')), set4)
        assert in_set(PhysicalValue(3000, get_unit('mm')), set4)
        assert in_set(PhysicalValue(2.5e6, get_unit('um')), set4)
        assert in_set(PhysicalValue(4e6, get_unit('um')),
                      [PhysicalValue(4, get_unit('m'))])
        assert in_set(PhysicalValue(4e6, get_unit('um')), set4)
        assert not in_set(PhysicalValue(1, get_unit('s')), set4)

def _parse_physical_value(s, get_unit):
    split = s.split()
    if len(split) == 1:
        return PhysicalValue(float(split[0]), None)
    elif len(split) == 2:
        return PhysicalValue(float(split[0]), get_unit(split[1]))
    else:
        return PhysicalValue(RangeValue(float(split[0]),
                                        float(split[2])),
                             get_unit(split[3]))

class IntersectionTest (UTest):

    def _pre(self):
        self.units = units = UnitCollection()

    def _post(self):
        del self.units

    def _testrv (self, a, b, expect):
        ra = RangeValue(*a)
        rb = RangeValue(*b)
        assert get_range_intersection(ra, rb) == RangeValue(*expect)
        assert get_range_intersection(rb, ra) == RangeValue(*expect)

    def _testp (self, a, b, expect):
        pa = _parse_physical_value(a, self.units.get_unit)
        pb = _parse_physical_value(b, self.units.get_unit)
        pe = expect and _parse_physical_value(expect, self.units.get_unit)
        assert _get_physical_value_intersection(pa, pb) == pe
        assert _get_physical_value_intersection(pb, pa) == pe

    def _tests (self, a, b, expect):
        pa = [_parse_physical_value(x, self.units.get_unit)
              for x in split_comma(a)]
        pb = [_parse_physical_value(x, self.units.get_unit)
              for x in split_comma(b)]
        pe = expect and [_parse_physical_value(x, self.units.get_unit)
                         for x in  split_comma(expect)]
        assert get_set_intersection(pa, pb) == pe
        assert get_set_intersection(pb, pa) == pe

    def check_intersections_of_range_value(self):
        self._testrv((0.0, 1.0), (0.0, 0.9), (0.0, 0.90))
        self._testrv((0.0, 1.0), (0.0, 1.0), (0.0, 1.0))
        self._testrv((0.0, 1.0), (0.0, 1.1), (0.0, 1.0))
        self._testrv((0.0, 1.0), (0.1, 0.9), (0.1, 0.90))
        self._testrv((0.0, 1.0), (0.1, 1.0), (0.1, 1.0))
        self._testrv((0.0, 1.0), (0.1, 1.1), (0.1, 1.0))
        self._testrv((0.0, 1.0), (-0.1, 0.9), (0.0, 0.90))
        self._testrv((0.0, 1.0), (-0.1, 1.0), (0.0, 1.0))
        self._testrv((0.0, 1.0), (-0.1, 1.1), (0.0, 1.0))

    def check_intersections_of_physical_value(self):
        self._testp("0 um", "0 .. 5 um", "0 um")
        self._testp("-1 um", "0 .. 5 um", None)
        self._testp("1 um", "0 .. 5 um", "1 um")
        self._testp("1 .. 3 um", "0 .. 5 um", "1 .. 3 um")
        self._testp("1 .. 6 um", "0 .. 5 um", "1 .. 5 um")
        self._testp("1 .. 6 um", "9 .. 11 um", None)

    def check_intersections_of_lists_of_physical_value(self):
        self._tests("1 um, 3 um", "3 um, 5 um", "3 um")
        self._tests("1 um, 3 um", "3, 5 um", [])
        self._tests("1 um, 3 um", "3 .. 5 um", "3 um")
        self._tests("1 um, 3 um, 5 um", "3 .. 5 um", "3 um, 5 um")
        self._tests("1 um, 3 .. 5 um", "3 um, 5 um", "3 um, 5 um")
        self._tests("1 um, 3 um", "1 um, 5 um", "1 um")

if __name__ == "__main__":
    CompareTest()
    IntersectionTest()
