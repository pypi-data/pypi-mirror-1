from operator import attrgetter
import copy
import itertools
from new import classobj

import numpy

from pydap.lib import quote
from pydap.util.odict import odict


__all__ = ['StructureType', 'SequenceType', 'DatasetType', 'GridType',
           'BaseType', 'Float32', 'Float64', 'Int16', 'Int32', 'UInt16',
           'UInt32', 'Byte', 'String', 'Url', 'typemap']


# Define the basic Opendap types as classes. Each class has a correspondent
# Numpy typecode and item size. Instead of explicitly defining classes we
# can use the ``classobj`` function, since the classes are basically just
# placeholders for attributes.
def TypeFactory(name, typecode, size):
    return classobj(name, (object,),
            {'typecode': typecode, 'size': size, 'descriptor': name})

Float64 = TypeFactory('Float64', 'd', 8)
Float32 = TypeFactory('Float32', 'f', 4)
Int32 = TypeFactory('Int32', 'i', 4)
Int16 = TypeFactory('Int16', 'i', 4)
UInt32 = TypeFactory('UInt32', 'I', 4)
UInt16 = TypeFactory('UInt16', 'I', 4)
Byte = TypeFactory('Byte', 'B', 1)
String = TypeFactory('String', 'S', None)
Url = TypeFactory('Url', 'S', None)
basetypes = [Float64, Float32, Int32, Int16, Byte, UInt32, UInt16, String, Url]

# A simple map to convert between commonly used identifiers
# and our classes.
typemap = {
    # type.__name__.lower()
    'float64': Float64,
    'float32': Float32,
    'int32': Int32,
    'int16': Int16,
    'uint32': UInt32,
    'uint16': UInt16,
    'byte': Byte,
    'string': String,
    'url': Url,

    # numpy
    'd': Float64,
    'f': Float32,
    'h': Int16,
    'i': Int32, 'l': Int32, 'q': Int32,
    'b': Byte,
    'H': UInt16,
    'I': UInt32, 'L': UInt32, 'Q': UInt32,
    'B': Byte,
    'S': String,

    # extra from the stdlib array module
    'c': String,
    'u': String,
}


class DapType(object):
    """
    The common Opendap type.

    This class is an abstract class, defining common methods and
    attributes for other all classes in the Opendap data model.

    """
    def __init__(self, name='nameless', attributes=None):
        self.name = quote(name)
        self._id = name
        self.attributes = attributes or {}

    def __getattr__(self, attr):
        """
        Attribute shortcut.

        The data classes have their attributes stored in the 
        ``attributes`` attribute, which is a dictionary. Access
        to these values can be shortcutted by accessing the 
        attribute directly::

            >>> var = DapType()
            >>> var.attributes['foo'] = 'bar'
            >>> print var.foo
            bar

        """
        try:
            return self.attributes[attr]
        except (KeyError, TypeError):
            raise AttributeError
    
    def walk(self):
        """
        Iterate over children.

        This method is used in constructor variables to iterate
        over the variable's children. The default behavior is to
        return and empty iterable (ie, no children).

        """
        return ()

    def _set_id(self, parent=None):
        """
        Set the variable id.

        The id of a variable is a representation of its hierarchy
        in the dataset, using dots to join the variable names.

        """
        if parent:
            self._id = '%s.%s' % (parent, self.name)
        else:
            self._id = self.name

        # Propagate id to children.
        for var in self.walk():
            var._set_id(self._id)
    id = property(attrgetter('_id'))  # read-only


class BaseType(DapType):
    """
    The base Opendap type.

    This class represents basic Opendap types, which contain data.
    Variables can be scalars or multi-dimensional arrays, of one of
    the basic Opendap types (Int32, String, etc.)::

        >>> a = BaseType(name='a', data=1, type=Int32)
        >>> b = BaseType(name='b', data=range(5), shape=(5,),
        ...         dimensions=('time',), type=UInt16)
        >>> print b.attributes
        {}
        >>> b.attributes['units'] = 'days since 1980-1-1'

    Comparisons and other operators are usually applied to the ``data``
    attribute::

        >>> print b[1]
        1
        >>> print len(b)
        5
        >>> print a > 0
        True
        >>> data = numpy.arange(4)
        >>> data.shape = (2, 2)
        >>> c = BaseType(name='c', data=data)
        >>> for block in c:
        ...     print block
        [0 1]
        [2 3]

    """
    def __init__(self, name='nameless', data=None, shape=None,
            dimensions=None, type=Int32, attributes=None):
        DapType.__init__(self, name, attributes)
        self.type = type in basetypes and type or typemap[type]
        self.data = data
        self.shape = shape or ()
        self.dimensions = dimensions or ()

    # Comparisons and other operations are applied directly to
    # the ``data`` attribute.
    def __eq__(self, other): return self.data == other
    def __ne__(self, other): return self.data != other
    def __ge__(self, other): return self.data >= other
    def __le__(self, other): return self.data <= other
    def __gt__(self, other): return self.data > other
    def __lt__(self, other): return self.data < other
    def __iter__(self): return iter(self.data)
    def __getitem__(self, index): return self.data[index]
    def __len__(self): return len(self.data)

    def __copy__(self):
        out = self.__class__(self.name, self.data, self.shape,
                self.dimensions, self.type, self.attributes.copy())
        out._id = self._id
        return out

    def __deepcopy__(self, memo=None, _nil=[]):
        """
        Return a copy of the object, with a copy of the data too.

        """
        out = self.__copy__()
        out.data = copy.copy(self.data)
        return out


class StructureType(odict, DapType):
    """
    An Opendap Structure.

    A StructureType is simply a fancy dictionary, used to hold groups of
    variables that share common characteristics (in theory).  They work
    exactly like Python dictionaries::

        >>> s = StructureType(name='s')
        >>> s['a'] = BaseType(name='a')
        >>> s['b'] = BaseType(name='b')
        >>> print s.keys()
        ['a', 'b']

    """
    def __init__(self, name='nameless', attributes=None):
        odict.__init__(self)
        DapType.__init__(self, name, attributes)

    def __getattr__(self, attr):
        """
        Allow lazy access to children.

        We override ``__getattr__`` to allow children variables
        to be accessed using a lazy syntax::

            >>> s = StructureType(name='s')
            >>> s['a'] = BaseType(name='a')
            >>> print s.a.id
            s.a

        """
        if attr in self:
            return self[attr]
        else:
            return DapType.__getattr__(self, attr)

    # Walk returns each stored variable.
    walk = __iter__ = odict.itervalues

    def __setitem__(self, key, item):
        odict.__setitem__(self, key, item)

        # Fix id in item.
        item._set_id(self._id)

    # Propagate to and collect data from children.
    def _get_data(self):
        return tuple([var.data for var in self])
    def _set_data(self, data):
        for col, var in itertools.izip(data, self):
            var.data = col
    data = property(_get_data, _set_data)

    def __copy__(self):
        out = self.__class__(name, attributes.copy())
        out._id = self._id

        # Stored variables are not copied.
        out.update(self)
        return out

    def __deepcopy__(self, memo=None, _nil=[]):
        out = self.__class__(self.name, self.attributes.copy())
        out._id = self._id

        # Make copies of the stored variables.
        for k, v in self.items():
            out[k] = copy.deepcopy(v, memo)
        return out


class DatasetType(StructureType):
    """
    An Opendap Dataset.

    A DatasetType works pretty much like a Structure; the major
    difference is that its name is not used when composing the id of
    stored variables::

        >>> dataset = DatasetType(name='dataset')
        >>> dataset['a'] = BaseType(name='a', attributes={'foo': 'bar'})
        >>> print dataset.a.foo
        bar

    """
    def __setitem__(self, key, item):
        odict.__setitem__(self, key, item)

        # Do not propagate id.
        item._set_id(None)

    def _set_id(self, parent=None):
        self._id = self.name

        for var in self.walk():
            var._set_id(None)


class SequenceType(StructureType):
    """
    An Opendap Sequence.

    Sequences are a special kind of constructor, holding records for
    the stored variables. They are somewhat similar to record arrays
    in Numpy::

        >>> s = SequenceType(name='s')
        >>> s['id'] = BaseType(name='id', type=Int32)
        >>> s['x'] = BaseType(name='x', type=Float64)
        >>> s['y'] = BaseType(name='y', type=Float64)

        >>> s.data = numpy.array(
        ...         [(1, 10, 100), (2, 20, 200), (3, 30, 300)],        
        ...         {'names': ('id', 'x', 'y'), 'formats': ('i4', 'f8', 'f8')})

        >>> for struct_ in s: print struct_.data
        (1, 10.0, 100.0)
        (2, 20.0, 200.0)
        (3, 30.0, 300.0)
        >>> print s['id'].data
        [1 2 3]

    Note that we had to use ``s['id']`` to refer to the variable ``id``,
    since ``s.id`` already points to the id of the Sequence.
    
    (An important point is that the ``data`` attribute must be copiable,
    so don't use consumable iterables like older versions of Pydap
    allowed.)

    Sequences are quite versatile; they can be indexed::

        >>> print s[0].data
        [(1, 10.0, 100.0)]
        >>> print s[0].x.data
        [ 10.]

    Or filtered::

        >>> print s[ (s['id'] > 1) & (s.x > 10) ].data
        [(2, 20.0, 200.0) (3, 30.0, 300.0)]

    Or even both::

        >>> print s[ s['id'] > 1 ][1].x.data
        [ 30.]

    If you mix indexing and filtering, be sure to use the right Sequence
    on the filter::

        >>> print s[ s['id'] > 1 ][1].x.data
        [ 30.]
        >>> print s[1][ s['id'] > 1 ].x.data
        Traceback (most recent call last):
            ...
        ValueError: too many boolean indices
        >>> print s[1][ s[1]['id'] > 1 ].x.data
        [ 20.]

    (Note that there's a difference between filtering first and then
    slicing, and slicing first and then indexing. This might not be the
    case always, since an Opendap server will always apply the filter
    first, while in this case we're working locally with the data. Don't
    worry, though: when this happens while accessing an Opendap server
    a warning will be issued by the client.)
    
    When filtering a Sequence, don't use the Python extended comparison
    syntax of ``1 < a < 2``, otherwise bad things will happen.

    And of course, slices are also used to access children::

        >>> print s['x'] is s.x
        True

    """
    def __init__(self, name='nameless', attributes=None, data=None):
        StructureType.__init__(self, name, attributes)
        self.data = data

    # When we set the Sequence data we also set the data for its children,
    # using the record array syntax.
    def _set_data(self, data):
        self._data = data
        for var in self.walk():
            var.data = data[var.name]
    def _get_data(self):
        return self._data
    data = property(_get_data, _set_data)

    def __getitem__(self, key):
        """
        Fancy Sequence slicing.

        The basic rule for Sequence slices is that it always return a new
        variable -- either a child or a new Sequence. To select a child,
        just use the common dictionary syntax::

            >>> s = SequenceType(name='s')
            >>> s['a'] = BaseType(name='a')
            >>> print s['a'].id
            s.a

        A Sequence can also be filtered or indexed using the slice::

            >>> s['b'] = BaseType(name='b')
            >>> s['c'] = BaseType(name='c')
            >>> s.data = numpy.array(
            ...         [(1, 10, 100), (2, 20, 200), (3, 30, 300)],        
            ...         {'names': ('a', 'b', 'c'), 'formats': ('i4', 'i4', 'i4')})

            >>> print s[0].data
            [(1, 10, 100)]
            >>> print s[2:10].data
            [(3, 30, 300)]
            >>> print s[ s.a > 10 ].data
            []

        These will return new Sequence objects with the appropriate data.

        Finally, Sequences can also be reduced, selecting only a few
        children::

            >>> s2 = s[ ('b', 'a') ]
            >>> print s.keys()
            ['a', 'b', 'c']
            >>> print s2.keys()
            ['b', 'a']
            >>> print s2.data
            [(10, 1) (20, 2) (30, 3)]

        """
        if isinstance(key, basestring) and key in self:
            return odict.__getitem__(self, key)
        elif isinstance(key, tuple):
            out = copy.deepcopy(self)

            # Keep only requested children, in the proper order.
            for child in out.keys():
                if child not in key:
                    del out[child]
            out._keys = list(key)  # put in order

            # We try to pass the tuple directly to the data, for "smart"
            # objects like a ``SequenceProxy``. If it fails, we have no
            # option other than reading the data and creating a new
            # record array.
            try:
                out.data = self.data[key]
            except:
                out.data = numpy.rec.fromarrays(
                        [out[k] for k in out._keys], names=out._keys)
            return out
        else:
            out = copy.deepcopy(self)
            if isinstance(key, (int, long)): key = slice(key, key+1, 1)
            out.data = self.data[key]
            return out

    def __iter__(self):
        """
        Return a Structure for each record in the Sequence.

        When a Sequence is iterated it returns Structure objects
        containing each record.

        """
        out = copy.deepcopy(self)
        for row in out.data:
            struct_ = StructureType(out.name, out.attributes)
            for col, name in zip(row, out.keys()):
                var = struct_[name] = copy.deepcopy(out[name])
                var.data = col
            yield struct_

    def __deepcopy__(self, memo=None, _nil=[]):
        out = StructureType.__deepcopy__(self, memo, _nil)
        out.data = copy.copy(self.data)
        return out


class GridType(StructureType):
    """
    An Opendap Grid.

    A Grid works both like an array and a Structure. The Grid is basically
    a Structure containing an array and more variables describing its
    axes; the first defined variable is the multi-dimensional array,
    while later each individual axis should be defined::

        >>> g = GridType(name='g')
        >>> data = numpy.arange(6.)
        >>> data.shape = (2, 3)
        >>> g['a'] = BaseType(name='a', data=data, shape=data.shape, type=Float32, dimensions=('x', 'y'))
        >>> g['x'] = BaseType(name='x', data=numpy.arange(2.), shape=(2,), type=Float64)
        >>> g['y'] = BaseType(name='y', data=numpy.arange(3.), shape=(3,), type=Float64)
        >>> print g.data
        [[ 0.  1.  2.]
         [ 3.  4.  5.]]
    
    We can treat the Grid like an array::

        >>> print g[:,0]
        [ 0.  3.]

    We can also use a shortcut notation for maps and the array::

        >>> print g['y'][0]
        0.0
        >>> print g.y[:]
        [ 0.  1.  2.]

    A nice thing about Grids is that we can slice them by the maps::

        >>> print g[ :,(g.y > 0) ]
        [[ 1.  2.]
         [ 4.  5.]]

    Though for remote Grids (ie, on Opendap servers) this only works
    for continuous conditions, ie, with a start and an end index.

    """
    def __getitem__(self, key):
        if isinstance(key, basestring):
            return StructureType.__getitem__(self, key)
        else:
            return self.array[key]

    @property
    def array(self):
        return self[self._keys[0]]

    @property
    def maps(self):
        return dict((k, self[k]) for k in self._keys[1:])

    @property
    def dimensions(self):
        return tuple(self._keys[1:])

    # These attributes all come from the array object.
    def __len__(self): return len(self.array)
    def _get_data(self): return self.array.data
    def _set_data(self, data): self.array.data = data
    data = property(_get_data, _set_data)
    def _get_shape(self): return self.array.shape
    def _set_shape(self, shape): self.array.shape = shape
    shape = property(_get_shape, _set_shape)
    @property
    def type(self): return self.array.type


def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()
