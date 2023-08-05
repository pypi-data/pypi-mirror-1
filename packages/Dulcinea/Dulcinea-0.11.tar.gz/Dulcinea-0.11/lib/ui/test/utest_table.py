"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/ui/test/utest_table.py $
$Id: utest_table.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from quixote import enable_ptl
enable_ptl()

from dulcinea.ui.table import Table
from quixote import publish
from quixote.http_request import HTTPRequest
from sancho.utest import UTest

class Test (UTest):

    def a(self):
        table = Table()
        table.tbody_id = 'test_id'
        table.render()
        table.column(a=1)
        table.column(b=2)
        table.render()
        class Publisher:
            def get_request(self):
                return HTTPRequest(None, {})
        publish._publisher = Publisher()
        for x in range(1000):
            table.row(a=x, b=x)
        table.render()

if __name__ == '__main__':
    Test()
