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

"""This is the pyviblib.calc package.

The package is a collection of calculation routines used throughout the
pyviblib class library.

The following modules are exported :
    common      --  commonly used routines
    qtrfit      --  superimpose molecules using a quaternion fit
    spectra     --  Raman/ROA as well as IR/VCD spectra generation
    vibrations  --  handling vibrational motion

"""
__author__ = 'Maxim Fedorovsky'

__all__ = ['common', 'qtrfit', 'spectra', 'vibrations']
