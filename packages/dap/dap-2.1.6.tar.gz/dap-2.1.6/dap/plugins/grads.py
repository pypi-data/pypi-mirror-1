__author__ = "Roberto De Almeida <rob@pydap.org>"

import os.path
import re

from dap import dtypes
from dap.server import BaseHandler
from dap.exceptions import OpenFileError

extensions = r"""^.*\.(ctl|CTL)$"""


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        """Handler constructor.
        """
        self.filepath = filepath
        self.environ = environ
        dir, self.filename = os.path.split(filepath)

    def _parseconstraints(self, constraints=None):
        """Dataset builder.
        """
        try:
            self._file = open(self.filepath)
            #self.environ['logger'].info('Opened file %s.' % self.filepath)
        except:
            message = 'Unable to open file %s.' % self.filepath
            #self.environ['logger'].error(message)
            raise OpenFileError, message

        # Build the dataset.
        dataset = dtypes.DatasetType(name=self.filename)
        dataset.attributes['filename'] = self.filename

        for line in self._file:
            k, v = line.split(' ', 1)
            if k == "vars":
                nvars = int(v)
                p = re.compile(r"""(?P<name>\w+) (?P<shape>(\d+\ )+)\- (?P<long_name>.*?)\[(?P<units>.*)\]""")
                for var in range(nvars):
                    line = self._file.readline()
                    print line
                    m = p.match(line)
                    if m: print m.groupdict()
        
        return dataset

    def close(self):
        """Close the CTL file."""
        if hasattr(self, '_file'): self._file.close()


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    import os
    h = Handler("/home/roberto/Projects/dap/data/grib/d2006-03-16-1200/descriptor1.ctl", os.environ)
    h._parseconstraints()
    #_test()
