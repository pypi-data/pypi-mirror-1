"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/timestamped.py $
$Id: timestamped.py 27308 2005-09-06 17:31:20Z dbinger $
"""
from datetime import datetime
from dulcinea.sort import attr_sort

def timestamp_sorted(timestamped_sequence):
    return attr_sort(timestamped_sequence, 'timestamp')

def reverse_timestamp_sorted(timestamped_sequence):
    result = timestamp_sorted(timestamped_sequence)
    result.reverse()
    return result

class Timestamped(object):

    timestamp_is = datetime

    def __init__(self):
        self.set_timestamp()

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self):
        self.timestamp = datetime.now()
