"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_address.py $
$Id: utest_address.py 27310 2005-09-06 18:03:40Z dbinger $
"""
from dulcinea.address import Address, ContactAddress
from dulcinea.spec import get_spec_problems
from sancho.utest import UTest

class AddressTest (UTest):

    def check_init (self):
        Address()
        a=Address(street1="s1", street2="s2")
        assert a.street1 == 's1'
        assert a.street2 == 's2'
        try:
            Address(bogus="goofy")
            assert 0
        except AttributeError: pass

    def check_complete(self):
        addr = ContactAddress(contact_name="Bogus Contact",
                              contact_phone_number="888 555 1212",
                              street1='1320 St.',
                              city='Arlington',
                              state='VA',
                              country_code='US',
                              zip='22201')
        assert get_spec_problems(addr) == []
        assert addr.has_valid_phone_number()
        assert list(addr._check_complete()) == list([])

        # Test an empty contact phone number
        addr.contact_phone_number = ''
        assert addr._check_complete() == [('contact_phone_number',
                                           'missing')]
        addr.contact_phone_number = "888 555 1212"

        # Test the checks on the state field
        addr.address.state = ''
        assert addr._check_complete() == [('state', 'missing')]

        addr.address.state = 'VAR'
        assert addr._check_complete() == [('state', 'bad')]

        addr.address.state = 'VB'
        assert addr._check_complete() == [('state', 'bad')]

        addr.address.state = 'VA'
        addr.address.zip = '29999-'
        assert addr._check_complete() == [('zip', 'bad')]

        addr.address.state = 'XX'
        addr.address.zip = None
        assert addr._check_complete() == [('state', 'bad'), ('zip', 'missing')]

        # Will a Canadian province work?`
        addr.address.country_code = 'CA'
        addr.address.state = 'QC'
        assert list(addr._check_complete()) == list([])


    def check_valid (self):
        addr = ContactAddress()
        assert len(addr._check_complete()) > 0
        assert not addr.is_valid()

        addr.address.street1 = "123 Main St."
        assert len(addr._check_complete()) > 0
        assert not addr.is_valid()

        addr.address.city = "Paris"
        addr.address.country_code = "FR"
        assert addr._check_complete() == [('contact_name', 'missing'),
                                          ('contact_phone_number', 'missing')]
        assert not addr.is_valid()
        addr.contact_name = 'foo'
        addr.contact_phone_number = '1112223333'
        assert addr.is_valid()
        assert get_spec_problems(addr) == []


    def check_phone (self):

        for number in ('514-482-7346',
                       '1-514-482-7346',
                       '+1-514-482-7346',
                       '5144827346',
                       '514 482 7346',
                       '(514) 482-7346',
                       '1 (514) 482-7346',
                       '+1 (514) 482-7346',
                       '703-620-8990 x123',
                       '703-620-8990 x 123',
                       '703-620-8990 ext123',
                       '703-620-8990 ext. 123',
                       '703-620-8990 X123',
                       '703-620-8990 X 123',
                       '703-620-8990 Ext123',
                       '703-620-8990 Ext. 123',
                       '+44 (0)20 8681 9603',
                       '+33 01 47 42 20 34',
                       '+33 03 83 27 56 52'):
            addr = ContactAddress(country_code='US',
                                  contact_phone_number=number)
            assert addr.has_valid_phone_number()
        addr = ContactAddress(country_code='US',
                              contact_phone_number='482 7346')
        assert not addr.has_valid_phone_number()
        addr = ContactAddress(country_code='US',
                              contact_phone_number='482- 7346')
        


if __name__ == "__main__":
    AddressTest()

