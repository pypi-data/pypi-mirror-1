"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/item.py $
$Id: item.py 27528 2005-10-07 20:50:40Z dbinger $
"""
from dulcinea.base import DulcineaPersistent
from dulcinea.spec import boolean, mapping, init, require, specify
from dulcinea.spec import add_getters_and_setters, string
from dulcinea.timestamped import Timestamped, reverse_timestamp_sorted
from dulcinea.util import datetime_to_int
from durus.persistent_dict import PersistentDict

class Item(DulcineaPersistent, Timestamped):

    title_is = string
    key_is = string
    approved_is = boolean

    def __init__(self):
        assert self.__class__ is not Item, "abstract class"
        Timestamped.__init__(self)
        init(self, approved=False)

    def __cmp__(self, other):
        require(other, Item)
        return cmp(self.get_timestamp(), other.get_timestamp())

    def absorb(self, other):
        assert self.__class__ is other.__class__
        self._p_note_change()
        for attr_name in self.__dict__:
            if attr_name != 'key':
                self.__dict__[attr_name] = other.__dict__[attr_name]

    def set_key(self, key):
        assert self.key is None, "Item already has a key"
        specify(self, key=key)

    def is_approved(self):
        return self.approved

    def can_modify(self, user):
        return user.is_admin()

add_getters_and_setters(Item)


class ItemFolder(DulcineaPersistent):
    """
    Stores a collection of Items and defines an API for storage
    and creation-time-based retrieval.
    """
    items_is = mapping({string:Item}, PersistentDict)

    def __init__(self):
        specify(self, items=PersistentDict())

    def clear(self):
        self.items.clear()

    def add_item(self, item):
        """(item : Item)
        """
        require(item, Item)
        i = 0
        while 1:
            key =  '%s-%s' % (datetime_to_int(item.get_timestamp()), i)
            if not self.items.has_key(key):
                break
            i += 1
        item.set_key(key)
        self.items[key] = item

    def delete_item(self, item):
        """(item : Item)
        """
        require(item, Item)
        if item.get_key() is None:
            raise KeyError, "Item %r not in any database" % item
        if not self.items.has_key( item.key ):
            raise KeyError, "Item %r not in this database" % item
        del self.items[item.get_key()]

    def get_item(self, key):
        """(key : string) -> Item
        """
        return self.items[key]

    def get_items(self):
        """() -> [Item]
        """
        return self.items.values()

    def get_recent_items(self, count=None, include_unapproved=False):
        """(count : int = None, include_unapproved : bool = False) -> [Item]

        Return the 'count' most recent items.  If 'include_unapproved' is True,
        both un-approved and approved items are returned.
        The list returned is in reverse-chronological order by timestamp.
        """
        result = []
        for item in self.items.values():
            if item.is_approved() or include_unapproved:
                result.append(item)
        result = reverse_timestamp_sorted(result)
        if count is not None:
            result = result[:count]
        return result
