"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_typeutils.py $
$Id: utest_typeutils.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from sancho.utest import UTest, raises
from dulcinea.typeutils import typecheck, typecheck_seq


class TypeUtilsTest (UTest):

    def check_typecheck_seq (self):
        typecheck_seq([4, 2], int)
        raises(TypeError, typecheck_seq, [4.0, 2], int)
        raises(TypeError, typecheck_seq, [4.0, 2], float)
        typecheck_seq([4.0, 2.0], float)
        typecheck_seq(['foo', 'bar', 'baz'], str)
        raises(TypeError, typecheck_seq, ['foo', 'bar', 666], str)
        typecheck_seq([], str)
        typecheck_seq([], float)
        typecheck_seq([], int)
        raises(TypeError, typecheck_seq, 4, int)
        raises(TypeError, typecheck_seq, None, int)
        typecheck_seq(None, int, allow_none=1)

    def check_typecheck (self):
        typecheck(4, int)
        raises(TypeError, typecheck, 4.0, int, allow_none=1)
        typecheck(4.0, (float, int))
        raises(TypeError, typecheck, 'foo', (float, int)) 
        raises(TypeError, typecheck, None, int)
        typecheck(None, int, allow_none=1)

if __name__ == "__main__":
    TypeUtilsTest()
