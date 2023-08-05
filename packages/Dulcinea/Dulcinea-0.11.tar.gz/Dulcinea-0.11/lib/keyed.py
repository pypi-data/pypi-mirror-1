"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/keyed.py $
$Id: keyed.py 27471 2005-09-23 20:57:16Z dbinger $
"""
from dulcinea.spec import require, get_spec_problems, anything, mapping, spec
from dulcinea.spec import specify, either
from durus.btree import BTree
from durus.persistent import Persistent
from durus.persistent_dict import PersistentDict

class Keyed:

    """
    An item with an int key used as a key in an KeyedMap.
    Note that the key attribute is set when the item is put in the KeyedMap,
    so there is no set_key() method.
    """
    key_is = int

    def __init__(self):
        self.key = None

    def get_key(self):
        return self.key


class Counter (Persistent):

    """
    Keep a key counter.  This may change often, so we keep this
    isolated here instead of on the Keep itself.
    """
    next_available_is = int

    def __init__(self):
        self.next_available = 1

    def __iadd__(self, value):
        self.next_available += value
        return self

    def __int__(self):
        return self.next_available

class KeyedMap:
    """
    A mixin for a simple database that stores a map of objects by key.
    """
    mapping_is = mapping({int:Keyed}, either(PersistentDict, BTree))
    value_spec_is = spec(
        anything,
        "Specifies the type of values allowed in mapping")
    key_counter_is = either(int, Counter)

    def __init__(self, value_spec=Keyed):
        specify(self,
                key_counter=Counter(),
                value_spec=value_spec,
                mapping=BTree())

    def get(self, key, *args):
        return self.mapping.get(key, *args)

    def get_mapping(self):
        return self.mapping

    def add(self, value):
        require(value, self.value_spec)
        assert value.key is None
        value.key = int(self.key_counter)
        if get_spec_problems(value):
            value.key = None
            raise TypeError(''.join(get_spec_problems(value)))
        self.key_counter += 1
        self.mapping[value.key] = value

