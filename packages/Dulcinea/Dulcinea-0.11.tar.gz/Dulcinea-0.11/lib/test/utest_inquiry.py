#!/www/python/bin/python
"""$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_inquiry.py $
$Id: utest_inquiry.py 27242 2005-08-22 20:22:08Z rmasse $
"""
from StringIO import StringIO
from sancho.utest import UTest
from dulcinea.contact import Contact
from dulcinea.inquiry import Inquiry, InquiryDatabase

test_msg = '''\
From nobody Thu Dec 2 15:48:02 2004
Received: (qmail 17230 invoked from network); 2 Dec 2004 20:48:00 -0000
Received: from localhost (HELO ion.mems-exchange.org) (127.0.0.1)
\tby 10.27.8.146 with SMTP; 02 Dec 2004 15:48:00 -0500
From: Roger <mail@rogermasse.com>
Subject: Quote inquiry: from the get-a-quote form
To: inquiry@rogermasse.com

[debug mode, message actually sent to inquiry@rogermasse.com]
------------------------------------------------------------------------
Name: Roger
Phone: None
Email: mail@rogermasse.com

This is a test from the get a quote form'''

class InquiryTest(UTest):

    def check_inquiry(self):
        inquiry = Inquiry('Guido')
        assert inquiry.is_open()
        assert inquiry.get_msg() == 'Guido'
        inquiry.set_text('van Rossum')
        assert inquiry.get_text() == 'van Rossum'
        inquiry.set_title('Python')
        assert inquiry.get_title() == 'Python'
        inquiry.set_from_address('guido@python.org')
        assert inquiry.get_from_address() == 'guido@python.org'
        inquiry.set_open(False)
        assert not inquiry.is_open()
        user = Contact('Guido')
        assert inquiry.get_user() is None
        inquiry.set_user(user)
        assert inquiry.get_user() is user

    def check_inquiry_db(self):
        idb = InquiryDatabase()
        inquiry = idb.add_inquiry_from_file(StringIO(test_msg))
        assert inquiry.get_from_address() == 'Roger <mail@rogermasse.com>'
        assert inquiry is idb.get_inquiries()[-1]
        assert inquiry is idb.get_inquiries(sort=1)[-1]

if __name__ == "__main__":
    InquiryTest()
