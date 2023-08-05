"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/numeric.py $
$Id: numeric.py 27372 2005-09-13 14:06:21Z dbinger $

Provides near_cmp()
"""


def near_cmp(x, y, fudge = 2.5e-16):
    """Compare two numbers (presumably floating-point) with a fudge
    factor to account for accumulated round-off error.  Returns
    0, < 0, or > 0 just like the builtin 'cmp()'.
    """
    # The fudge factor for floating-point comparisons is 2.5e-16: this
    # is based on DBL_EPSILON from <float.h>, which is
    # 2.2204460492503131e-16 on every C compiler/hardware combination I
    # have access to right now (GCC/Intel, GCC/SPARC, GCC/MIPS, and
    # SGI/MIPS).  Must be an IEEE thing.

    if x is None or y is None:
        return cmp(x, y)
    elif isinstance(x, float) or isinstance(y, float):
        if x == 0.0 or y == 0.0:
            if abs(x - y) < fudge:
                return 0
        elif abs((x - y) / x) < fudge:
            return 0
    return cmp(x, y)


