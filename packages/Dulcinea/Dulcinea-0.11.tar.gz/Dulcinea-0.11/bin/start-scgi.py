#!/www/python/bin/python
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/bin/start-scgi.py $
$Id: start-scgi.py 27327 2005-09-07 20:07:10Z dbinger $

Script invoked by site command to start scgi.
"""
import os, sys
site = os.environ['SITE'] = sys.argv[1]
from dulcinea import local
from dulcinea.site_util import enable_email, log_to, get_base_path
from dulcinea.site_util import ensure_uid_gid_not_root, parse_address, is_devel
from dulcinea.site_util import get_administrator_address, is_live, is_staging
from dulcinea.site_util import get_config_value, get_pid_file_name, is_local
from dulcinea.ui.publisher import DulcineaPublisher
from durus.logger import logger
from quixote.config import Config
from quixote.server.scgi_server import run as run_scgi
import pwd
import socket

ensure_uid_gid_not_root()
pid_file_name = get_pid_file_name('scgi', site)
ip, port = parse_address(
    get_config_value('scgi_address', site=site))
site_log_dir = os.path.join(get_config_value('log_directory', site=site), site)
error_log = os.path.join(site_log_dir, 'error.log')
assert is_local(get_config_value('scgi_address', site=site))
logger.setLevel(int(get_config_value('logginglevel', fallback=20, site=site)))

def create_publisher():
    local.open_database()
    # set config options
    config = Config()
    config.form_tokens = 1
    config.display_exceptions = 0
    config.session_cookie_path = '/'
    site_log_dir = os.path.join(get_config_value('log_directory', site=site),
                                site)
    config.access_log = os.path.join(site_log_dir, 'access.log')
    config.error_log = error_log
    try:
        import zlib
        zlib # to quiet import checker
        config.compress_pages = 1
    except ImportError:
        config.compress_pages = 0
    administrator = get_administrator_address()

    if is_live(site):
        config.error_email = administrator[0]
        config.mail_from = administrator
    elif is_staging(site):
        config.error_email = administrator[0]
        config.mail_from = administrator
        config.mail_debug_addr = administrator[0]
    else: # devel
        config.display_exceptions = 1
        user = pwd.getpwuid(os.geteuid())[0] # Owner of the SCGI process
        user_email = user + '@' + socket.getfqdn()
        config.mail_debug_addr = get_config_value(
            'mail_debug_addr',
            fallback=user_email,
            site=site)
        config.mail_from = user_email

    # Adjust any values that are set in the site configuration.
    for config_var in config.config_vars:
        if get_config_value(config_var, site=site):
            setattr(config, config_var,
                    get_config_value(config_var, site=site))
    if get_config_value('email_enabled', site=site):
        enable_email()
    publisher = DulcineaPublisher(config=config)
    publisher.log("SCGI server for %s started (pid %d)" %(site, os.getpid()))

    # We have to commit the current transaction here, just in case there wasn't
    # an existing session manager object in the DB.  In the case,
    # get_session_manager() created a new session manager and added it to the
    # DB root, but then start_request() will call abort(), losing the
    # modification to the DB root.  The net result is that, without the
    # following commit, the session manager is never written to disk and
    # sessions are always immediately thrown away.
    local.get_connection().commit()

    return publisher


log_to(error_log)

if is_devel(site):
    max_children = 1 # faster for development
else:
    max_children = 5

max_children = get_config_value('max_children', site=site,
                                fallback=max_children)

pid = os.fork()
if pid == 0:
    pid = os.getpid()
    pidfile = open(pid_file_name, 'w')
    pidfile.write(str(pid))
    pidfile.close()
    try:
        run_scgi(create_publisher,
                 port=port,
                 max_children=max_children,
                 script_name=get_base_path())
    finally:
        # grandchildren get here too, don't let them unlink the pid
        if pid == os.getpid():
            try:
                os.unlink(pid_file_name)
            except OSError:
                pass
