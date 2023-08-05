"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/stored_file.py $
$Id: stored_file.py 27535 2005-10-11 15:47:38Z dbinger $

Store a file in the filesystem.
"""
import os, grp
import errno
from datetime import datetime
from quixote.util import randbytes
from dulcinea.site_util import get_config_value
from dulcinea.spec import spec, specify, add_getters_and_setters, either, string
from dulcinea.base import DulcineaPersistent
from dulcinea.user import DulcineaUser
from string import lowercase, digits

ALLOWABLE_SPECIAL_CHARS = "-_.@"

def path_check(path):
    """(path:string) -> string | None

    Return a lower-case and normalized version of the 'path' after
    checking for allowable characters.
    Return None if path has '..' or any special characters
    other than what's in string.lowercase, string.digits, and
    the ALLOWABLE_SPECIAL_CHARS string
    """
    if '..' in path:
        return None
    path = path.lower()
    for letter in path:
        if (letter != '/' and letter not in lowercase and
            letter not in digits and
            letter not in ALLOWABLE_SPECIAL_CHARS):
            return None
    return path

MIME_TYPES = [("image/gif", "GIF image"),
              ("image/jpeg", "JPEG image"),
              ("image/png", "PNG image"),
              ("image/tiff", "TIFF image"),
              ("image/x-ms-bmp", "BMP image"),
              ("text/plain", "plain text"),
              ("text/html", "HTML text"),
              ("text/rtf", "richtext document"),
              ("application/pdf", "PDF document"),
              ("application/msword", "Word document"),
              ("application/vnd.ms-powerpoint", "PowerPoint document"),
              ("application/vnd.ms-excel", "Excel document"),
              ("application/postscript", "PostScript file"),
              ("application/octet-stream", "Binary data"),
              ("application/x-gtar", "gzipped tar file"),
              ("application/x-gzip", "gzipped file"),
              ("application/x-tar", "tar file"),
              ("application/zip", "zip file"),
              ]

def get_file_store():
    return get_config_value('file_store', '/var/tmp')


class StoredFile (DulcineaPersistent):
    """Class for reading from or writing to a stored file

    A StoredFile is a wrapper around a file in a place in the
    filesystem known as the 'file_store'.

    StoredFiles can be instantiated with a fresh source file to move a new
    file into the file_store, or instantiated by referencing an existing
    file in the file_store.
    """
    path_is = spec(
        string,
        "Path to the physical file containing the stored file's data.")
    filename_is = spec(
        string,
        "Filename to use when downloading this file")
    mime_type_is = spec(
        either(None, *[pair[0] for pair in MIME_TYPES]),
        "MIME type of the contents of this file.")
    description_is = spec(
        (string, None),
        "Description of this file.")
    owner_is = spec(
        (DulcineaUser, None),
        "The file's owner")
    date_is = spec(
        datetime,
        "timestamp")

    def __init__(self, path):
        path = os.path.normpath(path)
        self.path = path_check(path)
        assert self.path, 'Bad name: %r' % path
        specify(self,
                description=None,
                owner=None,
                date=datetime.now(),
                filename=os.path.basename(self.path),
                mime_type=None)

    def get_id(self):
        return self.path.replace('/', '')

    def open(self):
        """() -> file
        Returns a Python file object opened for reading.  This can be used to
        read the file's content.
        """
        return open(self.get_full_path())

    def chgrp(self, grp_id):
        """(grp_id : string | int)
        Change the category ownership of this file to the specified ID.
        """
        if isinstance(grp_id, string):
            grnam, grpass, gid, grmembers = grp.getgrnam(grp_id)
            grp_id = gid
        os.chown(self.get_full_path(), -1, grp_id)

    def set_mime_type(self, mime_type):
        """(mime_type:string)
        Sets the MIME type for the file.
        """
        # Check there's a single '/' in the MIME type
        if mime_type.count('/') != 1:
            raise ValueError, "Invalid MIME type %r" % mime_type
        self.mime_type = mime_type

    def get_size(self):
        """() -> int
        Return the size of the file, measured in bytes, or None if
        the file doesn't exist.
        """
        path = self.get_full_path()
        if not os.path.exists(path):
            return None
        stats = os.stat(path)
        return stats.st_size

    def get_full_path(self):
        """() -> string
        """
        return os.path.join(get_file_store(), self.path)

    def has_manage_access(self, user):
        return (user is self.owner or user.is_admin())

add_getters_and_setters(StoredFile)


def get_random_path():
    h = randbytes(6)
    return '%s/%s/%s' % (h[-1], h[-3:-1], h[:-3])

def new_file(fp):
    root_directory = get_file_store()
    flags = os.O_WRONLY|os.O_CREAT|os.O_EXCL
    try:
        flags |= os.O_BINARY    # for Windows
    except AttributeError:
        pass
    for attempt in xrange(1000):
        path = get_random_path()
        full_path = os.path.join(root_directory, path)
        destdir = os.path.dirname(full_path)
        if not os.path.exists(destdir):
            os.makedirs(destdir, mode=0775)
        try:
            fd = os.open(full_path, flags)
        except OSError, exc:
            if exc.errno == errno.EEXIST:
                pass # destination exists, retry
            else:
                raise # some other error
        else:
            break
    else:
        raise RuntimeError("Unable to make temp file.")
    dest_fp = os.fdopen(fd, "wb")
    while 1:
        chunk = fp.read(10000)
        if not chunk:
            break
        dest_fp.write(chunk)
    fp.close()
    dest_fp.close()
    return StoredFile(path)
