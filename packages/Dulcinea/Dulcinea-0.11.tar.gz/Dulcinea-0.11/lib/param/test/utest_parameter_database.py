"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/param/test/utest_parameter_database.py $
$Id: utest_parameter_database.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea import local
from dulcinea.param.parameter_template import MasterTemplate
from dulcinea.param.parameter_type import get_string_parameter_type
from sancho.utest import UTest

class ParameterDatabaseTest (UTest):

    def check_master_templates (self):
        local.open_database()
        parameter_db = local.get_parameter_db()
        try:
            parameter_db.add_master_template('foo')
            assert 0
        except TypeError: pass

        # Create some templates
        s = get_string_parameter_type()
        self.foo = MasterTemplate('foo',s)
        self.bar = MasterTemplate('bar',s)
        try:
            parameter_db.rename_master_template(self.bar,'foo')
            assert 0
        except ValueError: pass


        # Add templates
        parameter_db.add_master_template(self.foo)
        parameter_db.add_master_template(self.bar)
        try:
            parameter_db.add_master_template(self.foo)
            assert 0
        except ValueError: pass

        # Test renaming of a template
        try:
            parameter_db.rename_master_template(self.bar,'foo')
        except ValueError: pass
        parameter_db.rename_master_template(self.bar,'baz')
        assert self.bar == parameter_db.get_master_template('baz')


if __name__ == "__main__":
    ParameterDatabaseTest()
