"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/ui/test/utest_util.py $
$Id: utest_util.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from quixote import enable_ptl
enable_ptl()

from dulcinea.ui.util import csv
from quixote.http_response import HTTPResponse
from sancho.utest import UTest
import dulcinea.ui.util

class MiscTest (UTest):

    def check_csv (self):
        fake_response = HTTPResponse()
        dulcinea.ui.util.get_response = lambda: fake_response
        s = csv(['a','b'], [{'a':1}, {'a':2, 'b':3}])
        assert s == 'a,b\r\n1,\r\n2,3\r\n'
        assert fake_response.content_type == 'text/comma-separated-values'


if __name__ == "__main__":
    MiscTest()
