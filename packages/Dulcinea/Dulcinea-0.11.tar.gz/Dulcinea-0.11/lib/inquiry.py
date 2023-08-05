"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/inquiry.py $
$Id: inquiry.py 27538 2005-10-11 23:00:36Z rmasse $
"""
from StringIO import StringIO
from dulcinea.attachable import Attachable
from dulcinea.base import DulcineaPersistent
from dulcinea.contact import Contact
from dulcinea.interaction import Interactable
from dulcinea.keyed import Keyed, KeyedMap
from dulcinea.spec import boolean, require, add_getters_and_setters, string
from dulcinea.timestamped import Timestamped, reverse_timestamp_sorted
from dulcinea.util import html2txt
import email

class Inquiry(DulcineaPersistent, Keyed, Timestamped, Interactable):

    msg_is = string
    text_is = string
    title_is = string
    from_address_is = (None, string)
    user_is = (None, Contact)
    open_is = boolean

    def __init__(self, raw_msg):
        require(raw_msg, string)
        assert raw_msg, "Cannot instantiate an Inquiry with an empty string"
        Interactable.__init__(self)
        Timestamped.__init__(self)
        Keyed.__init__(self)
        self.set_msg(raw_msg)
        parsed_msg = self.parse()
        if parsed_msg.is_multipart():
            text = '\n'.join(
                [sub_msg.get_payload() for sub_msg in parsed_msg.walk()
                 if sub_msg.get_content_type() == 'text/plain'])
            if not text:
               text = html2txt('\n'.join(
                   [sub_msg.get_payload() for sub_msg in parsed_msg.walk()
                    if sub_msg.get_content_type() == 'text/html']))
            if not text:
                text = 'MIME message with no "text/plain" or "text/html" parts'
        elif parsed_msg.get_content_type() == 'text/html':
            text = html2txt(parsed_msg.get_payload())
        elif parsed_msg.get_content_type() == 'text/plain':
            text = parsed_msg.get_payload()
        else:
            text = 'Content type not "text/plain" or "text/html"'
        self.set_text(text)
        self.set_from_address(parsed_msg.get('from', ''))
        self.set_title(parsed_msg.get(
            'subject', '%s: No Subject' % self.get_key()))
        self.set_open(True)
        self.user = None

    def get_title(self):
        return self.title or self.get_key()

    def is_open(self):
        return self.open

    def has_interactions(self):
        return bool(len(self.get_interaction_history()))

    def parse(self):
        """() -> email.Message
        """
        return email.message_from_file(StringIO(self.get_msg()))

add_getters_and_setters(Inquiry)


class InquiryDatabase(DulcineaPersistent, KeyedMap, Attachable):

    def __init__(self):
        KeyedMap.__init__(self, value_spec=Inquiry)
        Attachable.__init__(self)

    def get_inquiries(self, sort=True):
        inquiries = self.get_mapping().values()
        if sort:
            inquiries = reverse_timestamp_sorted(inquiries)
        return inquiries

    def add_inquiry_from_file(self, stream):
        inquiry = Inquiry(stream.read())
        self.add(inquiry)
        return inquiry
