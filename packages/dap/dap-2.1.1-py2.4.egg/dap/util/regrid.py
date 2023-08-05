"""Spline n-dimensional regridding."""

__author__ = 'Roberto De Almeida <rob@pydap.org>'

import copy
import bisect

import numarray
from numarray.nd_image import map_coordinates
from Scientific.Functions.Interpolation import InterpolatingFunction

from dap.util.arrayterator import arrayterator


def smart_slice(grid, bbox):
    """Slice a grid using map values instead of indexes.
    
        >>> from dap import dtypes
        >>> from numarray import *
        >>> a = arange(24, shape=(2,4,3), type = Float64)
        >>> g = dtypes.GridType(name='g', type='Float64', data=a, shape=[2,4,3], dimensions=['time', 'lat', 'lon'])
        >>> g.maps['lat'] = dtypes.ArrayType(name='lat', type='Float64', shape=[4])
        >>> g.maps['lat'].data = array([10.0, 20.0, 30.0, 40.0])
        >>> g.maps['lon'] = dtypes.ArrayType(name='lon', type='Float64', shape=[3])
        >>> g.maps['lon'].data = array([100.0, 110.0, 120.0])
        >>> g.maps['time'] = dtypes.ArrayType(name='time', type='Float64', shape=[2])
        >>> g.maps['time'].data = array([1.0, 2.0])
        >>> g2 = smart_slice(g, [(1.0, 2.0), (22.0, 28.0), (100.0, 105.0)])
        >>> print g2.shape
        (2, 2, 2)
        >>> for map_, data in g2.maps.items():
        ...     print map_, data[:]
        lat [ 20.  30.]
        lon [ 100.  110.]
        time [ 1.  2.]
        >>> print g2.data[:]
        [[[  3.   4.]
          [  6.   7.]]
        <BLANKLINE>
         [[ 15.  16.]
          [ 18.  19.]]]
    """
    # Create new grid.
    out = copy.deepcopy(grid)

    slice_ = []
    for dim, limits in zip(out.dimensions, bbox):
        map_ = out.maps[dim]
        
        start = max(0, bisect.bisect(map_, limits[0]) - 1)
        stop = min(map_.shape[0], bisect.bisect(map_, limits[1]) + 1)
        assert start < stop

        map_.data = map_.data[start:stop]
        slice_.append(slice(start, stop, None))

    out.data = grid.data[tuple(slice_)]
    out.shape = out.data.shape

    return out


# Based on http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/302478
def combine(dims):
    """Returns a list of all combinations of argument sequences.
    
        >>> combine([(1, 2), (3, 4)])
        [(1, 1, 2, 2), (3, 4, 3, 4)]
    """
    def rloop(dims, listout, comb):
        """Recursive looping function"""
        if dims:
            for item in dims[0]:
                newcomb = comb + [item]
                # call rloop w/ rem seqs, newcomb
                rloop(dims[1:], listout, newcomb)
        else:
            listout.append(comb)
    listout = []
    rloop(dims, listout, [])
    return zip(*listout)


def regrid_array(a, dims, ndims):
    """Spline interpolation into a new grid.

        >>> from numarray import *
        >>> a = arange(12, shape=(4,3), type=Float64)
        >>> lat = array([10.0, 20.0, 30.0, 40.0])
        >>> lon = array([100.0, 110.0, 120.0])
        >>> nlat = array([15.0, 30.0])
        >>> nlon = array([105.0, 110.0])
        >>> print regrid_array(a, [lat, lon], [nlat, nlon])
        [[ 1.3625  2.05  ]
         [ 6.3125  7.    ]]

    Interpolating in time:
        
        >>> b = arange(12, shape=(12,), type=Float64)
        >>> import datetime
        >>> time = [datetime.datetime(2005, 3, i+1) for i in range(12)]
        >>> from dap.util.coards import datetimeToUdunits
        >>> units = 'days since 2005-01-01 12:00:00 -3:00'
        >>> time = [datetimeToUdunits(dt, units) for dt in time]
        >>> time = array(time)
        >>> print time
        [ 58.5  59.5  60.5  61.5  62.5  63.5  64.5  65.5  66.5  67.5  68.5
          69.5]
        >>> ntime = datetime.datetime(2005, 3, 9, 18)
        >>> ntime = datetimeToUdunits(ntime, units)
        >>> ntime = [ntime]
        >>> print ntime
        [67.25]
        >>> print regrid_array(b, [time], [ntime])
        [ 8.76099596]
    """
    # Fix shape crazyness.
    if not isinstance(a.shape, tuple): a.shape = tuple(a.shape)

    # Linearly interpolate axes.
    indexes = []
    for dim, ndim in zip(dims, ndims):
        if not isinstance(dim.shape, tuple): dim.shape = tuple(dim.shape)
        interp = InterpolatingFunction([dim], numarray.arange(len(dim)), None)
        ##interp = InterpolatingFunction([dim], numarray.arange(len(dim)), 0.0)
        indexes.append([interp(i) for i in ndim])
    coordinates = combine(indexes)
        
    # Spline interpolation of data.
    b = map_coordinates(a, coordinates, output_type=None, output=None, order=3, mode='constant', cval=0.0, prefilter=True)
    b.shape = [len(ndim) for ndim in ndims]
    return b

def regrid(grid, ndims):
    """Regrid a GridType object.

        >>> from dap import dtypes
        >>> from numarray import *
        >>> a = arange(24, shape=(2,4,3), type = Float64)
        >>> g = dtypes.GridType(name='g', type='Float64', data=a, shape=[2,4,3], dimensions=['time', 'lat', 'lon'])
        >>> g.maps['lat'] = dtypes.ArrayType(name='lat', type='Float64', shape=[4])
        >>> g.maps['lat'].data = array([10.0, 20.0, 30.0, 40.0])
        >>> g.maps['lon'] = dtypes.ArrayType(name='lon', type='Float64', shape=[3])
        >>> g.maps['lon'].data = array([100.0, 110.0, 120.0])
        >>> g.maps['time'] = dtypes.ArrayType(name='time', type='Float64', shape=[2])
        >>> g.maps['time'].data = array([1.0, 2.0])
        >>> nlat = array([15.0, 30.0])
        >>> nlon = array([105.0, 110.0])
        >>> g2 = regrid(g, [g.maps['time'], nlat, nlon])
        >>> print g2.data
        [[[  1.3625   2.05  ]
          [  6.3125   7.    ]]
        <BLANKLINE>
         [[ 13.3625  14.05  ]
          [ 18.3125  19.    ]]]
        >>> from dap.responses import dds, ascii
        >>> print ''.join(dds.build(g2))
        Grid {
            Array:
                Float64 g[time = 2][lat = 2][lon = 2];
            Maps:
                Float64 lat[lat = 2];
                Float64 lon[lon = 2];
                Float64 time[time = 2];
        } g;
        <BLANKLINE>
        >>> print ''.join(ascii.build(g2))
        g[2][2][2]
        [0][0], 1.3625, 2.05
        [0][1], 6.3125, 7
        [1][0], 13.3625, 14.05
        [1][1], 18.3125, 19
        <BLANKLINE>
        lat[2]
        1, 2
        <BLANKLINE>
        lon[2]
        15, 30
        <BLANKLINE>
        time[2]
        105, 110
        <BLANKLINE>
        <BLANKLINE>
    """
    dims = [grid.maps[dim] for dim in grid.dimensions]
    b = regrid_array(grid.data, dims, ndims)

    # Create new grid.
    out = copy.deepcopy(grid)
    for dim, data in zip(out.maps.values(), ndims):
        dim.data = data[:]
        dim.shape = data.shape
    out.data = arrayterator(b)
    out.shape = b.shape
    return out
    

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
