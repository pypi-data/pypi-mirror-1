from wsgi_intercept import add_wsgi_intercept
from wsgi_intercept import httplib2_intercept
httplib2_intercept.install()

from pydap.lib import isiterable
from pydap.handlers.lib import SimpleHandler


def UnitTestServer(dataset, host='localhost', port=8080, script_name=''):
    app = SimpleHandler(dataset)
    add_wsgi_intercept(host, port, lambda: app, script_name=script_name)


def to_list(L):
    if isiterable(L): return [to_list(item) for item in L]
    else: return L
