#!/www/python/bin/python

"""$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/bin/start-durus.py $
$Id: start-durus.py 26324 2005-03-09 21:32:54Z dbinger $

Script invoked by the site command to start and stop Durus storage server.
"""

import sys, os
from dulcinea.site_util import get_pid_file_name, parse_address, \
     get_config_value, ensure_uid_gid_not_root, is_local
from durus import run_durus, storage_server
ensure_uid_gid_not_root()
site = sys.argv[1]
action = sys.argv[2]

pid_file_name = get_pid_file_name('durus', site)
ip, port = parse_address(get_config_value('durus_address', site=site))
assert is_local(get_config_value('durus_address', site=site))

db = os.path.join(
    get_config_value('var_directory', site=site), '%s.durus' % site)

site_log_dir = os.path.join(get_config_value('log_directory', site=site),
                            site)
durus_log = os.path.join(site_log_dir, 'durus.log')

durus = get_config_value('durus', fallback=run_durus.__file__, site=site)
logginglevel = get_config_value('logginglevel', fallback=20, site=site)

if durus.endswith('c'):
    durus = durus[:-1]

args =  [sys.executable,
         durus,
         '--host', ip,
         '--port', str(port),
         '--file', db,
         '--logginglevel', str(logginglevel),
         '--logfile', durus_log]
if action == 'stop':
    args.append('--stop')
elif action != 'start':
    raise SystemExit, 'action must be "start" or "stop"'

pid = os.fork()
if pid == 0:
    os.execve(args[0], args, {})
else:
    if action == 'start':
        pid_file = open(pid_file_name, 'w')
        pid_file.write("%s" % pid)
        pid_file.close()
        storage_server.wait_for_server(ip, port)
