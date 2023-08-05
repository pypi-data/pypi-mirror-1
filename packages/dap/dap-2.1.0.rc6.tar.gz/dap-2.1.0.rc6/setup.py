"""DAP (Data Access Protocol) client and server for Python.

The Data Access Protocol (DAP) is a data transmission protocol
designed specifically for science data. The protocol relies on the
widely used HTTP and MIME standards, and provides data types to
accommodate gridded data, relational data, and time series, as well
as allowing users to define their own data types.

This module implements a DAP client that can access remote datasets
stored in DAP servers. The client downloads metadata describing the
datasets, and builds array-like objects that act as proxies for the
data. These objects download the data from the server transparently
when necessary.

The module also implements a DAP server, able to serve data from
different formats through a plugin architecture. The server is
implemented as a WSGI application, and can be run on a variety of
servers: as a CGI script; with Twisted and mod_python; or even as
a ISAPI extension under IIS; for example.

For more information on the DAP, visit http://opendap.org/.
"""

classifiers = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Internet
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

import dap
version = '.'.join([str(_) for _ in dap.__version__])

# Generate description and long_description.
doclines = __doc__.split("\n")

setup(
    name = "dap",
    version = version,
    packages = find_packages(),

    # Scripts to run and control the server.
    scripts = [
        'servers/dap-server.py',
        'servers/server-ctl',
    ],

    # Example configuration for Paste Deploy.
    package_data = {
        '': ['servers/paste.conf'],
    },

    # Requirements.
    install_requires = [
        'fpconst',
    ],

    # Extra requirements.
    extras_require = {
        'server': ['Paste'],
    },

    entry_points = {
        'dap.plugin'          : ['netcdf = dap.plugins.netcdf',
                                 'matlab = dap.plugins.matlab',
                                 'csv = dap.plugins.csvfiles',
                                 'sql = dap.plugins.sql',
                                 'compression = dap.plugins.compress',
                                 'python = dap.plugins.pydap',
                                ],

        'paste.app_factory'   : ['main = dap.wsgi.application:make_app',
                                ],
        'paste.filter_factory': ['catalog = dap.wsgi.middleware:make_catalog_filter',
                                 'logger = dap.util.logger:make_logger_filter',
                                 'memcache = dap.util.memcached:make_memcached_filter',
                                 'diskcache = dap.util.diskcache:make_diskcache_filter',
                                ],
    },

    zip_safe = True,

    # Metadata for PyPI.
    author = "Roberto De Almeida",
    author_email = "rob@pydap.org",

    description = doclines[0],
    long_description = "\n".join(doclines[2:]),
    license = "MIT",
    keywords = "dods opendap dap data science network oceanography meteorology climate",
    url = "http://pydap.org/",
    download_url = "http://pydap.org/dap-%s.tar.gz" % version,
    platforms = ['any'],
    classifiers = filter(None, classifiers.split("\n")),
)
