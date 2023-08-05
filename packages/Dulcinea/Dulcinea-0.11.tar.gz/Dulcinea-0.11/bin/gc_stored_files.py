#!/usr/bin/env python
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/bin/gc_stored_files.py $
$Id: gc_stored_files.py 26302 2005-03-08 14:06:55Z dbinger $

Delete files that are not referenced by StoredFile instances.
"""

import sys, os, glob, time
from durus.storage import gen_oid_class
from durus.connection import Connection
from durus.file_storage import FileStorage
from dulcinea.site_util import get_config_value

# new files are not deleted since someone could be in the process of
# uploading them or attaching them in another transaction
MIN_AGE = 60*60*24

size = 0

def maybe_remove(filename):
    global size
    if (time.time() - os.stat(filename).st_mtime) > MIN_AGE:
        print filename
        size += os.stat(filename).st_size
        os.unlink(filename)


def main (prog, args):
    usage = "usage: %s <dbfile>" % prog

    if len(args) != 1:
        sys.exit(usage)

    connection = Connection(FileStorage(args[0], readonly=True))
    used = {}
    for oid, class_name in gen_oid_class(connection.storage, 'StoredFile'):
        s = connection.get(oid)
        used[s.full_path] = 1
    now = time.time()
    root_directory = get_config_value('file_store')
    print 'root_directory', root_directory
    for filename in glob.glob(os.path.join(root_directory, '?/??/*')):
        if filename not in used:
            maybe_remove(filename)
    for filename in glob.glob(os.path.join(root_directory, 'tmp/upload.*')):
        maybe_remove(filename)
    print size / (1024*1024), 'MB'

if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
