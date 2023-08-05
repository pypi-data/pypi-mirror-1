"""EOF-based interpolation for missing values.

Based on  J. M. Beckers and M. Rixen, 2003. EOF Calculations and Data
Filling from Incomplete Oceanographic Datasets.
"""

__author__ = 'Roberto De Almeida <rob@pydap.org>'

from __future__ import division

import random

import numarray
from numarray import ma, mlab


def reconstruct(u, d, v, neofs=None):
    """Reconstruct a matrix from the SVD.

        >>> A = numarray.array([[2.0, 4.0, -6.0, 8.0], [1.0, 2.0, -3.0, 4.0]])
        >>> u, d, v = mlab.svd(A)
        >>> print reconstruct(u, d, v)
        [[ 2.  4. -6.  8.]
         [ 1.  2. -3.  4.]]
    """
    if neofs is None: neofs = u.shape[0]

    Xa = 0
    for k in range(neofs):
        u2 = u[:,k].copy()
        v2 = numarray.transpose(v[k,:]).copy()
        u2.shape = (-1,1)
        v2.shape = (1,-1)
        uv = numarray.matrixmultiply(u2, v2)
        Xa = Xa + (d[k] * uv)

    return Xa


def RMS(A, B):
    assert A.shape == B.shape
    sum = numarray.sum((A.flat - B.flat)**2)
    n = len(A.flat)
    rms = numarray.sqrt(sum/n)
    
    return rms


def eofinterp(A, maxeofs=20, precision=1e-3):
    """Interpolate using EOFs.
    
        >>> A = ma.masked_values([[2.0, 1.e20, -6.0, 8.0], [1.0, 2.0, -3.0, 4.0], [4.0, 8.0, -12.0, 16.0]], 1.e20)
        >>> print A.mask()
        [[0 1 0 0]
         [0 0 0 0]
         [0 0 0 0]]
        >>> print eofinterp(A)
    """
    # Reshape data to 2D.
    A.shape = (A.shape[0], -1)
    holes = A.mask()
    
    # Fill with zeros (initial guess).
    Xo = A.filled(0.0)

    # Limits EOFs to available number.
    maxeofs = min(maxeofs, A.shape[0])

    # Cross-validation. Select 30 random points where we have data.
    points = numarray.zeros(A.shape, numarray.Bool)
    n = min(30, A.flat.shape[0]//10)
    while numarray.sum(points.flat) < n:
        i,j = random.randint(0, Xo.shape[0]-1), random.randint(0, Xo.shape[1]-1)
        if not A.mask()[i,j]:
            points[i,j] = 1

    # Fill removed points with zeros.
    Xo[points] = 0.0 

    rmss = []
    for neofs in range(maxeofs):
        # Converge to solution.
        drms = 1.e30
        rms_ = 1.e30
        it = 0
        while drms > precision:
            # Reconstruct time series with neofs+1 truncated EOFs.
            u, d, v = mlab.svd(Xo)
            Xa = reconstruct(u, d, v, neofs+1)

            # Calculate RMS.
            rms = RMS(Xa[holes], Xo[holes]) 
            drms = rms_ - rms
            rms_ = rms
            
            # Fill A with analysed data.
            Xo = A.filled(Xa)

            # Fill removed points.
            Xo[points] = Xa[points]

            it += 1

        print '%d iterations for convergence...' % it

        # Calculate RMS.
        rms = RMS(Xo[points], A[points])
        rmss.append(rms)

    # Optimal number of EOFs.
    neofs = rmss.index(min(rmss)) + 1
    print 'Using %d EOFs to reconstruct time series...' % neofs

    Xo = A.filled(0.0)

    # Converge to solution.
    drms = 1.e30
    rms_ = 1.e30
    it = 0
    while drms > precision:
        # Reconstruct time series with neofs+1 truncated EOFs.
        u, d, v = mlab.svd(Xo)
        Xa = reconstruct(u, d, v, neofs)

        # Calculate RMS.
        rms = RMS(Xa[holes], Xo[holes])
        drms = rms_ - rms
        rms_ = rms

        # Fill A with analysed data.
        Xo = A.filled(Xa)

        # Fill removed points.
        Xo[points] = Xa[points]

        it += 1    
    
    Xa = reconstruct(u, d, v, neofs)

    return Xa


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
