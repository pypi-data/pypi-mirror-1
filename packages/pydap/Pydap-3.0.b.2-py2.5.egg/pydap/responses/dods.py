from pydap.responses.dds import dispatch as dds_dispatch
from pydap.responses.lib import BaseResponse
from pydap.xdr import DapPacker


class DODSResponse(BaseResponse):
    def __init__(self, dataset):
        BaseResponse.__init__(self, dataset)
        self.headers.extend([
                ('Content-description', 'dods_data'),
                ('Content-type', 'application/octet-stream'),
                ])

    @staticmethod
    def serialize(dataset):
        # Generate DDS.
        for line in dds_dispatch(dataset):
            yield line
        yield 'Data:\n'
        for line in DapPacker(dataset):
            yield line
        if hasattr(dataset, 'close'): dataset.close()
