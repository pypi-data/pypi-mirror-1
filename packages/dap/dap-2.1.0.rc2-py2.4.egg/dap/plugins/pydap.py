"""Plugin for datasets generated from Python code.

This plugins load datasets from Python code. It runs arbitrary code from 
the data file, so it should be used only for testing.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import os.path
import sys

from dap.server import BaseHandler
from dap.helper import trim
from dap.exceptions import PluginError

extensions = r"""((^.*/)|(^))_[^/]+\.py$"""

# Change by hand to enable.
ENABLED = False


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        if not ENABLED: raise PluginError, 'Plugin not enabled!'

        self.filepath = filepath
        self.environ = environ
        
        self.dir, self.filename = os.path.split(filepath)

    def _parseconstraints(self, constraints=None):
        # Add dir to sys.path.
        sys.path.insert(0, self.dir)

        # Load module.
        name = self.filename[:-3]  # strip .py
        module = __import__(name, globals(), locals(), ['*'])
        self.environ['logger'].debug('Loading module %s.' % name)

        dataset = module.dataset
        return trim(dataset, constraints)
