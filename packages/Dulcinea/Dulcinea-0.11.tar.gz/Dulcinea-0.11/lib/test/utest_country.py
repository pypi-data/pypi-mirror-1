"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_country.py $
$Id: utest_country.py 27310 2005-09-06 18:03:40Z dbinger $
"""
from sancho.utest import UTest, raises
from dulcinea.country import get_country_name, get_country_list, \
     get_country_codes

class CountryTest (UTest):

    def check_country_lookup(self):
        assert get_country_name('CA') == "Canada"
        assert get_country_name('AU') == "Australia"
        assert get_country_name('TV') == "Tuvalu"
        raises(KeyError, get_country_name, 'XX')
        raises(KeyError, get_country_name, None)

    def check_country_list(self):
        list = get_country_list()
        assert len(list) > 200
        assert ('FI', 'Finland') in list
        assert ('BR', 'Brazil') in list
        assert 0 not in [type(x) is tuple and len(x) == 2 for x in list]

    def check_country_codes(self):
        assert get_country_codes()

if __name__ == "__main__":
    CountryTest()
