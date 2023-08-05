"""Fast(er) implementation of xdrlib for the DAP.

This module reimplements Python's xdrlib module for the DAP. It uses the
"array" module for speed, and encodes bytes according to the DAP spec.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import array
import struct
import operator

import fpconst

import dap
from dap import dtypes
from dap.lib import isiterable


# Convert from DAP types to array types.
typeconvert = {'float64': ('d', 8),
               'float32': ('f', 4),
               'float'  : ('f', 4),
               'uint'   : ('I', 4),
               'uint16' : ('I', 4),
               'uint32' : ('I', 4),
               'int'    : ('i', 4),
               'int16'  : ('i', 4),
               'int32'  : ('i', 4),
              }

                     
class DapPacker(object):
    r"""Pack variable data into XDR.

    This is a faster reimplementation of xdrlib using the native module
    "array".

        >>> dapvar = dtypes.BaseType(data=1, type='Int32')
        >>> xdrdata = DapPacker(dapvar)
        >>> for i in xdrdata:
        ...     print repr(i)
        '\x00\x00\x00\x01'

        >>> dapvar = dtypes.ArrayType(data=['one', 'two'], shape=[2], type='String')
        >>> xdrdata = DapPacker(dapvar)
        >>> for i in xdrdata:
        ...     print repr(i)
        '\x00\x00\x00\x02'
        '\x00\x00\x00\x03one\x00'
        '\x00\x00\x00\x03two\x00'

        >>> dapvar = dtypes.ArrayType(data=range(2), shape=[2], type='Int32')
        >>> xdrdata = DapPacker(dapvar)
        >>> for i in xdrdata:
        ...     print repr(i)
        '\x00\x00\x00\x02\x00\x00\x00\x02'
        '\x00\x00\x00\x00\x00\x00\x00\x01'

        >>> dapvar = dtypes.ArrayType(data=range(2), shape=[2], type='Float64')
        >>> xdrdata = DapPacker(dapvar)
        >>> for i in xdrdata:
        ...     print repr(i)
        '\x00\x00\x00\x02\x00\x00\x00\x02'
        '\x00\x00\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00'

    Check against test server at http://dods.coas.oregonstate.edu:8080/dods/dts/test.01:

        >>> import urllib
        
        >>> dapvar = dtypes.BaseType(data=0, type='Byte')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.01.dods?b").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)
        
        >>> dapvar = dtypes.BaseType(data=1, type='Int32')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.01.dods?i32").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)
        
        >>> dapvar = dtypes.BaseType(data=0, type='UInt32')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.01.dods?ui32").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)

        >>> dapvar = dtypes.BaseType(data=0, type='Int16')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.01.dods?i16").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)
        
        >>> dapvar = dtypes.BaseType(data=0, type='UInt16')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.01.dods?ui16").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)
        
        >>> dapvar = dtypes.BaseType(data=0.0, type='Float32')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.01.dods?f32").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)
        
        >>> dapvar = dtypes.BaseType(data=1000.0, type='Float64')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.01.dods?f64").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)

        >>> dapvar = dtypes.BaseType(data="This is a data test string (pass 0).", type='String')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.01.dods?s").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)

        >>> dapvar = dtypes.BaseType(data="http://www.dods.org", type='Url')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.01.dods?u").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata[:-1] == ''.join(xdrdata)[:-1]  # server pads with \x01?
        
    Check against test server at http://dods.coas.oregonstate.edu:8080/dods/dts/test.02:

        >>> dapvar = dtypes.ArrayType(data=range(25), shape=[25], type='Byte')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.02.dods?b").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)

        >>> dapvar = dtypes.ArrayType(data=[i*2048 for i in range(25)], shape=[25], type='Int32')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.02.dods?i32").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)
        
        >>> dapvar = dtypes.ArrayType(data=[i*4096 for i in range(25)], shape=[25], type='UInt32')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.02.dods?ui32").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)
        
        >>> dapvar = dtypes.ArrayType(data=[i*256 for i in range(25)], shape=[25], type='Int16')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.02.dods?i16").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)
        
        >>> dapvar = dtypes.ArrayType(data=[i*1024 for i in range(25)], shape=[25], type='UInt16')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.02.dods?ui16").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)
        
        >>> dapvar = dtypes.ArrayType(data=[0.0, 0.009999833, 0.019998666, 0.029995501, 0.039989334, 0.04997917, 0.059964005, 0.06994285, 0.0799147, 0.08987855, 0.099833414, 0.1097783, 0.119712204, 0.12963414, 0.13954312, 0.14943813, 0.15931821, 0.16918235, 0.17902957, 0.1888589, 0.19866933, 0.2084599, 0.21822962, 0.22797753, 0.23770262], shape=[25], type='Float32')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.02.dods?f32").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)
        
        >>> dapvar = dtypes.ArrayType(data=[1.0, 0.9999500004166653, 0.9998000066665778, 0.9995500337489875, 0.9992001066609779, 0.9987502603949663, 0.9982005399352042, 0.9975510002532796, 0.9968017063026194, 0.9959527330119943, 0.9950041652780257, 0.9939560979566968, 0.9928086358538663, 0.9915618937147881, 0.9902159962126371, 0.9887710779360422, 0.9872272833756269, 0.9855847669095608, 0.9838436927881214, 0.9820042351172703, 0.9800665778412416, 0.9780309147241483, 0.9758974493306055, 0.9736663950053749, 0.9713379748520297], shape=[25], type='Float64')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.02.dods?f64").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)

        >>> dapvar = dtypes.ArrayType(data=["This is a data test string (pass %d)." % i for i in range(25)], shape=[25], type='String')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.02.dods?s").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)
        >>> print repr(testdata)
        >>> print repr(''.join(xdrdata))

        >>> dapvar = dtypes.ArrayType(data=["http://www.dods.org"]*25, shape=[25], type='Url')
        >>> xdrdata = DapPacker(dapvar)
        >>> testdata = urllib.urlopen("http://dods.coas.oregonstate.edu:8080/dods/dts/test.02.dods?u").read()
        >>> testdata = testdata[testdata.index("Data:\n")+6:]
        >>> assert testdata == ''.join(xdrdata)
    """
    def __init__(self, dapvar, data=None):
        self.var = dapvar

        if data is None:
            data = dapvar.data

        # Make data iterable.
        if not isiterable(data): data = [data]

        # Put data in blocks/chunks. Useful for arrayterators.
        self.data = getattr(data, 'blocks', [data])

    def __iter__(self):
        # Yield length (twice) if array.
        if isinstance(self.var, dtypes.ArrayType):
            if self.var.type.lower() in ['url', 'string']:
                yield self._pack_length()
            else:
                yield self._pack_length() * 2

        # Bytes are sent differently.
        if self.var.type.lower() == 'byte':
            for b in self._yield_bytes(): yield b
        # String are zero padded to 4n.
        elif self.var.type.lower() in ['url', 'string']:
            for block in self.data:
                for d in block:
                    yield self._pack_string(d)
        else:
            type_,size = typeconvert[self.var.type.lower()]
            for block in self.data:
                data = array.array(type_, block)

                # Ensure big-endianess.
                if not fpconst._big_endian: data.byteswap()

                data = data.tostring()
                yield data

    def _pack_length(self):
        """Yield array length."""
        shape = getattr(self.var, 'shape', [1])
        length = reduce(operator.mul, shape)
        return struct.pack('>L', length)

    def _yield_bytes(self):
        r"""Yield bytes.

        Bytes are encoded as is, padded to a four-byte boundary. An array
        of five bytes, eg, is encoded as eight bytes:

            >>> dapvar = dtypes.ArrayType(data=range(5), shape=[5], type='Byte')
            >>> xdrdata = DapPacker(dapvar)
            >>> for i in xdrdata:
            ...     print repr(i)
            '\x00\x00\x00\x05\x00\x00\x00\x05'
            '\x00'
            '\x01'
            '\x02'
            '\x03'
            '\x04'
            '\x00\x00\x00'

        Again, the first line correponds to the array size packed twice,
        followed by the bytes and the padding.
        """
        count = 0
        for block in self.data:
            data = array.array('b', block).tostring()
            for d in data:
                yield d
                count += 1

        padding = (4 - (count % 4)) % 4
        yield padding * '\0'

    def _pack_string(self, s):
        # Pack length first.
        n = len(s)
        length = struct.pack('>L', n)

        n = ((n+3)/4)*4
        data = length + s + (n - len(s)) * '\0'
        return data


class DapUnpacker(object):
    r"""A XDR data unpacker.

    Unpacking data from a base type:

        >>> from dap import dtypes
        >>> from dap.responses import dods
        >>> dapvar = dtypes.BaseType(data=1, name='b', type='Byte')
        >>> print dapvar.data
        1
        >>> for line in dods.build(dapvar):
        ...     print repr(line)
        '\x01'
        '\x00\x00\x00'
        >>> data = DapUnpacker(''.join(dods.build(dapvar)), dapvar)
        >>> print data.getvalue()
        1
    
    An array of bytes:

        >>> dapvar = dtypes.ArrayType(data=range(5), shape=[5], type='Byte')
        >>> data = DapUnpacker(''.join(dods.build(dapvar)), dapvar, outshape=[5])
        >>> print data.getvalue()
        [0 1 2 3 4]

    Another array:

        >>> dapvar = dtypes.ArrayType(data=range(25), shape=[5,5], type='Float32')
        >>> data = DapUnpacker(''.join(dods.build(dapvar)), dapvar, outshape=[5,5])
        >>> print data.getvalue()
        [[  0.   1.   2.   3.   4.]
         [  5.   6.   7.   8.   9.]
         [ 10.  11.  12.  13.  14.]
         [ 15.  16.  17.  18.  19.]
         [ 20.  21.  22.  23.  24.]]
    """
    def __init__(self, data, dapvar, outshape=None):
        self.__buf = data
        self.var = dapvar
        self.outshape = outshape
        
        # Buffer position.
        self.__pos = 0

    def getvalue(self):
        # Get current position.
        i = self.__pos

        # Check for empty sequence.
        if self.__buf[i:i+4] == '\xa5\x00\x00\x00':
            return []

        # Check for sequence with data.
        elif self.__buf[i:i+4] == '\x5a\x00\x00\x00':
            # Unpack sequence start marker (uint 1509949440).
            mark = self._unpack_uint()
            out = []
            while mark != 2768240640L:
                tmp = self.getvalue()
                out.append(tmp)
                # Unpack marker.
                mark = self._unpack_uint()
            return out

        # Get data length.
        n = 1
        if isinstance(self.var, dtypes.ArrayType):
            n = self._unpack_uint()
            # Strings pack the size only once?
            if self.var.type.lower() not in ['url', 'string']:
                self._unpack_uint()

        # Bytes are treated differently.
        if getattr(self.var, 'type', '').lower() == 'byte':
            out = self._unpack_bytes(n)
        # As are strings...
        elif self.var.type.lower() in ['url', 'string']:
            out = self._unpack_string(n)
        else:
            i = self.__pos
            type_,size = typeconvert[self.var.type.lower()]
            out = array.array(type_, self.__buf[i:i+n*size])
            self.__pos = i+n*size

            # Ensure big-endianess.
            if not fpconst._big_endian: out.byteswap()

        if isinstance(self.var, dtypes.ArrayType):
            # Numeric/numarray can't handle arrays of strings.
            if self.var.type.lower() not in ['url', 'string']:
                # Convert to array and reshape.
                out = dap.array(out)
                if self.outshape:
                    out.shape = tuple(self.outshape)
        elif isinstance(self.var, dtypes.BaseType):
            out = out[0]

        return out

    def _unpack_uint(self):
        i = self.__pos
        self.__pos = j = i+4
        data = self.__buf[i:j]
        if len(data) < 4:
            raise EOFError
        x = struct.unpack('>L', data)[0]
        try:
            return int(x)
        except OverflowError:
            return x

    def _unpack_bytes(self, count):
        i = self.__pos
        out = array.array('b', self.__buf[i:i+count])
        padding = (4 - (count % 4)) % 4
        self.__pos = i + count + padding
        
        return out
        
    def _unpack_string(self, count):
        out = []
        for s in range(count):
            # Unpack string length.
            n = self._unpack_uint()

            i = self.__pos
            j = i+n
            data = self.__buf[i:j]

            # Fix cursor position.
            padding = (4 - (n % 4)) % 4
            self.__pos = j + padding
            
            out.append(data)
        return out


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

