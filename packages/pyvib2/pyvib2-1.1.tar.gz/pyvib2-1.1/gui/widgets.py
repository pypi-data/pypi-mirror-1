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

"""GUI building blocks of the windows and dialogs of PyVib2.

The following classes are exported :
    BaseWidget                 -- base class for all widgets
    MoleculeRenderWidget       -- widget for 3D rendering
    MoleculeThumbnailWidget    -- small frame for exploring a molecule
    ButtonToolbar              -- button toolbar
    VibrationalToolbar         -- navigation through vibrations
    VibrationalToolbarLight    -- for exploring single vibration
    NavigationToolbar          -- manipulating camera of MoleculeRenderWidget
    WindowNavigationToolbar    -- toolbar for switching between windows
    GeometryMeasureToolbar     -- widget for measuring distances, angles etc.
    VibNavigationFrame         -- component of VibrationalToolbar
    SplashScreen               -- shown during a long operation
    InfoWidget                 -- widget for providing a help text
    TwoDCircles                -- canvas for rendering matrices
    CorrelationResultsTable    -- table for representing matrices
    CorrelationResultsNoteBook -- exploring results of a correlation of v/m
    WizardWidget               -- wizard widget
    ChooseColorWidget          -- widget for choosing a color
    AxesSettingsWidget         -- widget for setting properties of axes
    PropertiesWidget           -- widget for showing text properties

The following functions are exported :
    show_exception()           -- show an exception in a text dialog
    mouse_wheel()              -- mouse wheel callback for a widget
    bind_mouse_wheel()         -- bind the mouse wheel events to a widget
    
"""
__author__ = 'Maxim Fedorovsky'

import os
import sys
import tempfile
from   math import fabs, sqrt, ceil, floor, log
from   time import clock
import Tkinter
import tkFileDialog
import tkFont
import tkMessageBox
import tkColorChooser
import tkSimpleDialog
import cPickle
from   traceback import format_tb

import Pmw
from   numpy import zeros, ndarray, array, any

import vtk
import vtk.tk.vtkTkRenderWidget as vtktkrw

from pyviblib                 import molecule
from pyviblib.calc.common     import make_gcp, mass_center
from pyviblib.gui             import rendering, resources
from pyviblib.gui.images      import getimage
from pyviblib.util            import misc
from pyviblib.util.constants  import AMU2AU
from pyviblib.util.exceptions import ConstructorError, InvalidArgumentError

__all__ = ['BaseWidget', 'MoleculeRenderWidget', 'MoleculeThumbnailWidget',
           'ButtonToolbar', 'VibrationalToolbar', 'VibrationalToolbarLight',
           'NavigationToolbar', 'WindowNavigationToolbar',
           'GeometryMeasureToolbar', 'VibNavigationFrame', 'SplashScreen',
           'InfoWidget', 'TwoDCircles', 'CorrelationResultsTable',
           'CorrelationResultsNoteBook', 'WizardWidget',
           'ChooseColorWidget', 'AxesSettingsWidget', 'PropertiesWidget',
           'show_exception', 'mouse_wheel', 'bind_mouse_wheel']


class BaseWidget(object) :
  """Base class for all widgets.

  This class defines a set of protected methods which are called in the
  constructor in the following sequence :
      _init_vars()          -- initialize some variables
      _constructGUI()       -- construct the GUI of the widget
      _declare_properties() -- declare properties of the widget
      _bind_help()          -- bind help messages to the GUI components
      _bind_events()        -- bind events

  These methods are intended to be overridden in subclasses. The base class
  implementations do *nothing*.

  The following protected instance variables are created :
      _smartdict            -- to store options (pyviblib.util.misc.SmartDict)
      _varsdict             -- to store GUI variables (dictionary)
      _balloon              -- to provide help message on the GUI (Pmw.Balloon)
      
  """
  def __init__(self, **kw) :
    """Constructor of the class.

    Keywords arguments are options of the widget.
    
    """
    # smart properties
    self._smartdict = misc.SmartDict(kw=kw)
    self.__class__.smartdict = property(
        misc.Command(misc.Command.fget_attr, '_smartdict'))

    # dictionary for GUI variables
    self._varsdict = {}

    # help system
    self._balloon = Pmw.Balloon()

    # typical operations
    self._init_vars()
    self._constructGUI()
    self._declare_properties()
    self._bind_help()
    self._bind_events()

  def _init_vars(self) :
    """Initialize variables."""
    pass

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    pass

  def _declare_properties(self) :
    """Declare properties of the widget."""
    pass

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    pass

  def _bind_events(self) :
    """Bind events."""
    pass

  def _add_property(self, name, readonly=True, doc=None) :
    """Add a property.

    Positional arguments :
    name      -- name of the property
                 self._smartdict[prop_name] must point to the variable

    Keywords arguments :
    readonly  -- whether the property should be read-only (default True)
    doc       -- doc string for the property (default None)

    """
    if name is None :
      raise InvalidArgumentError('Property name must be supplied')

    str_to_exec = '%s.%s = property(' % (self.__class__.__name__, name) + \
                  r"fget=misc.Command(self._get_property, '%s')," % name
    
    if not readonly :
      str_to_exec = ''.join((
          str_to_exec,
          r"fset=misc.Command(self._set_property, '%s')," % name))

    str_to_exec = ''.join((str_to_exec, 'doc=doc)'))

    exec str_to_exec

  def _get_property(obj, name) :
    """Emulate the getter function for a property.

    Positional arguments :
    obj   -- object whose property is to be read
    name  -- name of the property
    
    """
    return obj._smartdict[name]

  _get_property = staticmethod(_get_property)

  def _set_property(obj, value, name) :
    """Emulate the setter function for a property.

    Positional arguments :
    obj   -- object whose property is to be set
    value -- value to set
    name  -- name of the property
    
    """
    obj._smartdict[name] = value

  _set_property = staticmethod(_set_property)

  def _change_render_widget_size(self, rw) :
    """Show the dialog for changing size of a given render widget.

    The function can be used as a callback for changing the size of the widget.

    Positional arguments :
    rw       -- render widget

    """
    cursize = rw.GetRenderWindow().GetSize()    
    kw = dict(parent = hasattr(self, 'tk') and self or self.interior(),
              title='New size',
              prompt='Enter the new size of the render widget',
              initialvalue='%dx%d' % cursize)
    
    newsize = tkSimpleDialog.askstring(**kw)
    
    if newsize is not None :
      # try to parse the size
      try :
        w, h = [ int(val) for val in newsize.strip().split('x') ]

        if 0 >= w or 0 >= h :
          raise InvalidArgumentError('Invalid size entered')

        self._set_render_widget_size(rw, w, h)

      except :
        tkMessageBox.showerror(title='Error',
                               message=r'Invalid size : "%s"' % newsize)

  def _set_render_widget_size(self, rw, w, h) :
    """Set the size of a given render widget.

    Positional arguments :
    rw       -- render widget
    w        -- desired width in pixel for the render widget
    h        -- desired height in pixel for the render widget

    """
    self.update_idletasks()
    
    # current size of the render widget and of the whole window
    cur_w, cur_h = rw.GetRenderWindow().GetSize()

    geom  = self.geometry()
    delim = '+' in geom and '+' or '-'
    w_, h_ = [ int(val) for val in geom[:geom.index(delim)].split('x') ]

    # setting the new size (keep old coordinates of the upper left corner)
    geom = (w_ + w - cur_w, h_ + h - cur_h, geom[geom.index(delim):])
    self.geometry('%dx%d%s' % geom)
    self.update_idletasks()


class MoleculeRenderWidget(BaseWidget, vtktkrw.vtkTkRenderWidget) :
  """Widget for 3D rendering.

  The class inherits from vtkTkRenderWidget and overrides the mouse button
  events.

  The following readable and writable properties are exposed :
      molecule                   -- molecule (pyviblib.molecule.Molecule)
      molecule_mode              -- molecule rendering mode
      bonds_mode                 -- bonds rendering mode
      color_sphere_1             -- used for rendering vibrational motion
      color_sphere_2             -- used for rendering vibrational motion
      color_picked_atom          -- color of picked atoms
      marked_vib_atoms           -- mark vibrational motion of these atoms 
      mark_fragment              -- whether to mark v/m on marked_vib_atoms
      show_marked_only           -- whether to show v/m motion only on fragment
      do_picking                 -- whether the picking of atoms is allowed
      do_render_picked           -- whether picked atoms are to be rendered
      do_sync_rotation           -- whether the synchronized rotation is on
      do_sync_zoom               -- whether the synchronized zooming is om
      clicked_atom_callback      -- called when an atom has been clicked
      clicked_bond_callback      -- called when a bond has been clicked
      clicked_vibatom_callback   -- called when an v/m atom has been clicked
      background                 -- background of the widget
      perspective_projection     -- whether the perspective projection is used
      resolution                 -- resolution
      camera                     -- camera installed in the widget
      camera_state               -- state of the camera currenly installed

  The following read-only properties are exposed :
      picked_atoms_indices       -- list of picked atoms  
      Npicked                    -- number of picked atoms
      renderer                   -- renderer (vtk.vtkRenderer)

  The following public methods are exported :
      cleanup()                  -- remove all actor from the widget
      render_molecule()          -- render the molecule
      render_vibration()         -- render a vibration
      render_triangle()          -- render a triangle
      render_scalars()           -- render scalar values e.g. ACPs
      render_gcp()               -- render group coupling matrices (GCPs)
      rotate()                   -- rotate the molecule
      zoom()                     -- zoom in/out
      start_pairs_picking()      -- start a subsequent selection of atom pairs
      end_pairs_picking()        -- end a subsequent selection of atom pairs
      depick_atoms()             -- unpick atoms
      highlight_picked_atoms()   -- highlight picked atoms
      remove_triangles()         -- remove triangles
      synchronize_camera_state() -- specify a render widget for sync operations
      get_node()                 -- get a certain node in the widget
      snapshot()                 -- make a snapshot of the 3D window
      create_animation_frames()  -- create frames for animating vibration
  
  """

  def __init__(self, master, **kw) :
    """Constructor of the class.

    Positional arguments :
    master             -- parent widget

    Keywords arguments :
    molecule           -- molecule
                          (pyviblib.molecule.Molecule, default None)
    vib_toolbar        -- vibrational toolbar
                          (pyviblib.gui.widgets.VibrationalToolbar,
                          default None)
                          used for retrieving properties of vibrations
    msgBar             -- message bar (Pmw.MessageBar, default None)
    molecule_mode      -- render the molecule in the ball & stick, stick or
                          van der Waals radii representation
                          one of (resources.NUM_MODE_BALLSTICK,
                          resources.NUM_MODE_STICK,
                          resources.NUM_MODE_VDW)
                          (default resources.NUM_MODE_BALLSTICK)
    bonds_mode         -- render a bond in the molecule as a cylinder
                          or two cylinders
                          one of (resources.NUM_MODE_BONDS_MONOLITH_COLOR,
                          resources.NUM_MODE_BONDS_ATOMS_COLOR)
                          (default resources.NUM_MODE_BONDS_ATOMS_COLOR)
    resolution         -- resolution (default resources.NUM_RESOLUTION_VTK)
    background         -- background color in the HTML format
                          (default resources.COLOR_MOLECULE_WINDOW_BG)
    hydrogen_bond      -- whether hydrogen bonds are to be rendered
                          (default True)
    atom_labels        -- whether atom labels are to be rendered
                          (default False)
    color_sphere_1     -- color of the first hemisphere in the sphere mode
                          representation of vibrational motion
                          (default resources.COLOR_VIB_HEMISPHERE_1)
    color_sphere_2     -- color of the first hemisphere in the sphere mode
                          representation of vibrational motion
                          (default resources.COLOR_VIB_HEMISPHERE_2)                          
    bonds_transparency -- transparency level of the bonds (default 0.)
                          a value between 0. (completely opaque) and 1.
                          (completely transparent)
    color_picked_atom  -- color of picked atoms in the HTML format
                          (default resources.COLOR_PICKED_ATOM)
    invert_phase       -- whether the phase of vibrations is to be inverted
    mark_fragment      -- whether to mark the vibrational motion of a fragment
                          defined by the marked_vib_atoms property
                          (default False)
    show_marked_only   -- whether to show vibrational motion only on a fragment
                          defined by the marked_vib_atoms property
                          (default False)
    do_picking         -- whether picking of atoms is allowed (default False)
    do_render_picked   -- whether picked atoms are to be rendered
                          (default True)
    do_sync_rotation   -- whether the synchronized rotation is to be enabled
                          the second render widget must be supplied for this to
                          work
                          see synchronize_camera_state()
                          (default False)
    do_sync_zoom       -- whether the synchronized zooming is to be enabled
                          the second render widget must be supplied for this to
                          work
                          see synchronize_camera_state()
                          (default False)
    
    """
    vtktkrw.vtkTkRenderWidget.__init__(self, master,
                                       **self._tk_widget_kw(**kw))
    
    BaseWidget.__init__(self, **kw)

  def _init_vars(self) :
    """Initialize variables."""
    # 
    self.__molecule     = self._smartdict['molecule']
    self.__vib_toolbar  = self._smartdict['vib_toolbar']

    ## default keywords for rendering
    self._smartdict['molecule_mode']    = resources.NUM_MODE_BALLSTICK
    self._smartdict['bonds_mode']       = resources.NUM_MODE_BONDS_ATOMS_COLOR
    self._smartdict['resolution']       = resources.NUM_RESOLUTION_VTK
    self._smartdict['background']       = resources.COLOR_MOLECULE_WINDOW_BG
    self._smartdict['hydrogen_bond']      = True
    self._smartdict['atom_labels']        = False
    self._smartdict['color_sphere_1']     = resources.COLOR_VIB_HEMISPHERE_1
    self._smartdict['color_sphere_2']     = resources.COLOR_VIB_HEMISPHERE_2
    self._smartdict['bonds_transparency'] = 0.
    self._smartdict['color_picked_atom']  = resources.COLOR_PICKED_ATOM
    self._smartdict['invert_phase']       = False

    # 0-based list of picked atoms
    self.__picked_atoms_indices = []

    # will be used if a synchronous picking is desired
    # the users uses the left mouse button to pick atoms
    self.__picked_atom_pairs          = None
    self.__picked_atom_pairs_callback = None

    # do not marke a fragment by default
    self._smartdict['mark_fragment'] = False

    # do not show the vibrational motion on a fragment ONLY
    self._smartdict['show_marked_only'] = False
    
    # picking disabled by default
    self._smartdict['do_picking'] = False

    # a picked atom is rendered by default
    self._smartdict['do_render_picked'] = True

    # synchronous camera change
    # can set synchronous rotation, zoom
    self._sync_widget       = None

    # synchronous rotation is disabled by default
    self._smartdict['do_sync_rotation'] = False
    
    # synchronous zoom is disabled by default
    self._smartdict['do_sync_zoom'] = False

    # collecting all nodes is an internal dictionary
    self.__nodes = dict(atoms=[],
                        atom_labels=[],
                        bonds=[],
                        vibatoms=[],
                        triangles=[])

    # animator function id
    self.__animator_id = None

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    self.__renderer = vtk.vtkRenderer()
    self.GetRenderWindow().AddRenderer(self.__renderer)

    # installing a picker for atom selection
    # The picking is available with the left mouse button
    # if mouse does not move
    self.__picker = vtk.vtkPropPicker()
    self.__mouse_motion = False

    #self.background = self._smartdict['background']
    self.__renderer.SetBackground(
      misc.color_html_to_RGB(self._smartdict['background']))

    # installing lights
    lightKit = vtk.vtkLightKit()
    lightKit.MaintainLuminanceOn()
    lightKit.SetKeyLightIntensity(1.0)

    # warmth of the lights
    lightKit.SetKeyLightWarmth(0.65)
    lightKit.SetFillLightWarmth(0.6)

    # the function is called SetHeadLightWarmth starting from VTK 5.0
    # this is a very big stupidity :(
    try :
      lightKit.SetHeadLightWarmth(0.45)

    except :
      lightKit.SetHeadlightWarmth(0.45)
      
    # intensity ratios
    # back lights will be very dimm ;)
    lightKit.SetKeyToFillRatio(2.)
    lightKit.SetKeyToHeadRatio(7.)
    lightKit.SetKeyToBackRatio(1000.)
    
    lightKit.AddLightsToRenderer(self.__renderer)

    # first rendering of the molecule
    self.render_molecule()
    
    # install the camera if given
    if self._smartdict['camera'] is not None :
      self.camera = self._smartdict['camera']

  def _declare_properties(self) :
    """Declare properties of the widget."""
    # smart dictionary variables
    for prop in ('color_sphere_1', 'color_sphere_2',
                 'marked_vib_atoms', 'mark_fragment', 'show_marked_only',
                 'do_picking', 'do_render_picked', 'color_picked_atom',
                 'do_sync_rotation', 'do_sync_zoom',
                 'molecule_mode', 'bonds_mode',
                 'clicked_atom_callback', 'clicked_bond_callback',
                 'clicked_vibatom_callback') :
      self._add_property(prop, readonly=False)

    # Number of picked atoms
    self.__class__.Npicked = property(fget=self._get_Npicked)

    # List of 0-based indices of picked atoms
    self.__class__.picked_atoms_indices = property(
      fget=misc.Command(misc.Command.fget_value, self.__picked_atoms_indices))

    # Current molecule as an instance of pyviblic.molecule.Molecule
    self.__class__.molecule = property(fget=self._get_molecule,
                                       fset=self._set_molecule)
  
    # Background color of a 3D-window in hex format
    self.__class__.background = property(fget=self._get_background,
                                         fset=self._set_background)    

    # Renderer object
    self.__class__.renderer = property(fget=self._get_renderer)

    # If the perspective projection
    self.__class__.perspective_projection = property(
      fget=self._get_perspective_projection,
      fset=self._set_perspective_projection)

    # resolution of all the nodes of the current widget
    self.__class__.resolution = property(
      fget=self._get_resolution, fset=self._set_resolution)
    
    # Currently installed camera
    self.__class__.camera = property(
      fget=self._get_camera, fset=self._set_camera)

    # State of the currently installed camera (as a dictionary)
    self.__class__.camera_state = property(
      fget=self._get_camera_state, fset=self._set_camera_state)
  
  def _bind_events(self) :
    """Redefine the event binding of the base class.

    Final bindings :
          Left mouse button         -> rotate
          Right mouse button        -> zoom in/out
          Middle mouse button       -> pan
          Ctrl + left mouse button  -> roll

    """
    # events to be unbounded
    to_be_unbound = ('<ButtonPress>', '<ButtonRelease>',
                     '<B1-Motion>', '<Shift-B1-Motion>',
                     '<B3-Motion>',
                     '<KeyPress-r>', '<KeyPress-u>',
                     '<KeyPress-w>', '<KeyPress-s>', '<KeyPress-p>' )

    for ev in to_be_unbound :
      self.unbind(ev)

    # overriding the mouse press / release events
    # for picking with the left mouse button
    self.bind('<ButtonPress>'  , misc.Command(self.__ButtonPress))
    self.bind('<ButtonRelease>', misc.Command(self.__ButtonRelease))

    # slower rotation
    self.bind('<B1-Motion>', misc.Command(self.__rotate))

    # rolling function
    self.bind('<Control-B1-Motion>', misc.Command(self.__roll))

    # overriding zoom for synchronized camera motion ;)
    self.bind('<B3-Motion>', misc.Command(self.__zoom))

  def _tk_widget_kw(**kw) :
    """Get the keywords of the vtkTkRenderWidget.

    These are : width, height, rw
    
    """
    if kw :
      tk_widget_kw = {}

      for key in ('width', 'height', 'rw') :
        if key in kw :
          tk_widget_kw[key] = kw[key]
      return tk_widget_kw
    else :
      return {}

  _tk_widget_kw = staticmethod(_tk_widget_kw)

  def __ButtonPress(self, e) :
    """Handler for the mouse event <ButtonPress>."""
    self.StartMotion(e.x, e.y)
    self.__mouse_motion = False

  def __ButtonRelease(self, e) :
    """Handler for the mouse event <ButtonRelease>."""
    # superclass implementation
    self.EndMotion(e.x, e.y)

    if not self.__mouse_motion :
      self.__clicked_node(e.x, e.y, e.num)

  def __rotate(self, e) :
    """Reimplementation of the rotate function.

    Affects the widget to be synchronized with.
    
    """
    x, y = e.x, e.y
    
    euler_azimuth   = (self._LastX - x) * resources.NUM_MOUSE_SLOWING_FACTOR
    euler_elevation = (y - self._LastY) * resources.NUM_MOUSE_SLOWING_FACTOR
    
    self.rotate(euler_azimuth, euler_elevation)

    self._LastX = x
    self._LastY = y
    
    if self._sync_widget is not None and self.do_sync_rotation :
      self._sync_widget.rotate(euler_azimuth, euler_elevation)

  def __roll(self, e) :
    """Rotate the camera about the direction of projection.

    Affects the widget to be synchronized with.
    
    """
    x, y = e.x, e.y
    
    euler_roll = float(y - self._LastY) * resources.NUM_MOUSE_SLOWING_FACTOR

    self._LastX = x
    self._LastY = y
    
    self.rotate(0., 0., euler_roll)
    
    if self._sync_widget and self.do_sync_rotation :
      self._sync_widget.rotate(0., 0., euler_roll)

  def __zoom(self, e) :
    """Zoom in/out the camera.

    Affects the widget to be synchronized with.
    
    """
    x, y = e.x, e.y
    
    zoomFactor = pow(1.02, (0.5*(self._LastY - y)))

    self._LastX = x
    self._LastY = y

    self.zoom(zoomFactor)
    
    if self._sync_widget and self.do_sync_zoom :
      self._sync_widget.zoom(zoomFactor)

  def __clicked_node(self, x, y, num) :
    """The user has clicked on a node.

    num :
      1   : left mouse button
      2   : middle mouse button (the wheel)
      3   : right mouse button

    Callback functions must accept two args : (num, node_index)
    node_index is 0-based.

    Picking is handled *only* for the left mouse button.
    
    """
    self.__picker.Pick(x, self.winfo_height() - y - 1, 0., self.__renderer)
    node = self.__picker.GetAssembly()
      
    # processing only registered nodes
    if not isinstance(node, rendering.BaseNode ) :
      return

    node_index = -1
    callback   = None

    # atoms
    if isinstance(node, rendering.AtomNode) :
      # first all events
      if node in self.__nodes['atoms'] :
        node_index = self.__nodes['atoms'].index(node)
        callback   = self.clicked_atom_callback

      # only for picking
      # one can suppress the picking by setting the nodes
      # property "pickable" to False !
      if 1 == num and self.do_picking and \
         not node.get_picked() and node.get_pickable() :        
        if self.do_render_picked :
          # render a picked atom
          node.pick()
          self.Render()

          # saving the picked atom index
          self.__picked_atoms_indices.append(node_index)

          # handling atom pairs picking
          if self.__picked_atom_pairs is not None and \
             callable(self.__picked_atom_pairs_callback) :
            pairs = self.__picked_atom_pairs

            # the very first pair ;)
            if 0 == len(pairs) :
              pairs.append([node_index, -1])
            else :
              last_pair = pairs[len(pairs)-1]

              # completing a pair
              if -1 == last_pair[1] :
                last_pair[1] = node_index

              # starting the new pair
              elif 0 == last_pair.count(-1) :
                pairs.append([node_index, -1])

              else :
                return
            self.__picked_atom_pairs_callback(self)

    # bonds
    elif isinstance(node, rendering.BondNode) :
      if node in self.__nodes['bonds'] :
        node_index = self.__nodes['bonds'].index(node)
        callback   = self.clicked_bond_callback

    # vibrating atoms
    elif isinstance(node, rendering.VibratingAtomNode) :
      if node in self.__nodes['vibatoms'] :
        node_index = self.__nodes['vibatoms'].index(node)
        callback   = self.clicked_vibatom_callback

    # don't know how to handle
    else :
      return
    
    # calling
    if -1 != node_index and callable(callback) :
      callback(num, node_index)

  def __animate(self, Lx, scale_factor, nFrames, ms) :
    """Animate a normal node.

    Positional arguments :
    Lx           : cartesian excursions (one-based ndarray)
                   shape : (1 + Natoms, 4) with Natoms being
                   the number of atoms
    scale_factor : numeric factor with which the amplitude of vibrational
                   motion is multiplied
    nFrames      : number frames pro direction
    ms           : the time in milliseconds
    
    """
    # animating    
    self.__render_animation_frame(Lx, scale_factor, self.__frameno, nFrames)

    # frame number varies from -nFrames to +NFrames
    if self.__plus_direction :
      if self.__frameno == nFrames :
        self.__plus_direction = False
        self.__frameno -= 1
      else :
        self.__frameno += 1
    else :
      if self.__frameno == -nFrames :
        self.__plus_direction = True
        self.__frameno += 1
      else :
        self.__frameno -= 1

    self.__animator_id = self.after(ms, self.__animate, Lx,
                                    scale_factor, nFrames, ms)    

  def __render_animation_frame(self, Lx, scale_factor, frameno, nFrames) :
    """Render a frame."""
    coeff   = frameno * scale_factor / nFrames
      
    # transforming atoms (translation)
    atom_nodes = self.__nodes['atoms']

    for a in xrange(len(atom_nodes)) :
      t = vtk.vtkTransform()
      t.Translate(coeff * Lx[1 + a, 1:])
      
      atom_nodes[a].SetUserTransform(t)
      #atom_nodes[a].translate(coeff * Lx[1 + a, 1:])

    # transforming bonds (translation + rotation + scaling)
    bond_nodes = self.__nodes['bonds']

    for bond_node in bond_nodes :
      bond = bond_node.get_bond()
      bond_node.render_displaced(coeff * Lx[bond.atom1.index],
                                 coeff * Lx[bond.atom2.index])
    # making the changes visible
    self.Render()

  def _get_atom_labeldata(atom, mode) :
    """Get the label & radius of an Atom node."""
    if resources.NUM_MODE_STICK == mode :
      r = 0.1
    elif resources.NUM_MODE_BALLSTICK == mode :
      r = atom.element.r_coval * resources.NUM_FACTOR_SPHERE_RADIUS * 0.7
    else :
      r = atom.element.r_vdw * resources.NUM_FACTOR_SPHERE_RADIUS * 0.7
    
    return r, '%s%d' % (atom.element.symbol, atom.index)

  _get_atom_labeldata = staticmethod(_get_atom_labeldata)

  def __animate_vibration_poll(self, Lx, scale_factor, nFrames, ms) :
    """Animate a vibration via the Tkinter polling."""
    # current frame settings
    self.__frameno        = 0
    self.__plus_direction = True
    
    # if another animation already runs -> kill it and start a new one
    if self.__animator_id is not None :
      self.after_cancel(self.__animator_id)
    
    self.__animator_id = self.after(ms,
                                    self.__animate,
                                    Lx,
                                    scale_factor,
                                    nFrames,
                                    ms)

  def _set_camera(obj, camera) :
    """Install a new camera to the widget."""
    if camera is None :
      return
    MoleculeRenderWidget._set_camera_state(
      obj, MoleculeRenderWidget._get_camera_state(obj, camera=camera))

  _set_camera = staticmethod(_set_camera)

  def _set_camera_state(obj, camera_state) :
    """Set a new camera state."""
    for prop in resources.STRINGS_CAMERA_PROPERTIES :
      if prop not in camera_state :
        raise InvalidArgumentError('%s key missing' % prop)
    
    camera = obj.camera

    # set new values
    camera.SetParallelScale(camera_state['ParallelScale'])
    camera.SetFocalPoint(camera_state['FocalPoint'])
    camera.SetPosition(camera_state['Position'])
    camera.SetClippingRange(camera_state['ClippingRange'])
    camera.ComputeViewPlaneNormal()
     
    camera.SetViewUp(camera_state['ViewUp'])
    camera.OrthogonalizeViewUp()

    camera.SetParallelProjection(camera_state['ParallelProjection'])

    obj.Render()

  _set_camera_state = staticmethod(_set_camera_state)

  def _get_camera_state(obj, **kw) :
    """Return the camera state of a given camera.

    Keywords arguments :
    camera -- camera (default None)
              if None use the current camera

    """
    camera = kw.get('camera', None) or obj.camera
    
    camera_state = {}

    # saving the camera properties
    camera_state['ParallelProjection']  = camera.GetParallelProjection()
    camera_state['ParallelScale']       = camera.GetParallelScale()
    camera_state['FocalPoint']          = camera.GetFocalPoint()
    camera_state['Position']            = camera.GetPosition()
    camera_state['ClippingRange']       = camera.GetClippingRange()
    camera_state['ViewUp']              = camera.GetViewUp()
      
    return camera_state

  _get_camera_state = staticmethod(_get_camera_state)

  def _get_camera(obj) :
    """Get the current camera installed in the widget."""
    return obj.__renderer.GetActiveCamera()

  _get_camera = staticmethod(_get_camera)

  def _set_molecule(obj, newmol) :
    """Install a new molecule to the widget."""
    obj.__molecule = newmol
    obj.render_molecule()
    obj.Render()

  _set_molecule = staticmethod(_set_molecule)

  def _get_molecule(obj) :
    """Get the molecule."""
    return obj.__molecule

  _get_molecule = staticmethod(_get_molecule)

  def _set_perspective_projection(obj, perspective) :
    """Turn the perspective projection on / off."""
    if perspective :
      obj.camera.ParallelProjectionOff()
    else :
      obj.camera.ParallelProjectionOn()

    obj.Render()

  _set_perspective_projection = staticmethod(_set_perspective_projection)

  def _get_perspective_projection(obj) :
    """Whether the camera is instructed to do the perspective projection."""
    return not obj.camera.GetParallelProjection()

  _get_perspective_projection = staticmethod(_get_perspective_projection)

  def _set_resolution(obj, resolution) :
    """Set the a resolution for all nodes of the widget.

    Usefull when the user makes a snapshot and
    wants to use the better rendering quality.
    
    """
    for t in obj.__nodes :
      for node in obj.__nodes[t] :
        if isinstance(node, rendering.BaseNode) :
          node.set_resolution(resolution)

    obj.Render()
    obj._smartdict.update_(dict(resolution=resolution))

  _set_resolution = staticmethod(_set_resolution)

  def _get_resolution(obj) :
    """Get the current resolution."""
    return obj._smartdict['resolution']

  _get_resolution = staticmethod(_get_resolution)

  def _get_Npicked(obj) :
    """Get the number of picked atoms."""
    return len(obj.__picked_atoms_indices)

  _get_Npicked = staticmethod(_get_Npicked)

  def _get_background(obj) :
    """Get the background color in the HTML format."""
    return misc.color_RGB_to_html(obj.__renderer.GetBackground())

  _get_background = staticmethod(_get_background)

  def _set_background(obj, value) :
    """Set the new background."""
    obj.__renderer.SetBackground(misc.color_html_to_RGB(value))

  _set_background = staticmethod(_set_background)

  def _get_renderer(obj) :
    """Get the renderer."""
    return obj.__renderer

  _get_renderer = staticmethod(_get_renderer)
  
  def cleanup(self) :
    """Clean up the widget by removing all its actors."""
    if self.__renderer is None :
      return

    # kill an animation if it runs
    if self.__animator_id is not None :
      self.after_cancel(self.__animator_id)

    # clean of picked atoms
    del self.__picked_atoms_indices[:]

    # reinitializing the nodes 
    for key in self.__nodes.keys() :
      del self.__nodes[key][:]

    # finally cleaning the renderer
    # vtkViewport::RemoveAllProps() is deprecated in VTK-5.0
    try :
      self.__renderer.RemoveAllViewProps()
    except :
      # for older VTK
      self.__renderer.RemoveAllProps()

  def render_molecule(self, **kw) :
    """Render the molecule.
    
    Keywords arguments :
    resolution         -- resolution (default resources.NUM_RESOLUTION_VTK)
    molecule_mode      -- render the molecule in the ball & stick, stick or
                          van der Waals radii representation
                          one of (resources.NUM_MODE_BALLSTICK,
                          resources.NUM_MODE_STICK,
                          resources.NUM_MODE_VDW)
    bonds_mode         -- render a bond in the molecule as a cylinder
                          or two cylinders
                          one of (resources.NUM_MODE_BONDS_MONOLITH_COLOR,
                          resources.NUM_MODE_BONDS_ATOMS_COLOR)
                          (default resources.NUM_MODE_BONDS_ATOMS_COLOR)                          
    color_picked_atom  -- color of picked atoms in the HTML format
                          (default resources.COLOR_PICKED_ATOM)
    rounded_bond       -- whether the bonds are to be rendered rounded
                          (default False)
    hydrogen_bond      -- whether hydrogen bonds are to be rendered
                          (default True)
    atom_labels        -- whether atom labels are to be rendered
                          (default False)
                          
    """
    if self.__molecule is None :
      return

    # do not forget to clean !!!
    self.cleanup()

    self._smartdict.merge()
    self._smartdict.kw = kw
    props = self._smartdict
    
    ## let the control change without waiting for the rendering to complete
    self.update_idletasks()

    # atoms & labels
    if ( resources.NUM_MODE_BALLSTICK == props['molecule_mode'] \
         or resources.NUM_MODE_VDW == props['molecule_mode'] ) :    
      for atom in self.__molecule.atoms :
        atom_node = rendering.AtomNode(
          atom,
          mode=props['molecule_mode'],
          resolution=props['resolution'],
          color_picked_atom=props['color_picked_atom'])
        
        self.__nodes['atoms'].append(atom_node)        
        self.__renderer.AddActor(atom_node)
                  
    # rendering bonds
    for bond in self.__molecule.bonds :
      if not bond.is_hydrogen or bond.is_hydrogen and props['hydrogen_bond'] :
        bond_node = rendering.BondNode(
          bond,
          mode=props['bonds_mode'],
          transparency=props['bonds_transparency'],
          resolution=props['resolution'],
          rounded_bond=props['rounded_bond'])

        self.__nodes['bonds'].append(bond_node)        
        self.__renderer.AddActor(bond_node)

    # atom labels
    if props['atom_labels'] :      
      self.Render()
      
      camera = self.__renderer.GetActiveCamera()      
      for atom in self.__molecule.atoms :      
        r, text = self._get_atom_labeldata(atom,
                                           self._smartdict['molecule_mode'])
        atom_label = rendering.TextFollowerNode(text,
                                               (r, r, r) + atom.coord[1:],
                                                camera)
        self.__nodes['atom_labels'].append(atom_label)
        self.__renderer.AddActor(atom_label)          

    # reporting to the user
    if self._smartdict['msgBar'] is not None :
      self._smartdict['msgBar'].message('state', 'Structure')
      
  def render_vibration(self, **kw) :
    """Render a vibration.
    
    Keyword arguments :
    vib_no          -- number of the vibration
                       *must* be supplied if vib_toolbar is None
    resolution      -- resolution (default resources.NUM_RESOLUTION_VTK)
    mode            -- sphere, arrow representation or animation
                       one of
                       (resources.STRING_MODE_VIB_REPRESENTATION_SPHERES,
                       resources.STRING_MODE_VIB_REPRESENTATION_ARROWS,
                       resources.STRING_MODE_VIB_REPRESENTATION_ANIMATION)
                       *must* be supplied if vib_toolbar is None
    rep_type        -- cartesian or mass-weighted excursions
                       one of (resources.STRING_VIB_ENERGY,
                       STRING_VIB_EXCURSIONS)
                       *must* be supplied if vib_toolbar is None                  
    rep_subtype     -- representation subtype
                       one of (STRING_VIB_ENERGY_VOLUME,
                       STRING_VIB_ENERGY_VOLUME_ZERO_POINT,
                       STRING_VIB_EXCURSIONS_DIAMETER,
                       STRING_VIB_EXCURSIONS_DIAMETER_ZEROPOINT,
                       STRING_VIB_EXCURSIONS_DIAMETER_STANDARD)
                       *must* be supplied if vib_toolbar is None
    scale_factor    -- multiply factor for the amplitude of vibrational motion
                       *must* be supplied if vib_toolbar is None
    invert_phase    -- whether the phase of the vibration is to be inverted
                       *must* be supplied if vib_toolbar is None                       
    color_sphere_1  -- color of the first hemisphere in the sphere mode, i.e.
                       mode = resources.STRING_MODE_VIB_REPRESENTATION_SPHERES
                       (default resources.COLOR_VIB_HEMISPHERE_1)
    color_sphere_2  -- color of the first hemisphere in the sphere mode, i.e.
                       mode == resources.STRING_MODE_VIB_REPRESENTATION_ARROWS
                       (default resources.COLOR_VIB_HEMISPHERE_2)
                                       
    """
    if self.__vib_toolbar is None and kw is None :
      raise InvalidArgumentError(
        'Vibrational toolbar or correspondent keywords must be given')

    # do nothing if the representation type is not set
    # for a static representation
    if self.__vib_toolbar is not None and \
       ( self.__vib_toolbar.rep_type is None and \
         resources.STRING_MODE_VIB_REPRESENTATION_ANIMATION != \
         self.__vib_toolbar.mode ):
      return

    self._smartdict.merge()
    self._smartdict.kw = kw
    props = self._smartdict

    ## packing keywords for atoms
    atoms_kw = dict()

    # vibration properties
    params_vib = ('mode', 'rep_type', 'rep_subtype', 'scale_factor',
                  'invert_phase')

    for param in params_vib :
      if self.__vib_toolbar :
        atoms_kw[param] = getattr(self.__vib_toolbar, param)
      else :
        if props[param] is None :
          raise InvalidArgumentError('Keyword %s must be supplied' % param)

        atoms_kw[param] = props[param]
        
    # vibration number
    # negative vibrations mean translations / rotations
    if self.__vib_toolbar is not None :
      vib_no = self.__vib_toolbar.vib_no      
    else :
      if props['vib_no'] is None :
        raise InvalidArgumentError(
          'vib_no must be given if a vibrational toolbar is not given')    
      vib_no = props['vib_no']

    # frequency
    # translations / rotations have the frequency of 0.
    if 0 > vib_no :
      freq = 0.
    else :
      freq = self.__molecule.freqs[vib_no]
      
    if atoms_kw['invert_phase'] :
      atoms_kw['color_sphere_1'] = self._smartdict['color_sphere_2']
      atoms_kw['color_sphere_2'] = self._smartdict['color_sphere_1']
    else :
      atoms_kw['color_sphere_1'] = self._smartdict['color_sphere_1']
      atoms_kw['color_sphere_2'] = self._smartdict['color_sphere_2']

    atoms_kw['resolution'] = props['resolution']

    ## let the control change without waiting for the rendering to complete
    self.tk.call('update', 'idletasks')
    
    ## choose an appropriate displacement type for a selected vibration
    if resources.STRING_VIB_ENERGY == atoms_kw['rep_type'] :
      if vib_no < 0 :
        L_displ = self.__molecule.L_tr_rot[-vib_no]
      else :
        L_displ = self.__molecule.L[vib_no]      
    else :
      if vib_no < 0 :
        L_displ = self.__molecule.Lx_tr_rot[-vib_no]
      else :
        L_displ = self.__molecule.Lx[vib_no]
        
    ## rendering 
    self.cleanup()

    ## dynamic representation : animation
    if resources.STRING_MODE_VIB_REPRESENTATION_ANIMATION == atoms_kw['mode'] :

      # render the molecule in ball & stick representation
      # do not render hydrogen bonds !
      self.render_molecule(molecule_mode=resources.NUM_MODE_BALLSTICK,
                           bonds_mode=resources.NUM_MODE_BONDS_ATOMS_COLOR,
                           resolution=self._smartdict['resolution'],
                           rounded_bond=False,
                           hydrogen_bond=False,
                           atom_labels=False)

      anim_kw = dict(Lx=sqrt(AMU2AU) * self.__molecule.Lx[vib_no],
                     scale_factor=atoms_kw['scale_factor'],
                     nFrames=5,
                     ms=30)      
      self.__animate_vibration_poll(**anim_kw)
                 
    ## static representations : spheres & arrows
    else :
      # kill the animation if it runs
      if self.__animator_id is not None :
        self.after_cancel(self.__animator_id)
        self.__animator_id = None

      # render the molecule in monolith stick representation
      # do not render hydrogen bonds !
      self.render_molecule(molecule_mode=resources.NUM_MODE_STICK,
                           bonds_mode=resources.NUM_MODE_BONDS_MONOLITH_COLOR,
                           resolution=props['resolution'],
                           rounded_bond=False,
                           hydrogen_bond=False,
                           atom_labels=False)      
      # render
      for atom in self.__molecule.atoms :
        # exclude unnecessary atoms
        if self.marked_vib_atoms is not None :
          if self.show_marked_only and \
             atom.index not in self.marked_vib_atoms :
            continue
        
        vibrating_atom_node = rendering.VibratingAtomNode(atom,
                                                          L_displ,
                                                          freq, **atoms_kw)
        self.__nodes['vibatoms'].append(vibrating_atom_node)        
        self.__renderer.AddActor(vibrating_atom_node)

        # mark the vibrational motion if all atoms will be shown
        # and it is explicitely set by the 'mark fragment'
        # do not mark if the user wants to see the fragment only !
        mark_it = self.mark_fragment and self.marked_vib_atoms is not None \
                  and atom.index in self.marked_vib_atoms and \
                  not self.show_marked_only        
        if mark_it :
          vibrating_atom_node.pick()

      self.Render()

    # reporting to the user
    if self._smartdict['msgBar'] is not None :
      p = (vib_no, freq, atoms_kw['rep_type'], atoms_kw['rep_type'])
      
      self._smartdict['msgBar'].message(
        'state', 'Vibration %d ( %.2f ), %s / %s' % p)

  def render_triangle(self, i1, i2, i3, **kw) :
    """Render a triangle.

    Positional arguments :
    i1, i2, i3 -- coordinates of the vertices (one-based ndarray)
                  shape : (4,)

    Keyword arguments :
    see pyviblib.gui.rendering.BaseNode

    """
    Natoms = self.__molecule.Natoms
    indices = (i1, i2, i3)
    for i in indices :
      if 0 > i or i >= Natoms :
        raise InvalidArgumentError('Invalid atom index passed : %d' % i)

    # rendering
    p = []
    for i in indices :
      p.append(self.__molecule.atoms[i].coord)
    
    triag = rendering.TriangleNode(*p, **kw)

    self.__nodes['triangles'].append(triag)
    self.__renderer.AddActor(triag)

    self.Render()

  def render_scalars(self, scalars, scale_factor=1.0) :
    """Render scalar values on the atoms such as e.g. ACPs.

    Position arguments :
    scalars      -- values to be rendered (one-based array)
                    shape : (1 + Natoms) with Natoms being the number of atoms
                    in the molecule

    Keyword arguments :
    scale_factor -- numeric factor with which the radii of the spheres are
                    multiplied
                    (default 1.)
              
    """
    if self.__molecule is None :
      return
    
    if scalars is None or (1 + self.__molecule.Natoms) != len(scalars) :
      raise InvalidArgumentError('Invalid arguments passed')
    
    # render the molecule in monolith stick representation
    self.render_molecule(molecule_mode=resources.NUM_MODE_STICK,
                         bonds_mode=resources.NUM_MODE_BONDS_MONOLITH_COLOR,
                         hydrogen_bond=False,
                         resolution=self._smartdict['resolution'])
    # scalars on the atom positions
    if 'scalars' not in self.__nodes :
      self.__nodes['scalars'] = []
      
    for atom in self.__molecule.atoms :
      scalar_node = rendering.ScalarSphereNode(
        scalars[atom.index],
        atom.coord[1:],
        mode=resources.NUM_MODE_PROPORTIONAL_TO_SURFACE,
        resolution=self._smartdict['resolution'],
        scale_factor=scale_factor)
      
      self.__nodes['scalars'].append(scalar_node)  
      self.__renderer.AddActor(scalar_node)

  def render_gcp(self, acp, groups, scale_factor=1.0) :
    """Render group contribution patterns (GCPs).

    The contributions are placed in center of gravities of the groups.

    Positional arguments :
    acp          -- atomic contribution patterns (one-based ndarray)
                    shape : (1 + Ngr,) with Ngr being the number of groups
    groups       -- groups (null-based list)
                    atom numbers are one-based
                    example : [[1, 4], [2, 7]]

    Keyword arguments :                  
    scale_factor -- numeric factor with which the radii of the spheres are
                    multiplied
                    (default 1.)

    """
    if self.__molecule is None :
      return

    # trying to sum up the acps
    acp_g = make_gcp(acp, groups)

    # render the molecule in monolith stick representation
    self.render_molecule(molecule_mode=resources.NUM_MODE_STICK,
                         bonds_mode=resources.NUM_MODE_BONDS_MONOLITH_COLOR,
                         resolution=self._smartdict['resolution'],
                         rounded_bond=True,
                         hydrogen_bond=False,
                         atom_labels=False)

    # saving references to the vtk objects
    if 'acp_groups' not in self.__nodes :
      self.__nodes['acp_groups'] = []

    # rendering the scalars acp_g in the mass centers of the groups
    for g in xrange(len(groups)) :
      
      # mass center
      grp = array([0] + groups[g], 'l')
      M_g = mass_center(self.__molecule.coords, self.__molecule.masses, grp)

      # sphere
      scalar_node = rendering.ScalarSphereNode(
        acp_g[1 + g],
        M_g[1:],
        mode=resources.NUM_MODE_PROPORTIONAL_TO_SURFACE,
        resolution=self._smartdict['resolution'],
        scale_factor=scale_factor)
      
      self.__nodes['acp_groups'].append(scalar_node)  
      self.__renderer.AddActor(scalar_node)

      # text following labeling the group
      r = scalar_node.get_radius()
      
      group_label = rendering.TextFollowerNode('%d' % (1 + g),
                                              (r, r, r) + M_g[1:],
                                               self.camera)
      self.__nodes['acp_groups'].append(group_label)
      self.__renderer.AddActor(group_label)

  def rotate(self, euler_azimuth=0., euler_elevation=0., euler_roll=0.):
    """Rotate the active camera at given Euler angles.

    Keyword arguments :
    euler_azimuth   -- angle of rotation about the view up vector
                       centered at the focal point of the camera
                       (default 0.)
    euler_elevation -- angle of rotation about the cross product of the
                       direction of projection and the view up vector
                       centered on the focal point
                       (default 0.)
    euler_roll      -- angle of rotation about the direction of projection
                       of the camera
                       (default 0.)
    
    The rotation does *not* affect the synchronized widget.
    
    """
    self._CurrentCamera = self.camera

    if self._CurrentCamera is None :
      return
      
    self._CurrentCamera.Azimuth(euler_azimuth)
    self._CurrentCamera.Elevation(euler_elevation)
    self._CurrentCamera.Roll(euler_roll)
    
    self._CurrentCamera.OrthogonalizeViewUp()
    
    self.__renderer.ResetCameraClippingRange()
    self.Render()

    self.__mouse_motion = True

  def zoom(self, zoomFactor):
    """Zoom in/out.

    Positional arguments :
    zoomFactor -- the height of the viewport in world-coordinate distances.
                  Note that this factor works as an "inverse scale" i.e.
                  larger numbers produce smaller images.
                  This factor has no meaning in perspective projection mode.

    The zooming does *not* affect the synchronized widget.
    
    """
    renderer = self.__renderer

    self._CurrentZoom *= zoomFactor

    if self.camera.GetParallelProjection():
      parallelScale = self.camera.GetParallelScale() / zoomFactor
      self.camera.SetParallelScale(parallelScale)
    else:
      self.camera.Dolly(zoomFactor)
      renderer.ResetCameraClippingRange()

    self.Render()
      
  def start_pairs_picking(self, pairs, callback) :
    """Start a synchronous picking of atoms in two render widgets.

    Positional arguments :
    pairs    -- reference to the picked atom pairs
    callback -- callable function which accepts one argument being the
                the widget

    """
    if pairs is None :
      raise InvalidArgumentError('Invalid pairs parameter')
    
    if not callable(callback) :
      raise InvalidArgumentError('callback must be a callable')

    self.do_picking = True
    self.__picked_atom_pairs          = pairs
    self.__picked_atom_pairs_callback = callback

  def end_pairs_picking(self) :
    """End the synchronous picking of atoms started with start_pairs_picking().
    """
    self.do_picking                   = False
    self.__picked_atom_pairs          = None
    self.__picked_atom_pairs_callback = None

  def depick_atoms(self, atom_index_list=None) :
    """Deselect the picked atoms.

    Keyword arguments :
    atom_index_list -- list of 0-based indices of *PICKED* atoms
                       these are NOT indices of atoms to be unpicked !!!
                       If None, use all the *PICKED* atoms
                       
    If the only element in the list is -1 -> depick the last picked atom.
    
    """
    if self.__picked_atoms_indices is None :
      return

    Natoms_picked = len(self.__picked_atoms_indices)

    # if list is not given -> remove all picked atoms
    if atom_index_list is None :
      atom_index_list = xrange(Natoms_picked)

    elif 1 == len(atom_index_list) and -1 in atom_index_list :
      atom_index_list = [Natoms_picked - 1]
      
    # depicking
    for a in atom_index_list :
      if 0 <= a and a < Natoms_picked :
        self.__nodes['atoms'][self.__picked_atoms_indices[a]].unpick()

    # finally removing from the list
    misc.remove_indices_from_list(self.__picked_atoms_indices, atom_index_list)

    self.Render()

  def pick_atoms(self, atom_index_list=None) :
    """Pick given atoms.

    If the atom list is not supplied, all the atoms are picked.

    Positional arguments :
    atom_index_list -- atom indices (null-based ndarray)
                       indices are null-based
    
    """
    # if list is None pick all atoms
    if atom_index_list is None :
      atom_index_list = xrange(self.molecule.Natoms)

    for a in atom_index_list :
      self.__nodes['atoms'][a].pick()
      
      # save the picked atom if it is not in the list
      if a not in self.__picked_atoms_indices :
        self.__picked_atoms_indices.append(a)

    self.Render()
    
  def highlight_picked_atoms(self, atom_index_list, highlight=True) :
    """Highlight/unhighlight the picked atoms.

    Nothing is done the atom list is not supplied.

    Positional arguments :
    atom_index_list -- atom indices (null-based ndarray)
                       indices are null-based

    Keyword arguments :
    highlight       -- whether to highlight (default True)
  
    """
    if self.__picked_atoms_indices is None :
      return

    Natoms_picked = len(self.__picked_atoms_indices)

    # highlight
    for a in atom_index_list :
      if 0 > a or a >= Natoms_picked :
        continue

      atom_node = self.__nodes['atoms'][self.__picked_atoms_indices[a]]
      atom_node.highlight_picked(highlight)

    self.Render()

  def remove_triangles(self) :
    """Remove the triangles."""
    if not self.__renderer or 0 == len(self.__nodes['triangles']) :
      return

    for triag in self.__nodes['triangles'] :
      self.__renderer.RemoveActor(triag)

    del self.__nodes['triangles'][:]

    self.Render()

  def synchronize_camera_state(self, sync_widget) :
    """Set a render widget for synchronous rotation/zooming.

    By default the rotation and zooming are synchronized.
    Consider the do_sync_rotation and do_sync_zoom properties to control the
    synchronized behaviour.
  
    Positional arguments :
    sync_widget -- the render widget
                   can be None
    
    """
    self._sync_widget     = sync_widget
    self.do_sync_rotation = True
    self.do_sync_zoom     = True

  def get_node(self, category, index) :
    """Get a node.

    Positional arguments :
    category -- type of the node
                one of ('atoms', 'bonds', 'vibatoms', 'atom_labels')
    index    -- index of the node (null-based)
    
    Return None unless argument are valid or nothing is found.
    
    """
    if category is None or category not in self.__nodes :
      return None

    if 0 > index or len(self.__nodes[category]) <= index :
      return None

    return self.__nodes[category][index]

  def snapshot(self, filename,
               format='tiff', magnification=1, resolution=None) :
    """Make a snapshot of the 3D render window.

    Positional arguments :
    filename       -- file name of the snapshot

    Keyword arguments :
    format         -- image format
                      one of ('jpeg', 'tiff', 'png', 'eps', 'ppm')
                      (default 'tiff')
    magnification  -- integer magnification factor for the 3D render window
                      (default 1)
    resolution     -- resolution (default None)
                      if None, use the current resolution

    """
    # assigning an appropriate writer
    format = format.lower()
    
    if format not in resources.STRINGS_VTK_SNAPSHOT_FORMATS :
      raise InvalidArgumentError('Unsupported format : %s' % format)

    writer = None
    
    if 'jpeg' == format :
      writer = vtk.vtkJPEGWriter()
      writer.SetQuality(100)
      
    elif 'tiff' == format :
      writer = vtk.vtkTIFFWriter()
      
    elif 'png' == format :
      writer = vtk.vtkPNGWriter()
      
    elif 'eps' == format :
      writer = vtk.vtkPostScriptWriter()

    elif 'ppm' == format :
      writer = vtk.vtkPNMWriter()

    # setting the resolution
    if resolution :
      self.resolution = resolution
      self.Render()

    # setting the image filter & saving
    image_filter = vtk.vtkWindowToImageFilter()
    image_filter.SetMagnification(magnification)
    
    image_filter.SetInput(self.GetRenderWindow())
    writer.SetInput(image_filter.GetOutput())

    writer.SetFileName(filename)
    writer.Write()

    # reminding to vtk that the actual object should be seen in the window
    self.Render()

  def create_animation_frames(self, Lx, scale_factor, nFrames,
                              resolution=10, format='ppm',
                              transparent_bg=False) :
    """Create a series of files for animation of a vibration.

    The function does not compile the result images to the animation.
    It produces the files and returns the name of file with a list
    of the created frames.
    The files will be stored in a temporaral directory.

    Positional arguments :
    Lx              -- cartesian excursion of the vibration (one-based ndarray)
                       shape : (1 + Natoms, 4) with Natoms being the number of
                       atoms
    scale_factor    -- numeric factor with which the radii of the spheres are
                       multiplied
    nFrames         -- number of frame pro direction

    Keyword arguments :
    resolution      -- resolution (default 10)
    format          -- image format
                       one of ('jpeg', 'tiff', 'png', 'eps', 'ppm', 'gif')
                       (default 'ppm')
                       if 'gif' is supplied, then the ppmtogif utility from the
                       Netpbm package should be installed
                       See http://netpbm.sourceforge.net/
    transparent_bg  -- whether the background should be made transparent
                       (default False)                    
    
    """
    if Lx is None or 0. > scale_factor or 0 > nFrames or 0 > resolution or \
       not (format.lower() in resources.STRINGS_VTK_SNAPSHOT_FORMATS or \
            format.lower() == 'gif') :
      raise InvalidArgumentError('Invalid input parameter(s) passed')

    # if an animation runs -> stop it
    if self.__animator_id :
      self.after_cancel(self.__animator_id)

    # rendering the molecule with the specified resolution
    self.render_molecule(resolution=resolution,
                         molecule_mode=resources.NUM_MODE_BALLSTICK,
                         bonds_mode=resources.NUM_MODE_BONDS_ATOMS_COLOR,
                         rounded_bond=False,
                         hydrogen_bond=False,
                         atom_labels=False)

    # make sure that all GUI elements are updated
    self.tk.call('update')

    ## making snapshots & a list file :
    # 1) from 0 to nFrames
    # 2) from nFrames to -nFrames
    # 3) from -nFrames to 0
    range_ = range(nFrames) + range(nFrames, -nFrames, -1) + range(-nFrames, 0)

    # creating a temporaral directory for storing of the files
    # list file will be saved there
    tmpdir   = tempfile.mkdtemp()
    
    listfile = os.path.join(tmpdir, 'list')
    file_ = open(listfile, 'w+')

    # total number of frames
    nTotalFrames = 4 * nFrames

    # 
    no_fields = 1 + int(floor(log(nTotalFrames, 10)))
    format_file = os.path.join(tmpdir, 'frame%%0%dd.%%s' % no_fields)
    
    start_time = clock()
    for i in xrange(len(range_)) :
      frameno = range_[i]      

      # saving to the list file
      filename = format_file % (i, format)
      file_.write(filename + '\n')

      # sending a message to the status bar of the molecule window
      if self._smartdict['msgBar'] is not None :
        self._smartdict['msgBar'].message('state',
                                          'Saving frame %d / %d' % \
                                          (1 + i, nTotalFrames))

      self.__render_animation_frame(Lx, scale_factor, frameno, nFrames)
      self.update()

      # if format is gif one needs first to generate a ppm file
      # and then start ppmtogif to convert it finally to gif
      # raising an exception if this conversion failed
      if 'gif' == format.lower() :
        # producing ppm
        ppmname = format_file % (i, 'ppm')
        self.snapshot(ppmname, format='ppm', magnification=1)

        # using Netpbm utilities to convert it to gif
        palette = os.path.join(tmpdir, 'palette')
        gifname = format_file % (i, 'gif')
        
        cmd = r'pnmcolormap 256 "%s" > "%s" && ' % (ppmname, palette) + \
              r'pnmremap -mapfile "%s" "%s" | ppmtogif ' % \
              (palette, ppmname)

        if transparent_bg :
          cmd = ''.join((cmd, r'--transparent="%s"' % self.background))

        cmd = ''.join((cmd, r'> "%s"' % gifname))
        
        if os.system(cmd) :
          raise RuntimeError(
              r'Conversion to "%s" failed :(' % os.path.basename(gifname))
      else :
        self.snapshot(filename, format=format, magnification=1)

    file_.close()

    if self._smartdict['msgBar'] is not None :
      total_time = clock() - start_time
      self._smartdict['msgBar'].message(
        'state',
        'Completed in %.3fs (%.3fs pro frame)' % \
        (total_time, total_time / nTotalFrames))

    return listfile


class ButtonToolbar(BaseWidget, Tkinter.Frame) :
  """Button toolbar.

  The widget is based on Tkinter.Frame.

  The following public methods are exported :
      add_button()    -- add a button
      add_separator() -- add a separator
  
  """

  def __init__(self, master, **kw) :
    """Constructor of the class.

    Positional arguments :
    master     -- parent widget
    
    Keyword arguments :
    style      -- style of the toolbar
                  0 : raised with a thin border
                  1 : flat without any border
                  (default 0)
    horizontal -- whether the toolbar is horizontal (default True)
    button_pad -- padding for the buttons being added (default 3)
    
    """
    Tkinter.Frame.__init__(self, master, **self._frame_kw(**kw))
    BaseWidget.__init__(self, **kw)

  def _frame_kw(**kw) :
    """Retrieve the keywords for the Tkinter.Frame."""
    frame_kw = {}

    style = kw.get('style', 0)

    # raised frame with a thin border
    if 0 == style :
      frame_kw['borderwidth'] = 1
      frame_kw['relief']      = 'raised'

    # flat frame without any border
    elif 1 == style :
      frame_kw['borderwidth'] = 0
      frame_kw['relief']      = 'flat'
    else :
      raise ConstructorError('Invalid style: %s' % style)

    return frame_kw

  _frame_kw = staticmethod(_frame_kw)
    
  def _init_vars(self) :
    """Initialize variables."""
    self._smartdict['style']      = 0
    self._smartdict['horizontal'] = True
    self._smartdict['button_pad'] = 3

    # default keywords for buttons
    if 0 == self._smartdict['style'] :
      self._varsdict['button_relief']     = 'flat'
      self._varsdict['button_overrelief'] = 'raised'

    elif 1 == self._smartdict['style'] :
      self._varsdict['button_relief']     = 'raised'
      self._varsdict['button_overrelief'] = 'raised'

    # last value of row or column depending on if the toolbar is horizonal
    self._varsdict['grid_counter'] = 0

    # list of the buttons
    self._varsdict['ar_buttons'] = []    

  def _constructGUI(self) :
    """Nothing is done since the buttons are added dynamically."""
    pass

  def __get_grid_params(self, forbutton=True) :
    """Get the grid parameters for self.grid().

    Keyword arguments :
    forbutton -- True for an usual button, False for a separator (default True)

    The grid counter will not be incremented !
    
    """
    if self._smartdict['horizontal'] :
      row    = 0
      column = self._varsdict['grid_counter']

      if forbutton :
        sticky = 'w'
      else :
        sticky = 'ns'
    else :
      row    = self._varsdict['grid_counter']
      column = 0

      if forbutton :
        sticky = 'n'
      else :
        sticky = 'we'

    return dict(row=row,
                column=column,
                padx=self._smartdict['button_pad'],
                pady=self._smartdict['button_pad'],
                sticky=sticky)

  def add_button(self, **kw) :
    """Add a button.

    The methods accepts the keyword arguments for Tkinter.Button.

    Keyword arguments (specific for this method):
    helptext  -- help message which is shown if the mouse is over the button
                 (default None)
    imagename -- name of the image resource
                 either the imagename or image argument must be supplied

    Return the reference to the button created.
    
    """
    # customizing the button's keywords
    if 'helptext' in kw :
      helptext = kw['helptext']
      del kw['helptext']

    # images
    if 'image' in kw and 'imagename' in kw :
      raise InvalidArgumentError(
        'Either the image or imagename arguments must be supplied')

    if 'imagename' in kw :
      kw['image'] = getimage(kw['imagename'])
      del kw['imagename']

    kw['relief']     = kw.get('relief', self._varsdict['button_relief'])
    kw['overrelief'] = kw.get('overrelief', self._varsdict['button_overrelief'])
    
    btn = Tkinter.Button(self, **kw)
    btn.grid(**self.__get_grid_params(forbutton=True))

    # saving
    self._varsdict['ar_buttons'].append(btn)

    # help
    if helptext :
      self._balloon.bind(btn, helptext)

    self._varsdict['grid_counter'] += 1

    return btn

  def add_separator(self) :
    """Add a separator."""
    kw = dict(bd=1, relief='sunken')
    
    if self._smartdict['horizontal'] :
      kw['width']  = 2
    else :
      kw['height'] = 2
      
    separator = Tkinter.Frame(self, **kw)
    separator.grid(**self.__get_grid_params(forbutton=False))

    self._varsdict['grid_counter'] += 1
    

class VibrationalToolbar (BaseWidget, Pmw.ScrolledFrame) :
  """Widget for navigating through vibrations.

  The widget is based on Pmw.ScrolledFrame.

  The following read-only properties are exposed :      
      mode                    -- sphere, arrow, animation or structure
      rep_type                -- cartesian or mass-weighted excursions
      rep_subtype             -- representation subtype
      invert_phase            -- whether the phase is to be inverted
      scale factor            -- factor for the amplitude of vibrational motion

  The following readable and writable properties are exposed :
      vib_no                  -- number of the current vibration  

  The following public methods are exported :
      go_backward()           -- go one vibration backward
      go_forward()            -- go one vibration forward
      go_first()              -- go to the first vibration
      go_last()               -- go to the last vibration
      increase_scale_factor() -- increase the scale factor
      decrease_scale_factor() -- decrease the scale factor
      
  """

  def __init__(self, master, **kw) :
    """Constructor of the class.
    
    The size of the toolbar is hardcoded to be 1000x105.

    Positional arguments :
    master -- parent widget

    Keyword arguments :
    freqs           -- wavenumbers of the vibrations (one-based ndarray)
                       shape : (1 + NFreq, ) with NFreq being the number of
                       vibrations
    render_callback -- called if a vibration is to rendered (default None)
                       the callable does not require any arguments.
                       
    """
    Pmw.ScrolledFrame.__init__(self, master,
                               usehullsize=True,
                               hull_width=1000,
                               hull_height=105,
                               horizflex='expand',
                               vertflex='expand',
                               hscrollmode='static')
    BaseWidget.__init__(self, **kw)

  def _init_vars(self) :
    """Initialize variables."""
    if self._smartdict['freqs'] is not None :
      self.__NFreq = len(self._smartdict['freqs']) - 1
      
    else :
      self.__NFreq = -1

    if self._smartdict['render_callback'] is not None \
       and not callable(self._smartdict['render_callback']) :
      raise InvalidArgumentError('Invalid render_callback supplied')
        

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    ## create a group with the title "Vibrational toolbar"
    group = Pmw.Group(self.interior(), tag_text='Vibrational toolbar')
    group.pack(padx=3, pady=3)

    column = 0
    ## vibrational rendering mode
    width = max(len(resources.STRINGS_MODE_VIB_REPRESENTATION[0]),
                len(resources.STRINGS_MODE_VIB_REPRESENTATION[1]),
                len(resources.STRINGS_MODE_VIB_REPRESENTATION[2]))
    
    self._varsdict['options_mode'] = Pmw.OptionMenu(
      group.interior(),
      labelpos='w',
      label_text='Mode : ',
      items=resources.STRINGS_MODE_VIB_REPRESENTATION,
      menubutton_width=width,
      command=self.__change_mode)
    
    self._varsdict['options_mode'].grid(row=0, column=column,
                                        padx=3, pady=0, sticky='w')
    column += 1

    ## frame with vibrations navigation
    self._varsdict['vibframe'] = VibNavigationFrame(
      group.interior(),
      self._smartdict['freqs'],
      changed_callback=self.__changed_vibrations)
    self._varsdict['vibframe'].grid(row=0, column=column,
                                    padx=3, pady=3, sticky='w')
    column += 1    

    ## frame with selection of the displacement types
    frame_select = Tkinter.Frame(group.interior(),
                                 borderwidth=2, relief='sunken',
                                 padx=3, pady=3)
    frame_select.grid(row=0, column=column, padx=3, pady=3)
    column += 1

    # Energy or excursions choice
    widget = Pmw.OptionMenu(frame_select,
                            menubutton_width=20,            
                            command=self.__change_rep_type)
    self._varsdict['options_respresentation'] = widget
    self._varsdict['options_respresentation'].grid(row=0, column=1,
                                                   padx=3, pady=0, sticky='ew')
    # radio buttons
    widget = Pmw.RadioSelect(frame_select,
                             buttontype='radiobutton',
                             orient='horizontal',
                             command=self.__change_rep_type)
    self._varsdict['radio_select'] = widget
    self._varsdict['radio_select'].add(resources.STRING_VIB_ENERGY)
    self._varsdict['radio_select'].add(resources.STRING_VIB_EXCURSIONS)
    self._varsdict['radio_select'].grid(row=0, column=0, padx=3, pady=0)

    ## frame with the scale factor and show button
    frame_show = Tkinter.Frame(group.interior(), borderwidth=2,
                               relief='sunken', padx=3, pady=3)
    frame_show.grid(row=0, column=column, padx=3, pady=3)
    column += 1

    # entry field scale factor with a validator :)
    validate = dict(validator='real',
                    min=0.,
                    max=10.,
                    separator='.')
    widget = Pmw.Counter(frame_show,
                         labelpos='w',
                         label_text='Scale factor:',
                         label_justify='left',
                         entry_width=4,
                         entryfield_value='1.0',
                         entryfield_modifiedcommand=\
                         self._smartdict['render_callback'],
                         datatype=dict(counter='real', separator='.'),
                         entryfield_validate=validate,
                         autorepeat=False,
                         increment = 0.1)
    self._varsdict['counter_scale_factor'] = widget
    self._varsdict['counter_scale_factor'].pack(side='left', padx=5, pady=3)

    # invert phase checkbox (off by default)
    self._varsdict['var_invert_phase'] = Tkinter.IntVar()
    self._varsdict['var_invert_phase'].set(0)
    
    widget = Tkinter.Checkbutton(frame_show,
                                 text='Invert phase',
                                 variable=self._varsdict['var_invert_phase'],
                                 command=self.__invert_phase)
    self._varsdict['check_invert'] = widget
    self._varsdict['check_invert'].pack(side='left', padx=3, pady=3)

    # disabling the controlls if the frequencies were not given
    self.__enable_controls(-1 != self.__NFreq)

  def _declare_properties(self) :
    """Declare properties of the widget."""
    # Mode : spheres, arrows, animation or structure.
    self.__class__.mode = property(fget=self._get_mode)

    # Vibration number from 1 to N (writable).
    self.__class__.vib_no = property(fget=self._get_vib_no,
                                     fset=self._set_vib_no)
    # Radius scale factor.
    self.__class__.scale_factor = property(fget=self._get_scale_factor)

    # Volume or surface excursions
    self.__class__.rep_type = property(fget=self._get_rep_type)

    # Subtype according to value of rep_type
    self.__class__.rep_subtype = property(fget=self._get_rep_subtype)

    # Invert phase
    self.__class__.invert_phase = property(fget=self._get_invert_phase)

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    self._balloon.bind(self._varsdict['options_mode'],
                       'Rendering mode of vibrational motion.')
    self._balloon.bind(self._varsdict['options_respresentation'],
                  'Options appropriate for the current representation type.')
    self._balloon.bind(self._varsdict['radio_select'],
                  'Choose between vibrational energy and ' + \
                       'surface excursions representations.')
    self._balloon.bind(self._varsdict['counter_scale_factor'],
                        'Set the scale factor for the diameter of spheres.')
    self._balloon.bind(self._varsdict['check_invert'],
                        'Invert the phase of a vibration.')

  def __enable_controls(self, enable_=True) :
    """Enable/disable the controls."""
    if enable_ :
      state = 'normal'
    else :
      state = 'disabled'

    # vib frame
    self._varsdict['vibframe'].enable_controls(enable_)

    # the rest controls
    for control in (self._varsdict['radio_select'].button(0),
                    self._varsdict['radio_select'].button(1)) :
      control.configure(state=state)

    for option_control in (self._varsdict['options_mode'],
                           self._varsdict['options_respresentation']) :
      option_control.configure(menubutton_state=state)

    self._varsdict['counter_scale_factor'].configure(entry_state=state)
    self._varsdict['check_invert'].configure(state=state)

  def __change_mode(self, tag) :
    """Change the vibrational representation mode."""
    # if changed to the animation -> set Lx / standard & block it
    state = 'normal'
    if resources.STRING_MODE_VIB_REPRESENTATION_ANIMATION ==  self.mode :
      state = 'disabled'
      self._varsdict['radio_select'].setvalue(resources.STRING_VIB_EXCURSIONS)
      self._varsdict['options_respresentation'].setvalue(
        resources.STRING_VIB_EXCURSIONS_DIAMETER_STANDARD)

    self._varsdict['radio_select'].button(0).configure(state=state)
    self._varsdict['radio_select'].button(1).configure(state=state)
    self._varsdict['options_respresentation'].configure(menubutton_state=state)

    if callable(self._smartdict['render_callback']) :
      self._smartdict['render_callback']()

  def __changed_vibrations(self, p) :
    """VibNavigation frame changed callback."""
    if callable(self._smartdict['render_callback']) :
      self._smartdict['render_callback']()      

  def __change_rep_type(self, tag) :
    """Changes the representation option menu."""
    cur_sel = self._varsdict['radio_select'].getvalue()

    if resources.STRING_VIB_ENERGY == cur_sel :
      self._varsdict['options_respresentation'].setitems(
        resources.STRINGS_ENERGY_VOLUME_REPRESENTATIONS)
    else :
      self._varsdict['options_respresentation'].setitems(
        resources.STRINGS_EXCURSIONS_DIAMETER_REPRESENTATIONS)

    if callable(self._smartdict['render_callback']) :
      self._smartdict['render_callback']()

  def __invert_phase(self) :
    """Invert the phase."""
    if callable(self._smartdict['render_callback']) :
      self._smartdict['render_callback']()

  def _set_vib_no(obj, vib_no) :
    """Setter function for the vib_no property."""
    obj._varsdict['vibframe'].vib_no = vib_no

  _set_vib_no = staticmethod(_set_vib_no)

  def _get_vib_no(obj) :
    """Getter function for the vib_no property."""
    return obj._varsdict['vibframe'].vib_no

  _get_vib_no = staticmethod(_get_vib_no)

  def _get_mode(obj) :
    """Getter function for the mode property."""
    return obj._varsdict['options_mode'].getvalue()

  _get_mode = staticmethod(_get_mode)

  def _get_scale_factor(obj) :
    """Getter function for the scale_factor property.
    
    Return 0 if failed to convert the user input to the float value.
    
    """
    try :
      scale_factor = float(obj._varsdict['counter_scale_factor'].get())
    except :
      scale_factor = 0.

    return scale_factor

  _get_scale_factor = staticmethod(_get_scale_factor)

  def _get_rep_type(obj) :
    """Getter function for the rep_type property."""
    return obj._varsdict['radio_select'].getvalue()

  _get_rep_type = staticmethod(_get_rep_type)

  def _get_rep_subtype(obj) :
    """Getter function for the rep_subtype property."""
    return obj._varsdict['options_respresentation'].getvalue()

  _get_rep_subtype = staticmethod(_get_rep_subtype)

  def _get_invert_phase(obj) :
    """Getter function for the invert_phase property."""
    return obj._varsdict['var_invert_phase'].get()

  _get_invert_phase = staticmethod(_get_invert_phase)

  def go_backward(self, *dummy) :
    """Go one vibration back."""
    self.vib_no = self.vib_no - 1
  
  def go_forward(self, *dummy) :
    """Go one vibration forward."""
    self.vib_no = self.vib_no + 1
      
  def go_first(self) :
    """Go to the first vibration."""
    self.vib_no = 1
    
  def go_last(self) :
    """Go to the last vibration."""
    self.vib_no = self.__NFreq

  def increase_scale_factor(self, *dummy) :
    """Increase the scale factor."""
    self._varsdict['counter_scale_factor'].increment()

  def decrease_scale_factor(self, *dummy) :
    """Decrease the scale factor."""
    self._varsdict['counter_scale_factor'].decrement()
    

class VibrationalToolbarLight(BaseWidget, Tkinter.Frame) :
  """Like VibrationalToolbar but for exploring single vibration.

  Supports also marking of vibrational motion on a fragment.

  The following readable and writable properties are exposed :
      vib_no                  -- number of the vibration  
      rep_type                -- cartesian or mass-weighted excursions
      rep_subtype             -- representation subtype
      invert_phase            -- whether the phase is to be inverted
      sync_toolbar            -- VibrationalToolbarLight to synchronize with

  The following properties are exposed uf fragment_controls=True was supplied
  in the constructor of the class :
      mark_fragment           -- fragment to be marked
      show_marked_only        -- show vibrational motion only on the fragment

  The following public methods are exported :
      increase_scale_factor() -- increase the scale factor
      decrease_scale_factor() -- decrease the scale factor      

  """

  def __init__(self, master, **kw) :
    """Constructor of the class.

    Positional arguments :
    master -- parent widget

    Keyword arguments :
    rep_type            -- cartesian or mass-weighted excursions
                           one of (resources.STRING_VIB_ENERGY,
                           STRING_VIB_EXCURSIONS)
                           (no default)
    rep_subtype         -- representation subtype
                           one of (STRING_VIB_ENERGY_VOLUME,
                           STRING_VIB_ENERGY_VOLUME_ZERO_POINT,
                           STRING_VIB_EXCURSIONS_DIAMETER,
                           STRING_VIB_EXCURSIONS_DIAMETER_ZEROPOINT,
                           STRING_VIB_EXCURSIONS_DIAMETER_STANDARD)
                           (no default)
    scale_factor        -- multiply factor for the amplitude of
                           vibrational motion
                           (no default)
    invert_phase        -- whether the phase of the vibration is to be inverted
                           (no default)
    fragment_controls   -- whether to create the controls for marking fragment
                           (default True)
    mark_fragment       -- whether to mark vibrational motion of a fragment
                           (default False)
    show_marked_only    -- whether to show vibrational motion on a fragment only
                           (default False)
    show_gcm            -- whether to show the Raman/ROA generation button
                           (default False)
    sync_toolbar        -- VibrationalToolbarLight to synchronize with
                           (default None)
    invert_roa          -- whether to invert the sign of ROA (default False)
  
    """
    Tkinter.Frame.__init__(self, master, relief='raised', borderwidth=2)
    BaseWidget.__init__(self, **kw)

  def _init_vars(self) :
    """Initialize variables."""
    # default keywords values
    self._smartdict['invert_phase']     = False
    self._smartdict['scale_factor']     = 1.0

    # show the fragment GUI controls by default
    self._smartdict['fragment_controls'] = True

    # fragment gui keywords
    #self._smartdict['mark_fragment']    = True
    self._smartdict['mark_fragment']    = False
    self._smartdict['show_marked_only'] = False

    # show_acp
    self._smartdict['show_gcm'] = False
 
    # validating
    if self._smartdict['rep_type'] is not None and self._smartdict['rep_type']\
       not in resources.STRINGS_VIB_REPRESENTATIONS :
      raise ConstructorError(
        'Invalid representation type : %s' % self._smartdict['rep_type'])

    if self._smartdict['rep_subtype'] is not None and \
       self._smartdict['rep_subtype'] not in \
       resources.STRINGS_VIB_REPRESENTATIONS_ALL :
      raise ConstructorError(
        'Invalid representation subtype : %s' % self._smartdict['rep_subtype'])
    
    if not isinstance(self._smartdict['scale_factor'], float) and \
       self._smartdict['scale_factor'] < 0. :
      raise ConstructorError(
        'Invalid scale factor : %s' % self._smartdict['scale_factor'])

    if not isinstance(self._smartdict['invert_phase'], int) :
      raise ConstructorError(
        'Invalid value of invert_phase : %s' % self._smartdict['invert_phase'])

    # if the synchronized toolbar is given it must be
    # instance of the same class
    if self._smartdict['sync_toolbar'] is not None and not \
       isinstance(self._smartdict['sync_toolbar'], VibrationalToolbarLight) :
      raise ConstructorError('Invalid sync_toolbar argument')

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    # saving variables for the controls
    self._varsdict['var_invert_phase'] = Tkinter.IntVar()
    self._varsdict['var_scale_factor'] = Tkinter.StringVar()

    self._varsdict['var_invert_phase'].set(self._smartdict['invert_phase'])
    self._varsdict['var_scale_factor'].set(self._smartdict['scale_factor'])

    # these depend on if one wants to see the fragment GUI controls
    if self._smartdict['fragment_controls'] :
      self._varsdict['var_mark_fragment']    = Tkinter.IntVar()
      self._varsdict['var_show_marked_only'] = Tkinter.IntVar()
    
      self._varsdict['var_mark_fragment'].set(self._smartdict['mark_fragment'])
      self._varsdict['var_show_marked_only'].set(
        self._smartdict['show_marked_only'])

    #
    self.grid_rowconfigure(0, weight=1)
    self.grid_rowconfigure(1, weight=1)
    self.grid_columnconfigure(0, weight=1)
    
    ## frame with selection of the displacement types
    frm_select = Tkinter.Frame(self, borderwidth=2, relief='sunken',
                               padx=3, pady=3)
    frm_select.grid(row=0, column=0, padx=3, pady=3, sticky='we')

    frm_select.grid_rowconfigure(0, weight=1)
    frm_select.grid_columnconfigure(0, weight=1)
    frm_select.grid_columnconfigure(1, weight=1)

    # Energy or excursions choice
    widget = Pmw.RadioSelect(frm_select,
                             buttontype='radiobutton',
                             orient='horizontal',
                             command=self.__change_rep_type)
    self._varsdict['radio_select'] = widget
    self._varsdict['radio_select'].add(resources.STRING_VIB_ENERGY)
    self._varsdict['radio_select'].add(resources.STRING_VIB_EXCURSIONS)

    self._varsdict['radio_select'].grid(row=0, column=0,
                                        padx=3, pady=0, sticky='w')

    # options for the chosen type
    widget = Pmw.OptionMenu(frm_select,
                            menubutton_width=20,
                            command=self.__change_rep_subtype)
    self._varsdict['options_respresentation'] = widget
    self._varsdict['options_respresentation'].grid(row=0, column=1,
                                                   padx=3, pady=0, sticky='w')

    # installing the smaller fonts for monitors narrow or equal than 1024
    if 1024 >= self.winfo_screenwidth() :
      font = tkFont.Font(
        self, font=self._varsdict['radio_select'].button(0).cget('font'))
      font.configure(size=int(font.cget('size')) - 1)
      
      self._varsdict['radio_select'].button(0).configure(font=font)
      self._varsdict['radio_select'].button(1).configure(font=font)
      self._varsdict['options_respresentation'].configure(menubutton_font=font)
      self._varsdict['options_respresentation'].configure(menu_font=font)

    ## second line of the toolbar
    # scale factor & invert button
    frm_show = Tkinter.Frame(self, borderwidth=2, relief='sunken',
                             padx=3, pady=3)
    frm_show.grid(row=1, column=0, padx=3, pady=3, sticky='we')

    frm_show.grid_rowconfigure(0, weight=1)
    frm_show.grid_columnconfigure(0, weight=1)
    
    column = 0
    validate = dict(validator='real',
                    min=0.0,
                    max=66.0,
                    separator='.')
    widget = Pmw.Counter(frm_show,
                         entry_width=3,
                         entryfield_value='1.0',
                         entry_textvariable=self._varsdict['var_scale_factor'],
                         entryfield_modifiedcommand=self.__render,
                         datatype=dict(counter='real', separator='.'),
                         entryfield_validate=validate,
                         autorepeat=False,
                         increment = 0.1)
    self._varsdict['counter_scale_factor'] = widget
    self._varsdict['counter_scale_factor'].grid(row=0, column=column,
                                                padx=3, pady=3, sticky='w')
    column += 1
    # show the structure
    widget = Pmw.RadioSelect(frm_show,
                             selectmode='multiple',
                             command=misc.Command(self.__render))
    self._varsdict['radio_structure'] = widget
    self._varsdict['radio_structure'].grid(row=0, column=column,
                                           padx=3, pady=3, sticky='e')
    column += 1

    self._varsdict['radio_structure'].add('structure',
                                          image=getimage('structure'))
    # optional gcm button
    # add if a reference to the main application is given and
    # the Raman/ROA data are available
    if self._smartdict['show_gcm'] and \
       self._smartdict['mainApp'] is not None and \
       self.__are_raman_roa_available() :
      self._varsdict['btn_show_gcm'] = Tkinter.Button(frm_show,
                                                      image=getimage('gcm'),
                                                      relief='flat',
                                                      overrelief='raised',
                                                      command=self.__show_gcm)
      self._varsdict['btn_show_gcm'].grid(row=0, column=column,
                                          padx=3, pady=3, sticky='e')
      column += 1

    # invert the phase of a vibration
    self._varsdict['check_invert'] = Tkinter.Checkbutton(
      frm_show,
      text='Invert phase',
      variable=self._varsdict['var_invert_phase'],
      command=self.__render)
    self._varsdict['check_invert'].grid(row=0, column=column,
                                        padx=3, pady=3, sticky='e')
    column += 1
    # optional fragment controls
    if self._smartdict['fragment_controls'] :
      self._varsdict['check_mark_fragment'] = Tkinter.Checkbutton(
        frm_show,
        text='Mark fragment',
        variable=self._varsdict['var_mark_fragment'],
        command=self.__change_mark_fragment)
      self._varsdict['check_mark_fragment'].grid(row=0, column=column,
                                                 padx=3, pady=3, sticky='e')
      column += 1
      
      self._varsdict['check_show_marked_only'] = Tkinter.Checkbutton(
        frm_show,
        text='Fragment only',
        variable=self._varsdict['var_show_marked_only'],
        command=self.__change_show_marked_only)
      self._varsdict['check_show_marked_only'].grid(row=0, column=column,
                                                    padx=3, pady=3, sticky='e')
      column += 1
    
    ## setting the initial values if given
    if self._smartdict['rep_type'] is not None :
      #
      self._varsdict['radio_select'].setvalue(self._smartdict['rep_type'])
      
      if resources.STRING_VIB_ENERGY == self._smartdict['rep_type'] :
        self._varsdict['options_respresentation'].setitems(
          resources.STRINGS_ENERGY_VOLUME_REPRESENTATIONS)        
      else :
        self._varsdict['options_respresentation'].setitems(
          resources.STRINGS_EXCURSIONS_DIAMETER_REPRESENTATIONS)

    if self._smartdict['rep_subtype'] is not None :    
      self._varsdict['options_respresentation'].setvalue(
        self._smartdict['rep_subtype'])

    self.__render()

  def _declare_properties(self) :
    """Declare properties of the widget."""
    self.__class__.rep_type = property(fget=self._get_rep_type,
                                       fset=self._set_rep_type)
    self.__class__.rep_subtype = property(fget=self._get_rep_subtype,
                                          fset=self._set_rep_subtype)

    self.__class__.invert_phase = property(fget=self._get_invert_phase,
                                           fset=self._set_invert_phase)
    self.__class__.sync_toolbar = property(fget=self._get_sync_toolbar,
                                           fset=self._set_sync_toolbar)
    self.__class__.vib_no = property(fget=self._get_vib_no,
                                     fset=self._set_vib_no)
    
    # these depend on whether one wants to see the fragment GUI controls
    if self._smartdict['fragment_controls'] :
      self.__class__.mark_fragment = property(fget=self._get_mark_fragment,
                                              fset=self._set_mark_fragment)
      self.__class__.show_marked_only = property(
        fget=self._get_show_marked_only,
        fset=self._set_show_marked_only)

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    self._balloon.bind(self._varsdict['options_respresentation'],
      'Options appropriate for the current representation type.')
    self._balloon.bind(self._varsdict['radio_select'],
      'Choose between differenct representations.')
    self._balloon.bind(self._varsdict['counter_scale_factor'],
      'Set the scale factor for the diameter of spheres.')

    self._balloon.bind(self._varsdict['check_invert'],
      'Invert the phase of a vibration.')
    
    # these controls can be absent 
    if self._smartdict['fragment_controls'] :
      self._balloon.bind(self._varsdict['check_mark_fragment'],
        'Mark the fragment being analized with partially transparent spheres.')
      self._balloon.bind(self._varsdict['check_show_marked_only'],
        'Show vibrational motion on the fragment being analized only.')

    if 'btn_show_gcm' in self._varsdict :
      self._balloon.bind(self._varsdict['btn_show_gcm'], 'ACP / GCM.')

    self._balloon.bind(self._varsdict['radio_structure'],
                       'Show only the structure of the molecule.')

  def __are_raman_roa_available(self) :
    """Whethe the Raman/ROA data are available."""
    if self._smartdict['widget'] is None :
      return False

    if self._smartdict['widget'].molecule is None :
      return False

    return self._smartdict['widget'].molecule.raman_roa_tensors is not None
      
  def __change_rep_type(self, tag) :
    """Changes the representation type in the option menu."""
    cur_sel = self._varsdict['radio_select'].getvalue()
    self._set_rep_type(self, cur_sel)

    # synchronized toolbar
    if self._smartdict['sync_toolbar'] :
      self._smartdict['sync_toolbar'].rep_type = cur_sel

  def __change_rep_subtype(self, tag) :
    """Changes the representation subtype."""
    cur_sel = self._varsdict['options_respresentation'].getvalue()
    self._set_rep_subtype(self, cur_sel)

    # synchronized toolbar
    if self._smartdict['sync_toolbar'] :
      self._smartdict['sync_toolbar'].rep_subtype = cur_sel

  def __change_mark_fragment(self) :
    """Changes the state of the mark fragment checkbox."""
    mark_fragment = self._varsdict['var_mark_fragment'].get()
    self._set_mark_fragment(self, mark_fragment)

    # synchronized toolbar
    if self._smartdict['sync_toolbar'] :
      self._smartdict['sync_toolbar'].mark_fragment = mark_fragment

  def __change_show_marked_only(self) :
    """Changes the show marked only checkbox."""
    show_marked_only = self._varsdict['var_show_marked_only'].get()
    self._set_show_marked_only(self, show_marked_only)

    # synchronized toolbar
    if self._smartdict['sync_toolbar'] :
      self._smartdict['sync_toolbar'].show_marked_only = show_marked_only

  def __render(self, *dummy, **dummy_kw) :
    """Called if the user changes the settings."""
    if self._smartdict['widget'] is None :
      return

    self.tk.call('update', 'idletasks')

    # render a vibration if the structure button is released
    if 1 == len(self._varsdict['radio_structure'].getvalue()) :
      self._smartdict['widget'].render_molecule(
        molecule_mode=resources.NUM_MODE_BALLSTICK,
        bonds_mode=resources.NUM_MODE_BONDS_ATOMS_COLOR,
        hydrogen_bond=True)
      self._smartdict['widget'].Render()      
    else :
      # packing vars
      kw = {}
      kw['mode']         = resources.STRING_MODE_VIB_REPRESENTATION_SPHERES
      kw['vib_no']       = self._smartdict['vib_no']
      kw['rep_type']     = self._varsdict['radio_select'].getvalue()
      kw['rep_subtype']  = self._varsdict['options_respresentation'].getvalue()
      kw['scale_factor'] = misc.str_to_float(
        self._varsdict['var_scale_factor'].get(), 0.)
      kw['invert_phase'] = self._varsdict['var_invert_phase'].get()

      if self._smartdict['fragment_controls'] :
        kw['mark_fragment']     = self._varsdict['var_mark_fragment'].get()
        kw['show_marked_only']  = self._varsdict['var_show_marked_only'].get()
      else :
        kw['mark_fragment']    = False
        kw['show_marked_only'] = False
        
      # calling
      self._smartdict['widget'].render_vibration(**kw)

  def __show_gcm(self) :
    """Show the Raman/ROA generation interface for the current vibration."""
    from pyviblib.gui.windows import RamanROAMatricesWindow

    self.tk.call('update', 'idletasks')

    splash = SplashScreen(self, 'Please wait...')
    
    wnd = RamanROAMatricesWindow(self._smartdict['mainApp'],
                                 self._smartdict['widget'].molecule,
                                 vib_no=self._smartdict['vib_no'],
                                 camera=self._smartdict['widget'].camera,
                                 molinv=self._smartdict['molinv'] or 'a2',
                                 tabname='ACP',
                                 invert_roa=self._smartdict['invert_roa'])
    splash.destroy()

  def _set_vib_no(obj, vib_no) :
    """Setter function for the vib_no property."""
    if obj._smartdict['widget'] is None :
      return
    
    if not vib_no in xrange(1, 1 + obj._smartdict['widget'].molecule.NFreq) :
      raise InvalidArgumentError(
        'Invalid number of vibration %s' % str(vib_no))
    
    obj._smartdict.kw['vib_no'] = vib_no
    obj.__render()

  _set_vib_no = staticmethod(_set_vib_no)

  def _get_vib_no(obj) :
    """Getter function for the vib_no property."""
    return obj._smartdict['vib_no']

  _get_vib_no = staticmethod(_get_vib_no)

  def _set_rep_type(obj, rep_type) :
    """Setter function for the rep_type property."""
    if rep_type not in resources.STRINGS_VIB_REPRESENTATIONS :
      raise InvalidArgumentError(
        'Invalid representation type : %s' % rep_type)

    # set value without invoking of the command !
    obj._varsdict['radio_select'].setvalue(rep_type)

    if resources.STRING_VIB_ENERGY == rep_type :
      obj._varsdict['options_respresentation'].setitems(
        resources.STRINGS_ENERGY_VOLUME_REPRESENTATIONS)
    else :
      obj._varsdict['options_respresentation'].setitems(
        resources.STRINGS_EXCURSIONS_DIAMETER_REPRESENTATIONS)

    obj.__render()

  _set_rep_type = staticmethod(_set_rep_type)

  def _get_rep_type(obj) :
    """Getter function for the rep_type property."""
    return obj._varsdict['radio_select'].getvalue()

  _get_rep_type = staticmethod(_get_rep_type)

  def _set_rep_subtype(obj, rep_subtype) :
    """Setter function for the rep_subtype property."""
    if rep_subtype not in resources.STRINGS_ENERGY_VOLUME_REPRESENTATIONS and\
       rep_subtype not in \
       resources.STRINGS_EXCURSIONS_DIAMETER_REPRESENTATIONS :
      raise InvalidArgumentError(
        'Invalid representation subtype : %s' % rep_subtype)

    # set value without invoking of the command !
    obj._varsdict['options_respresentation'].setvalue(rep_subtype)    
    obj.__render()

  _set_rep_subtype = staticmethod(_set_rep_subtype)

  def _get_rep_subtype(obj) :
    """Getter function for the rep_subtype property."""
    return obj._varsdict['options_respresentation'].getvalue()

  _get_rep_subtype = staticmethod(_get_rep_subtype)

  def _set_mark_fragment(obj, mark_fragment) :
    """Setter function for the mark_fragment property.

    Raise an exception if the control was not created.
    
    """
    if not obj._smartdict['fragment_controls'] :
      raise RuntimeError(
        'fragment_controls is set to False, cannot call the function')
      
    # set value without invoking of the command !
    if mark_fragment :
      obj._varsdict['check_mark_fragment'].select()      
    else:
      obj._varsdict['check_mark_fragment'].deselect()

    obj.__render()

  _set_mark_fragment = staticmethod(_set_mark_fragment)

  def _get_mark_fragment(obj) :
    """Getter function for the mark_fragment property."""
    return obj._varsdict['var_mark_fragment'].get()

  _get_mark_fragment = staticmethod(_get_mark_fragment)

  def _set_sync_toolbar(obj, sync_toolbar) :
    """Setter function for the sync_toolbar property."""
    obj._smartdict['sync_toolbar'] = sync_toolbar

  _set_sync_toolbar = staticmethod(_set_sync_toolbar)

  def _get_sync_toolbar(obj) :
    """Getter function for the sync_toolbar property."""
    return obj._smartdict['sync_toolbar']

  _get_sync_toolbar = staticmethod(_get_sync_toolbar)

  def _set_show_marked_only(obj, show_marked_only) :
    """Setter function for the show_marked_only property."""
    if not obj._smartdict['fragment_controls'] :
      raise RuntimeError(
        'fragment_controls is set to False, cannot call the function')

    if show_marked_only :
      obj._varsdict['check_show_marked_only'].select()      
    else:
      obj._varsdict['check_show_marked_only'].deselect()
    
    obj.__render()

  _set_show_marked_only = staticmethod(_set_show_marked_only)

  def _get_show_marked_only(obj) :
    """Getter function for the show_marked_only property."""
    return obj._varsdict['var_show_marked_only'].get()

  _get_show_marked_only = staticmethod(_get_show_marked_only)

  def _get_invert_phase(obj) :
    """Getter function for the invert_phase property."""
    return obj._varsdict['var_invert_phase'].get()

  _get_invert_phase = staticmethod(_get_invert_phase)

  def _set_invert_phase(obj, invert_phase) :
    """Getter function for the invert_phase property."""
    obj._varsdict['var_invert_phase'].set(invert_phase)
    obj.__render()

  _set_invert_phase = staticmethod(_set_invert_phase)

  def increase_scale_factor(self, *dummy) :
    """Increase the scale factor."""
    self._varsdict['counter_scale_factor'].increment()

  def decrease_scale_factor(self, *dummy) :
    """Decrease the scale factor."""
    self._varsdict['counter_scale_factor'].decrement()

    
class VibNavigationFrame(BaseWidget, Tkinter.Frame) :
  """Frame for navigating through vibrations.

  Component of VibrationalToolbar.

  The following readable and writable property is exposed :
      vib_no            -- number of the current vibration

  The following public method is exported :
      enable_controls() -- enable / disable the controls
  
  """

  def __init__(self, master, freqs, **kw) :
    """Constructor of the class.

    Positional arguments :
    master            -- parent widget
    freqs             -- wavenumbers (one-based ndarray)
                         shape : (1 + NFreq,) with NFreq being the number of
                         vibrations
                         
    Keyword arguments :
    changed_callback  -- callable (default None)
                         accepts one argument being the number of vibration
    
    """
    self.__freqs = freqs    
    Tkinter.Frame.__init__(self, master,
                           borderwidth=2, relief='sunken', padx=3, pady=3)
    BaseWidget.__init__(self, **kw)
    
  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    # variables
    self._varsdict['vib_no'] = Tkinter.StringVar()
    self._varsdict['freq']   = Tkinter.StringVar()
    self._varsdict['NFreq']  = Tkinter.StringVar()

    if self.__freqs is not None and 1 < len(self.__freqs) :
      self.__NFreq  = len(self.__freqs) - 1

      # user can specify a valid start value
      if self._smartdict['vib_no'] is not None and \
         self._smartdict['vib_no'] <= self.__NFreq :
        self.__vib_no = self._smartdict['vib_no']
      else :
        self.__vib_no = 1
        
      self._varsdict['vib_no'].set(self.__vib_no)
      self._varsdict['freq'].set('%.2f' % self.__freqs[self.__vib_no])
      self._varsdict['NFreq'].set(self.__NFreq)
    else :
      self.__NFreq  = -1
      self.__vib_no = -1
      self._varsdict['vib_no'].set('-')
      self._varsdict['freq'].set('----')
      self._varsdict['NFreq'].set('-')
    
    # back button
    column = 0
    self._varsdict['btn_back'] = Tkinter.Button(self,
                                                image=getimage('back'),
                                                command=self.__go_backward)
    self._varsdict['btn_back'].grid(row=0, column=column, padx=3, pady=3)
    column += 1
    
    # vib_no label
    widget = Tkinter.Label(self,
                           textvariable=self._varsdict['vib_no'],
                           relief='ridge',
                           borderwidth=3,
                           width=3)
    self._varsdict['lbl_vib_no'] = widget
    self._varsdict['lbl_vib_no'].grid(row=0, column=column, padx=0, pady=3)
    column += 1
    
    # '/' label
    label_from = Tkinter.Label(self, text='/')
    label_from.grid(row=0, column=column, padx=0, pady=3)
    column += 1

    # total number of frequencies label
    widget = Tkinter.Label(self,
                           textvariable=self._varsdict['NFreq'],
                           relief='ridge',
                           borderwidth=3,
                           width=3)
    self._varsdict['lbl_nfreq'] = widget
    self._varsdict['lbl_nfreq'].grid(row=0, column=column, padx=0, pady=3)
    column += 1

    # forward button
    self._varsdict['btn_forward'] = Tkinter.Button(self,
                                                   image=getimage('forward'),
                                                   command=self.__go_forward)
    self._varsdict['btn_forward'].grid(row=0, column=column, padx=5, pady=3)
    column += 1

    # freq label
    widget = Tkinter.Label(self,
                           textvariable=self._varsdict['freq'],
                           relief='ridge',
                           borderwidth=2,
                           width=8)
    self._varsdict['lbl_freq'] = widget
    self._varsdict['lbl_freq'].grid(row=0, column=column, padx=0, pady=3)
    column += 1
    
    # label for cm**(-1)
    label_cm = Tkinter.Label(self, image=getimage('cm-1'))
    label_cm.grid(row=0, column=column, padx=5, pady=3)
    column += 1

    # select vibration button
    widget = Tkinter.Button(self,
                           image=getimage('freq_list'),
                           command=self.__show_freq_list)
    self._varsdict['btn_freq_list'] = widget
    self._varsdict['btn_freq_list'].grid(row=0, column=column, padx=3, pady=3)
    column += 1

  def _declare_properties(self) :
    """Declare properties of the widget."""
    # Number of the currently selected vibration
    self.__class__.vib_no = property(fget=self.__get_current_vib_no,
                                     fset=self.__set_current_vib_no)
  
  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    self._balloon.bind(self._varsdict['btn_back'],
                        'Go one vibration backward.')
    self._balloon.bind(self._varsdict['lbl_vib_no'],
                        'Number of the current vibration.')
    self._balloon.bind(self._varsdict['lbl_nfreq'],
                        'Total number of vibrations.')
    self._balloon.bind(self._varsdict['btn_forward'],
                        'Go one vibration forward.')
    self._balloon.bind(self._varsdict['lbl_freq'],
                        'Wavenumber of the current vibration.')
    self._balloon.bind(self._varsdict['btn_freq_list'],
                        'Select a vibration from the list.')

  def __show_freq_list(self) :
    """Show the list of frequencies to the user for selection."""    
    list_items = ['%3d%20.2f' % (i, self.__freqs[i]) for i \
                  in xrange(1, 1 + self.__NFreq) ]

    dlg = Pmw.SelectionDialog(self,
                              title='Available vibrations',
                              buttons=\
                              resources.STRINGS_BUTTONS_OK_APPLY_CANCEL,
                              defaultbutton=resources.STRING_BUTTON_APPLY,
                              scrolledlist_labelpos='n',
                              label_text='Select a vibration :',
                              scrolledlist_items=list_items)
    dlg.configure(command=misc.Command(self.__dlg_freq_command, dlg))
    dlg.component('listbox').see(self.__vib_no - 1)
    dlg.component('listbox').selection_set((self.__vib_no - 1, ))    
    dlg.show()

  def __dlg_freq_command(self, btn_name, dlg) :
    """Callback for the frequency selection dialog."""
    sel_indices = dlg.component('listbox').curselection()

    # close the dialog if pressed Ok or Cancel
    if btn_name in resources.STRINGS_BUTTONS_OK_CANCEL or not btn_name :
      dlg.destroy()
      self.tk.call('update')
 
    if btn_name in resources.STRINGS_BUTTONS_OK_APPLY :
      if 1 == len(sel_indices) :
        self.__set_current_vib_no(self, 1 + int(sel_indices[0]))

  def __go_backward(self) :
    """Go one vibration backward."""
    self.vib_no = self.__vib_no - 1
  
  def __go_forward(self) :
    """Go one vibration forward."""
    self.vib_no = self.__vib_no + 1

  def __set_current_vib_no(obj, new_vib_no) :
    """Setter function for the vib_no property."""
    if 0 < new_vib_no and -1 != obj.__NFreq and \
       new_vib_no != obj._varsdict['vib_no'].get() and \
       new_vib_no <= obj.__NFreq :

      obj.__vib_no = new_vib_no
      obj._varsdict['vib_no'].set(new_vib_no)
      obj._varsdict['freq'].set('%.2f' % obj.__freqs[new_vib_no])

      if callable(obj._smartdict['changed_callback']) :
        obj._smartdict['changed_callback'](new_vib_no)

  __set_current_vib_no = staticmethod(__set_current_vib_no)

  def __get_current_vib_no(obj) :
    """Getter function for the vib_no property."""
    return obj.__vib_no

  __get_current_vib_no = staticmethod(__get_current_vib_no)

  def enable_controls(self, enable_) :
    """Enable / disable the controls.

    Positional arguments :
    enable_  -- whether the controls are to be enabled.
    
    """
    if enable_ :
      state = 'normal'
    else :
      state = 'disabled'

    for name in ('btn_back', 'btn_forward', 'btn_freq_list') :
      self._varsdict[name].configure(state=state)
    

class NavigationToolbar(BaseWidget, Tkinter.Frame) :
  """Manipulating camera of MoleculeRenderWidget.

  The following public methods are exported :
      save_camera_state() -- save the camera state to a dictionary
      update_camera()     -- update the camera state
  
  """

  def __init__(self, master, renderWidget, **kw) :
    """Constructor of the class.

    Positional arguments :
    master       -- parent widget
    renderWidget -- render widget to be manipulated

    Keyword arguments :
    orientation  -- orientation for the toolbar
                    0 : horizontal
                    1 : vertical
                    (default 0)
    
    """
    # the only required parameter
    if not isinstance(renderWidget, MoleculeRenderWidget) :
      raise ConstructorError('Invalid render widget')

    self._master          = master
    self.__renderWidget   = renderWidget
    
    Tkinter.Frame.__init__(self, master, borderwidth=2, relief='ridge')
    BaseWidget.__init__(self, **kw)

  def _init_vars(self) :
    """Initialize variables."""
    self._smartdict['molecule_name'] = ''
    self._smartdict['orientation'] = 0

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    self.grid_columnconfigure(0, weight=1)
    self.grid_rowconfigure(0, weight=1)
    self.grid_rowconfigure(1, weight=1)
    
    # projection types
    widget = Pmw.RadioSelect(self,
                             orient='vertical',
                             command=self.__set_projection)
    self._varsdict['radio_projection'] = widget    
    self._varsdict['radio_projection'].grid(row=0, column=0, sticky='n')

    self._varsdict['radio_projection'].add('perspective',
                                           image=getimage('perspective'))
    self._varsdict['radio_projection'].add('parallel',
                                           image=getimage('orthogonal'))

    # set the camera projection type properly
    if self.__renderWidget.perspective_projection :
      self._varsdict['radio_projection'].setvalue('perspective')
    else :
      self._varsdict['radio_projection'].setvalue('parallel')

    ## button toolbar with the camera navigation buttons
    btn_toolbar = ButtonToolbar(self, horizontal=False)
    btn_toolbar.configure(borderwidth=0)
    
    btn_toolbar.grid(row=1, column=0, sticky='n')

    row = 0
    # restore camera state
    btn_toolbar.add_button(imagename='restore',
                           command=self.__restore_camera,
                           helptext='Restore the last saved camera state.')

    # remember camera state
    btn_toolbar.add_button(imagename='set_pos',
                           command=self.__remember_camera_state,
                           helptext='Remember the current camera state.')
    
    # save camera state
    btn_toolbar.add_button(imagename='save_camera',
                           command=self.__save_camera,
                           helptext='Save the camera state to a file.')


    # load camera state
    btn_toolbar.add_button(imagename='load_camera',
                           command=self.__load_camera,
                           helptext='Load the camera state from a file.')

    ## initial camera position
    self.__camera_state = {}

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    self._balloon.bind(self._varsdict['radio_projection'],
                       'Set the perspective or orthogonal projection.')
      
  def __set_projection(self, tag) :
    """Set the perspective or orthogonal projection."""
    renderer = self.__renderWidget.renderer
    if not renderer :
      return
    
    if 'parallel' == tag :
      renderer.GetActiveCamera().ParallelProjectionOn()      
    else :
      renderer.GetActiveCamera().ParallelProjectionOff()

    self.__renderWidget.GetRenderWindow().Render()

  def __restore_camera(self) :
    """Restore to the initial state of the camera."""
    self.update_camera(self.__camera_state)
  
  def __serialize_camera_state(self, filename) :
    """Save the properties of the CURRENT camera to the file."""
    f = open(filename, 'w+')    
    renderer = self.__renderWidget.renderer

    if renderer is not None :
      camera = renderer.GetActiveCamera()  

      # saving properties
      cPickle.dump(camera.GetParallelProjection(), f)
      cPickle.dump(camera.GetParallelScale(), f)
      cPickle.dump(camera.GetFocalPoint(), f)
      cPickle.dump(camera.GetPosition(), f)
      cPickle.dump(camera.GetClippingRange(), f)
      cPickle.dump(camera.GetViewUp(), f)

      f.close()
  
  def _format_tuple_string(name, name_tuple) :
    """Format name and 3-tuple: name_tuple.
    
    Used by saving the camera state to the file.
    
    """
    s = '%20s' % name

    for t in name_tuple :
      s = ''.join((s, '%20.6f' % t))
      
    return ''.join((s, '\n'))

  _format_tuple_string = staticmethod(_format_tuple_string)
  
  def __save_camera(self) :
    """Save the camera to a file."""
    filename = tkFileDialog.SaveAs(
      parent=self._master,
      filetypes=[(resources.STRING_FILETYPE_CAMERAFILE_DESCRIPTION, '*.cam')],
      initialfile='%s.cam' % self.__renderWidget.molecule.name,
      defaultextension='.cam'
      ).show()
    
    if filename :
      self.__serialize_camera_state(filename)

  def __load_camera(self) :
    """Load the camera from a file."""
    filename = tkFileDialog.Open(
      parent=self._master,
      filetypes=[(resources.STRING_FILETYPE_CAMERAFILE_DESCRIPTION, '*.cam')]
      ).show()

    if filename :
      # de-serialize a camera state previosly stored with the cPickle package
      f = open(filename, 'r')
      
      camera_state = {}

      for prop in resources.STRINGS_CAMERA_PROPERTIES :
        camera_state[prop] = cPickle.load(f)

      f.close()
      self.update_camera(camera_state)

  def __remember_camera_state(self) :
    """Remember the camera state."""
    self.save_camera_state()

  def save_camera_state(self, camera_state=None) :
    """Save the camera camera state to a dictionary.

    Keyword arguments :
    camera_state -- the dictionary to save to (default None)
                    if None save to the internal dictionary
    
    """
    renderer = self.__renderWidget.renderer

    if renderer :
      camera = renderer.GetActiveCamera()

      if camera_state is None :
        camera_state = self.__camera_state

      # saving the camera properties
      camera_state['ParallelProjection']  = camera.GetParallelProjection()
      camera_state['ParallelScale']       = camera.GetParallelScale()
      camera_state['FocalPoint']          = camera.GetFocalPoint()
      camera_state['Position']            = camera.GetPosition()
      camera_state['ClippingRange']       = camera.GetClippingRange()
      camera_state['ViewUp']              = camera.GetViewUp()

  def update_camera(self, camera_state) :
    """Update the current camera.
    
    Positional arguments :
    camera_state -- dictionary with the camera state
                    
    """
    if camera_state is None :
      return
    
    renderer = self.__renderWidget.renderer

    if renderer :
      camera = renderer.GetActiveCamera()

      # set new values
      camera.SetParallelScale(camera_state['ParallelScale'])
      camera.SetFocalPoint(camera_state['FocalPoint'])
      camera.SetPosition(camera_state['Position'])
      camera.SetClippingRange(camera_state['ClippingRange'])
      camera.ComputeViewPlaneNormal()
       
      camera.SetViewUp(camera_state['ViewUp'])
      camera.OrthogonalizeViewUp()

      self.__renderWidget.Render()

      # update buttons
      if camera_state['ParallelProjection'] :
        self._varsdict['radio_projection'].invoke('parallel')
      else :
        self._varsdict['radio_projection'].invoke('perspective')


class SplashScreen(BaseWidget, Tkinter.Toplevel) :
  """Splash screen which can be shown during a long operation.

  """

  def __init__(self, master, text, **kw) :
    """Constructor of the class.

    Positional arguments :
    master           -- parent widget
    text             -- text to be shown

    Keyword arguments :
    font             -- font for rendering text
                        (default ('Helvetica', 12, 'bold'))
    overrideredirect -- if True the splash will be ignored be the
                        window manager

    """
    self.__text = text
    
    Tkinter.Toplevel.__init__(self, master)
    BaseWidget.__init__(self, **kw)
    
  def _init_vars(self) :
    """Initialize variables."""
    self._smartdict['font'] = ('Helvetica', 12, 'bold')
    self._smartdict['overrideredirect'] = True

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    self.withdraw()
    self.wm_title('Operation in progress')

    # showing text
    text = Tkinter.Label(self,
                         font=self._smartdict['font'],
                         relief = 'raised',
                         borderwidth = 2,
                         padx=50, pady=50,
                         text=self.__text,
                         image=self._smartdict['image'],
                         compound='left')
    text.pack(side='top', fill = 'both', expand = 1)
    
    self.update_idletasks()

    width  = self.winfo_reqwidth()
    height = self.winfo_reqheight()
    
    x = (self.winfo_screenwidth() - width) / 2 - self.winfo_vrootx()
    y = (self.winfo_screenheight() - height) / 3 - self.winfo_vrooty()
    if x < 0:
      x = 0
    if y < 0:
      y = 0
    geometry = '%dx%d+%d+%d' % (width, height, x, y)

    self.overrideredirect(self._smartdict['overrideredirect'])
    self.geometry(geometry)
    self.update_idletasks()
    self.deiconify()
    self.update()
    

class CorrelationResultsTable(BaseWidget, Pmw.ScrolledText) :
  """Table for representing matrices e.g. overlaps or similarities.

  The widget is based on Pmw.ScrolledText.

  The following read-only properties are exposed :
      csv            -- contents in the CSV format
      data           -- contents as a matrix
      labels         -- labels as a dictionary

  The following public methods are exported :
      update_table() -- update the table
      ij_to_vibno()  -- convert rows and columns to vibration numbers
      vibno_to_ij()  -- convert vibration numbers to rows and columns
      
  """

  def __init__(self, master, matrix,
               freqs_ref, freqs_tr, include_tr_rot, **kw) :
    """Constructor of the class.    

    Positional arguments :
    matrix            --  matrix to show (one-based ndarray)
                          shape : (1 + NFreq_ref, 1 + NFreq_tr)
    freqs_ref         --  wavenumbers of the reference molecule
                          (one-based ndarray)
                          shape : (1 + NFreq_ref, )
    freqs_tr          --  wavenumbers of the trial molecule
                          (one-based ndarray)
                          shape : (1 + NFreq_tr, )
    include_tr_rot    --  whether translations/rotations are in the matrix

    Keyword keywords :
    dblclick_callback --  called when double clicked on an element
                          (default None)
                          if supplied, must accept 2 arguments :
                            ref_no and tr_no
    msgBar            --  message bar (Pmw.MessageBar, default None)
      
    """
    if matrix is None or freqs_ref is None or freqs_tr is None :
      raise ConstructorError('Invalid arguments')
    
    self._matrix         = matrix
    self._freqs_ref      = freqs_ref
    self._freqs_tr       = freqs_tr
    self._include_tr_rot = include_tr_rot
    
    Pmw.ScrolledText.__init__(self,
                              master,
                              columnheader=True,
                              rowheader=True,
                              rowcolumnheader=True,
                              columnheader_height= 2,
                              rowheader_width= 4 + 5,
                              rowcolumnheader_width=3,
                              Header_font= resources.FONT_TABLE_ELEMENT,
                              text_font= resources.FONT_TABLE_ELEMENT,
                              text_wrap='none',)

    BaseWidget.__init__(self, **kw)

  def _init_vars(self) :
    """Initialize variables."""    
    if self._smartdict['dblclick_callback'] is not None and \
       not callable(self._smartdict['dblclick_callback']) :
      raise ConstructorError('dblclick_callback must be a callable')

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    # marking of the matrix elements
    self.tag_configure('marked',
                       background=resources.COLOR_MARKED_TABLE_ELEMENT_BG)

    # unmarking the headers when mouse leaves
    self.tag_bind('matrix_element', '<Leave>', self.__mouse_leave)

    # keep track of the mouse motion on the matrix elements
    self.tag_bind('matrix_element', '<Motion>', self.__mouse_motion)

    # keep track of double clicks on the matrix elements
    self.tag_bind('matrix_element', '<Button-1>',
                  self.__mouse_doubleclick_element)

  def _declare_properties(self) :
    """Declare properties of the widget."""
    self.__class__.csv    = property(fget=self._get_csv)
    self.__class__.data   = property(fget=self._get_data)
    self.__class__.labels = property(fget=self._get_labels)

  def _bind_events(self) :
    """Bind events."""
    bind_mouse_wheel(self.component('text'))

  def __mouse_motion(self, e) :
    """Callback for the mouse motion."""
    pos = self.index('@%d,%d' % (e.x, e.y)).split('.')

    row_index    = int(pos[0])
    column_index = 1 + int(pos[1]) / (5 + self.__current_precision)

    # one has to mark the selected tags
    text_rowheaders    = self.component('rowheader')
    text_columnheaders = self.component('columnheader')

    kw_marked  = dict(foreground='red',
                      font=resources.FONT_TABLE_SEL_HEADER2)
    
    kw_default = dict(foreground=self.cget('text_foreground'),
                      font=self.cget('text_font'))

    # frequecy labels and numbers
    kw_head1      = dict(foreground='blue',
                         font=resources.FONT_TABLE_SEL_HEADER1)
    kw_head2      = dict(foreground='blue',
                         font=resources.FONT_TABLE_SEL_HEADER2)
    kw_head1_def  = dict(foreground=self.cget('text_foreground'),
                         font=resources.FONT_TABLE_HEADER1)
    kw_head2_def  = dict(foreground=self.cget('text_foreground'),
                         font=resources.FONT_TABLE_HEADER2)
    
    # mark only the selected tag
    # column headers
    for i in xrange(1, 1 + self.__last_tr_header) :
      if i == column_index :
        kw1 = kw_head1
        kw2 = kw_head2
      else :
        kw1 = kw_head1_def
        kw2 = kw_head2_def
        
      text_columnheaders.tag_configure('tr_header%d'  % i, **kw1)
      text_columnheaders.tag_configure('tr2_header%d' % i, **kw2)

    # row headers
    for i in xrange(1, 1 + self.__last_ref_header) :
      if i == row_index :
        kw1 = kw_head1
        kw2 = kw_head2
      else :
        kw1 = kw_head1_def
        kw2 = kw_head2_def
        
      text_rowheaders.tag_configure('ref_header%d'  % i, **kw1)
      text_rowheaders.tag_configure('ref2_header%d' % i, **kw2)

    # sending info to the message bar
    ref_index, tr_index = self.__text_indices2vib_indices(
      [ int(str_ind) for str_ind in pos ])
    
    msg = ''
    labels = resources.STRINGS_TRANSLATIONS_ROTATIONS_LABELS
    if ref_index < 0 :
      msg = ''.join((msg, '%s -> ' % labels[-ref_index - 1]))
    else :
      msg = ''.join((
          msg,
          '%d / %6.2f -> ' % (ref_index, self._freqs_ref[ref_index])))

    if tr_index < 0 :
      msg = ''.join((msg, '%s' % labels[-tr_index - 1]))
    else :
      msg = ''.join((msg, '%d / %6.2f' % (tr_index, self._freqs_tr[tr_index])))

    if self._smartdict['msgBar'] :
      self._smartdict['msgBar'].message('help', msg)

  def __mouse_leave(self, e) :
    """Callback for <Leave>."""
    kw_head1_def  = dict(foreground=self.cget('text_foreground'),
                         font=resources.FONT_TABLE_HEADER1)
    kw_head2_def  = dict(foreground=self.cget('text_foreground'),
                         font=resources.FONT_TABLE_HEADER2)
    # column headers
    for i in xrange(1, 1 + self.__last_tr_header) :      
      self.component('columnheader').tag_configure(
        'tr_header%d'  % i, **kw_head1_def)
      self.component('columnheader').tag_configure(
        'tr2_header%d' % i, **kw_head2_def)

    # row headers
    for i in xrange(1, 1 + self.__last_ref_header) :      
      self.component('rowheader').tag_configure(
        'ref_header%d'  % i, **kw_head1_def)
      self.component('rowheader').tag_configure(
        'ref2_header%d' % i, **kw_head2_def)

    if self._smartdict['msgBar'] :
      self._smartdict['msgBar'].message('help', '')
    
  def __mouse_doubleclick_element(self, e) :
    """Callback for a double click on an element of the table."""
    indices = self.index('@%d,%d' % (e.x, e.y)).split('.')
    text_indices = [ int(str_ind) for str_ind in indices ]

    ref_no, tr_no = self.__text_indices2vib_indices(text_indices)

    if callable(self._smartdict['dblclick_callback']) :
      self.interior().tk.call('update', 'idletasks')
      self._smartdict['dblclick_callback'](ref_no, tr_no)

  def __text_indices2vib_indices(self, text_indices) :
    """Converts a text character index to the vibrational index.

    Lines indices are one-based, column indices are null-based.
    
    """     
    columnheader_width = 5 + self.__current_precision

    i = text_indices[0]
    j = 1 + text_indices[1] / columnheader_width
    
    return self.ij_to_vibno(i, j)

  def _get_csv(obj) :
    """Return the contents of the table as in the CSV format."""
    rowheader_width = int(obj.component('rowheader').cget('width'))

    # first two lines - trial frequecies and labels
    indent = ('%%%ds' % rowheader_width) % ''

    text_csv = ''
    colheaders = obj.component('columnheader').get('1.0', 'end').split('\n')
  
    text_csv = ''.join((text_csv, indent, colheaders[0], '\n'))
    text_csv = ''.join((text_csv, indent, colheaders[1], '\n'))
      
    # following line are row data
    rowheaders = obj.component('rowheader').get('1.0', 'end').split('\n')
    elements   = obj.get('1.0', 'end').split('\n')

    for i in xrange(len(elements)) :
      text_csv = ''.join((text_csv, rowheaders[i], elements[i], '\n'))

    return text_csv

  _get_csv = staticmethod(_get_csv)

  def _get_data(obj) :
    """Get the contents of the table as a matrix.

    Usefull to update TwoDCircles.
    
    """    
    data = []
    
    for line in obj.get('1.0', 'end').split('\n') :
      line = line.strip()
      
      if 0 == len(line) :
        continue

      data.append( [ float(val) for val in line.split() ] )
        
    n, m = len(data), len(data[0])

    ans = zeros((1 + n, 1 + m), 'd')
    ans[1:, 1:] = array(data, 'd')
      
    return ans

  _get_data = staticmethod(_get_data)

  def _get_labels(obj) :
    """Return a dictionary with labels.

    All values of the dictionary are one-based lists.
    
    Keys of the dictionary :
    labels1_cols : first column headers
    labels2_cols : second column headers
    labels1_rows : first row headers
    labels2_cols : second row headers
    
    """
    colheaders = obj.component('columnheader').get('1.0', 'end').split('\n')
    rowheaders = obj.component('rowheader').get('1.0', 'end').split('\n')

    # saving in a dictionary
    ans = dict(labels1_cols=[0.],
               labels2_cols=[0.],
               labels1_rows=[0.],
               labels2_rows=[0.])

    # columns
    ans['labels1_cols'].extend(colheaders[0].split())
    ans['labels2_cols'].extend(colheaders[1].split())

    # rows
    for row in rowheaders :
      vals = row.split()
      if 2 == len(vals) :
        ans['labels1_rows'].append(vals[0])
        ans['labels2_rows'].append(vals[1])

    return ans

  _get_labels = staticmethod(_get_labels)

  def update_table(self, ref_from, ref_to, tr_from, tr_to,
                   precision, show_tr_rot, nrot_ref, nrot_tr,
                   mark=False, threshold_marked=0.) :
    """Update the contents of the table.

    Positional arguments :
    ref_from          -- start vibration number of the reference molecule
    ref_to            -- end vibration number of the reference molecule
    tr_from           -- start vibration number of the trial molecule
    tr_to             -- end vibration number of the reference molecule
    precision         -- number of decimal points to show
    show_tr_rot       -- whether translations/rotations are to be shown
    nrot_ref          -- number of rotations in the reference molecule
    nrot_tr           -- number of rotations in the trial molecule

    Keyword arguments :
    mark              -- whether to mark elements exceeding a threshold
                         supplied by the threshold_marked argument
                         (default False)
    threshold_marked  -- threshold for marking elements (default 0.)
    
    """
    matrix = self._matrix
    
    # unblocking
    self.configure(text_state = 'normal', Header_state = 'normal')

    # cleaning
    self.clear()
    self.component('columnheader').delete('1.0', 'end')
    self.component('rowheader').delete('1.0', 'end')

    # column headers
    columnheader_width = 5 + precision

    format_rowheader = '%%%ds\n' % int(self.cget('rowheader_width'))
    format_rowheader_1 = '%5.0f'
    format_rowheader_2 = '%4s\n'
    format_columnheader_1 = '%%%d.0f' % columnheader_width
    format_columnheader_2 = '%%%ds' % columnheader_width
    format_el_f = '%%%d.%df' % (columnheader_width, precision)
    format_el_i = '%%%dd'    % columnheader_width

    # user can show translations / rotations if they were calculated
    if self._include_tr_rot :
      include_tr_rot = show_tr_rot
    else :
      include_tr_rot = False

    labels_tr_rot = resources.STRINGS_TRANSLATIONS_ROTATIONS_LABELS

    ## column headers
    # vibrational frequencies(first line)
    self.__last_tr_header = 0
    
    if include_tr_rot :
      for i in xrange(1, 4 + nrot_tr) :
        self.__last_tr_header += 1

        tag_name = 'tr_header%d' % self.__last_tr_header
        self.component('columnheader').tag_configure(
          tag_name, font=resources.FONT_TABLE_HEADER1)  
        self.component('columnheader').insert('end',
                                              format_columnheader_1 % 0.,
                                              tag_name)
    for i in xrange(tr_from, 1 + tr_to) :
      self.__last_tr_header += 1

      tag_name = 'tr_header%d' % self.__last_tr_header
      self.component('columnheader').tag_configure(
        tag_name, font=resources.FONT_TABLE_HEADER1)      
      self.component('columnheader').insert(
        'end', format_columnheader_1 % self._freqs_tr[i], tag_name)

    self.component('columnheader').insert('end', '\n')
    
    # vibrational labels (second line)
    self.__last_tr_header = 0

    if include_tr_rot :
      for i in xrange(1, 4 + nrot_tr) :
        self.__last_tr_header += 1

        tag_name = 'tr2_header%d' % self.__last_tr_header
        self.component('columnheader').tag_configure(
          tag_name, font=resources.FONT_TABLE_HEADER2)
        self.component('columnheader').insert(
          'end', format_columnheader_2 % labels_tr_rot[i-1], tag_name)

    for i in xrange(tr_from, 1 + tr_to) :
      self.__last_tr_header += 1

      tag_name = 'tr2_header%d' % self.__last_tr_header
      self.component('columnheader').tag_configure(
        tag_name, font=resources.FONT_TABLE_HEADER2)
      self.component('columnheader').insert(
        'end', format_columnheader_2 % str(i), tag_name)
    
    # row headers : freq label
    self.__last_ref_header = 0
    
    if include_tr_rot :
      for i in xrange(1, 4 + nrot_ref) :
        self.__last_ref_header += 1

        # freq
        tag_name = 'ref_header%d' % self.__last_ref_header
        self.component('rowheader').tag_configure(
          tag_name, font=resources.FONT_TABLE_HEADER1)
        self.component('rowheader').insert(
          'end', format_rowheader_1 % 0., tag_name)

        # label
        tag_name = 'ref2_header%d' % self.__last_ref_header
        self.component('rowheader').tag_configure(
          tag_name, font=resources.FONT_TABLE_HEADER2)
        self.component('rowheader').insert(
          'end', format_rowheader_2 % labels_tr_rot[i-1], tag_name)
        
    for i in xrange(ref_from, 1 + ref_to) :
      self.__last_ref_header += 1

      # freq
      tag_name = 'ref_header%d' % self.__last_ref_header
      self.component('rowheader').tag_configure(
        tag_name, font=resources.FONT_TABLE_HEADER1)
      self.component('rowheader').insert(
        'end', format_rowheader_1 % self._freqs_ref[i], tag_name)

      # label
      tag_name = 'ref2_header%d' % self.__last_ref_header
      self.component('rowheader').tag_configure(
        tag_name, font=resources.FONT_TABLE_HEADER2)
      self.component('rowheader').insert(
        'end', format_rowheader_2 % str(i), tag_name)
      
    # data
    range_ref = xrange(ref_from, 1 + ref_to)
    range_tr  = xrange(tr_from, 1 + tr_to)

    threshold = pow(10., -1. * precision)
        
    for i in xrange(1, matrix.shape[0]) :
      # print only valid i !
      if include_tr_rot :
        if i > (3 + nrot_ref) and (i - 3 - nrot_ref) not in range_ref :
          continue
      else :
        if i not in range_ref :
          continue

      print_ij = True
      for j in xrange(1, matrix.shape[1]) :
        el_ij = matrix[i, j]
        if include_tr_rot :
          if i <= 3 + nrot_ref :
            if j <= 3 + nrot_tr :
              print_ij = True
            else :
              print_ij = (j - 3 - nrot_tr) in range_tr
          else :
            if j <= 3 + nrot_tr :
              print_ij = (i - 3 - nrot_ref) in range_ref
            else :
              print_ij = (i - 3 - nrot_ref) in range_ref and \
                         (j - 3 - nrot_tr) in range_tr
        else :
          if i in range_ref and j in range_tr :
            print_ij = True
            if self._include_tr_rot :
              el_ij = matrix[i + 3 + nrot_ref, j + 3 + nrot_tr]
          else :
            print_ij = False
        #
        if print_ij :
          if threshold > el_ij :
            self.insert('end', format_el_i % 0, 'matrix_element')
          else :
            tags = ['matrix_element']
            if mark and threshold_marked <= el_ij :
              tags.append('marked')
              
            self.insert('end', format_el_f % el_ij, tuple(tags))

      self.insert('end', '\n')
          
    # blocking
    self.configure(text_state = 'disabled', Header_state = 'disabled')

    self.__current_precision = precision
    self.__show_tr_rot       = show_tr_rot
    self.__nrot_ref          = nrot_ref
    self.__nrot_tr           = nrot_tr
    self.__vib_ranges        = ref_from, ref_to, tr_from, tr_to

  def ij_to_vibno(self, i, j) :
    """Get the numbers of vibrations.

    Positional arguments :
    i -- row number
    j -- column number

    Return (ref_index, tr_index). Negative indices correspond to
    translations/rotations.
    
    """
    ref_from, ref_to, tr_from, tr_to = self.__vib_ranges

    if self._include_tr_rot and self.__show_tr_rot :
      if i <= 3 + self.__nrot_ref :
        ref_index = -i
      else :
        ref_index = ref_from - 1 + i - (3 + self.__nrot_ref)

      if j <= 3 + self.__nrot_tr :
        tr_index = -j
      else :
        tr_index = tr_from -1 + j - (3 + self.__nrot_tr)
    else :
      ref_index = min(ref_from + i - 1, ref_to)
      tr_index  = min(tr_from  + j - 1, tr_to)

    return ref_index, tr_index

  def vibno_to_ij(self, ref_index, tr_index) :
    """Get the number of the row and column.

    Positional arguments :
    ref_index -- vibration number of the reference molecule
    tr_index  -- vibration number of the trial molecule

    Opposite destination to ij_to_vibno().

    """
    ref_from, ref_to, tr_from, tr_to = self.__vib_ranges

    # reference i (rows)
    if 0 > ref_index :
      i = -ref_index    
    else :
      if self._include_tr_rot and self.__show_tr_rot :
        i = 3 + self.__nrot_ref + ref_index - ref_from + 1
      else :
        i = max(ref_index - ref_from + 1, ref_index - ref_to)

    # trial j (columns)
    if 0 > tr_index :
      j = -tr_index
      
    else :
      if self._include_tr_rot and self.__show_tr_rot :
        j = 3 + self.__nrot_tr + tr_index - tr_from + 1
      else :
        j = max(tr_index - tr_from + 1, tr_index - tr_to)
        
    return i, j


    
def show_exception(exception_info) :
  """Show an exception in a dialog.

  Positional arguments :
  exception_info -- must be the return value of sys.exc_info()
  
  """
  dialog = Pmw.TextDialog(None,
                          scrolledtext_labelpos = 'n',
                          title='Error occured',
                          defaultbutton = 0,
                          text_height=10,
                          text_font=\
                          Pmw.logicalfont('Times', sizeIncr=-1, weight='bold'),
                          text_wrap='char',
                          label_text='Details:')  
  dialog.withdraw()
  dialog.focus_set()

  text = dialog.component('text')
  text.tag_configure('msg_head', foreground='red')

  # exception details are to be shown with the red color  
  text.insert('end', exception_info[1], 'msg_head')

  # traceback - in black
  msg_trace = '\n\nTraceback :\n'
  for exc_line in format_tb(exception_info[2]) :
    msg_trace = ''.join((msg_trace, exc_line))
  
  text.insert('end', msg_trace)
  dialog.configure(text_state = 'disabled')
  
  # center the dialog
  Pmw.setgeometryanddeiconify(dialog, dialog._centreonscreen())

def mouse_wheel(e, widget) :
  """Mouse wheel callback for a widget.

  Positional arguments :
  widget -- widget
  
  Usage :
  >>> from pyviblib.util.misc import Command
  >>> from pyviblib.gui.widgets import mouse_wheel
  >>> widget.bind('<Button-4>', Command(mouse_wheel, widget))
  >>> widget.bind('<Button-5>', Command(mouse_wheel, widget))
  
  """
  # scroll direction : always 1 unit
  if 4 == e.num :
    number = -1
  else :
    number = 1
    
  widget.yview('scroll', number, 'units')

def bind_mouse_wheel(widget) :
  """Bind the mouse wheel events to a widget."""
  widget.bind('<Button-4>', misc.Command(mouse_wheel, widget))
  widget.bind('<Button-5>', misc.Command(mouse_wheel, widget))


class WindowNavigationToolbar(BaseWidget, Tkinter.Frame) :
  """Toolbar for switching between windows.

  Can have a home and back buttons.

  """

  def __init__(self, master, **kw) :
    """Constructor of the class.

    Positional arguments :
    master             -- parent widget
    
    Keyword arguments :
    mainApp            -- reference to the main window of PyVib2
                          (pyviblib.gui.main.Main, default None)
    backbutton         -- whether to create a back button (default False)
    homebutton         -- whether to create a home button (default False)
    backbutton_command -- command for the back button (default None)
    
    """
    Tkinter.Frame.__init__(self, master)
    BaseWidget.__init__(self, **kw)


  def _init_vars(self) :
    """Initialize variables."""
    if self._smartdict['mainApp'] is not None :
      self._smartdict['homebutton_command'] = \
                  self._smartdict['mainApp'].activate

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    current_column = 0

    if self._smartdict['backbutton'] :
      widget = Tkinter.Button(self,
                              image=getimage('goback'),
                              relief='flat',
                              overrelief='raised',
                              command=self._smartdict['backbutton_command'])
      self._varsdict['btn_back'] = widget      
      self._varsdict['btn_back'].grid(row=0, column=current_column,
                                      padx=3, pady=3, sticky='w')
      current_column += 1

    if self._smartdict['homebutton'] :
      widget = Tkinter.Button(self,
                              image=getimage('home'),
                              relief='flat',
                              overrelief='raised',
                              command=self._smartdict['homebutton_command'])
      self._varsdict['btn_home'] = widget
      self._varsdict['btn_home'].grid(row=0, column=current_column,
                                      padx=3, pady=3, sticky='w')

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    if self._smartdict['backbutton'] :
      self._balloon.bind(self._varsdict['btn_back'], 'Go back.')
    
    if self._smartdict['homebutton'] :
      self._balloon.bind(self._varsdict['btn_home'],
                         'Switch to the main window.')
    
        
class InfoWidget(BaseWidget, Tkinter.Frame) :
  """Widget for providing a help text."""

  def __init__(self, master, **kw) :
    """Constructor of the class.

    Positional arguments :
    master -- parent widget

    Keyword arguments :
    text   -- text to be shown (default '')
    height -- number of rows in the widget (default 4)
    icon   -- whether to render the icon to the left of the text (default True)
    
    """
    Tkinter.Frame.__init__(self, master)
    BaseWidget.__init__(self, **kw)

  def _init_vars(self) :
    """Initialize variables."""
    self._smartdict['text']   = ''
    self._smartdict['height'] = 4
    self._smartdict['icon']   = True
    
  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    column = 0
    
    # image
    if self._smartdict['icon'] :
      lbl_image = Tkinter.Label(self, image=getimage('message'))
      lbl_image.grid(row=0, column=column, padx=3, pady=3, sticky='w')
      column += 1

    # scrolled text
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(column, weight=1)

    # setting the background of a readonly text
    bg = Tkinter.Entry(None, state='readonly').cget('readonlybackground')
    
    scrolled_text = Pmw.ScrolledText(self,
                                     text_height=self._smartdict['height'],
                                     text_bg=bg)
    scrolled_text.grid(row=0, column=column, padx=3, pady=3, sticky='we')

    scrolled_text.insert('end', self._smartdict['text'])
    scrolled_text.configure(text_state='disabled')


class TwoDCircles(BaseWidget, Tkinter.Canvas) :
  """Canvas for rendering matrices such as e.g. GCMs, overlaps or similarities.

  The widget is based on Tkinter.Canvas.

  The following public methods are exported :
      update()        -- update the canvas
      mark_rect_ij()  -- mark a rectangle on the canvas

  """

  def __init__(self, master, **kw) :
    """Constructor of the class.

    All arrays supplied in the keyword arguments must be one-based ndarrays.

    Positional arguments :
    master                -- parent widget
    
    Keyword arguments :
    data                  -- matrix with numeric values (default None)
    mode                  -- how to render the matrix
                             one of (resources.NUM_MODE_WHOLE,
                             resources.NUM_MODE_UPPERHALFONLY,
                             resources.NUM_MODE_LOWERHALFONLY
                             (default resources.NUM_MODE_WHOLE)
    sumup_diag            -- whether to sum the elements in the upper- or
                             lowerhalf mode (default False)
    type                  -- whether the square or the diameters of the circles
                             are proportional to the values
                             one of (resources.NUM_TYPE_PROPORTIONAL_TO_SQUARE,
                             resources.NUM_TYPE_PROPORTIONAL_TO_DIAMETER)
                             (default resources.NUM_TYPE_PROPORTIONAL_TO_SQUARE)
    labels_on             -- render the labels (default True)
    labels1_cols          -- first column headers  (default None)
    labels2_cols          -- second column headers (default None)
    labels1_rows          -- first row headers     (default None)
    labels2_cols          -- second row headers    (default None)
    bbox_on               -- whether to render the bounding box around the
                             circles (default False)
    font_labels1          -- font for the headers1
                             (default resources.FONT_TWODCIRCLES_LABEL1)
    font_labels2          -- font for the headers2
                             (default resources.FONT_TWODCIRCLES_LABEL2)
    color_positive        -- filling color for positive values (default 'black')
    color_negative        -- filling color for negative values (default 'white')
    color_rect            -- color of the bounding rectangles (default 'black')
    scale_factor          -- number for the radii of the circles (default 1.0)
    max_circlewidth       -- maximum width of the bounding box of a circle
                             in pixel (default 30)
    indent                -- indent from the upper left corner of the canvas
                             (default 5)
    text_padding          -- padding with a label box (default 15)
    full_circle           -- value of a completely filled circle (default 1.0)
    color_highlight       -- highlighting color for a selected pair
                             (default 'red')
    ndigits               -- show numbers under 10**(-ndigits) in the
                             message bar as 0 (default None)
                             if None, show the number is a scientific notation
    msgBar                -- message bar for messages (default None)
    dblclick_callback     -- called on a double click (default None)
    mouse_motion_callback -- called when the mouse enters the canvas
                             (args : i j) (default None)
    mouse_leave_callback  -- called when the mouse leaves the canvas (no args)    
    
    """
    Tkinter.Canvas.__init__(self, master, background='white')
    BaseWidget.__init__(self, **kw)

    self.update()

  def _init_vars(self) :
    """Initialize variables."""
    self._props = self._smartdict
    
    defaults = dict(data=None,
                    mode=resources.NUM_MODE_WHOLE,
                    sumup_diag=False,
                    type=resources.NUM_TYPE_PROPORTIONAL_TO_SQUARE,
                    labels_on=True,
                    labels1_cols=None,
                    labels2_cols=None,
                    labels1_rows=None,
                    labels2_rows=None,
                    bbox_on=False,
                    font_labels1=resources.FONT_TWODCIRCLES_LABEL1,
                    font_labels2=resources.FONT_TWODCIRCLES_LABEL2,
                    color_positive='black',
                    color_negative='white',
                    color_rect='black',
                    scale_factor=1.0,
                    max_circlewidth=50,
                    indent=15,
                    text_padding=5,
                    full_circle=1.0,
                    color_highlight='blue',
                    dblclick_callback=None,
                    msgBar=None)

    # copy defaults to the smart dictionary
    for key in defaults.keys() :
      self._props[key] = defaults[key]

    # validate
    if self._props['data'] is not None :
      if not isinstance(self._props['data'], ndarray) or \
         2 != len(self._props['data'].shape) :
        raise ConstructorError('Invalid matrix')

    if (self._props['labels1_rows'] is not None and \
        self._props['labels1_cols'] is None ) or \
       (self._props['labels1_rows'] is None and \
        self._props['labels1_cols'] is not None ) :
      raise ConstructorError(
        'labels1 for rows and cols must be given or not given at all')

    if (self._props['labels2_rows'] is not None and \
        self._props['labels2_cols'] is None ) or \
       (self._props['labels2_rows'] is None and \
        self._props['labels2_cols'] is not None ) :
      raise ConstructorError(
        'labels2 for rows and cols must be given or not given at all')

    # controlling dimensions
    if self._props['data'] is None :
      return
    
    n, m = self._props['data'].shape

    if self._props['labels1_rows'] is not None :
      if m != len(self._props['labels1_cols']) or \
         n != len(self._props['labels1_rows']) :
        raise ConstructorError(
          'Labels1 dimensions are incompatible with the matrix')

    if self._props['labels2_rows'] is not None :
      if m != len(self._props['labels2_cols']) or \
         n != len(self._props['labels2_rows']) :
        raise ConstructorError(
          'Labels2 dimensions are incompatible with the matrix')

    # number of digits must be positive
    if self._smartdict['ndigits'] is not None and \
       0 >= self._smartdict['ndigits'] :
      raise ConstructorError('ndigits must be positive')

  def _maxwidth_labels(labels) :
    """Calculate the maximum width of symbols in a given tuple of labels.

    Return 0 if labels are not given.
    
    """
    if labels is None or 0 == len(labels) :
      return 0

    maxwidth = len(str(labels[0]))
    for l in labels[1:] :
      if len(str(l)) > maxwidth :
        maxwidth = len(str(l))

    return maxwidth

  _maxwidth_labels = staticmethod(_maxwidth_labels)

  def _create_string_n(n) :
    """Return a string with a given number of spaces
    """
    if not n or 0 > n :
      return ''

    return ('%%%ds' % n) % ''

  _create_string_n = staticmethod(_create_string_n)

  def __get_text_height(self, font) :
    """Get the height of a text of a given font."""
    if font is None :
      return 0

    metrics = tkFont.Font(self, font=font).metrics()
    return metrics['ascent']

  def __get_text_width(self, text, font) :
    """
    Return the width of a given text with a given font.
    """
    if not text or not font :
      return 0

    return tkFont.Font(self, font=font).measure(text)

  def __mousepos_to_ij(self, x, y) :
    """Return i, j from the mouse position."""
    items = self.find_closest(self.canvasx(x), self.canvasy(y))

    for item in items :
      if item in self.__id_to_ij :
        return self.__id_to_ij[item]    
    else :
      return None

  def __mouse_motion(self, e) :
    """Handler for the mouse move event."""
    if self._props['data'] is None :
      return
    
    ij = self.__mousepos_to_ij(e.x, e.y)
    
    if ij is None :
      return
    
    i, j = ij

    # mouse motion callback
    if callable(self._props['mouse_motion_callback']) :
      self._props['mouse_motion_callback'](i, j)

    # message bar message
    if self._props['msgBar'] :
      message = ''
      
      if self._props['labels1_rows'] is not None :
        message = ''.join((message, '%s / ' % self._props['labels1_rows'][i]))

      if self._props['labels2_rows'] is not None :
        message = ''.join((message, '%s -> ' % self._props['labels2_rows'][i]))

      if self._props['labels1_cols'] is not None :
        message = ''.join((message, '%s / ' % self._props['labels1_cols'][j]))

      if self._props['labels2_cols'] is not None :
        message = ''.join((message, '%s : ' % self._props['labels2_cols'][j]))

      # do not forget about summed diagonals
      # very small values format in scientific notation
      if ((resources.NUM_MODE_UPPERHALFONLY == \
           self._props['mode'] and j > i ) or \
          (resources.NUM_MODE_LOWERHALFONLY == \
           self._props['mode'] and j < i ) ) \
           and self._props['sumup_diag'] :

        val = self._props['data'][i, j] + self._props['data'][j, i]
        
      else :
        val = self._props['data'][i, j]
      
      str_val = ''
      if self._smartdict['ndigits'] is not None :
        if pow(10., -self._smartdict['ndigits']) > abs(val) :
          str_val = '0'
        else :
          str_val = ('%%.%df' % self._smartdict['ndigits']) % val
      else :
        str_val = '%.2e' % val

      message = ''.join((message, 'value = %s' % str_val))
      self._props['msgBar'].message('help', message)

  def __mouse_leave(self, e) :
    """When the mouse leaves the canvas."""
    # cleaning the message bar
    if self._props['msgBar'] :
      self._props['msgBar'].message('help', '')

    # callback
    if callable(self._props['mouse_leave_callback']) :
      self._props['mouse_leave_callback']()

  def __deselect_all(self) :
    """Deselect all labels."""
    if self._props['data'] is None :
      return
    
    # default labels text foreground
    fg_default = 'black'

    # rows
    for i in xrange(1, self._props['data'].shape[0]) :     
      self.itemconfig('row%d' % i, fill=fg_default)

    # columns
    for j in xrange(1, self._props['data'].shape[1]) :
      self.itemconfig('col%d' % j, fill=fg_default)

  def __mouse_doubleclick_element(self, e) :
    """Double clicked on an element."""
    ij = self.__mousepos_to_ij(e.x, e.y)

    if ij is not None :
      # callback : arguments are row & column indices of the given matrix
      # NOT vibration numbers !!!
      if callable(self._props['dblclick_callback']) :
        self.tk.call('update', 'idletasks')
        self._props['dblclick_callback'](*ij)

  def __find_rect_ij(self, ij) :
    """Find the rectangle identifier for given ij.

    Return None unless found.
    
    """
    ids = self.find_withtag('rect%d_%d' % ij)
    
    if 1 == len(ids) :
      return ids[0]
    else :
      return None

  def update(self, **kw) :
    """Update the canvas.

    See the constructor __init__() for the keyword arguments.

    """
    # refresh properties
    self._smartdict.merge()
    self._smartdict.kw = kw
    
    props = self._smartdict
    self._props = self._smartdict

    # do nothing if data not given
    if props['data'] is None :
      return

    # cleaning the canvas and waiting for the operation to be completed
    self.delete(Tkinter.ALL)
    self.tk.call('update')

    # dictionary for mapping between items ids and position in the table
    self.__id_to_ij = {}

    # define the maximum width of the labels
    # the can suppress the labels with labels_on = False
    # even if they are given
    if props['labels_on'] :
      maxwidth_labels1_rows = self._maxwidth_labels(props['labels1_rows'])
      maxwidth_labels2_rows = self._maxwidth_labels(props['labels2_rows'])
      maxwidth_labels1_cols = self._maxwidth_labels(props['labels1_cols'])
      maxwidth_labels2_cols = self._maxwidth_labels(props['labels2_cols'])
      
    else :
      maxwidth_labels1_rows = 0
      maxwidth_labels2_rows = 0
      maxwidth_labels1_cols = 0
      maxwidth_labels2_cols = 0

    # text metrics
    text_labels1_width  = self.__get_text_width(
      self._create_string_n(maxwidth_labels1_rows), props['font_labels1'])
    
    text_labels2_width  = self.__get_text_width(
      self._create_string_n(maxwidth_labels2_rows), props['font_labels2'])
    
    text_labels1_height = self.__get_text_height(props['font_labels1'])
    text_labels2_height = self.__get_text_height(props['font_labels2'])

    # width of the labels
    labels1_box_width   = text_labels1_width  + 2 * props['text_padding']
    labels2_box_width   = text_labels2_width  + 2 * props['text_padding']
    labels1_box_height  = text_labels1_height + 2 * props['text_padding']
    labels2_box_height  = text_labels2_height + 2 * props['text_padding']

    # quadrat face around the circles
    list_sizes = [ props['max_circlewidth'] ]

    if 0 < maxwidth_labels1_rows :
      list_sizes.append(labels1_box_height)
      list_sizes.append(labels1_box_width)

    if 0 < maxwidth_labels2_rows :
      list_sizes.append(labels2_box_height)
      list_sizes.append(labels2_box_width)
      
    a = max(list_sizes)

    ## set the approptiate size of the canvas
    n = props['data'].shape[0] - 1
    m = props['data'].shape[1] - 1
    
    canvas_width  = 2 * props['indent'] + m * a
    canvas_height = 2 * props['indent'] + n * a

    if 0 < maxwidth_labels1_rows :
      canvas_width  += labels1_box_width
      canvas_height += labels1_box_height

    if 0 < maxwidth_labels2_rows :
      canvas_width  += labels2_box_width
      canvas_height += labels2_box_height

    self.configure(width=canvas_width, height=canvas_height)

    ## rendering labels1 and labels2 in rows
    # define start positions
    start_x = props['indent']
    
    start_y = props['indent']
    if 0 < maxwidth_labels1_rows :
      start_y += labels1_box_height

    if 0 < maxwidth_labels2_rows :
      start_y += labels2_box_height

    # starting position for circles - x
    circles_start_x = start_x

    # labels1 rows
    if 0 < maxwidth_labels1_rows :        
      for i in xrange(1, 1 + n) :
        x = start_x + labels1_box_width / 2
        y = start_y + (i - 1) * a + a / 2
        self.create_text(x, y,
                         text=props['labels1_rows'][i],
                         font=props['font_labels1'],
                         anchor='center',
                         tags='row%d' % i)

      start_x         += labels1_box_width
      circles_start_x += labels1_box_width
        
    # labels2 rows
    if 0 < maxwidth_labels2_rows :
      for i in xrange(1, 1 + n) :
        x = start_x + labels2_box_width / 2
        y = start_y + (i - 1) * a + a / 2
        self.create_text(x, y,
                         text=props['labels2_rows'][i],
                         font=props['font_labels2'],
                         anchor='center',
                         tags='row%d' % i)
        
      circles_start_x += labels2_box_width
    
    ## rendering labels1 and labels2 in columns
    start_x = props['indent']
    
    if 0 < maxwidth_labels1_cols :
      start_x += labels1_box_width

    if 0 < maxwidth_labels2_cols :
      start_x += labels2_box_width

    start_y = props['indent']

    # starting position for circles - y
    circles_start_y = start_y

    # labels1 cols
    if 0 < maxwidth_labels1_cols :    
      for i in xrange(1, 1 + m) :
        x = start_x + (i - 1) * a + a / 2
        y = start_y + labels1_box_height / 2
        self.create_text(x, y,
                         text=props['labels1_cols'][i],
                         font=props['font_labels1'],
                         anchor='center',
                         tags='col%d' % i)

      start_y         += labels1_box_height
      circles_start_y += labels1_box_height

    # labels2 cols
    if 0 < maxwidth_labels2_cols :    
      for i in xrange(1, 1 + m) :
        x = start_x + (i - 1) * a + a / 2
        y = start_y + labels2_box_height / 2
        self.create_text(x, y,
                         text=props['labels2_cols'][i],
                         font=props['font_labels2'],
                         anchor='center',
                         tags='col%d' % i)

      circles_start_y += labels2_box_height

    ## rendering the bounding rectangles for the circles
    for i in xrange(1, 1 + n) :
      y = circles_start_y + (i - 1) * a
      
      for j in xrange(1, 1 + m) :
        if ( resources.NUM_MODE_UPPERHALFONLY == props['mode'] and j < i ) or \
           ( resources.NUM_MODE_LOWERHALFONLY == props['mode'] and j > i ) :
          continue          
        #
        x = circles_start_x + (j - 1) * a
        
        tag_rect   = 'rect%d_%d' % (i, j)
        element_id = self.create_rectangle(x,
                                           y,
                                           x + a,
                                           y + a,
                                           tags=('element', tag_rect),
                                           outline=props['color_rect'],
                                           fill='white')        
        self.__id_to_ij[element_id] = (i, j)

    ## rendering a bounding frame around the circles
    ## very usefull if one has only circles !
    if props['bbox_on'] :
      self.create_rectangle(circles_start_x, circles_start_y,
                            circles_start_x + m * a, circles_start_y + n * a)

    ## rendering the circles after the bounding boxes
    ## to prevent the "cutted" view
    for i in xrange(1, 1 + n) :
      y = circles_start_y + (i - 1) * a
      
      for j in xrange(1, 1 + m) :
        if (resources.NUM_MODE_UPPERHALFONLY == props['mode'] and j < i) or \
           (resources.NUM_MODE_LOWERHALFONLY == props['mode'] and j > i) :
          continue

        # variable val is the final value to show
        # sum up elements if demanded (useful for the molecular invariants)
        if ((resources.NUM_MODE_UPPERHALFONLY == props['mode'] and j > i ) or \
             (resources.NUM_MODE_LOWERHALFONLY == props['mode'] and j < i )) \
             and props['sumup_diag'] :
          val = props['data'][i, j] + props['data'][j, i]
        else :
          val = props['data'][i, j]          
        #
        x = circles_start_x + (j - 1) * a
        abs_value = fabs(val)
        
        if val > 0. :
          color = props['color_positive']
        else :
          color = props['color_negative']
        
        if resources.NUM_TYPE_PROPORTIONAL_TO_SQUARE == props['type'] :
          r = float(0.5 * a * sqrt(abs_value/props['full_circle']))          
        else :
          r = float(0.5 * a * (abs_value/props['full_circle']))

        r *= props['scale_factor']

        # do not render null contributions
        if r < 1e-5 :
          continue

        if 0. != r :
          x_left  = x + int(ceil(0.5 * a - r))
          y_left  = y + int(ceil(0.5 * a - r))
          x_right = x + int(float(0.5 * a + r))
          y_right = y + int(float(0.5 * a + r))

          element_id = self.create_oval(x_left, y_left, x_right, y_right,
                                        fill=color,
                                        tags=('element',),
                                        outline=color)
          self.__id_to_ij[element_id] = (i, j)

    # binding    
    self.tag_bind('element', '<Motion>', self.__mouse_motion)
    self.tag_bind('element', '<Leave>', self.__mouse_leave)
    self.tag_bind('element', '<Button-1>', self.__mouse_doubleclick_element)

  def mark_rect_ij(self, ij, mark=True) :
    """Mark/unmark a rectangle.

    Positional arguments :
    ij   -- identifier of the rectangle

    Keyword arguments :
    mark -- whether to mark (default True)
    
    """
    id_ = self.__find_rect_ij(ij)
    
    if id_ is not None :
      if mark :
        self.itemconfig(id_, outline='red', fill='red')
      else :
        self.itemconfig(id_, outline='black', fill='')
        

class CorrelationResultsNoteBook(BaseWidget, Pmw.NoteBook) :
  """Widget for representing results of a correlation of vibrational motions.

  The widget is based on Pmw.NoteBook.

  The following read-only properties are exposed :
      table              -- table with the text, see CorrelationResultsTable
      circles_frame      -- frame with the circles

  The following public methods are exported :
      update_contents()  -- update the contents of the widget
      show_A4()          -- switch to the A4 representation of circles
  
  """

  def __init__(self, master, matrix,
               freqs_ref, freqs_tr, include_tr_rot, **kw) :
    """Constructor of the class.

    Positional arguments :
    matrix            -- matrix (one-based ndarray)
    freqs_ref         -- wavenumbers of the reference molecule
                         (one-based ndarray)
    freqs_tr          -- wavenumbers of the trial molecule
                         (one-based ndarray)
    include_tr_rot    -- whether translations / rotations are present
                         in the table

    Keyword arguments :
    dblclick_callback -- called on a double clicke on an element (default None)
                         function of 2 arguments : ref_no and tr_no
    msgBar            -- message bar (default None)
    
    """
    Pmw.NoteBook.__init__(self,
                          master,
                          raisecommand=None,
                          lowercommand=None,
                          arrownavigation=False)
    # saving data
    self._matrix         = matrix
    self._freqs_ref      = freqs_ref
    self._freqs_tr       = freqs_tr
    self._include_tr_rot = include_tr_rot

    BaseWidget.__init__(self, **kw)

  def _init_vars(self) :
    """Initialize variables."""
    # last visited directory
    self.__lastdir = None

    # construct filetypes
    # add pdf if ps2pdf is found
    self.__save_filetypes = []

    if misc.is_command_on_path('ps2pdf') :
      self.__save_filetypes.append(
        (resources.STRING_FILETYPE_PDFFILE_DESCRIPTION, '*.pdf'))

    self.__save_filetypes.append(
      (resources.STRING_FILETYPE_EPSFILE_DESCRIPTION, '*.ps *.eps'))

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    ## first tab - values
    tabValues = self.add('Values')

    tabValues.grid_rowconfigure(0, weight=1)
    tabValues.grid_columnconfigure(1, weight=1)

    # save csv button
    widget = Tkinter.Button(tabValues,
                            image=getimage('oo_calc'),
                            relief='flat',
                            overrelief='raised',
                            command=self.__export_table)
    self._varsdict['btn_save_values'] = widget
    self._varsdict['btn_save_values'].grid(row=0, column=0,
                                           padx=3, pady=3, sticky='n')
    # table with the values
    widget = CorrelationResultsTable(tabValues,
                                     matrix=self._matrix,
                                     freqs_ref=self._freqs_ref,
                                     freqs_tr=self._freqs_tr,
                                     include_tr_rot=self._include_tr_rot,
                                     msgBar=self._smartdict['msgBar'],
                                     dblclick_callback=\
                                     self._smartdict['dblclick_callback'])
    self._varsdict['table_values'] = widget
    self._varsdict['table_values'].grid(row=0, column=1,
                                        padx=3, pady=3, sticky='news')
    
    ## second tab - circles
    tabCircles = self.add('Circles')

    tabCircles.grid_rowconfigure(1, weight=1)
    tabCircles.grid_columnconfigure(2, weight=1)

    # buttons (left side)
    buttons = Tkinter.Frame(tabCircles)
    buttons.grid(row=0, column=0, rowspan=2, padx=3, pady=3, sticky='n')
    
    # save button
    widget = Tkinter.Button(buttons,
                            image=getimage('save'),
                            relief='flat',
                            overrelief='raised',
                            command=self.__export_circles)
    self._varsdict['btn_save_circles'] = widget
    self._varsdict['btn_save_circles'].grid(row=0, column=0,
                                            padx=3, pady=3, sticky='n')
    # plot all_ref -> all_tr on an A4 page
    self._varsdict['btn_A4'] = Tkinter.Button(buttons,
                                              image=getimage('A4'),
                                              relief='flat',
                                              overrelief='raised',
                                              command=self.__resize_canvas)    
    self._varsdict['btn_A4'].grid(row=1, column=0, padx=3, pady=3, sticky='n')

    # counter to control the size of the canvas
    self._varsdict['var_scale_size'] = Tkinter.DoubleVar()
    self._varsdict['var_scale_size'].set(1.0)

    validate = dict(validator='real', min=0.5, max=10.0)
    counter_size = Pmw.Counter(buttons,
                               autorepeat=False,
                               orient='vertical',
                               entry_width=3,
                               entryfield_value=1.0,
                               datatype=dict(counter='real', separator='.'),
                               entry_textvariable=\
                               self._varsdict['var_scale_size'],
                               entryfield_validate=validate,
                               entryfield_modifiedcommand=self.__resize_canvas,
                               increment=0.1)
    counter_size.grid(row=2, column=0, padx=3, pady=3, sticky='n')

    ## properties in the upper left corner of the circles
    self._varsdict['btn_settings'] = Tkinter.Button(tabCircles,
                                                    image=getimage('prefs'),
                                                    relief='flat',
                                                    overrelief='raised',
                                                    command=self.__settings)
    self._varsdict['btn_settings'].grid(row=0, column=1, padx=3, pady=3)

    ## scrollable area for circles and
    ## headers with freq/no as text controls

    # row header
    widget = Tkinter.Text(tabCircles,
                          height=2,
                          font=resources.FONT_TABLE_SEL_HEADER1,
                          foreground='blue',
                          state='disabled',
                          wrap='none')
    self._varsdict['canvas_columnheader'] = widget
    self._varsdict['canvas_columnheader'].grid(row=0, column=2,
                                               padx=1, pady=1, sticky='ew')
    # column headers
    widget = Tkinter.Text(tabCircles,
                          width=9,
                          font = resources.FONT_TABLE_SEL_HEADER1,
                          foreground='blue',
                          state='disabled')
    self._varsdict['canvas_rowheader'] = widget
    self._varsdict['canvas_rowheader'].grid(row=1, column=1,
                                            padx=1, pady=1, sticky='ns')

    # circles
    self._varsdict['scrolled_frame'] = Pmw.ScrolledFrame(tabCircles)
    self._varsdict['scrolled_frame'].grid(row=1, column=2, columnspan=2,
                                          padx=3, pady=3, sticky='news')
    self._varsdict['scrolled_frame'].interior().grid_rowconfigure(0, weight=1)
    self._varsdict['scrolled_frame'].interior().grid_columnconfigure(0,
                                                                     weight=1)
    # do not update the circles
    self._varsdict['circles'] = TwoDCircles(
                          self._varsdict['scrolled_frame'].interior(),
                          msgBar=self._smartdict['msgBar'],
                          dblclick_callback=self.__dblclick_circle,
                          mouse_motion_callback=self.__show_ij_freqno,
                          mouse_leave_callback=self.__clean_circle_headers,
                          ndigits=3)
    
    self._varsdict['circles'].grid(row=0, column=0,
                                   padx=0, pady=0, sticky='news')
    # circles in A4 representation should be shown
    self.selectpage(1)

  def _declare_properties(self) :
    """Declare properties of the widget."""
    self.__class__.table = property(fget=self._get_table)
    self.__class__.circles_frame = property(fget=self._get_circles_frame)

  def _bind_events(self) :
    """Bind events."""
    cmd = misc.Command(mouse_wheel, self._varsdict['scrolled_frame'])
    self._varsdict['circles'].bind('<Button-4>', cmd)
    self._varsdict['circles'].bind('<Button-5>', cmd)

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    self._balloon.bind(self._varsdict['btn_save_values'],
                      'Save the table to a CSV file.')
    self._balloon.bind(self._varsdict['btn_save_circles'],
                      'Save the matrix in PS/EPS/PDF formats.')
    
  def _get_table(obj) :
    """Getter function for the table property."""
    return obj.__table_values

  _get_table = staticmethod(_get_table)

  def _get_circles_frame(obj) :
    """Getter function for the circles_frame property."""
    return obj.__scrolled_frame

  _get_circles_frame = staticmethod(_get_circles_frame)

  def __dblclick_circle(self, i, j) :
    """Double clicked on a circle."""
    if callable(self._smartdict['dblclick_callback']) :
      # convert the circle positions to the vibrational numbers
      ref_index, tr_index = self._varsdict['table_values'].ij_to_vibno(i, j)
      
      self._smartdict['dblclick_callback'](ref_index, tr_index)

      # saving the last clicked vibrational pair
      # marking the currently clicked pair
      # unmarking the previous one
      if not hasattr(self, '_last_clicked_vibno') :
        self._last_clicked_vibno = None

      if self._last_clicked_vibno is not None :
        self._varsdict['circles'].mark_rect_ij(
          self._varsdict['table_values'].vibno_to_ij(*self._last_clicked_vibno),
          False)
    
      self._varsdict['circles'].mark_rect_ij(
        self._varsdict['table_values'].vibno_to_ij(ref_index, tr_index))
      
      self._last_clicked_vibno = (ref_index, tr_index)

  def __export_table(self) :
    """Export the table as a *.csv file."""
    filetypes = [ (resources.STRING_FILETYPE_CSVFILE_DESCRIPTION, '*.csv') ]
    
    filename = tkFileDialog.SaveAs(parent=self.interior(),
                                   filetypes=filetypes,
                                   defaultextension='.csv',
                                   initialdir=self.__lastdir).show()
    if filename is not None :
      file_csv = open(filename, 'w+')
      file_csv.write(self._varsdict['table_values'].csv)
      file_csv.close()

      self.__lastdir = os.path.dirname(filename)

  def __export_circles(self) :
    """Export the circles."""    
    filename = tkFileDialog.SaveAs(parent=self.interior(),
                                   filetypes=self.__save_filetypes,
                                   initialdir=self.__lastdir).show()
    if filename is not None :
      try :
        base, ext = os.path.splitext(filename)
        ext = ext.lower()

        if ext not in ('.eps', '.ps', '.pdf') :
          raise InvalidArgumentError('Unsupported type : %s' % ext)

        # unmark the rectangle before saving
        if self._last_clicked_vibno is not None :
          self._varsdict['circles'].mark_rect_ij(
            self._varsdict['table_values'].vibno_to_ij
            (*self._last_clicked_vibno),
            mark=False)

        # just ps        
        if ext in ('.eps', '.ps') :
          self._varsdict['circles'].postscript(file=filename)

        # pdf
        else :
          # as a first step save to ps, and then to pdf
          psname = '%s.ps' % base
          self._varsdict['circles'].postscript(file=psname)
          status = misc.ps2pdf(psname,
                               removesrc=True,
                               CompatibilityLevel='1.3')

        self.__lastdir = os.path.dirname(filename)
        
      except :
        show_exception(sys.exc_info())

  def __find_font(self, max_vibno, maxwidth) :
    """Find a font for which the width of the number max_vibno would
    be smaller than maxwidth.
    
    """
    # ('Courier', 13, 'bold')
    for size in xrange(13, 1, -1) :
      font = ('Courier', size, 'bold')
      if tkFont.Font(self.interior(), font=font).\
         measure(str(max_vibno)) < maxwidth :
        break

    return font

  def __resize_canvas(self) :
    """Resize the canvas with circles."""
    try :
      kw = dict(scale_factor=self._varsdict['var_scale_size'].get(),
                show_tr_rot=self.__show_tr_rot,
                nrot_ref=self.__nrot_ref,
                nrot_tr=self.__nrot_tr)
      self.show_A4(**kw)  
    except :
      pass

  def __show_ij_freqno(self, i, j) :
    """Show frequency / no in the text widgets associated with the circles."""
    # position of the mouse poiter and upper left coordinates of the headers
    # x is important for the column header, y for the row headers
    x, y = self._varsdict['circles'].winfo_pointerxy()
    colrootx = self._varsdict['canvas_columnheader'].winfo_rootx()
    colrooty = self._varsdict['canvas_rowheader'].winfo_rooty()

    # position of the text
    delta_x = x - colrootx
    delta_y = y - colrooty

    #
    if 0 > delta_x or 0 > delta_y :
      return

    # calculating the width and height of a single symbol to
    # place the labels properly
    # the font should be with fixed width
    font = tkFont.Font(self.interior(), font=resources.FONT_TABLE_SEL_HEADER1)

    symbol_width, symbol_height = font.measure(' '), font.metrics()['ascent']

    # current sizes of the headers = size of the circles frame
    self.interior().tk.call('update', 'idletasks')
    cur_colheader_width  = self._varsdict['canvas_columnheader'].winfo_width()
    cur_rowheader_height = self._varsdict['canvas_rowheader'].winfo_height()

    # enabling the text editing
    self._varsdict['canvas_columnheader'].configure(state='normal')
    self._varsdict['canvas_rowheader'].configure(state='normal')
    
    # cleaning the headers
    self._varsdict['canvas_columnheader'].delete('1.0', 'end')
    self._varsdict['canvas_rowheader'].delete('1.0', 'end')

    # transforming the raw ij of the canvas to
    # the indices of the reference & trial molecules
    ref_index, tr_index = self._varsdict['table_values'].ij_to_vibno(i, j)

    ## column headers (trial molecule)
    nempty = int(cur_colheader_width / symbol_width) + 20
    dummytext = ('%%%ds' % nempty) % ''
    format_no   = '%s'
    format_freq = '%.0f'

    # consider the translations / rotations
    if 0 > tr_index :
      freq_col = format_freq % 0.
      no_col   = format_no % \
                 resources.STRINGS_TRANSLATIONS_ROTATIONS_LABELS[-tr_index-1]
    else :
      freq_col = format_freq % self._freqs_tr[tr_index]
      no_col   = format_no % str(tr_index)
    
    self._varsdict['canvas_columnheader'].configure(width=nempty)
    self._varsdict['canvas_columnheader'].insert('end',
                                                 dummytext + '\n' + dummytext)
    self._varsdict['canvas_columnheader'].insert(
      '@%d,%d' % (delta_x, symbol_height), freq_col)
    self._varsdict['canvas_columnheader'].insert(
      '@%d,%d' % (delta_x, 2*symbol_height), no_col)

    ## row headers
    rowheader_width = int(self._varsdict['canvas_rowheader'].cget('width'))
    
    nlines = int(cur_rowheader_height / symbol_height)
    dummylineformat = '%%%ds\n' % rowheader_width
    format_rowheader = '%5s%4s'
    dummytext = ''
    for q in xrange(nlines) :
      dummytext = ''.join((dummytext, dummylineformat % ''))

    # consider the translations / rotations
    if 0 > ref_index :
      freq_row = format_freq % 0.
      no_row   = format_no % \
                 resources.STRINGS_TRANSLATIONS_ROTATIONS_LABELS[-ref_index-1]
    else :
      freq_row = format_freq % self._freqs_ref[ref_index]
      no_row   = format_no % str(ref_index)
      
    self._varsdict['canvas_rowheader'].insert('end', dummytext)
    self._varsdict['canvas_rowheader'].insert(
      '@0,%d' % (delta_y + symbol_height/2),
      format_rowheader % (freq_row, no_row))

    ## disabling the text editing to prevent its modification
    self._varsdict['canvas_columnheader'].configure(state='disabled')
    self._varsdict['canvas_rowheader'].configure(state='disabled')

  def __clean_circle_headers(self) :
    """Clean the headers of the circles canvas.

    Called when the mouse leaves the widget.
    
    """
    # unblocking the text controlls so that they could be edited
    self._varsdict['canvas_columnheader'].configure(state='normal')
    self._varsdict['canvas_rowheader'].configure(state='normal')
    
    self._varsdict['canvas_columnheader'].delete('1.0', 'end')
    self._varsdict['canvas_rowheader'].delete('1.0', 'end')

    # blocking it to prevent modification
    self._varsdict['canvas_columnheader'].configure(state='disabled')
    self._varsdict['canvas_rowheader'].configure(state='disabled')    

  def __settings(self) :
    """Callback for the settings button."""
    if 'dlg_settings' not in self._varsdict :
      from pyviblib.gui.dialogs import TwoDCirclesSettingsDialog
      
      self._varsdict['dlg_settings'] = TwoDCirclesSettingsDialog(
        self.page(0), self._varsdict['circles'])
      
    self._varsdict['dlg_settings'].update_controls()
    self._varsdict['dlg_settings'].show()

  def update_contents(self, ref_from, ref_to, tr_from, tr_to,
             precision, show_tr_rot, nrot_ref, nrot_tr,
             mark=False, threshold_marked=0.) :
    """Update the contents of the table and circles.

    Positional arguments :
    ref_from          -- start vibration number of the reference molecule
    ref_to            -- end vibration number of the reference molecule
    tr_from           -- start vibration number of the trial molecule
    tr_to             -- end vibration number of the reference molecule
    precision         -- number of decimal points to show
    show_tr_rot       -- whether translations/rotations are to be shown
    nrot_ref          -- number of rotations in the reference molecule
    nrot_tr           -- number of rotations in the trial molecule

    Keyword arguments :
    mark              -- whether to mark elements exceeding a threshold
                         supplied by the threshold_marked argument
                         (default False)
    threshold_marked  -- threshold for marking elements (default 0.)
    
    """
    # saving the information
    self.__show_tr_rot = show_tr_rot
    self.__nrot_ref    = nrot_ref
    self.__nrot_tr     = nrot_tr
    
    # table
    self._varsdict['table_values'].update_table(
      ref_from, ref_to, tr_from, tr_to, precision, show_tr_rot, nrot_ref,
      nrot_tr, mark, threshold_marked)

    # circles
    labels = self._varsdict['table_values'].labels
    self.__max_circlewidth = 50
    
    self._varsdict['circles'].update(
      data=self._varsdict['table_values'].data,
      labels1_cols=labels['labels1_cols'],
      labels1_rows=labels['labels1_rows'],
      labels2_cols=labels['labels2_cols'],
      labels2_rows=labels['labels2_rows'],
      dblclick_callback=self.__dblclick_circle,
      font_labels1=resources.FONT_TWODCIRCLES_LABEL1,
      font_labels2=resources.FONT_TWODCIRCLES_LABEL2,
      text_padding=5,
      indent=15,
      max_circlewidth=50)
    
    self.__a4_enabled = False

    # marking the last clicked element
    if hasattr(self, '_last_clicked_vibno') and \
       self._last_clicked_vibno is not None :
      # prevent marking of tr / rot in the a4 representation & if is not desired
      if (self.__a4_enabled and any(0 > array(self._last_clicked_vibno))) or \
         (not show_tr_rot and any(0 > array(self._last_clicked_vibno))) :
        pass
      else :
        self._varsdict['circles'].mark_rect_ij(
          self._varsdict['table_values'].vibno_to_ij(*self._last_clicked_vibno))

  def show_A4(self, scale_factor=1.0,
              show_tr_rot=False, nrot_ref=0, nrot_tr=0) :
    """Switch to the A4 representation of the circles.

    Keyword arguments :
    scale_factor -- number for scaling the canvas size (default 1.)
    show_tr_rot  -- whether to show translations/rotations (default False)
    nrot_ref     -- number of rotations in the reference molecule (default 0)
    nrot_tr      -- number of rotations in the trial molecule (default 0)
    
    """
    if self._freqs_ref is None or self._freqs_tr is None :
      return

    # can show tr/rot if they are present in the matrix
    show_tr_rot = show_tr_rot and self._include_tr_rot
    
    # number of frequencies in the reference and trial molecules
    # m defines the width of the whole matrix
    n = len(self._freqs_ref) - 1
    m = len(self._freqs_tr)  - 1
    
    if show_tr_rot :
      n += 3 + nrot_ref
      m += 3 + nrot_tr
    
    # resolution dots per mm

    # width of an A4-page in pixels
    width_A4 = scale_factor * self.winfo_fpixels('210m')
    
    # indent on the page - 5 mm
    indent = self.winfo_pixels('5m')

    # approximate width of circles
    maxwidth = int( float(width_A4 - 2. * indent) / float(m + 1) )

    # appropriate font
    font_labels2 = self.__find_font(m, maxwidth)

    # width of the label text
    labels2text_width = tkFont.Font(
      self.interior(), font=font_labels2).measure(str(m))

    # text_padding
    text_padding = max(0, (maxwidth - labels2text_width) / 2)

    # all circles must pass to the width of an A4 page : 210 mm
    self.__max_circlewidth = int(
      float(width_A4 - 2. * indent - maxwidth) / float(m+1))

    # updating the controls
    self._varsdict['table_values'].update_table(ref_from=1,
                                                ref_to=len(self._freqs_ref)-1,
                                                tr_from=1,
                                                tr_to=len(self._freqs_tr)-1,
                                                precision=3,
                                                show_tr_rot=show_tr_rot,
                                                nrot_ref=nrot_ref,
                                                nrot_tr=nrot_tr,
                                                mark=False,
                                                threshold_marked=0.)
    # circles : set the labels properly
    labels = resources.STRINGS_TRANSLATIONS_ROTATIONS_LABELS
    if show_tr_rot :
      labels_ref = [None] + list(labels[:3+nrot_ref]) + \
                   range(1, len(self._freqs_ref))

      labels_tr  = [None] + list(labels[:3+nrot_tr]) + \
                   range(1, len(self._freqs_tr))

    else :
      labels_ref = range(len(self._freqs_ref))
      labels_tr  = range(len(self._freqs_tr))
        
    self._varsdict['circles'].update(data=self._varsdict['table_values'].data,
                                     labels1_cols=None,
                                     labels1_rows=None,
                                     labels2_cols=labels_tr,
                                     labels2_rows=labels_ref,
                                     max_circlewidth=self.__max_circlewidth,
                                     indent=indent,
                                     text_padding=text_padding,
                                     font_labels2=font_labels2)
    self.__a4_enabled = True
    
    # marking the last clicked element
    if hasattr(self, '_last_clicked_vibno') and \
       self._last_clicked_vibno is not None :
      # prevent marking of tr / rot in the a4 representation
      if any(0 > array(self._last_clicked_vibno)) :
        pass
      else :
        self._varsdict['circles'].mark_rect_ij(
          self._varsdict['table_values'].vibno_to_ij(
            *self._last_clicked_vibno))


class WizardWidget(BaseWidget, Tkinter.Frame) :
  """Wizard widget.

  The following read-only properties are exposed :
      notebook  -- encapsulated internal notebook
      buttonbox -- Back and Next buttons

  """

  def __init__(self, master, **kw) :
    """Constructor of the class.

    Positional arguments :
    master       -- parent widget
    
    Keyword arguments :
    back_command -- command for the Back button (default None)
    next_command -- command for the Next button (default None)
    
    """
    Tkinter.Frame.__init__(self, master)
    BaseWidget.__init__(self, **kw)

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=1)

    # notebook without tabs
    self._varsdict['notebook'] = Pmw.NoteBook(self, tabpos=None)
    self._varsdict['notebook'].grid(row=0, column=0,
                                    padx=3, pady=3, sticky='news')
    # separator
    separator = Tkinter.Frame(self, height=2, bd=1, relief='sunken')
    separator.grid(row=1, column=0, padx=3, pady=3, sticky='we')

    # buttons
    self._varsdict['buttonbox'] = Pmw.ButtonBox(self)
    self._varsdict['buttonbox'].grid(row=2, column=0,
                                     padx=3, pady=3, sticky='we')

    self._varsdict['buttonbox'].add(resources.STRING_BUTTON_BACK,
                                    command=self._smartdict['back_command'])
    self._varsdict['buttonbox'].add(resources.STRING_BUTTON_NEXT,
                                    command=self._smartdict['next_command'])

    self._varsdict['buttonbox'].setdefault(resources.STRING_BUTTON_NEXT)
    self._varsdict['buttonbox'].alignbuttons()

  def _declare_properties(self) :
    """Declare properties of the widget."""
    self.__class__.notebook = property(
      fget=misc.Command(misc.Command.fget_value, self._varsdict['notebook']))
      
    self.__class__.buttonbox = property(
      fget=misc.Command(misc.Command.fget_value, self._varsdict['buttonbox']))


class GeometryMeasureToolbar(ButtonToolbar) :
  """Toolbar for measuring distances, angles and dihedral angles.

  The following readable and writable property is exposed :
      resolution -- resolution of the connected render widget
      
  """

  def __init__(self, master, renderWidget, **kw) :
    """Constructor of the class.

    Positional arguments :
    master    -- parent widget
    widget    -- render widget to connect to
    
    Keyword arguments :
    horizontal -- whether the toolbar is horizontal (default False)
    
    """
    if not isinstance(renderWidget, MoleculeRenderWidget) :
      raise ConstructorError('Invalid renderWidget argument')

    self._master        = master
    self.__renderWidget = renderWidget

    ButtonToolbar.__init__(self, master, **self._toolbar_kw(**kw))
    self.configure(relief='ridge', borderwidth=2)  

  def _toolbar_kw(**kw) :
    """Retrieve the keywords of the parent class."""
    tb_kw = dict(kw)

    tb_kw['horizontal'] = kw.get('horizontal', False)
    tb_kw['style']      = 0

    return tb_kw

  _toolbar_kw = staticmethod(_toolbar_kw)
    
  def _init_vars(self) :
    """Initialize variables."""
    ButtonToolbar._init_vars(self)
    self._smartdict['resolution'] = resources.NUM_RESOLUTION_VTK    

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    # distance
    self.add_button(imagename='distance',
                    command=misc.Command(self.__start_measure, 2),
                    helptext='Measure a distance.')

    # angle
    self.add_button(imagename='angle',
                    command=misc.Command(self.__start_measure, 3),
                    helptext='Measure an angle.')

    # dihedral angle
    self.add_button(imagename='dihedral_angle',
                    command=misc.Command(self.__start_measure, 4),
                    helptext='Measure a dihedral angle.')

    # remove selection
    widget = self.add_button(imagename='remove',
                             command=self.__remove,
                             helptext='Measure a dihedral angle.')
    self._varsdict['btn_remove'] = widget

    # settings
    self._varsdict['color_angle']    = resources.COLOR_MARKING_TRIANGLE
    self._varsdict['color_dihedral'] = misc.color_complementary(
      self._varsdict['color_angle'])
    
    self.__renderWidget.clicked_atom_callback = self.__clicked_atom_callback
    self.__updateGUI()

  def _declare_properties(self) :
    """Declare properties of the widget."""
    self.__class__.resolution = property(fget=self._get_resolution,
                                         fset=self._set_resolution)

  def _bind_help(self) :
    """Bind help messages to the GUI components."""
    pass

  def __remove(self) :
    """Remove marked atoms."""
    self.__renderWidget.cleanup()
    
    self.__renderWidget.render_molecule(
                resolution=self._smartdict['resolution'],
                molecule_mode=resources.NUM_MODE_BALLSTICK,
                bonds_mode=resources.NUM_MODE_BONDS_ATOMS_COLOR)
    
    self.__renderWidget.Render()
    self.__renderWidget.do_picking = False
    self.__updateGUI()

  def _set_resolution(obj, res) :
    """Setter function for the resolution property."""
    obj._smartdict.kw['resolution'] = res

  _set_resolution = staticmethod(_set_resolution)

  def _get_resolution(obj) :
    """Getter function for the resolution property."""
    return obj._smartdict['resolution']

  _get_resolution = staticmethod(_get_resolution)

  def __start_measure(self, Nmaxpicked) :
    """Prepare the widget for measuring.

    Enable the picking and set the number of maximaly allowed picked atoms.
    
    """
    # cleaning the list of picked atoms
    self.__remove()
    self.__renderWidget.do_picking = True
    self._Nmaxpicked               = Nmaxpicked

  def __clicked_atom_callback(self, num, node_index) :
    """Called when the user left clicks on an atom.

    max_picked : maximal number of atoms that can be picked
    (disable picking if exceeded)
    
    """
    # processing only left clicks on non-picked atoms
    if 1 != num or not hasattr(self, '_Nmaxpicked') or \
       not self.__renderWidget.do_picking:
      return

    node = self.__renderWidget.get_node('atoms', node_index)
    if node is None :
      return

    # disabling the picking if maximal number of picked atoms is reached
    self.__renderWidget.do_picking = (self.__renderWidget.Npicked < \
                                      self._Nmaxpicked)
    self.__updateGUI()

    if self.__renderWidget.Npicked == self._Nmaxpicked :
      # render the triangles for the bonds
      atoms_list = self.__renderWidget.picked_atoms_indices
      
      if 3 <= self._Nmaxpicked :
        
        # making the middle atom completely opaque for an angle !
        if 3 == self._Nmaxpicked :
          middle_node = self.__renderWidget.get_node('atoms', atoms_list[1])
          middle_node.highlight_picked(True, transparency=0.6)
        
        self.__renderWidget.render_triangle(
          atoms_list[0],
          atoms_list[1],
          atoms_list[2],
          color=self._varsdict['color_angle'])

      if 4 == self._Nmaxpicked :
        self.__renderWidget.render_triangle(
          atoms_list[1],
          atoms_list[2],
          atoms_list[3],
          color=self._varsdict['color_dihedral'])

      self.__show_result(atoms_list)       

  def __show_result(self, atoms_list) :
    """Show the result of to the user.

    Positional arguments :
    atoms_list -- list of 0-based atoms
    
    """
    if atoms_list is None :
      return
    
    len_list = len(atoms_list)
    if len_list not in (2, 3, 4) :
      return

    mol = self.__renderWidget.molecule
    
    if 2 == len_list :
      d   = mol.distance(1 + atoms_list[0], 1 + atoms_list[1])
      msg = u'Distance (%d,%d) is %.3f \u00C5' % \
            (1 + atoms_list[0], 1 + atoms_list[1], d)

    if 3 == len_list :
      a   = mol.angle(1 + atoms_list[0], 1 + atoms_list[1], 1 + atoms_list[2])
      msg = u'Angle (%d,%d,%d) is %.3f\u00B0' % \
              (1 + atoms_list[0], 1 + atoms_list[1], 1 + atoms_list[2], a)

    if 4 == len_list :
      dh  = mol.dihedral(1 + atoms_list[0], 1 + atoms_list[1],
                         1 + atoms_list[2], 1 + atoms_list[3])
      msg = u'Dihedral angle (%d,%d,%d,%d) is %.3f\u00B0' % \
              (1 + atoms_list[0], 1 + atoms_list[1], 1 + atoms_list[2],
               1 + atoms_list[3], dh)

    if self._smartdict['msgBar'] is not None :
      self._smartdict['msgBar'].message('state', msg)

    tkMessageBox.showinfo(parent=self._master, title='Result', message=msg)    

  def __updateGUI(self) :
    """Update the remove button."""
    if 0 == self.__renderWidget.Npicked :
      state = 'disabled'
    else :
      state = 'normal'

    self._varsdict['btn_remove'].configure(state=state)
    

class ChooseColorWidget(BaseWidget, Tkinter.Frame) :
  """Widget for choosing a color.

  Consists of a label with a description and a button for changing the color.

  The following readable and writable property is exposed :
      color -- color in the HTML format

  """
  

  def __init__(self, master, **kw) :
    """Constructor of the class.

    Positional arguments :
    master        -- parent widget

    Keyword arguments :
    text          -- description (default '')
    initialcolor  -- initial color of the button (default default)
    sticky        -- sticky option for the button (default 'w')
    label_width   -- width of the label (default length of the text)
    button_width  -- width of the button (default 7)
    
    """
    Tkinter.Frame.__init__(self, master)
    BaseWidget.__init__(self, **kw)

  def _init_vars(self) :
    """Initialize variables."""
    self._smartdict['text'] = ''
    self._smartdict['initialcolor'] = None
    self._smartdict['sticky'] = 'w'

    self._smartdict['label_width'] = len(self._smartdict['text'])
    self._smartdict['button_width'] = 7

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    # label with the description (empty unless given)
    # text aligned to the left
    lbl = Tkinter.Label(self,
                        text=self._smartdict['text'],
                        width=self._smartdict['label_width'],
                        anchor='w',
                        padx=3, pady=3)
    lbl.grid(row=0, column=0, sticky='w')

    # button which allows to change the color
    # sticky option can be specified (default : 'w')
    self.grid_columnconfigure(1, weight=1)
    
    widget = Tkinter.Button(self,
                            bg=self._smartdict['initialcolor'],
                            activebackground=self._smartdict['initialcolor'],
                            width=self._smartdict['button_width'])
    self._varsdict['btn_color'] = widget
    self._varsdict['btn_color'].configure(command=self.__set_button_color)
    
    self._varsdict['btn_color'].grid(row=0, column=1,
                                     padx=3, pady=3,
                                     sticky=self._smartdict['sticky'])

  def _declare_properties(self) :
    """Declare properties of the widget."""
    self.__class__.color = property(fget=self._get_color,
                                    fset=self._set_color)    

  def _set_color(obj, color) :
    """Setter function for the color property."""
    obj._varsdict['btn_color'].configure(bg=color, activebackground=color)

  _set_color = staticmethod(_set_color)

  def _get_color(obj) :
    """Getter function for the color property."""
    return obj._varsdict['btn_color'].cget('bg')

  _get_color = staticmethod(_get_color)

  def __set_button_color(self) :
    """
    Choose a color and set it to the background of the button.
    """
    color_chosen = tkColorChooser.Chooser(
                    parent=self._varsdict['btn_color'],
                    initialcolor=self._varsdict['btn_color'].cget('bg'),
                    title=self._smartdict['text']).show()

    if color_chosen[0] is not None :
      self.color = color_chosen[1]


class AxesSettingsWidget(BaseWidget, Tkinter.Frame) :
  """Widget for setting properties of axes.

  The following readable and writable properties are exposed
      limits_auto          -- whether the limits are to be set automatically (*)
      from_                -- upper range of the y axis (*)
      to_                  -- lower range of the y axis (*)
      multfactor           -- order of magnitude for y values (*)
      ticks_number         -- number of ticks(*)
      ticks_scaling_factor -- scaling factor (*)
      linewidth            -- line width
      linecolor            -- line color

  The following read-only properties are exposed :      
      ticks_option         -- how to render ticks (*)
      ticks_auto           -- whether the ticks are rendered automatically (*)      

  Properties marked with an asterisk (*) are exposed if the add_limits argument
  of the constructor was set to True.  
  
  """

  """List of properties."""
  LIST_PROPERTIES = ('limits_auto', 'from_', 'to_', 'multfactor',
                     'ticks_option', 'ticks_auto', 'ticks_number',
                     'ticks_scaling_factor', 'linewidth', 'linecolor',
                     'invert')

  def __init__(self, master, **kw) :
    """Constructor of the class.

    Positional arguments :
    master              -- parent widget
    
    Keyword arguments :
    add_limits          -- whether to add the controls for the y values
                           (default True)
    add_invert          -- whether to add a checkbox for inverting y values
                           (default False)
    buttons_to_validate -- list of buttons to block if the user
                           input is invalid (default None)
    
    """
    Tkinter.Frame.__init__(self, master)
    BaseWidget.__init__(self, **kw)      

  def _init_vars(self) :
    """Initialize variables."""
    # add limits by default
    self._smartdict['add_limits'] = True

  def _declare_properties(self) :
    """Declare properties of the widget."""
    # auto adjust limits ?
    self.__class__.limits_auto = property(fget=self.__get_limits_auto,
                                          fset=self.__set_limits_auto)

    # can be definied automatically
    if self._smartdict['add_limits'] :
      # limits
      self.__class__.from_      = self.__create_property('from_')
      self.__class__.to_        = self.__create_property('to_')
      self.__class__.multfactor = self.__create_property('multfactor')

      # ticks
      self.__class__.ticks_option = property(fget=self.__get_ticks_option)
      self.__class__.ticks_auto   = property(fget=self.__get_ticks_auto)
      
      self.__class__.ticks_number = self.__create_property('ticks_number')
      self.__class__.ticks_scaling_factor = \
                            self.__create_property('ticks_scaling_factor')

    if self._smartdict['add_invert'] :
      self.__class__.invert = self.__create_property('invert')
      
    # appearance
    self.__class__.linewidth = self.__create_property('linewidth')
    self.__class__.linecolor = property(fget=self.__get_linecolor,
                                        fset=self.__set_linecolor)

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=1)

    row = 0
    ### axis settings
    if self._smartdict['add_limits'] :
      group_axis = Pmw.Group(self, tag_text='Axis')
      group_axis.grid(row=row, column=0, padx=3, pady=3, sticky='nwe')
      row += 1

      ## Axis limits : manual or auto
      group_axis.interior().grid_rowconfigure(0, weight=1)
      group_axis.interior().grid_columnconfigure(0, weight=1)

      widget = Pmw.RadioSelect(group_axis.interior(),
                               buttontype='radiobutton',
                               orient='vertical',
                               labelpos='w',
                               label_text='Limits ')
      self._varsdict['radio_axis_lim'] = widget
      self._varsdict['radio_axis_lim'].grid(row=0, column=0,
                                            padx=3, pady=3, sticky='w')
      self._varsdict['radio_axis_lim'].add('manual')
      self._varsdict['radio_axis_lim'].add('auto')
      self._varsdict['radio_axis_lim'].setvalue('manual')

      # from, to for the manual choice
      # one can specify values between 0 and 1
      self._varsdict['var_axis_from_'] = Tkinter.DoubleVar()
      self._varsdict['var_axis_to_']   = Tkinter.DoubleVar()
      
      validate = dict(validator='real',
                      min=-1.0,
                      max=1.0,
                      separator='.')
      var = self._varsdict['var_axis_from_']
      entryfield_from = Pmw.EntryField(group_axis.interior(),
                                       entry_textvariable=var,
                                       label_text='From ',
                                       labelpos='w',
                                       entry_width=7,
                                       validate=validate,
                                       modifiedcommand=self.__updateGUI)
      entryfield_from.grid(row=0, column=1, padx=3, pady=8, sticky='wn')

      var = self._varsdict['var_axis_to_']
      entryfield_xto = Pmw.EntryField(group_axis.interior(),
                                      entry_textvariable=var,
                                      label_text='to ',
                                      labelpos='w',
                                      entry_width=7,
                                      validate=validate,
                                      modifiedcommand=self.__updateGUI)
      entryfield_xto.grid(row=0, column=2, padx=3, pady=8, sticky='wn')

      # multiply factor 10**(x)
      self._varsdict['var_axis_multfactor'] = Tkinter.IntVar()
      
      validate = dict(validator='integer',
                      min=-25,
                      max=+25)
      var = self._varsdict['var_axis_multfactor']
      counter_multfactor = Pmw.Counter(group_axis.interior(),
                                       entry_textvariable=var,
                                       label_text='Multiply factor ',
                                       labelpos='w',
                                       datatype=dict(counter='integer'),
                                       entry_state='readonly',
                                       entry_width=3,
                                       entryfield_validate=validate,
                                       increment=1,
                                       autorepeat=True,
                                       entryfield_value=-14)
      counter_multfactor.grid(row=0, column=3, padx=3, pady=8, sticky='wn')

      ## Ticks' settings
      group_axis.interior().grid_rowconfigure(1, weight=1)

      widget = Pmw.RadioSelect(group_axis.interior(),
                               buttontype='radiobutton',
                               orient='vertical',
                               labelpos='w',
                               label_text='Ticks ')
      self._varsdict['radio_axis_ticks'] = widget
      self._varsdict['radio_axis_ticks'].grid(row=1, column=0,
                                              padx=3, pady=3, sticky='w')
      self._varsdict['radio_axis_ticks'].add('scaling factor')
      self._varsdict['radio_axis_ticks'].add('fixed number')
      self._varsdict['radio_axis_ticks'].add('auto')
      
      self._varsdict['radio_axis_ticks'].setvalue('auto')

      # vertical frame for the options
      group_axis.interior().grid_rowconfigure(1, weight=1)
      group_axis.interior().grid_columnconfigure(1, weight=1)
      
      frm = Tkinter.Frame(group_axis.interior())
      frm.grid(row=1, column=1, padx=3, pady=3, sticky='nw')

      # scaling factor : from 0. to 1. (default : 0.1)
      self._varsdict['var_axis_ticks_scaling_factor'] = Tkinter.DoubleVar()
      self._varsdict['var_axis_ticks_scaling_factor'].set(0.1)

      validate = dict(validator='real',
                      min=0.0,
                      max=1.0,
                      separator='.')
      var = self._varsdict['var_axis_ticks_scaling_factor']
      entryfield_sf = Pmw.EntryField(frm,
                                     labelpos='w',
                                     label_text='',
                                     entry_textvariable=var,
                                     entry_width=10,
                                     validate=validate,
                                     modifiedcommand=self.__updateGUI)
      entryfield_sf.grid(row=0, column=0, padx=3, pady=4, sticky='wn')

      # fixed number of ticks (from 0 to 10, default : 3)
      self._varsdict['var_axis_ticks_number'] = Tkinter.IntVar()
      self._varsdict['var_axis_ticks_number'].set(3)
      
      validate = dict(validator='integer',
                      min=0,
                      max=10)
      var = self._varsdict['var_axis_ticks_number']
      counter_multfactor = Pmw.Counter(frm,
                                       labelpos='w',
                                       label_text='',
                                       entry_textvariable=var,
                                       datatype=dict(counter='integer'),
                                       entry_state='readonly',
                                       entry_width=3,
                                       entryfield_validate=validate,
                                       increment=1,
                                       autorepeat=True)
      counter_multfactor.grid(row=1, column=0, padx=3, pady=4, sticky='wn')

      # invert axes (useful for ROA:)
      if self._smartdict['add_invert'] :
        self._varsdict['var_axis_invert'] = Tkinter.IntVar()
        self._varsdict['var_axis_invert'].set(0)

        checkbtn = Tkinter.Checkbutton(group_axis.interior(),
                                       text='Invert values',
                                       variable=\
                                       self._varsdict['var_axis_invert'])
        checkbtn.grid(row=2, column=0, padx=3, pady=6, sticky='w')

      # align the controls of the first row
      Pmw.alignlabels((entryfield_sf, counter_multfactor))
      
    ### Appearance
    self.grid_rowconfigure(row, weight=1)
    
    group_appearance = Pmw.Group(self, tag_text='Appearance')
    group_appearance.grid(row=row, column=0, padx=3, pady=3, sticky='nwe')

    group_appearance.interior().grid_rowconfigure(0, weight=1)
    group_appearance.interior().grid_columnconfigure(0, weight=1)

    # linewidth
    self._varsdict['var_axis_linewidth'] = Tkinter.DoubleVar()
    
    validate = dict(validator='real',
                    min=0.5,
                    max=3.0,
                    separator='.')
    var = self._varsdict['var_axis_linewidth']
    counter_linewidth = Pmw.Counter(group_appearance.interior(),
                                    entry_textvariable=var,
                                    label_text='Line width ',
                                    labelpos='w',
                                    datatype=dict(counter='real'),
                                    entry_state='readonly',
                                    entry_width=3,
                                    entryfield_validate=validate,
                                    increment=0.5,
                                    autorepeat=True,
                                    entryfield_value=1.0)
    counter_linewidth.grid(row=0, column=0, padx=3, pady=3, sticky='w')

    # linecolor : label + button with a desired background
    widget = ChooseColorWidget(group_appearance.interior(),
                               text='Line color',
                               sticky='w')
    self._varsdict['widget_axis_linecolor'] = widget
    self._varsdict['widget_axis_linecolor'].grid(row=0, column=1,
                                                 padx=3, pady=3, sticky='w')

  def __create_property(self, name) :
    """Create a readable and writable property."""
    if 'var_axis_%s' % name in self._varsdict :
      stmt = r"property(fget=misc.Command(self._get_property_, '%s')," + \
             r"fset=misc.Command(self._set_property_, '%s'))"
      return eval(stmt % (name, name))    
    else :
      return None

  def _get_property_(obj, name) :
    """Getter function for a property."""
    return obj._varsdict['var_axis_%s' % name].get()

  _get_property_ = staticmethod(_get_property_)

  def _set_property_(obj, value, name) :
    """Setter function for a property."""
    obj._varsdict['var_axis_%s' % name].set(value)

  _set_property_ = staticmethod(_set_property_)

  def __get_limits_auto(obj) :
    """Getter function for the limits_auto property."""
    return 'auto' == obj._varsdict['radio_axis_lim'].getvalue()

  __get_limits_auto = staticmethod(__get_limits_auto)

  def __set_limits_auto(obj, val) :
    """Setter function for the limits_auto property."""
    obj._varsdict['radio_axis_lim'].setvalue(val and 'auto' or 'manual')
 
  __set_limits_auto = staticmethod(__set_limits_auto)

  def __get_ticks_option(obj) :
    """Getter function for the ticks_option property."""
    return obj._varsdict['radio_axis_ticks'].getvalue()

  __get_ticks_option = staticmethod(__get_ticks_option)

  def __get_ticks_auto(obj) :
    """Getter function for the ticks_auto property."""
    return 'auto' == obj._varsdict['radio_axis_ticks'].getvalue()

  __get_ticks_auto = staticmethod(__get_ticks_auto)

  def __get_linecolor(obj) :
    """Getter function for the linecolor property."""
    return obj._varsdict['widget_axis_linecolor'].color

  __get_linecolor = staticmethod(__get_linecolor)

  def __set_linecolor(obj, value) :
    """Setter function for the linecolor property."""
    obj._varsdict['widget_axis_linecolor'].color = value

  __set_linecolor = staticmethod(__set_linecolor)
  
  def __updateGUI(self) :
    """Check the validity of the input data."""
    if self._smartdict['buttons_to_validate'] is None :
      return
    
    state = 'normal'
    # axes limits should be valid
    try :
      from_ = self._varsdict['var_axis_from_'].get()
      to_   = self._varsdict['var_axis_to_'].get()      
    except ValueError:
      state = 'disabled'      
    else :
      if from_ == to_ :
        state = 'disabled'

    # axis scaling factor cannot be 0.
    try :
      scaling_factor = self._varsdict['var_axis_ticks_scaling_factor'].get()
    except ValueError :
      state = 'disabled'
    else :
      if 0. == scaling_factor :
        state = 'disabled'

    # configuring the buttons
    for btn in self._smartdict['buttons_to_validate'] :
      btn.configure(state=state)
      

class PropertiesWidget(BaseWidget, Pmw.ScrolledFrame) :
  """Widget for showing text properties.

  Each property is represented by one line with the name of the property
  shown at the left and its value at the right.

  The following public methods are exported :
      add_line()      -- add a new line
      add_separator() -- add a separator
      
  """

  def __init__(self, master, **kw) :
    """Constructor of the class.

    Positional arguments :
    master  -- parent widget
    
    Keyword arguments :
    title   -- title at the top of the widget (default '')
    width   -- width in pixel (default 500)
    height  -- heigh in pixel (default 250)
    
    """
    Pmw.ScrolledFrame.__init__(self, master, **self._scrolled_frame_kw(**kw))
    BaseWidget.__init__(self, **kw)
      
  def _scrolled_frame_kw(**kw) :
    """Retrieve the keywords for initialization of the scrolled frame."""
    sf_kw = dict(usehullsize=True, horizflex='expand', vertflex='expand')

    # no title by default
    if kw.get('title', None) is not None :
      sf_kw['labelpos']   = 'n'
      sf_kw['label_text'] = kw['title']

    # size is 500 x 250 by default
    sf_kw['hull_width']  = kw.get('width', 500)
    sf_kw['hull_height'] = kw.get('height', 250)

    return sf_kw

  _scrolled_frame_kw = staticmethod(_scrolled_frame_kw)

  def _init_vars(self) :
    """Initialize variables."""
    self._varsdict['cur_row'] = 0    

  def _constructGUI(self) :
    """GUI is constructed dynamically."""
    pass

  def add_line(self, key, value) :
    """Add a new line.

    Positional arguments :
    key   -- property name
    value -- property value
    
    """
    if 'ar_entries' not in self._varsdict :
      self._varsdict['ar_entries'] = []
      self.interior().grid_columnconfigure(0, weight=1)  

    self.interior().grid_rowconfigure(self._varsdict['cur_row'], weight=1)
    
    item = Pmw.EntryField(self.interior(),
                          labelpos='w',
                          label_text=key,
                          value=value,
                          labelmargin=3,
                          entry_state='readonly')
    item.grid(row=self._varsdict['cur_row'],
              column=0,
              padx=3,
              pady=3,
              sticky='nwe')
    self._varsdict['ar_entries'].append(item)

    self._varsdict['cur_row'] += 1

    Pmw.alignlabels(self._varsdict['ar_entries'])

  def add_separator(self) :
    """Add a separator."""
    self.interior().grid_rowconfigure(self._varsdict['cur_row'], weight=1)
    
    separator = Tkinter.Frame(self.interior(), height=2, bd=1, relief='sunken')
    separator.grid(row=self._varsdict['cur_row'],
                   column=0,
                   padx=3,
                   pady=3,
                   sticky='nwe')

    self._varsdict['cur_row'] += 1
    

class MoleculeThumbnailWidget(BaseWidget, Tkinter.Frame) :
  """Small frame for viewing a molecule.

  The widget is made up of a Molecule menu at the top, a 3D render widget
  and a check box. The contents of the menu reflects the data which
  the molecule possesses.

  The following readable and writable property is exposed :
      checked       -- if the widget is "checked"

  The following read-only properties are exposed :
      molecule      -- molecule
      renderWidget  -- render widget

  """

  def __init__(self, master, mol, **kw) :
    """Constructor of the class.

    Positional arguments :
    master        -- parent widget
    
    Keyword arguments :
    mainApp       -- reference to the main window (default None)
                     if supplied, the Molecule menu is added

    parser        -- parser object (default None)
                     must be supplied if mainApp is not None
    check_command -- called if the status of the check box is changed
                     (default None)
    """
    if not isinstance(mol, molecule.Molecule) :
      raise ConstructorError('Invalid mol argument')

    # validate
    if kw.get('mainApp', None) is not None and kw.get('parser', None) is None :
      raise ConstructorError(
        'The mainApp and parser arguments must be given simultaneously !')

    self.__mol = mol

    Tkinter.Frame.__init__(self, master)
    BaseWidget.__init__(self, **kw)

  def _init_vars(self) :
    """Initialize variables."""
    # size of the render widgets (pixel).
    self._varsdict['SIZE_RENDERWIDGET'] = 150

  def _constructGUI(self) :
    """Construct the GUI of the widget."""
    row = 0
    
    ## menubar at the top
    ## add only if the mainApp is given
    if self._smartdict['mainApp'] is not None :
      self._varsdict['menubar'] = self.__constructMenubar(self)
      self._varsdict['menubar'].grid(row=row, column=0, sticky='w')
      row += 1

    ## molecule widget
    kw = dict(molecule=self.__mol,
              width=self._varsdict['SIZE_RENDERWIDGET'],
              height=self._varsdict['SIZE_RENDERWIDGET'],
              resolution=self._smartdict['resolution'] or \
              resources.NUM_RESOLUTION_VTK,
              molecule_mode=resources.NUM_MODE_STICK,
              rounded_bond=True,
              hydrogen_bond=True,
              atom_labels=False,
              background='#FFFFFF')

    self._varsdict['renderWidget'] = MoleculeRenderWidget(self, **kw)
    self._varsdict['renderWidget'].grid(row=row, column=0,
                                        padx=3, pady=3, sticky='w')
    row += 1

    ## checkpoint with the name
    self._varsdict['var_checkname'] = Tkinter.IntVar()
    
    widget = Tkinter.Checkbutton(self,
                                 text=self.__mol.name,
                                 font=resources.get_font_molecules(self),
                                 variable=self._varsdict['var_checkname'],
                                 command=self._smartdict['check_command'])
    self._varsdict['check_name'] = widget
    self._varsdict['check_name'].grid(row=row, column=0,
                                      padx=3, pady=3, sticky='w')

  def _declare_properties(self) :
    """Declare properties of the widget."""
    self.__class__.molecule = property(fget=self._get_molecule)
    
    self.__class__.renderWidget = property(
      fget=misc.Command(misc.Command.fget_value,
                        self._varsdict['renderWidget']))

    self.__class__.checked = property(fget=self._get_checked,
                                      fset=self._set_checked)

  def __constructMenubar(self, parent) :
    """Construct the menu bar and return it."""    
    menubar = Pmw.MenuBar(parent, hotkeys=False)

    # the only menu
    # fill the menu depending on which properties the molecule has
    menubar.addmenu('Molecule', None, tearoff=False)

    # Information
    menubar.addmenuitem('Molecule',
                        'command',
                         label='Info...',
                         command=self.__info)

    menubar.addmenuitem('Molecule', 'separator')
  
    # Explore - show a molecule window
    menubar.addmenuitem('Molecule',
                        'command',
                         label='Explore...',
                         command=self.__explore)
    # Spectra
    if self.__mol.raman_roa_tensors is not None or \
       self.__mol.ir_vcd_tensors is not None :
      menubar.addcascademenu('Molecule', 'Spectra')

      if self.__mol.raman_roa_tensors is not None :
        menubar.addmenuitem('Spectra',
                            'command',
                            label='Raman / ROA / Degree of circularity',
                            command=self.__spectra_raman_roa_degcirc)

      if self.__mol.ir_vcd_tensors is not None :
        menubar.addmenuitem('Spectra',
                            'command',
                            label='IR / VCD',
                            command=self.__spectra_ir_vcd)
    # GCM / ACP
    if self.__mol.raman_roa_tensors is not None :
      menubar.addmenuitem('Molecule',
                          'command',
                          label='Raman / ROA generation',
                          command=self.__raman_roa_matrices)
      
    menubar.addmenuitem('Molecule', 'separator')

    # Remove - remove oneself from the main application window
    menubar.addmenuitem('Molecule',
                        'command',
                         label='Remove',
                         command=self.__remove)
    
    return menubar

  def __info(self) :
    """Molecule / Info... menu file handler."""
    from pyviblib.gui.dialogs import FileInfoDialog
    
    self.tk.call('update', 'idletasks')
    info_dlg = FileInfoDialog(self, self.__mol, self._smartdict['parser'])
    info_dlg.configure(title = r'Information for "%s"' % self.__mol.name)
    info_dlg.show()

  def __explore(self) :
    """Molecule / Explore command."""
    from pyviblib.gui.windows import MoleculeWindow

    self.tk.call('update', 'idletasks')
    splash = SplashScreen(self, 'Opening %s ...' % self.__mol.name)
    
    MoleculeWindow(self._smartdict['mainApp'],
                   self._smartdict['parser'],
                   molecule=self.__mol,
                   camera=self.renderWidget.camera,
                   size='500x500')
    splash.destroy()

  def __spectra_raman_roa_degcirc(self) :
    """Molecule / Spectra / Raman/ROA/Degree of circularity command."""
    from pyviblib.gui.windows import RamanROADegcircCalcWindow
    
    self.tk.call('update', 'idletasks')
    splash = SplashScreen(self, 'Calculating the Raman/ROA invariants...')
    
    RamanROADegcircCalcWindow(self._smartdict['mainApp'],
                              self.__mol,
                              camera=self.renderWidget.camera)
    splash.destroy()

  def __spectra_ir_vcd(self) :
    """Molecule / Spectra / IR/VCD of circularity command."""
    from pyviblib.gui.windows import IRVCDCalcWindow
    
    self.tk.call('update', 'idletasks')    
    splash = SplashScreen(self, 'Calculating the IR/VCD invariants...')    
    IRVCDCalcWindow(self._smartdict['mainApp'], self.__mol)
    splash.destroy()

  def __raman_roa_matrices(self) :
    """Molecule / GCM / ACP menu command handler."""
    self.tk.call('update', 'idletasks')

    from pyviblib.gui.windows import RamanROAMatricesWindow    
    splash = SplashScreen(self.master,
                          'Calculating the Raman/ROA invariants...')    
    RamanROAMatricesWindow(self._smartdict['mainApp'], self.__mol,
                           vib_no=1,
                           camera=self.renderWidget.camera)
    splash.destroy()
  
  def __remove(self) :
    """Molecule / Remove command."""
    if self in self._smartdict['mainApp']._varsdict['thumbnails'] :
      self._smartdict['mainApp'].remove_thumbnail(self)

  def _get_molecule(obj) :
    """Getter function for the molecule property."""
    return obj.__mol

  _get_molecule = staticmethod(_get_molecule)

  def _set_checked(obj, check) :
    """Setter function for the checked property."""
    obj._varsdict['var_checkname'].set(check)
    if callable(obj.smartdict['check_command']) :
      obj.smartdict['check_command']()

  _set_checked = staticmethod(_set_checked)

  def _get_checked(obj) :
    """Getter function for the checked property."""
    return obj._varsdict['var_checkname'].get()

  _get_checked = staticmethod(_get_checked)
