"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_sort.py $
$Id: utest_sort.py 27147 2005-08-03 13:59:08Z dbinger $
"""

from sancho.utest import UTest
from dulcinea.sort import sort, str_sort, lexical_sort, natural_sort
from dulcinea.sort import attr_sort, lex_attr_sort, method_sort, function_sort

class Thing:
    counter = 0

    def __init__(self, name):
        self.name = name
        Thing.counter += 1
        self.id = "T-%03d" % Thing.counter

    def __str__(self):
        return self.name

    def __cmp__(self, other):
        return cmp(self.id, other.id)

    def get_id(self):
        return self.id


def gen(*args):
    for arg in args:
        yield arg


class SortTest (UTest):

    def check_sort(self):
        words = ["foo", "BAR", "aBc-123", "blah!", "123-abc"]
        sorted = ["123-abc", "BAR", "aBc-123", "blah!", "foo"]
        assert sort(gen(*words)) == sorted
        words2 = words[:]
        assert sort(words2) == sorted
        assert sort(words) == sorted
        assert words == sorted

    def check_instances(self):
        thing1 = Thing("bob")
        thing2 = Thing("Tim")
        thing3 = Thing("123-abc")
        things = [thing2, thing1, thing3]
        assert sort(gen(thing2, thing1, thing3)) == [thing1, thing2, thing3]
        assert str_sort(things) == [thing3, thing2, thing1]
        assert lexical_sort(gen(thing1, thing2, thing3)) == [
            thing3, thing1, thing2]
        assert attr_sort(things, 'id') == [thing1, thing2, thing3]
        assert attr_sort(things, 'name') == [thing3, thing2, thing1]
        assert lex_attr_sort(things, 'name') == [thing3, thing1, thing2]
        assert method_sort(gen(thing2, thing1, thing3), 'get_id') == [
            thing1, thing2, thing3]
        def fun_get_id(x):
            return x.get_id()
        assert function_sort(gen(thing2, thing1, thing3), fun_get_id) == [
            thing1, thing2, thing3]

    def check_natural(self):
        nums = [1, 5, 9, 10, 15, 105]
        assert str_sort(gen(*nums)) == [1, 10, 105, 15, 5, 9]
        nums = map(str, nums)
        assert sort(nums[:]) == ["1", "10", "105", "15", "5", "9"]
        assert natural_sort(nums) == nums

        # Check that the promises made in the docstring hold.
        l = ["a1b", "a1", "a20", "a", "a0", "a1a", "a10", "a2"]
        assert natural_sort(l) == [
            "a", "a0", "a1", "a1a", "a1b", "a2", "a10", "a20"]
        l = ["x2-y7", "x8-y8", "x2-g8", "x2-y08"]
        assert natural_sort(l) == [
            "x2-g8", "x2-y7", "x2-y08", "x8-y8"]
        l = ["1.02", "1.001", "1.3", "1.002", "1.1", "1.010"]
        assert natural_sort(l) == [
            "1.001", "1.002", "1.010", "1.02", "1.1", "1.3"]


if __name__ == "__main__":
    SortTest()
