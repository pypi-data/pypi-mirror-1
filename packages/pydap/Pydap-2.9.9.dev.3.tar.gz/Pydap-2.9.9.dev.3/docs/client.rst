Using the client
================

Pydap can be used as a client to inspect and retrieve data from any of the `hundreds of scientific datasets <http://www.opendap.org/data/datasets.cgi?xmlfilename=datasets.xml&exfunction=none>`_ available on the internet on `OPeNDAP <http://opendap.org/>`_ servers. This way, it's possible to instrospect and manipulate a dataset as if it were stored locally, with data being downloaded on-the-fly as necessary.

Accessing gridded data
----------------------

Let's start accessing gridded data, i.e., data that is stored as a regular multidimensional array. Here's a simple example where we access the `COADS <http://www.ncdc.noaa.gov/oa/climate/coads/>`_ climatology from the official OPeNDAP server:

.. doctest::

    >>> from pydap.client import open_url
    >>> dataset = open_url('http://test.opendap.org/dap/data/nc/coads_climatology.nc')
    >>> print type(dataset)
    <class 'pydap.model.DatasetType'>

Here we use the ``pydap.client.open_url`` function to open an URL specifying the location of the dataset; this URL should be stripped of the extensions commonly used for OPeNDAP datasets, like `.dds` or `.das`. When we access the remote dataset the function returns a ``DatasetType`` object, which is a *Structure* -- a fancy dictionary that stores other variables. We can check the names of the store variables like we would do with a Python dictionary:

.. doctest::

    >>> print sorted(dataset.keys())
    ['AIRT', 'COADSX', 'COADSY', 'SST', 'TIME', 'UWND', 'VWND']

Let's work with the ``SST`` variable; we can reference it using the usual dictionary syntax (``dataset['SST']``) or a "lazy" syntax (``dataset.SST``):

.. doctest::

    >>> sst = dataset['SST']  # or dataset.SST
    >>> print type(sst)
    <class 'pydap.model.GridType'>

Note that the variable is of type ``GridType``, a multidimensional array with specific axes defining each of its dimensions:

.. doctest::
    
    >>> print sst.dimensions
    ('TIME', 'COADSY', 'COADSX')
    >>> print sst.maps  #doctest: +ELLIPSIS
    {'COADSX': <pydap.model.BaseType object at ...>, 'COADSY': <pydap.model.BaseType object at ...>, 'TIME': <pydap.model.BaseType object at ...>}

Each map is also, in turn, a variable that can be accessed using the same syntax used for Structures:

.. doctest::

    >>> print sst.TIME  #doctest: +ELLIPSIS
    <pydap.model.BaseType object at ...>

The axes are all of type ``BaseType``. This is the OPeNDAP equivalent of a multidimensional array, with a specific shape and type. Even though no data have been downloaded up to this point, we can introspect these attributes from the axes or from the Grid itself:

.. doctest::

    >>> print sst.shape
    (12, 90, 180)
    >>> print sst.type
    <class 'pydap.model.Float32'>
    >>> print sst.TIME.shape
    (12,)
    >>> print sst.TIME.type
    <class 'pydap.model.Float64'>

We can also introspect the variable attributes; they are stored in an attribute appropriately called ``attributes``, and they can also be accessed with a "lazy" syntax:

.. doctest::

    >>> import pprint
    >>> pprint.pprint(sst.attributes)
    {'_FillValue': -9.999999790214768e+33,
     'history': 'From coads_climatology',
     'long_name': 'SEA SURFACE TEMPERATURE',
     'missing_value': -9.999999790214768e+33,
     'units': 'Deg C'}
    >>> print sst.units
    Deg C

Finally, we can also download some data. To download data we simply access it like we would access a `Numpy <http://numpy.scipy.org/>`_ array, and the data for the corresponding subset will be dowloaded on the fly from the server:

.. doctest::

    >>> print sst.shape
    (12, 90, 180)
    >>> print sst[0,10:14,10:14]  # this will download data from the server
    [[ -1.26285708e+00  -9.99999979e+33  -9.99999979e+33  -9.99999979e+33]
     [ -7.69166648e-01  -7.79999971e-01  -6.75454497e-01  -5.95714271e-01]
     [  1.28333330e-01  -5.00000156e-02  -6.36363626e-02  -1.41666666e-01]
     [  6.38000011e-01   8.95384610e-01   7.21666634e-01   8.10000002e-01]]

Instead of indexes we can also subset the data using its maps, in a more natural way. Just keep in mind that sometimes axes can be cyclic, like longitude, and you may have to download two separate parts and concatenate them together. This is not the case here:

.. doctest::

    >>> print sst[ 0 , (-10 < sst.COADSY) & (sst.COADSY < 10) , (sst.COADSX > 320) & (sst.COADSX < 328) ]
    [[ -9.99999979e+33  -9.99999979e+33   2.75645447e+01   2.74858131e+01]
     [ -9.99999979e+33  -9.99999979e+33   2.75924988e+01   2.74538631e+01]
     [  2.74333324e+01   2.75676193e+01   2.75849991e+01   2.72220459e+01]
     [  2.74995346e+01   2.75236359e+01   2.75734081e+01   2.71845455e+01]
     [  2.75163631e+01   2.74263630e+01   2.73368282e+01   2.72538090e+01]
     [  2.74848824e+01   2.74654541e+01   2.72157135e+01   2.71914806e+01]
     [  2.75176182e+01   2.74858055e+01   2.71117859e+01   2.71154156e+01]
     [  2.74184361e+01   2.71918182e+01   2.70971432e+01   2.68821430e+01]
     [  2.66373062e+01   2.65258331e+01   2.66468735e+01   2.65185719e+01]
     [  2.56100006e+01   2.62577419e+01   2.62805882e+01   2.62171783e+01]]


Accessing sequential data
-------------------------

Now let's see an example of accessing sequential data. Sequential data consists of one or more records of related variables, such as a simultaneous measurements of temperature and wind velocity, for example. In this example we're going to access data from the `Argo project <http://www.argo.ucsd.edu/>`_, consisting of profiles made by autonomous buoys drifting on the ocean:

.. code-block:: python

    >>> dataset = open_url('http://dapper.pmel.noaa.gov/dapper/argo/argo_all.cdp')

This dataset is fairly complex, with several variables representing heterogeneous 4D data. The layout of the dataset follows the `Dapper in-situ conventions <http://www.epic.noaa.gov/epic/software/dapper/dapperdocs/conventions/>`_, consisting of two nested sequences: the outer sequence contains, in this case, a latitude, longitude and time variable, while the inner sequence contains measurements along a z axis.

The first thing we'd like to do is limit our region; let's work with a small region in the Tropical Atlantic:

.. code-block:: python

    >>> print type(dataset.location)
    <class 'pydap.model.SequenceType'>
    >>> print dataset.location.keys()
    ['LATITUDE', 'JULD', 'LONGITUDE', '_id', 'profile', 'attributes', 'variable_attributes']
    >>> my_location = dataset.location[
    ...         (dataset.location.LATITUDE > -2) &
    ...         (dataset.location.LATITUDE < 2) &
    ...         (dataset.location.LONGITUDE > 320) &
    ...         (dataset.location.LONGITUDE < 330)]

Here we're limiting the sequence ``dataset.location`` to measurements between given latitude and longitude boundaries. Let's access the identification number of each profile:

.. code-block:: python

    >>> for i, id_ in enumerate(my_location['_id']):
    ...     print id_
    ...     if i == 10:
    ...         print '...'
    ...         break
    835304
    839894
    875344
    110975
    864748
    832685
    887712
    962673
    881368
    782747
    661070
    ...
    >>> print len(my_location['_id'])
    604

(Note that calculating the length of a sequence takes some time, since the client has to download all the data and do the calculation locally.)

We can select just the first 5 profiles from our sequence:

.. code-block:: python

    >>> my_location = my_location[:5]
    >>> print len(my_location['_id'])
    5

And we can print the temperature profiles at each location. We're going to use the `coards <http://pypi.python.org/pypi/coards>`_ module to convert the time to a Python ``datetime`` object:

.. code-block:: python

    >>> from coards import from_udunits
    >>> for position in my_location:
    ...     date = from_udunits(position.JULD.data, position.JULD.units)
    ...     print
    ...     print position.LATITUDE.data, position.LONGITUDE.data, date
    ...     print '=' * 40
    ...     i = 0
    ...     for pressure, temperature in zip(position.profile.PRES, position.profile.TEMP):
    ...         print pressure, temperature
    ...         if i == 10:
    ...             print '...'
    ...             break
    ...         i += 1

    -0.675 320.027 2006-12-25 13:24:11+00:00
    ==================================================
    5.0 27.675
    10.0 27.638
    15.0 27.63
    20.0 27.616
    25.0 27.617
    30.0 27.615
    35.0 27.612
    40.0 27.612
    45.0 27.605
    50.0 27.577
    55.0 27.536
    ...

    -0.303 320.078 2007-01-12 11:30:31.001000+00:00
    ==================================================
    5.0 27.727
    10.0 27.722
    15.0 27.734
    20.0 27.739
    25.0 27.736
    30.0 27.718
    35.0 27.694
    40.0 27.697
    45.0 27.698
    50.0 27.699
    55.0 27.703
    ...

    -1.229 320.095 2007-04-22 13:03:35.002000+00:00
    ==================================================
    5.0 28.634
    10.0 28.71
    15.0 28.746
    20.0 28.758
    25.0 28.755
    30.0 28.747
    35.0 28.741
    40.0 28.737
    45.0 28.739
    50.0 28.748
    55.0 28.806
    ...

    -1.82 320.131 2003-04-09 13:20:03+00:00
    ==================================================
    5.1 28.618
    9.1 28.621
    19.4 28.637
    29.7 28.662
    39.6 28.641
    49.6 28.615
    59.7 27.6
    69.5 26.956
    79.5 26.133
    89.7 23.937
    99.2 22.029
    ...

    -1.939 320.169 2007-03-22 11:39:54.002000+00:00
    ==================================================
    5.0 28.618
    10.0 28.612
    15.0 28.619
    20.0 28.623
    25.0 28.623
    30.0 28.607
    35.0 28.6
    40.0 28.586
    45.0 28.541
    50.0 28.452
    55.0 28.45
    ...

These profiles could be easily plotted using `matplotlib <http://matplotlib.sf.net/>`_:

.. code-block:: python

    >>> for position in my_location:
    ...     plot(position.profile.TEMP, position.profile.PRES)
    >>> show()

Pydap 3.0 has been rewritten to make it easier to work with Dapper datasets like this one.

Advanced features
-----------------

Calling server-side functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you open a remote dataset, the ``DatasetType`` object has a special attribute named ``functions`` that can be used to invoke any server-side functions. Here's an example of using the ``geogrid`` function from Hyrax:

.. doctest::

    >>> dataset = open_url('http://test.opendap.org/dap/data/nc/coads_climatology.nc')
    >>> new_dataset = dataset.functions.geogrid(dataset.SST, 10, 20, -10, 60)
    >>> print new_dataset.SST.shape
    (12, 12, 21)
    >>> print new_dataset.SST.COADSY[:]
    [-11.  -9.  -7.  -5.  -3.  -1.   1.   3.   5.   7.   9.  11.]
    >>> print new_dataset.SST.COADSX[:]
    [ 21.  23.  25.  27.  29.  31.  33.  35.  37.  39.  41.  43.  45.  47.  49.
      51.  53.  55.  57.  59.  61.]

Unfortunately, there's currently no standard mechanism to discover which functions the server support. 

Opening a specific URL
~~~~~~~~~~~~~~~~~~~~~~

You can pass any URL to the ``open_url`` function, together with any valid constraint expression. Here's an example of restricting values for the months of January, April, July and October:

.. doctest::

    >>> dataset = open_url('http://test.opendap.org/dap/data/nc/coads_climatology.nc?SST[0:3:11][0:1:89][0:1:179]')
    >>> print dataset.SST.shape
    (4, 90, 180)

Accessing raw data
~~~~~~~~~~~~~~~~~~

.. doctest::

    >>> from pydap.client import open_dods
    >>> dataset = open_dods()

This method downloads the data directly, and skips metadata from the DAS response, so it's not useful to investigate and introspect datasets. The advantage is that it allows you to access raw data from any URL, including appending expressions to `F-TDS <http://ferret.pmel.noaa.gov/LAS/documentation/the-ferret-thredds-data-server-f-tds/>`_ and `GDS <http://www.iges.org/grads/gds/>`_ servers.

Using a cache
~~~~~~~~~~~~~

You can specify a cache directory in the ``pydap.lib.CACHE`` global variable. If this value is different than ``None``, the client will try (if the server headers don't prohibit) to cache the result, so repeated requests will be read from disk instead of the network:

.. code-block:: python

    >>> import pydap.lib
    >>> pydap.lib.CACHE = "/tmp/pydap-cache/"

Timeout
~~~~~~~

To specify a timeout for the client, just set the global variable ``pydap.lib.TIMEOUT`` to the desired number of seconds; after this time trying to connect the client will give up. The default is ``None`` (never timeout).

.. code-block:: python

    >>> import pydap.lib
    >>> pydap.lib.TIMEOUT = 60

Configuring a proxy
~~~~~~~~~~~~~~~~~~~

It's possible to configure Pydap to access the network through a proxy server. Here's an example for an HTTP proxy running on ``localhost`` listening on port 8000:

.. code-block:: python

    >>> import httplib2
    >>> from pydap.util import socks
    >>> import pydap.lib
    >>> pydap.lib.PROXY = httplib2.ProxyInfo(
    ...         socks.PROXY_TYPE_HTTP, 'localhost', 8000)

This way, all further calls to ``pydap.client.open_url`` will be routed through the proxy server.

Authentication
--------------

Basic & Digest
~~~~~~~~~~~~~~

To use Basic and Digest authentication, simple add your username and password to the dataset URL. Keep in mind that if the server only supports Basic authentication your credentials will be sent as plaintext, and could be sniffed on the network.

.. code-block:: python

    >>> from pydap.client import open_url
    >>> dataset = open_url('http://username:password@server.example.com/path/to/dataset')

CAS
~~~

The `Central Authentication Service <http://en.wikipedia.org/wiki/Central_Authentication_Service>`_ (CAS) is a single sign-on protocol for the web, usually involving a web browser and cookies. Nevertheless it's possible to use Pydap with an OPeNDAP server behind a CAS. The function ``install_cas_client`` below replaces Pydap's default HTTP function with a new version able to submit authentication data to an HTML form and store credentials in cookies. (In this particular case, the server uses Javascript to redirect the browser to a new location, so the client has to parse the location from the Javascript code; other CAS would require a tweaked function.)

To use it, just call the function before any requests:

.. code-block:: python

    >>> install_cas_client()
    >>> from pydap.client import open_url  # this function is now monkeypatched

And here is the function. It depends on the `BeautifulSoup <http://www.crummy.com/software/BeautifulSoup/>`_ module to parse the HTML.

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
                data = r.read()
                code = BeautifulSoup(data)

                # Check if we need to authenticate:
                if code.find('form'):
                    # Ok, we need to authenticate. Let's get the location
                    # where we need to POST the information.
                    post_location = code.find('form').get('action', r.url)

                    # Do a post, passing our credentials.
                    inputs = code.find('form').findAll('input')
                    params = dict([(el['name'], el['value']) for el in inputs
                                     if el['type']=='hidden'])
                    params[username_field] = url.username
                    params[password_field] = url.password
                    params = urllib.urlencode(params)
                    req = urllib2.Request(post_location, params)
                    r = urllib2.urlopen(req)

                    # Parse the response.
                    data = r.read()
                    code = BeautifulSoup(data)

                # Get the location from the Javascript code. Depending on the
                # CAS this code has to be changed. Ideally, the server would
                # redirect with HTTP headers and this wouldn't be necessary.
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
