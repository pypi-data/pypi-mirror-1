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

"""Module for Raman/ROA as well as IR/VCD spectra generation.

The following classes are exported :
    RamanROATensors        -- manipulating the Raman/ROA tensors
    IRVCDTensors           -- manipulating the IR/VCD tensors
    ExpRamanROAData        -- exp. Raman, ROA or Degree of circularity spectra

The following functions are exported :
    contract_A_tensor()    -- contract A tensor with unit tensor of Levi-Civita
    f_Qp_i()               -- transition integral between two states
    Kp()                   -- constant Kp used for the Raman/ROA cross-sections
    conv_units_raman_roa() -- convenience function for conversions
    conv_invariant()       -- conversion : a.u. -> invariants' units
    conv_cross_sections()  -- conversion : a.u. -> cross-sections' units
    conv_A4_AMU()          -- conversion : a.u. -> A^4 / AMU
    inv_coeffs_raman_roa() -- linear combinations for the cross-sections
    stick_raman_roa()      -- generate Raman/ROA stick spectra
    fit_raman_roa()        -- generate Raman/ROA spectra as curves
    make_acp()             -- generate atomic contribution patterns (ACPs)

"""
__author__ = 'Maxim Fedorovsky'

import os.path
from math  import pi, sqrt, ceil, log
from numpy import zeros, ndarray, arange, dot

from pyviblib.calc.common     import contract, decompose_t, \
                                     voigt_norm, fitgauss_params, \
                                     boltzmann_factor, norm, levi_civita
from pyviblib.calc.vibrations import create_dyad
from pyviblib.util.constants  import HBAR, C, MU_VACUUM, RAMAN_ROA_INV2SI, \
                                     C_AU, AMU2AU, INVCM2AU, \
                                     DIPSTRENGTH2SI, DIPSTRENGTH2EPSILON, \
                                     ROTSTRENGTH2SI, ROTSTRENGTH2DEPSILON
from pyviblib.util.exceptions import InvalidArgumentError, ConstructorError, \
                                     DataInconsistencyError
from pyviblib.util.misc       import Command, PropertiesContainer
import pyviblib.io.parsers

__all__ = ['RamanROATensors', 'IRVCDTensors', 'ExpRamanROAData',
           'contract_A_tensor', 'f_Qp_i', 'Kp', 'conv_units_raman_roa',
           'conv_invariant', 'conv_cross_sections',
           'conv_A4_AMU', 'inv_coeffs_raman_roa', 'stick_raman_roa',
           'fit_raman_roa', 'make_acp']

# List of available invariants
LIST_INVARIANTS = ('a2', 'b2', 'aG', 'b2G', 'b2A')

# List of available V tensors
LIST_VTENSORS   = tuple([ 'V_%s' % inv for inv in LIST_INVARIANTS ])

# List of available units of the invariants (J)
LIST_INVARIANTSUNITS = ('invariant', 'cross-section', 'A^4/AMU', 'reduced')

# Length of a peak's fitting interval
X_PEAK_INTERVAL = 500.


def contract_A_tensor(A) :
  """Contract A tensor with antisymmetric unit tensor of Levi-Civita.

  PQ[m, n] = sum_{l, k} eps[m, l, k] * A[l, k, n]

  Positional arguments :
  A -- A tensor (one-based ndarray)
       shape : (1 + Natoms, 4, 4, 4, 4) with Natoms being the number of atoms

  Return the contracted tensor PQ with a shape of (1 + Natoms, 4, 4, 4).
  
  """
  if not isinstance(A, ndarray) or 5 != len(A.shape) or \
     (4, 4, 4, 4) != A.shape[1:] :
    raise InvalidArgumentError('Invalid non-contracted A tensor')

  PQ  = zeros(A.shape[:-1], 'd')
  eps = levi_civita()

  for a in xrange(1, A.shape[0]) :
    for q in xrange(1, 4) :
      for m in xrange(1, 4) :
        for n in xrange(1, 4) :
          # summing over l and k
          for l in xrange(1, 4) :
            for k in xrange(1, 4) :
              PQ[a, q, m, n] += eps[m, l, k] * A[a, q, l, k, n]

  return PQ      

def f_Qp_i(nu) :
  """Transition integral between two molecular vibrational states |i> and <f|.

  <f|Qp|i> = sqrt(HBAR / 400 * pi * C * nu)

  It is assumed that the f <- i is a fundamental transition and that the
  vibration is harmonic, i.e. described by the normal mode p. For details
  refer to W. Hug. Chem. Phys., 264(1):53-69, 2001.

  Positional arguments :
  nu -- wavenumber in cm**(-1)

  Return value is expressed in SI units.
  
  """
  if 0. > nu :
    raise InvalidArgumentError('Bad value of the wavenumber : %s' % str(nu))

  return sqrt(HBAR / (400 * pi * C  * nu))

def Kp(nu_0, nu) :
  """Factor appearing in the calculating of the Raman/ROA cross-sections.

  Kp = 10^7 / 9 * pi^2 * MU_VACUUM^2 * C^4 * (nu_0 - nu)^3 * nu_0
  
  For details refer to W. Hug. Chem. Phys., 264(1):53-69, 2001.

  Positional arguments :
  nu_0  -- wavenumber of the incident light in cm**(-1)
  nu    -- shift in cm**(-1)

  Return value is expressed in SI units.
  
  """
  if 0. >= nu_0 or 0. >= nu :
    raise InvalidArgumentError('Invalid values of the input parameters')
  
  return 1E+07/9 * pi**2 * MU_VACUUM **2 * C**4 * (nu_0 - nu)**3 * nu_0

def conv_units_raman_roa(units, lambda_incident, nu, J) :
  """Conversion factor for a Raman/ROA quantity.

  Positional arguments :
  units           -- units of the molecular invariant
                     one of ('invariant', 'cross-section', 'A^4/AMU', 'reduced')
  lambda_incident -- wavelength of the incident light in nm
  nu              -- wavenumber in cm**(-1)
  J               -- molecular invariant (if applicable)
                     one of ('a2', 'b2', 'aG', 'b2G', 'b2A')

  """
  if units not in LIST_INVARIANTSUNITS :
    raise InvalidArgumentError('units must be one of %s, got %s' % \
                               (str(LIST_INVARIANTSUNITS), str(units)))
  
  if 'invariant' == units :
    factor = conv_invariant(nu)

  elif 'cross-section' == units :
    factor = conv_cross_sections(lambda_incident, nu)
    
  elif 'A^4/AMU' == units :
    factor = conv_A4_AMU(J)

  # reduced invariants -- no conversion :)
  else :
    factor = 1.

  return factor

def conv_invariant(nu) :
  """Conversion factor from J_ab in a.u. to molecular invariants in SI units.

  For details refer to W. Hug. Chem. Phys., 264(1):53-69, 2001.

  Positional arguments :
  nu  -- wavenumber in cm**(-1)
    
  """
  if 0. >= nu :
    raise InvalidArgumentError('Invalid frequency : %s' % str(nu))

  return f_Qp_i(nu)**2 * RAMAN_ROA_INV2SI

def conv_cross_sections(lambda_incident, nu) :
  """Conversion factor from J_ab in a.u. to the cross-sections in A^2 / sr.

  For details refer to W. Hug. Chem. Phys., 264(1):53-69, 2001.

  Positional arguments :
  lambda_incident -- wavelength of the incident light in nm
  nu              -- wavenumber in cm**(-1)

  """
  # wavenumber of the incident light in cm**(-1)
  nu_0 = 1E+07 / lambda_incident

  # taking into account the thermal population of vibrational states  
  KBoltz = boltzmann_factor(nu)

  # 1E+20 : factor m^2 -> A^2
  return Kp(nu_0, nu) * conv_invariant(nu) * KBoltz * 1E+20

def conv_A4_AMU(J) :
  """Conversion factor from J_ab in a.u. to A^4/AMU.

  For a2 and b2 (Raman invariants)  : 142.943570.
  For aG, b2G, b2A (ROA invariants) : 142.943570 / C_AU, with C_AU being the
  speed of light in a.u.
.
  Positional arguments :
  J -- molecular invariant
       one of ('a2', 'b2', 'aG', 'b2G', 'b2A')

  """
  if J not in LIST_INVARIANTS :
    raise InvalidArgumentError('J must be one of %s, got %s' % \
                               (str(LIST_INVARIANTS), str(J)))

  J_i = list(LIST_INVARIANTS).index(J)

  if 2 > J_i :
    return 142.943570
  
  else :
    return 142.943570 / C_AU

def inv_coeffs_raman_roa(scattering=0) :
  """Linear combination coefficients of the five molecular invariants for the
  Raman/ROA cross-sections for a given scattering type.

  RAMAN = K_raman * (x1_ram * a2 + x2_ram * b2)
  ROA   = K_roa   * (x1_roa * aG + x2_roa * b2G + x3_roa * b2A)

  For details refer to W. Hug. Chem. Phys., 264(1):53-69, 2001.

  Keyword arguments :
  scattering -- scattering type (default 0)

  Possible values of the scattering argument :
      0 : backward  (     1.,  90., 14.,      4./C_AU,   0., 12.,  4.)
      1 : forward   (     1.,  90., 14.,      4./C_AU,  90.,  2., -2.)
      2 : ICP_perp  (     1.,  45.,  7.,      2./C_AU,  45.,  7.,  1.)
      3 : ICP_par   (     1.,   0.,  6.,      2./C_AU,   0.,  6., -2.)
      4 : integral  (4*pi/3., 180., 40., 8*pi/3./C_AU, 180., 40.,  0.)

      where C_AU is the speed of light in a.u.

  Return (K_raman, x1_ram, x2_ram, K_roa, x1_roa, x2_roa, x3_roa)
      
  """
  if scattering not in xrange(5) :
    raise InvalidArgumentError(\
      'Invalid value of scattering : %s, should be integer in range 0-4.' % \
      str(scattering))

  if 0 == scattering :
    return (     1.,  90., 14.,      4./C_AU,   0., 12.,  4.)

  elif 1 == scattering :
    return (     1.,  90., 14.,      4./C_AU,  90.,  2., -2.)

  elif 2 == scattering :
    return (     1.,  45.,  7.,      2./C_AU,  45.,  7.,  1.)

  elif 3 == scattering :
    return (     1.,   0.,  6.,      2./C_AU,   0.,  6., -2.)

  else :
    return (4*pi/3., 180., 40., 8*pi/3./C_AU, 180., 40.,  0.)

def stick_raman_roa(scattering, J_all) :
  """Generate Raman/ROA stick spectra.

  Positional arguments :
  scattering -- scattering type (see inv_coeffs_raman_roa())
  J_all      -- the five molecular invariants (null-based ndarray)
                shape : (NFreq, 5) with NFreq being the number of vibrations
                returned by RamanROATensors.J_all()

  Return X, raman_Y, roa_Y, degcirc_Y. Each of these arrays is null-based and
  of the length NFreq.
  
  """
  if not isinstance(J_all, ndarray) or 2 != len(J_all.shape) :
    raise InvalidArgumentError('Invalid value of J_all')
  
  # invariants coefficients
  coeffs = inv_coeffs_raman_roa(scattering=scattering)
  
  raman_Y   = coeffs[0] * (coeffs[1] * J_all[:, 0] + coeffs[2] * J_all[:, 1])
  roa_Y     = coeffs[3] * (coeffs[4] * J_all[:, 2] + coeffs[5] * J_all[:, 3] + \
                           coeffs[6] * J_all[:, 4])

  if 2 > scattering :
    degcirc_Y = (5. * J_all[:, 1] - 45. * J_all[:, 0]) / \
                (7. * J_all[:, 1] + 45. * J_all[:, 0])

    # for a forward roa spectrum - invert the sign
    if 1 == scattering :
      degcirc_Y *= -1.
  else :
    degcirc_Y = zeros(J_all.shape, 'd')

  return raman_Y, roa_Y, degcirc_Y

def fit_raman_roa(freqs, J_all, scattering=0, N_G=6,
                  FWHM_is=3.5, FWHM_anis=10., FWHM_inst=7.0,
                  startx=None, endx=None) :
  """Generate Raman/ROA spectra as curves.

  For details refer to W. Hug and J. Haesler. Int. J. Quant. Chem. 104:695-715,
  2005

  Positional arguments :
  freqs      -- wavenumbers of vibrations in ascending order (one-based array)
  J_all      -- invariants in approptiate units
                returned by RamanROATensors.J_all()

  Keyword arguments :
  scattering -- scattering type (see inv_coeffs_raman_roa())
  N_G        -- number of Gauss functions (default 6)
  FWHM_is    -- full width at half maximum for the isotropic invariants
                a2 and b2 (default 3.5)
  FWHM_anis  -- full width at half maximum for the anisotropic invariants
                b2, b2G, b2A (default 10.)
  FWHM_instr -- full width at half maximum for the Gaussian instrument profile
                (default 7.0)
  startx     -- start wavenumber of the fitting interval (default None)
  endx       -- end wavenumbers of the fitting interval (default None)
                if the latter two keyword arguments are None, they are generated
                automatically

  Return X, raman_Y, roa_Y, degcirc_Y.
  
  """
  if freqs is None :
    raise InvalidArgumentError('Frequencies must be given')

  NFreq = len(freqs) - 1

  if not isinstance(J_all, ndarray) or (NFreq, 5) != J_all.shape :
    raise InvalidArgumentError('Invalid J_all argument')

  # fitting interval (calculating from the given frequency array unless given)
  # step is always 1. cm**(-1)
  if startx is None and endx is None :
    #startx = max(0., ceil(freqs[1] - X_PEAK_INTERVAL))
    startx = 0.
    endx   = ceil(freqs[-1] + X_PEAK_INTERVAL)

  X = arange(startx, 1. + endx, 1.)

  # result spectra arrays
  raman_Y   = zeros(X.shape, 'd')
  roa_Y     = zeros(X.shape, 'd')
  degcirc_Y = zeros(X.shape, 'd')

  # help arrays for the nominator and denominator of the degree of circularity
  if 2 > scattering :
    degcirc_nom   = zeros(X.shape, 'd')
    degcirc_denom = zeros(X.shape, 'd')

  # coefficients for the invariants
  coeffs = inv_coeffs_raman_roa(scattering=scattering)

  # fit parameter of a Lorentz curve
  fitparams = fitgauss_params(N_G)

  # bandwidthes
  k_is    = FWHM_is  / 2.
  k_anis  = FWHM_anis  / 2.
  b       = FWHM_inst / ( 2. * sqrt(2. * log(2.)) )

  # iterating through all vibrations
  for p in xrange(1, 1 + NFreq) :
    freq = freqs[p]
    
    # fitting interval for the current peak
    x0 = max(ceil(freq - X_PEAK_INTERVAL), startx)
    x1 = min(ceil(freq + X_PEAK_INTERVAL), endx)

    # indices in the X array
    # WARNING : works with the step 1.0 ONLY !
    i0 = int(x0 - startx)
    i1 = int(x1 - startx)

    x_cur = arange(x0, 1. + x1, 1.) - freq

    # approximating separately the isotropic & anisotropic parts
    is_conv   = voigt_norm(x_cur, N_G, fitparams, k_is , b)
    anis_conv = voigt_norm(x_cur, N_G, fitparams, k_anis , b)

    # and finally combining
    a2, b2, aG, b2G, b2A = J_all[p-1]
    
    raman_Y[i0:1+i1]        += coeffs[0] * (coeffs[1] * a2 * is_conv + \
                                            coeffs[2] * b2 * anis_conv)
    roa_Y[i0:1+i1]          += coeffs[3] * \
                               (coeffs[4] * aG * is_conv + \
                               (coeffs[5] * b2G + coeffs[6] * b2A) * anis_conv)

    if 2 > scattering :
      degcirc_nom[i0:1+i1]    += (5. * b2 * anis_conv - 45. * a2 * is_conv)
      degcirc_denom[i0:1+i1]  += (7. * b2 * anis_conv + 45. * a2 * is_conv)

  # degree of circularity exists for the backward and forward scattering
  if 2 > scattering :
    degcirc_Y = degcirc_nom / ( degcirc_denom + 0.002*1E-14 )

    if 1 == scattering :
      degcirc_Y *= -1.    
  else :
    degcirc_Y = zeros(X.shape, 'd')

  return X, raman_Y, roa_Y, degcirc_Y

def make_acp(J, Lx, V) :
  """Generate atomic contribution patterns (ACPs).

  For details refer to W. Hug. Chem. Phys., 264(1):53-69, 2001.

  Positional arguments :
  J  -- molecular invariant (one-based ndarray)
        shape : (1 + Natoms, 1 + Natoms) with Natoms being the number of atoms
  Lx -- cartesian excursions for the vibration (one-based ndarray)
        shape : (1 + Natoms, 4)
  V  -- correspondent V-tensor (one-based ndarray)
        shape : (1 + Natoms, 4, 1 + Natoms, 4)

  Return the ACPs as a one-based ndarray.
  
  """
  # check the input parameters
  for ar in (J, Lx, V) :
    if not isinstance(ar, ndarray) :
      raise InvalidArgumentError('all the input parameters must be ndarrays')

  if 2 != len(J.shape) or 2 != len(Lx.shape) :
    raise InvalidArgumentError('J and Lx must be square ndarrays')

  if 4 != len(V.shape) :
    raise InvalidArgumentError('V must be four-dimentional ndarray')

  if J.shape[0] != Lx.shape[0] != V.shape[0] != V.shape[2] :
    raise InvalidArgumentError('Incompatible dimensions of J, Ly and V')

  # go :)
  acp = zeros(J.shape[0], 'd')
  
  for a in xrange(1, J.shape[0]) :
    norm_Lxa_Vaa = norm(dot(Lx[a], V[a, :, a, :]))
    norm_Vaa_Lxa = norm(dot(V[a, :, a, :], Lx[a]))
    
    for b in xrange(1, J.shape[0]) :
      norm_Lxa_Vab = norm(dot(Lx[a], V[a, :, b, :]))
      norm_Vba_Lxa = norm(dot(V[b, :, a, :], Lx[a]))
      
      # weighting coefficients
      denom_1 = norm_Lxa_Vab + norm_Lxa_Vaa + \
                norm(dot(V[a, :, b, :], Lx[b])) + \
                norm(dot(V[b, :, b, :], Lx[b]))

      if 0. != denom_1 :
        r_ab = (norm_Lxa_Vab + norm_Lxa_Vaa) / denom_1
      else :
        r_ab = 0.

      denom_2 = norm_Vba_Lxa + norm_Vaa_Lxa + \
                norm(dot(Lx[b], V[b, :, a, :])) + \
                norm(dot(Lx[b], V[b, :, b, :]))

      if 0. != denom_2 :
        r_ba = (norm_Vba_Lxa + norm_Vaa_Lxa) / denom_2
      else :
        r_ba = 0.
             
      acp[a] += r_ab * J[a, b] + r_ba * J[b, a]

  return acp


class RamanROATensors(PropertiesContainer) :
  """Class for manipulating the Raman/ROA tensors.

  For details refer to W. Hug. Chem. Phys., 264(1):53-69, 2001.

  Refer to the DALTON manual page for information how to request a ROA job.
  http://www.kjemi.uio.no/software/dalton/resources/dalton20manual.pdf

  The following read-only properties are exposed :
      Natoms          -- number of atoms
      NFreq           -- number of vibrations
      Lx              -- cartesian excursions for the vibrations
      freqs           -- wavenumbers of vibrations in ascending order
      PP              -- gradients of the polarizability tensor
      PM              -- gradients of the G' tensor
      PQ              -- gradients of the A tensor (contracted)
      lambda_incident -- wavelength of the incident light

  The following public methods are exported :
      V_a2()          -- V-tensor for the a2 molecular invariant
      V_b2()          -- V-tensor for the b2 molecular invariant
      V_aG()          -- V-tensor for the aG molecular invariant
      V_b2G()         -- V-tensor for the b2G molecular invariant
      V_b2A()         -- V-tensor for the b2A molecular invariant
      a2()            -- matrix of the a2 molecular invariant
      b2()            -- matrix of the b2 molecular invariant
      aG()            -- matrix of the aG molecular invariant
      b2G()           -- matrix of the b2G molecular invariant
      b2A()           -- matrix of the b2A molecular invariant
      J_all()         -- all five molecular invariants for all vibrations
      J_rot()         -- all five reduced molecular invariants for the rotations
      acp()           -- generate atomic contribution patterns (ACPs)
      intensities()   -- calculate the Raman/ROA intensities
      norm_sum_vib()  -- normalized sum of ROA over the vibrations
      norm_sum_rot()  -- normalized sum of ROA over the rotations
                  
  """

  def __init__(self, PP, PM, PQ, Lx, freqs, lambda_incident, A=None) :
    """Constructor of the class.

    PP, Lx, freqs and lambda_incident are required to be set.
    If PM or PQ are not set, they will be filled with zeros.

    Positional arguments :
    PP              -- gradients of the polarizability tensor
                       (one-based ndarray)
                       shape : (1 + Natoms, 4, 4, 4) with Natoms being
                       the number of atoms
    PM              -- gradients of the G' tensor
                       (one-based ndarray)
                       shape : (1 + Natoms, 4, 4, 4)
    PQ              -- gradients of the A tensor (contracted)
                       (one-based ndarray)
                       shape : (1 + Natoms, 4, 4, 4)
    Lx              -- cartesian excursions for the vibrations
                       (one-based ndarray)
                       shape : (1 + NFreq, 1 + Natoms, 4) with NFreq being the
                       number of vibrations
    freqs           -- wavenumbers of vibrations in ascending order
                       (one-based ndarray)
                       shape : (1 + NFreq,)
    lambda_incident -- wavelength of the incident light in nm

    Keyword arguments :
    A               -- gradients of the non-contracted A tensor
                       (one-based ndarray, default None)
                       shape : (1 + Natoms, 4, 4, 4, 4)
    
    """
    self._PP              = PP
    self._PM              = PM
    self._PQ              = PQ
    self._Lx              = Lx
    self._freqs           = freqs
    self._lambda_incident = lambda_incident
    self._A               = A

    # internal dictionary to store the calculated data
    self.__data = {}

    PropertiesContainer.__init__(self, modulename='pyviblib.calc.spectra')

  def _check_consistency(self) :
    """Check the consistency of the input data."""
    if 0. >= self._lambda_incident or self._lambda_incident is None :
      raise ConstructorError(
        'Invalid value of the wavelength of the incident light : %s' % \
        str(self._lambda_incident))

    # the following data must be available
    for tensor in ('freqs', 'Lx', 'PP') :
      T = getattr(self, '_%s' % tensor)
      if not isinstance(T, ndarray) :
        raise ConstructorError('%s must be a valid ndarray' % tensor)

    # if PM and PQ are not available, fill them with zeros
    if self._PM is None :
      self._PM = zeros(self._PP.shape, 'd')
    else :
      if not isinstance(self._PM, ndarray) :
        raise ConstructorError('PM must be a valid ndarray')

    if self._PQ is None :
      self._PQ = zeros(self._PP.shape, 'd')
    else :
      if not isinstance(self._PQ, ndarray) :
        raise ConstructorError('PQ must be a valid ndarray')

    if 3 != len(self._Lx.shape) :
      raise InvalidArgumentError(
        'Displacement vector Lx must be a three-dimensional ndarray.')

    if 1 != len(self._freqs.shape) or \
       self._freqs.shape[0] != self._Lx.shape[0] :
      raise ConstructorError(
        'Frequencies list must be an one-dimensional one-based ndarray')

    if 4 != len(self._PP.shape) or self._PP.shape != self._PM.shape or \
       self._PP.shape != self._PQ.shape :
      raise ConstructorError(
        'Polarizability, G & A tensor gradients must have the same dimension!')

    if self._Lx.shape[1] != self._PP.shape[0] :
      raise ConstructorError(
        'Number of atoms must be the same for the displacements and tensors.')

  def _declare_properties(self) :
    """Declate properties of the class."""
    # for convenience create a variable for the number
    # of atoms and frequencies
    self._Natoms = self._PP.shape[0] - 1
    self._NFreq  = len(self._freqs)  - 1
    
    prop_list = ('Natoms', 'NFreq', 'Lx', 'freqs',
                 'PP', 'PM', 'PQ',
                 'lambda_incident', 'A')
    for prop in prop_list :
      self._add_property(prop, readonly=True)

  def __calc_V(self) :
    """Calculate all V-tensors.

    Dimension of a V-tensor is (4, 1+Natoms, 4, 1+Natoms, 4).
    It can be decomposed in isotropic, anisotropic and antisymmetric parts.
    
    """
    # coefficient for the beta^2_A invariant (omega_0 / 2)
    coeff = 45.563350 / self._lambda_incident * 0.5

    # V tensors in atomic units
    shape_V     = (1 + self._Natoms, 4, 1 + self._Natoms, 4)
    V_a2  = zeros(shape_V, 'd')
    V_b2  = zeros(shape_V, 'd')
    V_aG  = zeros(shape_V, 'd')
    V_b2G = zeros(shape_V, 'd')
    V_b2A = zeros(shape_V, 'd')

    PP = self._PP
    PM = self._PM
    PQ = self._PQ

    for a in xrange(1, 1 + self._Natoms) :
      for b in xrange(1, 1 + self._Natoms) :
        for i in xrange(1, 4) :
          for j in xrange(1, 4) :
            for mu in xrange(1, 4):
              for nu in xrange(1, 4):
                V_a2[a, i, b, j]  += PP[a, i, mu, mu] * PP[b, j, nu, nu]
                V_b2[a, i, b, j]  += 3 * PP[a, i, mu, nu] * PP[b, j, mu, nu] - \
                                     PP[a, i, mu, mu] * PP[b, j, nu, nu]
                V_aG[a, i, b, j]  += PP[a, i, mu, mu] * PM[b, j, nu, nu]
                V_b2G[a, i, b, j] += 3 * PP[a, i, mu, nu] * PM[b, j, mu, nu] - \
                                     PP[a, i, mu, mu] * PM[b, j, nu, nu]
                V_b2A[a, i, b, j] += PP[a, i, mu, nu] * PQ[b, j, mu, nu]

            V_a2[a, i, b, j]  /= 9.
            V_b2[a, i, b, j]  /= 2.
            V_aG[a, i, b, j]  /= 9.
            V_b2G[a, i, b, j] /= 2.
            V_b2A[a, i, b, j] *= coeff

    # save in the internal variable
    # decompose to the parts
    shape_V_all = (4,) + shape_V

    for V in LIST_VTENSORS :
      # create an entry
      self.__data[V] = zeros(shape_V_all, 'd')

      # fill it
      self.__data[V][0]  = eval(V)
      self.__data[V][1:] = decompose_t(self.__data[V][0])

  def __get_V(self, V, i) :
    """Return a V-tensor.

    Positional arguments :
    V -- V-tensor, one of ('V_a2', 'V_b2', 'V_aG', 'V_b2G', 'V_b2A')
    i -- part of the decomposed tensor
         possible values :  
         0 : total sum
         1 : isotropic part
         2 : anisotropic part
         3 : antisymmetric part

    """
    if V not in LIST_VTENSORS :
      raise InvalidArgumentError('V must be one of %s, got %s' % \
                                 (str(LIST_VTENSORS), str(V)))

    if i not in xrange(4) :
      raise InvalidArgumentError('i must be in range 0-3, got %s' % str(i))

    # calculate the V tensors if necessary
    if V not in self.__data :
      self.__calc_V()

    return self.__data[V][i]

  def __calc_Jp(self, p) :
    """Calculate the invariants for a given vibration p.

    Positional arguments :
    p -- number of vibration

    Dimension of an invariant is (4, 1 + Natoms, 1 + Natoms).
    Units : atomic units.
    It can be decomposed in isotropic, anisotropic and antisymmetric parts.
    
    """
    if p not in xrange(1, 1 + self._NFreq) :
      raise InvalidArgumentError('Invalid number of vibration: %s' % str(p))
    
    # V tensors must be calculated.
    if 'V_a2' not in self.__data :
      self.__calc_V()
    
    LxLx_p_dec = decompose_t(create_dyad(self._Lx[p]))

    shape_Jp     = (4, 1 + self._Natoms, 1 + self._Natoms)

    # creating entries (J, p) for each invariant J
    for J in LIST_INVARIANTS :
      self.__data[(J, p)] = zeros(shape_Jp, 'd')

      V_dec = self.__data['V_%s' % J]

      # iterating through parts
      for i in xrange(1, 4) :
        # iterating through diatomic terms
        for a in xrange(1, 1 + self._Natoms) :
          for b in xrange(1, 1 + self._Natoms) :
            self.__data[(J, p)][i, a, b]    = contract(
                V_dec[i, a, :, b, :], LxLx_p_dec[i-1][a, :, b, :])
        
      self.__data[(J, p)][0] = self.__data[(J, p)][1] + \
                               self.__data[(J, p)][2] + self.__data[(J, p)][3]

  def __get_Jp(self, J, p, i, units) :
    """Get the matrix of an invariant J.

    Positional arguments :
    J     -- molecular invariant
             one of ('a2', 'b2', 'aG', 'b2G', 'b2A')
    p     -- number of vibration
    i     -- part of the decomposed tensor
             possible values :  
             0 : total sum
             1 : isotropic part
             2 : anisotropic part
             3 : antisymmetric part
    units -- units of the V-tensor
             one of ('invariant', 'cross-section', 'A^4/AMU')

    """
    if J not in LIST_INVARIANTS :
      raise InvalidArgumentError('J must be one of %s, got %s' % \
                                 (str(LIST_INVARIANTS), str(J)))

    if i not in xrange(4) :
      raise InvalidArgumentError('i must be in range 0-3, got %s' % str(i))
    
    if units not in LIST_INVARIANTSUNITS :
      raise InvalidArgumentError('units must be one of %s, got %s' % \
                                 (str(LIST_INVARIANTSUNITS), str(units)))

    # calculate the invariants for the given p if necessary
    if (J, p) not in self.__data :
      self.__calc_Jp(p)

    # choose the appropriate numerical factor
    factor = conv_units_raman_roa(units, self._lambda_incident, \
                                  self._freqs[p], J)

    return factor * self.__data[(J, p)][i]

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'RamanROATensors(%s, %s, %s, %s, %s, %s, A=%s)' % \
           (repr(self._PP),
            repr(self._PM),
            repr(self._PQ),
            repr(self._Lx),
            repr(self._freqs),
            repr(self._lambda_incident),
            repr(self._A))
  
  def V_a2(self, i=0) :
    """Calculate the V-tensor for the a2 molecular invariant.
    
    Keyword arguments :
    i -- part of the decomposed tensor (default 0, i.e. total sum)
         possible values :  
         0 : total sum
         1 : isotropic part
         2 : anisotropic part
         3 : antisymmetric part

    The tensor is expressed in a.u.
    
    """
    return self.__get_V('V_a2', i)

  def V_b2(self, i=0) :
    """Calculate the V-tensor for the b2 molecular invariant.
    
    Keyword arguments :
    i -- part of the decomposed tensor (default 0, i.e. total sum)
         possible values :  
         0 : total sum
         1 : isotropic part
         2 : anisotropic part
         3 : antisymmetric part

    The tensor is expressed in a.u.
    
    """
    return self.__get_V('V_b2', i)

  def V_aG(self, i=0) :
    """Calculate the V-tensor for the aG molecular invariant.
    
    Keyword arguments :
    i -- part of the decomposed tensor (default 0, i.e. total sum)
         possible values :  
         0 : total sum
         1 : isotropic part
         2 : anisotropic part
         3 : antisymmetric part

    The tensor is expressed in a.u.
    
    """
    return self.__get_V('V_aG', i)

  def V_b2G(self, i=0) :
    """Calculate the V-tensor for the b2G molecular invariant.
    
    Keyword arguments :
    i -- part of the decomposed tensor (default 0, i.e. total sum)
         possible values :  
         0 : total sum
         1 : isotropic part
         2 : anisotropic part
         3 : antisymmetric part

    The tensor is expressed in a.u.
    
    """
    return self.__get_V('V_b2G', i)

  def V_b2A(self, i=0) :
    """Calculate the V-tensor for the b2A molecular invariant.
    
    Keyword arguments :
    i -- part of the decomposed tensor (default 0, i.e. total sum)
         possible values :  
         0 : total sum
         1 : isotropic part
         2 : anisotropic part
         3 : antisymmetric part

    The tensor is expressed in a.u.
    
    """
    return self.__get_V('V_b2A', i)

  def a2(self, p, i=0, units='invariant') :
    """Calculate the a2 molecular invariant.

    Positional arguments :
    p     -- number of vibration

    Keyword arguments :
    i     -- part of the decomposed invariant (default 0, i.e. total sum)
             possible values :  
             0 : total sum
             1 : isotropic part
             2 : anisotropic part
             3 : antisymmetric part
    units -- units of the V-tensor (default 'invariant')
             one of ('invariant', 'cross-section', 'A^4/AMU')

    """
    return self.__get_Jp('a2', p, i, units)

  def b2(self, p, i=0, units='invariant') :
    """Calculate the b2 molecular invariant.

    Positional arguments :
    p     -- number of vibration

    Keyword arguments :
    i     -- part of the decomposed invariant (default 0, i.e. total sum)
             possible values :  
             0 : total sum
             1 : isotropic part
             2 : anisotropic part
             3 : antisymmetric part
    units -- units of the V-tensor (default 'invariant')
             one of ('invariant', 'cross-section', 'A^4/AMU')

    """
    return self.__get_Jp('b2', p, i, units)


  def aG(self, p, i=0, units='invariant') :
    """Calculate the aG molecular invariant.

    Positional arguments :
    p     -- number of vibration

    Keyword arguments :
    i     -- part of the decomposed invariant (default 0, i.e. total sum)
             possible values :  
             0 : total sum
             1 : isotropic part
             2 : anisotropic part
             3 : antisymmetric part
    units -- units of the V-tensor (default 'invariant')
             one of ('invariant', 'cross-section', 'A^4/AMU')

    """
    return self.__get_Jp('aG', p, i, units)


  def b2G(self, p, i=0, units='invariant') :
    """Calculate the b2G molecular invariant.

    Positional arguments :
    p     -- number of vibration

    Keyword arguments :
    i     -- part of the decomposed invariant (default 0, i.e. total sum)
             possible values :  
             0 : total sum
             1 : isotropic part
             2 : anisotropic part
             3 : antisymmetric part
    units -- units of the V-tensor (default 'invariant')
             one of ('invariant', 'cross-section', 'A^4/AMU')

    """
    return self.__get_Jp('b2G', p, i, units)

  def b2A(self, p, i=0, units='invariant') :
    """Calculate the b2A molecular invariant.

    Positional arguments :
    p     -- number of vibration

    Keyword arguments :
    i     -- part of the decomposed invariant (default 0, i.e. total sum)
             possible values :  
             0 : total sum
             1 : isotropic part
             2 : anisotropic part
             3 : antisymmetric part
    units -- units of the V-tensor (default 'invariant')
             one of ('invariant', 'cross-section', 'A^4/AMU')

    """
    return self.__get_Jp('b2A', p, i, units)

  def J_all(self, units='invariant') :
    """Calculate the five molecular invariants for all vibrations.

    A row is made up of a2, b2, aG, b2G and b2A.

    Keyword arguments :
    units -- units of the invariants (default 'invariant')
             one of ('invariant', 'cross-section', 'A^4/AMU', 'reduced')

    Return value is a null-based ndarray with the shape of (NFreq, 5) with
    NFreq being the number of vibrations.
    
    """
    # V tensors should be calculated
    if 'V_a2' not in self.__data :
      self.__calc_V()

    # saving the reduced invariants
    if 'J_all' not in self.__data :
      self.__data['J_all'] = zeros((self._NFreq, 5), 'd')

      for p in xrange(1, 1 + self._NFreq) :
        LxLxp  = create_dyad(self._Lx[p])
        self.__data['J_all'][p-1, :] = [ contract(LxLxp, self.__data[V][0]) \
                                         for V in LIST_VTENSORS ]

    factors = zeros((self._NFreq, 5), 'd')

    for p in xrange(1, 1 + self._NFreq) :
      factors[p-1, :] = [ conv_units_raman_roa(units,
                                               self._lambda_incident,
                                               self._freqs[p], J) \
                          for J in LIST_INVARIANTS ]
   
    return self.__data['J_all'] * factors

  def J_rot(self, Lx_rot) :
    """Calculate the five reduced molecular invariants for the rotations.

    A row is made up of a2, b2, aG, b2G and b2A.

    Return value is a null-based ndarray with the shape of (nrot, 5) with
    nrot being the number of rotations.

    Positional arguments :
    Lx_rot -- rotations
              shape : (nrot, 1 + Natoms, 4)

    Lx_rot can be obtained as follows :
    
    Lx_rot = mol.Lx_tr_rot[1 + mol.nrot:]
             
    """
    if not isinstance(Lx_rot, ndarray) or 3 != len(Lx_rot.shape) or \
       (1 + self._Natoms, 4) != Lx_rot.shape[1:] :
      raise InvalidArgumentError('Invalid rotations supplied')
    
    # V tensors should be calculated
    if 'V_a2' not in self.__data :
      self.__calc_V()

    # saving the invariants
    if 'J_rot' not in self.__data :
      self.__data['J_rot'] = zeros((Lx_rot.shape[0], 5), 'd')

      for p in xrange(Lx_rot.shape[0]) :
        LxLxp  = create_dyad(Lx_rot[p])
        self.__data['J_rot'][p, :] = [ contract(LxLxp, self.__data[V][0]) \
                                       for V in LIST_VTENSORS ]
   
    return self.__data['J_rot']

  def acp(self, item, p) :
    """Generate atomic contribution patterns (ACPs).

    See also make_acp().

    Positional arguments :
    item -- moleculular invariant or a cross-section
            one of ('raman', 'roa_backward', 'roa_forward',
                    'a2', 'b2', 'aG', 'b2G', 'b2A')            
    p    -- number of vibration

    The ACPs have units of the cross-sections.
    """
    Lx_p = self._Lx[p]
    units = 'cross-section'
    
    if 'raman' == item :
      coeffs = inv_coeffs_raman_roa(0)
      
      a2 = self.a2(p, 0, units=units)
      b2 = self.b2(p, 0, units=units)

      acp = coeffs[0] * ( coeffs[1] * make_acp(a2, Lx_p, self.V_a2()) + \
                          coeffs[2] * make_acp(b2, Lx_p, self.V_b2()) )

    elif 'roa_backward' == item :
      coeffs = inv_coeffs_raman_roa(0)
      
      b2G = self.b2G(p, 0, units=units)
      b2A = self.b2A(p, 0, units=units)

      acp = coeffs[3] * ( coeffs[5] * make_acp(b2G, Lx_p, self.V_b2G()) + \
                          coeffs[6] * make_acp(b2A, Lx_p, self.V_b2A()) )

    elif 'roa_forward' == item :
      coeffs = inv_coeffs_raman_roa(1)
      
      aG  = self.aG(p, 0, units=units)
      b2G = self.b2G(p, 0, units=units)
      b2A = self.b2A(p, 0, units=units)

      acp = coeffs[3] * ( coeffs[4] * make_acp(aG, Lx_p, self.V_aG()) + \
                          coeffs[5] * make_acp(b2G, Lx_p, self.V_b2G()) + \
                          coeffs[6] * make_acp(b2A, Lx_p, self.V_b2A()) )

    else :
      J = eval('self.%s(p=%d,i=0,units=\'invariant\')' % (item, p))
      V = eval('self.V_%s(i=0)' % item)

      acp = make_acp(J, Lx_p, V)
      
    return acp

  def intensities(invars, scattering) :
    """Calculate the Raman/ROA intensities.

    Positional arguments :
    invars     -- array with the five invariants (ndarray)
                  shape : (5,)
    scattering -- scattering type (see inv_coeffs_raman_roa())

    """
    if not isinstance(invars, ndarray) or 5 != invars.shape[0] :
      raise InvalidArgumentError('Invalid invariants array')

    coeffs    = inv_coeffs_raman_roa(scattering)

    raman_int = coeffs[0] * (coeffs[1] * invars[0] + coeffs[2] * invars[1])
    roa_int   = coeffs[3] * (coeffs[4] * invars[2] + coeffs[5] * invars[3] + \
                             coeffs[6] * invars[4])

    return (raman_int, roa_int)

  intensities = staticmethod(intensities)

  def norm_sum_vib(self, scattering=0, start_p=1, end_p=None) :
    """Calculate the normalized sum of ROA over the vibrations.

    It is a measure of the influence of the chiral distribution of a molecule's
    electrons on vibrational ROA alone.

    See eq 34 in W. Hug and J. Haesler. Int. J. Quant. Chem. 104:695-715, 2005.

    Keyword arguments :
    scattering -- scattering type (see inv_coeffs_raman_roa()) (default 0)
    start_p    -- start vibration (default 1)
    end_p      -- end vibration (default None)
                  use None to specify the last
    
    """
    if start_p not in xrange(1, 1 + self._NFreq) :
      raise InvalidArgumentError('Invalid start vibration number')

    if end_p is not None :
      if end_p not in xrange(1, 1 + self._NFreq) :
        raise InvalidArgumentError('Invalid end vibration number')
    else :
      end_p = self._NFreq

    if start_p > end_p :
      start_p, end_p = end_p, start_p
          
    # calculating the reduced invariants
    roa_vals = stick_raman_roa(scattering, self.J_all(units='reduced'))[1]

    sum_numer = roa_vals[start_p-1:end_p].sum()
    sum_denom = abs(roa_vals).sum()

    if 0. == sum_denom :
      raise DataInconsistencyError(
        'norm_sum_vib() : sum over the vibrations is 0.!')

    return sum_numer / sum_denom

  def norm_sum_rot(self, masses, scattering=0) :
    """Calculate the normalized sum of ROA over the rotations.

    See eq 33 in W. Hug and J. Haesler. Int. J. Quant. Chem. 104:695-715, 2005.

    Positional arguments :
    masses     -- masses of the atoms in AMU (one-based ndarray)
                  shape : (1 + Natoms,)

    Keyword arguments :
    scattering -- scattering type (see inv_coeffs_raman_roa()) (default 0)
        
    """
    roa_vals = stick_raman_roa(scattering, self.J_all(units='reduced'))[1]

    sum_vib   = roa_vals.sum()
    sum_denom = abs(roa_vals).sum()

    if 0. == sum_denom :
      raise DataInconsistencyError(
        'norm_sum_rot() : sum over the vibrations is 0.!')    

    # summing the V-tensors
    V_aG, V_b2G, V_b2A = self.V_aG(), self.V_b2G(), self.V_b2A()
    
    coeffs = inv_coeffs_raman_roa(scattering=scattering)
  
    V_sum = coeffs[3] * (coeffs[4] * V_aG + coeffs[5] * V_b2G + \
                         coeffs[6] * V_b2A)
    sum_v_alpha = 0.
    for a in xrange(1, 1 + self._Natoms) :
      for i in xrange(1, 4) :
        sum_v_alpha += V_sum[a, i, a, i] / (masses[a] * AMU2AU)

    return (sum_v_alpha - sum_vib) / sum_denom
    

class IRVCDTensors(PropertiesContainer) :
  """Class for manipulating the IR/VCD tensors.

  For details refer to W. Hug and J. Haesler. Int. J. Quant. Chem. 104:695-715,
  2005

  Refer to the DALTON manual page for information on how to request a VCD job.
  http://www.kjemi.uio.no/software/dalton/resources/dalton20manual.pdf

  The following read-only properties are exposed :
      Natoms              -- number of atoms
      NFreq               -- number of vibrations
      Lx                  -- cartesian excursions for the vibrations
      freqs               -- wavenumbers of vibrations in ascending order
      P                   -- gradients of the electric dipole moment (APTs)
      M                   -- gradients of the magnetic dipole moment (AATs)
      V_D                 -- dyadics for the dipole strength
      V_R                 -- dyadics for the rotational strength

  The following public methods are exported :
      D()                 -- reduced dipole strength in a.u.
      R()                 -- reduced rotational strength in a.u.
      fit_spectra()       -- generate the IR/VCD/g in the curve representation
      integrated_coeffs() -- integrated absorbtion coefficients and g-factor
      norm_sum_vib()      -- normalized sum of VCD over the vibrations
      norm_sum_rot()      -- normalized sum of VCD over the rotations
      
  """

  def __init__(self, P, M, Lx, freqs) :
    """
    Constructor of the class.

    P, Lx and freqs are required to be set.
    If M is not set, it will be filled with zeros.    

    Positional arguments :
    P     -- gradients of the electric dipole moment (one-based ndarray)             
             known in the VCD literature also as atomic polar tensors (APTs)
             shape : (1 + Natoms, 4, 4) with Natoms being the number of atoms
    M     -- gradients of the magnetic dipole moment (one-based ndarray)
             known in the VCD literature also as atomic axial tensors (AATs)
             shape : (1 + Natoms, 4, 4) with Natoms being the number of atoms
    Lx    -- cartesian excursions for the vibrations (one-based ndarray)
             shape : (1 + NFreq, 1 + Natoms, 4) with NFreq being the number of
             vibrations
    freqs -- wavenumbers of vibrations in ascending order (one-based ndarray)
             shape : (1 + NFreq,)
    """
    self._P     = P
    self._M     = M
    self._Lx    = Lx 
    self._freqs = freqs
  
    # internal dictionary to store the calculated data
    self.__data = {}

    PropertiesContainer.__init__(self, modulename='pyviblib.calc.spectra')

  def _check_consistency(self) :
    """Check the consistency of the input data.

    An exception is raised should an inconsistency be found.
    
    """
    # the following data must be available
    for tensor in ('P', 'Lx', 'freqs') :
      T = getattr(self, '_%s' % tensor)
      if not isinstance(T, ndarray) :
        raise ConstructorError('%s must be a valid ndarray' % tensor)

    # if M is not available, fill it with zeros
    if self._M is None :
      self._M = zeros(self._P.shape, 'd')
    else :
      if not isinstance(self._M, ndarray) :
        raise ConstructorError('M must be a valid ndarray')      

    if 3 != len(self._Lx.shape) :
      raise ConstructorError(
          'Displacement vector Lx must be a three-dimensional ndarray')

    if 1 != len(self._freqs.shape) or \
       self._freqs.shape[0] != self._Lx.shape[0] :
      raise ConstructorError(
          'Frequencies list must be an one-dimensional one-based ndarray')

    if 3 != len(self._P.shape) or self._P.shape != self._M.shape:
      raise ConstructorError('The tensors must have the same dimension!')

    if self._Lx.shape[1] != self._P.shape[0] :
      raise ConstructorError(
        'Number of atoms must be the same for the displacements and tensors.')

  def _declare_properties(self) :
    """Declare properties of the class."""
    # for convenience create a variable for the number of atoms and frequencies
    self._Natoms = self._P.shape[0] - 1
    self._NFreq  = len(self._freqs) - 1
    
    prop_list = ('Natoms', 'NFreq', 'Lx', 'freqs', 'P', 'M')
    for prop in prop_list :
      self._add_property(prop, readonly=True)
      
    # V tensors for IR and VCD
    self.__class__.V_D = property(fget=Command(self.__get_V, 'V_D'))
    self.__class__.V_R = property(fget=Command(self.__get_V, 'V_R'))

  def __calc_V(self) :
    """Calculate the V-tensors for IR and VCD."""
    # V tensors in atomic units
    shape_V     = (1 + self._Natoms, 4, 1 + self._Natoms, 4)

    # IR - V_D, VCD - V_R
    V_D = zeros(shape_V, 'd')
    V_R = zeros(shape_V, 'd')

    # go    
    for a in xrange(1, 1 + self._Natoms) :
      for b in xrange(1, 1 + self._Natoms) :
        for i in xrange(1, 4) :
          for j in xrange(1, 4) :
            for mu in xrange(1, 4):
              V_D[a, i, b, j]  += self._P[a, i, mu] * self._P[b, j, mu]
              V_R[a, i, b, j]  += self._P[a, i, mu] * self._M[b, j, mu]

    # save it
    self.__data['V_D'] = V_D
    self.__data['V_R'] = V_R

  def __calc_inv_p(self, p) :
    """Calculate the reduced dipole and rotational strengths in a.u.

    Positional arguments :
    p -- number of vibration.

    """
    if 'V_D' not in self.__data :
      self.__calc_V()
      
    V_D = self.__data['V_D']
    V_R = self.__data['V_R']

    #
    L_p = self._Lx[p]
    D_p = zeros((1 + self._Natoms, 1 + self._Natoms), 'd')
    R_p = zeros(D_p.shape, 'd')
  
    for a in xrange(1, 1 + self._Natoms) :
      for b in xrange(1, 1 + self._Natoms) :
        D_p[a, b] = dot(dot(L_p[a], V_D[a, :, b, :]), L_p[b])
        R_p[a, b] = dot(dot(L_p[a], V_R[a, :, b, :]), L_p[b])

    self.__data[('D', p)] = D_p
    self.__data[('R', p)] = R_p

  def __calc_strengths(self) :
    """Calculate the dipole and rotational strengths in SI.

    The result is saved internally as a ndarray with a shape of (NFreq, 2).
    
    """
    if 'strengths' in self.__data :
      return
          
    V_D = self.__get_V('V_D')
    V_R = self.__get_V('V_R')

    # result
    self.__data['strengths'] = zeros((self._NFreq, 2), 'd')

    for p in xrange(1, 1 + self._NFreq) :
      L_p  = self._Lx[p]
      freq = self._freqs[p]

      # hbar divided by 2 omega in a.u. (for D)
      h_2omega_au = 1./(2.*(freq*INVCM2AU))

      # dipole and rotational strengths in a.u
      D_p_au = 0.
      R_p_au = 0.
      
      for a in xrange(1, 1 + self._Natoms) :
        for b in xrange(1, 1 + self._Natoms) :
          D_p_au += dot(dot(L_p[a], V_D[a, :, b, :]), L_p[b])
          R_p_au += dot(dot(L_p[a], V_R[a, :, b, :]), L_p[b])
            
      D_p_au *= h_2omega_au

      self.__data['strengths'][p - 1] = (D_p_au * DIPSTRENGTH2SI, \
                                         R_p_au * ROTSTRENGTH2SI)

  def __get_V(self, *args) :
    """Return the V-tensor for IR or VCD.

    The last positional argument is the type of the V-tensor.
    It must be one of ('V_D', 'V_R').
    
    """
    if 0 == len(args) :
      raise InvalidArgumentError('At least one argument must be supplied')

    V = args[-1]
    if V not in ('V_D', 'V_R') :
      raise InvalidArgumentError('Invalid tensor : %s' % str(V))
    
    if V not in self.__data :
      self.__calc_V()

    return self.__data[V]    

  def __get_inv_p(self, invar, p) :
    """Return the reduced dipole or rotational strength.

    Positional arguments :
    invar -- 'D' or 'R'
    p     -- number of vibration.
    
    """
    if invar not in ('D', 'R') :
      raise InvalidArgumentError('Invalid invariant : %s' % str(invar))
    
    if (invar, p) not in self.__data :
      self.__calc_inv_p(p)

    return self.__data[(invar, p)]

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'IRVCDTensors(%s, %s, %s, %s)' % \
           (repr(self._P),
            repr(self._M),
            repr(self._Lx),
            repr(self._freqs))

  def D(self, p) :
    """Calculate the reduced dipole strength.

    Positional arguments :
      p -- number of vibration

    Returned value is expressed in a.u.
    
    """
    return self.__get_inv_p('D', p)

  def R(self, p) :
    """Calculate the reduced rotational strength.

    Positional arguments :
      p -- number of vibration

    Returned value is expressed in a.u.
    
    """
    return self.__get_inv_p('R', p)

  def integrated_coeffs(self) :
    """Get the integrated absorption coeffcients (in SI) and the g-factor.

    The shape of the bands is considered to be Lorentzian.
    
    See Atkins, 6th edition, p. 459.

    Return a ndarray with a shape of (NFreq, 3).
    
    """
    if 'strengths' not in self.__data :
      self.__calc_strengths()
      
    ans = zeros((self._NFreq, 3), 'd')
    
    for p in xrange(1, 1 + self._NFreq) :
      # strengths
      dipstr, rotstr = self.__data['strengths'][p - 1]

      # boltzmann factor
      KBoltz_p = boltzmann_factor(self._freqs[p])

      a_eps  = DIPSTRENGTH2EPSILON  * dipstr * self._freqs[p] * KBoltz_p * 100.
      a_deps = ROTSTRENGTH2DEPSILON * rotstr * self._freqs[p] * KBoltz_p * 100.
      g      = a_deps / a_eps

      ans[p-1] = (a_eps, a_deps, g)

    return ans

  def fit_spectra(self, ngauss=6, fwhm_fit=8.0, fwhm_inst=8.0, \
                  startx=None, endx=None) :
    """Generate the IR/VCD spectra as curves.

    Refer to W. Hug and J. Haesler. Int. J. Quant. Chem. 104:695-715, 2005

    Keyword arguments :
    scattering -- scattering type (see inv_coeffs_raman_roa())
    ngauss     -- number of Gauss functions (default 6)
    fwhm_fit   -- full width at half maximum for the bandwidthes (default 8.)
    fwhm_inst  -- full width at half maximum for the Gaussian instrument profile
                  (default 8.0)
    startx     -- start wavenumber of the fitting interval (default None)
    endx       -- end wavenumbers of the fitting interval (default None)
                  if the latter two keyword arguments are None, they are
                  generated automatically

    Return X, eps_Y, deps_Y, g_Y

    """
    # strengths must be calculated
    if 'strengths' not in self.__data :
      self.__calc_strengths()
    
    # step is always 1. cm**(-1)
    if startx is None and endx is None :
      startx = max(0., ceil(self._freqs[1] - X_PEAK_INTERVAL))
      endx   = ceil(self._freqs[-1] + X_PEAK_INTERVAL)

    X = arange(startx, 1. + endx, 1.)

    # result spectra arrays
    eps_Y  = zeros(X.shape, 'd')
    deps_Y = zeros(X.shape, 'd')

    # fit parameter of a Lorentz curve
    fitparams = fitgauss_params(ngauss)

    # bandwidthes
    k_fit   = fwhm_fit / 2.
    b       = fwhm_inst / (2. * sqrt(2. * log(2.)))

    # iterating through all vibrations
    for p in xrange(1, 1 + self._NFreq) :
      freq = self._freqs[p]
      KBoltz_p = boltzmann_factor(freq)

      diprot = self.__data['strengths'][p - 1]

      # intensities
      eps_p  = diprot[0] * DIPSTRENGTH2EPSILON  * KBoltz_p
      deps_p = diprot[1] * ROTSTRENGTH2DEPSILON * KBoltz_p
      
      # fitting interval for the current peak
      x0 = max(ceil(freq - X_PEAK_INTERVAL), startx)
      x1 = min(ceil(freq + X_PEAK_INTERVAL), endx)

      # indices in the X array
      # WARNING : works with the step of 1.0 *only* !
      i0 = int(x0 - startx)
      i1 = int(x1 - startx)

      # approximating
      x_cur = arange(x0, 1. + x1, 1.) - freq
      conv  = voigt_norm(x_cur, ngauss, fitparams, k_fit, b)

      eps_Y[i0:1+i1]  += eps_p  * conv
      deps_Y[i0:1+i1] += deps_p * conv

    # finally multiplying with wavenumbers
    eps_Y  *= X
    deps_Y *= X

    # g
    g_Y = deps_Y / (0.001 + eps_Y)
    
    return X, eps_Y, deps_Y, g_Y

  def norm_sum_vib(self, start_p=1, end_p=None) :
    """Calculate the normalized sum of VCD over the vibrations.

    Keyword arguments :
    start_p    -- start vibration (default 1)
    end_p      -- end vibration (default None)
                  use None to specify the last

    """
    if start_p not in xrange(1, 1 + self._NFreq) :
      raise InvalidArgumentError('Invalid start vibration number')

    if end_p is not None :
      if end_p not in xrange(1, 1 + self._NFreq) :
        raise InvalidArgumentError('Invalid end vibration number')
    else :
      end_p = self._NFreq

    if start_p > end_p :
      start_p, end_p = end_p, start_p
          
    if 'strengths' not in self.__data :
      self.__calc_strengths()

    rotstr = self.__data['strengths'][:, 1]

    sum_numer = rotstr[start_p-1:end_p].sum()
    sum_denom = abs(rotstr).sum()

    if 0. == sum_denom :
      raise DataInconsistencyError(
        'norm_sum_vib() : sum over the vibrations is 0.!')

    return sum_numer / sum_denom

  def norm_sum_rot(self, masses) :
    """Calculate the normalized sum of VCD over the rotations.

    Positional arguments :
    masses     -- masses of the atoms in AMU (one-based ndarray)
                  shape : (1 + Natoms,)

    """          
    if 'strengths' not in self.__data :
      self.__calc_strengths()

    # rotational strengths are given is SI => recalculating in a.u.
    rotstr = self.__data['strengths'][:, 1] / ROTSTRENGTH2SI

    sum_numer = rotstr.sum()
    sum_denom = abs(rotstr).sum()

    if 0. == sum_denom :
      raise DataInconsistencyError(
        'norm_sum_vib() : sum over the vibrations is 0.!')

    V_R = self.V_R

    sum_v_alpha = 0.
    for a in xrange(1, 1 + self._Natoms) :
      for i in xrange(1, 4) :
        sum_v_alpha += V_R[a, i, a, i] / (masses[a] * AMU2AU)    

    return (sum_v_alpha - sum_numer) / sum_denom


class ExpRamanROAData(PropertiesContainer) :
  """Storing experimental Raman, ROA or Degree of circularity spectra.

  The following read-only properties are exposed :
      filename      -- file name
      laser_power   -- laser power (mW)
      exposure_time -- exposure time (min)
      datatype      -- see resources.STRINGS_EXPSPECTRA_TYPES
      scattering    -- see resources.STRINGS_SCATTERING_TYPES
      wavenumbers   -- wavenumbers
      raman         -- raman
      roa           -- roa
      degcirc       -- degree of circularity
      
  """

  def __init__(self, filename,
               laser_power, exposure_time, datatype, scattering) :
    """Constructor of the class.

    Positional arguments :
    filename      -- file name
    laser_power   -- laser power (mW)
    exposure_time -- exposure time (min)
    datatype      -- see resources.STRINGS_EXPSPECTRA_TYPES
    scattering    -- see resources.STRINGS_SCATTERING_TYPES
    
    """
    self._filename = filename
    self._laser_power = laser_power
    self._exposure_time = exposure_time
    self._datatype = datatype
    self._scattering = scattering

    # process the file
    self.__process()
    
    PropertiesContainer.__init__(self, modulename='pyviblib.calc.spectra')

  def _check_consistency(self) :
    """Checking the input data."""
    if 0. >= self._laser_power :
      raise ConstructorError('Invalid laser_power argument')

    if 0. >= self._exposure_time :
      raise ConstructorError('Invalid exposure_time argument')

    import pyviblib.gui.resources
    if self._datatype not in pyviblib.gui.resources.STRINGS_EXPSPECTRA_TYPES :
      raise ConstructorError('Invalid datatype argument')

    if self._scattering not in pyviblib.gui.resources.STRINGS_SCATTERING_TYPES :
      raise ConstructorError('Invalid scattering argument')

  def _declare_properties(self) :
    """Declare properties."""
    for prop in ('filename', 'laser_power', 'exposure_time',
                 'datatype', 'scattering',
                 'wavenumbers', 'raman', 'roa', 'degcirc') :
      self._add_property(prop, readonly=True)

  def __process(self) :
    """Parse the file and create the raman, roa and degcirc attributes."""
    parser_ = pyviblib.io.parsers.NumericDataFileParser(self._filename, ncols=3)

    if 0 == parser_.data.shape[0] :
      raise DataInconsistencyError('The file %s is empty' % \
                                   repr(self._filename))
    
    self._wavenumbers = parser_.data[:, 0]
    if 'Raman/ROA' == self._datatype :
      self._raman       = parser_.data[:, 1]
      self._roa         = parser_.data[:, 2]
      self._degcirc     = None
    # Degree of circularity
    else :
      self._raman       = None
      self._roa         = None
      self._degcirc     = parser_.data[:, 2] / parser_.data[:, 1]

  def __str__(self) :
    """Details."""
    return '%s @ %.0f mW (%.2f min)' % \
           (os.path.realpath(self._filename),
            self._laser_power,
            self._exposure_time)

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'ExpRamanROAData(%s, %s, %s, %s, %s)' % \
           (repr(self._filename),
            repr(self._laser_power),
            repr(self._exposure_time),
            repr(self._datatype),
            repr(self._scattering))
