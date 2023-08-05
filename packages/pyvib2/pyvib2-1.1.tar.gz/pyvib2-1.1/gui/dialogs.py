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

"""Dialogs of PyVib2.

The following classes are exported :
    BaseDialog                        -- base class for all dialogs
    ApplicationSettingsDialog         -- settings of PyVib2
    MoleculeWindowSettingsDialog      -- settings of a molecule window
    FileInfoDialog                    -- information about a file
    IsotopesDialog                    -- customizing the isotopic composition
    ElementIsotopeDialog              -- select an isotope for an element
    SaveVibrationsDialog              -- dialog for saving vibrations
    AnimationSettingsDialog           -- dialog for saving animations
    SnapshotDialog                    -- making a snapshot of a render widget
    DefineGroupsDialog                -- defining groups in a molecule
    RamanRoaDegcircCalcSettingsDialog -- settings of Raman/ROA/Degcirc spectra
    TwoDCirclesSettingsDialog         -- settings of a circles canvas
    MultipleSpectraSettingsDialog     -- settings of spectra of several mols.
    IRVCDCalcSettingsDialog           -- settings of IR/VCD/g spectra
    RamanRoaDegcircExpSettingsDialog  -- settings of Raman/ROA/Degcirc exp.sp.
    
"""
__author__ = 'Maxim Fedorovsky'

import os
import os.path
import sys
from   math import pi, cos, sin
from   copy import copy
from   time import strftime, localtime
import Tkinter
import tkColorChooser
import tkFileDialog

import Pmw
from   numpy import array

import vtk
import vtk.tk.vtkTkRenderWidget

from pyviblib                 import APPNAME, molecule
from pyviblib.util            import misc, pse
from pyviblib.util.exceptions import ConstructorError, ParseError
from pyviblib.gui             import widgets, resources, figures, rendering
from pyviblib.gui.images      import getimage

__all__ = ['BaseDialog', 'ApplicationSettingsDialog',
           'MoleculeWindowSettingsDialog', 'FileInfoDialog',
           'IsotopesDialog', 'ElementIsotopeDialog', 'SaveVibrationsDialog',
           'AnimationSettingsDialog', 'SnapshotDialog',
           'DefineGroupsDialog', 'RamanRoaDegcircCalcSettingsDialog',
           'TwoDCirclesSettingsDialog', 'MultipleSpectraSettingsDialog',
           'IRVCDCalcSettingsDialog', 'RamanRoaDegcircExpSettingsDialog']


class BaseDialog(Pmw.Dialog, widgets.BaseWidget) :
  """Base class for all dialogs.

  The _command() protected method is a handler for the button events.
  Subclasses should override it.
  
  """

  def __init__(self, parent, **kw) :
    """Constructor of the class.

    Positional arguments :
    parent -- parent widget

    Keyword arguments :
    Accepts the keywords arguments of Pmw.Dialog.
    
    """
    Pmw.Dialog.__init__(self, parent, **self.__dialog_kw(**kw))
    self.withdraw()
    
    widgets.BaseWidget.__init__(self, **kw)

    # center the dialog on the screen
    Pmw.setgeometryanddeiconify(self, self._centreonscreen())

  def __dialog_kw(self, **kw) :
    """Retrieve the keywords for Pmw.Dialog."""
    dlg_kw = {}

    for opt in ('activatecommand', 'buttonboxpos', 'deactivatecommand',
                'defaultbutton', 'master', 'separatorwidth', 'title',
                'buttons') :
      if opt in kw :
        dlg_kw[opt] = kw[opt]

    # all options are copied except for the command keyword
    dlg_kw['command'] = self._command

    return dlg_kw

  def _command(self, btn_name) :
    """Handler for the button events.

    Subclasses should override this methods.
    
    """
    pass


class MoleculeWindowSettingsDialog(BaseDialog) :
  """Settings of a molecule window.

  The following read-only property is exposed :
      settings          -- dictionary with the settings

  The following public method is exposed :
      update_controls() -- update the controls of the dialog
      
  """

  def __init__(self, molWindow) :
    """Constructor of the class.

    Positional arguments :
    molWindow -- reference to the molecule window
    
    """
    self.__molWindow = molWindow
    
    BaseDialog.__init__(self,
                        molWindow,
                        buttons=resources.STRINGS_BUTTONS_OK_APPLY_CANCEL,
                        defaultbutton=resources.STRING_BUTTON_OK,
                        title='Molecule window settings')

  def _init_vars(self) :
    """Initialize variables."""
    self.__settings = self.__molWindow.settings

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    ## create a notebook object
    self.interior().grid_rowconfigure(0, weight=1)
    self.interior().grid_columnconfigure(0, weight=1)
    
    self._varsdict['notebook'] = Pmw.NoteBook(self.interior())
    self._varsdict['notebook'].grid(row=0, column=0,
                                    padx=3, pady=3, sticky='news')
    ### Appearance tab
    tab_appearance = self._varsdict['notebook'].add('Appearance')
    self._varsdict['notebook'].tab('Appearance').focus_set()

    tab_appearance.grid_columnconfigure(0, weight=1)
    tab_appearance.grid_rowconfigure(0, weight=1)
    tab_appearance.grid_rowconfigure(1, weight=1)

    ## group colors
    grp_colors = Pmw.Group(tab_appearance, tag_text='Colors')
    grp_colors.grid(row=0, column=0, sticky='new')
    
    grp_colors.interior().grid_columnconfigure(0, weight=1)

    # width of the labels describing the colors
    label_width = 20

    # background color
    widget = widgets.ChooseColorWidget(grp_colors.interior(),
                                       text='Background',
                                       label_width=label_width,
                                       sticky='we')
    self._varsdict['widget_bg_color'] = widget
    self._varsdict['widget_bg_color'].grid(row=0, column=0, sticky='we')
    
    # hemisphere colors
    widget = widgets.ChooseColorWidget(grp_colors.interior(),
                                       text='Vib. hemisphere 1',
                                       label_width=label_width,
                                       sticky='we')
    self._varsdict['widget_color_sphere_1'] = widget
    self._varsdict['widget_color_sphere_1'].grid(row=1, column=0, sticky='we')

    widget = widgets.ChooseColorWidget(grp_colors.interior(),
                                       text='Vib. hemisphere 2',
                                       label_width=label_width,
                                       sticky='we')
    self._varsdict['widget_color_sphere_2'] = widget
    self._varsdict['widget_color_sphere_2'].grid(row=2, column=0, sticky='we')

    ## group Structure
    grp_structure = Pmw.Group(tab_appearance, tag_text='Structure')
    grp_structure.grid(row=1, column=0, sticky='new')

    grp_structure.interior().grid_rowconfigure(0, weight=1)
    grp_structure.interior().grid_columnconfigure(0, weight=1)

    # Ball & stick, stick or van der Waals
    widget = Pmw.OptionMenu(grp_structure.interior(),
                            items=resources.STRINGS_MODE_MOLECULE,
                            menubutton_width=20,
                            label_text='Molecule mode :',
                            labelpos='w')
    self._varsdict['options_molecule_mode'] = widget
    self._varsdict['options_molecule_mode'].grid(row=0, column=0,
                                                 padx=3, pady=3, sticky='w')
    # monolith, atoms colors
    widget = Pmw.OptionMenu(grp_structure.interior(),
                            items=resources.STRINGS_MODE_BONDS,
                            menubutton_width=13,
                            label_text='Bonds color :',
                            labelpos='w')
    self._varsdict['options_bonds_mode'] = widget
    self._varsdict['options_bonds_mode'].grid(row=0, column=1,
                                              padx=3, pady=3, sticky='w')
    # next line : render hydrogen bonds
    self._varsdict['var_hydrogen_bond'] = Tkinter.IntVar()
    widget = Tkinter.Checkbutton(grp_structure.interior(),
                                 text='Render hydrogen bonds',
                                 variable=self._varsdict['var_hydrogen_bond'])
    self._varsdict['check_hydrogen_bond'] = widget
    self._varsdict['check_hydrogen_bond'].grid(row=1, column=0,
                                               padx=3, pady=3, sticky='w')
    # render atom labels
    self._varsdict['var_atom_labels'] = Tkinter.IntVar()

    widget = Tkinter.Checkbutton(grp_structure.interior(),
                                 text='Render atom labels',
                                 variable=self._varsdict['var_atom_labels'])
    self._varsdict['check_atom_labels'] = widget
    self._varsdict['check_atom_labels'].grid(row=1, column=1,
                                             padx=3, pady=3, sticky='w')

    ### Rendering tab
    tab_rendering = self._varsdict['notebook'].add('Rendering')
    
    tab_rendering.grid_rowconfigure(0, weight=1)
    tab_rendering.grid_columnconfigure(0, weight=1)
    
    # VTK resolution : reflects the quality
    validate = dict(validator='integer',
                    min=resources.NUM_RESOLUTION_VTK_MIN,
                    max=resources.NUM_RESOLUTION_VTK_MAX)
    widget = Pmw.Counter(tab_rendering,
                         labelpos='w',
                         label_text='VTK resolution',
                         labelmargin=5,
                         entry_width=3,
                         datatype=dict(counter='integer'),
                         entryfield_validate=validate,
                         entry_state='readonly',
                         #autorepeat=False,
                         increment=1)
    self._varsdict['counter_res'] = widget
    self._varsdict['counter_res'].grid(row=0, column=0,
                                       padx=3, pady=3, sticky='nw')
    self._varsdict['counter_res'].configure(entryfield_modifiedcommand=\
                                            self.__update_res_counter)
    ## finally
    self._varsdict['notebook'].setnaturalsize()

  def _declare_properties(self) :
    """Declare properties of the widget."""
    self.__class__.settings = property(
      fget=misc.Command(misc.Command.fget_value, self.__settings))
    
  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    pass

  def _command(self, btn_name) :
    """Handler for the button events."""
    if btn_name in (resources.STRING_BUTTON_APPLY,
                    resources.STRING_BUTTON_OK) :
      self.__pack_settings()
      self.__molWindow.apply_settings(resources.STRING_BUTTON_OK == btn_name)
    else :
      self.withdraw()

  def __update_res_counter(self) :
    """Update the counter with the VTK resolution."""
    res = int(self._varsdict['counter_res'].component('entryfield').getvalue())
    self.__settings.update(dict(resolution=res))

  def __pack_settings(self) :
    """Update the settings dictionary."""
    # colors
    self.__settings['window_bg'] = self._varsdict['widget_bg_color'].color
    
    # hemisphere colors
    self.__settings['color_sphere_1'] = \
                              self._varsdict['widget_color_sphere_1'].color
    self.__settings['color_sphere_2'] = \
                              self._varsdict['widget_color_sphere_2'].color
    
    self.__settings['molecule_mode'] = \
        list(resources.STRINGS_MODE_MOLECULE).index(
          self._varsdict['options_molecule_mode'].getvalue())
    
    self.__settings['bonds_mode']    = \
        list(resources.STRINGS_MODE_BONDS).index(
          self._varsdict['options_bonds_mode'].getvalue())

    self.__settings['hydrogen_bond'] = self._varsdict['var_hydrogen_bond'].get()
    self.__settings['atom_labels']   = self._varsdict['var_atom_labels'].get()
    
  def update_controls(self) :
    """Synchronize the GUI controls with the molecule window."""
    self.__settings = self.__molWindow.settings

    # molecule window background color
    self._varsdict['widget_bg_color'].color = self.__settings['window_bg']

    # vibrational hemisphere colors
    self._varsdict['widget_color_sphere_1'].color = \
                                            self.__settings['color_sphere_1']
    self._varsdict['widget_color_sphere_2'].color = \
                                            self.__settings['color_sphere_2']
    # rendering modes    
    self._varsdict['options_molecule_mode'].setvalue(
      resources.STRINGS_MODE_MOLECULE[self.__settings['molecule_mode']])
    self._varsdict['options_bonds_mode'].setvalue(
      resources.STRINGS_MODE_BONDS[self.__settings['bonds_mode']])

    self._varsdict['var_hydrogen_bond'].set(self.__settings['hydrogen_bond'])
    self._varsdict['var_atom_labels'].set(self.__settings['atom_labels'])

    # current VTK resolution
    self._varsdict['counter_res'].component('entryfield').setvalue(
      self.__settings['resolution'])


class ApplicationSettingsDialog(BaseDialog) :
  """Settings of PyVib2.

  The following read-only property is exposed :
      settings          -- dictionary with the settings of PyVib2

  The following public method is exported :
      update_controls() -- update the controls of the dialog
      
  """

  def __init__(self, mainApp) :
    """Constructor of the class.

    Positional arguments :
    mainApp -- reference to the main window of PyVib2.
    
    """
    # current settings
    self.__settings = mainApp.settings
    
    BaseDialog.__init__(self,
                        mainApp.master,
                        buttons=resources.STRINGS_BUTTONS_OK_CANCEL,
                        defaultbutton=resources.STRING_BUTTON_OK,
                        title='%s settings' % APPNAME)
    self.__init_vtk()

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    self.interior().grid_rowconfigure(0, weight=1)
    self.interior().grid_columnconfigure(0, weight=1)
    
    self._varsdict['notebook'] = Pmw.NoteBook(self.interior())
    self._varsdict['notebook'].grid(row=0, column=0,
                                    padx=3, pady=3, sticky='news')
    ## Rendering tab
    tab_rendering = self._varsdict['notebook'].add('Rendering')
    self._varsdict['notebook'].tab('Rendering').focus_set()

    tab_rendering.grid_rowconfigure(2, weight=1)
    tab_rendering.grid_columnconfigure(0, weight=1)

    # group with a widget with spheres    
    group_quality = Pmw.Group(tab_rendering, tag_text='Quality')
    group_quality.grid(row=2, column=0, padx=3, pady=3, sticky='news')

    group_quality.interior().grid_rowconfigure(1, weight=1)
    group_quality.interior().grid_columnconfigure(0, weight=1)

    # default vtk resolution for all windows
    self._varsdict['var_resolution'] = Tkinter.IntVar()
    
    if 'resolution' in self.__settings :
      self._varsdict['var_resolution'].set(self.__settings['resolution'])      
    else :
      self._varsdict['var_resolution'].set(resources.NUM_RESOLUTION_VTK)

    validate = dict(validator='integer',
                    min=resources.NUM_RESOLUTION_VTK_MIN,
                    max=resources.NUM_RESOLUTION_VTK_MAX)
    widget = Pmw.Counter(group_quality.interior(),
                         labelpos='w',
                         label_text='VTK resolution',
                         orient='horizontal', 
                         entry_width=4,
                         labelmargin=3,
                         entry_textvariable=self._varsdict['var_resolution'],
                         datatype=dict(counter='integer'),
                         entryfield_validate=validate,
                         entryfield_modifiedcommand=self.__update_test_sphere,
                         autorepeat=True,
                         increment=1)
    self._varsdict['counter_resolution'] = widget
    self._varsdict['counter_resolution'].grid(row=0, column=0,
                                              padx=3, pady=3, sticky='w')
    # vtk widget
    self._varsdict['vtk_widget'] = \
        vtk.tk.vtkTkRenderWidget.vtkTkRenderWidget(group_quality.interior(),
                                                   height=300,
                                                   width=400)
    self._varsdict['vtk_widget'].grid(row=1, column=0, columnspan=2,
                                      padx=5, pady=5, sticky='news')

    if self._varsdict['vtk_widget'].GetRenderWindow().IsDirect() :
      text_rendering = 'Enabled'
    else :
      text_rendering = 'Disabled'

    # direct rendering enabled ? (very first control on the tab)
    widget = Pmw.EntryField(tab_rendering,
                            labelpos='w',
                            label_text='Direct rendering :',
                            labelmargin=3,
                            value=text_rendering,
                            entry_state='readonly',
                            entry_justify='right')
    self._varsdict['entry_direct_rendering'] = widget
    self._varsdict['entry_direct_rendering'].grid(row=0, column=0,
                                                  columnspan=2,
                                                  padx=3, pady=3, sticky='we')
    # vtk version
    version = vtk.vtkVersion().GetVTKVersion()
    widget = Pmw.EntryField(tab_rendering,
                            labelpos='w',
                            label_text='VTK version :',
                            labelmargin=3,
                            value=version,
                            entry_state='readonly',
                            entry_justify='right')
    self._varsdict['entry_vtk_version'] = widget
    self._varsdict['entry_vtk_version'].grid(row=1, column=0, columnspan=2,
                                             padx=3, pady=3, sticky='we')
    # aligning the entryfields
    Pmw.alignlabels((self._varsdict['entry_direct_rendering'],
                     self._varsdict['entry_vtk_version']))
    
    ## setting appropriate notebook size
    self._varsdict['notebook'].setnaturalsize()

  def _declare_properties(self) :
    """Declare properties of the widget."""
    self.__class__.settings = property(
      fget=misc.Command(misc.Command.fget_value, self.__settings))

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    self._balloon.bind(self._varsdict['entry_direct_rendering'],
              'Shows if the direct rendering is enabled.\n\n' + \
              'Unless enabled the CPU is used for rendering what ' + \
              'can be very slow.')    
    self._balloon.bind(self._varsdict['entry_vtk_version'],
                       'Full version label of the used VTK.')

    self._balloon.bind(self._varsdict['counter_resolution'],
                       'Reflects the quality of 3D rendering.\n\n' + \
                       'Set an appropriate value for the productivity ' + \
                       'of your system.')

  def _command(self, btn_name) :
    """Handler for the button events."""
    if resources.STRING_BUTTON_CANCEL == btn_name :
      self.withdraw()
    else :
      self.withdraw()
      self.__apply_settings()

  def __init_vtk(self) :
    """Initialize the vtk widget."""
    self.__renderer = vtk.vtkRenderer()
    self._varsdict['vtk_widget'].GetRenderWindow().AddRenderer(self.__renderer)

    self.__renderer.SetBackground(
      misc.color_html_to_RGB(resources.COLOR_MOLECULE_WINDOW_BG))

    lightKit = vtk.vtkLightKit()
    lightKit.AddLightsToRenderer(self.__renderer)

    self.__update_test_sphere()

    camera = self.__renderer.GetActiveCamera()
    camera.Azimuth(90.0)
    camera.Dolly(1.3)
    camera.OrthogonalizeViewUp()
    self.__renderer.ResetCameraClippingRange()
  
    self._varsdict['vtk_widget'].Render()

  def __render_test_sphere(self, resolution) :
    """Render 30 test spheres."""
    # cleaning the renderer
    # vtkViewport::RemoveAllProps() is deprecated in VTK-5.0
    try :
      self.__renderer.RemoveAllViewProps()
    except :
      # for older VTK
      self.__renderer.RemoveAllProps()

    # making many spheres
    n = 10
    r = 0.3
    
    for i in xrange(n) :
      phi = 2. * pi * i / n
      pos = (cos(phi), sin(phi), 0.)
      
      actor = rendering.create_sphere(r, pos, resolution)[1]
      actor.GetProperty().SetDiffuseColor((1., 0., 0.))
      
      self.__renderer.AddActor(actor)

    for i in xrange(n) :
      phi = 2. * pi * i / n
      pos = (0., cos(phi), 1.5 + sin(phi))
      
      actor = rendering.create_sphere(r, pos, resolution)[1]
      actor.GetProperty().SetDiffuseColor((0., 1., 0.))
      
      self.__renderer.AddActor(actor)

    for i in xrange(n) :
      phi = 2. * pi * i / n

      pos = (0., cos(phi), -1.5 + sin(phi))
    
      actor = rendering.create_sphere(r, pos, resolution)[1]
      actor.GetProperty().SetDiffuseColor((0., 0., 1.))
      
      self.__renderer.AddActor(actor)
    
    self._varsdict['vtk_widget'].Render()

  def __update_test_sphere(self) :
    """Update the resolution as the user changes the counter control."""
    try :
      res = self._varsdict['var_resolution'].get()      
    except ValueError :
      return
    else :
      self.__render_test_sphere(res)
    
  def __apply_settings(self) :
    """Apply settings."""
    self.__settings['resolution'] = self._varsdict['var_resolution'].get()

  def update_controls(self) :
    """Synchronize the GUI controls with the main window of PyVib2."""
    if 'resolution' in self.__settings :
      self._varsdict['var_resolution'].set(self.__settings['resolution'])      
    else :
      self._varsdict['var_resolution'].set(resources.NUM_RESOLUTION_VTK)

  
class SaveVibrationsDialog(BaseDialog) :
  """Dialog for saving vibrations."""  
  
  VIB_OPTIONS       = ('Current', 'Range', 'List')
  PARAM_LIST        = ('image_format', 'magnify_factor', 'filepattern',
                       'vibs_list', 'create_archive')


  def __init__(self, molWindow, **kw) :
    """Constructor of the class.

    Positional arguments :
    molWindow -- reference to the molecule window
    
    """
    self.__molWindow = molWindow

    BaseDialog.__init__(self,
                        molWindow,
                        buttons = resources.STRINGS_BUTTONS_OK_CANCEL,
                        defaultbutton=resources.STRING_BUTTON_OK,
                        title='Save vibrations',
                        **kw)

  def _init_vars(self) :
    """Initialize variables."""
    self._smartdict['initialdir'] = os.getcwd()

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    ## Vibrations to be saved (left side)
    grp_vibs = Pmw.Group(self.interior(), tag_text='Vibrations')
    grp_vibs.grid(row=0, column=0, sticky='new', padx=3, pady=3)

    self._varsdict['radio_vibs'] = Pmw.RadioSelect(grp_vibs.interior(),
                                                   buttontype='radiobutton',
                                                   orient='vertical')
    self._varsdict['radio_vibs'].grid(row=0, column=0, rowspan=3,
                                      padx=3, pady=0)

    for vib_opt in SaveVibrationsDialog.VIB_OPTIONS :
      self._varsdict['radio_vibs'].add(vib_opt)

    self._varsdict['radio_vibs'].invoke(SaveVibrationsDialog.VIB_OPTIONS[0])
    
    # dummy label to expand
    lbl_dummy = Tkinter.Label(grp_vibs.interior())
    lbl_dummy.grid(row=0, column=1, sticky='we')

    # counters for a range of vibrations
    NFreq = self.__molWindow.molecule.NFreq
    validate = dict(validator='integer', min=1, max=NFreq)

    widget   = Pmw.Counter(grp_vibs.interior(),
                           labelpos='w',
                           label_text='To',
                           label_justify='left',
                           entry_width=4,
                           entryfield_value=NFreq,
                           entryfield_modifiedcommand=None,
                           datatype=dict(counter='integer'),
                           entryfield_validate=validate,
                           autorepeat=False,
                           increment = 1)
    self._varsdict['counter_to'] = widget
    self._varsdict['counter_to'].grid(row=1, column=2,
                                      padx=3, pady=0, sticky='we')
    
    widget = Pmw.Counter(grp_vibs.interior(),
                         labelpos='w',
                         label_text='From',
                         label_justify='left',
                         entry_width=4,
                         entryfield_value='1',
                         entryfield_modifiedcommand=None,
                         datatype=dict(counter='integer'),           
                         autorepeat=False,
                         increment = 1)
    self._varsdict['counter_from'] = widget
    self._varsdict['counter_from'].grid(row=1, column=1,
                                        padx=0, pady=0, sticky='we')
    self._varsdict['counter_from'].configure(
      entryfield_validate = self.__counter_from_validate)

    # entry for the list
    self._varsdict['entry_list'] = Tkinter.Entry(grp_vibs.interior())
    self._varsdict['entry_list'].grid(row=2, column=1, columnspan=2,
                                      padx=3, pady=0, sticky='we')

    ## Image settings (right side)
    grp_settings = Pmw.Group(self.interior(), tag_text='Image settings')
    grp_settings.grid(row=0, column=1, padx=3, pady=3, sticky='new')

    # image format
    lbl_format = Tkinter.Label(grp_settings.interior(),
                               text='Format',
                               anchor='w')
    lbl_format.grid(row=0, column=0, padx=3, pady=3, sticky='w')

    widget = Pmw.OptionMenu(grp_settings.interior(),
                            items=resources.STRINGS_VTK_SNAPSHOT_FORMATS,
                            menubutton_width=7)
    self._varsdict['options_format'] = widget
    self._varsdict['options_format'].grid(row=0, column=1,
                                          padx=3, pady=3, sticky='ew')
    # image size
    lbl_size_label = Tkinter.Label(grp_settings.interior(),
                                   text='Size (pixel)',
                                   anchor='w')
    lbl_size_label.grid(row=2, column=0, padx=3, pady=3, sticky='w')

    self._varsdict['var_image_size'] = Tkinter.StringVar() 
    widget = Tkinter.Label(grp_settings.interior(),
                           relief='ridge',
                           textvariable=self._varsdict['var_image_size'])
    
    self._varsdict['lbl_size'] = widget
    self._varsdict['lbl_size'].grid(row=2, column=1,
                                    padx=5, pady=3, sticky='ew')
    # image resolution
    lbl_res = Tkinter.Label(grp_settings.interior(),
                            text='Resolution (dpi)',
                            anchor='w')
    lbl_res.grid(row=1, column=0, padx=3, pady=3, sticky='w')

    widget = Pmw.OptionMenu(grp_settings.interior(),
                            items=resources.NUMS_VTK_SCREENSHOT_RESOLUTIONS,
                            menubutton_width=5,
                            command=self.__recalc_image_size)
    self._varsdict['options_res'] = widget
    self._varsdict['options_res'].grid(row=1, column=1,
                                       padx=3, pady=3, sticky='ew')
    self._varsdict['options_res'].invoke(0)    

    ## Filename pattern frame    
    frm_filepattern = Tkinter.Frame(self.interior())
    frm_filepattern.grid(row=1, column=0, columnspan=2,
                         padx=0, pady=3, sticky='ew')
    
    # allowing frame to expand
    frm_filepattern.grid_rowconfigure(0, weight=1)
    frm_filepattern.grid_columnconfigure(1, weight=1)
    
    lbl_pattern = Tkinter.Label(frm_filepattern,
                                text='File name pattern',
                                anchor='w')
    lbl_pattern.grid(row=0, column=0, padx=3, pady=3, sticky='w')

    # initialize properly
    self._varsdict['var_filepattern'] = Tkinter.StringVar()
    self._varsdict['var_filepattern'].set(os.path.join(
      self._smartdict['initialdir'], self.__molWindow.molecule_name))

    widget = Tkinter.Entry(frm_filepattern,
                           textvariable=self._varsdict['var_filepattern'])
    self._varsdict['entry_filepattern'] = widget
    self._varsdict['entry_filepattern'].grid(row=0, column=1,
                                             padx=3, pady=3, sticky='ew')
    
    widget = Tkinter.Button(frm_filepattern,
                            image=getimage('open_dir2'),
                            relief='flat',
                            overrelief='raised',
                            command=self.__open_filepattern)
    self._varsdict['btn_filepattern'] = widget
    self._varsdict['btn_filepattern'].grid(row=0, column=2,
                                           padx=3, pady=3, sticky='e')
    # create archive
    self._varsdict['var_create_archive'] = Tkinter.IntVar()
    self._varsdict['var_create_archive'].set(0)
    
    widget = Tkinter.Checkbutton(frm_filepattern,
                                 text='Create zip archive',
                                 variable=self._varsdict['var_create_archive'])
    self._varsdict['checkbtn_archive'] = widget
    self._varsdict['checkbtn_archive'].grid(row=1, column=0,
                                            padx=3, pady=3, sticky='w')

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    self._balloon.bind(self._varsdict['radio_vibs'],
                      'Specify which vibrations are to be saved.')
    self._balloon.bind(self._varsdict['counter_from'],
                      'Start from a given vibration.')
    self._balloon.bind(self._varsdict['counter_to'],
                      'End with a given vibration.')
    self._balloon.bind(self._varsdict['entry_list'],
                      'Enter manually a list of vibrations.\n\n' + \
                       'Numbers within the list can be separated ' + \
                       'with white spaces or commas or semicolons.')
    self._balloon.bind(self._varsdict['options_format'],
                       'Image format.')
    self._balloon.bind(self._varsdict['lbl_size'],
                       'Size of the pictures with respect to the ' + \
                       'selected resolution.\n\nDepends on the size ' + \
                       'of the CURRENT molecule window.')
    self._balloon.bind(self._varsdict['options_res'],
                       'Picture resolution in dots per inch (DPI).')
    self._balloon.bind(self._varsdict['entry_filepattern'],
       'Pattern used to generate filenames of the images.\n\n' +
       'The file name is of the form \"$pattern_$suffix_$number.$format\",' + \
       ' where $suffix is :\n' + \
       '\tenergy_tvf\t\tEnergy / Total volume fix.\n' + \
       '\tenergy_zp\t\tEnergy / Zero point.\n\n' + \
       '\texcurs_tsf\t\tExcursions / Total surface fix.\n' + \
       '\texcurs_zp\t\tExcursions / Zero point.\n' + \
       '\texcurs_sn\t\tExcursions / Standard normalization.\n')
    self._balloon.bind(self._varsdict['btn_filepattern'],
                      'Select a file pattern.')
    self._balloon.bind(self._varsdict['checkbtn_archive'],
                      'Create a zip archive with the pictures and delete' + \
                       'them afterwards.\n\n' +
                      'Filename of the archive is \"$pattern_vibs.zip\".')

  def _command(self, btn_name) :
    """Handler for the button events."""
    if resources.STRING_BUTTON_OK == btn_name :
      if self.__are_data_valid() :
        # withdraw it
        self.withdraw()   
        self.__molWindow.save_vibrations(**self.__get_kw())      
    else :
      self.withdraw()

  def __recalc_image_size(self, res) :
    """Recalculate the image size dependent on a selected resolution."""
    magnify_factor = self.__get_magnify_factor(res)
    w, h           = self.__molWindow.renderWidget.GetRenderWindow().GetSize()
  
    self._varsdict['var_image_size'].set(
      '%dx%d' % (w * magnify_factor, h * magnify_factor))

  def __get_magnify_factor(self, res) :
    """Calculate the magnify factor from the user input."""
    current_DPI  = self.__molWindow.renderWidget.GetRenderWindow().GetDPI()
    selected_DPI = int(res)
    
    magnify_factor = int(round(float(selected_DPI) / float(current_DPI)))

    return magnify_factor

  def __open_filepattern(self) :
    """"""
    filepattern = tkFileDialog.SaveAs(
      parent=self.interior(),
      initialdir=self._smartdict['initialdir'],
      initialfile='%s' % self.__molWindow.molecule_name).show()

    if filepattern :
      self._smartdict.kw['initialdir'] = os.path.dirname(filepattern)
      self._varsdict['var_filepattern'].set(filepattern)

  def __get_kw(self) :
    """Return the keywords for saving of the selected vibrations."""
    magnify_factor = self.__get_magnify_factor(
      self._varsdict['options_res'].getvalue())
    
    kw = dict(filepattern=self._varsdict['var_filepattern'].get(),
              create_archive=self._varsdict['var_create_archive'].get(),
              image_format=self._varsdict['options_format'].getvalue(),
              magnify_factor=magnify_factor)
    
    from_vib = int(self._varsdict['counter_from'].get())
    to_vib   = int(self._varsdict['counter_to'].get())

    vibs_list = []

    if SaveVibrationsDialog.VIB_OPTIONS[0] == \
       self._varsdict['radio_vibs'].getvalue() :
      vibs_list.append(-1)

    elif SaveVibrationsDialog.VIB_OPTIONS[1] == \
         self._varsdict['radio_vibs'].getvalue() :
      # return if the start_vib is > end_vib
      if from_vib > to_vib :
        vibs_list = None
      else :
        for v in xrange(from_vib, 1 + to_vib) :
          vibs_list.append(v)
    else :
      vibs_list = self.__parse_vibs_list()
      
    kw['vibs_list'] = vibs_list

    return kw

  def __counter_from_validate(self, new_value) :
    """Validator function for the from counter."""
    try :
      new_from_vib_value = int(new_value)
      
      if new_from_vib_value > int(self._varsdict['counter_to'].get()) or \
         1 > new_from_vib_value :
        return Pmw.ERROR
      
      return Pmw.OK
    
    except ValueError:
      return Pmw.ERROR

  def __parse_vibs_list(self) :
    """Parse the vibrational list given and return."""
    list_str = self._varsdict['entry_list'].get()
    separator = ' '
    
    if 0 < list_str.count(',') :
      separator = ','
    elif 0 < list_str.count(';') :
      separator = ';'

    vibs_list = []
    try :
      for v in list_str.split(separator) :
        v = int(v)
        if v > self.__molWindow.molecule.NFreq :
          return None
        else :
          vibs_list.append(v)
      
    except ValueError :
      return None
    
    else :
      if 0 == len(vibs_list) :
        return None
      else :
        return vibs_list

  def __are_data_valid(self) :
    """Enables / disable the ok button dependant on user choise.
    
    Return False if the input is incomplete.
    
    """
    if 0 == len( self._varsdict['var_filepattern'].get().strip() ) :
      return False

    # control list
    if self._varsdict['radio_vibs'].getvalue() == \
       SaveVibrationsDialog.VIB_OPTIONS[2] :
      if not self.__parse_vibs_list() :
        return False

    return True


class IsotopesDialog(BaseDialog) :
  """Dialog for customizing the isotopic composition of a molecule."""

  def __init__(self, master, mol, **kw) :
    """Constructor of the class.

    Positional arguments :
    master         -- parent widget
    mol            -- molecule
    
    Keyword arguments :
    ok_command     -- command for the Ok button (default None)
                      callable with two arguments :
                        isotopes data and molecule name
    cancel_command -- command for the Cancel button (default None)
                      callable without arguments
                      
    """
    if not isinstance(mol, molecule.Molecule) :
      raise ConstructorError('Invalid mol argument')

    self.__molecule       = mol
    
    BaseDialog.__init__(self,
                        master,
                        buttons=resources.STRINGS_BUTTONS_OK_CANCEL,
                        defaultbutton=resources.STRING_BUTTON_OK,
                        title='Isotopic composition',
                        **kw)

  def _init_vars(self) :
    """Initialize variables."""
    self._smartdict['molecule_name'] = 'unknown molecule'
    
    # list with affected atoms (indices are one-based !) : [index, mass]
    self.__affected_atoms = []

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    # allowing to expand
    self.interior().grid_rowconfigure(1, weight=0)
    self.interior().grid_columnconfigure(0, weight=0)

    # help
    help_text  = 'It is possible to customize the isotopic '\
                 'composition of a molecule :\n\n'\
                 '  a) Pick an atom in the molecule window.\n'\
                 '  b) Point out which isotope is to be used for the atom.\n'\
                 '  c) Continue until a desired substitution is done.\n\n'\
                 'Should the default isotopic composition be used, '\
                 'just press the Ok button.'
    
    info_widget = widgets.InfoWidget(self.interior(),
                                     text=help_text,
                                     height=7)
    info_widget.grid(row=0, column=0, columnspan=3,
                     padx=3, pady=3, sticky='we')

    # molecule widget - left
    group = Pmw.Group(self.interior(), tag_text='Molecule')
    group.grid(row=1, column=0, padx=5, pady=3, sticky='w')

    # molecule name can be entered
    self._varsdict['var_molecule_name'] = Tkinter.StringVar()
    self._varsdict['var_molecule_name'].set(self._smartdict['molecule_name'])

    var = self._varsdict['var_molecule_name']    
    widget = Pmw.EntryField(group.interior(),
                            labelpos='w',
                            label_text='Name',
                            labelmargin=3,
                            entry_textvariable=var,
                            entry_font=\
                            resources.get_font_molecules(self.interior()))
    self._varsdict['entryfield_name'] = widget
    self._varsdict['entryfield_name'].grid(row=0, column=0, padx=3, pady=3,
                                           sticky='ew')
    # widget
    widget = widgets.MoleculeRenderWidget(group.interior(),
                                          molecule=self.__molecule,
                                          atom_labels=True,
                                          width=400,
                                          height=400)
    self._varsdict['renderWidget'] = widget
    self._varsdict['renderWidget'].grid(row=1, column=0, padx=5, pady=5,
                                        sticky='w')

    # enabling picking
    self._varsdict['renderWidget'].do_picking = True
    self._varsdict['renderWidget'].clicked_atom_callback = \
                                     self.__ask_element_isotope
    # affected atoms - right
    group = Pmw.Group(self.interior(), tag_text='Atoms affected')
    group.grid(row=1, column=1, padx=5, pady=3, sticky='n')

    selectioncommand = self.__highlight_affected_atoms
    widget = Pmw.ScrolledListBox(group.interior(),
                                 items=(),
                                 listbox_selectmode='multiple',
                                 listbox_width=20,
                                 vscrollmode='static',
                                 selectioncommand=selectioncommand)
    self._varsdict['listbox'] = widget
    self._varsdict['listbox'].grid(row=0, column=0, padx=3, pady=3, sticky='en')

    # button toolbar - rightmost
    btn_toolbar = widgets.ButtonToolbar(group.interior(),
                                        horizontal=False,
                                        style=1)
    btn_toolbar.grid(row=0, column=1, padx=3, pady=3, sticky='ne')

    widget = btn_toolbar.add_button(imagename='remove',
                                    command=self.__remove,
                                    helptext='Remove custom settings for ' + \
                                    'selected atom(s).')
    self._varsdict['btn_remove'] = widget

    widget = btn_toolbar.add_button(imagename='remove_all',
                                    command=self.__remove_all,
                                    helptext='Remove all custom settings.')
    self._varsdict['btn_remove_all'] = widget

    #
    self.__update_GUI()

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    self._balloon.bind(self._varsdict['entryfield_name'],
                       'Give the name to a molecule to' + \
                       ' reflect the isotope substitution.')
    self._balloon.bind(self._varsdict['listbox'],
                       'List of atoms with custom isotope(s).')

  def _command(self, btn_name) :
    """Handler for the button events."""      
    self.deactivate()
    self.interior().tk.call('update')
    
    if resources.STRING_BUTTON_OK == btn_name :
      self.__execute_ok()
      
    else :
      if callable(self._smartdict['cancel_command']) :
        self._smartdict['cancel_command']()

  def __execute_ok(self) :
    """
    Execute.
    """
    if callable(self._smartdict['ok_command']) :
      if 0 < len(self.__affected_atoms) :
        self._smartdict['ok_command'](
          array(self.__affected_atoms, 'l'),
          self._varsdict['var_molecule_name'].get())
        
      else :
        self._smartdict['ok_command'](
          None, self._varsdict['var_molecule_name'].get())

  def __ask_element_isotope(self, num, atom_index) :
    """Ask the user to specify a certain isotope for a picked atom.
    
    Callback for the Ok-button of pyviblib.gui.widgets.MoleculeRenderWidget.
    atom_index is 0-based !!!
    
    """
    # processing only left button
    # do not pick twice
    if 1 == num :
      if self.__is_atom_affected(1 + atom_index) :
        return
        
      atomno = self.__molecule.elements[1 + atom_index].atomno
      
      ok_command = misc.Command(self.__append_element, atom_index)
      dlg = ElementIsotopeDialog(self.interior(),
                                 atomno,
                                 1 + atom_index,
                                 ok_command=ok_command,
                                 cancel_command=self.__depick_atom)
      dlg.show()                                 

  def __append_element(self, data, atom_index) :
    """Append an atom to the list of affected atoms.
    
    Callback for the Ok-button of ElementIsotopeDialog.
    atom_index is null-based !!!
    
    """
    if data is None :
      return

    # current operation
    atoms_to_pick = []
    mass = data['mass']

    if data['use_for_all'] :
      atomno = self.__molecule.elements[1+atom_index].atomno
      
      for atom in self.__molecule.atoms :
        if atomno == atom.element.atomno :
          atoms_to_pick.append(atom.index)
    else :
      atoms_to_pick.append(1+atom_index)

    # avoid duplicate entries in the list
    # add only atoms which are not present
    for a in atoms_to_pick :
      if not self.__is_atom_affected(a) :
        self.__affected_atoms.append([a, mass])
        self.__add_to_listbox(a, self.__molecule.elements[a].symbol, mass)

        # picked the added atom
        self._varsdict['renderWidget'].pick_atoms( (a-1,) )
    #
    self.__update_GUI()
    
  def __depick_atom(self, atom_index) :
    """Callback for the Cancel-button of ElementIsotopeDialog.

    Depick a picked atom since the operation was canceled.
    atom_index is 0-based.
    
    """
    self._varsdict['renderWidget'].depick_atoms((-1,))    

  def __is_atom_affected(self, index) :
    """Whether an atom is already saved in the affected atoms list.

    index is one-based.
    
    """
    for p in self.__affected_atoms :
      if index == p[0] :
        return True

    return False

  def __add_to_listbox(self, atom_index, symbol, mass) :
    """Add a specified entry to the listbox.

    atom_index is one-based (just for information).
    
    """
    self._varsdict['listbox'].insert(
      'end', '%s # %d    %f' % (symbol, atom_index, mass))

  def __remove(self) :
    """Remove the selected atoms from the list."""
    all_elements = self._varsdict['listbox'].get()
    sel_indices, notsel_indices = self.__get_listbox_indices()

    # deleting from the list
    self._varsdict['listbox'].clear()
    
    for i in xrange(len(all_elements)) :
      if i not in sel_indices :
        self._varsdict['listbox'].insert('end', all_elements[i])

    # deleting from the molecule widget
    self._varsdict['renderWidget'].depick_atoms(sel_indices)

    # deleting from the list of affected atoms
    misc.remove_indices_from_list(self.__affected_atoms, sel_indices)

    # update
    self.__update_GUI()

  def __remove_all(self) :
    """Clean the list."""
    # deleting from the molecule widget
    self._varsdict['renderWidget'].depick_atoms()

    self._varsdict['listbox'].clear()
    self.__affected_atoms = []

    self.__update_GUI()

  def __get_listbox_indices(self) :
    """Get selected and not selected listbox indices."""
    sel_atom_pairs = self._varsdict['listbox'].getvalue()
    all_elements   = self._varsdict['listbox'].get()

    sel_indices    = []
    notsel_indices = []

    for i in xrange(len(all_elements)) :
      if all_elements[i] in sel_atom_pairs :
        sel_indices.append(i)
      else :
        notsel_indices.append(i)

    return sel_indices, notsel_indices

  def __highlight_affected_atoms(self) :
    """Highlight affected atoms in the molecule widget."""
    sel_indices, notsel_indices = self.__get_listbox_indices()

    self._varsdict['renderWidget'].highlight_picked_atoms(sel_indices, True)
    self._varsdict['renderWidget'].highlight_picked_atoms(notsel_indices, False)

    self._varsdict['renderWidget'].Render()
    self.__update_GUI()
    
  def __update_GUI(self) :
    """"""
    # block the remove button if nothing selected
    if 0 < len(self._varsdict['listbox'].getvalue()) :
      state = 'normal'
    else :
      state = 'disabled'

    self._varsdict['btn_remove'].configure(state=state)

    # block the remove all button if no items in the listbox
    if 0 < len(self.__affected_atoms) :
      state = 'normal'
    else :
      state = 'disabled'

    self._varsdict['btn_remove_all'].configure(state=state)
        

class ElementIsotopeDialog(BaseDialog) :
  """Dialog for selecting an isotope for an element."""

  def __init__(self, master, atomno, atom_index, **kw) :
    """Constructor of the class.

    Positional arguments :
    master         -- parent widget
    atomno         -- atomic number of the element.
    atom_index     -- number of the atom in the molecule (one-based)

    Keyword arguments :
    ok_command     -- command for the Ok button (default None)
                      callable with one argument being a dictionary with the
                      following keys :
                        mass        : mass of the element
                        use_for_all : whether to use for all such elements
                        
    cancel_command -- command for the Cancel button (default None)
                      callable with one argument being the null-based atom index
    
    """
    self.__atomno      = atomno
    self.__atom_index  = atom_index
    
    BaseDialog.__init__(self,
                        master,
                        buttons=resources.STRINGS_BUTTONS_OK_CANCEL,
                        defaultbutton=resources.STRING_BUTTON_OK,
                        title='Element isotopes',
                        **kw)

  def _init_vars(self) :
    """Initialize variables."""
    pass
    
  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    # find an element
    self.__element = pse.find_element_by_atomno(self.__atomno)
    
    if self.__element is None :
      raise ConstructorError(
        'Element with the atomic number %d was not found' % self.__atomno)

    var_element = Tkinter.StringVar()
    var_element.set('%s # %d' % (self.__element.symbol, self.__atom_index))
    
    widget = Pmw.EntryField(self.interior(),
                            labelpos='w',
                            label_text='Element',
                            entry_textvariable=var_element,
                            entry_state='readonly')
    self._varsdict['entryfield_element'] = widget
    self._varsdict['entryfield_element'].grid(row=0, column=0, columnspan=2,
                                              padx=3, pady=3, sticky='we')

    # selection between known isotopes and the user-definied input
    self._varsdict['radio_mass'] = Pmw.RadioSelect(self.interior(),
                                                   buttontype='radiobutton',
                                                   orient='vertical')
    self._varsdict['radio_mass'].grid(row=1, column=0, rowspan=2,
                                      padx=3, pady=3, sticky='w')

    self._varsdict['radio_mass'].add('Isotope')
    self._varsdict['radio_mass'].add('User defined')
    
    self._varsdict['radio_mass'].invoke('Isotope')
    self._varsdict['radio_mass'].configure(command=self.__update_radio)

    # option menu with the known isotops
    widget = Pmw.OptionMenu(self.interior(),
                            items=self.__element.isotopes,
                            menubutton_width=10,
                            command=None)
    self._varsdict['options_isotopes'] = widget
    self._varsdict['options_isotopes'].grid(row=1, column=1,
                                            padx=3, pady=3, sticky='w')
    # entry field for the user definied mass
    self._varsdict['var_mass'] = Tkinter.DoubleVar()
    self._varsdict['var_mass'].set(self.__element.standard_weight)

    widget = Pmw.EntryField(self.interior(),
                            entry_textvariable=self._varsdict['var_mass'],
                            entry_width=16,
                            modifiedcommand=self.__update_GUI,
                            entry_state='readonly')
    self._varsdict['entryfield_mass'] = widget
    self._varsdict['entryfield_mass'].grid(row=2, column=1,
                                           padx=5, pady=3, sticky='w')
    # use for all atoms checkbox
    self._varsdict['var_use_for_all'] = Tkinter.IntVar()
    self._varsdict['var_use_for_all'].set(False)
    
    widget = Tkinter.Checkbutton(self.interior(),
                                 text='Use for all elements of this type',
                                 variable=self._varsdict['var_use_for_all'],
                                 command=None)
    self._varsdict['check_use_for_all'] = widget
    self._varsdict['check_use_for_all'].grid(row=3, column=0, columnspan=2,
                                             padx=3, pady=3, sticky='w')

    # update
    self.__update_GUI()
    
  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    self._balloon.bind(self._varsdict['entryfield_element'], 'Element.')
    self._balloon.bind(self._varsdict['options_isotopes'],
                       'List of known isotopes for the element.')
    self._balloon.bind(self._varsdict['entryfield_mass'],
                       'User definied for the element.')
    self._balloon.bind(self._varsdict['check_use_for_all'],
                       'Check if the selected mass should be used for ' + \
                       'all such elements in a molecule.')

  def _command(self, btn_name) :
    """Handler for the button events."""
    self.withdraw()
    
    if resources.STRING_BUTTON_OK == btn_name :
      if callable(self._smartdict['ok_command']) :
        # packing
        data = dict(mass=self.__get_mass(),
                    use_for_all=self._varsdict['var_use_for_all'].get())        
        self._smartdict['ok_command'](data)
        
    elif 'Cancel' == btn_name :
      if callable(self._smartdict['cancel_command']) :
        self._smartdict['cancel_command'](self.__atom_index-1)

  def __update_radio(self, tag) :
    """Command for the radio buttons control."""
    if 'Isotope' == tag :
      self._varsdict['options_isotopes'].configure(menubutton_state='normal')
      self._varsdict['entryfield_mass'].configure(entry_state='readonly')      
    else :
      self._varsdict['options_isotopes'].configure(menubutton_state='disabled')
      self._varsdict['entryfield_mass'].configure(entry_state='normal')

      self._varsdict['var_mass'].set(self.__element.standard_weight)

  def __update_GUI(self) :
    """Check validity of the user input and enable/disable the Ok-button."""
    state = 'normal'

    # mass must be a positive number
    if 'User defined' == self._varsdict['radio_mass'].getvalue() :
      try :
        val = self._varsdict['var_mass'].get()

        if 0. >= val :
          state = 'disabled'
      except :
        state = 'disabled'
    else :
      state = 'normal'
    
    self.component('buttonbox').button(0).configure(state=state)

  def __get_mass(self) :
    """Return the mass of the element selected by the user."""
    if 'User defined' == self._varsdict['radio_mass'].getvalue() :
      return self._varsdict['var_mass'].get()
    else :
      return float(self._varsdict['options_isotopes'].getvalue())


class SnapshotDialog(BaseDialog) :
  """Dialog for making a snapshot of a render widget."""

  def __init__(self, master, **kw) :
    """
    Positional arguments :
    master          -- parent widget
    
    Keyword arguments :
    mode            -- open a file or a directory (default 'file')
    renderWidget    -- use it instead of ok_command if given (default None)
    vtk_resolution  -- initial value of the vtk resolution (default)
    background      -- initial value of the render widget background (default)
    ok_command      -- command for the ok button (default None)
                       if renderWidget is supplied, no need to specify this
                       callback
    cancel_command  -- command for the cancel button (default None)
    
    """
    BaseDialog.__init__(self,
                        master,
                        buttons = resources.STRINGS_BUTTONS_OK_CANCEL,
                        defaultbutton=resources.STRING_BUTTON_OK,
                        title='Snapshot settings',
                        **kw)

  def _init_vars(self) :
    """Initialize variables."""
    # mode of the dialog 
    self._smartdict['mode'] = 'file'
    if self._smartdict['mode'] not in ('file', 'dir') :
      raise ConstructorError(
        'Invalid dialog mode : %s' % self._smartdict['mode'])

    # for convenience
    self._smartdict.kw['initialdir'] = self._smartdict['initialdir'] or \
                                       os.getcwd()

    if self._smartdict['renderWidget'] is not None :
      self._smartdict['initialfile'] = \
        self._smartdict['initialfile'] or \
        self._smartdict['renderWidget'].molecule.name

    # initial value of the VTK resolution
    if self._smartdict['renderWidget'] is not None :
      self._smartdict['vtk_resolution'] = \
          self._smartdict['vtk_resolution'] or \
          self._smartdict['renderWidget'].resolution
    else :
      self._smartdict['vtk_resolution'] = 30
    
  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    self.interior().grid_rowconfigure(0, weight=1)
    self.interior().grid_columnconfigure(0, weight=1)
    
    frm_image = Tkinter.Frame(self.interior())
    frm_image.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky='we')

    frm_image.grid_rowconfigure(0, weight=1)
    frm_image.grid_rowconfigure(1, weight=1)
    frm_image.grid_columnconfigure(1, weight=1)

    # image on the left of settings
    label_image = Tkinter.Label(frm_image,
                                image=getimage('snapshot2'))
    label_image.grid(row=0, column=0, rowspan=3, padx=3, pady=3, sticky='w')    
    
    # image format
    widget = Pmw.OptionMenu(frm_image,
                            labelpos='w',
                            label_text='Image format',
                            labelmargin=3,
                            items=resources.STRINGS_VTK_SNAPSHOT_FORMATS,
                            command=self.__change_format)
    self._varsdict['options_format'] = widget
    self._varsdict['options_format'].grid(row=0, column=1, columnspan=2,
                                          padx=3, pady=3, sticky='we')

    # image resolution
    widget = Pmw.OptionMenu(frm_image,
                            labelpos='w',
                            label_text='Resolution',
                            labelmargin=3,
                            items=resources.NUMS_VTK_SCREENSHOT_RESOLUTIONS)
    self._varsdict['options_res'] = widget
    self._varsdict['options_res'].grid(row=1, column=1, columnspan=2,
                                       padx=3, pady=3, sticky='we')

    # VTK resolution : reflects the quality
    validate = dict(validator='integer',
                    min=resources.NUM_RESOLUTION_VTK_MIN,
                    max=resources.NUM_RESOLUTION_VTK_MAX)
    widget = Pmw.Counter(frm_image,
                         labelpos='w',
                         label_text='VTK resolution',
                         labelmargin=5,
                         entry_width=3,
                         datatype=dict(counter='integer'),
                         entryfield_value=self._smartdict['vtk_resolution'],
                         entryfield_validate=validate,
                         entry_state='readonly',
                         increment=1)
    self._varsdict['counter_res'] = widget
    self._varsdict['counter_res'].grid(row=2, column=1, padx=3, pady=3,
                                       sticky='w')

    # restore the original resolution (default : no)
    self._varsdict['var_restore_res'] = Tkinter.IntVar()
    self._varsdict['var_restore_res'].set(0)
    
    widget = Tkinter.Checkbutton(frm_image,
                                 text='Restore the original VTK resolution',
                                 variable=self._varsdict['var_restore_res'])
    self._varsdict['check_restore_res'] = widget
    self._varsdict['check_restore_res'].grid(row=2, column=2,
                                             padx=3, pady=3, sticky='w')
    # background
    if self._smartdict['renderWidget'] is not None :
      initialbg = self._smartdict['background'] or \
                  self._smartdict['renderWidget'].background
    else :
      initialbg = resources.COLOR_MOLECULE_WINDOW_BG
      
    widget = widgets.ChooseColorWidget(frm_image,
                                       text='Background ',
                                       label_width=12,
                                       initialcolor=initialbg,
                                       sticky='we')
    self._varsdict['widget_bg_color'] = widget
    self._varsdict['widget_bg_color'].grid(row=3, column=1,
                                           padx=3, pady=3, sticky='we')
    # restore the original background
    self._varsdict['var_restore_bg'] = Tkinter.IntVar()
    self._varsdict['var_restore_bg'].set(0)
    
    widget = Tkinter.Checkbutton(frm_image,
                                 text='Restore the original background',
                                 variable=self._varsdict['var_restore_bg'])
    self._varsdict['check_restore_bg'] = widget
    self._varsdict['check_restore_bg'].grid(row=3, column=2,
                                            padx=3, pady=3, sticky='w')    
    # aligning the GUI controls
    Pmw.alignlabels((self._varsdict['options_format'],
                     self._varsdict['options_res'],
                     self._varsdict['counter_res']))

    # file or directory label
    self._varsdict['var_filename'] = Tkinter.StringVar()

    if 'file' == self._smartdict['mode'] :
      label_text = 'File name :'
    else :
      label_text = 'Directory :'
      self._varsdict['var_filename'].set(self._smartdict['initialdir'])

    widget = Pmw.EntryField(self.interior(),
                            labelpos='w',
                            label_text=label_text,
                            labelmargin=3,
                            entry_width=50,
                            entry_textvariable=self._varsdict['var_filename'],
                            entry_state='readonly')
    self._varsdict['entryfield_filename'] = widget
    self._varsdict['entryfield_filename'].grid(row=1, column=0,
                                               padx=3, pady=3, sticky='we')
    # open button
    widget = Tkinter.Button(self.interior(),
                            image=getimage('open_dir2'),
                            command=self.__open,
                            relief='flat',
                            overrelief='raised')
    self._varsdict['btn_open'] = widget
    self._varsdict['btn_open'].grid(row=1, column=1, padx=5, pady=3, sticky='e')

    #
    self.__updateGUI()
  
  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    self._balloon.bind(self._varsdict['options_format'], 'Supported formats.')
    self._balloon.bind(self._varsdict['options_res'],
                       'Resolution of the image in dots per inch (DPI)')
    self._balloon.bind(self._varsdict['counter_res'],
                       'VTK resolution reflecting the quality of rendering.')
    self._balloon.bind(self._varsdict['entryfield_filename'], 'Location.')
    self._balloon.bind(self._varsdict['btn_open'], 'Open the save location.')

  def _command(self, btn_name) :
    """Handler for the button events."""
    self.withdraw()
    
    kw = self.__callback_kw()
    
    if resources.STRING_BUTTON_OK == btn_name :
      if self._smartdict['renderWidget'] is not None :
        self.__save_snapshot(**kw)
        
      elif callable(self._smartdict['ok_command']) :
        self._smartdict['ok_command'](**kw)
        
    elif resources.STRING_BUTTON_CANCEL == btn_name :
      if callable(self._smartdict['cancel_command']) :
        self._smartdict['cancel_command']()

  def __callback_kw(self) :
    """Get the keywords for the Ok button."""
    vtk_resolution = int(
      self._varsdict['counter_res'].component('entryfield').getvalue())
    
    kw = dict(format=self._varsdict['options_format'].getvalue(),
              resolution=self._varsdict['options_res'].getvalue(),
              vtk_resolution=vtk_resolution,
              location=self._varsdict['var_filename'].get(),
              initialdir=self._smartdict['initialdir'],
              restore_res=self._varsdict['var_restore_res'].get(),
              background=self._varsdict['widget_bg_color'].color,
              restore_bg=self._varsdict['var_restore_bg'].get())

    return kw
        
  def __open(self) :
    """
    Open button handler.
    """
    if 'file' == self._smartdict['mode'] :
      extension = '.' + self._varsdict['options_format'].getvalue().lower()
      if '.tiff' == extension :
        extension = '.tif'

      # initial filename is always with an explicit extension
      initialfile = self._smartdict['initialfile'] + extension

      # determining the filetype
      i = self._varsdict['options_format'].index(
        self._varsdict['options_format'].getvalue())
      filetypes = [resources.LIST_VTK_SNAPSHOT_FILETYPES[i],
                   (resources.STRING_FILETYPE_ALLFILES_DESCRIPTION, '*')]
      
      filename = tkFileDialog.asksaveasfilename(parent=self.interior(),
                                                filetypes=filetypes,
                                                defaultextension=extension,
                                                initialfile=initialfile,
                                                initialdir=\
                                                self._smartdict['initialdir'])
    else :
      filename = tkFileDialog.askdirectory(parent=self.interior(),
                                           initialdir=\
                                           self._smartdict['initialdir'])

    if filename :
      # adding the extension explicitely
      if 'file' == self._smartdict['mode'] and \
         not filename.lower().endswith(extension) :
        filename = ''.join((filename, extension))
      
      self._varsdict['var_filename'].set(filename)
      
      if 'file' == self._smartdict['mode'] :
        self._smartdict.kw['initialdir'] = os.path.dirname(filename)
      else :
        self._smartdict.kw['initialdir'] = filename

    self.__updateGUI()

  def __change_format(self, format) :
    """Called when the user changes the image format.

    Append the extension to the chosen filename.
    
    """
    name, ext = os.path.splitext(self._varsdict['var_filename'].get())

    if 0 == len(name) or 'file' != self._smartdict['mode'] :
      return
    
    if ext != format :
      if 'tiff' == format :
        format = 'tif'
        
      self._varsdict['var_filename'].set('%s.%s' % (name, format))

    self.__updateGUI()

  def __updateGUI(self) :
    """Block the ok button unless the location selected."""
    state = 'normal'
    if 0 == len(self._varsdict['var_filename'].get()) :
      state = 'disabled'

    self.component('buttonbox').button(0).configure(state=state)

  def __save_snapshot(self, **kw) :
    """
    Callback for the Ok button if the renderWidget is given
    """
    if self._smartdict['renderWidget'] is None :
      return

    # do it explicitely
    self.interior().tk.call('update')

    renderWidget = self._smartdict['renderWidget']

    # background
    old_bg = renderWidget.background
    renderWidget.background = kw['background']

    # appropriate extension for the TIFF format
    extension = kw['format'].lower()
    if 'tiff' == extension :
      extension = 'tif'

    # magnification
    current_DPI   = renderWidget.GetRenderWindow().GetDPI()
    magnification = int(round(float(kw['resolution'])/float(current_DPI)))
    
    old_vtk_resolution = renderWidget.resolution

    # save
    renderWidget.snapshot(kw['location'],
                          format=kw['format'],
                          magnification=magnification,
                          resolution=kw['vtk_resolution'])

    # restoring the original vtk resolution & background
    if kw['restore_res'] :
      renderWidget.resolution = old_vtk_resolution

    if kw['restore_bg'] :
      renderWidget.background = old_bg

    renderWidget.Render()
  

class DefineGroupsDialog(BaseDialog) :
  """Dialog for defining groups in a molecule.

  The following read-only property is exposed :
      renderWidget -- render widget

  """

  def __init__(self, master, mol, **kw) :
    """Constructor of the class.

    Positional arguments :
    master         -- parent widget
    mol            -- molecule
    
    Keyword arguments :
    ok_command     -- command for the Ok button (default None)
                      callable with one argument being a list of groups where
                      atom indices are null-based
    cancel_command -- command for the Cancel button (default None)
                      callable without arguments
                      
    """
    if not isinstance(mol, molecule.Molecule) :
      raise ConstructorError('Invalid mol argument')

    self.__molecule   = mol
    
    BaseDialog.__init__(self,
                        master,
                        buttons = resources.STRINGS_BUTTONS_OK_CANCEL,
                        defaultbutton=resources.STRING_BUTTON_OK,
                        title='Define groups',
                        **kw)

  def _init_vars(self) :
    """Initialize variables."""
    pass

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    # top : help    
    help_text = 'To add a group :\n' + \
                '  1) Press the "add a group" button\n' + \
                '  2) Click on atoms in the window with the molecule\n' + \
                '  3) Press the "complete group" button'
    
    info_widget = widgets.InfoWidget(self.interior(),
                                     text=help_text,
                                     height=4)
    info_widget.grid(row=0, column=0, columnspan=2,
                     padx=3, pady=3, sticky='we')

    ## middle : button toolbar
    btn_toolbar = widgets.ButtonToolbar(self.interior())
    btn_toolbar.grid(row=1, column=0, padx=3, pady=3, sticky='w')

    # snapshot
    btn_toolbar.add_button(imagename='snapshot',
                           command=self.__snapshot,
                           helptext='Save a snapshot of the render window.')

    # size of the render widget
    self._varsdict['var_renderwidget_size'] = Tkinter.StringVar()    
    btn_kw = dict(textvariable=self._varsdict['var_renderwidget_size'],
                  justify='center',
                  helptext='Current size of the render widget.')
    btn_size = btn_toolbar.add_button(**btn_kw)
    btn_size.configure(overrelief='flat')  
    
    # bottom left : window with the molecule
    self.interior().grid_rowconfigure(2, weight=1)
    self.interior().grid_columnconfigure(0, weight=1)
    
    group_mol = Pmw.Group(self.interior(), tag_text='Molecule')
    group_mol.grid(row=2, column=0, padx=3, pady=3, sticky='news')

    group_mol.interior().grid_rowconfigure(0, weight=1)
    group_mol.interior().grid_columnconfigure(0, weight=1)

    # installing the camera if given
    # setting resolution
    resolution = self._smartdict['resolution'] or resources.NUM_RESOLUTION_VTK
    bonds_mode = resources.NUM_MODE_BONDS_MONOLITH_COLOR,
    widget = widgets.MoleculeRenderWidget(group_mol.interior(),
                                          molecule=self.__molecule,
                                          resolution=resolution,
                                          bonds_mode=bonds_mode,
                                          width=400,
                                          height=400)
    self._varsdict['renderWidget'] = widget
    self._varsdict['renderWidget'].grid(row=0, column=0, padx=3, pady=3,
                                        sticky='news')

    # adding command to the "size button"
    command = misc.Command(self._change_render_widget_size,
                           self._varsdict['renderWidget'])
    btn_size.configure(command=command)

    if self._smartdict['camera'] is not None :
      self._varsdict['renderWidget'].camera = self._smartdict['camera']

    self._varsdict['renderWidget'].do_picking = False
    self._varsdict['renderWidget'].clicked_atom_callback = self.__clicked_atom

    # bottom right : scrolled frame for results + button toolbar    
    group_groups = Pmw.Group(self.interior(), tag_text='Groups')
    group_groups.grid(row=2, column=1, padx=3, pady=3, sticky='n')

    group_groups.interior().grid_rowconfigure(0, weight=1)
    group_groups.interior().grid_columnconfigure(0, weight=1)

    # scrolled frame
    self._varsdict['frm_groups'] = Pmw.ScrolledFrame(group_groups.interior(),
                                                     usehullsize=True,
                                                     hull_width=150,
                                                     hull_height=200,
                                                     horizflex='fixed',
                                                     vertflex='fixed')
    self._varsdict['frm_groups'].grid(row=0, column=0, padx=3, pady=3,
                                      sticky='news')
    # collected added groups in a list
    # each added group is a frame consisting of :
    # a) checkbox (Group 1, etc)
    # b) read-only entryfield with a list of atoms in the group
    # c) label with a color
    self._varsdict['frames_list'] = []
    self._varsdict['vars_list'] = []
    self._varsdict['current_picked_list'] = []

    # saving the information about groups : [color_html, atoms_list]
    self._varsdict['groups'] = []

    # group button toolbar :
    # add a group, finish group, remove groups, remove all, save, load list
    btn_toolbar = self.__constructButtonToolbar(group_groups.interior())
    btn_toolbar.grid(row=0, column=1, padx=3, pady=3, sticky='ne')
    
    ## load the initial group if set
    if self._smartdict['groups'] is not None :
      self.__replace_groups(self._smartdict['groups'])

  def _declare_properties(self) :
    """Declare properties of the widget."""
    self.__class__.renderWidget = property(fget=misc.Command(
      misc.Command.fget_value, self._varsdict['renderWidget']))

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    pass

  def _bind_events(self) :
    """Bind events."""
    self.bind('<Configure>', self.__Configure)

  def __Configure(self, e) :
    """<Configure> event handler."""
    self._varsdict['var_renderwidget_size'].set(
      '%dx%d' % self._varsdict['renderWidget'].GetRenderWindow().GetSize())

  def _command(self, btn_name) :
    """Handler for the button events."""
    self.withdraw()
    self.interior().tk.call('update')

    if btn_name is None :
      return
    
    if resources.STRING_BUTTON_OK == btn_name :
      # concatinate the color with the null-based indices
      groups = [ [ group[0] ] + group[1] \
                 for group in self._varsdict['groups']]
              
      if callable(self._smartdict['ok_command']) :   
        self._smartdict['ok_command'](groups)
        
    else :
      if callable(self._smartdict['cancel_command']) :
        self._smartdict['cancel_command']()

  def __constructButtonToolbar(self, parent) :
    """Contruct the toolbar with the group manipulation buttons."""
    btn_toolbar = widgets.ButtonToolbar(parent, horizontal=False, style=1)
    
    widget = btn_toolbar.add_button(imagename='add',
                                    command=self.__add_group,
                                    helptext='Add a new group.')
    self._varsdict['btn_add'] = widget
    
    widget = btn_toolbar.add_button(imagename='complete',
                                    command=self.__complete_group,
                                    state='disabled',
                                    helptext='Complete the current group.')
    self._varsdict['btn_complete'] = widget

    widget = btn_toolbar.add_button(imagename='remove',
                                    command=self.__remove,
                                    state='disabled',
                                    helptext='Remove the selected groups.')
    self._varsdict['btn_remove'] = widget

    widget = btn_toolbar.add_button(imagename='remove_all',
                                    command=self.__remove_all,
                                    state='disable',
                                    padx=2,
                                    helptext='Remove all groups.')
    self._varsdict['btn_remove_all'] = widget

    widget = btn_toolbar.add_button(imagename='save',
                                    command=self.__save,
                                    state='disabled',
                                    helptext='Save the groups.')
    self._varsdict['btn_save'] = widget

    btn_toolbar.add_button(imagename='open_file',
                           command=self.__load,
                           helptext='Load groups from a file.')

    return btn_toolbar

  def __add_group(self) :
    """Start atom picking in the window."""
    self._varsdict['renderWidget'].do_picking = True

    # save the current picked atoms
    self._varsdict['current_picked_list'] = []

    # buttons
    self._varsdict['btn_add'].configure(state='disabled')
    self._varsdict['btn_complete'].configure(state='normal')
    
  def __complete_group(self, atom_list=None, color=None) :
    """Finish atom picking in the window and add information to the GUI.

    Generate a random group color unless color given.

    Take the picked atoms list unless atom_list is not given.
    
    """
    if atom_list is None :
      atom_list = self._varsdict['current_picked_list']
    
    if 0 == len(atom_list) :
      return
    
    self._varsdict['renderWidget'].do_picking = False

    # depick atoms & change their diffuse color
    self._varsdict['renderWidget'].depick_atoms()

    # save the group
    # color the atoms with a randomly generated color
    group_color = color or misc.random_color()

    self._varsdict['groups'].append([group_color, copy(atom_list)])

    self.__change_atom_colors()

    # add to GUI
    self.__add_group_frame(group_color)

    ## buttons
    # enable the "add a group" only if it is possible !
    if self.__can_add_groups() :
      self._varsdict['btn_add'].configure(state='normal')

    # group with minimum one atom can be completed !
    self._varsdict['btn_complete'].configure(state='disabled')
    self._varsdict['btn_remove_all'].configure(state='normal')
    self._varsdict['btn_save'].configure(state='normal')

  def __remove(self) :
    """Remove groups."""
    # getting the list of groups to be deleted
    to_delete = []
    for var in self._varsdict['vars_list'] :
      if var.get() :
        to_delete.append(self._varsdict['vars_list'].index(var))

    # removing from GUI
    for i in xrange(len(self._varsdict['frames_list'])) :
      if i in to_delete :
        self._varsdict['frames_list'][i].grid_forget()

    # removing from the lists
    misc.remove_indices_from_list(self._varsdict['vars_list'], to_delete)
    misc.remove_indices_from_list(self._varsdict['frames_list'], to_delete)
    misc.remove_indices_from_list(self._varsdict['groups'], to_delete)
    
    # canceling the currently picked atoms
    del self._varsdict['current_picked_list'][:]
    
    # updating GUI
    # renumber the groups
    for i in xrange(len(self._varsdict['frames_list'])) :
      check_btn = self._varsdict['frames_list'][i].grid_slaves(
        row=0, column=0)[0]
      check_btn.configure(text='Group%3d' % (1 + i))

    # updating the 3D window
    self._varsdict['renderWidget'].render_molecule(
      bonds_mode=resources.NUM_MODE_BONDS_MONOLITH_COLOR)
    self.__change_atom_colors()

    # buttons
    self._varsdict['btn_add'].configure(state='normal')
    self._varsdict['btn_complete'].configure(state='disabled')
    self._varsdict['btn_remove'].configure(state='disabled')

    # if there is minimum one group, one can delete it and save it.
    if 0 < len(self._varsdict['groups']) :
      state = 'normal'
    else :
      state = 'disabled'
    self._varsdict['btn_remove_all'].configure(state=state)
    self._varsdict['btn_save'].configure(state=state)

  def __remove_all(self) :
    """Remove all groups."""
    # rendering molecule
    self._varsdict['renderWidget'].render_molecule(
      bonds_mode=resources.NUM_MODE_BONDS_MONOLITH_COLOR)
    self._varsdict['renderWidget'].Render()
    
    # removing from the gui
    for frame in self._varsdict['frames_list'] :
      frame.grid_remove()

    del self._varsdict['frames_list'][:]
    del self._varsdict['vars_list'][:]

    # cleaning the groups
    del self._varsdict['groups'][:]

    # cleaning the list of currently picked atoms
    del self._varsdict['current_picked_list'][:]

    # buttons
    self._varsdict['btn_add'].configure(state='normal')
    self._varsdict['btn_complete'].configure(state='disabled')
    self._varsdict['btn_remove'].configure(state='disabled')
    self._varsdict['btn_remove_all'].configure(state='disabled')
    self._varsdict['btn_save'].configure(state='disabled')

  def __save(self) :
    """Save groups in a *.grp file.

    Colors will be saved as the first field.
    
    """
    filetypes = [(resources.STRING_FILETYPE_GROUPFILE_DESCRIPTION, '*.grp')]
    
    filepattern = tkFileDialog.SaveAs(parent=self.interior(),
                                      filetypes=filetypes,
                                      defaultextension='.grp').show()

    if filepattern is not None :
      # dump the list of groups
      # atom indices are one-based
      file_ = open(filepattern, 'w+')

      for group in self._varsdict['groups'] :
        # first field is the color of the group
        group_str = '%s' % group[0]

        # then one-based list of indices
        for a in group[1] :
          group_str = ''.join((group_str, ' %d ' % (1 + a)))
          
        group_str = ''.join((group_str, '\n'))
        file_.write(group_str)

      file_.close()

  def __load(self) :
    """Load groups from a *.grp file.

    Colors can be optionally present in the first column.
    Unless specified the random colors will be used.
    
    """    
    filetypes = [(resources.STRING_FILETYPE_GROUPFILE_DESCRIPTION, '*.grp')]

    filepattern = tkFileDialog.Open(parent=self.interior(),
                                    filetypes=filetypes,
                                    ).show()

    if filepattern :
      # read the list of groups
      # atom indices are one-based
      try :
        file_ = open(filepattern, 'r')

        # each group : [color, atomnumbers]
        groups = []

        for line in file_.readlines() :
          line = line.strip()
          vals = line.split()
          
          group = []

          # if the first field starts with '#' it is considered
          # to be the group color
          group_color = None
          starti      = 0
          if vals[0].startswith('#') :
            # the group has to have at least 1 atom
            if 2 > len(vals) :
              raise ParseError(
                filepattern, 'A group has to have at least one atom, 0 found')

            # try to read the color
            try :
              misc.color_html_to_RGB(vals[0])
            except :
              raise ParseError(
                filepattern, 'Invalid color for the group %d : %s' % \
                (1+len(groups), vals[0]))
            
            else :
              group_color = vals[0]
              starti      = 1

          group.append(group_color)
            
          # reading one-based atom numbers
          # saving the null-based atom numbers
          for val in vals[starti:] :
            if not val.isdigit() :
              raise ParseError(
                filepattern,
                r'Invalid atom number(s) found in the line "%s"' % line)

            val = int(val)
            if 0 >= val or self.__molecule.Natoms < val :
              raise ParseError(filepattern, 'Invalid atom number %d' % val)

            group.append(val - 1)
            
          groups.append(group)

        #
        file_.close()

        self.__replace_groups(groups)

      except :
        widgets.show_exception(sys.exc_info())

  def __replace_groups(self, grps) :
    """Replace the current groups with a given list.

    grps is a null-based list of lists of
    [group_color & null-based atom indices]
    
    useful during loading of groups.
    
    """
    # load the groups in GUI
    self.__remove_all()

    for grp in grps :
      self.__complete_group([ a for a in grp[1:] ], color=grp[0])

    # check if addition of new groups is available
    if self.__can_add_groups() :
      state = 'normal'
    else :
      state = 'disabled'

    self._varsdict['btn_add'].configure(state=state)   

  def __clicked_atom(self, num, atom_index) :
    """Callback for the molecule widget."""
    if 1 != num or not self._varsdict['renderWidget'].do_picking or \
       atom_index in self._varsdict['current_picked_list'] :
      return

    # an atom can be a member only of one group
    atom_node = self._varsdict['renderWidget'].get_node('atoms', atom_index)

    if atom_node.get_pickable() :
      # one atom should be clickable only one time !
      atom_node.set_pickable(False)

      # saving to the list
      self._varsdict['current_picked_list'].append(atom_index)

  def __add_group_frame(self, color) :
    """Create a frame for a given atom list and a label color.
    
    Add it to GUI and save in the list of frames.
    atom_list : a list of null-based indices.
    color     : html color for the label
    """
    group_no = len(self._varsdict['frames_list'])

    # this guarantees that the frame to be added will be last !
    if 0 == group_no :
      row = 0
    else :
      row = int(self._varsdict['frames_list'][group_no - 1].grid_info()['row'])
      row += 1

    frame = Tkinter.Frame(self._varsdict['frm_groups'].interior())
    frame.grid(row=row, column=0, padx=3, pady=3, sticky='n')

    # saving to the list
    self._varsdict['frames_list'].append(frame)

    # checkbox "Group n"
    var = Tkinter.IntVar()
    self._varsdict['vars_list'].append(var)
    
    checkbox = Tkinter.Checkbutton(frame,
                                   text='Group%3d' % (1 + group_no),
                                   command=self.__checkbutton_group,
                                   variable=var)
    checkbox.grid(row=0, column=0, padx=3, pady=3, sticky='w')

    # button with the color
    # the user can modify it
    btn_color = Tkinter.Button(frame,
                               width=3,
                               bg=color,
                               activebackground=color)
    btn_color.grid(row=0, column=1, padx=3, pady=3, sticky='w')

    btn_color.configure(
      command=misc.Command(self.__change_group_color, btn_color))

  def __change_atom_colors(self) :
    """Change the diffuse colors of atoms."""    
    for group in self._varsdict['groups'] :
      for a in group[1] :
        # making a copy of a material & changing the diffuse color
        material = copy(self.__molecule.elements[1 + a].material)
        material.diffuse_color = misc.color_html_to_RGB(group[0])

        # applying to the current atom
        # it cannot be pickable anymore !
        node = self._varsdict['renderWidget'].get_node('atoms', a)
        node.set_material(material)
        node.set_pickable(False)

    self._varsdict['renderWidget'].Render()

  def __change_group_color(self, btn) :
    """Change the color of the button."""
    group_no = self.__find_button_group(btn)
    
    if -1 != group_no :
      title = 'Choose the color for the group %d' % (1 + group_no)
      color_chosen = tkColorChooser.Chooser(parent=self.interior(),
                                            initialcolor=btn.cget('bg'),
                                            title=title).show()
      if color_chosen[0] is not None :
        btn.configure(bg=color_chosen[1], activebackground=color_chosen[1])
        self._varsdict['groups'][group_no][0] = color_chosen[1]

        self.__change_atom_colors()

  def __find_button_group(self, btn) :
    """Find the index of the group for a button in the frame list."""
    for frame in self._varsdict['frames_list'] :
      if frame.grid_slaves(row=0, column=1)[0] == btn :
        return self._varsdict['frames_list'].index(frame)

    return -1

  def __can_add_groups(self) :
    """If groups can be added."""
    sum_ = 0
    for group in self._varsdict['groups'] :
      sum_ += sum(group[1]) + len(group[1])

    n = self.__molecule.Natoms

    return sum_ < n * (n + 1) / 2

  def __snapshot(self) :
    """Ask the user about the screenshot settings.
    
    Ask for a directory where files are to be saved.
    
    """
    dlg = SnapshotDialog(self.interior(),
                         mode='file',
                         renderWidget=self._varsdict['renderWidget'])
    dlg.show()
     
  def __checkbutton_group(self) :
    """Called when the checkbutton of a group was pressed."""
    if 0 < self.__count_checked_groups() :
      state = 'normal'
    else :
      state = 'disabled'

    self._varsdict['btn_remove'].configure(state=state)

  def __count_checked_groups(self) :
    """The number of checked groups."""
    c = 0
    for var in self._varsdict['vars_list'] :
      if var.get() :
        c += 1
      
    return c
  

class AnimationSettingsDialog(BaseDialog) :
  """Dialog for saving animations of vibrations."""

  def __init__(self, molWindow) :
    """Constructor of the class.

    Positional arguments :
    molWindow -- reference to the molecule window
    
    """
    self.__molWindow = molWindow
    
    BaseDialog.__init__(self,
                        molWindow,
                        buttons=resources.STRINGS_BUTTONS_OK_CANCEL,
                        defaultbutton=resources.STRING_BUTTON_OK,
                        title='Save an animation')

  def _init_vars(self) :
    """Initialize variables."""
    self._smartdict['nFrames']    = 7
    self._smartdict['resolution'] = 20
    self._smartdict['speed']      = 5

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    # informational message
    self.interior().grid_columnconfigure(0, weight=1)
    self.interior().grid_rowconfigure(0, weight=1)
    
    info_text = \
      'Currently two animation formats are supported : ' + \
      'animated gifs and FLIC animations.\n\n' + \
      'Requirements :\n' + \
      '\tAnimated gifs   : gifsicle & Netpbm graphics package.\n' + \
      '\tFLIC animations : ppm2fli.\n\n' + \
      'Availability : Posix & Cygwin.'
    
    info_msg = widgets.InfoWidget(self.interior(),
                                  text=info_text,
                                  height=7,
                                  icon=False)
    info_msg.grid(row=0, column=0, columnspan=4, padx=3, pady=3, sticky='we')
    
    ## left top
    label_movie = Tkinter.Label(self.interior(),
                                image=getimage('movie'))
    label_movie.grid(row=1, column=0, rowspan=3, padx=3, pady=3, sticky='w')

    ## right top line 1 : choose between animated gif & fli
    self._varsdict['radio_type'] = Pmw.RadioSelect(self.interior(),
                                                   buttontype='radiobutton')
    self._varsdict['radio_type'].grid(row=1, column=1, padx=3, pady=3,
                                      sticky='w')

    self._varsdict['radio_type'].add('Animated GIF')
    self._varsdict['radio_type'].add('FLI')

    # checking if necessary programs are installed
    gifsicle_installed = misc.is_command_on_path('gifsicle')
    netpbm_installed  = misc.is_command_on_path('pnmcolormap') and \
                        misc.is_command_on_path('pnmremap') and \
                        misc.is_command_on_path('ppmtogif')
    ppm2fli_installed = misc.is_command_on_path('ppm2fli')
          
    # animated gif
    state_gifanim = (gifsicle_installed and netpbm_installed) and \
                    'normal' or \
                    'disabled'
    self._varsdict['radio_type'].button(0).configure(state=state_gifanim)
    if gifsicle_installed :
      self._varsdict['radio_type'].invoke('Animated GIF')

    # fli
    state_fli = ppm2fli_installed and 'normal' or 'disabled'
    self._varsdict['radio_type'].button(1).configure(state=state_fli)
    if not gifsicle_installed and ppm2fli_installed:
      self._varsdict['radio_type'].invoke('FLI')

    ## right top line 2 : number of frames, speed, quality
    self._varsdict['nFrames']    = Tkinter.IntVar()
    self._varsdict['resolution'] = Tkinter.IntVar()
    self._varsdict['speed']      = Tkinter.IntVar()
    self._varsdict['filename']   = Tkinter.StringVar()

    self._varsdict['nFrames'].set(self._smartdict['nFrames'])
    self._varsdict['resolution'].set(self._smartdict['resolution'])
    self._varsdict['speed'].set(self._smartdict['speed'])

    # number of frames
    validate = dict(validator='integer', min=1, max=66)
    widget = Pmw.Counter(self.interior(),
                         labelpos='w',
                         label_text='Number of frames :',
                         entry_width=3,
                         entry_textvariable=self._varsdict['nFrames'],
                         datatype=dict(counter='integer'),
                         entryfield_validate=validate,
                         entry_state='readonly',
                         autorepeat=True,
                         increment=1)
    self._varsdict['counter_nFrames'] = widget
    self._varsdict['counter_nFrames'].grid(row=2, column=1,
                                           padx=3, pady=3, sticky='w')

    # VTK resolution : reflects the quality
    validate = dict(validator='integer',
                    min=resources.NUM_RESOLUTION_VTK_MIN,
                    max=resources.NUM_RESOLUTION_VTK_MAX)
    widget = Pmw.Counter(self.interior(),
                         labelpos='w',
                         label_text='Resolution :',
                         entry_width=3,
                         entry_textvariable=self._varsdict['resolution'],
                         datatype=dict(counter='integer'),
                         entryfield_validate=validate,
                         entry_state='readonly',
                         autorepeat=True,
                         increment=1)
    self._varsdict['counter_res'] = widget
    self._varsdict['counter_res'].grid(row=2, column=2,
                                       padx=3, pady=3, sticky='w')
    # Animation speed
    validate = dict(validator='integer', min=0, max=100)
    widget = Pmw.Counter(self.interior(),
                         labelpos='w',
                         label_text='Delay :',
                         entry_width=3,
                         entry_textvariable=self._varsdict['speed'],
                         datatype=dict(counter='integer'),
                         entryfield_validate=validate,
                         entry_state='readonly',
                         autorepeat=True,
                         increment=1)
    self._varsdict['counter_speed'] = widget
    self._varsdict['counter_speed'].grid(row=2, column=3,
                                         padx=8, pady=3, sticky='e')
    # transparent background (applied to an animated gif)
    self._varsdict['var_transparent_bg'] = Tkinter.IntVar()
    self._varsdict['var_transparent_bg'].set(0)

    var = self._varsdict['var_transparent_bg']
    widget = Tkinter.Checkbutton(self.interior(),
                                 text='Transparent background',
                                 variable=var)
    self._varsdict['check_transparent_bg'] = widget
    self._varsdict['check_transparent_bg'].grid(row=3, column=1,
                                                padx=3, pady=3, sticky='w')
    self._varsdict['radio_type'].configure(
      command=self.__change_animation_type)

    # frame with the filename
    frame_filename = Tkinter.Frame(self.interior())
    frame_filename.grid(row=4, column=0, columnspan=4,
                        padx=3, pady=3, sticky='ew')

    frame_filename.grid_rowconfigure(0, weight=1)
    frame_filename.grid_columnconfigure(0, weight=1)

    widget = Pmw.EntryField(frame_filename,
                            labelpos='w',
                            label_text='File name : ',
                            labelmargin=3,
                            entry_textvariable=self._varsdict['filename'],
                            modifiedcommand=self.__updateGUI)
    self._varsdict['entry_filename'] = widget
    self._varsdict['entry_filename'].grid(row=0, column=0,
                                          padx=3, pady=3, sticky='ew')

    btn_open = Tkinter.Button(frame_filename,
                              image=getimage('open_dir2'),
                              relief='flat',
                              overrelief='raised',
                              command=self.__open_file)
    btn_open.grid(row=0, column=1, sticky='e', padx=3, pady=3)

    # if python supports the starting of file with its associated application
    # make a propose to the user to start the animation
    try :
      from os import startfile
    except ImportError :
      pass
    else :
      self._varsdict['openfile'] = Tkinter.IntVar()
      self._varsdict['openfile'].set(1)

      text = 'Open the resulting file upon successful completion'
      check_openfile = Tkinter.Checkbutton(self.interior(),
                                           text=text,
                                           variable=self._varsdict['openfile'])
      check_openfile.grid(row=5, column=0, columnspan=4,
                          padx=3, pady=3, sticky='w')

    # aligning the controls
    Pmw.alignlabels([self._varsdict['radio_type'],
                     self._varsdict['counter_nFrames'],
                     self._varsdict['check_transparent_bg']])
      
    self.__updateGUI()

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    self._balloon.bind(self._varsdict['counter_nFrames'],
                       'Number of frames in each direction.')
    self._balloon.bind(self._varsdict['counter_res'],
                       'VTK resolution reflecting the quality of rendering.')
    self._balloon.bind(self._varsdict['counter_speed'],
                       'Delay between frames in hundredths of a second.')
    self._balloon.bind(self._varsdict['check_transparent_bg'],
                       'Make a transparent background. Applicable to' + \
                       ' animated gifs.')
    self._balloon.bind(self._varsdict['entry_filename'],
                       'File name to the animation to.')
  
  def _command(self, btn_name) :
    """Handler for the button events."""
    self.withdraw()

    if resources.STRING_BUTTON_OK == btn_name :
      if 'openfile' in self._varsdict :
        openfile = self._varsdict['openfile']
      else :
        openfile = False

      format = self._varsdict['radio_type'].getvalue()
      transparent_bg = self._varsdict['var_transparent_bg'].get()
      
      self.__molWindow.save_animation(self._varsdict['filename'].get(),
                                      self._varsdict['nFrames'].get(),
                                      self._varsdict['resolution'].get(),
                                      self._varsdict['speed'].get(),
                                      format=format,
                                      transparent_bg=transparent_bg,
                                      openfile=openfile)

  def __updateGUI(self) :
    """Update the GUI."""
    if 0 < len(self._varsdict['filename'].get().strip()) :
      state = 'normal'
    else :
      state = 'disabled'

    # if the external programs are not install -- block
    if self._varsdict['radio_type'].getvalue() is None :
      state = 'disabled'

    self.component('buttonbox').button(0).configure(state=state)

  def __change_animation_type(self, tag) :
    """Called when the user chooses the animation type."""
    if 'Animated GIF' == tag :
      state = 'normal'
      
    else :
      state = 'disabled'

    self._varsdict['check_transparent_bg'].configure(state=state)
    
  def __open_file(self) :
    """Ask the user where the animation is to be saved."""
    initialfile = '%s_vib%d' % (self.__molWindow.molecule_name,
                                self.__molWindow.vib_toolbar.vib_no)

    if 'Animated GIF' == self._varsdict['radio_type'].getvalue() :
      filetypes       =  [(resources.STRING_FILETYPE_GIFFILE_DESCRIPTION,
                           '*.gif *.gifanim')]
      defaultextension = '.gif'
    else :
      filetypes        = [(resources.STRING_FILETYPE_FLIFILE_DESCRIPTION,
                           '*.fli *.flc')]
      defaultextension = '.fli'
    
    filename = tkFileDialog.SaveAs(parent=self.interior(),
                                   title=r'Save the animation as',
                                   filetypes=filetypes,
                                   defaultextension=defaultextension,
                                   initialfile=initialfile).show()
    if filename is not None :
      if not filename.lower().endswith(defaultextension) :
        filename = ''.join((filename, defaultextension))
        
      self._varsdict['filename'].set(filename)
      self.__updateGUI()
      

class RamanRoaDegcircCalcSettingsDialog(BaseDialog) :
  """Settings of Raman/Roa/Degree of circularity spectra.

  The following read-only property is exposed :
      figsize_inches    -- spectra canvas size

  The following public methods are exported :
      update_controls() -- update the controls of the dialog
      selectpage()      -- select a tab
      
  """
  
  def __init__(self, master, **kw) :
    """Constructor of the class.

    Positional arguments :
    master     -- parent widget
    
    Keyword arguments :
    ok_command -- callback for the Ok button (default None)
    
    """
    BaseDialog.__init__(self,
                        master,
                        buttons = resources.STRINGS_BUTTONS_OK_APPLY_CANCEL,
                        defaultbutton=resources.STRING_BUTTON_APPLY,
                        title='Spectra settings',
                        **kw)

  def _init_vars(self) :
    """Initialize variables."""
    # which spectra ?
    self._varsdict['spectra_names']    = resources.STRINGS_SPECTRA_NAMES
    self._varsdict['spectra_prefices'] = resources.STRINGS_SPECTRA_PREFICES
    self._varsdict['FIGURE_SIZES']     = ('current', 'A4')

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    ## all options are organized like tabs in a notebook
    self.interior().grid_columnconfigure(0, weight=1)
    self.interior().grid_rowconfigure(0, weight=1)
    
    self._varsdict['notebook'] = Pmw.NoteBook(self.interior())
    self._varsdict['notebook'].grid(row=0, column=0, padx=3, pady=3,
                                    sticky='news')
    ## Common tab
    tabCommon = self._varsdict['notebook'].add('Common')
    self._constructCommonTab(tabCommon)

    ## spectra tabs
    buttons_to_validate = (self.component('buttonbox').button(0),
                           self.component('buttonbox').button(1))

    for name, prefix in zip(self._varsdict['spectra_names'],
                            self._varsdict['spectra_prefices']) :
      tab = self._varsdict['notebook'].add(name)
      widget = widgets.AxesSettingsWidget(tab,
                                          add_limits='degcirc' != prefix,
                                          add_invert='roa' == prefix,
                                          buttons_to_validate=\
                                          buttons_to_validate)
      self._varsdict['axes_%s' % prefix] = widget
      self._varsdict['axes_%s' % prefix].pack(expand=True, fill='both')
      
    ## Profile tab
    tabProfile = self._varsdict['notebook'].add('Profile')
    self._constructProfileTab(tabProfile)

    ## Export tab
    tabExport = self._varsdict['notebook'].add('Export')
    self._constructExportTab(tabExport)

    ### update controls
    self._varsdict['notebook'].setnaturalsize()

  def _declare_properties(self) :
    """Declare properties of the widget."""
    self.__class__.figsize_inches = property(
      fget=self._get_figsize_inches)
    
  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    pass

  def _command(self, btn_name) :
    """Handler for the button events."""
    self.interior().tk.call('update', 'idletasks')
    
    # ok, cancel - withdraw
    if resources.STRING_BUTTON_APPLY != btn_name :
      self.withdraw()
      self.interior().tk.call('update')

    # ok, apply - apply
    if btn_name in resources.STRINGS_BUTTONS_OK_APPLY and \
      callable(self._smartdict['ok_command']) :
      self._smartdict['ok_command'](**self._get_kw())
      
  def _updateGUI(self) :
    """Check the validity of the input data."""
    state = 'normal'

    # float values
    try :
      xfrom = self._varsdict['var_xfrom'].get()
      xto   = self._varsdict['var_xto'].get()            
    except ValueError:
      state = 'disabled'      
    else :
      if xfrom == xto :
        state = 'disabled'

    # set the state of the 'Apply' & 'Ok' buttons
    self.component('buttonbox').button(0).configure(state=state)
    self.component('buttonbox').button(1).configure(state=state)

  def _constructCommonTab(self, tabCommon, add_titles=True) :
    """Construct the common tab."""
    tabCommon.grid_columnconfigure(0, weight=1)

    row = 0

    if add_titles :
      ## Group 'Compound information'
      tabCommon.grid_rowconfigure(row, weight=1)
      
      group_info = Pmw.Group(tabCommon, tag_text='Compound information')
      group_info.grid(row=row, column=0, padx=3, pady=3, sticky='nwe')
      row += 1

      group_info.interior().grid_rowconfigure(0, weight=1)
      group_info.interior().grid_columnconfigure(0, weight=1)

      self._varsdict['var_title1'] = Tkinter.StringVar()
      self._varsdict['var_title2'] = Tkinter.StringVar()

      # to restrict the number of symbols
      # title1 on the top : Arial bold 22
      var = self._varsdict['var_title1']
      entryfield_title1 = Pmw.EntryField(group_info.interior(),
                                         entry_textvariable=var,
                                         label_text='Title 1 ',
                                         labelpos='w',
                                         entry_width=25)
      entryfield_title1.grid(row=0, column=0, padx=3, pady=3, sticky='we')

      # title2 on the top : Arial 18
      var = self._varsdict['var_title2']
      entryfield_title2 = Pmw.EntryField(group_info.interior(),
                                         entry_textvariable=var,
                                         label_text='Title 2 ',
                                         labelpos='w',
                                         entry_width=25)
      entryfield_title2.grid(row=1, column=0, padx=3, pady=3, sticky='we')

    ## Group 'Plotting region'
    tabCommon.grid_rowconfigure(row, weight=1)
    
    group_pr = Pmw.Group(tabCommon, tag_text='Plotting region')
    group_pr.grid(row=row, column=0, padx=3, pady=3, sticky='nwe')
    row += 1

    group_pr.interior().grid_rowconfigure(0, weight=1)
    group_pr.interior().grid_columnconfigure(0, weight=1)
    group_pr.interior().grid_columnconfigure(1, weight=1)

    self._varsdict['var_xfrom'] = Tkinter.DoubleVar()
    self._varsdict['var_xto']   = Tkinter.DoubleVar()

    # wavenumber limits
    av_lims = figures.RamanROADegcircCalcFigure.LIM_AVAIL_WAVENUMBERS
    
    validate = dict(validator='real',
                     min=min(av_lims),
                     max=max(av_lims),
                     separator='.')
    var = self._varsdict['var_xfrom']
    entryfield_xfrom = Pmw.EntryField(group_pr.interior(),
                                      entry_textvariable=var,
                                      label_text='Wavenumbers from ',
                                      labelpos='w',
                                      entry_width=7,
                                      validate=validate,
                                      modifiedcommand=self._updateGUI)
    entryfield_xfrom.grid(row=0, column=0, padx=3, pady=3, sticky='w')

    var = self._varsdict['var_xto']
    entryfield_xto = Pmw.EntryField(group_pr.interior(),
                                    entry_textvariable=var,
                                    label_text='to ',
                                    labelpos='w',
                                    entry_width=7,
                                    validate=validate,
                                    modifiedcommand=self._updateGUI)
    entryfield_xto.grid(row=0, column=1, padx=3, pady=3, sticky='w')

    # restore the default wavenumbers interval of (1900., 100.)
    btn_restore_interval = Tkinter.Button(group_pr.interior(),
                                          image=getimage('reset_range'),
                                          command=self.__restore_lims,
                                          relief='flat',
                                          overrelief='raised')
    btn_restore_interval.grid(row=0, column=2, padx=3, pady=3, sticky='w')

    # separating line
    frm_separator = Tkinter.Frame(group_pr.interior(),
                                  height=2,
                                  bd=1,
                                  relief='sunken')
    frm_separator.grid(row=1, column=0, columnspan=3,
                       padx=3, pady=5, sticky='we')

    # x ticks
    # major : 100-1000
    # minor fractions : 0.25 - 1.00
    self._varsdict['var_majortick']          = Tkinter.IntVar()
    self._varsdict['var_minortick_fraction'] = Tkinter.DoubleVar()

    validate = dict(validator='integer', min=100, max=1000)
    var = self._varsdict['var_majortick']    
    counter_majortick = Pmw.Counter(group_pr.interior(),
                                    entry_textvariable=var,
                                    label_text='major tick ',
                                    labelpos='w',
                                    datatype=dict(counter='integer'),
                                    entry_state='readonly',
                                    entry_width=4,
                                    entryfield_validate=validate,
                                    increment=100,
                                    autorepeat=False,
                                    entryfield_value=100)
    counter_majortick.grid(row=2, column=0, padx=3, pady=3, sticky='w')

    validate = dict(validator='real',
                     min=0.25,
                     max=0.75,
                     separator='.')
    var = self._varsdict['var_minortick_fraction']
    counter_minortick_fraction = Pmw.Counter(group_pr.interior(),
                                             entry_textvariable=var,
                                             label_text=\
                                             'minor tick fraction ',
                                             labelpos='w',
                                             datatype=dict(counter='real'),
                                             entry_state='readonly',
                                             entry_width=4,
                                             entryfield_validate=validate,
                                             increment=0.25,
                                             autorepeat=False,
                                             entryfield_value=0.5)
    counter_minortick_fraction.grid(row=3, column=0,
                                    padx=3, pady=3, sticky='w')

    Pmw.alignlabels((entryfield_xfrom,
                     counter_majortick,
                     counter_minortick_fraction))
    # x grid
    self._varsdict['var_majorgrid']          = Tkinter.IntVar()
    self._varsdict['var_minorgrid']          = Tkinter.IntVar()

    var = self._varsdict['var_majorgrid']
    check_majorgrid = Tkinter.Checkbutton(group_pr.interior(),
                                          text='Major grid',
                                          variable=var)
    check_majorgrid.grid(row=2, column=1, padx=3, pady=3, sticky='w')

    var = self._varsdict['var_minorgrid']
    check_minorgrid = Tkinter.Checkbutton(group_pr.interior(),
                                          text='Minor grid',
                                          variable=var)
    check_minorgrid.grid(row=3, column=1, padx=3, pady=3, sticky='w')

  def _constructExportTab(self, tab) :
    """Construct the Export tab with PNG/PDF settings."""
    tab.grid_columnconfigure(0, weight=1)
    tab.grid_rowconfigure(0, weight=1)

    frm_all = Tkinter.Frame(tab)
    frm_all.grid(row=0, column=0, padx=3, pady=3, sticky='wen')
    
    # dpi
    self._varsdict['var_dpi'] = Tkinter.IntVar()

    var = self._varsdict['var_dpi']
    validate = dict(validator='integer', min=10, max=600)
    
    widget = Pmw.Counter(frm_all,
                         entry_textvariable=var,
                         label_text='Figure resolution (dpi) ',
                         labelpos='w',
                         datatype=dict(counter='integer'),
                         entry_state='readonly',
                         entry_width=4,
                         entryfield_validate=validate,
                         increment=10,
                         autorepeat=True,
                         entryfield_value=150)
    self._varsdict['counter_dpi'] = widget
    self._varsdict['counter_dpi'].grid(row=0, column=0,
                                       padx=3, pady=3, sticky='w')
    # PDF compatibility
    widget = Pmw.OptionMenu(frm_all,
                            labelpos='w',
                            label_text='PDF compatibility level ',
                            items=resources.STRINGS_PDFCOMPATIBILITYLEVELS)
    self._varsdict['options_pdfcompatibility'] = widget
    self._varsdict['options_pdfcompatibility'].grid(row=0, column=1,
                                                    padx=3, pady=3, sticky='w')
    
    # figure size : width
    widget = Pmw.OptionMenu(frm_all,
                            labelpos='w',
                            label_text='Size ',
                            items=self._varsdict['FIGURE_SIZES'])
    self._varsdict['options_size'] = widget
    self._varsdict['options_size'].grid(row=0, column=2,
                                        padx=3, pady=3, sticky='wn')

  def _constructProfileTab(self, tab) :
    """Construct the Profile tab."""
    tab.grid_columnconfigure(0, weight=1)
    
    self._varsdict['var_N_G']       = Tkinter.IntVar()
    self._varsdict['var_FWHM_is']   = Tkinter.DoubleVar()
    self._varsdict['var_FWHM_anis'] = Tkinter.DoubleVar()
    self._varsdict['var_FWHM_inst'] = Tkinter.DoubleVar()
    
    # number of gaussians (3-8)
    row = 0
    validate = dict(validator='integer', min=3, max=8)
    var = self._varsdict['var_N_G']
    widget = Pmw.Counter(tab,
                         entry_textvariable=var,
                         label_text='Number of gaussians : ',
                         labelpos='w',
                         datatype=dict(counter='integer'),
                         entry_state='readonly',
                         entry_width=4,
                         entryfield_validate=validate,
                         increment=1,
                         autorepeat=False,
                         entryfield_value=6)
    self._varsdict['counter_N_G'] = widget
    self._varsdict['counter_N_G'].grid(row=row, column=0,
                                       padx=3, pady=3, sticky='w')
    row += 1

    # isotropic bandwidth (Lorentz)
    var = self._varsdict['var_FWHM_is']
    validate = dict(validator='real', min=3.0, max=100., separator='.')
    widget = Pmw.Counter(tab,
                         entry_textvariable=var,
                         label_text='Isotropic FWHM : ',
                         labelpos='w',
                         datatype=dict(counter='real'),
                         entry_state='readonly',
                         entry_width=4,
                         entryfield_validate=validate,
                         increment=0.5,
                         autorepeat=True,
                         entryfield_value=3.5)
    self._varsdict['counter_FWHM_is'] = widget
    self._varsdict['counter_FWHM_is'].grid(row=row, column=0,
                                           padx=3, pady=3, sticky='w')
    row += 1

    # anisotropic bandwidth (Lorentz)
    var = self._varsdict['var_FWHM_anis']
    widget = Pmw.Counter(tab,
                         entry_textvariable=var,
                         label_text='Anisotropic FWHM : ',
                         labelpos='w',
                         datatype=dict(counter='real'),
                         entry_state='readonly',
                         entry_width=4,
                         entryfield_validate=validate,
                         increment=0.5,
                         autorepeat=True,
                         entryfield_value=10.0)
    self._varsdict['counter_FWHM_anis'] = widget
    self._varsdict['counter_FWHM_anis'].grid(row=row, column=0,
                                             padx=3, pady=3, sticky='w')
    row += 1

    # instrument bandwidth (Gauss)
    var = self._varsdict['var_FWHM_inst']    
    widget = Pmw.Counter(tab,
                         entry_textvariable=var,
                         label_text='Instrument profile : ',
                         labelpos='w',
                         datatype=dict(counter='real'),
                         entry_state='readonly',
                         entry_width=4,
                         entryfield_validate=validate,
                         increment=0.1,
                         entryfield_value=7.0)
    self._varsdict['counter_FWHM_inst'] = widget
    self._varsdict['counter_FWHM_inst'].grid(row=row, column=0,
                                             padx=3, pady=3, sticky='w')
    row += 1
    
    tab.grid_rowconfigure(row, weight=1)

    Pmw.alignlabels((self._varsdict['counter_N_G'],
                     self._varsdict['counter_FWHM_is'],
                     self._varsdict['counter_FWHM_anis'],
                     self._varsdict['counter_FWHM_inst']))
    
  def _get_kw(self) :
    """Return the keywords for a ok callback."""
    plot_kw = {}

    ## Common tab
    plot_kw.update(self._get_common_kw())

    ## Raman, ROA, Degree of circularity tabs
    plot_kw.update(self._get_spectra_kw())

    ## Profile tab
    plot_kw.update(self._get_profile_kw())

    ## Export tab
    plot_kw.update(self._get_export_kw())

    return plot_kw

  def _get_common_kw(self) :
    """Get the keywords of the Common tab."""
    kw = {}

    # titles
    if 'var_title1' in self._varsdict :
      kw['title1'] = self._varsdict['var_title1'].get()
      kw['title2'] = self._varsdict['var_title2'].get()

    # wavenumbers
    kw['lim_wavenumbers'] = (self._varsdict['var_xfrom'].get(),
                             self._varsdict['var_xto'].get())
    # x ticks
    kw['tick_wavenumbers']   = self._varsdict['var_majortick'].get()
    kw['minortick_fraction'] = self._varsdict['var_minortick_fraction'].get()

    # x grids
    kw['majorgrid']   = self._varsdict['var_majorgrid'].get()
    kw['minorgrid']   = self._varsdict['var_minorgrid'].get()

    return kw

  def _get_spectra_kw(self) :
    """Get the keywords of the spectra tabs."""
    kw = dict()
    
    for prefix in self._varsdict['spectra_prefices'] :
      axes_widget = self._varsdict['axes_%s' % prefix]
      for prop in widgets.AxesSettingsWidget.LIST_PROPERTIES :
        if hasattr(axes_widget, prop) :

          # for the keywords from_, to_
          if prop.endswith('_') :
            kw_name = '%s_%s' % (prefix, prop[:-1])
          else :
            kw_name = '%s_%s' % (prefix, prop)
            
          kw[kw_name] = getattr(axes_widget, prop)

      # handle the ticks properties
      if hasattr(axes_widget, 'ticks_auto') :
        # no need to store the properties for the automatic choice
        if axes_widget.ticks_auto :
          kw['%s_ticks_number' % prefix]          = None
          kw['%s_ticks_scaling_factor' % prefix]  = None
          
        # 
        else :
          if 'scaling factor' == axes_widget.ticks_option :
            kw['%s_ticks_number' % prefix]          = None
            
          else :
            kw['%s_ticks_scaling_factor' % prefix]  = None

    return kw

  def _get_profile_kw(self) :
    """Get the keywords from the Profile tab."""
    kw = {}
    
    kw['N_G']       =   self._varsdict['var_N_G'].get()
    kw['FWHM_is']   =   self._varsdict['var_FWHM_is'].get()
    kw['FWHM_anis'] =   self._varsdict['var_FWHM_anis'].get()
    kw['FWHM_inst'] =   self._varsdict['var_FWHM_inst'].get()

    return kw

  def _get_export_kw(self) :
    """Get the keywords from the Export tab."""
    kw = {}
    
    kw['dpi']                   = self._varsdict['var_dpi'].get()
    kw['PDFCompatibilityLevel'] = \
                self._varsdict['options_pdfcompatibility'].getvalue()

    return kw

  def __restore_lims(self) :
    """Restore the default wavenumbers interval of (1900., 100.)."""
    lims = figures.RamanROADegcircCalcFigure.LIM_WAVENUMBERS
    self._varsdict['var_xfrom'].set(int(lims[0]))
    self._varsdict['var_xto'].set(int(lims[1]))

  def _get_figsize_inches(obj) :
    """Getter function for the figsize_inches property."""
    val = obj._varsdict['options_size'].getvalue()

    size = None
    if 'A4' == val :
      size = figures.RamanROADegcircCalcFigure.FIGSIZE_A4

    return size

  _get_figsize_inches = staticmethod(_get_figsize_inches)

  def _update_common_controls(self, fig) :
    """Update the controls on the first tab."""
    settings = fig.settings

    if 'var_title1' in self._varsdict :
      self._varsdict['var_title1'].set(settings['title1'] or '')
      self._varsdict['var_title2'].set(settings['title2'] or '')

    xlim = fig.get_spectra_axes('bounding').get_xlim()
    xlim = ( int(xlim[0]), int(xlim[1]) )
    self._varsdict['var_xfrom'].set(xlim[0])
    self._varsdict['var_xto'].set(xlim[1])

    self._varsdict['var_majortick'].set(int(settings['tick_wavenumbers']))
    self._varsdict['var_minortick_fraction'].set(
      settings['minortick_fraction'])

    self._varsdict['var_majorgrid'].set(settings['majorgrid'])
    self._varsdict['var_minorgrid'].set(settings['minorgrid'])

  def _update_spectra_controls(self, fig) :
    """"""
    settings = fig.settings
    
    for prefix in self._varsdict['spectra_prefices'] :
      axes_widget = self._varsdict['axes_%s' % prefix]

      if 'degcirc' != prefix :
        ax    = fig.get_spectra_axes(prefix)    
        y_lim = ax.get_ylim()
        
        # limits
        axes_widget.from_ = float('%.2f' % y_lim[0])
        axes_widget.to_   = float('%.2f' % y_lim[1])

        axes_widget.multfactor = - ax.multfactor
      
      for prop in ('linewidth', 'linecolor') :
        setattr(axes_widget, prop, settings['%s_%s' % (prefix, prop)])    

  def update_controls(self, fig) :
    """Synchronize the GUI controls with a figure.

    Positional arguments :
    fig -- figure to synchronize with

    """
    self._varsdict['figure'] = fig
    settings = fig.settings
    
    ## Common tab
    self._update_common_controls(fig)

    ## Raman, ROA , Degree of circularity
    self._update_spectra_controls(fig)
    
    ## Profile tab
    self._varsdict['var_N_G'].set(settings['N_G'])
    self._varsdict['var_FWHM_is'].set(settings['FWHM_is'])
    self._varsdict['var_FWHM_anis'].set(settings['FWHM_anis'])
    self._varsdict['var_FWHM_inst'].set(settings['FWHM_inst'])

    ## Export tab
    self._varsdict['var_dpi'].set(int(settings['dpi']))
    self._varsdict['options_pdfcompatibility'].setvalue(
      settings['PDFCompatibilityLevel'])

  def selectpage(self, page) :
    """Select a page in the notebook.

    Do nothing if the page does not exist.

    Positional arguments :
    page -- page name 
    
    """
    if page in self._varsdict['notebook'].pagenames() :
      self._varsdict['notebook'].selectpage(page)


class TwoDCirclesSettingsDialog(BaseDialog) :
  """Settings of a circles canvas.

  The following public method is exported :
      update_controls() --  update the controls of the dialog
      
  """

  def __init__(self, master, circles, **kw) :
    """Constructor of the class.

    Positional arguments :
    master  -- parent widget
    circles -- instance of pyviblib.gui.widgets.TwoDCircles
    
    """
    if not isinstance(circles, widgets.TwoDCircles) :
      raise ConstructorError('Invalid circles parameter')

    self.__circles = circles
    
    BaseDialog.__init__(self,
                        master,
                        buttons = resources.STRINGS_BUTTONS_OK_APPLY_CANCEL,
                        defaultbutton=resources.STRING_BUTTON_APPLY,
                        title='Circles canvas settings',
                        **kw)

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    ## grid on
    self._varsdict['var_gridon'] = Tkinter.IntVar()
    widget = Tkinter.Checkbutton(self.interior(),
                                text='Grid on',
                                variable=self._varsdict['var_gridon'])
    self._varsdict['check_gridon'] = widget
    self._varsdict['check_gridon'].grid(row=0, column=0,
                                        padx=3, pady=3, sticky='w')

    ## labels on
    self._varsdict['var_labelson'] = Tkinter.IntVar()

    widget = Tkinter.Checkbutton(self.interior(),
                                 text='Labels on',
                                 variable=self._varsdict['var_labelson'])
    self._varsdict['check_labelson'] = widget
    self._varsdict['check_labelson'].grid(row=0, column=1,
                                          padx=3, pady=3, sticky='w')

    ## bounding box on
    self._varsdict['var_bboxon'] = Tkinter.IntVar()

    widget = Tkinter.Checkbutton(self.interior(),
                                 text='Bounding box',
                                 variable=self._varsdict['var_bboxon'])
    self._varsdict['check_bboxon'] = widget
    self._varsdict['check_bboxon'].grid(row=0, column=2, padx=3, pady=3,
                                        sticky='w')

    ### update controls
    self.update_controls()    

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    self._balloon.bind(self._varsdict['check_gridon'],
                       'Show bounding rectangles.')
    self._balloon.bind(self._varsdict['check_labelson'],
                       'Show the vibration labels.')
    self._balloon.bind(self._varsdict['check_bboxon'],
                       'Render the bounding box around the circles.')
  
  def _command(self, btn_name) :
    """Handler for the button events."""
    self.interior().tk.call('update', 'idletasks')
    
    # ok, cancel - withdraw
    if resources.STRING_BUTTON_APPLY != btn_name :
      self.withdraw()
      self.interior().tk.call('update')

    # ok, apply - apply
    if btn_name is not None and resources.STRING_BUTTON_CANCEL != btn_name :
      self.__apply()

  def __apply(self) :
    """Apply the settings."""
    kw = {}

    # grid on
    if self._varsdict['var_gridon'].get() :
      kw['color_rect'] = 'black'      
    else :
      kw['color_rect'] = self.__circles.cget('bg')

    # labels on
    kw['labels_on'] = self._varsdict['var_labelson'].get()

    # bounding box on
    kw['bbox_on'] = self._varsdict['var_bboxon'].get()

    self.__circles.update(**kw)

  def update_controls(self) :
    """Synchronize the contents of the dialog with the circles."""
    # 
    props = self.__circles._smartdict

    # grid on : canvas background == color of bounding rectangles
    self._varsdict['var_gridon'].set(
      self.__circles.cget('bg') != props['color_rect'])

    # labels on
    self._varsdict['var_labelson'].set(props['labels_on'])

    # bounding box on
    self._varsdict['var_bboxon'].set(props['bbox_on'])


class MultipleSpectraSettingsDialog(RamanRoaDegcircCalcSettingsDialog) :
  """Settings of Raman/Roa/Degree of circularity spectra for several molecules.

  The following read-only property is inherited from the superclass :
      figsize_inches    -- spectra canvas size

  The following public method is exported :
      update_controls() --  update the controls of the dialog
      
  """

  def __init__(self, master, nmol, **kw) :
    """
    Positional arguments :
    master              -- parent widget
    nmol                -- number of molecules.
    
    Keyword arguments :
    ok_command          -- callback for the Ok button (default None)
    add_profile_export  -- whether to add the Profile and Export tabs
                           (default False)
                           
    """
    if 0 >= nmol :
      raise ConstructorError('Invalid number of molecules')

    self.__nmol = nmol
    
    RamanRoaDegcircCalcSettingsDialog.__init__(self, master, **kw)    

  def _init_vars(self) :
    """Initialize variables."""
    # base class function
    RamanRoaDegcircCalcSettingsDialog._init_vars(self)
    
    # Add the Profile and Export tabs ? (default : no)
    self._smartdict['add_profile_export'] = False

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    pass

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    ## all options are organized like tabs in a notebook
    self.interior().grid_columnconfigure(0, weight=1)
    self.interior().grid_rowconfigure(0, weight=1)
    
    self._varsdict['notebook'] = Pmw.NoteBook(self.interior())
    self._varsdict['notebook'].grid(row=0, column=0,
                                    padx=3, pady=3, sticky='news')

    ## Common tab (without titles)
    tabCommon = self._varsdict['notebook'].add('Common')
    self._constructCommonTab(tabCommon, add_titles=False)

    ## Subscription tab
    tab = self._varsdict['notebook'].add('Subscriptions')
    self.__constructSubscriptionsTab(tab)

    ## Raman, ROA and Degree of Circularity tabs
    buttons_to_validate = (self.component('buttonbox').button(0),
                           self.component('buttonbox').button(1))

    for name, prefix in zip(resources.STRINGS_SPECTRA_NAMES,
                            resources.STRINGS_SPECTRA_PREFICES) :
      tab = self._varsdict['notebook'].add(name)
      widget = widgets.AxesSettingsWidget(tab,
                                          add_limits='degcirc' != prefix,
                                          add_invert='roa' == prefix,
                                          buttons_to_validate=\
                                          buttons_to_validate)
      self._varsdict['axes_%s' % prefix] = widget
      self._varsdict['axes_%s' % prefix].pack(expand=True, fill='both')

    ## optinally add the Profile and export tabs
    if self._smartdict['add_profile_export'] :
      tabProfile = self._varsdict['notebook'].add('Profile')
      self._constructProfileTab(tabProfile)

      tabExport = self._varsdict['notebook'].add('Export')
      self._constructExportTab(tabExport)
      
    self._varsdict['notebook'].setnaturalsize()

  def _get_kw(self) :
    """Return the keywords for a ok callback."""
    plot_kw = {}

    ## Common tab
    common_kw = self._get_common_kw()
    for prefix in resources.STRINGS_SPECTRA_PREFICES :
      for prop in common_kw :
        plot_kw['%s_%s' % (prefix, prop)] = common_kw[prop]

    ## Labels tab
    plot_kw['molecule_labels'] = [ var.get() for var in \
                                   self._varsdict['var_labels'] ]

    for prefix in resources.STRINGS_SPECTRA_PREFICES :

      for t in ('title1', 'title2') :
        plot_kw['%s_%s' % (prefix, t)] = self._varsdict[
          'var_%s_%s' % (prefix, t)].get()      

    ## Raman, ROA, Degree of circularity tabs
    plot_kw.update(self._get_spectra_kw())

    ## optional Profile and Export tabs
    if self._smartdict['add_profile_export'] :
      plot_kw.update(self._get_profile_kw())
      plot_kw.update(self._get_export_kw())

    return plot_kw
    
  def __constructSubscriptionsTab(self, tab) :
    """Construct the tab with the labels."""
    tab.grid_columnconfigure(0, weight=1)
    tab.grid_rowconfigure(1, weight=1)
    
    frm_labels = Pmw.ScrolledFrame(tab,
                                   labelpos='n',
                                   label_text='Labels of the molecules',
                                   usehullsize=True,
                                   hull_height=200,
                                   horizflex='expand')
    frm_labels.grid(row=0, column=0, padx=3, pady=3, sticky='we')

    frm_labels.interior().grid_columnconfigure(0, weight=1)

    self._varsdict['var_labels'] = []

    font_molecules = resources.get_font_molecules(self.interior())

    entryfields = []
    for i in xrange(self.__nmol) :
      frm_labels.interior().grid_rowconfigure(i, weight=1)
      
      # saving the reference
      var_i = Tkinter.StringVar()
      self._varsdict['var_labels'].append(var_i)
      
      entryfield_i = Pmw.EntryField(frm_labels.interior(),
                                    labelpos='w',
                                    label_text='Conformer %d' % (1 + i),
                                    entry_textvariable=var_i,
                                    entry_font=font_molecules)
      entryfield_i.grid(row=i, column=0, padx=3, pady=3, sticky='we')
      entryfields.append(entryfield_i)

    Pmw.alignlabels(entryfields)

    ## Titles for the conformers (at the top of the spectra)
    grp_titles = Pmw.Group(tab, tag_text='Titles')
    grp_titles.grid(row=1, column=0, padx=3, pady=3, sticky='news')

    grp_titles.interior().grid_columnconfigure(0, weight=1)

    for i in xrange(len(resources.STRINGS_SPECTRA_PREFICES)) :
      grp_titles.interior().grid_rowconfigure(i, weight=1)
      
      panel = self.__constructTitlesPanel(
        grp_titles.interior(), resources.STRINGS_SPECTRA_PREFICES[i])
      panel.grid(row=i, column=0, padx=3, pady=3, sticky='we')

  def __constructTitlesPanel(self, parent, prefix) :
    """Construct a panel with title1 and title2."""    
    tag_text = resources.STRINGS_SPECTRA_NAMES[
      list(resources.STRINGS_SPECTRA_PREFICES).index(prefix)]
    
    grp = Pmw.Group(parent, tag_text=tag_text)

    grp.interior().grid_rowconfigure(0, weight=1)
    grp.interior().grid_rowconfigure(1, weight=1)
    grp.interior().grid_columnconfigure(0, weight=1)

    self._varsdict['var_%s_title1' % prefix] = Tkinter.StringVar()
    self._varsdict['var_%s_title2' % prefix] = Tkinter.StringVar()

    # title1
    var = self._varsdict['var_%s_title1' % prefix]
    entryfield_title1 = Pmw.EntryField(grp.interior(),
                                       entry_textvariable=var,
                                       label_text='Title 1 ',
                                       labelpos='w',)
    entryfield_title1.grid(row=0, column=0, padx=3, pady=3, sticky='we')

    # title2
    var = self._varsdict['var_%s_title2' % prefix]
    entryfield_title2 = Pmw.EntryField(grp.interior(),
                                       entry_textvariable=var,
                                       label_text='Title 2 ',
                                       labelpos='w')
    entryfield_title2.grid(row=1, column=0, padx=3, pady=3, sticky='we')

    return grp    

  def __update_spectra_controls(self, figs) :
    """figs is a tuple for multiple spectra,"""    
    for i in xrange(len(resources.STRINGS_SPECTRA_PREFICES)) :
      prefix      = resources.STRINGS_SPECTRA_PREFICES[i]
      axes_widget = self._varsdict['axes_%s' % prefix]

      if 'degcirc' != prefix :
        y_lim = figs[i].ylim

        # limits
        axes_widget.from_ = float('%.2f' % y_lim[0])
        axes_widget.to_   = float('%.2f' % y_lim[1])

        axes_widget.multfactor = - figs[i].multfactor

      for prop in ('linewidth', 'linecolor') :
        setattr(axes_widget, prop, figs[i].settings[prop])    

  def update_controls(self, figs) :
    """Synchronize the GUI controls with a figure.

    Positional arguments :
    figs -- figures to synchronize with (tuple or list)
            (fig_raman, fig_roa, fig_degcirc)  
  
    """    
    ## Common tab, all three tabs share the x axes settings
    self._update_common_controls(figs[0])

    ## Subscriptions
    # molecule_labels
    if figs[0].settings['molecule_labels'] is not None :
      for i in xrange(self.__nmol) :
        self._varsdict['var_labels'][i].set(
          figs[0].settings['molecule_labels'][i])

    # titles of the spectra
    for i in xrange(len(resources.STRINGS_SPECTRA_PREFICES)) :
      prefix = resources.STRINGS_SPECTRA_PREFICES[i]
      for t in ('title1', 'title2') :
        self._varsdict['var_%s_%s' % (prefix, t)].set(
          figs[i].settings[t] or '')
        
    ## Spectra tabs
    self.__update_spectra_controls(figs)

    ## Export tab
    if self._smartdict['add_profile_export'] :
      self._varsdict['var_dpi'].set(int(figs[0].settings['dpi']))
      self._varsdict['options_pdfcompatibility'].setvalue(
        figs[0].settings['PDFCompatibilityLevel'])    


class IRVCDCalcSettingsDialog(RamanRoaDegcircCalcSettingsDialog) :
  """Settings of Raman/Roa/Degree of circularity spectra.

  The following public methods are exported :
      update_controls() -- update the controls of the dialog

  """  

  def __init__(self, master, **kw) :
    """Constructor of the class.

    Positional arguments :
    master     -- parent widget
    
    Keyword arguments :
    ok_command -- callback for the Ok button (default None)
    
    """
    RamanRoaDegcircCalcSettingsDialog.__init__(self, master, **kw)

  def _init_vars(self) :
    """Initialize variables."""
    # which spectra ?
    self._varsdict['spectra_names']    = \
                              resources.STRINGS_VROA_SPECTRA_NAMES[3:]
    self._varsdict['spectra_prefices'] = \
                              resources.STRINGS_VROA_SPECTRA_PREFICES[3:]
    self._varsdict['FIGURE_SIZES']     = ('current', 'A4')
    
  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    pass

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    RamanRoaDegcircCalcSettingsDialog._constructGUI(self)

  def _constructProfileTab(self, tab) :
    """Construct the Profile tab.

    Overrides the method of the parent class.
    
    """
    tab.grid_columnconfigure(0, weight=1)
    
    self._varsdict['var_N_G']       = Tkinter.IntVar()
    self._varsdict['var_FWHM']      = Tkinter.DoubleVar()
    self._varsdict['var_FWHM_inst'] = Tkinter.DoubleVar()
    
    # number of gaussians (3-8)
    row = 0
    var = self._varsdict['var_N_G']
    validate = dict(validator='integer', min=3, max=8)
    widget = Pmw.Counter(tab,
                         entry_textvariable=var,
                         label_text='Number of gaussians : ',
                         labelpos='w',
                         datatype=dict(counter='integer'),
                         entry_state='readonly',
                         entry_width=4,
                         entryfield_validate=validate,
                         increment=1,
                         autorepeat=False,
                         entryfield_value=6)
    self._varsdict['counter_N_G'] = widget
    self._varsdict['counter_N_G'].grid(row=row, column=0,
                                       padx=3, pady=3, sticky='w')
    row += 1

    # bandwidth (Lorentz)
    var = self._varsdict['var_FWHM']
    validate = dict(validator='real', min=3., max=100., separator='.')
    widget = Pmw.Counter(tab,
                         entry_textvariable=var,
                         label_text='FWHM : ',
                         labelpos='w',
                         datatype=dict(counter='real'),
                         entry_state='readonly',
                         entry_width=4,
                         entryfield_validate=validate,
                         increment=0.5,
                         autorepeat=True,
                         entryfield_value=3.5)
    self._varsdict['counter_FWHM'] = widget
    self._varsdict['counter_FWHM'].grid(row=row, column=0,
                                        padx=3, pady=3, sticky='w')
    row += 1

    # instrument bandwidth (Gauss)
    var = self._varsdict['var_FWHM_inst']
    widget = Pmw.Counter(tab,
                         entry_textvariable=var,
                         label_text='Instrument profile : ',
                         labelpos='w',
                         datatype=dict(counter='real'),
                         entry_state='readonly',
                         entry_width=4,
                         entryfield_validate=validate,
                         increment=0.1,
                         entryfield_value=7.0)
    self._varsdict['counter_FWHM_inst'] = widget
    self._varsdict['counter_FWHM_inst'].grid(row=row, column=0,
                                             padx=3, pady=3, sticky='w')
    row += 1
    
    tab.grid_rowconfigure(row, weight=1)

    Pmw.alignlabels((self._varsdict['counter_N_G'],
                     self._varsdict['counter_FWHM'],
                     self._varsdict['counter_FWHM_inst']))

  def _get_kw(self) :
    """Return the keywords for a ok callback."""
    plot_kw = {}

    ## Common tab
    plot_kw.update(self._get_common_kw())

    ## IR/VCD/g tabs
    plot_kw.update(self._get_spectra_kw())

    ## Profile tab
    plot_kw['N_G']       =   self._varsdict['var_N_G'].get()
    plot_kw['FWHM_fit']  =   self._varsdict['var_FWHM'].get()
    plot_kw['FWHM_inst'] =   self._varsdict['var_FWHM_inst'].get()

    ## Export tab
    plot_kw['dpi']                   = self._varsdict['var_dpi'].get()
    plot_kw['PDFCompatibilityLevel'] = \
                      self._varsdict['options_pdfcompatibility'].getvalue()

    return plot_kw  

  def update_controls(self, fig) :
    """Synchronize the GUI controls with a figure.

    Positional arguments :
    fig -- figure to synchronize with

    """
    self._varsdict['figure'] = fig
    settings = fig.settings
    
    ## Common tab
    self._update_common_controls(fig)

    ## IR/VCD/g tabs
    self._update_spectra_controls(fig)
    
    ## Profile tab
    self._varsdict['var_N_G'].set(settings['N_G'])
    self._varsdict['var_FWHM'].set(settings['FWHM_fit'])
    self._varsdict['var_FWHM_inst'].set(settings['FWHM_inst'])

    ## Export tab
    self._varsdict['var_dpi'].set(int(settings['dpi']))
    self._varsdict['options_pdfcompatibility'].setvalue(
      settings['PDFCompatibilityLevel'])
    

class FileInfoDialog(BaseDialog) :
  """Information about a file."""

  def __init__(self, master, mol, parser) :
    """Constructor of the class.

    Positional arguments :
    master -- parent widget
    mol    -- molecule
    parser -- parser object
    
    """
    self.__mol    = mol
    self.__parser = parser
    
    BaseDialog.__init__(self,
                        master,
                        buttons = (resources.STRING_BUTTON_OK, ),
                        defaultbutton=resources.STRING_BUTTON_OK,
                        title='File information')

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    self.interior().grid_columnconfigure(0, weight=1)
    self.interior().grid_rowconfigure(0, weight=1)

    ## add properties to a special container
    prop_widget = widgets.PropertiesWidget(self.interior(),
                                           width=500,
                                           height=250)
    prop_widget.grid(row=0, column=0, padx=3, pady=3, sticky='news')

    # file name
    prop_widget.add_line('File name', self.__parser.filename)

    # format
    prop_widget.add_line('Format', self.__parser.get_description())

    # program version if available
    if hasattr(self.__parser, 'version') :
      prop_widget.add_line('Version', self.__parser.version)

    # last modified
    stats = os.stat(self.__parser.filename)
    prop_widget.add_line('Last modified',
                         strftime(resources.STRING_FORMAT_TIME,
                                  localtime(stats.st_mtime)))
    # file size
    prop_widget.add_line('Size, bytes', stats.st_size)

    # separator
    prop_widget.add_separator()

    # comment
    if hasattr(self.__parser, 'comment') and \
       self.__parser.comment is not None :
      prop_widget.add_line('Comment', self.__parser.comment)

    # number of atoms
    prop_widget.add_line('Number of atoms', self.__parser.Natoms)

    # number of vibrations
    if self.__mol.L is not None :
      prop_widget.add_line('Number of vibrations', self.__mol.NFreq)

    # number of basis function
    if hasattr(self.__parser, 'NBasis') and self.__parser.NBasis is not None :
      prop_widget.add_line('Number of basis functions', self.__parser.NBasis)
      
    # total energy
    if hasattr(self.__parser, 'Etotal') and self.__parser.Etotal is not None :
      prop_widget.add_line('Total energy (hartree)', self.__parser.Etotal)

    # wavelength of the incident light
    if hasattr(self.__parser, 'lambda_incident') and \
       self.__parser.lambda_incident is not None :
      prop_widget.add_line(
        'Lambda incident, nm', '%.2f' % self.__parser.lambda_incident)

  def _command(self, btn_name) :
    """Handler for the button events."""
    self.withdraw()


class RamanRoaDegcircExpSettingsDialog(RamanRoaDegcircCalcSettingsDialog) :
  """Settings of experimental Raman/Roa/Degree of circularity spectra.

  The following public methods are exported :
      update_controls() -- update the controls of the dialog

  """  

  def __init__(self, master, **kw) :
    """Constructor of the class.

    Positional arguments :
    master     -- parent widget
    
    Keyword arguments :
    ok_command -- callback for the Ok button (default None)
    
    """
    RamanRoaDegcircCalcSettingsDialog.__init__(self, master, **kw)
    
  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    pass

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    ## all options are organized like tabs in a notebook
    self.interior().grid_columnconfigure(0, weight=1)
    self.interior().grid_rowconfigure(0, weight=1)
    
    self._varsdict['notebook'] = Pmw.NoteBook(self.interior())
    self._varsdict['notebook'].grid(row=0, column=0, padx=3, pady=3,
                                    sticky='news')
    ## Common tab
    tabCommon = self._varsdict['notebook'].add('Common')
    self._constructCommonTab(tabCommon)

    ## spectra tabs
    buttons_to_validate = (self.component('buttonbox').button(0),
                           self.component('buttonbox').button(1))

    for name, prefix in zip(self._varsdict['spectra_names'],
                            self._varsdict['spectra_prefices']) :
      tab = self._varsdict['notebook'].add(name)
      widget = widgets.AxesSettingsWidget(tab,
                                          add_limits='degcirc' != prefix,
                                          add_invert='roa' == prefix,
                                          buttons_to_validate=\
                                          buttons_to_validate)
      self._varsdict['axes_%s' % prefix] = widget
      self._varsdict['axes_%s' % prefix].pack(expand=True, fill='both')
      
    ## Setup tab
    tabSetup = self._varsdict['notebook'].add('Setup')
    self._constructSetupTab(tabSetup)

    ## Export tab
    tabExport = self._varsdict['notebook'].add('Export')
    self._constructExportTab(tabExport)

    ### update controls
    self._varsdict['notebook'].setnaturalsize()

  def _constructSetupTab(self, tab) :
    """Construct the Setup tab.

    Overrides the method of the parent class.
    
    """    
    tab.grid_columnconfigure(0, weight=1)

    self._varsdict['var_normalize_energy'] = Tkinter.IntVar()    
    self._varsdict['var_smooth'] = Tkinter.IntVar()

    # normalize to the laser energy
    row = 0
    var = self._varsdict['var_normalize_energy']
    text = 'Normalize to the laser energy (for Raman and ROA)'
    norm_check = Tkinter.Checkbutton(tab,
                                     text=text,
                                     variable=var,
                                     command=self.__change_limits)
    norm_check.grid(row=row, column=0, padx=3, pady=3, sticky='w')
    row += 1
    
    # smooth data
    var = self._varsdict['var_smooth']
    smooth_check = Tkinter.Checkbutton(tab,
                                       text='Smooth the experimental curves',
                                       variable=var)
    smooth_check.grid(row=row, column=0, padx=3, pady=3, sticky='w')
    row += 1

    ## Savitzky-Golay parameters
    tab.grid_rowconfigure(row, weight=1)
    group_sg = Pmw.Group(tab, tag_text='Savitzky-Golay')
    group_sg.grid(row=row, column=0, padx=3, pady=3, sticky='wn')
    
    # polynomial order : 2 - 10
    row = 0
    widget = Pmw.OptionMenu(group_sg.interior(),
                            items=range(2, 12, 2),
                            menubutton_width=2,
                            label_text='Polynomial order ',
                            labelpos='w')
    self._varsdict['optmenu_order'] = widget
    self._varsdict['optmenu_order'].grid(row=row, column=0,
                                         padx=3, pady=3, sticky='w')
    row += 1

    # total number of points : 5 - 21
    widget = Pmw.OptionMenu(group_sg.interior(),
                            items=range(5, 23, 2),
                            menubutton_width=2,
                            label_text='Number of points ',
                            labelpos='w')
    self._varsdict['optmenu_sg_npoints'] = widget
    self._varsdict['optmenu_sg_npoints'].grid(row=row, column=0,
                                              padx=3, pady=3, sticky='w')
    row += 1

    Pmw.alignlabels((self._varsdict['optmenu_order'],
                     self._varsdict['optmenu_sg_npoints']))

  def _get_setup_kw(self) :
    """Get the keywords of the Setup tab."""
    kw = {}

    kw['normalize_energy'] = self._varsdict['var_normalize_energy'].get()
    kw['smooth'] = self._varsdict['var_smooth'].get()
    kw['order']  = int(self._varsdict['optmenu_order'].getvalue())
    kw['sg_npoints'] = int(self._varsdict['optmenu_sg_npoints'].getvalue())

    return kw
    
  def _get_kw(self) :
    """Return the keywords for a ok callback."""
    plot_kw = {}

    ## Common tab
    plot_kw.update(self._get_common_kw())

    ## Raman, ROA, Degree of circularity tabs
    plot_kw.update(self._get_spectra_kw())

    ## Smoothing tab
    plot_kw.update(self._get_setup_kw())

    ## Export tab
    plot_kw.update(self._get_export_kw())

    return plot_kw

  def __change_limits(self) :
    """
    If the user enables/remove the normalization to the laser energy, the
    Raman and ROA limits change dramatically. This functions makes sure that
    they are recalculated appropriately.
    
    """
    for prefix in ('raman', 'roa') :
      self._varsdict['axes_%s' % prefix].limits_auto = True

  def update_controls(self, fig) :
    """Synchronize the GUI controls with a figure.

    Positional arguments :
    fig -- figure to synchronize with

    """
    self._varsdict['figure'] = fig
    settings = fig.settings
    
    ## Common tab
    self._update_common_controls(fig)

    ## Raman, ROA , Degree of circularity
    self._update_spectra_controls(fig)

    ## Setup tab
    self._varsdict['var_normalize_energy'].set(
        settings['normalize_energy'] and 1 or 0)
    self._varsdict['var_smooth'].set(settings['smooth'] and 1 or 0)
    self._varsdict['optmenu_order'].setvalue(settings['order'] or 2)
    self._varsdict['optmenu_sg_npoints'].setvalue(settings['sg_npoints'] or 5)

    ## Export tab
    self._varsdict['var_dpi'].set(int(settings['dpi']))
    self._varsdict['options_pdfcompatibility'].setvalue(
      settings['PDFCompatibilityLevel'])
