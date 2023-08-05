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

"""Module for handling molecules.

The following classes are exported :
    Atom      --  describing atoms
    Bond      --  describing bonds
    Molecule  --  describing molecules

"""
__author__ = 'Maxim Fedorovsky'

from  math  import sqrt
from  numpy import ndarray, zeros, array, any

from pyviblib.io              import parsers
from pyviblib.calc            import vibrations, spectra
from pyviblib.calc.common     import distance, angle, dihedral, \
                                     orthogonalize_set, normalize_set
from pyviblib.util.exceptions import InvalidArgumentError, ConstructorError
from pyviblib.util.constants  import AMU2AU
from pyviblib.util.pse        import Element
from pyviblib.util.misc       import Command

__all__ = ['Atom', 'Bond', 'Molecule']


class Atom(object) :
  """Class for describing atoms.

  An atom can be a part of a bond.

  The following read-only properties are exposed :
      index   -- one-based index of the atom
      coord   -- coordinates of the atom (one-based ndarray)
      element -- element for the atom (pyviblib.util.pse.Element)
      
  """
  
  def __init__(self, index, coord, element) :
    """Constructor of the class.

    Positional arguments :
    index   -- one-based index of the atom
    coord   -- coordinates of the atom (one-based ndarray)
    element -- element for the atom (pyviblib.util.pse.Element)
    
    """
    if 0 >= index :
      raise ConstructorError('Atom index must start by 1')

    if not isinstance(coord, ndarray) or 1 != len(coord.shape) :
      raise ConstructorError('Invalid coord argument')

    if not isinstance(element, Element) :
      raise ConstructorError('Invalid element argument')
    
    self._index   = index
    self._coord   = coord
    self._element = element

    # declare properties
    for prop in ('index', 'coord', 'element') :
      exec 'self.__class__.%s = property(' % prop + \
           r'fget=Command(Command.fget_attr, "_%s"))' % prop


class Bond(object) :
  """Class for describing bonds.

  A bond is made up of two atoms and can be a part of a molecule.

  The following read-only properties are exposed :
      atom1       -- first atom comprising the bond
      atom2       -- second atom comprising the bond
      is_hydrogen -- whether it is a hydrogen bond

  The following public methods are exposed :
      length()
      
  """

  def __init__(self, atom1, atom2, is_hydrogen=False) :
    """Constructor of the class.

    Positional arguments :
    atom1   -- first atom comprising the bond (Atom)
    atom2   -- second atom comprising the bond (Atom)

    Keyword arguments :
    is_hydrogen -- whether it is a hydrogen bond (default False)
    
    """
    if not isinstance(atom1, Atom) or not isinstance(atom2, Atom) :
      raise ConstructorError('Invalid atom1 or/and atom2 parameter(s)')
    
    self._atom1       = atom1
    self._atom2       = atom2
    self._is_hydrogen = is_hydrogen

    # declare properties
    for prop in ('atom1', 'atom2', 'is_hydrogen') :
      exec 'self.__class__.%s = property(' % prop + \
           r'fget=Command(Command.fget_attr, "_%s"))' % prop

  def __str__(self) :
    """Text description of the bond."""  
    return 'Bond between atoms # %d and % d' % \
           (self._atom1.index, self._atom2.index)

  def length(self) :
    """Calculate the bond length."""
    return distance(self._atom1.coord, self._atom2.coord)


class Molecule(object) :
  """Class for describing molecules.

  A molecule consists of atoms and bonds.
  The bonds can be automatically generated from the cartesian coordinates of
  the atoms.

  The following read-only properties are exposed :
      parser            -- parser object used to create the molecule
      elements          -- elements for the atoms
                           (one-based list of pyviblib.util.pse.Element)
      masses            -- masses (a.m.u.) of the atoms (one-based ndarray)
      atoms             -- atoms (null-based list of Atom)
      Natoms            -- number of atoms (int)
      bonds             -- bonds (null-based list of Bond)
      bonds_matrix      -- matrix of the bonds (one-based ndarray)
                           If a bond between atoms a and b exists, then
                           bonds_matrix[a, b] = 1
      nrot              -- number of rotational degrees of freedom (int)
                           
      the properties below are set if the normal modes are available :
      (tr/rot is an abbreviated form of translations/rotations)
      
      NFreq             -- number of frequencies (int, -1 unless set)
      Lx                -- cartesian excursions (one-based ndarray)
                           shape : (1 + NFreq, 1 + Natoms, 4)
      Lx_norm           -- normalized cartesian excursions (one-based ndarray)
                           shape : (1 + NFreq, 1 + Natoms, 4)
      
      L_tr_rot          -- mass-weighted excursions for tr/rot
                           (one-based ndarray)
                           shape : (4 + nrot, 1 + Natoms, 4)
      Lx_tr_rot         -- cartesian excursions for tr/rot
                           (one-based ndarray)
                           shape : (4 + nrot, 1 + Natoms, 4)
      Lx_tr_rot_norm    -- normalized cartesian excursions for tr/rot
                           (one-based ndarray)
                           shape : (4 + nrot, 1 + Natoms, 4)
      hessian           -- hessian (one-based ndarray)
                           shape : (1 + Natoms, 4, 1 + Natoms, 4)

  The following readable and writable properties are exposed :
      coords            -- cartesian coordinates (one-based ndarray)
                           shape : (1 + Natoms, 4)
      name              -- name of the molecule (string)
      raman_roa_tensors -- Raman/ROA tensors (set if the data available)
                           (pyviblib.calc.spectra.RamanROATensors)
      ir_vcd_tensors    -- IR/VCD tensors (set if the data available)
                           (pyviblib.calc.spectra.IRVCDTensors)

      the properties below are set if the normal modes are available :

      freqs             -- wavenumbers of the vibrations in cm**(-1)
                           (one-based ndarray)
      L                 -- mass-weighted excursions (one-based ndarray)
                           shape : (1 + NFreq, 1 + Natoms, 4)

  The following public methods are exposed :
      update_masses()
      distance()
      angle()
      dihedral()
      
  """

  __THRESHOLD_BOND = 0.1

  def __init__(self, parser) :
    """Constructor of the class.

    Positional arguments :
    parser -- parser object
              (subclass of pyviblib.io.parsers.AbstractFileParser)
    
    """
    if isinstance(parser, parsers.AbstractFileParser) :
      # common attributes
      self._parser    = parser
      self._name      = None
      self._coords    = parser.coords
      self._elements  = parser.elements

      # VROA
      self._raman_roa_tensors = None
      self._ir_vcd_tensors    = None

      if hasattr(parser, 'freqs') and hasattr(parser, 'L') :
        self._set_freqs(self, parser.freqs)
        self._set_L(self, parser.L)

      else :
        self._set_freqs(self, None)
        self._set_L(self, None)

      # if hessian is available
      if hasattr(parser, 'hessian') :
        self._hessian = parser.hessian

      else :
        self._hessian = None

      # Raman/ROA      
      if hasattr(parser, 'PP') and hasattr(parser, 'PM') \
         and hasattr(parser, 'PQ') and hasattr(parser, 'lambda_incident') :
        if parser.PP is not None and self._Lx is not None and \
           any(0. != parser.PP) :
          
          # non-contracted A tensor cannot be available for VOAVIEW files
          if hasattr(parser, 'A') :
            A = parser.A
          else :
            A = None
          
          self._raman_roa_tensors = \
                               spectra.RamanROATensors(parser.PP,
                                                       parser.PM,
                                                       parser.PQ,
                                                       self._Lx,
                                                       self._freqs,
                                                       parser.lambda_incident,
                                                       A=A)

      # IR/VCD
      if hasattr(parser, 'P') and hasattr(parser, 'M') :
        if parser.P is not None and self._Lx is not None and \
           any(0. != parser.P) :
          self._ir_vcd_tensors = spectra.IRVCDTensors(parser.P,
                                                      parser.M,
                                                      self._Lx,
                                                      self._freqs)
 
    else :
      raise ConstructorError(
        'parser must be a subclass of pyviblib.io.parsers.AbstractFileParser')
 
    # internal
    self.__create_atoms()
    self.__calc_bonds()
    self.__change_isotops()
    
    self.__declare_properties()

  def __create_atoms(self) :
    """Create a list of atoms."""
    self._Natoms = len(self._elements) - 1    
    self._atoms = [ ]

    for a in xrange(1, 1 + self._Natoms) :
      self._atoms.append( Atom(a, self._coords[a, :], self._elements[a]) )

  def __calc_bonds(self) :
    """Generate bonds from the cartesian coordinates of the atoms."""
    self._bonds        = [ ]
    self._bonds_matrix = zeros( (1 + self._Natoms, 1 + self._Natoms), 'l' )

    # atoms which can be a part of a hydrogen bond
    els_h = ('o', 'n', 'p', 's', 'f')

    for i in xrange(self._Natoms) :
      for j in xrange(1 + i, self._Natoms) :

        d = distance(self._atoms[i].coord, self._atoms[j].coord)

        # usual bond ?
        if ( self._atoms[i].element.r_coval + \
             self._atoms[j].element.r_coval + self.__THRESHOLD_BOND) > d :
          self.__add_bond(i, j, False)

        # hydrogen bond ?
        elif ( ('h' == self._atoms[i].element.symbol.lower() and \
                self._atoms[j].element.symbol.lower() in els_h) or \
               ('h' == self._atoms[j].element.symbol.lower() and \
                self._atoms[i].element.symbol.lower() in els_h) ) and \
             ( 1.6 <= d and 1.99 >=d ) :
          self.__add_bond(i, j, True)

  def __add_bond(self, i, j, is_hydrogen) :
    """Add a bond between atoms with null-based indices i & j."""
    self._bonds.append( Bond(self._atoms[i], self._atoms[j], is_hydrogen) )
    self._bonds_matrix[1 + i, 1 + j] = 1
    self._bonds_matrix[1 + j, 1 + i] = 1

  def _get_masses(obj) :
    """Getter function for the masses property."""
    if not hasattr(obj, '_masses') :
      obj._masses = None
    
    if obj._masses is None :
      obj._masses = array([0.] + [ el.mass for el in obj._elements[1:] ])

    return obj._masses

  _get_masses = staticmethod(_get_masses)

  def __change_isotops(self) :
    """Scan all the atoms and change the diffuse color for non-default isotopes.

    Set the rgb components of the diffuse color to be 25% of the original.
    """
    masses = self._get_masses(self)
    
    for atom in self._atoms :
      if 0 != atom.element.isotopno or \
         0.1 < abs(masses[atom.index] - atom.element.isotopes[0]) :
        diffuse_color = list(atom.element.material.diffuse_color)
        
        atom.element.material.diffuse_color = [ c*0.25 for c in diffuse_color ]

  def __declare_properties(self) :
    """Declare properties of the class."""
    # usual read-only properties
    for ro_prop in ('elements', 'atoms', 'Natoms', 'bonds', 'bonds_matrix',
                    'NFreq', 'Lx', 'Lx_norm', 'nrot',
                    'L_tr_rot', 'Lx_tr_rot', 'Lx_tr_rot_norm', 'hessian',
                    'parser') :
      exec 'self.__class__.%s = property(' % ro_prop + \
           r'fget=Command(Command.fget_attr, "_%s"))' % ro_prop

    # writable properties
    for wr_prop in ('coords', 'name', 'raman_roa_tensors', 'ir_vcd_tensors') :
      exec 'self.__class__.%s = property(' % wr_prop + \
           r'fget=Command(Command.fget_attr, "_%s"),' % wr_prop + \
           r'fset=Command(Command.fset_attr, "_%s"))' % wr_prop

    # other
    self.__class__.masses = property(fget=self._get_masses)
    self.__class__.freqs = property(fget=Command(Command.fget_attr, '_freqs'),
                                    fset=self._set_freqs)

    self.__class__.L = property(fget=Command(Command.fget_attr, '_L'),
                                fset=self._set_L)
    
  def __eq__(self, mol) :
    """Overloaded version of the comparison operator.

    Two Molecule objects are considered to be equal if their elements,
    coordinates and the normal modes are the same.

    Positional arguments :
    mol -- object to compare with
    
    """
    # comparing elements, coordinates and displacements
    return self._elements == mol.elements and \
           self._coords.tolist() == mol.coords.tolist() and \
           self._L.tolist() == mol.L.tolist()

  def _set_L(obj, L) :
    """Setter function for the L property."""
    if L is None :
      obj._L           = None
      obj._Lx          = None
      obj._Lx_norm     = None
      obj._L_tr_rot    = None
      obj._Lx_tr_rot   = None

      obj._NFreq       = -1
      obj._freqs       = None
      obj._nrot        = -1

    else :
      # make a copy for safety ;)
      obj._L = L.copy()

      # orthonormalize L
      orthogonalize_set(obj._L)

      # generate translations / rotations
      ans = vibrations.generate_tr_rot(obj._L, obj._coords,
                                       Molecule._get_masses(obj))

      obj._L_tr_rot  = ans['L_tr_rot']
      obj._Lx_tr_rot = zeros(obj._L_tr_rot.shape, 'd')

      # recalculate Lx and Lx_tr_rot from L and L_tr_rot
      obj._Lx = zeros(obj._L.shape, 'd')
      
      for a in xrange(1, obj._L.shape[1] ) :
        const_m = sqrt(Molecule._get_masses(obj)[a] * AMU2AU)

        obj._Lx[1:, a, 1:]        = obj._L[1:, a, 1:] / const_m
        obj._Lx_tr_rot[1:, a, 1:] = obj._L_tr_rot[1:, a, 1:] / const_m

      # assign the number of rotations
      obj._nrot = obj._L_tr_rot.shape[0] - 4

      # normalized cartesian displacements (gaussian style)
      obj._Lx_norm         = obj._Lx.copy()
      obj._Lx_tr_rot_norm  = obj._Lx_tr_rot.copy()
      
      normalize_set(obj._Lx_norm)
      normalize_set(obj._Lx_tr_rot_norm)

  _set_L = staticmethod(_set_L)

  def _set_freqs(obj, freqs) :
    """Setter function for the freqs property."""
    if freqs is None :
      obj._freqs = None
      obj._NFreq = -1
      
    else :        
      obj._freqs = array(freqs, 'd')
      
      # controlling the frequencies - only positive allowed !
##      if any(0. >= self._freqs[1:]) :
##        raise InvalidArgumentError('Found non-positive frequencies !')
      
      obj._NFreq = obj._freqs.shape[0] - 1

  _set_freqs = staticmethod(_set_freqs)
     
  def update_masses(self, data_pairs) :
    """Modify the masses of atoms.

    Positional arguments :
    data_pairs -- information about the atoms (null-based ndarray)
                  shape : (Natoms_to_modify, 2)
                  atom numbers are one-based

                  Example :
                    a1  new_mass1
                    a2  new_mass2

    """
    if data_pairs is None :
      return

    if not isinstance(data_pairs, ndarray) or 2 != len(data_pairs.shape) :
      raise InvalidArgumentError('data_pairs must be a \
      two-dimensional null-based ndarray')

    masses = self._get_masses(self)

    for i in xrange(data_pairs.shape[0]) :
      masses[int(data_pairs[i, 0])] = data_pairs[i, 1]

    self.__change_isotops()

  def distance(self, i1, i2) :
    """Return the distance between atoms.

    Positional arguments :
    i1 -- one-based index of the first atom
    i2 -- one-based index of the second atom
    
    """
    for i in (i1, i2) :
      if 0 > i or i > self._Natoms :
        raise InvalidArgumentError('Invalid atom index : %s' % i)
    
    return distance(self._atoms[i1-1].coord, self._atoms[i2-1].coord, base=1)

  def angle(self, i1, i2, i3) :
    """Return the angle in grad between atoms.

    Positional arguments :
    i1 -- one-based index of the first atom
    i2 -- one-based index of the second atom
    i3 -- one-based index of the third atom
    
    """
    for i in (i1, i2, i3) :
      if 0 > i or i > self._Natoms :
        raise InvalidArgumentError('Invalid atom index : %s' % i)
    
    return angle(self._atoms[i1-1].coord, self._atoms[i2-1].coord, \
                 self._atoms[i3-1].coord, base=1)


  def dihedral(self, i1, i2, i3, i4) :
    """Return the dihedral angle in grad between atoms.

    Positional arguments :
    i1 -- one-based index of the first atom
    i2 -- one-based index of the second atom
    i3 -- one-based index of the third atom
    i4 -- one-based index of the fourth atom
    
    """
    for i in (i1, i2, i3, i4) :
      if 0 > i or i > self._Natoms :
        raise InvalidArgumentError('Invalid atom index : %s' % i)
    
    return dihedral(self._atoms[i1-1].coord, self._atoms[i2-1].coord, \
                    self._atoms[i3-1].coord, self._atoms[i4-1].coord, base=1)

