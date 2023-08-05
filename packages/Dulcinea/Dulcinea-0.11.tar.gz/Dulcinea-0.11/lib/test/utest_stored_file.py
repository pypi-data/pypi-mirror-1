"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/test/utest_stored_file.py $
$Id: utest_stored_file.py 27147 2005-08-03 13:59:08Z dbinger $
"""
import os, shutil
from datetime import datetime
from sancho.utest import UTest, raises
from dulcinea.stored_file import path_check, new_file
from dulcinea.user import DulcineaUser

TEST_ROOT_DIR = '/tmp/storedfiletest'
TEST_CONTENT = "Contents of a file go here."

import dulcinea.stored_file
def get_file_store():
    return TEST_ROOT_DIR
dulcinea.stored_file.get_file_store = get_file_store


assert dulcinea.stored_file.get_file_store() == TEST_ROOT_DIR

class StoredFileTest (UTest):

    def _pre(self):
        if os.path.exists(TEST_ROOT_DIR):
            shutil.rmtree(TEST_ROOT_DIR)
        os.mkdir(TEST_ROOT_DIR)
        self.user = DulcineaUser('a')
        self.content_filename = os.path.join(TEST_ROOT_DIR, 'test_content')
        content = open(self.content_filename, 'w')
        content.write(TEST_CONTENT)
        content.close()

    def _post(self):
        shutil.rmtree(TEST_ROOT_DIR)
        del self.content_filename

    def check_file(self):
        sf = new_file(open(self.content_filename))
        self.f = sf.open()
        assert self.f.read() == TEST_CONTENT
        self.f.close()
        assert sf.get_size() == len(TEST_CONTENT)
        raises(ValueError, sf.set_mime_type, "textplain")
        sf.set_mime_type("text/plain")
        sf.set_filename("foo")
        assert sf.get_filename() == 'foo'
        sf.set_description("boo")
        assert sf.get_description() == 'boo'
        u = DulcineaUser()
        sf.set_owner(u)
        assert sf.get_owner() == u
        assert sf.has_manage_access(u)
        adate = datetime.now()
        sf.set_date(adate)
        assert sf.get_date() == adate


    def check_path_check(self):
        assert path_check("Abc") == 'abc'
        assert path_check("abc/../../../etc/passwd") == None
        assert path_check("/special/characters/-_@.cif") == (
                      "/special/characters/-_@.cif")
        assert path_check("/illegal/characters\001/") == None


if __name__ == "__main__":
    StoredFileTest()
