import os, sys
sys.path.append('/usr/local/pydap/mysite')
os.environ['PYTHON_EGG_CACHE'] = '/usr/local/pydap/python-eggs'

from paste.deploy import loadapp
application = loadapp('config:/usr/local/pydap/mysite/server.ini')

config = os.path.join(os.path.dirname(__file__), 'development.ini')
application = loadapp('config:%s' % config)
