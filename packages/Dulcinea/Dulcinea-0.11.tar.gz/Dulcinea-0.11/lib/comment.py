"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/comment.py $
$Id: comment.py 27538 2005-10-11 23:00:36Z rmasse $
"""
from dulcinea.base import DulcineaPersistent
from dulcinea.spec import specify, add_getters, spec, string
from dulcinea.timestamped import Timestamped
from dulcinea.user import DulcineaUser

class Comment(DulcineaPersistent, Timestamped):

    text_is = spec(
        string)
    user_is = spec(
        (None, DulcineaUser),
        "The author of the comment")

    def __init__ (self, text, user):
        Timestamped.__init__(self)
        specify(self, text=text, user=user)

    def __str__ (self):
        return "%s at %s" % (self.user, self.get_timestamp())

    def __cmp__ (self, other):
        return cmp((self.text, self.user, self.get_timestamp()),
                   (other.text, other.user, other.get_timestamp()))

add_getters(Comment)
