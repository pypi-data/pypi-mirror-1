"""Parsing routines.

This module implements a DDS parser.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import shlex

from dap import dtypes, proxy
from dap.parsers import BaseParser


# string.digits + string.ascii_letters + string.punctuation - {};[]:="
#WORDCHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&\'()*+,-./<>?@\\^_`|~'
WORDCHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&\'()*+-./<>?@\\^_`|~'

        
atomic_types = ('byte', 'int', 'uint', 'int16', 'uint16', 'int32', 'uint32', 'float32', 'float64', 'string', 'url')
constructors = ('grid', 'sequence', 'structure')
        

class DDSParser(BaseParser):
    """A parser for Dataset Descriptor Structure.
    
    First we create a dataset and get its DDS:

        >>> from dap.responses import dds
        >>> dataset = dtypes.DatasetType(name='test')
        >>> dataset['a'] = dtypes.BaseType(name='a', data=1, type='Int32')
        >>> dds_ = ''.join(dds.build(dataset)).strip()
        >>> print dds_
        Dataset {
            Int32 a;
        } test;

    Now we try to parse it. We'll get a second dataset that should have the
    same DDS:
    
        >>> dataset2 = DDSParser(dds_, '').parse()
        >>> print ''.join(dds.build(dataset2)).strip()
        Dataset {
            Int32 a;
        } test;
    """
    def __init__(self, dds, url):
        shlex.shlex.__init__(self, dds)
        self.url = url
                        
        # Add punctuation to words.
        #self.wordchars += '/_%.-+'
        self.wordchars = WORDCHARS

    def parse(self):
        return self._dataset()

    def _dataset(self):
        self._consume('Dataset')
        self._consume('{')

        dataset = dtypes.DatasetType()

        # Scan type declarations.
        while self._check(*(atomic_types + constructors)):
            var = self._declaration()
            dataset[var.name] = var

        self._consume('}')

        # Scan the filename.
        dataset.name = self.get_token()
        self._consume(';')

        return dataset

    def _declaration(self):
        if self._check('grid'): return self._grid()
        elif self._check('sequence'): return self._sequence()
        elif self._check('structure'): return self._structure()
        else: return self._base_declaration()

    def _base_declaration(self):
        type_ = self.get_token()
        name = self.get_token()

        # Get the dimensions, if any.
        shape, dimensions = self._dimensions()
        self._consume(';')

        if shape:
            var = dtypes.ArrayType(name=name, shape=shape, dimensions=dimensions, type=type_)
        else:
            var = dtypes.BaseType(name=name, type=type_)
            var.shape = None

        # Set the data.
        url = self.url[:-4]  # strip .dds from URL.
        var.data = proxy.Proxy(url, var)
        return var

    def _dimensions(self):
        shape = []
        names = []
        while not self._check(';'):
            self._consume('[')
            _token = self.get_token()
            if self._check('='):
                names.append(_token)
                self._consume('=')
                shape.append(int(self.get_token()))
            else:
                shape.append(int(_token))

            self._consume(']')
        return tuple(shape), tuple(names)

    def _sequence(self):
        sequence = dtypes.SequenceType()
        self._consume('sequence')
        self._consume('{')

        while 1:
            var = self._declaration()
            sequence[var.name] = var
            if self._check('}'): break

        self._consume('}')

        # Get the sequence name.
        sequence.name = self.get_token()
        
        self._consume(';')
        return sequence

    def _structure(self):
        structure = dtypes.StructureType()
        self._consume('structure')
        self._consume('{')

        while 1:
            var = self._declaration()
            structure[var.name] = var
            if self._check('}'): break

        self._consume('}')

        # Get structure name.
        structure.name = self.get_token()

        self._consume(';')
        return structure

    def _grid(self):
        grid = dtypes.GridType()
        self._consume('grid')
        self._consume('{')

        # Scan the array.
        self._consume('array')
        self._consume(':')
        var = self._base_declaration()
        grid.array = var

        grid.dimensions = []
        
        # Scan the maps.
        self._consume('maps')
        self._consume(':')
        while 1:
            var = self._base_declaration()
            grid.maps[var.name] = var
            grid.dimensions.append(var.name)
            if self._check('}'): break

        self._consume('}')

        grid.name = self.get_token()
        self._consume(';')
        return grid


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
