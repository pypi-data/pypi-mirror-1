import logging
import urllib
import urllib2

logger = logging.getLogger('mailprocess')
debug = logger.debug

class Post(object):
    """Send an HTTP POST request with Basic auth.
    """
    def __init__(self, url, username=None, password=None):
        self.url = url
        self.username = username
        self.password = password

    def __call__(self, **kwargs):
        data = urllib.urlencode(kwargs, doseq=True)
        debug("Sending HTTP POST data %r to %s" % (data, self.url))
        request = urllib2.Request(self.url, data)
        if self.username and self.password:
            cred = ('%s:%s' % (self.username, self.password)).encode('base64')
            request.add_header('Authorization', 'Basic %s' % cred)
        request.add_header('User-Agent', 'mailprocess')
        opener = urllib2.build_opener()
        response = opener.open(request).read()
        debug("Response:\n%r") % response
