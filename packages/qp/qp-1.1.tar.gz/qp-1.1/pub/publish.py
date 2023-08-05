"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/pub/publish.py $
$Id: publish.py 27643 2005-10-29 20:42:08Z dbinger $
"""
from datetime import datetime
from durus.btree import BTree
from durus.connection import Connection
from durus.error import ConflictError
from durus.file_storage import TempFileStorage
from os import getpid
from pprint import pformat
from qp.fill.directory import Directory
from qp.fill.form import Form
from qp.lib.site import Site
from qp.lib.spec import spec, add_getters
from qp.lib.util import randbytes
from qp.mail.send import Email
from qp.pub.common import get_hit, set_publisher, get_request, get_response
from qp.pub.common import get_user, get_session
from qp.pub.hit import Hit
from qp.pub.session import Session
from qp.pub.user import User, compute_digest
from qpy import h8
from socket import getfqdn
from sys import exc_info
from traceback import format_exception
from urlparse import urljoin
import binascii
import qp.lib.site

class RespondNow (Exception):
    """
    This Exception is used to break out of the path traversal.
    The Publisher expects the contents of the response to be
    set before this exception is raised.
    """

class Publisher (object):

    connection_is = spec(
        Connection,
        "the Durus Connection")
    site_is = spec(
        Site,
        "the QP Site")
    root_directory_is = spec(
        Directory,
        "The root directory")
    hit_is = spec(
        Hit,
        "The Hit (Request, Response, Session, etc.) currently being "
        "processed, or None.")

    def __init__(self, connection=None, site=None):
        set_publisher(self)
        self.connection = connection or Connection(TempFileStorage())
        self.set_hit(None)
        self.ensure_initialized()
        self.site = site or qp.lib.site.Site.get_sites().values()[0]
        self.root_directory = self.site.get_root_directory_class()()

    def get_webmaster_address(self):
        """() -> email_address:str
        """
        return 'webmaster@%s' % getfqdn()

    def get_debug_address(self):
        """() -> email_address:str|None

        If this returns a nonempty string, the qp.mail.send.Email
        class will use this as the smtp recipient for all messages it
        sends.  If you want email sent by that class to go to the normal
        recipients, you must override this to return None.
        """
        return self.get_webmaster_address()

    def is_email_enabled(self):
        """() -> bool
        The qp.mail.send.Email class will never send any email unless this
        returns true.  If you want any email sent (using that class),
        you must override this to return True.
        """
        return False

    def get_smtp_server(self):
        """() -> str
        """
        return 'localhost'

    def ensure_initialized(self):
        """
        Make sure that database root has sessions and users mappings.
        If not, make them and commit().
        """
        if self.get_sessions() is None:
            self.get_root()['sessions'] = BTree()
            self.commit()
        if self.get_users() is None:
            self.get_root()['users'] = BTree()
            self.get_root()['users'][''] = self.create_user('') # null user
            self.commit()

    def commit(self):
        """Commit changes to the database."""
        self.get_connection().commit()

    def abort(self):
        """
        Make sure that the connection has no uncommitted object state.
        """
        self.get_connection().abort()

    def get_root(self):
        """() -> PersistentDict
        Return the root object of the database.
        """
        return self.get_connection().get_root()

    def get_sessions(self):
        """() -> BTree
        Return the session mapping.
        """
        return self.get_root().get('sessions')

    def get_users(self):
        """() -> BTree
        Return the user mapping.
        """
        return self.get_root().get('users')

    def set_hit(self, hit):
        """(hit:Hit)
        Set the current Hit.
        """
        self.hit = hit

    def respond_now(self):
        """
        This breaks out of path traversal.  When this is called, the
        response should have already been prepared for sending.
        """
        raise RespondNow

    def process_hit(self, hit):
        """(hit:Hit)
        This processes the request on the hit and sets the response
        on the hit.  It handles conflict errors and commits changes
        when there are no error exceptions.
        """
        self.set_hit(hit)
        try:
            hit.get_request().process_inputs()
            for attempt in range(5):
                try:
                    hit.init_response()
                    self.abort()
                    try:
                        self.fill_response()
                    except RespondNow:
                        pass
                    self.log_hit()
                    self.commit()
                    return
                except ConflictError:
                    self.log_exception()
                    self.abort()
            else:
                raise RuntimeError("too many Conflict errors")
        except:
            self.handle_exception()
            self.log_hit()
            self.abort()

    def create_user(self, user_id):
        return User(user_id)

    def create_session(self):
        return Session()

    def fill_response(self):
        """
        Use the request to prepare the response.
        This method takes care of session management, and calls the
        fill_response_with_session_present() method to do the rest.
        """
        cookie_name = self.get_site().get_name()
        cookie = get_request().get_cookie(cookie_name)
        session = self.get_sessions().get(cookie)
        if session and not session.is_valid():
            del self.get_sessions()[cookie]
            session = None
        if session is None:
            session = self.create_session()
        self.get_hit().set_session(session)
        try:
            self.fill_response_with_session_present()
        finally:
            session = self.get_hit().get_session()
            if session.needs_saving():
                cookie = randbytes(8)
                self.get_sessions()[cookie] = session
                get_response().set_cookie(
                    cookie_name, cookie,
                    path=get_request().get_script_name(),
                    secure=(get_request().get_scheme() == 'https'))

    def handle_exception(self):
        """
        This is called when there is an error exception while processing
        a request.
        """
        self.log_exception()
        if exc_info()[0] is SystemExit:
            raise
        self.get_hit().init_response()
        self.get_hit().get_response().set_status(500)
        if self.display_exceptions():
            self.display_exception()
        else:
            self.hide_exception()

    def secure(self):
        """If the scheme is not https, redirect so that it will be.
        """
        if get_request().get_scheme() != 'https':
            self.redirect(self.complete_url('', secure=True))

    def complete_url(self, path, secure=False):
        """(path:str, secure:bool=False) -> str
        Turn path into a complete url to this publisher, changing the
        scheme to https if secure is True.
        """
        s = str(path)
        if not secure and s.startswith('http://'):
            return s
        if s.startswith('https://'):
            return s
        if s.startswith('/'):
            complete_path = get_request().get_script_name() + s
        else:
            complete_path = s
        if secure:
            host, port = self.get_site().get_https_address()
            if port == 443:
                address = str(host)
            else:
                address = "%s:%s" % (host, port)
            base = 'https://%s%s' % (address,
                                     get_request().get_path_query())
        else:
            base = get_request().get_url()
        return urljoin(base, complete_path)

    def redirect(self, location, permanent=False):
        """(location:str, permanent:boolean=False)
        This prepares a redirect response and uses an exception
        to break out of the path traversal and return the response
        immediately.
        """
        if permanent:
            status = 301
        else:
            status = 302
        self.get_hit().init_response()
        response = self.get_hit().get_response()
        response.set_status(status)
        response.set_header('location', self.complete_url(location))
        response.set_content_type('text/plain', 'iso-8859-1')
        response.set_body(
            "Your browser should have redirected you to %s" % location)
        self.respond_now()

    def not_found(self, body=None):
        """(body:str)
        This prepares a 404 response and uses an exception
        to break out of the path traversal and return the response
        immediately.
        """
        self.respond('Not Found', body or 'That page is not here.', status=404)

    def log_exception(self):
        """
        This is called to record an error exception.
        """
        report = self.format_exception_report()
        print report
        self.send_to_administrator(report)

    def display_exception(self):
        """
        This places an exception report in the response.
        """
        get_hit().get_response().set_body(self.format_exception_report())
        get_hit().get_response().set_content_type('text/plain', 'iso-8859-1')

    def log_hit(self):
        """
        This logs the processing of a request.
        """
        hit = get_hit()
        code = hit.get_response().get_status_code()
        duration = str(datetime.utcnow() - hit.get_time()).lstrip('0:')
        request = hit.get_request()
        path_query = request.get_path_query()
        method = request.get_method()
        remote = request.get_remote_address()
        if request.get_scheme() == 'https':
            ssl = "SSL "
        else:
            ssl = ""
        agent = request.get_header('user-agent', '-').replace(' ', '_')
        referer = request.get_header('http-referer') or '-'
        time = hit.get_time().strftime("%m/%d %H:%M:%S")
        pid = getpid()
        msg = ('%(time)s %(code)s %(duration)s %(remote)s %(pid)s '
               '%(ssl)s%(method)s %(path_query)s %(agent)s %(referer)s' %
               locals())
        print msg

    def format_exception_report(self):
        """() -> str
        This returns a string that reports an error exception.
        """
        hit = get_hit()
        request = hit.get_request()
        report = ''.join(format_exception(*exc_info()))
        report += '\npath = %r' % request.get_path()
        report += '\nquery= %r' % request.get_query()
        report += '\n\ninfo:\n' + pformat(hit.get_info())
        report += '\n\nvars(request):\n' + pformat(vars(request))
        report += '\n'
        return report

    def hide_exception(self):
        """
        This sets the response to be a page that can be shown when there
        is an error exception, but you don't want to expose the details
        of the exception.
        """
        get_hit().get_response().set_status(500)
        get_hit().get_response().set_body(
            self.page('Regrets',
                      h8("<p>This page is temporarily unavailable.</p>"
                         "<p>Please try again later.</p>")))

    def fill_response_with_session_present(self):
        """
        Traverse the components, set the response body.
        """
        path = get_request().get_path_info()
        if path[:1] != '/':
            return self.redirect('/' + path, permanent=True)
        components = path[1:].split('/')
        body = self.get_root_directory()._q_traverse(components)
        get_response().set_body(body)

    def send_to_administrator(self, message):
        """(message:str)
        """
        email = Email()
        email.set_subject(self.get_site().get_name())
        email.set_body(message)
        if email.send():
            print '\nemail:sent'

    def display_exceptions(self):
        """() -> bool
        Should the details of error exceptions be reported in responses?
        """
        return False

    def respond(self, title, *content, **kwargs):
        """(title:str, *content, **kwargs)
        Fill the response using the page() method and the given title,
        content, and **kwargs and return immediately.
        """
        self.get_hit().init_response()
        if 'status' in kwargs:
            status = kwargs['status']
            del kwargs['status']
        else:
            status = 400
        self.get_hit().get_response().set_status(status)
        self.get_hit().get_response().set_body(
            self.page(title, *content, **kwargs))
        self.respond_now()

    def header(self, title, **kwargs):
        """(title, **kwargs) -> h8
        Return the site-standard html header.
        """
        return h8('<html><head><title>%s</title></head><body>') % title

    def footer(self, **kwargs):
        """(**kwargs) -> h8
        Return the site-standard html footer.
        """
        return h8('</body></html>')

    def page(self, title, *content, **kwargs):
        """(title, *content, **kwargs) -> h8
        Return a page formatted according to the site-standard.
        """
        return (self.header(title, **kwargs) +
                h8.from_list(content) +
                self.footer(title=title, **kwargs))

    def sign_out(self, url):
        """(url:str)
        Un-authenticate the current user and redirect to `url`.
        """
        get_session().clear_authentication()
        self.redirect(url)

    def ensure_signed_in_using_form(self, title='Please Sign In',
                                    realm=None, **kwargs):
        """
        Make sure that the current user is signed in.
        This presents a form to the user.  Because the form transmits the
        password, this redirects to the https address before presenting the
        form.

        The realm, if given, identifies which of the user's passwords
        should be used.  The default realm is the name of the site.
        """
        if not get_user():
            self.secure()
            form = Form(use_tokens=False)
            default_user_id = None
            if get_session().get_owner():
                default_user_id = get_session().get_owner().get_id()
            form.add_string(
                'name', value=default_user_id, title="Email", required=True)
            form.add_password('password', title="Password", required=True)
            form.add_submit('login', 'Sign in')
            def show_form():
                self.respond(title, form.render(), status=403, **kwargs)
            if not form.is_submitted()or form.has_errors():
                show_form()
            user = self.get_users().get(form.get('name'))
            if user and user.has_password(form.get('password') or '',
                                          realm=realm):
                get_session().set_authenticated(user)
                self.redirect('')
            if not user:
                form.set_error('name', 'unknown user')
            else:
                form.set_error('password', 'wrong password')
            show_form()


    def ensure_signed_in_using_basic(self, realm=None):
        """
        Make sure that the current user is signed in.
        This uses HTTP Basic Authentication.  Because Basic Authentication
        transmits the password, this implementation redirects if necessary
        to make sure that the challenge only happens when the scheme is
        https.

        The realm, if given, identifies which of the user's passwords
        should be used.  The default realm is the name of the site.
        """
        if not get_user():
            # Look to see if authentication credentials have been delivered.
            authorization = get_request().get_header(
                'HTTP_AUTHORIZATION', '').split()
            if len(authorization) == 2:
                scheme, encoded = authorization
                try:
                    decoded = binascii.a2b_base64(encoded).split(':')
                except binascii.Error:
                    pass
                else:
                    if scheme.lower() == 'basic' and len(decoded) == 2:
                        username, password = decoded
                        user = self.get_users().get(username)
                        if user and user.has_password(password, realm=realm):
                            get_session().set_authenticated(user) # success
        if not get_user():
            # Issue an authentication challenge.
            assert self.get_site().get_https_address(), (
                "If you want basic authentication, use https.")
            self.secure() # This redirects to https.
            if realm is None:
                realm = self.get_site().get_name()
            self.get_hit().init_response()
            self.get_hit().get_response().set_status(401)
            self.get_hit().get_response().set_header(
                'WWW-Authenticate',
                'Basic realm="%s"' % realm)
            self.respond_now()

    def ensure_signed_in_using_digest(self, realm=None):
        """
        Make sure that the current user is signed in.
        This uses HTTP Digest Authentication.  Since this does not transmit
        the password itself, we allow this to work even when https is not
        available.  If https is available, though, we redirect to it first.

        The realm, if given, identifies which of the user's passwords
        should be used.  The default realm is the name of the site.
        """
        if not get_user():
            if realm is None:
                realm = self.get_site().get_name()
            def attempt_digest_authentication():
                authorization = get_request().get_header(
                    'HTTP_AUTHORIZATION', '').split()
                if len(authorization) < 5:
                    return
                if authorization[0].lower() != 'digest':
                    return
                parameters = {}
                for item in authorization[1:]:
                    item_split = item.split('=')
                    if len(item_split) != 2:
                        continue
                    name, value = item_split
                    if value[-1] == ',':
                        value = value[:-1]
                    if value and value[0]=='"' and value[-1]=='"':
                        value = value[1:-1]
                    parameters[name.lower()] = value
                username = parameters.get('username', None)
                if not username:
                    return
                user = self.get_users().get(username)
                if not user:
                    return
                nonce = parameters.get('nonce')
                if nonce not in get_user().get_tokens():
                    return
                get_user().get_tokens().remove(nonce)
                cnonce = parameters.get('cnonce')
                if not cnonce:
                    return
                nc = parameters.get('nc')
                if not nc:
                    return
                qop = parameters.get('qop')
                if not qop:
                    return
                request_digest = parameters.get('response', '')
                if len(request_digest) != 32:
                    return
                realm = parameters.get('realm')
                user_digest = user.get_digester().get_digest(realm)
                if not user_digest:
                    return
                method = get_request().get_method()
                if request_digest == compute_digest(
                    user_digest,
                    nonce,
                    nc,
                    cnonce,
                    qop,
                    compute_digest(method, parameters.get('uri', ''))):
                    # success
                    get_session().set_authenticated(user)
            attempt_digest_authentication()
        if not get_user():
            # Issue an authentication challenge.
            self.secure()
            self.get_hit().init_response()
            self.get_hit().get_response().set_status(401)
            self.get_hit().get_response().set_body("Do I know you?")
            nonce = get_user().get_tokens().new_token()
            self.get_hit().get_response().set_header(
                'WWW-Authenticate',
                ('Digest realm="%s", nonce="%s", opaque="0%s", stale=false, '
                 'algorithm=MD5, qop="auth"' % (realm, nonce, nonce)))
            self.respond_now()

    def ensure_signed_in(self, **kwargs):
        self.ensure_signed_in_using_digest()

add_getters(Publisher)
