"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/news.py $
$Id: news.py 27538 2005-10-11 23:00:36Z rmasse $
"""
from dulcinea.base import DulcineaPersistent
from dulcinea.keyed import Keyed, KeyedMap
from dulcinea.spec import specify, spec, add_getters_and_setters, string
from dulcinea.timestamped import Timestamped, reverse_timestamp_sorted


class NewsItem(Keyed, Timestamped, DulcineaPersistent):
    """
    A single announcement.
    """
    title_is = spec(
        string,
        "Title of this announcement.")
    subtitle_is = spec(
        string,
        "A subtitle that can be shown with the link text, but isn't required.")
    text_is = spec(
        string,
        "HTML text of this announcement.  This field will not be escaped.")

    def __init__ (self):
        Keyed.__init__(self)
        Timestamped.__init__(self)
        specify(self, title='', subtitle='', text='')

add_getters_and_setters(NewsItem)

class NewsDatabase(KeyedMap, DulcineaPersistent):

    def __init__(self):
        KeyedMap.__init__(self, value_spec=NewsItem)

    def delete_news_item(self, item):
        """(item : NewsItem)
        """
        del self.mapping[item.get_key()]

    def get_news_item(self, key):
        return self.mapping[key]

    def get_news_items(self):
        return self.mapping.values()

    def get_sorted_news_items(self):
        return reverse_timestamp_sorted(self.mapping.values())
