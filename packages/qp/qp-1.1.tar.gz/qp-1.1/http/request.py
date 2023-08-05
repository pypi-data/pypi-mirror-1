"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/http/request.py $
$Id: request.py 27632 2005-10-28 14:40:59Z dbinger $
"""
from cStringIO import StringIO
from urllib import quote, unquote
import re
import rfc822
import string
import tempfile

# Various regexes for parsing specific bits of HTTP, all from RFC 2616.

# These are used by _parse_pref_header().
# LWS is linear whitespace; the latter two assume that LWS has been removed.
_http_lws_re = re.compile(r"(\r\n)?[ \t]+")
_http_list_re = re.compile(r",+")
_http_encoding_re = re.compile(r"([^;]+)(;q=([\d.]+))?$")

def get_content_type(environ):
    ctype = environ.get("CONTENT_TYPE")
    if ctype:
        return ctype.split(";")[0]
    else:
        return None

def _decode_string(s, charset):
    return s.decode(charset)

def parse_header(line):
    """Parse a Content-type like header.

    Return the main content-type and a dictionary of options.

    """
    plist = [x.strip() for x in line.split(';')]
    key = plist.pop(0).lower()
    pdict = {}
    for p in plist:
        i = p.find('=')
        if i >= 0:
            name = p[:i].strip().lower()
            value = p[i+1:].strip()
            if len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1]
            pdict[name] = value
    return key, pdict

def parse_content_disposition(full_cdisp):
    (cdisp, cdisp_params) = parse_header(full_cdisp)
    name = cdisp_params.get('name')
    if not (cdisp == 'form-data' and name):
        raise ValueError('expected Content-Disposition: form-data '
                         'with a "name" parameter: got %r' % full_cdisp)
    return (name, cdisp_params.get('filename'))

def parse_query(qs, charset):
    """(qs: string) -> {key:string, string|[string]}

    Parse a query given as a string argument and return a dictionary.
    """
    fields = {}
    for chunk in filter(None, qs.split('&')):
        if '=' not in chunk:
            name = chunk
            value = ''
        else:
            name, value = chunk.split('=', 1)
        name = unquote(name.replace('+', ' '))
        value = unquote(value.replace('+', ' '))
        name = _decode_string(name, charset)
        value = _decode_string(value, charset)
        _add_field_value(fields, name, value)
    return fields

def _add_field_value(fields, name, value):
    if name in fields:
        values = fields[name]
        if not isinstance(values, list):
            fields[name] = values = [values]
        values.append(value)
    else:
        fields[name] = value


class HTTPRequest:
    """
    Model a single HTTP request and all associated data: environment
    variables, form variables, cookies, etc.

    To access environment variables associated with the request, use
    get_environ(): eg. request.get_environ('SERVER_PORT', 80).

    To access form variables, use get_field(), eg.
    request.get_field("name").

    To access cookies, use get_cookie().

    Various bits and pieces of the requested URL can be accessed with
    get_url(), get_path(), get_server()
    """

    # In qp, we will encode html pages using utf-8.
    # Unless the client specifies otherwise, we will assume that requests use
    # the same charset.
    DEFAULT_CHARSET = 'utf-8' 

    def __init__(self, stdin, environ):
        self.stdin = stdin
        self.environ = environ
        self.fields = {}
        self.cookies = parse_cookies(environ.get('HTTP_COOKIE', ''))
        if environ.get('HTTPS', 'off').lower() == 'on':
            self.scheme = "https"
        else:
            self.scheme = "http"

    def process_inputs(self):
        query = self.get_query()
        if query:
            self.fields.update(parse_query(query, self.DEFAULT_CHARSET))
        length = self.environ.get('CONTENT_LENGTH') or "0"
        try:
            length = int(length)
        except ValueError:
            raise ValueError('invalid content-length header')
        content_type = self.environ.get("CONTENT_TYPE")
        if content_type:
            ctype, ctype_params = parse_header(content_type)
            if ctype == 'application/x-www-form-urlencoded':
                self._process_urlencoded(length, ctype_params)
            elif ctype == 'multipart/form-data':
                self._process_multipart(length, ctype_params)

    def _process_urlencoded(self, length, params):
        query = self.stdin.read(length)
        if len(query) != length:
            raise ValueError('unexpected end of request body')
        charset = params.get('charset', self.DEFAULT_CHARSET)
        self.fields.update(parse_query(query, charset))

    def _process_multipart(self, length, params):
        boundary = params.get('boundary')
        if not boundary:
            raise ValueError('multipart/form-data missing boundary')
        charset = params.get('charset')
        mimeinput = MIMEInput(self.stdin, boundary, length)
        try:
            for line in mimeinput.readpart():
                pass # discard lines up to first boundary
            while mimeinput.moreparts():
                self._process_multipart_body(mimeinput, charset)
        except EOFError:
            raise ValueError('unexpected end of multipart/form-data')

    def _process_multipart_body(self, mimeinput, charset):
        headers = StringIO()
        lines = mimeinput.readpart()
        for line in lines:
            headers.write(line)
            if line == '\r\n':
                break
        headers.seek(0)
        headers = rfc822.Message(headers)
        ctype, ctype_params = parse_header(headers.get('content-type', ''))
        if ctype and 'charset' in ctype_params:
            charset = ctype_params['charset']
        cdisp, cdisp_params = parse_header(headers.get('content-disposition',
                                                       ''))
        if not cdisp:
            raise ValueError('expected Content-Disposition header')
        name = cdisp_params.get('name')
        filename = cdisp_params.get('filename')
        if not (cdisp == 'form-data' and name):
            raise ValueError('expected Content-Disposition: form-data'
                               'with a "name" parameter: got %r' %
                               headers.get('content-disposition', ''))
        # FIXME: should really to handle Content-Transfer-Encoding and other
        # MIME complexity here.  See RFC2048 for the full horror story.
        if filename:
            # it might be large file upload so use a temporary file
            upload = Upload(filename, ctype, charset)
            upload.receive(lines)
            _add_field_value(self.fields, name, upload)
        else:
            value = _decode_string(''.join(lines),
                                   charset or self.DEFAULT_CHARSET)
            _add_field_value(self.fields, name, value)

    def get_header(self, name, default=None):
        """(name : str, default : str = None) -> str

        Return the named HTTP header, or an optional default argument
        (or None) if the header is not found.  Note that both original
        and CGI-ified header names are recognized, e.g. 'Content-Type',
        'CONTENT_TYPE' and 'HTTP_CONTENT_TYPE' should all return the
        Content-Type header, if available.
        """
        environ = self.environ
        name = name.replace("-", "_").upper()
        val = environ.get(name)
        if val is not None:
            return val
        if name[:5] != 'HTTP_':
            name = 'HTTP_' + name
        return environ.get(name, default)

    def get_cookie(self, cookie_name, default=None):
        return self.cookies.get(cookie_name, default)

    def get_cookies(self):
        return self.cookies

    def get_fields(self):
        return self.fields

    def get_field(self, name, default=None):
        return self.fields.get(name, default)

    def get_method(self):
        """Returns the HTTP method for this request
        """
        return self.environ.get('REQUEST_METHOD', 'GET')

    def get_scheme(self):
        return self.scheme

    def get_server(self):
        """() -> str

        Return the server name with an optional port number, eg.
        "www.example.com" or "foo.bar.com:8000".
        """
        http_host = self.environ.get("HTTP_HOST")
        if http_host:
            return http_host
        server_name = self.environ["SERVER_NAME"].strip()
        server_port = self.environ.get("SERVER_PORT")
        if (not server_port or
            (self.get_scheme() == "http" and server_port == "80") or
            (self.get_scheme() == "https" and server_port == "443")):
            return server_name
        else:
            return server_name + ":" + server_port

    def get_script_name(self):
        return self.environ.get('SCRIPT_NAME', '')

    def get_path_info(self):
        return self.environ.get('PATH_INFO', '')

    def get_path(self, n=0):
        """(n : int = 0) -> str

        Return the path of the current request, chopping off 'n' path
        components from the right.  Eg. if the path is "/bar/baz/qux",
        n=0 would return "/bar/baz/qux" and n=2 would return "/bar".
        Note that the query string, if any, is not included.

        A path with a trailing slash should just be considered as having
        an empty last component.  Eg. if the path is "/bar/baz/", then:
          get_path(0) == "/bar/baz/"
          get_path(1) == "/bar/baz"
          get_path(2) == "/bar"

        If 'n' is negative, then components from the left of the path
        are returned.  Continuing the above example,
          get_path(-1) = "/bar"
          get_path(-2) = "/bar/baz"
          get_path(-3) = "/bar/baz/"

        Raises ValueError if absolute value of n is larger than the number of
        path components."""
          
        path = self.get_script_name() + self.get_path_info()
        if path[:1] !='/':
            path = '/' + path
        if n == 0:
            return path
        else:
            path_comps = path.split('/')
            if abs(n) > len(path_comps)-1:
                raise ValueError, "n=%d too big for path '%s'" % (n, path)
            if n > 0:
                return '/'.join(path_comps[:-n])
            elif n < 0:
                return '/'.join(path_comps[:-n+1])

    def get_query(self):
        """() -> string

        Return the query component of the URL.
        """
        return self.environ.get('QUERY_STRING', '')

    def get_path_query(self):
        query = self.get_query()
        path = quote(self.get_path())
        if query:
            return path + '?' + query
        else:
            return path

    def get_url(self):
        """() -> str

        Return the URL of the current request.
        """
        return "%s://%s%s" % (self.get_scheme(), self.get_server(),
                              self.get_path_query())

    def get_environ(self, key, default=None):
        """(key : string) -> str

        Fetch a CGI environment variable from the request environment.
        See http://hoohoo.ncsa.uiuc.edu/cgi/env.html
        for the variables specified by the CGI standard.
        """
        return self.environ.get(key, default)

    def get_remote_address(self):
        return self.get_environ('REMOTE_ADDR')

    def get_encoding(self, encodings):
        """(encodings : [string]) -> str

        Parse the "Accept-encoding" header. 'encodings' is a list of
        encodings supported by the server sorted in order of preference.
        The return value is one of 'encodings' or None if the client
        does not accept any of the encodings.
        """
        accept_encoding = self.get_header("accept-encoding") or ""
        found_encodings = self._parse_pref_header(accept_encoding)
        if found_encodings:
            for encoding in encodings:
                if found_encodings.has_key(encoding):
                    return encoding
        return None

    def get_accepted_types(self):
        """() -> {string:float}
        Return a dictionary mapping MIME types the client will accept
        to the corresponding quality value (1.0 if no value was specified).
        """
        accept_types = self.environ.get('HTTP_ACCEPT', "")
        return self._parse_pref_header(accept_types)

    def _parse_pref_header(self, S):
        """(S:str) -> {str:float}
        Parse a list of HTTP preferences (content types, encodings) and
        return a dictionary mapping strings to the quality value.
        """

        found = {}
        # remove all linear whitespace
        S = _http_lws_re.sub("", S)
        for coding in _http_list_re.split(S):
            m = _http_encoding_re.match(coding)
            if m:
                encoding = m.group(1).lower()
                q = m.group(3) or 1.0
                try:
                    q = float(q)
                except ValueError:
                    continue
                if encoding == "*":
                    continue # stupid, ignore it
                if q > 0:
                    found[encoding] = q
        return found


# See RFC 2109 for details.  Note that this parser is more liberal.
_COOKIE_RE = re.compile(r"""
                \s*
                (?P<name>[^=;,\s]+)
                \s*
                (
                    =
                    \s*
                    (
                        (?P<qvalue> "(\\[\x00-\x7f] | [^"])*")
                        |
                        (?P<value> [^";,\s]*)
                    )
                )?
                \s*
                [;,]?
                """, re.VERBOSE)

def parse_cookies(text):
    result = {}
    for m in _COOKIE_RE.finditer(text):
        name = m.group('name')
        if name[0] == '$':
            # discard, we don't handle per cookie attributes (e.g. $Path)
            continue
        qvalue = m.group('qvalue')
        if qvalue:
            value = re.sub(r'\\(.)', r'\1', qvalue)[1:-1]
        else:
            value = m.group('value') or ''
        result[name] = value
    return result

SAFE_CHARS = string.letters + string.digits + "-@&+=_., "
_safe_trans = None

def make_safe_filename(s):
    global _safe_trans
    if _safe_trans is None:
        _safe_trans = ["_"] * 256
        for c in SAFE_CHARS:
            _safe_trans[ord(c)] = c
        _safe_trans = "".join(_safe_trans)

    return s.translate(_safe_trans)


class Upload:
    r"""
    Represents a single uploaded file.  Uploaded files live in the
    filesystem, *not* in memory.

      fp
        an open file containing the content of the upload.  The file pointer
        points to the beginning of the file
      orig_filename
        the complete filename supplied by the user-agent in the
        request that uploaded this file.  Depending on the browser,
        this might have the complete path of the original file
        on the client system, in the client system's syntax -- eg.
        "C:\foo\bar\upload_this" or "/foo/bar/upload_this" or
        "foo:bar:upload_this".
      base_filename
        the base component of orig_filename, shorn of MS-DOS,
        Mac OS, and Unix path components and with "unsafe"
        characters neutralized (see make_safe_filename())
      content_type
        the content type provided by the user-agent in the request
        that uploaded this file.
      charset
        the charset provide by the user-agent
    """

    def __init__(self, orig_filename, content_type=None, charset=None):
        if orig_filename:
            self.orig_filename = orig_filename
            bspos = orig_filename.rfind("\\")
            cpos = orig_filename.rfind(":")
            spos = orig_filename.rfind("/")
            if bspos != -1:                 # eg. "\foo\bar" or "D:\ding\dong"
                filename = orig_filename[bspos+1:]
            elif cpos != -1:                # eg. "C:foo" or ":ding:dong:foo"
                filename = orig_filename[cpos+1:]
            elif spos != -1:                # eg. "foo/bar/baz" or "/tmp/blah"
                filename = orig_filename[spos+1:]
            else:
                filename = orig_filename

            self.base_filename = make_safe_filename(filename)
        else:
            self.orig_filename = None
            self.base_filename = None
        self.content_type = content_type
        self.charset = charset
        self.fp = None

    def receive(self, lines):
        self.fp = tempfile.TemporaryFile("w+b")
        for line in lines:
            self.fp.write(line)
        self.fp.seek(0)

    def read(self, n):
        return self.fp.read(n)

    def readline(self):
        return self.fp.readline()

    def readlines(self):
        return self.fp.readlines()    

    def __iter__(self):
        return iter(self.fp)

    def close(self):
        self.fp.close()


class LineInput:
    r"""
    A wrapper for an input stream that has the following properties:

        * lines are terminated by \r\n

        * lines shorter than 'maxlength' are always returned unbroken

        * lines longer than 'maxlength' are broken but the pair of
          characters \r\n are never split

        * no more than 'length' characters are read from the underlying
          stream

        * if the underlying stream does not produce at least 'length'
          characters then EOFError is raised

    """
    def __init__(self, fp, length):
        self.fp = fp
        self.length = length
        self.buf = ''

    def readline(self, maxlength=4096):
        # fill buffer
        n = min(self.length, maxlength - len(self.buf))
        if n > 0:
            self.length -= n
            assert self.length >= 0
            chunk = self.fp.read(n)
            if len(chunk) != n:
                raise EOFError('unexpected end of input')
            self.buf += chunk
        # split into lines
        buf = self.buf
        i = buf.find('\r\n')
        if i >= 0:
            i += 2
            self.buf = buf[i:]
            return buf[:i]
        elif buf.endswith('\r'):
            # avoid splitting CR LF pairs
            self.buf = '\r'
            return buf[:-1]
        else:
            self.buf = ''
            return buf

class MIMEInput:
    """
    Split a MIME input stream into parts.  Note that this class does not
    handle headers, transfer encoding, etc.
    """

    def __init__(self, fp, boundary, length):
        self.lineinput = LineInput(fp, length)
        self.pat = re.compile(r'--%s(--)?[ \t]*\r\n' % re.escape(boundary))
        self.done = False

    def moreparts(self):
        """Return true if there are more parts to be read."""
        return not self.done

    def readpart(self):
        """Generate all the lines up to a MIME boundary.  Note that you
        must exhaust the generator before calling this function again."""
        assert not self.done
        last_line = ''
        while 1:
            line = self.lineinput.readline()
            if not line:
                # Hit EOF -- nothing more to read.  This should *not* happen
                # in a well-formed MIME message.
                raise EOFError('MIME boundary not found (end of input)')
            if last_line.endswith('\r\n') or last_line == '':
                m = self.pat.match(line)
                if m:
                    # If we hit the boundary line, return now. Forget
                    # the current line *and* the CRLF ending of the
                    # previous line.
                    if m.group(1):
                        # hit final boundary
                        self.done = True
                    yield last_line[:-2]
                    return
            if last_line:
                yield last_line
            last_line = line
