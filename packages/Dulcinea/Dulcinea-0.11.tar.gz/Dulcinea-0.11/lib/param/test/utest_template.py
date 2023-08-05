"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/param/test/utest_template.py $
$Id: utest_template.py 27556 2005-10-13 14:04:46Z dbinger $
"""
from dulcinea import local
from dulcinea.material import Material
from dulcinea.param.errors import ParamTypeError, ConstraintError
from dulcinea.param.parameter_template import MasterTemplate
from dulcinea.param.parameter_type import ParameterType
from dulcinea.param.parameter_type import get_material_parameter_type
from dulcinea.param.parameter_type import get_physical_value_parameter_type
from dulcinea.param.parameter_type import get_string_parameter_type
from dulcinea.physical_unit import get_standard_unit
from dulcinea.physical_value import PhysicalValue
from dulcinea.range_value import RangeValue
from sancho.utest import UTest, raises
from sets import Set


class TestTemplateParameter (UTest):

    def _pre(self):
        local.open_database()
        self.plib = local.get_parameter_db()
        get_type = self.plib.get_parameter_type
        self.int_type = get_type(ParameterType.ATOMIC,
                                 ParameterType.INT)
        self.material_type = get_type(ParameterType.ATOMIC,
                                      ParameterType.MATERIAL)
        pv1 = PhysicalValue(100, "degC")
        pv2 = PhysicalValue(1, "mm")
        pv3 = PhysicalValue(1, "min")
        self.pv_type = get_type(ParameterType.ATOMIC,
                                   ParameterType.PHYSICAL_VALUE,
                                   element_sub_type=pv1.unit)
        self.pv_len_type = get_type(ParameterType.ATOMIC,
                                    ParameterType.PHYSICAL_VALUE,
                                    element_sub_type=pv2.unit)
        self.pv_time_type = get_type(ParameterType.ATOMIC,
                                     ParameterType.PHYSICAL_VALUE,
                                     element_sub_type=pv3.unit)

        self.upv_type = get_type(ParameterType.ATOMIC,
                                    ParameterType.PHYSICAL_VALUE)
        self.pv_list_type = get_type(ParameterType.LIST,
                                     ParameterType.PHYSICAL_VALUE,
                                     element_sub_type=pv2.unit)
        self.pv_time_list_type = get_type(ParameterType.LIST,
                                          ParameterType.PHYSICAL_VALUE,
                                          element_sub_type=pv3.unit)
        self.mat_list_type = get_type(ParameterType.LIST,
                                      ParameterType.MATERIAL)
        self.str_pv_table_type = get_type(ParameterType.TABLE,
                                          ParameterType.PHYSICAL_VALUE,
                                          key_type=ParameterType.STRING,
                                          element_sub_type=pv2.unit)
        self.str_mat_table_type = get_type(ParameterType.TABLE,
                                           ParameterType.MATERIAL,
                                           key_type=ParameterType.STRING)

    def _post(self):
        local.close_database()

    def check_basic(self):
        template = MasterTemplate("foo", self.int_type, description="bar")

        assert template.get_name() == "foo"
        assert template.get_description() == "bar"
        assert template.get_title() == "Foo"
        template.set_description(None)
        template.title=None

        template.name = "foo_bar"
        assert template.get_title() == None

        # illegal parameter name
        raises(TypeError, MasterTemplate, '123', self.int_type)

        # unknown type
        raises(TypeError, MasterTemplate, 'blah', 'xint')


    def check_unconstrained(self):
        nocon_template = MasterTemplate('foo', self.int_type)
        assert nocon_template.get_constraint() == None
        assert nocon_template.format() == "(unconstrained)"
        assert nocon_template.explain_constraint() == None
        assert not nocon_template.is_discrete()
        nocon_template.check_value(-23432)
        nocon_template.check_value(124321431)
        raises(ParamTypeError, nocon_template.check_value, 'foo')

    def check_simple_set_constr (self):
        # material constraints are a special case of strings ...
        silicon = local.get_material_db().get_material('silicon')
        boron = local.get_material_db().get_material('boron')
        gold = local.get_material_db().get_material('gold')
        silicon_or_boron = Material('silicon_or_boron')
        silicon_or_boron.set_label('silicon or boron')
        silicon_or_boron.add_child(silicon)
        silicon_or_boron.add_child(boron)
        mat_template = MasterTemplate(
            'substrate', self.material_type,
            constraint=[silicon_or_boron])
        assert mat_template.get_constraint_unit() == None
        assert Set(mat_template.get_constraint()) == Set([silicon_or_boron])
        assert mat_template.is_discrete()
        mat_template.check_value(silicon)
        raises(ConstraintError, mat_template.check_value, gold)

        assert mat_template.explain_constraint() == "must be silicon or boron"
        assert mat_template.format() == "silicon or boron"

        int_template = MasterTemplate('foo', self.int_type,
                                      constraint=[10, 20])
        assert int_template.get_constraint_range() == RangeValue(10, 20)
        assert int_template.is_discrete()
        assert int_template.format() == "10, 20"
        assert int_template.explain_constraint() == "must be 10 or 20"

    def check_pv_set_constr (self):
        # Try PhysicalValues with unit (this time, three values in the set,
        # because that's a different case in explain_constraint()).
        pv1 = PhysicalValue(100, "degC")
        pv2 = PhysicalValue(150, "degC")
        pv3 = PhysicalValue(200, "degC")
        pv4 = PhysicalValue(RangeValue(250, 300), "degC")
        pv5 = PhysicalValue(10, "degF")

        temp_template = MasterTemplate('temperature', self.pv_type,
                                       constraint=[pv1, pv2, pv3, pv4])
        assert Set(temp_template.get_constraint()) == Set([pv1, pv2, pv3, pv4])
        assert not temp_template.is_discrete()
        temp_template.check_value(PhysicalValue(100, 'degC'))
        temp_template.check_value(PhysicalValue(212, 'degF'))
        temp_template.check_value(PhysicalValue(270, 'degC'))
        temp_template.check_value(PhysicalValue(550, 'degF'))
        raises(ConstraintError,
               temp_template.check_value, PhysicalValue(101, 'degC'))

        assert temp_template.format(html=1) == (
                      "100, 150, 200, 250 .. 300&nbsp;&deg;C")
        assert temp_template.format(html=0) == (
                      "100, 150, 200, 250 .. 300 degC")
        assert temp_template.explain_constraint() == (
                    "must be one of 100, 150, 200, 250 .. 300 degC")
        assert temp_template.explain_constraint(html=1) == (
                    "must be one of 100, 150, 200, 250 .. 300&nbsp;&deg;C")

        # Now unitless PhysicalValues because the formatting is different.
        pv1 = PhysicalValue(50)
        pv2 = PhysicalValue(60)
        foo_template = MasterTemplate('foo', self.upv_type,
                                      constraint=[pv1, pv2])
        assert Set(foo_template.get_constraint()) == Set([pv1, pv2])
        foo_template.check_value(PhysicalValue(50))
        raises(ParamTypeError, foo_template.check_value, 50)
        assert foo_template.format() == "50, 60"
        assert foo_template.explain_constraint() == "must be 50 or 60"

    def check_aggr_set_constr (self):
        depth_100 = PhysicalValue(100, "um")
        depth_150 = PhysicalValue(150, "um")
        depth_200 = PhysicalValue(200, "um")

        gold = local.get_material_db().get_material('gold')
        aluminum = local.get_material_db().get_material('aluminum')
        silver = local.get_material_db().get_material('silver')
        boron = local.get_material_db().get_material('boron')
        three_metals = Material('three_metals')
        three_metals.add_child(gold)
        three_metals.add_child(aluminum)
        three_metals.add_child(silver)
        valid_depths = [depth_100, depth_200]
        matl_template = MasterTemplate("material", self.mat_list_type,
                                       constraint=[three_metals])
        depth_template = MasterTemplate("depth",
                                        self.pv_list_type,
                                        constraint=valid_depths)

        raises(ParamTypeError, matl_template.check_value, gold)
        raises(ParamTypeError, matl_template.check_value, boron)
        matl_template.check_value([gold])
        raises(ConstraintError, matl_template.check_value, [boron])
        raises(ConstraintError, matl_template.check_value, [gold, boron])
        matl_template.check_value([gold, silver])

        raises(ParamTypeError, depth_template.check_value, depth_100)
        depth_template.check_value([depth_100])
        raises(ConstraintError,
               depth_template.check_value, [depth_100, depth_150])
        depth_template.check_value([depth_200, depth_100])


    def check_allowed_units(self):
        min = get_standard_unit("min")
        sec = get_standard_unit("s")
        hour = get_standard_unit("hour")

        int_template = MasterTemplate('foo', self.int_type)
        assert int_template.get_default_unit() == None

        pv_template = MasterTemplate('duration', self.pv_time_type)
        assert min in pv_template.get_allowed_units()
        assert sec in pv_template.get_allowed_units()
        assert pv_template.get_default_unit() == min
        assert pv_template.is_allowed_unit(min)
        assert pv_template.is_allowed_unit('min')
        assert pv_template.is_allowed_unit(hour)

        # Ensure that check_value() enforces allowed_units
        pv1 = PhysicalValue(2, "min")
        pv2 = PhysicalValue(3, "day")
        pv3 = PhysicalValue(1.5, "m")
        pv4 = PhysicalValue(1.5)

        raises(ParamTypeError, int_template.check_value, pv1)
        pv_template.check_value(pv1)
        raises(ParamTypeError, pv_template.check_value, pv3)
        raises(ParamTypeError, pv_template.check_value, pv4)
        raises(ParamTypeError, pv_template.check_value, 1.5)

        list_template = MasterTemplate('durations',
                                       self.pv_time_list_type)
        list_template.check_value([])
        list_template.check_value([pv1])
        list_template.check_value([pv1, pv1*3])

        raises(ParamTypeError, list_template.check_value, [pv1, pv3])
        raises(ParamTypeError, list_template.check_value, [pv4])

    def check_consistent_units (self):
        pv1 = PhysicalValue(1, "mm")
        pv2 = PhysicalValue(1.5, "mm")
        pv3 = PhysicalValue(1000, "um")
        mm_um = [pv1.unit, pv3.unit]
        templ1 = MasterTemplate('pvlist',
                                self.pv_list_type)
        templ2 = MasterTemplate('pvtable',
                                self.str_pv_table_type)

        templ1.check_value([])
        templ1.check_value([pv1])
        templ1.check_value([pv1, pv2])

        value = {'foo': pv1, 'bar': pv2}
        templ2.check_value(value)
        del value['foo']
        templ2.check_value(value)


    def check_factories (self):
        templ = MasterTemplate('duration', self.pv_time_type)
        pv1 = PhysicalValue(20.0, "min")
        pv2 = PhysicalValue(25.0, "min")
        try:
            templ.create_value(10)
            assert 0
        except ParamTypeError: pass
        param1 = templ.create_value(pv1)
        assert param1.get_name() == templ.get_name()
        assert param1.get_type() == templ.get_type()
        assert param1.get_value() == pv1
        assert param1.template is templ

        param2 = templ.create_input_template(constraint=[pv1, pv2])
        assert param2.get_constraint() == [pv1, pv2]
        assert param2.get_name() == templ.get_name()
        assert param2.get_type() == templ.get_type()
        assert param2.template == templ

        pv3 = PhysicalValue(30.0, "min")
        assert param2.get_default_value() == None
        try:
            param2.set_default_value('bad')
            assert 0
        except ParamTypeError: pass
        try:
            param2.set_default_value(pv3)
            assert 0
        except ConstraintError: pass
        param2.set_default_value(pv2)
        assert param2.get_default_value() == pv2

        set_templ = MasterTemplate("spam", self.int_type, constraint=[1, 10])
        set_templ.create_input_template(constraint=[1,10])

    def check_copy (self):
        foo1 = MasterTemplate("foo", self.int_type, constraint=[1, 5])
        foo2 = foo1.copy()
        assert foo1 is not foo2
        assert foo1.name == foo2.name
        assert foo1.type is foo2.type
        assert foo1.title == foo2.title
        assert foo1.description is foo2.description is None
        assert foo1.constraint == foo2.constraint

        bar1 = MasterTemplate("bar", self.pv_len_type,
                              constraint=[PhysicalValue(1, "um"),
                              PhysicalValue(2, "um")])
        bar2 = bar1.copy()
        assert bar1 is not bar2
        assert bar1.name == bar2.name
        assert bar1.type is bar2.type
        assert bar1.constraint == bar2.constraint
        assert bar1.constraint[0] == bar2.constraint[0]
        assert bar1.constraint[0].unit is bar2.constraint[0].unit

    def check_simplify (self):
        # physical value
        constraint = [PhysicalValue(RangeValue(0, 10), 'um')]
        pv_um = get_physical_value_parameter_type('um')
        depth_templ = MasterTemplate("depth", pv_um, constraint=constraint)
        assert depth_templ.simplify() == RangeValue(0, 10)
        depth_param = depth_templ.create_value(PhysicalValue(5300, "nm"))
        assert depth_param.simplify() == 5.3

        # material
        material_db = local.get_material_db()
        photoresist = material_db.get_material('blah')
        resist = material_db.get_material("blah")
        material_templ = MasterTemplate("material",
                                        get_material_parameter_type(),
                                        constraint=[photoresist])
        material_param = material_templ.create_value(resist)
        assert material_param.simplify() == resist.get_name()

        # string
        string_templ = MasterTemplate("letter",
                                      get_string_parameter_type(),
                                      constraint=["a", "b", "c"])
        string_param = string_templ.create_value("a")
        assert string_param.simplify() == "a"


if __name__ == "__main__":
    TestTemplateParameter()
