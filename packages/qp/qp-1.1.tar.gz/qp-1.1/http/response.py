"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/http/response.py $
$Id: response.py 27524 2005-10-06 19:56:57Z dbinger $
"""
from rfc822 import formatdate
import struct
import time
import zlib

status_reasons = {
    100: 'Continue',
    101: 'Switching Protocols',
    102: 'Processing',
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi-Status',
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Moved Temporarily',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    307: 'Temporary Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Time-out',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request-URI Too Large',
    415: 'Unsupported Media Type',
    416: 'Requested range not satisfiable',
    417: 'Expectation Failed',
    422: 'Unprocessable Entity',
    423: 'Locked',
    424: 'Failed Dependency',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Time-out',
    505: 'HTTP Version not supported',
    507: 'Insufficient Storage',
}

_GZIP_HEADER = ("\037\213" # magic
                "\010" # compression method
                "\000" # flags
                "\000\000\000\000" # time, who cares?
                "\002"
                "\377")

_GZIP_EXCLUDE = set(["application/pdf",
                     "application/zip",
                     "audio/mpeg",
                     "image/gif",
                     "image/jpeg",
                     "image/png",
                     "video/mpeg",
                     "video/quicktime",
                     "video/x-msvideo",
                     ])


class HTTPResponse:
    """
    An object representation of an HTTP response.

    The Response type encapsulates all possible responses to HTTP
    requests.  

    Instance attributes:
      content_type : (mime_type:str, charset:str)
      status : (status_code:int, reason_phrase:str)
      headers : { string : string }
        most of the headers included with the response; every header set
        by 'set_header()' goes here.  Does not include "Status" or
        "Set-Cookie" headers (unless someone uses set_header() to set
        them, but that would be foolish).
      body : str | Stream
        the response body, None by default.  Note that if the body is not a
        stream then it is already encoded using 'charset'.
      buffered : bool
        if false, response data will be flushed as soon as it is
        written (the default is true).  This is most useful for
        responses that use the Stream() protocol.  Note that whether the
        client actually receives the partial response data is highly
        dependent on the web server
      cookies : { name:string : { attrname : value } }
        collection of cookies to set in this response; it is expected
        that the user-agent will remember the cookies and send them on
        future requests.  The cookie value is stored as the "value"
        attribute.  The other attributes are as specified by RFC 2109.
      cache : int | None
        the number of seconds the response may be cached.  The default is 0,
        meaning don't cache at all.  This variable is used to set the HTTP
        expires header.  If set to None then the expires header will not be
        added.
      compress : bool
        should the body of the response be compressed?
    """

    def __init__(self):
        self.set_content_type('text/html', 'utf-8')
        self.set_status(200)
        self.set_compress(False)
        self.set_expires(0)
        self.set_buffered(True)
        self.headers = {}
        self.cookies = {}
        self.body = None

    def set_content_type(self, mime_type, charset):
        """(mime_type:basicstr, charset:basicstr)
        """
        self.content_type = (mime_type, charset)

    def get_mime_type(self):
        return self.content_type[0]

    def get_charset(self):
        return self.content_type[1]

    def set_compress(self, value):
        self.compress = value

    def get_compress(self):
        return self.compress

    def set_buffered(self, value):
        self.buffered = value

    def get_buffered(self):
        return self.buffered

    def set_status(self, status_code, reason=None):
        """(status_code : int, reason : string = None)
	
        Sets the HTTP status code of the response.  'status_code' must be an
        integer in the range 100 .. 599.  'reason' must be a string; if
        not supplied, the default reason phrase for 'status_code' will be
        used.  If 'status_code' is a non-standard status code, the generic
        reason phrase for its group of status codes will be used; eg.
        if status == 493, the reason for status 400 will be used.
        """
        if not isinstance(status_code, int):
            raise TypeError, "status_code must be an integer"
        if not (100 <= status_code <= 599):
            raise ValueError, "status_code must be between 100 and 599"
        self.status = (status_code,
                       (reason or
                        status_reasons.get(status_code) or
                        status_reasons.get(status_code - (status_code % 100))))

    def get_status(self):
        return self.status

    def get_status_code(self):
        return self.status[0]

    def set_header(self, name, value):
        """(name : string, value : string)"""
        self.headers[name] = value

    def get_header(self, name, default=None):
        """(name : string, default=None) -> value : string

        Gets an HTTP return header "name".  If none exists then 'default' is
        returned.
        """
        lower_name = name.lower()
        for header in self.headers:
            if header.lower() == lower_name:
                return self.headers[header]
        return default

    def set_expires(self, seconds=0, minutes=0, hours=0, days=0):
        if seconds is None:
            self.cache = None # don't generate 'Expires' header
        else:
            self.cache = seconds + 60*(minutes + 60*(hours + 24*days))

    def _compress_body(self, body):
        """(body: str) -> str
        Try to compress the body using gzip and return either the original
        body or the compressed body.  If the compressed body is returned, the
        content-encoding header is set to 'gzip'.
        """
        if not self.get_compress() or self.get_mime_type() in _GZIP_EXCLUDE:
            return body
        n = len(body)
        co = zlib.compressobj(6, zlib.DEFLATED, -zlib.MAX_WBITS,
                              zlib.DEF_MEM_LEVEL, 0)
        chunks = [_GZIP_HEADER,
                  co.compress(body),
                  co.flush(),
                  struct.pack("<ll", zlib.crc32(body), n)]
        compressed_body = "".join(chunks)
        ratio = float(n) / len(compressed_body)
        #print "gzip original size %d, ratio %.1f" % (n, ratio)
        if ratio > 1.0:
            self.set_header("Content-Encoding", "gzip")
            return compressed_body
        else:
            return body

    def _encode_chunk(self, chunk):
        """(chunk:str|unicode)
        Returns the chunk encoded using the charset of the response.
        If the chunk is a str, it is assumed to be encoded already
        using the charset of the response.  
        """
        if isinstance(chunk, unicode):
            return chunk.encode(self.get_charset())
        else:
            return chunk

    def set_body(self, body):
        """(body : Stream|basestring)

        Sets the response body equal to the argument 'body'.
        If the argument is a str, or a Stream that generates str instances,
        it is the caller's responsibility to make sure that these str instances
        use the charset of the response.
        """
        if isinstance(body, Stream):
            self.body = body
        else:
            encoded = self._encode_chunk(body)
            self.body = self._compress_body(encoded)

    def expire_cookie(self, name, **attrs):
        """
        Cause an HTTP cookie to be removed from the browser

        The response will include an HTTP header that will remove the cookie
        corresponding to "name" on the client, if one exists.  This is
        accomplished by sending a new cookie with an expiration date
        that has already passed.  Note that some clients require a path
        to be specified - this path must exactly match the path given
        when creating the cookie.  The path can be specified as a keyword
        argument.
        """
        params = {'max_age': 0, 'expires': 'Thu, 01-Jan-1970 00:00:00 GMT'}
        params.update(attrs)
        self.set_cookie(name, "deleted", **params)

    def set_cookie(self, name, value, **attrs):
        """(name : string, value : string, **attrs)

        Set an HTTP cookie on the browser.

        The response will include an HTTP header that sets a cookie on
        cookie-enabled browsers with a key "name" and value "value".
        Cookie attributes such as "expires" and "domains" may be
        supplied as keyword arguments; see RFC 2109 for a full list.
        (For the "secure" attribute, use any true value.)

        This overrides any previous value for this cookie.  Any
        previously-set attributes for the cookie are preserved, unless
        they are explicitly overridden with keyword arguments to this
        call.
        """
        cookies = self.cookies
        if cookies.has_key(name):
            cookie = cookies[name]
        else:
            cookie = cookies[name] = {}
        cookie.update(attrs)
        cookie['value'] = value

    def get_content_length(self):
        if self.body is None:
            return None
        if isinstance(self.body, Stream):
            return self.body.get_length()
        return len(self.body)

    def _gen_cookie_headers(self):
        """() -> [(str, str)]
        """
        for name, attrs in self.cookies.iteritems():
            value = str(attrs['value'])
            if '"' in value:
                value = value.replace('"', '\\"')
            chunks = ['%s="%s"' % (name, value)]
            for name, val in attrs.items():
                name = name.lower()
                if val is None:
                    continue
                if name in ('expires', 'domain', 'path', 'max_age', 'comment'):
                    name = name.replace('_', '-')
                    chunks.append('%s=%s' % (name, val))
                elif name == 'secure' and val:
                    chunks.append("secure")
            yield ("Set-Cookie", '; '.join(chunks))


    def generate_headers(self):
        """() -> [(name:string, value:string)]

        Generate a list of headers to be returned as part of the response.
        """
        for name, value in self.headers.iteritems():
            yield (name.title(), value)

        for name, value in self._gen_cookie_headers():
            yield name, value

        # Date header
        now = time.time()
        if "date" not in self.headers:
            yield ("Date", formatdate(now))

        # Cache directives
        if self.cache is None:
            pass # don't mess with the expires header
        elif "expires" not in self.headers:
            if self.cache > 0:
                expire_date = formatdate(now + self.cache)
            else:
                expire_date = "-1" # allowed by HTTP spec and may work better
                                   # with some clients
            yield ("Expires", expire_date)

        # Content-type
        if "content-type" not in self.headers:
            mime_type, charset = self.content_type
            value = mime_type
            if charset:
                value += '; charset=%s' % charset
            yield ('Content-Type', value)

        # Content-Length
        if "content-length" not in self.headers:
            length = self.get_content_length()
            if length is not None:
                yield ('Content-Length', str(length))


    def generate_body_chunks(self):
        """
        Return a sequence of body chunks, encoded using 'charset'.
        Note that the chunks in the iteration of a Stream, if they
        are str instances, are assumed to be encoded already.
        """
        if self.body is None:
            pass
        elif isinstance(self.body, Stream):
            for chunk in self.body:
                yield self._encode_chunk(chunk)
        else:
            yield self.body # already encoded by set_body().

    def write(self, output, include_status=True, include_body=True):
        """(output:file, include_status:bool=True, include_body:bool=True)

        Write the HTTP response headers and body to 'output'.  This is not
        a complete HTTP response, as it doesn't start with a response
        status line as specified by RFC 2616.  By default, it does start
        with a "Status" header as described by the CGI spec.  It is expected
        that this response is parsed by the web server and turned into a
        complete HTTP response.  If include_body is False, only the headers
        are written to 'output'.  This is used to support HTTP HEAD requests.
        """
        flush_output = not self.get_buffered() and hasattr(output, 'flush')
        if include_status:
            # "Status" header must come first.
            output.write("Status: %03d %s\r\n" % self.status)
        for name, value in self.generate_headers():
            output.write("%s: %s\r\n" % (name, value))
        output.write("\r\n")
        if flush_output:
            output.flush()
        if not include_body:
            return
        for chunk in self.generate_body_chunks():
            output.write(chunk)
            if flush_output:
                output.flush()
        if flush_output:
            output.flush()

class Stream:
    """
    A wrapper around response data that can be streamed.  The 'iterable'
    argument must support the iteration protocol.
    Beware that exceptions raised while writing the stream will not be
    handled gracefully.

    Instance attributes:
      iterable : any
        an object that supports the iteration protocol.  The items produced
        by the stream must be be unicode or str instances.
        If they are str instances, the encoding is assumed to be that of
        the response.
      length: int | None
        the number of bytes that will be produced by the stream, None
        if it is not known.  Used to set the Content-Length header.
    """
    def __init__(self, iterable, length=None):
        self.iterable = iterable
        self.length = length

    def __iter__(self):
        return iter(self.iterable)

    def get_length(self):
        return self.length


