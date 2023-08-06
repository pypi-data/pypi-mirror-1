Using the client
================

Pydap can be used as a client to inspect and retrieve data from any of the hundreds of scientific datasets available on the internet on OPeNDAP servers. Using a client like Pydap, it's possible to instrospect and manipulate a dataset as if it were stored locally, with data being downloaded on-the-fly as necessary.

Accessing gridded data
----------------------

.. doctest::

    >>> from pydap.client import open_url
    >>> dataset = open_url('http://test.opendap.org/dap/data/nc/coads_climatology.nc')
    >>> print dataset.keys()
    >>> sst = dataset['SST']
    >>> print sst.shape
    >>> print sst.attributes
    >>> print sst.units
    >>> print sst[0,10:15,10:15]
    >>> print sst.dimensions
    >>> print sst[ 0,(-10 < sst.COADSY) & (sst.COADSY < 10),(sst.COADSX > 320) & (sst.COADSX < 330) ]

Accessing sequential data
-------------------------


Configuring a proxy
-------------------

It's possible to configure Pydap to access the network through a proxy server. Here's an example for an HTTP proxy running on ``localhost`` listening on port 8000:

.. code-block:: python

    >>> import httplib2
    >>> from pydap.util import socks
    >>> import pydap.lib
    >>> pydap.lib.PROXY = httplib2.ProxyInfo(
    ...         socks.PROXY_TYPE_HTTP, 'localhost', 8000)

This way, all further calls to ``pydap.client.open_url`` will be routed through the proxy server.

Using CAS authentication
------------------------

.. code-block:: python

    import cookielib
    import urllib
    import urllib2
    from urlparse import urlparse
    import re
    import os

    from BeautifulSoup import BeautifulSoup

    import pydap.lib
    from pydap.exceptions import ClientError


    def install_cas_client(username_field='username', password_field='password'):
        # Create special opener with support for Cookies.
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent', pydap.lib.USER_AGENT)]
        urllib2.install_opener(opener)

        def new_request(url):
            # Remove username/password from url.
            netloc = '%s:%s' % (url.hostname, url.port or 80)
            url = urlunsplit((
                    url.scheme, netloc, url.path, url.query, url.fragment
                    )).rstrip('?&')

            log.INFO('Opening %s' % url)
            r = urllib2.urlopen(url)

            # Detect redirection.
            if r.url != url:
                # Read form data, parse and extract the location where
                # we need to POST the authentication.
                data = r.read()
                code = BeautifulSoup(data)

                # Check if we need to authenticate:
                if code.find('form'):
                    post_location = code.find('form').get('action', r.url)

                    # Do a post.
                    inputs = code.find('form').findAll('input')
                    params = dict([(el['name'], el['value']) for el in inputs
                                     if el['type']=='hidden'])
                    params[username_field] = url.username
                    params[password_field] = url.password
                    params = urllib.urlencode(params)
                    req = urllib2.Request(post_location, params)
                    r = urllib2.urlopen(req)

                    # Parse response.
                    data = r.read()
                    code = BeautifulSoup(data)

                # Get the location from the Javascript code.
                script = code.find('script').string
                redirect = re.search('window.location.href="(.*)"', script).group(1)
                r = urllib2.urlopen(redirect)

            resp = r.headers.dict
            resp['status'] = str(r.code)
            data = r.read()

            # When an error is returned, we parse the error message from the
            # server and return it in a ``ClientError`` exception.
            if resp.get("content-description") == "dods_error":
                m = re.search('code = (?P<code>\d+);\s*message = "(?P<msg>.*)"',
                        data, re.DOTALL | re.MULTILINE)
                msg = 'Server error %(code)s: "%(msg)s"' % m.groupdict()
                raise ClientError(msg)

            return resp, data

        from pydap.util import http
        http.request = new_request
