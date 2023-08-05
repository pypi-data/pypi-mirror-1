"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_specified_list.py $
$Id: utest_specified_list.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea.specified_list import StringList
from sancho.utest import UTest, raises

class Test (UTest):

    def check_stringlist (self):
        s=StringList()
        raises(TypeError, StringList, [1])
        s=StringList(['a'])
        s.append('b')
        assert list(s) == ['a', 'b']
        s.insert(1, 'c')
        assert list(s) == ['a', 'c', 'b']
        s.insert(0, 'd')
        assert list(s) == ['d', 'a', 'c', 'b']
        try:
            s.insert(0, 3)
            assert 0
        except TypeError: pass
        s.insert(7, 'e')
        assert list(s) == ['d', 'a', 'c', 'b', 'e']
        try:
            s[0] = 7
            assert 0
        except TypeError: pass
        s[0] = 'f'
        assert list(s) == ['f', 'a', 'c', 'b', 'e']
        try:
            s[3:4] = ['a', 4]
            assert 0
        except TypeError: pass
        s[3:4] = ['a', 'b']
        assert list(s) == ['f', 'a', 'c', 'a', 'b', 'e']
        raises(TypeError, s.extend, ['a', 4])
        s.extend(['a', 'b'])
        assert list(s) == ['f', 'a', 'c', 'a', 'b', 'e', 'a', 'b']

if __name__ == "__main__":
    Test()
