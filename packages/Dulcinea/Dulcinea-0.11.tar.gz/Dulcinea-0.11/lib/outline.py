"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/outline.py $
$Id: outline.py 27456 2005-09-22 13:22:17Z dbinger $
"""
from dulcinea.spec import add_getters_and_setters
from durus.persistent_list import PersistentList

class Outline (PersistentList):
    """
    An Outline is a list of items, which may themselves be Outlines.
    An index into an Outline may be a list of integers, and in this
    case it refers to position in one of the nested Outlines.
    """
    def iteritems(self):
        """
        Generates (int | [int], anything) in depth-first traversal order.
        """
        for j, item in enumerate(self):
            yield j, item
            if isinstance(item, Outline):
                for k, subitem in item.iteritems():
                    if isinstance(k, list):
                        yield [j] + k, subitem
                    else:
                        yield [j, k], subitem

    def iterkeys(self):
        for j, item in self.iteritems():
            yield j

    def itervalues(self):
        for item in self:
            yield item
            if isinstance(item, Outline):
                for subitem in item.itervalues():
                    yield subitem

    def index(self, obj):
        """() -> int | [int]
        Returns the first index of obj in depth-first traversal order.
        If obj is not found, raises ValueError.
        """
        for index, item in self.iteritems():
            if item is obj:
                return index
        raise ValueError

    def __getitem__(self, index):
        if isinstance(index, basestring):
            index = self.string_to_index(index)
        if isinstance(index, int):
            return PersistentList.__getitem__(self, index)
        else:
            next = PersistentList.__getitem__(self, index[0])
            remainder = index[1:]
            if not remainder:
                return next
            elif isinstance(next, Outline):
                return next[remainder]

    def _apply(self, method, index, *args):
        if isinstance(index, basestring):
            index = self.string_to_index(index)
        if isinstance(index, int):
            method(self, index, *args)
        elif len(index) == 1:
            method(self, index[0], *args)
        else:
            target = self[index[:-1]]
            if not isinstance(target, Outline):
                raise IndexError
            method(target, index[-1], *args)

    def __setitem__(self, index, value):
        self._apply(PersistentList.__setitem__, index, value)

    def __delitem__(self, index):
        self._apply(PersistentList.__delitem__, index)

    def insert(self, index, value):
        self._apply(PersistentList.insert, index, value)

    def get(self, index, default=None):
        try:
            return self[index]
        except IndexError:
            return default

    @staticmethod
    def string_to_index(str_index):
        split = str_index.split('.')
        if len(split) == 1:
            return int(split[0]) - 1
        else:
            return [int(component)-1 for component in split]

    @staticmethod
    def index_to_string(index):
        if isinstance(index, int):
            return str(index + 1)
        else:
            return '.'.join([str(component + 1) for component in index])


class TextOutline (Outline):

    text_is = basestring

    def __init__(self, *args, **kwargs):
        Outline.__init__(self, *args, **kwargs)
        self.text = ''

add_getters_and_setters(TextOutline)
