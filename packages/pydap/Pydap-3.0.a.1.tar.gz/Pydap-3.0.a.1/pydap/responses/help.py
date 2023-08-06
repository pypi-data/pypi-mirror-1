from paste.request import construct_url

from pydap.lib import __dap__, __version__
from pydap.util.template import GenshiRenderer, StringLoader
from pydap.responses.lib import ResponseSerializer


DEFAULT_TEMPLATE = """<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>pyDAP help page for file $location</title>

        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    </head>

    <body>
        <h1>How to access this file</h1>

        <p>The resource <code>$location</code> is a dataset available through the <a href="http://opendap.org/">OPeNDAP</a> protocol. The best way to access this dataset is using an <a href="http://www.opendap.org/faq/whatClients.html">OPeNDAP client</a> like Ferret, GrADS or Matlab.</p>

        <p>In case you <strong>don't have</strong> a client installed, you can try to download data by accessing the <a href="${location}.html">web interface</a> for this dataset.</p>

        <hr />
        <p><em><a href="http://pydap.org/">pydap/$version</a></em> &copy; Roberto De Almeida</p>
    </body>
</html>"""


class HelpResponse(object):

    renderer = GenshiRenderer(
            options={}, loader=StringLoader( {'help.html': DEFAULT_TEMPLATE} ))

    def __init__(self, dataset=None):
        self.dataset = dataset

    def __call__(self, environ, start_response):
        headers = [('XDODS-Server', 'dods/%s' % '.'.join(str(d) for d in __dap__)),
                   ('Content-type', 'text/html')]

        def serialize(dataset):
            location = construct_url(environ, with_query_string=False)
            dataset, response = location.rsplit('.', 1)
            context = {
                'location': dataset,
                'version' : '.'.join(str(d) for d in __version__),
            }
            renderer = environ.get('pydap.renderer', self.renderer)
            template = renderer.loader('help.html')
            output = renderer.render(template, context)
            if hasattr(dataset, 'close'): dataset.close()
            return [output]

        start_response('200 OK', headers)

        if environ.get('x-wsgiorg.want_parsed_response'):
            return ResponseSerializer(self.dataset, serialize)
        else:
            return serialize(self.dataset)
