import os.path

from dap import dtypes
from dap.server import BaseHandler
from dap.helper import parse_querystring

# This is a regular expression that should match the
# files supported by your plugin.
extensions = r"""^.*\.(ext|EXT)$"""  


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        """
        This method receives the full path to the
        file and the WSGI environment (you probably
        won't need this.
        """
        dir, self.filename = os.path.split(filepath)

    def _parseconstraints(self, constraints=None):
        """
        This method should build the dataset according to the
        constraint expression. 
        """
        # Build dataset.
        dataset = dtypes.DatasetType(name=self.filename)

        # Grab requested variables.
        fields, queries = parse_querystring(constraints)

        # Add variables to dataset here depending on
        # ``fields`` and ``queries``.
        # ...

        return dataset
                    
    def close(self):
        """
        Close files, connections, etc.
        """
        pass
