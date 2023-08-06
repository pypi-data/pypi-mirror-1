# If true, then the svn revision won't be used to calculate the
# revision (set to True for real releases)
RELEASE = True

from setuptools import setup, find_packages
import sys, os

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

import dap.lib
version = '.'.join([str(_) for _ in dap.lib.__version__])

setup(name='dap',
      version=version,
      description="DAP (Data Access Protocol) client and server for Python.",
      long_description="""\
Implementation of the `Data Access Protocol <http://opendap.org>`_. 

This is a Python implementation of the Data Access Protocol, a
scientific protocol for data access developed by the OPeNDAP team
(http://opendap.org). This implementation is developed from scratch,
following the latest specification of the protocol (DAP 2.0 Draft
Community Standard 2005/04/27) and based on my experience with
OPeNDAP servers on the wild.

Using this module one can access hundreds of scientific datasets
from Python programs, accessing data in an efficient, transparent
and pythonic way. Arrays are manipulated like normal multi-dimensional
arrays (like numpy.array, e.g.), with the fundamental difference
that data is downloaded on-the-fly when a variable is sliced.
Sequential data can be filtered on the server side before being
downloaded, saving bandwith and time.

The module also implements a DAP server, allowing datasets from a
multitude of formats (netCDF, Matlab, CSV, GrADS/GRIB files, SQL
RDBMS) to be served on the internet. The server specifies a plugin
API for supporting new data formats in an easy way. The DAP server
is implemented as a WSGI application (see PEP 333), running on a
variery of servers, and can be combined with WSGI middleware to
support authentication, gzip compression and much more.

The latest version is available in a `Subversion repository
<http://pydap.googlecode.com/svn/trunk/dap#egg=dap-dev>`_.""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='dap opendap dods data science climate meteorology oceanography',
      author='Roberto De Almeida',
      author_email='rob@pydap.org',
      url='http://pydap.org/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['dap.plugins', 'dap.responses'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'httplib2',
      ],
      extras_require={
          'server': ['Paste', 'PasteScript', 'PasteDeploy', 'Cheetah'],
          'proxy': ['Paste', 'WSGIFilter'],
      },
      entry_points="""
      # -*- Entry points: -*-
      [dap.response]
      dds = dap.responses.dds
      das = dap.responses.das
      dods = dap.responses.dods
      asc = dap.responses.ascii
      ascii = dap.responses.ascii
      ver = dap.responses.version
      version = dap.responses.version
      help = dap.responses.help

      [dap.plugin]
      csv = dap.plugins.csvfiles

      [paste.app_factory]
      main = dap.wsgi.application:make_app
      proxy = dap.wsgi.proxy:make_proxy

      [paste.paster_create_template]
      dap_server = dap.wsgi.templates:DapServerTemplate
      dap_plugin = dap.plugins.templates:DapPluginTemplate
      """,
      )
      
