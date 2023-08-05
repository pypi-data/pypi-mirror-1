"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_user.py $
$Id: utest_user.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea.user import DulcineaUser as User
from sancho.utest import UTest, raises

class DulcineaUserTest (UTest):

    def check_init (self):
        raises(ValueError, User, '!@#$%^')
        User('amk')
        u = User()
        u.set_id('foo')
        raises(AssertionError, User('foo').set_id, 'foo')
        raises(ValueError, User().set_id, '!foo')
        u = User()
        assert u.id == None
        u.set_id('foo')
        assert u.id == "foo"
        raises(AssertionError, u.set_id, 'bar')

    def check_password (self):
        user = User('foo')
        user.set_password("biteme")
        assert user.valid_password("biteme")
        assert not user.valid_password("dontbiteme")
        password1 = user.generate_password()
        assert user.valid_password(password1)
        password2 = user.generate_password()
        assert user.valid_password(password2)
        assert password1 != password2


if __name__ == "__main__":
    DulcineaUserTest()
