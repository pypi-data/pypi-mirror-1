"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_material.py $
$Id: utest_material.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea.material import Material, material_sort, MaterialDatabase
from sancho.utest import UTest


class MaterialTest (UTest):

    def check_materials_constructor (self):
        mdb = MaterialDatabase()
        assert list(mdb.get_materials()) == []
        m1 = Material('silicon')
        mdb.add_material(m1)
        assert list(mdb.get_materials()) == [m1]
        m2 = Material('silicon', 'Si')
        try:
            mdb.add_material(m2)
            assert 0
        except ValueError: pass
        assert list(mdb.get_materials()) == [m1]
        m2 = Material('silicon2', 'Si')
        mdb.add_material(m2)
        assert len(mdb.get_materials()) == 2
        m3 = Material('Oxygen', 'O<sub>2</sub>')
        mdb.add_material(m3)
        assert len(mdb.get_materials()) == 3
        assert len(mdb.get_material('Oxygen').html_color) == 7
        assert mdb.get_material('Oxygen').html_name == 'O<sub>2</sub>'
        assert mdb.get_material('Oxygen').name == 'Oxygen'
        m3 = Material('Oxygen2', 'O<sub>2</sub>', 'blue')
        mdb.add_material(m3)
        assert len(mdb.get_materials()) == 4

    def check_materials_database (self):
        mdb = MaterialDatabase()
        mdb.add_material(Material('silicon'))
        mdb.add_material(Material('silicon2', 'Si'))
        mdb.add_material(Material('Oxygen', 'O<sub>2</sub>'))
        mdb.add_material(Material('Oxygen2', 'O<sub>2</sub>','blue'))
        mdb.add_material(Material('gas'))
        assert len(mdb.get_material('gas').get_leaves()) == 1
        assert len(mdb.get_material('Oxygen').get_leaves()) == 1
        mdb.get_material('gas').add_child(mdb.get_material('Oxygen'))
        assert len(mdb.get_material('gas').get_leaves()) == 1
        assert len(mdb.get_material('gas').get_descendants()) == 1
        mdb.get_material('gas').add_child(mdb.get_material('Oxygen2'))
        assert len(mdb.get_material('gas').get_leaves()) == 2
        assert len(mdb.get_material('gas').get_descendants()) == 2
        mdb.get_material('gas').remove_child(mdb.get_material('Oxygen2'))
        assert len(mdb.get_material('gas').get_leaves()) == 1
        assert len(mdb.get_material('gas').get_descendants()) == 1

    def check_sort (self):
        material_list = []
        for (name, label) in (("chocolate_sauce", "chocolate sauce"),
                              ("peanut_butter", "peanut butter"),
                              ("1_2_3_foobaroxynol", "1,2,3-foobaroxynol"),
                              ("H2O", None)):
            m = Material(name)
            if label:
                m.set_label(label)
            material_list.append(m)

        sorted_list = [material_list[2],
                       material_list[0],
                       material_list[3],
                       material_list[1]]

        assert material_sort(list(material_list)) == sorted_list

        material_list.reverse()
        material_tuple = tuple(material_list)
        assert material_sort(material_tuple) == sorted_list

        def gen_materials ():
            for m in material_list:
                yield m

        materials = gen_materials()
        assert material_sort(materials) == sorted_list

if __name__ == "__main__":
    MaterialTest()
