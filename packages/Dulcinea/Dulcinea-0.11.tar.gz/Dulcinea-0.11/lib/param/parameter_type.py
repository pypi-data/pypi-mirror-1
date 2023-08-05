"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/param/parameter_type.py $
$Id: parameter_type.py 27538 2005-10-11 23:00:36Z rmasse $

Provides classes for representing parameter types.

Also provides create_atomic_type, get_physical_value_parameter_type, and
several similar functions that make it more convenient to locate common
types.
"""
from dulcinea import local
from dulcinea.base import DulcineaPersistent
from dulcinea.material import Material
from dulcinea.param.errors import ParamTypeError, ConstraintError
from dulcinea.physical_unit import PhysicalUnit, get_standard_unit
from dulcinea.physical_value import PhysicalValue
from dulcinea.range_value import RangeValue
from dulcinea.set_utils import in_set
from dulcinea.spec import mapping, anything, instance, spec, require, string
from durus.persistent import Persistent
from durus.persistent_dict import PersistentDict
from quixote.html import htmltext, htmlescape, stringify
import dulcinea.param.parameter_template

class ParameterType (DulcineaPersistent):

    INT = 1
    STRING = 2
    PHYSICAL_VALUE = 3
    MATERIAL = 4
    BOOLEAN = 5

    ATOMIC_TYPES = ((INT, "integer"),
                    (STRING, "string"),
                    (PHYSICAL_VALUE, "physical value"),
                    (MATERIAL, "material"),
                    (BOOLEAN, 'boolean'))

    ATOMIC = 10
    LIST = 20
    TABLE = 30

    AGGREGATE_TYPES = ((ATOMIC, "atomic"),
                       (LIST, "list"),
                       (TABLE, "table"))

    def is_atomic (self):
        return 0

    def is_int (self):
        return 0

    def is_string (self):
        return 0

    def is_physical_value (self):
        return 0

    def is_atomic_physical_value (self):
        return self.is_atomic() and self.is_physical_value()

    def is_material (self):
        return 0

    def is_boolean (self):
        return 0

    def is_list (self):
        return 0

    def is_table (self):
        return 0

    def is_discrete (self, constraint):
        raise NotImplementedError

    def allow_tolerance (self):
        return False

    def get_unit (self):
        return None

    def get_compatible_units (self):
        return None

    def check_value (self, value):
        """Checks that the *type* of value is compatible
        with this type of parameter.
        Raise ParamTypeError if problems are discovered.
        """
        raise NotImplementedError

    def supports_simplify (self):
        return True

    def supports_constraints (self):
        "Returns true if setting constraints makes sense for this type."
        return True

    def check_constraint (self, constraint):
        """Checks that constraint is a sequence of
        items whose types are compatible with this type
        of parameter.
        Raise ParamTypeError if problems are discovered.
        """
        if constraint is None:
            return
        if type(constraint) is list:
            for item in constraint:
                self.check_value(item)
        else:
            raise ParamTypeError, (
                'invalid constraint %r for %r' % (constraint, self))

    def check_value_in_constraint (self, value, constraint):
        if not in_set(value, constraint):
            self.value_in_constraint_error(value, constraint)

    def check_set_in_constraint (self, set, constraint):
        self.check_constraint(set)
        if constraint is None or set == constraint:
            return
        if set is None:
            raise ConstraintError
        for element in set:
            if not in_set(element, constraint):
                raise ConstraintError(
                    '%s not within constraint %s' % (element, constraint))


    def value_in_constraint_error (self, bad_value, constraint):
        raise ConstraintError(
            '%s not allowed: %s' % (bad_value,
                                    self.explain_constraint(constraint)))

    def explain_constraint (self, constraint, html=0):
        if html:
            texttype = htmltext
        else:
            texttype = str
        if not constraint:
            return None
        else:
            set = self.format_set(constraint, html=html)
            if set is None:
                return None
            elif len(set) <= 2:
                return texttype("must be ") + texttype(" or ").join(set)
            else:
                return texttype("must be one of ") + texttype(", ").join(set)

    def value_error (self, value):
        raise ParamTypeError(
            'invalid value %r for %r' % (value, self))

    def format_value (self, value, html=0):
        if html:
            return htmlescape(value)
        else:
            return str(value)

    def format_set (self, set, html=False):
        """(set:[any], html:bool=False) -> [str|htmltext]
        Return a list of nice string (or htmltext) renderings of the elements
        of set, which is a constraint for this parameter type.

        Implemented in subclasses.
        """
        raise NotImplementedError

    def format_constraint (self, set, html=0):
        if set is not None:
            formatted_set = self.format_set(set, html=html)
            if formatted_set is not None:
                if html:
                    comma = htmltext(", ")
                else:
                    comma = ", "
                return comma.join(formatted_set)
        if html:
            return htmltext('<em>unconstrained</em>')
        else:
            return '(unconstrained)'


class IntParameterType (ParameterType):

    def get_key (self):
        return (ParameterType.ATOMIC, ParameterType.INT,
                None, None, None)

    def is_atomic (self):
        return 1

    def is_int (self):
        return 1

    def is_discrete(self, constraint):
        if constraint is None:
            return False
        for item in constraint:
            if isinstance(item, RangeValue):
                return False
        return True

    def __str__ (self):
        return "Int"

    def check_value (self, value):
        if value is None:
            return
        if type(value) is int:
            return
        if isinstance(value, RangeValue):
            if type(value.get_min()) is int:
                return
        self.value_error(value)

    def simplify_value (self, value):
        return value

    def reconstitute_value (self, value):
        return value

    def format_set (self, set, html=0):
        if html:
            return map(htmlescape, set)
        else:
            return map(str, set)

    def get_constraint_range (self, constraint):
        if constraint is None:
            return None

        def get_min_and_max (val):
            if isinstance(val, RangeValue):
                return val.get_min(), val.get_max()
            else:
                return val, val

        val_min, val_max = get_min_and_max(constraint[0])
        for value in constraint[1:]:
            next_min, next_max = get_min_and_max(value)
            val_min = min(val_min, next_min)
            val_max = max(val_max, next_max)
        return RangeValue(val_min, val_max)

class StringParameterType (ParameterType):

    def get_key (self):
        return (ParameterType.ATOMIC, ParameterType.STRING,
                None, None, None)

    def is_atomic (self):
        return 1

    def is_string (self):
        return 1

    def is_discrete (self, constraint):
        if constraint is None:
            return False
        else:
            return True

    def __str__ (self):
        return "String"

    def check_value (self, value):
        if value is None:
            return
        if string(value):
            return
        self.value_error(value)

    def simplify_value (self, value):
        return value

    def reconstitute_value (self, value):
        return value

    def format_set (self, set, html=0):
        return set

class BooleanParameterType (ParameterType):

    def get_key (self):
        return (ParameterType.ATOMIC, ParameterType.BOOLEAN,
                None, None, None)

    def is_atomic (self):
        return 1

    def is_boolean (self):
        return 1

    def is_discrete(self, constraint):
        return True

    def __str__ (self):
        return "Boolean"

    def check_value (self, value):
        if value in (True, False, None):
            return
        self.value_error(value)

    def simplify_value (self, value):
        return value

    def reconstitute_value (self, value):
        return value

    def supports_constraints (self):
        return False

    def format_value (self, value, html=0):
        if value:
            return 'yes'
        else:
            return 'no'

    def format_constraint (self, set, html=0):
        if html:
            return htmltext('<em>yes</em> or <em>no</em>')
        else:
            return '(yes or no)'


class PhysicalValueParameterType (ParameterType):

    sub_type_is = (None, PhysicalUnit)

    def __init__ (self, sub_type):
        assert sub_type is None or isinstance(sub_type, PhysicalUnit), (
            'invalid sub_type %r for %r' % (sub_type, self))
        self.sub_type = sub_type

    def get_key (self):
        return (ParameterType.ATOMIC, ParameterType.PHYSICAL_VALUE,
                None, self.sub_type, None)

    def get_unit (self):
        return self.sub_type

    def get_compatible_units (self):
        unit = self.get_unit()
        if not unit:
            return []
        return local.get_standard_units().get_compatible_units(unit)

    def is_atomic (self):
        return 1

    def is_physical_value (self):
        return 1

    def is_discrete(self, constraint):
        if constraint is None:
            return False
        for item in constraint:
            if item.is_range():
                return False
        return True

    def allow_tolerance(self):
        return True

    def __str__ (self):
        if self.sub_type is None:
            return "PhysicalValue"
        else:
            return "PhysicalValue (%s)" % self.sub_type

    def check_value (self, value):
        if value is None:
            return
        if isinstance(value, PhysicalValue):
            if self.sub_type is value.get_unit():
                return
            if self.sub_type and self.sub_type.is_compatible(value.get_unit()):
                return
        self.value_error(value)

    def get_constraint_range (self, constraint):
        if constraint is None:
            return None

        val_min = constraint[0].get_min()
        val_max = constraint[0].get_max()
        for value in constraint[1:]:
            val_min = min(val_min, value.get_min())
            val_max = max(val_max, value.get_max())
        assert val_min.get_unit() is val_max.get_unit(), (
            'unmatched units %r and %r for %r' % (val_min.get_unit(),
                                                  val_max.get_unit(),
                                                  self))
        return PhysicalValue(RangeValue(val_min.get_value(),
                                        val_max.get_value()),
                             val_min.get_unit())

    def simplify_value (self, value):
        default_unit = self.get_unit()
        if value.unit is not default_unit:
            value = value.convert(default_unit)
        return value.value

    def reconstitute_value (self, value):
        if string(value) and value.find(' .. ') != -1:
            value = RangeValue(*map(float, value.split(' .. ', 1)))
        return PhysicalValue(value, self.get_unit())

    def format_value (self, value, html=0):
        if isinstance(value, PhysicalValue):
            return value.format(html=html)
        return stringify(value)

    def format_set (self, set, html=0):
        items = [value.format(show_unit=0, html=html)
                 for value in set[0:-1]]
        items.append(set[-1].format(show_unit=1, html=html))
        return items


class MaterialParameterType (ParameterType):

    def get_key (self):
        return (ParameterType.ATOMIC, ParameterType.MATERIAL,
                None, None, None)

    def is_atomic (self):
        return 1

    def is_material (self):
        return 1

    def is_discrete(self, constraint):
        return True

    def __str__ (self):
        return "Material"

    def check_value (self, value):
        if (value is None or
            isinstance(value, Material)):
            return
        self.value_error(value)

    def check_value_in_constraint (self, value, constraint):
        for material in constraint:
            if value.is_descendant_of(material):
                break
        else:
            self.value_in_constraint_error(value, constraint)

    def simplify_value (self, value):
        return value.get_name()

    def reconstitute_value (self, value):
        material = local.get_material_db().get_material(value)
        if material is None:
            raise ParamTypeError, 'unknown material %r' % value
        return material
            

    def format_set (self, set, html=0):
        if len(set) == len(local.get_material_db().get_materials()):
            return None
        else:
            return [value.get_label()
                    for value in set]


class ListParameterType (ParameterType):

    element_type_is = ParameterType

    def __init__ (self, element_type):
        assert isinstance(element_type, ParameterType), (
            'invalid element_type %r for %r' % (element_type, self))
        self.element_type = element_type

    def get_key (self):
        element_key = self.element_type.get_key()
        return (ParameterType.LIST, element_key[1],
                None, element_key[3], None)

    def is_int (self):
        return self.element_type.is_int()

    def is_string (self):
        return self.element_type.is_string()

    def is_physical_value (self):
        return self.element_type.is_physical_value()

    def get_compatible_units (self):
        return self.element_type.get_compatible_units()

    def get_unit (self):
        return self.element_type.get_unit()

    def is_material (self):
        return self.element_type.is_material()

    def is_list (self):
        return 1

    def is_discrete(self, constraint):
        return self.element_type.is_discrete(constraint)

    def __str__ (self):
        return "List of %s" % self.element_type

    def check_value (self, value):
        if value is None:
            return
        if type(value) is list:
            for val in value:
                self.element_type.check_value(val)
            return
        self.value_error(value)

    def supports_simplify (self):
        return False

    def supports_constraints (self):
        return self.element_type.supports_constraints()

    def check_value_in_constraint (self, values, constraint):
        for value in values:
            self.element_type.check_value_in_constraint(value, constraint)

    def check_constraint (self, constraint):
        self.element_type.check_constraint(constraint)

    def format_value (self, value, html=0):
        fv = self.element_type.format_value
        values_format = [fv(val, html=html) for val in value]
        if html:
            comma = htmltext(", ")
        else:
            comma = ", "
        return comma.join(values_format)

    def format_set (self, set, html=0):
        return self.element_type.format_set(set, html=0)


class TableParameterType (ParameterType):

    key_type_is = ParameterType
    element_type_is = ParameterType

    def __init__ (self, element_type, key_type):
        assert isinstance(element_type, ParameterType), (
            'invalid element_type %r for %r' % (element_type, self))
        assert isinstance(key_type, ParameterType), (
            'invalid key_type %r for %r' % (key_type, self))
        self.element_type = element_type
        self.key_type = key_type

    def get_key (self):
        element_key = self.element_type.get_key()
        key_key = self.key_type.get_key()
        return (ParameterType.TABLE, element_key[1],
                key_key[1], element_key[3], key_key[3])

    def is_int (self):
        return self.element_type.is_int()

    def is_string (self):
        return self.element_type.is_string()

    def is_physical_value (self):
        return self.element_type.is_physical_value()

    def get_compatible_units (self):
        return (self.key_type.get_compatible_units() or
                self.element_type.get_compatible_units())

    def get_unit (self):
        return self.element_type.get_unit()

    def is_material (self):
        return self.element_type.is_material()

    def is_key_int (self):
        return self.key_type.is_int()

    def is_key_string (self):
        return self.key_type.is_string()

    def is_key_physical_value (self):
        return self.key_type.is_physical_value()

    def is_key_material (self):
        return self.key_type.is_material()

    def is_table (self):
        return 1

    def is_discrete(self, constraint):
        assert constraint is None, 'cannot constrain %r' % self
        return False

    def get_key_type (self):
        return self.key_type

    def get_element_type (self):
        return self.element_type

    def __str__ (self):
        return "Table (%s to %s)" % (self.key_type, self.element_type)

    def check_value (self, value):
        if value is None:
            return
        if type(value) is dict:
            for key, val in value.items():
                self.key_type.check_value(key)
                self.element_type.check_value(val)
            return
        self.value_error(value)

    def supports_simplify (self):
        return False

    def supports_constraints (self):
        "Returns true if setting constraints makes sense for this type."
        return False

    def check_value_in_constraint (self, value, constraint):
        assert constraint is None, 'cannot constrain %r' % self

    def check_constraint (self, constraint):
        assert constraint is None, 'cannot constrain %r' % self

    def format_value (self, value, html=0):
        if html:
            texttype = htmltext
        else:
            texttype = str
        rows = [texttype("%s: %s") % (
                    self.key_type.format_value(key, html=html),
                    self.element_type.format_value(value, html=html))
                for key, value in value.items()]
        rows.sort()
        return texttype(", ").join(rows)


def create_atomic_type (element_type, element_sub_type=None):
    if element_type == ParameterType.INT:
        parameter_type = IntParameterType()
    elif element_type == ParameterType.STRING:
        parameter_type = StringParameterType()
    elif element_type == ParameterType.PHYSICAL_VALUE:
        parameter_type = PhysicalValueParameterType(element_sub_type)
    elif element_type == ParameterType.MATERIAL:
        parameter_type = MaterialParameterType()
    elif element_type == ParameterType.BOOLEAN:
        parameter_type = BooleanParameterType()
    else:
        assert False, 'unknown atomic type %r' % element_type
    return parameter_type


def get_parameter_type (*args, **kw):
    return local.get_parameter_db().get_parameter_type(*args, **kw)

def get_physical_value_parameter_type (unit_string=None):
    unit = unit_string and get_standard_unit(unit_string)
    return get_parameter_type(ParameterType.ATOMIC,
                              ParameterType.PHYSICAL_VALUE,
                              element_sub_type=unit)

def get_list_of_physical_value_parameter_type (unit_string=None):
    unit = unit_string and get_standard_unit(unit_string)
    return get_parameter_type(ParameterType.LIST,
                              ParameterType.PHYSICAL_VALUE,
                              element_sub_type=unit)

def get_int_parameter_type ():
    return get_parameter_type(ParameterType.ATOMIC,
                              ParameterType.INT)

def get_list_of_int_parameter_type ():
    return get_parameter_type(ParameterType.LIST,
                              ParameterType.INT)

def get_string_parameter_type ():
    return get_parameter_type(ParameterType.ATOMIC,
                              ParameterType.STRING)

def get_list_of_string_parameter_type ():
    return get_parameter_type(ParameterType.LIST,
                              ParameterType.STRING)

def get_boolean_parameter_type ():
    return get_parameter_type(ParameterType.ATOMIC,
                              ParameterType.BOOLEAN)

def get_material_parameter_type ():
    return get_parameter_type(ParameterType.ATOMIC,
                              ParameterType.MATERIAL)

def get_list_of_material_parameter_type ():
    return get_parameter_type(ParameterType.LIST,
                              ParameterType.MATERIAL)

def get_string_int_table_parameter_type ():
    return get_parameter_type(ParameterType.TABLE,
                              ParameterType.INT,
                              key_type=ParameterType.STRING)

def get_physical_value_int_table_parameter_type (unit_string=None):
    unit = unit_string and get_standard_unit(unit_string)
    return get_parameter_type(ParameterType.TABLE,
                              element_type=ParameterType.INT,
                              key_type=ParameterType.PHYSICAL_VALUE,
                              key_sub_type=unit)



class ParameterDatabase (Persistent):

    parameter_types_is = spec(
        mapping({(int, int, (None, int), anything, anything): ParameterType},
                PersistentDict),
        "The first three elements of the tuple are constants, defined "
        "in ParameterType that identify the aggregate type, the key "
        "type, and the element type of this particular ParameterType. "
        "The last two elements of the tuple identify subtypes of "
        "the key and the element types.  These subtypes are "
        "usually instances of PhysicalUnit.")
    master_templates_is = spec(
        mapping({str:instance('MasterTemplate')}, PersistentDict),
        "master templates by name")

    def __init__(self):
        self.parameter_types = PersistentDict()
        self.master_templates = PersistentDict()


    def add_master_template(self, master):
        require(master, dulcinea.param.parameter_template.MasterTemplate)
        if self.master_templates.has_key(master.get_name()):
            raise ValueError, ("MasterTemplate '%s' is already defined in "
                               "the process_library" % master.get_name())
        self.master_templates[master.get_name()] = master

    def rename_master_template(self, master, new_name):
        """(master : MasterTemplate, new_name : string)

        This should only be called by MasterTemplate.set_name()
        """
        if not self.master_templates.has_key(master.get_name()):
            raise ValueError, ("MasterTemplate '%s' is not defined in "
                               "the process_library" % master.get_name())
        if self.master_templates.has_key(new_name):
            raise ValueError, ("MasterTemplate '%s' is already defined in "
                               "the process_library" % master.get_name())
        old_name = master.get_name()
        master.set_name(new_name)
        del self.master_templates[old_name]
        self.master_templates[new_name] = master

    def get_master_template(self, name):
        return self.master_templates.get(name)

    def get_master_templates(self):
        return self.master_templates.values()

    def _create_parameter_type(self,
                               aggregate_type,
                               element_type,
                               key_type=None,
                               element_sub_type=None,
                               key_sub_type=None):
        assert aggregate_type is ParameterType.TABLE or (
            key_type is None and key_sub_type is None), (
            "invalid type creation: key_type %r or key_sub_type %r "
            "defined for non table type" % (key_type, key_sub_type))
        assert element_type is ParameterType.PHYSICAL_VALUE or (
            element_sub_type is None), (
            "invalid type creation: element_type %r does not take "
            "sub_type argument %r" % (element_type, element_sub_type))

        if aggregate_type is ParameterType.ATOMIC:
            parameter_type = create_atomic_type(element_type,
                                                element_sub_type)

        elif aggregate_type is ParameterType.LIST:
            element_inst = self.get_parameter_type(
                ParameterType.ATOMIC, element_type,
                element_sub_type=element_sub_type)
            parameter_type = ListParameterType(element_inst)

        elif aggregate_type is ParameterType.TABLE:
            assert key_type is ParameterType.PHYSICAL_VALUE or (
                key_sub_type is None), (
                "invalid type creation: key_type %r does not take "
                "sub_type argument %r" % (key_type, key_sub_type))
            element_inst = self.get_parameter_type(
                ParameterType.ATOMIC, element_type,
                element_sub_type=element_sub_type)
            key_inst = self.get_parameter_type(
                ParameterType.ATOMIC, key_type, element_sub_type=key_sub_type)
            parameter_type = TableParameterType(element_inst, key_inst)

        else:
            assert False, (
                "unknown aggregate type: %r" % aggregate_type)

        self.parameter_types[(aggregate_type,
                              element_type,
                              key_type,
                              element_sub_type,
                              key_sub_type)] = parameter_type

        return parameter_type


    def get_parameter_type(self,
                           aggregate_type,
                           element_type,
                           key_type=None,
                           element_sub_type=None,
                           key_sub_type=None):
        parameter_type = self.parameter_types.get((aggregate_type,
                                                   element_type,
                                                   key_type,
                                                   element_sub_type,
                                                   key_sub_type))
        if parameter_type is None:
            parameter_type = self._create_parameter_type(aggregate_type,
                                                         element_type,
                                                         key_type,
                                                         element_sub_type,
                                                         key_sub_type)
        return parameter_type

