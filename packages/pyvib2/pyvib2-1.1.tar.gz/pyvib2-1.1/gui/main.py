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

"""Main graphical user interface of PyVib2.

The following classes are exported :
    Main  --  the main window of PyVib2
    
"""
__author__ = 'Maxim Fedorovsky'

import os.path
import sys
import Tkinter
import tkFileDialog
from   ConfigParser import ConfigParser, DEFAULTSECT
import webbrowser

from numpy import any

import Pmw

import pyviblib
from pyviblib.gui import resources
from pyviblib.gui import windows
from pyviblib.gui import widgets
from pyviblib.gui import dialogs
from pyviblib.calc.vibrations import vibana
from pyviblib.calc.spectra    import RamanROATensors, IRVCDTensors
from pyviblib.io              import parsers
from pyviblib.molecule        import Molecule
from pyviblib.util.misc       import Command, readconfig_option, \
                                     gen_molecule_name
from pyviblib.util.exceptions import ConstructorError

__all__ = ['Main']


class Main(widgets.BaseWidget) :
  """The main window of PyVib2.

  The following properties are exposed :
      master              -- reference to the root Tkinter.Tk object
      settings            -- dictionary with some application settings
      lastdir             -- last visited directory
      opened_vibmolecules -- list of molecules with the normal modes

  The following functions are exported :
      register_window()   -- register a window in the Windows menu
      unregister_window() -- unregister a window from the Windows menu
      remove_thumbnail()  -- remove a thumbnail from the thumbnail pane
      activate()          -- activate a window
      
  """

  def __init__(self, master, startfiles=None) :
    """Constructor of the class.

    Positional arguments :
    master -- must be a reference to the root Tkinter.Tk object

    Keyword arguments :
    startfiles -- list of files to be opened at startup (default None)

    """
    if not isinstance(master, Tkinter.Tk) :
      raise ConstructorError(\
        'The constructor expects an instance of Tkinter.Tk')

    # reference to Tkinter.Tk
    self._master = master

    # reading the configurations from ~/.pyvib2rc
    self.__readconfig()

    # initializing the base class
    widgets.BaseWidget.__init__(self, startfiles=startfiles)

    # opening startfiles
    self.__open_startfiles()

  def _init_vars(self) :
    """Internal variables"""
    # size of the mainPane
    self._varsdict['SIZE_SCROLLEDAREA'] = (750, 230)

    # number of thumbnails pro line
    self._varsdict['N_thumbnails_line'] = 3

    # lists for storing opened molecules and their parser objects
    self._varsdict['molecules'] = []
    self._varsdict['parsers']   = []

    # list of all opened windows
    self._varsdict['windows']   = []

    # list of the thumbnails
    self._varsdict['thumbnails'] = []
 
  def _constructGUI(self) :
    """Construct the main interface :)"""
    self._master.withdraw()
    self._master.wm_title('%s - %s' % (pyviblib.APPNAME, pyviblib.DESCRIPTION))

    ## menubar at the top
    self._varsdict['menubar'] = self.__constructMenubar(self._master)
    self._varsdict['menubar'].grid(row=0, column=0, sticky='w')

    ## toolbar beneath the menubar
    self._varsdict['toolbar'] = self.__constructButtonToolbar(self._master)
    self._varsdict['toolbar'].grid(row=1, column=0, padx=3, pady=3, sticky='w')

    ## mainPane - scrollable frame with all opened molecules
    self._master.grid_rowconfigure(2, weight=1)
    self._master.grid_columnconfigure(0, weight=1)

    sf_kw = dict(usehullsize=True,
                 hull_width=self._varsdict['SIZE_SCROLLEDAREA'][0],
                 hull_height=self._varsdict['SIZE_SCROLLEDAREA'][1],
                 horizflex='expand',
                 vertflex='fixed')
    
    self._varsdict['mainPane'] = Pmw.ScrolledFrame(self._master, **sf_kw)
    self._varsdict['mainPane'].grid(row=2, column=0, padx=3, pady=3,
                                    sticky='news')
    #
    self.__update_GUI()

    # make the window visible
    self._master.deiconify()
    self._master.focus_set()

  def _declare_properties(self) :
    """Declare properties of the class."""
    # Reference to the root Tk object
    self.__class__.master = property(\
      fget=Command(Command.fget_attr, '_master'))

    # Application settings
    self.__class__.settings = property(\
      fget=Command(Command.fget_attr, '_appsettings'))

    # Last visited directory
    self.__class__.lastdir = property(\
      fget=Command(Command.fget_value, self._configdict['lastdir']))
    
    # opened molecule with the vibrational information
    self.__class__.opened_vibmolecules = property(\
      fget=self.__get_opened_vibmolecules)

  def _bind_events(self) :
    """Bind events."""
    # exit handler unless with File / Exit
    self._master.protocol('WM_DELETE_WINDOW', self.__file_exit)

  def __constructButtonToolbar(self, parent) :
    """Contruct the toolbar and return it."""
    toolbar = widgets.ButtonToolbar(parent, horizontal=True)

    # open a molecule
    toolbar.add_button(imagename='open_file',
                       command=self.__file_open,
                       helptext='Open a molecule.'
                       )

    # correlate vibrations
    btn = toolbar.add_button(imagename='correlate',
                             command=self.__correlate_vibrations,
                             helptext='Correlate vibrations...')
    self._varsdict['btn_correlate'] = btn

    # spectra - single or mix depending on current selection of molecules !
    btn = toolbar.add_button(imagename='spectrum',
                             command=self.__plot_raman_roa_spectra,
                             helptext='Plot spectra...')
    self._varsdict['btn_spectra'] = btn

    # spectra of a mixture
    btn = toolbar.add_button(imagename='boltzmann',
                             command=self.__plot_boltzmann_mixture,
                             helptext='Plot spectra of a mixture.')
    self._varsdict['btn_mixture'] = btn
    
    toolbar.add_separator()

    # check all
    btn = toolbar.add_button(imagename='select_all',
                             command=Command(self.__check_all, True),
                             helptext='Select all molecules.')
    self._varsdict['btn_sel_all'] = btn

    # uncheck all
    btn = toolbar.add_button(imagename='deselect_all',
                             command=Command(self.__check_all, False),
                             helptext='Deselect all molecules.')
    self._varsdict['btn_desel_all'] = btn

    return toolbar

  def __constructMenubar(self, parent) :
    """Construct the menu bar for the main window and return it."""
    menubar = Pmw.MenuBar(parent, hotkeys=False)

    ## File
    menubar.addmenu('File', None, tearoff=False)

    menubar.addmenuitem('File', 'command',
                        label='Open...',
                        command=self.__file_open)

    menubar.addmenuitem('File', 'command',
                        label='Import exp spectra...',
                        command=self.__file_import_exp_spectra)

    # Recent Files
    menubar.addcascademenu('File', 'Recent Files')

    self._varsdict['menu_recent_files'] = menubar.component('Recent Files-menu')

    # do not check if files are existing
    # since it is already done during reading of the user config file
    for rf in self._configdict['recentFiles'] :
      menubar.addmenuitem('Recent Files',
                          'command',
                          label=os.path.basename(rf),
                          command=Command(self.__open_file, rf))
    
    menubar.addmenuitem('File', 'separator')
    
    menubar.addmenuitem('File', 'command',                        
                        label='Close all',
                        command=self.__file_close_all)
    menubar.addmenuitem('File', 'command',
                        label='Exit', command=self.__file_exit)

    ## Options
    menubar.addmenu('Options', None, tearoff=False)
    menubar.addmenuitem('Options', 'command',
                        label='Configure %s...' % pyviblib.APPNAME,
                        command=self.__options_configure)
    
    ## menu Windows
    menubar.addmenu('Windows', None, tearoff=False)
    self._varsdict['menu_windows'] = menubar.component('Windows-menu')
    
    ## menu Help
    menubar.addmenu('Help', None, side='right', tearoff=False)

    menubar.addmenuitem('Help', 'command',
                        label='pyviblib Class Library Reference',
                        command=self.__help_pyviblib)

    menubar.addmenuitem('Help', 'separator')

    menubar.addmenuitem('Help', 'command',
                        label='About...',
                        command=self.__help_about)
    return menubar

  def __open_startfiles(self) :
    """Open a list of files passed to the contructor."""
    if self._smartdict['startfiles'] is not None :
      for f in self._smartdict['startfiles'] :
        if os.path.exists(f) :
          self.__open_file(f)
        else :
          print >> sys.stdout, r'File "%s" does not exist => skipping...' % f

  def __append_molecule(self, mol, parser) :
    """Add a molecule to the end of the mainPane."""
    cur_thumbnail = widgets.MoleculeThumbnailWidget(
                                    self._varsdict['mainPane'].interior(), mol,
                                    mainApp=self,
                                    parser=parser,
                                    check_command=self.__update_GUI)
    self._varsdict['thumbnails'].append(cur_thumbnail)

    # grid coords of the current thumbnail
    i, j = self.__grid_ij(len(self._varsdict['thumbnails']) - 1)

    self._varsdict['mainPane'].interior().grid_rowconfigure(i, weight=1)
    self._varsdict['mainPane'].interior().grid_columnconfigure(j, weight=1)

    # placing finally
    cur_thumbnail.grid(row=i, column=j, padx=3, pady=3, sticky='wn')

  def __grid_ij(self, index) :
    """Calculate the coordinates of a thumbnail with a null-based index."""
    i  = int(index / self._varsdict['N_thumbnails_line'])
    j  = index - self._varsdict['N_thumbnails_line'] * i

    return i, j
    
  def __file_open(self) :
    """File / Open menu command handler."""
    filenames = tkFileDialog.Open(filetypes=resources.LIST_INPUT_FILETYPES,
                                  initialdir=self._configdict['lastdir'],
                                  multiple=True).show()
    if filenames :
      for filename in filenames :
        self.__open_file(filename)

  def __file_import_exp_spectra(self) :
    """File / Import experimental spectra command handler."""
    windows.ImportExpSpectraWindow(self)

  def __file_exit(self) :
    """File / Exit menu command handler."""
    # saving the configuration file
    self.__writeconfig()
    self.__file_close_all()
    self._master.destroy()

  def __file_close_all(self) :
    """Close all opened windows."""
    self._master.update_idletasks()

    # opened windows
    for wnd in self._varsdict['windows'] :
      wnd.destroy(False)
      
    self._master.update_idletasks()

    self._varsdict['menu_windows'].delete(0, len(self._varsdict['windows']))
    del self._varsdict['windows'][:] 

    # opened thumbnails
    for thmb in self._varsdict['thumbnails'] :
      thmb.grid_remove()

    del self._varsdict['thumbnails'][:]

    #
    self.__update_GUI()

  def __options_configure(self) :
    """Options / Configure PyVib2... menu command handler."""
    if 'dlg_settings' not in self._varsdict :
      self._varsdict['dlg_settings'] = dialogs.ApplicationSettingsDialog(self)

    self._varsdict['dlg_settings'].update_controls()      
    self._varsdict['dlg_settings'].show()

  def __open_file(self, filename) :
    """Open a file."""
    try :
      splash = widgets.SplashScreen(self._master,
                                 'Opening %s ...' % os.path.basename(filename))

      #
      parser   = parsers.ParserFactory.create_parser(filename)
      mol      = Molecule(parser)
      mol.name = gen_molecule_name(filename)

      # processing a FCHK file
      if filename.lower().endswith('.fchk') :
        splash.withdraw()
        self.__open_fchk_file(parser, mol)

      else :
        self._read_successfully = True

      if not self._read_successfully :
        splash.destroy()
        return

      # saving the molecule and parser
      self._varsdict['molecules'].append(mol)
      self._varsdict['parsers'].append(parser)

      # adding to the interface
      self.__append_molecule(mol, parser)

      # finished reading
      splash.destroy()

      # save the directory name
      self._configdict['lastdir'] = os.path.dirname(filename)

      # insert in the recent file list
      self.__register_in_recent_files(filename)

      #
      self.__update_GUI()
      
    except :
      splash.destroy()

      # delete the file from the recent file list if it was there
      self.__unregister_from_recent_files(filename)

      widgets.show_exception(sys.exc_info())

  def __help_about(self) :
    """Help / About menu command handler."""
    version_with_time = '%s (deployed on %s)' % (pyviblib.VERSION,
                                                 pyviblib.DEPLOY_TIME)
    
    Pmw.aboutversion(version_with_time)

    Pmw.aboutcopyright(pyviblib.COPYRIGHT)
    Pmw.aboutcontact(pyviblib.CONTACT)

    about = Pmw.AboutDialog(self._master, applicationname=pyviblib.APPNAME)
    about.show()

  def __help_pyviblib() :
    """Help / pyviblib reference command handler."""
    html_to_open = os.path.join(str(pyviblib.get_rootdir()),
                                'doc', 'pyviblib.html')

    if os.path.exists(html_to_open) :
      webbrowser.open(html_to_open)
    else :
      dlg = Pmw.MessageDialog(
        title='File not found',
        message_text='The documentation is not properly installed :(',
        iconpos='w',
        icon_bitmap='error')

      dlg.withdraw()
      Pmw.setgeometryanddeiconify(dlg, dlg._centreonscreen())

  __help_pyviblib = staticmethod(__help_pyviblib)

  def __open_fchk_file(self, parser, mol) :
    """Open a fchk file."""
    self._read_successfully = True
    
    # perform the vibrational analysis if possible
    if parser.hessian is not None :
      ok_command     = Command(self.__finalize_fchk, parser.hessian, mol)      
      cancel_command = Command(Command.fset_attr,
                               self,
                               False,
                               '_read_successfully')

      initname = '%s_subst' % gen_molecule_name(parser.filename)

      isotopes_dlg = dialogs.IsotopesDialog(self._master,
                                            mol,
                                            molecule_name=initname,
                                            ok_command=ok_command,
                                            cancel_command=cancel_command)
      isotopes_dlg.activate()

  def __readconfig(self) :
    """Read the configuration file ~/.pyvib2rc."""
    # application settings dictionary
    self._appsettings  = dict(resolution=resources.NUM_RESOLUTION_VTK)

    # values from config
    self._configdict   = dict(lastdir=os.path.expanduser('~'), recentFiles=[])

    # read setting from the config file
    try :
      cfp = ConfigParser()

      fp = open(os.path.expanduser('~/.pyvib2rc'))
      cfp.readfp(fp)

      ## DEFAULT section
      # last visited directory
      lastdir = readconfig_option(cfp, DEFAULTSECT, 'lastdir',
                                  os.path.expanduser('~'))
      if os.path.exists(lastdir) :
        self._configdict['lastdir'] = lastdir

      # recent files list
      # raw_recentfiles is a string like ['a.fchk', 'c.out'],
      # which can be restored with the builtin eval function
      
      raw_recentfiles = readconfig_option(cfp, DEFAULTSECT, 'recentfiles')
      if raw_recentfiles :
        try :
          recentFiles = eval(raw_recentfiles)

          # add only existing files !
          # the maximum number of recent files is
          # restricted by resources.NUM_MAXRECENTFILES
          for rf in recentFiles :
            if os.path.exists(rf) and resources.NUM_MAXRECENTFILES > \
               len(self._configdict['recentFiles']) :
              self._configdict['recentFiles'].append(rf)
        except :
          pass

      ## Rendering section
      resolution = readconfig_option(cfp, 'Rendering', 'resolution',
                                     resources.NUM_RESOLUTION_VTK)
      if isinstance(resolution, int) or ( isinstance(resolution, str) and \
                                         resolution.isdigit() ):
        # resolution shoulb in reasonable ranges        
        self._appsettings['resolution'] = min(
          max(resources.NUM_RESOLUTION_VTK_MIN, int(resolution)),
          resources.NUM_RESOLUTION_VTK_MAX)

      # finished
      fp.close()

    except :
      # be silent on error
      pass

  def __writeconfig(self) :
    """Write the ~/.pyvib2rc."""
    # be silent on errors
    try :
      # each time the configuration file will be overwritten
      f_ = open(os.path.expanduser('~/.pyvib2rc'), 'w+')

      # parser object
      cfp = ConfigParser()

      ## DEFAULT section
      # last visited directory
      if self._configdict['lastdir'] :
        cfp.set(DEFAULTSECT, 'lastdir',
                self.__conv_str(self._configdict['lastdir']))

      # recent file list
      if 0 != len(self._configdict['recentFiles']) :        
        cfp.set(DEFAULTSECT, 'recentfiles', self._configdict['recentFiles'])

      ## Rendering section
      cfp.add_section('Rendering')

      cfp.set('Rendering', 'resolution', self._appsettings['resolution'])

      # finally writing : be silent on error
      cfp.write(f_)
      f_.close()

    except :
      pass

  def __conv_str(s) :
    """Convert a string to the form suitable for writing with ConfigParser."""
    return isinstance(s, unicode) and s.encode('utf-8') or s

  __conv_str = staticmethod(__conv_str)

  def __register_in_recent_files(self, filename) :
    """Insert a filename at the top of the recent files.

    Do nothing if the maximum number of recent files was reached.
    See resources.NUM_MAXRECENTFILES

    Positional arguments :
    filename -- file name to be inserted
                if the file is already registered - put it on the top    

    """
    # deleting the filename if it is already in the list
    if filename in self._configdict['recentFiles'] :
      self.__unregister_from_recent_files(filename)

    # if the list is full - remove the last (oldest file)
    # pushing it to the top
    if resources.NUM_MAXRECENTFILES == len(self._configdict['recentFiles']) :
      self.__unregister_from_recent_files(self._configdict['recentFiles'][-1])

    command = Command(self.__open_file, filename)
    self._varsdict['menu_recent_files'].insert(0,
                                               'command',
                                               label=os.path.basename(filename),
                                               command=command)
    self._configdict['recentFiles'].insert(0, filename)

  def __unregister_from_recent_files(self, filename) :
    """Delete a filename from the recent files list if it was there."""
    if filename in self._configdict['recentFiles'] :
      i = self._configdict['recentFiles'].index(filename)

      # delete from the menu
      self._varsdict['menu_recent_files'].delete(i)

      # and from the list
      self._configdict['recentFiles'].remove(filename)

  def __finalize_fchk(self, affected_atoms_data, molecule_name, hessian, mol) :
    """Diagonalize the hessian with respect to a given isotopic composition."""
    self._master.update_idletasks()
    
    if molecule_name is not None and 0 < len(molecule_name) :
      mol.name = molecule_name

    # generate normal coordinates
    mol.update_masses(affected_atoms_data)
    
    ans_vibana = vibana(hessian, mol.coords, mol.masses)

    mol.L      = ans_vibana['L']
    mol.freqs  = ans_vibana['freqs']

    # create the Raman/ROA tensors if possible
    parser = mol.parser

    # Raman is required only
    if parser.PP is not None and any(0. != parser.PP) :
      mol.raman_roa_tensors = RamanROATensors(parser.PP,
                                              parser.PM,
                                              parser.PQ,
                                              mol.Lx,
                                              mol.freqs,
                                              parser.lambda_incident,
                                              A=parser.A)

    # create IR/VCD tensors (only P is required)
    if parser.P is not None and any(0. != parser.P) :
      mol.ir_vcd_tensors = IRVCDTensors(parser.P,
                                        parser.M,
                                        mol.Lx,
                                        mol.freqs)
  
  def __get_opened_vibmolecules(obj) :
    """Getter function for the opened_vibmolecules property."""
    retval = []

    for thmb in obj._varsdict['thumbnails'] :
      if thmb.molecule.L is not None :
        retval.append(thmb.molecule)

    return retval

  __get_opened_vibmolecules = staticmethod(__get_opened_vibmolecules)

  def __get_checked_raman_roa_molecules(self) :
    """Get the checked molecules with the Raman/ROA data."""
    retval = []
    
    for thmb in self._varsdict['thumbnails'] :
      if thmb.molecule.raman_roa_tensors is not None and thmb.checked :
        retval.append(thmb.molecule)

    return retval

  def __get_checked_vib_molecules(self) :
    """Get the checked molecules with the normal modes."""
    retval = []
    
    for thmb in self._varsdict['thumbnails'] :
      if thmb.molecule.L is not None and thmb.checked :
        retval.append(thmb.molecule)

    return retval

  def __check_all(self, check_=True) :
    """Check/Uncheck all thumbnails."""
    for thmb in self._varsdict['thumbnails'] :
      thmb.checked = check_

  def __update_GUI(self) :
    """Update the state of the GUI controls."""
    # select/deselect all - min 1 mol opened
    s1 = 1 <= len(self._varsdict['thumbnails']) and 'normal' or 'disabled'

    self._varsdict['btn_sel_all'].configure(state=s1)
    self._varsdict['btn_desel_all'].configure(state=s1)

    # correlate - min 1 with vibs
    s2 = 1 <= len(self.__get_checked_vib_molecules()) \
         and 'normal' or 'disabled'
    
    self._varsdict['btn_correlate'].configure(state=s2)

    # spectra - at least 1 molecule with the Raman/ROA data
    n = len(self.__get_checked_raman_roa_molecules())
    s3 = 1 <= n and 'normal' or 'disabled'
    
    self._varsdict['btn_spectra'].configure(state=s3)

    # spectra of a mixture - at least 2 molecule with the Raman/ROA data
    s4 = 2 <= n and 'normal' or 'disabled'
    
    self._varsdict['btn_mixture'].configure(state=s4)    

  def __plot_raman_roa_spectra(self) :
    """Plot the Raman/ROA spectra depending on the context."""
    mols = self.__get_checked_raman_roa_molecules()

    self._master.update_idletasks()

    # if only one molecule is checked - plot the usual spectra.
    if 1 == len(mols) :        
      splash = widgets.SplashScreen(self._master,
              'Calculating the Raman/ROA invariants for %s...' % mols[0].name)
    
      windows.RamanROADegcircCalcWindow(self, mols[0])

    # plotting the spectra beneath each other
    else :
      labels = [ mol.name for mol in mols ]

      splash = widgets.SplashScreen(self._master,
        'Calculating the Raman/ROA invariants for %d molecules...' % len(mols))
      
      windows.RamanROADegcircCalcMixtureWindow(self, mols, None, labels)

    splash.destroy()

  def __plot_boltzmann_mixture(self) :
    """Plot spectra of a mixture of molecules."""    
    mols = self.__get_checked_raman_roa_molecules()
    assert 1 < len(mols)

    self._master.update_idletasks()

    windows.BoltzmannMixtureSpectraWindow(self, mols, check_all=True)

  def __correlate_vibrations(self) :
    """Correlate the vibrations depending on the context."""
    mols = self.__get_checked_vib_molecules()

    self._master.update_idletasks()

    # for one molecule propose correlation with all opened molecules
    if 1 == len(mols) :
      windows.CorrelateVibrationsWindow(self,
                                        ref_mol=mols[0],
                                        tr_mol=mols[0],
                                        molecules=None)
    else :
      windows.CorrelateVibrationsWindow(self,
                                        ref_mol=mols[0],
                                        tr_mol=mols[1],
                                        molecules=mols)

  def register_window(self, window) :
    """Register a new window in the Windows menu.

    Positional arguments :
    window -- the window to be registered
              must be a subclass of pyviblib.gui.windows.BaseWindow
               
    """
    # add to the Windows menu
    self._varsdict['menu_windows'].add('command',
                                       label=window.wm_title(),
                                       command=Command(self.activate, window))
    # and finally save the reference
    self._varsdict['windows'].append(window)

  def unregister_window(self, window) :
    """Remove a window from the Windows menu.

    Positional arguments :
    window -- the window to be registered
              must be a subclass of pyviblib.gui.windows.BaseWindow               
    
    """      
    # find where it is
    i = self._varsdict['windows'].index(window)

    # remove from the Windows menu
    self._varsdict['menu_windows'].delete(i)

    # and finally from the windows list
    del self._varsdict['windows'][i]

  def remove_thumbnail(self, thmb) :
    """Remove a thumbnail from the thumbnail pane.

    Positional arguments :
    thmb -- thumbnail to be removed
    
    """
    # remove it first    
    thmb.grid_remove()
    self._varsdict['thumbnails'].remove(thmb)

    # re-arange in mainPane
    for index in xrange(len(self._varsdict['thumbnails'])) :
      i, j = self.__grid_ij(index)

      self._varsdict['thumbnails'][index].grid(row=i, column=j)

    self.__update_GUI()

  def activate(self, window=None) :
    """Activate a window.

    Keyword arguments :
    window -- window to be activated (default None)
              if None, activate oneself

    Note : this won't under KDE, but works fine e.g. under IceWM (or Windows).
    
    """
    if window is None :
      window = self._master
    
    try :
      if 'iconic' == window.wm_state() :
        window.wm_deiconify()
      else :
        window.tkraise()
        
      window.focus_set()

    except :
      pass
