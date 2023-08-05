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

"""This is the root package of the class library.

The following modules are exported :
    molecule      -- handling molecules

The following subpackages are exported :
    calc          -- calculation routines
    gui           -- elements of the graphical user interface of PyVib2
    io            -- parsing and writing data
    util          -- utility modules

The following function is exported :
    get_rootdir() -- get the root directory of pyviblib

"""
__author__ = 'Maxim Fedorovsky'

import sys
import os.path


__all__ = ['molecule', 'get_rootdir']

AUTHOR        = __author__
AUTHOR_EMAIL  = 'Maxim.Fedorovsky@unifr.ch; mutable@yandex.ru'
VERSION_MAJOR = '1'
VERSION_MINOR = '1'
VERSION_PATCH =  None
VERSION       = '%s.%s%s' % (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH or '')
DEPLOY_TIME   = 'Thu, 05 Apr 2007 10:39:32 +0200'
APPNAME       = 'PyVib2'
UNIXNAME      = 'pyvib2'
DESCRIPTION   = 'A program for analyzing vibrational motion '\
                'and vibrational spectra'
COPYRIGHT     = 'Copyright (c) 2007 Maxim Fedorovsky, '\
                'University of Fribourg (Switzerland)'
CONTACT       = 'email : %s' % AUTHOR_EMAIL
URL           = 'http://pyvib2.sourceforge.net'
DOWNLOAD_URL  = \
          'http://sourceforge.net/project/platformdownload.php?group_id=190160'
LICENSE       = 'GNU GPL'


def get_rootdir() :
  """Get the root directory of pyviblib."""
  # looking for the doc/ and util/ directories
  curdir = os.path.dirname(__file__)
  
  if os.path.isdir(os.path.join(curdir, 'doc')) and \
     os.path.isdir(os.path.join(curdir, 'util')) :
    return curdir

  else :
    # using pyvib2.exe frozen with py2exe ?
    if getattr(sys, 'frozen', None) :
      curdir = os.path.split(sys.path[0])[0]

      if os.path.isdir(os.path.join(curdir, 'pyviblibdata', 'doc')) and \
         os.path.isdir(os.path.join(curdir, 'pyviblibdata', 'util')) :
        return os.path.join(curdir, 'pyviblibdata')
      # give in
      else :
        return None

    # give in
    else :
      return None
