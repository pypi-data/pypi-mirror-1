#!/usr/bin/env python
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/bin/qpcensus.py $
$Id: qpcensus.py 27519 2005-10-05 22:14:49Z dbinger $
"""
from durus.connection import Connection
from durus.file_storage import FileStorage
from durus.storage import gen_oid_class, get_reference_index
from durus.serialize import ObjectWriter
from qp.lib.site import Site
from qp.lib.spec import get_spec_problems, get_specs, get_spec_doc

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
        return locate(obj, set())

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
        bases = '(%s):' % ', '.join(
            [b.__name__ for b in klass.__bases__])
    else:
        bases = ":"
    s = "class %s%s\n    " % (klass.__name__, bases)
    s += get_spec_doc(klass).replace('\n', '\n    ') or 'pass'
    s += "\n\n"
    return s

def check_durus(file, schema, klasses):
    storage = FileStorage(file, readonly=True)
    connection = Connection(storage)
    where_is = ObjectLocator(connection).where_is
    if schema:
        schema_output = open(schema, 'w')
        written = set()
    num_instances_checked = 0
    get_state = ObjectWriter(connection).get_state
    def get_size(obj):
        state, refs = get_state(obj)
        # 8 for tid, 4 for len of state, 4 for len of record, 8 for oid
        return len(state) + len(refs) + 24
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
    print

def check_durus_main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.set_description("Searches for spec anomolies in a durus database.")
    all_sites = Site.get_sites().keys()
    parser.add_option(
        '-s', '--site', dest='site', default=[], action='append',
        type='choice',
        choices=all_sites,
        help=("Check only the named site.  Default is all sites."))
    parser.add_option(
        '--file', dest="file", default=None,
        help="If this is given, check this file only.")
    parser.add_option(
        '--schema', dest="schema", default=None,
        help="If given, a schema will be written to this file")
    parser.add_option(
        '--class', dest="classes", default=[], action="append",
        help="If given, limit study to this class.")
    (options, args) = parser.parse_args()
    if options.file:
        check_durus(options.file, options.schema, options.classes)
    else:
        for name, site in Site.get_sites().items():
            if options.site and name not in options.site:
                continue
            print "%s:" % name
            check_durus(site.get_durus_file(), options.schema, options.classes)

if __name__ == '__main__':
    check_durus_main()

