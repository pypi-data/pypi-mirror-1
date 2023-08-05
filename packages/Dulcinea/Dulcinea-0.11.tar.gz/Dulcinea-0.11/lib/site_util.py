"""$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/site_util.py $
$Id: site_util.py 27538 2005-10-11 23:00:36Z rmasse $

Provides access to site configuration data.
"""

import sys, os, re, socket, errno
try:
    import site_config
except ImportError:
    if 'SITE' in os.environ:
        raise
    # No SITE is set, so we won't really be using a site_config.
    # Put 'site_config' in sys modules so that other site_config
    # imports don't raise ImportError.
    sys.modules['site_config'] = None

def get_config_value(name, fallback=None, site=None):
    """(name:string, fallback:any=None, site:string=None) -> any

    The site_config module must be provided so that
    site_config.config is a dictionary whose keys are the site
    identifiers for your sites, and whose values are dictionaries
    containing configuration variables for that site.

    Example site_config.py contents:
    
    toboso=dict(
        apache_version=2,
        httpd="/sw/sbin/httpd",
        administrator="You <webmaster@example.org>",
        allow_anonymous_registration="True",
        conf_directory="/tmp/toboso/conf",
        var_directory="/tmp/toboso/var",
        log_directory="/tmp/toboso/logs",
        sites_directory="/tmp/toboso/sites",
        start_script_directory="/sw/bin",
        daemon_uid="web",
        servername="127.0.0.1",
        # comment out the next line if apache should not be started.
        http_address="127.0.0.1:8000",
        #https_address="0:443",
        scgi_address="localhost:1984",
        durus_address="localhost:2001",
        root_namespace="toboso.ui.qslash",
        root_exports=['_q_index', 'css', 'user', 'admin',
                      'login', 'logout', 'my'],
        cache_size=5000)
    config={"toboso" : toboso}
    """
    if site is None:
        site = os.environ.get('SITE', None)
    if site is None and len(site_config.config) == 1:
        site = site_config.config.keys()[0]
    return site_config.config[site].get(name, fallback)

def list_sites():
    return site_config.config.keys()

def get_hostname():
    return socket.gethostbyname_ex(socket.gethostname())[0]

def is_staging(site=None):
    return get_config_value('mode', site=site) == 'staging'

def is_live(site=None):
    return get_config_value('mode', site=site) == 'live'

def is_devel(site=None):
    return not (is_live(site) or is_staging(site))

def any_live_sites():
    """Returns True if any sites are live."""
    for site in list_sites():
        if is_live(site):
            return True
    else:
        return False

def any_staging_sites():
    """Returns True if any sites are staging."""
    for site in list_sites():
        if is_staging(site):
            return True
    else:
        return False

def _get_local_interfaces():
    """Return a list of local IP addresses for this machine."""
    # Currently a Linux specific hack. :-(
    addrs = []
    p = os.popen("/sbin/ifconfig")
    for line in p.readlines():
        m = re.search(r'inet (addr:)?(\d+\.\d+\.\d+\.\d+)', line)
        if m:
            addrs.append(m.group(2))
    return addrs

local_interfaces = _get_local_interfaces()

def parse_address(s):
    ip, port = s.strip().split(':')
    if not ip[0].isdigit():
        # not an IP address, resolve it
        ip = socket.gethostbyname(ip)
    return ip, port and int(port)

def is_local(address):
    ip, port = parse_address(address)
    return ip in local_interfaces

def get_dbspec(site=None):
    durus_address = get_config_value('durus_address', site=site)
    if durus_address:
        return 'client:%s,%s' % parse_address(durus_address)
    return None

def get_root_exports(site=None):
    return get_config_value('root_exports', fallback=[], site=site)

def get_scgi_off(site=None):
    return get_config_value('scgi_off', fallback=[], site=site)

def get_cache_size(site=None, default=10000):
    return int(get_config_value('cache_size', fallback=default, site=site))

_email_pat = re.compile(r'^(.*)\s+<(.*)>$')

def get_administrator_address(site=None):
    administrator = get_config_value('administrator', fallback='', site=site)
    m = _email_pat.match(administrator)
    if not m:
        raise ValueError, '"administrator" in site.conf missing real name'
    realname = m.group(1)
    email = m.group(2)
    return (email, realname)

_email_enabled = False

def enable_email():
    global _email_enabled
    _email_enabled = True

def is_email_enabled():
    """Return true if email should be sent.  This is false for various sites
    and also when tests are being run (for example).
    """
    return _email_enabled

def get_base_path(site=None):
    return get_config_value('base_path', fallback='', site=site)

def get_pid_file_name(daemon, site=None):
    name = '%s.pid' % daemon
    if site:
        name = site + '-' + name
    pid_dir = get_config_value('var_directory', site=site)
    return os.path.join(pid_dir, name)

def write_pid_file(daemon, site=None):
    file = open(get_pid_file_name(daemon, site), 'w')
    file.write(str(os.getpid()))
    file.close()

def change_uid_gid(uid, gid=None):
    "Try to change UID and GID to the provided values"
    # This will only work if this script is run by root.
    # Try to convert uid and gid to integers, in case they're numeric
    import pwd, grp
    try:
        uid = int(uid)
        default_grp = pwd.getpwuid(uid)[3]
    except ValueError:
        uid, default_grp = pwd.getpwnam(uid)[2:4]

    if gid is None:
        gid = default_grp
    else:
        try:
            gid = int(gid)
        except ValueError:
            gid = grp.getgrnam(gid)[2]
    os.setgid(gid)
    os.setuid(uid)

def ensure_uid_gid_not_root():
    if os.getuid() == 0:
        uid = get_config_value('daemon_uid')
        change_uid_gid(uid)
    assert os.getuid() != 0

def log_to(log_file_name):
    log = open(log_file_name, "a", 1)
    os.dup2(log.fileno(), 1)
    os.dup2(log.fileno(), 2)
    os.close(0)

def fetch_database(site, destination=None, source_file=None):
    """
    Pull a copy of the live database for site to the local
    machine using scp.
    If destination is given, it is the name of local file.
    If source file is given, it is a file name
    in the var_directory of the remote host.
    If neither of the keyword arguments are provided, the
    database is pulled from the standard place on the remote machine
    and put in the standard place on the local machine.
    The standard place is <site>.durus in the var_directory.
    """
    remote = get_config_value('live_db', site=site)
    if not destination:
        var_directory = get_config_value('var_directory', site=site)
        destination = os.path.join(var_directory, "%s.durus" % site)
    if remote:
        cmd = 'scp -C -p %s %s' % (remote, destination)
        print cmd
        os.system(cmd)
    return 'file:' + destination

def import_class(name):
    i = name.rfind('.')
    module_name = name[:i]
    class_name = name[i+1:]
    __import__(module_name)
    return getattr(sys.modules[module_name], class_name)

def get_root_directory(site=None):
    root_directory_name = get_config_value('root_directory', site=site)
    return import_class(root_directory_name)()

def get_docroot(site=None):
    if site is None:
        site = os.environ.get('SITE', None)
    sites_directory = get_config_value('sites_directory', site=site,
                                       fallback='')
    return '%s/%s/docroot' % (sites_directory, site)

class SiteModule:
    """
    A module-like object that provides access to site-specific variants
    of a module, delaying the import of the site-specific variants until
    they are actually needed.

    This is used for dulcinea.local and dulcinea.local_ui.

    Accessing attributes of an instance of this class requires that the
    SITE environment variable is set to the name of a package that
    contains the site-specific module.
    """
    def __init__(self, module_name):
        self._loaded = False
        self.__name__ = module_name

    def __getattr__(self, name):
        if not self._loaded and not name.startswith('_'):
            site = os.environ.get('SITE', 'dulcinea.test')
            module_name = site + '.' + self.__name__
            __import__(module_name)
            for n, v in vars(sys.modules[module_name]).items():
                if not n.startswith('_'):
                    setattr(self, n, v)
            self._loaded = True
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError, name


def is_running(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except OSError, e:
        if e.errno == errno.EPERM:
            return True
    return False
