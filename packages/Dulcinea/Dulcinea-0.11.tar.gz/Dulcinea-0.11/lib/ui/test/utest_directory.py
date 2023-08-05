"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/ui/test/utest_directory.py $
$Id: utest_directory.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea.ui.directory import DynamicExportingDirectory
from sancho.utest import UTest


class DirectoryTest (UTest):

    def a(self):
        class Dir (DynamicExportingDirectory):
            pass
        try:
            Dir()._q_translate('')
            assert 0
        except AttributeError:
            pass

    def b(self):
        class Dir (DynamicExportingDirectory):
            def get_exports(self):
                return []
        return Dir()._q_translate('') is None

    def c(self):
        class Dir (DynamicExportingDirectory):
            def get_exports(self):
                return [('')]
        try:
            Dir()._q_translate('') is None
            assert 0
        except ValueError:
            pass

    def d(self):
        class Dir (DynamicExportingDirectory):
            def get_exports(self):
                return [('', '_q_index', 'crumb', 'title')]
        assert Dir()._q_translate('') == '_q_index'

if __name__ == "__main__":
    DirectoryTest()
