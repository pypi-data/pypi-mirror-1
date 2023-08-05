"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/physical_value.py $
$Id: physical_value.py 27528 2005-10-07 20:50:40Z dbinger $
"""
from dulcinea import local
from dulcinea.base import DulcineaBase
from dulcinea.numeric import near_cmp
from dulcinea.physical_unit import PhysicalUnit, UnitError
from dulcinea.range_value import RangeValue
from dulcinea.spec import spec, either, add_getters, string
from quixote.html import htmltext, stringify
import operator


def _rsub(a, b):
    return b - a

def _rdiv(a, b):
    return b / a


class PhysicalValue (DulcineaBase):
    """
    A physical value: a number (or range value) tied to a physical
    unit that automatically performs unit conversion when arithmetic
    operations are performed.
    """

    value_is = spec(
        either(float, RangeValue),
        "the numerical part of the physical value")
    unit_is = spec(
        (None, PhysicalUnit),
        "the unit")

    def __init__(self, value, unit=None):
        self._set_value(value)
        if unit is None or isinstance(unit, PhysicalUnit):
            self.unit = unit
        elif string(unit):
            # for convenience, only works if get_standard_units is defined
            self.unit = local.get_standard_units().get_unit(unit)
        else:
            raise ValueError, 'invalid unit %r' % unit

    def __str__(self):
        if self.unit:
            return "%s %s" % (self.value, self.unit)
        else:
            return stringify(self.value)

    def __hash__(self):
        return hash((self.value, self.unit))

    def is_range(self):
        """Test if value is a RangeValue"""
        return isinstance(self.value, RangeValue)

    def format(self, html=0, show_unit=1):
        if self.is_range():
            value = self.value.format()
        else:
            value = "%g" % self.value
        if self.unit and show_unit:
            if html: space = htmltext("&nbsp;")
            else:    space = " "
            result = value + space + self.unit.get_name(html=html)
        else:
            result = value
        return result

    def get_tuple(self):
        return (self.value, self.unit)

    def get_unit_name(self, html=0):
        if self.unit is None:
            return None
        else:
            return self.unit.get_name(html)

    def get_type(self):
        if hasattr(self.value, '__class__'):
            return self.value.__class__
        else:
            return type(self.value)

    def _set_value(self, value):
        # We permit only float and RangeValue of float for the "value"
        # of a PhysicalValue.  Int and range of int both get coerced,
        # to float or range of float respectively. Anything else is a
        # TypeError.

        if value is None:
            raise ValueError, "value can't be None"

        if isinstance(value, int):
            self.value = float(value)

        elif isinstance(value, RangeValue):
            rtype = value.get_type()
            if rtype is int:
                self.value = value.to_float() # makes a copy
            elif rtype is float:
                self.value = value
            else:
                raise TypeError, "range values must be int or float ranges"

        elif isinstance(value, float):
            self.value = value

        else:
            raise TypeError, ("invalid value %s for PhysicalValue: "
                              "must be int, float, range of int, or "
                              "range of float" % `value`)

    def unit_compatible(self, other):
        """(other : PhysicalValue|PhysicalUnit) -> boolean

        Returns true if the PhysicalValue's unit is compatible with
        'other', which may be a PhysicalValue or a PhysicalUnit.
        """
        if self.unit is None:           # self is dimensionless
            unitless_pv = (isinstance(other, PhysicalValue) and
                           other.unit is None)
            dimless_unit = (isinstance(other, PhysicalUnit) and
                            other.is_dimensionless())
            return (unitless_pv or dimless_unit or other is None)

        if isinstance(other, PhysicalValue):
            return self.unit.is_compatible(other.get_unit())
        elif isinstance(other, PhysicalUnit):
            return self.unit.is_compatible(other)
        else:
            raise ValueError, 'invalid unit %r' % other


    def is_dimension(self, name):
        if self.unit is not None:
            return self.unit.is_dimension(name)
        else:
            return 0

    def _additive_op(self, other, primitive_op):

        # for arithmetic ops where the units must match, ie. addition
        # and subtraction

        # case 1: adding (subtracting) two PhysicalValue instances
        if isinstance(other, PhysicalValue):
            # case 1a: both self and other have a unit (if they are
            # incompatible, that'll be caught in PhysicalUnit)
            if (self.unit is not None) and (other.unit is not None):
                if self.unit == other.unit:
                    other_value = other.value
                else:
                    other_value = other.unit.convert_value(
                        other.value, self.unit)
                return self.__class__(primitive_op(self.value, other_value),
                                      self.unit)

            # case 1b: neither self nor other has a unit
            elif (self.unit is None) and (other.unit is None):
                return self.__class__(primitive_op(self.value, other.value),
                                      None)

            # case 1c: one of them has a unit, but the other does not
            else:
                raise UnitError, \
                      ("either both values must have a unit, "
                       "or both must be unitless")

        # case 2: adding (subtracting) a PhysicalValue and a scalar or range
        elif isinstance(other, (int, long, float, RangeValue)):
            # case 2a: the PhysicalValue is unitless, so it's OK to
            # add/subtract a non-PhysicalValue
            if self.unit is None:
                return self.__class__(primitive_op(self.value, other), None)

            # case 2b: the PhysicalValue has a unit -- bomb!
            else:
                raise UnitError, \
                      ("either both values must be physical values, "
                       "or the physical value must be unitless")

        else:
            return NotImplemented


    def _mult_op(self, other, primitive_op):

        # case 1: multiplying (dividing) two PhysicalValue instances
        if isinstance(other, PhysicalValue):
            assert primitive_op is not _rdiv, \
                   "rdiv impossible: self and other are both PhysicalValues"

            # case 1a: both values have a unit -- don't do any conversion,
            # it's all handled by arithmetic on the units
            if (self.unit is not None) and (other.unit is not None):
                value = primitive_op(self.value, other.value)
                unit = primitive_op(self.unit, other.unit)

                # If all dimensions are zero, then all units cancelled
                # out.  Convert the value to the "standard" no-unit
                # unit, so there's no more useful information lurking in
                # the unit object and we can get rid of it.  (Eg. if we
                # divide "3 m / 1 ft", at this point we'd have "3 m/ft",
                # which is dimensionless but has the conversion factor
                # 3.28 (number of feet in a metre) hidden in the
                # dimensionless "unit".  That's bad -- "3 m / 1 ft" is
                # really the dimensionless quantity "9.84" (= "3 m /
                # .3048 m"), at least if the SI is your fundamental
                # system.  Hence, we convert from some arbitrary
                # dimensionless unit (could have any conversion factor)
                # to the "standard" dimensionless unit (conversion
                # factor = 1).
                #
                # Note that this is different from how we act if the
                # units *don't* cancel out: if you divide miles/hour,
                # you get miles/hour.  This is definitely the right
                # thing to do; it's the units-cancel-out case that's
                # tricky, and I think that ferreting out the hidden
                # conversion factor is the "least-surprise" way of
                # operating.
                #if reduce(operator.add, map (abs, unit.get_powers())) == 0:
                if unit.is_dimensionless():
                    value = unit.convert_value(value)
                    unit = None

                return self.__class__(value, unit)

            # case 1b: self is unitless, but other has a unit -- we either
            # use other's unit or its inverse (if dividing)
            elif (self.unit is None) and (other.unit is not None):
                if primitive_op is operator.mul:
                    unit = other.unit
                elif primitive_op is operator.div:
                    unit = other.unit.inv()
                return self.__class__(primitive_op(self.value, other.value),
                                      unit)

            # case 1c: other is unitless, so self's unit doesn't matter
            # (we're just scaling self's value)
            else:
                return self.__class__(primitive_op(self.value, other.value),
                                      self.unit)

        # case 2: multiplying a PhysicalValue by a number or
        # range -- this is just like 1c, except we use 'other'
        # instead of 'other.value'
        elif isinstance(other, (int, long, float, RangeValue)):
            if primitive_op is _rdiv:
                unit = self.unit.inv()
            else:
                unit = self.unit
            return self.__class__(primitive_op(self.value, other), unit)

        else:
            return NotImplemented

    def __add__(self, other):
        return self._additive_op(other, operator.add)

    __radd__ = __add__                  # addition is still commutative!

    def __sub__(self, other):
        return self._additive_op(other, operator.sub)

    def __rsub__(self, other):
        return self._additive_op(other, _rsub)

    def __mul__(self, other):
        return self._mult_op(other, operator.mul)

    __rmul__ = __mul__                  # yep, this one's commutative too

    def __div__(self, other):
        return self._mult_op(other, operator.div)

    def __rdiv__(self, other):
        return self._mult_op(other, _rdiv)

    def __eq__(self, other):
        other = self.get_comparable_value(other)
        if isinstance(self.value, RangeValue) or isinstance(other, RangeValue):
            return self.value == other
        else:
            return 0 == near_cmp(self.value, other)

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        other = self.get_required_comparable_value(other)
        if isinstance(self.value, RangeValue) or isinstance(other, RangeValue):
            return self.value > other
        else:
            return 1 == near_cmp(self.value, other)

    def __le__(self, other):
        return not self > other

    def __lt__(self, other):
        other = self.get_required_comparable_value(other)
        if isinstance(self.value, RangeValue) or isinstance(other, RangeValue):
            return self.value < other
        else:
            return -1 == near_cmp(self.value, other)

    def __ge__(self, other):
        return not self < other

    def get_comparable_value(self, other):
        """( any ) -> float | int | long | None

        Return a number that represents the other,
        expressed in the units of self.
        If there isn't any sensible number to return, return None.
        """
        if isinstance(other, PhysicalValue):
            if self.unit is other.unit:
                return other.value
            elif (self.unit is not None and
                  other.unit is not None and
                  self.unit.powers == other.unit.powers):
                return other.unit.convert_value(other.value, self.unit)
        elif self.unit is None and isinstance(other, (int, long, float)):
            return other
        return None

    def get_required_comparable_value(self, other):
        """( any ) -> float | int | long

        Return a number that represents the other,
        expressed in the units of self.
        If there isn't any sensible number to return,
        raise an UnitError exception.
        """
        val = self.get_comparable_value(other)
        if val is None:
            raise UnitError, "can't compare %s to %s" % (`self`, `other`)
        return val

    def convert(self, target_unit):
        """(target_unit : PhysicalUnit) -> PhysicalValue

        Return a (possibly new) PhysicalValue instance with the current
        instance's value converted to 'target_unit'.
        """
        if self.unit is target_unit:
            return self
        return self.__class__(self.unit.convert_value(self.value, target_unit),
                              target_unit)

    def get_min(self):
        if self.is_range():
            return PhysicalValue(self.value.get_min(), self.unit)
        return self

    def get_max(self):
        if self.is_range():
            return PhysicalValue(self.value.get_max(), self.unit)
        return self

    def in_range(self, other):
        if self.is_range():
            return self.value.in_range(self.get_comparable_value(other))
        return self == other

add_getters(PhysicalValue)
