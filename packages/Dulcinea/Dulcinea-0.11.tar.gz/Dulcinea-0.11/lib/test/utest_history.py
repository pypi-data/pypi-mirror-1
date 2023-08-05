"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_history.py $
$Id: utest_history.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from datetime import datetime, timedelta
from dulcinea.history import History, Event, Historical
from dulcinea.user import DulcineaUser
from sancho.utest import UTest
import time


class HistoryTest (UTest):

    def _pre(self):
        self.user1 = DulcineaUser("joe")
        self.user2 = DulcineaUser("jane")

    def _post(self):
        del self.user1, self.user2

    def check_historical(self):
        Historical().get_history()

    def check_event(self):
        user = DulcineaUser("jblow")
        message = "created new foobar ding-dong"
        event1 = Event(user, "create", message)
        assert event1.get_user() == user
        assert event1.get_event_code() == 'create'
        assert event1.get_message() == message

        assert str(event1) == "%s create" % event1.timestamp

        event2 = Event(user, "modify", "changed blah blah on foobar")
        assert event2.timestamp >= event1.timestamp
        time.sleep(0.01)
        event3 = Event(user, "delete", "jblow deleted foobar")
        assert event3.timestamp > event2.timestamp
        assert event3.timestamp is event3.get_timestamp()

    def check_history(self):
        history = History()
        assert len(history) == 0
        assert str(history) == "history (0 events)"
        history.add_event(self.user1, 'create', 'joe created blah')
        history.add_event(None, 'modify', 'jane modified blah')
        assert len(history) == 2
        assert history[0].timestamp <= history[1].timestamp
        assert history[0].user == self.user1
        assert history[1].user == None

        history.add_event(self.user2, 'create', 'a')
        assert len(history) == 3
        assert (history[0].timestamp <
                history[1].timestamp <=
                history[2].timestamp)
        history.add_event(None, 'create', 'modern age begins')
        assert len(history) == 4
        assert history[0].message == "joe created blah"
        assert history[1].message == "jane modified blah"


    def check_variations(self):
        history = History()
        # Works with no user object
        history.add_event(None, 'modify', 'tweaked it')
        assert history[-1].user == None

        # Replacing existing event
        history.update_last_event(None, 'modify', 'tweaked it more')
        assert history[-1].message == 'tweaked it more'

        history.update_last_event(None, 'create', 'creation')
        assert history[-2].message == 'tweaked it more'

    def check_find(self):
        history = History()
        assert history.find_event() == None
        assert history.find_event(latest=True) == None

        history.add_event(self.user1, "create", "joe created it")
        assert history.find_event().message == "joe created it"
        assert history.find_event(latest=True).message == "joe created it"
        assert history.find_event(user=self.user1).message == "joe created it"
        assert history.find_event(user=self.user2) == None
        assert history.find_event(event_code='create').message == (
            "joe created it")
        assert history.find_event(message='no created it') == None

        assert history.find_event(event_code='access') == None
        assert history.find_event(event_codes=['access']) == None

        start = datetime.now() - timedelta(1)
        history.add_event(self.user2, "access", "jane accessed it")
        history.add_event(self.user1, "modify", "joe modified it")
        history.add_event(self.user2, "modify", "jane modified it")
        history.add_event(self.user2, "delete", "jane deleted it")

        assert history.find_event().message == "joe created it"
        assert history.find_event(latest=True).message == "jane deleted it"
        assert history.find_event(user=self.user1,latest=True).message == (
            "joe modified it")
        assert history.find_event(event_code='modify').message == (
            "joe modified it")
        assert history.find_event(event_code='modify',latest=True).message == (
            "jane modified it")
        assert len(history.find_events_after(start)) == 5
        assert history.find_last_date('foo') == None


if __name__ == "__main__":
    HistoryTest()
