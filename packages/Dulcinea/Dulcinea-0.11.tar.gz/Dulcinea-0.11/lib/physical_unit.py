"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/physical_unit.py $
$Id: physical_unit.py 27528 2005-10-07 20:50:40Z dbinger $

Provides the PhysicalUnit and UnitCollection.
"""
from dulcinea import local
from dulcinea.base import DulcineaPersistent
from dulcinea.spec import instance, boolean, mapping, spec, specify, require
from dulcinea.spec import string
from durus.persistent_dict import PersistentDict
from quixote.html import htmltext, stringify


class UnitError (Exception):
    """Error with inconsistent or invalid physical units.
    """


class PhysicalUnit (DulcineaPersistent):
    """
    A single physical unit, consisting of a name, dimensionality,
    conversion factor to the standard (SI) unit of the same
    dimensionality, and offset to the SI unit.  (Offset is only for
    temperature units.)
    """
    name_is = spec(
        string,
        'the name of this unit in plain 7-bit ASCII (.e.g "kg*m/s^2").')
    html_name_is = spec(
        (string, None),
        "the name of the unit as it will be presented on the web.")
    powers_is = spec(
        (int, int, int, int, int, int, int),
        "denotes which SI quantity this unit measures, as a tuple of "
        "exponents on the seven fundamental SI dimensions listed in "
        "UnitCollection.DIMENSIONS.")
    units_is = spec(
        instance('UnitCollection'),
        "the UnitCollection to which this unit belongs")
    factor_is = spec(
        float,
        "the conversion factor from this unit to the standard SI unit "
        "for the same quantity (ie. with the same 'powers' tuple). "
        "By definition, the unit with factor 1.0 (and offset 0.0) is "
        "the standard SI unit for a particular quantity.")
    offset_is = spec(
        float,
        "the conversion offset from this unit to the standard SI "
        "unit for the same quantity.  Only relevant for temperature "
        "units, specifically degC and degF.")
    artificial_is = spec(
        boolean,
        "true if this unit was artificially created as a result of unit "
        "arithmetic, in which case this unit probably should not be "
        "visible to users selecting from a set of available units")

    def __init__(self, name=None, powers=None, units=None,
                 factor=1.0, offset=0.0,
                 html_name=None, artificial=0):
        self.set_name(name, html_name)
        specify(self, powers=powers, units=units, factor=factor, offset=offset,
                artificial=artificial)

    def __str__(self):
        return self.name

    def set_name(self, name, html_name):
        self.name = name
        if html_name == name:
            self.html_name = None
        else:
            self.html_name = html_name

    def get_name(self, html=0):
        if html and self.html_name is not None:
            return htmltext(self.html_name)
        else:
            return self.name

    def get_protected_name(self, html=0):
        name = stringify(self.get_name(html=html))
        if ('/' in name or '*' in name or '^' in name):
            name = "(%s)" % name
        if html:
            return htmltext(name)
        else:
            return name

    def get_powers(self):
        return self.powers

    def get_conversion_factor(self, other=None):
        """(other=None : PhysicalUnit) -> factor : float

        Return the factor that converts a value in the current unit
        to units of 'other'.  'other' may be another PhysicalUnit
        instance or None (the default).  If None, just returns the
        conversion factor from the current unit to the appropriate SI
        unit, otherwise return conversion factor to the unit specified
        by 'other'.

        Raises UnitError if 'self' and 'other' are incompatible units,
        or if the conversion between them is not a simple multiplicative
        factor (eg. converting units with different offsets, such as
        degC to K or degC to degF).
        """
        if other is None:
            return self.factor
        require(other, PhysicalUnit)
        if self.powers != other.powers:
            raise UnitError, "Incompatible units: %s, %s" % (self, other)
        if self.offset != other.offset and self.factor != other.factor:
            raise UnitError, \
                  ('Unit conversion (%s to %s) cannot be expressed ' +
                   'as a simple multiplicative factor') % \
                  (self.name, other.name)
        return self.factor/other.factor

    def get_conversion_tuple(self, other=None):
        """(other : PhysicalUnit = None) -> (factor : float, offset : float)

        Returns the (factor,offset) tuple that converts values in the
        current unit to another, compatible, unit.  Same rules for
        'other' apply as for 'get_conversion_factor()'.

        The returned conversion tuple is used as follows:
          new_value = (old_value + offset) * factor
        where old_value is in the units of 'self'; new_value will be in
        the units of 'other'.  Note that 'convert_value()' will happily
        do this arithmetic for you.

        Raises UnitError if 'self' and 'other' are incompatible units.
        """
        # no "other" unit? return tuple to convert to base unit
        if other is None:
            return (self.factor, self.offset)
        if string(other):
            other = self.units.get_unit(other)

        require(other, PhysicalUnit)

        # incompatible "other" unit? bomb!
        if self.powers != other.powers:
            raise UnitError, "Incompatible units: %s, %s" % (self, other)

        # otherwise, a little arithmetic is in order... here's the
        # algebra to back it up:
        # "Let (f1,o1) be the conversion tuple from 'self' to base units
        # (ie. (x+o1)*f1 converts a value x from 'self' to base units,
        # and (x/f1)-o1 converts x from base to 'self' units)
        # and (f2,o2) be the conversion tuple from 'other' to base units
        # then we want to compute the conversion tuple (F,O) from
        #   'self' to 'other' such that (x+O)*F converts x from 'self'
        #   units to 'other' units
        # the formula to convert x from 'self' to 'other' units via the
        #   base units is (by definition of the conversion tuples):
        #     ( ((x+o1)*f1) / f2 ) - o2
        #   = ( (x+o1) * f1/f2) - o2
        #   = ( (x+o1) * f1/f2 ) - (o2*f2/f1) * f1/f2
        #   = ( (x+o1) - (o1*f2/f1) ) * f1/f2
        #   = (x + o1 - o2*f2/f1) * f1/f2
        # thus, O = o1 - o2*f2/f1 and F = f1/f2"
        factor = self.factor / other.factor
        offset = self.offset - (other.offset * other.factor / self.factor)
        return (factor, offset)

    def convert_value(self, value, other=None):
        """(value : number, other : PhysicalUnit = None) -> new_value : number

        Convert 'value', implicitly in the current unit, to a new unit
        'other'.  If 'other' is None, convert 'value' to the
        corresponding SI unit; otherwise, 'other' must be a PhysicalUnit
        object.  Raises UnitError if 'other' is incompatible with
        'self'.
        """
        require(other, (PhysicalUnit, None))
        (factor, offset) = self.get_conversion_tuple(other)
        return (value + offset) * factor

    def is_compatible(self, other):
        if other is None and self.powers is not None:
            return 0
        return self.powers == other.powers

    def is_dimension(self, name):
        """Test if the unit has the same dimensions as the supplied
        quantity name (eg. "mass", "time", etc.)
        """
        powers = self.units.quantity_powers[name]
        return self.powers == powers

    def is_inverse_compatible(self, other):
        return list(self.powers) == [-p for p in other.powers]

    def is_dimensionless(self):
        return self.powers == (0, 0, 0, 0, 0, 0, 0)

    def is_time(self):
        return self.powers == (0, 0, 1, 0, 0, 0, 0)

    def _mul(self, other):
        if self.offset != 0:
            raise UnitError, \
                  "cannot multiply unit '%s' with non-zero offset %s" % \
                  (self, self.offset)

        if type(other) in (float, int):
            name = "%g*%s" % (other, self.get_protected_name())
            html_name = "%g*%s" % (other, self.get_protected_name(html=1))
            powers = self.powers
            factor = float(other) * self.factor

            return (name, html_name, powers, factor)

        elif isinstance(other, PhysicalUnit):
            if other.offset != 0:
                raise UnitError, \
                      ("cannot multiply unit '%s' by other unit '%s' "
                       "with non-zero offset (%g)") % \
                      (self, other, other.offset)
            name = "%s*%s" % (self.get_protected_name(),
                              other.get_protected_name())
            html_name = "%s*%s" % (self.get_protected_name(html=1),
                                   other.get_protected_name(html=1))
            powers = [p1+p2 for (p1, p2) in zip(self.powers, other.powers)]
            powers = tuple(powers)
            factor = self.factor * other.factor

            return (name, html_name, powers, factor)
        else:
            raise TypeError(
                "can only multiply physical unit by a number or "
                "another PhysicalUnit instance: not %r" % other)

    def _div(self, other):
        if self.offset != 0:
            raise UnitError, \
                  "cannot divide unit '%s' with non-zero offset (%g)" % \
                  (self, self.offset)

        if type(other) in (float, int): # "self / 4"
            name = "%s/%g" % (self.name, other)
            html_name = "%s/%g" % (self.get_name(html=1), other)
            powers = self.powers
            factor = self.factor / other
            return (name, html_name, powers, factor)

        elif isinstance(other, PhysicalUnit):
            if other.offset != 0:
                raise UnitError, \
                      ("cannot divide unit '%s' by unit '%s' "
                       "with non-zero offset (%g)") % \
                       (self, other, other.offset)
            name = "%s/%s" % (self.get_protected_name(),
                              other.get_protected_name())
            html_name = "%s/%s" % (self.get_protected_name(html=1),
                                   other.get_protected_name(html=1))
            powers = [p1-p2 for (p1,p2) in zip(self.powers, other.powers)]
            powers = tuple(powers)
            factor = self.factor / other.factor
            return (name, html_name, powers, factor)

        else:
            raise TypeError, \
                  "can only divide by a number or " \
                  "another PhysicalUnit instance"

    def _inv(self, junk=None):
        if self.offset != 0:
            raise UnitError, \
                  "cannot invert unit '%s' with non-zero offset (%g)" % \
                  (self, self.offset)
        assert junk is None             # _arith_op() expects an 'other' arg

        name = "1/%s" % self.get_protected_name()
        if self.html_name:
            html_name = "1/%s" % self.get_protected_name(html=1)
        else:
            html_name = None
        powers = tuple([-p for p in self.powers])
        factor = 1/self.factor
        return (name, html_name, powers, factor)

    def _pow(self, n):
        if not isinstance(n, int):
            raise ValueError(
                "pow(unit, n): n must be an integer (not %r)" % n)
        if self.offset != 0:
            raise ValueError(
                "pow(unit, n): makes no sense for unit with offset")

        name = "%s^%d" % (self.get_protected_name(), n)
        html_name = "%s<sup>%d</sup>" % (self.get_protected_name (), n)
        powers = tuple([e * n for e in self.powers])
        factor = self.factor ** n
        return (name, html_name, powers, factor)


    def _arith_op(self, other, method, add=1):
        (name, html_name, powers, factor) = method(other)
        unit = self.units.reverse_lookup(powers, factor)
        if unit:
            return unit
        else:
            return self.units.create_unit(name, html_name, powers, factor,
                                          add=add, artificial=1)


    def __mul__(self, other):
        """(self : PhysicalUnit, other : number | PhysicalUnit)
           -> PhysicalUnit

        Multiply the current unit by another unit or a number and return
        a PhysicalUnit instance with appropriate dimensionality and
        conversion factor.
        """
        if other == 1:
            return self
        else:
            return self._arith_op(other, self._mul)


    def __div__(self, other):
        """(self : PhysicalUnit, other : number | PhysicalUnit)
           -> PhysicalUnit

        Divide the current unit by another unit or a number and return a
        new PhysicalUnit instance with appropriate dimensionality and
        conversion factor.  Does nothing smart about finding an existing
        PhysicalUnit for the result, since this class knows nothing
        about unit collections.
        """
        if other == 1:
            return self
        else:
            return self._arith_op(other, self._div)

    def __pow__(self, n, mod=None):
        """Raise a unit the power n (an integer).
        """
        if n == 1:
            return self
        else:
            return self._arith_op(n, self._pow)

    def inv(self):
        """Return the inverse of a unit.
        """
        return self._arith_op(None, self._inv)

    def __cmp__(self, other):
        """Compare two PhysicalUnit instances for equality.  If 'other'
        is a PhysicalUnit with the same dimensionality and conversion
        factor and offset as 'self', then they are equal.

        Comparing PhysicalUnit instances for anything other than
        equality is not defined.
        """
        if (isinstance(other, PhysicalUnit) and
            (self.powers == other.powers and
             self.factor == other.factor and
             self.offset == other.offset)):
            return 0
        else:
            return -1

    def get_artificial(self):
        return self.artificial


class UnitCollection (DulcineaPersistent):
    """
    A collection of physical units.

    Class attributes:
      dimensions : [string]
        the seven fundamental SI dimensions.  All SI quantities are
        either on this list or are arithmetically derived from members
        of this list.  Eg. "length" is an SI quantity that is also a
        fundamental dimension; "force" is a derived SI quantity:
        "mass * length / time^2".
      si_prefixes : { string : float }
        defines the SI prefixes and how much they scale a unit by
    """
    units_is = spec(
        mapping({string:PhysicalUnit}, PersistentDict),
        "the complete collection of physical units")
    unit_rev_is = spec(
        {(int,int,int,int,int,int,int):[PhysicalUnit]},
        "used for looking up units based on their quantitative "
        "description, rather than by name.  Needed by the "
        "PhysicalUnit arithmetic operator overload methods.")
    si_units_is = spec(
        {(string,None):PhysicalUnit},
        "a subset of 'units' that may have SI prefixes tacked on to "
        'create a new, valid unit.  Eg. "m" is in si_units, since "mm" '
        'and "km" are both valid units that we might want to create '
        'on-the-fly.  But "mm" is not, nor is "inch", since neither "mmm" '
        'nor "minch" make any sense.')
    quantity_powers_is = spec(
        {string:(int,int,int,int,int,int,int)},
        'defines the known SI quantities by mapping their names ("length", '
        '"force", etc.) to exponent vectors')

    DIMENSIONS = [
        'length',                       # metre
        'mass',                         # kilogram
        'time',                         # second
        'current',                      # ampere
        'temperature',                  # kelvin
        'substance_amount',             # mole
        'luminous_intensity',           # candela
        ]

    # This includes every SI prefix except "da" (*10), which is tricky
    # because it's two letters long.  Oh well, whatever.
    si_prefix = {
        'E': 1e18,                  # exa-
        'P': 1e15,                  # peta-
        'T': 1e12,                  # tera-
        'G': 1e9,                   # giga-
        'M': 1e6,                   # mega-
        'k': 1e3,                   # kilo-
        'h': 1e2,                   # hecto-
        'd': 1e-1,                  # deci-
        'c': 1e-2,                  # centi-
        'm': 1e-3,                  # milli-
        'u': 1e-6,                  # micro-
        'n': 1e-9,                  # nano-
        'p': 1e-12,                 # pico-
        'f': 1e-15,                 # femto-
        'a': 1e-18,                 # atto-
        }

    def __init__(self):
        self.units = PersistentDict()
        self.unit_rev = {}
        self.si_units = {}
        self.quantity_powers = {}

        # base dimensions
        num_dim = len(self.DIMENSIONS)
        for i, dim in enumerate(self.DIMENSIONS):
            powers = [0] * num_dim
            powers[i] = 1
            self.quantity_powers[dim] = tuple(powers)

        # First, we must define the seven base SI units, one per SI
        # dimension.  This defines the foundation of the unit system.
        self.add_base_unit("length", "m")
        self.add_base_unit("mass", "kg")
        self.add_base_unit("time", "s")
        self.add_base_unit("current", "A")
        self.add_base_unit("temperature", "K")
        self.add_base_unit("substance_amount", "mol")
        self.add_base_unit("luminous_intensity", "cd")

        # kg is the base unit of mass.
        g = PhysicalUnit("g", self["kg"].powers, self, factor=0.001)
        self._add(g)
        del self.si_units["kg"]
        self.si_units["g"] = g

        # Next, we define the SI derived units.  Unlike the calls to
        # add_base_unit(), which are based on the seven already-defined
        # SI dimensions, each of these defines a new SI "quantity" and
        # associates a canonical unit with it.  Eg. the canonical unit
        # for the quantity "area" is "m^2".

        self.add_derived_unit("area", self["m"] * self["m"], "m^2")
        self.add_derived_unit("volume", self["m^2"] * self["m"], "m^3")
        self.create_unit("Hz", None, (0, 0, -1, 0, 0, 0, 0), 1.0)
        self.add_derived_unit("frequency", self["Hz"])

        self.add_derived_unit("density", self['kg'] / self['m^3'], "kg/m^3")
        self.add_derived_unit("speed", self['m'] / self['s'], 'm/s')
        self.add_derived_unit("acceleration",
                              self['m'] / self['s']**2, "m/s^2")
        self.add_derived_unit("force",
                              self['kg'] * self['m'] / (self['s']**2), 'N')
        self.add_derived_unit("pressure", self["N"] / self['m']**2, "Pa")
        self.add_derived_unit("energy", self["N"] * self["m"], "J")
        self.add_derived_unit("power", self["J"] / self["s"], "W")
        self.add_derived_unit("intensity", self["W"] / self["m"]**2, "W/m^2")
        self.add_derived_unit("charge", self["A"] * self["s"], "C")
        self.add_derived_unit("voltage", self["W"] / self["A"], "V")
        self.add_derived_unit("resistance",
                              self["V"] / self["A"], "Ohm", "&Omega;")
        self.add_derived_unit("resistivity",
                              self["Ohm"] * self["m"], "Ohm*m", "&Omega;*m")
        self.add_derived_unit("capacitance",
                              self["A"] * self["s"] / self["V"], "F")
        self.add_derived_unit("magnetic_flux", self["V"] * self["s"], "Wb")
        self.add_derived_unit("inductance",
                              self["V"] * self["s"] / self["A"], "H")
        self.add_derived_unit("magnetic_flux_density",
                              self["Wb"] / self["m"]**2, "T")

        # Finally, we add non-SI units: each is defined in terms of an
        # existing unit, usually by just supplying a name and a
        # conversion factor.  (Sometimes we supply a conversion offset,
        # sometimes an HTML name.)  The only units we should have to
        # define here are units whose name or HTML name cannot be
        # derived from existing units, either arithmetically
        # (eg. "Ohm*cm") or through SI prefixing ("um").

        self.add_unit("Ang", self["m"], 1e-10, html_name="&Aring;")
        self.add_unit("inch", self.get_unit("cm"), 2.54)
        self.add_unit("mil", self["inch"], 0.001)

        self.add_unit("min", self["s"], 60)
        self.add_unit("hour", self["min"], 60)
        self.add_unit("day", self["hour"], 24)
        self.add_unit("week", self["day"], 7)

        # Let gf (grams of force) look like an SI unit,
        # so ugf and mgf work automatically.
        gf = self.add_unit("gf", self["N"], 0.00980665)
        self.si_units["gf"] = gf

        self.add_unit("bar", self["Pa"], 1e5)
        self.add_unit("mb", self["Pa"], 100)
        self.add_unit("atm", self.get_unit("kPa"), 101.325)
        self.add_unit("Torr", self["atm"], 1./760)
        self.add_unit("mTorr", self["Torr"], 1e-3)
        self.add_unit("psi", self["kPa"], 6.89475)
        self.add_unit("inHg", self["kPa"], 3.387)
        self.add_unit("mmHg", self["Pa"], 133.3)
        self.add_unit("degC", self["K"], 1, 273.15, html_name="&deg;C")
        self.add_unit("degF", self["degC"], 5./9., -32, html_name="&deg;F")
        self.add_unit("dyne", self["N"], 1e-5)
        self.add_unit("lb", self["N"], 4.448221615)


    def _add(self, unit):
        name = unit.name
        assert not self.units.has_key(name), \
               "already in units dict: %r" % name
        assert not self.units.has_key(unit.name), \
               "already in units dict: %r" % unit.name
        assert not (self.unit_rev.has_key(unit.powers) and
                    filter(None, [unit is u
                                  for u in self.unit_rev[unit.powers]])), \
               "already in unit_rev dict: %r" % unit
        self._p_note_change()
        self.units[name] = unit
        self.unit_rev.setdefault(unit.powers, []).append(unit)
        return unit

    def add_base_unit(self, quantity, name):
        assert quantity in self.DIMENSIONS, (
            "quantity %r is not a fundamental dimension" % quantity)
        powers = self.quantity_powers[quantity]
        unit = PhysicalUnit(name, powers, self)
        self.si_units[name] = unit
        return self._add(unit)

    def add_derived_unit(self, quantity, unit, name=None, html_name=None):
        if name and unit.name != name:
            unit = PhysicalUnit(name, unit.powers, units=unit.units,
                                factor=unit.factor, offset=unit.offset,
                                html_name=html_name)
            self._add(unit)
        if unit.html_name and html_name:
            unit.html_name = html_name
        self.quantity_powers[quantity] = unit.powers
        self.si_units[name] = unit

    def add_unit(self, name, base, factor=1.0, offset=0.0, html_name=None):
        (bfactor, boffset) = base.get_conversion_tuple()
        unit = PhysicalUnit(name, base.powers, self,
                            bfactor * factor,
                            boffset/factor + offset,
                            html_name=html_name)
        return self._add(unit)

    def create_unit(self, name, html_name, powers, factor,
                     add=1, artificial=0):
        unit = PhysicalUnit(name, powers, self,
                            factor=factor, html_name=html_name,
                            artificial=artificial)
        if add:
            self._add(unit)
        return unit

    def __len__(self):
        return len(self.units)

    def __getitem__(self, name):
        return self.units[name]

    def __delitem__(self, name):
        self.delete_unit(name)

    def keys(self):
        return self.units.keys()

    def values(self):
        return self.units.values()

    def has_unit(self, name):
        return self.units.has_key(name)

    has_key = has_unit

    def prefix_lookup(self, name):
        if len(name) >= 2:            # prefix 1 char, unit >= 1 char
            factor = self.si_prefix.get(name[0])
            base_unit = self.si_units.get(name[1:])

            if factor and base_unit:
                if name[0] == "u":
                    html_name = "&micro;" + name[1:]
                else:
                    html_name = None
                unit = PhysicalUnit(name, base_unit.powers, self,
                                    factor=factor*base_unit.factor,
                                    html_name=html_name)
                return unit
        return None

    def reverse_lookup(self, powers, factor=1.0, offset=0.0):
        compat = self.unit_rev.get(powers)
        if compat:
            for unit in compat:
                if unit.factor == factor and unit.offset == offset:
                    return unit
        return None

    def get_unit(self, name, create=True):
        """(name : string) -> PhysicalUnit

        Lookup a unit 'name' in the collection's dictionary of known
        units.  Raise KeyError if not unit with that name exists.
        """
        if isinstance(name, PhysicalUnit):
            return name
        require(name, string)
        try:
            unit = self.units[name]
        except KeyError:
            if not create:
                raise ValueError
            unit = self.prefix_lookup(name)
            if unit is None:
                raise ValueError
            # This unit did not previously exist -- give it the name
            # preferred by the caller and store it for future reference.
            self._add(unit)
        return unit

    def get_natural_units(self):
        def get_lower_name(unit):
            return unit.get_name().lower()
        return sorted([u for u in self.units.values()], key=get_lower_name)

    def get_compatible_units(self, unit):
        """Return the list of units (as PhysicalUnit instances) that
        are compatible with 'unit' (which maybe a PhysicalUnit instance
        or a unit name (string)).
        """
        if string(unit):
            unit = self.get_unit(unit)
        require(unit, PhysicalUnit)
        return self.unit_rev[unit.powers]

    def delete_unit(self, unit):
        require(unit, PhysicalUnit)
        assert unit.name not in self.si_units, (
            "can't delete standard SI unit %r" % unit)
        assert self.units[unit.name] is unit
        assert unit in self.unit_rev[unit.powers]

        del self.units[unit.name]
        self.unit_rev[unit.powers].remove(unit)

        if self.si_units.has_key(unit.name):
            assert self.si_units[unit.name] is unit
            del self.si_units[unit.name]

    def get_conversion_factor(self, unit1, unit2=None):
        if string(unit1):
            unit1 = self.get_unit(unit1)
        require(unit1, PhysicalUnit)
        return unit1.get_conversion_factor(unit2)

    def get_conversion_tuple(self, unit1, unit2=None):
        if string(unit1):
            unit1 = self.get_unit(unit1)
        require(unit1, PhysicalUnit)
        return unit1.get_conversion_tuple(unit2)

    def convert_value(self, value, unit1, unit2=None):
        if string(unit1):
            unit1 = self.get_unit(unit1)
        require(unit1, PhysicalUnit)
        return unit1.convert_value(value, unit2)


def get_standard_unit(unit_expression):
    return local.get_standard_units().get_unit(unit_expression)

