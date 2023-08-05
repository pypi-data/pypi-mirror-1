"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/persistent_session.py $
$Id: persistent_session.py 27594 2005-10-18 17:29:55Z dbinger $

Provides persistent versions of Quixote's session management classes.
"""
from dulcinea import local
from dulcinea.attachable import Attachable
from dulcinea.base import DulcineaPersistent
from dulcinea.spec import subclass, mapping, sequence, spec, string
from dulcinea.user import DulcineaUser
from durus.persistent_dict import PersistentDict
from durus.persistent_list import PersistentList
from quixote.session import Session as QuixoteSession
from quixote.session import SessionManager as QuixoteSessionManager

class DulcineaSession (DulcineaPersistent, QuixoteSession, Attachable):
    user_is = spec(
        DulcineaUser,
        "(overrides Session's attribute for stronger typing) "
        "the user object used for access control checks.  Usually "
        "user == actual_user, but when an admin user is acting as some other "
        "user, user is the person being impersonated, and actual_user is "
        "the person actually doing the work (ie.  the admin user)")
    actual_user_is = DulcineaUser
    last_user_is = DulcineaUser
    _form_tokens_is = sequence(string, PersistentList)
    _remote_address_is = (None, string)
    _access_time_is = float
    id_is = string
    _creation_time_is = float

    def __init__ (self, id):
        QuixoteSession.__init__(self, id)
        Attachable.__init__(self)
        self.user = local.get_user_db().get_null_user()
        self.actual_user = self.user
        self.last_user = self.user
        self._form_tokens = PersistentList()

    def clear_app_state(self):
        """Override to clear any session data when acting as another user
        """
        pass

    def has_info (self):
        return bool(self._form_tokens or self.get_last_user())

    def set_actual_user (self, user):
        self.user = self.actual_user = user
        if user:
            self.last_user = user

    def get_last_user(self):
        return self.last_user

class DulcineaSessionManager (DulcineaPersistent, QuixoteSessionManager):

    sessions_is = mapping({string:DulcineaSession}, PersistentDict)
    session_class_is = subclass(DulcineaSession)

    ACCESS_TIME_RESOLUTION = 900 # in seconds (don't dirty the session on
                                 # every hit)

    def __init__ (self, session_class=DulcineaSession, session_mapping=None):
        if session_mapping is None:
            session_mapping = PersistentDict()
        QuixoteSessionManager.__init__(self,
                                       session_class=session_class,
                                       session_mapping=session_mapping)

    def forget_changes (self, session):
        local.get_connection().abort()

    def commit_changes (self, session):
        local.get_connection().commit()





