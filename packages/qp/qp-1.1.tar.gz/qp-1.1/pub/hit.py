"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/pub/hit.py $
$Id: hit.py 27422 2005-09-14 19:13:54Z dbinger $
"""
from datetime import datetime
from qp.http.request import HTTPRequest
from qp.http.response import HTTPResponse
from qp.pub.session import Session
from qp.lib.spec import add_getters, spec, specify

class Hit (object):

    request_is = HTTPRequest
    response_is = HTTPResponse
    session_is = Session
    time_is = spec(
        datetime,
        "utc time of the creation of the Hit.")
    info_is = spec(
        dict,
        "A place for application code to squirrel away things as needed "
        "while processing the request.")

    def __init__(self, input_stream, cgi_environment):
        self.request = self.request_is(input_stream, cgi_environment)
        self.init_response()
        self.time = datetime.utcnow()
        self.info = {}

    def init_response(self):
        self.response = self.response_is()
        self.response.set_compress(bool(self.request.get_encoding(['gzip'])))

    def set_session(self, session):
        specify(self, session=session)

add_getters(Hit)


