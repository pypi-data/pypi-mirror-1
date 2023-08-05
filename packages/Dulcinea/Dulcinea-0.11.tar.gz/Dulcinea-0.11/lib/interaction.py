"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/interaction.py $
$Id: interaction.py 27389 2005-09-13 14:25:21Z dbinger $
"""
from dulcinea.history import History

class Interactable:
    """
    Storage for a set of interaction events on an object of interest
    """
    interactions_is = History

    EMAIL = 'email'
    MAIL = 'mail'
    PHONE = 'phone'
    FAX = 'fax'
    OTHER = 'other'

    INTERACTION_CODES = (EMAIL, MAIL, PHONE, FAX, OTHER)

    def __init__(self):
        self.interactions = History()

    def get_interaction_history(self):
        return self.interactions

    def get_interaction_codes(self):
        return self.INTERACTION_CODES

    def record_interaction(self, user, code, comment):
        self.interactions.add_event(user, code, comment)


