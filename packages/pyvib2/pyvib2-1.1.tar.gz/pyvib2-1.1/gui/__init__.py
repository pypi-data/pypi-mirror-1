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

"""This is the pyviblib.gui package.

The package is a collection of the GUI components of PyVib2.

The following modules are exported :
    widgets   --  GUI building blocks of the windows and dialogs of PyVib2
    main      --  main window of PyVib2
    windows   --  windows
    dialogs   --  dialogs
    images    --  image resources
    resources --  string resources of PyVib2
    rendering --  classes for 3D rendering based on VTK
    figures   --  classes for plotting based on Matplotlib
    
"""
__author__ = 'Maxim Fedorovsky'

__all__ = ['widgets', 'main', 'windows', 'dialogs',
           'images', 'resources','rendering', 'figures']
