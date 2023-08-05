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

"""Commonly used routines.

The following functions are exported :
    normalize_set()       --  normalize a set of vectors
    orthogonalize_set()   --  orthogonalize a set of vectors
    contract()            --  double contraction of two arrays
    contract_t()          --  double contraction of a tensor
    rotate_t()            --  rotate the dinuclear terms of a tensor
    norm()                --  norm of an array
    cosine()              --  cosine between two arrays
    mass_center()         --  center of gravity
    inertia_tensor()      --  inertia tensor
    rotmatrix_axis()      --  matrix for rotation about an arbitrary axis
    quat2matrix()         --  left rotation matrix from a normalized quaternion
    calc_dcm()            --  direction cosine matrix
    levi_civita()         --  antisymmetric unit tensor of Levi-Civita
    is_even_permutation() --  determine whether a permutation is even
    kronecker()           --  kronecker symbol
    decompose()           --  decompose a 3x3 matrix into parts
    decompose_t()         --  decompose the dinuclear terms of a tensor
    crossproduct()        --  cross product of two vectors
    spatproduct()         --  scalar triple product of three vectors
    angle_vectors()       --  angle between vectors
    distance()            --  distance between two points
    angle()               --  angle between three points
    dihedral()            --  dihedral angle between four points
    make_gcm()            --  generate a group coupling matrix (GCM)
    make_gcp()            --  generate group contribution patterns (GCPs)
    boltzmann_distr()     --  Boltzmann energy distribution of molecules
    signum()              --  signum
    fitgauss_params()     --  fitting a Lorentz function with Gaussian functions
    voigt_norm()          --  normalized approximate Voigt profile
    boltzmann_factor()    --  Boltzmann correction
    savitzky_golay()      --  smooth data with the Savitzky-Golay algorithm
    
"""
__author__ = 'Maxim Fedorovsky'

from math  import sqrt, pi, cos, sin, acos, exp
from numpy import ndarray, zeros, array, identity, dot, reshape, trace, \
                  transpose, exp as numpy_exp, mat, concatenate
from numpy.linalg import det, pinv

from pyviblib.util.constants  import HARTREE2KJMOL, R, H, C, KB, T_KELVIN
from pyviblib.util.exceptions import InvalidArgumentError

__all__ = ['normalize_set', 'orthogonalize_set',
           'contract', 'contract_t', 'rotate_t',
           'norm', 'cosine', 'mass_center', 'inertia_tensor',
           'rotmatrix_axis', 'quat2matrix', 'calc_dcm',
           'levi_civita', 'is_even_permutation', 'kronecker',
           'decompose', 'decompose_t', 'crossproduct', 'spatproduct',
           'angle_vectors', 'distance', 'angle', 'dihedral',
           'make_gcm', 'make_gcp', 'boltzmann_distr', 'signum',
           'fitgauss_params', 'voigt_norm', 'boltzmann_factor',
           'savitzky_golay']


def normalize_set(set_in, set_out=None, base=1) :
  """Normalize a set of vectors.

  Positional arguments :
  set_in  -- vectors to be normalized (threes-dimensional ndarray)
             their base is given by the keyword argument of the same name

  Keyword arguments :
  set_out -- where the result is to be placed (default None)
             unless given, use set_in
             the caller is responsible for memory allocation
  base    -- base index (default 1)

  """
  if not isinstance(set_in, ndarray) or 2 > len(set_in.shape) :
    raise InvalidArgumentError('Invalid set_in argument')

  for i in xrange(base, set_in.shape[0]) :
    norm_ = sqrt(contract(set_in[i], set_in[i]))

    if norm_ :
      if set_out is not None :
        set_out[i] = set_in[i] / norm_
      else :
        set_in[i]  /= norm_

def orthogonalize_set(set_in, make_orthonormal=True, set_out=None, base=1) :
  """Orthogonalize a set of vectors using the Gram-Schmidt algorithm.

  Positional arguments :
  set_in  -- vectors to be orthogonalized (threes-dimensional ndarray)
             their base is given by the keyword argument of the same name

  Keyword arguments :
  set_out           -- where the result is to be placed (default None)
                       unless given, use set_in
                       the caller is responsible for memory allocation
  make_orthonormal  -- whether the result set is to be normalized        
  base              -- base index (default 1)

  """
  if not isinstance(set_in, ndarray) or 2 > len(set_in.shape) :
    raise InvalidArgumentError('Invalid set_in argument')
  
  set_u = zeros(set_in.shape    , 'd')
  sum_  = zeros(set_in.shape[1:], 'd')

  # u1 = v1
  set_u[base] = set_in[base].copy()

  for i in xrange(1 + base, set_in.shape[0]) :
    sum_ *= 0.
    
    for j in xrange(base, i) :
      ujvi = contract(set_u[j], set_in[i])
      ujuj = contract(set_u[j], set_u[j])

      if 0. != ujuj :
        sum_ += (ujvi / ujuj) * set_u[j]

    set_u[i] = set_in[i] - sum_

  # orthonormalize if necessary
  if make_orthonormal :
    normalize_set(set_u, set_out=None, base=base)

  # finally copy results
  if set_out is None :
    set_in[base:]  = set_u[base:]
  else :
    set_out[base:] = set_u[base:]

def contract(ar1, ar2) :
  """Double contract two arrays and return the result as a scalar.

  The arrays can be e.g. vectors, matrices, tensors, provided that they are of
  the same dimension.

  Positional argument :
  ar1 -- first array (ndarray)
  ar2 -- first array (ndarray)

  """
  if not isinstance(ar1, ndarray) or \
     not isinstance(ar2, ndarray) or ar1.shape != ar2.shape :
    raise InvalidArgumentError('Invalid tensor(s) supplied')

  nelements = ar1.size

  # reshaping to an one-dimensional array for an easy access to elements
  return dot(reshape(ar1, nelements), reshape(ar2, nelements))

def contract_t(tens) :
  """Double contract a second-rank tensor with itself and decompose the result.

  The function calls the contract() function for each dinuclear term of the
  tensor. The latter can be e.g. a hessian or a V-tensor.

  Positional arguments :
  tens -- second-rank tensor to be double contracted (one-based ndarray)
          shape : (1 + N, 4, 1 + N, 4) with N being the number of atoms
       
  Return a tuple with the total, isotropic, anisotropic and antisymmetric parts
  of the double contracted tensor. Their shape : (1 + N, 1 + N).
  
  """
  if not isinstance(tens, ndarray) or 4 != len(tens.shape) or \
     tens.shape[0] != tens.shape[2] or tens.shape[1] != tens.shape[3] or \
     4 != tens.shape[1] :
    raise InvalidArgumentError('Invalid tensor supplied')

  tens_dec_t    = zeros((tens.shape[0], tens.shape[0]), 'd')
  tens_dec_is   = zeros(tens_dec_t.shape, 'd')
  tens_dec_anis = zeros(tens_dec_t.shape, 'd')
  tens_dec_a    = zeros(tens_dec_t.shape, 'd')

  for i in xrange(1, tens.shape[0]) :
    for j in xrange(1, tens.shape[0]) :
      tens_ij_dec = decompose(tens[i, :, j, :])

      tens_dec_is[i, j]   = contract(tens_ij_dec[0], tens_ij_dec[0])
      tens_dec_anis[i, j] = contract(tens_ij_dec[1], tens_ij_dec[1])
      tens_dec_a[i, j]    = contract(tens_ij_dec[2], tens_ij_dec[2])

      tens_dec_t[i, j]    = tens_dec_is[i, j] + tens_dec_anis[i, j] + \
                            tens_dec_a[i, j]

  return tens_dec_t, tens_dec_is, tens_dec_anis, tens_dec_a

def rotate_t(tens, rotm) :
  """Rotate the dinuclear terms of a tensor.

  Positional arguments :
  tens -- second-rank tensor to be rotated (one-based ndarray)
          shape : (1 + N, 4, 1 + N, 4) with N being the number of atoms
  rotm -- left rotation matrix (one-based ndarray)
          shape : (4, 4)
  
  """
  if not isinstance(tens, ndarray) or 4 != len(tens.shape) or \
     tens.shape[0] != tens.shape[2] or 4 != tens.shape[1] or \
     4 != tens.shape[3] :
    raise InvalidArgumentError('Invalid tensor')

  if not isinstance(rotm, ndarray) or (4, 4) != rotm.shape :
    raise InvalidArgumentError('Invalid rotation matrix')
  
  tens_rot = zeros(tens.shape, 'd')

  # rotate each dinuclear term Tab
  for i in range(1, tens.shape[0]) :
    for j in range(1, tens.shape[0]) :
      tens_rot[i, :, j, :] = dot(dot(transpose(rotm), tens[i, :, j, :]), rotm)

  return tens_rot

def norm(ar_) :
  """Calculate the norm of an array.

  The norm is considered to be the square root of the double contraction of the
  array with itself. The array can be multi-dimensional such as e.g. tensors.

  Positional arguments :
  ar_ -- array (ndarray)
  
  """
  return sqrt(contract(ar_, ar_))

def cosine(tens1, tens2) :
  """Calculate the cosinus between two arrays.

  Teh cosine is considered to be the result of the double contraction of the
  arrays divided by the product of their norms.

  Positional arguments :
  tens1 -- first array (ndarray)
  tens2 -- second array (ndarray)
  
  """
  if tens1 is None or tens2 is None :
    raise InvalidArgumentError('Invalid T1 and/or T2 arguments')
  
  t1t1 = contract(tens1, tens1)
  t1t2 = contract(tens1, tens2)
  t2t2 = contract(tens2, tens2)

  if 0. != t1t1 * t2t2 :
    return t1t2 / sqrt(t1t1 * t2t2)
  else :
    return 0.

def mass_center(coords, masses, atom_list=None) :
  """Calculate the center of gravity.

  Positional arguments :
  coords    -- coordinates (one-based ndarray)
               shape : (1 + N, 4) with N being the number of atoms
  masses    -- masses (one-based ndarray)
               shape : (1 + N,)

  Keyword arguments :
  atom_list -- list of atoms involved (list, default None)
               if None, use all the atoms

  """
  if not isinstance(coords, ndarray) or not isinstance(masses, ndarray) :
    raise InvalidArgumentError('Invalid coordinates or masses')

  if 2 != len(coords.shape) or 1 != len(masses.shape) or \
     coords.shape[0] != masses.shape[0] :
    raise InvalidArgumentError('Incompatible shapes of coords and masses')

  if atom_list is None :
    atom_list = [ (1 + i) for i in xrange(coords.shape[0]-1) ]
    atom_list = array(atom_list)

  # finally  
  mass_c = zeros(4, 'd')
  
  for i in atom_list :
    mass_c[1:] += coords[i, 1:] * masses[i]

  return mass_c / masses[atom_list.tolist()].sum()

def inertia_tensor(coords, masses, atom_list=None, move2mass_center=True) :
  """Calculate the inertia tensor.

  Positional arguments :
  coords           -- coordinates (one-based ndarray)
                      shape : (1 + N, 4) with N being the number of atoms
  masses           -- masses (one-based ndarray)
                      shape : (1 + N,)

  Keyword arguments :
  atom_list        -- list of atoms involved (list, default None)
                      if None, use all the atoms
               
  move2mass_center -- whether to move to the center of gravity of the atoms
                      (default True)

  Return the inertia tensor as a null-based two-dimensional ndarray.
  
  """
  if not isinstance(coords, ndarray) or not isinstance(masses, ndarray) :
    raise InvalidArgumentError('Invalid coordinates or masses')

  if 2 != len(coords.shape) or 1 != len(masses.shape) or \
     coords.shape[0] != masses.shape[0] :
    raise InvalidArgumentError('Incompatible shapes of coords and masses')

  if atom_list is None :
    atom_list = [ (1 + i) for i in xrange(coords.shape[0]-1) ]
    atom_list = array(atom_list)

  if move2mass_center :
    mass_c = mass_center(coords, masses, atom_list=atom_list)
    
    coords_m = zeros( coords.shape, 'd' )
    coords_m[1:, 1:] = coords[1:, 1:] - mass_c[1:]

    coords = coords_m

  itensor = zeros((3, 3), 'd')

  for i in atom_list :
    itensor[0, 0] += masses[i] * (coords[i, 2] * coords[i, 2] + \
                                  coords[i, 3] * coords[i, 3])
    itensor[0, 1] -= masses[i] *  coords[i, 1] * coords[i, 2]
    itensor[0, 2] -= masses[i] *  coords[i, 1] * coords[i, 3]
    itensor[1, 1] += masses[i] * (coords[i, 1] * coords[i, 1] + \
                                  coords[i, 3] * coords[i, 3])
    itensor[1, 2] -= masses[i] *  coords[i, 2] * coords[i, 3]
    itensor[2, 2] += masses[i] * (coords[i, 1] * coords[i, 1] + \
                                  coords[i, 2] * coords[i, 2])

  itensor[1, 0] = itensor[0, 1]
  itensor[2, 0] = itensor[0, 2]
  itensor[2, 1] = itensor[1, 2]

  return itensor

def rotmatrix_axis(axis, phi) :
  """Generate a matrix of rotation about an arbitrary axis.

  Positional arguments :
  axis -- axis about which the rotation is being done (null-based ndarray)
  phi  -- angle in grad

  The result rotation matrix is an one-based two-dimensional ndarray.
  
  """
  # frame of reference
  axes = identity(3, 'd')

  # result rotation matrix
  rotm = zeros((4, 4), 'd')
  
  phi *= pi / 180.
  
  cos0 = cosine(axes[0], axis)
  cos1 = cosine(axes[1], axis)
  cos2 = cosine(axes[2], axis)

  rotm[1, 1] = cos0 * cos0 + ( 1 - cos0 * cos0 ) * cos(phi)
  rotm[1, 2] = cos0 * cos1 * ( 1 - cos(phi) ) + cos2 * sin(phi)
  rotm[1, 3] = cos0 * cos2 * ( 1 - cos(phi) ) - cos1 * sin(phi)
  rotm[2, 1] = cos0 * cos1 * ( 1 - cos(phi) ) - cos2 * sin(phi)
  rotm[2, 2] = cos1 * cos1 + ( 1 - cos1 * cos1 ) * cos(phi)
  rotm[2, 3] = cos1 * cos2 * ( 1 - cos(phi) ) + cos0 * sin(phi)
  rotm[3, 1] = cos0 * cos2 * ( 1 - cos(phi) ) + cos1 * sin(phi)
  rotm[3, 2] = cos1 * cos2 * ( 1 - cos(phi) ) - cos0 * sin(phi)
  rotm[3, 3] = cos2 * cos2 + ( 1 - cos2 * cos2 ) * cos(phi)

  return rotm

def quat2matrix(quat) :
  """Generate a left rotation matrix from a normalized quaternion.

  Positional arguments :
  quat -- normalized quaternion (null-based array of the length 4)

  The result matrix is an one-based two-dimensional ndarray.
  
  """
  rotm = zeros((4, 4), 'd')
  
  rotm[1, 1] = quat[0] * quat[0] + quat[1] * quat[1] - quat[2] * quat[2] - \
               quat[3] * quat[3]
  rotm[2, 1] = 2.   * (quat[1] * quat[2] - quat[0] * quat[3])
  rotm[3, 1] = 2.   * (quat[1] * quat[3] + quat[0] * quat[2])

  rotm[1, 2] = 2.   * (quat[2] * quat[1] + quat[0] * quat[3])
  rotm[2, 2] = quat[0] *  quat[0] - quat[1] * quat[1] + quat[2] * quat[2] - \
               quat[3] * quat[3]
  rotm[3, 2] = 2.   * (quat[2] * quat[3] - quat[0] * quat[1])

  rotm[1, 3] = 2.   * (quat[3] * quat[1] - quat[0] * quat[2])
  rotm[2, 3] = 2.   * (quat[3] * quat[2] + quat[0] * quat[1])
  rotm[3, 3] = quat[0] *  quat[0] - quat[1] * quat[1] - quat[2] * quat[2] + \
               quat[3] * quat[3]

  return rotm

def calc_dcm(frame_ref1, frame_ref2) :
  """Calculate the direction cosine matrix between two coordinates systems.

  Positional arguments :
  frame_ref1 -- first frame of reference (null-based ndarray)
                shape : (3, 3)
  frame_ref2 -- second frame of reference (null-based ndarray)
                shape : (3, 3)

  The result matrix is an one-based two-dimensional ndarray.
  
  """
  if not isinstance(frame_ref1, ndarray) or \
     not isinstance(frame_ref2, ndarray) :
    raise InvalidArgumentError('Invalid frames of reference')

  shape = (3, 3)
  if shape != frame_ref1.shape or shape != frame_ref2.shape :
    raise InvalidArgumentError('Invalid shapes of the frames of reference')

  rotm = zeros( (4, 4), 'd' )

  for i in xrange(3) :
    for j in xrange(3) :
      rotm[1+i, 1+j] = dot(frame_ref1[i], frame_ref2[j])

  return rotm

def align_inertia_axes(pairs, coords_ref, masses_ref, coords_fit, masses_fit) :
  """Align the inertia axes of two frames.

  UNDER CONSTRUCTION.
  
  """
  assert pairs and coords_ref and masses_ref and coords_fit and masses_fit
##  if pairs is None or coords_ref is None or coords_fit is None or \
##     masses_ref is None or masses_fit is None:
##    raise InvalidArgumentError('Invalid argument(s) supplied')
##
##  # calculating the inertia tensors
##  i_ref = inertia_tensor(coords_ref, masses_ref, pairs[:, 0], True)
##  i_fit = inertia_tensor(coords_fit, masses_fit, pairs[:, 1], True)
##
##  # diagonalizing it
##  i_data_ref = Heigenvectors(i_ref)
##  i_data_fit = Heigenvectors(i_fit)
##
##  mat = calc_dcm(i_data_ref[1], i_data_fit[1])
##
##  # like in qtrfit :
##  npairs = pairs.shape[0]
##  
##  atoms_ref = [0] + pairs[:, 0].tolist()
##  atoms_fit = [0] + pairs[:, 1].tolist()
##  
##  ref_xyz = transpose(coords_ref[atoms_ref]).copy()
##  fit_xyz = transpose(coords_fit[atoms_fit]).copy()
##  weight  = masses_ref[ atoms_ref ]
##
##  #
##  m_ref = mass_center(coords_ref, masses_ref, pairs[:, 0])
##  m_fit = mass_center(coords_fit, masses_fit, pairs[:, 1])
##
##  #from pyviblib.calc.qtrfit import center
##  
##  #center(npairs, fit_xyz, None, 2, m_fit)
##  
##  fit_xyz = dot(mat, fit_xyz)
##  
##  #center(npairs, fit_xyz, None, 3, m_ref)
##
##  # 3) calculating rms
##  rms = 0.
##  for i in xrange(1, 1 + npairs) :
##    delta  = ref_xyz[1:, i] - fit_xyz[1:, i]
##    rms   += weight[i] * contract( delta, delta )
##
##  rms = sqrt( rms / weight[1:].sum() )
##
##  # packing results
##  ans = {}
##
##  ans['U']    = mat
##  #ans['rms']  = rms
##
##  return ans

def levi_civita():
  """Return the antisymmetric unit tensor of Levi-Civita.
               
              /-
              |  +1 if (i,j,k) is an even permutation of (1,2,3)
  eps(i,j,k) =|  -1 if (i,j,k) is an odd  permutation of (1,2,3)
              |   0 if at lease two indices are equal
              \-

  The result tensor is an one-based two-dimensional ndarray.
  
  """
  eps = zeros((4, 4, 4), 'l')

  for i in xrange(1, 4) :
    for j in xrange(1, 4) :
      for k in xrange(1, 4) :
        if i != j and i != k and j != k:
          if is_even_permutation((i, j, k)):
            eps[i, j, k] =  1
          else:
            eps[i, j, k] = -1
        else:
          eps[i, j, k] =  0

  return eps

def is_even_permutation(perm):
  """Determine whether a permutation is even.

  An even permutation is a permutation that can be produced by an even number
  of exchanges.

  Positional arguments :
  perm -- permutation (tuple)

  """
  dim = len(perm)
  even = True
  for i in xrange(dim):
    for j in xrange(1 + i, dim):
      if perm[j] < perm[i]:
        even = not even

  return even

def kronecker(i, j):
  """Kronecker symbol.
  
               /- 1 if i = j
  delta(i,j) = |
               \- 0 otherwise

  Positional arguments :
  i -- first index
  j -- second index
  
  """
  if i == j :
    return 1
  else :
    return 0

def decompose(mat_) :
  """Decompose a matrix into the isotropic, anisotropic & antisymmetric parts.

  M = M_is + M_anis + M_a
  
  tr = trace(M) / 3

  M_is(i,j)   = tr * kronecker(i,j)
  M_anis(i,j) = [M(i,j) + M(j,i)] / 2 - M_is(i,j)
  M_a(i,j)    = [M(i,j) - M(j,i)] / 2

  Positional arguments :
  mat_ -- matrix to be decomposed (one-based ndarray)
          shape : (4, 4)

  Return a tuple with the isotropic, anisotropic and antisymmetric parts.
  
  """
  if not isinstance(mat_, ndarray) or 2 != len(mat_.shape) or \
     (4, 4) != mat_.shape :
    raise InvalidArgumentError(
      'The matrix must be an one-based ndarray with the shape (4, 4)')

  mat_is   = zeros(mat_.shape, 'd')
  mat_anis = zeros(mat_.shape, 'd')
  mat_a    = zeros(mat_.shape, 'd')

  # trace of the matrix devided by 3
  coeff = trace(mat_[1:, 1:]) / 3.

  for i in xrange(1, mat_.shape[0]) :
    for j in xrange(1, mat_.shape[1]) :
      mat_is[i, j]   = coeff * kronecker(i, j)
      mat_anis[i, j] = 0.5 * (mat_[i, j] + mat_[j, i]) - mat_is[i, j]
      mat_a[i, j]    = 0.5 * (mat_[i, j] - mat_[j, i])

  return mat_is, mat_anis, mat_a

def decompose_t(tens) :
  """Decompose the dinuclear terms of a tensor.

  The decompose() function is called for each dinuclear term of the tensor.

  Positional arguments :
  tens -- second-rank tensor to be decomposed (one-based ndarray)
          shape : (1 + N, 4, 1 + N, 4) with N being the number of atoms

  Return a tuple with the isotropic, anisotropic and antisymmetric parts of T.

  """
  if not isinstance(tens, ndarray) or 4 != len(tens.shape) or \
     tens.shape[0] != tens.shape[2] or 4 != tens.shape[1] or \
     4 != tens.shape[3] :
    raise InvalidArgumentError('Invalid tensor')

  tens_is   = zeros(tens.shape, 'd')
  tens_anis = zeros(tens.shape, 'd')
  tens_a    = zeros(tens.shape, 'd')

  for i in xrange(1, tens.shape[0]) :
    for j in xrange(1, tens.shape[0]) :
      tens_ij_dec = decompose(tens[i, :, j, :])
      
      tens_is[i, :, j, :]   = tens_ij_dec[0]
      tens_anis[i, :, j, :] = tens_ij_dec[1]
      tens_a[i, :, j, :]    = tens_ij_dec[2]

  return tens_is, tens_anis, tens_a

def crossproduct(ar1, ar2, base=1) :
  """Calculate the cross-product of two vectors.

  Positional arguments :
  ar1    -- first vector (ndarray)
  ar2    -- second vector (ndarray)
          their base is given by the keyword argument of the same name

  Keyword arguments :
  base -- base index (default 1)

  """
  for ar_ in (ar1, ar2) :
    if ar_ is None or 3 + base != len(ar_) :
      raise InvalidArgumentError('Invalid parameter passed')

  q1_ = ar1[base+1] * ar2[base+2] - ar1[base+2] * ar2[base+1]
  q2_ = ar1[base+2] * ar2[base+0] - ar1[base+0] * ar2[base+2]
  q3_ = ar1[base+0] * ar2[base+1] - ar1[base+1] * ar2[base+0]

  ans = zeros(base + 3, 'd')
  ans[base:] = (q1_, q2_, q3_)
  
  return ans

def spatproduct(ar1, ar2, ar3, base=1) :
  """Calculate the scalar triple product of three vectors.

  Positional arguments :
  ar1    -- first vector (ndarray)
  ar2    -- second vector (ndarray)
  ar3    -- third vector (ndarray)
          their base is given by the keyword argument of the same name

  Keyword arguments :
  base -- base index (default 1)

  """
  for ar_ in (ar1, ar2, ar3) :
    if ar_ is None or 3 + base != len(ar_) :
      raise InvalidArgumentError('Invalid parameter passed')

  mat_ = zeros((3, 3), 'd')
  mat_[0] = ar1[base:]
  mat_[1] = ar2[base:]
  mat_[2] = ar3[base:]

  return det(mat_)

def angle_vectors(ar1, ar2, base=1) :
  """Calculate the angle between two vectors.

  Positional arguments :
  ar1    -- first vector (ndarray)
  br2    -- second vector (ndarray)
            their base is given by the keyword argument of the same name

  Keyword arguments :
  base -- base index (default 1)

  Return the angle in grad.
  
  """
  for ar_ in (ar1, ar2) :
    if ar_ is None or 3 + base != len(ar_) :
      raise InvalidArgumentError('Invalid parameter passed')

  ar1 = array(ar1[base:], 'd')
  ar2 = array(ar2[base:], 'd')
    
  scalar_prod = dot(ar1, ar2)
  
  if 0. == scalar_prod :
    return 90./pi

  arg_ = scalar_prod / sqrt(dot(ar1, ar1) * dot(ar2, ar2))

  # sometimes acos behaves strange...
  if 1. < arg_ :
    arg_ = 1.
  elif -1. > arg_ :
    arg_ = -1

  return 180./pi * acos(arg_)

def distance(ar1, ar2, base=1) :
  """Calculate the distance between two points.

  Positional arguments :
  ar1    -- first point (ndarray)
  ar2    -- second point (ndarray)
            their base is given by the keyword argument of the same name

  Keyword arguments :
  base -- base index (default 1)
  
  """
  for ar_ in (ar1, ar2) :
    if ar_ is None or 3 + base != len(ar_) :
      raise InvalidArgumentError('Invalid parameter passed')
    
  dist = array(ar1[base:], 'd') - array(ar2[base:], 'd')

  return norm(dist)

def angle(ar1, ar2, ar3, base=1) :
  """Calculate the angle between three points.

  Positional arguments :
  ar1    -- first point (ndarray)
  ar2    -- second point (ndarray)
  ar3    -- third point (ndarray)
            their base is given by the keyword argument of the same name

  Keyword arguments :
  base -- base index (default 1)

  Return the angle in grad.
  
  """
  for ar_ in (ar1, ar2, ar3) :
    if ar_ is None or 3 + base != len(ar_) :
      raise InvalidArgumentError('Invalid parameter passed')
  
  v_ba = array(ar1, 'd') - array(ar2, 'd')
  v_bc = array(ar3, 'd') - array(ar2, 'd')

  return angle_vectors(v_ba, v_bc, base)

def dihedral(ar1, ar2, ar3, ar4, base=1) :
  """Calculate the dihedral angle between four points.

  Positional arguments :
  ar1    -- first point (ndarray)
  ar2    -- second point (ndarray)
  ar3    -- third point (ndarray)
  ar4    -- fourth point (ndarray)
            their base is given by the keyword argument of the same name

  Keyword arguments :
  base -- base index (default 1)

  Return the dihedral angle in grad.
  
  """
  for ar_ in (ar1, ar2, ar3, ar4) :
    if ar_ is None or 3 + base != len(ar_) :
      raise InvalidArgumentError('Invalid parameter passed')

  v_ba = array(ar1, 'd') - array(ar2, 'd')
  v_bc = array(ar3, 'd') - array(ar2, 'd')
  v_cb = array(ar2, 'd') - array(ar3, 'd')
  v_cd = array(ar4, 'd') - array(ar3, 'd')

  # normal to the plane (a, b, c)
  norm1 = crossproduct(v_ba, v_bc, base)

  # normal to the plane (b, c, d)
  norm2 = crossproduct(v_cb, v_cd, base)

  # scalar triple product which defines the sign of the dihedral angle
  if 0. > spatproduct(v_bc, norm1, norm2, base) :
    sign = -1.
  else :
    sign = +1.
  
  return sign * angle_vectors(norm1, norm2, base)

def make_gcm(mat, groups):
  """Generate a group coupling matrix (GCM).

  The GCM is obtained by separately adding up intra-group mono- and di-nuclear
  terms, and inter-group di-nuclear terms.

  For details refer to W. Hug. Chem. Phys., 264(1):53-69, 2001.

  Positional arguments :
  mat     --  matrix (one-based two-dimensional ndarray)
  groups  --  groups (list)
              atom indices are one-based
              example : [ [1, 2], [4, 5], [6, 3] ]

  Return the GCM. Shape : (1 + N_gr, 1 + N_gr) with N_gr being the number of
  groups.

  """
  if not isinstance(mat, ndarray) or 2 != len(mat.shape) or \
     mat.shape[0] != mat.shape[1] :
    raise InvalidArgumentError('Invalid matrix')

  if groups is None :
    raise InvalidArgumentError('Invalid groups')
  
  n_gr = len(groups)
  mat_ = zeros((1 + n_gr, 1 + n_gr), 'd')

  for gr1 in xrange(n_gr):
    for gr2 in xrange(n_gr):  
      sum_ = 0.
      
      m_1 = len(groups[gr1])
      m_2 = len(groups[gr2])

      for i in xrange(m_1):
        for j in xrange(m_2):
          sum_ += mat[groups[gr1][i], groups[gr2][j]]

      mat_[gr1 + 1][gr2 + 1] = sum_

  return mat_

def make_gcp(acp, groups) :
  """Generate group contribution patterns (GCPs).

  The GCPs are obtained by adding the contributions of atoms comprising the
  groups.

  For details refer to W. Hug. Chem. Phys., 264(1):53-69, 2001.

  Positional arguments :
  acp     --  atomic contribution patterns (one-based ndarray)
              it can be generated e.g. with pyviblib.calc.spectra.make_acp()
  groups  --  groups (list)
              atom indices are one-based
              example : [ [1, 2], [4, 5], [6, 3] ]

  Return the GCP of the length 1 + N_gr with N_gr being the number of groups.

  """
  if not isinstance(acp, ndarray) or groups is None or \
     1 != len(acp.shape) :
    raise InvalidArgumentError('Invalid input arguments')

  gcp    = zeros(1 + len(groups), 'd')
  natoms = acp.shape[0] - 1

  for i in xrange(len(groups)) :    
    for j in groups[i] :
      # check the validity
      if j > natoms :
        raise InvalidArgumentError('Group %d has invalid atom number %d' \
                                   % (1 + i, j))
      else :
        gcp[1 + i] += acp[j]

  return gcp

def boltzmann_distr(energies, energy_units=0, temperature=298.15) :
  """Calculate the Boltzmann energy distribution of molecules.

  Positional arguments :
  energies     -- array with the energies of the molecules (null-based)
                   units of the energies are given by the energy_units
                   keyword argument

  Keyword arguments :
  energy_units --  units of the energies (default 0, i.e. hartree)
                    possible values :
                      0 -- hartree
                      1 -- kJ/mol
  temperature  --  temperature in Kelvin (default 298.15)

  Return a null-based ndarray with the percentages of the molecules
  (values between 0 to 1).
  
  """
  if energies is None or 0 == len(energies) :
    raise InvalidArgumentError('Invalid array with energies')

  if energy_units not in (0, 1) :
    raise InvalidArgumentError('Invalid energy units : %d.' % energy_units)

  factor =  1000. / (R * temperature)
  
  if 0 == energy_units :
    factor *= HARTREE2KJMOL
  
  denominator = 0.
  for i in xrange(len(energies)) :
    delta = (energies[i] - energies[0]) * factor
    
    # this avoids the overflow
    if -100. < delta :
      denominator += exp(-delta)

  # finally
  ans = []
  for i in xrange(len(energies)) :
    delta = (energies[i] - energies[0]) * factor

    # this avoids the overflow
    if -100. < delta :
      ans.append(exp(-delta) / denominator)

    else :
      ans.append(0.)

  return array(ans, 'd')

def signum(num) :
  """Signum of a number.
  
              /-  1  if x > 0
  signum(x) = |   0  if x = 0
              \- -1 otherwise
            
  """
  if 0. > num :
    return -1
  elif 0. < num :
    return 1
  else :
    return 0

def fitgauss_params(n_gauss=6) :
  """Parameters of a least square fitting Gauss functions to the shape of
  a Lorentz function with a full width at half-maximum (FWHM) of 1.

  For details refer to W. Hug and J. Haesler. Int. J. Quant. Chem. 104:695-715,
  2005

  Keyword arguments :
  n_gauss -- number of Gauss functions (default 6)
         Currently the supported range of values is between 3 and 8

  Return a ndarray of the dimension (2, n_gauss), each column of which
  corresponds to the pair (c_i, a_i).

  """
  if 0 >= n_gauss or not isinstance(n_gauss, int) :
    raise InvalidArgumentError('Number of Gauss functions should be a \
    positive integer, got %s' % str(n_gauss))

  if n_gauss < 3 or n_gauss > 8 :
    raise InvalidArgumentError('Parameters for %d Gauss function are \
    not available yet.' % n_gauss)

  params = zeros((2, n_gauss), 'd')

  # 1 - r^2 : deviation of the correlation coefficient
  # delta_F : error on the area for the fit expressed in %

  # 1 - r^2 = 3.47E-4
  # delta_F = 4.65
  if 3 == n_gauss :
    params[0] = (5.69E-1, 3.63E-1, 5.85E-2)
    params[1] = (3.05E-1, 7.48E-1, 2.60E+0)

  # 1 - r^2 = 6.12E-5
  # delta_F = 2.50
  elif 4 == n_gauss :
    params[0] = (4.26E-1, 4.27E-1, 1.25E-1, 1.73E-2)
    params[1] = (2.68E-1, 5.63E-1, 1.38E+0, 4.82E+0)

  # 1 - r^2 = 1.28E-5
  # delta_F = 1.44
  elif 5 == n_gauss :
    params[0] = (3.20E-1, 4.44E-1, 1.85E-1, 4.34E-2, 5.76E-3)
    params[1] = (2.43E-1, 4.65E-1, 9.75E-1, 2.40E+0, 8.36E+0)

  # 1 - r^2 = 3.01E-6
  # delta_F = 0.86
  elif 6 == n_gauss :
    params[0] = (2.41E-1, 4.32E-1, 2.34E-1, 7.37E-2, 1.60E-2, 2.10E-3)
    params[1] = (2.26E-1, 4.04E-1, 7.69E-1, 1.61E+0, 3.97E+0, 1.38E+1)

  # 1 - r^2 = 7.84E-7
  # delta_F = 0.53
  elif 7 == n_gauss :
    params[0] = (1.83E-1, 4.05E-1, 2.70E-1, 1.05E-1, 2.98E-2, 6.32E-3, 8.26E-4)
    params[1] = (2.12E-1, 3.62E-1, 6.45E-1, 1.23E+0, 2.58E+0, 6.34E+0, 2.21E+1)

  # 1 - r^2 = 2.20E-7
  # delta_F = 0.34
  elif 8 == n_gauss :
    params[0] = (1.40E-1, 3.71E-1, 2.93E-1, 1.34E-1, \
                 4.58E-2, 1.25E-2, 2.63E-3, 3.43E-4)
    params[1] = (2.01E-1, 3.31E-1, 5.61E-1, 9.99E-1, \
                 1.90E+0, 3.99E+0, 9.84E+0, 3.43E+1)

  return params


def voigt_norm(arx, n_gauss, fitparams, param_k, param_b) :
  """Normalized approximate Voigt profile as a combination of Gauss functions.

  For details refer to W. Hug and J. Haesler. Int. J. Quant. Chem. 104:695-715,
  2005

  Positional arguments :
  arx       --  value (number or an array)
  n_gauss   --  number of Gauss functions
  fitparams --  fit coeffitiens (c_i, a_i)
                returned by fitgauss_params()
  param_k   --  FWHM of the Lorentz curve = 2k
  param_b   --  Gaussian instrument profile

  """
  if isinstance(arx, ndarray) :
    sum_ = zeros(arx.shape, 'd')
    _exp = numpy_exp
  else :
    sum_ = 0.
    _exp = exp

  arx2  = arx * arx
  
  for i in xrange(n_gauss) :
    ai_   = fitparams[1, i]
    
    sum_ += fitparams[0, i] / \
            sqrt( 4 * param_k * param_k + param_b * param_b / (ai_ * ai_) ) * \
            _exp(- arx2 / (8 * param_k * param_k * ai_ * ai_ + \
                           2 * param_b * param_b))

  return 2. / pi * sum_

def boltzmann_factor(wavnu) :
  """Boltzmann correction.

  The correction takes into account the thermal population of vibrational
  states. It is applied to the Raman/ROA scattering cross-sections, since they
  depend on the temperature at which a sample is measured.
  
  KBoltz = 1 / [1 - exp(- 100 * H * c * wavnu / KB * T)]

  Positional arguments :
  wavnu -- wavenumber in cm**(-1)

  """
  return 1. / (1. - exp(-100. * H * C / KB / (25. + T_KELVIN) * wavnu))

def savitzky_golay(data, order=2, nl=2, nr=2) :
  """Smooth data with the Savitzky-Golay algorithm.

  The returned smoothed data array has the same dimension as the original one.

  Positional arguments :
  data  -- y data

  Keyword arguments :
  order -- order of the polynomial (default 2)
  nl    -- number leftward data points (default 2)
  nr    -- number leftward data points (default 2)
  
  """
  if not isinstance(data, ndarray) or 1 != len(data.shape) :
    raise InvalidArgumentError('data must be an one-dimensional ndarray')

  if 0 > nl or 0 > nr :
    raise InvalidArgumentError('nl and nr must be positive')

  # coefficients of the polynomial
  b = mat([ [k**i for i in xrange(1 + order)] for k in xrange(-nl, 1 + nr) ])
  weights = pinv(b).A[0]

  # finally
  idata = zip(xrange(-nl, 1 + nr), weights)

  smoothed_data = zeros(data.shape, 'd')
  data_ = concatenate((zeros(nl), data, zeros(nr)))

  for i in xrange(nl, len(data_) - nr) :
    val = 0.
    for k, weight in idata :
      val += weight * data_[k + i]

    smoothed_data[i - nl] = val

  return smoothed_data
