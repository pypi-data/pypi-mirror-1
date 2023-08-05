"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/address.py $
$Id: address.py 27528 2005-10-07 20:50:40Z dbinger $
"""
from dulcinea.base import DulcineaPersistent
from dulcinea.country import get_country_codes
from dulcinea.spec import spec, add_getters, add_getters_and_setters
from dulcinea.spec import either, init, specify, string
import re

class Address (DulcineaPersistent):

    street1_is = (string, None)
    street2_is = (string, None)
    city_is = (string, None)
    state_is = (string, None)
    zip_is = (string, None)
    country_code_is = spec(
        either(None, *get_country_codes()),
        "ISO-3166 two-letter country code")

    STATES = [
        "AL", "AK", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD",
        "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH",
        "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY",

        # Commonwealths & territories
        "AS", "DC", "FM", "GU", "MP", "PR", "VI",

        # Armed forces codes
        "AA", "AE", "AP"]


    def __init__(self, **kwargs):
        init(self, **kwargs)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                other.__dict__ == self.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_valid(self):
        """() -> bool

        Return true if this address is valid: either it's empty or
        it's complete (and correct!).
        """
        return self._check_complete() == []

    def _check_complete(self):
        """() -> [(attrname:str, errtype:str)]

        Check whether this address is complete: must have at least one
        line of street address, city, and country; if country is US,
        must have a valid state and ZIP code too.

        Returns a list of (attrname, errtype) 2-tuples explaining any
        problems.  'errtype' is either "missing" or "bad".
        """
        errors = []
        for field in ['street1', 'city', 'country_code']:
            if not getattr(self, field):
                errors.append((field, "missing"))

        # US-specific checks
        if self.country_code == 'US':
            if not self.state:
                errors.append(('state', "missing"))
            else:
                state = self.state.upper()
                if state not in self.STATES:
                    errors.append(('state', "bad"))
                elif state != self.state:
                    self.state = state  # make uppercase

            # Check the Zip code (5 digits, or 5+4 format)
            if not self.zip:
                errors.append(('zip', "missing"))
            elif not self.has_valid_zip():
                errors.append(('zip', "bad"))

        return errors

    def has_valid_zip(self):
        if self.country_code == 'US':
            if not self.zip:
                return False
            return re.match(r'\d{5}(-\d{4})?$', self.zip) is not None
        return True

    def has_valid_state(self):
        if self.country_code == 'US':
            return self.state and self.state in self.STATES
        return True

    def error_message(self):
        msg = ""
        for errors in self._check_complete():
            msg = msg + "%s is %s, " % (
                " ".join([word.capitalize() for word in errors[0].split("_")]),
                errors[1])
        return (msg and msg[:-2] + '.') or msg

    def format(self):
        address = ""
        if self.street1:
            address += self.street1 + "\n"
        if self.street2:
            address += self.street2 + "\n"
        if self.city:
            address += self.city + ", "
        if self.state:
            address += self.state + " "
        if self.zip:
            address += self.zip
        if address[-1:] != "\n":
            address += "\n"
        if self.country_code:
            address += self.country_code
        return address

    def format_street(self):
        result = self.street1 or ''
        if self.street2:
            result += ', ' + self.street2
        return result

add_getters(Address)


class Addressable:
    """
    Mixin for objects that contain addresses
    """
    address_is = Address

    def __init__(self, address=None, **kwargs):
        self.address = address or Address(**kwargs)

    def set_address(self, address):
        """(address : Address)
        """
        specify(self, address=address)

    def get_address(self):
        """() -> Address
        """
        return self.address


class ContactAddress(DulcineaPersistent, Addressable):
    """
    This is an address with the additional information normally needed
    for shipping.
    """
    contact_name_is = (string, None)
    contact_phone_number_is = (string, None)
    company_name_is = (string, None)

    def __init__(self, contact_name=None, contact_phone_number=None,
                 company_name=None, **kwargs):
        Addressable.__init__(self, **kwargs)
        specify(self,
                contact_name=contact_name,
                contact_phone_number=contact_phone_number,
                company_name=company_name)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                other.__dict__ == self.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_valid(self):
        return self._check_complete() == []

    def error_message(self):
        return self.address.error_message()

    def set_address(self, address):
        raise RuntimeError("ContactAddress is treated as immutable")

    def get_street1(self):
        return self.address.get_street1()

    def get_street2(self):
        return self.address.get_street2()

    def get_city(self):
        return self.address.get_city()

    def get_state(self):
        return self.address.get_state()

    def get_zip(self):
        return self.address.get_zip()

    def get_country_code(self):
        return self.address.get_country_code()

    def has_valid_phone_number(self):
        return is_valid_phone_number(self.get_contact_phone_number(),
                                     self.get_country_code())
    def _check_complete(self):
        """() -> [(attrname:str, errtype:str)]

        Returns a list of (attrname, errtype) 2-tuples explaining any
        problems.  'errtype' is either "missing" or "bad".
        """
        errors = self.address._check_complete()
        for field in ['contact_name', 'contact_phone_number']:
            if not getattr(self, field):
                errors.append((field, "missing"))
        if self.contact_phone_number and not self.has_valid_phone_number():
            errors.append(('contact_phone_number', 'bad'))
        return errors

    def format(self):
        if self.get_contact_name():
            output = self.get_contact_name() + "\n"
        else:
            output = ""
        if self.company_name:
            output += self.company_name + "\n"
        output += self.address.format()
        return output

add_getters(ContactAddress)

def is_valid_phone_number(number, country_code):
    if not number:
        return False
    number_of_digits = 0
    for token in number:
        if token.isdigit():
            number_of_digits += 1
    if country_code == 'US':
        return number_of_digits >= 10
    else:
        return number_of_digits >= 7

class ContactAddressable:
    """
    Mixin for objects that have a contact address.
    """

    contact_address_is = ContactAddress

    def __init__(self):
        self.contact_address = ContactAddress()

add_getters_and_setters(ContactAddress)




