import email
import logging

from mailman.Bouncers.BouncerAPI import ScanMessages

logger = logging.getLogger('mailprocess')
debug = logger.debug

class MailmanBounceDetect(object):
    def __init__(self, next=None, clean_up='false'):
        self.next = next
        self.clean_up = clean_up.lower() in ('t', '1', 'true', 'yes')

    def __call__(self, messages):
        debug("Starting bounce detection")
        to_clean_up = []
        addrs = set()
        for (id, message) in messages:
            message = email.message_from_string(message)
            found = ScanMessages([], message)
            if found:
                debug("Found bouncing address: %s" % (found,))
                to_clean_up.append(id)
                addrs.update(found)

        debug("%s bouncing addresses found" % len(addrs))

        if addrs and self.next is not None:
            debug("Passing on found addresses to %r" % self.next)
            self.next(addrs=addrs)

        if self.clean_up:
            debug("Returning %s message ids to clean up" % len(to_clean_up))
            return to_clean_up
