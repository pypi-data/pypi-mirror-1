"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/param/parameter_list.py $
$Id: parameter_list.py 27538 2005-10-11 23:00:36Z rmasse $
"""

from durus.persistent import Persistent
from dulcinea.spec import either, require
from dulcinea.param.parameter import Parameter
from dulcinea.param.parameter_template import ParameterTemplate

class ParameterList (Persistent):
    """
    A special typed list which allows either Parameters or ParameterTemplates.
    """
    list_is = [either(Parameter, ParameterTemplate)]

    def __init__(self, values=None):
        self.list = []
        if values:
            for value in values:
                self.add(value)

    def copy(self):
        result = self.__class__()
        result.list = self.list[:]
        return result

    def __str__(self):
        return "ParameterList(%s)" % self.list

    def __len__(self):
        return len(self.list)

    def __getitem__(self, index):
        return self.list[index]

    def __add__(self, other):
        newlist = ParameterList()
        if isinstance(other, ParameterList):
            newlist.list = self.list + other.list
        else:
            newlist.list = self.list[:]
            for item in other:
                newlist.add(item)
        return newlist

    def get_names(self):
        """() -> [string]

        Return the list of all names in the list.
        """
        return [parameter.get_name() for parameter in self]

    def find(self, name):
        """(name : string) -> any

        Searches the list for a value with name 'name'.  Returns the
        matching value, or None if it couldn't find one.
        """
        for parameter in self.list:
            if name == parameter.get_name():
                return parameter
        require(name, basestring)
        return None

    def add(self, parameter):
        """(parameter : Parameter|ParameterTemplate)

        Raises ValueError if this list already has a value with the same name.
        """
        require(parameter, either(Parameter, ParameterTemplate))
        if self.find(parameter.get_name()) is not None:
            raise ValueError, \
                  "list already has a value named %r" % parameter.get_name()
        self._p_note_change()
        self.list.append(parameter)

    def remove(self, name):
        """(name : string)

        Find the value named by 'name' and remove it.
        """
        require(name, basestring)
        for index, parameter in enumerate(self):
            if name == parameter.get_name():
                self._p_note_change()
                del self.list[index]

    def __iter__(self):
        for item in self.list:
            yield item

    def _get_instances(self, klass):
        return [p for p in self.list if isinstance(p, klass)]

    def get_value_parameters(self):
        """Return a new ParameterList containing all parameters from the
        current list that have values.
        """
        result = ParameterList()
        result.list = self._get_instances(Parameter)
        return result

    def get_templates(self):
        """Return a new ParameterList containing all parameters from the
        current list that don't have values.
        """
        result = ParameterList()
        result.list = self._get_instances(ParameterTemplate)
        return result

    def get_visible(self):
        result = ParameterList()
        result.list = [parameter for parameter in self
                       if not parameter.is_hidden()]
        return result
