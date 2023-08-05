"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/hub/http.py $
$Id: http.py 26507 2005-04-07 10:30:19Z dbinger $

Provides a HubServer-based HTTP server.
"""
from BaseHTTPServer import BaseHTTPRequestHandler
from qp.hub.dispatcher import HubServer
from qp.pub.common import get_publisher
from qp.pub.hit import Hit
from urllib import unquote
import sys

class HTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, connection, address, info, **kwargs):
        self.required_cgi_environment = dict(
            SERVER_SOFTWARE="qp/1.0",
            GATEWAY_INTERFACE='CGI/1.1')
        self.required_cgi_environment.update(kwargs)
        BaseHTTPRequestHandler.__init__(
            self, connection, address, info)

    def get_cgi_env(self, method):
        env = dict(
            SERVER_NAME=self.server.server_name,
            SERVER_PROTOCOL=self.protocol_version,
            SERVER_PORT=str(self.server.server_port),
            REQUEST_METHOD=method,
            REMOTE_ADDR=self.client_address[0],
            REMOTE_PORT=self.client_address[1])
        if '?' in self.path:
            env['PATH_INFO'], env['QUERY_STRING'] = self.path.split('?', 1)
        else:
            env['PATH_INFO'] = self.path
        env['PATH_INFO'] = unquote(env['PATH_INFO'])
        script_name = self.required_cgi_environment.get('SCRIPT_NAME', '')
        if script_name:
            path_info = env['PATH_INFO']
            if path_info.startswith(script_name): # and it better!
                env['PATH_INFO'] = path_info[len(script_name):]
            else:
                print
                print "All paths are expected to start with the script_name."
                print "  The script_name is %r." % script_name
                print "  The requested path is %r." % self.path
                print
        if self.headers.typeheader is None:
            env['CONTENT_TYPE'] = self.headers.type
        else:
            env['CONTENT_TYPE'] = self.headers.typeheader
        env['CONTENT_LENGTH'] = self.headers.getheader(
            'content-length') or "0"
        for name, value in self.headers.items():
            header_name = 'HTTP_' + name.upper().replace('-', '_')
            env[header_name] = value
        accept = []
        for line in self.headers.getallmatchingheaders('accept'):
            if line[:1] in "\t\n\r ":
                accept.append(line.strip())
            else:
                accept = accept + line[7:].split(',')
        env['HTTP_ACCEPT'] = ','.join(accept)
        co = filter(None, self.headers.getheaders('cookie'))
        if co:
            env['HTTP_COOKIE'] = ', '.join(co)
        env.update(self.required_cgi_environment)
        return env

    def process(self, env):
        hit = Hit(self.rfile, env)
        get_publisher().process_hit(hit)
        response = hit.get_response()
        try:
            self.send_response(*response.get_status())
            response.write(self.wfile, include_status=False,
                           include_body=(self.command!='HEAD'))
        except IOError, err:
            print "IOError while sending response ignored: %s" % err

    def handle_one_request(self):
        self.raw_requestline = self.rfile.readline()
        if not self.raw_requestline:
            self.close_connection = 1
            return
        if not self.parse_request():
            return
        return self.process(self.get_cgi_env(self.command))
    
    def log_request(self, *args, **kwargs):
        pass

    def send_response(self, code, message=None):
        """
        Copied, with regret, from BaseHTTPRequestHandler, except that the line
        that adds the 'Date' header is removed.
        """
        self.log_request(code)
        if message is None:
            if code in self.responses:
                message = self.responses[code][0]
            else:
                message = ''
        if self.request_version != 'HTTP/0.9':
            self.wfile.write("%s %d %s\r\n" %
                             (self.protocol_version, code, message))
        self.send_header('Server', self.version_string())


# netstring utility functions
def ns_read_size(input):
    size = ""
    while 1:
        c = input.read(1)
        if c == ':':
            break
        elif not c:
            if not size:
                return None
            raise IOError, 'short netstring read'
        size = size + c
    return long(size)

def ns_reads(input):
    size = ns_read_size(input)
    if size is None:
        return None
    data = ""
    while size > 0:
        s = input.read(size)
        if not s:
            raise IOError, 'short netstring read'
        data = data + s
        size -= len(s)
    if input.read(1) != ',':
        raise IOError, 'missing netstring terminator'
    return data

def read_env(input):
    headers = ns_reads(input)
    if headers is None:
        return None
    items = headers.split("\0")
    items = items[:-1]
    assert len(items) % 2 == 0, "malformed headers"
    env = {}
    for i in range(0, len(items), 2):
        env[items[i]] = items[i+1]
    return env


class SCGIHandler(object):

    def __init__(self, script_name=''):
        self.script_name = script_name

    def handle_connection(self, conn):
        input = conn.makefile("r")
        output = conn.makefile("w")
        env = read_env(input)
        if env is None:
            # Nothing here.
            return
        if (env.get('SCRIPT_NAME') and
            env.get('SCRIPT_NAME') == env.get('REQUEST_URI') and
            env.get('SCRIPT_NAME').startswith(self.script_name) and
            env.get('PATH_INFO') is None):
            # This looks like it is coming through mod_scgi and
            # needs repair.
            env['PATH_INFO'] = env['SCRIPT_NAME'][len(self.script_name):]
            env['SCRIPT_NAME'] = self.script_name
            assert env['SCRIPT_NAME'] + env['PATH_INFO'] == env['REQUEST_URI']
        hit = Hit(input, env)
        get_publisher().process_hit(hit)
        response = hit.get_response()
        try:
            response.write(output)
            input.close()
            output.close()
            conn.close()
        except IOError, err:
            print "IOError while sending response: %s" % err


def run_web(site):
    logfile = site.get_logfile()
    sys.stderr = sys.stdout = open(logfile, 'a')
    scgi_address = site.get_scgi_address()
    http_address = site.get_http_address()
    as_https_address = site.get_as_https_address()
    https_address = site.get_https_address()
    scgi_port = scgi_address and scgi_address[1]
    http_port = http_address and http_address[1]
    as_https_port = as_https_address and as_https_address[1]
    script_name = site.get_script_name()
    def create_connection_handler():
        class ConnectionHandler(object):
            def handle_connection(self, connection):
                port = connection.getsockname()[1]
                if port == scgi_port:
                    return SCGIHandler(
                        script_name=script_name).handle_connection(connection)
                elif port == http_port:
                    self.server_name, self.server_port = http_address
                    client_address = connection.getpeername()
                    HTTPRequestHandler(connection, client_address, self,
                                       SCRIPT_NAME=script_name)
                elif port == as_https_port:
                    self.server_name, self.server_port = https_address
                    client_address = connection.getpeername()
                    HTTPRequestHandler(
                        connection, client_address, self, HTTPS='on',
                        SCRIPT_NAME=script_name)
                else:
                    connection.send(str(locals()))
        site.get_create_publisher()()
        return ConnectionHandler()
    server = HubServer(create_connection_handler,
                       max_children=site.get_max_children(),
                       banned=site.get_banned())
    server.listen(scgi_address, http_address, as_https_address)
    site.ensure_uid_gid_not_root()
    server.run()



