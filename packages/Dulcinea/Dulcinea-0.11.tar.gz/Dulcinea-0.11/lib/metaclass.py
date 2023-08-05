"""$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/metaclass.py $
$Id: metaclass.py 27378 2005-09-13 14:16:18Z dbinger $
"""
from types import FunctionType

class ClassMethodsClass (type):
    """
    A class that uses this class as the value of its __metaclass__ attribute
    gets all of its methods (except those with names that start with '__')
    converted into class methods.  This is a way to define
    classes that can act as singleton instances.

    The str method of classes with this metaclass returns the name of
    the class.
    """

    def __init__ (self, class_name, bases, namespace):
        for name, obj in namespace.items():
            if isinstance(obj, FunctionType) and not name.startswith('__'):
                setattr(self, name, classmethod(obj))

    def __str__ (self):
        return self.__name__

