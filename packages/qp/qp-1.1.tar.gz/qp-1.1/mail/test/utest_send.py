"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/mail/test/utest_send.py $
$Id: utest_send.py 26833 2005-05-23 00:50:41Z dbinger $
"""
from os import getuid, environ
from pwd import getpwuid
from sancho.utest import UTest
from socket import getfqdn
from qp.mail.send import Email
from qp.pub.common import clear_publisher, get_publisher
from qp.pub.publish import Publisher


class Test(UTest):

    def _pre(self):
        Publisher()

    def _post(self):
        clear_publisher()

    def a(self):
        e = Email()
        webmaster = get_publisher().get_webmaster_address()
        assert e.format_headers() == ('From: %(webmaster)s\n'
                                      'Subject: \n'
                                      'To: %(webmaster)s\n\n') % locals()
        e.set_to(['al', 'bo', 'ci'])
        e.set_subject('the subject')
        assert e.format_headers() == ('From: %(webmaster)s\n'
                                      'Subject: the subject\n'
                                      'To: al,\n'
                                      '    bo,\n'
                                      '    ci\n'
                                      'Precedence: junk\n'
                                      'X-No-Archive: yes\n\n') % locals()
        e.set_extra_headers(['Spam: yes', 'Ham: no'])
        e.set_reply_to([webmaster])
        assert e.format_headers() == ('From: %(webmaster)s\n'
                                      'Subject: the subject\n'
                                      'To: al,\n'
                                      '    bo,\n'
                                      '    ci\n'
                                      'Reply-To: %(webmaster)s\n'
                                      'Spam: yes\n'
                                      'Ham: no\n'
                                      'Precedence: junk\n'
                                      'X-No-Archive: yes\n\n') % locals()

    def b(self):
        e = Email()
        e.set_to([str(x) for x in range(30)])
        e.set_cc('a')
        webmaster = get_publisher().get_webmaster_address()
        assert e.format_headers() == ('From: %(webmaster)s\n'
                                      'Subject: \n'
                                      'To: (long recipient list suppressed) : ;\n'
                                      'Cc: a\n'
                                      'Precedence: junk\n'
                                      'X-No-Archive: yes\n\n') % locals()
    def c(self):
        user = "%s@%s" % (getpwuid(getuid()).pw_name, getfqdn())
        e = Email()
        e.set_to([user])
        assert get_publisher().is_email_enabled() == False
        if not environ.get('TESTEMAIL'):
            return
        assert e.send() == False
        def is_email_enabled():
            return True
        get_publisher().is_email_enabled = is_email_enabled
        e.set_body('This was sent when %s ran utest_send.py' % user)
        e.set_subject('utest_send.py')
        assert e.send() == True
        def get_debug_address():
            return None
        get_publisher().get_debug_address = get_debug_address
        f = Email()
        f.set_to([user])
        f.set_subject('utest_send.py')
        f.set_body('This was also sent when %s ran utest_send.py '
                   '\n(with a debug_address).\n' %
                   user)
        assert f.send() == True

if __name__ == '__main__':
    Test()
