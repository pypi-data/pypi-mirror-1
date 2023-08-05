"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/tolerance.py $
$Id: tolerance.py 27417 2005-09-14 18:19:15Z dbinger $
"""
from dulcinea.base import DulcineaBase
from dulcinea.spec import either, require, add_getters

class Tolerance (DulcineaBase):
    """
    A tolerance value can be associated with another value (e.g. a
    Parameter) in order to specify the relative tolerance (in percent) of
    that value.
    """

    lo_is = either(int, long, float)
    hi_is = either(int, long, float)

    def __init__(self, hi, lo=None):
        assert hi >= 0
        require(hi, float)
        if lo is None:
            lo = hi
        else:
            assert lo >= 0
            require(lo, float)
        self.hi = hi
        if abs(hi - lo) < 1e-9:
            lo = hi # avoid having to compare with fudge elsewhere
        self.lo = lo

    def __str__(self):
        return self.format()

    def format(self, html=0):
        if html:
            plusminus = '&plusmn;' # a one character version of +/-
        else:
            plusminus = '+/-'
        if self.hi == self.lo:
            return '%s%g%%' % (plusminus, self.hi)
        else:
            return '+%g%%/-%g%%' % (self.hi, self.lo)

    def __hash__(self):
        return hash((self.lo, self.hi))

    def is_symmetric(self):
        """Return true if the high and low magnitudes are the same."""
        return self.hi == self.lo

add_getters(Tolerance)
