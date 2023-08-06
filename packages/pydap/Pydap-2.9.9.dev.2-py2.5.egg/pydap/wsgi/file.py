"""
A simple file-based Opendap server.

Serves files from a root directory, handling those recognized by installed
handlers.

"""

import re
import os
from urllib import unquote

from paste.urlparser import StaticURLParser

from pydap.handlers.lib import get_handler, load_handlers
from pydap.lib import __version__
from pydap.exceptions import ExtensionNotSupportedError
from pydap.util.template import FileLoader, GenshiRenderer


class FileServer(StaticURLParser):
    def __init__(self, root, root_directory=None, cache_max_age=None, templates='templates', **config):
        StaticURLParser.__init__(self, root, root_directory, cache_max_age)
        self.config = config

        loader = FileLoader(templates)
        self.renderer = GenshiRenderer(
                options={}, loader=loader)

        self.handlers = load_handlers()

    def not_found(self, environ, start_response, debug_message=None):
        request = os.path.split(environ['SCRIPT_NAME'])[1]
        request = os.path.normpath(os.path.join(self.directory, request))
        filepath, response = os.path.splitext(request)
        if os.path.sep != '/': filepath = filepath.replace('/', os.path.sep)

        if environ['PATH_INFO'] == '/':
            return self.index(environ, start_response)
        elif os.path.exists(filepath):
            # Update environ with configuration keys (environ wins in case of conflict).
            for k in self.config:
                environ.setdefault(k, self.config[k])
            environ['pydap.renderer'] = self.renderer
            handler = get_handler(filepath, self.handlers)
            return handler(environ, start_response)
        else:
            return StaticURLParser.not_found(
                    self, environ, start_response, debug_message)

    def index(self, environ, start_response):
        # Return directory listing.
        dirs = []
        files = []
        for name in os.listdir(self.directory):
            path = os.path.normpath(os.path.join(self.directory, name))
            if os.path.isdir(path) and not name.startswith('.'):
                dirs.append(name)
            elif os.path.isfile(path) and not name.startswith('.'):
                file = {'name': name,
                        'size': format_size(os.stat(path)[6]),
                        'supported': False}
                try:
                    get_handler(path, self.handlers)
                    file['supported'] = True
                except ExtensionNotSupportedError:
                    pass
                files.append(file)
        # Sort naturally using Ned Batchelder's algorithm.
        dirs.sort(key=alphanum_key)
        files.sort(key=lambda l: alphanum_key(l['name']))

        context = {
                'title': 'Index of %s' % unquote(environ.get('SCRIPT_NAME') or '/'),
                'dirs' : dirs,
                'files': files,
                'version': '.'.join(str(d) for d in __version__)
        }
        template = self.renderer.loader('index.html')
        output = self.renderer.render(template, context)
        headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response("200 OK", headers)
        return [output]


# http://svn.colorstudy.com/home/ianb/ImageIndex/indexer.py
def format_size(size):
    if not size:
        return 'empty'
    if size > 1024:
        size = size / 1024.
        if size > 1024:
            size = size / 1024.
            return '%.1iMb' % size
        return '%.1fKb' % size
    return '%i bytes' % size


def alphanum_key(s):
    """
    Turn a string into a list of string and number chunks.

        >>> alphanum_key("z23a")
        ['z', 23, 'a']

    From http://nedbatchelder.com/blog/200712.html#e20071211T054956

    """
    def tryint(s):
        try:
            return int(s)
        except:
            return s
    return [tryint(c) for c in re.split('([0-9]+)', s)]


def make_app(global_conf, root, templates, **kwargs):
    return FileServer(root, templates=templates, **kwargs)
