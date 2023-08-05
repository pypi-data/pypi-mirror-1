"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/ui/test/utest_crumbs.py $
$Id: utest_crumbs.py 27325 2005-09-07 18:54:51Z rmasse $
"""

from dulcinea.ui.crumbs import get_crumb_tree, format_crumbs
from dulcinea.ui.crumbs import get_path_directory_list, get_exports
from dulcinea.ui.directory import DynamicExportingDirectory
from dulcinea.ui.util import set_environment, clear_environment
from quixote.directory import Directory
from sancho.utest import UTest
import dulcinea.ui.crumbs

class CrumbTest (UTest):

    def _pre(self):
        clear_environment()

    def _post(self):
        clear_environment()

    def test_get_path_directory_list(self):
        class Dir(DynamicExportingDirectory):
            def _q_traverse(self, component):
                return get_path_directory_list()
        set_environment()
        assert get_path_directory_list() == []
        directory = Dir()
        assert directory._q_traverse('') == [('./', directory)]

    def test_get_exports1(self):
        exports = [('', '_q_index', 'crumb', 'title')]
        class Dir(DynamicExportingDirectory):
            def get_exports(self):
                return exports
        assert get_exports(Dir()) == exports

    def test_get_exports_fallback(self):
        class Dir(Directory):
            _q_exports = ['', ('a','b'), 'foo']
        print get_exports(Dir())
        assert get_exports(Dir()) == [('', '_q_index', None, ''),
                                      ('a', 'b', '', ''),
                                      ('foo', 'foo', '', '')]

    def test_get_crumb_tree(self):
        class Dir3(DynamicExportingDirectory):
            def get_exports(self):
                return [('', '_q_index', 'crumb3', 'title3'),
                        ('c3', 'n3', 'acrumb', 'atitle')]

            def _q_traverse(self, components):
                return get_crumb_tree()
            n3 = 'ok'
        class Dir2(DynamicExportingDirectory):
            def get_exports(self):
                return [('', '_q_index', 'crumb2', 'title2'),
                        ('c2', 'n2', 'acrumb', 'atitle')]
            n2 = Dir3()
        class Dir1(DynamicExportingDirectory):
            def get_exports(self):
                return [('', '_q_index', 'crumb', 'title'),
                        ('c1', 'n1', 'acrumb', 'atitle')]
            n1 = Dir2()

        directory = Dir1()
        set_environment()
        print directory._q_traverse(['c1', 'c2', ''])
        assert directory._q_traverse(['c1', 'c2', ''])  == [
            [('./../../', 'crumb', 'title'),
             ('./../../c1', 'acrumb', 'atitle')],
            [('./../', 'crumb2', 'title2'),
             ('./../c2', 'acrumb', 'atitle')]]

    def test_get_crumb_tree_no_menu(self):
        class Dir2(DynamicExportingDirectory):
            def get_exports(self):
                return [('', '_q_index', 'crumb3', 'title3'),
                        ('c2', 'n2', 'acrumb', 'atitle')]

            def _q_traverse(self, components):
                return get_crumb_tree()
            n2 = 'ok'
        class Dir(DynamicExportingDirectory):
            def get_exports(self):
                return [('', 'c', '', 'title'),
                        ('c1', 'n1', 'no see crumb', 'no see title')]
            n1 = Dir2()

        directory = Dir()
        set_environment()
        print directory._q_traverse(['c1', 'c2'])
        assert directory._q_traverse(['c1', 'c2'])  == [
            [('./', 'crumb3', 'title3'), ('./c2', 'acrumb', 'atitle')]]

    def test_format_crumbs(self):
        class Dir3(DynamicExportingDirectory):
            def get_exports(self):
                return [('', '_q_index', 'crumb', 'title'),
                        ('c3', 'n3', 'acrumb', 'atitle')]

            def _q_traverse(self, components):
                return format_crumbs()
            n3 = 'ok'
        class Dir2(DynamicExportingDirectory):
            def get_exports(self):
                return [('', '_q_index', 'crumb', 'title'),
                        ('c2', 'n2', 'acrumb', 'atitle')]
            n2 = Dir3()
        class Dir1(DynamicExportingDirectory):
            def get_exports(self):
                return [('', '_q_index', 'crumb', 'title'),
                        ('c1', 'n1', 'acrumb', 'atitle')]
            n1 = Dir2()

        directory = Dir1()
        set_environment()
        crumb_menus = False
        def get_config_value(name):
            return crumb_menus
        dulcinea.ui.crumbs.get_config_value = get_config_value
        print repr(str(directory._q_traverse(['c1', 'c2', ''])))
        crumb_menus = True
        print repr(str(directory._q_traverse(['c1', 'c2', ''])))

if __name__ == "__main__":
    CrumbTest()
