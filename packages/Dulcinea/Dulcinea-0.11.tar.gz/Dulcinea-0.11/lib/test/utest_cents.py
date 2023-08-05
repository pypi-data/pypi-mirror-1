"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_cents.py $
$Id: utest_cents.py 27276 2005-09-01 21:07:07Z dbinger $
"""
from dulcinea.cents import Cents
from dulcinea.spec import get_spec_problems
from sancho.utest import UTest


class CentsTest(UTest):

    def notice_bad(self):
        try:
            a = Cents(None)
            assert 0
        except TypeError: pass
        a = Cents(0)
        assert get_spec_problems(a) == []
        try:
            a + 1
            assert 0
        except TypeError: pass
        try:
            a * 1
            assert 0
        except TypeError: pass
        try:
            a / 1
            assert 0
        except TypeError: pass
        try:
            a > 1
            assert 0
        except TypeError: pass
        try:
            a += 1
            assert 0
        except TypeError: pass
        try:
            a -= 1
            assert 0
        except TypeError: pass

    def do_good_things(self):
        a = Cents(23)
        assert 23 == a.get_cents()
        assert 0.23 == a.get_dollars(), a.get_dollars()
        assert str(a) == '$0.23'
        assert (a - a).get_cents() == 0
        assert (a + a).get_cents() == 46
        assert a == Cents(23)
        a += Cents(5)
        assert a == Cents(28)
        a -= Cents(30)
        assert a == Cents(-2)

if __name__ == '__main__':
    CentsTest()
