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

"""Resources used in PyVib2.

The following function is exported :
    get_font_molecules() -- optimal font for displaying names of molecules

The following prefices are used to identify the type of the resources :
    STRING_              -- string
    STRINGS_             -- tuple of strings
    NUM_                 -- number
    FONT_                -- font
    LIST_                -- list of objects

"""
__author__ = 'Maxim Fedorovsky'

from Pmw    import logicalfont
from tkFont import Font

import pyviblib
import pyviblib.io.parsers

## Maximal number of recent files
NUM_MAXRECENTFILES  =   13

## Descriptions of file types.
STRING_FILETYPE_ALLFILES_DESCRIPTION     = 'All Files'
STRING_FILETYPE_VOAVIEWFILE_DESCRIPTION  = \
                       pyviblib.io.parsers.VOAVIEWFileParser.get_description()
STRING_FILETYPE_FCHKFILE_DESCRIPTION     = \
                       pyviblib.io.parsers.FCHKFileParser.get_description()
STRING_FILETYPE_DALTONOUTPUT_DESCRIPTION = \
                       pyviblib.io.parsers.DaltonOutputParser.get_description()
STRING_FILETYPE_MOLDENFILE_DESCRIPTION   = \
                       pyviblib.io.parsers.MOLDENFileParser.get_description()
STRING_FILETYPE_XMOLXYZFILE_DESCRIPTION  = \
                       pyviblib.io.parsers.XMolXYZFileParser.get_description()
STRING_FILETYPE_GROUPFILE_DESCRIPTION    = 'Group Files'
STRING_FILETYPE_EPSFILE_DESCRIPTION      = 'PostScript / Encapsulated ' + \
                                           'PostScript Files'
STRING_FILETYPE_CSVFILE_DESCRIPTION      = 'Comma Separated Values Files'
STRING_FILETYPE_CAMERAFILE_DESCRIPTION   = '%s Camera Files' % pyviblib.APPNAME
STRING_FILETYPE_FLIFILE_DESCRIPTION      = 'Autodesk Animator Flic Files'
STRING_FILETYPE_FLIFILE_DESCRIPTION      = 'Autodesk Animator Flic Files'
STRING_FILETYPE_GIFFILE_DESCRIPTION      = 'CompuServe GIF Files'
STRING_FILETYPE_PNGFILE_DESCRIPTION      = 'Portable Network Graphic Files'
STRING_FILETYPE_JPEGFILE_DESCRIPTION     = 'Joint Photographic Experts ' + \
                                           'Group Files'
STRING_FILETYPE_TIFFFILE_DESCRIPTION     = 'Tagged Image File Format Files'
STRING_FILETYPE_PPMFILE_DESCRIPTION      = 'Netpbm Color Image Format Files'
STRING_FILETYPE_PDFFILE_DESCRIPTION      = 'Portable Document Format Files'
STRING_FILETYPE_GAUSSINFILE_DESCRIPTION  = 'Gaussian Input Files'
STRING_FILETYPE_PLTFILE_DESCRIPTION      = 'Instrument PLT files'
STRING_FILETYPE_TXTFILE_DESCRIPTION      = 'Text files'

## Supported file formats of input files of PyVib2
LIST_INPUT_FILETYPES = (
        (STRING_FILETYPE_ALLFILES_DESCRIPTION,     '*'),
        (STRING_FILETYPE_FCHKFILE_DESCRIPTION,     '*.fchk *.fch'),
        (STRING_FILETYPE_VOAVIEWFILE_DESCRIPTION,  '*.dat *.voa'),
        (STRING_FILETYPE_DALTONOUTPUT_DESCRIPTION, '*.out'),
        (STRING_FILETYPE_MOLDENFILE_DESCRIPTION,   '*.mol'),
        (STRING_FILETYPE_XMOLXYZFILE_DESCRIPTION,  '*.xyz'))

## Supported file formats for Save as...
LIST_SAVEAS_FILETYPES = (
        (STRING_FILETYPE_VOAVIEWFILE_DESCRIPTION,  '*.dat *.voa'),)

## Supported file formats for export
LIST_EXPORT_FILETYPES = (
        (STRING_FILETYPE_MOLDENFILE_DESCRIPTION,   '*.mol'),
        (STRING_FILETYPE_XMOLXYZFILE_DESCRIPTION,  '*.xyz'),
        (STRING_FILETYPE_GAUSSINFILE_DESCRIPTION,  '*.in *.inp'))

## File formats for the supported by tvk image formats
LIST_VTK_SNAPSHOT_FILETYPES = (
        (STRING_FILETYPE_JPEGFILE_DESCRIPTION,     '*.jpg *.jpeg'),
        (STRING_FILETYPE_TIFFFILE_DESCRIPTION,     '*.tif *.tiff'),
        (STRING_FILETYPE_PNGFILE_DESCRIPTION,      '*.png'),
        (STRING_FILETYPE_EPSFILE_DESCRIPTION,      '*.eps *.ps'),
        (STRING_FILETYPE_PPMFILE_DESCRIPTION,      '*.ppm *.pnm'))

## Default and minimum VTK resolution
NUM_RESOLUTION_VTK       = 10
NUM_RESOLUTION_VTK_MIN   = 5
NUM_RESOLUTION_VTK_MAX   = 100

## Molecule structure rendering modes
NUM_MODE_BALLSTICK       = 0
NUM_MODE_STICK           = 1
NUM_MODE_VDW             = 2

## Slowing factor for the rotation with the mouse
NUM_MOUSE_SLOWING_FACTOR = 1./3.

## Molecule rendering modes
STRINGS_MODE_MOLECULE = ('Ball & Stick', 'Stick', 'Van der Waals radii')

## Bonds rendering mode
NUM_MODE_BONDS_MONOLITH_COLOR   = 0
NUM_MODE_BONDS_ATOMS_COLOR      = 1

COLOR_BONDS_DEFAULT             = '#008989'

## Bond rendering modes
STRINGS_MODE_BONDS = ('Monolith', 'Two-colored')

## Radius of bonds
NUM_RADIUS_BONDS = 0.05

## Vibration representation attributes
STRING_MODE_VIB_REPRESENTATION_SPHERES   = 'Spheres'
STRING_MODE_VIB_REPRESENTATION_ARROWS    = 'Arrows'
STRING_MODE_VIB_REPRESENTATION_ANIMATION = 'Animation'
STRING_MODE_VIB_REPRESENTATION_STRUCTURE = 'Structure'

STRINGS_MODE_VIB_REPRESENTATION  = (STRING_MODE_VIB_REPRESENTATION_SPHERES,
                                    STRING_MODE_VIB_REPRESENTATION_ARROWS,
                                    STRING_MODE_VIB_REPRESENTATION_ANIMATION,
                                    STRING_MODE_VIB_REPRESENTATION_STRUCTURE)

## Color of arrows for representation of vibrational motion
COLOR_VIB_REPRESENTATION_ARROWS  = '#FF0000'

NUM_RADIUS_ARROWS = 0.025
NUM_RADIUS_ARROWS_CONES = NUM_RADIUS_ARROWS * 2.
NUM_HEIGHT_ARROWS_CONES = 0.1

## Multiplication radius for rendering of spheres
NUM_FACTOR_SPHERE_RADIUS    = 1./2.5

## Representation types of vibrational motion
STRING_VIB_ENERGY                        = 'Energy (volume)'
STRING_VIB_EXCURSIONS                    = 'Excursions (diameter)'

STRING_VIB_ENERGY_VOLUME                 = 'Total volume fix'
STRING_VIB_ENERGY_VOLUME_ZERO_POINT      = 'Zero-point'

STRING_VIB_EXCURSIONS_DIAMETER           = 'Total surface fix'
STRING_VIB_EXCURSIONS_DIAMETER_ZEROPOINT = 'Zero-point'
STRING_VIB_EXCURSIONS_DIAMETER_STANDARD  = 'Standard normalization'

## Categorized visualization possibilities
STRINGS_VIB_REPRESENTATIONS           = (STRING_VIB_ENERGY,
                                         STRING_VIB_EXCURSIONS)

STRINGS_ENERGY_VOLUME_REPRESENTATIONS = (STRING_VIB_ENERGY_VOLUME,
                                         STRING_VIB_ENERGY_VOLUME_ZERO_POINT)

STRINGS_EXCURSIONS_DIAMETER_REPRESENTATIONS = (STRING_VIB_EXCURSIONS_DIAMETER,
                                      STRING_VIB_EXCURSIONS_DIAMETER_ZEROPOINT,
                                      STRING_VIB_EXCURSIONS_DIAMETER_STANDARD)

STRINGS_VIB_REPRESENTATIONS_ALL = (STRING_VIB_ENERGY_VOLUME,
                                   STRING_VIB_ENERGY_VOLUME_ZERO_POINT,
                                   STRING_VIB_EXCURSIONS_DIAMETER,
                                   STRING_VIB_EXCURSIONS_DIAMETER_ZEROPOINT,
                                   STRING_VIB_EXCURSIONS_DIAMETER_STANDARD)


## Molecule window color
COLOR_MOLECULE_WINDOW_BG = '#646464'

## Colors for rendering vibrations
COLOR_VIB_HEMISPHERE_1 = '#0000FF'
COLOR_VIB_HEMISPHERE_2 = '#FFFF00'

## Picked atom color
COLOR_PICKED_ATOM      = '#FFFFFF'

## Picked vibrating atom color
COLOR_PICKED_VIBATOM   = '#C0C0C0'

## Color of a picked atom of a fit fragment
COLOR_PICKED_ATOM_FIT  = '#B9D3EE'

## Color of a picked atom of a comparison fragment
COLOR_PICKED_ATOM_COMPARISON = '#98FB98'

## Highlighted picked atom color
COLOR_HIGHLIGHTED_PICKED_ATOM = '#FFFF00'

## Highlighted picked vibrating atom color
COLOR_HIGHLIGHTED_PICKED_VIBATOM = '#FF0000'

## Alignment types
STRING_ALIGNMENT_ORIENTATIONAL =   'Orientational'
STRING_ALIGNMENT_INERTIA_AXES  =   'Inertia axes'

STRINGS_ALIGNMENT_TYPES = (STRING_ALIGNMENT_ORIENTATIONAL,
                           STRING_ALIGNMENT_INERTIA_AXES)

STRINGS_TRANSLATIONS_ROTATIONS_LABELS = ('Tx', 'Ty', 'Tz', 'I1', 'I2', 'I3')

## Transparency levels for atoms ( <= 1. )
NUM_TRANSPARENCY_PICKED_ATOM  = 0.40
NUM_TRANSPARENCY_VIB_ATOM     = 0.70

## Color of the sphere which marks the vibrational motion of an atom
COLOR_MARKED_VIB_ATOM                       =   '#FFFFFF'

## Fonts for similarity and overlap tables
FONT_MOLECULE_NAMES    = ('Arial', 12, 'bold')
FONT_OTHER_WINDOWS     = ('Arial', 12)
FONT_TABLE_ELEMENT     = logicalfont(name='Fixed', sizeIncr=-2)
FONT_TABLE_HEADER1     = logicalfont(name='Fixed', sizeIncr=-2)
FONT_TABLE_HEADER2     = logicalfont(name='Fixed', sizeIncr=-2)
FONT_TABLE_SEL_HEADER1 = logicalfont(name='Fixed', sizeIncr=-2, weight='bold')
FONT_TABLE_SEL_HEADER2 = logicalfont(name='Fixed', sizeIncr=-2, weight='bold')


## Color of marked elements in CorrelationResultsTable
COLOR_MARKED_TABLE_ELEMENT_BG       = '#FFFF00'

## Camera properties
STRINGS_CAMERA_PROPERTIES = ('ParallelProjection', 'ParallelScale',
                             'FocalPoint', 'Position',
                             'ClippingRange', 'ViewUp')

## Button labels
STRING_BUTTON_OK                 = 'Ok'
STRING_BUTTON_CANCEL             = 'Cancel'
STRING_BUTTON_APPLY              = 'Apply'
STRING_BUTTON_BACK               = '< Back'
STRING_BUTTON_NEXT               = 'Next >'
STRINGS_BUTTONS_OK_CANCEL        = (STRING_BUTTON_OK, STRING_BUTTON_CANCEL)
STRINGS_BUTTONS_OK_APPLY         = (STRING_BUTTON_OK, STRING_BUTTON_APPLY)
STRINGS_BUTTONS_OK_APPLY_CANCEL  = (STRING_BUTTON_OK, STRING_BUTTON_APPLY,
                                    STRING_BUTTON_CANCEL)
STRINGS_BUTTONS_BACK_NEXT_CANCEL = (STRING_BUTTON_BACK, STRING_BUTTON_NEXT,
                                    STRING_BUTTON_CANCEL)

## Representation modes of 2D-data
NUM_MODE_WHOLE         = 0
NUM_MODE_UPPERHALFONLY = 1
NUM_MODE_LOWERHALFONLY = 2

## Types of circle representation
NUM_TYPE_PROPORTIONAL_TO_SQUARE   = 0
NUM_TYPE_PROPORTIONAL_TO_DIAMETER = 1

## Fonts for labels in TwoDCircles canvas
FONT_TWODCIRCLES_LABEL1  =   ('Courier', 11, 'italic', 'bold')
FONT_TWODCIRCLES_LABEL2  =   ('Courier', 13, 'bold')

## Supported formats & resolutions for screenshots of vtk windows
STRINGS_VTK_SNAPSHOT_FORMATS    = ('jpeg', 'tiff', 'png', 'eps', 'ppm')
NUMS_VTK_SCREENSHOT_RESOLUTIONS = (72, 150, 300, 600)

## Color of a triangle for marking of angles & dihedral angles
COLOR_MARKING_TRIANGLE              = '#0080FF'

## Color for picked atoms during geometry measurments
COLOR_PICKED_ATOM_MEASURE           = '#FFFF00'

## Scattering types
#STRINGS_SCATTERING_TYPES = ('Backward', 'Forward', 'ICP_perp', 'ICP_par')
STRINGS_SCATTERING_TYPES = ('Backward', 'Forward')

## Spectra representation types
STRINGS_SPECTRA_REPRESENTATION_TYPES = ('Curves', 'Stick')

## Type of experimental spectra
STRINGS_EXPSPECTRA_TYPES = ('Raman/ROA', 'Degree of circularity')

## PDF Compatibility levels (used by p2pdf)
STRINGS_PDFCOMPATIBILITYLEVELS = ('1.2', '1.3', '1.4')

## Representation of scalar values with spheres (for instance ACPs)
NUM_MODE_PROPORTIONAL_TO_SURFACE =   0
NUM_MODE_PROPORTIONAL_TO_VOLUME  =   1

## Units of energy
STRING_UNIT_ENERGY_HARTREE = 'Hartree'
STRING_UNIT_ENERGY_KJMOL   = 'kJ / mol'

## Format of the time for time.strftime()
STRING_FORMAT_TIME = '%a, %d %b %Y %H:%M:%S'

## Prefices and names of the spectra types
STRINGS_VROA_SPECTRA_PREFICES = ('raman', 'roa', 'degcirc',
                                 'ir', 'vcd', 'g')
STRINGS_VROA_SPECTRA_NAMES    = ('Raman', 'ROA', 'Degree of circularity',
                                 'IR', 'VCD', 'G')

## Prefices for Raman, ROA, Degree of circularity
STRINGS_SPECTRA_PREFICES = STRINGS_VROA_SPECTRA_PREFICES[:3]
STRINGS_SPECTRA_NAMES    = STRINGS_VROA_SPECTRA_NAMES[:3]


def get_font_molecules(tk_widget) :
  """Return the optimal font for displaying names of molecules."""
  # using the smaller fonts for monitors narrower or equal than 1024
  if 1024 >= tk_widget.winfo_screenwidth() :
    font = Font(tk_widget, font=FONT_MOLECULE_NAMES)
    font.configure(size=int(font.cget('size')) - 2)
  else :
    font = FONT_MOLECULE_NAMES

  return font
