#!/usr/bin/python

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

"""PyVib2 setup script.

PyVib2 is a program for analyzing vibrational motion and vibrational
spectra, written in pure Python. The program was developed by
Maxim Fedorovsky during his Ph.D. thesis work in Prof. Werner Hug's research
group. PyVib2 permits the automatic correlation of vibrational motions of
molecules thereby allowing an understanding of Raman, Raman optical
activity (ROA), infrared vibrational absorption (IR), and vibrational
circular dichroism (VCD) spectra. The versatile representation of
vibrational motions, the visualization techniques of Raman/ROA and
IR/VCD generation in molecules and the production of publication quality
spectra, are features of PyVib2.

Output files of Raman/ROA and IR/VCD calculations, produced with the
DALTON and Gaussian quantum chemistry packages, can be directly opened.
Files in the MOLDEN and XMol XYZ format can be imported and exported.
A variety of formats (JPEG, TIFF, PNG, PNM, PS, PDF, Animated GIF, FLI)
are available to the user for saving results. 

All the functionalities are accessible via the pyviblib class library.
    
"""
__author__ = 'Maxim Fedorovsky'

import os.path
from glob import glob
from distutils.core import setup
from distutils import  sysconfig

from  __init__  import  UNIXNAME, VERSION, AUTHOR_EMAIL, \
                        URL, DOWNLOAD_URL, LICENSE, DESCRIPTION


__packages__ = ['pyviblib', 'pyviblib.calc', 'pyviblib.gui',
                'pyviblib.io', 'pyviblib.util']

# done for Python 2.3
__pyviblib_installdir__ = os.path.join(sysconfig.get_python_lib(), 'pyviblib')

__data_files__ = [
    (os.path.join(__pyviblib_installdir__, 'util'), glob('util/*.dat')),
    (os.path.join(__pyviblib_installdir__, 'doc'),  glob('doc/*.html'))]

# list of categories
# see http://cheeseshop.python.org/pypi?:action=list_classifiers
__classifiers__ = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License (GPL)
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering :: Chemistry
Topic :: Scientific/Engineering :: Visualization
Natural Language :: English
"""
    
__scripts__    = ['pyvib2']

setup(name             = UNIXNAME,
      version          = VERSION,
      author           = __author__,
      author_email     = AUTHOR_EMAIL,
      url              = URL,
      download_url     = DOWNLOAD_URL,
      license          = LICENSE,
      platforms        = 'Any',
      description      = DESCRIPTION,
      long_description = '\n'.join(__doc__.split('\n')[1:]),
      classifiers      = filter(None, __classifiers__.split('\n')),
      packages         = __packages__,
      package_dir      = {'pyviblib' : ''},
      data_files       = __data_files__,
      scripts          = __scripts__)
