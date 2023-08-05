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

"""Miscellaneous operations.

The following classes are exported :
    SmartDict                  -- container for storage of overridable options
    Command                    -- emulator of lambda functions
    PropertiesContainer        -- class for exposing properties via attributes

The following functions are exported :
    random_color()             -- generate a random color
    color_html_to_RGB()        -- convert a color in the HTML format to RGB
    color_RGB_to_html()        -- convert a color in the RGB format to HTML
    color_complementary()      -- generate the complementary of a color
    gen_molecule_name()        -- generate the molecule name
    save_matrix()              -- save a matrix
    ps2pdf()                   -- convert a PS or EPS file to the PDF format.

"""
__author__ = 'Maxim Fedorovsky'

import os
import os.path
from random import seed, randint

from numpy import ndarray, array

from pyviblib.util.exceptions import InvalidArgumentError, ConstructorError

__all__ = ['SmartDict', 'Command', 'PropertiesContainer',
           'random_color', 'color_html_to_RGB', 'color_RGB_to_html',
           'color_complementary', 'gen_molecule_name', 'save_matrix', 'ps2pdf']


class SmartDict(dict) :
  """A container for a convenient storage of overridable options.

  The class is based on the Python builtin dictionary. It is made up of two
  containers for the options : internal dictionary for their default values
  and a second dictionary, where the options are searched first. The former is
  refered as the default dictionary and the latter as the reference dictionary.

  The following readable and writable property is exposed :
      kw        -- reference dictionary

  The following public methods are exported :
      update_() -- update the reference dictionary
      merge()   -- overwrite the default dictionary with the reference one
      
  """

  def __init__(self, mapping_or_sequence=None, kw=None, default_value=None) :
    """Constructor of the class.

    Keyword arguments :
    mapping_or_sequence -- initial contents of the default dictionary
                           (default : None, i.e. empty sequence)
    kw                  -- reference dictionary (default None) 
    default_value       -- returned if a key is found in neither in the default
                           nor in the reference dictionary (default None)
    
    """
    dict.__init__(self, mapping_or_sequence or {})

    self._kw = kw
    self._default_value = default_value
    self._mapping_or_sequence = mapping_or_sequence

    self.__class__.kw = property(fget=Command(Command.fget_attr, '_kw'),
                                 fset=Command(Command.fset_attr, '_kw'))

  def __getitem__(self, key) :
    """Overridden subscripting operator."""    
    if self._kw is not None and key in self._kw :
      return self._kw[key]
    else :
      return self.get(key, self._default_value)

  def __delitem__(self, key) :
    """Delete a key from the default dictionary.

    Positional arguments :
    key -- key to be deleted 

    Nothing is done if the key does not exist.

    """
    if key in self :
      dict.__delitem__(self, key)

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'SmartDict(mapping_or_sequence=%s, kw=%s, default_value=%s)' % \
           (repr(self._mapping_or_sequence),
            repr(self._kw),
            repr(self._default_value))

  def update_(self, kw) :
    """Update the reference dictionary.

    If it is not defined, update the default dictionary.

    Positional arguments :
    kw -- dictionary to update with

    """
    if self._kw is not None :
      self._kw.update(kw)      
    else :
      self.update(kw)
  
  def merge(self) :
    """Update the default dictionary with the reference one."""
    self.update(self._kw)


class Command :
  """Emulator of lambda functions.

  The idea is taken from H.P. Langtangen, Python Scripting for Computational
  Science. Springer Verlag Berlin Heidelberg, 2004. p. 519.
  
  """

  def __init__(self, func, *args, **kwargs) :
    """Constructor of the class.

    Positional arguments :
    func   -- function to be called
              must be callable, otherwise an exception is raised
    args   -- positional arguments to the function

    Keyword arguments :
    kwargs -- keyword arguments to the function

    """
    if not callable(func) :
      raise ConstructorError('Function must be callable!')
    
    self.__func   = func
    self.__args   = args
    self.__kwargs = kwargs

  def __call__(self, *args, **kwargs) :
    """Emulate a call of the function supplied in the constructor.

    Positional arguments are obtained by appending args to the ones
    supplied in the constructor. The keywords arguments are the ones supplied
    in the constructor updated by kwargs.

    """
    args = args + self.__args
    kwargs.update(self.__kwargs)
    
    return self.__func(*args, **kwargs)

  def fget_value(obj, value) :
    """Emulate a fget function used by definition of a property (via value).

    This is a static method of the class.

    Positional arguments :
    obj   -- supposed to be the first argument of the fget function
    value -- value to return
    
    """
    return value

  fget_value = staticmethod(fget_value)

  def fget_attr(obj, name) :
    """Emulate a fget function used by definition of a property (via attribute).

    This is a static method of the class.

    Positional arguments :
    obj  -- supposed to be the first argument of the fget function
    name -- name of the attribute
    
    """
    return getattr(obj, name)

  fget_attr = staticmethod(fget_attr)

  def fset_attr(obj, value, name) :
    """Emulate a fset function used by definition of a property.

    This is a static method of the class.

    Positional arguments :
    obj   -- object
    value -- value of the attribute to be set
    name  -- attribute of the object to be set
    
    """
    setattr(obj, name, value)
    
  fset_attr = staticmethod(fset_attr)


class PropertiesContainer(object) :
  """Class for exposing properties via attributes.

  The following protected methods are called in the constructor :
      _check_consistency()  -- check the consistency of the data passed
      _declare_properties() -- declare properties

  The following protected method should be used for adding properties :
      _add_property()       -- expose a given class attribute as a property
  
  """
  def __init__(self, modulename=None) :
    """Constructor of the class.

    Keyword arguments :
    modulename -- name of the package where the class is located (default None)
               if not None, import that package first

    """
    self._modulename = modulename
    
    self._check_consistency()
    self._declare_properties()

  def _check_consistency(self) :
    """Check consistency of the data passed to the constructor."""
    pass

  def _declare_properties(self) :
    """Declare properties of the class."""
    pass

  def _add_property(self, name, readonly=True, doc=None) :
    """Expose a given class attribute as a property.

    Positional arguments :
    name -- property name (self._name *must* exist)

    Keyword arguments :
    readonly -- whether the property should be read-only (default True)
    doc      -- docstring for the property (default None)
    
    """
    if name is None :
      raise InvalidArgumentError('Invalid property name')

    str_to_exec = ''
    if self._modulename is not None :
      str_to_exec = ''.join((str_to_exec,
                             r'from %s import %s; ' % \
                             (self._modulename, self.__class__.__name__)))

    str_to_exec = ''.join(
      (str_to_exec,
       r'%s.%s = property(fget=Command(Command.fget_attr, "_%s"),' % \
       (self.__class__.__name__, name, name)))

    if not readonly :
      str_to_exec = ''.join((str_to_exec,
                             r'fset=Command(Command.fset_attr, "_%s"),' % name))
                  
    str_to_exec = ''.join((str_to_exec, 'doc=doc)'))

    exec str_to_exec

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'PropertiesContainer(modulename=%s)' % repr(self._modulename)
  

def color_html_to_RGB(colorstr) :
  """Convert a color in the HTML format to RGB.
  
  Positional arguments :
  colorstr -- color in the HTML format e.g. '#FF0000'

  Return the tuple of float RGB values.
  
  """
  colorstr = str(colorstr).strip()
  
  if '#' != colorstr[0] or 7 != len(colorstr) :
    raise InvalidArgumentError('Invalid color supplied: %s' % colorstr)

  red, green, blue = colorstr[1:3], colorstr[3:5], colorstr[5:]
  return tuple([ float( int(n, 16) / 255. ) for n in (red, green, blue) ])

def color_RGB_to_html(rgb) :
  """Convert a color in the RGB format to HTML.
  
  Positional arguments :
  rgb --  tuple of float RGB values e.g. (1., 0., 0.)

  Return the color in the HTML format.
  
  """
  hex_color = '#'

  for elem in rgb :
    hex_color = ''.join((hex_color, '%.2x' % int(elem * 255)))
    
  return hex_color

def color_complementary(colorstr) :
  """Generate the complementary of a color.

  Positional arguments :
  colorstr -- color in the HTML format e.g. '#FF0000'

  Return the complementary color in the HTML format.

  """
  colorstr = str(colorstr).strip()
  
  if '#' != colorstr[0] or 7 != len(colorstr) :
    raise InvalidArgumentError('Invalid color supplied: %s' % colorstr)

  rgb = colorstr[1:3], colorstr[3:5], colorstr[5:]

  colorstr_compl = '#'
  for col in rgb :
    colorstr_compl = ''.join((colorstr_compl, '%.2X' % (255 - int(col, 16))))

  return colorstr_compl

def str_to_float(val, default=0.0) :
  """Convenient conversion from string to float.

  If the convertion is failed, return the default value.

  Positional arguments :
  val    -- string value to converted to float

  Keyword arguments :
  default -- float value to be returned on error (default 0.)
  
  """
  try :
    return float(val)  
  except ValueError :
    return default

def remove_indices_from_list(list_, indices) :
  """Remove indices from a list.

  Positional arguments :
  list_   -- list to be processed
  indices -- indices to be removed from the list

  No exception is raised if invalid indices are found.
  
  """
  if list_ is None or 0 == len(list_) or indices is None or 0 == len(indices) :
    return

  vals = []
  for i in indices :
    if 0 <= i and len(list_) > i :
      vals.append(list_[i])

  for val in vals :
    list_.remove(val)

def random_color() :
  """Generate a random color in the HTML format."""
  seed()

  color_html = '#%.2X%.2X%.2X' % \
               (randint(0, 255), randint(0, 255), randint(0, 255))

  return color_html

def save_matrix(mat, filename, value_format='%13.6f', base=1) :
  """Save a matrix.

  Positional arguments :
  mat          -- matrix to be saved (ndarray)
  filename     -- file name or file object to save to

  Keyword arguments :
  value_format -- format for writing elements of the matrix (default '%13.6f')
  base         -- start index of the matrix

  """
  if not isinstance(mat, ndarray) :
    raise InvalidArgumentError('Invalid matrix supplied')

  if not isinstance(filename, file) :
    file_ = open(filename, 'w+')
  else :
    file_ = filename

  for i in xrange(base, mat.shape[0]) :
    str_ = ''
    for j in xrange(base, mat.shape[1]) :
      str_ = ''.join((str_, ' ', value_format % mat[i, j], ' '))

    str_ = ''.join((str_, '\n'))
    file_.write(str_)

  if not isinstance(filename, file) :
    file_.close()
    
def unique(arr) :
  """Make a unique array.

  Positional arguments :
  arr -- input ndarray
  
  """
  if not isinstance(arr, ndarray) or 1 != len(arr.shape) :
    raise InvalidArgumentError('Invalid array supplied')

  if 1 == len(arr) :
    return arr[:1]

  unique_a = [arr[0]]
  for val in arr[1:] :
    if val not in unique_a :
      unique_a.append(val)

  return array(unique_a)
    
def is_command_on_path(cmd) :
  """Check whether a command is on the path.

  The function searches in directories specified by the PATH environmental
  variable.

  Positional arguments :
  cmd -- command name

  """
  if cmd is None or 'PATH' not in os.environ :
    return False
  
  for dir_ in os.environ['PATH'].split(os.path.pathsep) :
    if os.path.exists(os.path.join(dir_, cmd)) :
      return True

    # additional check under a Microsoft platform
    if os.name in ('nt', 'ce') :
      if not os.path.splitext(cmd)[1].lower() in ('.exe', '.com') :
        if os.path.exists(os.path.join(dir_, '%s.exe' % cmd)) or \
           os.path.exists(os.path.join(dir_, '%s.com' % cmd)) :
          return True

  return False

def ps2pdf(filesrc, removesrc=True, **options) :
  """Convert a PS or EPS file to the PDF format.
  
  This is done by calling ps2pdf.
  See http://www.cs.wisc.edu/~ghost/doc/AFPL/6.50/Ps2pdf.htm#Options

  Positional arguments :
  filesrc   -- PS or EPS to be converted to the PDF format

  Keyword arguments :
  removesrc -- remove the source file after the conversion (default True)
  options   -- any options recognized by ps2pdf

  Return the exit status of the os.system() call.
  
  """
  cmd = 'ps2pdf'

  if not is_command_on_path(cmd) :
    raise RuntimeError('ps2pdf must be on PATH.')

  for opt in options :
    cmd = ''.join((cmd, r' "-d%s=%s"' % (opt, options[opt])))

  # destination file
  base = os.path.splitext(filesrc)[0]
  filedest = r'%s.pdf' % base
  
  # executing
  cmd = ''.join((cmd, r' "%s" "%s"' % (filesrc, filedest)))
  status = not os.system(cmd)

  # remove upon successful conversion
  if status and removesrc :
    os.remove(filesrc)

  return status

def rests(num, divisor=3):
  """Retrieve atomno, i."""
  return 1 + (num - 1) / divisor, num - divisor * ((num - 1) / divisor)

def readconfig_option(cfp, section, option, default=None) :
  """Read an option from a section from a ConfigParser.

  If the option cannot be read or on error the function returns the default.

  Positional arguments :
  section -- name of the section
  option  -- name of the option

  Keyword arguments :
  default -- default value (default None)  

  """
  try :
    return cfp.get(section, option)

  except :
    return default

def gen_molecule_name(filename, maxchar=40) :
  """Generate the molecule name from the full path of a file.

  Keyword arguments :
  maxchar -- maximal number of characters in the molecule name (default : 40)
  
  """
  molname = os.path.basename(filename)
  ind = molname.rfind('.')

  if -1 != ind :
    molname = molname[0:ind]

  # removing 'pro_' and 'dal_' at the beginning
  if (molname.lower().startswith('pro_') or \
      molname.lower().startswith('dal_')) and 4 < len(molname) :
    molname = molname[4:]

  if isinstance(maxchar, int) and 0 < maxchar :
    molname = molname[:maxchar]

  return molname
