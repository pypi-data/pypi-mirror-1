"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/util.py $
$Id: util.py 27542 2005-10-12 13:17:01Z dbinger $
"""
from StringIO import StringIO
from datetime import datetime
from distutils.fancy_getopt import wrap_text
from formatter import AbstractFormatter, DumbWriter
from htmllib import HTMLParser
from os.path import isdir, dirname
from quixote.html import htmlescape, htmltext, stringify
import re
import time

SAFE_TAGS = ['<p>', '</p>', '<b>', '</b>', '<i>', '</i>', '<ul>',
             '</ul>', '<li>', '</li>', '<br>', '<pre>', '</pre>',
             '<strong>', '</strong>']

def _htmlescape_except(text):
    """(text) -> htmltext

    Quotes 'text' for use in an HTML page, except for the tags
    listed in 'safe_tags' which are considered safe (e.g. <p>, <b>).
    Both upper and lower case versions of the tags will be applied
    """
    if text is None:
        return None
    text = stringify(htmlescape(text))
    for tag in SAFE_TAGS:
        tag_re = re.compile(stringify(htmlescape(tag)), re.IGNORECASE)
        text = tag_re.sub(tag, text)
    return htmltext(text)

# re to automatically hyperlink email addresses and URLs
_link_re = re.compile(r"""\b(
    # email address
      [\w.-]+ # local part
      @
      [\w.-]+\.[\w]{2,4} # domain
    |
    # URL
      (?:https?://|www\.) # must start with http or www
      [\w.-]+\.[\w]{2,4} # domain
      (?::\d+)? # optional port
      (?:/[\w#$%&+,-./:;=?@\[\]^_|~]*)? # optional path
   )""", re.VERBOSE)

def activate_links(text):
    """(text:str|None) -> htmltext|None
    Returns an htmlescaped version of text, with things that look like email
    addresses and URLs turned into hyperlinks.
    """
    def _link_replace(m):
        text = url = m.group(0)
        extra = ""
        if text.find("@") == -1:
            if text[-1] in ".,":
                # don't include as part of the URL (easier to handle here
                # than in the regex)
                extra = text[-1]
                text = text[:-1]
            if not text.startswith("http"):
                url = "http://" + text
        else:
            if not text.startswith("mailto"):
                url = "mailto:" + text
        return '<a href="%s">%s</a>%s' % (url, text, extra)

    if text is None:
        return None
    return htmltext(_link_re.sub(_link_replace, stringify(htmlescape(text))))


def format_text(text, safe_tags=None):
    """(text : string, safe_tags : [str]) -> htmltext

    Convert an ASCII string containing text into HTML.
    The resulting HTML has been reformatted in the following ways:
       * <, &, and > are escaped
       * Things that look like email addresses and URLs will be turned into
         hyperlinks.
       * If safe_tags is defined, it is expected to be a list of tags
         considered to be safe (e.g. <p>, <b>, etc).  These tags will
         not be escaped.
    """
    return activate_links(_htmlescape_except(text))

def sanitize_url(url):
    """(url:string) -> string
    Try to ensure a URL is well-formed, by adding http:// if it isn't present.
    """
    if url is None:
        return None
    if '@' in url and not url.startswith('mailto:'):
        # assume it's an e-mail address
        url = "mailto:" + url
    elif url.find(":") == -1:
        # assume http:// is missing
        url = "http://" + url
    return url

_paragraph_re = re.compile('\n\n+')

def split_paragraphs(text):
    return _paragraph_re.split(text)

def wrap_paragraphs(text):
    """(text) -> string
    Wrap a sequence of paragraphs for output as plain text.
    """
    if text is None:
        return ""
    line_length = 70
    return '\n\n'.join(['\n'.join(wrap_text(paragraph, line_length))
                        for paragraph in split_paragraphs(text)])

def insert_paragraph_tags(text):
    """(text:string|None) -> htmltext|None

    Prepare a text field for display as HTML.
    Currently this just HTML quotes the string and then inserts
    <p> tags at blank lines.  
    """
    if text is None:
        return None
    return htmltext(
        '\n<p>' +
        _paragraph_re.sub('</p>\n<p>', stringify(htmlescape(text))) +
        '</p>')

def datetime_to_int(date_time):
    """(date_time:datetime) -> int
    Returns the number of seconds since the epoch.
    """
    return int(time.mktime(date_time.timetuple()))

def beginning_of_next_month(date_time):
    """(date_time:datetime) -> datetime
    Return a datetime for the exact beginning of the month
    following the given date_time.  
    """
    year = date_time.year
    month = date_time.month + 1
    if month == 13:
        year += 1
        month = 1
    return datetime(year=year, month=month, day=1, hour=0, minute=0,
                    second=0, microsecond=0)

def html2txt(text):
    """(any) -> str
    """
    sio = StringIO()
    parser = HTMLParser(AbstractFormatter(DumbWriter(sio)))
    parser.feed(stringify(text))
    return sio.getvalue()

def is_new(persistent_object):
    """(persistent_object : durus.persistent.Persistent) -> boolean
    """
    return persistent_object._p_connection is None

def get_module_directory(module):
    result = module.__file__
    if isdir(result):
        return result
    else:
        return dirname(result)

import re
pat = re.compile(r'([\x80-\xff]{2,}(?:"|\(tm\))?)')
utf8indicator = re.compile(r'[\xc2-\xc3]')
cp1252indicator = re.compile(r'[\x80-\x9f]')

def get_targets(s):
    return [w for w in pat.findall(s)
            if utf8indicator.search(w)]

def ureduce(s):
    for depth in range(10):
        try:
            s = unicode(s, 'utf8')
            try:
                s = s.encode('latin1')
            except UnicodeEncodeError:
                return s
        except UnicodeDecodeError:
            pass
    return s

def demangle(s):
    if s.endswith('(tm)'):
        s = s.replace('(tm)', '\xc3\x82\xc2\x99')
    if s.endswith('"'):
        s = '"'
    if s.endswith('-'):
        s = '-'
    return s

def find_using_utf8(s):
    orig = s
    if not utf8indicator.search(s):
        return s
    for target in get_targets(s):
        result = ureduce(demangle(target))
        if isinstance(result, unicode):
            result = result.encode('utf8')
        s = s.replace(target, result)
    try:
        return unicode(s, 'utf8')
    except UnicodeDecodeError:
        return orig

def unify_instance(obj):
    from dulcinea.spec import get_specs, match
    for name, spec in get_specs(obj.__class__).items():
        if match(u'', spec):
            old_value = getattr(obj, name)
            if not isinstance(old_value, str):
                continue
            # Try ascii first.
            try:
                setattr(obj, name, unicode(old_value, 'ascii'))
                continue
            except UnicodeDecodeError:
                pass
            # try hyper utf8.
            result = find_using_utf8(old_value)
            if isinstance(result, unicode):
                setattr(obj, name, result)
                if u'\xc3' in result or u'\xc2' in result:
                    print 'hyper utf8', obj
                continue
            if cp1252indicator.search(old_value):
                try:
                    setattr(obj, name, unicode(old_value, 'cp1252'))
                    continue
                except UnicodeDecodeError:
                    pass
            if utf8indicator.search(old_value):
                try:
                    setattr(obj, name, unicode(old_value, 'utf16'))
                    continue
                except UnicodeDecodeError:
                    pass
                print 'utf8', obj
            setattr(obj, name, unicode(old_value, 'latin1'))

def unify(connection):
    from durus.connection import gen_every_instance
    from durus.persistent import Persistent
    for item in gen_every_instance(connection, Persistent):
        unify_instance(item)
