#!/usr/bin/env python
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/bin/expire_session.py $
$Id: expire_session.py 27591 2005-10-18 17:14:41Z dbinger $

Delete sessions whose access time is older than the age passed in as an
argument (in hours).

This script is meant to be run by cron.
"""

import sys, os
from dulcinea import local
from time import time

def main (prog, args):
    usage = "usage: %s [site] [expire time]" % prog

    if len(args) != 2:
        sys.exit(usage)

    site = os.environ['SITE'] = args[0]
    expiration_hours = float(args[1])

    local.open_database()
    session_manager = local.get_session_manager()
    now = time()
    limit = expiration_hours * 3600
    for key in session_manager.keys():
        if session_manager.get(key).get_access_age(_now=now) > limit:
            del session_manager[key]
    local.get_connection().commit()

if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
