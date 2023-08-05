"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/lib/database.py $
$Id: database.py 27373 2005-09-13 14:07:30Z dbinger $

Provides the ObjectDatabase class.
"""
from durus.connection import Connection
from durus.file_storage import TempFileStorage
import sys, os

class ObjectDatabase:

    """Class used to initialize, access, and close a Durus DB containing a set
    of root objects.
    
    NOTE: Care must be taken to ensure that only one instance exists for each
    Durus database.

    Instance attributes:
      _dbspec : string
        the connection specification for this database
      _current_root_accessors : [str]
      storage : durus.connection.Storage
      connection : durus.connection.Connection
      root : any
    """

    def __init__ (self):
        self._dbspec = None
        self.storage = None
        self.connection = None
        self.root = None
        self._current_root_accessors = []

    def open(self, dbspec):
        assert self.root is None, 'database already open'
        self._dbspec = dbspec
        if dbspec.find(":") != -1:
            try:
                (storage_type, args) = dbspec.split(":")
            except ValueError:
                raise ValueError, ("dbspec may have at most one "
                                   "colon: '%s' invalid" % dbspec)
            args = tuple(args.split(","))
        else:
            storage_type = dbspec
            args = ()

        if storage_type == "file":
            (filename,) = args
            self.connection = self._open_file(filename)

        elif storage_type == "client":
            try:
                host, port = args
                port = int(port)
            except ValueError:
                raise ValueError("invalid dbspec: must be "
                                 "'client:<host>,<port>'" % dbspec)
            self.connection = self._open_client((host, port))

        elif storage_type == "empty":
            # leave database and connection as None
            self.storage = TempFileStorage()
            self.connection = Connection(self.storage)
            self.root = {}

        else:
            raise ValueError, "invalid storage type '%s'" % storage_type

        if self.connection is not None:
            self.root = self.connection.get_root()

        self.update_root_accessors()

    def close(self):
        "Close the database connection"
        self._dbspec = None
        self.connection = None
        self.storage = None
        self.root = None

    def get_storage(self):
        return self.storage

    def get_connection(self):
        return self.connection

    def get_root(self):
        return self.root

    def pack(self):
        self.database.pack()

    def _open_file(self, filename):
        """Open 'filename' as a FileStorage, and then open a connection
        around that.  Return a (database, connection) tuple containing the
        DB instance and the Connection instance that results from calling
        its 'open()' method."""

        from durus.file_storage import FileStorage
        created = (not os.path.isfile(filename))
        self.storage = FileStorage(filename)
        if created:
            os.chmod(filename, 0664)            # ensure group writeable
        return Connection(self.storage)

    def _open_client(self, location):
        """Open 'location' (a (hostname, port_number) tuple) as a 
        ClientStorage, and then open a connection around that.  Return
        a (database, connection) tuple."""

        host, port = location
        if host == "":
            # If the specified hostname is the empty string, then
            # 'localhost' is used.
            location = ('localhost', port)

        from durus.client_storage import ClientStorage
        self.storage = ClientStorage(port=port, host=host)
        return Connection(self.storage)

    def get_root_object(self, name):
        assert self.root is not None, "database not initialized"
        if not self.root.has_key(name):
            raise ValueError, "invalid database root '%s'" % name
        return self.root[name]

    def _add_root_accessor(self, name):
        assert not hasattr(self, name)
        setattr(self, name, self.root[name])
        self._current_root_accessors.append(name)

    def init_root(self, name, modulename, klassname):
        __import__(modulename)
        module = sys.modules[modulename]
        klass = getattr(module, klassname)
        assert name not in self.root.keys(), name
        self.root[name] = klass()
        self._add_root_accessor(name)

    def update_root_accessors(self):
        for name in self._current_root_accessors:
            if hasattr(self, name):
                delattr(self, name)
        for name in self.root.keys():
            self._add_root_accessor(name)

    def get_root_names(self):
        return self.root.keys()

    def __iter__(self):
        """
        Yield the objects.
        This works best with a FileStorage.
        """
        for oid, record in self.storage.gen_oid_record():
            yield self.connection[oid]

