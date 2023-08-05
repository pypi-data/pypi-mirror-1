"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/ui/publisher.py $
$Id: publisher.py 27528 2005-10-07 20:50:40Z dbinger $
"""
from dulcinea import local
from dulcinea.site_util import get_root_directory, get_config_value
from dulcinea.ui.errors import format_exception, RespondNow
from dulcinea.ui.user.util import ensure_signed_in
from durus.error import ConflictError
from quixote import get_response
from quixote.html import stringify
from quixote.http_response import HTTPResponse, Stream
from quixote.publish import Publisher
import os
import random
import tempfile
import time

TIDY_IGNORE = [
    'Warning: <table> lacks "summary" attribute',
    'Warning: trimming empty <div>',
    'Warning: trimming empty <option>',
    'Warning: <form> attribute "action" lacks value',
    ]

class DulcineaPublisher (Publisher):

    # times to retry a request that failed due to a conflict error
    CONFLICT_RETRIES = 3

    def __init__(self, **kwargs):
        import quixote
        quixote.DEFAULT_CHARSET = 'utf-8'
        Publisher.__init__(self, get_root_directory(),
                           session_manager=local.get_session_manager(),
                           **kwargs)

    def respond_now(self):
        """
        Exit the publishing loop and return the current response.
        """
        raise RespondNow

    def start_request(self):
        local.get_connection().abort()
        Publisher.start_request(self)

    def format_publish_error(self, exc):
        return format_exception(exc)

    def finish_interrupted_request(self, exc):
        if isinstance(exc, RespondNow):
            output = get_response().body
            self.session_manager.finish_successful_request()
        else:
            output = Publisher.finish_interrupted_request(self, exc)
        return output

    def try_publish(self, request):
        """Try to process a single request.  Use the base class method to the
        do actual the work.  If a conflict error occurs retry a number of
        times.
        """
        for i in range(self.CONFLICT_RETRIES + 1):
            try:
                value = Publisher.try_publish(self, request)
                if value is None:
                    return ensure_signed_in()
                return value
            except ConflictError, exc:
                self.log("ConflictError (%s): retrying request" % exc)
                local.get_connection().abort()
                request.response = HTTPResponse() # reset response object
                time.sleep(random.random() * (i+1))
        else:
            raise RuntimeError("too many conflict errors")

    def filter_output(self, request, output):
        if get_config_value('tidy_check'):
            ctype = request.response.content_type
            if (output and
                (not ctype or ctype=="text/html") and
                not isinstance(output, Stream)):
                self.html_tidy(request, output)
        return Publisher.filter_output(self, request, output)

    def html_tidy(self, request, output):
        """
        Small hack to call html-tidy for every html
        page which is serverd by quixote.

        It is used for checking the html syntax only, the html
        output won't be changed.
        """
        htmlfile = tempfile.NamedTemporaryFile()
        output = stringify(output)
        if isinstance(output, unicode):
            output = output.encode(request.response.charset)
        htmlfile.write(output)
        htmlfile.flush()
        htmlfile.seek(0)
        fp = os.popen("/usr/bin/tidy -q -e '%s' 2>&1" % htmlfile.name, "r")
        errors = []
        for line in fp:
            line = line.strip()
            if line:
                for ign in TIDY_IGNORE:
                    if ign in line:
                        break
                else:
                    errors.append(line)
        if errors:
            self.log("HTML-Tidy: %s" % request.get_path())
            for line in errors[:20]:
                self.log("   " + line)
            if len(errors) > 20:
                self.log("   [...more errors...]")
        else:
            self.log("HTML-Tidy: %s okay" % request.get_path())
        fp.close()
        htmlfile.close()
