"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/material.py $
$Id: material.py 27528 2005-10-07 20:50:40Z dbinger $
"""
from dulcinea.base import DulcineaPersistent
from dulcinea.category import Category
from dulcinea.sort import function_sort
from dulcinea.spec import boolean, sequence, instance, mapping
from dulcinea.spec import spec, specify, require, string
from durus.persistent_dict import PersistentDict
from durus.persistent_list import PersistentList
from quixote.html import htmlescape, htmltext
from random import randrange


class Material (Category):
    """
    Represents a material and a category of materials.
    """
    html_name_is = spec(
        (string, None),
        "The name to be used in html displays. "
        "This may include html tags for subscripts. "
        "Other materials may have the same html_name, "
        "but that is probably a bad idea.")
    html_color_is = spec(
        (string, None),
        "A string in the form #ffee99 that identifies "
        "a color that might be used in html concerning "
        "this Material. "
        "Other materials may have the same color.")
    deleted_is = spec(
        boolean,
        "Tells if this this material is deprecated.")

    children_is = sequence(instance('Material'), PersistentList)
    parents_is = sequence(instance('Material'), PersistentList)

    def __init__(self, name, html_name=None, html_color=None):
        Category.__init__(self)
        specify(self,
                name=name,
                html_color=html_color or random_light_color(),
                html_name=html_name or name,
                deleted=0)

    def __str__(self):
        if self.get_children():
            return '%s (category)' % self.get_label()
        else:
            return self.get_label()

    def set_label(self, label):
        specify(self, label=label)

    def set_html_name(self, html_name):
        specify(self, html_name=html_name)

    def set_html_color(self, color=None):
        specify(self, html_color=color)

    def get_label(self):
        return self.label or self.name

    def get_html_name(self):
        return self.html_name

    def get_html_color(self):
        return self.html_color

    def format(self, html=False):
        if html:
            if self.html_name:
                return htmltext(self.html_name)
            else:
                return htmlescape(self.get_label())
        else:
            return self.get_label()

    def set_deleted(self, value=1):
        self.deleted = value

    def is_deleted(self):
        return self.deleted

    def is_other(self):
        return self.name == "other"


def random_light_color():
    red   = 256
    green = 256
    blue  = 256
    maximum_light = (256*3-100)
    minimum_light = 300
    while ((red+green+blue > maximum_light) or
           (red+green+blue < minimum_light)):
        red = randrange(16,256)
        green = randrange(16,256)
        blue = randrange(16,256)
    r = hex(red)[-2:]
    g = hex(green)[-2:]
    b = hex(blue)[-2:]
    return '#%s%s%s' % (r,g,b)

def material_sort(materials):
    """(seq [Material]) -> [Material]"""
    def lower_case_label(material):
        return material.get_label().lower()
    return function_sort(materials, lower_case_label)


class MaterialDatabase (DulcineaPersistent):

    materials_is = spec(
        mapping({string:Material}, PersistentDict),
        "all material objects keyed on name")

    def __init__(self):
        specify(self, materials=PersistentDict())

    def __getitem__(self, material_name):
        return self.materials[material_name]

    def add_material(self, material):
        require(material, Material)
        if self.materials.has_key(material.get_name()):
            raise ValueError, (
                "material named '%s' already exists" % material.get_name())
        self.materials[material.get_name()] = material

    def get_material(self, material_name):
        return self.materials.get(material_name)

    def get_materials(self):
        return self.materials.values()

