"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_calendar.py $
$Id: utest_calendar.py 27502 2005-09-30 14:25:36Z dbinger $
"""
from datetime import datetime, timedelta
from dulcinea.calendar import Calendar, Reservation, Reservable, Resources
from dulcinea.calendar import Resource, weekdays
from dulcinea.user import DulcineaUser
from sancho.utest import UTest
from dulcinea.base import DulcineaPersistent

class PersistentReservable(Reservable, DulcineaPersistent):
    pass

class Test (UTest):


    def check_a(self):
        self.calendar = Calendar()
        self.block1 = Reservation()
        try:
            self.calendar.add(self.block1)
            assert 0
        except TypeError: pass
        title = 'test1'
        self.block1.set_title(title)
        assert self.block1.get_title() == title
        self.block1.set_description(title)
        assert self.block1.get_description() == title
        reserved = Resource()
        self.block1.set_reserved(reserved)
        assert self.block1.get_reserved() == reserved
        user = DulcineaUser()
        self.block1.set_reserver(user)
        start1 = datetime(1,1,1)
        self.block1.set_start_time(start1)
        assert self.block1.get_start_time() == start1
        end1 = start1 + timedelta(days=1)
        self.block1.set_end_time(end1)
        assert self.block1.get_end_time() == end1

        self.calendar.add(self.block1)
        assert self.calendar.get(self.block1.get_key()) == self.block1
        assert self.calendar.get('', None) == None
        assert dict(self.calendar.get_mapping()) == {
            self.block1.get_key():  self.block1 }
        for entry in self.calendar:
            assert entry is self.block1
        self.reservable = PersistentReservable()
        self.reservable.set_active(True)
        assert self.reservable.is_active() == True
        title = 'room 1'
        self.reservable.set_title(title)
        assert self.reservable.get_title() == title
        self.block1.set_reserved(self.reservable)

        assert self.reservable.allows_control(user) == False
        assert self.reservable.allows_reserve(user) == False
        class AdminUser(DulcineaUser):
            def is_admin(self):
                return True
        admin_user = AdminUser()
        assert self.block1.can_modify(None) == False
        assert self.block1.can_modify(admin_user) == True

        self.block1.set_reserver(admin_user)
        assert self.block1.can_modify(user) == False
        user.get_permissions().grant('control', self.reservable)
        assert self.block1.can_modify(user) == True

        user2 = DulcineaUser()
        self.block1.set_reserver(user2)
        assert self.block1.can_modify(user2) == True

        Resources()

        time_increment = timedelta(hours=2)
        start_time = start1
        end_time = start_time + timedelta(days=3)
        start_time_of_day = timedelta(hours=8)
        end_time_of_day = timedelta(hours=18)
        resource = Resource()
        reservation = Reservation()
        reservation.set_title("")
        reservation.set_description("")
        reservation.set_reserved(resource)
        reservation.set_reserver(user)
        reservation.set_start_time(start_time + start_time_of_day)
        reservation.set_end_time(start_time + start_time_of_day + 
                                 2 * time_increment)
        reservation.set_reserved(resource)
        self.calendar.add(reservation)
        self.calendar.get_table_map(
            resource, time_increment, start_time, end_time, 
            start_time_of_day, end_time_of_day)


    def check_weekdays(self):
        failures = False
        for length in range(9):
            for offset in range(9):
                start = datetime(2000, 1, 1) + timedelta(days=offset)
                end = start + timedelta(days=length)
                weekdays1 = weekdays(start, end)
                currentday = start
                weekdays2 = 0
                for i in range(length):
                    if 5 <= currentday.weekday() <= 6:
                        pass
                    else:
                        weekdays2 += 1
                    currentday += timedelta(days=1)
                if weekdays1 != weekdays2:
                    failures = True
        assert not failures

if __name__ == "__main__":
    Test()
