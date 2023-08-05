"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/pub/test/utest_common.py $
$Id: utest_common.py 27231 2005-08-19 01:17:30Z dbinger $
"""
from qp.pub.common import get_publisher, get_request, get_hit, not_found
from qp.pub.common import get_response, get_path, redirect, clear_publisher
from qp.pub.common import get_user, get_session, get_path, redirect, not_found
from qp.pub.common import header, footer, page, respond, ensure_signed_in
from qp.pub.hit import Hit
from qp.pub.publish import Publisher, RespondNow
from qp.pub.user import User
from qp.pub.session import Session
from qpy import h8
from sancho.utest import UTest


class Test(UTest):

    def _pre(self):
        clear_publisher()

    def _post(self):
        clear_publisher()

    def check_common(self):
        publisher = Publisher()
        assert publisher == get_publisher()
        try:
            get_request()
            assert 0
        except AttributeError:
            pass
        hit = Hit(None, dict(SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w'))
        publisher.set_hit(hit)
        assert get_hit() is hit
        assert get_request() is hit.get_request()
        assert get_response() is hit.get_response()
        get_hit().set_session(publisher.create_session())
        assert isinstance(get_session(), Session), repr(get_session())
        assert isinstance(get_user(), User)
        assert not get_user()
        assert get_path() == '/a'
        try:
            redirect('there', permanent=True)
            assert 0
        except RespondNow:
            assert get_response().get_status_code() == 301
        try:
            not_found()
            assert 0
        except RespondNow:
            assert get_response().get_status_code() == 404
        assert isinstance(header('ok'), h8)
        assert isinstance(footer(), h8)
        assert isinstance(page('ok'), h8)
        try:
            respond('ok')
            assert 0
        except RespondNow:
            assert get_response().get_status_code() == 400
        try:
            respond('ok', status=200)
            assert 0
        except RespondNow:
            assert get_response().get_status_code() == 200
        try:
            ensure_signed_in()
            assert 0
        except RespondNow:
            assert get_response().get_status_code() == 302

if __name__ == '__main__':
    Test()
