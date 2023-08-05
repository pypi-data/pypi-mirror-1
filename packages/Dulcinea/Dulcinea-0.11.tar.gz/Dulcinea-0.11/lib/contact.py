"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/contact.py $
$Id: contact.py 27528 2005-10-07 20:50:40Z dbinger $
"""
from dulcinea.address import Addressable, ContactAddress
from dulcinea.base import DulcineaPersistent
from dulcinea.history import Historical
from dulcinea.permission import PermissionManager
from dulcinea.spec import mapping, init, add_getters_and_setters, spec, string
from dulcinea.user import DulcineaUser, DulcineaUserDatabase
from durus.persistent_dict import PersistentDict


class Contact(DulcineaUser, Addressable, Historical):
    """
    A more heavyweight user object that contains an Address object.
    Expects on a PermissionManager to determine if the user has admin power.
    """
    prefix_is = (string, None)
    first_name_is = (string, None)
    last_name_is = (string, None)
    phone_is = (string, None)
    fax_is = (string, None)
    company_name_is = (string, None)

    def __init__(self, user_id=None):
        DulcineaUser.__init__(self, user_id=user_id)
        Addressable.__init__(self)
        Historical.__init__(self)
        init(self)

    def get_contact_address(self):
        address = self.get_address()
        return ContactAddress(
            contact_name=self.get_contact_name(),
            contact_phone_number = self.get_phone(),
            company_name=self.get_company_name(),
            **address.__dict__)

    def get_contact_name(self, limit=35):
        last_name = self.last_name or ''
        first_name = self.first_name
        contact_name = last_name
        if first_name and len(contact_name) <= limit:
            if limit - len(contact_name) > len(first_name) + 1:
                contact_name = first_name + ' ' + last_name
            elif limit - len(contact_name) > 2:
                contact_name = first_name[0] + ' ' + last_name
        return contact_name[:limit]

    def format_realname(self):
        first_name = self.first_name or ''
        last_name = self.last_name or ''
        if first_name and last_name:
            return first_name + ' ' + last_name
        else:
            return first_name or last_name

    def format(self):
        """() -> string

        Return a string representing this user: either their real name
        (as returned by 'format_realname()') or their user ID.
        Guaranteed to return a non-empty string.
        """
        return self.format_realname() or self.id

    def record_registration (self, host):
        self.history.add_event(None, 'register',
                               'new user ID registered from host %s' % host)

    def record_login (self, host):
        self.history.add_event(None, 'login', 'login from host %s' % host)

    def record_logout (self, host):
        self.history.add_event(None, 'logout', 'logout from host %s' % host)

    def record_failed_login (self, host):
        self.history.add_event(None, 'failed_login',
                               'failed login attempt from host %s' % host)

    def record_change (self, user, host, msg=None, password=0):
        code = password and 'change_password' or 'change'
        if msg is None:
            if password:
                msg = 'changed password'
            else:
                msg = 'changed other data'
        self.history.add_event(user, code, msg + ' (host %s)' % host)


    def get_registration_time (self):
        """() -> datetime | None
        """
        return self.history.find_last_date('register')

    def get_last_login_time (self):
        """() -> datetime | None"""
        return self.history.find_last_date('login')


add_getters_and_setters(Contact)


class ContactAdmin(DulcineaPersistent, PermissionManager):
    pass

class ContactDatabase(DulcineaUserDatabase):

    user_class = Contact

    users_is = spec(
        mapping({string:user_class}, PersistentDict),
        "Maps user_ids to user instances")

    def __init__(self):
        DulcineaUserDatabase.__init__(self)
        system_user = self.user_class("SYSTEM")
        self.add_user(system_user)

