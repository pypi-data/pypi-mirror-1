"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/cents.py $
$Id: cents.py 27367 2005-09-13 13:54:34Z dbinger $
"""
from dulcinea.spec import either, require, specify

class Cents(object):

    cents_is = either(int, long)

    def __init__(self, value):
        specify(self, cents=value)

    def get_cents(self):
        return self.cents

    def __str__(self):
        return "$%.02f" % self.get_dollars()

    def get_dollars(self):
        return self.cents / 100.0

    def __add__(self, other):
        require(other, Cents)
        return Cents(self.cents + other.cents)

    def __sub__(self, other):
        require(other, Cents)
        return Cents(self.cents - other.cents)

    def __cmp__(self, other):
        require(other, Cents)
        return cmp(self.cents, other.cents)

