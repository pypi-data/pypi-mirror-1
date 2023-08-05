from dulcinea.spec import anything, require, sequence, string
from durus.persistent_list import PersistentList

class SpecifiedList(PersistentList):

    """
    A PersistentList that restricts the type of elements.
    Subclasses should set the class attribute `data_is` to
    be a list containing one type specifier.
    """

    data_is = [anything]

    def __init__(self, *args, **kwargs):
        PersistentList.__init__(self, *args, **kwargs)
        require(self.data, self.data_is)

    def __setitem__(self, i, item):
        require(item, self.data_is[0])
        PersistentList.__setitem__(self, i, item)

    def __setslice__(self, i, j, other):
        require(other, sequence(self.data_is[0]))
        PersistentList.__setslice__(self, i, j, other)

    def append(self, item):
        require(item, self.data_is[0])
        PersistentList.append(self, item)

    def insert(self, i, item):
        require(item, self.data_is[0])
        PersistentList.insert(self, i, item)

    def extend(self, other):
        require(other, sequence(self.data_is[0]))
        PersistentList.extend(self, other)


class StringList(SpecifiedList):

    """
    A PersistentList of strings.

    Instance attributes:
      data : [ string ]
    """
    data_is = [string]

