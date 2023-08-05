"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/calendar.py $
$Id: calendar.py 27538 2005-10-11 23:00:36Z rmasse $
"""
from datetime import datetime, timedelta
from dulcinea.base import DulcineaPersistent
from dulcinea.keyed import Keyed, KeyedMap
from dulcinea.permission import PermissionManager
from dulcinea.sort import method_sort
from dulcinea.spec import boolean, add_getters_and_setters, init, specify
from dulcinea.spec import string
from dulcinea.user import DulcineaUser as User

def weekdays(start, end):
    """(start: datetime, end: datetime) -> int

    Return the number of weekdays between two dates.
    """
    days = (end - start).days
    if days < 0:
        raise ValueError, 'end date must be after start date'
    weeks, partial = divmod(days, 7)
    if partial > 0:
        sunday_distance = (6 - start.weekday()) % 7
        saturday_distance = (5 - start.weekday()) % 7
        if sunday_distance < partial:
            partial -= 1
        if saturday_distance < partial:
            partial -= 1
    return 5*weeks + partial


class Titled:

    title_is = string
    description_is = string

    def __init__(self):
        init(self)

add_getters_and_setters(Titled)


class Reservable(object, PermissionManager, Keyed, Titled):

    active_is = boolean

    valid_permissions = {
        'primary_contact' : 'primary contact',
        'control' : 'able to change any reservations of this item',
        'reserve' : 'able to make a reservation of this item',
        }

    def __init__(self):
        Keyed.__init__(self)
        Titled.__init__(self)
        self.active = True

    def set_active(self, value):
        self.active = value

    def is_active(self):
        return self.active

    def allows_reserve(self, user):
        return user.is_granted('reserve', self)

    def allows_control(self, user):
        return (user.is_granted('control', self) or
                user.is_granted('primary_contact', self))


class Resource (DulcineaPersistent, Reservable):

    def __init__(self):
        Reservable.__init__(self)


class Resources (DulcineaPersistent, KeyedMap):

    def __init__(self):
        KeyedMap.__init__(self, Resource)

    def delete_resource(self, resource):
        del self.get_mapping()[resource.get_key()]


class Reservation (DulcineaPersistent, Keyed, Titled):

    start_time_is = datetime
    end_time_is = datetime
    reserved_is = Reservable
    reserver_is = User

    def __init__(self):
        Keyed.__init__(self)
        Titled.__init__(self)
        init(self)

    def __str__ (self):
        return "%s: %s" % (self.key, self.start_time)

    def set_start_time (self, time):
        time.replace(second=0, microsecond=0)
        specify(self, start_time=time)

    def set_end_time(self, time):
        assert time >= self.start_time
        time.replace(second=0, microsecond=0)
        specify(self, end_time=time)

    def is_active(self, start, end):
        return (self.get_end_time() > start and
                self.get_start_time() < end)

    def can_modify(self, user):
        """(user: User) -> bool
        """
        if user is self.reserver:
            return True
        if not user:
            return False
        if user.is_admin():
            return True
        if self.reserved.allows_control(user):
            return True
        return False

add_getters_and_setters(Reservation)


def create_reservation_table(reservations, time_increment,
                             start_time, end_time,
                             start_time_of_day, end_time_of_day):
    """(reservations : [Reservation]
        time_increment:timedelta,
        start_time:datetime,
        end_time:datetime,
        start_time_of_day:timedelta,
        end_time_of_day:timedelta) -> {
            (day:datetime, time_of_day:timedelta) :
            (reservation:Reservation, rowspan:int) | None }

    This calculates information useful for displaying a tabular view
    of a set of reservations.
    The time_increment is amount of time for each row of the table.
    The start_time and end_time determine the columns (days) of the table.
    The start_time_of_day and end_time_of_day limit the rows that are shown.

    The function returns a dictionary with an entry for each time block
    that is not vacant.  For the first block of each day for a given
    reservation, the dictionary maps (day, time_of_day) to
    (reservation, rowspan), meaning that this reservation appears first
    on this day at this time of day, and that it extends across rowspan
    time increments.

    The cells of the table that are continuations of a reservation that
    has already appeared above have entries that map (day, time_of_day)
    to None.
    """

    reservations = [reservation for reservation in reservations
                    if (reservation.get_start_time() < end_time and
                        reservation.get_end_time() > start_time)]
    reservations = method_sort(reservations, 'get_start_time')
    tableau = {}
    day_delta = timedelta(days=1)
    def gen_days():
        day = start_time
        while day < end_time:
            yield day
            day = day + day_delta
    for day in gen_days():
        day_reservations = [
            reservation for reservation in reservations
            if reservation.is_active(day + start_time_of_day,
                                     day + end_time_of_day)]
        time_of_day = start_time_of_day
        while time_of_day < end_time_of_day:
            if day_reservations:
                reservation = day_reservations[0]
                period_end = day + time_of_day + time_increment
                if reservation.get_start_time() < period_end:
                    start = (day, time_of_day)
                    reservation_end = reservation.get_end_time()
                    rows = 1
                    next_time = time_of_day + time_increment
                    while (next_time < end_time_of_day and
                           day + next_time < reservation_end):
                        rows += 1
                        time_of_day = next_time
                        next_time = next_time + time_increment
                        tableau[(day, time_of_day)] = None # mark continuation
                    tableau[start] = (reservation, rows)
                    day_reservations = day_reservations[1:]
            time_of_day = time_of_day + time_increment
    return tableau



class Calendar (DulcineaPersistent, KeyedMap):

    def __init__(self):
        KeyedMap.__init__(self, Reservation)

    def get_reservations(self):
        return self.get_mapping().values()

    def __iter__(self):
        return self.get_mapping().itervalues()

    def delete_reservation(self, reservation):
        del self.get_mapping()[reservation.get_key()]

    def get_reservations_for(self, resource):
        return [reservation for reservation in self.get_reservations()
                if resource is reservation.get_reserved()]

    def get_table_map(self, resource, time_increment,
                      start_time, end_time,
                      start_time_of_day, end_time_of_day):
        return create_reservation_table(self.get_reservations_for(resource),
                                        time_increment, start_time, end_time,
                                        start_time_of_day, end_time_of_day)
