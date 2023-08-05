"""Proxy class to DAP data.

This module implements a proxy object that behaves like an array and 
downloads data transparently from a DAP server when sliced. It is used
when building a representation of the dataset, and should be not 
directly used.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import sys
#import urllib

from dap import dtypes
from dap.xdr import DapUnpacker
from dap.helper import fix_slice
from dap.util import http
from dap.util.arrayterator import arrayterator

class Proxy(object):
    """A proxy to data stored in a DODS server.
    
        >>> dapvar = dtypes.ArrayType(name='LAT121_47', type='Float64', shape=[27])
        >>> data = Proxy("http://server.pydap.org/test/sst.nc", dapvar)
        >>> print data[:]
        [-50.47520065 -48.57049942 -46.66579819 -44.76110077 -42.85639954 -40.9516983 
              -39.04700089 -37.14220047 -35.23749924 -33.33280182 -31.42810059
              -29.52339935 -27.61860085 -25.71389961 -23.80920029 -21.90439987
              -19.99970055 -18.09499931 -16.19020081 -14.28549957 -12.38080025
              -10.47603989  -8.57131004  -6.66657019  -4.76183987  -2.85710001
               -0.95236802]
        >>> print data[0]
        [-50.47520065]
        >>> print data[-1]
        [-0.95236802]
        >>> print data[-2:-1]
        [-2.85710001]
        >>> print data[-3:-1]
        [-4.76183987 -2.85710001]
        >>> print data[-4:-2]
        [-6.66657019 -4.76183987]
    """
    def __init__(self, url, dapvar):
        self.url = url
        self.var = dapvar

        self.shape = self.var.shape

    def __len__(self):
        """Emulate the behaviour of a Numeric/numarray/scipy_core array.

        This method returns the length of the first dimension, so it can
        be used directly in functions from Numeric, numarray or Scipy
        Core.
        """
        try:
            return self.var.shape[0]
        except AttributeError:
            raise TypeError

    def __iter__(self):
        if isinstance(self.var, dtypes.ArrayType):
            return arrayterator(self[:])
        else:
            return iter(self[:])

    def __getitem__(self, index):
        """Download data from DAP server.
        
        When the proxy object is sliced, it build an URL from the slice
        and retrieves the data from the DAP server.
        """
        # Build the base URL.
        url = '%s.dods?%s' % (self.url, self.var.id)

        if isinstance(self.var, dtypes.ArrayType):
            # Fix the index for incomplete slices or ellipsis.
            index = fix_slice(len(self.var.shape), index)

            # Force index to tuple, to iterate over the slices.
            if not isinstance(index, tuple):
                index = index,

            # Iterate over the sliced dimensions.
            i = 0
            outshape = []
            for dimension in index:
                # If dimension is a slice, get start, step and stop.
                if isinstance(dimension, slice):
                    start = dimension.start  or 0
                    step  = dimension.step   or 1
                    if dimension.stop:
                        stop = dimension.stop-1
                    else:
                        stop = self.var.shape[i]-1

                # Otherwise, retrieve a single value.
                else:
                    start = dimension
                    stop  = dimension
                    step  = 1

                # When stop is not specified, use the shape.
                if stop == sys.maxint:
                    stop = self.var.shape[i]-1
                # Negative slices. 
                elif stop < 0:
                    stop = self.var.shape[i]+stop

                # Negative starting slices.
                if start < 0: start = self.var.shape[i]+start

                # Build the URL used to retrieve the data.
                url = '%s[%s:%s:%s]' % (url, str(start), str(step), str(stop))

                # outshape is a list of the slice dimensions.
                outshape.append(int((1+stop-start)/step))
                
                # Update to next dimension.
                i += 1

        else:
            # No need to resize the data.
            outshape = None

        # Check for filters.
        if self.var.filters:
            #ce = urllib.quote('&'.join(self.var.filters))
            # Some servers don't understand quoted CEs.
            ce = '&'.join(self.var.filters)
            url = '%s&%s' % (url, ce)

        # Fetch data.
        data = http.fetch(url)['data']

        # First lines are ASCII information that end with 'Data:\n'.
        start = data.index('Data:\n') + len('Data:\n')
        xdrdata = data[start:]
        
        # Unpack data.
        output = DapUnpacker(xdrdata, self.var, outshape).getvalue()

        return output


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
