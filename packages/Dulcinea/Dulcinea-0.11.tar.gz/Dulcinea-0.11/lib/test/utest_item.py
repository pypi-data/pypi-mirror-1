"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_item.py $
$Id: utest_item.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from datetime import datetime
from dulcinea.item import Item, ItemFolder
from sancho.utest import UTest
from sets import Set

class MyItem(Item):
    pass

class TestItem (UTest):
    def _pre(self):
        self.item1 = MyItem()
        self.item1.timestamp = datetime(2000,1,1)
        self.item1.set_approved(True)
        self.item1a = MyItem()
        self.item1a.timestamp = datetime(2000,1,1)
        self.item2 = MyItem()
        self.item2.timestamp = datetime(2002,1,1)
        self.item2.set_approved(True)
        self.item3 = MyItem()
        self.item3.timestamp = datetime(2003,1,1)
        self.item3.set_approved(True)
        self.folder = ItemFolder()

    def check_basic(self):
        self.folder.add_item(self.item1)
        self.folder.add_item(self.item2)
        assert Set(self.folder.get_items()) == Set([self.item1, self.item2])
        assert self.folder.get_recent_items(count=2) == [self.item2, self.item1]
        self.folder.add_item(self.item3)
        assert self.folder.get_recent_items(count=2) == [self.item3, self.item2]
        assert self.folder.get_recent_items(count=3) == [
            self.item3, self.item2, self.item1]
        assert self.folder.get_recent_items() == [
            self.item3, self.item2, self.item1]
        self.folder.add_item(self.item1a)
        assert self.folder.get_recent_items(count=2) == [
            self.item3, self.item2]
        self.item3.absorb(self.item2)
        assert self.item3.timestamp == self.item2.timestamp

    def check_delete(self):
        self.folder.add_item(self.item1)
        self.folder.add_item(self.item1a)
        item = MyItem() # auto timestamp
        self.folder.add_item(item)
        assert Set(self.folder.get_items()) == Set(
            [self.item1, self.item1a, item])
        self.folder.delete_item(self.item1a)
        assert Set(self.folder.get_items()) == Set([self.item1, item])

if __name__ == "__main__":
    TestItem()
