"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_news.py $
$Id: utest_news.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from dulcinea.news import NewsItem, NewsDatabase
from dulcinea.spec import get_spec_problems
from sancho.utest import UTest

class NewsTest(UTest):

    def test_item(self):
        a = NewsItem()
        db = NewsDatabase()
        db.add(a)
        assert a.get_title() == ""
        assert a.get_subtitle() == ""
        assert a.get_text() == ""
        assert not get_spec_problems(a), get_spec_problems(a)
        a.set_title('foo')
        assert a.get_title() == 'foo'
        a.set_subtitle('boo')
        assert a.get_subtitle() == 'boo'
        a.set_text('moo')
        assert a.get_text() == 'moo'
        a.set_timestamp()
        assert not get_spec_problems(a)
        b = NewsItem()
        db.add(b)
        assert db.get_news_item(a.get_key()) == a
        assert db.get_sorted_news_items() == [b, a]
        db.delete_news_item(b)
        assert db.get_news_items() == [a]

if __name__ == '__main__':
    NewsTest()

