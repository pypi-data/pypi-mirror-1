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

"""This is the pyviblib.util package.

The following modules are exported :
    constants    -- physical constants and conversion factors
    exceptions   -- exceptions which are raised in pyviblib
    misc         -- miscellaneous
    pse          -- handling chemical elements

The following resource files are located in the package directory :
    pse.dat      -- properties of the elements
    isotopes.dat -- information about the isotopes of the elements
    
"""
__author__ = 'Maxim Fedorovsky'

__all__ = ['constants', 'exceptions', 'misc', 'pse']
