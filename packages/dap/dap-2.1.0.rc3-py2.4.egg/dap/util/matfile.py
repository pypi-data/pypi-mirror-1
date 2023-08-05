# Copyright (c) 2003 Heiko Henkelmann, 2005 Roberto De Almeida.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.




"""Module with Class and Functions to read MatLab(tm) 5 compatible data files

2005-07-01: fixed problem with big-endian machines.
"""

import struct
import array
import cStringIO

import Numeric


__author__ = ["Heiko Henkelmann <heiko@hhenkelmann.de>", "Roberto De Almeida <rob@pydap.org>"]
__version__= "0.1.1"

__all__ = ['matWorkspace', 'matStruct', 'matObject', 'matFile',
           'read', 'open']


def _split_fixed_width(sequence, width):
    """Split a sequence into fixed width parts and return a list of them.

    """
    return [ sequence[i:i+width] for i in xrange(0,len(sequence),width) ]




class matWorkspace(dict):
    """Mimics a Workspace similar to the one used in ML.

    Essentially a dictionary with currently two additional Methods:
        who  - Print a short overview over the ML variables in the workspace.
        whos - Print a verbose overview over the ML variables in the workspace.

    """
    
    _TypeDict = {
        'l' : 'int',
        '1' : 'int',
        's' : 'int',
        'f' : 'single',
        'd' : 'double',
        'O' : 'cell',
        'F' : 'complex single',
        'D' : 'complex double',
        }

    def who(self):
        """Print a short overview over the ML variables in the workspace.
        
        """
        print
        print "Workspace variables are:"
        print
        variables = self.keys()
        variables.sort()
        i=0
        for variable in variables:
            i=i+1
            print "%-8s" % (variable,),
            if (i%5)==0:
                print

    def whos(self):
        """Print a verbose overview over the ML variables in the workspace.

        """
        print
        print "   Name    Class"
        print
        variables = self.keys()
        variables.sort()
        for variable in variables:
            print "   %-8s" % (variable,),
            if isinstance(self[variable], matStruct):
                print "struct array",
            elif isinstance(self[variable], matObject):
                print "struct object",
            elif isinstance(self[variable], type("")):
                print "string",
            elif isinstance(self[variable], type(Numeric.array([1]))):
                print self._TypeDict[self[variable].typecode()],
                print "array",
            else:
                print "unkown type,"

            print

class matStruct(dict):
    """Python representation of a ML Struct Array.

    Essentially a dictionary.

    """
    pass

class matObject(dict):
    """Python representation of a ML Object.

    Essentially a dictionary with one additional property:
        ClassName

    """
    def __init__(self, ClassName):
        self.ClassName = ClassName
        dict.__init__(self)



miINT8 = 1
miUINT8 = 2
miINT16 = 3
miUINT16 = 4
miINT32 = 5
miUINT32 = 6
miSINGLE = 7
miDOUBLE = 9
miINT64 =12
miUINT64 = 13
miMATRIX = 14

miNumbers = (
    miINT8,
    miUINT8,
    miINT16,
    miUINT16,
    miINT32,
    miUINT32,
    miSINGLE,
    miDOUBLE,
    miINT64,
    miUINT64,
    )

miDataTypes = {
    miINT8 : ('miINT8', 1,'1'),
    miUINT8 : ('miUINT8', 1,'1'),
    miINT16 : ('miINT16', 2,'s'),
    miUINT16 :('miUINT16',2,'s'),
    miINT32 : ('miINT32',4,'l'),
    miUINT32 : ('miUINT32',4,'l'),
    miSINGLE : ('miSINGLE',4,'f'),
    miDOUBLE : ('miDOUBLE',8,'d'),
    miINT64 : ('miINT64',8,None),   # TODO How to handle 64bit Integers
    miUINT64 : ('miUINT64',8,None),
    miMATRIX : ('miMATRIX',0,None),
    }

miDataTypesArray = {
    miINT8 : ('miINT8', 1,'b'),
    miUINT8 : ('miUINT8', 1,'B'),
    miINT16 : ('miINT16', 2,'h'),
    miUINT16 :('miUINT16',2,'H'),
    miINT32 : ('miINT32',4,'l'),
    miUINT32 : ('miUINT32',4,'L'),
    miSINGLE : ('miSINGLE',4,'f'),
    miDOUBLE : ('miDOUBLE',8,'d'),
    miINT64 : ('miINT64',8,None),   # TODO How to handle 64bit Integers
    miUINT64 : ('miUINT64',8,None),
    miMATRIX : ('miMATRIX',0,None),
    }

    

mxCELL_CLASS = 1
mxSTRUCT_CLASS = 2
mxOBJECT_CLASS = 3
mxCHAR_CLASS = 4
mxSPARSE_CLASS = 5
mxDOUBLE_CLASS = 6
mxSINGLE_CLASS = 7
mxINT8_CLASS = 8
mxUINT8_CLASS = 9
mxINT16_CLASS = 10
mxUINT16_CLASS = 11
mxINT32_CLASS = 12
mxUINT32_CLASS = 13

mxArrays = (
    mxCHAR_CLASS,
    mxDOUBLE_CLASS,
    mxSINGLE_CLASS,
    mxINT8_CLASS,
    mxUINT8_CLASS,
    mxINT16_CLASS,
    mxUINT16_CLASS,
    mxINT32_CLASS,
    mxUINT32_CLASS,
    )


mxArrayTypes = {
    mxCELL_CLASS : 'mxCELL_CLASS',
    mxSTRUCT_CLASS : 'mxSTRUCT_CLASS',
    mxOBJECT_CLASS : 'mxOBJECT_CLASS',
    mxCHAR_CLASS : 'mxCHAR_CLASS',
    mxSPARSE_CLASS : 'mxSPARSE_CLASS',
    mxDOUBLE_CLASS : 'mxDOUBLE_CLASS',
    mxSINGLE_CLASS : 'mxSINGLE_CLASS',
    mxINT8_CLASS : 'mxINT8_CLASS',
    mxUINT8_CLASS : 'mxUINT8_CLASS',
    mxINT16_CLASS : 'mxINT16_CLASS',
    mxUINT16_CLASS : 'mxUINT16_CLASS',
    mxINT32_CLASS : 'mxINT32_CLASS',
    mxUINT32_CLASS : 'mxUINT32_CLASS',
    }



class matFile(object):
    def __init__(self, name_or_file):

        if not isinstance(name_or_file, file):
            self.file = file(name_or_file,'rb')

        self.header_text = self.file.read(124).rstrip()
        raw_version = self.file.read(2)
        header_endian_indicator = self.file.read(2)

        test = struct.unpack('=H', header_endian_indicator)[0]
        self.native = (test == 19785)

        if header_endian_indicator == 'MI':
            self.little_endian = False
            self.endian = '>'
        elif header_endian_indicator == 'IM':
            self.little_endian = True
            self.endian = '<'
        else:
            raise IOError, 'Not a Matlab(tm) Version 5 format'

        self.header_version = struct.unpack(self.endian+'H',raw_version)[0]

    def cat(self, verbose=False):
        print
        print self.header_text
        print
        if verbose:
            print "Version: %x" % self.header_version
            print "Little endian: %s" % self.little_endian
            print "Native: %s" % self.native
            print

    def _isCompressed(self, raw_tag):
        if self.little_endian:
            return (ord(raw_tag[2])>0) or (ord(raw_tag[3])>0)
        else:
            return (ord(raw_tag[0])>0) or (ord(raw_tag[1])>0)

    def _parse_Element(self, file=None):
        """ return type, data

        """
        if file is None:
            file = self.file
        raw_tag = file.read(8)
        if len(raw_tag)==0:   # nothing left to be parsed
            return None, None
        elif len(raw_tag)!=8:
            raise "incomplete data element"
        if self._isCompressed(raw_tag):
            type, numofbytes = struct.unpack(self.endian+'HHxxxx',raw_tag)
            data_bytes = raw_tag[4:4+numofbytes]
        else:
            type, numofbytes = struct.unpack(self.endian+'LL',raw_tag)
            data_bytes = file.read(numofbytes)
            mod8 = numofbytes%8
            if mod8:
                skip = 8-mod8
                file.seek(skip,1)

        if type in miNumbers:
            result = self._parse_data(data_bytes, type, numofbytes)
            name = None
        elif type == miMATRIX:
            strio = cStringIO.StringIO(data_bytes)
            name, result = self._parse_matrix(strio)
            strio.close()
        else:
            raise IOError, 'Unknown data type'
        return name, result

    def _parse_data(self, data_bytes, type, numofbytes):
        numofelements = numofbytes/miDataTypes[type][1]

        # Fix endianess.
        if not self.native:
            data_bytes = array.array(miDataTypesArray[type][2], data_bytes)
            data_bytes.byteswap()
            data_bytes_bytes = data_bytes.tostring()

        elements = Numeric.fromstring(data_bytes,miDataTypes[type][2])
        return elements

    def _parse_matrix(self, strio):
        type,cmplx=self._parse_array_flags(strio)
        dims = self._parse_dimensions_array(strio)
        # We need to invert the dimensions so it works with Ferret. Weird.
        dims = dims[::-1]
        name = self._parse_array_name(strio)
        if type in mxArrays:
            unused, result=self._parse_Element(strio)
            if type == mxCHAR_CLASS:
                result = ''.join(result.astype('c'))
            else:
                if cmplx:
                    unused, imag=self._parse_Element(strio)
                    result = result + 1j * imag
                result = Numeric.reshape(result,dims)
                # We also need to transpose the matrix.
                result = Numeric.transpose(result)
        elif type == mxCELL_CLASS:
            length = dims[0]*dims[1]
            result = Numeric.zeros(length, Numeric.PyObject)
            for i in range(length):
                dummy, sa = self._GetNextSubArray(strio)
                result[i]= sa
            result = Numeric.reshape(result,dims)
            # We also need to transpose the matrix.
            result = Numeric.transpose(result)
        elif type == mxSTRUCT_CLASS:
            FieldNameLength = self._parse_Element(strio)[1][0]
            unused,FieldNames = self._parse_Element(strio)
            FieldNames = _split_fixed_width(FieldNames,FieldNameLength)
            FieldNames = [ ''.join(x.astype('c')).strip('\x00')
                           for x in FieldNames]
            result = matStruct()
            for element in FieldNames:
                dummy, sa = self._GetNextSubArray(strio)
                result[element]=sa
        elif type == mxOBJECT_CLASS:
            ClassName = self._parse_array_name(strio)
            FieldNameLength = self._parse_Element(strio)[1][0]
            unused, FieldNames = self._parse_Element(strio)
            FieldNames = _split_fixed_width(FieldNames,FieldNameLength)
            FieldNames = [ ''.join(x.astype('c')).strip('\x00')
                           for x in FieldNames]
            result = matObject(ClassName)
            for element in FieldNames:
                dummy, sa = self._GetNextSubArray(strio)
                result[element]=sa
        elif type == mxSPARSE_CLASS:
            unused, unused = self._parse_Element(strio)
            unused, unused = self._parse_Element(strio)
            unused, unused = self._parse_Element(strio)
            if cmplx:
                unused, unused = self._parse_Element(strio)
            result = "Can't handle sparse matrix"
        return name, result

    def _parse_array_flags(self, strio):
        data = strio.read(8)
        type, numofbytes = struct.unpack(self.endian+'LL',data)
        data = strio.read(numofbytes)
        (Class_,Flags)=struct.unpack('BBxxxxxx',data) # TODO remove hard coded
        if (Flags & 8):
            cmplx = 1
        else:
            cmplx = 0
        return Class_, cmplx

    def _parse_dimensions_array(self, strio):
        unused, dims=self._parse_Element(strio);
        return tuple(dims)

    def _parse_array_name(self, strio):
        unused, data=self._parse_Element(strio);
        #name = ''.join(data.astype('c'))
        name = data.tostring()
        return name

    def GetNextArray(self):
        name, result = self._parse_Element()
        return name, result

    def _GetNextSubArray(self, file):
        name, result = self._parse_Element(file)
        return name, result

    def GetAllArrays(self):
        workspace = matWorkspace()
        while 1:
            name,array = self.GetNextArray()
            if name is None:
                break
            workspace[name]=array

        return workspace

    def close(self):
        self.file.close()



def read(filename):
    """Read a complete ML file and return content as a Workspace.

    """
    mf=matFile(filename)
    workspace = mf.GetAllArrays()
    mf.close()
    return workspace


def open(filename):
    """Open a ML file and return an associated matFile object.

    """
    mf=matFile(filename)
    return mf


def _test():
    """Test case only used for internal purposes"""
    import time
    start = time.time()

    for count in range(1,6):
        print 79 * '*'
        filename = "test%s.mat" % (count,)
        print filename, ':'
        mf=matFile(filename)
        mf.cat(verbose=True)
        workspace = mf.GetAllArrays()
        workspace.whos()

    end = time.time()

    print
    print
    print "Time needed: %s seconds" % (end-start,)


if __name__ == '__main__':
    _test()
