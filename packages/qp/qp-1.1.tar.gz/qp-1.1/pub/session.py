"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/pub/session.py $
$Id: session.py 27444 2005-09-20 17:09:39Z dbinger $
"""
from datetime import datetime, timedelta
from durus.persistent import Persistent
from qp.lib.spec import specify, spec, either, add_getters
from qp.pub.common import get_request, get_publisher
from qp.pub.user import User

class Session (Persistent):
    """
    Class attribute:
      lease_time: timedelta
        The amount of time for which an authentication is valid.
    """
    lease_time = timedelta(days=30)

    remote_address_is = spec(
        either(None, basestring),
        "The remote address of the request when this session was created.")
    authentication_time_is = spec(
        either(None, datetime),
        "The time of the current authentication into this session, or "
        "None if there is no current authentication.")
    effective_user_is = spec(
        either(None, User),
        "The user that should be used in ui code at this time. "
        "This is the null user if the authentication_time is None.")
    owner_is = spec(
        either(None, effective_user_is),
        "The first user to have authenticated into this session. "
        "If no user has ever authenticated, this is the null user. "
        "The id of this user is used to initialize the value of the "
        "username field on a login form.")

    def __init__(self):
        null_user = get_publisher().get_users()['']
        specify(self,
                authentication_time=None,
                remote_address=get_request().get_remote_address(),
                owner=null_user,
                effective_user=null_user)

    def clear_authentication(self):
        """
        Remove the current authentication record.
        Set the authentication-time to None,
        Set the effective_user to be the null user.
        """
        specify(self, authentication_time=None,
                effective_user=get_publisher().get_users()[''])

    def is_valid(self):
        """() -> bool
        Can this Session continue as authenticated?
        This may have a side-effect of clearing the authentication if
        it has expired or is rejected for some other reason.
        """
        if self.remote_address != get_request().get_remote_address():
            self.clear_authentication()
            return False
        if self.authentication_time is None:
            return True
        if self.authentication_time + self.lease_time < datetime.utcnow():
            self.clear_authentication()
            return False
        return True

    def set_authenticated(self, user):
        """(user:User)
        Called when the User has just delivered valid evidence of authenticity.
        """
        if not self.owner:
            specify(self, owner=user)
        specify(self, effective_user=user,
                authentication_time=datetime.utcnow(),
                remote_address=get_request().get_remote_address())

    def set_effective_user(self, user):
        """(user:User)
        This is a way to set the effective user *without* changing the
        authentication time.  This allows administrative users to temporarily
        act as other users.
        """
        specify(self, effective_user=user)

    def needs_saving(self):
        """Should this session be *added* to database?"""
        if self._p_oid:
            # This is already in the Durus database
            return False
        if not self.owner:
            # Don't bother maintaining sessions for anonymous users.
            return False
        return True

add_getters(Session)
