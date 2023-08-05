"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_util.py $
$Id: utest_util.py 27542 2005-10-12 13:17:01Z dbinger $
"""
from datetime import datetime
from dulcinea.util import format_text, sanitize_url, wrap_paragraphs
from dulcinea.util import html2txt, activate_links, beginning_of_next_month
from dulcinea.util import _htmlescape_except, datetime_to_int, is_new
from dulcinea.util import insert_paragraph_tags
from quixote.html import htmltext
from sancho.utest import UTest
from time import time


class UtilTest (UTest):

    def check_html2txt(self):
        html = '''
        <H1>Hello</H1>
        <i>11/17/04</i>
        <p>ido</p>
        <ul>
          <li> one
          <li> two
        </ul>
        <br>
        Bye now
        '''
        text = '\nHello\n\n11/17/04\n\nido\n\none\ntwo\n\nBye now'
        assert html2txt(html) == text
        assert html2txt(htmltext(html)) == text
        assert html2txt(unicode(html)) == text
        assert html2txt(htmltext(unicode(html))) == text
        html += ' \x99'
        text += ' \x99'
        assert html2txt(html) == text, (html2txt(html), text)
        assert html2txt(htmltext(html)) == text

    def check_format_text(self):
        assert format_text('text') == 'text'
        format_text('http://www.example.org')

    def check_htmlescape_except(self):
        assert _htmlescape_except('<Br><bru>') == '<br>&lt;bru&gt;'

    def check_sanitize_url(self):
        assert sanitize_url(None) == None
        assert sanitize_url('www.example.org') == 'http://www.example.org'
        assert sanitize_url('nobody@example.com') == 'mailto:nobody@example.com'
        assert sanitize_url("ftp://ftp.example.com") == 'ftp://ftp.example.com'

    def check_wrap_paragraphs(self):
        assert wrap_paragraphs("text\n\nboo") == "text\n\nboo"
        assert wrap_paragraphs(None) == ''

    def check_insert_paragraph_tags(self):
        assert insert_paragraph_tags(None) == None
        assert str(insert_paragraph_tags('\n')) == '\n<p>\n</p>'

    def check_activate_links(self):
        assert activate_links(None) == None
        s = 'this http://example.org is fine'
        s_active = ('this <a href="http://example.org">http://example.org</a>'
                    ' is fine')
        assert str(activate_links(s)) == s_active
        s = 'this mailto:nobody@example.org is fine'
        s_active = (
            'this '
            'mailto:<a href="mailto:nobody@example.org">nobody@example.org</a>'
            ' is fine')
        assert str(activate_links(s)) == s_active
        s = 'this nobody@example.org is fine'
        s_active = (
            'this '
            '<a href="mailto:nobody@example.org">nobody@example.org</a>'
            ' is fine')
        assert str(activate_links(s)) == s_active
        s = 'this www.example.org/a. is fine'
        s_active = (
            'this '
            '<a href="http://www.example.org/a">www.example.org/a</a>.'
            ' is fine')
        assert str(activate_links(s)) == s_active

    def check_datetime_to_int(self):
        t = int(time())
        assert datetime_to_int(datetime.fromtimestamp(t)) == t
        for t in range(1, 10):
            assert datetime_to_int(datetime.fromtimestamp(t)) == t

    def check_beginning_of_next_month(self):
        a = datetime(year=2004, month=12, day=3, hour=1, minute=2, second=3,
                     microsecond=3)
        assert beginning_of_next_month(a).year == 2005
        assert beginning_of_next_month(a).month == 1
        assert beginning_of_next_month(a).day == 1
        assert beginning_of_next_month(a).hour == 0
        assert beginning_of_next_month(a).minute == 0
        assert beginning_of_next_month(a).second == 0
        assert beginning_of_next_month(a).microsecond == 0

    def check_is_new(self):
        class TestPersistent:
            def __init__(self, value):
                self._p_connection = value

        assert is_new(TestPersistent(None)) == True
        assert is_new(TestPersistent(1)) == False


if __name__ == "__main__":
    UtilTest()
