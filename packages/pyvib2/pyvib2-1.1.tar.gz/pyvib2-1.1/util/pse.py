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

"""Module for handling chemical elements.

The following classes are exported :
    Material                          -- apearance of a chemical element
    Element                           -- describing chemical elements

The following functions are exported :
    find_element_by_symbol()          -- find an element by its symbol
    find_element_by_atomno()          -- find an element by its atomic number
    find_element_by_isotope()         -- find an element by its isotope mass
    find_element_by_standard_weight() -- find an element by its standard weight
    find_isotopes()                   -- find the isotopes of an element

"""
__author__ = 'Maxim Fedorovsky'

from math import fabs
import os.path

from pyviblib import get_rootdir
from pyviblib.util.misc        import color_html_to_RGB, Command
from pyviblib.util.exceptions  import ConstructorError, ParseError

__all__ = ['Material', 'Element',
           'find_element_by_symbol', 'find_element_by_atomno',
           'find_element_by_isotope', 'find_element_by_standard_weight',
           'find_isotopes']

## Internal list of known chemical __elements__
__elements__ = None

## Internal dictionary with known __isotopes__
__isotopes__ = None


class Material(object) :
  """Class for describing appearance of a chemical element.

  The following readable and writable properties are exposed :
      diffuse_color  -- diffuse color, i.e. color when illuminated
      specular_color -- specular color (highlights)
      ambient_color  -- ambient color, i.e. color reflected off the surface
      
  """
  
  def __init__(self,
               diffuse_color=(1., 1., 1.),
               specular_color=(1., 1., 1.),
               ambient_color=(0., 0., 0.)) :
    """Constructor of the class.
    
    Each color is given as a tuple with the RGB values ranged from 0. to 1.
    
    Keyword arguments :
    diffuse_color  -- diffuse color  (default (1., 1., 1.), i.e. white)
    specular_color -- specular color (default (1., 1., 1.), i.e. white)
    ambient_color  -- ambient color (default (0., 0., 0.), i.e. black)
    
    """
    self._diffuse_color  = diffuse_color
    self._specular_color = specular_color
    self._ambient_color  = ambient_color

    # create properties
    for prop in ('diffuse_color', 'specular_color', 'ambient_color') :
      exec 'self.__class__.%s = property(' % prop + \
           r'fget=Command(Command.fget_attr, "_%s"),' % prop + \
           r'fset=Command(Command.fset_attr, "_%s"))' % prop

  def __eq__(self, material) :
    """Compare two materials."""
    return isinstance(material, Material) and \
           self._diffuse_color  == material.diffuse_color and \
           self._specular_color == material.specular_color and \
           self._ambient_color  == material.ambient_color

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'Material(diffuse_color=%s, specular_color=%s, ambient_color=%s)' \
           % (repr(self._diffuse_color),
              repr(self._specular_color),
              repr(self._ambient_color))

class Element(object) :
  """Describing chemical elements.

  The following properties are exposed :
      atomno          -- atomic number
      symbol          -- symbol
      standard_weight -- standard weight in a.m.u.
      r_coval         -- covalent radius in angstrom
      r_vdw           -- van der Waals radius in angstrom
      material        -- material, see Material
      isotopes        -- tuple with the known isotopes
      mass            -- mass in a.m.u. (*)
      isotopno        -- number of the isotope (*)

  Properties marked with an asterisk are also writable.
      
  """

  def __init__(self, atomno, symbol, standard_weight,
               r_coval, r_vdw, material=Material()) :
    """Constructor of the class.

    Positional arguments :
    atomno          -- atomic number
    symbol          -- symbol
    standard_weight -- standard weight in a.m.u.
    r_coval         -- covalent radius in angstrom
    r_vdw           -- van der Waals radius in angstrom    

    Keyword arguments :
    material        -- material (default Material())
    
    """
    self._atomno              = atomno
    self._symbol              = symbol
    self._mass                = None
    self._standard_weight     = standard_weight
    self._r_coval             = r_coval
    self._r_vdw               = r_vdw
    self._material            = material

    # find __isotopes__ & quit if failed
    self._isotopno = 0
    self._isotopes = find_isotopes(self._atomno)
    
    if self._isotopes is None :
      raise ConstructorError('Cannot find any isotopes for the element')

    # create read-only properties
    for prop in ('atomno', 'symbol', 'standard_weight',
                 'r_coval', 'r_vdw', 'material', 'isotopes') :
      exec 'self.__class__.%s = property(' % prop + \
           r'fget=Command(Command.fget_attr, "_%s"))' % prop

    # create two writable properties
    self.__class__.mass = property(fget=self._get_mass,
                                   fset=Command(Command.fset_attr, '_mass'))

    # isotope number writable property (0 by default)
    self.__class__.isotopno = property(
      fget=Command(Command.fget_attr, '_isotopno'),
      fset=Command(Command.fset_attr, '_isotopno'))

  def _get_mass(obj) :
    """Getter function for the mass property.

    By default it is the mass of its most stable isotope.
    
    """
    if obj._mass is not None :
      return obj._mass

    obj._mass = obj._isotopes[0]  
    return obj._mass

  _get_mass = staticmethod(_get_mass)

  def __eq__(self, elem) :
    """Comparing two elements."""
    return self._atomno == elem.atomno and \
           self._symbol == elem.symbol and \
           self._standard_weight == elem.standard_weight and \
           self._r_coval == elem.r_coval and \
           self._r_vdw == elem.r_vdw
    

def __load_elements() :
  """Load the information in __elements__ from pse.dat."""
  global __elements__

  # do nothing if already initialized
  if __elements__ is not None :
    return

  pse_filename = os.path.join(str(get_rootdir()), 'util', 'pse.dat')
  
  try :    
    pse_file     = open(pse_filename)    
  except IOError :
    __elements__ = None
    raise RuntimeError('Could not open pse.dat')

  atomno  = 0
  symbol  = ""
  mass    = .0
  r_coval = .0
  r_vdw   = .0
  diff    = None
  spec    = None
  amb     = None

  for line in pse_file.readlines() :
    line = line.strip()

    if 0 == len(line) or line.startswith('#'):
      continue
    
    vals = line.strip().split()

    if ( 6 > len(vals) or 8 < len(vals) ) :
      __elements__ = None
      raise ParseError(pse_filename,
                       'Each line of pse.dat must have from 6 to 8 fields')

    # reading values
    try :
      atomno = int(vals[0])
      
    except ValueError :
      __elements__ = None
      raise ParseError(pse_filename, 'Invalid atom number : %d' % vals[0])

    symbol = vals[1]

    try :
      mass    = float(vals[2])
      r_coval = float(vals[3])
      r_vdw   = float(vals[4])
      
    except ValueError :
      __elements__ = None
      raise ParseError(pse_filename, 'Invalid float value encountered')

    try :
      diff = color_html_to_RGB(vals[5])
      
      if 6 < len(vals) :
        spec  =     color_html_to_RGB(vals[6])
      if 8 == len(vals) :
        amb   =     color_html_to_RGB(vals[7])

    except ValueError :
      __elements__ = None
      raise ParseError(pse_filename,
                       'Could not read the colors for element %d' % atomno)

    # add a new element only on successfull reading
    if __elements__ is None :
      __elements__ = []

    if not spec :
      spec = (1., 1., 1.)

    if not amb :
      amb  = (.0, .0, .0)

    __elements__.append(Element(atomno, symbol, mass,
                               r_coval, r_vdw, Material(diff, spec, amb)))

  # finished reading
  pse_file.close()

def __load_isotopes() :
  """Load the information in __isotopes__ from isotopes.dat."""
  global __isotopes__

  if __isotopes__ is not None :
    return

  isotopes_filename = os.path.join(str(get_rootdir()), 'util', 'isotopes.dat')
  
  try :
    isotopes_file = open(isotopes_filename)
    
  except IOError :
    __isotopes__ = None
    raise ParseError(isotopes_filename,
                     'Could not open isotopes.dat')

  for line in isotopes_file.readlines() :
    line = line.strip()
    
    if 0 == len(line) or line.startswith('#') :
      continue

    vals = line.split()

    if 1 == len(vals) :
      raise ParseError(isotopes_filename, 'Invalid format')

    # atom number
    try :
      atomno = int(vals[0])      
    except ValueError :
      raise ParseError(isotopes_filename,
                       r'Could not read the atom number from : "%s"' % line)

    # isotop masses
    i_masses = []
    try :
      for i in xrange(1, len(vals)) :
        vals[i] = float(vals[i])
        
        if 0. > vals[i] :
          raise ParseError(isotopes_filename,
                           'Invalid isotope mass: %f' % vals[i])
        elif 0. < vals[i] :
          i_masses.append(vals[i])
          
    except ValueError :
      raise ParseError(isotopes_filename,
                       r'Could not read isotops from : "%s"' % line)

    # adding only after successfull reading
    if __isotopes__ is None :
      __isotopes__ = {}

    __isotopes__[atomno] = tuple(i_masses)
    
  # finished reading
  isotopes_file.close()


def find_element_by_standard_weight(standard_weight, threshold=0.001) :
  """Find an element by its standard weight.
  
  Positional arguments :
  standard_weight -- standard weight in a.m.u.

  Keyword arguments :
  threshold       -- tolerance for searching (default 0.001)

  Return None if not found.
  
  """
  if 0. >= standard_weight or __elements__ is None :
    return None
  
  element = None
  for elem in __elements__ :
    if threshold > fabs(elem.standard_weight - standard_weight) :
      element = elem
      break

  return element

def find_element_by_isotope(isotope_mass, threshold=0.001) :
  """Find an element by its isotope mass.
  
  Positional arguments :
  isotope_mass -- isotope mass in a.m.u.

  Keyword arguments :
  threshold    -- tolerance for searching (default 0.001)

  Return None if not found.
  
  """
  if 0. >= isotope_mass or __isotopes__ is None :
    return None
  
  element = None
  
  for atomno in __isotopes__.keys() :
    for mass in __isotopes__[atomno] :
      if threshold > fabs(mass - isotope_mass) :
        element = find_element_by_atomno(atomno)
        # new : isotop number
        element.isotopno = list(__isotopes__[atomno]).index(mass)
        break

  return element  

def find_element_by_symbol(symbol) :
  """Find an element by its symbol.
  
  Positional arguments :
  symbol -- symbol

  Return None if not found.

  """
  if symbol is None or '' == symbol or __elements__ is None :
    return None
  
  element = None
  for elem in __elements__ :
    # comparison must be case insensitive !
    if elem.symbol.upper() == symbol.upper() :
      element = elem
      break

  return element

def find_isotopes(atomno) :
  """Find the isotopes of an element.
  
  Return a tuple with the masses (in a.m.u) of the known isotopes.
  Return None if not found.
  
  """
  global __isotopes__

  if __isotopes__ is None :
    __load_isotopes()
  
  if 1 > atomno or not __isotopes__ :
    return None

  if atomno in __isotopes__ :
    return __isotopes__[atomno]
  
  else :
    return None

def find_element_by_atomno(atomno) :
  """Find an element by its atomic number.
  
  Positional arguments :
  atomno -- atomic number

  Return None if not found.
  
  """
  if atomno is None or 1 > atomno or __elements__ is None :
    return None
  
  element = None
  for elem in __elements__ :
    if elem.atomno == atomno :
      element = elem
      break

  return element


# Load elements and isotopes from pse.dat and isotopes.dat
__load_elements()
__load_isotopes()
