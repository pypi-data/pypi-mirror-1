"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/demo/proto/__init__.py $
$Id: __init__.py 27139 2005-08-02 14:38:48Z dbinger $
"""
from qpy.compile import compile_qpy_files
compile_qpy_files(__path__[0])

from qp.sites.proto.slash import SitePublisher, SiteRootDirectory
used = [SitePublisher, SiteRootDirectory]


