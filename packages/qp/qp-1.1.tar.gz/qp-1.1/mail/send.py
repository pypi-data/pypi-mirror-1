"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/mail/send.py $
$Id: send.py 26815 2005-05-17 11:07:27Z dbinger $
"""

from smtplib import SMTP
from qp.mail.rfc822_mailbox import rfc822_mailbox
from qp.pub.common import get_publisher
import socket

class Email(object):

    max_header_recipients = 10

    def __init__(self):
        self.set_subject('')
        self.set_body('')
        webmaster = self.get_webmaster_address()
        self.set_from_address(webmaster)
        self.set_smtp_sender(webmaster)
        self.set_to([webmaster])
        self.set_cc([])
        self.set_reply_to([])
        self.set_extra_headers([])
        self.set_smtp_recipients([])
        self.sent = False

    def set_subject(self, subject):
        self.subject = str(subject)

    def get_subject(self):
        return self.subject

    def set_body(self, body):
        self.body = str(body)

    def get_body(self):
        return self.body

    def set_from_address(self, address):
        self.from_address = rfc822_mailbox(address)

    def get_from_address(self):
        return self.from_address

    def set_reply_to(self, addresses):
        self.reply_to = self.mailboxes(addresses)

    def get_reply_to(self):
        return self.reply_to

    def set_smtp_sender(self, address):
        self.smtp_sender = rfc822_mailbox(address)

    def get_smtp_sender(self):
        return self.smtp_sender

    def set_to(self, addresses):
        self.to = self.mailboxes(addresses)

    def get_to(self):
        return self.to

    def set_cc(self, addresses):
        self.cc = self.mailboxes(addresses)

    def get_cc(self):
        return self.cc

    def set_extra_headers(self, headers):
        self.extra_headers = [str(header) for header in headers]

    def get_extra_headers(self):
        return self.extra_headers

    def set_smtp_recipients(self, addresses):
        self.smtp_recipients = self.mailboxes(addresses)

    def get_smtp_recipients(self):
        if self.smtp_recipients:
            return self.smtp_recipients
        else:
            return self.get_to() + self.get_cc()

    def get_bulk_headers(self):
        to = self.get_to()
        if len(to) == 1 and to  == [self.get_webmaster_address()]:
            return []
        else:
            return ["Precedence: junk", "X-No-Archive: yes"]

    def get_smtp_server(self):
        return get_publisher().get_smtp_server()

    def format_headers(self):
        headers = ["From: %s" % self.get_from_address().format(),
                   "Subject: %s" % self.get_subject()]
        def address_headers(field_name, addresses):
            if not addresses:
                return
            if len(addresses) == 1:
                headers.append("%s: %s" % (field_name, addresses[0].format()))
            elif len(addresses) <= self.max_header_recipients:
                headers.append("%s: %s," % (field_name, addresses[0].format()))
                for address in addresses[1:-1]:
                    headers.append("    %s," % address.format())
                headers.append("    %s" % addresses[-1].format())
            else:
                headers.append(
                    "%s: (long recipient list suppressed) : ;" % field_name)
        address_headers("To", self.get_to())
        address_headers("Cc", self.get_cc())
        address_headers("Reply-To", self.get_reply_to())
        headers += self.get_extra_headers()
        headers += self.get_bulk_headers()
        return '\n'.join(headers) + '\n\n'

    def get_smtp_sender(self):
        return self.smtp_sender

    def set_smtp_sender(self, address):
        self.smtp_sender = rfc822_mailbox(address)

    def is_email_enabled(self):
        return get_publisher().is_email_enabled()

    def get_webmaster_address(self):
        return rfc822_mailbox(get_publisher().get_webmaster_address())

    def get_debug_address(self):
        return rfc822_mailbox(get_publisher().get_debug_address())

    def mailboxes(self, addresses):
        return [rfc822_mailbox(address) for address in addresses if address]

    def send(self):
        assert not self.sent # Make sure duplicates are not sent.
        if not self.is_email_enabled():
            return False
        debug_address = self.get_debug_address()
        smtp_recipients = self.get_smtp_recipients()
        if debug_address:
            recipients = [debug_address.get_addr_spec()]
            message = self.format_headers() 
            message += ('[debug mode, message actually sent to %s]\n' %
                        debug_address.format())
            if self.get_smtp_recipients():
                message += ('[original SMTP recipients: %s]\n' %
                            ', '.join([address.format()
                                       for address in smtp_recipients]))
            message += '-' * 72 + '\n'
            message += self.get_body()
        else:
            recipients = [address.get_addr_spec()
                          for address in smtp_recipients]
            message = self.format_headers() + self.get_body()
        sender = self.get_smtp_sender().get_addr_spec()
        server = self.get_smtp_server()
        assert server
        assert sender
        assert recipients
        assert message
        try:
            smtp = SMTP(server)
            smtp.sendmail(sender, recipients, message)
            smtp.quit()
        except socket.error, e:
            print "Email.send() failed: %s" % e
            return False
        self.sent = True
        return True

def sendmail(subject, msg_body, to_addrs, from_addr=None, reply_to=None,
             smtp_sender=None, cc_addrs=None, extra_headers=None,
             smtp_recipients=None):
    email = Email()
    email.set_subject(subject)
    email.set_body(msg_body)
    email.set_to(to_addrs)
    if from_addr:
        email.set_from_address(from_addr)
    if reply_to:
        email.set_reply_to(reply_to)
    if smtp_sender:
        email.set_smtp_sender(smtp_sender)
    if cc_addrs:
        email.set_cc(cc_addrs)
    if extra_headers:
        email.set_extra_headers(extra_headers)
    if smtp_sender:
        email.set_smtp_sender(smtp_sender)
    if smtp_recipients:
        email.set_smtp_recipients()
    return email.send()


