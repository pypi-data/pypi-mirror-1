#!/usr/bin/env python
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/bin/start-apache.py $
$Id: start-apache.py 27203 2005-08-12 17:45:18Z dbinger $

Script invoked by site command to start apache.
"""

import os
from dulcinea.site_util import get_config_value, get_hostname, \
     get_root_exports, get_pid_file_name, get_administrator_address,\
     parse_address, any_live_sites, any_staging_sites, list_sites, \
     is_live, is_staging, get_base_path, get_docroot
from dulcinea.site_util import get_scgi_off

default_site = list_sites()[0]
sites_directory = get_config_value('sites_directory',
                                   site=default_site,
                                   fallback='')
var_directory = get_config_value('var_directory',
                                 site=default_site,
                                 fallback='')
httpd_conf_name = os.path.join(var_directory, 'generated-httpd.conf')

httpd_conf = open(httpd_conf_name, 'w')

def w (*s):
    httpd_conf.write(' '.join(map(str, s)) + '\n')

def include_site_conf (include_file, site):
    file_name = os.path.join(sites_directory,
                             site,
                             'conf',
                             include_file)
    if os.path.exists(file_name):
        w('Include', file_name)

def include_global_conf (conf_file_name):
    full_name = os.path.join(get_config_value('conf_directory',
                                              site=default_site),
                             'apache',
                             conf_file_name)
    if not os.path.exists(full_name):
        raise SystemExit, 'missing configuration file %r' % full_name
    w('Include', full_name)

def is_apache2():
    return str(get_config_value('apache_version', '1.3',
                                site=default_site)).startswith('2')

def common (site):
    w('ServerName %s' % (get_config_value('servername', site=site) or
                         get_hostname()))
    scgi_address = get_config_value('scgi_address', site=site)
    if scgi_address:
        exports = list(get_root_exports(site))
        if exports:
            exports.sort()
            if '' in exports: # dynamic root
                exports.append('$')
                exports.remove('')
            w('<LocationMatch "^%s/(%s)($|/.*)">' % (get_base_path(site),
                                                     '|'.join(exports)))
            if is_apache2():
                # the apache2 mod_scgi.c requires a slightly different format.
                w('    SCGIServer %s:%s' % parse_address(scgi_address))
            else:
                w('    SCGIServer %s %s' % parse_address(scgi_address))
            w('    SCGIHandler On')
            w('</LocationMatch>')
        else:
            host, port = parse_address(scgi_address)
            base_path = get_base_path(site)
            w('SCGIMount %s %s:%s' % (base_path or '/', host, port))
            for name in get_scgi_off(site):
                w('<LocationMatch "^%s%s">' % (base_path, name))
                w('    SCGIHandler off')
                w('</LocationMatch>')
    include_site_conf('apache-common.conf', site)

w('# Generated. Edit site.conf and/or start_apache.py to change.')
w('ServerAdmin', get_administrator_address(site=default_site)[0])
w('User', get_config_value('daemon_uid', site=default_site))
w('PidFile', get_pid_file_name('apache', site=default_site))

any_live = any_live_sites()
any_staging = any_staging_sites()
assert not (any_live and any_staging)

ports = {}
for site in list_sites():
    for option in ('http_address', 'https_address'):
        option_value = get_config_value(option, site=site)
        if option_value:
            ip, port = parse_address(option_value)
            ports[port]=1
for port in ports:
    w('Listen', port)


if not any_live:
    # Directives if not live for any site.
    w('CoreDumpDirectory', get_config_value('var_directory', site=default_site))
    w('LogLevel debug')

include_global_conf('apache-global.conf')

print
for site in list_sites():
    if not get_config_value('http_address', site=site):
        continue
    if (any_live and not is_live(site)):
        # In live mode, skip sections that aren't live 
        continue
    if (any_staging and not is_staging(site)):
        # In staging mode, skip sections that aren't staging
        continue

    docroot = get_docroot(site)
    if not os.path.exists(docroot):
        raise SystemExit, 'docroot directory %r does not exist' % docroot
    host_iface = get_config_value('http_address', site=site)
    host_ssl_iface = get_config_value('https_address', site=site)

    w('\n<VirtualHost %s>' % host_iface, '# %s http' % site)
    print ' ', site, host_iface,
    w('DocumentRoot ' + docroot)
    common(site)
    include_site_conf('apache-http.conf', site)
    w('</VirtualHost>')
    if host_ssl_iface:
        print host_ssl_iface,
        w('\n<VirtualHost %s>' % host_ssl_iface,
          '# %s https' % site)
        w('DocumentRoot ' + docroot)
        common(site)
        w('SSLEngine on')
        w('SSLOptions +StdEnvVars')
        ssl_cert = get_config_value('ssl_certificate', site=site)
        ssl_cert_key = ssl_cert.replace('.crt', '.key')
        w('SSLCertificateFile %s' % ssl_cert)
        w('SSLCertificateKeyFile %s' % ssl_cert_key)
        w('</VirtualHost>')
    if is_live(site):
        print 'live',
        include_site_conf('apache-live.conf', site)
    print

httpd_conf.close()

httpd = get_config_value('httpd', site=default_site)
print "  " + httpd + " -f " + httpd_conf_name
os.execv(httpd, [httpd, '-f', httpd_conf_name])

