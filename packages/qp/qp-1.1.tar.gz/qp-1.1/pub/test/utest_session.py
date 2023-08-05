"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/pub/test/utest_publish.py $
$Id: utest_publish.py 26445 2005-03-31 18:36:58Z dbinger $
"""
from datetime import timedelta
from qp.pub.user import User
from qp.pub.hit import Hit
from qp.pub.common import clear_publisher
from qp.pub.session import Session
from qp.pub.publish import Publisher
from sancho.utest import UTest

class Test(UTest):

    def _pre(self):
        clear_publisher()

    def _post(self):
        clear_publisher()

    def check_a(self):
        publisher = Publisher()
        publisher.set_hit(Hit(None, dict(REMOTE_ADDR='1.1.1.1')))
        user = User('a')
        session = Session()
        assert session.get_remote_address() == '1.1.1.1'
        assert session.is_valid()
        publisher.set_hit(Hit(None, dict(REMOTE_ADDR='1.1.1.2')))
        assert not session.is_valid()
        assert session.get_owner().get_id() == ''
        assert session.get_authentication_time() is None
        assert not session.needs_saving()
        session.set_authenticated(user)
        assert session.needs_saving()
        assert session.get_effective_user() is user
        assert session.get_owner() is user
        assert session.get_authentication_time() is not None
        user2 = User('b')
        session.set_effective_user(user2)
        assert session.get_effective_user() is user2
        assert session.get_owner() is user
        session._p_oid = 42 # as if it had been saved
        assert not session.needs_saving()
        assert session.is_valid()
        session.lease_time = timedelta(0)
        assert not session.is_valid()


if __name__ == '__main__':
    Test()
