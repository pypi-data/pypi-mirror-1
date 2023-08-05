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

"""Exceptions which are raised in pyviblib.

The following classes are exported :
    InvalidArgumentError   -- function received an invalid argument
    IOOperationError       -- input/output operations
    ConstructorError       -- constructor called with invalid arguments
    ParseError             -- errors by parsing
    WriteError             -- errors by writing
    DataInconsistencyError -- inconsistency in data found
    
"""
__author__ = 'Maxim Fedorovsky'

__all__ = ['InvalidArgumentError', 'IOOperationError', 'ConstructorError',
           'ParseError', 'WriteError', 'DataInconsistencyError']


class InvalidArgumentError(ValueError) :
  """Raised when a function received an invalid argument."""

  def __init__(self, desc) :
    """Constructor of the class.

    Positional arguments :
    desc -- description
    
    """
    ValueError.__init__(self)
    self._desc = desc

  def __str__(self) :
    """Details."""
    return r'Exception during the function call : "%s".' % self._desc

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'InvalidArgumentError(%s)' % repr(self._desc)


class IOOperationError(IOError) :
  """Raised when an error occurs by input/output operations."""
  
  def __init__(self, filename, desc) :
    """Constructor of the class.

    Positional arguments :
    filename -- file name where the exception occured
    desc     -- description
    
    """
    IOError.__init__(self)
    
    self._filename = filename
    self._desc     = desc

  def __str__(self) :
    """Details."""
    return r'Input/output error : "%s".' % self._desc    

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'IOOperationError(%s, %s)' % \
           (repr(self._filename), repr(self._desc))


class ConstructorError(InvalidArgumentError) :
  """Raised if the constructor of a class called with invalid arguments."""

  def __init__(self, desc) :
    """Constructor of the class.

    Positional arguments :
    desc -- description
    
    """
    InvalidArgumentError.__init__(self, desc)

  def __str__(self) :
    """Details."""
    return r'Exception during the constructor call : "%s".' % self._desc

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'ConstructorError(%s)' % repr(self._desc)


class ParseError(IOOperationError) :
  """Raised when an error occurs by parsing."""
 
  def __init__(self, filename, desc) :
    """Constructor of the class.

    Positional arguments :
    filename -- file name where the exception occured
    desc     -- description
        
    """
    IOOperationError.__init__(self, filename, desc)

  def __str__(self) :
    """Details."""
    return r'Error by parsing "%s" : "%s".' % (self._filename, self._desc)

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'ParseError(%s, %s)' % (repr(self._filename), repr(self._desc))


class WriteError(IOOperationError) :
  """Raised when an error occurs by writing."""
 
  def __init__(self, filename, desc) :
    """Constructor of the class.

    Positional arguments :
    filename -- file name where the exception occured
    desc     -- description
    
    """
    IOOperationError.__init__(self, filename, desc)

  def __str__(self) :
    """Details."""
    return r'Error by writing "%s" : "%s".' % (self._filename, self._desc)

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'WriteError(%s, %s)' % (repr(self._filename), repr(self._desc))


class DataInconsistencyError(ValueError) :
  """Raised when an inconsistency found in data."""

  def __init__(self, desc) :
    """Constructor of the class.

    Positional arguments :
    desc -- description
    
    """
    ValueError.__init__(self)
    self._desc = desc

  def __str__(self) :
    """Details."""
    return r'Inconsistency found : "%s".' % self._desc

  def __repr__(self) :
    """Can be used to recreate an object with the same value."""
    return 'DataInconsistencyError(%s)' % repr(self._desc)
