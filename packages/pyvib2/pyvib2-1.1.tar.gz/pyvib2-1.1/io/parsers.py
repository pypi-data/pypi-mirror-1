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

"""Module for parsing files.

The following classes are exported :
    AbstractFileParser      -- abstract base class for the parsers
    DaltonOutputParser      -- Dalton 1.x or 2.0 files
    FCHKFileParser          -- Gaussian Formatted Checkpoint files
    VOAVIEWFileParser       -- VOAVIEW files
    MOLDENFileParser        -- MOLDEN files
    XMolXYZFileParser       -- XMol XYZ files
    HESFileParser           -- cartesian hessian files of DALTON
    NumericDataFileParser   -- files with numeric data only
    FittedSpectraFileParser -- fitted spectra files of VOAPlot 4.2+
    FCMINTFileParser        -- cartesian hessian files of AcesII    
    ParserFactory           -- instantiating parsers

"""
__author__ = 'Maxim Fedorovsky'

import os.path
from   math import sqrt, ceil
import copy

from  numpy import zeros, array, sort

from  pyviblib.util.pse         import find_element_by_isotope, \
                                       find_element_by_atomno, \
                                       find_element_by_symbol
from  pyviblib.util.constants   import AMU2AU, BOHR2ANGSTROM, C_AU
from  pyviblib.util.exceptions  import ParseError
from  pyviblib.util.exceptions  import InvalidArgumentError, ConstructorError
from  pyviblib.util.misc        import Command, rests, PropertiesContainer
import pyviblib.calc.spectra

__all__ = ['AbstractFileParser', 'DaltonOutputParser', 'FCHKFileParser',
           'VOAVIEWFileParser', 'MOLDENFileParser', 'XMolXYZFileParser',
           'HESFileParser', 'NumericDataFileParser', 'FittedSpectraFileParser',
           'FCMINTFileParser', 'ParserFactory']


class AbstractFileParser(PropertiesContainer) :
  """Abstract base class for all parsers.

  This class defines a set of protected methods which are called in the
  constructor in the following sequence :
      _parse()              -- initialize some variables (*)
      _validate()           -- validate the read data (*)

  The following static method is exported :
      get_description()     -- get the description of a parser (*)

  Methods marked with an asterisk *must* be overridden in subclasses.
  Their default implementations raise a NotImplementedError.

  The following read-only common properties are exposed for all subclasses :
      filename              -- filename argument passed to the contructor
      Natoms                -- number of atoms in the molecule
      coords                -- cartesian coordinates
      elements              -- one-based list of elements
 
  """

  def __init__(self, filename) :
    """Constructor of the class.

    Positional arguments :
    filename -- file name or file object
    
    """
    self._filename = filename
    self._file = isinstance(filename, file) and filename or open(filename, 'r')

    # initialize fields
    self._Natoms   = -1
    self._coords   = None
    self._elements = None

    # do parsing and consistency checking
    self._parse()
    self._validate()

    PropertiesContainer.__init__(self, modulename='pyviblib.io.parsers')

  def _parse(self) :
    """Parse the file.

    Subclasses *must* override the method.
    Otherwise a NotImplementedError is raised.
    
    """
    raise NotImplementedError('_parse() method must be implemented')

  def _validate(self) :
    """Validate the read data.
    
    Subclasses *must* override the method.
    Otherwise a NotImplementedError is raised.
    
    """
    raise NotImplementedError('_validate() method must be implemented')

  def _declare_properties(self) :
    """Declare properties of the parser.

    The following properties are declared in the base class implementation :
        filename Natoms coords elements
        
    """    
    for prop in ('filename', 'Natoms', 'coords', 'elements') :
      self._add_property(prop, readonly=True)
      
  def _raise(self, desc) :
    """Raise a ParseError with a given description."""
    raise ParseError(self._filename, desc)

  def get_description() :
    """Return the description of the parser.

    Subclasses *must* override this static method.
    Otherwise a NotImplementedError is raised.
    
    """
    raise NotImplementedError('get_description() must be implemented')

  get_description = staticmethod(get_description)
    

class ParserFactory(object) :
  """Instantiating parser objects based on a file's extension.

  The following extensions (case insensitive) are recognized :
      '.out'                -- Dalton 1.x and 2.0 output files
      '.fchk' '.fch' '.fck' -- Gaussian Formatted Checkpoint files
      '.dat' '.voa'         -- VOAVIEW files
      '.mol'                -- MOLDEN files
      '.xyz'                -- XMol XYZ files

  The class exports the only static method create_parser().
  
  """

  def create_parser(filename) :
    """Create an appropriate parser.

    The extension of the file is analyzed and the approapriate parser object
    is instantiated and returned.

    Positional arguments :
    filename -- file name
    
    """
    if filename is None :
      raise InvalidArgumentError('Invalid filename argument')

    base, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    # analize the file extension
    if ext in ('.dat', '.voa') :
      parser   = VOAVIEWFileParser(filename)      
    elif ext in ('.fchk', '.fch', '.fck') :
      parser   = FCHKFileParser(filename)      
    elif '.out' == ext :
      parser   = DaltonOutputParser(filename)
    elif '.mol' == ext :
      parser   = MOLDENFileParser(filename)
    elif '.xyz' == ext :
      parser   = XMolXYZFileParser(filename)
    else :
      raise InvalidArgumentError(
        'Cannot determine the type of %s' % repr(filename))

    return parser

  create_parser = staticmethod(create_parser)
  

class VOAVIEWFileParser(AbstractFileParser) :
  """Parser for VOAVIEW files.

  The following read-only properties are exposed :
      NFreq           -- number of vibrations
      L               -- mass-weighted excursions for the vibrations
      Lx              -- cartesian excursions for the vibrations
      freqs           -- wavenumbers of vibrations in ascending order
      PP              -- gradients of the polarizability tensor
      PM              -- gradients of the G' tensor
      PQ              -- gradients of the A tensor (contracted)
      lambda_incident -- wavelength of the incident light

  The wavelength of the incident light is implied to be always 532 nm.

  """
  
  def __init__(self, filename) :
    """Constructor of the class.

    Positional arguments :
    filename -- file name or file object
    
    """
    AbstractFileParser.__init__(self, filename)

    self.__postparse()  

  def _parse(self) :
    """Parse the file."""
    # read data is to saved to these variables
    self._masses     = None
    self._freqs      = []
    self._NFreq      = -1
    self._Lx         = None
    self._L          = None
    self._PP         = None
    self._PM         = None
    self._PQ         = None

    lineno = 0
    for line in self._file.readlines() :
      line    = line.strip()
      lineno += 1

      vals = line.split()

      if 0 == len(vals) :
        self._raise('Empty lines are not allowed : line %d' % lineno)

      # first line - number of atoms
      if 1 == lineno :
        # '         45         0            0'
        if 3 != len(vals) or not ('0' == vals[1] and '0' == vals[2]) :
          self._raise('Invalid format of the line %d' % lineno)
        
        if not vals[0].isdigit() :
          self._raise('Could not read the number of atoms')

        self._Natoms = int(vals[0])
  
        # initialize the masses &  coordinates
        self._masses = zeros( 1 + self._Natoms    , 'd')
        self._coords = zeros((1 + self._Natoms, 4), 'd')
        continue

      # reading the masses (a.m.u)
      if 2 <= lineno and (1 + self._Natoms) >= lineno :
        # '  12.000000         0            0'
        if 3 != len(vals) or not ('0' == vals[1] and '0' == vals[2]) :
          self._raise('Invalid format of the line %d' % lineno)
          
        try :
          self._masses[lineno - 1] = float(vals[0])

        except ValueError :
          self._raise('Could not read the mass of the atom %d' % (lineno - 1))

        else :
          continue

      # reading the coordinates
      if (2 + self._Natoms) <= lineno and (1 + 2 * self._Natoms) >= lineno :
        try :
          xyz = [ float(val) for val in vals ]
          self._coords[lineno - 2 - self._Natoms + 1, 1:] = array(xyz)
              
        except ValueError :
          self._raise(
            'Could not read the coordinates of the atom %d' % \
            (lineno - 2 - self._Natoms + 1))

        else :
          continue

      if (2 + 2 * self._Natoms) <= lineno :
        # read the wavenumbers
        if (3 == len(vals) and '0' == vals[1] and '0' == vals[2]) :    
          if 3 * self._Natoms < (lineno - 1 - 2 * self._Natoms) :
            self._raise('Number of frequencies exceeds 3 * Natoms')
          
          try :
            self._freqs.append(float(vals[0]))
            
          except ValueError :
            self._raise('Could not read the frequency # %d' % \
                        lineno - 1 - 2 * self._Natoms)
          else :
            continue

        # reading Lx and Raman / ROA tensors
        else :
          if -1 == self._NFreq :
            if 0 == len(self._freqs) :
              self._raise('Wavenumbers were not read => cannot proceed')
            
            self._NFreq  = len(self._freqs)
            
            self._Lx = zeros( (1 + self._NFreq, 1 + self._Natoms, 4), 'd')
            self._L  = zeros( self._Lx.shape, 'd')

          # Lx
          if (2 * self._Natoms + self._NFreq + 2) <= lineno and \
             lineno <= (2*self._Natoms + self._NFreq*(self._Natoms + 1) + 1) :
            
            L_no = lineno - (2 * self._Natoms + self._NFreq + 2) + 1
            freq_no = 1 + (L_no - 1) / self._Natoms
            atom_no = L_no - self._Natoms * (freq_no  - 1)

            # saving the displacements in the reverse order.
            # Frequency list will be afterwards sorted in ascending order.
            freq_no = 1 + self._NFreq - freq_no

            try :
              xyz = [ float(val) for val in vals ]
              self._Lx[freq_no, atom_no, 1:] = array(xyz)
                
            except ValueError :
              self._raise(
                'Could not read Lx for frequency # %d, atom # %d' % \
                (freq_no, atom_no))
            else :
              continue

          # gradients
          # polarizability tensor
          # start @ 2*Natom+2+(Natom+1)*Nfreq
          # end @ 11*Natom+1+(Natom+1)*Nfreq
          elif ( 2 * self._Natoms + self._NFreq * (self._Natoms + 1) + 2 ) \
               <= lineno and lineno <= \
               ( 11 * self._Natoms + self._NFreq * (self._Natoms + 1) + 1 ) :
            # initialize
            if self._PP is None :
              self._PP = zeros((1 + self._Natoms, 4, 4, 4), 'd')

            offset = lineno - (2 * self._Natoms + self._NFreq * \
                               (self._Natoms + 1) + 2 ) + 1
            self.__read_T(offset, line, self._PP)
            continue

          # G' tensor
          # start @ 11*Natom+2+(Natom+1)*Nfreq
          # end @ 20*Natom+1+(Natom+1)*Nfreq
          elif ( 11 * self._Natoms + self._NFreq * (self._Natoms + 1) + 2) <= \
               lineno and lineno <= \
               ( 20 * self._Natoms + self._NFreq * (self._Natoms + 1) + 1 ) :
            # initialize
            if self._PM is None :
              self._PM = zeros((1 + self._Natoms, 4, 4, 4), 'd')

            offset = lineno - ( 11 * self._Natoms + self._NFreq * \
                                (self._Natoms + 1) + 2 ) + 1
            self.__read_T(offset, line, self._PM)
            continue  

          # contracted A tensor
          # start @ 20*Natom+2+(Natom+1)*Nfreq
          # end @ 29*Natom+1+(Natom+1)*Nfreq
          elif ( 20 * self._Natoms + self._NFreq * (self._Natoms + 1) + 2 ) <= \
               lineno and lineno <= \
               ( 29 * self._Natoms + self._NFreq * (self._Natoms + 1) + 1 ) :
            # initialize
            if self._PQ is None :
              self._PQ = zeros((1 + self._Natoms, 4, 4, 4), 'd')

            offset = lineno - ( 20 * self._Natoms + self._NFreq * \
                                (self._Natoms + 1) + 2 ) + 1
            self.__read_T(offset, line, self._PQ)

            continue
        
    # finished parsing
    self._file.close()
      
  def _validate(self) :
    """Validate the read data."""
    if -1 == self._Natoms or self._coords is None :
      self._raise('Inconsistent data : Coordinates were not found')

    if self._freqs is None or self._L is None or self._masses is None :
      self._raise(
        'Inconsistent data : Vibrational informations were not found.')

  def _declare_properties(self) :
    """Declare properties of the parser."""
    AbstractFileParser._declare_properties(self)

    # lambda_incident is set to 532. by default
    self._lambda_incident = 532.

    for prop in ('freqs', 'NFreq', 'Lx', 'L', 'PP', 'PM', 'PQ',
                 'lambda_incident') :
      self._add_property(prop, readonly=True)

  def __read_T(self, offset, line, T):
    """Read values into a tensor of the dimension (Natoms, 3, 3, 3).

    offset is the one-based line number from the beginning
    of reading of the tensor.
    
    """
    vals = line.split()
    
    n, pos = rests(offset, 9)
    j, k   = rests(pos)

    try :
      for i in xrange(3) :
        T[n, 1+i, j, k] = float(vals[i])
        
    except ValueError:
      self._raise(r'Could not read tensor values from the line : "%s"' % line)      

  def __postparse(self) :
    """Perform some post parse operations."""
    # sorting the frequencies array in ascending order.
    self._freqs = sort(array([0.] + self._freqs))
    
    # mass weighted normal coordinates : L = L_x * sqrt(m)
    for a in xrange(1, 1 + self._Natoms ) :
      self._L[1:, a, 1:] = self._Lx[1:, a, 1:] * sqrt(self._masses[a] * AMU2AU)

    # constructing the elements array
    self._elements = [ None ]
          
    for mass in self._masses[1:] :
      el = find_element_by_isotope(mass)
      
      if el is not None :
        # modifying the element mass to its exact value
        # ONLY FOR VOAVIEW FILES !!!
        el      = copy.deepcopy(el)
        el.mass = mass
        
        self._elements.append(el)
      else :
        self._raise('Unknown element with a mass of %f found' % mass)

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'VOAVIEWFileParser(%s)' % repr(self._filename)

  def get_description() :
    """Get the description of the parser."""
    return 'VOAVIEW File'

  get_description = staticmethod(get_description)        


class FCHKFileParser(AbstractFileParser) :
  """Parser for Formatted Checkpoint files of Gaussian.

  The following read-only properties are exposed :
      hessian         -- hessian matrix
      NBasis          -- number of basis function
      Etotal          -- total electronic energy in hartree
      comment         -- comment
      lambda_incident -- wavelength of the incident light  
      PP              -- gradients of the polarizability tensor
      PM              -- gradients of the G' tensor
      PQ              -- gradients of the A tensor (contracted)
      A               -- gradients of the A tensor (non-contracted)
      P               -- gradients of the electric dipole moment (APTs)
      M               -- gradients of the magnetic dipole moment (AATs)
      
  """  

  def __init__(self, filename) :
    """Constructor of the class.

    Positional arguments :
    filename -- file name or file object
    
    """
    AbstractFileParser.__init__(self, filename)
    self.__postparse()

  def _parse(self) :
    """Parse the file."""
    # read data is to saved to these variables
    self._comment = None
    self._atomnos = None
    self._NBasis = None
    self._Etotal = None
    
    self._hessian         = None
    self._lambda_incident = None
    self._PP = None
    self._PM = None
    self._A  = None
    self._PQ = None
    self._P  = None
    self._M  = None

    # for reading
    lambda_found = False
    n_fconst = -1
    n_atomno_read = -1
    n_coords_read = -1
    n_fconst_read = -1

    # for reading tensor elements
    n_alpha_gprim = -1
    n_a = -1
    n_ir_vcd = -1
    n_alpha_read = -1
    n_gprim_read = -1
    n_a_read = -1
    n_apt_read = -1
    n_aat_read = -1

    for line in self._file.readlines() :
      line = line.strip()

      # first line : comment
      if self._comment is None :
        self._comment = line
        continue

      # Number of atoms
      if line.startswith('Number of atoms') :
        self._Natoms = self.__read_number(line, 'number of atoms',
                                          validate=False)
        continue

      # Atomic numbers
      if line.startswith('Atomic numbers') :
        if -1 == self._Natoms :
          self._raise('Number of atoms was not read')

        self.__read_number(line, 'number of atoms', nreq=self._Natoms)        
        n_atomno_read = 0
        
        self._atomnos = zeros(1 + self._Natoms, 'l')
        continue

      # Current cartesian coordinates
      if line.startswith('Current cartesian coordinates') :
        if -1 == self._Natoms :
          self._raise('Number of atoms was not read')

        self.__read_number(line, 'number of coordinates',
                           nreq=3 * self._Natoms)
        
        n_coords_read = 0
        self._coords = zeros( (1 + self._Natoms, 4), 'd' )
        continue

      # Cartesian Force Constants
      if line.startswith('Cartesian Force Constants') :
        if -1 == self._Natoms :
          self._raise('Number of atoms was not read')

        n_fconst = (3 * self._Natoms) * (1 + 3 * self._Natoms) / 2
        self.__read_number(line, 'number of force constants', nreq=n_fconst)
        
        n_fconst_read = 0
        
        self._hessian = zeros((1 + self._Natoms, 4, 1 + self._Natoms, 4),
                              'd')
        continue

      # Frequencies for DFD properties -- for reading lambda_incident
      if line.startswith('Frequencies for DFD properties') :
        self.__read_number(line, 'number of wavelengthes', nreq=2)

        lambda_found = True
        continue
      
      # Derivative Alpha(-w,w)
      if line.startswith('Derivative Alpha(-w,w)') :
        if -1 == self._Natoms :
          self._raise('Number of atoms was not read')

        n_alpha_gprim = 54 * self._Natoms
        self.__read_number(line, 'number of alpha gradient tensor elements',
                           nreq=n_alpha_gprim)
        
        n_alpha_read = 0
        
        self._PP = zeros((1 + self._Natoms, 4, 4, 4), 'd')
        continue

      # Derivative FD Optical Rotation Tensor
      if line.startswith('Derivative FD Optical Rotation Tensor') :
        if -1 == self._Natoms :
          self._raise('Number of atoms was not read')

        n_alpha_gprim = 54 * self._Natoms
        self.__read_number(line, 'number of G gradient tensor elements',
                           nreq=n_alpha_gprim)
        
        n_gprim_read = 0
        
        self._PM = zeros((1 + self._Natoms, 4, 4, 4), 'd')
        continue

      # Derivative D-Q polarizability
      if line.startswith('Derivative D-Q polarizability') :
        if -1 == self._Natoms :
          self._raise('Number of atoms was not read')

        n_a = 108 * self._Natoms
        self.__read_number(line, 'number of A gradient tensor elements',
                           nreq=n_a)
        
        n_a_read = 0
        
        self._A = zeros((1 + self._Natoms, 4, 4, 4, 4), 'd')
        continue

      # Dipole Derivatives
      if line.startswith('Dipole Derivatives') :
        if -1 == self._Natoms :
          self._raise('Number of atoms was not read')

        n_ir_vcd = 9 * self._Natoms
        self.__read_number(line, 'number of the electric dipole derivatives',
                           nreq=n_ir_vcd)
        
        n_apt_read = 0
        
        self._P = zeros((1 + self._Natoms, 4, 4), 'd')
        continue

      # AAT
      if line.startswith('AAT') :
        if -1 == self._Natoms :
          self._raise('Number of atoms was not read')

        n_ir_vcd = 9 * self._Natoms
        self.__read_number(line, 'number of the magnetic dipole derivatives',
                           nreq=n_ir_vcd)
        
        n_aat_read = 0
        
        self._M = zeros((1 + self._Natoms, 4, 4), 'd')
        continue          

      # Number of basis functions
      if line.startswith('Number of basis functions') :
        self._NBasis = self.__read_number(line, 'number of basis functions',
                                          validate=False)
        continue

      # Total Energy
      if line.startswith('Total Energy') :
        self._Etotal = self.__read_number(line, 'total energy',
                                          validate=False, type_=float)
        continue

      ########################## READING ###########################
      # atomic numbers
      if -1 != n_atomno_read and n_atomno_read < self._Natoms :        
        n_atomno_read += self.__read_values(line, n_atomno_read,
                                            self.__retrieve_atomno,
                                            self._atomnos)
                
        if n_atomno_read == self._Natoms :
          n_atomno_read = -1
        continue
        
      # cartesian coordinates
      if -1 != n_coords_read and n_coords_read < 3 * self._Natoms :        
        n_coords_read += self.__read_values(line, n_coords_read,
                                            self.__retrieve_coords,
                                            self._coords)
        
        if n_coords_read == 3 * self._Natoms :
          n_coords_read  = -1
        continue        

      # cartesian force constants
      if -1 != n_fconst_read and n_fconst_read < n_fconst :        
        n_fconst_read += self.__read_values(line, n_fconst_read,
                                            self.__retrieve_hessian_indices,
                                            self._hessian)
        
        if n_fconst_read == n_fconst :
          n_fconst_read = -1
        continue

      # wavelength of the incident light
      # recalculating in nanometers
      if lambda_found :
        self._lambda_incident = self.__read_number(line, 'lambda incident',
                                                   validate=False,
                                                   type_=float)
        self._lambda_incident = 45.563350 / self._lambda_incident
        
        lambda_found = False
        continue

      # alpha tensor gradients
      if -1 != n_alpha_read and n_alpha_read < n_alpha_gprim :
        n_alpha_read += self.__read_values(line, n_alpha_read,
                                           self.__retrieve_PX_indices,
                                           self._PP)
        
        if n_alpha_read == n_alpha_gprim :
          n_alpha_read = -1
        continue

      # G' tensor gradients
      if -1 != n_gprim_read and n_gprim_read < n_alpha_gprim :
        n_gprim_read += self.__read_values(line, n_gprim_read,
                                           self.__retrieve_PX_indices,
                                           self._PM)
        
        if n_gprim_read == n_alpha_gprim :
          n_gprim_read = -1
        continue

      # A tensor gradients
      if -1 != n_a_read and n_a_read < n_a :
        n_a_read += self.__read_values(line, n_a_read,
                                       self.__retrieve_A_indices,
                                       self._A)
    
        if n_a_read == n_a :
          n_a_read = -1
        continue

      # APT
      if -1 != n_apt_read and n_apt_read < n_ir_vcd :
        n_apt_read += self.__read_values(line, n_apt_read,
                                         self.__retrieve_AXT_indices,
                                         self._P)
    
        if n_apt_read == n_ir_vcd :
          n_apt_read = -1
        continue

      # AAT
      if -1 != n_aat_read and n_aat_read < n_ir_vcd :
        n_aat_read += self.__read_values(line, n_aat_read,
                                         self.__retrieve_AXT_indices,
                                         self._M)
    
        if n_aat_read == n_ir_vcd :
          n_aat_read = -1
        continue            
    
    # finished parsing
    self._file.close()

  def __retrieve_atomno(num) :
    """Retriever for atomic numbers."""
    return num

  __retrieve_atomno = staticmethod(__retrieve_atomno)

  def __retrieve_coords(num) :
    """Retriever for coordinates."""    
    atomno = 1 + int((num - 1) / 3)
    c      = num - 3 * (atomno - 1)

    return atomno, c

  __retrieve_coords = staticmethod(__retrieve_coords)  

  def __retrieve_hessian_indices(num):
    """Retrieve the position of a cartesian force constant.

    The only parameter is the number of the record.
    
    """
    q1 = int(ceil((-1 + sqrt(1 + 8*num))/2))
    q2 = int(num - q1 * (q1 - 1)/ 2 )

    r1 = rests(q1)
    r2 = rests(q2)

    return r2 + r1

  __retrieve_hessian_indices = staticmethod(__retrieve_hessian_indices)

  def __retrieve_PX_indices(self, num) :
    """Retriever for PP or PM.

    We are reading only the second half of the values since the calculation is
    done for freq = 0 and freq = 532 (e.g)

    Number of elements to skip : 27 * Natoms
    
    """
    if 1 + 27 * self._Natoms > num :
      return None
    
    else :
      a, temp  = rests(num - 27 * self._Natoms, divisor=27)
      q, temp2 = rests(temp, divisor=9)
      j, i     = rests(temp2, divisor=3)

      return a, q, i, j

  def __retrieve_A_indices(self, num) :
    """Retriever for the A tensor.

    Exactly as for __retrieve_PX_indices() reading only the second half of the
    elements.

    Number of elements to skip : 54 * Natoms
    
    """
    if 1 + 54 * self._Natoms > num :
      return None

    else :
      a, temp   = rests(num - 54 * self._Natoms, divisor=54)
      q1, temp2 = rests(temp, divisor=18)
      q2, temp3 = rests(temp2, divisor=6)

      if 4 > temp3 :
        i, j = temp3, temp3
      else :
        if 6 > temp3 :
          i, j = 1, temp3 - 2
        else :
          i, j = 2, 3

      return a, q1, q2, i, j

  def __retrieve_AXT_indices(num) :
    """Retriever for the APT or AAT tensors."""
    a, temp = rests(num, divisor=9)
    q, i    = rests(temp, divisor=3)

    return a, q, i

  __retrieve_AXT_indices = staticmethod(__retrieve_AXT_indices)
          
  def __read_number(self, line, desc, nreq=None, validate=True, type_=int) :
    """Read a number from a line and validate it.

    Positional arguments :
    line     -- line to parse
    desc     -- description of the number

    Keyword arguments :
    validate -- whether to compare the number with nreq (default : True)
    nreq     -- the expected value (default None)
    type_    -- type of the number (default int)

    Return the read number.
    
    """
    if validate and nreq is None :
      raise InvalidArgumentError('nreq must be supplied if validate = True')
    
    try :
      sep   = '=' in line and '=' or ' '
      nread = type_(line.split(sep).pop())

    except ValueError :
      self._raise('Could not read %s' % desc)

    else :
      if validate and nread != nreq :
        self._raise('%s must be exactly %d, got %d' % (desc, nreq, nread))

      return nread

  def __read_values(self, line, n_read, retriever, arr, desc=None) :
    """Read the value from a line to an array.

    retriever must be a function which accepts the number and return the
    indices of the array to read into.

    Return the number of read elements.
    
    """
    vals = line.split()

    try :
      for i in xrange(len(vals)) :
        indices = retriever(1 + i + n_read)
        
        if indices is not None :
          arr[indices] = float(vals[i])        
        
    except ValueError :
      self._raise('Could not read %s' % desc or 'the values')

    else :
      return len(vals)
    
  def _validate(self) :
    """Validate the read data."""
    if -1 == self._Natoms or self._coords is None or self._atomnos is None :
      self._raise('Inconsistent data : Coordinates were not found.')

    # if the Raman/ROA tensors are read, lambda_found *must* be set
    n_None = [self._PP, self._PM, self._A].count(None)

    # if at least on the tensors was read, lambda incident *must* be set
    if 3 > n_None and self._lambda_incident is None :
      self._raise('lamda incident must be supplied')

  def _declare_properties(self) :
    """Declare properties of the parser."""
    AbstractFileParser._declare_properties(self)

    for prop in ('hessian', 'PP', 'PM', 'PQ', 'A', 'lambda_incident',
                 'P', 'M', 'NBasis', 'comment', 'Etotal') :
      self._add_property(prop, readonly=True)
    
  def __postparse(self) :
    """Perform some post parse operations."""
    # recalculating the coordinates in angstrom
    self._coords *= BOHR2ANGSTROM    

    # constructing the full hessian
    if self._hessian is not None :      
      for a in range(1 + self._Natoms):
        for b in range(a, 1 + self._Natoms):
          # diagonal blocks
          if a == b :
            for i in (1, 2) :
              for j in range(1 + i, 4) :
                self._hessian[a, j, a, i] = self._hessian[a, i, a, j]

          # other block - just copy
          else :
            for i in xrange(1, 4) :
              for j in xrange(1, 4) :
                self._hessian[b, i, a, j] = self._hessian[a, j, b, i]

    ## converting the tensors : Gaussian -> Dalton
    # G'(Dalton) = G'(Gaussian) / sqrt(C_AU)
    if self._PM is not None :      
      self._PM /= sqrt(C_AU)
          
    # A(Dalton) = 1.5 * A(Gaussian)
    # A[a, q1, q2, i, j] = A[a, q1, q2, j, i]
    if self._A is not None :    
      self._A *= 1.5

      for a in xrange(1, 1 + self._Natoms) :
        for q1 in xrange(1, 4) :
          for q2 in xrange(1, 4) :
            for i in xrange(1, 4) :
              for j in xrange(1 + i, 4) :
                self._A[a, q1, q2, j, i] = self._A[a, q1, q2, i, j]

      self._PQ = pyviblib.calc.spectra.contract_A_tensor(self._A)

    # constructing the elements array from read atomic numbers
    self._elements = [None]
          
    for atomno in self._atomnos[1:] :
      el = find_element_by_atomno(atomno)
      
      if el is not None :
        el = copy.deepcopy(el)
        self._elements.append(el)
        
      else :
        self._raise('Unknown element with the atom number %d' % atomno)

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'FCHKFileParser(%s)' % repr(self._filename)
        
  def get_description() :
    """Get the description of the parser."""
    return 'Gaussian Formatted Checkpoint File'

  get_description = staticmethod(get_description)             


class DaltonOutputParser(AbstractFileParser) :
  """Parser for DALTON 1.x or 2.x output files.
      
  The following read-only properties are exposed :
      version         -- DALTON version
      NFreq           -- number of vibrations
      L               -- mass-weighted excursions for the vibrations
      Lx              -- cartesian excursions for the vibrations
      freqs           -- wavenumbers of vibrations in ascending order
      lambda_incident -- wavelength of the incident light  
      PP              -- gradients of the polarizability tensor
      PM              -- gradients of the G' tensor
      PQ              -- gradients of the A tensor (contracted)
      A               -- gradients of the A tensor (non-contracted)
      P               -- gradients of the electric dipole moment (APTs)
      M               -- gradients of the magnetic dipole moment (AATs)      
      
  """  

  def __init__(self, filename) :
    """Constructor of the class.

    Positional arguments :
    filename -- file name or file object
    
    """
    AbstractFileParser.__init__(self, filename)    
    self.__postparse()

  def _parse(self) :
    """Parse the file."""
    ## data to be read
    self._Natoms     = -1
    self.__symbols   = None
    self._coords     = None
    self._freqs      = None
    self._NFreq      = -1
    self._Lx         = None
    self._L          = None

    # wavelength of the incident light
    self._lambda_incident = None
    
    # polarizability tensor gradient
    self._PP = None
    
    # London G' tensor gradient
    self._PM = None
    
    # non-contracted and contracted A tensor gradient
    self._A  = None
    self._PQ = None

    # electric and magnetic dipole moment gradients
    self._P  = None
    self._M  = None

    ## value of -666 means that all required properties are read
    n_coords_found      = 0
    n_alpha_found       = 0
    n_G_found           = 0
    n_A_found           = 0
    n_Freqs_found       = 0
    n_Norm_coords_found = 0
    n_P_found           = 0
    n_M_found           = 0

    # current number of the row
    self.__ielement    = -1

    # last column number
    self.__ilastcolumn = -1

    # number of the isotopic molecule
    self.__molno = 1

    # DALTON version
    self._version = None

    # coordinates format : can be 0(old) or new(1)
    format_coords = 0

    # for reading of the normal coordinates
    self.__n_freq_start = -1
    self.__n_freq_end   = -1

    for line in self._file.readlines() :
      line    = line.strip()

      # quit if all the properties are read
      if -666 == n_coords_found and -666 == n_alpha_found and \
         -666 == n_G_found and \
         -666 == n_A_found and -666 == n_Freqs_found and \
         -666 == n_Norm_coords_found and \
         self._lambda_incident is not None :
        break

      # DALTON version
      if self._version is None and \
         'This is output from DALTON (Release ' in line :
        self._version = self.__get_version(line)

      # number of atoms
      if line.startswith('Total number of atoms'):        
        # raise an exception if the version was not read
        if self._version is None :
          self._raise('DALTON version could not be read')
        
        vals = line.split(':')
        
        if 2 != len(vals):
          self._raise('Cannot read the number of atoms')

        vals[1] = vals[1].strip()
        if not vals[1].isdigit() :
          self._raise('Number of atoms must be integer')
          
        else :
          self._Natoms = int(vals[1])
          continue

      # wavelength of the incident light
      if ( line.startswith('Raman Optical Activity properties for freq') or \
           line.startswith('Raman related properties for freq') ) and \
           self._lambda_incident is None :
        try :
          self._lambda_incident = float(line.split()[-2])
          continue

        except ValueError :
          self._raise('Could not read the wavelength of the incident light')

      if 'Cartesian Coordinates' in line :
        n_coords_found  += 1

        # in the new format '(a.u.)' is present
        if '(a.u.)' in line :
          format_coords = 1

        if 1 == n_coords_found :
          self._coords    = zeros((1 + self._Natoms, 4), 'd')
          self.__symbols  = []          
        continue
  
      if ( 2.0 > self._version and \
           line.startswith('Polarizability tensor Cartesian gradient') ) or \
         ( 2.0 <= self._version and \
           'Polarizability tensor (alpha) gradient' in line ) :
        n_alpha_found += 1

        if self.__molno == n_alpha_found :
          self._PP = zeros((1 + self._Natoms, 4, 4, 4), 'd')
          self.__ilastcolumn = -1          
        continue

      if ( 2.0 > self._version and \
           'London G tensor Cartesian gradient' == line ) or \
         ( 2.0 <= self._version and 'London G tensor gradient' in line ):
        n_G_found += 1

        if self.__molno == n_G_found :
          self._PM = zeros((1 + self._Natoms, 4, 4, 4), 'd')
          self.__ilastcolumn = -1          
        continue

      if ( 2.0 > self._version and 'A tensor Cartesian gradient' == line ) or \
         ( 2.0 <= self._version and 'A tensor gradient' in line ) :
        n_A_found += 1

        if self.__molno == n_A_found :
          self._A = zeros((1 + self._Natoms, 4, 4, 4, 4), 'd')
          self.__ilastcolumn = -1          
        continue

      if 'Dipole moment gradient (au)' in line :
        n_P_found += 1

        if self.__molno == n_P_found :
          self._P = zeros((1 + self._Natoms, 4, 4), 'd')          
        continue

      if 'Atomic axial tensors (AATs)' in line :
        n_M_found += 1

        if self.__molno == n_M_found :
          self._M = zeros((1 + self._Natoms, 4, 4), 'd')          
        continue

      if 'Vibrational Frequencies' in line :
        n_Freqs_found += 1
        
        if self.__molno == n_Freqs_found :
          self._freqs =  []        
        continue

      if 'Normal Coordinates (bohrs*amu**(1/2))' in line :
        n_Norm_coords_found += 1

        if self.__molno == n_Norm_coords_found :
          if 0 == len(self._freqs) :
            self._raise('Cannot read the normal modes unless the ' + \
                        'number of frequencies is known.')

          # initialize the cartesian displacements
          self._NFreq = len(self._freqs)
          self._Lx    = zeros((1 + self._NFreq, 1 + self._Natoms, 4), 'd')

          self.__ilastcolumn  = -1
          self.__ielement     = -1
          self.__n_freq_start = -1
          self.__n_freq_end   = -1          
        continue

      # for reading tensors
      if -1 != line.find('Column') and \
         (n_alpha_found or n_G_found or n_A_found) :
        self.__ilastcolumn = int(line.split().pop().strip())
        continue

      # for reading normal coordinates
      if 0 < n_Norm_coords_found and 0 < len(line) and \
         not (len(line.split()) & 1) and \
         ( not 'x' in line and not 'y' in line and not 'z' in line ) :
        vals = line.split()
        
        self.__n_freq_start = int(vals[0])
        self.__n_freq_end   = int(vals[-2])
        continue

      ## reading the data
      # cartesian coordinates in atomic units : converting to angstroms
      if 1 == n_coords_found :
        if self.__read_coords(line, format_coords) :
          n_coords_found     = -666
          self.__ilastcolumn = -1            
        continue

      # frequencies in cm**(-1)
      if self.__molno == n_Freqs_found :
        if len(line) > 0 :
          vals = line.split()
          if vals[0].isdigit() and 4 <= len(vals):
            if -1 != vals[2].find('i') :
              self._raise(\
                r'Found a negative frequency in the line "%s"' % line)
              
            try :
              self._freqs.append(float(vals[2]))
              
            except ValueError:
              self._raise(\
                r'Cannot read the wavenumber from the line : "%s".' % line)
        else :
          if 1 < len(self._freqs) :
            n_Freqs_found       = -666
            self.__ilastcolumn  = -1

        continue

      # mass-weighted displacements L
      if self.__molno == n_Norm_coords_found and self.__is_L_Line(line) :
        self.__read_Lx(line, self._Lx)

        if self._NFreq == self.__n_freq_end and \
           3 * self._Natoms == self.__ielement :         
          n_Norm_coords_found = -666
          self.__ilastcolumn  = -1
          self.__ielement     = -1
          self.__n_freq_start = -1
          self.__n_freq_end   = -1

      # Polarizability tensor gradient (PP)
      if self.__is_PX_Line(line) and self.__molno == n_alpha_found :
        self.__read_T(line, self._PP)
            
        if self.__ilastcolumn == 3 * self._Natoms and 9 == self.__ielement:
          n_alpha_found      = -666
          self.__ielement    = -1
          self.__ilastcolumn = -1

        continue

      # London G tensor gradient (PM)
      if self.__is_PX_Line(line) and self.__molno == n_G_found :
        self.__read_T(line, self._PM)
    
        if self.__ilastcolumn == 3 * self._Natoms and 9 == self.__ielement:
          n_G_found          = -666
          self.__ielement    = -1
          self.__ilastcolumn = -1

        continue

      # A tensor gradient (A)
      if self.__is_PX_Line(line) and self.__molno == n_A_found :
        self.__read_A(line, self._A)
    
        if self.__ilastcolumn == 3 * self._Natoms and 27 == self.__ielement:
          n_A_found          = -666
          self.__ielement    = -1
          self.__ilastcolumn = -1

        continue

      # electric dipole moment gradient (P)
      if self.__is_P_M_Line(line) and self.__molno == n_P_found :
        self.__read_P_M(line, self._P)

        if 3 * self._Natoms == self.__ielement :
          n_P_found         = -666
          self.__ielement   = -1

      # magnetic dipole moment gradient (M)
      if self.__is_P_M_Line(line) and self.__molno == n_M_found :
        self.__read_P_M(line, self._M)

        if 3 * self._Natoms == self.__ielement :
          n_M_found         = -666
          self.__ielement   = -1

    # quitting softly
    self._file.close()

  def __get_version(line) :
    """Extract the version of DALTON.

    Example :
      'This is output from DALTON (Release 2.0 rev. 0, Mar. 2005)' -> 2.0

    Return None for a not appropriate line.
    
    """
    if line is None or not 'This is output from DALTON (Release ' in line :
      return None

    strid = 'Release '
    line = line[line.index(strid) + len(strid):]

    index_last = min(line.index(' '), line.index(','))

    return float(line[:index_last])

  __get_version = staticmethod(__get_version)

  def __is_PX_Line(self, line):
    """Check if a line looks like PP, PM or A."""
    return -1 == line.find('Column') and 0 < len(line.strip()) \
           and -1 != self.__ilastcolumn

  def __is_L_Line(self, line) :
    """Check if a line contains displacements.

    Example :
      'O001 x    0.000000   -0.045509    0.004001    0.026395   -0.059492'
      
    """
    return ('x' in line or 'y' in line or 'z' in line) and \
           -1 != self.__n_freq_start and \
           -1 != self.__n_freq_end

  def __is_P_M_Line(line) :
    """Check if a line looks like P or M.

    Example :
      'O001 x    -0.69570315     0.00000000     0.00000000'
      
    """
    return ('x' in line or 'y' in line or 'z' in line) and \
           'Ex' not in line and 'Bx' not in line

  __is_P_M_Line = staticmethod(__is_P_M_Line)

  def __get_symbolno(symbolstr) :
    """'O001' -> ('O', 1)"""
    # scan for the first digit and extract the characters before it
    for i in xrange(len(symbolstr)) :
      if symbolstr[i].isdigit() :
        break

    return (symbolstr[:i], int(symbolstr[i:]))

  __get_symbolno = staticmethod(__get_symbolno)

  def __read_coords(self, line, format_coords) :
    """Read the cartesian coordinates depending on the DALTON version.

    format_coords - 0(old), 1(new)

    Return if all coodinates were read.
    
    """    
    vals = line.split()

    # old DALTON 1.x
    if 0 == format_coords :
      if 3 == len(vals) or 4 == len(vals) :
        # symbol
        if 4 == len(vals) :
          sym, no = self.__get_symbolno(vals[1])
          self.__symbols.append(sym)
        
        # coordinate
        coordno = int(vals[0])
        atomno, xyzno = rests(coordno, 3)
        self._coords[atomno, xyzno] = float(vals.pop()) * BOHR2ANGSTROM

        return 3 * self._Natoms == coordno

    # DALTON 2.x
    else :
      if 11 == len(vals) and 'x' == vals[3] and 'y' == vals[6] and \
         'z' == vals[9] :
        #
        sym, no = self.__get_symbolno(vals[0])
        self.__symbols.append(sym)

        #
        atomno, dummy = rests(int(vals[2]), 3)
        self._coords[atomno, 1:] = [ float(vals[i]) * BOHR2ANGSTROM \
                                     for i in (4, 7, 10) ]

        return 3 * self._Natoms == int(vals[8])

    return False

  def __read_Lx(self, line, Lx) :
    """Read the cartesian displacements in atomic mass units.

    'O001 x    0.000000   -0.045509    0.004001    0.026395   -0.059492'
    
    """
    vals = line.split()

    # retrieve the information about the atom
    sym, atomno = self.__get_symbolno(vals[0])
    xyz = 1 + ['x', 'y', 'z'].index(vals[1])

    for i in xrange(self.__n_freq_start, 1 + self.__n_freq_end) :
      Lx[1 + self._NFreq - i, atomno, xyz] = float(
        vals[2 + i - self.__n_freq_start]) / sqrt(AMU2AU)

    # saving in order to define when to stop
    self.__ielement = (atomno - 1) * 3 + xyz
    
  def __read_T(self, line, T):
    """Read values into a tensor of the dimension (Natoms, 3, 3, 3)."""
    vals = line.split()

    try :
      self.__ielement = int(vals[0])
      start = 2 + self.__ilastcolumn - len(vals)
      
      rest2 = rests(self.__ielement) # nu, mu
      for i in xrange(start, 1 + self.__ilastcolumn):
        rest1 = rests(i) # atom, i
        T[rest1[0], rest1[1], rest2[0], rest2[1]] = float(vals[i - start + 1])

    except ValueError:
      self._raise(r'Could not read tensor values from the line : "%s".' % line)

  def __read_A(self, line, A):
    """Read values into the uncontracted A tensor."""
    vals = line.split()

    try :
      self.__ielement = int(vals[0])
      start = 2 + self.__ilastcolumn - len(vals)

      j, temp = rests(self.__ielement, divisor=9)
      i, q2   = rests(temp, divisor=3)
      
      for b in xrange(start, 1 + self.__ilastcolumn) :
        a, q1 = rests(b, divisor=3)
        A[a, q1, q2, i, j] = float(vals[b - start + 1])
        
    except ValueError:
      self._raise(
        r'Could not read A tensor gradient from the line : "%s".' % line)      

  def __read_P_M(self, line, T) :
    """Read values into P or M tensor."""
    vals = line.split()

    # retrieve the information about the atom
    sym, atomno = self.__get_symbolno(vals[0])
    xyz = 1 + ['x', 'y', 'z'].index(vals[1])

    T[atomno, xyz, 1:4] = [ float(val) for val in vals[2:5] ]
    
    # saving in order to define when to stop
    self.__ielement = (atomno - 1) * 3 + xyz    
      
  def _validate(self) :
    """Validate the read data."""
    if -1 == self._Natoms or self._coords is None :
      self._raise('Inconsistent data : Coordinates were not found')

    if self._freqs is None or self._Lx is None :
      self._raise('Inconsistent data : Normal modes are not found')

    if self._lambda_incident is not None and 532. != self._lambda_incident :
      print 'Warning : using the wavelength of the incident light : %.2f' % \
            self._lambda_incident

  def _declare_properties(self) :
    """Declare properties of the parser."""
    AbstractFileParser._declare_properties(self)

    for prop in ('freqs', 'NFreq', 'Lx', 'L', 'PP', 'PM', 'PQ',
                 'A', 'P', 'M', 'version', 'lambda_incident') :
      self._add_property(prop, readonly=True)

  def __postparse(self) :
    """Perform some post parse operations."""
    if self.__symbols is None or 0 == len(self.__symbols) :
      self._raise('Coordinates are not read !')
    
    # sorting the frequencies array in ascending order.
    self._freqs = sort(array([0.] + self._freqs))
    
    # constructing the elements array
    self._elements = [None]
          
    for symbol in self.__symbols :
      el = find_element_by_symbol(symbol)
      
      if el is not None :
        self._elements.append(copy.deepcopy(el))
        
      else :
        self._raise('Unknown element : %s' % symbol)

    # cartesian displacements : Lx = L / sqrt(m)
    self._L = zeros(self._Lx.shape, 'd')
   
    for a in xrange(1, 1 + self._Natoms) :
      self._L[1:, a, 1:] = self._Lx[1:, a, 1:] * \
                           sqrt(self._elements[a].mass * AMU2AU)

    # contract the raw A tensor :
    if self._A is not None :
      self._PQ = pyviblib.calc.spectra.contract_A_tensor(self._A)

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'DaltonOutputParser(%s)' % repr(self._filename)

  def get_description() :
    """Get the description of the parser."""
    return 'DALTON 1.x or 2.0 Output File'

  get_description = staticmethod(get_description)              


class MOLDENFileParser(AbstractFileParser) :
  """Parser for MOLDEN files.

  Currently extracts only the geometry and normal modes of a molecule.

  The following read-only properties are exposed :
      NFreq           -- number of vibrations
      L               -- mass-weighted excursions for the vibrations
      Lx              -- cartesian excursions for the vibrations
      freqs           -- wavenumbers of vibrations in ascending order
      comment         -- comment

  """  
  
  def __init__(self, filename) :
    """Constructor of the class.

    Positional arguments :
    filename -- file name or file object
    
    """
    AbstractFileParser.__init__(self, filename)
    self.__postparse()

  def _parse(self) :
    """Parse the file.

    See http://www.cmbi.ru.nl/molden/molden_format.html

    """
    self.__symbols      = []
    # coordinates supplied in the [Atoms] section
    self.__atomcoords   = []
    self._freqs         = None
    
    # for reading
    geometries_found = False
    freq_found = False
    fr_coord_found = False
    fr_norm_coord_found = False
    atoms_found = False
    atoms_in_au = False

    lineno  = 0
    counter = 0
    vibno   = 0

    # initial values
    self._Natoms = None
    self._coords = None
    self._freqs = None
    self._Lx = None
    
    for line in self._file.readlines() :
      line    = line.strip()
      lineno += 1

      # first line must be [Molden Format]
      if 1 == lineno and '[Molden Format]' != line :
        self._raise('The first line of a MOLDEN file must be [Molden Format]')

      # Coordinates for the Electron Density/Molecular orbitals
      # reading only if [GEOMETRIES] and [FR-COORD] are not supplied !
      if line.startswith('[Atoms]') and 0 == len(self.__symbols) :
        atoms_in_au = 'AU' in line

        atoms_found = True
        counter = 1
        continue

      # coordinates in angstrom
      if line.startswith('[GEOMETRIES]') :
        if 'XYZ' not in line :
          self._raise('Currently only the cartesian coordinates are supported')

        geometries_found = True
        counter = 1
        continue

      # frequencies in cm**(-1)
      if '[FREQ]' == line :
        freq_found       = True
        geometries_found = False
        continue

      # equilibrium coordinates in bohr (a.u.)
      if '[FR-COORD]' == line :
        fr_coord_found = True

        if self._freqs is None :
          self._raise('Frequencies were not be read')

        if self._Natoms is None :
          self._raise('Number of atoms was not read')

        # stop reading of the wavenumbers & initialize the Ls
        freq_found  = False

        # reinitializing the coordinates
        del self.__symbols[:]
        self._coords = zeros((1 + self._Natoms, 4), 'd')
        
        self._NFreq  = len(self._freqs) - 1
        self._Lx     = zeros((1 + self._NFreq, 1 + self._Natoms, 4), 'd')
        
        counter      = 1
        continue

      # cartesian displacements Lx in bohr (a.u.)
      if '[FR-NORM-COORD]' == line :
        fr_norm_coord_found = True
        fr_coord_found = False
        continue

      ########## READING ##########
      # [Atoms] (Angst|AU)
      # recognizing the end of the section by number of fields in the line (<6)
      if atoms_found :
        if 6 == len(line.split()) :
          symb, coord = self.__read_coords(line)
          
          self.__symbols.append(symb)
          if atoms_in_au :
            coord *= BOHR2ANGSTROM
          self.__atomcoords.append(coord)
          
          counter += 1
          continue

        else :
          # set the number of atoms and coordinates
          self._Natoms = len(self.__atomcoords)
                  
          atoms_found = False
          counter = 0
          continue
      
      # [GEOMETRIES] XYZ
      if geometries_found :
        # number of atoms
        if 1 == counter :
          if not line.isdigit() :
            self._raise(
                r'Cannot read the number of atoms from the line "%s"' % line)

          self._Natoms = int(line)
          self._coords = zeros((1 + self._Natoms, 4), 'd')
          counter += 1
          continue

        # comment line
        if 2 == counter :
          self._comment = line
          counter += 1
          continue

        # coordinates
        if (self._Natoms + 2) >= counter:          
          symb, coord = self.__read_coords(line)
          
          self.__symbols.append(symb)
          self._coords[counter - 2, 1:] = coord
          
          counter += 1
          continue
        
        else :
          geometries_found = False
          counter = 0
          continue

      # [FREQ]
      if freq_found :
        if self._freqs is None :
          self._freqs = [0.]
        try :
          self._freqs.append(float(line))          
        except ValueError :
          self._raise(r'Cannot read the wavenumber from the line "%s"' % line)

        continue

      # [FR-COORD]
      # equilibrium coordinates in au : overriding previously read coordinates
      if fr_coord_found :
        if self._Natoms >= counter:
          symb, coord = self.__read_coords(line)

          self.__symbols.append(symb)
          self._coords[counter, 1:] = coord * BOHR2ANGSTROM
          
          counter += 1
          continue

        else :
          fr_coord_found = False
          counter = 0
          continue

      # [FR-NORM-COORD]
      # Lx cartesian excursions
      if fr_norm_coord_found :
        # number of vibration
        if line.startswith('vibration') :
          vals = line.split()

          if 2 > len(vals) or not vals[1].isdigit() :
            self._raise(r'Invalid format of the line "%s"' % line)

          vibno   = int(vals[1])
          counter = 1
          continue
        
        # excursions
        else :
          if 1 <= vibno and vibno <= self._NFreq and counter <= self._Natoms :
            symb, coord = self.__read_coords(line, read_symbol=False)
            self._Lx[vibno, counter, 1:] = coord

            counter += 1
            continue

          else :
            fr_norm_coord_found = False
            counter = 0
            continue

  def _validate(self) :
    """Validate the read data."""
    # if coordinates were not read from [GEOMETRIES] or [FR-COORD]
    if self._coords is None :
      if 0 == len(self.__atomcoords) :
        self._raise('Coordinates are not supplied !')

      self._coords = zeros((1 + self._Natoms, 4), 'd')
      for i in xrange(len(self.__atomcoords)) :
        self._coords[1 + i, 1:] = self.__atomcoords[i]
    
  def _declare_properties(self) :
    """Declare properties of the parser."""
    AbstractFileParser._declare_properties(self)

    for prop in ('freqs', 'NFreq', 'Lx', 'L', 'comment') :
      self._add_property(prop, readonly=True)

  def __read_coords(self, line, read_symbol=True) :
    """Read the coordinates from a line.

    Keyword arguments :
    read_symbol  -- consider the first token to be the symbol (default True)

    Return symbol, ndarray(x, y, z)

    """
    vals = line.split()

    if 3 + (read_symbol and 1 or 0) > len(vals) :
      self._raise(r'Could not read coordinates from the line "%s"' % line)

    symbol = read_symbol and vals[0] or None
    
    try :
      coords = array([ float(val) for val in vals[-3:] ], 'd')

    except ValueError :
      self._raise(r'Could not read coordinates from the line "%s"' % line)

    else :
      return symbol, coords    

  def __postparse(self) :
    """Perform some post parse operations."""
    # constructing the elements array
    self._elements = [None]
          
    for symbol in self.__symbols :
      el = find_element_by_symbol(symbol)
      
      if el is not None :
        self._elements.append(copy.deepcopy(el))        
      else :
        self._raise('Unknown element with symbol %s' % symbol)

    # if vibrational information is present
    # mass weighted normal coordinates : L = L_x * sqrt(m)
    if self._freqs is None :
      self._L = None      
    else :
      self._L = zeros(self._Lx.shape, 'd')
      
      for a in xrange(1, 1 + self._Natoms) :
        self._L[1:, a, 1:] = self._Lx[1:, a, 1:] * sqrt(self._elements[a].mass)

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'MOLDENFileParser(%s)' % repr(self._filename)

  def get_description() :
    """Get the description of the parser."""
    return 'MOLDEN File'

  get_description = staticmethod(get_description)         


class XMolXYZFileParser(AbstractFileParser) :
  """Parser for XMol XYZ files.

  The following read-only property is exposed :
      comment -- comment

  """  

  def __init__(self, filename) :
    """Constructor of the class.

    Positional arguments :
    filename -- file name or file object
    
    """
    AbstractFileParser.__init__(self, filename)
    self.__postparse()

  def _parse(self) :
    """Parse the file."""
    self._comment = None
    self.__symbols = []

    lineno = 0
    self.__count_atoms = 0
    
    for line in self._file.readlines() :
      line    = line.strip()
      lineno += 1

      if 0 == len(line) :
        continue

      # first line : number of atoms
      if 1 == lineno :
        if not line.isdigit() :
          self._raise(
            r'Cannot read the number of atoms from the line "%s"' % line)

        self._Natoms = int(line)
        if 0 >= self._Natoms :
          self._raise(
            r'Number of atoms must be positive, got "%d"' % self._Natoms)

        self._coords = zeros((1 + self._Natoms, 4), 'd')
        continue
        
      # second line : comment
      if 2 == lineno :
        self._comment = line
        continue

      # coordinates
      if 2 < lineno :
        vals = line.split()

        if 4 != len(vals) :
          self._raise(r'Invalid coordinates line : "%s"' % line)
        
        self.__symbols.append(vals[0])
        self.__count_atoms = lineno - 2

        if self._Natoms < self.__count_atoms :
          self._raise(
            r'Redundant data : only %d atoms are declared' % self._Natoms)
        
        try :
          self._coords[self.__count_atoms, 1:] = array(
            [float(val) for val in vals[1:]], 'd')
          
        except ValueError :
          self._raise(r'Cannot read coordinates from the line "%s"' % line)
      
    self._file.close()    

  def _validate(self) :
    """Validate the read data."""
    if self._coords is None :
      self._raise('Coordinates not found')

    if self.__count_atoms < self._Natoms :
      self._raise(
        'Read coodinates only for %d atoms but %d declared' % \
        (self.__count_atoms, self._Natoms))
    
  def _declare_properties(self) :
    """Declare properties of the parser."""
    AbstractFileParser._declare_properties(self)

    self._add_property('comment', readonly=True)

  def __postparse(self) :
    """Perform some post parse operations."""
    # constructing the elements array
    self._elements = [None]
          
    for symbol in self.__symbols :
      el = find_element_by_symbol(symbol)
      
      if el is not None :
        self._elements.append(copy.deepcopy(el))
        
      else :
        self._raise(r'Unknown element with symbol "%s"' % symbol)

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'XMolXYZFileParser(%s)' % repr(self._filename)

  def get_description() :
    """Get the description of the parser."""
    return 'XMol XYZ Files'

  get_description = staticmethod(get_description)


class Aces2OutputParser(AbstractFileParser) :
  """Parser for ACESII output files.

  Outputs of frequency calculation tasks can contain the cartesian hessian.

  The class in *under construction* -- use at your own risk.

  The following read-only property is exposed :
      hessian -- hessian matrix (None if not available)
  
  """
  
  def __init__(self, filename) :
    """Constructor of the class.

    Positional arguments :
    filename -- file name or file object
    
    """
    AbstractFileParser.__init__(self, filename)      

  def _parse(self) :
    """Parse the file."""
    # number of read cartesian hessian elements, -1 - skip,
    # 0 - start reading
    ireadhes = -1
    ireadcoords = -1

    # reading the coordinate specification in a list
    coords_spec = []

    ## go
    self._hessian = None

    for line in self._file.readlines():
      line = line.strip()

      # ignoring the internal coordinate Hessian
      if -1 != line.find('Full internal coordinate Hessian:') :
        ireadhes = -1

      if -1 != ireadhes :
        pass
        # UNDER CONSTRUCTION
        #Aces2OutputParser.__read_hesval(line)

      if -1 != line.find("---------"):
        if 0 == ireadcoords:
          ireadcoords = 1

        elif 1 < ireadcoords:
          ireadcoords = -1

      if 0 < ireadcoords:
        vals = line.split()
        
        if 1 < ireadcoords :
          # skipping dummy atoms (labeled with X)
          if 5 == len(vals) and 'x' != vals[0].lower() :
            coords_spec.append(vals)
            
          else :
            self._raise(r'Invalid coordinates specification : "%s"' % line)
        
        ireadcoords = 1 + ireadcoords

      # start reading of the coordinates in bohrs after this line
      if -1 != line.find(
        'Symbol    Number           X              Y              Z') :
        ireadcoords = 0

      # reading only the cartesian Hessian
      if -1 != line.find('Full Cartesian Hessian:') :
        ireadhes = 0

    self._file.close()

    ## construct the coordinates and elements arrays
    if 0 == len(coords_spec) :
      self._raise('Coordinates were not found')
    
    self._Natoms   = len(coords_spec)
    self._coords   = zeros((1 + self._Natoms, 4), 'd')
    self._elements = [ None ]

    for a in xrange(1, 1 + self._Natoms) :
      la = coords_spec[a-1]

      # element
      if not la[1].isdigit() :
        self._raise('Invalid atom number : %s' % la[1])
      
      el = find_element_by_atomno(int(la[1]))

      if el is None :
        self._raise(
          'Element with the atom number %d cannot be found' % int(la[1]))

      self._elements.append(copy.deepcopy(el))

      # coordinates (recalculating in angstrom !)
      try :
        self._coords[a][1:] = [ float(v) * BOHR2ANGSTROM for v in la[2:] ]
        
      except ValueError :
        self._raise('Could not read the coordinates for atom %d' % a)

  def __read_hesval(self, line):
    """UNDER CONTRUCTION.
    
    Process the hessian line:
	[  1,  1]  0.000000 [  2,  1]  0.000000 [  2,  2]  0.658898 \
	[  3,  1]  0.000000
	
    """
    n_openbracket = line.count("[")
    n_closebracket = line.count("]")

    if -1 != n_openbracket and -1 != n_closebracket :
      istart = line.find("[")
      
      while -1 != istart:
        next_bracket = line.find("[", 1 + istart)
        iend = next_bracket

        if -1 == next_bracket:
          iend = len(line)
      
        # to skip "[" in the last string
        if 1 < iend - istart :
          element = line[istart:iend]
          i, j, value = self.__parse_val(element)
          a, q_a = rests(i)
          b, q_b = rests(j)

          # assign if it is not a dummy atom
          # dummy atoms are not present in self.real_no
##          if 0 != self.real_no.count(a) and 0 != self.real_no.count(b) :
##            a_real = self.real_no.index(a)
##            b_real = self.real_no.index(b)
##
##            self._hessian[a_real][q_a][b_real][q_b] = value
##            self._hessian[b_real][q_b][a_real][q_a] = \
##              self._hessian[a_real][q_a][b_real][q_b]

        istart = next_bracket

  def __parse_val(data):
    """Parse : [  i,  j]  value.
    
    Return i, j, value.
    
    """
    iopen  = data.find("[")
    iclose = data.find("]")
    ikomma = data.find(",")

    i = int( data[1 + iopen:ikomma].strip() )
    j = int( data[1 + ikomma:iclose].strip() )
    value = float( data[1 + iclose:len(data)].strip() )

    return i, j, value

  __parse_val = staticmethod(__parse_val)

  def _validate(self) :
    """Validate the read data."""
    pass

  def _declare_properties(self) :
    """Declare properties of the parser."""
    AbstractFileParser._declare_properties(self)

    self._add_property('hessian', readonly=True)

  def get_description() :
    """Get the description of the parser."""
    return 'ACESII Output File'

  get_description = staticmethod(get_description)


class HESFileParser(AbstractFileParser) :
  """Parser for cartesian hessian files of DALTON (*.hes).

  The following read-only properties are exposed :
      hessian -- hessian matrix
      
  """  
  
  def __init__(self, hesfile):
    """Constructor of the class.

    Positional arguments :
    hesfile -- file name

    """
    AbstractFileParser.__init__(self, hesfile)

  def _parse(self):
    """Parse the file."""
    # first line - dimension of Hessian
    dim = self._file.readline().strip()
    
    if not dim.isdigit() :
      self._raise(r'Invalid dimension of the hessian : "%s"' % dim)

    # dim = 3*Natoms
    dim = int(dim)
    if 3 > dim or 0 != dim % 3 :
      self._raise(r'Invalid dimension of the hessian : "%d"' % dim)
    
    self._Natoms  = dim / 3
    self._hessian = zeros((1 + self._Natoms, 4, 1 + self._Natoms, 4), 'd')
    self._coords  = zeros((1 + self._Natoms, 4), 'd')

    #
    row_number    = 0
    column_number = 0

    for line in self._file.readlines():
      # recognize a non-empty string
      if 0 != len(line.strip()) :
        row_number += 1
        
        if 0 == (row_number - 1) % dim:
          column_number += 1

        # Hessian values
        if column_number <= dim :
          rest1 = rests((row_number - 1) % dim + 1)
          rest2 = rests(column_number)
          self._hessian[rest1[0], rest1[1], rest2[0], rest2[1]] = float(line)
          
        # Coordinates
        else:
          rest = rests((row_number - 1) % dim + 1)
          self._coords[rest[0], rest[1]] = float(line) * BOHR2ANGSTROM

    # close properly
    self._file.close()

  def _validate(self) :
    """Validate the read data."""
    pass

  def _declare_properties(self) :
    """Declare properties of the parser."""
    for prop in ('Natoms', 'coords', 'hessian') :
      self._add_property(prop, readonly=True)

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'HESFileParser(%s)' % repr(self._filename)

  def get_description() :
    """Get the description of the parser."""
    return 'Hessian File for DALTON 1.x and 2.0'

  get_description = staticmethod(get_description)  


class NumericDataFileParser(PropertiesContainer) :
  """Parser for files containing only numbers.

  The following read-only property is exposed :
      data -- read data as ndarray

  """

  def __init__(self, filename, ncols=None) :
    """Constructor of the class.

    Positional arguments :
    filename -- file name

    Keyword arguments :
    ncols    -- number of columns to be read (default None)

    """
    self._filename = filename
    self._ncols    = ncols

    self._parse()

    PropertiesContainer.__init__(self, modulename='pyviblib.io.parsers')    

  def _parse(self) :
    """Parse the file."""
    file_ = open(self._filename)

    lines = file_.readlines()    
    # first line could be a comment
    try :
      self.__parse_line(lines[0])
    except :
      start_index = 1
    else :
      start_index = 0

    data = []    
    for line in lines[start_index:] :
      data.append(self.__parse_line(line.strip()))

    file_.close()
    self._data = array(data, 'd')

  def _check_consistency(self) :
    """Check the input data."""
    if self._ncols is not None and \
       ( not isinstance(self._ncols, int) or 0 >= self._ncols ) :
      raise ConstructorError('if given, ncols must be a positive number')

  def _declare_properties(self) :
    """Declare properties."""
    self._add_property('data', readonly=True)

  def __parse_line(self, line) :
    """Parse a line that must contain ncols float numbers."""
    vals = line.split()
    
    if self._ncols is not None and self._ncols != len(vals) :
      raise ParseError(
        self._filename,               
        r'The line "%s" must have exactly %d fields' % (line, self._ncols))

    try :
      nums = [ float(val) for val in vals ]
      
    except ValueError :
      raise ParseError(
        self._filename,
        r'The line "%s" could not be parsed' % line)
    
    else :
      return nums

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'NumericDataFileParser(%s, ncols=%s)' % \
           (repr(self._filename), repr(self._ncols))


class FittedSpectraFileParser(NumericDataFileParser) :
  """Parser for fitted spectra files of VOAPlot 4.2+.

  This is *not* a subclass of AbstractFileParser.

  The most important columns of fitted spectra files are :
    nu      raman     roa     degree_of_circularity

  The following read-only properties are exposed :
      type          -- type of the spectrum
      molecule_name -- the molecule name
      data          -- matrix with all read data
      Npoints       -- number of points read
    
  """

  def __init__(self, filename) :
    """Constructor of the class.

    Positional arguments :
    filename -- file name

    """
    NumericDataFileParser.__init__(self, filename)

  def _parse(self) :
    """Parse the file."""
    # the base class implementation should do the job :)
    NumericDataFileParser._parse(self)

    # FitX_molname.dat
    # try to define the type of the spectrum
    # and the name of a molecule
    # X = 1 -> backward scattering
    # X = 2 -> forward scattering
    # X = 3 -> 90 grad scattering 1
    # X = 4 -> 90 grad scattering 2
    # X = 5 -> ? integral cross-sections ?
    basename_ = os.path.basename(self._filename)
    
    if 5 <= len(basename_) and basename_.startswith('Fit') and \
       basename_[3].isdigit() :      
      X = int(basename_[3])
      # type
      if 1 == X :          
        self._type = 'backward'
      elif 2 == X :
        self._type = 'forward'
      elif 3 == X :
        self._type = '90 grad / perpendicular'
      elif 4 == X :
        self._type = '90 grad / parallel'
      elif 5 == X :
        self._type = 'integral cross section'
      else :
        self._type = 'unknown'

      # molecule name
      if basename_.lower().endswith('.dat') :
        read_to_index = basename_.lower().rfind('.dat')
        self._molecule_name = basename_[5:read_to_index]
      else :
        self._molecule_name = 'unknown'
          
    else :
      self._type          = 'unknown'
      self._molecule_name = 'unknown'

  def _declare_properties(self) :
    """Declare properties of the parser."""
    for prop in ('type', 'molecule_name', 'data') :
      self._add_property(prop, readonly=True)

    self.__class__.Npoints = property(self.__get_Npoints)

  def __get_Npoints(obj) :
    """Getter function for the Npoints property."""
    return obj._data.shape[0]

  __get_Npoints = staticmethod(__get_Npoints)

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'FittedSpectraFileParser(%s)' % repr(self._filename)
    

class FCMINTFileParser(NumericDataFileParser) :
  """Parser for cartesian hessian files of AcesII (FCMINT).

  The following read-only properties are exposed :
      Natoms  -- number of atoms
      hessian -- hessian
  
  """
  
  def __init__(self, filename):
    """Constructor of the class.

    Positional arguments :
    filename -- file name

    """
    NumericDataFileParser.__init__(self, filename)

  def _parse(self):
    """Parse the file."""
    f = open(self._filename)
    lines = f.readlines()
    f.close()

    self._Natoms = self.__calcNatoms(lines)
    self._hessian = zeros((1 + self._Natoms, 4, 1 + self._Natoms, 4), 'd')

    no = 0
    for line in lines :
      vals = line.strip().split()

      for val in vals :
        val = float(val)
        no += 1

        a, i, b, j = self.__getpos(self._Natoms, no)
        self._hessian[a, i, b, j] = val

  def _declare_properties(self) :
    """Declare properties of the parser."""
    for prop in ('Natoms', 'hessian') :
      self._add_property(prop, readonly=True)

  def __getpos(Natoms, no):
    """Return a, i, b, j for the hessian.
    
    no - is a number of read element
    
    """
    q = int((no - 1) / (3 * Natoms)) + 1
    
    a = int((q - 1) / 3) + 1
    i = q - 3 * (a - 1)

    b = int((no - 1) / 3) + 1 - Natoms * (q - 1)
    j = no - 3 * int( (no - 1) / 3 ) 

    return a, i, b, j

  __getpos = staticmethod(__getpos)

  def __calcNatoms(lines) :
    """Calculate the number of atoms.

    Natoms = sqrt(Nall) / 3
    
    """
    count = 0
    for line in lines :
      count += len(line.strip().split())

    return int(sqrt(count) / 3)

  __calcNatoms = staticmethod(__calcNatoms)
          
  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'FCMINTFileParser(%s)' % repr(self._filename)
