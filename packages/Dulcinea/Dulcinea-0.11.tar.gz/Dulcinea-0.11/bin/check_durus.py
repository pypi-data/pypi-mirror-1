#!/usr/bin/env python
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/dulcinea/bin/check_durus.py $
$Id: check_durus.py 27353 2005-09-09 20:49:33Z dbinger $
"""
from dulcinea.spec import get_spec_problems, get_specs, get_spec_doc
from durus.client_storage import ClientStorage
from durus.connection import Connection
from durus.file_storage import FileStorage
from durus.serialize import ObjectWriter, pack_record
from durus.storage import gen_oid_class, get_reference_index
from durus.storage_server import DEFAULT_PORT, DEFAULT_HOST
from sets import Set

class ObjectLocator:

    def __init__(self, connection):
        self.connection = connection
        self.reference_index = get_reference_index(connection.get_storage())

    def where_is(self, obj):
        root = self.connection.get_root()
        def locate(obj, seen):
            if len(seen) > 50:
                return '...'
            if obj is root:
                return 'root'
            oid = obj._p_oid
            for referring_oid in self.reference_index[oid]:
                if referring_oid not in seen:
                    seen.add(referring_oid)
                    break
            else:
                return repr(obj) # give up
            referring = self.connection.get(referring_oid)
            ref = locate(referring, seen)
            try:
                vars(referring)
            except TypeError:
                print repr(referring)
                print referring.__dict__
                raise
            for key, value in vars(referring).iteritems():
                if obj is value:
                    return "%s.%s" % (ref, key)
                try:
                    for k, v in value.iteritems():
                        if obj is v:
                            return "%s[%r]" % (ref, k)
                except AttributeError:
                    pass
                try:
                    for k, v in enumerate(value):
                        if obj is v:
                            return "%s[%r]" % (ref, k)
                except TypeError:
                    pass
            return '%s ... ' % ref
        return locate(obj, Set())

def gen_class_name_oids(storage):
    oids_by_class_name = {}
    for oid, class_name in gen_oid_class(storage):
        oids_by_class_name.setdefault(class_name, []).append(oid)
    class_name_oids = oids_by_class_name.items()
    class_name_oids.sort()
    for item in class_name_oids:
        yield item

def format_specs(klass):
    if klass.__bases__:
        bases = '(%s):' % ', '.join([b.__name__ for b in klass.__bases__])
    else:
        bases = ":"
    s = "class %s%s\n    " % (klass.__name__, bases)
    s += get_spec_doc(klass).replace('\n', '\n    ') or 'pass'
    s += "\n\n"
    return s

def check_durus(file, host, port, schema, klasses):
    if file:
        storage = FileStorage(file, readonly=True)
    else:
        storage = ClientStorage(host=host, port=port)
    connection = Connection(storage)
    where_is = ObjectLocator(connection).where_is
    if schema:
        schema_output = open(schema, 'w')
        written = Set()
    num_instances_checked = 0
    get_state = ObjectWriter(connection).get_state
    def get_size(obj):
        state, refs = get_state(obj)
        return len(pack_record(obj._p_oid, state, refs)) + 4
    total_size = 0
    print "%7s %-35s %7s %7s %7s %12s" % (
        "Count",
        "Class",
        "Min",
        "Max",
        "Ave",
        "Sum")
    for class_name, oids in gen_class_name_oids(storage):
        if klasses and class_name not in klasses:
            continue
        sizes = []
        print "%7s %-35s" % (len(oids), class_name),
        for oid in oids:
            obj = connection.get(oid)
            sizes.append(get_size(obj))
            specs = get_specs(obj)
            if schema and obj.__class__ not in written:
                written.add(obj.__class__)
                schema_output.write(format_specs(obj.__class__))
            num_instances_checked += 1
            problems = get_spec_problems(obj, specs=specs)
            if problems:
                print
                print where_is(obj)
                for problem in problems:
                    for line in problem.splitlines():
                        if len(line) > 200:
                            line = line[:200] + ' ...'
                        print ' ', line
                break
            obj._p_set_status_ghost()
        total = sum(sizes)
        total_size += total
        print "%7s %7s %7s %12s" % (
            min(sizes),
            max(sizes),
            total/len(oids),
            total)
    print
    print 'Number of instances checked:', num_instances_checked
    print 'Total object record size:', total_size


def check_durus_main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.set_description("Searches for spec anomolies in a durus database.")
    parser.add_option(
        '--file', dest="file", default=None,
        help="If this is not given, the storage is through a Durus server.")
    parser.add_option(
        '--port', dest="port", default=DEFAULT_PORT,
        type="int",
        help="Port the server is on. (default=%s)" % DEFAULT_PORT)
    parser.add_option(
        '--host', dest="host", default=DEFAULT_HOST,
        help="Host of the server. (default=%s)" % DEFAULT_HOST)
    parser.add_option(
        '--schema', dest="schema", default=None,
        help="If given, a schema will be written to this file")
    parser.add_option(
        '--class', dest="classes", default=[], action="append",
        help="If given, limit study to this class.")
    (options, args) = parser.parse_args()
    check_durus(options.file, options.host, options.port, options.schema,
                options.classes)

if __name__ == '__main__':
    check_durus_main()

