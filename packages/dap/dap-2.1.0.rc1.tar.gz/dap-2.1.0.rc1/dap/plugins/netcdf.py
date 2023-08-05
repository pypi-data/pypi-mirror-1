"""Plugin for NetCDF files.

This is the reference plugin for the Python DAP server, since it's the one
I use the most. ;)
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

from __future__ import division

import os.path
import re
import types

# Requires NetCDFFile from http://starship.python.net/~hinsen/ScientificPython/.
from Scientific.IO.NetCDF import NetCDFFile

from dap import dtypes
from dap.server import BaseHandler
from dap.exceptions import ConstraintExpressionError, OpenFileError
from dap.util.arrayterator import arrayterator
from dap.helper import getslice, typecode_to_dap

extensions = r"""^.*\.(nc|NC)$"""

BUFFER = 1000  # how many values to read at a time.


def get_attributes(var):
    attributes = {}
    attrs = [attr for attr in dir(var) if not isinstance(getattr(var, attr), types.BuiltinMethodType)]
    for attr in attrs:
        value = getattr(var, attr)
        if hasattr(value, 'tolist'): value = value.tolist()
        attributes[attr] = value

    return attributes


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        self.filepath = filepath
        self.environ = environ
        
        dir, self.filename = os.path.split(filepath)
        try:
            self._file = NetCDFFile(filepath)
            self.environ['logger'].info('Opened file %s.' % filepath)

            # Add description.
            self.description = getattr(self._file, 'title', self.filename)
        except:
            message = 'Unable to open file %s.' % filepath
            self.environ['logger'].error(message)
            raise OpenFileError, message

    def _parseconstraints(self, constraints=None):
        # Build the dataset.
        dataset = dtypes.DatasetType(name=self.filename)

        # Add attributes as NC_GLOBAL.
        nc_global = dataset.attributes['NC_GLOBAL'] = get_attributes(self._file)

        # Add DODS_EXTRA for Unlimited dimensions.
        for dim, length in self._file.dimensions.items():
            if length is None:
                dataset.attributes['DODS_EXTRA'] = {'Unlimited_Dimension': dim}
                break  # only one unlimited dimension.

        # Add THREDDS attributes.
        thredds = dataset.attributes['THREDDS'] = {'dataType': 'Grid'}
        
        grids = [g for g in self._file.variables if g not in self._file.dimensions]

        if not constraints:
            # Build the grids.
            for name in grids:
                # Instantiate the grid.
                grid = self._file.variables[name]
                if grid.dimensions:
                    data = arrayterator(grid, nrecs=BUFFER)
                    g = dataset[name] = dtypes.GridType(data=data, 
                                                        name=name,
                                                        dimensions=grid.dimensions,
                                                        shape=grid.shape,
                                                        type=typecode_to_dap[grid.typecode()],
                                                        attributes=get_attributes(grid))
                    # Build maps.
                    for mapname,shape in zip(g.dimensions, g.shape):
                        if mapname in self._file.variables:
                            map_ = self._file.variables[mapname]
                            data = arrayterator(map_, nrecs=BUFFER)
                            dataset[mapname] = g.maps[mapname] = dtypes.ArrayType(data=data,
                                                                                  name=mapname,
                                                                                  shape=map_.shape,
                                                                                  type=typecode_to_dap[map_.typecode()],
                                                                                  attributes=get_attributes(map_))
                        else:
                            # Some NetCDF files have dimensions without values?!
                            self.environ['logger'].warning('Dimension %s in file %s without values.' % (mapname, self.filepath))
                            dataset[mapname] = g.maps[mapname] = dtypes.ArrayType(data=range(shape),
                                                                                  name=mapname,
                                                                                  shape=[shape],
                                                                                  type='Int32',
                                                                                  attributes={})
                else:
                    g = dataset[name] = dtypes.BaseType(data=grid.getValue(),
                                                        name=name,
                                                        type=typecode_to_dap[grid.typecode()],
                                                        attributes=get_attributes(grid))
            # Leftover arrays.
            arrays = [a for a in self._file.variables if a not in dataset.keys()]
            for name in arrays:
                array_ = self._file.variables[name]
                data = arrayterator(array_, nrecs=BUFFER)
                dataset[name] = dtypes.ArrayType(data=data,
                                                 name=name,
                                                 shape=array_.shape,
                                                 type=typecode_to_dap[array_.typecode()],
                                                 attributes=get_attributes(array_))
        else:
            vars = constraints.split(',')
            for var in vars:
                p = re.compile(r'(?P<name>[^[]+)(?P<shape>(\[[^\]]+\])*)')
                c = p.match(var).groupdict()
                name = c['name']

                #if name not in self._file.variables and name not in self._file.dimensions:
                #    raise ConstraintExpressionError, 'Variable %s not in dataset.' % name

                # Check if var is grid or array.
                if name not in self._file.dimensions and '.' not in name:
                    grid = self._file.variables[name]
                    slice_ = getslice(c['shape'], grid.shape)
                    start  = [i.start for i in slice_]
                    stride = [i.step for i in slice_]
                    shape  = [(i.stop - i.start) for i in slice_]

                    # Build grid.
                    if grid.dimensions:
                        data = arrayterator(grid, start=start, shape=shape, stride=stride, nrecs=BUFFER)
                        g = dataset[name] = dtypes.GridType(data=data,
                                                            name=name,
                                                            dimensions=grid.dimensions,
                                                            shape=shape,
                                                            type=typecode_to_dap[grid.typecode()],
                                                            attributes=get_attributes(grid))
                        # Build maps.
                        dimmap = zip(g.dimensions, start, shape, stride)
                        for mapname,start_,shape_,stride_ in dimmap:
                            if mapname in self._file.variables:
                                map_ = self._file.variables[mapname]
                                data = arrayterator(map_, start=[start_], shape=[shape_], stride=[stride_], nrecs=BUFFER)
                                g.maps[mapname] = dtypes.ArrayType(data=data,
                                                                   name=mapname,
                                                                   shape=[shape_],
                                                                   type=typecode_to_dap[map_.typecode()],
                                                                   attributes=get_attributes(map_))
                            else:
                                # Some NetCDF files have dimensions without values?!
                                self.environ['logger'].warning('Dimension %s in file %s without values.' % (mapname, self.filepath))
                                g.maps[mapname] = dtypes.ArrayType(data=range(shape_),
                                                                   name=mapname,
                                                                   shape=[shape_],
                                                                   type='Int32',
                                                                   attributes={})
                    else:
                        g = dataset[name] = dtypes.BaseType(data=grid.getValue(),
                                                            name=name,
                                                            type=typecode_to_dap[grid.typecode()],
                                                            attributes=get_attributes(grid))
                else:
                    # Build array.
                    if '.' in name:
                        try:
                            grid, name = name.split('.')
                            assert grid in grids
                            assert name in self._file.variables[grid].dimensions or name == grid
                        except:
                            message = 'Invalid name in constraint expression: %s.' % c['name'] 
                            self.environ['logger'].error(message)
                            raise ConstraintExpressionError, message

                        array_ = self._file.variables[name]
                        slice_ = getslice(c['shape'], array_.shape)
                        start  = [i.start for i in slice_]
                        stride = [i.step for i in slice_]
                        shape  = [(i.stop - i.start) for i in slice_]

                        data = arrayterator(array_, start=start, shape=shape, stride=stride, nrecs=BUFFER)
                        if not grid in dataset.keys():
                            structure = dataset[grid] = dtypes.StructureType(name=grid)
                        structure[name] = dtypes.ArrayType(data=data,
                                                           name=name,
                                                           shape=shape,
                                                           type=typecode_to_dap[array_.typecode()],
                                                           attributes=get_attributes(array_))
                    else:
                        if name in self._file.variables:
                            array_ = self._file.variables[name]
                            slice_ = getslice(c['shape'], array_.shape)
                            start  = [i.start for i in slice_]
                            stride = [i.step for i in slice_]
                            shape  = [(i.stop - i.start) for i in slice_]
                            
                            data = arrayterator(array_, start=start, shape=shape, stride=stride, nrecs=BUFFER)
                            dataset[name] = dtypes.ArrayType(data=data,
                                                             name=name,
                                                             shape=shape,
                                                             type=typecode_to_dap[array_.typecode()],
                                                             attributes=get_attributes(array_))
                        elif name in self._file.dimensions:
                            # Some NetCDF files have dimensions without values.
                            self.environ['logger'].warning('Dimension %s in file %s without values.' % (name, self.filepath))
                            shape = self._file.dimensions[name]
                            dataset[name] = dtypes.ArrayType(data=range(shape),
                                                             name=name,
                                                             shape=[shape],
                                                             type='Int32',
                                                             attributes={})

        return dataset

    def close(self):
        self._file.close()
