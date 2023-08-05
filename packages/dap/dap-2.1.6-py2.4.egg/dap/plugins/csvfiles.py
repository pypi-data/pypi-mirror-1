"""Plugin for CSV (comma separated values) files.

This plugin serves sequential data from a CSV file. It's a bit hackish and
abuses ``lambda`` and ``itertools``, but it works *very* nice. The plugin
uses the ``getfilter()`` function to create a filter from the constraint
expression, and applies it on-the-fly on the data as it is being read.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import os.path
import re
import csv
import itertools
import urllib

from dap import dtypes, responses
from dap.server import BaseHandler
from dap.exceptions import OpenFileError
from dap.helper import getfilter
from dap.util.safeeval import expr_eval

extensions = r"""^.*\.(csv|CSV)$"""


def lazy_eval(s):
    """Try to evalute expression or fallback to string.
    
        >>> lazy_eval("1")
        1
        >>> lazy_eval("None")
        'None'
    """
    try:
        s = expr_eval(s)
    except:
        pass
    return s
    

class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        """Handler constructor.
        """
        self.filepath = filepath
        self.environ = environ
        dir, self.filename = os.path.split(filepath)

        # Add dummy description.
        self.description = self.filename

    def _parseconstraints(self, constraints=None):
        """Dataset builder.

        This method opens a CSV reader, extracts the variable names from
        the first line and returns an iterator to the data. Constraint
        expressions or handled by the ``get_filter()`` function and a 
        filter to return only data from the columns corresponding to the
        requested variables.
        """
        try:
            self._file = open(self.filepath)
            self.environ['logger'].info('Opened file %s.' % self.filepath)
            reader = csv.reader(self._file)
        except:
            message = 'Unable to open file %s.' % self.filepath
            self.environ['logger'].error(message)
            raise OpenFileError, message

        if constraints:
            constraints = urllib.unquote(constraints)
            constraints = constraints.split('&')

            # Selection expression.
            queries = constraints[1:]

            # Requested vars.
            vars_ = constraints[0]
            vars_ = vars_.split(',')

        # Build the dataset.
        dataset = dtypes.DatasetType(name=self.filename)
        dataset.attributes['filename'] = self.filename

        # Create sequence.
        seq = dataset['csv'] = dtypes.SequenceType(name='csv')

        # Read variable names.
        variables = reader.next()
        ids = ['csv.%s' % n for n in variables]

        # Peek types.
        line = reader.next()
        types_ = [lazy_eval(i) for i in line]
        types_ = [responses.das.typeconvert[type(i)] for i in types_]

        if not constraints:
            for var, type_ in zip(variables, types_):
                seq[var] = dtypes.BaseType(name=var, type=type_)
        else:
            # Check for shorthand notation. Ugly, ugly hack. If the requested
            # var is not in the list of ids we append 'csv.' to it, assuming
            # that is was requested using the shorthand notation syntax.
            vars_ = [['csv.%s' % var, var][var in ids] for var in vars_]

            for var in vars_:
                i = ids.index(var)
                name = variables[i]
                type_ = types_[i]
                seq[name] = dtypes.BaseType(name=name, type=type_)

        # Reinsert first data line.
        data = itertools.chain([line], reader)
        data = itertools.imap(lambda l: map(lazy_eval, l), data)

        if constraints:
            # Get filter.
            f = getfilter(queries, ids)
            data = itertools.ifilter(f, data)

            # Get selected variables.
            if vars_:
                indexes = [ids.index(n) for n in vars_]
                filter_ = lambda x: [x[i] for i in indexes]
                data = itertools.imap(filter_, data)
            
        # Insert data directly into sequence.
        seq.data = data

        return dataset

    def close(self):
        """Close the CSV file."""
        if hasattr(self, '_file'): self._file.close()


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
