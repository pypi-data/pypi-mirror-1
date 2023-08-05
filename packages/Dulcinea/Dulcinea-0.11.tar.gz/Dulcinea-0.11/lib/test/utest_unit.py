"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_unit.py $
$Id: utest_unit.py 27507 2005-09-30 19:10:57Z dbinger $
"""
from sancho.utest import UTest, raises
from dulcinea.physical_unit import PhysicalUnit, UnitCollection, UnitError
from dulcinea.spec import get_spec_problems

class PhysicalUnitTest (UTest):

    def _pre (self):
        self.units = UnitCollection()

    def _post (self):
        del self.units

    def get_units (self, *names):
        return [self.units[name] for name in names]


    def check_basics (self):
        "basic unit finding and conversion"
        units = self.units

        # Assume these units already exist.
        kilogram = units['kg']
        gram = units['g']
        metre = units['m']
        inch = units['inch']

        assert kilogram.name == "kg"
        assert kilogram.get_name() == "kg"
        assert kilogram.get_name(html=1) == "kg"

        assert kilogram.factor == 1.0
        assert kilogram.offset == 0.0
        assert not kilogram.artificial

        assert kilogram.convert_value(1.5, gram) == 1500.0
        assert round(metre.get_conversion_factor(inch), 2) == 39.37

        get_unit = units.get_unit
        assert get_unit('kg') == kilogram
        assert (kilogram*metre).artificial
        assert get_unit('kg*m').artificial
        raises(TypeError, get_unit, 66)
        assert kilogram.is_dimension('mass')
        assert metre.is_dimension('length')
        assert units['Torr'].is_dimension('pressure')
        for a, b in units.si_units.items():
            print repr((a, b)), type(a), type(b)
        assert get_spec_problems(units) == [], get_spec_problems(units)
        assert get_spec_problems(kilogram) == []

    def check_temperature (self):
        units = self.units
        degF = units.get_unit('degF')
        degC = units.get_unit('degC')
        kelvin = units.get_unit('K')

        warm_day = 80                   # in fahrenheit
        cold_day = 0                    # in fahrenheit
        fpw = 0                         # "freezing point of water" in celsius
        htsc = 70                       # "high temperature" superconductivity
                                        # (at a brisk 70 K)
        abs_zero = 0                    # in kelvin

        assert round(degF.convert_value(warm_day, degC),2) == 26.67
        assert round(degF.convert_value(warm_day, kelvin),2) == 299.82

        assert round(degF.convert_value(cold_day, degC),2) == -17.78
        assert round(degF.convert_value(cold_day, kelvin),2) == 255.37

        assert degC.convert_value(fpw, degC) == fpw
        assert round(degC.convert_value(fpw, degF),2) == 32.00
        assert round(degC.convert_value(fpw, kelvin),2) == 273.15

        assert round(kelvin.convert_value(htsc, degC),2) == -203.15
        assert round(kelvin.convert_value(htsc, degF),2) == -333.67

        assert round(kelvin.convert_value(abs_zero, kelvin),2) == 0
        assert round(kelvin.convert_value(abs_zero, degC),2) == -273.15
        assert round(kelvin.convert_value(abs_zero, degF),2) == -459.67

        assert degC.is_dimension('temperature')
        assert degF.is_dimension('temperature')
        assert kelvin.is_dimension('temperature')
        assert not kelvin.is_dimension('mass')


    def check_conversion (self):
        "conversion functions on unit collection"
        units = self.units
        inch = units.get_unit('inch')
        mm = units.get_unit('mm')
        degC = units.get_unit('degC')
        degF = units.get_unit('degF')
        K = units.get_unit('K')
        assert round(units.convert_value(6, inch, mm), 2) == 152.4
        assert round(units.convert_value(0, degC, degC), 2) == 0.0
        assert round(units.convert_value(0, degC, degF), 2) == 32.00
        assert round(units.convert_value(0, degC, K), 2) == 273.15

    def check_add_units (self):
        "define alternate units and convert to/from them"

        units = self.units
        units.add_unit('ft', units['inch'], 12)
        units.add_unit('yard', units['ft'], 3)

        yard = units.get_unit('yard')
        assert round(yard.get_conversion_factor(), 4) == .9144
        inch = units.get_unit('inch')
        assert inch.powers == (1, 0, 0, 0, 0, 0, 0)
        assert round(inch.factor, 5) == 0.0254

        unit = units['ft'] / units['min']
        assert unit.powers == (1, 0, -1, 0, 0, 0, 0)
        assert round(unit.factor, 5) == 0.00508
        assert round(units.convert_value(3, units['yard'],
                                         units['m']), 4) == 2.7432
        assert round(units.convert_value(500, units['s'],
                                         units['hour']), 4) == .1389

    def check_implicit (self):
        "implicit unit definition"

        units = self.units

        units.add_unit('ft', units['inch'], 12)
        units.add_unit('mile', units['ft'], 5280)
        mph = units['mile'] / units['hour']
        assert units['mile/hour'] is mph

        mps = units.get_unit('m/s', 1)
        ipm = units['inch'] / units['min']
        assert round(ipm.convert_value(1.5, mps), 7) == 6.35e-4
        assert round(ipm.convert_value(1.5, mph), 6) == 1.42e-3

    def check_compare (self):
        units = self.units
        units.get_unit("cm")
        (metre, centimetre, inch, sec, hertz) = \
            self.get_units('m', 'cm', 'inch', 's', 'Hz')

        assert metre == metre
        assert not metre == centimetre
        assert metre.is_compatible(centimetre)
        assert metre.is_compatible(inch)
        assert not metre.is_compatible(None)

        assert not sec.is_compatible(hertz)
        assert sec.is_dimension('time')
        assert sec.is_inverse_compatible(hertz)

        assert hertz.is_dimension('frequency')

        metre2 = PhysicalUnit("m", metre.powers, units)
        metre3 = PhysicalUnit("foo", metre.powers, units)
        assert metre == metre2
        assert metre == metre3

        # This depends on the list of temperature units defined in
        # UnitCollection.  There aren't that many temperature units in
        # the world, though, so it's unlikely that we'd add more and
        # break this test.
        temp_units = units.get_compatible_units('degC')
        temp_units = [(u.factor, u.name) for u in temp_units]
        temp_units.sort()
        assert temp_units == [(5./9, 'degF'), (1, 'K'), (1, 'degC')]

        time_units = [(u.factor, u.name)
                      for u in units.get_compatible_units('s')]
        time_units.sort()
        expect = [(1, 's'), (60, 'min'), (60*60, 'hour'),
                  (60*60*24, 'day'), (60*60*24*7, 'week')]
        assert time_units == expect

        # Test that implicit addition affects get_compatible_units()
        units.get_unit("us")
        units.get_unit("ms")
        time_units = [(u.factor, u.name)
                      for u in units.get_compatible_units('s')]
        time_units.sort()
        expect = [(1e-6, "us"), (1e-3, "ms")] + expect
        assert time_units == expect


    def check_arith1 (self):
        self.units.get_unit("cm")
        (metre, centimetre, inch) = \
            self.get_units('m', 'cm', 'inch')

        scaled_cm = centimetre*100.0
        assert scaled_cm.powers == metre.powers
        assert scaled_cm.factor == metre.factor
        assert metre is scaled_cm
        assert str(scaled_cm) == "m"

        alt_cm = centimetre*1
        assert centimetre is alt_cm
        assert alt_cm*100 is metre
        assert str(alt_cm) == "cm"

        scaled_cm = centimetre * inch.get_conversion_factor(centimetre)
        assert scaled_cm.powers == inch.powers
        assert scaled_cm.factor == inch.factor
        assert inch is scaled_cm
        assert str(scaled_cm) == "inch"

    def check_arith2 (self):
        "arithmetic on physical units with other physical units"

        self.units.get_unit("um")
        (inch, um, sec, metre,) = \
               self.get_units('inch', 'um', 's', 'm')

        ips = inch/sec
        mps = metre/sec
        assert ips.get_name() == "inch/s"
        assert mps.get_name() == "m/s"
        assert ips.get_powers() == (1, 0, -1, 0, 0, 0, 0)
        assert mps.get_powers() == (1, 0, -1, 0, 0, 0, 0)
        assert ips.is_compatible(mps)
        assert round(ips.convert_value(10.0, mps),3) == 0.254

        minv = metre.inv()
        assert minv.get_name() == "1/m"
        assert minv.get_powers() == (-1, 0, 0, 0, 0, 0, 0)
        assert minv.get_conversion_factor() == 1.0

        assert (ips*metre).get_name() == "(inch/s)*m"
        assert (minv/ips).get_name() == "(1/m)/(inch/s)"
        assert (minv/4).get_name() == "1/m/4"

        umps = um/sec
        assert (umps*metre).get_name() == "(um/s)*m"
        assert (minv/umps).get_name() == "(1/m)/(um/s)"
        assert (minv/4).get_name(html=1) == "1/m/4"
        assert (minv/(1/3.0)).get_name(html=1) == "1/m/0.333333"

        msq = metre*metre
        assert msq.is_compatible(self.units['m^2'])
        assert msq.get_name() == "m*m"
        assert msq.get_powers() == (2, 0, 0, 0, 0, 0, 0)
        assert not msq.is_compatible(metre)
        raises(UnitError, msq.convert_value, 1, mps)

    def check_delete (self):
        # Can't delete standard SI units
        raises(TypeError, self.units.delete_unit, 'm')
        raises(AssertionError, self.units.delete_unit, self.units['g'])
        raises(AssertionError, self.units.delete_unit, self.units['Wb'])

        # Some deletions that should work
        cmps = self.units.get_unit('cm/s')
        assert self.units['cm/s'] == cmps
        self.units.delete_unit(cmps)
        raises(ValueError, self.units.get_unit, 'cm/s', create=False)

        # get_unit() can bring it back (but as a different object)
        assert self.units.get_unit('cm/s') == cmps
        assert self.units.get_unit('cm/s') is not cmps

        # This one can't be brought back
        mil = self.units['mil']
        self.units.delete_unit(mil)
        try:
            self.units['mil']
            assert 0
        except KeyError: pass
        raises(ValueError, self.units.get_unit, 'mil')

    def check_massquery (self):
        # Don't make any assumptions about which units are "natural" or
        # "artificial" -- it's non-obvious and a bit surprising in a
        # newly-created UnitCollection.  Doesn't really matter in real
        # life, though, since the 'artificial' flag was added well after
        # all the important units already existed in our live database.
        all_units = self.units.units.values()
        nat_units = self.units.get_natural_units()
        art_units = [u for u in self.units.units.values() if u.get_artificial()]
        assert set(all_units) == set(nat_units) | set(art_units)

if __name__ == "__main__":
    PhysicalUnitTest()
