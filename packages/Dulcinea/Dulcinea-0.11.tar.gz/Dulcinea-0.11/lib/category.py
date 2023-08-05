"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/category.py $
$Id: category.py 27586 2005-10-17 16:50:53Z dbinger $
"""
from dulcinea.base import DulcineaPersistent
from dulcinea.spec import instance, sequence, specify, mapping
from dulcinea.spec import spec, require, string, pattern, both
from dulcinea.spec import add_getters_and_setters
from durus.persistent import ComputedAttribute
from durus.persistent_dict import PersistentDict
from durus.persistent_list import PersistentList


class Category (DulcineaPersistent):
    """
    A category is a node in a partial ordering.
    """
    name_is = spec(
        (None, both(string, pattern('[a-zA-Z0-9_-]*$'))),
        "unique, URL-friendly identifier for this category")
    label_is = spec(
        (string, None),
        "human-readable string that describes this category; probably but "
        "not necessarily unique")
    description_is = spec(
        (string, None),
        "paragraph-length, human-readable prose description of this category")
    children_is = sequence(instance('Category'), PersistentList)
    parents_is = sequence(instance('Category'), PersistentList)
    _v_expansion_is = ComputedAttribute

    def __init__(self, name=None):
        specify(self, name=name, label=None, description=None,
                children=PersistentList(),
                parents=PersistentList(),
                _v_expansion=ComputedAttribute())

    def __str__(self):
        return self.name or "*unnamed*"

    def add_child(self, child):
        require(child, Category)
        if child.is_ancestor_of(self):
            raise ValueError, "Attempt to create circular relationship"
        if child not in self.children:
            self.children.append(child)
            child.parents.append(self)
        self._invalidate_expansion()

    def remove_child(self, child):
        require(child, Category)
        self.children.remove(child)
        child.parents.remove(self)
        self._invalidate_expansion()

    def set_children(self, children):
        require(children, list)
        for child in self.children[:]: # remove_child() modifies self.children
            self.remove_child(child)
        for child in children:
            self.add_child(child)

    def set_parents(self, parents):
        require(parents, list)
        for parent in self.parents[:]: # remove_child() modifies self.parents
            parent.remove_child(self)
        for parent in parents or []:
            parent.add_child(self)

    def _invalidate_expansion(self):
        self._v_expansion.invalidate()
        for parent in self.parents:
            parent._invalidate_expansion()

    def expand(self):
        """() -> { Category : bool }

        Return a set containing this category and its (recursive) children.
        """
        def compute():
            expansion = {self: 1}
            for child in self.children:
                if child not in expansion:
                    expansion.update(child.expand())
            return expansion
        return self._v_expansion.get(compute)

    def get_descendants(self):
        """() -> [ Category ]

        Return list containing this category's (recursive) children.
        """
        descendants = []
        for child in self.children:
            if child not in descendants:
                descendants.append(child)
                descendants += [descendant
                                for descendant in child.get_descendants()
                                if descendant not in descendants]
        return descendants

    def get_leaves(self):
        """() -> [ Category ]

        Return list containing this category or this category's
        (recursive) children that have no children.
        """
        if self.children:
            leaves = {}
            for child in self.children:
                for leaf in child.get_leaves():
                    leaves[leaf] = 1
            return leaves.keys()
        else:
            return [self]

    def is_descendant_of(self, other_category):
        """(Category) -> bool

        Is the other category the same as this one or one of the
        descendant categories?
        """
        return self in other_category.expand()

    def is_ancestor_of(self, other_category):
        """(Category) -> bool

        Is this category the same as or a proper descendant of
        other_category?
        """
        return other_category in self.expand()

    def get_label(self):
        return self.label or self.name

add_getters_and_setters(Category)


class Categorized:

    categories_is = sequence(Category, PersistentList)

    def __init__(self):
        self.categories = PersistentList()

    def add_category(self, category):
        self.set_categories(self.categories + [category])

    def set_categories(self, categories):
        """(categories : [Category])
        """
        specify(self, categories=PersistentList(categories))

    def get_categories(self):
        """() -> [Category]
        """
        return list(self.categories)

    def get_descendants_of(self, ancestor):
        return [category for category in self.categories
                if ancestor.is_ancestor_of(category)]

    def in_category(self, other_category):
        if other_category is None:
            return 0
        require(other_category, Category)
        other_categories = other_category.expand()
        for category in self.categories:
            if category in other_categories:
                return 1
        return 0

    def in_categories(self, categories):
        """Is self in all of the categories?
        """
        require(categories, [Category])
        for category in categories:
            if not self.in_category(category):
                return 0
        return 1


def remove_ancestors(categories):
    require(categories, [Category])
    no_ancestors = categories[:]
    for category in categories or []:
        for descendant in category.get_descendants():
            if descendant in categories and category in no_ancestors:
                no_ancestors.remove(category)
    return no_ancestors


class CategoryDatabase:

    categories_is = mapping({Category.name_is:Category}, PersistentDict)

    def __init__(self):
        assert self.__class__ is not CategoryDatabase, (
            "CategoryDatabase should be a mixin in a persistent subclass")
        self.categories = PersistentDict()

    def add_category(self, category):
        require(category, Category)
        if self.categories.has_key(category.get_name()):
            raise ValueError("Category %r already exists." %
                             category.get_name())
        self.categories[category.get_name()] = category

    def rename_category(self, category, new_name):
        """(category:Category, new_name:string)
        """
        old_name = category.get_name()
        if not self.categories.has_key(old_name):
            raise ValueError("Category %r not found." % old_name)
        if self.categories.has_key(new_name):
            raise ValueError("Category %r already exists." % new_name)
        category.set_name(new_name)
        self.add_category(category)
        del self.categories[old_name]

    def get_category(self, name):
        """(name:string) -> Category

        Retrieve the named category, or None.
        """
        return self.categories.get(name)

    def get_categories(self):
        """() -> [Category]"""
        return self.categories.values()

