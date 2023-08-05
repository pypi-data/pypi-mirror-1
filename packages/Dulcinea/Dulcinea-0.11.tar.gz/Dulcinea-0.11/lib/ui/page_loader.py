"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/ui/page_loader.py $
$Id: page_loader.py 27498 2005-09-29 19:57:40Z rmasse $
"""
from cStringIO import StringIO
from dulcinea import local
from dulcinea.site_util import get_root_directory
from dulcinea.ui.crumbs import get_exports
from dulcinea.ui.publisher import DulcineaPublisher
from popen2 import popen2
from pprint import pformat
from quixote import get_request
from quixote.http_request import HTTPRequest
from quixote.logger import DefaultLogger
from sancho.utest import UTest
import sys
import quixote.publish

class PrintLogger (DefaultLogger):

    def __init__(self):
        self.error_log = StringIO()
        self.access_log = None
        self.error_email = None

class TestPublisher (DulcineaPublisher):

    def __init__(self):
        DulcineaPublisher.__init__(self, logger=PrintLogger())
        # Make sure nothing gets committed.
        local.get_connection().commit = lambda: None
        local.get_connection().abort = lambda: None
        def expire_session():
            pass
        self.session_manager.expire_session = expire_session
        def del_session(self, key):
            pass
        self.session_manager.__class__.__delitem__ = del_session
        def set_actual_user(self, user):
            pass
        self.session_manager.session_class.set_actual_user = set_actual_user

    def process(self,
                PATH_INFO='/',
                input_string = '',
                SCRIPT_NAME='',
                SERVER_NAME='test@example.org',
                **kwargs):
        env = dict(PATH_INFO=PATH_INFO,
                   SCRIPT_NAME=SCRIPT_NAME,
                   SERVER_NAME=SERVER_NAME,
                   **kwargs)
        request = HTTPRequest(StringIO(input_string), env)
        self.process_request(request)
        return request


class PageTest(UTest):

    def __init__(self):
        db = local.open_database()
        self.publisher = TestPublisher()
        session_cookie_name = self.publisher.config.session_cookie_name
        session_key = "test"
        self.cookies='%s="%s"' % (session_cookie_name, session_key)
        request = HTTPRequest(None, dict(HTTP_COOKIE=self.cookies))
        self.publisher._set_request(request)
        session = local.get_session_manager()._create_session()
        self.user = self._get_admin_user()
        session.user = session.actual_user = session.last_user = self.user
        session.id = session_key
        local.get_session_manager()[session_key] = session
        assert session == local.get_session_manager().get_session()
        self.session = session
        UTest.__init__(self)
        quixote.publish._publisher = None
        db.close()

    def _get_admin_user(self):
        for user in local.get_user_db():
            if user.is_admin():
                return user
        return None

    def _get_paths(self, user):
        def _get_paths_inner(directory, base_path):
            get_request().environ['PATH_INFO'] = base_path + '/'
            exports = [export[0] for export in get_exports(directory)]
            exports.sort()
            for name in exports:
                objname = directory._q_translate(name)
                if objname is None:
                    obj = directory._q_lookup(name)
                else:
                    obj = getattr(directory, objname)
                if hasattr(obj, '_q_traverse'):
                    for path in _get_paths_inner(obj, base_path + '/' + name):
                        yield path
                else:
                    yield base_path +'/' + name
        request = HTTPRequest(None, dict(SCRIPT_NAME=''))
        self.publisher._set_request(request)
        request.session = local.get_session_manager().get_session()
        request.session.set_user(user)
        return [path for path in _get_paths_inner(get_root_directory(), '')]

    def _get_processed_request(self, path, follow_redirects=(301,),
                               **kwargs):
        """
        Returns a request after processing, after one redirect if necessary.
        """
        if 'HTTP_COOKIE' not in kwargs:
            kwargs['HTTP_COOKIE'] = self.cookies
        assert self.session.user is self.user
        request = self.publisher.process(path, **kwargs)
        assert self.publisher.session_manager.get(self.session.id) is self.session
        assert request.session is self.session
        assert request.session.user is self.user
        if request.response.get_status_code() in follow_redirects:
            location = request.response.get_header('location')
            path = '/' + location.split('/', 3)[-1] # strip http://server
            request = self.publisher.process(path, **kwargs)
        return request

    def _is_reportable(self, line):
        if 'Warning: ' in line:
            warning = line.split('Warning: ', 1)[1].strip()
            if warning in (
                '<table> lacks "summary" attribute',
                '<a> attribute "href" lacks value',
                '<form> attribute "action" lacks value',
                '<input> attribute "name" lacks value',
                'trimming empty <option>',
                'trimming empty <span>',
                '<textarea> proprietary attribute "wrap"',
                '<a> cannot copy name attribute to id', # starts with digit
                ):
                return False
            if warning.startswith("trimming empty <"):
                return False
            if (warning.endswith('" already defined') and
                warning.startswith('<a> anchor "')):
                return False
        return True

    def _expect(self, path, status=200, **kwargs):
        self.publisher.logger.error_log = StringIO()
        request = self._get_processed_request(path, **kwargs)
        assert request.session.user.is_admin(), request.session.user
        try:
            assert request.response.get_status_code() == status, (
                "%r (expected %r) %s" % (request.response.get_status_code(),
                                         status,
                                         path))
        except:
            print request.response.get_status_code(), path
            request.response.write(sys.stdout)
            if request.response.get_status_code() != status:
                print self.publisher.logger.error_log.getvalue()
            raise
        return request

    def _validate_html(self, request, assert_valid=True):
        if request.response.get_content_type() == 'text/html':
            s = StringIO()
            for chunk in request.response.generate_body_chunks():
                s.write(chunk)
            ins, outs = popen2("/usr/bin/env tidy -q -e 2>&1")
            outs.write(s.getvalue())
            outs.close()
            body_lines = s.getvalue().splitlines()
            errors = []
            for line in ins.readlines():
                if self._is_reportable(line):
                    splitline = line.split()
                    lineno = int(splitline[1])
                    colno = int(splitline[3])
                    if body_lines:
                        bodyline = body_lines[lineno-1]
                    else:
                        bodyline = ''
                    errors.append(
                        '%s    ->%s: %r\n\n' % (
                        line,
                        lineno,
                        bodyline[max(colno-20, 0):colno+100]))
            if errors:
                print (
                    "\nLoading %r:\n%s\n\n" % (
                    request.get_path(), ''.join(errors)))
                if assert_valid:
                    assert not errors, 'html errors found'
        return request

    def _crawl(self, user, omit_status=(200,)):
        """
        Collect information to use in a more general test.
        """
        expect = {}
        for path in self._get_paths(user):
            request = self._get_processed_request(path)
            if request.response.get_status_code() not in omit_status:
                expect[path] = request.response.get_status_code()
        assert 0, 'expect=\n%s' % pformat(expect)


