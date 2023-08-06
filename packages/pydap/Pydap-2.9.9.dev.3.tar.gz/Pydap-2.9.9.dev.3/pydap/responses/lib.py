from pydap.model import DatasetType


class ResponseSerializer(object):
    """
    A serializer for responses that keeps the dataset
    for modification by WSGI middleware.

    Follows this specification::

      http://wsgi.org/wsgi/Specifications/avoiding_serialization

    """
    def __init__(self, dataset, serializer):
        self.dataset = dataset
        self.serializer = serializer

    def x_wsgiorg_parsed_response(self, type):
        if type is DatasetType:
            return self.dataset

    def __iter__(self):
        return self.serializer(self.dataset)
