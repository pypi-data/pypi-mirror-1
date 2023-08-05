"""Plugin for datasets generated from Python code.

This plugins load datasets from Python code. It runs **arbitrary code**
from the data file, so it should be used only for testing and in a
trusted environment.

If you want to enable this module, set the variable ``ENABLED`` to
``True``.
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
        """Handler constructor.
        """
        if not ENABLED: raise PluginError, 'Plugin not enabled!'

        self.filepath = filepath
        self.environ = environ
        
        self.dir, self.filename = os.path.split(filepath)

    def _parseconstraints(self, constraints=None):
        """Dataset builder.

        This method simply imports the referenced file, we should be a
        Python module with a ``DatasetType`` object called ``dataset``.
        """
        # Add dir to sys.path.
        sys.path.insert(0, self.dir)

        # Load module.
        name = self.filename[:-3]  # strip .py
        module = __import__(name, globals(), locals(), ['*'])
        module = reload(module)
        self.environ['logger'].debug('Loading module %s.' % name)

        dataset = module.dataset
        return trim(dataset, constraints, copy=False)
