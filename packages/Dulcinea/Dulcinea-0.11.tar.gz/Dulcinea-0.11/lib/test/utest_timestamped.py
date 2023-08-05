"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_timestamped.py $
$Id: utest_timestamped.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from sancho.utest import UTest
from dulcinea.timestamped import Timestamped, timestamp_sorted
from dulcinea.timestamped import reverse_timestamp_sorted


class Test (UTest):

    def a(self):
        x = Timestamped()
        y = Timestamped()
        assert timestamp_sorted([x, y]) == [x,y]
        assert reverse_timestamp_sorted([x, y]) == [y,x]
        x.set_timestamp()
        assert timestamp_sorted([x, y]) == [y,x]

if __name__ == "__main__":
    Test()
