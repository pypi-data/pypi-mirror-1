import imaplib
import logging

logger = logging.getLogger('mailprocess')
debug = logger.debug

def _imap_message_generator(server, nums):
    for num in nums:
        debug("Getting message number %s" % num)
        typ, data = server.fetch(num, '(RFC822)')
        yield num, data[0][1]

class IMAP4(object):
    impl = imaplib.IMAP4

    def __init__(self, next, username, password, host='', port='143',
                 mailbox='INBOX'):
        self.next = next
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.mailbox = mailbox

    def __call__(self):
        debug("Opening connection to %s:%s" % (self.host, self.port))
        server = self.impl(self.host, int(self.port))
        server.login(self.username, self.password)
        debug("Searching all messages in %s" % self.mailbox)
        server.select(self.mailbox)
        typ, data = server.search(None, 'ALL')
        debug("Passing on messages to %r" % self.next)
        to_delete = self.next(
            _imap_message_generator(server, data[0].split()))
        if to_delete:
            debug("%r requested deletion of %s messages" %
                  (self.next, len(to_delete)))
            for num in to_delete:
                server.store(num, '+FLAGS', '\\Deleted')
        server.close()
        server.logout()

class IMAP4_SSL(IMAP4):
    impl = imaplib.IMAP4_SSL

    def __init__(self, next, username, password, host='', port='993',
                 mailbox='INBOX'):
        super(IMAP4_SSL, self).__init__(
            next, username, password, host, port, mailbox)
