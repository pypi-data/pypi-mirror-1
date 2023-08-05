"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/lib/util.py $
$Id: util.py 26974 2005-06-28 22:20:15Z dbinger $
"""
import os
import sys
from binascii import hexlify

def import_object(name):
    """
    Import and return the object with the given name.
    """
    i = name.rfind('.')
    if i != -1:
        module_name = name[:i]
        object_name = name[i+1:]
        try:
            __import__(module_name)
        except:
            print "Could not import", module_name
            raise
        try:
            return getattr(sys.modules[module_name], object_name)
        except AttributeError:
            pass
    __import__(name)
    return sys.modules[name]

# Define randbytes(), one way or another.
if hasattr(os, 'urandom'):
    # available in Python 2.4 and also works on win32
    def randbytes(bytes):
        """Return bits of random data as a hex string."""
        return hexlify(os.urandom(bytes))
elif os.path.exists('/dev/urandom'):
    # /dev/urandom is just as good as /dev/random for cookies (assuming
    # SHA-1 is secure) and it never blocks.
    def randbytes(bytes):
        """Return bits of random data as a hex string."""
        return hexlify(open("/dev/urandom").read(bytes))
else:
    # this is much less secure.
    import sha, time
    class _PRNG:
        def __init__(self):
            self.state = sha.new(str(time.time() + time.clock()))
            self.count = 0

        def _get_bytes(self):
            self.state.update('%s %d' % (time.time() + time.clock(),
                                         self.count))
            self.count += 1
            return self.state.hexdigest()

        def randbytes(self, bytes):
            """Return bits of random data as a hex string."""
            s = ""
            chars = 2*bytes
            while len(s) < chars:
                s += self._get_bytes()
            return s[:chars]

    randbytes = _PRNG().randbytes
