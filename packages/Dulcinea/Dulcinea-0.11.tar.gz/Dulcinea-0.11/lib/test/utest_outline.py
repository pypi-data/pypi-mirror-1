"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_outline.py $
$Id: utest_outline.py 27434 2005-09-16 15:02:48Z dbinger $
"""
from dulcinea.outline import Outline
from sancho.utest import UTest, raises

def outline_from_nested_lists(nested_lists):
    if not isinstance(nested_lists, list):
        return nested_lists
    return Outline([outline_from_nested_lists(x)
                    for x in nested_lists])

class OutlineTest(UTest):

    def a(self):
        x = Outline()
        raises(ValueError, x.index, 'b')
        x.extend(['a', 'b', 'b', 'c'])
        assert x.index('b') == 1, x.index('b')
        x[:] = ['a', Outline(['c', 'b']), 'd']
        assert x.index('b') == [1, 1]
        assert 'b' == x[[1, 1]]
        x[[1,1]] = 'e'
        assert 'e' == x[[1, 1]]
        raises(ValueError, x.index, 'b')
        raises(IndexError, x.__getitem__, 100)
        x[0] = 'j'
        assert x[2] == 'd', x.data
        del x[-1]
        raises(ValueError, x.index, 'd')

    def b(self):
        x = outline_from_nested_lists(['a', 'b', ['c', [['d']]], ['e'], []])
        assert x.get('3.1') == 'c'
        assert x.get([2, 0]) == 'c'
        for letter in 'abcde':
            assert x.get(x.index(letter)) == letter
            assert x.get(x.index_to_string(x.index(letter))) == letter
        keys = list(x.iterkeys())
        values = list(x.itervalues())
        assert keys == [k for k, v in x.iteritems()]
        assert values == [v for k, v in x.iteritems()]
        x.insert([2, 0], 'f')
        assert x.get('3.1') == 'f'
        assert x.get('3.2') == 'c'
        assert x.get('3.2.3.4') == None
        v =  x[[1]]
        del x[[1]]
        raises(ValueError, x.index, v)
        raises(IndexError, x.__setitem__, [0, 1], 'a')

    def c(self):
        x = Outline()
        assert x.get(0, 1) == 1

if __name__ == '__main__':
    OutlineTest()
