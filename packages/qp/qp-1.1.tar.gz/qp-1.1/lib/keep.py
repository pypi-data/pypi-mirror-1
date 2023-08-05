"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/lib/keep.py $
$Id: keep.py 27638 2005-10-28 22:54:30Z rmasse $
"""
from datetime import datetime
from durus.btree import BTree
from durus.persistent import Persistent
from durus.persistent_dict import PersistentDict
from qp.lib.spec import require, get_spec_problems, anything, mapping, spec
from qp.lib.spec import either

class Keyed (object):
    """
    An item with an int key used as a key in an Keep.
    Note that the key attribute is set when the item is put in the Keep,
    so there is no set_key() method.
    """
    key_is = int

    def __init__(self):
        self.key = None

    def get_key(self):
        return self.key


class Counter (Persistent):

    """
    Keep a key counter.  This may change often, so we keep this
    isolated here instead of on the Keep itself.
    """
    next_available_is = int

    def __init__(self):
        self.next_available = 1

    def next(self):
        result = self.next_available
        self.next_available = self.next_available + 1
        return result


class Keep (object):
    """
    A simple database that stores a mapping of objects by key.
    """
    value_spec_is = spec(
        anything,
        "Specifies the type of values allowed in mapping")
    mapping_is = mapping({int:Keyed}, either(PersistentDict, BTree))
    key_counter_is = Counter

    def __init__(self, value_spec=Keyed):
        assert isinstance(self, Persistent)
        self.mapping = BTree()
        self.key_counter = Counter()
        self.value_spec = value_spec

    def get_mapping(self):
        return self.mapping

    def get(self, key, default=None):
        return self.mapping.get(key, default)

    def itervalues(self):
        for value in self.mapping.itervalues():
            yield value

    def iterkeys(self):
        for key in self.mapping.iterkeys():
            yield key

    def iteritems(self):
        for item in self.mapping.iteritems():
            yield item

    def add(self, value):
        require(value, self.value_spec)
        assert value.key is None
        value.key = self.key_counter.next()
        if get_spec_problems(value):
            raise TypeError(''.join(get_spec_problems(value)))
        self.mapping[value.key] = value


class Stamped (object):

    stamp_is = datetime

    def __init__(self):
        self.set_stamp()

    def get_stamp(self):
        return self.stamp

    def set_stamp(self):
        self.stamp = datetime.utcnow()


def stamp_sorted(stamped_sequence):
    items = [(x.stamp, x) for x in stamped_sequence]
    items.sort()
    return [x for (stamp, x) in items]

def reverse_stamp_sorted(stamped_sequence):
    result = stamp_sorted(stamped_sequence)
    result.reverse()
    return result


