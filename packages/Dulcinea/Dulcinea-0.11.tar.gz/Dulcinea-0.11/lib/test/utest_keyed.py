"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_keyed.py $
$Id: utest_keyed.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea.keyed import Keyed, KeyedMap
from sancho.utest import UTest, raises

class Test (UTest):

    def check_a(self):
        self.map = KeyedMap()
        self.a = Keyed()
        assert self.a.get_key() == None
        self.map.add(self.a)
        raises(AssertionError, self.map.add, self.a)
        self.b = Keyed()
        self.b.junk = 1
        raises(TypeError, self.map.add, self.b)
        raises(TypeError, self.map.add, 1)
        assert self.a.get_key() == 1
        assert self.map.get_mapping().items() == [(1, self.a)]
        assert self.map.get(1) == self.a

if __name__ == "__main__":
    Test()
