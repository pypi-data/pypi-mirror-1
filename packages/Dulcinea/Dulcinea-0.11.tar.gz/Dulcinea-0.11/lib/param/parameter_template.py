"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/param/parameter_template.py $
$Id: parameter_template.py 27586 2005-10-17 16:50:53Z dbinger $

Provides ParameterTemplate, MasterTemplate and InputTemplate.
"""
from dulcinea.base import DulcineaPersistent
from dulcinea.physical_unit import get_standard_unit, PhysicalUnit
from dulcinea.physical_value import PhysicalValue
from dulcinea.spec import boolean, instance, anything, spec, specify
from dulcinea.spec import add_getters, string, pattern, both
from dulcinea import local
from quixote.html import stringify
import dulcinea.param.parameter_type


# Default value for 'check_constraint()' method -- can't use None because
# it's a legitimate constraint.
_no_value = "_no_value"


class ParameterTemplate (DulcineaPersistent):
    """
    Parameter templates are used to guide parameter input.
    """
    constraint_is = spec(
        (None, list),
        "a list of allowed values for the parameter")

    description_is = spec(
        (None, string),
        "an accurate, concise, technical, readable description of the "
        "parameter")

    def __init__(self):
        assert self.__class__ is not ParameterTemplate, "abstract class"

    def get_description(self):
        return self.description

    def set_description(self, description):
        specify(self, description=description)

    def check_type(self, value):
        """(value : any)

        Ensure that 'value' is compatible with the parameter type.
        Raise ParamTypeError if not.
        """
        self.get_type().check_value(value)

    def is_atomic(self):
        return self.get_type().is_atomic()

    def is_list(self):
        return self.get_type().is_list()

    def is_table(self):
        return self.get_type().is_table()

    def is_aggregate(self):
        return self.get_type().is_aggregate()

    def is_master(self):
        return 0

    def is_input(self):
        return 0

    def is_parameter(self):
        return 0

    def set_constraint(self, set):
        """(set : [param_value])

        Specify a constraint.  All elements of the constraint must be of the
        same type or a range, which must be the correct type for the
        parameter to which this constraint belongs.  For a value to meet the
        constraint, it must be equal to or within the range of one of the
        elements.
        """
        self.check_constraint(set)
        specify(self, constraint=set)

    def get_constraint(self):
        """Return the constraint or None if there is no constraint.
        """
        raise NotImplementedError

    def get_constraint_unit(self):
        constraint = self.get_constraint()
        if (constraint and isinstance(constraint[0], PhysicalValue)):
            return constraint[0].get_unit()
        else:
            return None

    def get_constraint_range(self):
        """() -> PhysicalValue

        Return the range of valid values described by the constraint.  If
        it's unconstrained, return None otherwise return the span of the
        set.
        """
        return self.get_type().get_constraint_range(self.get_constraint())

    def is_discrete(self):
        """Return true if this parameter can only take on discrete
        values.  If the constraint contains range values or there is no
        constraint then false is returned."""
        return self.get_type().is_discrete(self.get_constraint())

    def format(self, html=0):
        """Return a string with a brief summary of the parameter
        constraint, suitable to explain the constraint to a user before
        they supply a value.  Return None if constraint is empty.
        """
        return self.get_type().format_constraint(self.get_constraint(),
                                                 html=html)

    def explain_constraint(self, html=0):
        """Return a string with a fairly detailed explanation of the
        parameter constraint, suitable for use in error messages after
        user has violated the constraint.  Return None if constraint is
        empty.
        """
        constraint = self.get_constraint()
        return self.get_type().explain_constraint(constraint, html=html)

    def is_allowed_unit(self, unit):
        """Return true if 'unit' is an allowed unit for parameters
        derived from this parameter template, false otherwise.  (If the
        'allowed_units' attribute is not defined, no units are allowed).
        """
        allowed_units = self.get_allowed_units()
        if allowed_units is None:
            return unit is None
        elif unit is None:
            return 0
        else:
            unit = get_standard_unit(unit)
            return unit in allowed_units

    def check_value(self, value):
        """(value : param_value)

        Checks if 'value' is of the allowed type and meets the constraint
        specified earlier with 'set_constraint()'.  Returns silently if
        no constraint was set, or if the value meets the constraint.
        Raises ConstraintError if a constraint is defined, but 'value'
        doesn't meet it.  Raises ParamTypeError (indirectly) if the value
        is of the wrong type.
        """
        if value is None:
            return

        # Raises ParamTypeError if type is wrong.
        self.check_type(value)

        constraint = self.get_constraint()

        if constraint is not None:
            self.get_type().check_value_in_constraint(value, constraint)

    def get_default_unit(self):
        return self.get_type().get_unit()

    def is_time(self):
        """
        Return true if this parameter is a PhysicalValue and the units are
        time units.
        """
        unit = self.get_default_unit()
        return unit and unit.is_time()

    def simplify(self):
        """() -> RangeValue | None
        Return a simplified version of this template's constraint (a
        RangeValue containing ints or floats). Return None if there is
        no constraint or if the constraint cannot be simplified.
        """
        parameter_type = self.get_type()
        if parameter_type.is_int() or parameter_type.is_physical_value():
            constraint_range = self.get_constraint_range()
            if constraint_range is not None:
                return parameter_type.simplify_value(constraint_range)
        return None

    def create_value(self, value=None):
        """Create a new Parameter based on this template."""
        from dulcinea.param.parameter import Parameter
        return Parameter(self, value)

    def __str__(self):
        constraint = self.get_constraint()
        if constraint:
            constraint = map(stringify, constraint)
            if len(constraint) > 5:
                constraint = (", ".join(constraint[0:3]) + " ... " +
                              constraint[-1])
            else:
                constraint = ", ".join(constraint)
            return "%s : set %s" % (self.get_name(), constraint)
        else:
            return "%s (unconstrained)" % self.get_name()


class MasterTemplate (ParameterTemplate):
    """
    MasterTemplates define almost all relevant information for a
    parameter.  They either live in the template library (attached to
    process templates) or are created for ad hoc parameters on processes.
    """
    name_is = spec(
        both(string, pattern('^[a-z][a-z0-9_]*$')),
        "a software-friendly name for the parameter.")
    type_is = spec(
        instance('ParameterType'),
        "the type of this parameter")
    hidden_is = spec(
        boolean,
        "a UI hint to show the parameter less often")
    title_is = spec(
        (None, string),
        "the parameter name in a human-friendly form (if None, get_title "
        "derives the title from the name)")

    def __init__(self, name, param_type,
                 hidden=0,
                 description=None,
                 title=None,
                 constraint=None):
        self.set_name(name)
        if title is None:
            words = self.name.split("_")
            words[0] = words[0].capitalize()
            title = " ".join(words)
        specify(self,
                type=param_type,
                hidden=0,
                description=description,
                title=title,
                constraint=constraint)

    def get_allowed_units(self):
        units = self.get_type().get_compatible_units()
        if units:
            return [unit for unit in units if not unit.artificial]
        else:
            return None

    def get_master(self):
        return self

    def is_hidden(self):
        return self.hidden

    def is_master(self):
        return 1

    def set_name(self, name):
        specify(self, name=name)

    def set_hidden(self, hidden):
        specify(self, hidden=hidden)

    def set_title(self, title):
        specify(self, title=title)

    def get_constraint(self):
        """Return the constraint or None if there is no constraint.
        """
        if self.constraint is None and self.get_type().is_material():
            return list(local.get_material_db().get_materials())
        else:
            return self.constraint

    def create_input_template(self, constraint=None, description=None,
                              allowed_units=None, required=0,
                              default_value=None):
        """Create a new InputTemplate based on this template."""
        constraint = constraint or self.constraint
        return InputTemplate(self, constraint=constraint,
                             description=description,
                             allowed_units=allowed_units,
                             required=required,
                             default_value=default_value)

    def check_constraint(self, set=_no_value):
        if set is _no_value:
            set = self.constraint
        self.get_type().check_constraint(set)

    def is_required(self):
        return 0


add_getters(MasterTemplate)


class InputTemplate (ParameterTemplate):
    """
    Input templates are created to guide input.
    """
    template_is = spec(
        MasterTemplate,
        "the master template for this template; this must always be set")
    allowed_units_is = spec(
        (None, [PhysicalUnit]),
        "a list of PhysicalUnit instances that controls what unit may be "
        "used when entering a parameter.")
    required_is = spec(
        boolean,
        "true if a value is required for this parameter")
    default_value_is = spec(
        anything,
        "A typical value for this parameter")

    def __init__(self, template, constraint=None, description=None,
                 allowed_units=None, required=0, default_value=None):
        specify(self,
                template=template,
                default_value=default_value,
                description=description,
                required=required)
        self.set_allowed_units(allowed_units)
        self.set_constraint(constraint)

    def check_constraint(self, set=_no_value):
        """Verify that set is a valid constraint for this template.
        """
        if set is None:
            return
        if set is _no_value:
            set = self.constraint
        self.get_type().check_set_in_constraint(
            set,
            self.template.get_constraint())

    def get_template(self):
        return self.template

    def get_master(self):
        return self.template.get_master()

    def get_name(self):
        return self.template.get_name()

    def set_default_value(self, value):
        self.check_value(value)
        self.default_value = value

    def check_default_value(self):
        self.check_value(self.default_value)

    def get_default_value(self):
        return self.default_value

    def is_hidden(self):
        return self.get_master().is_hidden()

    def is_required(self):
        return self.required

    def is_input(self):
        return 1

    def get_title(self):
        return self.template.get_title()

    def get_description(self):
        return self.description or self.template.get_description()

    def get_type(self):
        return self.template.get_type()

    def set_allowed_units(self, units):
        """(units : [PhysicalUnit | string] | None)"""
        if not units:
            self.allowed_units = None
        else:
            assert self.get_type().is_physical_value(), (
                'allowed_units only apply to physical value parameters '
                'not %r' % self.get_type())
            self.allowed_units = [get_standard_unit(unit)
                                  for unit in units]

    def get_allowed_units(self):
        return (self.allowed_units or self.template.get_allowed_units())

    def get_constraint(self):
        """Return the constraint or None if there is no constraint.
        """
        if self.constraint is None:
            return self.template.get_constraint()
        else:
            return self.constraint

    def set_required(self, required):
        specify(self, required=required)

    def create_default_value(self):
        """Create a new Parameter based on this template."""
        from dulcinea.param.parameter import Parameter
        return Parameter(self, self.get_default_value())

