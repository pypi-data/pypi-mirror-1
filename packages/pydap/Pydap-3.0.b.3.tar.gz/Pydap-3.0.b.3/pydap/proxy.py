import sys
from urlparse import urlsplit, urlunsplit
import copy
import warnings 

from pydap.model import *
from pydap.model import SequenceData
from pydap.lib import hyperslab, combine_slices, fix_slice, walk
from pydap.util.http import request
from pydap.parsers.dds import DDSParser
from pydap.xdr import DapUnpacker


__all__ = ['VariableProxy', 'ArrayProxy', 'SequenceProxy']


class VariableProxy(object):
    """
    A proxy object pointing to an Opendap variable.

    The Opendap client works by defining proxy objects that point to
    specific variables in specific datasets. The object implements a
    typical interface (like an ndarray from Numpy) on the user-side,
    and download data on-the-fly from the server as necessary.

    This particular class is just an abstract implementation.

    """
    def __init__(self, id, url, _slice=None):
        self.id = id
        self.url = url
        self._slice = _slice or (slice(None),)

    def __repr__(self):
        return '<%s pointing to variable "%s%s" at "%s">' % (
                self.__class__.__name__, self.id, hyperslab(self._slice), self.url)

    def __deepcopy__(self, memo=None, _nil=[]):
        out = self.__class__(self.id, self.url, self._slice)
        return out


class ConstraintExpression(object):
    """
    An object representing a given constraint expression.

    These objects are used to build the constraint expression used when
    downloading data. They are produced when a SequenceProxy is compared
    to something::

        >>> from pydap.model import *
        >>> s = SequenceType(name='s')
        >>> s['x'] = BaseType(name='x')
        >>> s.data = SequenceProxy('s', 'http://example.com/dataset')
        >>> s.x.data = SequenceProxy('s.x', 'http://example.com/dataset')
        >>> print type(s.x > 10)
        <class 'pydap.proxy.ConstraintExpression'>
        
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __and__(self, other):
        """Join two CEs together."""
        return self.__class__('%s&%s' % (self.value, other))

    def __or__(self, other):
        raise Exception('OR constraints not allowed in the Opendap specification.')


class ArrayProxy(VariableProxy):
    """
    Proxy to an Opendap basetype.

    """
    def __init__(self, id, url, shape, slice_=None):
        self.id = id
        self.url = url
        self.shape = shape

        if slice_ is None:
            self._slice = (slice(None),) * len(shape)
        else:
            self._slice = slice_ + (slice(None),)*(len(shape)-len(slice_))

    def __iter__(self):
        return iter(self[:])

    def __getitem__(self, index):
        slice_ = combine_slices(self._slice, fix_slice(index, self.shape))
        url = urlsplit(self.url)
        url = urlunsplit((
                url.scheme, url.netloc, url.path + '.dods',
                self.id + hyperslab(slice_) + '&' + url.query,
                url.fragment))

        resp, data = request(url)
        dds, xdrdata = data.split('\nData:\n', 1)
        dataset = DDSParser(dds).parse()
        data = data2 = DapUnpacker(xdrdata, dataset).getvalue()

        # Retrieve the data from any parent structure(s).
        for var in walk(dataset):
            if type(var) in (StructureType, DatasetType):
                data = data[0]
            elif var.id == self.id: 
                return data

        # Some old servers return the wrong response. :-/
        # I found a server that would return an array to a request
        # for an array inside a grid (instead of a structure with
        # the array); this will take care of it.
        for var in walk(dataset):
            if type(var) in (StructureType, DatasetType):
                data2 = data2[0]
            elif self.id.endswith(var.id):
                return data2
            
    # Comparisons return a boolean array
    def __eq__(self, other): return self[:] == other 
    def __ne__(self, other): return self[:] != other
    def __ge__(self, other): return self[:] >= other
    def __le__(self, other): return self[:] <= other
    def __gt__(self, other): return self[:] > other
    def __lt__(self, other): return self[:] < other


class SequenceProxy(VariableProxy, SequenceData):
    """
    Proxy to an Opendap Sequence.

    This class simulates the behavior of a Numpy record array, proxying
    the data in an Opendap Sequence object (or a child variable inside
    a Sequence)::

        >>> from pydap.model import *
        >>> s = SequenceType(name='s')
        >>> s['id'] = BaseType(name='id')
        >>> s['x'] = BaseType(name='x')
        >>> s['y'] = BaseType(name='y')
        >>> s.data = SequenceProxy('s', 'http://example.com/dataset')
        >>> print s.data
        <SequenceProxy pointing to variable "s" at "http://example.com/dataset">
        >>> print s.x.data
        <SequenceProxy pointing to variable "s.x" at "http://example.com/dataset">

    We can use the same methods we would use if the data were local::

        >>> print s[0].x.data
        <SequenceProxy pointing to variable "s[0:1:0].x" at "http://example.com/dataset">
        >>> print s[10:20][2].y.data
        <SequenceProxy pointing to variable "s[12:1:12].y" at "http://example.com/dataset">
        >>> print s[ (s['id'] > 1) & (s.x > 10) ].data
        <SequenceProxy pointing to variable "s" at "http://example.com/dataset?s.id>1&s.x>10&">
        >>> print s[ ('y', 'x') ].data
        <SequenceProxy pointing to variable "s.y,s.x" at "http://example.com/dataset">
        >>> s2 = s[ ('y', 'x') ]
        >>> print s2[ s2.x > 10 ].x.data
        <SequenceProxy pointing to variable "s.x" at "http://example.com/dataset?s.x>10&">
        >>> print s[ ('y', 'x') ][0].data
        <SequenceProxy pointing to variable "s.y,s.x[0:1:0]" at "http://example.com/dataset">

    (While the last line may look strange, it's equivalent to
    ``s.y[0:1:0],s.x[0:1:0]`` -- at least on Hyrax).

    """
    def __iter__(self):
        url = urlsplit(self.url)
        url = urlunsplit((
                url.scheme, url.netloc, url.path + '.dods',
                self.id + hyperslab(self._slice) + '&' + url.query,
                url.fragment))

        resp, data = request(url)
        dds, xdrdata = data.split('\nData:\n', 1)
        dataset = DDSParser(dds).parse()
        data = DapUnpacker(xdrdata, dataset).getvalue()

        # Here ``data`` is the data for the whole dataset; we need to extract
        # the data for the corresponding Sequence here.
        for var in walk(dataset):
            if type(var) in (StructureType, DatasetType):
                data = data[0]
            elif var.id == self.id:
                return iter(data)
            elif (isinstance(var, SequenceType) and
                    self.id.startswith(var.id)):
                return iter(remove_tuples(data))

    def __len__(self):
        return len(list(self.__iter__()))

    def __getitem__(self, key):
        out = copy.deepcopy(self)
        if isinstance(key, ConstraintExpression):
            url = urlsplit(self.url)
            out.url = urlunsplit((
                    url.scheme, url.netloc, url.path, str(key & url.query), url.fragment))

            if out._slice != (slice(None),):
                warnings.warn('Selection %s will be applied before projection "%s".' % (
                        key, hyperslab(out._slice)))
        elif isinstance(key, basestring):
            out._slice = (slice(None),)
            parent = self.id
            if ',' in parent:
                parent = parent.split(',', 1)[0].rsplit('.', 1)[0]
            out.id = '%s%s.%s' % (parent, hyperslab(self._slice), key)
        elif isinstance(key, tuple):
            out.id = ','.join([self.id + '.' + child for child in key])
        else:
            out._slice = combine_slices(self._slice, fix_slice(key, (sys.maxint,)))
        return out

    # Comparisons return a ``ConstraintExpression`` object
    def __eq__(self, other): return ConstraintExpression('%s==%s' % (self.id, other))
    def __ne__(self, other): return ConstraintExpression('%s!=%s' % (self.id, other))
    def __ge__(self, other): return ConstraintExpression('%s>=%s' % (self.id, other))
    def __le__(self, other): return ConstraintExpression('%s<=%s' % (self.id, other))
    def __gt__(self, other): return ConstraintExpression('%s>%s' % (self.id, other))
    def __lt__(self, other): return ConstraintExpression('%s<%s' % (self.id, other))


def remove_tuples(data):
    if isinstance(data, tuple) and len(data) == 1:
        data = data[0]
    if isinstance(data, list):
        data = [remove_tuples(value) for value in data]
    return data
    

def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()
