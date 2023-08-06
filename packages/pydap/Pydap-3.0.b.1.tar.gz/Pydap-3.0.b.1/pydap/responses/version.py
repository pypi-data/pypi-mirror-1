from pydap.lib import __dap__, __version__


class VersionResponse(object):
    def __init__(self, dataset=None):
        if hasattr(dataset, 'close'): dataset.close()

    def __call__(self, environ, start_response):
        headers = [('XDODS-Server', 'dods/%s' % '.'.join(str(d) for d in __dap__)),
                   ('Content-type', 'text/plain')]

        output = """Core version: dods/%s
Server version: pydap/%s
""" % ('.'.join(str(d) for d in __dap__), '.'.join(str(d) for d in __version__))

        start_response('200 OK', headers)
        return [output]

