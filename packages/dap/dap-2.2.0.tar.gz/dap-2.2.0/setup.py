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

import dap
version = '.'.join([str(_) for _ in dap.__version__])

setup(name='dap',
      version=version,
      description="DAP (Data Access Protocol) client and server for Python.",
      long_description="""\
Implementation of the `Data Access Protocol <http://opendap.org>`_. 

The latest version is available in a `Subversion repository
<http://pydap.googlecode.com/svn/trunk/dap#egg=dap-dev>`_.""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='dap opendap dods data science climate meteorology oceanography',
      author='Roberto De Almeida',
      author_email='rob@pydap.org',
      url='http://pydap.org/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'httplib2',
      ],
      extras_require={
          'server': ['Paste', 'PasteScript', 'PasteDeploy', 'Cheetah'],
      },
      entry_points="""
      # -*- Entry points: -*-
      [dap.plugin]
      csv = dap.plugins.csvfiles

      [dap.response]
      dds = dap.responses.dds
      das = dap.responses.das
      dods = dap.responses.dods
      asc = dap.responses.ascii
      ascii = dap.responses.ascii
      ver = dap.responses.version
      help = dap.responses.help

      [paste.app_factory]
      main = dap.wsgi.application:make_app

      [paste.paster_create_template]
      dap_server = dap.util.templates:DapServerTemplate
      """,
      )
      
