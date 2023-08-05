#  Copyright (C) 2007 Maxim Fedorovsky, University of Fribourg (Switzerland).
#       email : Maxim.Fedorovsky@unifr.ch, mutable@yandex.ru
#
#  This file is part of PyVib2.
#
#  PyVib2 is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either VERSION 2 of the License, or
#  (at your option) any later VERSION.
#
#  PyVib2 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PyVib2; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""Windows of PyVib2.

The following classes are exported :
    BaseWindow                       -- base class of all windows
    MoleculeWindow                   -- exploring molecules
    CorrelateVibrationsWindow        -- correlating vibrations
    CorrelationResultsWindow         -- representing results of a correlation
    SingleVibrationWindow            -- exploring a single vibration
    VibrationPairWindow              -- exploring two vibrations simultaneously
    AbstractSpectrumWindow           -- for widnows having spectra figures    
    RamanROADegcircCalcWindow        -- exploring Raman/ROA spectra
    RamanROAMatricesWindow           -- Raman/ROA generation interface
    RamanROADegcircCalcMixtureWindow -- exploring spectra of several molecules
    BoltzmannMixtureSpectraWindow    -- spectra of a mixture of molecules
    IRVCDCalcWindow                  -- exploring IR/VCD spectra
    ImportExpSpectraWindow           -- importing experimetnal spectra
    RamanROADegcircExpWindow         -- exploring experimental Raman/ROA spectra

"""
__author__ = 'Maxim Fedorovsky'

import os
import os.path
import sys
import copy
import shutil
import zipfile
from math import floor, log, sqrt, ceil
from time import strftime, localtime
import Tkinter
import tkFileDialog
import tkMessageBox
import tkSimpleDialog

from numpy import zeros, array, arange, ndarray, any, transpose, dot

import Pmw
from vtk import vtkMatrix4x4, vtkTransform

from pyviblib                 import APPNAME, VERSION, molecule
from pyviblib.io              import parsers, writers
from pyviblib.util            import misc
from pyviblib.util.constants  import INCH2CM, C_AU
from pyviblib.calc            import qtrfit, vibrations, spectra
from pyviblib.calc.common     import contract, make_gcm, \
                                     contract_t, boltzmann_distr
from pyviblib.gui             import widgets, dialogs, resources
from pyviblib.gui.figures     import BaseFigure, BaseSpectrumFigure, \
                                     RamanROADegcircCalcFigure, \
                                     RamanROADegcircCalcMixtureFigure, \
                                     MultipleSpectraFigure, \
                                     PercentageFigure, IRVCDCalcFigure, \
                                     RamanROADegcircExpFigure
from pyviblib.gui.images      import getimage
from pyviblib.util.misc       import Command, gen_molecule_name
from pyviblib.util.exceptions import InvalidArgumentError, ParseError, \
                                     ConstructorError, DataInconsistencyError

__all__ = ['BaseWindow', 'MoleculeWindow',
           'CorrelateVibrationsWindow', 'CorrelationResultsWindow',
           'SingleVibrationWindow', 'VibrationPairWindow',
           'AbstractSpectrumWindow', 'RamanROADegcircCalcWindow',
           'RamanROADegcircCalcMixtureWindow', 'RamanROAMatricesWindow',
           'IRVCDCalcWindow', 'BoltzmannMixtureSpectraWindow',
           'ImportExpSpectraWindow', 'RamanROADegcircExpWindow']


class BaseWindow(Tkinter.Toplevel, widgets.BaseWidget) :
  """Base class for all windows of PyVib2.

  The following public methods are exported :
      destroy()   --  destroy the window
      maximize()  --  maximize the window
      clone()     --  clone the window (should be overriden in subclases)
  
  """

  def __init__(self, mainApp, **kw) :
    """Contructor of the class.

    Positional parameters :
    mainApp -- reference to the main window of PyVib2

    Keyword arguments (of this class):
    destroy_command -- function to be called before the window is destroyed
                       (default : None)

    """
    # initializing the base classes
    Tkinter.Toplevel.__init__(self, mainApp.master)

    # reference to the main application window
    self._mainApp = mainApp
    self.withdraw()
    
    widgets.BaseWidget.__init__(self, **kw)

    # redirect the exit event to the main interface
    self.protocol('WM_DELETE_WINDOW', self.destroy)

    mainApp.register_window(self)
    mainApp.activate(self)
    self.deiconify()

  def destroy(self, unregister=True) :
    """Destroy the window.

    Keyword arguments :
    unregister -- whether to unregister oneself from the Windows menu of the
                  main window of PyVib2
                  
    """
    if unregister :
      self._mainApp.unregister_window(self)

    if callable(self._smartdict['destroy_command']) :
      self._smartdict['destroy_command']()

    Tkinter.Toplevel.destroy(self)

  def maximize(self) :
    """Maximize oneself."""
    try :
      # should work under windows
      self.wm_state('zoomed')
      
    except :
      # else resize to the current display size
      w = self.winfo_screenwidth()  - 10
      h = self.winfo_screenheight() - 80

      self.geometry('%dx%d+0+0' % (w, h))

  def clone(self) :
    """Clone the window.

    Subclasses should override the method if this operation is supported.

    This implementation raises a NotImplementedError.
    """
    raise NotImplementedError(
      'The window of the type %s cannot be cloned.' % self.__class__.__name__)


class MoleculeWindow(BaseWindow) :
  """Window for exploring molecules.

  The following properties are exposed :
      filename          -- file name from which the molecule was read
      molecule_name     -- name of the molecule
      molecule          -- molecule (pyviblib.molecule.Molecule)
      vib_toolbar       -- vib toolbar (pyviblib.gui.widgets.VibrationalToolbar)
      renderWidget      -- 3D widget (pyviblib.gui.widgets.MoleculeRenderWidget)
      settings          -- dictionary with the settings of the window
      status            -- text to be set to the message bar of the window

  The following methods are exported :
      apply_settings()  -- callback for the buttons of the settings dialog
      save_vibrations() -- save vibrations
      save_animation()  -- save an animation of the current vibration
      clone()           -- clone the molecule window
  
  """
 
  def __init__(self, mainApp, datasrc, **kw) :
    """Constructor of the class.

    Positional arguments :
    mainApp  -- reference to the main window of PyVib2
    datasrc  -- data source
                either the file name or a parser object

    Keyword arguments :
    molecule -- instance of pyviblib.molecule.Molecule (default None)
                if None, take the data from the parser object
    """   
    self.__read_data(datasrc, mainApp, **kw)

    # continue on successful reading only
    if not self._read_successfully :
      return

    BaseWindow.__init__(self, mainApp, **kw)

  def _init_vars(self) :
    """Initialize variables."""
    # Size of the vtk render window of a molecule
    self._varsdict['RENDER_WINDOW_WIDTH']  = 450
    self._varsdict['RENDER_WINDOW_HEIGHT'] = 450

    # window settings
    self.__settings = dict(molecule_mode=resources.NUM_MODE_BALLSTICK,
                           bonds_mode=resources.NUM_MODE_BONDS_ATOMS_COLOR,
                           hydrogen_bond=True,
                           atom_labels=False)

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    self.wm_title(self.__molecule.name or 'noname')

    ### window consists of two frames :
    ### 1) upperpane : menu, button toolbar, vibrational toolbar
    ### 2) lowerpane : molecule render widget, message bar
    self._varsdict['mainPane'] = Pmw.PanedWidget(self, orient='vertical')
    self._varsdict['mainPane'].grid(row=0, column=0,
                                    padx=3, pady=3, sticky='news')

    # whole pane can expand
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=1)

    upperpane = self._varsdict['mainPane'].add('upperpane')
    lowerpane = self._varsdict['mainPane'].add('lowerpane')
    
    ## upperpane    
    # menus
    self.__menubar = self.__constructMenubar(upperpane)
    self.__menubar.grid(row=0, column=0, sticky='w')

    # button toolbar
    button_toolbar = self.__constructButtonToolbar(upperpane)
    button_toolbar.grid(row=1, column=0, sticky='w', padx=3, pady=3)
    
    # window navigation toolbar
    widget = widgets.WindowNavigationToolbar(upperpane,
                                             mainApp=self._mainApp,
                                             backbutton=False,
                                             homebutton=True)
    self._varsdict['window_toolbar'] = widget
    self._varsdict['window_toolbar'].grid(row=1, column=1,
                                          padx=3, pady=3, sticky='e')

    # vibrational toolbar (can grow)
    upperpane.grid_columnconfigure(0, weight=1)
    upperpane.grid_rowconfigure(3, weight=1)
    
    widget = widgets.VibrationalToolbar(upperpane,
                                        freqs=self.__molecule.freqs,
                                        render_callback=self.__render_current)
    self._varsdict['vib_toolbar'] = widget
    self._varsdict['vib_toolbar'].grid(row=3, column=0, columnspan=2,
                                       padx=3, pady=3, sticky='we')

    ## lowerpane
    lowerpane.grid_rowconfigure(0, weight=1)
    lowerpane.grid_columnconfigure(1, weight=1)
    
    ## my molecule render widget
    # message bar
    self._varsdict['msgBar'] = Pmw.MessageBar(lowerpane,
                                              entry_relief='sunken',
                                              label_text='Status :',
                                              labelpos='w')
    self._varsdict['msgBar'].grid(row=1, column=0, columnspan=2,
                                  padx=3, pady=3, sticky='we')

    # render widget
    rw_kw = dict(molecule=None,
                 msgBar=self._varsdict['msgBar'],
                 vib_toolbar=self._varsdict['vib_toolbar'],
                 width=self._varsdict['RENDER_WINDOW_WIDTH'],
                 height=self._varsdict['RENDER_WINDOW_HEIGHT'],
                 resolution=self._mainApp.settings['resolution'],
                 color_picked_atom=resources.COLOR_PICKED_ATOM_MEASURE,
                 camera=self._smartdict['camera'])
    
    widget = widgets.MoleculeRenderWidget(lowerpane, **rw_kw)
    self._varsdict['renderWidget'] = widget
    self._varsdict['renderWidget'].grid(row=0, column=1,
                                        padx=3, pady=3, sticky='news')
    
    self._varsdict['renderWidget'].molecule = self.__molecule
 
    # vertical navigation toolbar
    widget = widgets.NavigationToolbar(lowerpane,
                                       self._varsdict['renderWidget'])
    self._varsdict['nav_toolbar'] = widget
    self._varsdict['nav_toolbar'].grid(row=0, column=0,
                                       padx=0, pady=2, sticky='ns')
    
    # 3D-window size
    self._varsdict['var_renderwidget_size'] = Tkinter.StringVar()
    command = misc.Command(self._change_render_widget_size,
                           self._varsdict['renderWidget'])
    btn_kw = dict(textvariable=self._varsdict['var_renderwidget_size'],
                  relief='flat',
                  justify='center',
                  command=command)
         
    self._varsdict['btn_size'] = Tkinter.Button(lowerpane, **btn_kw) 
    self._varsdict['btn_size'].grid(row=1, column=1, columnspan=2,
                                    padx=0, pady=0, sticky='e')

    # vertical geometry measure toolbar
    geom_kw = dict(horizontal=False,
                   msgBar=self._varsdict['msgBar'],
                   resolution=self._mainApp.settings['resolution'])
    
    widget = widgets.GeometryMeasureToolbar(lowerpane,
                                            self._varsdict['renderWidget'],
                                            **geom_kw)
                              
    self._varsdict['geom_toolbar'] = widget
    self._varsdict['geom_toolbar'].grid(row=0, column=2,
                                        padx=0, pady=5, sticky='ns')

    ## adjusting the size of the paned widget
    ## minimum size of the lower pane is the width of the menu and the toolbar
    self._varsdict['mainPane'].setnaturalsize()

    upperpane_min_height = button_toolbar.winfo_reqheight() + \
                           self.__menubar.winfo_reqheight() + 6
    upperpane_max_height = upperpane.winfo_reqheight()
    
    self._varsdict['mainPane'].configurepane('upperpane',
                                             min=upperpane_min_height,
                                             max=upperpane_max_height,
                                             size=upperpane_max_height
                                             )
    upperpane.grid_columnconfigure(0, weight=1)

    #
    self._varsdict['nav_toolbar'].save_camera_state()
    self._varsdict['initialdir'] = self._mainApp.lastdir

    # setting the size
    self.geometry(self._smartdict['size'] or '500x500')
  
  def _declare_properties(self) :
    """Declare properties of the widget."""
    # File name
    self.__class__.filename = property(
      fget=Command(Command.fget_attr, '_filename'))

    # Name of the molecule based on the filname
    self.__class__.molecule_name = property(fget=self.__get_molecule_name)
    
    # molecule and vibrational toolbar
    self.__class__.molecule = property(
      fget=Command(Command.fget_value, self.__molecule))
    
    self.__class__.vib_toolbar = property(
      fget=Command(Command.fget_value, self._varsdict['vib_toolbar']))

    # Molecule render widget
    self.__class__.renderWidget = property(
      fget=Command(Command.fget_value, self._varsdict['renderWidget']))

    # Current window settings
    self.__class__.settings = property(
      fget=Command(Command.fget_value, self.__settings))

    # Molecule window status message (write-only)
    self.__class__.status = property(fset=self.__set_status)

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    self._balloon.bind(self._varsdict['btn_size'],
                       'Current size of the render widget.')

  def _bind_events(self) :
    """Bind events."""
    ## binding the arrow buttons to navigate through vibrations
    # left - right      -> backward - forward
    # pageup - pagedown -> increase / decrease the scale factor
    self.bind('<Left>' , Command(self._varsdict['vib_toolbar'].go_backward))
    self.bind('<Right>', Command(self._varsdict['vib_toolbar'].go_forward))
    self.bind('<Prior>',
              Command(self._varsdict['vib_toolbar'].increase_scale_factor))
    self.bind('<Next>',
              Command(self._varsdict['vib_toolbar'].decrease_scale_factor))

    # Changing the size of the window
    self.bind('<Configure>', self.__Configure)

  def __constructMenubar(self, parent) :
    """Construct and return the menubar.

    Do not pack !
    
    """
    menubar = Pmw.MenuBar(parent, hotkeys=False)

    ## menu File
    menubar.addmenu('File', None, tearoff=True)

    menubar.addmenuitem('File', 'command', label='Info...',
                        command=self.__file_info)
    menubar.addmenuitem('File', 'separator')
    menubar.addmenuitem('File', 'command', label='Save as...',
                        command=self.__file_saveas)
    menubar.addmenuitem('File', 'command', label='Export...',
                        command=self.__file_export)
    menubar.addmenuitem('File', 'separator')
    menubar.addmenuitem('File', 'command', label='Clone',
                        command=self.clone)
    menubar.addmenuitem('File', 'command', label='Close',
                        command=self.__file_close)
    
    ## menu Tools
    menubar.addmenu('Tools', None, tearoff=True)

    menubar.addmenuitem('Tools',
                        'command',
                        label='Correlate vibrations...',
                        command=self.__tools_correlate_vibrations)

    # all the menu items which require the vibrational data
    if self.__molecule.L is None :
      menubar.component('Tools-menu').entryconfigure(1, state='disabled')
      #menubar.component('Tools-menu').entryconfigure(2, state='disabled')
    
##      if Pmw.Blt.haveblt(self):
##        menubar.component(''l'ernuclear Distance Changes-menu').
## entryconfigure(1, state='disabled')


    # Raman/Roa GCM / ACP if available
    menubar.addmenuitem('Tools',
                        'command',
                        label='Raman / ROA generation',
                        command=self.__tools_raman_roa_matrices)
    
    if self.__molecule.raman_roa_tensors is None :
      menubar.component('Tools-menu').entryconfigure(2, state='disabled')
      
    ## menu Spectra
    menubar.addmenu('Spectra', None, tearoff=True)

    # Raman/ROA/Degree of circularity spectra
    menubar.addmenuitem('Spectra',
                        'command',
                        label='Raman / ROA / Degree of circularity',
                        command=self.__spectra_raman_roa_degcirc)

    # IR/VCD spectra
    menubar.addmenuitem('Spectra',
                        'command',
                        label='IR / VCD',
                        command=self.__spectra_ir_vcd)

    if self.__molecule.raman_roa_tensors is None :
      menubar.component('Spectra-menu').entryconfigure(1, state='disabled')

    if self.__molecule.ir_vcd_tensors is None :
      menubar.component('Spectra-menu').entryconfigure(2, state='disabled')
    
    ## menu Options
    menubar.addmenu('Options', None, tearoff=True)
  
    menubar.addmenuitem('Options',
                        'command',
                        label='Settings',
                        command=self.__options_settings)

    return menubar

  def __constructButtonToolbar(self, parent) :
    """Construct the button toolbar and return it."""
    btn_toolbar = widgets.ButtonToolbar(parent, horizontal=True)

    if self.__molecule.L is not None :
      # save vibrations
      btn = btn_toolbar.add_button(state='disabled',
                                   imagename='save_vibs',
                                   command=self.__show_save_vibrations_dlg,
                                   helptext='Save vibrations of the molecule.')
      self._varsdict['btn_save_vibs'] = btn

      # save animations
      btn_toolbar.add_button(imagename='animation',
                        command=self.__show_save_animation_dlg,
                        helptext='Save an animation of the current vibration.')

      btn_toolbar.add_separator()

      # correlate vibrations
      btn_toolbar.add_button(imagename='correlate',
                             command=self.__tools_correlate_vibrations,
                             helptext='Correlate vibrations...')

    btn_toolbar.add_separator()

    # preferences 
    btn_toolbar.add_button(imagename='prefs',
                           command=self.__options_settings,
                           helptext='Settings of the window.')

    btn_toolbar.add_separator()

    # snapshot
    btn_toolbar.add_button(imagename='snapshot',
                           command=self.__snapshot,
                           helptext='Snapshot of the render window.')
    
    return btn_toolbar

  def __Configure(self, e) :
    """<Configure> event handler."""
    self._varsdict['var_renderwidget_size'].set(
      '%dx%d' % self._varsdict['renderWidget'].GetRenderWindow().GetSize())
    
  def __read_data(self, datasrc, mainApp, **kw) :
    """Read data from a file or a parser object."""
    # created from a file
    if isinstance(datasrc, str) :
      self._filename  = datasrc
      self.__parser   = parsers.ParserFactory.create_parser(self._filename)
      
    elif isinstance(datasrc, parsers.AbstractFileParser) :
      self.__parser   = datasrc
      self._filename  = self.__parser.filename

    # if the user supplied the molecule keyword
    # to the contructor of the class use it
    if kw.get('molecule', None) is not None :
      self.__molecule = kw['molecule']

    else :
      self.__molecule      = molecule.Molecule(self.__parser)
      self.__molecule.name = self.__get_molecule_name()
      
    self.__filetype = self.__parser.get_description()

    if not isinstance(self.__parser, parsers.FCHKFileParser) :
      self._read_successfully = True

    else :
      # perform the vibrational analysis if the user
      # did not supply the ready molecule
      if self.__parser.hessian is not None and \
         kw.get('molecule', None) is None :
        ok_command     = Command(self.__finalize_fchk,
                                 self.__parser.hessian, self.__molecule)
        cancel_command = Command(Command.fset_attr,
                                 self,
                                 False,
                                 '_read_successfully')

        # created from a parser - give an appropriate name        
        if isinstance(datasrc, parsers.FCHKFileParser) :
          initname = self.__get_molecule_name() + '_subst'
        else :
          initname = self.__get_molecule_name()

        isotopes_dlg = dialogs.IsotopesDialog(mainApp.master,
                                              self.__molecule,
                                              molecule_name=initname,
                                              ok_command=ok_command,
                                              cancel_command=cancel_command
                                              )
        isotopes_dlg.activate()

      # do nothing unless the hessian is available
      else :
        self._read_successfully = True          

  def __finalize_fchk(self, affected_atoms_data, molecule_name, hessian, mol) :
    """Diagonalize the hessian with a given isotopic composition."""
    self._read_successfully = True

    if molecule_name is not None and 0 < len(molecule_name) :
      self._molecule_name = molecule_name
      mol.name = molecule_name

    mol.update_masses(affected_atoms_data)
    
    ans_vibana = vibrations.vibana(hessian, mol.coords, mol.masses)

    mol.L      = ans_vibana['L']
    mol.freqs  = ans_vibana['freqs']

  def __render_current(self, **kw) :
    """Delegates the rendering to the render widget."""
    # rendering the structure
    if self._varsdict['vib_toolbar'].rep_type is None or \
       resources.STRING_MODE_VIB_REPRESENTATION_STRUCTURE == \
       self._varsdict['vib_toolbar'].mode :
      
      self._varsdict['renderWidget'].cleanup()

      kw = dict(molecule_mode=self.__settings['molecule_mode'],
                bonds_mode=self.__settings['bonds_mode'],
                rounded_bond=False,
                hydrogen_bond=self.__settings['hydrogen_bond'],
                atom_labels=self.__settings['atom_labels'])

      if 'resolution' is self.__settings :
        kw['resolution'] = self.__settings['resolution']
      
      # in the stick mode render the rounded bonds :)
      if 1 == self.__settings['molecule_mode'] :
        kw['rounded_bond'] = True

      self._varsdict['renderWidget'].render_molecule(**kw)
      self._varsdict['renderWidget'].Render()

    # rendering a vibration
    elif self.__molecule.L is not None and \
         self._varsdict['vib_toolbar'].rep_subtype is not None :
      
      self._varsdict['renderWidget'].render_vibration(**kw)
      self._varsdict['btn_save_vibs'].configure(state='normal')

  def __generate_filename(self, filepattern, image_format,
                          only_basename=False) :
    """Generate the filename.
    
    Include information about the vibration's type and subtype.
    only_basename -> do not return the full path.
    
    """
    filename = filepattern

    # type : energy or excursions
    if resources.STRING_VIB_ENERGY == self._varsdict['vib_toolbar'].rep_type :
      filename = ''.join((filename, '_energy'))
    else :
      filename = ''.join((filename, '_excurs'))

    # subtype
    subtype = self._varsdict['vib_toolbar'].rep_subtype
    
    if resources.STRING_VIB_ENERGY_VOLUME == subtype :
      filename = ''.join((filename, '_tvf'))
    elif resources.STRING_VIB_ENERGY_VOLUME_ZERO_POINT == subtype:
      filename = ''.join((filename, '_zp'))
    elif resources.STRING_VIB_EXCURSIONS_DIAMETER == subtype :
      filename = ''.join((filename, '_tsf'))
    elif resources.STRING_VIB_EXCURSIONS_DIAMETER_STANDARD == subtype :
      filename = ''.join((filename, '_sn'))

    # vibrational number and extension
    # adding 0's if necessary
    no_fields = int(floor(log(self.__molecule.NFreq, 10)))
    format_no = '%%0%dd' % (1 + no_fields)
    
    str_vib_no = format_no % self._varsdict['vib_toolbar'].vib_no

    extension = image_format.lower()
    if 'tiff' == extension :
      extension = 'tif'
    
    filename = ''.join((filename, '_%s.%s' % (str_vib_no, extension)))

    if only_basename :
      return os.path.basename(filename)
    else :
      return filename      

  def __show_save_vibrations_dlg(self) :
    """Show the Save vibrations dialog."""
    self.tk.call('update', 'idletasks')
    dialogs.SaveVibrationsDialog(self,
                              initialdir=os.path.dirname(self.filename)).show()

  def __show_save_animation_dlg(self) :
    """Shows the Save animation dialog."""
    self.tk.call('update', 'idletasks')

    # check first if the required utilities are installed
    gifsicle_installed = misc.is_command_on_path('gifsicle')
    netpbm_installed   = misc.is_command_on_path('pnmcolormap') and \
                         misc.is_command_on_path('pnmremap') and \
                         misc.is_command_on_path('ppmtogif')
    ppm2fli_installed  = misc.is_command_on_path('ppm2fli')

    if not (gifsicle_installed and netpbm_installed) and \
       not ppm2fli_installed :
      msg = 'Make sure that either {gifsicle and Netpbm} or ppm2fli '\
            'are installed\nand can be found on the path '\
            '(PATH environmental variable).'

      dlg = Pmw.MessageDialog(title='Animation cannot be created',
                              message_text=msg,
                              iconpos='w',
                              icon_bitmap='warning')
      dlg.withdraw()
      Pmw.setgeometryanddeiconify(dlg, dlg._centreonscreen())

    else :
      dialogs.AnimationSettingsDialog(self).show()

  def __pack_settings(self) :
    """Pack the current settings to the internal dictionary."""
    self.tk.call('update')
    
    # molecule window background color as hex
    self.__settings['window_bg'] = self.renderWidget.background

    # vibrational hemispheres colors
    self.__settings['color_sphere_1'] = self.renderWidget.color_sphere_1
    self.__settings['color_sphere_2'] = self.renderWidget.color_sphere_2

    # molecule & bonds rendering modes
    self.__settings['molecule_mode'] = self.renderWidget.molecule_mode
    self.__settings['bonds_mode'] = self.renderWidget.bonds_mode

    # current VTK resolution
    self.__settings['resolution']  = self.renderWidget.resolution

  def __snapshot(self) :
    """Show the Snapshot dialog."""
    self.tk.call('update', 'idletasks')
    dialogs.SnapshotDialog(self,
                           mode='file',
                           initialdir=self._varsdict['initialdir'],
                           renderWidget=self.renderWidget
                           ).show()

  def __file_info(self) :
    """File / Info... menu file handler."""
    info_dlg = dialogs.FileInfoDialog(self, self.__molecule, self.__parser)
    info_dlg.configure(title=r'Information for "%s"' % self.__molecule.name)
    info_dlg.show()    
    
  def __file_saveas(self) :
    """File / Save as... menu file handler."""
    # remove the confusion with extensions
    initialfile = self.__molecule.name
    if '.' in initialfile :
      initialfile = initialfile.replace('.', '_')

    filename = tkFileDialog.SaveAs(parent=self._varsdict['mainPane'].interior(),
                                   filetypes=resources.LIST_SAVEAS_FILETYPES,
                                   initialfile=initialfile,
                                   initialdir=self._mainApp.lastdir).show()

    if filename is None or 0 == len(filename) :
      return

    ext = os.path.splitext(filename)[1].lower()
    
    try :    
      if ext in ('.dat', '.voa') :
        writer = writers.VOAVIEWFileWriter(filename, molecule=self.__molecule)

      elif '.pv2' == ext :
        #writer = writers.PyVib2FileWriter(filename, molwindow=self)
        pass

      elif ext in ('.fchk', '.fch') :
        if hasattr(self.__molecule.parser, 'hessian') :
          hessian = self.__molecule.parser.hessian
        else :
          hessian = None
          
        writer = writers.FCHKFileWriter(filename,
                                        molecule=self.__molecule,
                                        hessian=hessian,
                                        comment=self.__molecule.name)

      else :
        tkMessageBox.showwarning(title='Nothing to do',
                                 message='Specify the extension explicitely !')
        return

      self.tk.call('update')
      writer.write()

    except :
      widgets.show_exception(sys.exc_info())

  def __file_export(self) :
    """File / Export... menu file handler."""
    # remove the confusion with extensions
    initialfile = self.__molecule.name
    if '.' in initialfile :
      initialfile = initialfile.replace('.', '_')
      
    filename = tkFileDialog.SaveAs(parent=self._varsdict['mainPane'].interior(),
                                   filetypes=resources.LIST_EXPORT_FILETYPES,
                                   initialfile=initialfile,
                                   initialdir=self._mainApp.lastdir).show()

    if filename is None or 0 == len(filename) :
      return

    ext = os.path.splitext(filename)[1].lower()

    try :    
      if ext == '.mol' :
        writer = writers.MOLDENFileWriter(filename,
                                          molecule=self.__molecule,
                                          comment=self.__molecule.name)
        
      elif ext == '.xyz' :
        writer = writers.XMolXYZFileWriter(filename,
                                           molecule=self.__molecule,
                                           comment=self.__molecule.name)

      elif ext in ('.in', '.inp') :
        writer = writers.GaussianInputFileWriter(filename,
                                                 molecule=self.__molecule,
                                                 comment=self.__molecule.name)
        
      else :
        tkMessageBox.showwarning(title='Nothing to do',
                                 message='Specify the extension explicitely !')
        return

      self.tk.call('update')
      writer.write()

    except :
      widgets.show_exception(sys.exc_info())

  def __file_close(self) :
    """File / Close menu command handler."""
    self.destroy()

  def __tools_correlate_vibrations(self) :
    """Tools / Correlate vibrations... menu command handler."""
    self.tk.call('update', 'idletasks')
    CorrelateVibrationsWindow(self._mainApp, self.molecule)

  def __tools_raman_roa_matrices(self) :
    """Tools / Raman / ROA GCM / ACP menu command handler."""
    self.tk.call('update', 'idletasks')
    splash = widgets.SplashScreen(self.master,
                                  'Calculating the Raman/ROA invariants...')
    
    RamanROAMatricesWindow(self._mainApp, self.molecule,
                           vib_no=self.vib_toolbar.vib_no,
                           camera=self.renderWidget.camera)
    splash.destroy()

  def __spectra_raman_roa_degcirc(self) :
    """
    Spectra / Raman/ROA/Degree of circularity menu command handler.
    """
    self.tk.call('update', 'idletasks')
    splash = widgets.SplashScreen(self.master,
                                  'Calculating the Raman/ROA invariants...')
    
    RamanROADegcircCalcWindow(self._mainApp, self.molecule,
                              camera=self.renderWidget.camera)
    splash.destroy()

  def __spectra_ir_vcd(self) :
    """Spectra / IR/VCD menu command handler."""
    self.tk.call('update', 'idletasks')    
    splash = widgets.SplashScreen(self.master,
                                  'Calculating the IR/VCD invariants...')
  
    IRVCDCalcWindow(self._mainApp, self.molecule)
    
    splash.destroy()

  def __options_settings(self) :
    """Options / Settings menu file handler."""
    self.__pack_settings()

    if 'dlg_settings' not in self._varsdict :
      self._varsdict['dlg_settings'] = \
      dialogs.MoleculeWindowSettingsDialog(self)

    self._varsdict['dlg_settings'].update_controls()
    self._varsdict['dlg_settings'].show()

  def __get_molecule_name(self, *dummy) :
    """Generate the molecule name from the full path of the filename."""
    if not hasattr(self, '_molecule_name') or self._molecule_name is None :
      self._molecule_name = gen_molecule_name(self._filename)

    return self._molecule_name

  def __set_status(obj, msg) :
    """Setter function for the status property."""
    obj._varsdict['msgBar'].message('state', msg)

  __set_status = staticmethod(__set_status)

  def apply_settings(self, close_dialog=False) :
    """Callback for the Apply/Ok buttons of the settings dialog.

    Keyword arguments :
    close_dialog -- whether the dialog is to be closed (default False)
    
    """
    self.tk.call('update')
    
    if close_dialog :
      self._varsdict['dlg_settings'].withdraw()    

    ## apply new settings
    new_prefs = self._varsdict['dlg_settings'].settings
    
    # molecule window background color
    self.renderWidget.background = new_prefs['window_bg']

    # vtk resolution
    self.renderWidget.resolution   = new_prefs['resolution']
    self._varsdict['geom_toolbar'].resolution = new_prefs['resolution']

    # hemisphere colors
    self.renderWidget.color_sphere_1 = new_prefs['color_sphere_1']
    self.renderWidget.color_sphere_2 = new_prefs['color_sphere_2']

    self.__render_current()

    # update the renderer window
    self.renderWidget.GetRenderWindow().Render()

  def save_vibrations(self, **params) :
    """Save vibrations.
    
    Keyword arguments :
    filepattern    -- pattern to generating file names for the vibrations
    image_format   -- image format
                      one of ('jpeg', 'tiff', 'png', 'eps', 'ppm')
    magnify_factor -- integer magnification factor for the render widet
    vibs_list      -- list of vibrations to be saved
                      vibration numbers are one-based
    create_archive -- whether to create a zip-archive

    All the keyword arguments must be supplied.
    
    """
    self.tk.call('update')

    # verifying parameters
    if not params :
      return

    for p in dialogs.SaveVibrationsDialog.PARAM_LIST :
      if not params.has_key(p) :
        raise InvalidArgumentError('Missing the %s keyword argument' % p)
    #
    if params['create_archive'] :
      zip_file = zipfile.ZipFile(params['filepattern'] + '_vibs.zip',
                                 'w', zipfile.ZIP_DEFLATED)
      
    # iterating through all vibrations
    for v in params['vibs_list'] :
      if -1 == v :
        v = self._varsdict['vib_toolbar'].vib_no

      # rendering into the window
      self._varsdict['vib_toolbar'].vib_no = v

      filename = self.__generate_filename(params['filepattern'],
                                          params['image_format'])
      self.renderWidget.snapshot(filename, params['image_format'],
                                 params['magnify_factor'])
      
      if params['create_archive'] :
        zip_file.write(filename, os.path.basename(filename))
        os.remove(filename)

    # closing the archive
    if params['create_archive'] :
      zip_file.close()

  def save_animation(self, filename, nFrames, resolution, speed,
                     format='Animated GIF', transparent_bg=False,
                     openfile=False) :
    """Save an animation of the current vibration.

    The gifsicle and ppm2fli programs must be installed.

    Positional arguments :
    filename        --  file name for the animation
    nFrames         --  number of frames per each direction
    resolution      --  VTK resolution for rendering
    speed           --  speed of animation
                        delay between frames in hundredths of a second
                        http://www.lcdf.org/gifsicle/man.html
                        http://vento.pi.tu-berlin.de/ppm2fli/ppm2fli.1.html

    Keyword arguments :
    format          -- format (default 'Animated GIF')
                       one of ('Animated GIF', 'FLI')
    transparent_bg  -- whether the background should be made transparent
                       (default False)
    openfile        -- whether to open the animation after the saving
                       (default False)
                       this feature must be supported by the Python environment

    """
    if not format in ('Animated GIF', 'FLI') :
      raise InvalidArgumentError('Unknown format : %s' % format)
    
    # to make sure that gui is updated
    self.tk.call('update')

    # go
    try :
      if 'FLI' == format :
        format_ = 'ppm'
      else :
        format_ = 'gif'
        
      listfile = self._varsdict['renderWidget'].create_animation_frames(
        self.__molecule.Lx_norm[self._varsdict['vib_toolbar'].vib_no],
        self._varsdict['vib_toolbar'].scale_factor,
        nFrames,
        resolution=resolution,
        format=format_,
        transparent_bg=transparent_bg)
      
      tmpdir = os.path.dirname(listfile)

      # under unix it is necessary to convert the listfile to the unix format
      # because ppm2fli cannot handle Windows/MAC files
      # dos2unix does the work ;)
      if 'posix' != os.name :
        os.system(r'dos2unix "%s"' % listfile)

      self.tk.call('update')
      splash = widgets.SplashScreen(self, 'Creating %s...' % filename)

      # if an animation with the same name already exists
      if os.path.exists(filename) :
        os.unlink(filename)

      # logging the output in the temporary directory
      logfile = os.path.join(tmpdir, 'log')

      # saving FLI
      if 'FLI' == format :
        # one has to pass an exact size of the frames
        width, height = \
        self._varsdict['renderWidget'].GetRenderWindow().GetSize()

        # options of ppm2fli,
        # see http://vento.pi.tu-berlin.de/ppm2fli/ppm2fli.1.html :
        # -I  -> Perform an individual quantize of each image
        #        independently of all other images.
        # -g widthxheight -> Define a custom display_area
        # -D  -> Include additionally update information with respect
        #        to the frame before the last
        #        The additional update information is useful for
        #        players that use the double buffering technique
        # -s  -> delay in 1/1000 seconds
        cmd = r'ppm2fli -I -D -g %dx%d -s %d "%s" "%s" > "%s"' % \
        (width, height, int(10 * speed), listfile, filename, logfile)
        
        failed = os.system(cmd)

      # saving animated gif
      else :
        # all single gifs are given as command-line parameters to gifsicle
        # see the manual page of gifsicle
        # http://www.lcdf.org/gifsicle/man.html
        comment = \
        '%s vibration # %d / %.2f cm**(-1) (created with %s version %s)' % \
        (self.__molecule.name, self._varsdict['vib_toolbar'].vib_no,
         self.__molecule.freqs[self._varsdict['vib_toolbar'].vib_no],
         APPNAME, VERSION)
        
        cmd = r'gifsicle --comment "%s" --delay %d ' % (comment, speed) + \
              '--loopcount=forever --colors 256 '
        
        if transparent_bg :
          cmd = ''.join((cmd, r'--disposal background '))

        cmd = ''.join((cmd, r'frame*.gif >"%s" 2>"%s"' % (filename, logfile)))

        # changing to the temporary directory
        wrkdir = os.getcwd()
        os.chdir(tmpdir)
        failed = os.system(cmd)
        os.chdir(wrkdir)

      splash.destroy()

      if failed :
        # show the contents of the log file if it exists
        dialog = Pmw.TextDialog(self,
                                scrolledtext_labelpos = 'n',
                                title='Operation failed :(',
                                label_text='Contents of the log file :',
                                defaultbutton=0)
        dialog.withdraw()
        dialog.insert('end', open(logfile).read())
        dialog.configure(text_state='disabled')
        dialog.activate()

      # removing the temporary directory
      # ignoring errors
      shutil.rmtree(tmpdir, True)

      # opening the animation if it is possible
      if openfile :
        try :
          from os import startfile
        except ImportError :
          pass
        else :
          startfile(filename)

    # something went wrong...
    except :
      widgets.show_exception(sys.exc_info())

  def clone(self) :
    """Clone the molecule window.

    Overrides the base class method.
    
    """
    self.tk.call('update', 'idletasks')

    # do not show the splash screen for FCHK files
    is_fchk = isinstance(self.__parser, parsers.FCHKFileParser)

    if not is_fchk :
      splash = widgets.SplashScreen(self, 'Cloning the window...')
    
    MoleculeWindow(self._mainApp, self.__parser,
                   molecule=self.__molecule,
                   camera=self.renderWidget.camera)

    if not is_fchk :
      splash.destroy()
        

class CorrelateVibrationsWindow(BaseWindow) :
  """Window for correlating vibrations.

  No properties are exposed and no public methods are exported.
  
  """
 
  def __init__(self, mainApp, ref_mol=None, tr_mol=None,
               molecules=None, startpage=None) :
    """Constructor of the class.

    Positional arguments :
    mainApp   -- reference to the main window of PyVib2

    Keyword arguments :
    ref_mol   -- start reference molecule (default None)
                 must be instance of pyviblib.molecule.Molecule
                 if None, the choice is made automatically
    tr_mol    -- start trial molecule (default None)
                 must be instance of pyviblib.molecule.Molecule
                 if None, the choice is made automatically              
    molecules -- list of molecule whose vibrations are to be correlated
                 (default None)
                 if None, use the molecules listed in the thumbnail pane of
                 the main window of PyVib2
    startpage -- tab name of RamanROADegcircCalcMixtureWindow to be shown at
                 startup (default None)

    """
    # saving reference and trial molecule windows
    self.__ref_mol = ref_mol
    self.__tr_mol  = tr_mol

    BaseWindow.__init__(self, mainApp,
                        ref_mol=ref_mol, tr_mol=tr_mol, molecules=molecules,
                        startpage=startpage)

    #self.__init_picking()

  def _init_vars(self) :
    """Initialize variables."""
    # tab names
    self._varsdict['tablist'] = ('welcome', 'basic', 'expertFitFragment',
                                 'expertComparisonFragment')
    
    # for the picking
    self._varsdict['basic_picked_atom_pairs'] = []
    self._varsdict['fit_picked_atom_pairs']   = []
    self._varsdict['comparison_picked_atom_pairs'] = []

    # if the molecules keyword is given then use only that molecules
    # otherwise use all opened molecules with the normal modes
    mols = self._smartdict['molecules'] is not None and \
           self._smartdict['molecules'] or self._mainApp.opened_vibmolecules

    self._varsdict['opened_windows_titles'] = [ mol.name for mol in mols ]
    self._varsdict['opened_molecules'] = [ copy.deepcopy(mol) for mol in mols ]

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    self.wm_title('Correlate vibrations @ %s' % \
                  strftime(resources.STRING_FORMAT_TIME, localtime()))

    ## windows navigation toolbar
    widget = widgets.WindowNavigationToolbar(self,
                                             mainApp=self._mainApp,
                                             backbutton=False,
                                             homebutton=True)
    self._varsdict['windows_toolbar'] = widget
    self._varsdict['windows_toolbar'].grid(row=0, column=0,
                                           padx=3, pady=3, sticky='e')
    ## creating tabs
    self.grid_rowconfigure(1, weight=1)
    self.grid_columnconfigure(0, weight=1)
    
    self._varsdict['wizard'] = widgets.WizardWidget(self,
                                                    back_command=self.__back,
                                                    next_command=self.__next)
    self._varsdict['wizard'].grid(row=1, column=0,
                                  padx=3, pady=3, sticky='news')

    # 1
    tab = self._varsdict['wizard'].notebook.add('welcome')
    self._varsdict['welcome_tab'] = tab
    self.__constructWelcomeTab(self._varsdict['welcome_tab'])

    # 2
    tab = self._varsdict['wizard'].notebook.add('basic')
    self._varsdict['basic_tab'] = tab
    self.__constructBasicTab(self._varsdict['basic_tab'])

    # 3
    tab = self._varsdict['wizard'].notebook.add('expertFitFragment')
    self._varsdict['expertFitFragment_tab'] = tab
    self.__constructExpertFitFragmentTab(tab)

    # 4, should be always
    tab = self._varsdict['wizard'].notebook.add('expertComparisonFragment')
    self._varsdict['expertComparisonFragment_tab'] = tab
    self.__constructExpertComparisonTab(tab)

    # selecting the first tab
    self._varsdict['wizard'].notebook.selectpage(self._varsdict['tablist'][0])

    # adjusting the size
    self._varsdict['wizard'].notebook.setnaturalsize()

    # update the buttons
    self.__update_navibuttons()

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    pass

  def __constructWelcomeTab(self, parent) :
    """Construct the Welcome tab.

    Allows to choose the type of the correlation of vibrational motion :
    Basic  -- fit_fragment  = comparison_fragment
    Expert -- fit_fragment != comparison_fragment

    Positional arguments :
    parent -- parent widget
    
    """
    # image at the left
    lbl_magician = Tkinter.Label(parent,
                                 image=getimage('gears_wizard'))
    lbl_magician.grid(row=0, column=0, padx=20, pady=3, sticky='w')

    # compare nuclear motions
    label_text = 'Correlation mode of vibrational motion'
    widget = Pmw.RadioSelect(parent,
                             buttontype='radiobutton',
                             labelpos='n',
                             label_text=label_text,
                             orient='vertical',
                             frame_relief='ridge',
                             frame_borderwidth=2,
                             command=None)
    self._varsdict['radio_comparison'] = widget
    self._varsdict['radio_comparison'].grid(row=0, column=1,
                                            padx=0, pady=3, sticky='w')

    text_basic  = 'Basic  : The same fragment for alignment and comparison'
    text_expert = 'Expert : Different fragments for alignment and comparison'
    self._varsdict['radio_comparison'].add('basic', text=text_basic)
    self._varsdict['radio_comparison'].add('expert', text=text_expert)
    self._varsdict['radio_comparison'].invoke('basic')

  def __constructBasicTab(self, parent) :
    """Create the Basic tab.
    
    In the basic mode fit_fragment is equal to the comparison_fragment.
    Prefix : basic

    Positional arguments :
    parent -- parent widget
    
    """
    helptext  = 'Fragment for alignment and comparison of nuclear motion'
    helptext2 = \
    'a) Choose the reference and trial molecules from the option menus.\n' + \
    'b) To add an atom pair to the fragment click on an atom in ' + \
    'the reference molecule and than in the trial molecule.'
    self.__constructRefTrialPanel(parent, 'basic', helptext, helptext2)

  def __constructExpertFitFragmentTab(self, parent) :
    """Create the Fit tab.

    Allows to choose a fragment for geometrical alignment.

    Prefix : fit

    Positional arguments :
    parent -- parent widget
    
    """
    helptext  = 'Fragment for alignment'
    helptext2 = 'a) Choose the reference and trial molecules from the ' + \
                'option menus below.\n' + \
                'b) To add an atom pair to the fragment click on an atom' + \
                'in the reference molecule and than in the trial molecule.'
    self.__constructRefTrialPanel(parent, 'fit', helptext, helptext2)

  def __constructExpertComparisonTab(self, parent) :
    """Create the Comparison tab.

    Allows to choose a fragment for comparison of vibrational motion.
    This is the last tab of the expert mode.

    Positional arguments :
    parent -- parent widget
    
    """
    helptext  = 'Fragment for comparison of nuclear motions'
    helptext2 = 'Define a fragment for comparison of nuclear motions.'
    self.__constructRefTrialPanel(parent, 'comparison', helptext, helptext2)

  def __constructAtompairsPanel(self, parent, prefix) :
    """Construct the control panel with the buttons and sync rotation button.

    Positional arguments :
    parent -- parent widget
    prefix -- one of ('basic', 'fit', 'comparison')

    """
    panel = Tkinter.Frame(parent)

    # button toolbar    
    btn_toolbar = widgets.ButtonToolbar(panel, horizontal=False, style=1)
    btn_toolbar.grid(row=0, column=0, padx=3, pady=3, sticky='n')

    btn = btn_toolbar.add_button(imagename='1_to_1',
                                 helptext='Assign the atoms 1 to 1.')
    self._varsdict['%s_btn_one2one' % prefix] = btn

    btn = btn_toolbar.add_button(imagename='remove',
                                 helptext='Remove the selected atom pairs.')
    self._varsdict['%s_btn_pairs_remove' % prefix] = btn

    btn = btn_toolbar.add_button(imagename='remove_all',
                                 helptext='Remove all atom pairs.')
    self._varsdict['%s_btn_pairs_remove_all' % prefix] = btn

    if 'comparison' != prefix :
      helptext = 'Align the orientation of the molecules.'
      btn = btn_toolbar.add_button(imagename='align', helptext=helptext)
      self._varsdict['%s_btn_align' % prefix] = btn

      # synchronize the rotation and zoom
      widget = Pmw.RadioSelect(panel, selectmode='multiple')
      self._varsdict['%s_radio_sync' % prefix] = widget
      self._varsdict['%s_radio_sync' % prefix].grid(row=1, column=0,
                                                    padx=0, pady=3, sticky='n')
      self._varsdict['%s_radio_sync' % prefix].add('syncrotzoom',
                                                   image=getimage('rotate'))
    return panel

  def __constructCorrelatePanel(self, parent, prefix) :
    """Construct the correlate panel.

    Positional arguments :
    parent -- parent widget
    prefix -- one of ('basic', 'fit', 'comparison')
    
    """
    panel = Pmw.Group(parent, tag_text='Correlation options')

    self._varsdict['%s_var_do_align' % prefix]       = Tkinter.IntVar()
    self._varsdict['%s_var_use_Lx' % prefix]         = Tkinter.IntVar()
    self._varsdict['%s_var_remove_tr_rot' % prefix]  = Tkinter.IntVar()
    self._varsdict['%s_var_include_tr_rot' % prefix] = Tkinter.IntVar()
    
    self._varsdict['%s_var_do_align' % prefix].set(1)
    self._varsdict['%s_var_use_Lx' % prefix].set(0)
    self._varsdict['%s_var_remove_tr_rot' % prefix].set(0)
    self._varsdict['%s_var_include_tr_rot' % prefix].set(0)
    
    ## controls
    # the alignment can be canceled only in the basic mode !!!
    var = self._varsdict['%s_var_do_align' % prefix]
    widget = Tkinter.Checkbutton(panel.interior(),
                                 text='Do alignment',
                                 variable=var)
    self._varsdict['%s_check_do_align' % prefix] = widget
    
    if 'basic' == prefix :
      self._varsdict['%s_check_do_align' % prefix].grid(row=0, column=0,
                                                        padx=3, pady=3,
                                                        sticky='w')

    menubutton_width = max(len(resources.STRINGS_ALIGNMENT_TYPES[0]),
                           len(resources.STRINGS_ALIGNMENT_TYPES[1]))
    widget = Pmw.OptionMenu(panel.interior(),
                            #items=resources.STRINGS_ALIGNMENT_TYPES,
                            items=(resources.STRING_ALIGNMENT_ORIENTATIONAL,),
                            menubutton_width=menubutton_width)
    self._varsdict['%s_options_align' % prefix] = widget
    
    if 'basic' == prefix :
      self._varsdict['%s_options_align' % prefix].grid(row=0, column=1,
                                                       padx=3, pady=3,
                                                       sticky='w')

    # remove translations / rotations checkbutton
    var = self._varsdict['%s_var_remove_tr_rot' % prefix]
    widget = Tkinter.Checkbutton(panel.interior(),
                                 text='Remove non-vibrational contaminations',
                                 variable=var,
                                 command=None)
    self._varsdict['%s_check_remove_tr_rot' % prefix] = widget
    self._varsdict['%s_check_remove_tr_rot' % prefix].grid(row=0, column=2,
                                                           padx=0, pady=3,
                                                           sticky='w')
    # include translations / rotations checkbutton
    var = self._varsdict['%s_var_include_tr_rot' % prefix]
    widget = Tkinter.Checkbutton(panel.interior(),
                                 text='Include translations / rotations',
                                 variable=var,
                                 command=None)
    self._varsdict['%s_check_do_tr_rot' % prefix] = widget    
    self._varsdict['%s_check_do_tr_rot' % prefix].grid(row=0, column=3,
                                                       padx=0, pady=3,
                                                       sticky='w')
    # rightmost button : correlate
    widget = Tkinter.Button(parent,
                            image=getimage('gears'),
                            text='Correlate',
                            compound='top')
    self._varsdict['%s_btn_correlate' % prefix] = widget
    self._varsdict['%s_btn_correlate' % prefix].grid(row=2, column=1,
                                                     padx=3, pady=3,
                                                     sticky='e')
    return panel

  def __constructMoleculePanel(self, parent, prefix, moltype) :
    """Construct the panel for the molecule.

    Positional arguments :
    parent  -- parent widget
    prefix  -- one of ('basic', 'fit', 'comparison')
    moltype -- one of ('ref', 'tr')

    """
    tag_text = 'ref' == moltype and 'Reference molecule' or 'Trial molecule'
      
    mol_panel = Pmw.Group(parent, tag_text=tag_text)

    mol_panel.interior().grid_columnconfigure(0, weight=1)
    mol_panel.interior().grid_rowconfigure(1, weight=1)

    ## for the comparison tab show only the name of a molecule
    if 'comparison' == prefix :
      # name
      textvar = Tkinter.StringVar()
      self._varsdict['comparison_var_%s_mol_name' % moltype] = textvar
      lbl_name = Tkinter.Label(mol_panel.interior(),
                               textvariable=textvar,
                               font=resources.get_font_molecules(self),
                               relief='ridge',
                               anchor='c')
      lbl_name.grid(row=0, column=0, padx=3, pady=3, sticky='we')

    ## for the basis and fit tabs show all opened molecules
    else :
      # option menu with opened molecules names
      widget = Pmw.OptionMenu(mol_panel.interior(),
                              items=self._varsdict['opened_windows_titles'])
      self._varsdict['%s_options_%s_mol' % (prefix, moltype)] = widget
      self._varsdict['%s_options_%s_mol' % (prefix, moltype)].grid(row=0,
                                                                   column=0,
                                                                   padx=3,
                                                                   pady=3,
                                                                   sticky='we')
    # vtk window for the molecule
    if 'basic' == prefix :
      color_picked = resources.COLOR_PICKED_ATOM
    elif 'fit' == prefix :
      color_picked = resources.COLOR_PICKED_ATOM_FIT
    else :
      color_picked = resources.COLOR_PICKED_ATOM_COMPARISON

    resolution = self._mainApp.settings['resolution']
    widget = widgets.MoleculeRenderWidget(mol_panel.interior(),
                                          molecule=None,
                                          width=300,
                                          height=300,
                                          resolution=resolution,
                                          color_picked_atom=color_picked)
    self._varsdict['%s_%s_mol_widget' % (prefix, moltype)] = widget
    self._varsdict['%s_%s_mol_widget' % (prefix, moltype)].grid(row=1,
                                                                column=0,
                                                                padx=3,
                                                                pady=3,
                                                                sticky='news')

    return mol_panel

  def __constructRefTrialPanel(self, parent, prefix, tag_text, helptext) :
    """Construct a big panel containing the both reference and trial widgets.

    Positional arguments :
    parent   -- parent widget
    prefix   -- one of ('basic', 'fit', 'comparison')
    tag_text -- caption of the group
    helptext -- help text shown at the top
    
    """
    parent.grid_columnconfigure(0, weight=1)
    parent.grid_rowconfigure(1, weight=1)
    
    group_fragment = Pmw.Group(parent, tag_text=tag_text)
    group_fragment.grid(row=1, column=0, columnspan=2,
                        padx=3, pady=3, sticky='news')

    group_fragment.interior().grid_columnconfigure(0, weight=1)
    group_fragment.interior().grid_columnconfigure(2, weight=1)
    group_fragment.interior().grid_rowconfigure(1, weight=1)

    ## help on the top of the frame - spans three columns !    
    info_widget = widgets.InfoWidget(group_fragment.interior(),
                                     text=helptext,
                                     height=4)
    info_widget.grid(row=0, column=0, columnspan=3,
                     padx=3, pady=3, sticky='we')
    
    ## reference molecule on the left side
    ref_mol_panel = self.__constructMoleculePanel(group_fragment.interior(),
                                                  prefix, 'ref')
    ref_mol_panel.grid(row=1, column=0, padx=3, pady=3, sticky='news')
    
    ## selected atom pairs in the middle
    # selectioncommand will be configured at the end of the function
    group_pairs = Pmw.Group(group_fragment.interior(), tag_text='Atom pairs')
    group_pairs.grid(row=1, column=1, padx=3, pady=3, sticky='news')

    group_pairs.interior().grid_columnconfigure(0, weight=1)
    group_pairs.interior().grid_rowconfigure(0, weight=1)

    widget = Pmw.ScrolledListBox(group_pairs.interior(),
                                 items=(),
                                 listbox_selectmode='multiple',
                                 vscrollmode='static',
                                 listbox_width=15)
    self._varsdict['%s_listbox_pairs' % prefix] = widget
    self._varsdict['%s_listbox_pairs' % prefix].grid(row=0, column=0,
                                                     padx=3, pady=3,
                                                     sticky='wn')
    
    ## atom pairs button panel
    panel = self.__constructAtompairsPanel(group_pairs.interior(), prefix)
    panel.grid(row=0, column=1, padx=0, pady=0, sticky='en')
    
    ## trial molecule on the right side
    tr_mol_panel = self.__constructMoleculePanel(group_fragment.interior(),
                                                 prefix, 'tr')
    tr_mol_panel.grid(row=1, column=2, padx=3, pady=3, sticky='news')

    # binding the reference and trial widgets together
    # so that the camera state could be synchronized
    ref_widget = self._varsdict['%s_ref_mol_widget' % prefix]
    tr_widget  = self._varsdict['%s_tr_mol_widget' % prefix]
    
    ref_widget.synchronize_camera_state(tr_widget)
    tr_widget.synchronize_camera_state(ref_widget)

    # correlation panel for 'basic' and 'comparison'
    if 'fit' != prefix :
      corr_panel = self.__constructCorrelatePanel(parent, prefix)
      corr_panel.grid(row=2, column=0, padx=3, pady=3, sticky='w')

    ## configure the commands for the controls
    # keywords for all purposes
    kw = dict(listbox=self._varsdict['%s_listbox_pairs' % prefix],
              picked_atom_pairs=self._varsdict[\
                '%s_picked_atom_pairs' % prefix],
              btn_pairs_remove=self._varsdict[\
                '%s_btn_pairs_remove' % prefix],
              btn_pairs_remove_all=self._varsdict[\
                '%s_btn_pairs_remove_all' % prefix])

    if prefix in ('basic', 'fit') :
      kw['btn_align']  = self._varsdict['%s_btn_align' % prefix]
      kw['radio_sync'] = self._varsdict['%s_radio_sync' % prefix]

    if prefix in ('basic', 'comparison') :
      kw['options_align']      = self._varsdict['%s_options_align' % prefix]
      kw['btn_correlate']      = self._varsdict['%s_btn_correlate' % prefix]
      kw['var_do_align']       = self._varsdict['%s_var_do_align' % prefix]
      kw['var_use_Lx']         = self._varsdict['%s_var_use_Lx' % prefix]
      kw['var_include_tr_rot'] = self._varsdict[\
        '%s_var_include_tr_rot' % prefix]
      kw['var_remove_tr_rot']  = self._varsdict[\
        '%s_var_remove_tr_rot' % prefix]

    # saving the keywords
    self._varsdict['%s_kw' % prefix] = kw

    # option menus
    if prefix in ('basic', 'fit') :
      command_options_ref = Command(self.__set_new_molecule,
                               self._varsdict['%s_options_ref_mol' % prefix],
                               self._varsdict['%s_ref_mol_widget' % prefix],
                               self._varsdict['%s_ref_mol_widget' % prefix],
                               self._varsdict['%s_tr_mol_widget' % prefix],
                               **kw)
      self._varsdict['%s_options_ref_mol' % prefix].configure(
        command=command_options_ref)

      command_options_tr = Command(self.__set_new_molecule,
                             self._varsdict['%s_options_tr_mol' % prefix],
                             self._varsdict['%s_tr_mol_widget' % prefix],
                             self._varsdict['%s_ref_mol_widget' % prefix],
                             self._varsdict['%s_tr_mol_widget' % prefix],
                             **kw)
      self._varsdict['%s_options_tr_mol' % prefix].configure(
        command=command_options_tr)

      # align molecules
      command_align_molecules = Command(self.__align_molecules,
                                        self._varsdict[\
                                          '%s_ref_mol_widget' % prefix],
                                        self._varsdict[\
                                          '%s_tr_mol_widget' % prefix],
                                        self._varsdict[\
                                          '%s_picked_atom_pairs' % prefix])
      self._varsdict['%s_btn_align' % prefix].configure(
        command=command_align_molecules)

      # synchronize rotation/zoom
      command_syncrotation = Command(self.__set_sync_rotation,
                                     self._varsdict[\
                                       '%s_ref_mol_widget' % prefix],
                                     self._varsdict[\
                                       '%s_tr_mol_widget' % prefix],
                                     self._varsdict[\
                                       '%s_picked_atom_pairs' % prefix])
      self._varsdict['%s_radio_sync' % prefix].configure(
        command=command_syncrotation)

    if prefix in ('basic', 'comparison') :
      # do align
      self._varsdict['%s_check_do_align' % prefix].configure(
        command=Command(self.__validate_user_input, **kw))

      ## basic
      if 'basic' == prefix :
        fit_atoms    = self._varsdict['basic_picked_atom_pairs']
        comp_atoms   = self._varsdict['basic_picked_atom_pairs']
        
      else :
        fit_atoms    = self._varsdict['fit_picked_atom_pairs']
        comp_atoms   = self._varsdict['comparison_picked_atom_pairs']
            
      # correlate
      command_correlate = Command(self.__correlate,
                                  self._varsdict['%s_ref_mol_widget' % prefix],
                                  self._varsdict['%s_tr_mol_widget' % prefix],
                                  fit_atoms,
                                  comp_atoms,
                                  **kw)
      self._varsdict['%s_btn_correlate' % prefix].configure(
        command=command_correlate)
    
    # listbox select command
    sel_command = Command(self.__highlight_picked_pairs,
                          self._varsdict['%s_ref_mol_widget' % prefix],
                          self._varsdict['%s_tr_mol_widget' % prefix],
                          **kw)
    self._varsdict['%s_listbox_pairs' % prefix].configure(
      selectioncommand=sel_command)

    # 1:1 button
    command_1_to_1 = Command(self.__one2one,
                             self._varsdict['%s_ref_mol_widget' % prefix],
                             self._varsdict['%s_tr_mol_widget' % prefix],
                             **kw)
    
    self._varsdict['%s_btn_one2one' % prefix].configure(command=command_1_to_1)
    
    # remove pairs
    command_remove_pairs = Command(self.__remove_pairs_from_listbox,
                                   self._varsdict['%s_ref_mol_widget' % prefix],
                                   self._varsdict['%s_tr_mol_widget' % prefix],
                                   **kw)
    self._varsdict['%s_btn_pairs_remove' % prefix].configure(
      command=command_remove_pairs)

    # remove all
    command_remove_all_pairs = Command(self.__remove_all_pairs,
                                       self._varsdict[\
                                         '%s_ref_mol_widget' % prefix],
                                       self._varsdict[\
                                         '%s_tr_mol_widget' % prefix],
                                       **kw)
    self._varsdict['%s_btn_pairs_remove_all' % prefix].configure(
      command=command_remove_all_pairs)

    ## highlighting the atoms in the both widget
    # on the left clicked on a picked atom.
    clicked_atom_ref = Command(self.__highlight_clicked_pair,
                               self._varsdict['%s_ref_mol_widget' % prefix],
                               self._varsdict['%s_tr_mol_widget' % prefix],
                               self._varsdict['%s_ref_mol_widget' % prefix],
                               **kw)
    clicked_atom_tr  = Command(self.__highlight_clicked_pair,
                               self._varsdict['%s_ref_mol_widget' % prefix],
                               self._varsdict['%s_tr_mol_widget' % prefix],
                               self._varsdict['%s_tr_mol_widget' % prefix],
                               **kw)

    self._varsdict['%s_ref_mol_widget' % prefix].clicked_atom_callback = \
                                       clicked_atom_ref
    self._varsdict['%s_tr_mol_widget' % prefix].clicked_atom_callback = \
                                       clicked_atom_tr

    ## invoking the molecules ;)
    if prefix in ('basic', 'fit') :
      if self.__ref_mol is not None :
        index_ref = self.__find_molecule_index(self.__ref_mol)

        if 0 < len(self._varsdict['opened_windows_titles']) :
          self._varsdict['%s_options_ref_mol' % prefix].invoke(index_ref)
      else :
        self._varsdict['%s_options_ref_mol' % prefix].invoke(0)

      if self.__tr_mol is not None :
        index_tr = self.__find_molecule_index(self.__tr_mol)
        
        if 0 < len(self._varsdict['opened_windows_titles']) :
          self._varsdict['%s_options_tr_mol' % prefix].invoke(index_tr)
      else :
        self._varsdict['%s_options_tr_mol' % prefix].invoke(0)

      # installing the camera of the reference widget to the trial
      tr_widget.camera = ref_widget.camera

    ## validate
    self.__validate_user_input(**kw)

  def __changeto_ExpertComparisonFragment(self) :
    """Set the molecules when going to the comparison fragment tab."""
    # titles    
    self._varsdict['comparison_var_ref_mol_name'].set(
      self._varsdict['fit_options_ref_mol'].getvalue())
    self._varsdict['comparison_var_tr_mol_name'].set(
      self._varsdict['fit_options_tr_mol'].getvalue())

    # molecules in the widgets
    self._varsdict['comparison_ref_mol_widget'].molecule = \
           self._varsdict['fit_ref_mol_widget'].molecule
    self._varsdict['comparison_tr_mol_widget'].molecule  = \
           self._varsdict['fit_tr_mol_widget'].molecule

    self.__init_picking(self._varsdict['comparison_ref_mol_widget'],
                        self._varsdict['comparison_tr_mol_widget'],
                        **self._varsdict['comparison_kw'])

    # align the orientations
    # installing the same camera
    self._varsdict['comparison_ref_mol_widget'].camera = \
           self._varsdict['fit_ref_mol_widget'].camera
    
    self.__align_molecules(self._varsdict['comparison_ref_mol_widget'],
                           self._varsdict['comparison_tr_mol_widget'],
                           self._varsdict['fit_picked_atom_pairs'])

    # setting the fitted fragment as the default choice
    self.__add_pairs2listbox(self._varsdict['fit_picked_atom_pairs'],
                             self._varsdict['comparison_ref_mol_widget'],
                             self._varsdict['comparison_tr_mol_widget'],
                             **self._varsdict['comparison_kw'])

  def __init_picking(self, ref_widget=None, tr_widget=None, **kw) :
    """Initialize the picking."""
    if ref_widget is None or tr_widget is None or kw is None :
      return

    if kw.get('listbox', None) is None :
      return
    
    # remove picked atoms if there are some
    ref_widget.depick_atoms()
    tr_widget.depick_atoms()

    kw['listbox'].clear()
    
    del kw['picked_atom_pairs'][:]

    callback_picking = Command(self.__add_pair2listbox,
                               ref_widget, tr_widget, **kw)
    
    ref_widget.start_pairs_picking(kw['picked_atom_pairs'], callback_picking)
    tr_widget.start_pairs_picking(kw['picked_atom_pairs'] , callback_picking)

    # one should start with the reference molecule
    tr_widget.do_picking = False
    
    self.__validate_user_input(**kw)

  def __set_new_molecule(self, item,
                         option_menu, widget,
                         ref_widget, tr_widget, **kw) :
    """Show the currently selected molecule from option_menu in vtkWidget."""
    if option_menu is None or widget is None :
      return

    index_sel = option_menu.index(Pmw.SELECT)

    if len(self._varsdict['opened_molecules']) > index_sel :
      widget.molecule = self._varsdict['opened_molecules'][index_sel]

      self.__init_picking(ref_widget, tr_widget, **kw)

  def __find_molecule_index(self, mol) :
    """Find a molecule in the list of the opened molecules.

    Positional arguments :
    mol -- molecule to be found

    Return 0 if not found.
    
    """
    if not self._varsdict['opened_molecules'] or mol is None :
      return 0

    if mol in self._varsdict['opened_molecules'] :
      return self._varsdict['opened_molecules'].index(mol)
    else :
      return 0

  def __highlight_picked_pairs(self, ref_widget, tr_widget, **kw) :
    """Highlight picked atoms in given reference and trial widgets."""
    if kw is None or not 'listbox' in kw or \
       ref_widget is None or tr_widget is None :
      raise InvalidArgumentError('Invalid arguments')
    
    sel_indices, notsel_indices = self._get_listbox_indices(kw['listbox'])

    ref_widget.highlight_picked_atoms(sel_indices, True)
    ref_widget.highlight_picked_atoms(notsel_indices, False)
    
    tr_widget.highlight_picked_atoms(sel_indices, True)
    tr_widget.highlight_picked_atoms(notsel_indices, False)

    # validate
    self.__validate_user_input(**kw)

  def _get_listbox_indices(listbox) :
    """Get selected and not selected pairs from a given listbox."""
    sel_atom_pairs = listbox.getvalue()
    all_elements   = listbox.get()

    sel_indices    = []
    notsel_indices = []

    for i in xrange(len(all_elements)) :
      if all_elements[i] in sel_atom_pairs :
        sel_indices.append(i)
      else :
        notsel_indices.append(i)

    return sel_indices, notsel_indices

  _get_listbox_indices = staticmethod(_get_listbox_indices)

  def __validate_user_input(self, **kw) :
    """Validate the controls supplied in the keyword parameters."""
    if kw is None :
      return
    
    ## list manipulation buttons
    if 'listbox' in kw :
      indices = self._get_listbox_indices(kw['listbox'])
    
    # no items selected - nothing to delete
    if kw.has_key('btn_pairs_remove') and kw['btn_pairs_remove'] :
      state = 'normal'
      if 0 == len(indices[0]) :
        state = 'disabled'
      
      kw['btn_pairs_remove'].configure(state=state)

    # no items at all - cannot remove all
    if kw.has_key('btn_pairs_remove_all') and kw['btn_pairs_remove_all'] :
      state = 'normal'
      if 0 == ( len(indices[0]) + len(indices[1]) ) :
        state = 'disabled'

      kw['btn_pairs_remove_all'].configure(state=state)
    
    ## alignment
    # disable the option menu if an alignment is supressed
    if kw.has_key('options_align') and kw['options_align'] is not None :
      if kw['var_do_align'].get() :
        state = 'normal'
      else :
        state = 'disabled'
        
      kw['options_align'].configure(menubutton_state=state)
    
    ## correlate & align buttons, synchronize rotation radio button
    # 1) min. two pairs must be given; 2) all pairs should be complete
    state = 'disabled'
    if kw.has_key('picked_atom_pairs') and \
       kw['picked_atom_pairs'] is not None :
      if 2 > len(kw['picked_atom_pairs']) :
        state = 'disabled'
      else :
        # no uncompleted pairs !
        state = 'normal'
        for p in kw['picked_atom_pairs'] :
          if -1 in p :
            state = 'disabled'
            break 
    else :
      state = 'disabled'

    if kw.get('btn_correlate', None) is not None :
      kw['btn_correlate'].configure(state=state)

    if kw.get('btn_align', None) is not None :
      kw['btn_align'].configure(state=state)

    # synchronous rotation
    # if there are not enough atoms for alignment -> turn off and block
    if kw.get('radio_sync', None) is not None :
      kw['radio_sync'].button(0).configure(state=state)
      
      if 'disabled' == state :
        # the following invokes the command for the disabled button
        kw['radio_sync'].setvalue(['syncrotzoom'])
        kw['radio_sync'].invoke(0)

    # block the next button if the user has not chosen
    # minimum two atom pairs for alignment
    if 'expertFitFragment' == self.__get_current_tab() :
      self._varsdict['wizard'].buttonbox.button(1).configure(state=state)

  def __one2one(self, ref_widget, tr_widget, **kw) :
    """Add atom pairs 1:1."""
    if ref_widget is None or tr_widget is None or \
       kw is None or not 'listbox' in kw or not 'picked_atom_pairs' in kw :
      raise InvalidArgumentError('Invalid arguments')
    
    n = min(ref_widget.molecule.Natoms, tr_widget.molecule.Natoms)
    
    # clean first
    self.__init_picking(ref_widget, tr_widget, **kw)

    # disabling the button so that could not start
    # without the 1:1 having been finished !
    if 'btn_correlate' in kw and 'btn_correlate' in kw :
      kw['btn_correlate'].configure(state='disabled')

    for a in xrange(n) :
      kw['picked_atom_pairs'].append([a, a])

      pair_str = '%3d%5s%3d' % ( 1 + a, '', 1 + a )
      kw['listbox'].insert('end', pair_str)
      self.tk.call('update', 'idletasks')
      
      ref_widget.pick_atoms((a,))
      tr_widget.pick_atoms((a,))

    # validate
    self.__validate_user_input(**kw)

  def __remove_pairs_from_listbox(self, ref_widget, tr_widget, **kw) :
    """Remove selected atom pairs from the list."""
    if ref_widget is None or tr_widget is None or kw is None or \
       not 'listbox' in kw or not 'picked_atom_pairs' in kw :
      raise InvalidArgumentError('Invalid arguments')
    
    all_elements = kw['listbox'].get()
    sel_indices, notsel_indices = self._get_listbox_indices(kw['listbox'])

    # deleting from the list
    kw['listbox'].clear()
    
    for i in xrange(len(all_elements)) :
      if i not in sel_indices :
        kw['listbox'].insert('end', all_elements[i])

    # deleting from the widgets    
    ref_widget.depick_atoms(sel_indices)
    tr_widget.depick_atoms(sel_indices)

    misc.remove_indices_from_list(kw['picked_atom_pairs'], sel_indices)

    ref_atoms = [ p[0] for p in kw['picked_atom_pairs'] ]
    tr_atoms  = [ p[1] for p in kw['picked_atom_pairs'] ]

    # 
    if -1 in tr_atoms :
      ref_widget.do_picking = False
      tr_widget.do_picking  = True
    else :
      ref_widget.do_picking = True
      tr_widget.do_picking  = False

    # validate
    self.__validate_user_input(**kw)

  def __remove_all_pairs(self, ref_widget, tr_widget, **kw) :
    """Remove all atom pairs from the list."""
    if ref_widget is None or tr_widget is None :
      raise InvalidArgumentError('Invalid arguments')
    
    self.__init_picking(ref_widget, tr_widget, **kw)
    self.__validate_user_input(**kw)

  def __add_pair2listbox(self, widget, ref_widget, tr_widget, **kw) :
    """Update the listbox."""
    if kw is None or not 'listbox' in kw or \
       not 'picked_atom_pairs' in kw :
      raise InvalidArgumentError('Invalid arguments')

    for w in (ref_widget, tr_widget, widget) :
      if w is None :
        return

    if 1 > len(kw['picked_atom_pairs']) :
      return

    pairs     = kw['picked_atom_pairs']
    last_pair = pairs[len(pairs)-1]

    ref_widget.do_picking = 0 == last_pair.count(-1)
    tr_widget.do_picking = (-1 == last_pair[1])

    # finally update the GUI control
    vals = kw['listbox'].get('end').split()
    if 2 == len(vals) and 0 == int(vals[1]) :
      kw['listbox'].delete('end')
      
    pair_str = '%3d%5s%3d' % (1 + last_pair[0], '', 1 + last_pair[1])
    kw['listbox'].insert('end', pair_str)

    # validate
    self.__validate_user_input(**kw)

  def __correlate(self, ref_widget, tr_widget,
                  fit_pairs, comparison_pairs, **kw) :
    """Start a correlation.

    fit_pairs & comparison_pairs are 0-based => has to be recalculated.
    
    """
    for a in (ref_widget, tr_widget, fit_pairs, comparison_pairs, kw) :
      if a is None :
        raise InvalidArgumentError('Invalid arguments')

    vars_list = ('var_do_align', 'var_use_Lx',
                 'var_include_tr_rot', 'options_align')
    
    for var in vars_list :
      if var not in kw :
        raise InvalidArgumentError('Required parameter missing %s' % var)
    
    # go
    ref_mol = ref_widget.molecule
    tr_mol  = tr_widget.molecule

    # pairs for fitting
    fit_atompairs = self._make_atompairs(fit_pairs)

    # pairs for comparison of nuclear motion
    comparison_atompairs = self._make_atompairs(comparison_pairs)
    
    # Aligning if requested
    if kw['var_do_align'].get() :
      if resources.STRING_ALIGNMENT_ORIENTATIONAL == \
         kw['options_align'].getvalue() :
        # Orientational alignment
        # weights are one-based
        weight = [0.]
        for p in fit_pairs :
          weight.append(0.5*(ref_mol.masses[p[0]+1] + tr_mol.masses[p[1]+1]))

        ans_fit = qtrfit.fit(fit_atompairs, ref_mol.coords, tr_mol.coords,
                             array(weight))
        U = ans_fit['U']
      else :
        # Alignment of the inertia axes
##        ans_inertia = align_inertia_axes(fit_atompairs,
##                                         ref_mol.coords, ref_mol.masses,
##                                         tr_mol.coords, tr_mol.masses)
##        U = ans_inertia['U']
        raise NotImplementedError(
          'Aligning of the inertia axes is not implemented yet...')
    else :
      U = None    

    # finding apropriate displacements
    if kw['var_use_Lx'].get() :
      L_ref = ref_mol.Lx_norm
      L_tr  = tr_mol.Lx_norm
    else :
      L_ref = ref_mol.L
      L_tr  = tr_mol.L

    # include translations / rotations ?
    if kw['var_use_Lx'].get() :
      L_tr_rot_ref = ref_mol.Lx_tr_rot_norm
      L_tr_rot_tr  = tr_mol.Lx_tr_rot_norm

    else :
      L_tr_rot_ref = ref_mol.L_tr_rot
      L_tr_rot_tr  = tr_mol.L_tr_rot

    # generate translations/rotations of the reference & trial FRAGMENTs
    # do not make these motions orthogonal to other vibrations
    a_ref = vibrations.generate_tr_rot(None, ref_mol.coords, ref_mol.masses,
                                       atom_list=comparison_atompairs[:, 0])
    a_tr  = vibrations.generate_tr_rot(None, tr_mol.coords, tr_mol.masses,
                                       atom_list=comparison_atompairs[:, 1])

    L_tr_rot_F_ref = a_ref['L_tr_rot']
    L_tr_rot_F_tr  = a_tr['L_tr_rot']

    # finally start ;)
    text = 'Correlating vibrations, please wait...'
    splash = widgets.SplashScreen(self, text)
    
    # for statistics
    start_time = strftime(resources.STRING_FORMAT_TIME, localtime())
    t0 = os.times()

    cor_kw = dict(atom_pairs=comparison_atompairs,
                  U=U,
                  include_tr_rot=kw['var_include_tr_rot'].get(),
                  remove_tr_rot=kw['var_remove_tr_rot'].get(),
                  L_tr_rot_F_ref=L_tr_rot_F_ref,
                  L_tr_rot_F_tr=L_tr_rot_F_tr)

    ans_corr = vibrations.correlate_vibrations_all(L_ref, L_tr_rot_ref,
                                                   L_tr, L_tr_rot_tr,
                                                   **cor_kw)
    t1 = os.times()
    splash.destroy()
    
    # pack and show the results
    results_all = ans_corr.copy()

    results_all['atom_pairs']   = comparison_atompairs

    results_all['start_time']   = start_time
    results_all['t0']           = t0
    results_all['t1']           = t1

    results_all['ref_mol']      = ref_mol
    results_all['tr_mol']       = tr_mol

    if kw['var_do_align'].get() :
      results_all['alignment'] = kw['options_align'].getvalue()

      if resources.STRING_ALIGNMENT_ORIENTATIONAL == \
         kw['options_align'].getvalue() :
        for item in ans_fit.iteritems() :
          results_all[item[0]]  = item[1]        
      else :
        for item in ans_inertia.iteritems() :
          results_all[item[0]]  = item[1]
        
    else :
      results_all['alignment'] = None
      results_all['U']         = None

    results_all['use_Lx']         = kw['var_use_Lx'].get()
    results_all['include_tr_rot'] = kw['var_include_tr_rot'].get()
    results_all['remove_tr_rot']  = kw['var_remove_tr_rot'].get()

    # camera for the reference widget
    results_all['ref_camera']  = ref_widget.camera

    # show the window with the results in maxized state
    results_wnd = CorrelationResultsWindow(self._mainApp,
                                           results_all,
                                           goback_window=self,
                                           startpage=
                                           self._smartdict['startpage'])
    results_wnd.maximize()

  def _make_atompairs(pairs) :
    """Make a one-based ndarray from a 0-based list pairs."""
    atompairs = [ [ 1 + p[0], 1 + p[1] ] for p in pairs ]
    return array(atompairs)

  _make_atompairs = staticmethod(_make_atompairs)

  def __align_molecules(self, ref_widget, tr_widget, fit_pairs) :
    """Align the trial molecule."""
    for w in (ref_widget, tr_widget, fit_pairs) :
      if w is None :
        return

    # find a rotation matrix
    fit_atompairs = self._make_atompairs(fit_pairs)

    ref_mol = ref_widget.molecule
    tr_mol  = tr_widget.molecule
    
    weight = [0.] + \
             [ (ref_mol.masses[p[0]+1] + tr_mol.masses[p[1]+1]) * 0.5 \
               for p in fit_pairs ]

    ans_fit = qtrfit.fit(fit_atompairs, ref_mol.coords, tr_mol.coords,
                         array(weight))
    U = ans_fit['U']
    
    # set the common point of view ;)
    tr_widget.camera = ref_widget.camera

    # rotate the trial camera if a rotation matrix is given
    rotmatrix = vtkMatrix4x4()

    for i in xrange(3) :
      for j in xrange(3) :
        rotmatrix.SetElement(i, j, U[1+j, 1+i])

    transform = vtkTransform()
    transform.SetMatrix(rotmatrix)

    # translate the focal point of the trial camera
    # to the center of the trial fragment    
    tr_widget.camera.ApplyTransform(transform)
    tr_widget.Render()

  def __back(self) :
    """Back button callback of the wizard."""
    curtab = self.__get_current_tab()
    mode   = self._varsdict['radio_comparison'].getvalue()

    page = None
    # back to the welcome tab in the basic mode
    if ('basic' == mode and 'basic' == curtab) :
      page = 'welcome'

    # back in the expert mode
    else :
      if 'expertFitFragment' == curtab :
        page = 'welcome'
      else :
        page = 'expertFitFragment'
    if page is not None :
      self._varsdict['wizard'].notebook.selectpage(page)

    self.__update_navibuttons()

  def __next(self) :
    """Next button callback of the wizard."""
    curtab = self.__get_current_tab()
    mode   = self._varsdict['radio_comparison'].getvalue()

    page = None
    # next in the basic mode
    if 'basic' == mode and 'welcome' == curtab :
      page = 'basic'
    else :
      if 'welcome' == curtab :
        page = 'expertFitFragment'
      else :
        page = 'expertComparisonFragment'

    if page is not None :
      self._varsdict['wizard'].notebook.selectpage(page)

      # set the information for the comparison of nuclear motions properly
      if 'expertComparisonFragment' == page :
        self.__changeto_ExpertComparisonFragment()

    self.__update_navibuttons()

  def __update_navibuttons(self) :
    """Update the state of the back / next buttons."""
    curtab = self.__get_current_tab()
    mode   = self._varsdict['radio_comparison'].getvalue()

    # back button
    state = 'normal'
    if 'welcome' == curtab :
      state = 'disabled'

    self._varsdict['wizard'].buttonbox.button(0).configure(state=state)

    # next button
    state = 'normal'
    if ('basic' == mode and 'basic' == curtab) or \
       ('expert' == mode and 'expertComparisonFragment' == curtab) :
      state = 'disabled'

    self._varsdict['wizard'].buttonbox.button(1).configure(state=state)

    # validate the expert fit page for the first time
    self.__validate_user_input(**self._varsdict['fit_kw'])

  def __get_current_tab(self) :
    """Get the current wizard tab."""
    return self._varsdict['wizard'].notebook.getcurselection()

  def __add_pairs2listbox(self, pairs, ref_widget, tr_widget, **kw) :
    """Add pairs to the listbox."""
    for a in (ref_widget, tr_widget, pairs) :
      if a is None :
        return
    
    if kw is None or not 'listbox' in kw or not 'picked_atom_pairs' in kw :
      raise InvalidArgumentError('Invalid arguments')
    
    for p in pairs :
      kw['picked_atom_pairs'].append(p)

      pair_str = '%3d%5s%3d' % (1 + p[0], '', 1 + p[1])
      kw['listbox'].insert('end', pair_str)
      self.tk.call('update', 'idletasks')
      
      ref_widget.pick_atoms((p[0],))
      tr_widget.pick_atoms((p[1],))

    self.__validate_user_input(**kw)

  def __highlight_clicked_pair(self, num, node_index,
                               ref_widget, tr_widget, widget, **kw) :
    """Highlight atoms.

    Remove the highlighting if it is already present.
    Callback for the clicked_atom_callback.
    
    """
    #for a in (ref_widget, tr_widget, widget, kw) :
    #  if a is None :
    #    return

    picked_atom_pairs = kw['picked_atom_pairs']
    listbox = kw['listbox']

    # processing only right clicks
    if 3 != num :
      return

    # processing only picked atoms
    node = widget.get_node('atoms', node_index)
    if node is None or not node.get_picked() :
      return

    to_highlight = not node.get_highlighted()

    # find the atom index in the picked pairs
    pair_index = self._find_picked_pair(node_index, picked_atom_pairs,
                                        widget is ref_widget)
    if -1 == pair_index :
      return

    # highlighting in the both widgets
    node_ref = ref_widget.get_node('atoms', picked_atom_pairs[pair_index][0])
    node_tr  = tr_widget.get_node('atoms', picked_atom_pairs[pair_index][1])

    if node_ref :
      node_ref.highlight_picked(to_highlight)

    if node_tr :
      node_tr.highlight_picked(to_highlight)

    ref_widget.Render()
    tr_widget.Render()
    
    # selecting the pair in the listbox
    cur_sel = list(listbox.getvalue())
    affected_item = listbox.get()[pair_index]

    if to_highlight :
      cur_sel.append(affected_item)
    else :
      if affected_item in cur_sel :
        index = cur_sel.index(affected_item)
        del cur_sel[index]
      
    listbox.setvalue(cur_sel)

    self.__validate_user_input(**kw)

  def _find_picked_pair(index, picked_atom_pairs, in_ref) :
    """Find an atom in the reference or trial picked atom list.

    All indices are 0-based.
    Return -1 if nothing was found.
    
    """
    if picked_atom_pairs is None or 0 == len(picked_atom_pairs) :
      return -1

    if in_ref :
      li = array(picked_atom_pairs)[:, 0].tolist()
    else :
      li = array(picked_atom_pairs)[:, 1].tolist()

    if index in li :
      return li.index(index)
    else :
      return -1

  _find_picked_pair = staticmethod(_find_picked_pair)

  def __set_sync_rotation(self, tag, state, ref_widget, tr_widget, fit_pairs) :
    """Turn on/off the synchronous rotation/zoom."""
    if 'syncrotzoom' == tag :
      ref_widget.do_sync_rotation = state
      tr_widget.do_sync_rotation  = state

      ref_widget.do_sync_zoom = state
      tr_widget.do_sync_zoom  = state

      # if the synchronous rotation is set - align molecules first.
      if state :
        self.__align_molecules(ref_widget, tr_widget, fit_pairs)


class CorrelationResultsWindow(BaseWindow) :
  """Window for representing results of a correlation of vibrations.

  No properties are exposed and no public methods are exported.
  
  """
  
  def __init__(self, mainApp, correlation_results,
               goback_window=None, startpage=None) :
    """
    Constructor of the class.

    Positional arguments :
    mainApp             -- reference to the main window of PyVib2
    correlation_results -- results of the correlation (dictionary)

    correlation_results must have the following keys :
    start_time     :  formatted start time
    t0             :  start time as a tuple returned by os.times()
    t1             :  end   time as a tuple returned by os.times()
    ref_mol        :  reference molecule (pyviblib.molecule.Molecule)
    tr_mol         :  trial molecule (pyviblib.molecule.Molecule)
    atom_pairs     :  atom_pairs of the fit fragment (null-based ndarray)
                      shape : (Natoms_F, 2) with Natoms_F being the number
                      of atoms in the fragment
                      atom numbers are one-based
    alignment      :  type of the orientationsl alignment
                      must be one of ('Orientational', 'Inertia axes', None)
    include_tr_rot :  if translations / rotations were included
    overlaps       :  overlaps matrix (one-based ndarray)
                      shape : (1 + NFreq_ref, 1 + NFreq_tr) with NFreq_ref
                      and NFreq_tr being the number of the vibrations being
                      correlated
    similarities   :  overlaps matrix (one-based ndarray)
                      shape : (1 + NFreq_ref, 1 + NFreq_tr)
    camera         :  camera to be installed to the reference widget
      
      if the orientational alignment was performed :
      rms         : RMS value
      q           : quaternion (null-based ndarray)
                    shape : (4,)
      U           : left rotation matrix (one-based ndarray)
                    shape : (4, 4)
      ref_center  : center of the reference molecule (one-based ndarray)
                    shape : (4,)
      fit_center  : center of the fitted    molecule (one-based ndarray)
                    shape : (4,)

    Keyword arguments :
    goback_window       -- window to switch to (default None)
    startpage           -- tab name of RamanROADegcircCalcMixtureWindow to
                           be shown at startup (default None)
      
    """
    self.__correlation_results = correlation_results

    BaseWindow.__init__(self, mainApp,
                        goback_window=goback_window,
                        startpage=startpage)

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    results = self.__correlation_results
    
    # title
    title = 'Correlation results : %s -> %s @ %s' % (results['ref_mol'].name,
                                                     results['tr_mol'].name,
                                                     results['start_time'])
    self.wm_title(title)  
    
    self._varsdict['ref_range_from'] = Tkinter.IntVar()
    self._varsdict['ref_range_to']   = Tkinter.IntVar()
    self._varsdict['ref_range_freq'] = Tkinter.StringVar()
    self._varsdict['tr_range_from']  = Tkinter.IntVar()
    self._varsdict['tr_range_to']    = Tkinter.IntVar()
    self._varsdict['tr_range_freq']  = Tkinter.StringVar()
    self._varsdict['precision']      = Tkinter.IntVar()
  
    self._varsdict['ref_range_from'].set(1)
    self._varsdict['ref_range_to'].set(results['ref_mol'].NFreq)
    self._varsdict['ref_range_freq'].set('')
    self._varsdict['tr_range_from'].set(1)
    self._varsdict['tr_range_to'].set(results['tr_mol'].NFreq)
    self._varsdict['tr_range_freq'].set('')
    self._varsdict['precision'].set(3)

    self.__nrot_ref = results['ref_mol'].nrot
    self.__nrot_tr  = results['tr_mol'].nrot

    ## windows navigation toolbar
    btn_command = Command(self._mainApp.activate,
                          self._smartdict['goback_window'])
    widget = widgets.WindowNavigationToolbar(self,
                                             mainApp=self._mainApp,
                                             backbutton=True,
                                             homebutton=True,
                                             backbutton_command=btn_command)
    self._varsdict['windows_toolbar'] = widget
    self._varsdict['windows_toolbar'].grid(row=0, column=1,
                                           padx=3, pady=3, sticky='e')

    ## top frame : options   
    group_options = Pmw.Group(self, tag_text='Options')
    group_options.grid(row=1, column=0, padx=3, pady=3, sticky='w')

    # reference range
    validate = dict(validator='integer',
                    min=1,
                    max=results['ref_mol'].NFreq)
    widget = Pmw.Counter(group_options.interior(),
                         labelpos='w',
                         label_text='Reference range from ',
                         entry_width=4,
                         entry_textvariable=self._varsdict['ref_range_from'],
                         datatype = dict(counter='integer'),
                         entryfield_validate=validate,
                         entryfield_command=self.__refresh,
                         entryfield_modifiedcommand=self.__update_GUI,
                         autorepeat=True,    
                         increment=1)
    self._varsdict['counter_ref_from'] = widget
    self._varsdict['counter_ref_from'].grid(row=0, column=0,
                                            padx=3, pady=3, sticky='e')
  
    widget = Pmw.Counter(group_options.interior(),
                         labelpos='w',
                         label_text='to',
                         entry_width=4,
                         entry_textvariable=self._varsdict['ref_range_to'],
                         datatype=dict(counter='integer'),
                         entryfield_validate=validate,
                         entryfield_command=self.__refresh,
                         entryfield_modifiedcommand=self.__update_GUI,
                         autorepeat=True,
                         increment=1)
    self._varsdict['counter_ref_to'] = widget
    self._varsdict['counter_ref_to'].grid(row=0, column=1,
                                          padx=3, pady=3, sticky='e')

    # reset the reference range
    widget = Tkinter.Button(group_options.interior(),
                            image=getimage('reset_range'),
                            command=Command(self.__reset_vib_range,
                                            'reference'))
    self._varsdict['btn_reset_ref'] = widget    
    self._varsdict['btn_reset_ref'].grid(row=0, column=2,
                                         padx=3, pady=3, sticky='w')

    widget = Tkinter.Label(group_options.interior(),
                           relief='ridge',
                           borderwidth=2,
                           width=18,
                           padx=2,
                           pady=2,
                           textvariable=self._varsdict['ref_range_freq'])
    self._varsdict['lbl_freq_ref'] = widget
    self._varsdict['lbl_freq_ref'].grid(row=0, column=3, padx=10, pady=3)

    # trial range
    validate = dict(validator='integer',
                    min=1,
                    max=results['tr_mol'].NFreq)
    widget = Pmw.Counter(group_options.interior(),
                         labelpos='w',
                         label_text='Trial range from ',
                         entry_width=4,
                         entry_textvariable=self._varsdict['tr_range_from'],
                         datatype=dict(counter='integer'),
                         entryfield_validate=validate,
                         entryfield_command=self.__refresh,
                         entryfield_modifiedcommand=self.__update_GUI,
                         autorepeat=True,
                         increment=1)
    self._varsdict['counter_tr_from'] = widget
    self._varsdict['counter_tr_from'].grid(row=1, column=0,
                                           padx=3, pady=3, sticky='e')
    
    widget = Pmw.Counter(group_options.interior(),
                         labelpos='w',
                         label_text='to',
                         entry_width=4,
                         entry_textvariable=self._varsdict['tr_range_to'],
                         datatype=dict(counter='integer'),
                         entryfield_validate=validate,
                         entryfield_command=self.__refresh,
                         entryfield_modifiedcommand=self.__update_GUI,
                         autorepeat=True,
                         increment=1)
    self._varsdict['counter_tr_to'] = widget
    self._varsdict['counter_tr_to'].grid(row=1, column=1,
                                         padx=3, pady=3, sticky='e')
    # reset the trial range
    widget = Tkinter.Button(group_options.interior(),
                            image=getimage('reset_range'),
                            command=Command(self.__reset_vib_range, 'trial'))
    self._varsdict['btn_reset_tr'] = widget    
    self._varsdict['btn_reset_tr'].grid(row=1, column=2,
                                        padx=3, pady=3, sticky='w')

    widget = Tkinter.Label(group_options.interior(),
                           relief='ridge',
                           borderwidth=2,
                           width=18,
                           padx=2,
                           pady=2,
                           textvariable=self._varsdict['tr_range_freq'])
    self._varsdict['lbl_freq_tr'] = widget
    self._varsdict['lbl_freq_tr'].grid(row=1, column=3, padx=10, pady=3)

    # precision
    validate = dict(validator='integer',
                    min=1,
                    max=5)
    widget = Pmw.Counter(group_options.interior(),
                         labelpos='w',
                         label_text='Precision',
                         entry_width=3,
                         entry_textvariable=self._varsdict['precision'],
                         datatype=dict(counter='integer'),
                         entryfield_validate=validate,
                         entryfield_command=self.__refresh,
                         entryfield_modifiedcommand=self.__update_GUI,
                         autorepeat=False,
                         increment=1)
    self._varsdict['counter_prec'] = widget
    self._varsdict['counter_prec'].grid(row=0, column=4, rowspan=1,
                                        padx=15, pady=3, sticky='w')

    # show translations / rotations
    # adding this element if translations / rotations were
    # explicitely requested
    if results['include_tr_rot'] :
      self._varsdict['show_tr_rot'] = Tkinter.IntVar()
      self._varsdict['show_tr_rot'].set(1)

      widget = Tkinter.Checkbutton(group_options.interior(),
                                   text='Show translations / rotations',
                                   variable=self._varsdict['show_tr_rot'],
                                   command=self.__refresh)
      self._varsdict['check_show_tr_rot'] = widget
      self._varsdict['check_show_tr_rot'].grid(row=1, column=4,
                                               padx=15, pady=3, sticky='w')

    # mark overlaps and similarities which are >= ...
    self._varsdict['mark_overlaps']          = Tkinter.IntVar()
    self._varsdict['mark_similarities']      = Tkinter.IntVar()
    self._varsdict['threshold_overlaps']     = Tkinter.StringVar()
    self._varsdict['threshold_similarities'] = Tkinter.StringVar()

    self._varsdict['mark_overlaps'].set(1)
    self._varsdict['mark_similarities'].set(1)
    self._varsdict['threshold_overlaps'].set('0.5')
    self._varsdict['threshold_similarities'].set('0.9')

    widget = Tkinter.Checkbutton(group_options.interior(),
                                 text='Mark overlaps >=',
                                 variable=self._varsdict['mark_overlaps'],
                                 command=self.__update_GUI)
    self._varsdict['check_mark_overlaps'] = widget    
    self._varsdict['check_mark_overlaps'].grid(row=0, column=5,
                                               padx=3, pady=3, sticky='w')

    validate = dict(validator='real',
                    min=0.0,
                    max=0.999,
                    separator='.')
    widget = Pmw.EntryField(group_options.interior(),
                            entry_textvariable=
                            self._varsdict['threshold_overlaps'],
                            validate=validate,
                            entry_width=7,
                            command=self.__refresh,
                            modifiedcommand=self.__update_GUI)
    self._varsdict['entryfield_overlap'] = widget
    self._varsdict['entryfield_overlap'].grid(row=0, column=6,
                                              padx=3, pady=3, sticky='w')

    widget = Tkinter.Checkbutton(group_options.interior(),
                                 text='Mark similarities >=',
                                 variable=self._varsdict['mark_similarities'],
                                 command=self.__update_GUI)
    self._varsdict['check_mark_similarities'] = widget
    self._varsdict['check_mark_similarities'].grid(row=1, column=5,
                                                   padx=3, pady=3, sticky='w')

    widget = Pmw.EntryField(group_options.interior(),
                            entry_textvariable=
                            self._varsdict['threshold_similarities'],
                            validate=validate,
                            entry_width=7,
                            command=self.__refresh,
                            modifiedcommand=self.__update_GUI)
    self._varsdict['entryfield_similarities'] = widget
    self._varsdict['entryfield_similarities'].grid(row=1, column=6,
                                                   padx=3, pady=3, sticky='w')

    ## refresh button on the right   
    self._varsdict['btn_refresh'] = Tkinter.Button(self,
                                                   text='Refresh',
                                                   image=getimage('refresh'),
                                                   compound='top',
                                                   command=self.__refresh)
    self._varsdict['btn_refresh'].grid(row=1, column=1,
                                       padx=3, pady=3, sticky='es')

    ## tabs for results
    self.grid_columnconfigure(0, weight=1)
    self.grid_rowconfigure(2, weight=1)
    
    self._varsdict['notebook'] = Pmw.NoteBook(self,
                                             raisecommand=self.__select_tab,
                                             lowercommand=self.__deselect_tab,
                                             arrownavigation=True)
    self._varsdict['notebook'].grid(row=2, column=0, columnspan=2,
                                    padx=3, pady=3, sticky='news')

    # constructing a message bar for passing it to the tables
    self._varsdict['msgBar'] = Pmw.MessageBar(self,
                                              entry_relief='sunken',
                                              label_text='Info :',
                                              labelpos='w')
    # overlaps tab
    tab_overlaps = self._varsdict['notebook'].add('Overlaps')
    tab_overlaps.grid_rowconfigure(0, weight=1)
    tab_overlaps.grid_columnconfigure(0, weight=1)

    cr_kw = dict(matrix=self.__correlation_results['overlaps'],
                 freqs_ref=self.__correlation_results['ref_mol'].freqs,
                 freqs_tr=self.__correlation_results['tr_mol'].freqs,
                 include_tr_rot=self.__correlation_results['include_tr_rot'],
                 msgBar=self._varsdict['msgBar'],
                 dblclick_callback=self.__show_vibs)
    widget = widgets.CorrelationResultsNoteBook(tab_overlaps, **cr_kw)
    self._varsdict['notebook_overlaps'] = widget
    self._varsdict['notebook_overlaps'].grid(row=0, column=0,
                                             padx=3, pady=3, sticky='news')  

    # similarities tab
    tab_similarities = self._varsdict['notebook'].add('Similarities')
    tab_similarities.grid_rowconfigure(0, weight=1)
    tab_similarities.grid_columnconfigure(0, weight=1)

    cr_kw = dict(matrix=self.__correlation_results['similarities'],
                 freqs_ref=self.__correlation_results['ref_mol'].freqs,
                 freqs_tr=self.__correlation_results['tr_mol'].freqs,
                 include_tr_rot=self.__correlation_results['include_tr_rot'],
                 msgBar=self._varsdict['msgBar'],
                 dblclick_callback=self.__show_vibs)
    widget = widgets.CorrelationResultsNoteBook(tab_similarities, **cr_kw)
    self._varsdict['notebook_similarities'] = widget
    self._varsdict['notebook_similarities'].grid(row=0, column=0,
                                                 padx=3, pady=3, sticky='news')
    # summary tab
    tab_summary = self._varsdict['notebook'].add('Summary')
    tab_summary.grid_rowconfigure(0, weight=1)
    tab_summary.grid_columnconfigure(0, weight=1)

    prop_widget = self.__constructPropWidget(tab_summary)
    prop_widget.grid(row=0, column=0, padx=3, pady=3, sticky='new')

    # message bar
    self._varsdict['msgBar'].grid(row=3, column=0, columnspan=2,
                                  padx=0, pady=1, sticky='we')

    # first initialization of the tables
    self.__update_GUI()
    self.__refresh()

    # set the A4 representation for both overlaps and similarities
    kw = dict(scale_factor=1.0,
              show_tr_rot=results['include_tr_rot'],
              nrot_ref=results['ref_mol'].nrot,
              nrot_tr=results['tr_mol'].nrot
              )
    
    self._varsdict['notebook_overlaps'].show_A4(**kw)
    self._varsdict['notebook_similarities'].show_A4(**kw)

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    self._balloon.bind(self._varsdict['counter_ref_from'],
                       'Show the results for the reference molecule' + \
                       ' starting from a given vibration.')
    self._balloon.bind(self._varsdict['counter_ref_to'],
                        'Show the results for the reference molecule' + \
                       ' up to a given vibration.')
    self._balloon.bind(self._varsdict['btn_reset_ref'],
                       'Reset the whole reference vibrational range.')
    self._balloon.bind(self._varsdict['lbl_freq_ref'],
                       'Wavenumbers of the selected vibrational range' + \
                       ' of the reference molecule.')
    self._balloon.bind(self._varsdict['counter_tr_from'],
                       'Show the results for the trial molecule' + \
                       ' starting from a given vibration.')
    self._balloon.bind(self._varsdict['counter_tr_to'],
                       'Show the results for the trial molecule' + \
                       ' up to a given vibration.')
    self._balloon.bind(self._varsdict['btn_reset_tr'],
                       'Reset the whole trial vibrational range.')
    self._balloon.bind(self._varsdict['lbl_freq_tr'],
                       'Wavenumbers of the selected vibrational range' + \
                       ' of the trial molecule.')
    self._balloon.bind(self._varsdict['counter_prec'],
                       'Number of decimal points for printing of ' + \
                       'numeric values.\n\nAll values bellow this' + \
                       ' threshold are considered to be 0.')
    if self.__correlation_results['include_tr_rot'] :
      self._balloon.bind(self._varsdict['check_show_tr_rot'],
                        'Show contributions of translational/rotational' + \
                         ' modes in the tables.')
      
    self._balloon.bind(self._varsdict['check_mark_overlaps'],
                       'Mark overlaps which exceed a given value.')
    self._balloon.bind(self._varsdict['entryfield_overlap'],
                       'Threshold for overlaps.')
    self._balloon.bind(self._varsdict['check_mark_similarities'],
                       'Mark similarities which exceed a given value.')
    self._balloon.bind(self._varsdict['entryfield_similarities'],
                       'Threshold for similarities.')
    self._balloon.bind(self._varsdict['btn_refresh'],
                       'Update the contents of the tables.')

  def __refresh(self) :
    """Update the tables taking into account new vibrational ranges."""
    if not self.__is_input_valid() :
      return
    
    self.tk.call('update', 'idletasks')
    dict_vars = self._varsdict

    ref_from, ref_to, tr_from, tr_to = self.__get_vib_ranges()

    if self.__correlation_results['include_tr_rot'] :
      show_tr_rot = self._varsdict['show_tr_rot'].get()
    else :
      show_tr_rot = False

    kw_o = dict(precision=dict_vars['precision'].get(),
                show_tr_rot=show_tr_rot,
                nrot_ref=self.__nrot_ref,
                nrot_tr=self.__nrot_tr,
                mark=self._varsdict['mark_overlaps'].get(),
                threshold_marked=\
                float(self._varsdict['threshold_overlaps'].get()))
    self._varsdict['notebook_overlaps'].update_contents(ref_from, ref_to,
                                                        tr_from, tr_to,
                                                        **kw_o)
    kw_s = dict(precision=dict_vars['precision'].get(),
                show_tr_rot=show_tr_rot,
                nrot_ref=self.__nrot_ref,
                nrot_tr=self.__nrot_tr,
                mark=self._varsdict['mark_similarities'].get(),
                threshold_marked=\
                float(self._varsdict['threshold_similarities'].get()))
    self._varsdict['notebook_similarities'].update_contents(ref_from, ref_to,
                                                            tr_from, tr_to,
                                                            **kw_s)

    # the precision value which is actually set
    self._varsdict['current_precision'] = dict_vars['precision'].get()

  def __get_vib_ranges(self) :
    """Return a tuple of ref_from, ref_to, tr_from, tr_to."""
    dict_vars = self._varsdict
    
    range_ref = (int(dict_vars['ref_range_from'].get()),
                 int(dict_vars['ref_range_to'].get()))
    ref_from = min(range_ref)
    ref_to   = max(range_ref)

    range_tr = (int(dict_vars['tr_range_from'].get()),
                int(dict_vars['tr_range_to'].get()))
    tr_from = min(range_tr)
    tr_to   = max(range_tr)

    return ref_from, ref_to, tr_from, tr_to

  def __get_overlap_similarity(self, vibs_indices) :
    """Get the values of the overlap and similarity for given vib_indices.

    Values are strings.
    
    """
    if self.__correlation_results['include_tr_rot'] and \
       self._varsdict['show_tr_rot'].get() :
      if vibs_indices[0] < 0 :
        i = -vibs_indices[0]
      else :
        i = vibs_indices[0] + 3 + self.__correlation_results['ref_mol'].nrot

      if vibs_indices[1] < 0 :
        j = -vibs_indices[1]
      else :
        j = vibs_indices[1] + 3 + self.__correlation_results['tr_mol'].nrot
    else :
      if self.__correlation_results['include_tr_rot'] :
        i = vibs_indices[0] + 3 + self.__correlation_results['ref_mol'].nrot
        j = vibs_indices[1] + 3 + self.__correlation_results['tr_mol'].nrot
      else :
        i = vibs_indices[0]
        j = vibs_indices[1]

    o = max(self.__correlation_results['overlaps'][i, j], 0.)
    s = max(self.__correlation_results['similarities'][i, j], 0.)

    format = '%%.%df' % self._varsdict['current_precision']

    return format % o, format % s

  def __constructPropWidget(self, parent) :
    """Contruct the summary information in the property widget."""
    prop_widget = widgets.PropertiesWidget(parent, height=300)

    results = self.__correlation_results

    #
    prop_widget.add_line('Reference molecule', results['ref_mol'].name)
    prop_widget.add_line('Trial molecule', results['tr_mol'].name)
    prop_widget.add_separator()

    #
    prop_widget.add_line('Remove contaminations ?',
                         results['remove_tr_rot'] and 'yes' or 'no')
    if 'rms' in results :
      prop_widget.add_line('RMS',  '%20.6f' % results['rms'])

    prop_widget.add_separator()
    # 
    prop_widget.add_line('Started @', results['start_time'])

    t0 = results['t0']
    t1 = results['t1']
    prop_widget.add_line('Elapsed time', '%20.3f s' % (t1[4] - t0[4]))
    prop_widget.add_line('User time', '%20.3f s' % (t1[0] - t0[0]))
    prop_widget.add_line('System time', '%20.3f s' % (t1[1] - t0[1]))
    prop_widget.add_line('Elapsed time', '%20.3f s' %
                         (t1[0] - t0[0] + t1[1] - t0[1]))
    prop_widget.add_line('CPU system call time', '%20.3f s' %
                         (t1[2] - t0[2] + t1[3] - t0[3]))
    
    return prop_widget

  def __is_input_valid(self) :
    """Return True if the user input is valid."""
    try :
      for strval in ('ref_range_from', 'ref_range_to',
                     'tr_range_from', 'tr_range_to', 'precision') :
        int(self._varsdict[strval].get())

      if self._varsdict['mark_overlaps'].get() :
        float(self._varsdict['threshold_overlaps'].get())

      if self._varsdict['mark_similarities'].get() :
        float(self._varsdict['threshold_similarities'].get())
      
    except ValueError :
      return False
    else :
      return True

  def __update_GUI(self) :
    """Update the GUI."""
    if self.__is_input_valid() :
      
      ref_from, ref_to, tr_from, tr_to = self.__get_vib_ranges()
      ref_mol = self.__correlation_results['ref_mol']
      tr_mol  = self.__correlation_results['tr_mol']

      self._varsdict['ref_range_freq'].set(
        '%.2f - %.2f' % (ref_mol.freqs[ref_from], ref_mol.freqs[ref_to]))
      self._varsdict['tr_range_freq'] .set(
        '%.2f - %.2f' % (tr_mol.freqs[tr_from]  , tr_mol.freqs[tr_to]))
      
      self._varsdict['btn_refresh'].configure(state='normal')

      # block the threshold text fields unless checked
      state = 'normal'
      if not self._varsdict['mark_overlaps'].get() :
        state = 'disabled'
      self._varsdict['entryfield_overlap'].configure(entry_state=state)

      state = 'normal'
      if not self._varsdict['mark_similarities'].get() :
        state = 'disabled'
      self._varsdict['entryfield_similarities'].configure(entry_state=state)
        
    else :
      self._varsdict['btn_refresh'].configure(state='disabled')

  def __export_matrix(self, widget) :
    """Export command handler."""
    if widget is None :
      return

    filetypes = [ (resources.STRING_FILETYPE_CSVFILE_DESCRIPTION, '*.csv') ]
    
    filename = tkFileDialog.SaveAs(parent=self,
                                   filetypes=filetypes,
                                   initialdir=None).show()
    if filename :
      if not filename.endswith('.csv') :
        filename = ''.join((filename, '.csv'))
      
      file_csv = open(filename, 'w+')
      file_csv.write(widget.csv)
      file_csv.close()

      self.__lastdir = os.path.dirname(filename)

  def __select_tab(self, tab_name) :
    """Called when a tab is selected.

    Set the scroll view of a new tab to the values of the previous tab.
    
    """
    notebook = self.__get_tab_notebook(tab_name)
    
    if notebook is None :
      return

    # tables
    notebook.table.xview_moveto(self._varsdict['view_values'][0])
    notebook.table.yview_moveto(self._varsdict['view_values'][1])

    # circles
    notebook.circles_frame.xview('moveto',
                                 self._varsdict['view_circles'][0])
    notebook.circles_frame.yview('moveto',
                                  self._varsdict['view_circles'][1])

    # selecting the same page ;)
    notebook.selectpage(self._varsdict['sel_pagename'])

  def __deselect_tab(self, tab_name) :
    """Called when a tab is deselected.

    Save the scroll view if the tab is Overlaps or Similarities.
    """
    notebook = self.__get_tab_notebook(tab_name)
    
    if notebook is None :
      return

    # scroll positions
    self._varsdict['view_values']  = notebook.table.xview()[0] , \
                                     notebook.table.yview()[0]
    self._varsdict['view_circles'] = notebook.circles_frame.xview()[0], \
                                     notebook.circles_frame.yview()[0]
    # selected notebook page
    self._varsdict['sel_pagename'] = notebook.getcurselection()
    
  def __get_tab_notebook(self, tab_name) :
    """Return a reference to the selected main notebook page."""
    # this prevents the usage of uninitialized variables
    if not hasattr(self, '_notebook_overlaps') or \
       not hasattr(self, '_notebook_similarities') :
      return None
    
    index_tab = self._varsdict['notebook'].index(tab_name)

    if 2 > index_tab :
      if 0 == index_tab :
        return self._varsdict['notebook_overlaps']
      else :
        return self._varsdict['notebook_similarities']
    else :
      return None

  def __reset_vib_range(self, what_range) :
    """Reset to the whole vibrational range.

    Positional arguments :
    what_range -- one of ('reference', 'trial')
    
    """
    if what_range not in ('reference', 'trial') :
      return

    if 'reference' == what_range :
      self._varsdict['ref_range_from'].set(1)
      self._varsdict['ref_range_to'].set(
        self.__correlation_results['ref_mol'].NFreq)
    else :
      self._varsdict['tr_range_from'].set(1)
      self._varsdict['tr_range_to'].set(
        self.__correlation_results['tr_mol'].NFreq)

    self.__update_GUI()
    self.__refresh()

  def __show_vibs(self, ref_no, tr_no) :
    """Callback for the double click on a matrix element."""
    correlation_results = self.__correlation_results
    
    ref_mol = copy.deepcopy(correlation_results['ref_mol'])
    tr_mol  = copy.deepcopy(correlation_results['tr_mol'])

    overlap, similarity = self.__get_overlap_similarity((ref_no, tr_no))

    # setting the last camera
    ref_camera = 'last_ref_camera' not in self._varsdict and \
                 correlation_results['ref_camera'] or \
                 self._varsdict['last_ref_camera']

    kw = dict(ref_mol=ref_mol,
              tr_mol=tr_mol,
              atom_pairs=correlation_results['atom_pairs'],
              use_Lx=correlation_results['use_Lx'],
              remove_tr_rot=correlation_results['remove_tr_rot'],
              overlap=overlap,
              similarity=similarity,
              ref_no=ref_no,
              tr_no=tr_no,
              U=correlation_results['U'],
              goback_window=self,
              ref_camera=ref_camera,
              startpage=self._smartdict['startpage'])

    wnd_vibpairs = VibrationPairWindow(self._mainApp, **kw)
    wnd_vibpairs.smartdict['destroy_command'] = Command(
      self.__save_last_camera,wnd_vibpairs)
    
    # explicitely give the focus to the window
    # windows does not do it :(
    wnd_vibpairs.maximize()
    self.after_idle(wnd_vibpairs.focus_set)

  def __save_last_camera(self, wnd_vibpairs) :
    """Destroy callback for the VibrationPairWindow.

    Saves the reference camera of the window wnd_vibpairs.
    
    """
    self._varsdict['last_ref_camera'] = wnd_vibpairs.ref_camera
    

class SingleVibrationWindow(BaseWindow) :
  """Window for exploring a single vibration.

  No properties are exposed and no public methods are exported.

  """

  def __init__(self, mainApp, mol, **kw) :
    """
    Constructor of the class.

    Positional arguments :
    mainApp        -- reference to the main window of PyVib2
    mol            -- molecule
    
    Keyword arguments : 
    molecule_name  -- molecule name shown in the title of the window
                      (default None)
                      if given, override the value of molecule.name
    vib_no         -- number of vibration to show (default 1)    
    show_acp       -- whether the acp button is to be shown (default False)
    invert_roa     -- whether to invert the sign of ROA (default False)
    
    """
    if not isinstance(mol, molecule.Molecule) :
      raise ConstructorError('molecule must be given')

    if mol.L is None :
      raise ConstructorError('Molecule must have the normal modes')

    self.__mol = mol

    BaseWindow.__init__(self, mainApp, **kw)

  def _init_vars(self) :
    """Initialize variables."""
    # showing the first vibration by default
    self._smartdict['vib_no']  = 1

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    # placing the info in the title
    name = self._smartdict['molecule_name'] or self.__mol.name

    title = r'%s : vibration %d / %.2f cm**(-1)' % \
            (name, self._smartdict['vib_no'],
     self.__mol.freqs[self._smartdict['vib_no']])
    
    self.wm_title(title)

    #
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=1)

    grp = self._constructMoleculeFrame(self, self.__mol,
                                       self._smartdict['vib_no'],
                                       name=name,
                                       show_gcm=self._smartdict['show_gcm'],
                                       molinv=self._smartdict['molinv'],
                                       show_snapshot=True)
    grp.grid(row=0, column=0, padx=3, pady=3, sticky='news')

  def _constructMoleculeFrame(self, parent, mol, vib_no,
                              prefix='', title=None,
                              name=None, fragment_controls=False, camera=None,
                              marked_vib_atoms=None,
                              use_Lx=False,
                              show_gcm=False,
                              molinv=None,
                              show_snapshot=False) :
    """Construct the molecule frame."""
    assert parent is not None and mol is not None and vib_no is not None

    # parent of the whole frame
    grp = Pmw.Group(parent, tag_text=title or '')
    grp.interior().grid_columnconfigure(0, weight=1)
    
    # 0, name + formula, height = 1.0 cm
    name = name or mol.name or ''
    
    frm0 = Tkinter.Frame(grp.interior(), relief='ridge', borderwidth=2)
    frm0.grid(row=0, column=0, padx=3, pady=3, sticky='we')
    
    frm0.grid_rowconfigure(0, weight=1)
    frm0.grid_columnconfigure(0, weight=1)
    frm0.grid_columnconfigure(1, weight=1)
    
    lbl_name = Tkinter.Label(frm0,
                             text=name,
                             font=resources.get_font_molecules(self),
                             anchor='c')
    lbl_name.grid(row=0, column=0, padx=3, pady=3, sticky='we')

    # translations / rotations
    if 0 > vib_no :
      if -3 <= vib_no :
        tex_src = r'$T_%s$' % ('x', 'y', 'z')[-vib_no-1]
      else :
        tex_src = r'$I_%d$' % (-vib_no-3)

    else :
      tex_src = r'$\tilde{\nu}_{%d}\ =\ %.2f\ cm^{-1}$' % \
                (vib_no, mol.freqs[vib_no])
      
    fig = BaseFigure(frm0,
                     figsize=(6./INCH2CM, 0.7/INCH2CM),
                     edgecolor='black',
                     facecolor='white')

    fig.text(0.5, 0.45, tex_src,
             horizontalalignment='center',
             verticalalignment='center',
             fontsize=14,
             fontweight='bold')
    fig.tk_canvas.get_tk_widget().grid(row=0, column=1,
                                       padx=0, pady=0, sticky='e')

    # 3 - render widget
    row_rw = show_snapshot and 3 or 2    
    grp.interior().grid_rowconfigure(row_rw, weight=1)
    
    widget = widgets.MoleculeRenderWidget(grp.interior(),
                                          height=400,
                                          width=400,
                                          molecule=mol,
                                          resolution=\
                                          self._mainApp.settings['resolution'],
                                          camera=camera)
    self._varsdict['%s_mol_widget' % prefix] = widget
    self._varsdict['%s_mol_widget' % prefix].grid(row=row_rw, column=0,
                                                  padx=3, pady=3, sticky='news')
    self._varsdict['%s_mol_widget' % prefix].marked_vib_atoms = \
                                   marked_vib_atoms

    # 2 - button toolbar with a snapshot button if requested
    if show_snapshot :
      btn_toolbar = widgets.ButtonToolbar(grp.interior(), horizontal=True)
      btn_toolbar.grid(row=2, column=0, padx=3, pady=3, sticky='w')

      # snapshot
      btn_toolbar.add_button(imagename='snapshot',
                             command=self.__snapshot,
                             helptext='Make a snapshot of the render widget.')

      # size of the render widget
      self._varsdict['var_renderwidget_size'] = Tkinter.StringVar()
      command = misc.Command(self._change_render_widget_size,
                             self._varsdict['%s_mol_widget' % prefix])
      
      btn_kw = dict(textvariable=self._varsdict['var_renderwidget_size'],
                    justify='center',
                    command=command,
                    helptext='Current size of the render widget.')

      self._varsdict['btn_size'] = btn_toolbar.add_button(**btn_kw)
      self._varsdict['btn_size'].configure(overrelief='flat')  
    
    # 1 - vibrational toolbar light
    kw = dict()
    
    kw['widget'] = self._varsdict['%s_mol_widget' % prefix]
    kw['scale_factor'] = 1.0
    kw['vib_no'] = vib_no
    kw['invert_phase'] = False
    kw['show_gcm'] = show_gcm
    kw['molinv']   = molinv
    kw['mainApp'] = self._mainApp
    kw['fragment_controls'] = fragment_controls
    kw['invert_roa'] = self._smartdict['invert_roa']

    if use_Lx :
      kw['rep_type']      = resources.STRING_VIB_EXCURSIONS
      kw['rep_subtype']   = resources.STRING_VIB_EXCURSIONS_DIAMETER
      
    else :
      kw['rep_type']      = resources.STRING_VIB_ENERGY
      kw['rep_subtype']   = resources.STRING_VIB_ENERGY_VOLUME
      
    widget = widgets.VibrationalToolbarLight(grp.interior(), **kw)
    self._varsdict['vibtoolbar_%s' % prefix] = widget
    self._varsdict['vibtoolbar_%s' % prefix].grid(row=1, column=0,
                                                  padx=3, pady=3, sticky='we')

    return grp

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    pass


  def _bind_events(self) :
    """Bind events."""
    # pageup - pagedown -> increase / decrease the scale factor to 0.1
    self.bind('<Prior>',
              Command(self._varsdict['vibtoolbar_'].increase_scale_factor))
    self.bind('<Next>',
              Command(self._varsdict['vibtoolbar_'].decrease_scale_factor))

    self.bind('<Configure>', self.__Configure)

  def __snapshot(self) :
    """Show the Snapshot dialog."""
    self.tk.call('update', 'idletasks')
    dialogs.SnapshotDialog(self,
                           mode='file',
                           renderWidget=self._varsdict['_mol_widget']
                           ).show()

  def __Configure(self, e) :
    """<Configure> event handler."""
    if 'btn_size' in self._varsdict :
      self._varsdict['var_renderwidget_size'].set(
        '%dx%d' % self._varsdict['_mol_widget'].GetRenderWindow().GetSize())


class VibrationPairWindow(SingleVibrationWindow) :
  """Window for exploring two vibrations simultaneously.

  The following properties are exposed :
      ref_camera -- camera installed in the reference render widget

  No public methods are exported.
  
  """

  def __init__(self, mainApp, ref_mol, tr_mol, **kw) :
    """
    Constructor of the class.

    Positional arguments :
    mainApp     -- reference to the main window of PyVib2
    ref_mol     -- reference molecule which is shown at the left
    tr_mol      -- trial molecule which is shown at the right
    
    Keyword arguments (must be given):
    atom_pairs  -- atom pairs of the fragment to be marked
                   (null-based ndarray)
                   shape : (Natoms_F, 2) with Natoms_F being the number
                   of atoms in the fragment
                   atom numbers are one-based
    overlap     -- overlap
    similarity  -- similarity
    ref_no      -- reference number of vibration
    tr_no       -- trial number of vibration
    U           -- left rotation matrix for the trial frame
                   (one-based ndarray)
                   shape : (4, 4)
    ref_camera  -- camera to be installed to the reference widget

    Optional keyword arguments :
    startpage   -- tab name of RamanROADegcircCalcMixtureWindow to
                   be shown at startup (default None)
                  
    """
    if not isinstance(ref_mol, molecule.Molecule) or \
       not isinstance(tr_mol, molecule.Molecule) :
      raise ConstructorError(
        'Invalid ref_mol and/or tr_mol arguments')

    self._ref_mol = ref_mol
    self._tr_mol  = tr_mol

    SingleVibrationWindow.__init__(self, mainApp, ref_mol, **kw)

  def _init_vars(self) :
    """Initialize variables."""
    if self._smartdict.kw is None :
      raise InvalidArgumentError(
        'Keywords are required for the proper initialization of the window')
    
    # parameters
    req_params = ('overlap', 'similarity', 'ref_no', 'tr_no',
                  'atom_pairs', 'use_Lx')
    
    for param in req_params :
      if self._smartdict[param] is None :
        raise InvalidArgumentError('%s keyword must be supplied' % param)

    # initial directory for saving of screenshots
    self._varsdict['initialdir'] = None

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    labels = resources.STRINGS_TRANSLATIONS_ROTATIONS_LABELS
    # title
    if self._smartdict['ref_no'] < 0 :
      ref_label = labels[-self._smartdict['ref_no'] - 1]
    else :
      ref_label = str(self._smartdict['ref_no'])

    if self._smartdict['tr_no'] < 0 :
      tr_label = labels[-self._smartdict['tr_no'] - 1]
    else :
      tr_label = str(self._smartdict['tr_no'])

    title = 'Vibrations : %s # %s -> %s # %s' % \
            (self._ref_mol.name, ref_label, self._tr_mol.name, tr_label)
    
    self.wm_title(title)

    ## windows navigation toolbar
    command = Command(self._mainApp.activate, self._smartdict['goback_window'])
    widget = widgets.WindowNavigationToolbar(self,
                                             mainApp=self._mainApp,
                                             backbutton=True,
                                             homebutton=True,
                                             backbutton_command=command)
    self._varsdict['windows_toolbar'] = widget
    self._varsdict['windows_toolbar'].grid(row=0, column=2,
                                           padx=3, pady=3, sticky='e')

    # top - informational pane
    prop_widget = self.__constructPropWidget(self)
    prop_widget.grid(row=1, column=0, columnspan=3,
                     padx=3, pady=3, sticky='ew')

    # left - reference molecule with the name
    self.grid_rowconfigure(2, weight=1)
    self.grid_columnconfigure(0, weight=1)

    mf_kw = dict(prefix='ref',
                 title='Reference molecule',
                 name=None,
                 fragment_controls=True,
                 camera=self._smartdict['ref_camera'],
                 marked_vib_atoms=self._smartdict['atom_pairs'][:, 0],
                 use_Lx=False)
    group_ref = self._constructMoleculeFrame(self,
                                             self._ref_mol,
                                             self._smartdict['ref_no'],
                                             **mf_kw)
    group_ref.grid(row=2, column=0, padx=5, pady=3, sticky='news')

    # right - trial molecule with the name
    self.grid_columnconfigure(2, weight=1)

    mf_kw = dict(prefix='tr',
                 title='Trial molecule',
                 name=None,
                 fragment_controls=True,
                 camera=self._smartdict['tr_camera'],
                 marked_vib_atoms=self._smartdict['atom_pairs'][:, 1],
                 use_Lx=False)
    group_tr = self._constructMoleculeFrame(self,
                                            self._tr_mol,
                                            self._smartdict['tr_no'],
                                            **mf_kw)
    group_tr.grid(row=2, column=2, padx=5, pady=3, sticky='news')
    
    ## button toolbar between the reference and trial widgets
    btn_toolbar = self.__constructButtonToolbar(self)
    btn_toolbar.grid(row=2, column=1, padx=0, pady=3)

    ## adjusting the windows
    # set the common point of view ;)
    self._varsdict['tr_mol_widget'].camera = \
            self._varsdict['ref_mol_widget'].camera

    # rotate the trial camera if a rotation matrix is given
    if self._smartdict['U'] is not None :
      vtk_matrix = vtkMatrix4x4()

      for i in xrange(3) :
        for j in xrange(3) :
          vtk_matrix.SetElement(i, j, self._smartdict['U'][1+j, 1+i])

      vtk_transform = vtkTransform()
      vtk_transform.SetMatrix(vtk_matrix)

      self._varsdict['tr_mol_widget'].camera.ApplyTransform(vtk_transform)
      self._varsdict['tr_mol_widget'].Render()

    # should the phase of the trial vibration be inverted ?
    if self.__define_phase(self._smartdict['ref_no'],
                           self._smartdict['tr_no'],
                           self._smartdict['atom_pairs']
                           ) :
      self._varsdict['vibtoolbar_tr'].invert_phase = True

    # saving the camera states for restoring
    self.__camera_state0_ref = self._varsdict['ref_mol_widget'].camera_state
    self.__camera_state0_tr  = self._varsdict['tr_mol_widget'].camera_state

    # set the synchronous camera motion
    self._varsdict['ref_mol_widget'].synchronize_camera_state(
      self._varsdict['tr_mol_widget'])
    self._varsdict['tr_mol_widget'].synchronize_camera_state(
      self._varsdict['ref_mol_widget'])

    # synchronizing the toolbars
    self._varsdict['vibtoolbar_ref'].sync_toolbar = \
                                            self._varsdict['vibtoolbar_tr']
    self._varsdict['vibtoolbar_tr'].sync_toolbar = \
                                            self._varsdict['vibtoolbar_ref']

  def _declare_properties(self) :
    """Declare properties of the widget."""
    self.__class__.ref_camera = property(
      fget=Command(
        Command.fget_value, self._varsdict['ref_mol_widget'].camera))

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    # buttons
    self._balloon.bind(self._varsdict['radio_projection'],
                       'Set the perspective or orthogonal projection.')
    self._balloon.bind(self._varsdict['radio_sync'],
                       'Enable / disable the synchronous rotation, zoom.')
    self._balloon.bind(self._varsdict['btn_restore'],
                       'Restore the initial positions.')
    self._balloon.bind(self._varsdict['btn_screenshot'],
                       'Make a snapshot of both render widgets.')
    self._balloon.bind(self._varsdict['btn_resize'],
                       'Resize both render widgets.')

  def _bind_events(self) :
    """Bind events."""
    self.bind('<KeyPress>', self.__keypress)

  def __define_phase(self, ref_no, tr_no, atom_pairs) :
    """Return if the phase of the trial vibration should be inverted."""
    # ref
    if 0 > ref_no :
      L_ref = self._ref_mol.L_tr_rot[-ref_no]
    else :
      L_ref = self._ref_mol.L[ref_no]

    # tr
    if 0 > tr_no :
      L_tr = self._tr_mol.L_tr_rot[-tr_no]
    else :
      L_tr = self._tr_mol.L[tr_no]

    # rotate the trial fragment
    if self._smartdict['U'] is not None :
      L_tr_rotated = transpose(dot(self._smartdict['U'], transpose(L_tr)))
    else :
      L_tr_rotated = L_tr

    return 0. > contract(L_ref[atom_pairs[:, 0]],
                         L_tr_rotated[atom_pairs[:, 1]])

  def __constructPropWidget(self, parent) :
    """Set the information to the top text control."""
    prop_widget = widgets.PropertiesWidget(parent,
                                           title='Correlation summary:',
                                           height=83)

    prop_widget.add_line('overlap', self._smartdict['overlap'])
    prop_widget.add_line('similarity', self._smartdict['similarity'])
    prop_widget.add_line('remove contaminations ?',
                         self._smartdict['remove_tr_rot'] and 'yes' or 'no')
    return prop_widget

  def __constructButtonToolbar(self, parent) :
    """Construct the button toolbar."""
    btn_toolbar = Tkinter.Frame(parent)
    
    # projection types
    row = 0
    
    widget = Pmw.RadioSelect(btn_toolbar,
                             orient='vertical',
                             command=self.__set_projection)
    self._varsdict['radio_projection'] = widget
    self._varsdict['radio_projection'].grid(row=row, column=0,
                                            padx=0, pady=3, sticky='n')
    row += 1

    self._varsdict['radio_projection'].add('perspective',
                                           image=getimage('perspective'))
    self._varsdict['radio_projection'].add('parallel',
                                           image=getimage('orthogonal'))
    self._varsdict['radio_projection'].invoke('perspective')

    # synchronous rotation / zoom
    widget = Pmw.RadioSelect(btn_toolbar,
                             orient='vertical',
                             selectmode='multiple',
                             command=self.__set_sync_operation)
    self._varsdict['radio_sync'] = widget
    self._varsdict['radio_sync'].grid(row=row, column=0,
                                      padx=0, pady=10, sticky='n')
    row += 1

    self._varsdict['radio_sync'].add('syncrotation', image=getimage('rotate'))
    self._varsdict['radio_sync'].add('synczoom',  image=getimage('zoom'))
    self._varsdict['radio_sync'].invoke('syncrotation')
    self._varsdict['radio_sync'].invoke('synczoom')

    # restore initial positions button
    self._varsdict['btn_restore'] = Tkinter.Button(btn_toolbar,
                                                   image=getimage('restore'),
                                                   relief='ridge',
                                                   overrelief='raised',
                                                   command=self.__restore
                                                   )
    self._varsdict['btn_restore'].grid(row=row, column=0,
                                       padx=0, pady=20, sticky='n')
    row += 1

    # plot Raman/ROA spectra if possible
    if self._ref_mol.raman_roa_tensors is not None and \
       self._tr_mol.raman_roa_tensors is not None \
       and self._smartdict['ref_no'] >= 1 and self._smartdict['tr_no'] >= 1 :
      widget = Tkinter.Button(btn_toolbar,
                              image=getimage('spectrum'),
                              relief='flat',
                              overrelief='raised',
                              command=self.__plot_raman_roa_spectra)
      self._varsdict['btn_spectra'] = widget
      self._varsdict['btn_spectra'].grid(row=row, column=0,
                                         padx=0, pady=20, sticky='n')
      row += 1

    # make a screenshot
    widget = Tkinter.Button(btn_toolbar,
                            image=getimage('snapshot'),
                            relief='flat',
                            overrelief='raised',
                            command=self.__snapshot)
    self._varsdict['btn_screenshot'] = widget
    self._varsdict['btn_screenshot'].grid(row=row, column=0,
                                          padx=0, pady=3, sticky='n')
    row += 1

    # resize both widgets    
    cmd = misc.Command(self._change_render_widget_size,
                       self._varsdict['ref_mol_widget'])
    widget = Tkinter.Button(btn_toolbar,
                            image=getimage('resize'),
                            relief='flat',
                            overrelief='raised',
                            command=cmd)
    self._varsdict['btn_resize'] = widget
    self._varsdict['btn_resize'].grid(row=row, column=0,
                                      padx=0, pady=3, sticky='n')

    return btn_toolbar

  def __set_projection(self, tag) :
    """Set the perspective or orthogonal projection."""
    perspective = 'perspective' == tag

    self._varsdict['ref_mol_widget'].perspective_projection = perspective
    self._varsdict['tr_mol_widget'].perspective_projection  = perspective

  def __set_sync_operation(self, tag, state) :
    """Enable / disable a synchronous camera operation."""
    if 'syncrotation' == tag :
      self._varsdict['ref_mol_widget'].do_sync_rotation = state
      self._varsdict['tr_mol_widget'].do_sync_rotation  = state
    elif 'synczoom' == tag :
      self._varsdict['ref_mol_widget'].do_sync_zoom = state
      self._varsdict['tr_mol_widget'].do_sync_zoom  = state

  def __restore(self) :
    """Restore the initial camera state in the reference and trial widgets."""
    self._varsdict['ref_mol_widget'].camera_state = self.__camera_state0_ref
    self._varsdict['tr_mol_widget'].camera_state  = self.__camera_state0_tr

    self._varsdict['radio_projection'].invoke('perspective')
      
  def __snapshot(self) :
    """Ask for a directory where files are to be saved."""
    dlg = dialogs.SnapshotDialog(self,
                                 mode='dir',
                                 initialdir=self._varsdict['initialdir'],
                                 ok_command=self.__save_snapshot,
                                 vtk_resolution=\
                                 self._varsdict['ref_mol_widget'].resolution
                                 )
    dlg.show()

  def __save_snapshot(self, **kw) :
    """Saving the contents of the both render widgets."""
    # saving the initial directory
    self._varsdict['initialdir'] = kw['initialdir']

    # make sure that the snapshot dialog disappeared from the screen
    # and does not disturbe to render ;)
    self.tk.call('update')

    extension = kw['format'].lower()
    if 'tiff' == extension :
      extension = 'tif'

    # magnifications
    current_DPI   = self._varsdict['ref_mol_widget'].GetRenderWindow().GetDPI()
    magnification = int(round(float(kw['resolution'])/float(current_DPI)))

    # filenames
    filename_ref = os.path.join(kw['location'], '%s_ref.%s' % \
                                (self._ref_mol.name, extension))

    filename_tr  = os.path.join(kw['location'], '%s_tr.%s' % \
                                (self._tr_mol.name, extension))

    # old settings
    old_res = self._varsdict['ref_mol_widget'].resolution
    old_bg  = self._varsdict['ref_mol_widget'].background

    # saving
    self._varsdict['ref_mol_widget'].background = kw['background']
    self._varsdict['tr_mol_widget'].background  = kw['background']
    
    self._varsdict['ref_mol_widget'].snapshot(filename_ref,
                                              kw['format'],
                                              magnification,
                                              kw['vtk_resolution'])
    self._varsdict['tr_mol_widget'].snapshot(filename_tr,
                                             kw['format'],
                                             magnification,
                                             kw['vtk_resolution'])

    # restoring the original vtk resolution & background
    if kw['restore_res'] :
      self._varsdict['ref_mol_widget'].resolution = old_res
      self._varsdict['tr_mol_widget'].resolution  = old_res

    if kw['restore_bg'] :
      self._varsdict['ref_mol_widget'].background = old_bg
      self._varsdict['tr_mol_widget'].background  = old_bg

    self._varsdict['ref_mol_widget'].Render()
    self._varsdict['tr_mol_widget'].Render()

  def __keypress(self, e) :
    """Handle keyboard events.

    Keys :
      m : mark fragment on/off
      f : show marked only on/off
      
    """
    if 'm' == e.keysym :
      new_val = not self._varsdict['vibtoolbar_ref'].mark_fragment
      
      self._varsdict['vibtoolbar_ref'].mark_fragment = new_val
      self._varsdict['vibtoolbar_tr'].mark_fragment  = new_val

    elif 'f' == e.keysym :
      new_val = not self._varsdict['vibtoolbar_ref'].show_marked_only
      
      self._varsdict['vibtoolbar_ref'].show_marked_only = new_val
      self._varsdict['vibtoolbar_tr'].show_marked_only  = new_val

  def __plot_raman_roa_spectra(self) :
    """Plot the Raman/ROA spectra for the reference and trial molecules."""
    mols = (self._ref_mol, self._tr_mol)
    
    labels = [ mol.name for mol in mols ]
    mark_vibs = (self._smartdict['ref_no'], self._smartdict['tr_no'])

    # plotting the spectra in a certain region +-200
    freqs = ( self._ref_mol.freqs[self._smartdict['ref_no']],
              self._tr_mol.freqs[self._smartdict['tr_no']] )
    lim_wavenumbers = (max(freqs) + 200., max(0., min(freqs) - 200.))

    splash = widgets.SplashScreen(self, 'Plotting the spectra...')
      
    w = RamanROADegcircCalcMixtureWindow(self._mainApp, mols, None, labels,
                                         mark_vibs=mark_vibs,
                                         lim_wavenumbers=lim_wavenumbers,
                                         startpage=\
                                         self._smartdict['startpage'] or 'ROA',
                                         render_spectra_labels=False)
    w.geometry('550x600')

    splash.destroy()

  def _set_render_widget_size(self, rw, w, h) :
    """Overriding the base base method since there are two render widgets."""
    self.update_idletasks()
    
    # current size of the render widget and of the whole window
    cur_w, cur_h = rw.GetRenderWindow().GetSize()

    geom  = self.geometry()
    delim = '+' in geom and '+' or '-'
    w_, h_ = [ int(val) for val in geom[:geom.index(delim)].split('x') ]

    # setting the new size (keep old coordinates of the upper left corner)
    geom = (w_ + 2 * (w - cur_w), h_ + h - cur_h, geom[geom.index(delim):])
    self.geometry('%dx%d%s' % geom)
    self.update_idletasks()


class AbstractSpectrumWindow(BaseWindow) :
  """Abstract class for widnows having spectra figures.

  The canvas of the spectra is saved by resizing and there is a function for
  saving a figure.

  """

  def __init__(self, mainApp, **kw) :
    """Constructor of the class.

    Positional arguments :
    mainApp  -- reference to the main window of PyVib2

    """    
    BaseWindow.__init__(self, mainApp, **kw)

  def _init_vars(self) :
    """Initialize variables."""
    # construct filetypes
    # add pdf if ps2pdf is found
    # add all supported filetypes supported by matplotlib
    self.__save_filetypes = []

    if misc.is_command_on_path('ps2pdf') :
      self.__save_filetypes.append(
        (resources.STRING_FILETYPE_PDFFILE_DESCRIPTION, '*.pdf'))

    self.__save_filetypes.append(
      (resources.STRING_FILETYPE_EPSFILE_DESCRIPTION, '*.ps *.eps'))
    self.__save_filetypes.append(
      (resources.STRING_FILETYPE_PNGFILE_DESCRIPTION, '*.png'))

  def _bind_events(self) :
    """Bind events."""
    self.bind('<Configure>', self._Configure)    

  def _constructGUI(self) :
    """Subclasses *must* implement this function."""
    raise NotImplementedError('_constructGUI() *must* be implemented.')

  def _save(self, figure, name=None, size=None) :
    """Save the spectra.

    Positional arguments :
    name -- the name of the molecule
    size -- size in inches, None for the current size
    
    """
    if name is not None :
      initialfile = name
      
      # remove the confusion with extensions
      if '.' in initialfile :
        initialfile = initialfile.replace('.', '_')
    else :
      initialfile = ''

    # saving the visited directory
    if 'lastdir' not in self._varsdict :
      self._varsdict['lastdir'] = self._mainApp.lastdir
    
    filename = tkFileDialog.SaveAs(parent=self,
                                   filetypes=self.__save_filetypes,
                                   initialfile=initialfile,
                                   initialdir=self._varsdict['lastdir']).show()

    if filename is not None and 0 < len(filename) :
      try :
        self.tk.call('update', 'idletasks')
        
        self._varsdict['lastdir'] = os.path.dirname(filename)
        figure.save(filename, size=size)
      except :
        widgets.show_exception(sys.exc_info())

  def _Configure(self, e) :
    """Request the canvas state resaving if the size has been changed."""
    if 'old_size' not in self._varsdict :
      self._varsdict['old_size'] = (e.width, e.height)

    cursize = (e.width, e.height)
    if cursize != self._varsdict['old_size'] :
      self._varsdict['old_size'] = cursize
      
      self.tk.call('update', 'idletasks')

      # set the changed state to all figures
      for key in self._varsdict :
        if key.startswith('figure') and \
           hasattr(self._varsdict[key], 'canvas_changed') :
          self._varsdict[key].canvas_changed = True  


class RamanROADegcircCalcWindow(AbstractSpectrumWindow) :
  """Window for exploring Raman/ROA spectra.

  The following public methods are explorted :
      clone() -- clone the molecule window
  
  """

  def __init__(self, mainApp, mol, **kw) :
    """Constructor of the class.

    Positional arguments :
    mainApp  -- reference to the main window of PyVib2
    mol      -- molecule

    Keyword arguments :
    camera   -- camera to be set in secondary windows (default None)
    
    """
    if not isinstance(mol, molecule.Molecule) :
      raise ConstructorError('molecule must be given')

    self._mol = mol
    
    AbstractSpectrumWindow.__init__(self, mainApp, **kw)

##  def _init_vars(self) :
##    """Initialize variables."""
##    # construct filetypes
##    # add pdf if ps2pdf is found
##    # add all supported filetypes supported by matplotlib
##    self.__save_filetypes = []
##
##    if misc.is_command_on_path('ps2pdf') :
##      self.__save_filetypes.append(
##        (resources.STRING_FILETYPE_PDFFILE_DESCRIPTION, '*.pdf'))
##
##    self.__save_filetypes.append(
##      (resources.STRING_FILETYPE_EPSFILE_DESCRIPTION, '*.ps *.eps'))
##    self.__save_filetypes.append(
##      (resources.STRING_FILETYPE_PNGFILE_DESCRIPTION, '*.png'))

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    title = r'Calculated Raman/ROA/Degree of circularity spectra of "%s"' % \
            self._mol.name
    self.wm_title(title)

    ## top - the most important spectra
    group_settings = Pmw.Group(self, tag_text='Spectra')
    group_settings.grid(row=0, column=0,
                        padx=3, pady=3, columnspan=2, sticky='we')

    # scattering type : 180, 0, 90 etc.
    items = resources.STRINGS_SCATTERING_TYPES
    width = max([ len(item) for item in items ])
    widget = Pmw.OptionMenu(group_settings.interior(),
                            labelpos='w',
                            label_text='Scattering :',
                            labelmargin=3,
                            menubutton_width=width,
                            items=items,
                            command=Command(self.__redraw_figure))
    self._varsdict['options_scattering'] = widget
    self._varsdict['options_scattering'].grid(row=0, column=0,
                                              padx=3, pady=3, sticky='w')

    # representation type : fitted or stick
    items = resources.STRINGS_SPECTRA_REPRESENTATION_TYPES
    width = max([ len(item) for item in items ])
    widget = Pmw.OptionMenu(group_settings.interior(),
                            labelpos='w',
                            label_text='Representation :',
                            labelmargin=3,
                            menubutton_width=width,
                            items=items,
                            command=Command(self.__redraw_figure))
    self._varsdict['options_representation'] = widget
    self._varsdict['options_representation'].grid(row=0, column=1,
                                                  padx=3, pady=3, sticky='w')
    ## message bar at the bottom
    self._varsdict['msgBar'] = Pmw.MessageBar(self, entry_relief='sunken')
    self._varsdict['msgBar'].grid(row=2, column=0, columnspan=2,
                                  padx=3, pady=3, sticky='we')    

    ## plotting area
    self.grid_columnconfigure(0, weight=1)
    self.grid_rowconfigure(1, weight=1)
    
    widget = RamanROADegcircCalcFigure(self, self._mol,
                                       showvib_callback=self._showvib,
                                       msgBar=self._varsdict['msgBar'],
                                       title1=self._mol.name)
    self._varsdict['figure'] = widget
    self._varsdict['figure'].tk_canvas.get_tk_widget().grid(row=1, column=0,
                                                            padx=3, pady=3,
                                                            sticky='news')
    ## button toolbar to the right of the plot
    btn_toolbar = self.__constructButtonToolbar(self)
    btn_toolbar.grid(row=1, column=1, padx=3, pady=10, sticky='n')

    ## first rendering
    self.__redraw_figure()      

  def _showvib(self, info) :
    """Show a vibration in a separate window.

    Positional arguments :
    info -- molno, spectrum_type
    
    """
    self.tk.call('update', 'idletasks')

    if info is not None and not None in info :
      invert_roa = self._varsdict['figure'].settings['roa_invert']
      SingleVibrationWindow(self._mainApp,
                            self._mol,
                            vib_no=info[0],
                            molecule_name=self._mol.name,
                            show_gcm=True,
                            molinv=info[1],
                            invert_roa=invert_roa)

  def __redraw_figure(self, *dummy) :
    """Change the scattering or the representation type."""
    self.tk.call('update', 'idletasks')
    
    # setting the busy cursor
    self._varsdict['figure'].tk_canvas.get_tk_widget().configure(cursor='watch')

    # recalculate the limits since they are
    # rather different for the stick and fitted representations
    self._varsdict['figure'].plot_spectra(
      scattering=self._varsdict['options_scattering'].getvalue(),
      representation=self._varsdict['options_representation'].getvalue(),
      raman_limits_auto=True,
      roa_limits_auto=True)
    
    # refresh the values in the settings dialog if it is opened
    if 'dlg_settings' in self._varsdict :
      self._varsdict['dlg_settings'].update_controls(self._varsdict['figure'])
  
    # restoring the normal cursor
    self._varsdict['figure'].tk_canvas.get_tk_widget().configure(cursor='')

  def __constructButtonToolbar(self, parent) :
    """Construct the button toolbar and return it."""
    btn_toolbar = widgets.ButtonToolbar(parent, horizontal=False)

    # clone button
    btn_toolbar.add_button(imagename='clone',
                           command=self.clone,
                           helptext='Clone the window.')
    
    # save spectra
    btn_toolbar.add_button(imagename='save',
                           command=self._save_figure,
                           helptext='Export the spectrum in PNG, ' + \
                           'EPS and PDF (requires ps2pdf) formats.')
    
    # ACP / GCMs
    btn_toolbar.add_button(imagename='gcm',
                           command=self.__raman_roa_matrices,
                           helptext='GCM / ACPs')

    # spectra settings
    btn_toolbar.add_button(imagename='prefs',
                           command=self.__settings,
                           helptext='Settings of the spectra.')

    btn_toolbar.add_separator()

    # restore the previous zooming region
    command = Command(self._varsdict['figure'].restore_last_zoom)
    btn_toolbar.add_button(imagename='undo',
                           command=command,
                           helptext='Restore the previous plotting region.')
    return btn_toolbar

  def __settings(self) :
    """Show the settings of the spectra."""
    if 'dlg_settings' not in self._varsdict :
      ok_command = Command(self._varsdict['figure'].plot_spectra)
      widget = dialogs.RamanRoaDegcircCalcSettingsDialog(
          self, ok_command=ok_command)
      self._varsdict['dlg_settings'] = widget
      self._varsdict['dlg_settings'].configure(
        title=r'Spectra settings for "%s"' % self._mol.name)

    # do not forget to update the controls !
    self._varsdict['dlg_settings'].update_controls(self._varsdict['figure'])
    
    self._varsdict['dlg_settings'].show()

  def _save_figure(self) :
    """Callback for the save button."""
    if 'dlg_settings' in self._varsdict :
      size = self._varsdict['dlg_settings'].figsize_inches
    else :
      size = None

    self._save(self._varsdict['figure'], name=self._mol.name, size=size)

  def __raman_roa_matrices(self) :
    """Start the Raman/ROA generation interface."""
    self.tk.call('update', 'idletasks')
    
    splash = widgets.SplashScreen(self.master,
                                  'Calculating the Raman/ROA invariants...')

    invert_roa = self._varsdict['figure'].settings['roa_invert']
    RamanROAMatricesWindow(self._mainApp, self._mol,
                           camera=self._smartdict['camera'],
                           invert_roa=invert_roa)
    splash.destroy()

  def clone(self) :
    """Clone the molecule window.

    Overrides the base class method.
    
    """
    self.tk.call('update', 'idletasks')
    splash = widgets.SplashScreen(self, 'Cloning the window...')
    RamanROADegcircCalcWindow(self._mainApp, self._mol)
    splash.destroy()


class RamanROAMatricesWindow(BaseWindow) :
  """Raman/ROA generation interface.

  The following public methods are explorted :
      clone() -- clone the molecule window
  
  """

  def __init__(self, mainApp, mol, **kw) :
    """Constructor of the class.

    Positional arguments :
    mainApp  -- reference to the main window of PyVib2
    mol      -- molecule

    Keyword arguments :
    camera      -- camera to be set in secondary windows (default None)
    invert_roa  -- whether to invert the sign of ROA (default False)
    
    """
    if not isinstance(mol, molecule.Molecule) :
      raise ConstructorError('Invalid molecule argument')

    # raise an exception if the molecule does not have Raman/ROA data.
    if not hasattr(mol, 'raman_roa_tensors') or mol.raman_roa_tensors is None :
      raise ConstructorError('Molecule does not have the Raman/ROA data')

    self.__mol = mol
    
    BaseWindow.__init__(self, mainApp, **kw)

  def _init_vars(self) :
    """Initialize variables."""
    ## keywords available
    # vib_no - start vibration number (default : taken moleculeWindow)
    # camera - start camera position (default : taken moleculeWindow)
    # tabname - name of the start tab
    # (default : self._varsdict['STRINGS_TAB_NAMES'][0])
    # groups (atom indices are null-based) :
    #             [ ['#000000', 0, 1, 2], ['#113400', 5, 7, 8] ]    
    # molinv
    # group_mode - 'single atoms' or 'groups'

    # predefine the names of the tabs
    self._varsdict['STRINGS_TAB_NAMES'] = ('Molecular invariants',
                                'V-tensors\' invariants', \
                                'ACP', 'Vibration')

    # molinv - invariant
    self._varsdict['STRINGS_MOLINV'] = spectra.LIST_INVARIANTS + \
                            ('raman', 'roa_backward', 'roa_forward')
    
    if self._smartdict['tabname'] is not None and \
       self._smartdict['tabname'] not in self._varsdict['STRINGS_TAB_NAMES'] :
      raise InvalidArgumentError(
        'Invalid tab name : %s' % self._smartdict['tabname'])

    if self._smartdict['group_mode'] is not None and \
       self._smartdict['group_mode'] not in ('single atoms', 'groups') :
      raise InvalidArgumentError(
        'Invalid group mode : %s' % self._smartdict['group_mode'])

    # multiply factors for acps and invariants
    self._varsdict['MULTFACTOR_INVARIANT']     = 1.0E+80
    self._varsdict['MULTFACTOR_CROSS_SECTION'] = 1.0E+14

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    # the controls above the tabs
    self._balloon.bind(self._varsdict['radio_gcm'],
                       'Show the contributions of the single atoms' + \
                       ' or groups of atoms.')
    self._balloon.bind(self._varsdict['btn_groups'],
                       'Define groups within the molecule.')
    # molecular invariants tab
    self._balloon.bind(self._varsdict['options_items_molinv'],
                       'Particular invariant or combination of invariants.')
    self._balloon.bind(self._varsdict['counter_sf_molinv'],
                       'Multiplication factor for the radia of the circles.')
    # acp tab
    self._balloon.bind(self._varsdict['options_items_acp'],
                       'Particular invariant or combination of invariants.')
    self._balloon.bind(self._varsdict['counter_sf_acp'],
                       'Multiplication factor for the radia of the spheres.')

  def __Configure(self, e) :
    """<Configure> event handler."""
    self.update_idletasks()
    self._varsdict['var_acp_rw_size'].set(
      '%dx%d' % self._varsdict['render_widget'].GetRenderWindow().GetSize())

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    self.wm_title(r'Raman/ROA generation for "%s"' % self.__mol.name)

    ## top : panel with commonon controls
    frm_top = Tkinter.Frame(self)
    frm_top.grid(row=0, column=0, columnspan=2, padx=3, pady=3, sticky='w')
    
    # vibrational toolbar
    callback = Command(self.__refresh)
    widget = widgets.VibNavigationFrame(frm_top,
                                        self.__mol.freqs,
                                        changed_callback=callback,
                                        vib_no=self._smartdict['vib_no'] or 1)
    self._varsdict['vib_frame'] = widget
    self._varsdict['vib_frame'].grid(row=0, column=0,
                                     padx=3, pady=3, sticky='w')

    # atoms groups or single atoms
    self._varsdict['groups'] = None
    self._varsdict['groups_with_colors'] = None
    
    # default : atoms
    self._varsdict['radio_gcm'] = Pmw.RadioSelect(frm_top,
                                                  buttontype='radiobutton',
                                                  orient='horizontal',
                                                  labelpos='w',
                                                  label_text='Mode : ',
                                                  frame_borderwidth=2,
                                                  frame_relief='ridge',
                                                  command=callback)
    self._varsdict['radio_gcm'].grid(row=0, column=1,
                                     padx=5, pady=3, sticky='w')
    
    self._varsdict['radio_gcm'].add('single atoms')
    self._varsdict['radio_gcm'].add('groups')

    self._varsdict['radio_gcm'].setvalue(
      self._smartdict['group_mode'] or 'single atoms')

    # define groups button
    widget = Tkinter.Button(frm_top,
                            image=getimage('define_groups'),
                            relief='flat',
                            overrelief='raised',
                            command=self.__define_groups)
    self._varsdict['btn_groups'] = widget
    self._varsdict['btn_groups'].grid(row=0, column=2,
                                      padx=3, pady=3, sticky='w')

    ## window toolbar : can go back to the molecule window
    widget = widgets.WindowNavigationToolbar(self,
                                             mainApp=self._mainApp,
                                             homebutton=True)
    self._varsdict['window_toolbar'] = widget
    self._varsdict['window_toolbar'].grid(row=0, column=2,
                                          padx=3, pady=3, sticky='e')
    
    ## bottom : notebook for invariants, V-tensors & 3D-widget for ACP
    self.grid_rowconfigure(1, weight=1)
    self.grid_columnconfigure(0, weight=1)
    
    self._varsdict['notebook'] = Pmw.NoteBook(self,
                                              raisecommand=self.__tab_raise)
    self._varsdict['notebook'].grid(row=1, column=0, columnspan=2,
                                    padx=3, pady=3, sticky='news')

    ## right : vertical toolbar with buttons
    btn_toolbar = self.__constructButtonToolbar(self)
    btn_toolbar.grid(row=1, column=2, padx=3, pady=3, sticky='wn')

    # message bar
    self._varsdict['msgBar'] = Pmw.MessageBar(self,
                                              entry_relief='sunken',
                                              label_text='Status : ',
                                              labelpos='w')
    self._varsdict['msgBar'].grid(row=2, column=0, columnspan=2,
                                  padx=0, pady=3, sticky='we')

    # which invariant to show ?
    molinv = self._smartdict['molinv'] in self._varsdict['STRINGS_MOLINV'] and \
             self._smartdict['molinv'] or None
    
    tabMolInv = self._varsdict['notebook'].add(
      self._varsdict['STRINGS_TAB_NAMES'][0])
    self.__constructMatrixTab(tabMolInv, 'molinv',
                              self._varsdict['STRINGS_MOLINV'],
                              start_value=molinv)

    # V tensors' invariants : V_a2, V_b2, V_aG, V_b2G or V_b2A
##    tabVInv = self._varsdict['notebook'].add(
##      self._varsdict['STRINGS_TAB_NAMES'][1])
##    self.__constructMatrixTab(tabVInv, 'vinv', spectra.LIST_VTENSORS)

    # ACP tab : 3D-widget
    tabACP = self._varsdict['notebook'].add(
      self._varsdict['STRINGS_TAB_NAMES'][2])
    self.__constructACPTab(tabACP, self._varsdict['STRINGS_MOLINV'],
                           start_value=molinv)

    tabACP.bind('<Configure>', self.__Configure)

    # Vibration : current vibration
    tabVib = self._varsdict['notebook'].add(
      self._varsdict['STRINGS_TAB_NAMES'][3])
    self.__constructVibTab(tabVib)

    # raise a tab if requested
    # and set the natural size of the tabs
    self._varsdict['notebook'].selectpage(
      self._smartdict['tabname'] or self._varsdict['STRINGS_TAB_NAMES'][0])
    self._varsdict['notebook'].setnaturalsize()

    # set the groups if the given
    if self._smartdict['groups'] is not None :
      self._varsdict['groups_with_colors'] = self._smartdict['groups']
      self._varsdict['groups'] = self.__conv_groups(self._smartdict['groups'])

    # do the first rendering
    self.__refresh(auto_sf_molinv=True, auto_sf_vinv=True)

    self.__updateGUI()

  def __constructButtonToolbar(self, parent) :
    """Construct the button toolbar."""
    btn_toolbar = widgets.ButtonToolbar(parent, horizontal=False)

    # clone button
    btn_toolbar.add_button(imagename='clone',
                           command=self.clone,
                           helptext='Clone the window.')
    
    # save button (GCM or ACP)
    self._varsdict['btn_save'] = btn_toolbar.add_button(
      imagename='save',
      command=self.__save_gcm,
      helptext='Save the currently selected matrix.')

    # plot spectra
    btn_toolbar.add_button(imagename='spectrum',
                           command=self.__plot_spectra,
                           helptext='Plot the spectra.')

    return btn_toolbar

  def __constructMatrixTab(self, tab, prefix, items, start_value=None) :
    """Construct a tab for viewing of matrices : total, is, anis, a."""
    ## top : list of items & scale factor
    self._varsdict['var_sf_%s' % prefix] = Tkinter.StringVar()

    # for the molecular invariants : 100.
    # for the V-tensors invarians : 0.01
    if 'molinv' == prefix :
      width   = 12
      initval = 1.
    elif 'vinv' == prefix :
      width   = 5
      initval = 0.01
    else :
      initval = 1.
      
    self._varsdict['var_sf_%s' % prefix].set(initval)

    # text for the option menu
    if 'molinv' == prefix :
      label_text = 'Invariant / cross-section :'
    else :
      label_text = 'Tensor :'

    # invariants : synchronize with ACP
    if 'molinv' == prefix :
      command = Command(self.__sync_inv, 'molinv', 'acp')
    else :
      command = self.__refresh
    
    widget = Pmw.OptionMenu(tab,
                            labelpos='w',
                            label_text=label_text,
                            items=items,
                            menubutton_width=width,
                            command=command)
    self._varsdict['options_items_%s' % prefix] = widget
    self._varsdict['options_items_%s' % prefix].grid(row=0, column=0,
                                                     padx=3, pady=3,
                                                     sticky='w')
    if start_value :
      self._varsdict['options_items_%s' % prefix].setvalue(start_value)

    # scale factor : synchronize the molecular invariants with acp
    validate = dict(validator='real',
                    min=0.,
                    max=100000.0)
    
    if 'molinv' == prefix :
      mod_command = Command(self.__sync_counters, 'molinv', 'acp')
    else :
      mod_command = self.__refresh
      
    widget = Pmw.Counter(tab,
                         labelpos='w',
                         label_text='Scale factor : ',
                         entry_width=7,
                         entry_textvariable=\
                         self._varsdict['var_sf_%s' % prefix],
                         datatype=dict(counter='real'),
                         entryfield_validate=validate,
                         entryfield_modifiedcommand=mod_command,
                         autorepeat=False,
                         increment=0.1)
    self._varsdict['counter_sf_%s' % prefix] = widget
    self._varsdict['counter_sf_%s' % prefix].grid(row=0, column=1,
                                                  padx=3, pady=3, sticky='w')
    # optimal size of the scale factor
    kw = dict()
    if 'molinv' == prefix :
      kw['auto_sf_molinv'] = True
      kw['auto_sf_vinv']   = False
    else :
      kw['auto_sf_molinv'] = False
      kw['auto_sf_vinv']   = True
      
    btn_optimal_sf = Tkinter.Button(tab,
                                    image=getimage('optimal_size'),
                                    command=Command(self.__refresh, **kw))
    btn_optimal_sf.grid(row=0, column=2, padx=3, pady=3, sticky='w')

    # invert roa (controlled by the contructor keyword invert_roa)
    self._varsdict['var_invert_roa'] = Tkinter.IntVar()
    var = self._varsdict['var_invert_roa']
    if self._smartdict['invert_roa'] :
      var.set(1)
    
    check_invert_roa = Tkinter.Checkbutton(tab,
                                           text='Invert ROA',
                                           variable=var,
                                           command=self.__refresh)
    check_invert_roa.grid(row=0, column=3, padx=3, pady=3, sticky='w')
    

    ## bottom : expandable notebook with the total, is, anis & a parts
    tab.grid_columnconfigure(0, weight=1)
    tab.grid_rowconfigure(1, weight=1)
    
    self._varsdict['notebook_parts_%s' % prefix] = Pmw.NoteBook(tab)
    self._varsdict['notebook_parts_%s' % prefix].grid(row=1, column=0,
                                                      columnspan=4,
                                                      padx=3, pady=3,
                                                      sticky='news')
    # each tab of the notebook corresponds to a part of the invariants
    # it contains a scrollable frame with TwoDCircles
    labels = ('total', 'isotropic', 'anisotropic', 'antisymmetric')
    
    for i in xrange(len(labels)) :
      tab_part = self._varsdict['notebook_parts_%s' % prefix].add(labels[i])

      # creating a scrollframe
      tab_part.grid_columnconfigure(0, weight=1)
      tab_part.grid_rowconfigure(0, weight=1)  

      scrolled_frm = Pmw.ScrolledFrame(tab_part)
      scrolled_frm.grid(row=0, column=0, padx=3, pady=3, sticky='news')

      # creating and saving TwoDCircles
      scrolled_frm.interior().grid_columnconfigure(0, weight=1)
      scrolled_frm.interior().grid_rowconfigure(0, weight=1)  
      
      widget = widgets.TwoDCircles(scrolled_frm.interior(),
                                   color_positive='red',
                                   color_negative='yellow',
                                   msgBar=self._varsdict['msgBar'])
      self._varsdict['circles_%s_%d' % (prefix, i)] = widget
      self._varsdict['circles_%s_%d' % (prefix, i)].grid(row=0, column=0,
                                                         padx=3, pady=3,
                                                         sticky='news')

  def __constructACPTab(self, tab, items, start_value=None) :
    """Contstruct the ACP tab."""
    ## top : molecular invariant & scale factor
    command = Command(self.__sync_inv, 'acp', 'molinv')
    widget = Pmw.OptionMenu(tab,
                            labelpos='w',
                            label_text='Invariant / cross-section :',
                            items=items,
                            menubutton_width=12,
                            command=command)
    self._varsdict['options_items_acp'] = widget
    self._varsdict['options_items_acp'].grid(row=0, column=0,
                                             columnspan=2, padx=3, pady=3,
                                             sticky='w')
    if start_value :
      self._varsdict['options_items_acp'].setvalue(start_value)

    # scale factor
    self._varsdict['var_sf_acp'] = Tkinter.StringVar()
    self._varsdict['var_sf_acp'].set(1.0)

    validate = dict(validator='real',
                    min=0.,
                    max=100000.0)
    mod_command = Command(self.__sync_counters, 'acp', 'molinv')
    
    widget = Pmw.Counter(tab,
                         labelpos='w',
                         label_text='Scale factor : ',
                         entry_width=7,
                         entry_textvariable=self._varsdict['var_sf_acp'],
                         datatype=dict(counter='real'),
                         entryfield_validate=validate,
                         entryfield_modifiedcommand=mod_command,
                         autorepeat=False,
                         increment=0.1)
    self._varsdict['counter_sf_acp'] = widget    
    self._varsdict['counter_sf_acp'].grid(row=0, column=2,
                                          padx=3, pady=3, sticky='w')
    ## button button toolbar
    btn_toolbar = widgets.ButtonToolbar(tab)
    btn_toolbar.grid(row=1, column=0, columnspan=2, padx=3, pady=3, sticky='w')

    # snapshot
    btn_toolbar.add_button(imagename='snapshot',
                           command=self.__snapshot,
                           helptext='Make a snapshot of the render window.')

    # size of the render widget
    self._varsdict['var_acp_rw_size'] = Tkinter.StringVar()    
    btn_kw = dict(textvariable=self._varsdict['var_acp_rw_size'],
                  justify='center',
                  helptext='Current size of the render widget.')

    self._varsdict['btn_acp_rw_size'] = btn_toolbar.add_button(**btn_kw)
    self._varsdict['btn_acp_rw_size'].configure(overrelief='flat')

    ## bottom : render widget & navigation toolbar
    tab.grid_rowconfigure(2, weight=1)
    tab.grid_columnconfigure(1, weight=1)

    widget = widgets.MoleculeRenderWidget(tab,
                                          molecule=self.__mol,
                                          width=600,
                                          height=600,
                                          resolution=\
                                          self._mainApp.settings['resolution'],
                                          camera=self._smartdict['camera'])
    self._varsdict['render_widget'] = widget
    self._varsdict['render_widget'].grid(row=2, column=1, columnspan=2,
                                         padx=3, pady=3, sticky='news')

    command = misc.Command(self._change_render_widget_size,
                           self._varsdict['render_widget'])    
    self._varsdict['btn_acp_rw_size'].configure(command=command)

    # navigation toolbar
    navi_toolbar = widgets.NavigationToolbar(tab,
                                             self._varsdict['render_widget'])
    navi_toolbar.grid(row=2, column=0, padx=3, pady=3, sticky='ns')
    navi_toolbar.save_camera_state()

  def __constructVibTab(self, tab) :
    """Construct the Vibration tab."""
    tab.grid_columnconfigure(1, weight=1)
    tab.grid_rowconfigure(1, weight=1)
    
    # bottom part
    widget = widgets.MoleculeRenderWidget(tab,
                                          height=400,
                                          width=400,
                                          molecule=self.__mol,
                                          resolution=\
                                          self._mainApp.settings['resolution'],
                                          camera=self._smartdict['camera'])
    self._varsdict['render_widget2'] = widget
    self._varsdict['render_widget2'].grid(row=1, column=1,
                                          padx=3, pady=3, sticky='news')

    # navigation toolbar
    navi_toolbar = widgets.NavigationToolbar(tab,
                                             self._varsdict['render_widget2'])
    navi_toolbar.grid(row=1, column=0, padx=3, pady=3, sticky='ns')
    navi_toolbar.save_camera_state()
    
    # upper part
    kw = dict(widget=self._varsdict['render_widget2'],
              vib_no=self._varsdict['vib_frame'].vib_no,
              show_gcm=False,
              fragment_controls=False,
              rep_type=resources.STRING_VIB_ENERGY,
              rep_subtype=resources.STRING_VIB_ENERGY_VOLUME)      
    self._varsdict['vibtoolbarlight'] = widgets.VibrationalToolbarLight(tab,
                                                                        **kw)
    self._varsdict['vibtoolbarlight'].grid(row=0, column=0, columnspan=2,
                                           padx=3, pady=3, sticky='we')

  def __refresh(self, *dummy, **kw) :
    """Refresh all visual controls.

    Positional arguments :
    auto_sf_molinv -- set the optimal scale factor for
                      the molecular invariants.
    auto_sf_vinv   -- ... for the V tensor invariants.
    
    """    
    self.tk.call('update')

    auto_sf_molinv = kw.get('auto_sf_molinv', False)
    auto_sf_vinv   = kw.get('auto_sf_vinv', False)

    # installing the busy cursor
    self.configure(cursor='watch')

    # go
    p       = self._varsdict['vib_frame'].vib_no
    tensors = self.__mol.raman_roa_tensors

    use_gcm = 'groups' == self._varsdict['radio_gcm'].getvalue()

    ## updating the windows with the vibration
    self._varsdict['vibtoolbarlight'].vib_no = p

    ## labels for the matrices :
    ## single atoms : atom_index
    ## groups : gn
    if use_gcm :
      labels = [0] + [ 'g%d' % g for g \
                       in xrange(1, 1 + len(self._varsdict['groups'])) ]

    else :
      labels = [0] + [ '%s%d' % (a.element.symbol, a.index) for a \
                       in self.__mol.atoms ]

    ## V-tensors do not depend on p
    ## calculate only once
##    item = self._varsdict['options_items_vinv'].getvalue()
##    
##    if 'vinv_%s' % item not in self._varsdict :
##      V = eval('tensors.%s(%d)' % (item, 0))
##
##      self._varsdict['vinv_%s' % item] = contract_t(V)
##
##    for i in xrange(4) :
##      # reference to the object
##      circles  = self._varsdict['circles_vinv_%d' % i]
##      raw_data = self._varsdict['vinv_%s' % item][i]
##
##      if use_gcm :
##        data = make_gcm(raw_data, self._varsdict['groups'])
##        
##      else :
##        data = raw_data
##
##      # calculate the optimal scale factor for the total combination
##      if 0 == i and auto_sf_vinv:
##        scale_factor = self.__optimal_scale_factor(data, 4)
##        
##        self._varsdict['var_sf_vinv'].set(scale_factor)
##
##      # update the GUI
##      circles.update(
##        data=data,
##        scale_factor=\
##        misc.str_to_float(self._varsdict['var_sf_vinv'].get(), 0.),
##        labels2_cols=labels,
##        labels2_rows=labels,
##        mode=resources.NUM_MODE_UPPERHALFONLY,
##        sumup_diag=True)
      
    ## molecular invariants do depend on p
    item = self._varsdict['options_items_molinv'].getvalue()

    # invert ROA ?
    invert_roa = item in ('aG', 'b2G', 'b2A', 'roa_backward', 'roa_forward') \
                 and self._varsdict['var_invert_roa'].get()
      
    for i in xrange(4) :
      # reference to the object      
      circles  = self._varsdict['circles_molinv_%d' % i]

      # what is to be shown
      raw_data = self.__molinv(tensors, item, p, i)
      if invert_roa :
        raw_data *= -1.
  
      if use_gcm :
        data = make_gcm(raw_data, self._varsdict['groups'])        
      else :
        data = raw_data

      # multiply the elements for single invariants
      if item in spectra.LIST_INVARIANTS :
        data *= self._varsdict['MULTFACTOR_INVARIANT']
      else :
        data *= self._varsdict['MULTFACTOR_CROSS_SECTION']

      # calculate the optimal scale factor for the total combination
      if 0 == i and auto_sf_molinv:
        scale_factor = self.__optimal_scale_factor(data)
        
        self._varsdict['var_sf_molinv'].set(scale_factor)
        self._varsdict['var_sf_acp'].set(scale_factor)

      # update the GUI
      circles.update(
        data=data,
        scale_factor=\
        misc.str_to_float(self._varsdict['var_sf_molinv'].get(), 0.),
        labels2_cols=labels,
        labels2_rows=labels,
        mode=resources.NUM_MODE_UPPERHALFONLY,
        sumup_diag=True)

    # ACPs (only total part)
    # i must be 0, found on 20.06.2006
    item = self._varsdict['options_items_acp'].getvalue()

    acp = tensors.acp(item, p)
    if invert_roa :
      acp *= -1.

    # multiply the elements for single invariants
    if item in spectra.LIST_INVARIANTS :
      acp *= self._varsdict['MULTFACTOR_INVARIANT']
      
    else :
      acp *= self._varsdict['MULTFACTOR_CROSS_SECTION']
    
    scale_factor = misc.str_to_float(self._varsdict['var_sf_acp'].get(), 0.)

    # can sum up the acp for the groups :)
    if use_gcm :
      self._varsdict['render_widget'].render_gcp(
        acp, self._varsdict['groups'], scale_factor=scale_factor)
    else :    
      self._varsdict['render_widget'].render_scalars(
        acp, scale_factor=scale_factor)
      
    self._varsdict['render_widget'].Render()

    # returning the usual cursor
    self.configure(cursor='')

  def __sync_counters(self, prefix_src, prefix_dest) :
    """Synchronize the counters for GCM and ACP and finally refresh all."""
    self._varsdict['var_sf_%s' % prefix_dest].set(
      self._varsdict['var_sf_%s' % prefix_src].get())

    self.__refresh()

  def __sync_inv(self, dummy, prefix_src, prefix_dest) :
    """Synchronize the invariants for GCM and ACP and finally refresh all."""
    self._varsdict['options_items_%s' % prefix_dest].setvalue(\
      self._varsdict['options_items_%s' % prefix_src].getvalue())

    self.__refresh()

  def __optimal_scale_factor(m, ndigits=2) :
    """Calculate the optimal scale factor for a matrix.

    The square of a circle is proportional to the value.
    Empirically found : for val = 0.05 the scale factor is 4.

    Positional arguments :
    m       -- matrix

    Keyword arguments :
    ndigits -- number of digits after comma (default 2)

    """
    # transform the matrix to upper diagonal
    m_ = zeros(m.shape, 'd')
    for i in xrange(m.shape[0]) :
      for j in xrange(i, m.shape[0]) :
        m_[i, j] = m[i, j] + m[j, i]
        
    maxval = abs(m_).max()
    
    sf = 0. != maxval and sqrt(0.05/maxval) * 4. or 1.
    format = '%%.%df' % ndigits
    
    return float(format % sf)

  __optimal_scale_factor = staticmethod(__optimal_scale_factor)

  def __tab_raise(self, tabname) :
    """Called when a tab is raised."""
    # ACP
    if self._varsdict['STRINGS_TAB_NAMES'][2] == tabname :
      self._varsdict['render_widget'].camera_state = \
                        self._varsdict['render_widget2'].camera_state

    # Vibration
    elif self._varsdict['STRINGS_TAB_NAMES'][3] == tabname :
      self._varsdict['render_widget2'].camera_state = \
                        self._varsdict['render_widget'].camera_state

    # deactivate the save button if ACP or Vibration are selected
    if tabname not in self._varsdict['STRINGS_TAB_NAMES'][2:] :
      state = 'normal'
    else :
      state = 'disabled'

    self._varsdict['btn_save'].configure(state=state)
    
  def __molinv(tensors, item, p, i) :
    """Get a molecular invariant or a cross-section.

    Positional arguments :
    tensors -- must be instance of spectra.RamanROATensors
    item    -- one of ('raman', 'roa_backward',
                       'roa_forward', 'a2', 'b2', 'aG', 'b2G','b2A')
    p       -- number of vibration
    i       -- part (0-4)
    
    """
    units = 'cross-section'
    
    if 'raman' == item :
      coeffs   = spectra.inv_coeffs_raman_roa(0)
      raw_data = coeffs[0] * ( coeffs[1] * tensors.a2(p, i, units=units) + \
                               coeffs[2] * tensors.b2(p, i, units=units) )

    elif 'roa_backward' == item :
      coeffs   = spectra.inv_coeffs_raman_roa(0)
      raw_data = coeffs[3] *( coeffs[5] * tensors.b2G(p, i, units=units) + \
                              coeffs[6] * tensors.b2A(p, i, units=units) )
    elif 'roa_forward' == item :
      coeffs   = spectra.inv_coeffs_raman_roa(1)
      raw_data = coeffs[3] * ( coeffs[4] * tensors.aG(p, i, units=units) + \
                               coeffs[5] * tensors.b2G(p, i, units=units) + \
                               coeffs[6] * tensors.b2A(p, i, units=units) )

    # showing the invariant in atomic units (unlike for the combination!)
    else :
      raw_data = eval('tensors.%s(%d, i=%d, units=\'invariant\')' % \
                      (item, p, i))
    return raw_data

  __molinv = staticmethod(__molinv)

  def __updateGUI(self) :
    """Reflect changes in GUI."""
    # disable the group selection if no groups were defined
    state = 'normal'
    
    if self._varsdict['groups'] is None :
      state = 'disabled'

    self._varsdict['radio_gcm'].button(1).configure(state=state)

  def __define_groups(self) :
    """Define groups."""
    self.tk.call('update')

    # get the correct initial camera state
    tab_sel = self._varsdict['notebook'].index(
      self._varsdict['notebook'].getcurselection())
    
    if 3 == tab_sel :
      camera = self._varsdict['render_widget2'].camera  
    else :
      camera = self._varsdict['render_widget'].camera

    dlg = dialogs.DefineGroupsDialog(
      self,
      self.__mol,
      ok_command=self.__set_groups,
      resolution=self._mainApp.settings['resolution'],
      groups=self._varsdict['groups_with_colors'],
      camera=camera)
    self._varsdict['dlg_groups'] = dlg
    self._varsdict['dlg_groups'].show()

  def __set_groups(self, groups) :
    """Set groups and update the interface.

    Positional arguments :
    groups -- groups              
              atom indices are null-based
              example : [ ['#000000', 0, 1, 2], ['#113400', 5, 7, 8] ]

    """
    # ignore empty groups
    if groups is None or 0 == len(groups) :
      return
    
    self._varsdict['groups_with_colors'] = groups
    self._varsdict['groups'] = self.__conv_groups(groups)

    self.__updateGUI()

    self._varsdict['radio_gcm'].setvalue('groups')
    self.__refresh()

    # set the camera
    self._varsdict['render_widget'].camera  = \
                          self._varsdict['dlg_groups'].renderWidget.camera
    self._varsdict['render_widget2'].camera = \
                          self._varsdict['dlg_groups'].renderWidget.camera

  def __conv_groups(groups_with_colors) :
    """Convert groups with the colors to a list of groups.

    Positional arguments :
    groups_with_colors : groups
                         example :
                         [ ['#000000', 0, 1, 2], ['#113400', 5, 7, 8] ]

    Return [ [1, 2, 3], [6, 8, 9] ].
    
    """
    return [ (1 + array(group[1:])).tolist() for group in groups_with_colors ]

  __conv_groups = staticmethod(__conv_groups)
  
  def __save_gcm(self) :
    """Save currently active GCM."""
    # define which tab is currently active
    sel_tab_i = self._varsdict['notebook'].index(
      self._varsdict['notebook'].getcurselection())

    ## Molecular invariants or V-tensors' invariants
    if sel_tab_i in (0, 1) :
      prefices = ('molinv', 'vinv')
      
      subnotebook = self._varsdict['notebook_parts_%s' % prefices[sel_tab_i]]

      # selected index of the subnotebook
      sel_subtab_i = subnotebook.index(subnotebook.getcurselection())

      # TwoDCircles
      circles_to_save = self._varsdict[
        'circles_%s_%d' % (prefices[sel_tab_i], sel_subtab_i)]

      # can save only PostScript files
      filetypes  = [ (resources.STRING_FILETYPE_EPSFILE_DESCRIPTION, '*.ps') ]
      defaultext = '.ps'

      filename = tkFileDialog.SaveAs(parent=\
                                     self._varsdict['notebook'].interior(),
                                     initialdir=self.__get_lastdir(),
                                     filetypes=filetypes,
                                     defaultextension=defaultext).show()
      if not filename :
        return

      try :
        self.__save_lastdir(filename)
        circles_to_save.postscript(file=filename)
      except :
        widgets.show_exception(sys.exc_info())

  def __snapshot(self) :
    """Ask the user about the snapshot settings of the ACP."""
    self.tk.call('update', 'idletasks')
    
    dlg = dialogs.SnapshotDialog(self,
                                 mode='file',
                                 initialdir=self.__get_lastdir(),
                                 renderWidget=self._varsdict['render_widget'])
    dlg.show()

  def __get_lastdir(self) :
    """Return the last visited directory."""
    if 'lastdir' not in self._varsdict :
      self._varsdict['lastdir'] = self._mainApp.lastdir

    return self._varsdict['lastdir']

  def __save_lastdir(self, filename) :
    """Save the directory name of a file to the internal variable."""
    if filename is not None :
      self._varsdict['lastdir'] = os.path.dirname(filename)

  def __plot_spectra(self) :
    """Plot the spectra."""
    self.tk.call('update', 'idletasks')
    
    splash = widgets.SplashScreen(
      self.master,
      r'Plotting the spectra for %s...' % self.__mol.name)
    
    RamanROADegcircCalcWindow(self._mainApp, self.__mol,
                              camera=self._varsdict['render_widget'].camera)

    splash.destroy()
    
  def clone(self) :
    """Clone the molecule window.

    Overrides the base class method.
    
    """
    self.tk.call('update', 'idletasks')

    splash = widgets.SplashScreen(self, 'Cloning the window...')
    
    RamanROAMatricesWindow(
      self._mainApp,
      self.__mol,
      vib_no=self._varsdict['vib_frame'].vib_no,
      camera=self._varsdict['render_widget'].camera,
      tabname=self._varsdict['notebook'].getcurselection(),
      groups=self._varsdict['groups_with_colors'],
      molinv=self._varsdict['options_items_molinv'].getvalue(),
      group_mode=self._varsdict['radio_gcm'].getvalue())

    splash.destroy()


class RamanROADegcircCalcMixtureWindow(RamanROADegcircCalcWindow) :
  """Window for exploring Raman/ROA spectra of several molecules.

  The following public methods are explorted :
      clone() -- clone the molecule window
  
  """

  def __init__(self, mainApp, mols,
               composition=None, molecule_labels=None,
               mark_vibs=None, lim_wavenumbers=None,
               startpage=None, render_spectra_labels=True) :
    """Constructor of the class.

    Positional arguments :
    mainApp               -- reference to the main window of PyVib2
    mols                  -- list of molecules to be opened

    Keyword arguments :
    composition           -- composition of the mixture (null-based ndarray)
                             (default None)
                             if None, do not render the Mixture tab
    molecule_labels       -- labels for the molecules (default None)
    mark_vibs             -- list of vibrations to be marked on the spectra
                             (default None)
    startpage             -- start tab to activate
    render_spectra_labels -- whether to render the spectra labels,
                             appearing to the left side of the spectra canvas

    """
    # checking the validity
    if not isinstance(mols, (tuple, list)) :
      raise ConstructorError('Invalid mols argument')

    for mol in mols :
      if mol.raman_roa_tensors is None :
        raise ConstructorError(
          'All molecules must have the Raman/ROA data')

    if composition is not None and \
       ( not isinstance(composition, ndarray) or \
         len(composition) != len(mols) ) :
      raise ConstructorError('Invalid composition array')

    if composition is not None and \
       ( any(0. > composition) or any(1. < composition) ) :
      raise ConstructorError(
        'Composition has to have numbers between 0. and 1. inclusively')

    if molecule_labels is not None and len(molecule_labels) != len(mols) :
      raise ConstructorError('Invalid conformer labels')

    # the only required parameter
    self.__mols        = mols

    # do not show the spectra of the mixture unless
    # the composition is explicitely given
    self.__show_mixture = composition is not None

    # base class
    RamanROADegcircCalcWindow.__init__(self, mainApp, mols[0],
                                       composition=composition,
                                       molecule_labels=molecule_labels,
                                       mark_vibs=mark_vibs,
                                       lim_wavenumbers=lim_wavenumbers,
                                       startpage=startpage,
                                       render_spectra_labels=\
                                       render_spectra_labels)

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    self.wm_title('Calculated Raman/ROA/Degree of circularity ' + \
                  'spectra for several molecules')

    ## top
    # the major types of the spectra
    group_settings = Pmw.Group(self, tag_text='Spectra')
    group_settings.grid(row=0, column=0, columnspan=2,
                        padx=3, pady=3, sticky='we')

    # callback
    change_callback = Command(self.__redraw_all_spectra,
                              raman_limits_auto=True,
                              roa_limits_auto=True)

    # scattering type : 180, 0
    items = resources.STRINGS_SCATTERING_TYPES
    width = max([ len(item) for item in items])
    widget = Pmw.OptionMenu(group_settings.interior(),
                            labelpos='w',
                            label_text='Scattering :',
                            labelmargin=3,
                            menubutton_width=width,
                            items=items,
                            command=change_callback)
    self._varsdict['options_scattering'] = widget
    self._varsdict['options_scattering'].grid(row=0, column=0,
                                              padx=3, pady=3, sticky='w')

    # representation type : fitted or stick
    items = resources.STRINGS_SPECTRA_REPRESENTATION_TYPES
    width = max([ len(item) for item in items ])
    widget  = Pmw.OptionMenu(group_settings.interior(),
                             labelpos='w',
                             label_text='Representation :',
                             labelmargin=3,
                             menubutton_width=width,
                             items=items,
                             command=change_callback)
    self._varsdict['options_representation'] = widget
    self._varsdict['options_representation'].grid(row=0, column=1,
                                                  padx=3, pady=3, sticky='w')
    ## frame above the spectra
    frm_above = Tkinter.Frame(self)
    frm_above.grid(row=1, column=0, padx=3, pady=3, sticky='w')
    
    # button toolbar
    btn_toolbar = self.__constructButtonToolbar(frm_above)
    btn_toolbar.grid(row=0, column=0, padx=3, pady=3, sticky='w')
    
    ### the spectra will be shown in tabs
    self.grid_columnconfigure(0, weight=1)
    self.grid_rowconfigure(2, weight=1)
    
    self._varsdict['notebook'] = Pmw.NoteBook(self)
    self._varsdict['notebook'].grid(row=2, column=0, columnspan=2,
                                    padx=3, pady=3, sticky='news')

    ## message bar at the bottom
    self._varsdict['msgBar'] = Pmw.MessageBar(self, entry_relief='sunken')
    self._varsdict['msgBar'].grid(row=3, column=0, columnspan=2,
                                  padx=3, pady=3, sticky='we')    

    # Mixture tab
    if self.__show_mixture :
      self._varsdict['mixture_tab'] = self._varsdict['notebook'].add('Mixture')
      self.__constructMixtureTab(self._varsdict['mixture_tab'])

    for name, prefix in \
        zip(resources.STRINGS_SPECTRA_NAMES,
            resources.STRINGS_SPECTRA_PREFICES) :
      self._varsdict['%s_tab' % prefix] = self._varsdict['notebook'].add(name)
      self.__constructMultipleSpectraTab(
        self._varsdict['%s_tab' % prefix], prefix)

    # activate the start tab
    startpage = self._smartdict['startpage'] or \
                resources.STRINGS_SPECTRA_NAMES[0]
    if startpage in self._varsdict['notebook'].pagenames() :
      self._varsdict['notebook'].selectpage(startpage)

    # enable the synchronous zoom
    self.__build_sync_zoom_figures(add_mix=False)

    # resize the notebook appropriately
    self._varsdict['notebook'].setnaturalsize()

    ## performing the first rendering
    self.__redraw_all_spectra(show_splash=False)

  def __build_sync_zoom_figures(self, add_mix=True) :
    """Build the list of figure with a synchronized zoom.

    Keyword arguments :
    add_mix  -- if True the mixture spectra should be
                synchronized with the rest (default True)

    """
    # list with the figures to be synchronized
    sync_list = [ self._varsdict['figure_%s' % prefix] \
                  for prefix in resources.STRINGS_SPECTRA_PREFICES ]    
    if add_mix :
      sync_list.append(self._varsdict['figure_mixture'])
    
    n = len(sync_list)
    for i in xrange(n) :
      figs = []
      for j in xrange(n) :
        if j != i :
          figs.append(sync_list[j])

      sync_list[i].settings['sync_zoom_figures'] = figs

  def __constructButtonToolbar(self, parent) :
    """Construct the button toolbar."""
    btn_toolbar = widgets.ButtonToolbar(parent, horizontal=True)
    
    # clone button
    btn_toolbar.add_button(imagename='clone',
                           command=self.clone,
                           helptext='Clone the window.')

    # save spectra
    btn_toolbar.add_button(imagename='save',
                           command=self._save_figure,
                           helptext='Save the figure.')    

    # spectra settings
    btn_toolbar.add_button(imagename='prefs',
                           command=self.__settings,
                           helptext='Setting of the spectra.')

    if self.__show_mixture :
      # diagram with the percentage
      btn_toolbar.add_button(imagename='barchart',
                             command=self.__plot_diagram,
                             helptext='Percentage of the conformers.')

    btn_toolbar.add_separator()

    # correlate the vibrations of the molecules
    btn_toolbar.add_button(
      imagename='correlate',
      command=self.__correlate_vibrations,
      helptext='Correlation the vibrations of the molecules.')

    # adjust the y scale
    btn_toolbar.add_button(imagename='adjust_y',
                           command=self.__adjust_y,
                           helptext='Adjust the y scale of the active figure.')

    # restore the previous zooming region
    btn_toolbar.add_button(
      imagename='undo',
      command=self.__restore_last_zoom,
      helptext='Restore the previous plotting region of the active figure.')

    return btn_toolbar
  
  def __constructMixtureTab(self, parent) :
    """Construct the tab where the spectra of the mixture are shown."""
    parent.grid_columnconfigure(0, weight=1)
    parent.grid_rowconfigure(0, weight=1)
  
    widget = RamanROADegcircCalcMixtureFigure(parent,
                                              self.__mols,
                                              self._smartdict['composition'],
                                              msgBar=self._varsdict['msgBar'],
                                              showvib_callback=self._showvib,
                                              title1='Spectra of the mixture'
                                              )
    self._varsdict['figure_mixture'] = widget
    self._varsdict['figure_mixture'].tk_canvas.get_tk_widget().grid(
      row=0, column=0, padx=3, pady=3, sticky='news')

  def __constructMultipleSpectraTab(self, parent, prefix) :
    """Construct a tab for the spectra of the molecules."""
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    
    # figure
    widget = MultipleSpectraFigure(parent,
                                   self.__mols,
                                   msgBar=self._varsdict['msgBar'],
                                   showvib_callback=self._showvib,
                                   molecule_labels=\
                                   self._smartdict['molecule_labels'])
    self._varsdict['figure_%s' % prefix] = widget
    self._varsdict['figure_%s' % prefix].tk_canvas.get_tk_widget().grid(
      row=0, column=0, padx=3, pady=3, sticky='news')

  def __redraw_all_spectra(self, *dummy, **kw) :
    """Called when the user changes the scattering or the representation type.
    
    Keyword arguments :
      show_splash -- whether to show a splash window (default True)
      
    """
    self.tk.call('update', 'idletasks')

    show_splash = kw.get('show_splash', True)

    if show_splash :
      splash = widgets.SplashScreen(self, 'Redrawing the spectra...')

    # spectra of the mixture
    if self.__show_mixture :
      kw['scattering']     = self._varsdict['options_scattering'].getvalue()
      kw['representation'] = self._varsdict['options_representation'].getvalue()

      self._varsdict['figure_mixture'].plot_spectra(**kw)

      # refresh the values in the settings dialog if it is opened
      if 'dlg_settings_mix' in self._varsdict :
        self._varsdict['dlg_settings_mix'].update_controls(
          self._varsdict['figure_mixture'])

    # spectra of the single conformers
    self.__redraw_conf_spectra(raman_limits_auto=True,
                               roa_limits_auto=True,
                               show_splash=False)
    if show_splash :
      splash.destroy()

  def _showvib(self, info) :
    """Show a vibration in a separate window.

    Override the function of the parent class.

    Positional arguments :
    info -- (molno, p, spectrum_type)
      
    """
    self.tk.call('update', 'idletasks')

    curtab = self._varsdict['notebook'].getcurselection()

    # mixture
    if curtab not in resources.STRINGS_SPECTRA_NAMES :
      molinv = info[2]
      invert_roa = self._varsdict['figure_mixture'].settings['roa_invert']

    # single spectra
    else :
      i = list(resources.STRINGS_SPECTRA_NAMES).index(curtab)
      curprefix = resources.STRINGS_SPECTRA_PREFICES[i]

      if 'roa' == curprefix :
        molinv = 'roa_%s' % \
                 self._varsdict['options_scattering'].getvalue().lower()
      else :
        molinv = curprefix

      invert_roa = self._varsdict['figure_roa'].settings['invert']

    if info is not None and 0 == list(info).count(None) :
      SingleVibrationWindow(self._mainApp,
                            self.__mols[info[0]-1],
                            vib_no=info[1],
                            molecule_name=self.__mols[info[0]-1].name,
                            show_gcm=True,
                            molinv=molinv,
                            invert_roa=invert_roa)

  def __redraw_conf_spectra(self, **kw) :
    """Callback for the spectra settings of the conformers.

    Keyword arguments :
    show_splash -- whether to show a splash window (default True)
    
    """    
    show_splash = kw.get('show_splash', True)

    if show_splash :
      splash = widgets.SplashScreen(self, 'Redrawing the spectra...')
      
    # spectra of the single molecules    
    kw_conf = dict(
      scattering=self._varsdict['options_scattering'].getvalue(),
      representation=self._varsdict['options_representation'].getvalue(),
      mark_vibs=self._smartdict['mark_vibs'],
      render_spectra_labels=self._smartdict['render_spectra_labels'])

    # handling the molecule labels separately
    if 'molecule_labels' in kw :
      kw_conf['molecule_labels'] = kw['molecule_labels']
    else :
      if self._varsdict['figure_raman'].settings['molecule_labels'] is None :
        kw_conf['molecule_labels'] = self._smartdict['molecule_labels']

    # now the class accepts the lim_wavenumbers parameter
    # use it unless the limits are given
    c = 0
    for prefix in resources.STRINGS_SPECTRA_PREFICES :
      if '%s_lim_wavenumbers' % prefix in kw :
        c += 1

    if 0 == c :
      if 0 == self._varsdict.get('count_', 0) :
        for prefix in resources.STRINGS_SPECTRA_PREFICES :
          kw['%s_lim_wavenumbers' % prefix] = \
                                  self._smartdict['lim_wavenumbers']
          self._varsdict['count_'] = 1 + self._varsdict.get('count_', 0)

    # XY_data : where to take ?
    if self.__show_mixture :
      XY_data = self._varsdict['figure_mixture'].XY_data

    else :
      XY_data = self.__get_XY_data(**kw)
    
    for i in xrange(len(resources.STRINGS_SPECTRA_PREFICES)) :
      prefix = resources.STRINGS_SPECTRA_PREFICES[i]
      fig    = self._varsdict['figure_%s' % prefix]

      # extract the keywords for each tab
      for prop in kw.keys() :
        if prop.startswith(prefix) :
          kw_conf[prop[1 + len(prefix):]] = kw[prop]

      kw_conf['label_type']   = i
      kw_conf['make_degcirc'] = 2 == i

      fig.plot_spectra(self._extract_XY(XY_data, 1 + i), **kw_conf)

    # update the setting dialog
    if 'dlg_settings_conf' in self._varsdict :
      self._varsdict['dlg_settings_conf'].update_controls(
        (self._varsdict['figure_raman'],
         self._varsdict['figure_roa'],
         self._varsdict['figure_degcirc']
         ))

    if show_splash :
      splash.destroy()

  def _extract_XY(XY_data, i) :
    """Extract the data for plotting spectra of a molecule.

    Positional arguments :
    XY_data -- [[X1, Y_raman1, Y_roa1, Y_degcirc1], ...]
    i       -- the index of a desired Y data
    
    """
    XY = []
    
    for d in XY_data :
      XY.append([d[0], d[i]])

    return XY

  _extract_XY = staticmethod(_extract_XY)

  def _save_figure(self) :
    """Callback for the save button."""
    fig = self.__get_active_figure()

    # size of the figure
    if not self.__show_mixture :
      if 'dlg_settings_conf' in self._varsdict :
        size = self._varsdict['dlg_settings_conf'].figsize_inches
      else :
        size = None
    else :
      if 'dlg_settings_mix' in self._varsdict :
        size = self._varsdict['dlg_settings_mix'].figsize_inches
      else :
        size = None

    self._save(fig, name=None, size=size)

  def __settings(self) :
    """Show the settings of the spectra."""
    curtab = self._varsdict['notebook'].getcurselection()

    # mixture spectra
    if 'dlg_settings_mix' not in self._varsdict and 'Mixture' == curtab :
      ok_command_mix = Command(self.__redraw_all_spectra)
      
      dlg = dialogs.RamanRoaDegcircCalcSettingsDialog(
          self, ok_command=ok_command_mix)
      self._varsdict['dlg_settings_mix'] = dlg
      self._varsdict['dlg_settings_mix'].configure(
        title='Spectra settings for the mixture')

    # single conformers
    if 'dlg_settings_conf' not in self._varsdict and \
       curtab in resources.STRINGS_SPECTRA_NAMES :
      ok_command_conf = Command(self.__redraw_conf_spectra)
      
      dlg = dialogs.MultipleSpectraSettingsDialog(
          self,
          len(self.__mols),
          ok_command=ok_command_conf,
          add_profile_export=\
          not self.__show_mixture)

      self._varsdict['dlg_settings_conf'] = dlg
      self._varsdict['dlg_settings_conf'].configure(
        title='Spectra settings for the single molecules')
    
    # do not forget to update the controls !
    if 'Mixture' == curtab :
      self._varsdict['dlg_settings_mix'].update_controls(
        self._varsdict['figure_mixture'])
      self._varsdict['dlg_settings_mix'].show()
      
    else :
      self._varsdict['dlg_settings_conf'].update_controls(
        (self._varsdict['figure_raman'],
         self._varsdict['figure_roa'],
         self._varsdict['figure_degcirc']))

      self._varsdict['dlg_settings_conf'].selectpage(
        self._varsdict['notebook'].getcurselection())
      self._varsdict['dlg_settings_conf'].show()

  def __plot_diagram(self) :
    """Plot a bar chart diagram with percentages given by perc."""
    self.tk.call('update', 'idletasks')
    
    # figure with a toplevel
    wnd = Tkinter.Toplevel(self)
    wnd.withdraw()
    wnd.wm_title('Percentage of the conformers')

    fig = PercentageFigure(wnd, 100 * self._smartdict['composition'])
    fig.tk_canvas.get_tk_widget().grid(row=0, column=0, padx=3, pady=3)

    wnd.deiconify()

  def __correlate_vibrations(self) :
    """Correlate the vibrations of the molecules."""
    self.tk.call('update', 'idletasks')

    CorrelateVibrationsWindow(self._mainApp,
                              ref_mol=self.__mols[0], tr_mol=self.__mols[1],
                              molecules=self.__mols,
                              startpage=\
                              self._varsdict['notebook'].getcurselection())

  def __get_active_figure(self) :
    """Return the currently active figure."""
    curtab = self._varsdict['notebook'].getcurselection()

    if 'Mixture' == curtab :
      fig = self._varsdict['figure_mixture']

    else :
      i = list(resources.STRINGS_SPECTRA_NAMES).index(curtab)
      fig = self._varsdict['figure_%s' % resources.STRINGS_SPECTRA_PREFICES[i]]

    return fig

  def __get_XY_data(self, **kw) :
    """Get the data for plotting."""
    # spectra types
    scattering     = RamanROADegcircCalcFigure.get_scattering_as_index(
      self._varsdict['options_scattering'].getvalue())
    representation = BaseSpectrumFigure.get_representation_as_index(
      self._varsdict['options_representation'].getvalue())

    # calculating all invariants
    # making a cache :)
    if 'arr_J_all' not in self._varsdict :
      self._varsdict['arr_J_all'] = [ mol.raman_roa_tensors.J_all(
        units='cross-section') for mol in self.__mols ]

    # XY data for the single molecules
    XY_data = []
    
    # fitted
    if 0 == representation :
      # calculating the fitting interval
      startx = 0.      
      endx   = spectra.X_PEAK_INTERVAL + \
               max(array([ ceil(mol.freqs[-1]) for mol in self.__mols ]))

      X_mix = arange(startx, 1. + endx, 1.)

      # getting the fit keywords
      fit_kw = dict(scattering=scattering,
                    startx=startx,
                    endx=endx)

      # these keywords are present when called from the settings dialog
      if 'N_G' in kw and 'FWHM_is' in kw and 'FWHM_anis' in kw \
         and 'FWHM_inst' in kw :
        fig = self._varsdict[
          'figure_%s' % resources.STRINGS_SPECTRA_PREFICES[0]]
        
        for prop in ('N_G', 'FWHM_is', 'FWHM_anis', 'FWHM_inst') :
          fit_kw[prop] = kw[prop]
      
      for i in xrange(len(self.__mols)) :
        # current conformer
        X, raman_Y, roa_Y, degcirc_Y = spectra.fit_raman_roa(
          self.__mols[i].raman_roa_tensors.freqs,
          self._varsdict['arr_J_all'][i],
          **fit_kw)
        
        # saving
        XY_data.append([X_mix, raman_Y, roa_Y, degcirc_Y])
        
    # stick
    else :
      for i in xrange(len(self.__mols)) :
        mol = self.__mols[i]
        
        # single molecule
        X = mol.freqs[1:]
        raman_Y, roa_Y, degcirc_Y = spectra.stick_raman_roa(
          scattering, self._varsdict['arr_J_all'][i])

        # saving
        XY_data.append([mol.freqs[1:], raman_Y, roa_Y, degcirc_Y])

    return XY_data

  def __adjust_y(self) :
    """Adjust the y scale of the active figure."""
    self.tk.call('update', 'idletasks')
    
    curtab = self._varsdict['notebook'].getcurselection()

    if curtab in resources.STRINGS_SPECTRA_NAMES :
      XY_data = self.__get_XY_data()

      i = list(resources.STRINGS_SPECTRA_NAMES).index(curtab)
      prefix = resources.STRINGS_SPECTRA_PREFICES[i]

      kw = dict(make_degcirc = 2 == i, label_type=i, limits_auto=True)

      fig = self._varsdict['figure_%s' % prefix]
      
      fig.plot_spectra(self._extract_XY(XY_data, 1 + i), **kw)


  def __restore_last_zoom(self) :
    """Restore the last plotting interval."""
    self.__get_active_figure().restore_last_zoom()    

  def clone(self) :
    """Clone the molecule window.

    Overrides the base class method.
    
    """
    self.tk.call('update', 'idletasks')

    splash = widgets.SplashScreen(self, 'Cloning the window...')
    RamanROADegcircCalcMixtureWindow(self._mainApp,
                                     self.__mols,
                                     self._smartdict['composition'],
                                     self._smartdict['molecule_labels'])
    splash.destroy()


class BoltzmannMixtureSpectraWindow(BaseWindow) :
  """Window for plotting spectra of a mixture of molecules.

  No properties are exposed and no public methods are exported.
  
  """

  def __init__(self, mainApp, mols, check_all=False) :
    """Constructor of the class.

    Positional arguments :
    mainApp    -- reference to the main window of PyVib2
    mols       -- list of molecules to be opened

    Keyword arguments :
    check_all  -- whether to check all molecules at startup (default False)
    
    """
    # checking the validity
    if not isinstance(mols, (tuple, list)) :
      raise ConstructorError('Invalid mols argument')

    for mol in mols :
      if mol.raman_roa_tensors is None :
        raise ConstructorError(
          'All molecules must have the Raman/ROA data')

    self.__mols = mols
    
    BaseWindow.__init__(self, mainApp, check_all=check_all)    

  def _init_vars(self) :
    """Initialize variables."""
    # Size of the render widgets (pixel).
    self._varsdict['SIZE_RENDERWIDGET'] = 150
  
    # Size of the scrolled area.
    self._varsdict['SIZE_SCROLLEDAREA'] = (750, 500)

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    self.wm_title('Select molecules')
    
    # wizard should be expandable
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=1)
    
    self._varsdict['wizard'] = widgets.WizardWidget(
      self,
      back_command=self.__back_command,
      next_command=self.__next_command)
    self._varsdict['wizard'].grid(row=0, column=0,
                                  padx=3, pady=3, sticky='news')

    # select molecules
    # show all molecules which have the ROA data
    self._varsdict['select_tab'] = self._varsdict['wizard'].notebook.add(
      'selectconf')
    self.__constructFirstTab(self._varsdict['select_tab'])

    if self._smartdict['check_all'] :
      self.__select_all_molecules(True)

    self._varsdict['wizard'].notebook.setnaturalsize()

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    pass

  def __constructFirstTab(self, parent) :
    """Construct the first tab with the list of all molecules."""
    parent.grid_rowconfigure(2, weight=1)
    parent.grid_columnconfigure(0, weight=1)

    # help message
    help_widget = widgets.InfoWidget(
      parent,
      text='Select at least two molecules to proceed.',
      height=1)
    help_widget.grid(row=0, column=0, padx=3, pady=3, sticky='we')

    # button toolbar
    btn_toolbar = self.__constructButtonToolbar(parent)
    btn_toolbar.grid(row=1, column=0, padx=3, pady=3, sticky='w')
    
    # scrolled frame which holds whole the stuff
    scrolled_frm = Pmw.ScrolledFrame(
      parent,
      usehullsize=True,
      hull_width=self._varsdict['SIZE_SCROLLEDAREA'][0],
      hull_height=self._varsdict['SIZE_SCROLLEDAREA'][1],
      horizflex='expand',
      vertflex='fixed')
    scrolled_frm.grid(row=2, column=0, padx=3, pady=3, sticky='news')

    # placing N molecules pro line
    N = 3
    self._varsdict['mol_frms'] = []
    
    for no in xrange(len(self.__mols)) :
      mol_frm = self.__create_mol_frame(scrolled_frm.interior(),
                                        self.__mols[no])

      # i - row, j - column
      i = int(no / N)
      j = no - N * i

      scrolled_frm.interior().grid_rowconfigure(i, weight=1)
      scrolled_frm.interior().grid_columnconfigure(j, weight=1)

      mol_frm.grid(row=i, column=j, padx=3, pady=3, sticky='wn')

  def __constructSecondTab(self, parent) :
    """Construct the second tab."""
    parent.grid_rowconfigure(2, weight=1)
    parent.grid_columnconfigure(0, weight=1)

    ## help message
    help_widget = widgets.InfoWidget(
      parent,
      text='Specify the energies of the molecules.',
      height=1)
    help_widget.grid(row=0, column=0, padx=3, pady=3, sticky='we')

    ## control panel
    control_frm = Tkinter.Frame(parent)
    control_frm.grid(row=1, column=0, padx=3, pady=3, sticky='we')

    column = 0
    # button toolbar from the left
    btn_toolbar = self.__constructButtonToolbar2(control_frm)
    btn_toolbar.grid(row=0, column=column, padx=3, pady=3, sticky='w')
    column += 1

    #...
    control_frm.grid_rowconfigure(0, weight=1)
    control_frm.grid_columnconfigure(column, weight=1)

    # option menu with the energy units
    # take the previous value if possible
    items = (resources.STRING_UNIT_ENERGY_HARTREE,
             resources.STRING_UNIT_ENERGY_KJMOL)
    widget = Pmw.OptionMenu(control_frm,
                            items=items,
                            labelpos='w',
                            label_text='Energy units :',
                            menubutton_width=7,
                            command=Command(self.__update_percentage))
    self._varsdict['option_energy'] = widget
    self._varsdict['option_energy'].grid(row=0, column=column,
                                         padx=3, pady=3, sticky='e')
    column += 1

    ##
    scrolled_frm = Pmw.ScrolledFrame(
      parent,
      usehullsize=True,
      hull_width=self._varsdict['SIZE_SCROLLEDAREA'][0],
      hull_height=self._varsdict['SIZE_SCROLLEDAREA'][1],
      horizflex='fixed',
      vertflex='fixed')
    scrolled_frm.grid(row=2, column=0, padx=3, pady=3, sticky='news')

    ## create the cache if possible
    if 'conformer_data' in self._varsdict :
      cache = {}
      for d in self._varsdict['conformer_data'] :
        try :
          val = d[1].get()
        except :
          val = 0.
          
        cache[d[0]] = val

      del self._varsdict['conformer_data']

      if 'var_percentages' in self._varsdict :
        del self._varsdict['var_percentages']
    else :
      cache = None

    # adding the molecule checked at the first tab
    # saving the original numbers
    self._varsdict['frame_conformers'] = scrolled_frm.interior()

    sel_indices = self.__get_selected_indices()
    
    for i in xrange(len(sel_indices)) :
      frm = self.__create_conf_frame(scrolled_frm.interior(),
                                     sel_indices[i],
                                     cache=cache)
      frm.grid(row=i, column=0, padx=3, pady=3, sticky='w')
      frm.index_orig = i

    ## setting the energy units
    if 'energy_units' in self._varsdict and \
       self._varsdict['energy_units'] is not None :
      self._varsdict['option_energy'].invoke(self._varsdict['energy_units'])

  def __constructButtonToolbar(self, parent) :
    """Construct the toolbar for the first tab."""
    btn_toolbar = widgets.ButtonToolbar(parent, horizontal=True)
    
    # check all
    btn_toolbar.add_button(imagename='select_all',
                           command=Command(self.__select_all_molecules, True),
                           helptext='Select all molecules.')

    # uncheck all
    btn_toolbar.add_button(imagename='deselect_all',
                           command=Command(self.__select_all_molecules, False),
                           helptext='Deselect all molecules.')
    return btn_toolbar

  def __constructButtonToolbar2(self, parent) :
    """Construct the toolbar for the second tab."""
    btn_toolbar = widgets.ButtonToolbar(parent, horizontal=True)
    
    # save energies
    btn_toolbar.add_button(
      imagename='save',
      command=self.__save_energies,
      helptext='Save the energies of the selected conformers to a file.')

    # load energies
    btn_toolbar.add_button(
      imagename='open_file',
      command=self.__load_energies,
      helptext='Load the energies of the conformers from a file.')

    # separator
    btn_toolbar.add_separator()
    
    # diagram with the percentages
    widget = btn_toolbar.add_button(
      imagename='barchart',
      command=self.__plot_diagram,
      helptext='Show the percentages of the conformers as a diagram.')

    self._varsdict['btn_barchart'] = widget

    # sort by percentage in ascending order
    widget = btn_toolbar.add_button(
      imagename='sort_asc',
      command=Command(self.__sort_energies, True),
      helptext='Sort the conformers by percentage in ascending order.')
    self._varsdict['btn_sortasc'] = widget

    # sort by percentage in descending order
    widget = btn_toolbar.add_button(
      imagename='sort_desc',
      command=Command(self.__sort_energies, False),
      helptext='Sort the conformers by percentage in descending order.')
    self._varsdict['btn_sortdesc'] = widget

    # plot spectra
    widget = btn_toolbar.add_button(
      imagename='spectrum',
      command=self.__plot_spectra,
      helptext='Plot the spectra of the mixture of the conformers.')
    self._varsdict['btn_spectra'] = widget    

    return btn_toolbar
      
  def __create_mol_frame(self, master, mol) :
    """Create a frame for a molecule."""
    self.tk.call('update', 'idletasks')
    
    frm = Tkinter.Frame(master)

    # render widget which has a fixed size and cannot expand
    renderWidget = widgets.MoleculeRenderWidget(
      frm,
      molecule=mol,
      width=self._varsdict['SIZE_RENDERWIDGET'],
      height=self._varsdict['SIZE_RENDERWIDGET'],
      resolution=self._mainApp.settings['resolution'],
      molecule_mode=resources.NUM_MODE_STICK,
      rounded_bond=True,
      hydrogen_bond=True,
      atom_labels=False,
      background='#FFFFFF')
    renderWidget.grid(row=0, column=0, padx=3, pady=3, sticky='w')

    # saving the reference
    if 'renderwidgets' not in self._varsdict :
      self._varsdict['renderwidgets'] = []

    self._varsdict['renderwidgets'].append(renderWidget)

    # checkbox with the name of the molecule
    # saving the variables
    if 'var_checkboxes' not in self._varsdict :
      self._varsdict['var_checkboxes'] = []

    var = Tkinter.IntVar()
    self._varsdict['var_checkboxes'].append(var)
    
    check_name = Tkinter.Checkbutton(frm,
                                     text=mol.name,
                                     font=resources.get_font_molecules(self),
                                     variable=var,
                                     command=self.__updateGUI)
    check_name.grid(row=1, column=0, padx=3, pady=3, sticky='w')

    return frm

  def __create_conf_frame(self, master, index, cache=None) :
    """Create a frame with a thumbnail.

    Positional arguments :
    master -- parent widget
    index  -- null-based index of the molecule in the original
              list of the molecules.
    cache  -- dictionary with the energies of the conformers : index -> E
    
    """
    self.tk.call('update', 'idletasks')
    
    frm = Tkinter.Frame(master, borderwidth=2, relief='raised')

    mol = self.__mols[index]

    # render widget instead of a thumbnail
    renderWidget = widgets.MoleculeRenderWidget(
      frm,
      molecule=mol,
      width=self._varsdict['SIZE_RENDERWIDGET'],
      height=self._varsdict['SIZE_RENDERWIDGET'],
      resolution=self._mainApp.settings['resolution'],
      molecule_mode=resources.NUM_MODE_STICK,
      rounded_bond=True,
      hydrogen_bond=True,
      atom_labels=False,
      background='#FFFFFF',
      camera=self._varsdict['renderwidgets'][index].camera)
    renderWidget.grid(row=0, column=0, rowspan=4, padx=3, pady=3, sticky='w')

    ## number of the conformer and its energy
    # conformer_data is a list of [index, var_energy]
    if 'conformer_data' not in self._varsdict :
      self._varsdict['conformer_data'] = []

    # first row - number of the conformer
    number = 1 + len(self._varsdict['conformer_data'])
    
    var_number = Tkinter.IntVar()
    var_number.set(number)
    
    entryfield_number = Pmw.EntryField(frm,
                                       label_text='Number : ',
                                       labelpos='w',
                                       entry_textvariable=var_number,
                                       entry_width=30,
                                       entry_state='readonly')
    entryfield_number.grid(row=0, column=1, padx=5, pady=3, sticky='we')

    # second row - the name of the molecule
    var_name = Tkinter.StringVar()
    var_name.set(mol.name)
    
    entryfield_name = Pmw.EntryField(frm,
                                     label_text='Name : ',
                                     labelpos='w',
                                     entry_textvariable=var_name,
                                     entry_font=\
                                     resources.get_font_molecules(self))
    entryfield_name.grid(row=1, column=1, padx=5, pady=3, sticky='we')

    # third row - energy
    # taking the value of the energy from the cache
    var_energy = Tkinter.DoubleVar()
    if cache is not None and index in cache :
      var_energy.set(cache[index])

    entryfield_energy = Pmw.EntryField(
      frm,
      label_text='Gibbs energy : ',
      labelpos='w',
      entry_textvariable=var_energy,
      validate = {'validator' : 'real'},
      modifiedcommand=self.__update_percentage)
    entryfield_energy.grid(row=2, column=1, padx=5, pady=3, sticky='we')

    # percentage
    if 'var_percentages' not in self._varsdict :
      self._varsdict['var_percentages'] = []

    var_percentage = Tkinter.StringVar()
    self._varsdict['var_percentages'].append(var_percentage)

    entryfield_percentage = Pmw.EntryField(frm,
                                           label_text='Percentage : ',
                                           labelpos='w',
                                           entry_textvariable=var_percentage,
                                           entry_state='readonly',
                                           entry_foreground='#008000',
                                           entry_font=('Arial', 12, 'bold'))
    entryfield_percentage.grid(row=3, column=1, padx=5, pady=3, sticky='we')

    # align the labels
    Pmw.alignlabels((entryfield_number, entryfield_name,
                     entryfield_energy, entryfield_percentage))

    # save it
    self._varsdict['conformer_data'].append(
      [index, var_energy, var_number, var_name])

    ## buttons up/down to move the frame
    btn_up = Tkinter.Button(frm,
                            image=getimage('up'),
                            command=Command(self.__moveto, frm, True))
    btn_up.grid(row=1, column=2, padx=3, pady=3, sticky='e')
    self._balloon.bind(btn_up, 'Move the current conformer up in the list.')

    btn_down = Tkinter.Button(frm,
                              image=getimage('down'),
                              command=Command(self.__moveto, frm, False))
    btn_down.grid(row=2, column=2, padx=3, pady=3, sticky='e')
    self._balloon.bind(btn_down,
                       'Move the current conformer down in the list.')
    return frm

  def __get_selected_indices(self) :
    """Get a list of the indices of selected molecules."""
    sel = []
    for i in xrange(len(self._varsdict['var_checkboxes'])) :
      
      if self._varsdict['var_checkboxes'][i].get() :
        sel.append(i)

    return sel

  def __get_conf_indices(self) :
    """Get the indices of the molecules within the list
    of the selected molecules.

    Since the user can renumber the conformers one needs such a function.
    
    """
    indices     = self.__get_selected_indices()
    frm_indices = self.__get_frm_indices()

    return array(indices, 'l')[frm_indices].tolist()

  def __get_frm_indices(self) :
    """Get a list with the original frame indices.

    Example                : the user has selected 3 conformers.
    Original frame indices : 0, 1, 2
    Mixed indices          : 1, 2, 0
    
    """
    self.tk.call('update', 'idletasks')
    
    frm_indices = [ ]
    for i in xrange(len(self.__get_selected_indices())) :
      frm_indices.append(
        self._varsdict['frame_conformers'].\
        grid_slaves(row=i, column=0)[0].index_orig)

    return frm_indices
                                       
  def __back_command(self) :
    """Callback for the Back button."""
    self.tk.call('update', 'idletasks')
    
    # go from the second tab to the first one
    if 'energiesconf' == self._varsdict['wizard'].notebook.getcurselection() :
      self._varsdict['wizard'].notebook.selectpage('selectconf')

    self.__updateGUI()

  def __next_command(self) :
    """Callback for the Next button."""
    self.tk.call('update', 'idletasks')
    
    notebook = self._varsdict['wizard'].notebook
    
    # create the second tab and make it visible
    # delete it if already exists
    if 'selectconf' == notebook.getcurselection() :
      
      if 'energiesconf' in notebook.pagenames() :
        self._varsdict['energy_units'] = \
                        self._varsdict['option_energy'].getvalue()
        notebook.delete('energiesconf')
      else :
        self._varsdict['energy_units'] = None

      self._varsdict['energies_tab'] = notebook.add('energiesconf')
      self.__constructSecondTab(self._varsdict['energies_tab'])
      
      notebook.selectpage('energiesconf')
      self.__update_percentage()

    self.__updateGUI()

  def __moveto(self, frm, direction) :
    """Move a frame i in a given direction.

    Positional arguments :
    frm       -- the frame
    direction -- True for up, False for down
    
    """
    self.tk.call('update', 'idletasks')
    
    cur_i = int(frm.grid_info()['row'])
    conf_indices = self.__get_selected_indices()

    # cannot move the topmost frame up
    # and the bottommost down
    if (0 == cur_i and direction) or \
       (len(conf_indices) == 1 + cur_i and not direction) :
      return

    kw = {'column' : 0, 'padx' : 3, 'pady' : 3, 'sticky' : 'w'}

    # move up
    if direction :
      frm_prev = self._varsdict['frame_conformers'].\
                 grid_slaves(cur_i - 1, column=0)[0]
      frm_prev.grid(row=cur_i, **kw)

      frm.grid(row=cur_i - 1, **kw)

      # renumbering
      self.__renumber_conf_frame(frm_prev, 1 + cur_i)
      self.__renumber_conf_frame(frm, cur_i)

    # move down
    else :
      frm_next = self._varsdict['frame_conformers'].\
                 grid_slaves(cur_i + 1, column=0)[0]
      frm_next.grid(row=cur_i, **kw)

      frm.grid(row=cur_i + 1, **kw)

      # renumbering
      self.__renumber_conf_frame(frm_next, 1 + cur_i)
      self.__renumber_conf_frame(frm, 2 + cur_i)

  def __renumber_conf_frame(self, frm, number) :
    """Set a new number to the conformer frame."""
    self._varsdict['conformer_data'][frm.index_orig][2].set(number)

  def __updateGUI(self) :
    """Enable/disable the back and next buttons."""
    notebook  = self._varsdict['wizard'].notebook
    buttonbox = self._varsdict['wizard'].buttonbox

    # back button
    state = 'normal'
    if 'selectconf' == notebook.getcurselection() :
      state = 'disabled'

    buttonbox.button(0).configure(state=state)

    # next button
    state = 'normal'
    if 'energiesconf' == notebook.getcurselection() :
      state = 'disabled'
    else :
      if 2 > len(self.__get_selected_indices()) :
        state = 'disabled'

    buttonbox.button(1).configure(state=state)

  def __update_percentage(self, *dummy) :
    """Recalculate the percentages of the conformers."""
    try :
      perc = self.__calc_percentage()
      frm_indices = self.__get_frm_indices()

      for i in xrange(len(perc)) :
        self._varsdict['var_percentages'][frm_indices[i]].set(
          '%.2f' % perc[i])

      state = 'normal'
    except :
      for var in self._varsdict['var_percentages'] :
        var.set('---')

      state = 'disabled'
      
    # block/unblock the buttons which depend on the percentage
    for id_ in ('barchart', 'sortasc', 'sortdesc', 'spectra') :
      self._varsdict['btn_%s' % id_].configure(state=state)

  def __calc_percentage(self) :
    """Calculate the percentage of conformers in %.

    An exception can be raised.
    
    """
    energy_units = self._varsdict['option_energy'].index(
      self._varsdict['option_energy'].getvalue())

    energies = []
    for i in self.__get_frm_indices() :
      d = self._varsdict['conformer_data'][i]
      energies.append(float(d[1].get()))
    
    return 100. * boltzmann_distr(energies, energy_units)

  def __plot_diagram(self) :
    """Plot a bar chart diagram with percentages given by perc."""
    self.tk.call('update', 'idletasks')
    
    try :      
      Y = self.__calc_percentage()
    except :
      pass

    else :
      ## go
      # figure with a toplevel
      wnd = Tkinter.Toplevel(self)
      wnd.withdraw()
      wnd.wm_title('Percentage of the conformers')

      fig = PercentageFigure(wnd, Y)
      fig.tk_canvas.get_tk_widget().grid(row=0, column=0, padx=3, pady=3)

      wnd.deiconify()

  def __plot_spectra(self) :
    """Plot the spectra for the conformers."""
    try :
      composition = 0.01 * self.__calc_percentage()
    except :
      pass
    else :
      # list of the molecule and its labels
      mols  = [ self.__mols[index] for index in self.__get_conf_indices() ]
      molecule_labels = []

      for i in self.__get_frm_indices() :
        d = self._varsdict['conformer_data'][i]
        molecule_labels.append(d[-1].get())

      self.tk.call('update', 'idletasks')

      splash_text = 'Calculating the Raman/ROA invariants' + \
                    ' of the %d selected molecules...' % len(mols)
      splash = widgets.SplashScreen(self.master, splash_text)
      
      RamanROADegcircCalcMixtureWindow(self._mainApp, mols,
                                       composition, molecule_labels,
                                       startpage='Mixture')
      #wnd = RamanROADegcircCalcMixtureWindow(self._mainApp, mols,
      #                                       None, molecule_labels)

      splash.destroy()      
      
  def __sort_energies(self, ascending=True) :
    """Sort the molecules by the energy in a specified order."""
    self.tk.call('update', 'idletasks')

    try :
      perc = self.__calc_percentage()
    except :
      pass
    else :
      N    = len(self.__get_selected_indices())      
      if not ascending :
        perc *= -1.
      
      new_indices = perc.argsort()

      # old list of frames
      frms = [ self._varsdict['frame_conformers'].\
               grid_slaves(row=i, column=0)[0] for i in xrange(N) ]

      kw = {'column' : 0, 'padx' : 3, 'pady' : 3, 'sticky' : 'w'}

      for i in self.__get_frm_indices() :
        new_i = new_indices[i]

        frms[new_i].grid(row=i, **kw)

        # changing also the number
        self.__renumber_conf_frame(frms[new_i], 1 + i)

  def __save_energies(self) :
    """Save the energies to a file so that it could be loaded later."""
    # do nothing if energies are not given
    try :
      self.__calc_percentage()
    except :
      pass
    else :
      filename = tkFileDialog.SaveAs(parent=self._varsdict['energies_tab'],
                                     initialdir=self._mainApp.lastdir).show()
      if not filename :
        return
      try :
        # saving -> name : energy
        f_ = open(filename, 'w+')

        # finding the longest name to format it pretty :)
        len_names = [ len(d[3].get()) for d \
                      in self._varsdict['conformer_data'] ]

        format_line = '%%-%ds    %%13.8f\n' % max(len_names)

        for i in self.__get_frm_indices() :
          d = self._varsdict['conformer_data'][i]
          f_.write(format_line % (d[3].get(), d[1].get()))

        f_.close()
      except :
        widgets.show_exception(sys.exc_info())
    
  def __load_energies(self) :
    """Load the energies from a file.

    Names must be exactly the same (register does not matter).
    
    """
    filename = tkFileDialog.Open(parent=self._varsdict['energies_tab'],
                                 initialdir=self._mainApp.lastdir).show()

    if not filename :
      return

    try :
      ## reading...
      f_ = open(filename, 'r')
      
      names    = []
      energies = []
      for line in f_.readlines() :
        vals = line.strip().split()

        if 2 != len(vals) :
          raise ParseError(
            filename,
            'Each line must have exactly 2 fields : name & E.')

        # reading the energy value
        try :
          E = float(vals[1])
        except ValueError :
          raise ParseError(
            filename,
            r'Invalid energy in the line "%s".' % line.strip())
        else :
          names.append(vals[0].lower())
          energies.append(E)

      f_.close()

      ## trying to apply
      for i in self.__get_frm_indices() :
        d = self._varsdict['conformer_data'][i]

        if 0 != names.count(d[3].get().lower()) :
          index = names.index(d[3].get().lower())
          d[1].set(energies[index])

      self.__update_percentage()
    except :
      widgets.show_exception(sys.exc_info())

  def __select_all_molecules(self, sel) :
    """Check / uncheck all molecules on the first tab."""
    for var in self._varsdict['var_checkboxes'] :
      var.set(sel)

    self.__updateGUI()


class IRVCDCalcWindow(RamanROADegcircCalcWindow) :
  """Window for exploring IR/VCD spectra.

  The following public methods are explorted :
      clone() -- clone the molecule window
  
  """

  def __init__(self, mainApp, mol) :
    """Constructor of the class.

    Positional arguments :
    mainApp  -- reference to the main window of PyVib2
    mol      -- molecule

    """
    if not isinstance(mol, molecule.Molecule) :
      raise ConstructorError('Invalid mol argument')

    # raise an exception if the molecule does not have the IR/VCD data.
    if not hasattr(mol, 'ir_vcd_tensors') or mol.ir_vcd_tensors is None :
      raise ConstructorError('Molecule does not have the IR/VCD data')
    
    RamanROADegcircCalcWindow.__init__(self, mainApp, mol)

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    self.wm_title(r'Calculated IR/VCD spectra of "%s"' % self._mol.name)

    ## top - the most important spectra
    group_settings = Pmw.Group(self, tag_text='Spectra')
    group_settings.grid(row=0, column=0, columnspan=2,
                        padx=3, pady=3, sticky='we')

    # representation type : fitted or stick
    items = resources.STRINGS_SPECTRA_REPRESENTATION_TYPES
    width = max([ len(item) for item in items ])
    widget  = Pmw.OptionMenu(group_settings.interior(),
                             labelpos='w',
                             label_text='Representation :',
                             labelmargin=3,
                             menubutton_width=width,
                             items=items,
                             command=Command(self.__redraw_figure))
    self._varsdict['options_representation'] = widget
    self._varsdict['options_representation'].grid(row=0, column=0,
                                                  padx=3, pady=3, sticky='w')

    ## message bar at the bottom
    self._varsdict['msgBar'] = Pmw.MessageBar(self, entry_relief='sunken')
    self._varsdict['msgBar'].grid(row=2, column=0, columnspan=2,
                                  padx=3, pady=3, sticky='we')    
    ## plotting area
    self.grid_columnconfigure(0, weight=1)
    self.grid_rowconfigure(1, weight=1)
    
    self._varsdict['figure'] = IRVCDCalcFigure(self, self._mol,
                                               showvib_callback=self._showvib,
                                               msgBar=self._varsdict['msgBar'],
                                               title1=self._mol.name)
                                                         
    self._varsdict['figure'].tk_canvas.get_tk_widget().grid(row=1, column=0,
                                                            padx=3, pady=3,
                                                            sticky='news')
    ## button toolbar to the right of the plot
    btn_toolbar = self.__constructButtonToolbar(self)
    btn_toolbar.grid(row=1, column=1, padx=3, pady=10, sticky='n')

    ## first rendering
    self.__redraw_figure()

  def __redraw_figure(self, *dummy) :
    """Called by changing scattering or the representation type."""
    self.tk.call('update', 'idletasks')
    
    # setting the busy cursor
    self._varsdict['figure'].tk_canvas.get_tk_widget().configure(cursor='watch')

    # recalculate the limits since they are rather different
    # for the stick and fitted representations
    self._varsdict['figure'].plot_spectra(
      representation=self._varsdict['options_representation'].getvalue(),
      ir_limits_auto=True,
      vcd_limits_auto=True,
      g_limits_auto=True,
      g_ticks_auto=False,
      g_ticks_number=3)
    
    # refresh the values in the settings dialog if it is opened
    if 'dlg_settings' in self._varsdict :
      self._varsdict['dlg_settings'].update_controls(self._varsdict['figure'])
  
    # restoring the normal cursor
    self._varsdict['figure'].tk_canvas.get_tk_widget().configure(cursor='')

  def __constructButtonToolbar(self, parent) :
    """Construct the button toolbar and return it."""
    btn_toolbar = widgets.ButtonToolbar(parent, horizontal=False)

    # clone button
    btn_toolbar.add_button(imagename='clone',
                           command=self.clone,
                           helptext='Clone the window.')
    
    # save spectra
    btn_toolbar.add_button(
      imagename='save',
      command=self._save_figure,
      helptext='Export the spectrum in PNG, ' + \
      'EPS and PDF (requires ps2pdf) formats.')

    # spectra settings
    btn_toolbar.add_button(imagename='prefs',
                           command=self.__settings,
                           helptext='Settings of the spectra.')

    btn_toolbar.add_separator()

    # restore the previous zooming region
    btn_toolbar.add_button(
      imagename='undo',
      command=Command(self._varsdict['figure'].restore_last_zoom),
      helptext='Restore the previous plotting region.')

    return btn_toolbar

  def __settings(self) :
    """Show the settings of the spectra."""
    if 'dlg_settings' not in self._varsdict :
      ok_command = Command(self._varsdict['figure'].plot_spectra)
      self._varsdict['dlg_settings'] = \
        dialogs.IRVCDCalcSettingsDialog(self, ok_command=ok_command)
      self._varsdict['dlg_settings'].configure(
        title=r'Spectra settings for "%s"' % self._mol.name)

    # do not forget to update the controls !
    self._varsdict['dlg_settings'].update_controls(self._varsdict['figure'])
    self._varsdict['dlg_settings'].show()

  def clone(self) :
    """Clone the molecule window.

    Overrides the base class method.
    
    """
    self.tk.call('update', 'idletasks')

    splash = widgets.SplashScreen(self, 'Cloning the window...')
    
    IRVCDCalcWindow(self._mainApp, self._mol)

    splash.destroy()


class ImportExpSpectraWindow(BaseWindow) :
  """Window for importing experimetnal spectra.

  """

  def __init__(self, mainApp) :
    """Constructor of the class.

    Positional arguments :
    mainApp  -- reference to the main window of PyVib2

    """
    BaseWindow.__init__(self, mainApp)

  def _init_vars(self) :
    """Initialize variables."""
    self._varsdict['frames'] = []
    self._varsdict['vars_checked'] = []
    self._varsdict['vars_filename'] = []
    self._varsdict['vars_laser_power'] = []
    self._varsdict['vars_exposure_time'] = []
    self._varsdict['optmenus_datatype'] = []
    self._varsdict['optmenus_scattering'] = []
    
    self._varsdict['spectratypes'] = (
        (resources.STRING_FILETYPE_ALLFILES_DESCRIPTION, '*'),
        (resources.STRING_FILETYPE_TXTFILE_DESCRIPTION,  '*.txt'),
        (resources.STRING_FILETYPE_PLTFILE_DESCRIPTION,  '*.plt'))

  def _constructGUI(self) :
    """Construct the GUI."""
    self.wm_title('Import experimental spectra @ %s' % \
                  strftime(resources.STRING_FORMAT_TIME, localtime()))

    ## topmost line : button toolbar + compound name
    # button toolbar
    btn_toolbar = self.__constructButtonToolbar(self)
    btn_toolbar.grid(row=0, column=0, sticky='w', padx=3, pady=3)

    # compound name (pressing enter plots the spectra)
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(1, weight=1)
    
    var = Tkinter.StringVar()
    var.set('unknown')
    self._varsdict['var_compound_name'] = var
    
    entry_name = Pmw.EntryField(self,
                                labelpos='w',
                                label_text='Compound name ',
                                entry_textvariable=var,
                                command=self.__plot)
    entry_name.grid(row=0, column=1, sticky='ew', padx=5, pady=3)

    # scrolled frame that will contain all the spectra
    self.grid_rowconfigure(1, weight=1)
    self.grid_columnconfigure(0, weight=1)
        
    scrolled_frm = Pmw.ScrolledFrame(self,
                                     usehullsize=True,
                                     hull_width=800,
                                     hull_height=300,
                                     horizflex='expand',
                                     vertflex='fixed')
    scrolled_frm.grid(row=1, column=0, columnspan=2,
                      padx=3, pady=3, sticky='news')
    self._varsdict['central_frame'] = scrolled_frm

    # update the GUI for the first time
    self.__updateGUI()

  def __constructButtonToolbar(self, parent) :
    """Construct the button toolbar and return it."""
    btn_toolbar = widgets.ButtonToolbar(parent, horizontal=True)

    # add a spectrum
    btn_toolbar.add_button(imagename='add',
                           command=self.__add_spectrum,
                           helptext='Add an experimental spectrum.')
    
    # check all
    btn = btn_toolbar.add_button(imagename='select_all',
                                 command=Command(self.__select_all, True),
                                 helptext='Select all spectra.')
    self._varsdict['btn_select_all'] = btn
  
    # uncheck all
    btn = btn_toolbar.add_button(imagename='deselect_all',
                                 command=Command(self.__select_all, False),
                                 helptext='Deselect all spectra.')
    self._varsdict['btn_deselect_all'] = btn

    # separator
    btn_toolbar.add_separator()

    # remove selected spectra
    btn = btn_toolbar.add_button(imagename='remove',
                                 command=self.__remove_selected,
                                 helptext='Remove selected spectra.')
    self._varsdict['btn_remove_selected'] = btn

    # remove all spectra
    btn = btn_toolbar.add_button(imagename='remove_all',
                                 command=self.__remove_all,
                                 helptext='Remove all spectra.')
    self._varsdict['btn_remove_all'] = btn

    # separator
    btn_toolbar.add_separator()    

    # plot spectra
    btn = btn_toolbar.add_button(imagename='spectrum',
                                 command=self.__plot,
                                 helptext='Plot selected spectra.')
    self._varsdict['btn_plot'] = btn
    
    return btn_toolbar

  def __add_spectrum(self) :
    """Add an experimental spectrum."""
    # taking the last values of the laser power and exposure time be default
    if 0 != len(self._varsdict['frames']) :
      try :
        laser_power   = self._varsdict['vars_laser_power'][-1].get()
      except ValueError :
        laser_power   = None

      try :
        exposure_time = self._varsdict['vars_exposure_time'][-1].get()
      except ValueError :
        exposure_time = None

      scattering = self._varsdict['optmenus_scattering'][-1].getvalue()
        
    else :
      laser_power   = None
      exposure_time = None
      datatype      = None
      scattering    = None
  
    self.__add_frame(laser_power=laser_power,
                     exposure_time=exposure_time,
                     scattering=scattering)
    
    self.__updateGUI()
    
  def __select_all(self, check=True) :
    """Check / uncheck all spectra."""
    for var in self._varsdict['vars_checked'] :
      var.set(check and 1 or 0)

    self.__updateGUI()

  def __remove_selected(self) :
    """Remove selected spectra."""
    to_delete = self.__get_checked_indices()

    # removing from GUI
    for i in xrange(len(self._varsdict['frames'])) :
      if i in to_delete :
        self._varsdict['frames'][i].grid_forget()

    # removing from the lists
    for key in ('frames', 'vars_checked', 'vars_filename',
                'vars_laser_power', 'vars_exposure_time',
                'optmenus_datatype', 'optmenus_scattering') :        
      misc.remove_indices_from_list(self._varsdict[key], to_delete)

    self.__updateGUI()

  def __remove_all(self) :
    """Remove all spectra."""
    for frm in self._varsdict['frames'] :
      frm.grid_remove()

    # clean all the lists
    for key in ('frames', 'vars_checked', 'vars_filename',
                'vars_laser_power', 'vars_exposure_time',
                'optmenus_datatype', 'optmenus_scattering') :
      del self._varsdict[key][:]
    
    self.__updateGUI()

  def __plot(self) :
    """Plot selected spectra."""
    # proceed only if the button is active
    if self._varsdict['btn_plot'].cget('state') not in ('active', 'normal') :
      return
    
    # validate the data :
    checked = self.__get_checked_indices()
    
    try :
      scattering = self._varsdict['optmenus_scattering'][checked[0]].getvalue()

      # 1) only spectra with the same scattering
      for i in checked[1:] :
        if self._varsdict['optmenus_scattering'][i].getvalue() != scattering :
          raise DataInconsistencyError(
            'All the spectra must have the same scattering')

      # 2) only one spectrum of degree of circularity
      ndegcirc = 0
      for i in checked :
        if self._varsdict['optmenus_datatype'][i].getvalue() == \
           resources.STRINGS_EXPSPECTRA_TYPES[1] :
          ndegcirc += 1

      if 2 <= ndegcirc :
        raise DataInconsistencyError(
          'Only one degree of circularity spectrum allowed')
    
    except DataInconsistencyError, ex :
      dlg = Pmw.MessageDialog(title='The spectra cannot be plotted',
                              message_text=str(ex),
                              iconpos='w',
                              icon_bitmap='error')
      dlg.withdraw()
      Pmw.setgeometryanddeiconify(dlg, dlg._centreonscreen())
      return
    
    # try to parse the checked files
    try :
      expdata = []
      for i in checked :
        expdata.append(
          spectra.ExpRamanROAData(
            self._varsdict['vars_filename'][i].get(),
            self._varsdict['vars_laser_power'][i].get(),
            self._varsdict['vars_exposure_time'][i].get(),
            self._varsdict['optmenus_datatype'][i].getvalue(),
            self._varsdict['optmenus_scattering'][i].getvalue())
          )
        
    except :
      widgets.show_exception(sys.exc_info())
      
    else :
      self.tk.call('update', 'idletasks')
      splash = widgets.SplashScreen(self, 'Plotting experimental spectra...')
    
      RamanROADegcircExpWindow(
        self._mainApp, expdata,
        compound_name=self._varsdict['var_compound_name'].get())

      splash.destroy()

  def __add_frame(self, laser_power=None, exposure_time=None,
                  datatype=None, scattering=None) :
    """Add an empty frame for a spectrum.

    Keyword arguments :
    laser_power   -- start value of the laser power
    exposure_time -- start value of the exposure time
    datatype      -- start value of the data type
    scattering    -- start value of the scattering
    
    The frame is saved in self._varsdict['frames'].    
    Its components are saved in :
      self._varsdict['vars_checked'],
      self._varsdict['vars_filename'],
      self._varsdict['vars_laser_power'],
      self._varsdict['vars_exposure_time'],
      self._varsdict['optmenus_datatype'],
      self._varsdict['optmenus_scattering']
            
    """
    self.tk.call('update', 'idletasks')
    
    # create the frame
    if 0 == len(self._varsdict['frames']) :
      row = 0
    else :
      row = 1 + int(self._varsdict['frames'][-1].grid_info()['row'])

    frm = Tkinter.Frame(self._varsdict['central_frame'].interior(),
                        relief='raised',
                        borderwidth=2)
    frm.grid(row=row, column=0, padx=3, pady=3, sticky='w')
    self._varsdict['frames'].append(frm)

    ## adding the controls
    # check box
    col = 0
    var = Tkinter.IntVar()
    var.set(1)
    self._varsdict['vars_checked'].append(var)
    
    widget = Tkinter.Checkbutton(frm,
                                 text='File name ',
                                 variable=var,
                                 command=self.__updateGUI)
    widget.grid(row=0, column=col, padx=3, pady=3, sticky='w')
    col += 1

    # file name
    var = Tkinter.StringVar()
    self._varsdict['vars_filename'].append(var)
    
    widget = Pmw.EntryField(frm,
                            entry_textvariable=var,
                            entry_state='readonly',
                            entry_width=30)
    widget.grid(row=0, column=col, padx=3, pady=3, sticky='w')
    col += 1

    # button for opening file
    cmd = misc.Command(self.__open_file,
                       self._varsdict['vars_filename'][-1],
                       widget.component('entry'))
    widget = Tkinter.Button(frm,
                            image=getimage('open_file'),
                            command=cmd)
    widget.grid(row=0, column=col, padx=3, pady=3, sticky='w')
    col += 1

    # laser power
    var = Tkinter.DoubleVar()
    if laser_power is not None and 0. < laser_power :
      var.set(laser_power)
    else :
      var.set(200.)

    self._varsdict['vars_laser_power'].append(var)

    validate = dict(validator='real',
                    min=0.,
                    separator='.')    
    widget = Pmw.EntryField(frm,
                            labelpos='w',
                            label_text='Laser power (mW) ',
                            entry_textvariable=var,
                            modifiedcommand=self.__updateGUI,
                            command=self.__plot,
                            validate=validate,
                            entry_width=7)
    widget.grid(row=0, column=col, padx=3, pady=3, sticky='w')
    col += 1

    # exposure power
    var = Tkinter.DoubleVar()
    if exposure_time is not None and 0. < exposure_time :
      var.set(exposure_time)
    else :
      var.set(10.)

    self._varsdict['vars_exposure_time'].append(var)
    
    widget = Pmw.EntryField(frm,
                            labelpos='w',
                            label_text='Exposure time (min) ',
                            entry_textvariable=var,
                            modifiedcommand=self.__updateGUI,
                            command=self.__plot,
                            validate=validate,
                            entry_width=7)
    widget.grid(row=0, column=col, padx=3, pady=3, sticky='w')
    col += 1

    # datatype    
    maxwidth = max([len(item) for item in resources.STRINGS_EXPSPECTRA_TYPES])
    widget = Pmw.OptionMenu(frm,
                            items=resources.STRINGS_EXPSPECTRA_TYPES,
                            labelpos='w',
                            label_text='Data type ',
                            menubutton_width=maxwidth)
    widget.grid(row=0, column=col, padx=3, pady=3, sticky='w')
    col += 1
    self._varsdict['optmenus_datatype'].append(widget)
    if datatype is not None :
      widget.setvalue(datatype)

    # scattering
    maxwidth = max([len(item) for item in resources.STRINGS_SCATTERING_TYPES])
    widget = Pmw.OptionMenu(frm,
                            items=resources.STRINGS_SCATTERING_TYPES,
                            labelpos='w',
                            label_text='Scattering ',
                            menubutton_width=maxwidth)
    widget.grid(row=0, column=col, padx=3, pady=3, sticky='w')
    col += 1
    self._varsdict['optmenus_scattering'].append(widget)
    if scattering is not None :
      widget.setvalue(scattering)

    # change callback for the datatype option menu
    cmd = misc.Command(self.__change_datatype,
                       self._varsdict['optmenus_scattering'][-1])
    self._varsdict['optmenus_datatype'][-1].configure(command=cmd)

  def __get_checked_indices(self) :
    """Return a list of checked indices."""
    checked = []
    for i in xrange(len(self._varsdict['vars_checked'])) :
      if self._varsdict['vars_checked'][i].get() :
        checked.append(i)

    return checked

  def __open_file(self, var_filename, entry) :
    """Open a file and put its name to a given variable."""
    if os.path.exists(var_filename.get()) :
      initialdir = os.path.dirname(os.path.realpath(var_filename.get()))
    else :
      initialdir = self._varsdict.get('lastdir', os.getcwd())
    
    filename = tkFileDialog.Open(parent=self,
                                 initialdir=initialdir,
                                 filetypes=self._varsdict['spectratypes']
                                 ).show()
    
    if filename is not None and 0 != len(filename) :
      var_filename.set(filename)
      entry.xview(len(filename))
      self._varsdict['lastdir'] = os.path.dirname(os.path.realpath(filename))
      self.__updateGUI()

  def __updateGUI(self) :
    """Update GUI."""
    checked = self.__get_checked_indices()
    nchecked = len(checked)
    
    ## plot button
    state = 'normal'
    
    try :
      for i in checked :          
        # no negative laser powers or exposure times
        if 0. >= self._varsdict['vars_laser_power'][i].get() or \
           0. >= self._varsdict['vars_exposure_time'][i].get() :
          state = 'disabled'
          break

        # no empty file names
        if 0 == len(self._varsdict['vars_filename'][i].get().strip()) :
          state = 'disabled'
          break          

    except ValueError :
      state = 'disabled'

    # at least one file should be checked
    if 0 == nchecked :
      state = 'disabled'
      
    self._varsdict['btn_plot'].configure(state=state)

    ## remove button - at least one checked file
    self._varsdict['btn_remove_selected'].configure(
      state = 0 < nchecked and 'normal' or 'disabled')

    ## remove all, select / deselect all buttons - at least one file
    state = 0 < len(self._varsdict['frames']) and 'normal' or 'disabled'
    for btn in ('btn_remove_all', 'btn_select_all', 'btn_deselect_all') :
      self._varsdict[btn].configure(state=state)

  def __change_datatype(self, cursel, optmenu_scattering) :
    """Called when changing the data type.

    Degree of circularity is available only for the forward and backward
    scattering (no for ICP).

    """    
    if resources.STRINGS_EXPSPECTRA_TYPES[1] == cursel :
      iend = 2
    else :
      iend = len(resources.STRINGS_SCATTERING_TYPES)

    optmenu_scattering.setitems(resources.STRINGS_SCATTERING_TYPES[:iend])


class RamanROADegcircExpWindow(AbstractSpectrumWindow) :
  """Window for exploring experimental Raman/ROA/Degree of circularity spectra.

  The following public methods are explorted :
      clone() -- clone the molecule window
  
  """

  def __init__(self, mainApp, expdata, compound_name=None) :
    """Constructor of the class.

    Positional arguments :
    mainApp       -- reference to the main window of PyVib2
    expdata       -- list with the experimental data

    Keyword arguments :
    compound_name -- compound name (default None)

    """
    if not isinstance(expdata, (list, tuple)) or 1 > len(expdata) :
      raise ConstructorError('Invalid expdata argument')

    self._expdata = expdata
    
    AbstractSpectrumWindow.__init__(self, mainApp, compound_name=compound_name)

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    if self._smartdict['compound_name'] is not None :
      title = 'Experimental spectra of %s' % self._smartdict['compound_name']
    else :
      title = 'Experimental spectra'
      
    self.wm_title(title)

    ## message bar at the bottom
    self._varsdict['msgBar'] = Pmw.MessageBar(self, entry_relief='sunken')
    self._varsdict['msgBar'].grid(row=1, column=0, columnspan=2,
                                  padx=3, pady=3, sticky='we')    
    ## plotting area
    self.grid_columnconfigure(0, weight=1)
    self.grid_rowconfigure(0, weight=1)
    
    self._varsdict['figure'] = RamanROADegcircExpFigure(
      self, self._expdata, msgBar=self._varsdict['msgBar'])
                                                         
    self._varsdict['figure'].tk_canvas.get_tk_widget().grid(row=0, column=0,
                                                            padx=3, pady=3,
                                                            sticky='news')
    ## button toolbar to the right of the plot
    btn_toolbar = self.__constructButtonToolbar(self)
    btn_toolbar.grid(row=0, column=1, padx=3, pady=10, sticky='n')

    ## first rendering
    self.tk.call('update', 'idletasks')    
    self._varsdict['figure'].plot_spectra(title1=self.wm_title())

  def __constructButtonToolbar(self, parent) :
    """Construct the button toolbar and return it."""
    btn_toolbar = widgets.ButtonToolbar(parent, horizontal=False)

    # clone button
    btn_toolbar.add_button(imagename='clone',
                           command=self.clone,
                           helptext='Clone the window.')
    
    # save spectra
    btn_toolbar.add_button(
      imagename='save',
      command=self._save_figure,
      helptext='Export the spectrum in PNG, ' + \
      'EPS and PDF (requires ps2pdf) formats.')

    # spectra settings
    btn_toolbar.add_button(imagename='prefs',
                           command=self.__settings,
                           helptext='Settings of the spectra.')

    # information
    btn_toolbar.add_button(text='i',
                           command=self.__exp_info,
                           helptext='Information about the spectra.')

    btn_toolbar.add_separator()

    # restore the previous zooming region
    btn_toolbar.add_button(
      imagename='undo',
      command=Command(self._varsdict['figure'].restore_last_zoom),
      helptext='Restore the previous plotting region.')

    return btn_toolbar

  def _save_figure(self) :
    """Callback for the save button."""
    if 'dlg_settings' in self._varsdict :
      size = self._varsdict['dlg_settings'].figsize_inches
    else :
      size = None

    self._save(self._varsdict['figure'], name='exp_spectra', size=size)

  def __settings(self) :
    """Show the settings of the spectra."""
    if 'dlg_settings' not in self._varsdict :
      ok_command = Command(self._varsdict['figure'].plot_spectra)      
      self._varsdict['dlg_settings'] = \
        dialogs.RamanRoaDegcircExpSettingsDialog(self,ok_command=ok_command)
      
      self._varsdict['dlg_settings'].configure(title=r'Spectra settings')

    # do not forget to update the controls !
    self._varsdict['dlg_settings'].update_controls(self._varsdict['figure'])
    self._varsdict['dlg_settings'].show()

  def __exp_info(self) :
    """Information about the spectra."""
    total_exposure_time = 0.
    total_laser_energy  = 0.
    for data in self._expdata :
      if 'Raman/ROA' == data.datatype :
        total_exposure_time += data.exposure_time
        total_laser_energy  += data.exposure_time * data.laser_power * 0.06
        
    msg = 'Total exposure time (for Raman and ROA) = %.2f min\n'\
          'Total laser energy  (for Raman and ROA) = %.2f J\n\n'% \
          (total_exposure_time, total_laser_energy)

    msg_raman_roa = 'Raman/ROA :\n'
    msg_degcirc   = 'Degree of circularity :\n'
    for data in self._expdata :
      if 'Raman/ROA' == data.datatype :
        msg_raman_roa = ''.join((msg_raman_roa, str(data), '\n'))
      else :
        msg_degcirc   = ''.join((msg_degcirc, str(data), '\n'))

    msg = ''.join((msg, msg_raman_roa, '\n', msg_degcirc))

    dlg = Pmw.TextDialog(self,
                         title='Information about the spectra',
                         defaultbutton=0)
    dlg.insert('end', msg)
    dlg.configure(text_state='disabled')

  def clone(self) :
    """Clone the molecule window.

    Overrides the base class method.
    
    """
    self.tk.call('update', 'idletasks')

    splash = widgets.SplashScreen(self, 'Cloning the window...')
    
    RamanROADegcircExpWindow(self._mainApp, self._expdata)

    splash.destroy()
