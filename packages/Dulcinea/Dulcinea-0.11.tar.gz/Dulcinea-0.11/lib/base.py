"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/base.py $
$Id: base.py 27383 2005-09-13 14:20:09Z dbinger $

Provides DulcineaPersistent and DulcineaBase.
"""
from durus.persistent import Persistent
from types import ClassType
import new

class DulcineaBase:
    """
    The standard base class for classes whose instances do not need
    to be first-class database objects.  Instances of DulcineaBase can still
    be stored in the database if they happen to be attached to
    other persistent objects, but they don't really participate in
    persistence -- they just come along for the ride.
    """

    def copy (self):
        klass = self.__class__
        if type(klass) is ClassType:
            newself = new.instance(self.__class__, {})
        elif isinstance(klass, object):
            newself = klass.__new__(klass)
        else:
            raise RuntimeError, "unknown type of class object: %s" % `klass`
        newself.__dict__.update(self.__dict__)
        return newself

    def __copy__ (self):
        return self.copy()


class DulcineaPersistent (Persistent, DulcineaBase):
    """
    The standard base class for classes whose instances should be
    first-class database objects that participate fully in the
    persistence mechanism.  Instances of DulcineaPersistent still have to be
    referenced by an existing persistent object, i.e. they must
    ultimately connect back to one of the database root objects.
    """

