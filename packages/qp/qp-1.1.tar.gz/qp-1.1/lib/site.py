"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/lib/site.py $
$Id: site.py 27607 2005-10-19 23:55:56Z dbinger $
"""
from datetime import datetime
from durus.client_storage import ClientStorage
from durus.connection import Connection
from durus.file_storage import FileStorage
from durus.run_durus import stop_durus
from durus.storage_server import wait_for_server, StorageServer
from logging import StreamHandler, Formatter, getLogger
from os import listdir, fork, kill, getpid, unlink, system
from os import setuid, setgid, getuid
from os.path import join, isdir, exists
from qp.hub.web import run_web
from qp.lib.util import import_object
from qp.pub.common import get_publisher
from time import sleep
import errno, signal
import grp
import pwd
import qp.hub
import sys

class Site(object):

    sites_package_name = 'qp.sites'

    def __init__(self, name):
        """(name:str)
        Name is the name of the site, expected to be the name of the
        corresponding package in the sites module directory.
        """
        self.name = name

    def get_name(self):
        return self.name

    def get_sites(klass):
        """() -> {name:str : site:Site}
        Note that this is a method of the class.
        It returns an index of all of the installed sites.
        """
        sites_package= import_object(klass.sites_package_name)
        sites_directory = sites_package.__path__[0]
        return dict([(name, Site(name))
                     for name in listdir(sites_directory)
                     if (isdir(join(sites_directory, name))
                         and '.' not in name)])
    get_sites = classmethod(get_sites)

    def get_package_name(self):
        """() -> str
        The name of the package that defines this site.
        """
        return "%s.%s" % (self.sites_package_name, self.get_name())

    def get_package(self):
        """() -> module
        The package that defines this site.
        """
        return import_object(self.get_package_name())

    def get_package_directory(self):
        """() -> str
        The full path to the directory of this site package.
        """
        return self.get_package().__path__[0]

    def get_publisher_class(self):
        """() -> class
        Returns the publisher subclass defined for this site.
        """
        return self.get_package().SitePublisher

    def get_root_directory_class(self):
        """() -> class
        Returns the root directory class defined for this site.
        """
        return self.get_package().SiteRootDirectory

    def get_configuration(self):
        """() -> dict
        Returns the 'configuration' attribute of this site's publisher class.
        """
        return self.get_publisher_class().configuration

    def get(self, key, default=None):
        """
        Gets the value of a site configuration variable.
        """
        return self.get_configuration().get(key, default)

    def site_path(self, *rest):
        """
        Builds a path to something in the site module directory, by joining the arguments.
        """
        return join(self.get_package_directory(), *rest)

    def get_var_directory(self):
        """() -> str
        Get the directory where durus and pid files usually reside.
        """
        return self.get('var_directory') or self.site_path('var')

    def get_static_directory(self):
        """() -> str
        Get the directory where static content is expected.
        """
        return self.get('static_directory') or self.site_path('static')

    def get_durus_logginglevel(self):
        """() -> int
        Lower levels log more.
        """
        return self.get('durus_logginglevel', 20)

    def get_logfile(self):
        """() -> str
        The name of the file where the site logs events.
        """
        return (self.get('logfile') or
                join(self.get_var_directory(), '%s.log' % self.get_name()))

    def get_durus_file(self):
        """() -> str
        The name of the file containing the Durus database.
        """
        return (self.get('durus_file') or
                join(self.get_var_directory(),
                     '%s.durus' % self.get_name()))

    def get_banned(self):
        """() -> str
        The name of the file containing addresses for which access to the site
        should be denied.
        """
        return (self.get('banned') or
                join(self.get_var_directory(),
                     '%s.banned' % self.get_name()))

    def get_durus_address(self):
        """() -> (host:str, port:int)
        The address at which the Durus StorageServer listens.
        """
        return self.get('durus_address')

    def get_scgi_address(self):
        """() -> (host:str, port:int) | None
        The address at which the SCGI service listens.
        """
        return self.get('scgi_address')

    def get_http_address(self):
        """() -> (host:str, port:int) | None
        The address at which the HTTP service listens.
        """
        return self.get('http_address')

    def get_as_https_address(self):
        """() -> (host:str, port:int) | None
        The address at which the HTTP service listens and treats all connections
        as if they have been forwarded through an SSL tunnel.  The cgi
        environment for these connections has HTTP set to 'on', so the url
        scheme is treated as 'https'.
        """
        return self.get('as_https_address')

    def get_https_address(self):
        """() -> (host:str, port:int) | None
        The address at which the SSL tunnel or proxy accepts HTTPS requests.
        QP itself does not listen on this address.
        """
        return self.get('https_address')

    def get_web_addresses(self):
        """() -> [(host:str, port:int)*]
        Returns the addresses on on which the QP web server listens.
        """
        return [a for a in (self.get_scgi_address(),
                            self.get_http_address(),
                            self.get_as_https_address()) if a]


    def get_durus_pidfile(self):
        """() -> str
        The name of the file used to hold the process id of the running Durus
        StorageServer process.
        """
        return (self.get('durus_pidfile') or
                join(self.get_var_directory(),
                     '%s.durus.pid' % self.get_name()))

    def get_web_pidfile(self):
        """() -> str
        The name of the file used to hold the process id of the running QP web
        server process.
        """
        return (self.get('web_pidfile') or
                join(self.get_var_directory(),
                     '%s.web.pid' % self.get_name()))

    def is_live_pidfile(self, pidfile):
        """(pidfile:str) -> int | None
        Returns an int found in the named file, if there is one,
        and if there is a running process with that process id.
        Return None if no such process exists.
        """
        def read_pidfile(filename):
            if exists(filename):
                try:
                    return int(open(filename).read().strip())
                except (ValueError, IOError):
                    return None
            else:
                return None
        pid = read_pidfile(pidfile)
        if pid:
            try:
                kill(int(pid), 0)
                return pid
            except OSError, e:
                if e.errno == errno.EPERM:
                    return pid
        return None

    def is_durus_running(self):
        """() -> int | None
        Returns the pid of the Durus StorageServer, if it is running.
        """
        return self.is_live_pidfile(self.get_durus_pidfile())

    def is_web_running(self):
        """() -> int | None
        Returns the pid of the QP web server, if it is running.
        """
        return self.is_live_pidfile(self.get_web_pidfile())

    def get_max_children(self):
        """() -> int
        Returns the maximum number of child processes to be allowed for
        the QP web server.
        """
        return self.get('max_children', 5)

    def get_durus_cache_size(self):
        """() -> int
        The target number of loaded instances to keep in the Durus ClientStorage
        cache.
        """
        return self.get('durus_cache_size', 100000)

    def get_create_publisher(self):
        """() -> callable
        Return a function that can be called in a child process to create and
        initialize a publisher instance.
        """
        def create_publisher():
            log = open(self.get_logfile(), 'a', 1)
            sys.stdout = log
            sys.stderr = log
            return self.get_publisher()
        return create_publisher

    def get_publisher(self):
        """() -> Publisher
        Return the Publisher instance for this site.
        Make one if it does not already exist.
        This only works for one site per process.
        """
        if get_publisher() is None:
            publisher_class = self.get_publisher_class()
            durus_host, durus_port = self.get_durus_address()
            connection = Connection(ClientStorage(port=durus_port,
                                                  host=durus_host),
                                    cache_size=self.get_durus_cache_size())
            return publisher_class(connection=connection, site=self)
        else:
            assert get_publisher().get_site().get_name() is self.get_name()
        return get_publisher()

    def get_connection(self):
        """() -> Connection
        Return the Connection instance for this site.
        Make one if it does not already exist.
        This only works for one site per process.
        """
        return self.get_publisher().get_connection()

    def get_script_name(self):
        """() -> str
        Return value to use for CGI environment's SCRIPT_NAME
        variable.  This does not normally end with a '/'.  This is the
        part of the path that is not involved in the Publisher's
        traversal.
        """
        return self.get('script_name', '')

    def start_web(self):
        """
        Start the QP web server.
        """
        if self.is_web_running():
            return
        fork_result = fork()
        if fork_result == 0:
            server_pidfile = self.get_web_pidfile()
            pidfile = open(server_pidfile, 'w')
            parent_pid = getpid()
            pidfile.write(str(parent_pid))
            pidfile.close()
            log = open(self.get_logfile(), 'a')
            log.write("web[%s] started at %s UTC\n" % (
                parent_pid, datetime.utcnow()))
            log.close()
            try:
                run_web(self)
            finally:
                if parent_pid == getpid():
                    try:
                        unlink(server_pidfile)
                    except OSError:
                        pass
        for address in self.get_web_addresses():
            wait_for_server(*address)

    def start_durus(self):
        """
        Start the Durus StorageServer.
        """
        if self.is_durus_running():
            return
        fork_result = fork()
        if fork_result == 0:
            self.ensure_uid_gid_not_root()
            server_pidfile = self.get_durus_pidfile()
            pidfile = open(server_pidfile, 'w')
            parent_pid = getpid()
            pidfile.write(str(parent_pid))
            pidfile.close()
            log = open(self.get_logfile(), 'w')
            log.write("durus[%s] started at %s UTC\n" % (
                parent_pid, datetime.utcnow()))
            log.close()
            try:
                logger = getLogger('durus')
                file = open(self.get_logfile(), 'a+')
                sys.stdout = file
                handler = StreamHandler(file)
                handler.setFormatter(Formatter("durus[%(message)s]"))
                logger.handlers[:] = []
                logger.addHandler(handler)
                logger.setLevel(int(self.get_durus_logginglevel()))
                logger.propagate = False
                host, port = self.get_durus_address()
                StorageServer(FileStorage(self.get_durus_file()),
                              host=host,
                              port=port).serve()
            finally:
                if parent_pid == getpid():
                    try:
                        unlink(server_pidfile)
                    except OSError:
                        pass
        wait_for_server(*self.get_durus_address())

    def stop_durus(self):
        """
        Stop the Durus StorageServer.
        """
        if not self.is_durus_running():
            return
        stop_durus(*self.get_durus_address())
        if exists(self.get_durus_pidfile()):
            unlink(self.get_durus_pidfile())

    def stop_web(self):
        """
        Stop the QP web server.
        """
        pid = self.is_web_running()
        if pid:
            for j in range(10):
                if not self.is_web_running():
                    break
                kill(pid, signal.SIGTERM)
                sleep(1)
            else:
                print "\failed to kill web process %s" % pid
        if exists(self.get_web_pidfile()):
            unlink(self.get_web_pidfile())

    def status(self):
        """
        Show a summary of the current status of all servers.
        """
        print "%-6s" % self.get_name(),
        if self.is_durus_running():
            print "durus[%s]:%s" % (
                self.is_durus_running(),
                self.get_durus_address()[1]),
        else:
            print "durus:down",
        if self.is_web_running():
            print "web[%s]" % self.is_web_running(),
            if self.get_scgi_address():
                print "scgi:%s:%s" % self.get_scgi_address(),
            if self.get_http_address():
                print "http:%s:%s" % self.get_http_address(),
            if self.get_as_https_address():
                print "as_https:%s:%s" % self.get_as_https_address(),
            if self.get_https_address():
                print "https:%s:%s" % self.get_https_address(),
        else:
            print "web:down",
        print

    def log_tail(self):
        """
        Show the last 40 lines, and continue to show any new output in the
        logfile.  This doesn't stop until the user types Control-C or takes
        some other action to stop it.
        """
        system("tail -n 40 -f %s" % self.get_logfile())

    def build(self):
        """
        Compile cgi2scgi.c with the right options so that it can be used for
        connecting the the SCGI server of this site.  Print Apache configuration
        lines that can be used for this purpose.
        """
        address = self.get_scgi_address()
        if address is not None:
            port = address[1]
            src = join(qp.hub.__path__[0], 'cgi2scgi.c')
            target = join(self.get_package_directory(),
                          '%s.cgi' % self.get_name())
            command = "gcc -Wall -DPORT=%s %s -o %s" % (port, src, target)
            print "# " + command
            print 'ScriptAlias "%s/" "%s/"' % (self.get_script_name(), target)
            system(command)

    def show(self):
        """
        Display the configuration information for this site.
        """
        print
        print 'SITE: ', self.get_name()
        doc = self.get_root_directory_class().__doc__
        if doc:
            print doc
        print 'publisher', self.get_publisher_class()
        print 'root_directory', self.get_root_directory_class()
        print 'banned', self.get_banned()
        print 'logfile : %r' % self.get_logfile()
        print 'durus_pidfile : %r' % self.get_durus_pidfile()
        print 'web_pidfile : %r' % self.get_web_pidfile()
        print 'durus_address : %r' % (self.get_durus_address(),)
        print 'http_address : %r' % (self.get_http_address(),)
        print 'as_https_address : %r' % (self.get_as_https_address(),)
        print 'https_address : %r' % (self.get_https_address(),)
        print 'scgi_address : %r' % (self.get_scgi_address(),)

    def interaction(self):
        try:
            from pyrepl.python_reader import ReaderConsole
        except ImportError:
            print 'The pyrepl package is required for interaction.'
            print 'http://codespeak.net/pyrepl/'
            return
        from pyrepl.unix_console import UnixConsole
        try:
            console = UnixConsole(0, 1, None, None)
        except TypeError:
            try:
                console = UnixConsole(1, None) # older version?
            except AttributeError:
                console = UnixConsole() # even older?
        connection = self.get_connection()
        root=connection.get_root()
        env = dict(site=self, connection=connection, root=root)
        for key, value in root.items():
            env[key.replace('-', '_')] = value
        env_keys = env.keys()
        env_keys.sort()
        print ', '.join(env_keys)
        reader_console = ReaderConsole(console, env)
        reader_console.run_user_init_file()
        reader_console.interact()

    def change_uid_gid(self, uid, gid=None):
        """(uid:str, gid:str=None)
        Try to change UID and GID to the provided values
        This will only work if this script is run by root.
        Try to convert uid and gid to integers, in case they're numeric.
        """
        try:
            uid = int(uid)
            default_grp = pwd.getpwuid(uid)[3]
        except ValueError:
            uid, default_grp = pwd.getpwnam(uid)[2:4]
        if gid is None:
            gid = default_grp
        else:
            try:
                gid = int(gid)
            except ValueError:
                gid = grp.getgrnam(gid)[2]
        setgid(gid)
        setuid(uid)

    def ensure_uid_gid_not_root(self):
        """
        Make sure that the current user/group is not root, changing if the
        current user *is* root, to the uid identified by the 'daemon_uid'
        configuration value.
        """
        if getuid() == 0:
            uid = self.get('daemon_uid', 'nobody')
            self.change_uid_gid(uid)
        assert getuid() != 0
