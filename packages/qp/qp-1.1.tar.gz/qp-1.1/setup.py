"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/setup.py $
$Id: setup.py 27641 2005-10-29 14:49:07Z dbinger $
"""
import sys
from os import curdir, symlink
from os.path import join, exists
from distutils.core import setup
from distutils.extension import Extension
from shutil import copytree
try:
    from qpy.setup import qpy_build_py
except ImportError:
    print "Please install Qpy first."
    raise SystemExit

Passfd = Extension(name="qp.hub.passfd", sources=['hub/passfd.c'])

if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'install_sites_link':
        sites_directory = sys.argv[2]
        if not exists(sites_directory):
            print sites_directory, 'does not exist.'
        if not exists(join(sites_directory, '__init__.py')):
            print sites_directory, 'needs an __init__.py.'
        import qp
        symlink(sites_directory, join(qp.__path__[0], 'sites'))
    elif len(sys.argv) == 3 and sys.argv[1] == 'install_demo_sites':
        sites_directory = sys.argv[2]
        if exists(sites_directory):
            print sites_directory, 'already exists.'
        copytree('demo', sites_directory)
        f = open(join(sites_directory, "__init__.py"), "w")
        f.close()
    else:
        setup(name="qp",
              version="1.1",
              author="CNRI",
              author_email="webmaster@mems-exchange.org",
              url="http://www.mems-exchange.org/software/qp/",
              package_dir=dict(qp=curdir),
              scripts=['bin/qp', 'bin/qpcensus.py'],
              license="See LICENSE.txt",
              packages=['qp',
                        'qp.http',
                        'qp.hub',
                        'qp.pub',
                        'qp.fill',
                        'qp.lib',
                        'qp.mail',
                        ],
              ext_modules=[Passfd],
              description="A web-application framework.",
              cmdclass= {'build_py': qpy_build_py},
              long_description=(
            "QP is a package for defining and running multiple web "
            "applications based on Durus for persistence, standard persistent "
            "Session and User classes, easy interactive database sessions, "
            "qpy for assembling html, and Quixote2-style forms and path "
            "traversal.  ")
              )
