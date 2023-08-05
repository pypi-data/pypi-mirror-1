"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/mail/test/utest_rfc822_mailbox.py $
$Id: utest_rfc822_mailbox.py 26815 2005-05-17 11:07:27Z dbinger $
"""
from sancho.utest import UTest, raises
from qp.mail.rfc822_mailbox import rfc822_mailbox


class Test(UTest):

    def a(self):
        assert rfc822_mailbox(None) is None
        result = rfc822_mailbox('me')
        assert result.format() == 'me'
        assert result is rfc822_mailbox(result)
        assert raises(TypeError, rfc822_mailbox, 1)
        assert rfc822_mailbox(('a@b', 'bo')).format() == 'bo <a@b>'
        assert rfc822_mailbox(('a@b', 1)).format() == '1 <a@b>'
        assert raises(TypeError, rfc822_mailbox, (1, 2, 3))
        assert rfc822_mailbox(('a@b', 'b "bo" ba')).format() == (
            r'"b \"bo\" ba" <a@b>')

if __name__ == '__main__':
    Test()
