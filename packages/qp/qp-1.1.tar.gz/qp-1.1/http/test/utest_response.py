#!/usr/bin/env python
"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/http/test/utest_response.py $
$Id: utest_response.py 27623 2005-10-26 14:48:41Z dbinger $
"""
from cStringIO import StringIO
from qp.http.response import HTTPResponse, Stream
from sancho.utest import UTest

class Test(UTest):

    def a(self):
        response = HTTPResponse()
        response.set_content_type('text/html', 'utf8')
        response.set_status(200)
        response.set_status(200, 'Excellent')
        assert response.get_status_code() == 200
        assert response.get_status() == (200, 'Excellent')
        response.set_status(479)
        try:
            response.set_status(600)
            assert 0
        except ValueError:
            pass
        try:
            response.set_status('200')
            assert 0
        except TypeError:
            pass
        response.set_expires(None)
        response.set_expires(seconds=200)
        response.set_header('foo', 1)
        assert response.get_header('foo') == 1
        response.set_cookie('a', 23)
        response.expire_cookie('a')
        response.set_body('ok')
        response.set_compress(False)
        response.set_body('ok' * 1000)

    def b(self):
        response = HTTPResponse()
        assert response.get_mime_type() == 'text/html'
        response.set_content_type('text/plain', None)
        assert response.get_mime_type() == 'text/plain'
        assert (200, 'OK') == response.status
        assert response.get_content_length() == None
        response.set_body('ab')
        assert response.get_content_length() == 2
        response.set_body(Stream(StringIO('a'), 1))
        assert response.get_content_length() == 1
        response.set_cookie('cookie', 1)
        headers = response.generate_headers()
        headers_dict = dict(headers)
        del headers_dict['Date']
        print headers_dict
        assert headers_dict == dict([
            ('Content-Length', '1'),
            ('Content-Type', 'text/plain'),
            ('Expires', '-1'),
            ('Set-Cookie', 'cookie="1"')])
        response.set_expires(None)
        headers = response.generate_headers()
        response.set_expires(days=1)
        headers = response.generate_headers()
        response.set_cookie('a', 'x"', secure=1, expires=1,
                            b=None, a='all"ok"')
        response.set_header('bogus', 'yes')
        headers = response.generate_headers()

    def check_write(self):
        stream = Stream(StringIO('a'), 1)
        assert ''.join(stream) == 'a'
        response = HTTPResponse()
        response.buffered=False
        out = StringIO()
        response.write(out, include_status=False)
        response.write(out, include_status=True)
        response.write(out, include_body=False)
        response.set_body('a')
        response.write(out)
        response.set_body(stream)
        response.write(out)
        response.set_body(Stream(StringIO('a'*1000), 1000))
        response.write(out)
        response.set_body(u'0' * 1000)
        response.write(out)

    def c(self):
        response = HTTPResponse()
        response.set_cookie('a', '"ok', path="/", secure=True)
        response.set_cookie('b', None)
        response.set_header('ok', 'this')
        list(response.generate_headers())
        assert response.cache == 0
        response.set_expires(1)
        list(response.generate_headers())
        response.cache = None
        list(response.generate_headers())

if __name__ == '__main__':
    Test()
