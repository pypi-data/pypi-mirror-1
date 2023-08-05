"""DAS parser.

This module implements a DAS parser based on ``shlex.shlex``.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import shlex
import operator

import fpconst

from dap import dtypes
from dap.parsers import BaseParser
from dap.util.safeeval import expr_eval


# string.digits + string.ascii_letters + string.punctuation - {};[]:="
#WORDCHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&\'()*+,-./<>?@\\^_`|~'
WORDCHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&\'()*+-./<>?@\\^_`|~'

atomic_types = ('byte', 'int', 'uint', 'int16', 'uint16', 'int32', 'uint32', 'float32', 'float64', 'string', 'url', 'alias')


class DASParser(BaseParser):
    r"""A parser for Dataset Attribute Structure.

    First we create a dataset and get its DAS:

        >>> from dap import dtypes
        >>> from dap.responses import das, dds
        >>> dataset = dtypes.DatasetType(name='test', attributes={'GLOBAL': {'name': 'teste'}})
        >>> dataset['a'] = dtypes.BaseType(name='a', data=1, type='Int32', attributes={'pi': 3.1415})
        >>> das_ = ''.join(das.build(dataset)).strip()
        >>> print das_
        Attributes {
            GLOBAL {
                String name "teste";
            }
            a {
                Float32 pi 3.1415;
            }
        }

    Now we build a new dataset from the DDS:
    
        >>> dds_ = ''.join(dds.build(dataset)).strip()
        >>> from dap.parsers.dds import DDSParser
        >>> dataset2 = DDSParser(dds_, '').parse()
        >>> print ''.join(dds.build(dataset2)).strip()
        Dataset {
            Int32 a;
        } test;

    The new dataset has no attributes, since it was built only from the 
    DDS. We pass it to the DAS parser, together with the DAS:
    
        >>> dataset2 = DASParser(das_, '', dataset2).parse()
        >>> print ''.join(das.build(dataset2)).strip()
        Attributes {
            GLOBAL {
                String name "teste";
            }
            a {
                Float32 pi 3.1415;
            }
        }

    The parser should accept additional metadata:

        >>> das_ = 'Attributes {\nGLOBAL {\nString name "teste";\n}\nMETADATA {\nMETAMETADATA {\nString foo "bar";\n}\n}\na {\nFloat32 pi 3.1415;\n}\n}'
        >>> dataset2 = DASParser(das_, '', dataset2).parse()
        >>> print dataset2.attributes
        {'GLOBAL': {'name': ['teste']}, 'METADATA': {'METAMETADATA': {'foo': ['bar']}}}
        >>> print ''.join(das.build(dataset2)).strip()
        Attributes {
            GLOBAL {
                String name "teste";
            }
            METADATA {
                METAMETADATA {
                    String foo "bar";
                }
            }
            a {
                Float32 pi 3.1415;
            }
        }

    Checking a bug Rob Cermak found:

        >>> dataset3 = dtypes.DatasetType(name='dataset')
        >>> latLonCoordSys = dataset3['latLonCoordSys'] = dtypes.BaseType(name='latLonCoordSys', type='String', attributes={'_CoordinateAxes': "time lat long", 'DODS': {'strlen': 0}})
        >>> das_ = ''.join(das.build(dataset3)).strip()
        >>> print das_
        Attributes {
            latLonCoordSys {
                DODS {
                    Int32 strlen 0;
                }
                String _CoordinateAxes "time lat long";
            }
        }
        >>> dds_ = ''.join(dds.build(dataset3)).strip()
        >>> dataset4 = DDSParser(dds_, '').parse()
        >>> dataset4 = DASParser(das_, '', dataset4).parse()
        >>> print ''.join(das.build(dataset4)).strip()
        Attributes {
            latLonCoordSys {
                DODS {
                    Int32 strlen 0;
                }
                String _CoordinateAxes "time lat long";
            }
        }
    """
    def __init__(self, das, url, dataset):
        shlex.shlex.__init__(self, das)
        self.url = url
        self._dataset = dataset

        # Attribute target when parsing.
        self._target = self._dataset

        # Add punctuation to words.
        #self.wordchars += '/_%.-+'
        self.wordchars = WORDCHARS

    def parse(self):
        """Parse the DAS and return a ``DatasetType`` object with the attributes populated."""
        self._consume('attributes')
        self._consume('{')
        self._attrconts()
        self._consume('}')
        return self._dataset

    def _attrconts(self):
        while not self._check('}'):
            self._attrcont()

    def _attrcont(self):
        # Check for attributes or containers.
        if self._check(*atomic_types):
            name, values = self._attribute()
            self._target.attributes[name] = values
        else:
            self._container()

    def _container(self):
        name = self.get_token()
        self._consume('{')

        # Check for flat attributes, since it's relatively common.
        if '.' in name:
            names = name.split('.')
            old_target = self._target

            # Get the appropriate target: foo.bar should point to dataset['foo']['bar']
            d = [old_target]
            d.extend(names)
            try:
                self._target = reduce(operator.getitem, d)
            except KeyError:
                # This happens in this dataset, because it's wrong. We just ignore the attributes.
                # http://motherlode.ucar.edu/cgi-bin/dods/DODS-3.2.1/nph-dods/dods/amsua15_2002.279_22852_0156_0342_GC.eos.das
                pass  

            self._attrconts()
            self._target = old_target
        elif isinstance(self._target, dtypes.StructureType) and name in self._target.keys():
            old_target = self._target
            self._target = old_target[name]
            self._attrconts()
            self._target = old_target
        else:
            self._target.attributes[name] = self._metadata()

        self._consume('}')

    def _metadata(self):
        output = {}
        while not self._check('}'):
            if self._check(*atomic_types):
                name, values = self._attribute()
                output[name] = values
            else:
                name = self.get_token()
                self._consume('{')
                output[name] = self._metadata()
                self._consume('}')

        return output

    def _attribute(self):
        # Get type and name.
        type = self.get_token()
        name = self.get_token()

        # Get values: value_1 (, value_n)*
        values = []
        while not self._check(';'):
            value = self.get_token()

            # Check for NaN.
            if value.lower() == 'nan':
                value = fpconst.NaN
            else:
                try:
                    value = expr_eval(value)
                except: 
                    # IDs are unquoted. Leave it as string.
                    pass
            values.append(value)
            
            if self._check(','): self._consume(',')

        self._consume(';')
        return name, values


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
