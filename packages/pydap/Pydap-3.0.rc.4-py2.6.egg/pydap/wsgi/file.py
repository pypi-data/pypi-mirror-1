"""
A simple file-based Opendap server.

Serves files from a root directory, handling those recognized by installed
handlers.

"""

import re
import os
from urllib import unquote
import time

from paste.urlparser import StaticURLParser
from paste.request import construct_url, path_info_pop

from pydap.handlers.lib import get_handler, load_handlers
from pydap.lib import __version__
from pydap.exceptions import ExtensionNotSupportedError
from pydap.util.template import FileLoader, GenshiRenderer


class FileServer(StaticURLParser):
    def __init__(self, root, root_directory=None, cache_max_age=None, templates='templates', catalog='catalog.xml', **config):
        StaticURLParser.__init__(self, root, root_directory, cache_max_age)
        self.catalog = catalog
        self.config = config

        self.templates = templates
        loader = FileLoader(templates)
        self.renderer = GenshiRenderer(
                options={}, loader=loader)

        self.handlers = load_handlers()

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        if not path_info:
            return self.add_slash(environ, start_response)
        if path_info == '/':
            # @@: This should obviously be configurable
            filename = 'index.html'
        else:
            filename = path_info_pop(environ)
        full = os.path.normcase(os.path.normpath(
            os.path.join(self.directory, filename)))
        if os.path.sep != '/':
            full = full.replace('/', os.path.sep)
        if self.root_directory is not None and not full.startswith(self.root_directory):
            # Out of bounds
            return self.not_found(environ, start_response)
        if not os.path.exists(full):
            return self.not_found(environ, start_response)
        if os.path.isdir(full):
            # @@: Cache?
            child_root = self.root_directory is not None and \
                self.root_directory or self.directory
            return self.__class__(full, root_directory=child_root,
                                  cache_max_age=self.cache_max_age,
                                  templates=self.templates,
                                  catalog=self.catalog,
                                  **self.config)(environ, start_response)
        if environ.get('PATH_INFO') and environ.get('PATH_INFO') != '/':
            return self.error_extra_path(environ, start_response)
        if_none_match = environ.get('HTTP_IF_NONE_MATCH')
        if if_none_match:
            mytime = os.stat(full).st_mtime
            if str(mytime) == if_none_match:
                headers = []
                ETAG.update(headers, mytime)
                start_response('304 Not Modified', headers)
                return [''] # empty body

        fa = self.make_app(full)
        if self.cache_max_age:
            fa.cache_control(max_age=self.cache_max_age)
        return fa(environ, start_response)

    def not_found(self, environ, start_response, debug_message=None):
        request = os.path.split(environ['SCRIPT_NAME'])[1]
        request = os.path.normpath(os.path.join(self.directory, request))
        filepath, response = os.path.splitext(request)
        if os.path.sep != '/': filepath = filepath.replace('/', os.path.sep)

        if environ['PATH_INFO'] == '/':
            return self.index(environ, start_response,
                    'index.html', 'text/html')
        elif os.path.exists(filepath):
            # Update environ with configuration keys (environ wins in case of conflict).
            for k in self.config:
                environ.setdefault(k, self.config[k])
            environ['pydap.renderer'] = self.renderer
            handler = get_handler(filepath, self.handlers)
            return handler(environ, start_response)
        elif environ['SCRIPT_NAME'].endswith('/%s' % self.catalog):
            return self.index(environ, start_response,
                    'catalog.xml', 'text/xml')
        else:
            return StaticURLParser.not_found(
                    self, environ, start_response, debug_message)

    def index(self, environ, start_response, template_name, content_type):
        # Return directory listing.
        dirs = []
        files = []
        for name in os.listdir(self.directory):
            path = os.path.normpath(os.path.join(self.directory, name))
            if os.path.isdir(path) and not name.startswith('.'):
                dirs.append(name)
            elif os.path.isfile(path) and not name.startswith('.'):
                statinfo = os.stat(path)
                file = {'name': name,
                        'size': format_size(statinfo[6]),
                        'modified': time.localtime(statinfo[8]),
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

        # Base URL.
        location = construct_url(environ, with_query_string=False)
        base = location[:location.rfind('/')]

        context = {
                'root': construct_url(environ, with_query_string=False, script_name='').rstrip('/'),
                'base': base,
                'location': location,
                'title': 'Index of %s' % unquote(environ.get('SCRIPT_NAME') or '/'),
                'dirs' : dirs,
                'files': files,
                'version': '.'.join(str(d) for d in __version__)
        }
        template = self.renderer.loader(template_name)
        output = self.renderer.render(template, context)
        headers = [('Content-type', content_type)]
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
            return '%.1i MB' % size
        return '%.1f KB' % size
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
