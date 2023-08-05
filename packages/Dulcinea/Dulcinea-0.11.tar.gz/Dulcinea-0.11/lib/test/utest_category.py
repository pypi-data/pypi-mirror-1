"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_category.py $
$Id: utest_category.py 27554 2005-10-13 13:42:37Z dbinger $

"""
from sets import Set
from sancho.utest import UTest, raises
from dulcinea.category import Category, Categorized, remove_ancestors
from dulcinea.spec import get_spec_problems

class CategoryTest (UTest):

    def check_basic (self):
        self.category = Category()
        assert str(self.category) == '*unnamed*'
        assert not self.category.name_is("ab%")
        assert not self.category.name_is("[ab]")
        assert not self.category.name_is("a\b")
        assert not self.category.name_is("a b")
        assert not self.category.name_is("a/b")
        assert not self.category.name_is(" a/b")
        assert self.category.name_is("__")
        assert self.category.name_is("34")
        assert self.category.name_is("a8")
        assert self.category.name_is("_a8")
        raises(TypeError, self.category.set_name, " ")
        self.category.set_name("boo")
        assert self.category.get_name() == "boo"
        self.category.set_label("Boo")
        assert self.category.get_label() == "Boo"
        self.category.set_description("casual")
        assert self.category.get_description() == "casual"
        assert get_spec_problems(self.category) == []

    def check_categorized (self):
        self.categorized = Categorized()
        assert get_spec_problems(self.categorized) == []
        self.category1 = Category()
        self.category2 = Category()
        raises(TypeError, self.categorized.add_category, None)
        raises(TypeError, self.categorized.add_category, 42)
        self.categorized.add_category(self.category1)
        assert self.categorized.in_category(self.category1)
        assert not self.categorized.in_category(None)
        assert self.categorized.in_categories([self.category1])
        assert Set(self.categorized.get_categories()) == Set([self.category1])
        assert Set(self.categorized.get_descendants_of(self.category1)) == Set(
            [self.category1])
        assert Set(
            self.categorized.get_descendants_of(self.category2)) == Set([])
        assert not self.categorized.in_categories(
            [self.category1, self.category2])

    def check_ancestry (self):
        self.a = Category("a")
        self.b = Category("b")
        self.c = Category("c")
        self.d = Category("d")
        assert Set(self.a.get_children()) == Set([])
        assert Set(self.b.get_parents()) == Set([])
        self.a.add_child(self.b)
        assert Set(self.a.get_children()) == Set([self.b])
        assert Set(self.b.get_parents()) == Set([self.a])
        assert Set(self.a.get_children()) == Set([self.b])
        assert Set(self.b.get_parents()) == Set([self.a])
        raises(ValueError, self.b.add_child, self.a)
        self.b.add_child(self.c)
        assert Set(self.c.get_children()) == Set([])
        assert Set(self.c.get_parents()) == Set([self.b])
        # Now we have a -> b -> c.
        assert Set(self.a.get_descendants()) == Set([self.b, self.c])
        assert Set(self.b.get_descendants()) == Set([self.c])
        assert Set(self.c.get_descendants()) == Set([])
        assert self.c.is_descendant_of(self.a)
        assert self.c.is_descendant_of(self.b)
        assert self.c.is_descendant_of(self.c)
        assert self.c.is_ancestor_of(self.c)
        assert not self.d.is_ancestor_of(self.c)
        self.a.set_children([self.b, self.c])
        # a -> b, a-> c, b-> c, d-> b, d-> c
        assert self.c.is_descendant_of(self.a)
        assert self.c.is_descendant_of(self.b)
        assert self.c.is_descendant_of(self.c)
        raises(ValueError, self.a.set_parents, [self.b, self.c])
        assert self.c.is_descendant_of(self.a)
        assert self.c.is_descendant_of(self.b)
        assert self.c.is_descendant_of(self.c)
        self.a.set_parents([self.d])
        assert self.c.is_descendant_of(self.d)
        self.c.set_parents(list(self.c.get_parents()))
        assert Set(list(self.a.expand())) == Set([self.a, self.b, self.c])
        assert Set(list(self.b.expand())) == Set([self.b, self.c])
        assert Set(list(self.c.expand())) == Set([self.c])
        assert Set(self.d.expand()) == Set([self.a, self.b, self.c, self.d])
        self.a.remove_child(self.c)
        assert self.a.is_ancestor_of(self.c)
        self.b.remove_child(self.c)
        assert not self.a.is_ancestor_of(self.c)
        assert Set(list(self.b.expand())) == Set([self.b])
        assert Set(list(self.a.expand())) == Set([self.a, self.b])
        self.a.get_leaves()
        assert remove_ancestors([self.b, self.a]) == [self.b]
        assert remove_ancestors([]) == []
        assert remove_ancestors([self.a, self.b, self.c]) == [self.b, self.c]
        assert remove_ancestors([self.a, self.c]) == [self.a, self.c]

if __name__ == "__main__":
    CategoryTest()

