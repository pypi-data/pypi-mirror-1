"""
Client interface to OPeNDAP servers.

This module implements the ``open_url`` function, which returns an
object representing a remote dataset served by an OPeNDAP server. The
client builds the dataset representation from the DDS+DAS responses,
though in the future it can be extended to support other representations
(like DDX, or perhaps JSON).

"""

import sys
from urlparse import urlsplit, urlunsplit

from pydap.model import *
from pydap.proxy import *
from pydap.util.http import request
from pydap.exceptions import ClientError
from pydap.lib import walk, combine_slices, fix_slice, parse_qs, fix_shn


def open_url(url):
    """
    Open a given dataset URL, trying different response methods. 

    The function checks the stub DDX method, and falls back to the
    DDS+DAS responses. It can be easily extended for other representations
    like JSON.

    The URL should point to the dataset, omitting any response extensions
    like ``.dds``. Username and password can be passed in the URL like::

        http://user:password@example.com:port/path

    They will be transmitted as plaintext if the server supports only
    Basic authentication, so be careful. For Digest authentication this
    is safe.

    The URL can point directly to an Opendap dataset, or it can contain
    any number of contraint expressions (selection/projections)::

        http://example.com/dataset?var1,var2&var3>10

    You can also specify a cache directory, a timeout and a proxy using
    the global variables from ``pydap.lib``::

        >>> import pydap.lib
        >>> pydap.lib.TIMEOUT = 60  # seconds
        >>> pydap.lib.CACHE = '.cache'
        >>> import httplib2
        >>> from pydap.util import socks
        >>> pydap.lib.PROXY = httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP, 'localhost', 8000)

    """
    for response in [_ddx, _ddsdas]:
        dataset = response(url)
        if dataset: break
    else:
        raise ClientError("Unable to open dataset.")

    # Remove any projections from the url, leaving selections.
    o = urlsplit(url)
    projection, selection = parse_qs(o.query)
    url = urlunsplit(
            (o.scheme, o.netloc, o.path, '&'.join(selection), o.fragment))

    # Set data to a Proxy object for BaseType and SequenceType. These
    # variables can then be sliced to retrieve the data on-the-fly.
    for var in walk(dataset, BaseType):
        var.data = ArrayProxy(var.id, url, var.shape)
    for var in walk(dataset, SequenceType):
        var.data = SequenceProxy(var.id, url)

    # Apply the corresponding slices.
    projection = fix_shn(projection, dataset)
    for var in projection:
        target = dataset
        while var:
            token, slice_ = var.pop(0)
            target = target[token]
            if slice_ and isinstance(target.data, VariableProxy):
                shape = getattr(target, 'shape', (sys.maxint,))
                target.data._slice = fix_slice(slice_, shape)

    return dataset


def _ddx(url):
    """
    Stub function for DDX.

    Still waiting for the DDX spec to write this.

    """
    pass


def _ddsdas(url):
    """
    Build the dataset from the DDS+DAS responses.

    This function builds the dataset object from the DDS and DAS
    responses, adding Proxy objects to the variables.

    """
    from pydap.parsers.dds import DDSParser
    from pydap.parsers.das import DASParser

    o = urlsplit(url)
    ddsurl = urlunsplit(
            (o.scheme, o.netloc, o.path + '.dds', o.query, o.fragment))
    dasurl = urlunsplit(
            (o.scheme, o.netloc, o.path + '.das', o.query, o.fragment))

    respdds, dds = request(ddsurl)
    respdas, das = request(dasurl)

    # Build the dataset structure and attributes.
    dataset = DDSParser(dds).parse()
    dataset = DASParser(das, dataset).parse()
    return dataset

