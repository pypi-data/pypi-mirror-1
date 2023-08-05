"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/pub/test/utest_publish.py $
$Id: utest_publish.py 27268 2005-09-01 16:05:10Z dbinger $
"""
from qp.pub.common import clear_publisher
from qp.pub.hit import Hit
from qp.pub.publish import Publisher
from qp.pub.user import User, compute_digest
from sancho.utest import UTest

class Test(UTest):

    def _pre(self):
        clear_publisher()

    def _post(self):
        clear_publisher()

    def check_base(self):
        class Pub(Publisher):
            pass
        publisher = Pub()
        hit = Hit(None, dict(SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w'))
        publisher.process_hit(hit)

    def check_not_found(self):
        class Pub(Publisher):
            def fill_response(self):
                self.not_found()
        publisher = Pub()
        hit = Hit(None, dict(SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w'))
        publisher.process_hit(hit)
        print hit.get_response().get_status_code()
        assert hit.get_response().get_status_code() == 404

    def check_permanent_redirect(self):
        class Pub(Publisher):
            def fill_response(self):
                self.redirect('', permanent=True)
        publisher = Pub()
        hit = Hit(None, dict(SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w'))
        publisher.process_hit(hit)
        print hit.get_response().get_status_code()
        assert hit.get_response().get_status_code() == 301

    def check_temporary_redirect(self):
        class Pub(Publisher):
            def fill_response(self):
                self.redirect('')
        publisher = Pub()
        hit = Hit(None, dict(SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w'))
        publisher.process_hit(hit)
        print hit.get_response().get_status_code()
        assert hit.get_response().get_status_code() == 302

    def check_retry(self):
        class Pub(Publisher):
            def fill_response(self):
                assert 0
            def is_terminal_exception(self):
                return False
        publisher = Pub()
        hit = Hit(None, dict(SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w'))
        publisher.process_hit(hit)

    def check_display_exceptions(self):
        class Pub(Publisher):
            def fill_response(self):
                assert 0
            def display_exceptions(self):
                return True
        publisher = Pub()
        hit = Hit(None, dict(SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w',
                             QUERY_STRING='how'))
        publisher.process_hit(hit)

    def check_hide_exceptions(self):
        class Pub(Publisher):
            def fill_response(self):
                assert 0
        publisher = Pub()
        hit = Hit(None, dict(SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w',
                             QUERY_STRING='how'))
        publisher.process_hit(hit)

    def check_empty_path_info(self):
        publisher = Publisher()
        hit = Hit(None, dict(SCRIPT_NAME='', PATH_INFO='', SERVER_NAME='w'))
        publisher.process_hit(hit)
        print hit.get_response().get_status_code()
        assert hit.get_response().get_header('Location') == 'http://w/'
        assert hit.get_response().get_status_code() == 301

    def check_path_info_with_no_slash(self):
        publisher = Publisher()
        hit = Hit(None, dict(SCRIPT_NAME='', PATH_INFO='a', SERVER_NAME='w'))
        publisher.process_hit(hit)
        print hit.get_response().get_status_code()
        print hit.get_response().get_header('Location')
        assert hit.get_response().get_header('Location') == 'http://w/a'
        assert hit.get_response().get_status_code() == 301

    def check_ensure_signed_in_using_digest(self):
        publisher = Publisher()
        hit = Hit(None, dict(SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w'))
        def fill():
            publisher.ensure_signed_in_using_digest()
        def nothing():
            pass
        publisher.fill_response_with_session_present = fill
        publisher.abort = nothing
        publisher.commit = nothing
        publisher.process_hit(hit)
        assert hit.get_response().get_header('Location').startswith('https')
        assert hit.get_response().get_status_code() == 302
        hit = Hit(None, dict(SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w',
                             HTTPS="On"))
        publisher.process_hit(hit)
        assert hit.get_response().get_status_code() == 401
        challenge = hit.get_response().get_header('WWW-Authenticate')
        realm = publisher.get_site().get_name()
        nonce = publisher.get_users()[''].get_tokens().tokens[0]
        expected = ('Digest realm="%s", nonce="%s", opaque="0%s", stale=false, '
                    'algorithm=MD5, qop="auth"' % (realm, nonce, nonce))
        assert challenge == expected
        auth = "not_digest a b c d e"
        hit = Hit(None, dict(
            SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w',
            HTTPS="On", HTTP_AUTHORIZATION=auth))
        publisher.process_hit(hit)
        assert hit.get_response().get_status_code() == 401
        auth = "Digest a b c d e"  # no username
        hit = Hit(None, dict(
            SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w',
            HTTPS="On", HTTP_AUTHORIZATION=auth))
        publisher.process_hit(hit)
        assert hit.get_response().get_status_code() == 401
        auth = 'Digest username="db" b c d e' # no-nonce
        hit = Hit(None, dict(
            SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w',
            HTTPS="On", HTTP_AUTHORIZATION=auth))
        publisher.process_hit(hit)
        assert hit.get_response().get_status_code() == 401

        db =User('db')
        publisher.get_users()['db'] = db
        auth = 'Digest username="db", nonce="%s", c, d, e,' % 'bogus'
        hit = Hit(None, dict(
            SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w',
            HTTPS="On", HTTP_AUTHORIZATION=auth))
        publisher.process_hit(hit)
        assert hit.get_response().get_status_code() == 401

        nonce = publisher.get_users()[''].get_tokens().new_token()
        auth = 'Digest username="db", nonce="%s", c, d, e,' % nonce
        hit = Hit(None, dict(
            SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w',
            HTTPS="On", HTTP_AUTHORIZATION=auth))
        publisher.process_hit(hit)
        assert hit.get_response().get_status_code() == 401

        nonce = publisher.get_users()[''].get_tokens().new_token()
        auth = 'Digest username="db", nonce="%s", realm="%s", d, e,' % (
            nonce, realm)
        hit = Hit(None, dict(
            SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w',
            HTTPS="On", HTTP_AUTHORIZATION=auth))
        publisher.process_hit(hit)
        assert hit.get_response().get_status_code() == 401

        nonce = publisher.get_users()[''].get_tokens().new_token()
        auth = ('Digest username="db", ' +
                ('response="%s", ' % ('4' * 32)) +
                ('nonce="%s", realm="%s", , e,' % (
            nonce, realm)))
        hit = Hit(None, dict(
            SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w',
            HTTPS="On", HTTP_AUTHORIZATION=auth))
        publisher.process_hit(hit)
        assert hit.get_response().get_status_code() == 401

        db.set_password('s')
        nonce = publisher.get_users()[''].get_tokens().new_token()
        auth = ('Digest username="db", ' +
                ('response="%s", ' % ('4' * 32)) +
                ('nonce="%s", realm="%s", , e,' % (
            nonce, realm)))
        hit = Hit(None, dict(
            SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w',
            HTTPS="On", HTTP_AUTHORIZATION=auth))
        publisher.process_hit(hit)
        assert hit.get_response().get_status_code() == 401

        user_digest = db.get_digester().get_digest(realm)
        nonce = publisher.get_users()[''].get_tokens().new_token()
        response = compute_digest(
            user_digest, nonce, '01', 'bar', 'auth',
            compute_digest('GET', '/a'))
        auth = ('Digest username="db", uri="/a", ' +
                ('response="%s", ' % response) +
                ('cnonce="bar", nc=01, qop=auth, ') +
                ('nonce="%s", realm="%s" ' % (
            nonce, realm)))
        hit = Hit(None, dict(
            REQUEST_METHOD="GET",
            SCRIPT_NAME='', PATH_INFO='/a', SERVER_NAME='w',
            HTTPS="On", HTTP_AUTHORIZATION=auth))
        publisher.process_hit(hit)
        assert hit.get_response().get_status_code() != 401





if __name__ == '__main__':
    Test()
