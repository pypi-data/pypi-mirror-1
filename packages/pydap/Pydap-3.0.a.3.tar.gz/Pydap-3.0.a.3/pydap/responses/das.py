from pydap.model import *
from pydap.model import typemap
from pydap.lib import __dap__, INDENT, encode_atom, isiterable
from pydap.responses.lib import ResponseSerializer


class DASResponse(object):
    def __init__(self, dataset):
        self.dataset = dataset

    def __call__(self, environ, start_response):
        headers = [('Content-description', 'dods_das'),
                   ('XDODS-Server', 'dods/%s' % '.'.join(str(d) for d in __dap__)),
                   ('Content-type', 'text/plain')]

        def serialize(dataset):
            output = ''.join(dispatch(dataset))
            if hasattr(dataset, 'close'): dataset.close()
            return [output]

        start_response('200 OK', headers)

        if environ.get('x-wsgiorg.want_parsed_response'):
            return ResponseSerializer(self.dataset, serialize)
        else:
            return serialize(self.dataset)


def dispatch(var, level=0):
    dispatchers = [(DatasetType, _dataset),
                   (GridType, _base),
                   (StructureType, _structure),
                   (BaseType, _base)]

    for klass, func in dispatchers:
        if isinstance(var, klass):
            return func(var, level)


def _dataset(var, level=0):
    yield '%sAttributes {\n' % (level * INDENT)

    for attr, values in var.attributes.items():
        for line in _recursive_build(attr, values, level):
            yield line

    for child in var.walk():
        for line in dispatch(child, level=level+1):
            yield line
    yield '%s}\n' % (level * INDENT)


def _structure(var, level=0):
    yield '%s%s {\n' % (level * INDENT, var.name)

    for attr, values in var.attributes.items():
        for line in _recursive_build(attr, values, level):
            yield line

    for child in var.walk():
        for line in dispatch(child, level=level+1):
            yield line
    yield '%s}\n' % (level * INDENT)


def _base(dapvar, level=0):
    yield '%s%s {\n' % (level * INDENT, dapvar.name)

    for attr, values in dapvar.attributes.items():
        for line in _recursive_build(attr, values, level):
            yield line
    yield '%s}\n' % (level * INDENT)


def _recursive_build(attr, values, level=0):
    """
    Recursive function to build the DAS.
    
    """
    # Check for metadata.
    if isinstance(values, dict):
        yield '%s%s {\n' % ((level+1) * INDENT, attr)
        for k, v in values.items():
            for line in _recursive_build(k, v, level+1):
                yield line
        yield '%s}\n' % ((level+1) * INDENT)
    else:
        atoms = values
        if not isiterable(atoms):
            atoms = [atoms]

        # Get value type and encode properly.
        if hasattr(values, 'dtype'):
            type_ = typemap[values.dtype.char].descriptor  # numpy.array
        elif hasattr(values, 'typecode'):
            type_ = typemap[values.typecode].descriptor    # array.array
        else:
            types = [typeconvert(atom) for atom in atoms]
            precedence = ['String', 'Float64', 'Int32']
            types.sort(key=precedence.index)
            type_ = types[0]

        # Encode values
        atoms = [encode_atom(atom) for atom in atoms]
        yield '%s%s %s %s;\n' % ((level+1) * INDENT, type_,
                attr.replace(' ', '_'), ', '.join(atoms))


def typeconvert(obj):
    """Type conversion between Python and DODS, for the DAS."""
    types = [(basestring, 'String'),
             (float, 'Float64'),
             (long, 'Int32'),
             (int, 'Int32')]
    for klass, type_ in types:
        if isinstance(obj, klass):
            return type_
