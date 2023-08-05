from dulcinea.param.parameter_type import ParameterDatabase
from dulcinea.physical_unit import UnitCollection
from dulcinea.material import MaterialDatabase, Material

_db = None

def open_database():
    global _db
    _db = dict(parameter_db=ParameterDatabase(),
               material_db=MaterialDatabase(),
               standard_units=UnitCollection())
    mdb = _db['material_db']
    mdb.add_material(Material('gold'))
    mdb.add_material(Material('aluminum'))
    mdb.add_material(Material('silver'))
    mdb.add_material(Material('boron'))
    mdb.add_material(Material('silicon'))
    mdb.add_material(Material('blah'))
    return _db

def close_database():
    global _db
    _db = None

def get_material_db():
    return _db['material_db']

def get_parameter_db():
    return _db['parameter_db']

def get_standard_units():
    return _db['standard_units']

