"""Spline regridding."""

__author__ = 'Roberto De Almeida <rob@pydap.org>'

import copy

import numarray
from numarray.nd_image import map_coordinates
from Scientific.Functions.Interpolation import InterpolatingFunction


def regrid_array(a, lat, lon, nlat, nlon):
    """Spline interpolation into a new grid.

        >>> from numarray import *
        >>> a = arange(12, shape=(4,3), type = Float64)
        >>> lat = array([10.0, 20.0, 30.0, 40.0])
        >>> lon = array([100.0, 110.0, 120.0])
        >>> nlat = array([15.0, 30.0])
        >>> nlon = array([105.0, 110.0])
        >>> print regrid_array(a, lat, lon, nlat, nlon)
        [[ 1.3625  2.05  ]
         [ 6.3125  7.    ]]
    """
    # Linearly interpolate axes.
    interp_lat = InterpolatingFunction([lat], numarray.arange(len(lat)), None)
    interp_lon = InterpolatingFunction([lon], numarray.arange(len(lon)), None)
    ii = [interp_lon(i) for i in nlon]
    jj = [interp_lat(j) for j in nlat]
    coordinates = zip(*[[j, i] for j in jj for i in ii])

    # Spline interpolation of data.
    b = map_coordinates(a, coordinates, output_type=None, output=None, order=3, mode='constant', cval=0.0, prefilter=True)
    b.shape = (len(nlat), len(nlon))
    return b

def regrid(grid, nlat, nlon):
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
        >>> g2 = regrid(g, nlat, nlon)
        >>> print g2.data
        [[[  1.3625   2.05  ]
          [  6.3125   7.    ]]
        <BLANKLINE>
         [[ 13.3625  14.05  ]
          [ 18.3125  19.    ]]]
    """
    # We assume dimensions are [dim1, dim2, ... dimn,] lat, lon.
    latname = grid.dimensions[-2]
    lonname = grid.dimensions[-1]

    # Get data.
    lat = grid.maps[latname][:]
    lon = grid.maps[lonname][:]
    slice_ = [slice(None, None, None) for _ in grid.dimensions]
    slice_ = tuple(slice_)
    a = grid[slice_]

    # Reshape a.
    oldshape = a.shape
    a.shape = (-1, a.shape[-2], a.shape[-1])
    
    b = numarray.zeros((a.shape[0], nlat.shape[0], nlon.shape[0]), a.typecode())
    for i in range(a.shape[0]):
        b[i,:,:] = regrid_array(a[i,:,:], lat, lon, nlat, nlon)
    b.shape = oldshape[:-2] + (nlat.shape[0], nlon.shape[0])

    # Create new grid.
    out = copy.deepcopy(grid)
    out.maps[latname].data = lat[:]
    out.maps[lonname].data = lon[:]
    out.data = b
    out.shape = b.shape
    return out
    

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
