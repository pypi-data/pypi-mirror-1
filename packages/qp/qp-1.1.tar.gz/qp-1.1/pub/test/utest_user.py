"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/pub/test/utest_publish.py $
$Id: utest_publish.py 26445 2005-03-31 18:36:58Z dbinger $
"""
from qp.pub.common import clear_publisher
from qp.pub.publish import Publisher
from qp.pub.user import User, Permissions
from sancho.utest import UTest

class Test(UTest):

    def _pre(self):
        clear_publisher()

    def _post(self):
        clear_publisher()

    def check_a(self):
        publisher = Publisher()
        user = User('a')
        assert user
        assert not User('')
        assert user.get_id() == 'a'
        assert user.get_digester().get_realms() == []
        user.set_password('foo')
        assert user.get_digester().get_realms()
        assert user.has_password('foo')
        assert not user.has_password('bah')
        user.set_password('')
        assert user.get_digester().get_realms() == []
        assert isinstance(user.get_permissions(), Permissions)
        assert not user.is_granted('power')
        assert not user.is_admin()
        try:
            user.get_permissions().grant('administrator', None)
            assert 0
        except TypeError:
            pass
        user.get_permissions().grant('administrator', user)
        assert not user.is_admin()
        user.get_permissions().ungrant('administrator', user)
        user.get_permissions().grant('administrator', user)
        user.get_permissions().grant('administrator', True)
        assert user.is_admin()
        user.get_permissions().ungrant('administrator', True)
        assert not user.is_admin()
        user.get_permissions().grant('power', user)
        assert not user.is_granted('power')
        assert user.is_granted('power', user)
        token = user.get_tokens().new_token()
        assert token in user.get_tokens()
        user.get_tokens().remove(token)
        assert token not in user.get_tokens()
        user.get_tokens().clear()

if __name__ == '__main__':
    Test()
