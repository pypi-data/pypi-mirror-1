import re
from urlparse import urlsplit, urlunsplit
import logging

import httplib2
from pydap.util import socks
httplib2.socks = socks

import pydap.lib
from pydap.exceptions import ClientError


log = logging.getLogger('pydap')


def request(url):
    """
    Open a given URL and return headers and body.

    This function retrieves data from a given URL, returning the headers
    and the response body. Authentication can be set by adding the
    username and password to the URL; this will be sent as clear text
    only if the server only supports Basic authentication.

    """
    h = httplib2.Http(cache=pydap.lib.CACHE,
            timeout=pydap.lib.TIMEOUT,
            proxy_info=pydap.lib.PROXY)
    url = urlsplit(url)
    if url.username and url.password:
        h.add_credentials(url.username, url.password)

    # Remove username/password from url.
    netloc = '%s:%s' % (url.hostname, url.port or 80)
    url = urlunsplit((
            url.scheme, netloc, url.path, url.query, url.fragment
            )).rstrip('?&')

    log.info('Opening %s' % url)
    resp, data = h.request(url, "GET",
            headers = {'user-agent': pydap.lib.USER_AGENT})

    # When an error is returned, we parse the error message from the
    # server and return it in a ``ClientError`` exception.
    if resp.get("content-description") == "dods_error":
        m = re.search('code = (?P<code>\d+);\s*message = "(?P<msg>.*)"',
                data, re.DOTALL | re.MULTILINE)
        msg = 'Server error %(code)s: "%(msg)s"' % m.groupdict()
        raise ClientError(msg)

    return resp, data
