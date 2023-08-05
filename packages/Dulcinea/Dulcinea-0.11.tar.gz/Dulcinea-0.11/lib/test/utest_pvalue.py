"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_pvalue.py $
$Id: utest_pvalue.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea.physical_unit import UnitCollection
from dulcinea.physical_value import PhysicalValue, UnitError
from dulcinea.range_value import RangeValue
from sancho.utest import UTest


class PhysicalValueTest (UTest):

    def _pre (self):
        self.units = units = UnitCollection()
        units.add_unit('ft', units['inch'], 12)
        units.add_unit('km', units['m'], 1000)
        units.add_unit('mile', units['ft'], 5280)
        units.add_unit('L', units['m^3'], 0.1**3)
        units.add_unit('galUS', units['L'], 3.785411784)

        meters = units.get_unit('m')

        # an amusing collection of physical values to play with
        self.len1 = PhysicalValue(1.0, meters)
        self.len1a = PhysicalValue(1, meters)
        self.len2 = PhysicalValue(2.0, meters)
        self.len3 = PhysicalValue(3, units['ft'])
        self.len4 = PhysicalValue(36, units['inch'])
        self.len5 = PhysicalValue(RangeValue(3.0, 5.0), units['cm'])

        self.time1 = PhysicalValue(15, units['s'])
        self.time2 = PhysicalValue(0.5, units['min'])
        self.nounit1 = PhysicalValue(0.5)
        self.nounit2 = PhysicalValue(1.0)

    def check_basics(self):
        meters = self.units.get_unit('m')
        (len1, len1a, len2, len5) = \
            (self.len1, self.len1a, self.len2, self.len5)

        assert len1.unit is len2.unit
        assert len1.get_unit() is len2.get_unit()
        assert len2.get_unit() == meters
        assert len2.get_unit_name() == "m"
        assert len1.value == 1.0
        assert len1.get_value() == 1.0
        assert len2.value == 2.0
        assert len2.get_value() == 2.0

        assert self.nounit1.get_unit_name() == None

        assert len1.get_type() == float
        assert len1a.get_type() == float
        assert len5.get_type() == RangeValue

        try:
            PhysicalValue(RangeValue(1L, 2L))
            assert 0
        except TypeError: pass
        try:
            PhysicalValue( (1,2) )
            assert 0
        except TypeError: pass

    def check_format(self):
        (nounit1, len4, len5) = (self.nounit1, self.len4, self.len5)

        assert str(nounit1) == "0.5"
        assert nounit1.format() == "0.5"
        assert str(len4) == "36.0 inch"
        assert len4.format() == "36 inch"
        assert str(len5) == "3.0 .. 5.0 cm"
        assert len5.format() == "3 .. 5 cm"

        assert nounit1.format(html=1) == "0.5"
        assert nounit1.format(show_unit=0) == "0.5"
        assert len4.format(html=1) == "36&nbsp;inch"
        assert len4.format(show_unit=0) == "36"
        assert len4.format(show_unit=0, html=1) == "36"

        self.units.get_unit("um").set_name("um", "&micro;m")
        a = PhysicalValue(2, self.units.get_unit("um"))
        assert a.format() == "2 um"
        assert a.format(html=1) == "2&nbsp;&micro;m"
        b = a/3
        assert b.format() == "0.666667 um"
        assert b.format(html=1) == "0.666667&nbsp;&micro;m"
        c = a*4
        assert c.format() == "8 um"
        assert c.format(html=1) == "8&nbsp;&micro;m"
        d = a/1
        assert d.format() == "2 um"
        assert d.format(html=1) == "2&nbsp;&micro;m"
        e = a*1
        assert e.format() == "2 um"
        assert e.format(html=1) == "2&nbsp;&micro;m"

        pv = PhysicalValue(32078.1, self.units.get_unit("Ang"))
        assert pv.format() == "32078.1 Ang"
        assert pv.format(html=1) == "32078.1&nbsp;&Aring;"
        pv = pv.convert(self.units.get_unit("m"))
        assert pv.format() == "3.20781e-06 m"
        assert pv.format(html=1) == "3.20781e-06&nbsp;m"


    def check_compatible(self):
        meters = self.units.get_unit('m')
        sec = self.units.get_unit('s')
        mps = meters/sec

        (len1, len5) = (self.len1, self.len5)
        t1 = PhysicalValue(30, sec)

        assert len1.unit_compatible(meters)
        assert len5.unit_compatible(meters)

        assert len1.unit_compatible(len5)
        assert t1.unit_compatible(self.units.get_unit('hour'))
        assert t1.unit_compatible(t1)
        assert (len1/t1).unit_compatible(mps)

        assert not len1.unit_compatible(meters/sec)
        assert not t1.unit_compatible(meters)

        nodim = meters/meters
        assert not self.nounit1.unit_compatible(meters)
        assert not self.nounit1.unit_compatible(len1)
        assert self.nounit1.unit_compatible(self.nounit2)
        assert self.nounit1.unit_compatible(None)
        assert self.nounit1.unit_compatible(nodim)


    def check_dimension(self):
        assert self.len1.is_dimension('length')
        assert not self.len1.is_dimension('time')
        assert not self.nounit1.is_dimension('length')


    def check_cmp(self):
        (len1, len1a, len2) = (self.len1, self.len1a, self.len2)

        # compare "1.0 m" and "2.0 m"
        assert len1 != len2
        assert len1 < len2
        assert len1 <= len2
        assert len2 > len1
        assert len2 >= len1

        # compare "1.0 m" and "1 m" (float vs int)
        assert len1 == len1a
        assert len1 <= len1a
        assert len1 >= len1a

        # compare compatible but different units
        (time1, time2) = (self.time1, self.time2)
        assert time1 < time2
        assert time2 > time1
        assert time1 != time2
        time2.value = 0.25            # 0.25 min = 15 s
        assert time1 == time2
        assert time2 == time1
        assert not time1 < time2
        assert not time1 > time2
        assert time1 <= time2
        assert time1 >= time2

        # sign differences (-1 m != 1 m)
        len1_neg = PhysicalValue(-self.len1.value, self.len1.unit)
        assert len1 != len1_neg
        assert len1_neg != len1
        assert len1_neg == len1_neg

        # compare unitless PhysicalValues
        (nounit1, nounit2) = (self.nounit1, self.nounit2)
        assert nounit1 < nounit2
        assert nounit2 > nounit1
        assert not nounit2 == nounit1
        assert nounit1 == 0.5
        assert nounit1 != 25
        assert nounit1 != 'bogus'
        assert nounit1 > 0.4
        assert nounit2 < 2

        # nonsensical comparisons (units vs no units, or incompatible units)
        assert len1 != 1
        assert len2 != 0.0
        assert not len1 == nounit1
        assert not len2 == time1
        try:
            len1 < 1
            assert 0
        except UnitError: pass
        try:
            len2 >= 0.0
            assert 0
        except UnitError: pass
        try:
            len1 < nounit1
            assert 0
        except UnitError: pass
        try:
            len2 > 'bogus'
            assert 0
        except UnitError: pass

    def check_cmp_roundoff(self):
        "compare values that expose round-off errors: 16"

        pv1 = PhysicalValue(100, self.units.get_unit("um"))
        pv2 = PhysicalValue(100000, self.units.get_unit("nm"))
        # these all require conversion; which direction the conversion
        # goes determines which are susceptible to round-off problems!
        assert pv1 == pv2
        assert pv2 == pv1
        assert pv1 <= pv2
        assert pv2 <= pv1
        assert pv1 >= pv2
        assert pv2 >= pv1

        pv3 = pv1.convert(pv2.unit)
        pv4 = pv2.convert(pv1.unit)
        # these should require no conversion: the arithmetic has been done
        assert pv3 == pv2
        assert pv2 == pv3
        assert pv4 == pv1
        assert pv1 == pv4

        # these require even more conversions (eg. *back* to original
        # units), so the round-off should be even worse
        assert pv3 == pv1
        assert pv1 == pv3
        assert pv4 == pv2
        assert pv2 == pv4
        assert pv3 == pv4
        assert pv4 == pv3

    def check_convert(self):
        (len1, len1a, len2) = (self.len1, self.len1a, self.len2)
        units = self.units
        m = units.get_unit('m')
        s = units.get_unit('s')
        cm = units.get_unit('cm')
        inch = units.get_unit('inch')

        # convert to same unit (m -> m)
        assert len1a.convert(m).get_tuple() == (1, m)

        # convert m -> cm
        assert len1.convert(cm).get_tuple() == (100, cm)

        # convert m -> inch
        metre = len1a.convert(inch)
        assert round(metre.get_value(), 2) == 39.37

        # error case: m -> sec
        try:
            len1.convert(s)
            assert 0
        except UnitError: pass


    def check_add(self):
        foot = self.units.get_unit('ft')
        inch = self.units.get_unit('inch')
        (len1, len1a, len2, len3, len4) = \
            (self.len1, self.len1a, self.len2, self.len3, self.len4)

        # simple addition/subtraction (identical units)
        assert len1 + len1 == len2
        assert len1 + len1a == len2
        assert len2 - len1 == len1
        assert len2 - len1a == len1

        # compatible units -- make sure it preserves the unit of the
        # first one!
        assert (len3 + len4).get_tuple() == (6, foot)
        assert (len4 + len3).get_tuple() == (72, inch)

        assert round((len3 - len4).get_value(), 4) == 0
        assert round((len4 - len3).get_value(), 4) == 0

        # error case: incompatible units
        time1 = self.time1
        try:
            len1 + time1
            assert 0
        except UnitError: pass
        try:
            time1 - len1
            assert 0
        except UnitError: pass

        # two unitless PhysicalValues
        (nounit1, nounit2) = (self.nounit1, self.nounit2)
        assert nounit1 + nounit2 == PhysicalValue(1.5)
        assert nounit1 - nounit2 == PhysicalValue(-0.5)

        # unitless PhysicalValue with a regular number (and vice-versa)
        assert nounit1 + 1 == PhysicalValue(1.5)
        assert nounit1 - 1 == PhysicalValue(-0.5)
        assert 1 + nounit1 == PhysicalValue(1.5)
        assert 1 - nounit1 == PhysicalValue(0.5)

        # unitless PhysicalValue with a RangeValue
        rv = RangeValue(3.0, 4.5)
        assert nounit1 + rv == PhysicalValue(RangeValue(3.5, 5.0))
        assert rv + nounit1 == PhysicalValue(RangeValue(3.5, 5.0))
        assert nounit1 - rv == PhysicalValue(RangeValue(-4.0, -2.5))
        assert rv - nounit1 == PhysicalValue(RangeValue(2.5, 4.0))

        # error case: PhysicalValue-with-unit with a unitless
        # PhysicalValue
        try:
            len1 + nounit1
            assert 0
        except UnitError: pass
        try:
            nounit1 + len1
            assert 0
        except UnitError: pass

        # error case: PhysicalValue-with-unit with a regular number
        try:
            len1 + 2.0
            assert 0
        except UnitError: pass
        try:
            2.0 + len1
            assert 0
        except UnitError: pass
        try:
            2.0 - len1
            assert 0
        except UnitError: pass

        # error case: PhysicalValue with some random object (not another
        # PV, not a simple number, not a range)
        try:
            len1 + 'foo'
            assert 0
        except TypeError: pass

    def check_mult(self):
        units = self.units
        m = units.get_unit('m')
        s = units.get_unit('s')
        min = units.get_unit('min')
        msq = units.get_unit('m*m', 1)
        foot = units.get_unit('ft')
        fsq = units['ft'] * units['ft']
        ftm = foot * m                  # "foot-meters"? whatever...
        ftinch = units.get_unit('ft') * units.get_unit('inch')
        minv = units.create_unit("minv", None, (-1, 0, 0, 0, 0, 0, 0), 1.0)

        (len1, len2, len3, len4) = (self.len1, self.len2, self.len3, self.len4)
        (time1, time2) = (self.time1, self.time2)

        # identical units
        assert (len1 * len2).get_tuple() == (2, msq)
        assert (len2 * len2).get_tuple() == (4, msq)
        assert (len1 * len2).get_tuple() == (2, msq)
        assert (len1 / len1).get_tuple() == (1, None)
        assert (len1 / len2).get_tuple() == (0.5, None)

        # compatible units: 1 m * 3 ft = 3 ft*m = .9144 m^2 = 9.84 ft^2
        area = len1 * len3
        assert area.get_tuple() == (3, ftm)
        assert round(area.convert(msq).get_value(),4) == .9144
        assert round(area.convert(fsq).get_value(),4) == 9.8425

        # 1 m / 3 ft = 1 m / .9144 m = 1.0936 (dimensionless quantity)
        assert round((len1 / len3).get_value(), 4) == 1.0936

        # incompatible units: the dimensions just pile up
        assert (len2 * time1).get_tuple() == (2.0*15, m*s)
        assert (len2 / time1).get_tuple() == (2.0/15, m/s)
        assert round((len2 / time1).convert(foot/min).get_value(),
                     4) == 26.2467

        # Combine unitless and "unitfull" PhysicalValue
        (nounit1, nounit2) = (self.nounit1, self.nounit2)
        assert (nounit1 * len2).get_tuple() == (1.0, m)
        assert (len2 * nounit1).get_tuple() == (1.0, m)
        assert (nounit1 / len2).get_tuple() == (0.25, minv)
        assert (len2 / nounit1).get_tuple() == (4.0, m)

        # Ditto, but now use a regular number in place of a unitless
        # PhysicalValue
        assert (0.5 * len2).get_tuple() == (1.0, m)
        assert (len2 * 0.5).get_tuple() == (1.0, m)
        assert (0.5 / len2).get_tuple() == (0.25, minv)
        assert (len2 / 0.5).get_tuple() == (4.0, m)

        rv = RangeValue(1.5, 2.5)
        assert (len1 * rv).get_tuple() == (RangeValue(1.5, 2.5), m)
        assert (rv * len1).get_tuple() == (RangeValue(1.5, 2.5), m)
        try:
            len1 / rv
            assert 0
        except TypeError: pass
        assert (rv / len1).get_tuple() == (RangeValue(1.5, 2.5), minv)

        try:
            len1 * 'foo'
            assert 0
        except TypeError: pass


if __name__ == "__main__":
    PhysicalValueTest()
