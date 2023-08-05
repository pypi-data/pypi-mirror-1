#!/usr/bin/env python
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/lib/test/utest_util.py $
$Id: utest_util.py 26453 2005-04-01 02:15:29Z dbinger $
"""
from qp.lib.util import import_object
from sancho.utest import UTest

class Test(UTest):

    def check_import_object(self):
        import sys
        assert sys is import_object('sys')
        assert UTest is import_object('sancho.utest.UTest')

if __name__ == '__main__':
    Test()
