"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_interaction.py $
$Id: utest_interaction.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea.interaction import Interactable
from dulcinea.user import DulcineaUser
from sancho.utest import UTest

class TestUser(DulcineaUser, Interactable):

    def __init__(self, id):
        DulcineaUser.__init__(self, id)
        Interactable.__init__(self)

class InteractableTest (UTest):

    def check_interactions(self):
        user = TestUser('guido')
        assert len(user.get_interaction_history()) == 0
        user.record_interaction(user, 'email', 'email sent')
        assert len(user.get_interaction_history()) == 1
        assert user.get_interaction_codes() == user.INTERACTION_CODES

if __name__ == "__main__":
    InteractableTest()

