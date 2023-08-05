"""Plugin for NetCDF files.

This plugin serves data from a netCDF file, using the interface from
``Scientific.IO.NetCDF``. It uses a buffer to read the data in small
blocks, so it is able to server datasets of unlimited size.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

from __future__ import division

import os.path
import re
import types
import urllib

# Requires NetCDFFile from http://starship.python.net/~hinsen/ScientificPython/.
from Scientific.IO.NetCDF import NetCDFFile

from dap import dtypes
from dap.server import BaseHandler
from dap.exceptions import ConstraintExpressionError, OpenFileError
from dap.util.arrayterator import arrayterator
from dap.helper import getslice, typecode_to_dap, lenslice

extensions = r"""^.*\.(nc|NC)$"""

BUFFER = 10000  # how many values to read at a time.


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        """Handler constructor.
        """
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
        """Dataset builder.

        This method build the dataset according to the constraint
        expression. Dimensions in the netCDF file are treated as arrays,
        and other variables as grids.
        """
        # Build the dataset.
        dataset = dtypes.DatasetType(name=self.filename)

        # Add attributes as NC_GLOBAL.
        nc_global = dataset.attributes['NC_GLOBAL'] = self._file.__dict__.copy()

        # Add DODS_EXTRA for Unlimited dimensions.
        for dim, length in self._file.dimensions.items():
            if length is None:
                dataset.attributes['DODS_EXTRA'] = {'Unlimited_Dimension': dim}
                break  # only one unlimited dimension.

        # Add THREDDS attributes.
        thredds = dataset.attributes['THREDDS'] = {'dataType': 'Grid'}
        
        # Get all grids from the netCDF file.
        grids = []
        for name in self._file.variables:
            # Must not be a dimension.
            if name not in self._file.dimensions:
                var = self._file.variables[name]
                for dim in var.dimensions:
                    # Check that all dimensions are defined.
                    if dim not in self._file.variables: break
                grids.append(name)

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
                                                        attributes=grid.__dict__.copy())
                    # Build maps.
                    for mapname,shape in zip(g.dimensions, g.shape):
                        if mapname in self._file.variables:
                            map_ = self._file.variables[mapname]
                            data = arrayterator(map_, nrecs=BUFFER)
                            dataset[mapname] = g.maps[mapname] = dtypes.ArrayType(data=data,
                                                                                  name=mapname,
                                                                                  shape=map_.shape,
                                                                                  type=typecode_to_dap[map_.typecode()],
                                                                                  attributes=map_.__dict__.copy())
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
                                                        attributes=grid.__dict__.copy())
            # Leftover arrays.
            arrays = [a for a in self._file.variables if a not in dataset.keys()]
            for name in arrays:
                array_ = self._file.variables[name]
                data = arrayterator(array_, nrecs=BUFFER)
                dataset[name] = dtypes.ArrayType(data=data,
                                                 name=name,
                                                 shape=array_.shape,
                                                 type=typecode_to_dap[array_.typecode()],
                                                 dimensions=array_.dimensions,  # compatibility with ncks
                                                 attributes=array_.__dict__.copy())
        else:
            constraints = urllib.unquote(constraints)
            vars = constraints.split(',')
            for var in vars:
                p = re.compile(r'(?P<name>[^[]+)(?P<shape>(\[[^\]]+\])*)')
                c = p.match(var).groupdict()
                name = c['name']

                #if name not in self._file.variables and name not in self._file.dimensions:
                #    raise ConstraintExpressionError, 'Variable %s not in dataset.' % name

                # Check if var is grid or array.
                #if name not in self._file.dimensions and '.' not in name:
                if name in grids and '.' not in name:
                    grid = self._file.variables[name]
                    slice_ = getslice(c['shape'], grid.shape)
                    start  = [i.start for i in slice_]
                    stride = [i.step for i in slice_]
                    #shape  = [(i.stop - i.start) for i in slice_]
                    shape  = [lenslice(i) for i in slice_]

                    # Build grid.
                    if grid.dimensions:
                        data = arrayterator(grid, start=start, shape=shape, stride=stride, nrecs=BUFFER)
                        g = dataset[name] = dtypes.GridType(data=data,
                                                            name=name,
                                                            dimensions=grid.dimensions,
                                                            shape=shape,
                                                            type=typecode_to_dap[grid.typecode()],
                                                            attributes=grid.__dict__.copy())
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
                                                                   attributes=map_.__dict__.copy())
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
                                                            attributes=grid.__dict__.copy())
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
                        #shape  = [(i.stop - i.start) for i in slice_]
                        shape  = [lenslice(i) for i in slice_]

                        data = arrayterator(array_, start=start, shape=shape, stride=stride, nrecs=BUFFER)
                        if not grid in dataset.keys():
                            structure = dataset[grid] = dtypes.StructureType(name=grid)
                        structure[name] = dtypes.ArrayType(data=data,
                                                           name=name,
                                                           shape=shape,
                                                           type=typecode_to_dap[array_.typecode()],
                                                           dimensions=array_.dimensions,
                                                           attributes=array_.__dict__.copy())
                    else:
                        if name in self._file.variables:
                            array_ = self._file.variables[name]
                            slice_ = getslice(c['shape'], array_.shape)
                            start  = [i.start for i in slice_]
                            stride = [i.step for i in slice_]
                            #shape  = [(i.stop - i.start) for i in slice_]
                            shape  = [lenslice(i) for i in slice_]
                            
                            data = arrayterator(array_, start=start, shape=shape, stride=stride, nrecs=BUFFER)
                            dataset[name] = dtypes.ArrayType(data=data,
                                                             name=name,
                                                             shape=shape,
                                                             type=typecode_to_dap[array_.typecode()],
                                                             attributes=array_.__dict__.copy())
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
        """Close the netCDF file."""
        self._file.close()
