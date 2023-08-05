"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/param/test/utest_param.py $
$Id: utest_param.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea import local
from dulcinea.param import parameter_type as PT
from dulcinea.param.errors import ParamTypeError
from dulcinea.param.parameter import Parameter
from dulcinea.param.parameter_template import MasterTemplate
from dulcinea.physical_unit import get_standard_unit
from dulcinea.physical_value import PhysicalValue
from sancho.utest import UTest


class ParamTest (UTest):

    def _pre (self):
        local.open_database()
        self.int_type = PT.get_int_parameter_type()
        sec = get_standard_unit('s')
        self.pv_type = PT.get_physical_value_parameter_type('s')
        um =  get_standard_unit('um')
        self.pv_um_type = PT.get_physical_value_parameter_type('um')
        self.str_list_type = PT.get_list_of_string_parameter_type()
        self.str_int_table_type = PT.get_string_int_table_parameter_type()

    def _post (self):
        local.close_database()

    def check_basics (self):
        tmpl = MasterTemplate("foo", self.int_type)
        Parameter(tmpl)
        try:
            Parameter(None)
            assert 0
        except TypeError: pass
        Parameter(tmpl, 1)
        try:
            Parameter(tmpl, 1.0)
            assert 0
        except ParamTypeError: pass
        Parameter(tmpl, None)
        # __getattr__ attributes
        p = Parameter(tmpl)
        assert p.get_name() == tmpl.get_name()
        assert p.get_type() == tmpl.get_type()
        assert p.get_title() == tmpl.get_title()
        assert p.get_name() == tmpl.get_name()
        assert p.get_type() == tmpl.get_type()
        try:
            p.spam
            assert 0
        except AttributeError: pass

    def check_values (self):
        # int parameter
        int_param = Parameter(MasterTemplate('foo', self.int_type))
        assert int_param.get_type() == self.int_type
        assert int_param.format() == None
        int_param.set_value(1)
        assert str(int_param) == "foo = 1"
        assert int_param.get_value() == 1
        int_param.set_value(2)
        assert int_param.get_value() == 2
        assert int_param.format() == "2"
        try:
            int_param.set_value(2.1)
            assert 0
        except ParamTypeError: pass

        # pv parameter
        pv = PhysicalValue(1.0, "s")
        tmpl = MasterTemplate("bar", self.pv_type)
        pv_param = Parameter(tmpl, pv)
        assert pv_param.format() == "1 s"
        try:
            pv_param.set_value(1)
            assert 0
        except ParamTypeError: pass
        pv2 = PhysicalValue(2.0, "s")

        # list parameter
        list_param = Parameter(MasterTemplate("baz", self.str_list_type))
        list_param.set_value(['a', 'b'])
        assert list_param.format() == "a, b"

        # table parameter
        v = {"hello": 37}
        p1 = Parameter(MasterTemplate('foo', self.str_int_table_type), v)
        assert p1.format() == "hello: 37"
        assert str(p1) == "foo = hello: 37"

    def check_check (self):
        "parameter value-checking: 9"

        # Most of the work of value-checking is done by
        # MasterTemplate, so most testing is done in
        # test_template.py.  All we need to do here is ensure that
        # Parameter.check_value() correctly falls back on param's
        # current value if no value is passed in.
        templ = MasterTemplate('foo', self.int_type,
                               constraint=[1, 2, 3])
        param = Parameter(templ)
        param.set_value(3)
        try:
            param.set_value('foo')
            assert 0
        except ParamTypeError: pass

    def check_copy (self):
        "copying parameters"
        foo_templ = MasterTemplate("foo", self.int_type,
                                   constraint=[1, 5])
        foo1 = Parameter(foo_templ, value=3)
        foo2 = foo1.copy()
        assert foo1.template is foo2.template
        assert foo1.value is foo2.value

        bar_templ = MasterTemplate("bar", self.pv_um_type)
        bar1 = Parameter(bar_templ, value=PhysicalValue(3.5, "um"))
        bar2 = bar1.copy()
        assert bar1.template is bar2.template
        assert bar1.value is bar2.value
        assert bar1.value.unit is bar2.value.unit

if __name__ == "__main__":
    ParamTest()
