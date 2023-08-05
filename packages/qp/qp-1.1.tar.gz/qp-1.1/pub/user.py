"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/pub/user.py $
$Id: user.py 27489 2005-09-29 13:38:37Z dbinger $
"""
from durus.persistent import Persistent
from durus.persistent_dict import PersistentDict
from durus.persistent_set import PersistentSet
from md5 import md5
from qp.lib.spec import require, specify, spec, add_getters, sequence, either
from qp.pub.common import get_publisher
from qp.lib.util import randbytes

class Permissions (PersistentDict):

    data_is = {basestring:sequence(either(Persistent, True), PersistentSet)}

    def grant(self, permission, granter):
        require(permission, basestring)
        require(granter, either(Persistent, True))
        if permission not in self:
            self[permission] = PersistentSet([granter])
        else:
            self[permission].add(granter)

    def ungrant(self, permission, granter):
        require(permission, basestring)
        require(granter, either(Persistent, True))
        if self.is_granted(permission, granter):
            self.data[permission].remove(granter)
            if len(self.data[permission]) == 0:
                del self.data[permission]

    def is_granted(self, permission, granter):
        return granter in self.get(permission, [])


def compute_digest(*args):
    return md5(":".join([str(x) for x in args])).hexdigest()


class Digester (Persistent):

    digests_is = {str:str}

    def __init__(self):
        self.digests = {}

    def set_digest(self, realm, digest):
        self._p_note_change()
        self.digests[realm] = digest

    def get_digest(self, realm):
        return self.digests.get(realm)

    def get_realms(self):
        return self.digests.keys()

    def remove_digest(self, realm):
        self._p_note_change()
        del self.digests[realm]


class TokenSet(Persistent):
    """
    A set of randomly generated tokens that have been delivered with forms.
    These are used to make sure that forms can't be replayed.
    """
    tokens_is = spec(
        [str],
        "The tokens that have been delivered with forms recently.")

    def __init__(self):
        self.clear()

    def clear(self):
        self.tokens = []

    def __contains__(self, token):
        return token in self.tokens

    def remove(self, token):
        if token in self.tokens:
            self._p_note_change()
            self.tokens.remove(token)

    def new_token(self, bytes=8):
        token = randbytes(bytes)
        self.tokens = ([token] + self.tokens)[:16]
        return token


class User (Persistent):

    id_is = spec(
        str,
        "unique among users here")
    digester_is = spec(
        Digester,
        "holds password hashes")
    permissions_is = spec(
        Permissions,
        "Records permissions granted.")
    tokens_is = spec(
        TokenSet,
        "a nonce dealer")

    def __init__(self, user_id):
        specify(self, id=user_id,
                digester=Digester(),
                permissions=Permissions(),
                tokens=TokenSet())

    def __nonzero__(self):
        """The null user is the one with id == ''.
        """
        return bool(self.id)

    def set_password(self, password, realm=None):
        if realm is None:
            realm = get_publisher().get_site().get_name()
        digester = self.get_digester()
        if not password:
            digester.remove_digest(realm)
        else:
            digester.set_digest(
                realm, compute_digest(self.get_id(), realm, password))

    def has_password(self, password, realm=None):
        if realm is None:
            realm = get_publisher().get_site().get_name()
        digester = self.get_digester()
        digest = digester.get_digest(realm)
        return bool(
            digest and
            digest == compute_digest(self.get_id(), realm, password))

    def is_granted(self, permission, other=None):
        """(permission:basestring, other:Persistent=None) -> bool
        Does this user have the `permission` granted from the `other`?
        If no value is provided for other, the root object is used as
        the `other`.
        """
        if other is None:
            return self.permissions.is_granted(
                permission, get_publisher().get_root())
        else:
            return self.permissions.is_granted(permission, other)

    def is_admin(self):
        """() -> bool
        Has the root object granted 'administrator' to this user?
        """
        return self.permissions.is_granted('administrator', True)

add_getters(User)
