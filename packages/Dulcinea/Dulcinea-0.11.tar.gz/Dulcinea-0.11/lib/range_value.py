"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/range_value.py $
$Id: range_value.py 27380 2005-09-13 14:18:25Z dbinger $

Provides the RangeValue class.
"""

from dulcinea.base import DulcineaBase
from dulcinea.numeric import near_cmp
from dulcinea.spec import either

class RangeValue (DulcineaBase):
    """
    A numeric range.
    """
    lo_is = either(int, long, float)
    hi_is = either(int, long, float)

    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi
        if type(self.lo) is not type(self.hi):
            raise TypeError, "inconsistent types: %s and %s" % \
                  (self.lo, self.hi)
        if type(self.lo) not in (float, int, long):
            raise TypeError, "range endpoint must be float, int, or long"
        if self.lo > self.hi:
            raise ValueError, \
                  "backwards range: %s > %s" % (self.lo, self.hi)

    def __str__ (self):
        return "%s .. %s" % (self.lo, self.hi)

    def __hash__(self):
        return hash((self.lo, self.hi))

    def get_min(self):
        return self.lo

    def get_max(self):
        return self.hi

    def get_tuple(self):
        return (self.lo, self.hi)

    def get_type(self):
        return type(self.lo)

    def format(self):
        if self.lo == self.hi:
            return "%g" % self.lo
        else:
            return "%g .. %g" % (self.lo, self.hi)


    # A lot of arithmetic operations aren't supported since it's not clear what
    # they should mean.  Arithmetic operations involving two range values are
    # not supported at all.

    def __add__(self, other):
        if isinstance(other, (int, long, float)):
            return self.__class__(self.lo + other, self.hi + other)
        else:
            return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, (int, long, float)):
            return self.__class__(self.lo - other, self.hi - other)
        else:
            return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, (int, long, float)):
            return self.__class__(other - self.hi, other - self.lo)
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, long, float)):
            return self.__class__(self.lo * other, self.hi * other)
        else:
            return NotImplemented

    __rmul__ = __mul__

    def __div__(self, other):
        if isinstance(other, (int, long, float)):
            return self.__class__(self.lo / other, self.hi / other)
        else:
            return NotImplemented

    def __rdiv__(self, other):
        return NotImplemented

    def to_float(self):
        return self.__class__(float(self.lo),
                              float(self.hi))

    def __eq__(self, other):
        if isinstance(other, RangeValue):
            if isinstance(self.lo, float):
                return (near_cmp(self.lo, other.lo) == 0 and
                        near_cmp(self.hi, other.hi) == 0)
            else:
                return self.lo == other.lo and self.hi == other.hi
        else:
            return False

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        """
        Comparison is not well-defined for intervals, but this is
        provided anyway so that sorting does not fail.
        """
        if isinstance(other, RangeValue):
            return self.get_min() < other.get_min()
        else:
            return True # arbitrary

    def in_range(self, other):
        """Return true if 'other' is inside the range, ie. >= the low end
        and <= the high end.
        """
        if isinstance (other, RangeValue):
            return (near_cmp(self.lo, other.lo) <= 0 and
                    near_cmp(self.hi, other.hi) >= 0)
        elif isinstance(other, (int, long, float)):
            return (near_cmp(self.lo, other) <= 0 and
                    near_cmp(self.hi, other) >= 0)
        else:
            return False






