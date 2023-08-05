"""Plugin for gzip/bzip2 compressed files.

This plugin uncompresses the file to a temporary location and calls the
appropriate plugin to handle it. This way, *any* supported file can be
gzipped or bzipped.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import os

from dap.server import BaseHandler
from dap.plugins import loadhandler
from dap.exceptions import OpenFileError

extensions = r"""^.*\.(gz|bz2)$"""

TMP = '/tmp'

commands = {'.gz' : 'gunzip -c %s > %s',
            '.bz2': 'bunzip2 -c %s > %s',
           }


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        self.environ = environ

        dir, filename = os.path.split(filepath)
        filename, extension = os.path.splitext(filename)

        # New file.
        self.filepath = os.path.join(TMP, filename)

        # Uncompress file.
        try:
            command = commands[extension] % (filepath, self.filepath)
            os.popen(command)
        except:
            message = 'Unable to open file %s.' % filepath
            self.environ['logger'].error(message)
            raise OpenFileError, message
        
    def _parseconstraints(self, constraints=None):
        H = loadhandler(self.filepath, self.environ)
        return H._parseconstraints(constraints)

    def close(self):
        # Remove file.
        os.unlink(self.filepath)
