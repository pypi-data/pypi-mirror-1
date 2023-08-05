"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/user.py $
$Id: user.py 27528 2005-10-07 20:50:40Z dbinger $
"""
from dulcinea.base import DulcineaPersistent
from dulcinea.sort import lexical_sort
from dulcinea.spec import add_getters_and_setters, sequence, string
from dulcinea.spec import spec, require, mapping, init, either
from durus.persistent import Persistent
from durus.persistent_dict import PersistentDict
from durus.persistent_set import PersistentSet
from quixote.util import randbytes
import re, sha, binascii


def hash_password(password):
    """Apply a one way hash function to a password and return the result."""
    return sha.new(password).hexdigest()

class Permissions (PersistentDict):

    data_is = {string:sequence(either(Persistent, True), PersistentSet)}

    def grant(self, permission, granter):
        require(permission, string)
        require(granter, either(Persistent, True))
        if permission not in self:
            self[permission] = PersistentSet([granter])
        else:
            self[permission].add(granter)

    def ungrant(self, permission, granter):
        require(permission, string)
        require(granter, either(Persistent, True))
        if self.is_granted(permission, granter):
            self.data[permission].remove(granter)
            if len(self.data[permission]) == 0:
                del self.data[permission]

    def is_granted(self, permission, granter):
        return granter in self.get(permission, [])

class DulcineaUser(DulcineaPersistent):
    """
    a registered user.
    """
    global_permissions = {
        "act-as":
            "Allow to act as another user.",
        "create-users":
            "Allow the creation of other users.",
        "manage-permissions":
            "Allow changing of permissions.",
        "staff":
            ("Is a member of the staff, with all of the privileges and "
             "responsibilities thereunto appertaining."),
        "system":
            "Allow to do things normally done by the software system.",
        }
    user_id_re = re.compile('^[-A-Za-z0-9_@.]*$')
    id_is = spec(
        string,
        "unique identifier for this user")
    password_hash_is = spec(
        (string, None),
        "the hashed version of the user's password, created using "
        "the hash_password function")
    email_is = (string, None)
    permissions_is = Permissions

    def __init__(self, user_id=None):
        init(self, permissions=Permissions())
        if user_id is not None:
            self.set_id(user_id)

    def __str__(self):
        return self.id or "*no id*"

    format = format_realname = __str__ # subclasses should override

    def get_key(self):
        """ used for forming component representing this user in URLs
        """
        return self.get_id()

    def set_id(self, user_id):
        require(user_id, string)
        assert self.id is None, "'id' may only be set once"
        if not self.user_id_re.match(user_id):
            raise ValueError(
                'Invalid user ID %r: can only contain '
                'letters, numbers, and "-_@."' % user_id)
        self.id = user_id

    def set_password(self, new_password, check=True):
        """Set the user's password to 'new_password'."""
        if check and self.check_new_password(new_password) != "":
            raise ValueError, 'invalid password'
        self.password_hash = hash_password(new_password)

    def valid_password(self, password):
        """Return true if the provided password is correct."""
        return self.password_hash == hash_password(password)

    def generate_password (self, length=6):
        """Set the password to a random value and return the new password."""
        password = binascii.b2a_base64(binascii.unhexlify(randbytes(length)))
        password = password[:length]
        self.set_password(password)
        return password

    def check_new_password(self, new_password):
        """(string) -> string
        Check if a new password is valid.  Returns the empty string if the
        password is okay otherwise returns a string that describes what is
        wrong with the entered password.
        """
        return ""

    def format_realname(self):
        return ''

    def is_null(self):
        return self.id == ''

    def is_disabled(self):
        return self.password_hash is None

    def __nonzero__(self):
        return not self.is_null()

    def is_system(self):
        return self.id == 'SYSTEM'

    def is_admin(self):
        return self.is_granted('staff')

    def is_granted(self, permission, granter=True):
        return self.get_permissions().is_granted(permission, granter)

    def can_manage_permissions(self):
        return self.is_granted('manage-permissions')

add_getters_and_setters(DulcineaUser)


class DulcineaUserDatabase(DulcineaPersistent):
    """
    Class to hold all users in the system.  User IDs are always looked
    up in the user database, so you will generally not be able to use
    a user until it has been added to the user database.
    """

    users_is = spec(
        mapping({string:DulcineaUser}, PersistentDict),
        "all known users")
    motd_is = spec(
       string,
       "message-of-the-day")

    user_class = DulcineaUser

    def __init__(self):
        self.users =  PersistentDict()
        self.motd = ''

    def get_all_users(self):
        return self.users.values()

    def __iter__(self):
        return self.users.itervalues()

    def get_users(self, sort=0):
        users = [user for user in self.users.itervalues()
                 if not (user.is_null() or
                         user.is_system() or
                         user.is_disabled())]
        if sort:
            users = lexical_sort(users)
        return users

    def get_disabled_users(self, sort=0):
        users = [user for user in self.users.itervalues()
                 if user.is_disabled() and not (user.is_null() or
                                                user.is_system())]
        if sort:
            users = lexical_sort(users)
        return users

    def get_matching_user(self, identifier):
        """(identifier : string) -> DulcineaUser | None

        Return a user with matching id or email address, or None
        if no such user is found.
        """
        user = self.get_user(identifier)
        if user:
            return user
        elif '@' in identifier:
            identifier = identifier.lower()
            for user in self.users.itervalues():
                if (user.get_email() or '').lower() == identifier:
                    return user
        return None

    def get_user(self, user_id):
        """Return the User object with id 'user_id', or None if no such user.
        """
        return self.users.get(user_id)

    def __getitem__(self, user_id):
        return self.users[user_id]

    def add_user(self, user):
        """Add User object 'user' to the user database.
        """
        assert not self.users.has_key(user.get_id())
        self.users[user.id] = user

    def get_admin(self):
        """Subclasses should override to return a PermissionManager
        """
        return None

    def get_null_user(self):
        user = self.users.get('')
        if user is None:
            user = self.user_class(user_id='')
            self.add_user(user)
        return user

    def get_motd(self):
        return self.motd

    def set_motd(self, motd):
        self.motd = motd or ''

    def gen_users_granted(self, permission, granter=True):
        for user in self:
            if user.is_granted(permission, granter):
                yield user

