import itertools

import numpy

from pydap.model import *
from pydap.lib import __dap__, INDENT, encode_atom, n_iterate
from pydap.responses.dds import dispatch as dds_dispatch
from pydap.responses.lib import ResponseSerializer


class ASCIIResponse(object):
    def __init__(self, dataset):
        self.dataset = dataset

    def __call__(self, environ, start_response):
        headers = [('Content-description', 'dods_ascii'),
                   ('XDODS-Server', 'dods/%s' % '.'.join(str(d) for d in __dap__)),
                   ('Content-type', 'text/plain')]

        def serialize(dataset):
            # Generate DDS.
            for line in dds_dispatch(dataset):
                yield line
            yield 45 * '-'
            yield '\n'
            for line in dispatch(dataset):
                yield line
            if hasattr(dataset, 'close'): dataset.close()

        start_response('200 OK', headers)

        if environ.get('x-wsgiorg.want_parsed_response'):
            return ResponseSerializer(self.dataset, serialize)
        else:
            return serialize(self.dataset)


def dispatch(var, printname=True):
    dispatchers = [(SequenceType, _sequence),
                   (StructureType, _structure),
                   (BaseType, _base)]
    
    for klass, func in dispatchers:
        if isinstance(var, klass):
            return func(var, printname)


def _structure(var, printname):
    for child in var.walk():
        for line in dispatch(child, printname):
            yield line
        yield '\n'


def _sequence(var, printname):
    yield ', '.join(child.id for child in var.values())
    yield '\n'
    for struct_ in var:
        out = []
        for child in struct_:
            for line in dispatch(child, printname=False):
                out.append(line)
        out = ', '.join(out).split('\n')
        for line in out:
            if line:
                yield line.strip(', ') + '\n'


def _base(var, printname):
    if printname:
        yield var.id
        yield '\n'

    data = numpy.asarray(var.data).flat
    for indexes, value in itertools.izip(n_iterate(var.shape), data):
        index = '[%s]' % ']['.join(str(idx) for idx in indexes)
        yield '%s %s\n' % (index, encode_atom(value))
    if not var.shape:
        yield encode_atom(var.data)
