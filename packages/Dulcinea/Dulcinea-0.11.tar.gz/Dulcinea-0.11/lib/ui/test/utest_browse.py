"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/ui/test/utest_browse.py $
$Id: utest_browse.py 27147 2005-08-03 13:59:08Z dbinger $
"""
from quixote import enable_ptl ; enable_ptl()
from dulcinea import local_ui
from dulcinea.ui.browse import ArchiveDirectory, ImageArchiveDirectory
from dulcinea.ui.browse import IndexArchiveDirectory, format_browse_css
from dulcinea.util import get_module_directory
from quixote.http_request import HTTPRequest
from quixote.logger import DefaultLogger
from quixote.publish import Publisher
from sancho.utest import UTest
import dulcinea.ui
import quixote.publish
import sys

local_ui.header = lambda a : None
local_ui.footer = lambda a : None

def get_test_archive(type):
    test_directory = get_module_directory(dulcinea.ui) + '/test/'
    return test_directory + 'browse_test.%s' % type

class PrintLogger(DefaultLogger):

    def __init__(self):
        self.error_log = sys.stdout
        self.access_log = None
        self.error_email = None

def decorate (obj, content, title=None):
    return content

class ArchiveDirectoryTest (UTest):

    def _pre(self):
        quixote.publish._publisher = None

    def _post(self):
        quixote.publish._publisher = None

    def test_misc(self):
        format_browse_css()

    def test_archive_directory_with_zip(self):

        archive_dir = ArchiveDirectory(get_test_archive('zip'),
                                       decorate=decorate)
        publisher = Publisher(archive_dir, logger=PrintLogger())
        publisher._set_request(HTTPRequest(None, dict(SCRIPT_NAME='',
                                                      PATH_INFO='/')))

        assert archive_dir._q_translate('') == '_q_index'
        archive_dir()
        archive_dir._q_traverse(['browse_test', ''])
        archive_dir._q_traverse(['browse_test', 'trek.jpg'])
        archive_dir._q_traverse(['browse_test', 'a', 'trek.jpg'])
        contents = archive_dir._q_traverse(['browse_test', 'b', 'c', 'd.txt'])
        assert contents == 'Congratulations!\n'
        publisher._set_request(HTTPRequest(None, dict(SCRIPT_NAME='',
                                                      PATH_INFO='/',
                                                      QUERY_STRING = '40')))
        archive_dir._q_traverse(['browse_test', 'a', 'trek.jpg'])

    def test_image_archive_directory_with_zip(self):
        archive_dir = ImageArchiveDirectory(get_test_archive('zip'))
        publisher = Publisher(archive_dir, logger=PrintLogger())
        publisher._set_request(HTTPRequest(None, dict(SCRIPT_NAME='',
                                                      PATH_INFO='/',
                                                      QUERY_STRING = '40')))
        archive_dir._q_traverse(['browse_test', 'a', 'trek.jpg'])

    def test_image_archive_directory_with_tgz(self):

        archive_dir = ImageArchiveDirectory(get_test_archive('tgz'))
        publisher = Publisher(archive_dir, logger=PrintLogger())
        publisher._set_request(HTTPRequest(None, dict(SCRIPT_NAME='',
                                                      PATH_INFO='/')))

        assert archive_dir._q_translate('') == '_q_index'
        archive_dir._q_traverse(['browse_test', ''])
        archive_dir._q_traverse(['browse_test', 'trek.jpg'])
        archive_dir._q_traverse(['browse_test', 'a', 'trek.jpg'])
        fs = archive_dir._q_traverse(['browse_test', 'b', 'c', 'd.txt'])
        contents = [chunk for chunk in fs]
        assert contents == ['Congratulations!\n']
        publisher._set_request(HTTPRequest(None, dict(SCRIPT_NAME='',
                                                      PATH_INFO='/',
                                                      QUERY_STRING = '40')))
        archive_dir._q_traverse(['browse_test', 'a', 'trek.jpg'])

    def test_index_archive_directory_with_tar(self):

        archive_dir = IndexArchiveDirectory(get_test_archive('tar'))
        publisher = Publisher(archive_dir, logger=PrintLogger())
        publisher._set_request(HTTPRequest(None, dict(SCRIPT_NAME='',
                                                      PATH_INFO='/')))

        assert archive_dir._q_translate('') == '_q_index'
        archive_dir._q_traverse(['browse_test', ''])
        archive_dir._q_traverse(['browse_test', 'trek.jpg'])
        archive_dir._q_traverse(['browse_test', 'a', 'trek.jpg'])
        fs = archive_dir._q_traverse(['browse_test', 'b', 'c', 'd.txt'])
        contents = [chunk for chunk in fs]
        assert contents == ['Congratulations!\n']

if __name__ == "__main__":
    ArchiveDirectoryTest()
