"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_user_database.py $
$Id: utest_user_database.py 27498 2005-09-29 19:57:40Z rmasse $
"""
from dulcinea.contact import ContactDatabase, Contact
from dulcinea.spec import get_spec_problems
from dulcinea.user import DulcineaUser, DulcineaUserDatabase
from sancho.utest import UTest, raises

class Test (UTest):

    def check_user_database(self):
        user1 = DulcineaUser('1')
        user1.password_hash = 'junk'
        user2 = DulcineaUser('2')
        self.db = DulcineaUserDatabase()
        self.db.add_user(user1)
        assert self.db.get_users() == [user1]
        for user in self.db:
            assert user is user1
        self.db.add_user(user2)
        assert self.db.get_disabled_users() == [user2]
        assert self.db.get_users() == [user1]
        user2.password_hash = 'junk'
        assert self.db.get_users(sort=True) == [user1, user2]
        assert self.db.get_user('1') == user1
        assert self.db['1'] == user1
        raises(AssertionError, self.db.add_user, user1)
        assert self.db.get_admin() == None
        assert self.db.get_motd() == ''
        self.db.set_motd('The message')
        assert self.db.get_motd() == 'The message'

    def check_contact_database(self):
        self.db = ContactDatabase()
        assert get_spec_problems(self.db) == []
        user1 = Contact('1')
        user1.set_email('foo@bar.com')
        self.db.add_user(user1)
        assert self.db.get_matching_user('notfound@bar.com') == None
        assert self.db.get_matching_user('foo@bar.com') == user1

if __name__ == "__main__":
    Test()
