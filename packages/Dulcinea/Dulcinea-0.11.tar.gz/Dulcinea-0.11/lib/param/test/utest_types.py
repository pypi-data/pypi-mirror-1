"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/param/test/utest_types.py $
$Id: utest_types.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea import local
from dulcinea.param.errors import ParamTypeError
from dulcinea.param.parameter_type import ParameterType
from dulcinea.physical_unit import get_standard_unit
from dulcinea.physical_value import PhysicalValue
from dulcinea.range_value import RangeValue
from sancho.utest import UTest

class ParameterTypeTest (UTest):

    def _pre (self):
        local.open_database()
        self.plib = local.get_parameter_db()
        self.mdb = local.get_material_db()

    def _post (self):
        del self.plib
        del self.mdb
        local.close_database()

    def check_int_type (self):
        parameter_type1 = self.plib.get_parameter_type(ParameterType.ATOMIC,
                                                       ParameterType.INT)

        assert parameter_type1.is_atomic()
        assert parameter_type1.is_int()
        assert not parameter_type1.is_string()
        assert not parameter_type1.is_physical_value()
        assert not parameter_type1.is_material()
        assert not parameter_type1.is_list()
        assert not parameter_type1.is_table()
        assert not parameter_type1.is_boolean()

        parameter_type2 = self.plib.get_parameter_type(ParameterType.ATOMIC,
                                                       ParameterType.STRING)
        assert parameter_type2 is not parameter_type1
        parameter_type2 = self.plib.get_parameter_type(ParameterType.ATOMIC,
                                                       ParameterType.INT)
        assert parameter_type2 is parameter_type1

        parameter_type1.check_value(None)
        parameter_type1.check_value(10)
        parameter_type1.check_value(RangeValue(10, 20))
        try:
            parameter_type1.check_value([10, 20])
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value('hello')
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value(['hello', 'bye'])
            assert 0
        except ParamTypeError: pass

        try:
            parameter_type2 = self.plib.get_parameter_type(
                ParameterType.ATOMIC, ParameterType.INT, key_type=1)
            assert 0
        except AssertionError: pass

    def check_string_type (self):
        parameter_type1 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.STRING)

        assert parameter_type1.is_atomic()
        assert not parameter_type1.is_int()
        assert parameter_type1.is_string()
        assert not parameter_type1.is_physical_value()
        assert not parameter_type1.is_material()
        assert not parameter_type1.is_list()
        assert not parameter_type1.is_table()
        assert not parameter_type1.is_boolean()

        parameter_type2 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.INT)
        assert parameter_type2 is not parameter_type1
        parameter_type2 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.STRING)
        assert parameter_type2 is parameter_type1

        parameter_type1.check_value(None)
        parameter_type1.check_value('hello')
        try:
            parameter_type1.check_value(['hello', 'bye'])
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value(10)
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value(RangeValue(10, 20))
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value([10, 20])
            assert 0
        except ParamTypeError: pass

    def check_boolean_type (self):
        parameter_type1 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.BOOLEAN)

        assert parameter_type1.is_atomic()
        assert not parameter_type1.is_int()
        assert not parameter_type1.is_string()
        assert not parameter_type1.is_physical_value()
        assert not parameter_type1.is_material()
        assert not parameter_type1.is_list()
        assert not parameter_type1.is_table()
        assert parameter_type1.is_boolean()

        parameter_type2 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.INT)
        assert parameter_type2 is not parameter_type1
        parameter_type2 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.BOOLEAN)
        assert parameter_type2 is parameter_type1

        parameter_type1.check_value(True)
        parameter_type1.check_value(False)
        parameter_type1.check_value(0)
        parameter_type1.check_value(1)
        parameter_type1.check_value(None)
        try:
            parameter_type1.check_value('')
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value([True])
            assert 0
        except ParamTypeError: pass
        assert parameter_type1.format_value(True) == 'yes'
        assert parameter_type1.format_value(0) == 'no'

    def check_physical_value_type (self):
        parameter_type1 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.PHYSICAL_VALUE)

        assert parameter_type1.is_atomic()
        assert not parameter_type1.is_int()
        assert not parameter_type1.is_string()
        assert parameter_type1.is_physical_value()
        assert not parameter_type1.is_material()
        assert not parameter_type1.is_list()
        assert not parameter_type1.is_table()
        assert not parameter_type1.is_boolean()

        parameter_type2 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.PHYSICAL_VALUE)
        assert parameter_type2 is parameter_type1

        inch = get_standard_unit('inch')
        parameter_type2 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.PHYSICAL_VALUE,
            element_sub_type=inch)
        assert parameter_type2 is not parameter_type1

        parameter_type1.check_value(None)
        parameter_type1.check_value(PhysicalValue(10))
        parameter_type1.check_value(PhysicalValue(RangeValue(10, 20)))
        parameter_type2.check_value(PhysicalValue(10, 'inch'))
        parameter_type2.check_value(PhysicalValue(RangeValue(10, 20), 'inch'))
        parameter_type2.check_value(PhysicalValue(10, 'm'))
        parameter_type2.check_value(PhysicalValue(RangeValue(10, 20), 'm'))

        try:
            parameter_type1.check_value(PhysicalValue(10, 'inch'))
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type2.check_value(PhysicalValue(10))
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type2.check_value(PhysicalValue(10, 's'))
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value([PhysicalValue(10)])
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type2.check_value([PhysicalValue(10, 'inch')])
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value(10)
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value(RangeValue(10, 20))
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value([10, 20])
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value('hello')
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value(['hello', 'bye'])
            assert 0
        except ParamTypeError: pass

        try:
            parameter_type2 = self.plib.get_parameter_type(
                ParameterType.ATOMIC, ParameterType.PHYSICAL_VALUE,
                element_sub_type=1)
            assert 0
        except AssertionError: pass
        try:
            parameter_type2 = self.plib.get_parameter_type(
                ParameterType.ATOMIC, ParameterType.PHYSICAL_VALUE, key_type=1)
            assert 0
        except AssertionError: pass
        try:
            parameter_type2 = self.plib.get_parameter_type(
                ParameterType.ATOMIC, ParameterType.PHYSICAL_VALUE, key_sub_type=1)
            assert 0
        except AssertionError: pass

    def check_material_type (self):
        parameter_type1 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.MATERIAL)

        assert parameter_type1.is_atomic()
        assert not parameter_type1.is_int()
        assert not parameter_type1.is_string()
        assert not parameter_type1.is_physical_value()
        assert parameter_type1.is_material()
        assert not parameter_type1.is_list()
        assert not parameter_type1.is_table()
        assert not parameter_type1.is_boolean()

        parameter_type2 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.MATERIAL)
        assert parameter_type2 is parameter_type1

        silicone = self.mdb.get_material('silicone')
        gold = self.mdb.get_material('gold')
        inch = get_standard_unit('inch')

        parameter_type2 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.MATERIAL)
        assert parameter_type2 is parameter_type1

        parameter_type1.check_value(None)
        parameter_type1.check_value(silicone)
        parameter_type1.check_value(gold)
        try:
            parameter_type1.check_value([gold])
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value('hello')
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value(['hello', 'bye'])
            assert 0
        except ParamTypeError: pass
        parameter_type2.check_value(silicone)


    def check_list_type (self):
        parameter_type1 = self.plib.get_parameter_type(
            ParameterType.LIST, ParameterType.INT)
        assert not parameter_type1.is_atomic()
        assert parameter_type1.is_int()
        assert not parameter_type1.is_string()
        assert not parameter_type1.is_physical_value()
        assert not parameter_type1.is_material()
        assert parameter_type1.is_list()
        assert not parameter_type1.is_table()
        assert not parameter_type1.is_boolean()

        parameter_type2 = self.plib.get_parameter_type(
            ParameterType.LIST, ParameterType.INT)
        assert parameter_type2 is parameter_type1
        parameter_type2 = self.plib.get_parameter_type(
            ParameterType.LIST, ParameterType.STRING)
        assert parameter_type2 is not parameter_type1
        parameter_type3 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.STRING)
        assert parameter_type3 is parameter_type2.element_type

        assert not parameter_type2.is_int()
        assert parameter_type2.is_string()

        parameter_type1.check_value(None)
        parameter_type1.check_value([10])
        parameter_type1.check_value([10, 20])
        parameter_type1.check_value([RangeValue(10, 20)])
        parameter_type1.check_value([10, 20, RangeValue(10, 20)])
        try:
            parameter_type1.check_value(10)
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value(RangeValue(10, 20))
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value('hello')
            assert 0
        except ParamTypeError: pass

    def check_table_type (self):
        parameter_type1 = self.plib.get_parameter_type(
            ParameterType.TABLE, ParameterType.PHYSICAL_VALUE,
            key_type=ParameterType.MATERIAL)

        assert not parameter_type1.is_atomic()
        assert not parameter_type1.is_int()
        assert not parameter_type1.is_string()
        assert parameter_type1.is_physical_value()
        assert not parameter_type1.is_material()
        assert not parameter_type1.is_list()
        assert parameter_type1.is_table()
        assert not parameter_type1.is_boolean()

        assert not parameter_type1.is_key_int()
        assert not parameter_type1.is_key_string()
        assert not parameter_type1.is_key_physical_value()
        assert parameter_type1.is_key_material()

        silicone = self.mdb.get_material('silicone')
        gold = self.mdb.get_material('gold')
        inch = get_standard_unit('inch')

        parameter_type2 = self.plib.get_parameter_type(
            ParameterType.TABLE, ParameterType.PHYSICAL_VALUE,
            key_type=ParameterType.MATERIAL)
        assert parameter_type2 is parameter_type1
        parameter_type2 = self.plib.get_parameter_type(
            ParameterType.TABLE, ParameterType.PHYSICAL_VALUE,
            key_type=ParameterType.MATERIAL)
        assert parameter_type2 is parameter_type1
        parameter_type3 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.PHYSICAL_VALUE)
        assert parameter_type3 is parameter_type1.element_type
        assert parameter_type3 is parameter_type2.element_type
        parameter_type3 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.MATERIAL)
        assert parameter_type3 is parameter_type1.key_type
        assert parameter_type3 is parameter_type2.key_type
        parameter_type3 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.MATERIAL)
        assert parameter_type3 is parameter_type1.key_type
        assert parameter_type3 is parameter_type2.key_type
        parameter_type3 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.PHYSICAL_VALUE)
        assert parameter_type3 is parameter_type1.element_type
        parameter_type3 = self.plib.get_parameter_type(
            ParameterType.ATOMIC, ParameterType.MATERIAL)
        assert parameter_type3 is parameter_type1.key_type

        parameter_type1.check_value(None)
        parameter_type1.check_value(
            {gold:PhysicalValue(10),
             silicone:PhysicalValue(RangeValue(10, 20))})

        try:
            parameter_type1.check_value(10)
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value([10])
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value(RangeValue(10, 20))
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value('hello')
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value(PhysicalValue(10))
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value([PhysicalValue(10)])
            assert 0
        except ParamTypeError: pass
        try:
            parameter_type1.check_value([gold])
            assert 0
        except ParamTypeError: pass

        try:
            parameter_type2 = self.plib.get_parameter_type(
                ParameterType.TABLE, ParameterType.INT)
            assert 0
        except AssertionError: pass

if __name__ == "__main__":
    ParameterTypeTest()
