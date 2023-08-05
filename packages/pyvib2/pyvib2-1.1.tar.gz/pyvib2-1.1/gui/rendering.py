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

"""Module for 3D rendering based on VTK.

The following classes are exported :
    BaseNode             -- base class for 3D objects used in PyVib2
    AtomNode             -- atoms
    BondNode             -- bonds
    VibratingAtomNode    -- vibrational motion on atoms
    TriangleNode         -- triangle
    ScalarSphereNode     -- sphere whose size is dependent on scalar a value
    TextFollowerNode     -- text which follows a camera

The following functions are exported :
    create_sphere()      -- create a sphere
    create_cylinder()    -- create a cylinder
    orient_actor()       -- orientate an actor in a certain direction

"""
__author__ = 'Maxim Fedorovsky'

from math  import pi, acos, sqrt

from numpy import ndarray

import vtk

from pyviblib.molecule        import Atom, Bond
from pyviblib.gui             import resources
from pyviblib.util.pse        import Material
from pyviblib.calc.common     import contract, distance, crossproduct, \
                                     angle_vectors, norm
from pyviblib.util.misc       import SmartDict, color_html_to_RGB
from pyviblib.util.exceptions import InvalidArgumentError, \
                                     ConstructorError

__all__ = ['BaseNode', 'AtomNode', 'BondNode', 'VibratingAtomNode',
           'TriangleNode', 'ScalarSphereNode', 'TextFollowerNode',
           'create_sphere', 'create_cylinder', 'orient_actor']


def create_sphere(r, pos, resolution,
                  start_theta=0., end_theta=360., start_phi=0., end_phi=180.) :
  """Create a sphere.

  Positional arguments :
  r           -- radius
  pos         -- position (null-based array)
  resolution  -- number of points in the longitude and latitude directions

  Keywords arguments :
  start_theta -- the starting longitude angle (default 0.)
  end_theta   -- the ending longitude angle (default 360.)
  start_phi   -- the starting latitude angle (default 0.)
  end_phi     -- the ending latitude angle (default 180.)

  See :
  http://www.vtk.org/doc/nightly/html/classvtkSphereSource.html
  http://www.vtk.org/doc/nightly/html/classvtkPolyDataMapper.html
  http://www.vtk.org/doc/nightly/html/classvtkActor.html

  Return the sphere source and sphere actor.
  
  """
  sphere = vtk.vtkSphereSource()
  sphere.SetRadius(r)
  sphere.SetThetaResolution(resolution)
  sphere.SetPhiResolution(resolution)
  sphere.SetStartTheta(start_theta)
  sphere.SetEndTheta(end_theta)
  sphere.SetStartPhi(start_phi)
  sphere.SetEndPhi(end_phi)

  sphereMapper = vtk.vtkPolyDataMapper()
  sphereMapper.SetInput(sphere.GetOutput())
  actor = vtk.vtkActor()
  actor.SetMapper(sphereMapper)
  actor.SetPosition(tuple(pos))

  return sphere, actor

def create_cylinder(c, r, height, resolution) :
  """Create a cylinder.

  Positional arguments :
  c          -- cylinder center (null-based array)
  r          -- radius
  height     -- height
  resolution -- the number of facets used to define the cylinder

  See :
  http://www.vtk.org/doc/release/4.0/html/classvtkCylinderSource.html
  http://www.vtk.org/doc/nightly/html/classvtkPolyDataMapper.html
  http://www.vtk.org/doc/nightly/html/classvtkActor.html

  Return the cylinder source and cylinder actor.
  
  """
  cylinder = vtk.vtkCylinderSource()
  cylinder.SetResolution(resolution)
  cylinder.SetHeight(height)
  cylinder.SetRadius(r)
  cylinder.SetCenter(tuple(c))

  cylinderMapper = vtk.vtkPolyDataMapper()
  cylinderMapper.SetInput(cylinder.GetOutput())   

  actor = vtk.vtkActor()
  actor.SetMapper(cylinderMapper)
  actor.SetOrigin(c)

  return cylinder, actor

def orient_actor(actor, dir_vector) :
  """Orientate an actor in a cerain direction.

  See :
  http://www.vtk.org/doc/release/4.0/html/classvtkGeneralTransform.html#a8

  Positional arguments :
  dir_vector -- direction (null-based array)
  
  """
  norm_ = norm(dir_vector)
  
  if 0. == norm_ or actor is None :
    return
  
  angle_y = 180. / pi * acos(dir_vector[1] / norm_)

  if 0. == angle_y :
    actor.RotateWXYZ(0., 1., .0, .0)
    
  elif 180. == angle_y :
    actor.RotateWXYZ(180., 1., 0., 0.)

  else :
    actor.RotateWXYZ(angle_y, 
                     dir_vector[2],
                     .0, 
                    -dir_vector[0])

def apply_material(actor, material) :
  """Apply properties of a material to an actor.

  The following properties are set :
  diffuse_color  : diffuse color
  specular_color : specular color
  ambient_color  : ambient color
  
  Positional arguments :
  actor      -- actor
  material   -- element material (pyviblib.util.pse.Material)

  """
  if actor is None or material is None :
    return

  if not isinstance(material, Material) :
    raise InvalidArgumentError('Invalid material argument')

  actor.GetProperty().SetDiffuseColor(material.diffuse_color)
  actor.GetProperty().SetSpecularColor(material.specular_color)
  actor.GetProperty().SetAmbientColor(material.ambient_color)

def transform_cylinder(src, actor, start_coord, end_coord, W, XYZ) :
  """Transform a cylinder.

  Positional arguments :
  src         -- cylinder source
  actor       -- cylinder actor
  start_coord -- coordinates of the start (one-based ndarray)
  end_coord   -- coordinates of the end (one-based ndarray)
  W           -- parameter to RotateWXYZ
  XYZ         -- parameter to RotateWXYZ
  
  """
  src.SetHeight(distance(start_coord, end_coord))
  src.SetCenter(0.5*(start_coord[1:] + end_coord[1:]))
  
  actor.SetOrigin(src.GetCenter())
  actor.RotateWXYZ(W, *XYZ)


class BaseNode(vtk.vtkAssembly) :
  """Base class for 3D objects used in PyVib2.

  The class inherits from the vtk.vtkAssembly class. Since the multiple
  inheritance is not supported by VTK classes, one cannot inherit
  simultaneously from the object class and so, no properties are available.

  See :
  http://www.vtk.org/doc/release/5.0/html/a01164.html
  
  The following public methods are exported :
      pick()            -- pick the node
      unpick()          -- unpick the node
      get_pickable()    -- whether the node can be picked
      set_pickable()    -- set whether the node can be picked
      get_picked()      -- whether the node is picked
      get_highlighted() -- whether the node is highlighted
      set_resolution()  -- set the resolution of the node

  The following functions should be overriden in subclasses :
      pick()
      unpick()
      set_resolution()
      _render()         -- the rendering is performed in this function
      
  """

  def __init__(self, **kw) :
    """Constructor of the class.

    Keyword arguments (common to all nodes) :
    resolution     -- resolution (default resources.NUM_RESOLUTION_VTK)
    color          -- color (default white)
    diffuse_color  -- diffuse color (default white)
    specular_color -- specular color (default white)
    ambient_color  -- ambient color  (default white)
    diffuse        -- diffuse lightning coefficient (default 1.0)
    specular       -- specular lightning coefficient (default 0.1)
    specularPower  -- specular power (default 20)
    ambient        -- ambient lightning coefficient (default 0.)
    transparency   -- transparency (between 0. and 1.)
    
    """
    self.__init_vars(**kw)

    self._render()

  def __init_vars(self, **kw) :
    """Initialize the common properties of all the nodes."""
    defaults = dict(resolution=resources.NUM_RESOLUTION_VTK,
                    color='#FFFFFF',
                    diffuse_color='#FFFFFF',
                    specular_color='#FFFFFF',
                    ambient_color='#FFFFFF',
                    diffuse=1.0,
                    specular=0.8,
                    specularPower=100.,
                    ambient=0.2,
                    transparency=0.)
      
    self._smartdict = SmartDict(defaults)
    self._smartdict.kw = kw

    # picking
    self._actors_picked    = []  
    self._pickable         = True
    self._is_picked        = False
    self._is_highlighted   = False

  def _render(self) :
    """Perform the rendering.
    
    This implementation does nothing.
    Subclasses should override the method.
    
    """
    pass

  def _set_base_properties(self, actor) :
    """Set the common properties of an actor.

    The common properties are :
    diffuse       : diffuse color
    specular      : specular color
    specularPower : specular power
    ambient       : ambient color
    transparency  : transparency

    Positional arguments :
    actor   -- actor
    
    """
    if actor is None :
      return

    actor.GetProperty().SetDiffuse(self._smartdict['diffuse'])
    actor.GetProperty().SetAmbient(self._smartdict['ambient'])
    actor.GetProperty().SetSpecular(self._smartdict['specular'])
    actor.GetProperty().SetSpecularPower(self._smartdict['specularPower'])
    actor.GetProperty().SetOpacity(1.-self._smartdict['transparency'])

    # setting the Phong interpolation
    actor.GetProperty().SetInterpolationToPhong()

  def pick(self) :
    """Pick the node.

    Subclasses should override this function to do something reasonable.
    New actors should be collected to the self.__actors_picked list.
    
    """
    pass

  def unpick(self) :
    """Unpick the node.

    This implementation removes all actors from the self.__actors_picked list.
    
    """
    if self._is_picked and 0 < len(self._actors_picked) :
      for actor in self._actors_picked :
        self.RemovePart(actor)

      del self._actors_picked[:]
    
    self._is_picked      = False
    self._is_highlighted = False

  def get_pickable(self) :
    """Whether the node can be picked."""
    return self._pickable

  def set_pickable(self, value) :
    """Set whether the node can be picked.

    Positional arguments :
    value -- new state

    """
    self._pickable = value

  def get_picked(self) :
    """Whether the node is picked."""
    return self._is_picked

  def get_highlighted(self) :
    """Whether the node is highlighted."""
    return self._is_highlighted

  def set_resolution(self, resolution) :
    """Set the resolution of the node.

    Subclasses should override the function to make something reasonable.

    Positional arguments :
    resolution -- new resolution
    
    """
    pass


class AtomNode(BaseNode) :
  """Class for rendering atoms.

  The following public methods are exported :
      highlight_picked() -- highlight the node
      apply_material()     -- set a new material to the node
      
  """

  def __init__(self, atom, **kw) :
    """Constructor of the class.

    Accepts the common keywords for all nodes, see the constructor of BaseNode.

    Positional arguments :
    atom              -- atom (pyviblib.molecule.Atom)

    Keyword arguments (specific to this class) :
    mode              -- ball & stick or van der Waals
                         one of (resources.NUM_MODE_BALLSTICK,
                         resources.NUM_MODE_VDW)
                         (default resources.NUM_MODE_BALLSTICK)
    color_picked_atom -- color of a picked atom node
                         (default resources.COLOR_PICKED_ATOM)
 
    """
    if not isinstance(atom, Atom) :
      raise ConstructorError('Invalid atom argument')

    self.__atom = atom

    # initialize the base class
    BaseNode.__init__(self, **kw)

  def _render(self) :
    """Render the atom node."""
    # specific property
    self._smartdict['mode'] = resources.NUM_MODE_BALLSTICK

    ## rendering a sphere
    props = self._smartdict

    if resources.NUM_MODE_BALLSTICK == props['mode'] :
      r = self.__atom.element.r_coval * resources.NUM_FACTOR_SPHERE_RADIUS
    else :
      r = self.__atom.element.r_vdw * resources.NUM_FACTOR_SPHERE_RADIUS

    self.__sphere, self.__sphere_actor = create_sphere(r,
                                                       self.__atom.coord[1:],
                                                       props['resolution'])

    # properties
    apply_material(self.__sphere_actor, self.__atom.element.material)
    self._set_base_properties(self.__sphere_actor)
    
    # finally adding the sphere actor to oneself ;)
    self.AddPart(self.__sphere_actor)

  def pick(self) :
    """Pick the atom node.

    Overrides the method of the base class.
    
    Create a nimbus around the atom (25% transparent).
    Nothing is done if the node is not pickable or already picked.
    

    """
    if not self._pickable or self._is_picked :
      return

    # color for the sphere
    self._smartdict['color_picked_atom'] = resources.COLOR_PICKED_ATOM

    ## nimbus
    r = self.__atom.element.r_coval * resources.NUM_FACTOR_SPHERE_RADIUS * 1.4

    self.__sphere_picked, self.__nimbus = \
                          create_sphere(r,
                                        self.__atom.coord[1:],
                                        self._smartdict['resolution'])
    # properties
    self.__nimbus.GetProperty().SetDiffuseColor(
      color_html_to_RGB(self._smartdict['color_picked_atom']))
    
    self._set_base_properties(self.__nimbus)
    self.__nimbus.GetProperty().SetOpacity(0.75)
    
    ## finally adding the actor
    self.AddPart(self.__nimbus)
    self._actors_picked.append(self.__nimbus)

    self._is_picked = True    

  def highlight_picked(self, highlight=True, **kw) :
    """Highlight/unhighlight a picked atom node.

    The color of the picked atom node is set to
    resources.COLOR_HIGHLIGHTED_PICKED_ATOM.
    Nothing is done if the node is not picked.

    Keyword arguments :
    highlight    -- whether to highlight the atom node (default True)
    transparency -- transparency
    
    """
    if self._is_picked and 0 < len(self._actors_picked) :
      if highlight :
        color = resources.COLOR_HIGHLIGHTED_PICKED_ATOM
      else :
        color = self._smartdict['color_picked_atom']

      self._actors_picked[0].GetProperty().SetDiffuseColor(
        color_html_to_RGB(color))

      if kw :
        if 'transparency' in kw :
          self._actors_picked[0].GetProperty().SetOpacity(
            1. - kw['transparency'])

      self._is_highlighted = highlight

  def apply_material(self, material) :
    """Set a new material to the atom node.

    Positional arguments :
    material -- new material (pyviblib.util.pse.Material)
    
    """
    if not isinstance(material, Material) :
      raise InvalidArgumentError('Invalid material argument')

    # first part is the atom actor
    parts = self.GetParts()
    parts.InitTraversal()

    atom_actor = parts.GetNextProp()
    apply_material(atom_actor, material)

  def set_resolution(self, resolution) :
    """Set the resolution of the atom node.

    Overrides the method of the base class.

    Positional arguments :
    resolution -- new theta and phi resolution
    
    """
    if 0 >= resolution :
      raise InvalidArgumentError('Invalid resolution argument')

    # atom
    self.__sphere.SetThetaResolution(resolution)
    self.__sphere.SetPhiResolution(resolution)

    # if the atom is picked
    if self._is_picked :
      self.__sphere_picked.SetThetaResolution(resolution)
      self.__sphere_picked.SetPhiResolution(resolution)

  def set_material(self, material) :
    """Set a new material to the atom node.

    Positional arguments :
    material -- new material (pyviblib.util.pse.Material)
    
    """
    if not isinstance(material, Material) :
      raise InvalidArgumentError('Invalid material argument')

    # first part is the atom actor
    parts = self.GetParts()
    parts.InitTraversal()

    atom_actor = parts.GetNextProp()
    apply_material(atom_actor, material)

      
class BondNode(BaseNode) :
  """Class for rendering bonds.

  The following public methods are exported :
      get_bond()         -- get the bond passed to the constructor
      render_displaced() -- displace the bond node
      
  """

  def __init__(self, bond, **kw) :
    """Constructor of the class.

    Accepts the common keywords for all nodes, see the constructor of BaseNode.

    Positional arguments :
    bond         -- bond (pyviblib.molecule.Bond)

    Keyword arguments (specific to this class) :
    mode         -- one cylinder or two cylinders
                    one of (resources.NUM_MODE_BONDS_MONOLITH_COLOR,
                    resources.NUM_MODE_BONDS_ATOMS_COLOR)
                    (default resources.NUM_MODE_BONDS_ATOMS_COLOR)
    color        -- diffuse color of the bond node if mode is set to
                    resources.NUM_MODE_BONDS_MONOLITH_COLOR
                    (default resources.COLOR_BONDS_DEFAULT)
    rounded_bond -- whether to render hemispheres at the both ends of the
                    bond for a better appearance (default False)

    """
    if not isinstance(bond, Bond) :
      raise ConstructorError('Invalid bond argument')

    self.__bond = bond

    # initialize the base class
    BaseNode.__init__(self, **kw)

  def _render(self) :
    """Render the bond node."""
    # specific property
    self._smartdict['mode']  = resources.NUM_MODE_BONDS_ATOMS_COLOR
    self._smartdict['color'] = resources.COLOR_BONDS_DEFAULT

    # go
    props = self._smartdict
    
    bond = self.__bond
    pos = tuple((bond.atom1.coord[1:] + bond.atom2.coord[1:]) / 2.)
    bond_length = bond.length()

    ## usual bond
    if not bond.is_hydrogen :
      # for efficieny :
      # if the bond has to be rendering with two cylinders
      # but it consists of the same atom type
      # -> render only one cylinder with the atom material
      modified_mode = False
      
      if bond.atom1.element.material == bond.atom2.element.material \
         and resources.NUM_MODE_BONDS_ATOMS_COLOR == props['mode'] :
        modified_mode = True
        props['mode'] = resources.NUM_MODE_BONDS_MONOLITH_COLOR
      
      # null-based radius vector b - a
      r_ab = bond.atom2.coord[1:] - bond.atom1.coord[1:]
      
      self.__last_ab = bond.atom2.coord - bond.atom1.coord

      if (resources.NUM_MODE_BONDS_MONOLITH_COLOR == props['mode']) :

        self.__cylinder, self.__actorCylinder = create_cylinder(
          pos,
          resources.NUM_RADIUS_BONDS,
          bond_length,
          props['resolution'])
        
        orient_actor(self.__actorCylinder, r_ab)

        # properties
        if modified_mode :
          apply_material(self.__actorCylinder, bond.atom1.element.material)
        else :
          self.__actorCylinder.GetProperty().SetDiffuseColor(
            color_html_to_RGB(props['color']))
          
        self._set_base_properties(self.__actorCylinder)

        # finally adding the actor to oneself ;)
        self.AddPart(self.__actorCylinder)

      else :
        ## making two equal cylinders    
        ## atom 1
        pos1 = tuple((bond.atom1.coord[1:] + pos[:]) / 2.)
        
        self.__cylinder1, self.__actorCylinder1 = create_cylinder(
          pos1,
          resources.NUM_RADIUS_BONDS,
          bond_length / 2.,
          props['resolution'])
        
        orient_actor(self.__actorCylinder1, r_ab)

        # properties
        apply_material(self.__actorCylinder1, bond.atom1.element.material)
        self._set_base_properties(self.__actorCylinder1)

        # finally adding the actor to oneself ;)
        self.AddPart(self.__actorCylinder1)
        
        ## atom 2
        pos2 = tuple((bond.atom2.coord[1:] + pos[:]) / 2.)

        self.__cylinder2, self.__actorCylinder2 = create_cylinder(
          pos2,
          resources.NUM_RADIUS_BONDS,
          bond_length / 2.,
          props['resolution'])
        
        orient_actor(self.__actorCylinder2, r_ab)

        # properties
        apply_material(self.__actorCylinder2, bond.atom2.element.material)
        self._set_base_properties(self.__actorCylinder2)

        # finally adding the actor to oneself ;)
        self.AddPart(self.__actorCylinder2)

      ## rendering a rounded bond for the better appearance
      if props['rounded_bond'] and 0. < bond_length :

        src1, actor1 = create_sphere(resources.NUM_RADIUS_BONDS,
                                     bond.atom1.coord[1:],
                                     props['resolution'],
                                     start_theta=0.,
                                     end_theta=180.)

        src2, actor2 = create_sphere(resources.NUM_RADIUS_BONDS,
                                     bond.atom2.coord[1:],
                                     props['resolution'],
                                     start_theta=0.,
                                     end_theta=180.)
        orient_actor(actor1, -r_ab)
        orient_actor(actor2,  r_ab)
        
        # choosing the appropriate material
        self._set_base_properties(actor1)
        self._set_base_properties(actor2)
        
        if (resources.NUM_MODE_BONDS_MONOLITH_COLOR == props['mode']) :
          actor1.GetProperty().SetDiffuseColor(
            color_html_to_RGB(props['color']))
          actor2.GetProperty().SetDiffuseColor(
            color_html_to_RGB(props['color']))

        else :
          apply_material(actor1, bond.atom1.element.material)
          apply_material(actor2, bond.atom2.element.material)
          
        self.AddPart(actor1)
        self.AddPart(actor2)

    ## render a hydrogen bond
    else :
      # number of cylinder pro atom
      N = 7

      # radius vector a-b
      r_ab = bond.atom2.coord[1:] - bond.atom1.coord[1:]

      # radius of each cylinder
      r = resources.NUM_RADIUS_BONDS / 3.

      # length of each of N cylinder
      length_ = bond_length / (4 * N + 1)

      for i in xrange(1, 1 + 2 * N) :
        pos = bond.atom1.coord[1:] + \
              r_ab * float(2 * i - 0.5) / float(4 * N + 1)

        # cylinder
        cyl, actor = create_cylinder(pos, r, length_, props['resolution'])
        orient_actor(actor, r_ab)

        self.AddPart(actor)

        # rounding each cylinder
        pos1 = bond.atom1.coord[1:] + \
               r_ab * float(2 * i - 1) / float(4 * N + 1)
        src1, actor1 = create_sphere(r,
                                     pos1,
                                     props['resolution'],
                                     start_theta=0.,
                                     end_theta=180.)
        
        pos2 = bond.atom1.coord[1:] + r_ab * float(2 * i) / float(4 * N + 1)
        src2, actor2 = create_sphere(r,
                                     pos2,
                                     props['resolution'],
                                     start_theta=0.,
                                     end_theta=180.)

        self._set_base_properties(actor)
        self._set_base_properties(actor1)
        self._set_base_properties(actor2)

        if (resources.NUM_MODE_BONDS_MONOLITH_COLOR == props['mode']) :
          actor .GetProperty().SetDiffuseColor(
            color_html_to_RGB(props['color']))
          actor1.GetProperty().SetDiffuseColor(
            color_html_to_RGB(props['color']))
          actor2.GetProperty().SetDiffuseColor(
            color_html_to_RGB(props['color']))
        else :
          if N >= i :
            mat = bond.atom1.element.material

          else :
            mat = bond.atom2.element.material

          apply_material(actor , mat)
          apply_material(actor1, mat)
          apply_material(actor2, mat)

        orient_actor(actor1, -r_ab)
        orient_actor(actor2,  r_ab)

        self.AddPart(actor1)
        self.AddPart(actor2)

  def get_bond(self) :
    """Return the bond passed to the constructor."""
    return self.__bond

  def render_displaced(self, Lx1, Lx2) :
    """Displace the bond node.

    Called during an animation.
    Nothing is done for a hydrogen bond.

    Positional arguments :
    Lx1 -- displacement from the equilibrium position for the first atom
    Lx2 -- displacement from the equilibrium position for the second atom

    """
    if self.__bond.is_hydrogen :
      return

    # displaced coordinates & bond length
    coord1_ = self.__bond.atom1.coord + Lx1
    coord2_ = self.__bond.atom2.coord + Lx2
    ab      = coord2_ - coord1_

    W   = angle_vectors(ab, self.__last_ab)
    XYZ = crossproduct (self.__last_ab, ab)[1:]

    bond_center = 0.5*(coord1_ + coord2_)

    # one has to recalculate the height of the cylinder(s),
    # its orientation and center/origin
    if resources.NUM_MODE_BONDS_MONOLITH_COLOR == self._smartdict['mode'] :
      transform_cylinder(self.__cylinder,
                         self.__actorCylinder,
                         coord1_,
                         coord2_,
                         W,
                         XYZ)      
    else :     
      # 1
      transform_cylinder(self.__cylinder1,
                         self.__actorCylinder1,
                         coord1_,
                         bond_center,
                         W,
                         XYZ)
      # 2
      transform_cylinder(self.__cylinder2,
                         self.__actorCylinder2,
                         bond_center,
                         coord2_,
                         W,
                         XYZ)
      
    # saving the points
    self.__last_ab = ab

  def set_resolution(self, resolution) :
    """Set the resolution of the bond node.

    Overrides the method of the base class.

    Positional arguments :
    resolution -- new number of facets
    
    """
    if 0 >= resolution :
      raise InvalidArgumentError('Invalid resolution argument')

    # for the usual bond
    if not self.__bond.is_hydrogen :
      if resources.NUM_MODE_BONDS_MONOLITH_COLOR == self._smartdict['mode'] :
        self.__cylinder.SetResolution(resolution)

      else :
        self.__cylinder1.SetResolution(resolution)
        self.__cylinder2.SetResolution(resolution)
        

class VibratingAtomNode(BaseNode) :
  """Class for rendering vibrational motion on atoms.

  The following public methods are exported :
      highlight_picked() -- highlight the node

  """

  def __init__(self, atom, L, freq, **kw) :
    """Constructor of the class.

    Accepts the common keywords for all nodes, see the constructor of BaseNode.

    Positional arguments :
    atom            -- atom (pyviblib.molecule.Atom)
    L               -- excursion (one-based ndarray)
                       shape : (4,)
    freq            -- wavenumber in in cm**(-1)

    Keyword arguments (specific to this class) :
    mode            -- sphere or arrow representation
                       one of
                       (resources.STRING_MODE_VIB_REPRESENTATION_SPHERES,
                       resources.STRING_MODE_VIB_REPRESENTATION_ARROWS)
                       (default first)
    rep_type        -- cartesian or mass-weighted excursions
                       one of (resources.STRING_VIB_ENERGY,
                       STRING_VIB_EXCURSIONS)
                       (no default)
    rep_subtype     -- representation subtype
                       one of (STRING_VIB_ENERGY_VOLUME,
                       STRING_VIB_ENERGY_VOLUME_ZERO_POINT,
                       STRING_VIB_EXCURSIONS_DIAMETER,
                       STRING_VIB_EXCURSIONS_DIAMETER_ZEROPOINT,
                       STRING_VIB_EXCURSIONS_DIAMETER_STANDARD)
                       (no default)
    scale_factor    -- multiply factor for the amplitude of vibrational motion
                       (default 1.)
    color_sphere_1  -- color of the first hemisphere in the sphere mode, i.e.
                       mode = resources.STRING_MODE_VIB_REPRESENTATION_SPHERES
                       (default resources.COLOR_VIB_HEMISPHERE_1)
    color_sphere_2  -- color of the first hemisphere in the sphere mode, i.e.
                       mode == resources.STRING_MODE_VIB_REPRESENTATION_ARROWS
                       (default resources.COLOR_VIB_HEMISPHERE_2)
    color_arrows    -- color of the arrow in the arrow mode, i.e.
                       mode = STRING_MODE_VIB_REPRESENTATION_ARROWS
                       (default resources.COLOR_VIB_REPRESENTATION_ARROWS)
                       
    """
    if not isinstance(atom, Atom) :
      raise ConstructorError('Invalid atom argument')

    self.__atom = atom
    self.__L    = L
    self.__freq = freq

    # initialize the base class
    BaseNode.__init__(self, **kw)

  def _render(self) :
    """Render the vibrational motion."""
    # common properties for all rendering modes
    self._smartdict['mode']         = \
                            resources.STRING_MODE_VIB_REPRESENTATION_SPHERES
    self._smartdict['rep_type']     = resources.STRING_VIB_ENERGY
    self._smartdict['rep_subtype']  = resources.STRING_VIB_ENERGY_VOLUME
    self._smartdict['scale_factor'] = 1.

    if resources.STRING_MODE_VIB_REPRESENTATION_SPHERES == \
       self._smartdict['mode'] :
      self.__render_spheres()
      
    elif resources.STRING_MODE_VIB_REPRESENTATION_ARROWS == \
         self._smartdict['mode'] :
      self.__render_arrows()
      
    else :
      return

  def __render_spheres(self) :
    """Render the hemispheres."""
    # specific properties to the sphere rendering
    self._smartdict['color_sphere_1'] = resources.COLOR_VIB_HEMISPHERE_1
    self._smartdict['color_sphere_2'] = resources.COLOR_VIB_HEMISPHERE_2

    props = self._smartdict
    atom    = self.__atom
    L_displ = self.__L

    # radius
    self.__radius = self.__get_radius()

    # first hemisphere
    self.__sphere1, actor1 = create_sphere(self.__radius, atom.coord[1:],
                                           props['resolution'],
                                           start_theta=0.,
                                           end_theta=180.)

    orient_actor(actor1, L_displ[atom.index, 1:])    

    actor1.GetProperty().SetDiffuseColor(
      color_html_to_RGB(props['color_sphere_1']))
    self._set_base_properties(actor1)

    self.AddPart(actor1)
    
    # second hemisphere
    self.__sphere2, actor2 = create_sphere(self.__radius, atom.coord[1:],
                                           props['resolution'],
                                           start_theta=0.,
                                           end_theta=180.)

    orient_actor(actor2, -L_displ[atom.index, 1:])

    actor2.GetProperty().SetDiffuseColor(
      color_html_to_RGB(props['color_sphere_2']))
    self._set_base_properties(actor2)

    self.AddPart(actor2)

  def __render_arrows(self) :
    """Render the arrow."""
    self._smartdict['color_arrows'] = resources.COLOR_VIB_REPRESENTATION_ARROWS

    props = self._smartdict
    atom    = self.__atom
    L_displ = self.__L
    
    # radius
    self.__radius = self.__get_radius()
    r = self.__radius

    # do nothing on neglegible displacements
    if 1e-5 > r :
      return

    ## rendering an arrow consisting of a cylinder and a cone
    # radius = height of the cylinder + height of the cone
    if r > resources.NUM_HEIGHT_ARROWS_CONES :
      height_cylinder = r - resources.NUM_HEIGHT_ARROWS_CONES
      height_cone     = resources.NUM_HEIGHT_ARROWS_CONES      
    else :
      height_cylinder = 0
      height_cone     = r
    
    amplitude = sqrt(contract(L_displ[atom.index], L_displ[atom.index]))

    # cylinder
    # do not render if the height is null
    if 0 < height_cylinder :
      factor = height_cylinder / amplitude
      cylinder_center = (atom.coord[1] + 0.5 * factor * L_displ[atom.index, 1],
                         atom.coord[2] + 0.5 * factor * L_displ[atom.index, 2],
                         atom.coord[3] + 0.5 * factor * L_displ[atom.index, 3])
    
      self.__cylinder, cylinder_actor = create_cylinder(
        cylinder_center,
        resources.NUM_RADIUS_ARROWS,
        height_cylinder,
        props['resolution'])

      orient_actor(cylinder_actor, L_displ[atom.index, 1:])

      # properties
      cylinder_actor.GetProperty().SetDiffuseColor(
        color_html_to_RGB(props['color_arrows']))
      self._set_base_properties(cylinder_actor)

      self.AddPart(cylinder_actor)

    # cone
    temp = height_cylinder + height_cone / 2.
    cone_center = (atom.coord[1] + L_displ[atom.index, 1]/amplitude * temp,
                   atom.coord[2] + L_displ[atom.index, 2]/amplitude * temp,
                   atom.coord[3] + L_displ[atom.index, 3]/amplitude * temp)
       
    self.__cone = vtk.vtkConeSource()
    self.__cone.SetResolution(props['resolution'])
    self.__cone.SetHeight(height_cone)
    self.__cone.SetRadius(resources.NUM_RADIUS_ARROWS_CONES)
    self.__cone.SetCenter(cone_center)
    self.__cone.SetDirection(L_displ[atom.index, 1:])

    coneMapper = vtk.vtkPolyDataMapper()
    coneMapper.SetInput(self.__cone.GetOutput())   

    cone_actor = vtk.vtkActor()
    cone_actor.SetMapper(coneMapper)
    cone_actor.SetOrigin(cone_center)

    # properties
    cone_actor.GetProperty().SetDiffuseColor(
      color_html_to_RGB(props['color_arrows']))
    self._set_base_properties(cone_actor)

    self.AddPart(cone_actor)

  def __get_radius(self) :
    """Return the radius of the sphere or the arrow."""
    props = self._smartdict
    L_displ = self.__L
    atom    = self.__atom
 
    # the norm
    norm_L_displ = sqrt( contract(L_displ, L_displ) )

    # omega for zero-point modes
    # if the frequency is 0, one deals with translations / rotations
    if 0. == self.__freq :
      omega = 1.
    else :
      omega = 2. * pi * self.__freq


    # define the scale factor for vtk spheres.
    # this take the user supplied scale factor and
    # a constant specific to a visualization type
    sphere_scale_factor = props['scale_factor']
    
    if resources.STRING_VIB_ENERGY == props['rep_type'] :
      if resources.STRING_VIB_ENERGY_VOLUME == props['rep_subtype'] :
        sphere_scale_factor *= 1.

      # for the zero-point representation
      else :
        if 0. == self.__freq :
          sphere_scale_factor = 0.
        else :
          sphere_scale_factor *= 5.

    # excursions
    else :
      if resources.STRING_VIB_EXCURSIONS_DIAMETER == props['rep_subtype'] :
        sphere_scale_factor *= 2.5
        
      elif resources.STRING_VIB_EXCURSIONS_DIAMETER_ZEROPOINT == \
           props['rep_subtype'] :
        # for translations / rotations show nothing
        if 0. == self.__freq :
          sphere_scale_factor = 0.
        else :
          sphere_scale_factor *= 5000.
        
      else :
        sphere_scale_factor *= 250.

    # atom amplitude
    amplitude = sqrt(contract(L_displ[atom.index], L_displ[atom.index]))

    # set radius appropriately
    radius = 1.

    # volume
    if resources.STRING_VIB_ENERGY == props['rep_type'] :
      if resources.STRING_VIB_ENERGY_VOLUME == props['rep_subtype'] :
        # radius ~ amplitude**(2/3)
        radius = pow( ( amplitude ** 2 * 3. / (4. * pi) ), 1./3. )

      else :
        # radius ~ {amplitude/omega}**(2/3)
        radius = pow( ( amplitude ** 2 * 3. / omega / (4. * pi) ), 1./3. )
        
    # excursions
    else :
      if resources.STRING_VIB_EXCURSIONS_DIAMETER == props['rep_subtype'] :
        # radius ~ normalized amplitude Lx
        if 0. != norm_L_displ :
          radius =  ( amplitude / norm_L_displ ) / ( 2. * sqrt(pi) )
        else :
          radius = 0.

      elif resources.STRING_VIB_EXCURSIONS_DIAMETER_ZEROPOINT == \
           props['rep_subtype'] :
        # radius ~ amplitude / sqrt(omega)
        radius =  amplitude / ( 2. * sqrt( omega * pi ) )
      else :
        # radius ~ amplitude
        radius = amplitude / ( 2. * sqrt( pi ) )

    return radius * sphere_scale_factor    

  def pick(self) :
    """Pick the atom node.

    Overrides the method of the base class.
    
    Create a nimbus around the atom (60% transparent).
    Nothing is done if the node is not pickable or already picked.
    
    """
    if not self._pickable or self._is_picked :
      return

    radius = max(
      self.__atom.element.r_coval * resources.NUM_FACTOR_SPHERE_RADIUS,
      self.__radius)
    
    self.__sphere_picked, actor = create_sphere(radius * 1.2,
                                                self.__atom.coord[1:],
                                                self._smartdict['resolution'])

    actor.GetProperty().SetDiffuseColor(
      color_html_to_RGB(resources.COLOR_PICKED_VIBATOM))
    self._set_base_properties(actor)
    actor.GetProperty().SetOpacity(0.40)
    
    self.AddPart(actor)
    self._actors_picked.append(actor)

    #
    self._is_picked = True

  def highlight_picked(self, highlight=True) :
    """Highlight/unhighlight a picked atom node.

    The color of the picked atom node is set to
    resources.COLOR_HIGHLIGHTED_PICKED_ATOM.
    Nothing is done if the node is not picked.

    Keyword arguments :
    highlight    -- whether to highlight the atom node (default True)

    """
    if self._is_picked and 0 < len(self._actors_picked) :
      if highlight :
        color = resources.COLOR_HIGHLIGHTED_PICKED_VIBATOM
        self._is_highlighted = True
      else :
        color = resources.COLOR_PICKED_VIBATOM
        self._is_highlighted = False

      self._actors_picked[0].GetProperty().SetDiffuseColor(
        color_html_to_RGB(color))

      self._is_highlighted = highlight

  def set_resolution(self, resolution) :
    """Set the resolution of the atom node.

    Overrides the method of the base class.

    Positional arguments :
    resolution -- new resolution
                  in the sphere mode : theta and phi resolution
                  in the arrow  mode : number of facets

    """
    if 0 >= resolution :
      raise InvalidArgumentError('Invalid resolution argument')

    if resources.STRING_MODE_VIB_REPRESENTATION_SPHERES == \
       self._smartdict['mode'] :
      self.__sphere1.SetThetaResolution(resolution)
      self.__sphere2.SetPhiResolution(resolution)

    else :
      # cylinder is created if it is really necessary
      if 0 < self.__radius - resources.NUM_HEIGHT_ARROWS_CONES :
        self.__cylinder.SetResolution(resolution)
        
      self.__cone.SetResolution(resolution)

    # if the vibrating atom is picked
    if self._is_picked :
      self.__sphere_picked.SetThetaResolution(resolution)
      self.__sphere_picked.SetPhiResolution(resolution)
    

class TriangleNode(BaseNode) :
  """Rendering a triangle.
  
  """

  def __init__(self, p1, p2, p3, **kw) :
    """Constructor of the class.

    Accepts the common keywords for all nodes, see the constructor of BaseNode.

    Positional arguments :  
    p1 -- coordinates of the first vertex (one-based ndarray)
          shape : (4,)
    p2 -- coordinates of the second vertex (one-based ndarray)
          shape : (4,)
    p3 -- coordinates of the third vertex (one-based ndarray)
          shape : (4,)

    """
    for p in (p1, p2, p3) :
      if not isinstance(p, ndarray) :
        raise ConstructorError('Invalid coordinate of the vertex')
    
    self.__p1 = p1
    self.__p2 = p2
    self.__p3 = p3

    BaseNode.__init__(self, **kw)

  def _render(self) :
    """Render the triangle."""
    # default properties
    self._smartdict['color']        = resources.COLOR_MARKING_TRIANGLE
    self._smartdict['transparency'] = 0.7
    
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(3)
    points.InsertPoint(0, tuple(self.__p1[1:]))
    points.InsertPoint(1, tuple(self.__p2[1:]))
    points.InsertPoint(2, tuple(self.__p3[1:]))
    
    triag_coords = vtk.vtkFloatArray()
    triag_coords.SetNumberOfComponents(3)
    triag_coords.SetNumberOfTuples(3)
    triag_coords.InsertTuple3(0, 1, 1, 1)
    triag_coords.InsertTuple3(1, 2, 2, 2)
    triag_coords.InsertTuple3(2, 3, 3, 3)
    
    triag = vtk.vtkTriangle()
    triag.GetPointIds().SetId(0, 0)
    triag.GetPointIds().SetId(1, 1)
    triag.GetPointIds().SetId(2, 2)
    
    triagGrid = vtk.vtkUnstructuredGrid()
    triagGrid.Allocate(1, 1)
    triagGrid.InsertNextCell(triag.GetCellType(), triag.GetPointIds())
    triagGrid.SetPoints(points)
    triagGrid.GetPointData().SetTCoords(triag_coords)
    
    triagMapper = vtk.vtkDataSetMapper()
    triagMapper.SetInput(triagGrid)
    
    actor = vtk.vtkActor()
    actor.SetMapper(triagMapper)

    actor.GetProperty().SetDiffuseColor(
      color_html_to_RGB(self._smartdict['color']))
    self._set_base_properties(actor)

    self.AddPart(actor)


class ScalarSphereNode(BaseNode) :
  """Sphere whose size is dependent on a scalar value.

  Useful e.g. for representing ACPs and GCPs.

  The following public methods are exported :
      get_radius()  --  get the radius of the sphere
      
  """

  def __init__(self, value, pos, **kw) :
    """Constructor of the class.

    Accepts the common keywords for all nodes, see the constructor of BaseNode.

    Positional arguments :
    value          -- the value
    pos            -- position of the sphere (null-based array)

    Keyword arguments (specific to this class) :
    mode           -- whether the absolute value should be proportional to the
                      surface or to the volume of the sphere
                      one of (resources.NUM_MODE_PROPORTIONAL_TO_VOLUME,
                      resources.NUM_MODE_PROPORTIONAL_TO_SURFACE)
                      (default resources.NUM_MODE_PROPORTIONAL_TO_SURFACE)                    
    scale_factor   -- factor with which the radius is multiplied
                       (default 1.)
    color_positive -- diffuse color of the sphere for positive values
                      (default : red)
    color_negative -- diffuse color of the sphere for negative values
                      (default : yellow)
 
    """
    self.__value = value
    self.__pos   = pos

    BaseNode.__init__(self, **kw)

  def _render(self) :
    """Render the sphere."""
    # do nothing if the value is 0
    if 0. == self.__value :
      self.__r = 0.
      return
    
    # defaults
    self._smartdict['mode'] = resources.NUM_MODE_PROPORTIONAL_TO_SURFACE
    self._smartdict['scale_factor']   = 1.0
    self._smartdict['color_positive'] = '#FF0000'
    self._smartdict['color_negative'] = '#FFFF00'

    # go
    if resources.NUM_MODE_PROPORTIONAL_TO_SURFACE == self._smartdict['mode'] :
      self.__r = sqrt(abs(self.__value)/(4.*pi))

    else :
      self.__r = pow(abs(self.__value)*3./(4.*pi), 1./3.)

    self.__r *= self._smartdict['scale_factor']

    self.__sphere, actor = create_sphere(self.__r, self.__pos,
                                         self._smartdict['resolution'])
    # properties
    if 0. < self.__value :
      color = self._smartdict['color_positive']      
    else :
      color = self._smartdict['color_negative']
      
    actor.GetProperty().SetDiffuseColor(color_html_to_RGB(color))
    self._set_base_properties(actor)
    
    # finally adding the actor to oneself ;)
    self.AddPart(actor)

  def set_resolution(self, resolution) :
    """Set the resolution of the node.

    Overrides the method of the base class.

    Positional arguments :
    resolution -- new theta and phi resolution
    
    """
    if 0 == self.__r :
      return
    
    if 0 >= resolution :
      raise InvalidArgumentError('Invalid resolution argument')

    self.__sphere.SetThetaResolution(resolution)
    self.__sphere.SetPhiResolution(resolution)

  def get_radius(self) :
    """Get the radius of the sphere."""
    return self.__r


class TextFollowerNode(vtk.vtkFollower) :
  """Rendering a text which follows a camera.

  More specifically it will not change its position or scale,
  but it will continually update its orientation so that it is right
  side up and facing the camera.

  This class does not inherit from BaseNode.

  See :
  http://www.vtk.org/doc/release/4.0/html/classvtkFollower.html
  
  """

  def __init__(self, text, position, camera, scale=0.1) :
    """Constructor of the class.

    Positional arguments :
    text     -- text
    position -- position of the text
    camera   -- camera to follow

    Keyword arguments :
    scale    -- isotropic scale (default 0.1)
    
    """
    if text is None or position is None or camera is None :
      raise ConstructorError('invalid constructor parameter(s) passed')

    self._render(text, position, camera, scale)

  def _render(self, text, position, camera, scale) :
    """Render a vector text which follows the camera."""
    text_ = vtk.vtkVectorText()
    text_.SetText(text)
    
    textMapper = vtk.vtkPolyDataMapper()
    textMapper.SetInput(text_.GetOutput())

    self.SetMapper(textMapper)
    self.SetPosition(position)
    self.SetScale((scale, scale, scale))

    # the text should be white
    self.GetProperty().SetDiffuseColor((1., 1., 1.))

    self.SetCamera(camera)
