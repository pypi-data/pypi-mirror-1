"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/param/test/utest_list.py $
$Id: utest_list.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea import local
from dulcinea.param.parameter import Parameter
from dulcinea.param.parameter_list import ParameterList
from dulcinea.param.parameter_template import MasterTemplate
from dulcinea.param.parameter_type import ParameterType
from dulcinea.physical_value import PhysicalValue
from sancho.utest import UTest

class TestParameterList (UTest):

    def _pre(self):
        local.open_database()
        get_type = local.get_parameter_db().get_parameter_type
        self.int_type = get_type(ParameterType.ATOMIC,
                                 ParameterType.INT)
        sec = PhysicalValue(1, 's').unit
        self.pv_type = get_type(ParameterType.ATOMIC,
                                ParameterType.PHYSICAL_VALUE,
                                element_sub_type=sec)
        um =  PhysicalValue(1, 'um').unit
        self.pv_um_type = get_type(ParameterType.ATOMIC,
                                ParameterType.PHYSICAL_VALUE,
                                element_sub_type=um)
        self.str_list_type = get_type(ParameterType.LIST,
                                      ParameterType.STRING)
        self.str_int_table_type = get_type(ParameterType.TABLE,
                                           ParameterType.INT,
                                           key_type=ParameterType.STRING)

    def _post(self):
        local.close_database()

    def check_basic (self):
        template = MasterTemplate('downtime', self.pv_type)
        parameter = template.create_value()
        ParameterList([parameter])
        ParameterList([template])
        ParameterList([parameter])
        ParameterList([template])
        try:
            ParameterList([parameter, object()])
            assert 0
        except TypeError: pass

    def check_filtering (self):
        template = MasterTemplate("a", self.int_type)
        parameter = Parameter(MasterTemplate("b", self.pv_type))
        plist = ParameterList([template, parameter])
        assert list(plist.get_value_parameters()) == [parameter]
        assert list(plist.get_templates()) == [template]
        assert list(plist.get_visible()) == [template, parameter]
        assert list(plist + []) == list(plist)

if __name__ == "__main__":
    TestParameterList()
