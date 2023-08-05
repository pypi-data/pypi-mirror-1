"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/set_utils.py $
$Id: set_utils.py 27506 2005-09-30 18:49:55Z dbinger $

Provides utility functions for performing set operations with range values,
such as intersection and union.
"""
from dulcinea.physical_value import PhysicalValue
from dulcinea.range_value import RangeValue
from dulcinea.spec import require, either

def in_set(val, set):
    """(val : any, set : list|tuple) -> boolean

    Return true if 'val' is in 'set'. If set contains any ranges it will
    return true if 'val' is within one of those ranges.
    """
    require(set, either(list, tuple))
    for item in set:
        if val == item:
            return 1
        elif (isinstance(item, (RangeValue, PhysicalValue)) and
              item.in_range(val)):
            return 1
    return 0

def get_range_intersection(range1, range2):
    """( RangeValue | int | long | float,
         RangeValue | int | long | float ) ->
         None | RangeValue | int | long | float

    Returns the intersection.
    """
    def lo_hi(x):
        if isinstance(x, RangeValue):
            return x.get_min(), x.get_max()
        else:
            require(x, either(int, long, float))
            return x, x

    lo1, hi1 = lo_hi(range1)
    lo2, hi2 = lo_hi(range2)

    lo = max(lo1, lo2)
    hi = min(hi1, hi2)

    if lo > hi:
        return None
    elif lo == hi:
        return lo
    else:
        return RangeValue(lo, hi)


def _get_physical_value_intersection(physical_value1, physical_value2):
    require(physical_value1, PhysicalValue)
    require(physical_value2, PhysicalValue)
    range2 = physical_value1.get_comparable_value(physical_value2)
    if range2 is None:
        return None
    intersection = get_range_intersection(physical_value1.get_value(), range2)
    if intersection is None:
        return None
    else:
        return PhysicalValue(intersection, physical_value1.get_unit())

def get_set_intersection(set1, set2):
    """( list , list ) -> list

    Returns the intersection of two sets. For sets containing ranges, all of
    the items in the two sets must be either numbers (RangeValue, int, long,
    float) or PhysicalValues.
    """
    require(set1, list)
    require(set2, list)
    set = []
    for item1 in set1:
        for item2 in set2:
            if item1 == item2:
                intersection = item1
            elif isinstance(item1, PhysicalValue):
                intersection = _get_physical_value_intersection(item1, item2)
            elif (isinstance(item1, RangeValue) or
                  isinstance(item2, RangeValue)):
                intersection = get_range_intersection(item1, item2)
            if intersection is not None:
                set.append(intersection)
    return set

