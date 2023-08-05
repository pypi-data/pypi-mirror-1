#  Copyright (C) 2007 Maxim Fedorovsky, University of Fribourg (Switzerland).
#       email : Maxim.Fedorovsky@unifr.ch, mutable@yandex.ru
#
#  This file is part of PyVib2.
#
#  PyVib2 is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  PyVib2 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PyVib2; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""Superimpose molecules using a quaternion fit.

This is a Python port of the QTRFIT algorithm written by David J. Heisterberg.
Copyright: Ohio Supercomputer Center, David J. Heisterberg, 1990.
See http://www.ccl.net/cca/software/SOURCES/C/quaternion-mol-fit/quatfit.c.

There is, however, a subtle difference between this implementation and the
original one. It lies in a way how the center of a molecule is calculated. We
use the plain weighting coefficients rather than square roots from them. This
corresponds to physically meaningful results.

The module exports the only function :
    fit() --  perform a quaternion fit

"""
__author__ = 'Maxim Fedorovsky'

from math     import sqrt
from numpy import ndarray, zeros, transpose, dot
from numpy.linalg import eigh

from pyviblib.calc.common     import contract, quat2matrix
from pyviblib.util.exceptions import InvalidArgumentError

__all__ = ['fit']


def center(n, x, w, io, o) :
  """Center or translate a molecule.

  Positional arguments :
  n  -- number of atoms
  x  -- on input  - original xyz coordinates of a molecule
        on output - moved xyz coordinates (see io for modes).
  w  -- if io=1, weights of atoms
        if io=2 or 3, unused
  io -- 1 weighted geometric center of the molecule will be at (0,0,0)
        2 molecule will be moved by a vector -o (i.e., components of a vector o
          will be subtracted from atom coordinates). 
        3 molecule will be moved by a vector +o (i.e., components of a vector o
          will be added atom coordinates). 

  o  -- if io=1, output, center of original coordinates
        if io=2, input, vector o will be subtracted from atomic coordinates
        if io=3, input, vector o will be added to atomic coordinates
        
  """
  if 2 == io :
    modif = -1.
  elif 3 == io :
    modif =  1.
  else :
    modif = -1.
    o[1] = 0.
    o[2] = 0.
    o[3] = 0.

    wnorm = 0.
    for i in xrange(1, 1 + n) :
      o[1]  += x[1, i] * w[i]
      o[2]  += x[2, i] * w[i]
      o[3]  += x[3, i] * w[i]

      wnorm += w[i]

    if 0. != wnorm :
      o /= wnorm

  for i in xrange(1, 1 + n) :
    x[1, i] += modif * o[1]
    x[2, i] += modif * o[2]
    x[3, i] += modif * o[3]

def qtrfit (n, x, y, w) :
  """Find the quaternion, q,[and left rotation matrix, u] that minimizes

    |qTXq - Y| ^ 2  [|uX - Y| ^ 2]

  This is equivalent to maximizing Re (qTXTqY).

  This is equivalent to finding the largest eigenvalue and corresponding
  eigenvector of the matrix

  [A2   AUx  AUy  AUz ]
  [AUx  Ux2  UxUy UzUx]
  [AUy  UxUy Uy2  UyUz]
  [AUz  UzUx UyUz Uz2 ]

  where

    A2   = Xx Yx + Xy Yy + Xz Yz
    Ux2  = Xx Yx - Xy Yy - Xz Yz
    Uy2  = Xy Yy - Xz Yz - Xx Yx
    Uz2  = Xz Yz - Xx Yx - Xy Yy
    AUx  = Xz Yy - Xy Yz
    AUy  = Xx Yz - Xz Yx
    AUz  = Xy Yx - Xx Yy
    UxUy = Xx Yy + Xy Yx
    UyUz = Xy Yz + Xz Yy
    UzUx = Xz Yx + Xx Yz

  The left rotation matrix, u, is obtained from q by

    u = qT1q

  Positional arguments :
    n      -- number of points
    x      -- fitted molecule coordinates
    y      -- reference molecule coordinates
    w      -- weights

  Return the best-fit quaternion.
  
  """
  xxyx = 0.
  xxyy = 0.
  xxyz = 0.
  xyyx = 0.
  xyyy = 0.
  xyyz = 0.
  xzyx = 0.
  xzyy = 0.
  xzyz = 0.

  # matrix to be diagonalized
  c = zeros( (4, 4), 'd')
  
  for i in xrange(1, 1 + n) :
    xxyx += x[1, i] * y[1, i] * w[i]
    xxyy += x[1, i] * y[2, i] * w[i]
    xxyz += x[1, i] * y[3, i] * w[i]
    xyyx += x[2, i] * y[1, i] * w[i]
    xyyy += x[2, i] * y[2, i] * w[i]
    xyyz += x[2, i] * y[3, i] * w[i]
    xzyx += x[3, i] * y[1, i] * w[i]
    xzyy += x[3, i] * y[2, i] * w[i]
    xzyz += x[3, i] * y[3, i] * w[i]

  c[0, 0] = xxyx + xyyy + xzyz

  c[1, 0] = xzyy - xyyz
  c[1, 1] = xxyx - xyyy - xzyz

  c[2, 0] = xxyz - xzyx
  c[2, 1] = xxyy + xyyx
  c[2, 2] = xyyy - xzyz - xxyx

  c[3, 0] = xyyx - xxyy
  c[3, 1] = xzyx + xxyz
  c[3, 2] = xyyz + xzyy
  c[3, 3] = xzyz - xxyx - xyyy
 
  eigen = eigh(c)

  return eigen[1][:, 3]

def fit(pairs, coords_ref, coords_fit, weight) :
  """Perform a quaternion fit.

  Positional arguments :
  pairs       --  atom pairs to be superimposed (null-based ndarray)
                  shape : (npairs, 2) with npairs being the number of atom pairs
                  atom numbers are one-based
                  example : array([ [1, 1], [5, 5], [7, 7] ])
  coords_ref  --  coordinates of the reference frame (one-based ndarray)
                  shape : (Natoms_ref, 4) with Natoms_ref being the number
                  of atoms in the reference frame
  coords_fit  --  coordinates of the fitted frame (one-based ndarray)
                  shape : (Natoms_fit, 4) with Natoms_fit being the number
                  of atoms in the fitted frame
  weight      --  weights for the atoms to be superimposed (one-based ndarray)
  
  Return value is a dictionary with the following keys :
  rms         : root mean square (RMS) deviation 
  q           : quaternion (null-based ndarray of the length 4)
  U           : left rotation matrix (one-based two-dimensional ndarray)
  ref_center  : center of the reference molecule (one-based ndarray)
  fit_center  : center of the fitted molecule (one-based ndarray)
  
  """
  for ar_ in (pairs, coords_ref, coords_fit, weight) :
    if not isinstance(ar_, ndarray) :
      raise InvalidArgumentError('All input arguments must be ndarrays')

  if 2 != len(pairs.shape) or 1 != len(weight.shape) or \
     pairs.shape[0] != weight.shape[0] - 1 :
    raise InvalidArgumentError(
        'The shapes of pairs and weight are incompatible')

  # go
  #nat_r  = coords_ref.shape[0] - 1
  nat_f  = coords_fit.shape[0] - 1
  npairs = pairs.shape[0]

  # all atoms
  #xyz_r = transpose(coords_ref).copy()
  xyz_f = transpose(coords_fit).copy()

  # atoms to be fitted
  atoms_ref = [0] + pairs[:, 0].tolist()
  atoms_fit = [0] + pairs[:, 1].tolist()

  ref_xyz = transpose(coords_ref[atoms_ref]).copy()
  fit_xyz = transpose(coords_fit[atoms_fit]).copy()
 
  # allocating memory for the centers of mass
  ref_center = zeros(4 , 'd')
  fit_center = zeros(4 , 'd')

  # center ref molecule fitted atoms around (0,0,0)
  center (npairs, ref_xyz, weight, 1, ref_center)

  # center fitted molecule fitted atoms around (0,0,0)
  center (npairs, fit_xyz, weight, 1, fit_center)

  # fit specified atoms of fit_molecule to those of ref_molecule
  quat = qtrfit(npairs, fit_xyz, ref_xyz, weight)

  # transform the quaternion to a rotation matrix
  rotmat = quat2matrix(quat)

  # subtract coordinates of the center of fitted atoms of the fitted molecule
  # from all atom coordinates of the fitted molecule (note that weight is
  # a dummy parameter)
  center(nat_f, xyz_f, weight, 2, fit_center)

  # rotate the fitted molecule by the rotation matrix u
  xyz_f   = dot(rotmat, xyz_f)
  
  # same with set of fitted atoms of the fitted molecule
  fit_xyz = dot(rotmat, fit_xyz)

  # translate atoms of the fitted molecule to the center
  #    of fitted atoms of the reference molecule
  center(nat_f, xyz_f, weight, 3, ref_center)

  # same with set of fitted atoms of the fitted molecule
  center(npairs, fit_xyz, weight, 3, ref_center)

  # translate fitted atoms of reference molecule to their orig. location
  center(npairs, ref_xyz, weight, 3, ref_center)
  
  # finally calculating the rms value
  rms   = 0.
  for i in xrange(1, 1 + npairs) :
    delta = ref_xyz[1:, i] - fit_xyz[1:, i]
    rms   += weight[i] * contract(delta, delta)

  rms = sqrt(rms/weight[1:].sum())

  # packing results
  ans = {}

  ans['pairs']      = pairs
  ans['weight']     = weight  
  ans['rms']        = rms
  ans['q']          = quat
  ans['U']          = rotmat
  ans['ref_center'] = ref_center
  ans['fit_center'] = fit_center
  ans['xyz_f']      = transpose(xyz_f)

  return ans
