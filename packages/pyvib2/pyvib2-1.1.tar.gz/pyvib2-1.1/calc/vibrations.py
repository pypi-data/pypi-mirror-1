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

"""Module for handling vibrational motion.

For details refer to http://dx.doi.org/10.1007/s00214-006-0185-2.

The following functions are exported :
    correlate_vibrations()     -- correlate two vibrations
    remove_contaminations()    -- remove non-vibrational contaminations
    correlate_vibrations_all() -- correlate all found vibrations
    create_dyad()              -- create the dyad for a vibration
    generate_tr_rot()          -- generate translations/rotations
    vibana()                   -- perform vibrational analysis
    omega_p()                  -- angular frequency
    dcm_p()                    -- distance change matrix (DCM) for a vibration
    vib_amplitudes()           -- amplitudes of atoms for a vibration
    
"""
__author__ = 'Maxim Fedorovsky'

from math import sqrt, pi

from numpy import zeros, reshape, transpose, dot, array, outer, ndarray
from numpy.linalg import eigh, inv

from pyviblib.util.constants  import HARTREE2INVCM, AMU2AU, HBAR, C, M_AU
from pyviblib.calc.common     import contract, inertia_tensor, mass_center, \
                                       rotmatrix_axis, \
                                       orthogonalize_set, norm, normalize_set
from pyviblib.util.exceptions import InvalidArgumentError, \
                                     DataInconsistencyError

__all__ = ['correlate_vibrations', 'remove_contaminations',
           'correlate_vibrations_all', 'create_dyad',
           'generate_tr_rot', 'vibana',
           'omega_p', 'dcm_p', 'vib_amplitudes']


def correlate_vibrations(L_ref_p, L_tr_p, atom_pairs, U,
                         remove_tr_rot=False,
                         L_tr_rot_F_ref=None, L_tr_rot_F_tr=None) :
  """Calculate the similarity and overlap of two vibrations on a fragment.

  The vibrations must be given as mass-weighted excursions.
  Let us denote the first vibration as reference, and the second one as trial.

  Positional arguments :
  L_ref_p         -- reference vibration (one-based ndarray)
                     shape : (1 + Natoms_ref, 4) with Natoms_ref being the
                     number of atoms in the reference molecule
  L_tr_p          -- trial vibration (one-based ndarray)
                     shape : (1 + Natoms_tr, 4) with Natoms_ref being the
                     number of atoms in the trial molecule
  atom_pairs      -- atom pairs comprising the fragment
                     (null-based ndarray)
                     shape : (Natoms_F, 2) with Natoms_F being the number of
                     atoms in the fragment
                     atom numbers are one-based
                     example : array([ [1, 1], [3, 3], [9, 9] ])
  U               -- rotation matrix found by superimposing the reference and
                     trial molecules on the fragment (one-based ndarray)
                     shape : (4, 4)
                     The trial vibration is rotated with this matrix.
                     if None, the rotation is not carried out.
                     refer to pyviblib.calc.qtrfit.fit()
  
  Keyword arguments :
  remove_tr_rot   -- whether the non-vibrational contaminations are to be
                     removed (default False)
  L_tr_rot_F_ref  -- translations/rotations on the reference *FRAGMENT*
                     (one-based ndarray, default None)
                     shape : (4 + nrot_ref, Natoms_F, 4) with nrot_ref being the
                     number of rotational degrees of freedom in the reference
                     molecule
                     must be supplied if remove_tr_rot is True
  L_tr_rot_F_tr   -- translations/rotations on the trial *FRAGMENT*
                     (one-based ndarray, default None)
                     shape : (4 + nrot_tr, Natoms_F, 4) with nrot_tr being the
                     number of rotational degrees of freedom in the trial
                     molecule
                     must be supplied if remove_tr_rot is True

  Return a dictionary with the following keys :
  similarity      -- similarity
  overlap         -- overlap
  
  """
  if L_ref_p is None or L_tr_p is None or atom_pairs is None  :
    raise InvalidArgumentError('Some of the required parameters are not given')

  if remove_tr_rot and (L_tr_rot_F_ref is None or L_tr_rot_F_tr is None) :
    raise InvalidArgumentError('Translations/rotations are not supplied')

  ans = dict()
  
  # rotate the trial vibration if necessary
  if U is not None :
    L_tr_p = transpose(dot(U, transpose(L_tr_p)))

    # rotating the translations/rotations on the trial FRAGMENT
    if remove_tr_rot :
      for q in xrange(1, L_tr_rot_F_tr.shape[0]) :
        L_tr_rot_F_tr[q] = transpose(dot(U, transpose(L_tr_rot_F_tr[q])))

  # removing translations / rotations
  if remove_tr_rot :    
    # removing the contaminations
    # see the formulae (32, 33) in
    # "Characterization of Vibrational Motion beyond Internal coordinates"
    LL_ref = remove_contaminations(L_ref_p, L_tr_rot_F_ref, atom_pairs[:, 0])
    LL_tr  = remove_contaminations(L_tr_p , L_tr_rot_F_tr, atom_pairs[:, 1])

    # finally
    ans['overlap'] = contract(LL_ref, LL_tr)

    prod_norm = norm(LL_ref) * norm(LL_tr)

  else :
    # extracting the atoms    
    L_ref_p = L_ref_p[[0] + atom_pairs[:, 0].tolist()]
    L_tr_p  = L_tr_p [[0] + atom_pairs[:, 1].tolist()]
    
    # for effectiveness replacing the dyads through scalar products
    ans['overlap'] = contract(L_ref_p, L_tr_p)
    ans['overlap'] = ans['overlap'] * ans['overlap']

    prod_norm = contract(L_ref_p, L_ref_p) * contract(L_tr_p, L_tr_p)

  # finally calculating the similarity
  # be careful with the floating precision...
  if 1e-20 < prod_norm :
    ans['similarity'] = ans['overlap'] / prod_norm

  else :
    ans['similarity'] = 0.

  return ans

def remove_contaminations(L_p, L_tr_rot_F, atoms) :
  """Remove the translational and rotational contaminations on a fragment.

  Positional argument :
  L_p         --  mass-weighted excursion for the vibration (one-based ndarray)
                  shape : (1 + Natoms, 4) with Natoms being the number of atoms
                  in the molecule
  L_tr_rot_F  --  mass-weighted excursions for the translations/rotations on
                  the fragment (one-based ndarray)
                  shape : (4 + nrot, Natoms_F, 4) with nrot being the number of
                  rotational degrees of freedom and Natoms_F the number of atoms
                  in the fragment
  atoms       --  atoms comprising the fragment (null-based ndarray)
                  shape : (Natoms_F,)
                  atom numbers are one-based

  Return the dyad for the vibration on the fragment, from which the
  rotational/translational contaminations have been removed.
  Shape : (1 + Natoms_F, 4, 1 + Natoms_F, 4)

  """
  atoms = [0] + atoms.tolist()
  
  L_p   = L_p[atoms]
  LL    = outer(L_p, L_p)
  
  for q in xrange(1, L_tr_rot_F.shape[0]) :
    L_q = L_tr_rot_F[q]
    
    cross_term = contract(L_p, L_q)
    LL        -= (cross_term * cross_term) * outer(L_q, L_q)

  return LL

def correlate_vibrations_all(L_ref, L_tr_rot_ref, L_tr, L_tr_rot_tr, atom_pairs,
                             U=None, include_tr_rot=False,
                             remove_tr_rot=False,
                             L_tr_rot_F_ref=None, L_tr_rot_F_tr=None) :
  """Correlate a set of vibrations on a fragment.

  The vibrations to be correlated must be given as mass-weighted excursions.
  Let us denote by reference the first set of vibrations and by trial the second
  one.

  Positional arguments :
  L_ref           -- vibrations of the reference molecule (one-based ndarray)
                     shape : (1 + NFreq_ref, 1 + Natoms_ref, 4) with NFreq_ref
                     being the number of vibrations in the reference molecule
                     and Natoms_ref the number of atoms in it
  L_tr_rot_ref    -- translations/rotations of the reference molecule
                     (one-based ndarray)
                     shape : (4 + nrot_ref, 1 + Natoms_ref, 4) with nrot_ref
                     being the number of rotational degrees of freedom in the
                     reference molecule
  L_tr            -- vibrations of the trial molecule (one-based ndarray)
                     shape : (1 + NFreq_tr, 1 + Natoms_tr, 4) with NFreq_tr
                     being the number of vibrations in the trial molecule
                     and Natoms_tr the number of atoms in it
  L_tr_rot_tr     -- translations/rotations of the trial molecule
                     (one-based ndarray)
                     shape : (4 + nrot_tr, 1 + Natoms_tr, 4) with nrot_tr
                     being the number of rotational degrees of freedom in the
                     trial molecule
  atom_pairs      -- atom pairs comprising the fragment
                     (null-based ndarray)
                     shape : (Natoms_F, 2) with Natoms_F being the number of
                     atoms in the fragment
                     atom numbers are one-based
                     example : array([ [1, 1], [3, 3], [9, 9] ])
                     
  Keyword arguments :
  U               -- rotation matrix found by superimposing the reference and
                     trial fragments (one-based ndarray, default None)
                     shape : (4, 4)
                     The trial vibrations are rotated with this matrix.
                     if None, the rotation is not carried out.
  include_tr_rot  -- include the translations/rotations explicitely in the
                     result overlaps and similarities matrices.
  remove_tr_rot   -- whether the non-vibrational contaminations are to be
                     removed (default False)
  L_tr_rot_F_ref  -- translations/rotations on the reference fragment
                     (one-based ndarray, default None)
                     shape : (4 + nrot_ref, Natoms_F, 4) with nrot_ref being the
                     number of rotational degrees of freedom in the reference
                     molecule and Natoms_F the number of atoms in the fragment
                     must be supplied if remove_tr_rot is True
  L_tr_rot_F_tr   -- translations/rotations on the trial fragment
                     (one-based ndarray, default None)
                     shape : (4 + nrot_tr, Natoms_F, 4) with nrot_tr being the
                     number of rotational degrees of freedom in the trial
                     molecule
                     must be supplied if remove_tr_rot is True
  
  Return a dictionary with the following keys :
  overlaps        :  overlaps matrix (one-based ndarray)
  similarities    :  similarities matrix (one-based ndarray)
  
  """
  # control strictly input parameters
  if L_ref is None or L_tr is None or atom_pairs is None :
    raise InvalidArgumentError(\
      'Reference, trial vibrations and atom_pairs must be given')

  if 3 != len(L_ref.shape) or 3 != len(L_tr.shape) :
    raise InvalidArgumentError('Vibrations must be three-dimensional ndarrays')

  if 2 != len(atom_pairs.shape) :
    raise InvalidArgumentError('Atom pairs must be a two-dimensional ndarray')

  if (L_tr_rot_ref is not None and L_tr_rot_tr is None) or \
     (L_tr_rot_ref is None and L_tr_rot_tr is not None) :
    raise InvalidArgumentError(\
      'Reference and trial translations / rotations must ' +
      'be given or not given simultaneously')

  if L_tr_rot_ref is not None and L_tr_rot_tr is not None :
    if 3 != len(L_tr_rot_ref.shape) or 3 != len(L_tr_rot_tr.shape) :
      raise InvalidArgumentError(\
        'Translations / rotations must be three-dimensional ndarrays')

  # initializing
  include_tr_rot = include_tr_rot and \
                   ( L_tr_rot_ref is not None and L_tr_rot_tr is not None )

  NFreq_ref = L_ref.shape[0] - 1
  NFreq_tr  = L_tr.shape[0]  - 1

  if include_tr_rot :
    N_tr_rot_ref = L_tr_rot_ref.shape[0] - 1
    N_tr_rot_tr  = L_tr_rot_tr.shape[0]  - 1

    shape_matrices = (1 + N_tr_rot_ref + NFreq_ref,
                      1 + N_tr_rot_tr + NFreq_tr)
  else :
    N_tr_rot_ref = 0
    N_tr_rot_tr  = 0
    
    shape_matrices = ( 1 + NFreq_ref,  1 + NFreq_tr )

  overlaps     = zeros( shape_matrices, 'd' )
  similarities = zeros( shape_matrices, 'd' )
  
  # i -> reference vibrations
  # j -> trial     vibrations
  for i in xrange(1, shape_matrices[0]) :
    # reference vibration  
    if i <= N_tr_rot_ref :
      if include_tr_rot :
        L_ref_p = L_tr_rot_ref[i]
      else :
        L_ref_p = L_ref[i]
    else :
      L_ref_p = L_ref[i - N_tr_rot_ref]
      
    for j in xrange(1, shape_matrices[1]) :
      # trial vibration    
      if j <= N_tr_rot_tr :
        if include_tr_rot :
          L_tr_p = L_tr_rot_tr[j]
        else :
          L_tr_p = L_tr[j]
      else :
        L_tr_p = L_tr[j - N_tr_rot_tr]

      # go
      ans_ij = correlate_vibrations(L_ref_p, L_tr_p, atom_pairs, U,
                                    remove_tr_rot,
                                    L_tr_rot_F_ref, L_tr_rot_F_tr)

      overlaps[i, j]     = ans_ij['overlap']
      similarities[i, j] = ans_ij['similarity']


  # packing the results
  ans = {}

  ans['overlaps']     = overlaps
  ans['similarities'] = similarities

  return ans

def create_dyad(L_p, atom_list=None) :
  """Create the dyad tensor for a vibration on a fragment.

  Positional arguments :
  L_p       -- mass-weighted excursion for the vibration (one-based ndarray)
               shape : (1 + Natoms, 4) with Natoms being the number of atoms
               in the molecule

  Keyword arguments :
  atom_list -- atoms comprising the fragment (null-based ndarray, default None)
               atom numbers are one-based
               shape : (Natoms_F,) with Natoms_F being the number of atoms in
               the fragment
               if None, use all atoms

  Return the dyad with the shape (1 + Natoms_F, 4, 1 + Natoms_F, 4).
  
  """
  if not isinstance(L_p, ndarray) :
    raise InvalidArgumentError('L_p is not given')

  # if the atom list is not given generate it
  if atom_list is None :
    npairs = L_p.shape[0] - 1
    atom_list = array([ (1 + i) for i in xrange(npairs) ])
  else :
    npairs = atom_list.shape[0]

  # extracting the desired atoms
  # using a ndarray function for efficiency :)
  atom_list = [0] + atom_list.tolist()

  return reshape(outer(L_p[atom_list], L_p[atom_list]),
                 (1 + npairs, 4, 1 + npairs, 4) )
  
def generate_tr_rot(L, coords, masses, atom_list=None) :
  """Generate translations/rotations for a fragment in a molecule.

  Positional arguments :
  L         -- set of vibrations (one-based ndarray)
               if given, the result translations/rotations will be made
               orthogonal to the set
               shape : (1 + Nvib, 1 + Natoms, 4) with Nvib being number of
               vibrations, Natoms the number of atoms
  coords    -- coordinates of the atoms (one-based ndarray)
               shape : (1 + Natoms, 4)
  masses    -- masses of the atoms (one-based ndarray)
               shape : (1 + Natoms,)

  Keyword arguments :
  atom_list -- atoms comprising the fragment (null-based ndarray, default None)
               atom numbers are one-based
               shape : (Natoms_F,) with Natoms_F being the number of atoms in
               the fragment
               if None, use all atoms

  The return value is a dictionary with the following keys :
  L_tr_rot   : set of the translations and rotations (one-based ndarray)
               shape : (4 + nrot, 1 + Natoms_F, 4) with nrot being the number
               of rotational degrees of freedom
               The first three members are always translations.
               The number of rotations nrot can vary.
  I          : principal axes of the inertia tensor (null-based ndarray)
               shape : (3,)
  I_values   : principal values of the inertia tensor (null-based ndarray)
               shape : (3,)
  
  """
  if coords is None or masses is None :
    raise InvalidArgumentError('Coordinates and masses must be given')

  if atom_list is not None and not isinstance(atom_list, ndarray) :
    raise InvalidArgumentError(\
      'atom_list should be a null-based ndarray with one-based atom numbers')

  # if atom_list is given - use it
  if atom_list is not None :
    al = [0] + atom_list.tolist()

    coords = coords[al]
    masses = masses[al]

    if L is not None :
      # for orthogonalization
      L_F = zeros((L.shape[0], len(al), 4), 'd')
      for p in xrange(1, L.shape[0]) :
        L_F[p] = L[p][al]

      L = L_F

  Natoms = coords.shape[0] - 1
  L_tr_rot = zeros( (7, 1 + Natoms, 4), 'd' )

  # translations
  for t in xrange(1, 4) :
    for a in xrange(1, 1 + Natoms) :
      L_tr_rot[t, a, t] = sqrt(masses[a])
    
  # rotations around the mass center
  M = mass_center(coords, masses)

  coords_M = zeros(coords.shape, 'd')
  coords_M[1:, 1:] = coords[1:, 1:] - M[1:]

  I = inertia_tensor(coords_M, masses)
  I_values, I = eigh(I)
  
  # ignore inertia axes with small eigenvalues
  start_index_I = 0

  for e_val in I_values :
    if 1e-5 > e_val :
      start_index_I += 1
    
  if 3 == start_index_I and 1 != Natoms :
    raise DataInconsistencyError(\
      'All three principal values are too small, cannot proceed')

  # rotate around the found axes
  for i in xrange(start_index_I, 3) :
    U_i = rotmatrix_axis(I[i], 0.1)

    coords_i = transpose(dot(U_i, transpose(coords_M)))

    for a in xrange(1, 1 + Natoms) :
      L_tr_rot[4 + i - start_index_I, a, 1:] = \
                 (coords_i[a,1:] - coords_M[a,1:]) / sqrt(masses[a])

  # find the number of rotations
  nrot = 3

  for rot in L_tr_rot[4:] :
    if 1e-10 > contract(rot, rot) :
      nrot -= 1

  if 1 != Natoms and 2 > nrot :
    raise DataInconsistencyError(\
      'Molecule consisting of more than one atom cannot have ' +
      'less than two rotational degrees of freedom')

  # refine the translations and rotations
  L_tr_rot = L_tr_rot[:4+nrot]

  # if L is not given return raw non-normalized translations / rotations
  # orthonormalizing the merged system of the given
  # vibrations and the translations / rotations
  ans = {}
  
  ans['I']        = I[start_index_I:]
  ans['I_values'] = I_values[start_index_I:]
  
  if L is not None :
    L_all = zeros( (L.shape[0] + 4 + nrot, 1 + Natoms, 4), 'd')

    L_all[1:L.shape[0]   , 1:, 1:] = L[1:L.shape[0], 1:, 1:].copy()
    L_all[L.shape[0] + 1:, 1:, 1:] = L_tr_rot[1:   , 1:, 1:].copy()

    orthogonalize_set(L_all)

    ans['L_tr_rot'] = L_all[L.shape[0]:]
    
  else :
    L_tr_rot = L_tr_rot[:4 + nrot]
    normalize_set(L_tr_rot)
    
    ans['L_tr_rot'] = L_tr_rot

  return ans

def vibana(hessian, coords, masses) :
  """Perform the vibrational analysis.

  For details refer to http://www.gaussian.com/g_whitepap/vib.htm.
  This implementation generates the translations and rotations around
  the pricipal axes of the inertia tensor.

  Positional arguments :
  hessian -- Hessian matrix (one-based ndarray)
             shape : (1 + Natoms, 4, 1 + Natoms, 4)
  coords  -- coordinates of the atoms (one-based ndarray)
             shape : (1 + Natoms, 4)             
  masses  -- masses of the atoms (one-based ndarray)
             shape : (1 + Natoms,)
  
  Return a dictionary with the following keys :
  freqs    :   frequencies array sorted in ascending order (one-based ndarray)
               shape : (1 + NFreq,) with NFreq being the number of vibrations
  L        :   set of mass-weighted excursions (one-based ndarray)
               shape : (1 + NFreq, 1 + Natoms, 4)
  
  """
  # check the data before start
  if not isinstance(hessian, ndarray) or not isinstance(coords, ndarray) \
     or not isinstance(masses, ndarray) :
    raise InvalidArgumentError('All parameters must be ndarrays')

  if 4 != len(hessian.shape) :
    raise InvalidArgumentError('Hessian must be a 4-dimensional ndarray')

  if 2 != len(coords.shape) :
    raise InvalidArgumentError('Coordinates must be a two-dimensional ndarray')

  if 1 != len(masses.shape) :
    raise InvalidArgumentError('Coordinates must be a one-dimensional ndarray')

  if hessian.shape[0:2] != hessian.shape[2:] != coords.shape :
    raise InvalidArgumentError(\
      'Dimension of the hessian and coordinates must correspond')

  if coords.shape[0] != masses.shape[0] :
    raise InvalidArgumentError(\
      'Coordinates and mass must have the equal number of atoms')

  ## step 1 : construct the mass-weighted hessian (in a.u.)
  ## result : hessian_mw
  Natoms       =  coords.shape[0] - 1

  # we will manipulate internally with null-based arrays
  shape_0      = (Natoms, 3, Natoms, 3)
  shape_diag   = (3 * Natoms, 3 * Natoms)
  
  hessian_mw = zeros(shape_0, 'd')

  for a in xrange(1, 1 + Natoms) :
    for b in xrange(1, 1 + Natoms) :
      hessian_mw[a-1, :, b-1, :] = hessian[a, 1:, b, 1:].copy() / \
                                   (sqrt(masses[a] * masses[b]) * AMU2AU)

  hessian_mw = reshape(hessian_mw, shape_diag)

  ## step 2 : diagonalize the mass-weighted hessian
  ## result : D_raw (eigenvectors in rows)
  freqs, D_raw = eigh(hessian_mw)

  ## step 3 : a) generate translations / rotations around the inertia axes
  ##          b) make the vibrational modes orthogonal
  ##             to the translations / rotations
  ## result : D
  ans_tr_rot = generate_tr_rot(None, coords, masses)

  L_tr_rot   = ans_tr_rot['L_tr_rot']
  nrot       = L_tr_rot.shape[0] - 4

  D = zeros(shape_diag, 'd')

  for i in xrange(3 + nrot) :
    D[i] = reshape(L_tr_rot[1 + i, 1:, 1:], shape_diag[0]).copy()

  D[3 + nrot:] = D_raw[3 + nrot:]

  orthogonalize_set(set_in=D, make_orthonormal=True, set_out=None, base=0)

  ## step 4 : transform the mass-weighted hessian in one in internal coordinates
  ## result : hessian_int
  hessian_int = dot(dot(inv(D), hessian_mw), D)

  ## step 5 : a) diagonalize the hessian in internal coordinates, result :
  ##             L_int (eigenvectors in rows)
  ##          b) calculate the mass-weighted displacements as L = D * L_int
  ## result : L
  dummy, L_int = eigh(hessian_int)
  L            = dot(D, L_int)

  ## finalize
  # recalculate frequencies in a.u. to cm**(-1)
  for i in xrange(3 + nrot, len(freqs) ) :
    freqs[i] = HARTREE2INVCM * sqrt(freqs[i])

  # reshaping the mass-weighted displacements
  L_final = zeros((1 + 3 * Natoms - 3 - nrot, 1 + Natoms, 4), 'd')
  
  for i in xrange(3 + nrot, L.shape[0]) :   
    L_final[i - 3 - nrot + 1, 1:, 1:] = reshape(L[:, i], (Natoms, 3))

  # packing results
  ans = {}

  ans['freqs'] = array([0.] + list(freqs[3 + nrot:]))
  ans['L']     = L_final

  return ans

def omega_p(nu) :
  """Calculate the angular frequency.
  
  omega_p = 200 * pi * C * nu.

  Positional arguments :
  nu -- wavenumber in cm**(-1)

  The return value is expressed in inverse seconds.
  
  """
  return 200. * pi * C * nu

def dcm_p(coords, Lx, nu) :
  """Calculate the distance change matrix (DCM) for a normal mode.

  Positional arguments :
  coords  -- coordinates of the atoms (one-based ndarray)
             shape : (1 + Natoms, 4) with Natoms being the number of atoms
  Lx      -- cartesian excursions (one-based ndarray)
             shape : (1 + Natoms, 4)
  nu      -- wavenumber in cm**(-1)      

  The return value is an one-based ndarray with the
  shape (1 + Natoms, 1 + Natoms).
  
  """
  if not isinstance(coords, ndarray) or not isinstance(Lx, ndarray) :
    raise InvalidArgumentError('coords & Lx must be ndarrays')

  if coords.shape != Lx.shape :
    raise InvalidArgumentError(\
      'coords & Lx must have the equal number of atoms')

  dcm = zeros((coords.shape[0], coords.shape[0]), 'd')

  # constant for the conversion
  K = sqrt(HBAR / (pi * C * 100. * nu)) * 1E10 * sqrt(AMU2AU/M_AU)

  # matrix is antisymmetric with 0 on the diagonal
  for a in xrange(1, dcm.shape[0] - 1) :
    for b in xrange(1 + a, dcm.shape[0]) :
      dcm[a, b] = norm(coords[b] - coords[a] + K*(Lx[b] - Lx[a])) - \
                  norm(coords[b] - coords[a] - K*(Lx[b] - Lx[a]))
      dcm[b, a] = dcm[a, b]


  # the total distance change must be positive
  if 0. > dcm.sum() :
    dcm *= -1.

  return dcm
    
def vib_amplitudes(Lx, nu, n_p=0) :
  """Calculate the amplitudes of atoms for a vibration.

  Positional arguments :
  Lx  -- cartesian excursions (one-based ndarray)
         shape : (1 + Natoms, 4) with Natoms being the number of atoms
  nu  -- wavenumber in cm**(-1)

  Keyword arguments :
  n_p -- vibrational number (default 0)
         the default value instructs to calculate the zero-point amplitudes

  The return value is an one-based ndarray with the shape (1 + Natoms,).
  The units are angstroms.

  """
  if not isinstance(Lx, ndarray) or 0. >= nu or 0 > n_p :
    raise InvalidArgumentError('invalid input parameters')

  K = 2. * sqrt(HBAR * (0.5 + n_p) / omega_p(nu)) * 1E10 * \
      sqrt(AMU2AU / M_AU)

  ampl = [K * norm(Lx[a]) for a in xrange(Lx.shape[0])]
  
  return array(ampl, 'd')
