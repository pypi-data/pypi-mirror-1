from pydap.model import *
from pydap.lib import __dap__
from pydap.responses.dds import dispatch as dds_dispatch
from pydap.responses.lib import ResponseSerializer
from pydap.xdr import DapPacker


class DODSResponse(object):
    def __init__(self, dataset):
        self.dataset = dataset

    def __call__(self, environ, start_response):
        headers = [('Content-description', 'dods_data'),
                   ('XDODS-Server', 'dods/%s' % '.'.join(str(d) for d in __dap__)),
                   ('Content-type', 'application/octet-stream')]

        def serialize(dataset):
            # Generate DDS.
            for line in dds_dispatch(dataset):
                yield line
            yield 'Data:\n'
            for line in DapPacker(dataset):
                yield line
            if hasattr(dataset, 'close'): dataset.close()

        start_response('200 OK', headers)

        if environ.get('x-wsgiorg.want_parsed_response'):
            return ResponseSerializer(self.dataset, serialize)
        else:
            return serialize(self.dataset)
