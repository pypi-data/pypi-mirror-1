"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/lib/test/utest_keep.py $
$Id: utest_keep.py 27644 2005-10-29 20:54:06Z dbinger $
"""
from durus.btree import BTree
from durus.persistent import Persistent
from qp.lib.keep import Keyed, Keep, Stamped, stamp_sorted, reverse_stamp_sorted
from sancho.utest import UTest

class Test(UTest):

    def check_keep(self):
        class PKeep(Keep, Persistent):
            pass
        x = PKeep(value_spec=Keyed)
        y = Keyed()
        z = Keyed()
        x.add(y)
        x.add(z)
        assert list(x.iterkeys()) == [y.get_key(), z.get_key()]
        assert list(x.itervalues()) == [y, z]
        assert list(x.iteritems()) == zip(x.iterkeys(), x.itervalues())
        assert isinstance(x.get_mapping(), BTree)
        assert x.get(y.get_key()) is y
        assert x.get(None, 23) == 23
        try:
            x.add(None)
            assert 0
        except TypeError:
            pass
        bad = Keyed()
        bad.badattr = 1
        try:
            x.add(bad)
            assert 0
        except TypeError:
            pass

    def check_stamped(self):
        x = Stamped()
        y = Stamped()
        assert stamp_sorted([x, y]) == [x, y]
        assert reverse_stamp_sorted([x, y]) == [y, x]
        assert x.get_stamp() < y.get_stamp()


if __name__ == '__main__':
    Test()
