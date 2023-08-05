"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/http/test/utest_request.py $
$Id: utest_request.py 27443 2005-09-20 17:03:27Z dbinger $
"""
from cStringIO import StringIO
from qp.http.request import HTTPRequest, get_content_type, parse_header
from qp.http.request import make_safe_filename, Upload, parse_cookies
from qp.http.request import parse_content_disposition, parse_query, LineInput
from sancho.utest import UTest, raises

class Test(UTest):

    def a(self):
        request = HTTPRequest(StringIO(), {})
        assert request.get_path() == '/'
        request = HTTPRequest(StringIO(), dict(
            PATH_INFO='/',
            SERVER_NAME='ok'
            ))
        assert request.get_path() == '/'
        assert request.get_url() == 'http://ok/'

    def check_get_content_type(self):
        assert get_content_type(dict()) is None
        assert get_content_type(dict(CONTENT_TYPE='text/html')) == 'text/html'
        assert get_content_type(
            dict(CONTENT_TYPE='text/html; blah')) == 'text/html'

    def check_parse_header(self):
        assert parse_header('foo;  a=1;b=2') == ('foo', dict(a='1', b='2'))
        assert parse_header('foo;  a=1;b="2"') == ('foo', dict(a='1', b='2'))
        assert parse_header('foo') == ('foo', {})

    def check_parse_content_disposition(self):
        assert parse_content_disposition(
            'form-data; name=a;filename=b') == ('a', 'b')
        assert parse_content_disposition('form-data; name=a;') == ('a', None)
        raises(ValueError, parse_content_disposition, 'form-data; filename=a;')

    def check_parse_query(self):
        charset = 'iso-8859-1'
        assert parse_query('', charset) == {}
        charset = 'utf-8'
        assert parse_query('a=b', charset) == dict(a='b')
        assert parse_query('a=b&b=c', charset) == dict(a='b', b='c')
        assert parse_query('a=b&a=c', charset) == dict(a=['b', 'c'])
        assert parse_query('a=b&c', charset) == dict(a='b',c='')
        assert parse_query('a=b&c=', charset) == dict(a='b',c='')
        assert parse_query('a=b&=c', charset) == {'a' : 'b', '' : 'c'}
        assert parse_query('=', charset) == {'' : ''}
        raises(ValueError, parse_query, '\xff', 'ascii')
        raises(LookupError, parse_query, '\xff', 'bogus')

    def check_scheme(self):
        request = HTTPRequest(StringIO(), {})
        assert request.get_scheme() == 'http'
        request = HTTPRequest(StringIO(), dict(HTTPS='on'))
        assert request.get_scheme() == 'https'
        request = HTTPRequest(StringIO(), dict(HTTPS='ON'))
        assert request.get_scheme() == 'https'

    def check_cookies(self):
        request = HTTPRequest(StringIO(), {})
        assert request.get_cookies() == {}
        request = HTTPRequest(StringIO(), dict(HTTP_COOKIE='1'))
        assert request.get_cookies() == {'1': ''}
        request = HTTPRequest(StringIO(), dict(HTTP_COOKIE='1;u=a'))
        assert request.get_cookies() == {'1' : '', 'u' : 'a'}
        request = HTTPRequest(StringIO(), dict(HTTP_COOKIE='1;u="a"'))
        assert request.get_cookies() == {'1' : '', 'u' : 'a'}
        assert request.get_cookie('u') == 'a'
        request = HTTPRequest(StringIO(),
                              dict(HTTP_COOKIE='1;$Path=/;u="a"'))
        assert request.get_cookies() == {'1' : '', 'u' : 'a'}

    def check_process_inputs(self):
        request = HTTPRequest(StringIO(), {})
        request.process_inputs()
        assert request.get_fields() == {}

    def check_process_simple_query(self):
        request = HTTPRequest(StringIO(), dict(QUERY_STRING='a=b'))
        request.process_inputs()
        assert request.get_fields() == { 'a': 'b' }

    def check_bogus_length(self):
        request = HTTPRequest(StringIO(), dict(CONTENT_LENGTH='a'))
        raises(ValueError, request.process_inputs)

    def check_unknown_type(self):
        request = HTTPRequest(StringIO(), dict(CONTENT_TYPE='bogus'))
        request.process_inputs()

    def check_empty(self):
        request = HTTPRequest(
            StringIO(),
            dict(CONTENT_TYPE='application/x-www-form-urlencoded',
                 CONTENT_LENGTH=0))
        request.process_inputs()

    def check_short(self):
        request = HTTPRequest(
            StringIO(), # short
            dict(CONTENT_TYPE='application/x-www-form-urlencoded',
                 CONTENT_LENGTH=1))
        raises(ValueError, request.process_inputs)

    def check_short_multipart(self):
        s = '\r\n--x--\r\nok\r\n--x--\r\n'
        request = HTTPRequest(
            StringIO(s),
            dict(CONTENT_TYPE='multipart/form-data;boundary="x"',
                 CONTENT_LENGTH=len(s)+1))
        raises(ValueError, request.process_inputs)

    def check_boundary_not_in_content(self):
        s = '\r\n--x--\r\nok\r\n--x--\r\n'
        request = HTTPRequest(
            StringIO(s),
            dict(CONTENT_TYPE='multipart/form-data;boundary="z"',
                 CONTENT_LENGTH=len(s)))
        raises(ValueError, request.process_inputs)


    def check_missing_boundary(self):
        s = '\r\n--x--\r\nok\r\n--x--\r\n'
        request = HTTPRequest(
            StringIO(s),
            dict(CONTENT_TYPE='multipart/form-data', # missing boundary
                 CONTENT_LENGTH=len(s)))
        raises(ValueError, request.process_inputs)

    def check_multipart_form(self):
        s = ('\r\n--x\r\n'
             'Content-disposition: form-data; name=a;filename=b\r\n\r\n'
             'ok\r\n--x--\r\n')
        request = HTTPRequest(
            StringIO(s),
            dict(CONTENT_TYPE='multipart/form-data;boundary=x',
                 CONTENT_LENGTH=len(s)))
        request.process_inputs()

    def check_multipart_form_without_filename(self):
        s = ('\r\n--x\r\n'
             'Content-disposition: form-data; name=a\r\n\r\n'
             'ok\r\n--x--\r\n')
        request = HTTPRequest(
            StringIO(s),
            dict(CONTENT_TYPE='multipart/form-data;boundary=x',
                 CONTENT_LENGTH=len(s)))
        request.process_inputs()

    def check_content_disposition_header_missing(self):
        s = ('\r\n--x\r\n'
             'ok\r\n--x--\r\n')
        request = HTTPRequest(
            StringIO(s),
            dict(CONTENT_TYPE='multipart/form-data;boundary=x',
                 CONTENT_LENGTH=len(s)))
        try:
            request.process_inputs()
            assert 0
        except ValueError, e:
            assert str(e) == 'expected Content-Disposition header'

    def check_content_disposition_header_without_name(self):
        s = ('\r\n--x\r\n'
             'Content-disposition: form-data; filename=b\r\n'
             'Content-type: text/plain; charset=utf-8\r\n\r\n'
             'ok\r\n--x--\r\n')
        request = HTTPRequest(
            StringIO(s),
            dict(CONTENT_TYPE='multipart/form-data;boundary=x',
                 CONTENT_LENGTH=len(s)))
        raises(ValueError, request.process_inputs)

    def check_content_disposition_header_not_form_data(self):
        s = ('\r\n--x\r\n'
             'Content-disposition: form-bogus; name=a; filename=b\r\n\r\n'
             'ok\r\n--x--\r\n')
        request = HTTPRequest(
            StringIO(s),
            dict(CONTENT_TYPE='multipart/form-data;boundary=x',
                 CONTENT_LENGTH=len(s)))
        raises(ValueError, request.process_inputs)

    def check_lineinput(self):
        line_input = LineInput(StringIO('ok\r\n'), 4)
        s = line_input.readline(3)
        assert s == 'ok'
        s = '--x--\r\nok\r\n--x--\r\n'
        line_input = LineInput(StringIO(s), len(s))
        assert line_input.readline() == '--x--\r\n'
        assert line_input.readline() == 'ok\r\n'
        assert line_input.readline() == '--x--\r\n'
        assert line_input.readline() == ''

    def check_mimeinput(self):
        line_input = LineInput(StringIO('ok\r\n'), 4)
        assert line_input.readline() == 'ok\r\n'
        s = '--x--\r\nok\r\n--x--\r\n'
        line_input = LineInput(StringIO(s), len(s))
        assert line_input.readline() == '--x--\r\n'
        assert line_input.readline() == 'ok\r\n'
        assert line_input.readline() == '--x--\r\n'
        assert line_input.readline() == ''
        line_input = LineInput(StringIO(s), len(s) + 1)
        try:
            for line in range(6):
                line_input.readline()
            assert 0
        except EOFError:
            pass

    def check_get_server(self):
        request = HTTPRequest(StringIO(), dict(HTTP_HOST='a'))
        assert request.get_server() == 'a'
        request = HTTPRequest(StringIO(), dict(SERVER_NAME='b',
                                               SERVER_PORT='80'))
        assert request.get_server() == 'b'
        request = HTTPRequest(StringIO(), dict(SERVER_NAME='b',
                                               SERVER_PORT='83'))
        assert request.get_server() == 'b:83'

    def check_get_header(self):
        request = HTTPRequest(StringIO(), dict(SERVER_NAME='b',
                                               HTTP_HOST='c'))
        assert request.get_header('SERVER_NAME') == 'b'
        assert request.get_header('HOST') == 'c'

    def check_get_field(self):
        request = HTTPRequest(StringIO(), dict(SERVER_NAME='b'))
        assert request.get_field('a') == None

    def check_get_method(self):
        request = HTTPRequest(StringIO(), {})
        assert request.get_method() == 'GET'
        request = HTTPRequest(StringIO(), dict(REQUEST_METHOD='POST'))
        assert request.get_method() == 'POST'

    def check_get_path(self):
        request = HTTPRequest(StringIO(), {})
        assert request.get_path() == '/'
        request = HTTPRequest(StringIO(), dict(PATH_INFO='/'))
        assert request.get_path() == '/'
        request = HTTPRequest(StringIO(), dict(PATH_INFO='/a/b/c/d'))
        assert request.get_path() == '/a/b/c/d'
        assert request.get_path(1) == '/a/b/c'
        assert request.get_path(2) == '/a/b'
        assert request.get_path(3) == '/a'
        assert request.get_path(4) == ''
        assert request.get_path(-1) == '/a'
        assert request.get_path(-2) == '/a/b'
        assert request.get_path(-3) == '/a/b/c'
        assert request.get_path(-4) == '/a/b/c/d'
        raises(ValueError, request.get_path, -5)

    def check_get_encoding(self):
        request = HTTPRequest(
            StringIO(),  dict(HTTP_ACCEPT_ENCODING='gzip,deflate,*'))
        assert request.get_encoding(['gzip']) == 'gzip'
        assert request.get_encoding([]) == None

    def check_accepted_types(self):
        request = HTTPRequest(
            StringIO(),  dict(HTTP_ACCEPT='image/png,*/*;q=0.5'))
        assert request.get_accepted_types() == {'image/png' : 1.0,
                                                '*/*' : 0.5 }
        request = HTTPRequest(
            StringIO(),  dict(HTTP_ACCEPT='image/png,*/*;q=.9.9'))
        assert request.get_accepted_types() == {'image/png' : 1.0}

    def check_safe_filename(self):
        assert make_safe_filename('foo') == 'foo'

    def check_upload(self):
        upload = Upload('c:\\\\a\\b')
        upload = Upload('c:a')
        upload = Upload('/a/b')
        upload = Upload('')
        upload = Upload('a')
        upload.receive('\n'.join('asdf'))
        upload.read(1)
        upload.readlines()
        remaining = ''.join(upload)
        upload.close()


class ParseCookiesTest (UTest):

    def check_basic(self):
        assert parse_cookies('a') == {'a': ''}
        assert parse_cookies('a = ') == {'a': ''}
        assert parse_cookies('a = ""') == {'a': ''}
        assert parse_cookies(r'a = "\""') == {'a': '"'}
        assert parse_cookies('a, b; c') == {'a': '', 'b': '', 'c': ''}
        assert parse_cookies('a, b=1') == {'a': '', 'b': '1'}
        assert parse_cookies('a = ";, \t";') == {'a': ';, \t'}

    def check_rfc2109_example(self):
        s = ('$Version="1"; Customer="WILE_E_COYOTE"; $Path="/acme"; '
             'Part_Number="Rocket_Launcher_0001"; $Path="/acme"')
        result = {'Customer': 'WILE_E_COYOTE',
                  'Part_Number': 'Rocket_Launcher_0001',
                 }
        assert parse_cookies(s) == result

    def check_other(self):
        s = 'PREF=ID=0a06b1:TM=108:LM=1069:C2COFF=1:S=ETXrcU'
        result = {'PREF': 'ID=0a06b1:TM=108:LM=1069:C2COFF=1:S=ETXrcU'}
        assert parse_cookies(s) == result
        s = 'pageColor=White; pageWidth=990; fontSize=12; fontFace=1; E=E'
        assert parse_cookies(s) == {'pageColor': 'White',
                                    'pageWidth': '990',
                                    'fontSize': '12',
                                    'fontFace': '1',
                                    'E': 'E'}
        s = 'userid="joe"; QX_session="58a3ced39dcd0d"'
        assert parse_cookies(s) == {'userid': 'joe',
                                    'QX_session': '58a3ced39dcd0d'}

    def check_invalid(self):
        parse_cookies('a="123')
        parse_cookies('a=123"')

if __name__ == '__main__':
    Test()
    ParseCookiesTest()
