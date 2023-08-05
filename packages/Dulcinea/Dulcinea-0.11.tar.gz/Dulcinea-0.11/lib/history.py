"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/history.py $
$Id: history.py 27528 2005-10-07 20:50:40Z dbinger $
"""
from datetime import datetime
from dulcinea.base import DulcineaBase, DulcineaPersistent
from dulcinea.spec import add_getters, specify, require, string
from dulcinea.user import DulcineaUser

class Event (DulcineaBase):
    """
    Event objects should never be created outside of History.add_event().
    """
    timestamp_is = datetime
    user_is = (DulcineaUser, None)
    event_code_is = string
    message_is = (string, None)

    def __init__(self, user, event_code, message):
        specify(self, user=user, event_code=event_code, message=message,
                timestamp=datetime.now())

    def __str__(self):
        return "%s %s" % (self.timestamp, self.event_code)

add_getters(Event)


class History (DulcineaPersistent):

    events_is = [Event]

    def __init__(self):
        specify(self, events=[])

    def __str__(self):
        return "history (%d events)" % len(self.events)

    def __len__(self):
        return len(self.events)

    def __getitem__(self, i):
        return self.events[i]

    def add_event(self, user, event_code, message):
        """(user : DulcineaUser, event_code : string, message : string)

        Create and append a new Event instance. 
        """
        new_event = Event(user, event_code, message)
        self._p_note_change()
        self.events.append(new_event)

    def update_last_event(self, user, event_code, message):
        """(user : DulcineaUser, event_code : string, message : string)

        Create a new Event instance. If the last event on the list had
        the same event code and user, replace the last event with the
        new one.
        """
        self._p_note_change()
        if self.events:
            if (self.events[-1].event_code == event_code and
                self.events[-1].user == user):
                self.events = self.events[:-1]
        self.events.append(Event(user, event_code, message))

    def find_event(self, user=None, event_code=None, event_codes=None,
                   latest=False, message=None):
        """(user : DulcineaUser = None,
            event_code : string = None,
            latest : bool = False,
            message : string = None) -> Event

        Find the earliest(or latest, if latest is true) event
        matching 'user' and/or 'event_code'.  If either search criterion
        is not supplied or None, it does not affect the search, thus the
        default behaviour is to return the first event in the history
        list.  Return None if no events match.
        """
        require(user, (DulcineaUser, None))
        if latest:
            indices = xrange(len(self.events)-1, -1, -1)
        else:
            indices = xrange(len(self.events))
        for i in indices:
            event = self.events[i]
            if user and event.user is not user:
                continue
            if event_code is not None and event.event_code != event_code:
                continue
            if event_codes is not None and event.event_code not in event_codes:
                continue
            if message is not None and event.message != message:
                continue
            return event
        else:
            return None

    def find_events_after(self, time, event_code=None):
        return [event
                for event in self.events
                if event.get_timestamp() > time and (
                    event_code is None or
                    event.get_event_code() == event_code)]

    def find_last_date(self, event_code):
        """(event_code:string) -> datetime | None"""
        event = self.find_event(event_code=event_code, latest=True)
        return event and event.get_timestamp()


class Historical:

    history_is = History

    def __init__(self):
        self.history = History()

    def get_history(self):
        return self.history
