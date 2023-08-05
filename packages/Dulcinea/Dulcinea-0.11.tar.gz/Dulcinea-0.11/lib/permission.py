"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/permission.py $
$Id: permission.py 27502 2005-09-30 14:25:36Z dbinger $

Deprecated.  PermissionManager mixin has been replaced with a similar
functionality that is present now on DulcineaUser.  Use the new_permissions
function as an example of how to convert PermissionManager based permissions
to the new model.
"""
from dulcinea.spec import instance, sequence, anything, spec
from dulcinea.base import DulcineaPersistent
from sets import Set

def new_permissions(connection):
    from durus.connection import gen_every_instance
    from dulcinea.user import DulcineaUser, Permissions
    from dulcinea.contact import ContactAdmin
    from dulcinea.permission import PermissionManager
    users = list(gen_every_instance(connection, DulcineaUser))
    for user in users:
        user.permissions = Permissions()
    permission_managers = list(gen_every_instance(connection, PermissionManager))
    for permission_manager in permission_managers:
        if isinstance(permission_manager, ContactAdmin):
            granter = True
            valid_permissions = user.global_permissions
        else:
            granter = permission_manager
            valid_permissions = permission_manager.valid_permissions
        for permission in valid_permissions:
            for grantee in permission_manager.get_direct_grantees(permission):
                if isinstance(grantee, DulcineaUser):
                    grantee.permissions.grant(permission, granter)
                else:
                    print ("Found direct grantee that's not a user!",
                           permission_manager, grantee, permission)
            permission_set = permission_manager.permissions.get(permission)
            if permission_set and permission_set.indirect_grantees:
                if len(permission_set.indirect_grantees) == 1:
                    other, other_permission = list(
                        permission_set.indirect_grantees)[0]
                    if (permission == 'edit-resources' and
                        other_permission == 'edit-resources' and
                        isinstance(other, ContactAdmin)):
                        continue
                print permission, permission_manager, list(
                    permission_set.indirect_grantees)
                for user in users:
                    if permission_manager.grants(permission, user):
                        user.permissions.grant(permission, granter)
    for permission_manager in permission_managers:
        if hasattr(permission_manager, 'permissions'):
            del permission_manager.permissions
        else:
            print repr(permission_manager), 'has no permissions attr'
    del connection.get_root()['user_db'].admin

class PermissionSet(DulcineaPersistent):

    direct_grantees_is = spec(
        sequence(anything, Set),
        "This permission is granted to any object in this set.")
    indirect_grantees_is = spec(
        sequence((instance('PermissionManager'), str), Set),
        "This permission is granted if 'pm' grants the permission "
        "'prerequisite' to the object.")

    def get_items(self):
        items = [(obj, None) for obj in self.direct_grantees]
        items += list(self.indirect_grantees)
        return items

    def get_direct_grantees(self):
        return list(self.direct_grantees)

    def grants(self, obj, _covered=None):
        if obj in self.direct_grantees:
            return True
        for permission_manager, prerequisite in self.indirect_grantees:
            if permission_manager.grants(prerequisite, obj, _covered):
                return True
        return False


class PermissionManager:
    """
    Class attributes:
      valid_permissions : { permission:string : description:string }
        Subclasses should set this value to list and describe the permissions
        they may grant.

    """
    valid_permissions = None

    def get_direct_grantees(self, permission):
        """(permission: str) -> [obj]

        Return the list of objects that are directly granted 'permission'.
        """
        permission_set = self.permissions.get(permission)
        if permission_set is None:
            return []
        else:
            return permission_set.get_direct_grantees()

    def grants(self, permission, obj, _covered=None):
        """(permission:str, obj, _covered:Set=None) -> bool

        Return true if 'permission' is granted (directly or indirectly)
        to 'obj'.
        """
        if permission not in self.permissions:
            return False
        else:
            _covered = _covered or Set()
            if self in _covered:
                return False
            else:
                _covered.add(self)
                return self.permissions[permission].grants(obj, _covered)
