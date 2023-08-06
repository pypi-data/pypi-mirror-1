import string

from paver.runtime import *
from paver.setuputils import *
import paver.doctools

try:
    from pydap.lib import __version__
except ImportError:
    __version__ = ('unknown',)


options(
    setup=Bunch(
        name='Pydap',
        version='.'.join(str(d) for d in __version__),
        description='Pure Python Opendap/DODS client and server.',
        long_description='''
Pydap is an implementation of the Opendap/DODS protocol, written from
scratch. You can use Pydap to access scientific data on the internet
without having to download it; instead, you work with special array
and iterable objects that download data on-the-fly as necessary, saving
bandwidth and time.

The module also comes with a robust-but-lightweight Opendap server,
implemented as a WSGI application. The server can handle data in different
file formats (netCDF, HDF, Matlab, CSV, Grib) or stored in any DB API
2 compatible database.

This is an alpha version, work in progress, released for internal
testing. If you want to use Pydap, install the `2.x branch <http://pypi.python.org/pypi/dap>`_.
        ''',
        keywords='opendap dods dap data science climate oceanography meteorology',
        classifiers=filter(None, map(string.strip, '''
            Development Status :: 5 - Production/Stable
            Environment :: Console
            Environment :: Web Environment
            Framework :: Paste
            Intended Audience :: Developers
            Intended Audience :: Science/Research
            License :: OSI Approved :: MIT License
            Operating System :: OS Independent
            Programming Language :: Python
            Topic :: Internet
            Topic :: Internet :: WWW/HTTP :: WSGI
            Topic :: Scientific/Engineering
            Topic :: Software Development :: Libraries :: Python Modules
        '''.split('\n'))),
        author='Roberto De Almeida',
        author_email='rob@pydap.org',
        url='http://pydap.org/3.0/',
        license='MIT',

        packages=find_packages(),
        package_data=find_package_data("pydap", package="pydap",
                only_in_packages=False),
        include_package_data=True,
        zip_safe=False,
        namespace_packages=['pydap', 'pydap.responses', 'pydap.handlers'],

        test_suite='nose.collector',

        dependency_links=[],
        install_requires=[
            'numpy',
            'httplib2>=0.4.0',
            'Genshi',
            'Paste',
            'PasteScript',
            'PasteDeploy',
        ],
        extras_require={
            'test': ['nose', 'wsgi_intercept'],
            'docs': ['Paver', 'Sphinx', 'Pygments'],
        },
        entry_points="""
            [pydap.response]
            dds = pydap.responses.dds:DDSResponse
            das = pydap.responses.das:DASResponse
            dods = pydap.responses.dods:DODSResponse
            asc = pydap.responses.ascii:ASCIIResponse
            ascii = pydap.responses.ascii:ASCIIResponse
            ver = pydap.responses.version:VersionResponse
            version = pydap.responses.version:VersionResponse
            help = pydap.responses.help:HelpResponse
            html = pydap.responses.html:HTMLResponse
      
            [paste.app_factory]
            server = pydap.wsgi.file:make_app
      
            [paste.paster_create_template]
            pydap = pydap.wsgi.templates:DapServerTemplate
        """,
    ),

    sphinx=Bunch(
        builddir='.build',
    ),
    cog=Bunch(
        includedir='.',
    ),
    deploy=Bunch(
        htmldir = path('pydap.org'),
        username = 'roberto',
        host = 'pydap.org',
        hostpath = '/var/www/sites/pydap.org-3.x/'
    ),
    minilib=Bunch(
        extra_files=['doctools']
    ), 
)


if paver.doctools.has_sphinx:
    @task
    @needs(['cog', 'paver.doctools.html'])
    def html():
        """Build the docs and put them into our package."""
        destdir = path('pydap.org')
        destdir.rmtree()
        builtdocs = path("docs") / options.builddir / "html"
        builtdocs.move(destdir)


@task
@needs(['generate_setup', 'minilib', 'setuptools.command.sdist'])
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass


@task
@cmdopts([
    ('username=', 'u', 'Username to use when logging in to the servers')
])
def deploy():
    """Deploy the HTML to the server."""
    sh("rsync -avz -e ssh %s/ %s@%s:%s" % (options.htmldir,
            options.username, options.host, options.hostpath))

