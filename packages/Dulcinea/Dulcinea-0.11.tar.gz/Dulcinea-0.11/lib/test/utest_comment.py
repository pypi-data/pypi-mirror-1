"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_comment.py $
$Id: utest_comment.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from datetime import datetime
from dulcinea.comment import Comment
from dulcinea.user import DulcineaUser
from sancho.utest import UTest

class CommentTest (UTest):

    def check_comment (self):
        user = DulcineaUser("jblow")
        t1 = datetime.now()
        c = Comment("Hello", user)
        assert c.get_text() == "Hello"
        assert c.get_user() == user
        t2 = datetime.now()
        assert c.text == "Hello"
        assert c.user == user
        assert t1 <= c.get_timestamp() <= t2
        assert str(c) == "%s at %s" % (user, c.get_timestamp())
        d = Comment("H", user)
        assert d <= c

if __name__ == "__main__":
    CommentTest()
