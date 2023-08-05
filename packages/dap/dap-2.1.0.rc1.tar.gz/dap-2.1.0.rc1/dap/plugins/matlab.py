"""Plugin for Matlab files.

A simple plugin for serving Matlab files. Should work with files from
Matlab 4 and 5.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import os.path
import re

from dap import dtypes
from dap.server import BaseHandler
from dap.exceptions import ConstraintExpressionError, OpenFileError
from dap.util import matfile
from dap.util.arrayterator import arrayterator
from dap.helper import getslice, typecode_to_dap

extensions = r"""^.*\.(mat|MAT)$"""

BUFFER = 10000  # how many values to read at a time.


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        self.filepath = filepath
        self.environ = environ
        dir, self.filename = os.path.split(filepath)

        # Add dummy description.
        self.description = self.filename

    def _parseconstraints(self, constraints=None):
        try:
            f = matfile.open(self.filepath)
            self.environ['logger'].info('Opened file %s.' % self.filepath)
        except:
            message = 'Unable to open file %s.' % self.filepath
            self.environ['logger'].error(message)
            raise OpenFileError, message

        # Build the dataset.
        dataset = dtypes.DatasetType(name=self.filename)
        dataset.attributes['filename'] = self.filename

        # Add attributes.
        dataset.attributes['header'] = f.header_text

        # Add THREDDS attributes.
        dataset.attributes['THREDDS'] = {'dataType': 'Grid'}
        
        # Get workspace.
        workspace = f.GetAllArrays()
        f.close()

        # Build arrays.
        if not constraints:
            for name,array_ in workspace.items():
               data = arrayterator(array_, nrecs=BUFFER)
               dataset[name] = dtypes.ArrayType(data=data,
                                                name=name,
                                                shape=array_.shape,
                                                type=typecode_to_dap[array_.typecode()])
        else:
            vars = constraints.split(',')
            for var in vars:
                p = re.compile(r'(?P<name>[^[]+)(?P<shape>(\[[^\]]+\])*)')
                c = p.match(var).groupdict()
                name = c['name']

                if name not in workspace:
                    message = 'Variable %s not in dataset.' % name
                    self.environ['logger'].error(message)
                    raise ConstraintExpressionError, message

                # Build array.
                array_ = workspace[name]
                slice_ = getslice(c['shape'], array_.shape)

                # Slice it.
                array_ = array_[slice_].copy()
                data = arrayterator(array_, nrecs=BUFFER)
                dataset[name] = dtypes.ArrayType(data=data,
                                                 name=name,
                                                 shape=array_.shape,
                                                 type=typecode_to_dap[array_.typecode()])

        return dataset
