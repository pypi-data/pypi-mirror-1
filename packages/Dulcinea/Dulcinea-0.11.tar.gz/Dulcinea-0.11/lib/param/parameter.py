"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/param/parameter.py $
$Id: parameter.py 27538 2005-10-11 23:00:36Z rmasse $
"""
from dulcinea.base import DulcineaPersistent
from dulcinea.param.parameter_template import ParameterTemplate
from dulcinea.spec import anything, spec, specify, add_getters_and_setters
from dulcinea.tolerance import Tolerance
from quixote.html import htmltext, stringify
from sets import Set

class Parameter (DulcineaPersistent):
    """
    Parameters are used to describe properies of things like equipment,
    processes, and process steps within the system.  Each parameter has a
    name, a value and a type.  The name and type are stored in a parameter
    template because they are common between many instances of parameters.
    """
    template_is = spec(
        ParameterTemplate,
        "defines attributes of this parameter such as name, type and "
        "the constraints on the value")
    value_is = spec(
        anything,
        "the value this parameter has (may be None which means no value)")
    tolerance_is = spec(
        (None, Tolerance),
        "the relative tolerance of this parameter (in percent).  May be "
        "None.")

    def __init__(self, template, value=None):
        specify(self, template=template, tolerance=None)
        self.set_value(value)

    def __str__(self):
        if self.value is None:
            return "%s (no value)" % self.get_name()
        elif not self.value:            # empty list/string/etc.
            return "%s (empty value)" % self.get_name()
        else:
            return "%s = %s" % (self.get_name(), self.format())

    def is_required(self):
        return self.template.is_required()

    def is_hidden(self):
        return self.template.is_hidden()

    def is_master(self):
        return 0

    def is_input(self):
        return 0

    def is_parameter(self):
        return 1

    def set_value(self, value):
        """(any)

        May raise TypeError.
        """
        self.template.check_type(value)
        self.value = value

    def allow_tolerance(self):
        return self.template.get_type().allow_tolerance()

    def check_value(self):
        self.template.check_value(self.value)

    def format(self, html=0, show_tolerance=0):
        """Return the parameter's value (and unit, if any) as a useful,
        standalone string.  Return None if the value is undefined."""
        if self.value is None:
            return None

        param_type = self.template.get_type()
        s = param_type.format_value(self.value, html=html)
        if show_tolerance and self.tolerance is not None:
            s += ' ' + htmltext(self.tolerance.format(html=html))
        return s

    def check_type(self):
        """()

        Ensure that 'self.value' is compatible with the parameter type.
        Raise ParamTypeError if not.
        """
        self.get_type().check_value(self.value)

    def simplify(self):
        """() -> (string|int|float|None)
        Return a simplified version of this parameter's value. Physical
        values are converted to use the default unit from the master
        template and are returned as floats. Materials are returned as
        strings (using their names).  If self is an InputTemplate,
        simplify the default value
        """
        return self.get_type().simplify_value(self.value)

    # -- Delegates to our template -------------------------------------

    def is_discrete(self):
        return self.template.is_discrete()

    def is_atomic(self):
        return self.template.is_atomic()

    def is_list(self):
        return self.template.is_list()

    def is_table(self):
        return self.template.is_table()

    def is_array(self):
        return self.template.is_array()

    def is_aggregate(self):
        return self.template.is_aggregate()

    def is_time(self):
        return self.template.is_time()

    def get_master(self):
        return self.template.get_master()

    def get_name(self):
        return self.template.get_name()

    def get_type(self):
        return self.template.get_type()

    def get_title(self):
        return self.template.get_title()

    def get_description(self):
        return self.template.get_description()

    def get_hint(self, html=0):
        if html:
            texttype = htmltext
        else:
            texttype = stringify
        hint = texttype(self.get_description() or "")
        if not (self.is_discrete() or self.get_constraint() is None):
            if hint:
                hint += ', '
            hint += self.template.explain_constraint(html=html)
        return hint

    def get_constraint(self):
        constraint = self.template.get_constraint()
        if self.get_type().is_material():
            materials = Set()
            for material in constraint:
                materials.update(material.get_leaves())
            return list(materials)
        else:
            return constraint

    def get_material_constraint(self):
        assert self.get_type().is_material()
        materials = Set()
        for material in self.template.get_constraint():
            materials.add(material)
            materials.update(material.get_descendants())
        return list(materials)

    def get_allowed_units(self):
        return self.template.get_allowed_units()

add_getters_and_setters(Parameter)


def get_example_parameters(process_parameters):
    """() -> [Parameter]

    Return a list of example value parameters mirroring 'process_parameters'
    except that parameters lacking values (e.g. input) are duplicated
    with values created using the default value of the parameter.
    """
    example_parameters = []
    if process_parameters:
        for parameter in process_parameters:
            if parameter.is_input():
                example_parameters.append(parameter.create_value(
                    value=parameter.get_default_value()))
            else:
                example_parameters.append(parameter.copy())
    return example_parameters
