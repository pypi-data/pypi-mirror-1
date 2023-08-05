"""Plugin for CSV (comma separated values) files.

This plugin serves sequential data from a CSV file. It's a bit hackish and
abuses ``lambda`` and ``itertools``, but it works *very* nice. The plugin
uses the ``buildfilter()`` function to create a filter from the constraint
expression, and applies it on-the-fly on the data as it is being read.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import sys
import os.path
import re
import csv
import itertools
import urllib

from dap import dtypes
from dap.responses.das import typeconvert
from dap.server import BaseHandler
from dap.exceptions import OpenFileError
from dap.helper import buildfilter, parse_querystring
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
        self.description = "Comma Separated Values from file %s." % self.filename

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
            reader = csv.reader(self._file)
        except:
            message = 'Unable to open file %s.' % self.filepath
            raise OpenFileError(message)

        # Parse constraints.
        fields, queries = parse_querystring(constraints)

        # Build the dataset.
        dataset = dtypes.DatasetType(name=self.filename)
        dataset.attributes['filename'] = self.filename

        # Create sequence.
        name = self.filename[:-4].split('_', 1)[0]
        seq = dataset[name] = dtypes.SequenceType(name=name)

        # Read variables names.
        fieldnames = reader.next()
        ids = ['%s.%s' % (seq.name, n) for n in fieldnames]

        # We need to read the first line to grab the fields names and peek types.
        line = reader.next()
        types_ = [lazy_eval(i) for i in line]
        types_ = [typeconvert[type(i)] for i in types_]
        
        # Get list of requested variables.
        if seq.id in fields.keys():
            req_ids = []  # put everything
        else:
            # Check for shorthand notation. Ugly, ugly hack. If the requested
            # var is not in the list of ids we append the sequence id to it,
            # assuming that is was requested using the shorthand notation syntax.
            req_ids = [['%s.%s' % (seq.id, var), var][var in ids] for var in fields.keys()]

        # Add requested variables.
        if req_ids:
            indexes = []
            for id_ in req_ids:
                if id_ in ids:
                    i = ids.index(id_)
                    indexes.append(i)
                    name = fieldnames[i]
                    type_ = types_[i]
                    seq[name] = dtypes.BaseType(name=name, type=type_)
        else:
            for name, type_ in zip(fieldnames, types_):
                seq[name] = dtypes.BaseType(name=name, type=type_)

        # Reinsert first data line.
        data = itertools.chain([line], reader)
        data = itertools.imap(lambda l: map(lazy_eval, l), data)

        # Filter results.
        if queries:
            # Get filter.
            filter1 = buildfilter(queries, ids)
            data = itertools.ifilter(filter1, data)

        # Select only requested variables.
        if req_ids:
            filter2 = lambda x: [x[i] for i in indexes]
            data = itertools.imap(filter2, data)

        # Apply stride to sequence?
        slice_ = fields.get(seq.id)
        if slice_:
            slice_ = slice_[0]
            data = itertools.islice(data, slice_.start or 0, slice_.stop or sys.maxint, slice_.step or 1)
        else:
            # Check stored variables. If more than one variable is selected,
            # and they have different slices, use the most restritive start,
            # step and stop.
            #
            # Behaviour rev-eng'ed from http://test.opendap.org/dap/data/ff/1998-6-avhrr.dat
            slices = []
            for var in seq.walk():
                slice_ = fields.get(var.id)
                if slice_: slices.append(slice_[0])
            if slices:
                start, step, stop = zip(*[(s.start or 0, s.step or 1, s.stop or sys.maxint) for s in slices])
                data = itertools.islice(data, max(start), min(stop), max(step))

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
