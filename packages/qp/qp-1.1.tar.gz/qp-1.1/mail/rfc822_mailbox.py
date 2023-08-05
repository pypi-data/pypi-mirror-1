"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/mail/rfc822_mailbox.py $
$Id: rfc822_mailbox.py 26724 2005-04-29 20:16:23Z dbinger $
"""

import re
rfc822_specials_re = re.compile(r'[\(\)\<\>\@\,\;\:\\\"\.\[\]]')

class RFC822Mailbox:
    """
    In RFC 822, a "mailbox" is either a bare e-mail address or a bare
    e-mail address coupled with a chunk of text, most often someone's
    name.  Eg. the following are all "mailboxes" in the RFC 822 grammar:
      luser@example.com
      Joe Luser <luser@example.com>
      Paddy O'Reilly <paddy@example.ie>
      "Smith, John" <smith@example.com>
      Dick & Jane <dickjane@example.net>
      "Tom, Dick, & Harry" <tdh@example.org>

    This class represents an (addr_spec, real_name) pair and takes care
    of quoting the real_name according to RFC 822's rules for you.
    Just use the format() method and it will spit out a properly-
    quoted RFC 822 "mailbox".
    """

    def __init__(self, addr_spec, real_name=''):
        self.addr_spec = str(addr_spec)
        self.real_name = str(real_name)

    def get_addr_spec(self):
        return self.addr_spec

    def get_real_name(self):
        return self.real_name

    def __eq__(self, other):
        return (isinstance(other, RFC822Mailbox) and
                self.get_addr_spec() == other.get_addr_spec() and
                self.get_real_name() == other.get_real_name())

    def format(self):
        if self.real_name and rfc822_specials_re.search(self.real_name):
            return '"%s" <%s>' % (self.real_name.replace('"', '\\"'),
                                  self.addr_spec)
        elif self.real_name:
            return '%s <%s>' % (self.real_name, self.addr_spec)

        else:
            return self.addr_spec


def rfc822_mailbox(s):
    """(s:None|str|tuple|RFC822Mailbox) -> RFC822Mailbox | None
    Tries to make an RFC822Mailbox from the argument if it is a tuple or str.
    """
    if s is None:
        return s
    if isinstance(s, RFC822Mailbox):
        return s
    if type(s) is tuple:
        return RFC822Mailbox(*s)
    if type(s) is str:
        return RFC822Mailbox(s, '')
    raise TypeError("expected None, 2-tuple, or str\ngot %r" % s)


