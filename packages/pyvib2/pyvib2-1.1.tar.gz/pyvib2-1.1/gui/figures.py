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

"""Classes for plotting based on Matplotlib.

The following classes are exported :
    BaseFigure                       -- base class for all figures
    BaseSpectrumFigure               -- template spectrum
    SingleMoleculeSpectraFigure      -- spectra of a single molecule
    RamanROADegcircCalcFigure        -- Raman/ROA spectra of a single molecule
    RamanROADegcircCalcMixtureFigure -- Raman/ROA spectra of a mixture
    MultipleSpectraFigure            -- spectra for several molecules
    IRVCDCalcFigure                  -- IR/VCD/g spectra for a single molecule
    PercentageFigure                 -- showing composition as a bar chart

"""
__author__ = 'Maxim Fedorovsky'

import os.path
from   math     import ceil, floor, log10

from numpy import zeros, less, any, arange, ndarray, array, isfinite, all

# matplotlib imports
import matplotlib
from matplotlib import rcParams
from matplotlib.figure        import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker        import MultipleLocator, LinearLocator, \
                                     FormatStrFormatter
from matplotlib.artist        import setp
from matplotlib.lines         import Line2D
from matplotlib.patches       import Rectangle

from pyviblib.molecule        import Molecule
from pyviblib.util.misc       import SmartDict, ps2pdf, Command
from pyviblib.gui             import resources
from pyviblib.calc.spectra    import fit_raman_roa, stick_raman_roa, \
                                     X_PEAK_INTERVAL
from pyviblib.calc.common     import savitzky_golay
from pyviblib.util.constants  import INCH2CM
from pyviblib.util.exceptions import ConstructorError, InvalidArgumentError

__all__ = ['BaseFigure', 'BaseSpectrumFigure',
           'RamanROADegcircCalcFigure', 'RamanROADegcircCalcMixtureFigure',
           'SingleMoleculeSpectraFigure', 'MultipleSpectraFigure',
           'IRVCDCalcFigure', 'PercentageFigure']


def init_matplotlib() :
  """Override some defaults of Matplotlib."""  
  matplotlib.use('TkAgg')
  rcParams['numerix'] = 'numpy'
  rcParams['ps.papersize']  = 'A4'

  # using Arial if possible
  rcParams['font.family'] = 'sans-serif'

  if not isinstance(rcParams['font.sans-serif'], list) :
    rcParams['font.sans-serif'] = 'sans-serif'

  else :
    if 'Arial' in rcParams['font.sans-serif'] :
      rcParams['font.sans-serif'].remove('Arial')

    rcParams['font.sans-serif'].insert(0, 'Arial')

  # ticks looking outside
  rcParams['xtick.direction']  = 'out'
  rcParams['xtick.major.size'] = 8
  rcParams['xtick.minor.size'] = 4
  
  rcParams['ytick.direction'] = 'out'
  rcParams['ytick.major.size'] = 8
  rcParams['ytick.minor.size'] = 4

def plot_sticks(ax, X, Y, **kw) :
  """Plot a stick spectrum.

  Positional arguments :
  X          -- x data
  Y          -- y data

  Keyword arguments :
  barchart   -- make a bar chart, otherwise a stem plot (default bar chart)
  width      -- width of a single bar (default 0.8)
  color      -- color of a single bar (default 'black')
  linefmt    -- vertical line specifier (default 'k-')
  markerfmt  -- marker specifier (default 'ko')
  basefmt    -- base line specifier (default 'k-')
  mark_stick -- one-based index of the stick to mark (default None)
  mark_color -- marking color (default 'red')
  
  """
  sd = SmartDict(kw=kw)

  ## defaults
  sd['barchart']   = True
  # for a bar chart
  sd['width']      =   0.8
  sd['color']      =   'k'
  # for a stem spectrum
  sd['linefmt']    =   'k-'
  sd['markerfmt']  =   'ko'
  sd['basefmt']    =   'k-'
  # marking a stick
  sd['mark_stick'] = None
  sd['mark_color'] = 'red'

  # replacing all infinite values with zeros
  b_inf = isfinite(Y)
  if not all(b_inf) :
    for i in xrange(len(b_inf)) :
      if not b_inf[i] :
        Y[i] = 0.

  if sd['barchart'] :
    # avoid an exception under windows if the x and y error are not given
    err = zeros(X.shape, 'd')
    
    rects = ax.bar(X, Y, bottom=0., width=sd['width'], color=sd['color'],
                   xerr=err,
                   yerr=err,
                   ecolor='w',
                   capsize=0)

    if sd['mark_stick'] is not None :
      rects[sd['mark_stick'] - 1].set_facecolor(sd['mark_color'])

    # set the edge color of the rectangles explicitely
    # otherwise one won't see an effect of color changing
    for i in xrange(len(rects)) :
      if sd['mark_stick'] is not None and 1 + i == sd['mark_stick'] :
        color = sd['mark_color']
      else :
        color = sd['color']
        
      rects[i].set_edgecolor(color)

  else :
    ax.stem(X, Y, linefmt=sd['linefmt'], markerfmt=sd['markerfmt'],
            basefmt=sd['basefmt'])
    

class BaseFigure(Figure, object) :
  """Base class for all figures.

  This class defines a set of protected methods which are called in the
  constructor in the following sequence :
      _init_vars()          -- initialize some variables
      _declare_properties() -- declare properties of the widget
      _bind_events()        -- bind events

  These methods are intended to be overridden in subclasses. The base class
  implementations do *nothing*.

  The following protected instance variables are created :
      _smartdict            -- to store options (pyviblib.util.misc.SmartDict)
      _varsdict             -- to store GUI variables (dictionary)

  The following read-only properties are exposed :
      tk_canvas             -- Tkinter.Canvas to be used in GUI
      settings              -- reference to self._smartdict

  The following public method is exported :
      save()                -- save the figure

  """


  def __init__(self, master, **kw) :
    """Constructor of the class.

    Positional arguments :
    master -- parent widget

    Keyword arguments :
    accepts all keywords arguments of the matplotlib.figure.Figure constructor.
    
    """
    # initialize matplotlib
    init_matplotlib()
    
    # initialize the Figure
    Figure.__init__(self, **self._figure_kw(**kw))

    # create the internal dictionaries
    self._smartdict = SmartDict(kw=kw)
    self._varsdict  = {}

    self._Tk_canvas = FigureCanvasTkAgg(self, master=master)
    self.__declare_base_properties()

    # typical operations
    self._init_vars()
    self._declare_properties()
    self._bind_events()

    # show
    self.tk_canvas.show()

  def _figure_kw(**kw) :
    """Retrieve the keyword arguments for the parent class constructor."""
    if kw is not None :
      figure_kw = {}

      for key in ('figsize', 'dpi', 'facecolor', 'edgecolor',
                  'linewidth', 'frameon', 'subplotpars') :
        if key in kw :
          figure_kw[key] = kw[key]

      return figure_kw
    else :
      return {}

  _figure_kw = staticmethod(_figure_kw)

  def __declare_base_properties(self) :
    """Declare the base properties."""
    # create the Tk canvas (read-only outside of the class)    
    self.__class__.tk_canvas = property(
      fget=Command(Command.fget_attr, '_Tk_canvas'))

    # read-only plot settings
    self.__class__.settings = property(
      fget=Command(Command.fget_attr, '_smartdict'))

  def _init_vars(self) :
    """Initialize some variables.

    Subclasses should override this method.
    
    """
    pass

  def _declare_properties(self) :
    """Declare properties.

    Subclasses should override this method.
    
    """
    pass

  def _bind_events(self) :
    """Bind events.

    Subclasses should override this method.
    
    """
    pass

  def _set_size(self, newsize_inches) :
    """Set the new size of the figure."""
    try :
      self.set_size_inches(newsize_inches)
      
    except AttributeError :
      self.set_figsize_inches(newsize_inches)

  def save(self, filename, **kw) :
    """Save the figure.

    Positional arguments :
    filename           -- file name to save to

    Keyword arguments : 
    dpi                -- resolution in dots per inch (default 150).
    CompatibilityLevel -- PDF compatibility level (default '1.3')
    orientation        -- 'landscape' or 'portrait' (default 'portrait').
    size               -- size in inches to set     (default None)
                          if None, use the current size
    restoresize        -- restore the current size (default True)
    
    """
    if filename is None or 0 == len(filename) :
      raise InvalidArgumentError('Filename must be given')

    # initialize the default values
    smartdict = SmartDict(kw=kw)

    smartdict['dpi']                = 150
    smartdict['CompatibilityLevel'] = '1.3'
    smartdict['orientation']        = 'portrait'
    smartdict['size']               =  None
    smartdict['restoresize']        =  True

    # proceed only if the file is writable
    _f = open(filename, 'w+')
    _f.close()
    
    base, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext not in ('.pdf', '.eps', '.ps', '.png', ) :
      raise InvalidArgumentError('Unsupported file type : %s' % ext[1:])

    # setting the appropriate size
    # saving the old size for the further restoration  
    old_size = self.get_size_inches()

    if smartdict['size'] is not None :
      self._set_size(smartdict['size'])

    # keywords for the saving function
    savefigkw = dict(orientation=smartdict['orientation'],
                     dpi=smartdict['dpi'])

    # for pdf : convert to eps first and finally to pdf
    if '.pdf' == ext :
      # as a first step save to eps, and then to pdf
      epsname = '%s.eps' % base
      self.savefig(epsname, **savefigkw)
      status = ps2pdf(epsname,
                      removesrc=True,
                      CompatibilityLevel=smartdict['CompatibilityLevel'])

      if not status :
        raise RuntimeError(r'Conversion to "%s" failed' % filename)

    # the rest : ps, eps, png
    else :
      self.savefig(filename, **savefigkw)

    # restore the original size if demanded
    if smartdict['restoresize'] :
      self._set_size(old_size)
      

class BaseSpectrumFigure(BaseFigure) :
  """Template spectrum.

  The plotting region is be defined in the class.

  The following readable and writable properties are exposed :
      canvas_changed                -- canvas state
      xlim                          -- region of wavenumbers

  The following public methods are exposed :
      get_spectra_axes()            -- get a reference to spectra axes
      restore_last_zoom()           -- restore the last plotting region
      save()                        -- save the figure
  
  """

  ## Names of the three axes
  THREE_AXES_NAMES = ('bottom', 'middle', 'top')
  
  ## Size of the plotting area in inches
  FIGSIZE_DEFAULT = (20./INCH2CM, 18./INCH2CM)

  ## A4 size
  FIGSIZE_A4 = (19.72/INCH2CM, 28.41/INCH2CM)
  
  ## Spectra facecolor (background)
  FACECOLOR = 'white'

  ## Spectra edgecolor (foreground)
  EDGECOLOR = 'black'

  ## Linewidth of the figure
  LINEWIDTH = 1.0

  ## Width of the bounding axes in fracting units
  WIDTH_AXES = 0.775

  ## Height of the bounding axes in fracting units
  HEIGHT_AXES = 0.79

  ## Starting x value of the spectra axes in fracting units
  XSTART_AXES = 0.13

  ## Starting y value of the spectra axes in fracting units
  YSTART_AXES = 0.09

  ## Axes rectangle for a bottom spectrum
  RECT_BOTTOM = (XSTART_AXES, YSTART_AXES, WIDTH_AXES, 0.28)

  ## Axes rectangle for a middle spectrum
  RECT_MIDDLE = (XSTART_AXES, 0.41, WIDTH_AXES, 0.28)

  ## Axes rectange for a top spectrum
  RECT_TOP = (XSTART_AXES, 0.73, WIDTH_AXES, 0.12)
    
  ## Bounding axes rectangle which enclose all other axes
  RECT_BOUNDING = (XSTART_AXES, YSTART_AXES, WIDTH_AXES, HEIGHT_AXES)

  ## TeX source for the axis of wavenumbers
  TEX_AXIS_WAVENUMBER = r'$Wavenumber,\ [\ cm^{-1}\ ]$'

  ## Maximum available range of the wavenumbers
  LIM_AVAIL_WAVENUMBERS = (0., 10000.)

  ## Default values of the wavenumbers
  LIM_WAVENUMBERS = (1900., 100.)

  ## Maximum zooming interval
  MAX_ZOOMING_INTERVAL = 50.

  ## Relative position of a axes label
  POS_AXES_UNITS = (-0.127, 0.5)


  def __init__(self, master, **kw) :
    """Constructor of the class.

    Positional arguments :
    master -- parent widget

    Keyword arguments :
    
    """
    # some defaults
    kw_ = dict(figsize=BaseSpectrumFigure.FIGSIZE_DEFAULT,
               facecolor=BaseSpectrumFigure.FACECOLOR,
               edgecolor=BaseSpectrumFigure.EDGECOLOR,
               linewidth=BaseSpectrumFigure.LINEWIDTH,
               frameon=True)
    kw_.update(kw)
    
    BaseFigure.__init__(self, master, **kw_)
  
  def _init_vars(self) :
    """Initialize variables."""
    # for all axes but bounding and global
    self._varsdict['ar_axes'] = []
    
    # message bar, no default
    self._smartdict['msgBar'] = None

    # spectra representation type, default : Curves
    # see resources.STRINGS_SPECTRA_REPRESENTATION_TYPES
    self._smartdict['representation'] = \
            resources.STRINGS_SPECTRA_REPRESENTATION_TYPES[0]

    # Number of Gauss functions for fitting
    self._smartdict['N_G']   = 6

    # callback when the user want to see a vibration
    # it should accept one argument being the number of vibration to show
    self._smartdict['showvib_callback'] = None

    # resolution of the graph in dpi
    self._smartdict['dpi'] = self.get_dpi()
    
    # pdf compatibility level
    self._smartdict['PDFCompatibilityLevel'] = '1.3'
    
    # Wavenumbers ranges.
    self._smartdict['lim_wavenumbers'] = BaseSpectrumFigure.LIM_WAVENUMBERS

    # Wavenumbers main tick.
    self._smartdict['tick_wavenumbers'] = 200.

    # Minor tick being a fraction (0.,1.) of the major tick
    self._smartdict['minortick_fraction'] = 0.5

    # Major/Minor grids (on by default)
    self._smartdict['majorgrid'] = True
    self._smartdict['minorgrid'] = True

    # Font size of the labels (axes & spectra labels)
    self._smartdict['labels_fontsize'] = 17

    # Font size for the two titles
    self._smartdict['title1_fontsize'] = 21
    self._smartdict['title2_fontsize'] = 16

    # if spectra labels are to be rendered
    self._smartdict['render_spectra_labels'] = True

  def _declare_properties(self) :
    """Declare properties."""
    # canvas state
    self.__class__.canvas_changed = property(
      fget=self._get_canvas_changed,
      fset=self._set_canvas_changed)
    
    # new wavenumbers
    self.__class__.xlim = property(fget=self._get_xlim,
                                   fset=self._set_xlim)

  def _bind_events(self) :
    """Bind events."""
    # binding the mouse events
    self.canvas.mpl_connect('motion_notify_event', self._mouse_motion)
    self.canvas.mpl_connect('button_press_event', self._button_press)
    self.canvas.mpl_connect('button_release_event', self._button_release)

    # restore the original x limits
    self.canvas.mpl_connect('key_press_event', self._key_press)
    self.canvas.mpl_connect('key_release_event', self._key_release)

  def _pre_render(self) :
    """Clear the figure and prepare it for rendering of data."""
    # reinit matplotlib
    init_matplotlib()
    
    # clear the whole graph
    self.clear()

    # releasing the axes array
    del self._varsdict['ar_axes'][:]

    # before the rendering lim_wavenumbers must be set
    self._smartdict.kw['lim_wavenumbers'] = \
      self._smartdict['lim_wavenumbers'] or BaseSpectrumFigure.LIM_WAVENUMBERS

    # bounding axes
    self.__render_bounding_axes()

    # spectra axes
    self._render_axes()

    # global axes
    self.__render_global_axes()

    self._make_axes_aliases()

  def _render_axes(self) :
    """Render the axes.

    Subclasses should override this method.
    
    """
    pass
    
  def __render_bounding_axes(self) :
    """Render the base axes which enclose all the spectra axes :
    bounding and global.

    Title1 and title2 are rendered here.

    Used keywords :
      lim_wavenumbers
      tick_wavenumbers
      minortick_fraction
      majorgrid
      minorgrid
      title1
      title2
      
    """
    rcParams['xtick.direction']  = 'out'
    
    ax = self.add_axes(BaseSpectrumFigure.RECT_BOUNDING,
                       frameon=True,
                       XLim=self._smartdict['lim_wavenumbers'],
                       YLim=(0.,1.),
                       yticks=[])
    self._varsdict['axes_bounding'] = ax
    
    major_locator = MultipleLocator(self._smartdict['tick_wavenumbers'])
    minor_locator = MultipleLocator(self._smartdict['tick_wavenumbers'] *
                                   self._smartdict['minortick_fraction'])
    
    self._varsdict['axes_bounding'].xaxis.set_major_locator(major_locator)
    self._varsdict['axes_bounding'].xaxis.set_minor_locator(minor_locator)

    # no xticks at the bottom of the spectrum (denoted with index 1)
    for tick in self._varsdict['axes_bounding'].xaxis.get_minor_ticks() + \
        self._varsdict['axes_bounding'].xaxis.get_major_ticks():
      #tick.tick1On = False
      tick.tick2On = False

    # grid
    self._varsdict['axes_bounding'].xaxis.grid(
      self._smartdict['majorgrid'], which='major')
    self._varsdict['axes_bounding'].xaxis.grid(
      self._smartdict['minorgrid'], which='minor')
    
    setp(self._varsdict['axes_bounding'].xaxis.get_gridlines(),
         'linestyle', '-')

    # wavenumbers labels
    ax.set_xlabel(BaseSpectrumFigure.TEX_AXIS_WAVENUMBER,
                  fontsize=self._smartdict['labels_fontsize'],
                  fontname='Arial')
    self._varsdict['axes_bounding'] = ax

    ## two titles at the bottom part of the spectrum      
    title = self._varsdict['axes_bounding'].text(
      0.5, 1.10,
      self._smartdict['title1'] or '',
      fontsize=self._smartdict['title1_fontsize'],
      fontweight='bold',
      fontname='Arial',
      horizontalalignment='center',
      verticalalignment='center',
      transform=self._varsdict['axes_bounding'].transAxes)
    
    self._varsdict['title1'] = title
    
    title = self._varsdict['axes_bounding'].text(
      0.5, 1.04,
      self._smartdict['title2'] or '',
      fontsize=self._smartdict['title2_fontsize'],
      fontname='Arial',
      horizontalalignment='center',
      verticalalignment='center',
      transform=self._varsdict['axes_bounding'].transAxes)
    
    self._varsdict['title2'] = title

  def __render_global_axes(self) :
    """Render the invisible global axes.

    Purpose : to track down the mouse position in fraction units and
    spectra labels.
    
    """
    # invisible global axes occupying the whole plottable area
    self._varsdict['axes_global'] = self.add_axes((0., 0., 1., 1.),
                                                  frameon=False,
                                                  XLim=(0., 1.),
                                                  YLim=(0., 1.))
    self._varsdict['axes_global'].xaxis.set_visible(False)
    self._varsdict['axes_global'].yaxis.set_visible(False)

    # render spectra labels if 3-axes are set
    if 'axes_bottom' in self._varsdict :
      labels_kw = dict(fontsize=self._smartdict['labels_fontsize'],
                       fontweight='bold',
                       fontname='Arial')
      
      # coordinates of the labels in fraction units
      xstart_labels_global = 0.15
      y_labels_global = (0.37, 0.68, 0.83)

      for name, y in zip(BaseSpectrumFigure.THREE_AXES_NAMES,
                         y_labels_global) :
        self._varsdict['label_%s' % name] = \
            self._varsdict['axes_global'].text(xstart_labels_global,
                                               y,
                                               '',
                                               **labels_kw)
        
  def _render_three_axes(self) :
    """Render three axes : bottom, middle, top.

    Used keywords :
      lim_wavenumbers
      tick_wavenumbers
      minortick_fraction
      majorgrid
      minorgrid
      labels_fontsize
      title1
      title2
      
    """
    axes_rects = (BaseSpectrumFigure.RECT_BOTTOM,
                  BaseSpectrumFigure.RECT_MIDDLE,
                  BaseSpectrumFigure.RECT_TOP)

    # for y axes
    formatter = FormatStrFormatter('%.2f')

    for name, rect in zip(BaseSpectrumFigure.THREE_AXES_NAMES, axes_rects) :
      ax = self.add_axes(rect,
                         frameon=False,
                         sharex=self._varsdict['axes_bounding'])
      self._varsdict['axes_%s' % name] = ax
      self._varsdict['axes_%s' % name].xaxis.set_visible(False)
      self._varsdict['axes_%s' % name].yaxis.set_major_formatter(formatter)

      # saving the rectangle
      self._varsdict['axes_%s' % name].rect = rect

      # saving in the array
      self._varsdict['ar_axes'].append(self._varsdict['axes_%s' % name])
      
    # add a dick line separating the top and middle spectra
    line = Line2D(BaseSpectrumFigure.LIM_AVAIL_WAVENUMBERS,
                  (-1., -1.),
                  color=BaseSpectrumFigure.EDGECOLOR,
                  linewidth=2.)
    self._varsdict['axes_top'].add_line(line)

  def _make_axes_aliases(self) :
    """Define some aliases for axes."""
    pass

  def _redraw(self) :
    """Redraw the canvas and save the of the bounding axes."""
    if 'text_hint' in self._varsdict :
      self._varsdict['text_hint'].set_text('')

    self.canvas.draw()
    self._varsdict['default_canvas_state'] = self.canvas.copy_from_bbox(
      self._varsdict['axes_bounding'].bbox)
    self.canvas_changed = False

  def _mouse_motion(self, event) :
    """Mouse motion.

    Override in a subclass if *really* necessary.
    
    """
    x, y = event.xdata, event.ydata

    ## repaint canvas if requested
    ## should be done before any processing occurs
    if self.canvas_changed :
      self._redraw()
    
    ## if the mouse pointer is outside of the spectrum region - do nothing
    if not self._axes_contains(x, y) :
      # clean the message bar
      self._set_message()

      # clean the hint text
      if 'text_hint' in self._varsdict :
        self._varsdict['text_hint'].set_text('')

      # clean the canvas
      if 'default_canvas_state' in self._varsdict :
        self.canvas.restore_region(self._varsdict['default_canvas_state'])
        self.canvas.blit(self._varsdict['axes_bounding'].bbox)
        
      return

    ## zoom - draw a rectangle
    if 'do_drawrect' in self._varsdict and self._varsdict['do_drawrect'] :
      self.canvas.restore_region(self._varsdict['default_canvas_state'])

      bounds = self._calc_bounds(self._varsdict['startcoords'][0],
                                 self._varsdict['startcoords'][1], x, y)
      self._varsdict['rect_zoom'].set_bounds(*bounds)
      
      self._varsdict['axes_bounding'].draw_artist(self._varsdict['rect_zoom'])
      self.canvas.blit(self._varsdict['axes_bounding'].bbox)

      # showing the info about zooming rectangle
      freq_start = self._x_to_freq(bounds[0])
      freq_end   = self._x_to_freq(bounds[0] + bounds[2])

      self._set_message('Zoom from %.0f to %.0f cm**(-1)' % \
                        (freq_start, freq_end))
        
    ## show the information
    else :
      
      # one should resave the canvas state after each plotting !
      if 'default_canvas_state' not in self._varsdict or self.canvas_changed :
        self._redraw()

      # calling the class implementation :)
      hint_text, msgbar_text = self._gen_help_texts(x, y)

      # context sensitive hint text
      if 'text_hint' not in self._varsdict :
        text = self._varsdict['axes_global'].text(0, 0, '',
                                                  color='red',
                                                  fontname='Arial',
                                                  fontweight='bold',
                                                  animated=True)
        self._varsdict['text_hint'] = text

      self._varsdict['text_hint'].set_x(x)
      self._varsdict['text_hint'].set_y(y)

      self.canvas.restore_region(self._varsdict['default_canvas_state'])
      self._varsdict['text_hint'].set_text(hint_text or '')
      self._varsdict['axes_bounding'].draw_artist(self._varsdict['text_hint'])
      self.canvas.blit(self._varsdict['axes_bounding'].bbox)

      # message bar text
      self._set_message(msgbar_text)

  def _button_press(self, event) :
    """Mouse button pressed on the figure.

    Initiate zooming on a left click.

    Override in a subclass if *really* necessary.
    
    """
    # processing left and right clicks only
    if 1 == event.button or 3 == event.button :
      # allowing only zooming withing the axes
      x = event.x / self.bbox.width()
      y = event.y / self.bbox.height()

      if not self._axes_contains(x, y) :
        return
      
      self._varsdict['do_drawrect'] = True

      # creating a zooming rectangle      
      if 'rect_zoom' not in self._varsdict :        
        self._varsdict['rect_zoom'] = Rectangle((x, y),
                                                0.0, 0.0,
                                                fill=False,
                                                edgecolor='red',
                                                animated=True)
        self._varsdict['axes_global'].add_patch(self._varsdict['rect_zoom'])

      # red - for usual zoom, blue for the both zooms
      self._varsdict['rect_zoom'].set_ec(3 == event.button and 'blue' or 'red')
        
      # saving the start coordinates where the zoom started
      self._varsdict['startcoords'] = (x, y)
      self.canvas.restore_region(self._varsdict['default_canvas_state'])
      self.canvas.blit(self._varsdict['axes_bounding'].bbox)

  def _button_release(self, event) :
    """Mouse button released on the figure.

    Perform zooming here !

    Override in a subclass if *really* necessary.
    
    """
    # processing left and right clicks
    if 1 == event.button or 3 == event.button :
      # coordinates in global axes
      x = event.x / self.bbox.width()
      y = event.y / self.bbox.height()
      
      self._varsdict['do_drawrect'] = False

      # removing the hint text
      if 'text_hint' in self._varsdict :
        self._varsdict['text_hint'].set_text('')

      # cleaning the message bar
      self._set_message()

      # simple left click or zoom
      if 'startcoords' in self._varsdict and \
         self._varsdict['startcoords'] == (x, y) and 1 == event.button :
        self.__do_click(x, y)
        
      else :
        if 'rect_zoom' in self._varsdict :
          l, b, w, h = self._varsdict['rect_zoom'].get_x(), \
                       self._varsdict['rect_zoom'].get_y(), \
                       self._varsdict['rect_zoom'].get_width(), \
                       self._varsdict['rect_zoom'].get_height()

          if 0. < w :
            # saving the previous zoom
            if 1 == event.button or (3 == event.button and 0. < h) :
              if 'cur_zoom_info' in self._varsdict :
                self._varsdict['last_zoom_info'] = \
                          self._varsdict['cur_zoom_info']

            # zooming
            self.__do_zoom(l, b, w, h, 3 == event.button)

  def _key_press(self, event) :
    """Pressed a key on the figure. Override in subclasses."""
    pass

  def _key_release(self, event) :
    """Pressed a key on the figure. Override in subclasses."""
    pass

  def _set_message(self, msg=None) :
    """Set a message to the message bar."""
    if self._smartdict['msgBar'] is not None :
      self._smartdict['msgBar'].message('help', msg or '')

  def _restore_lims(self) :
    """Restore the limits of the wavenumbers x axis to the default range."""
    self.xlim = BaseSpectrumFigure.LIM_WAVENUMBERS

  def _x_to_freq(self, x) :
    """Recalculate the x value (fraction units) to the frequency."""
    lim_wavenumbers = self.xlim
    range_wavenumbers = abs(lim_wavenumbers[0] - lim_wavenumbers[1])
    
    delta = (x - BaseSpectrumFigure.XSTART_AXES) / \
            BaseSpectrumFigure.WIDTH_AXES * range_wavenumbers

    ## for the reversed direction of the x axis
    if lim_wavenumbers[0] > lim_wavenumbers[1] :
      freq = lim_wavenumbers[0] - delta
    else :
      freq = lim_wavenumbers[0] + delta

    return freq

  def _xy_to_local(x, y, ax) :
    """Recalculate x, y in global coords to the local coords of ax."""
    rect  = ax.rect

    # 
    xlim_ = ax.get_xlim()
    ylim_ = ax.get_ylim()
    
    delta_x = (x - rect[0]) / rect[2] * abs(xlim_[1] - xlim_[0])
    delta_y = (y - rect[1]) / rect[3] * abs(ylim_[1] - ylim_[0])

    x_local = (xlim_[0] > xlim_[1]) and xlim_[0] - delta_x or \
              xlim_[0] + delta_x
    y_local = (ylim_[0] > ylim_[1]) and ylim_[0] - delta_y or \
              ylim_[0] + delta_y

    return x_local, y_local

  _xy_to_local = staticmethod(_xy_to_local)
      
  def _gen_help_texts(self, x, y) :
    """Generate the text for the hint and for the message bar.

    Return (hint_text, msgbar_text)

    This implementation does nothing.
    
    """
    return (None, None)

  def _find_point_info(self, freq, thr=None, where=None, x=None, y=None) :
    """Find the number of vibration which wavenumber is closest to a
    given number.

    Keyword arguments :
    thr  --  if set it is the difference between the found vibration
             and freq is bigger than this threshold - return None
    where -- array to look in. Use the internal array of frequencies
             unless specified.
    x, y  -- x, y in fraction units (dummy parameters in this implementation)

    """
    # no pain - no gain
    if where is None :
      return None

    # find the element with the smallest deviation from the given value
    diff_freqs = abs(where - freq)

    min_el = min(diff_freqs)
    p = 1 + diff_freqs.tolist().index(min_el)

    if thr is not None :
      if thr <= abs(where[p-1] - freq) :
        return None
      else :
        return p    
    else :
      return p

  def _axes_contains(self, x, y, ax=None) :
    """Return if a point (x, y in fractional units) is within a given axes.

    Use the bounding axes unless ax given.
    
    """
    if not x and not y :
      return False
      
    ax = ax or self._varsdict['axes_bounding']
    w, h = self.canvas.get_width_height()

    return ax.bbox.contains(x * w, y * h)

  def _find_lim(ydata) :
    """Find the limits for axes where ydata is to be plotted.

    Return a tuple with two numbers being the limits of the axes.
    Should the data contain only positive numbers use 0 as the lower limit.
    
    """
    if ydata is None or 0 == len(ydata) :
      return (-1., 1.)
    
    upper_lim = max(abs(ydata))
    # if there are negative numbers
    if any(less(ydata, 0.)) :
      lower_lim = -upper_lim
    else :
      lower_lim = 0.

    # for the cases where all values are nulls (e.g. if ROA not supplied)
    if 0. == upper_lim and 0. == lower_lim :
      lower_lim = -1.
      upper_lim = 1.

    return (lower_lim, upper_lim)

  _find_lim = staticmethod(_find_lim)

  def _multiply_factor(data) :
    """Return the order to bring the original data to the scale
    between 0.0 and 1.0.

    Example :
        1     -> -1 (divide by 10)
        0.1   ->  1 (multiply with 1)
        0.001 ->  2 (multiply with 100)
        100   -> -3 (divide by 1000)
        
    """
    if data is None or 0 == len(data) :
      return -1
    
    maxval = abs(data).max()
    if 0. == maxval or not isfinite(maxval) :
      return 25
    else :
      return -int(floor(log10(maxval))) - 1

  _multiply_factor = staticmethod(_multiply_factor)

  def _make_yticks(ax, ticks_auto=True, ticks_number=None,
                   ticks_scaling_factor=None) :
    """Make numticks on the y axis of ax.

    Keyword arguments :
    ticks_auto           -- default behaviour,
    ticks_number         -- fixed number of ticks
    ticks_scaling_factor -- fixed scaling factor
    
    """
    if not ticks_auto :
      # check this first :)
      if ticks_number is not None :
        major_locator = LinearLocator(ticks_number)

      elif ticks_scaling_factor is not None :
        major_locator = MultipleLocator(ticks_scaling_factor)

      # nothing to do ?
      else :
        return
    
      ax.yaxis.set_major_locator(major_locator)

  _make_yticks = staticmethod(_make_yticks)

  def _calc_Y_stick(self, lim_wavenumbers, xdata, ydata, where=None) :
    """Calculate the plot data in the stick mode.

    where  -- array to look in.
              Use the internal array of frequencies unless specified.

    Return Y, y_lim
    
    """
    vibno1, vibno2 = self._find_vibnos(lim_wavenumbers, where=where)

    multfactor = self._multiply_factor(ydata[vibno1-1:vibno2])
    
    Y     = pow(10., multfactor) * ydata
    y_lim = self._find_lim(Y[vibno1-1:vibno2])

    return Y, y_lim, multfactor

  def _find_vibnos(self, lim_wavenumbers, where=None) :
    """Find the numbers of vibration within a lim_wavenumbers.
    carefull ! the indices returned are one-based.

    return vibno1, vibno2 where vibno1 < vibno2
    
    """
    vibno1, dummy = self._find_point_info(lim_wavenumbers[0], where=where)
    vibno2, dummy = self._find_point_info(lim_wavenumbers[1], where=where)
    
    if vibno1 > vibno2 :
      vibno1, vibno2 = vibno2, vibno1

    return vibno1, vibno2

  def _adjust_axes_data(self, xdata, ydata,
                        representation, lim_wavenumbers, **kw) :
    """Return Y, y_lim for a given axes.

    Base multfactor is considered to be 10**(-14) by default.

    Positional arguments :
    xdata           -- raw X data
    ydata           -- raw Y data
    representation  -- 0 for fitted, 1 for stick spectra
    
    Keyword arguments :
    limits_auto     -- True/False
    yfrom, yto      -- used if limits_auto is False
    multfactor      -- used if limits_auto is False
    where           -- frequency array where to look
    
    """
    sd = SmartDict(kw=kw)
    
    # manual values
    if not sd['limits_auto'] :
      multfactor = -sd['multfactor']
       
      Y     = pow(10., multfactor) * ydata
      y_lim = (sd['yfrom'], sd['yto'])

    # auto adjusted values
    else :
      # fitted
      if 0 == representation :
        starti = self._find_nearest(xdata, min(lim_wavenumbers))
        endi   = self._find_nearest(xdata, max(lim_wavenumbers))
        
        multfactor = self._multiply_factor(ydata[starti:1+endi])

        Y     = pow(10., multfactor) * ydata
        y_lim = self._find_lim(Y[starti:1+endi])

      # stick
      else :
        Y, y_lim, multfactor = self._calc_Y_stick(lim_wavenumbers,
                                                  xdata, ydata, sd['where'])
        
    return Y, y_lim, multfactor

  def _find_nearest(xdata, x) :
    """Find the index of an element nearest to x."""
    return abs(xdata - x).argmin()

  _find_nearest = staticmethod(_find_nearest)

  def _get_canvas_changed(obj) :
    """Getter function for the canvas_changed property."""
    if 'canvas_changed' in obj._varsdict :
      return obj._varsdict['canvas_changed']
    else :
      return False

  _get_canvas_changed = staticmethod(_get_canvas_changed)

  def _set_canvas_changed(obj, value) :
    """Setter function for the canvas_changed property."""
    obj._varsdict['canvas_changed'] = value

  _set_canvas_changed = staticmethod(_set_canvas_changed)

  def _set_xlim(obj, xlim) :
    """Setter function for the xlim property."""
    obj._smartdict.kw['lim_wavenumbers'] = xlim    
    obj._varsdict['axes_bounding'].set_xlim(xlim)

    # saving the actual info
    if 'cur_zoom_info' not in obj._varsdict :
      obj._varsdict['cur_zoom_info'] = {}
      
    obj._varsdict['cur_zoom_info']['xlim'] = xlim
    obj._redraw()

  _set_xlim = staticmethod(_set_xlim)

  def _calc_bounds(oldl, oldb, tox, toy) :
    """Recalculate the bounds."""
    # x coords
    l = min(oldl, tox)
    w = abs(oldl - tox)

    # y coords
    b = min(oldb, toy)
    h = abs(oldb - toy)

    return l, b, w, h

  _calc_bounds = staticmethod(_calc_bounds)

  def __set_xlim_sync(self, xlim) :
    """Set the xlim for the list of synch figures."""
    # synchronized widgets
    if self._smartdict['sync_zoom_figures'] is not None :
      for fig in self._smartdict['sync_zoom_figures'] :
        fig.xlim = xlim    
        fig.canvas_changed = True

  def _get_xlim(obj) :
    """Getter function for the xlim property."""
    return obj._varsdict['axes_bounding'].get_xlim()

  _get_xlim = staticmethod(_get_xlim)

  def __do_click(self, x, y) :
    """Clicked on a point x, y (in global axes)."""
    # cleaning the canvas
    self.canvas.restore_region(self._varsdict['default_canvas_state'])
    self.canvas.blit(self._varsdict['axes_bounding'].bbox)

    # processing clicks inside of the axes
    if not self._axes_contains(x, y) :
      return

    # go
    freq = self._x_to_freq(x)
    info = self._find_point_info(freq, thr=10., x=x, y=y)

    if info is not None and callable(self._smartdict['showvib_callback']) :
      self._smartdict['showvib_callback'](info)

  def __do_zoom(self, l, b, w, h, zoom_y=False) :
    """Perform the zoom (also in synchronized widgets).

    Positional arguments :
    l      -- left coord of the rectangle
    b      -- bottom coord of the rectangle
    w      -- width of the rectangle
    h      -- height of the rectangle

    Keyword arguments :
    zoom_y -- zoom also in y direction

    Units : bounding axes.
    
    """
    # do nothing if the width of rectangle is 0
    # prevent saving of the hint text
    if 0 == w :
      return

    ## applying zoom
    # do nothing if the interval is smaller than xxx cm**(-1)
    freq_start = self._x_to_freq(l)
    freq_end   = self._x_to_freq(l+w)
    
    if abs(freq_end - freq_start) < BaseSpectrumFigure.MAX_ZOOMING_INTERVAL :
      self._set_message(
        'Zoom interval threshold of %.0f exceeded.' % \
        BaseSpectrumFigure.MAX_ZOOMING_INTERVAL)
      
      self._varsdict['text_hint'].set_text('')
      self.canvas.restore_region(self._varsdict['default_canvas_state'])
      self.canvas.blit(self._varsdict['axes_bounding'].bbox)
      return

    ## saving the info about the zooming point
    ## dictionary : xlim, ylim, ax
    self._varsdict['cur_zoom_info'] = dict()

    ## zooming Y if dragged with the right mouse button
    if zoom_y and 0. < h :
      # the rectangle must be with an axes
      ax_y_zoom = None
      
      for ax in self._varsdict['ar_axes'] :
        if self._axes_contains(l, b, ax) and \
           self._axes_contains(l+w, b+h, ax) :
          ax_y_zoom = ax
          break

      if ax_y_zoom is not None :
        # bottom point
        x1, y1 = self._xy_to_local(l, b, ax_y_zoom)

        # top point
        x2, y2 = self._xy_to_local(l+w, b+h, ax_y_zoom)

        ax_y_zoom.set_ylim((y1, y2))

        self._varsdict['cur_zoom_info']['ylim'] = (y1, y2)
        self._varsdict['cur_zoom_info']['ax']   = ax_y_zoom

    ## zooming X
    lim_wavenumbers = int(freq_start), int(freq_end)
    self.xlim = lim_wavenumbers

    # sync widgets
    self.__set_xlim_sync(lim_wavenumbers)
          
    # finally request the resaving of the canvas
    self.canvas_changed = True

  def _get_order_string(multfactor) :
    """If multfactor is not 0, return 10^{-multfactor}."""
    return 0 != multfactor and '10^{%d}' % -multfactor or ''

  _get_order_string = staticmethod(_get_order_string)

  def get_representation_as_index(repr_string) :
    """Get the representation type (0 - curves, 1 - stick)."""
    if repr_string not in resources.STRINGS_SPECTRA_REPRESENTATION_TYPES :
      raise InvalidArgumentError(
        'Invalid representation type : %s' % repr_string)
    
    return list(resources.STRINGS_SPECTRA_REPRESENTATION_TYPES).index(
      repr_string)

  get_representation_as_index = staticmethod(get_representation_as_index)

  def get_spectra_axes(self, name) :
    """Get a reference of an axes.

    Positional arguments :
    name -- 'axes_%s' % name key should be in the internal dictionary.
    
    """
    entry = 'axes_%s' % name
    
    if entry not in self._varsdict :
      raise InvalidArgumentError('Invalid axes name : %s' % str(name))

    return self._varsdict[entry]

  def restore_last_zoom(self) :
    """Restore the last viewing region."""
    if 'last_zoom_info' not in self._varsdict :
      self._varsdict['last_zoom_info'] = None

    if self._varsdict['last_zoom_info'] is None :
      self._restore_lims()
      
    else :
      # restoring all the local info
      info = self._varsdict['last_zoom_info']

      if 'ylim' in info and 'ax' in info and info['ylim'] is not None \
         and info['ax'] is not None :
        info['ax'].set_ylim(info['ylim'])

        # saving the current state
        self._varsdict['cur_zoom_info']['ylim'] = info['ylim']
        self._varsdict['cur_zoom_info']['ax']   = info['ax']

      if 'xlim' in info and info['xlim'] is not None :
        self.xlim = info['xlim']

    # taking care about the synch widgets
    self.__set_xlim_sync(self.xlim)

  def save(self, filename, size=None, limits='current') :
    """Save the figure.

    Positional arguments :
    filename -- file name to save to

    Keyword arguments :
    size     -- size in inches (default None)
                if None, keep the current size
    limits   -- 'default' - 1900-100
                'current' - do not change
                (default 'current')

    """    
    if limits not in ('default', 'current') :
      raise InvalidArgumentError('Invalid limits parameter : %s' % limits)

    if 'default' == limits :
      self._restore_lims()    
    
    # call the base class function
    BaseFigure.save(self,
                    filename,
                    dpi=self._smartdict['dpi'],
                    CompatibilityLevel=self._smartdict['PDFCompatibilityLevel'],
                    orientation='portrait',
                    size=size,
                    restoresize=True)

    # after saving the canvas has changed
    self.canvas_changed = True


class SingleMoleculeSpectraFigure(BaseSpectrumFigure) :
  """Spectra of a single molecule. The spectra consist of three parts."""

  def __init__(self, master, mol, **kw) :
    """Constructor of the class.

    Positional arguments :
    master -- parent widget
    mol    -- molecule with the normal modes

    Accepts all the keyword arguments of the base class.
    
    """
    if not isinstance(mol, Molecule) or mol.L is None :
      raise ConstructorError('Invalid molecule supplied')

    self._mol = mol
    BaseSpectrumFigure.__init__(self, master, **kw)

  def _render_axes(self) :
    """Always rendering three axes."""
    self._render_three_axes()    

  def _find_point_info(self, freq, thr=None, where=None, x=None, y=None) :
    """Find the number of vibration which wavenumber is closest to a
    given number.

    thr     -> if set it is the difference between the found vibration
               and freq is bigger than this threshold - return None

    where   -> array to look in. Use the internal array of frequencies
               unless specified.
    x, y    -> x, y in fraction units
               (dummy parameters in this implementation)
               
    """
    if where is not None :
      ar = where
    else :
      ar = self._mol.freqs[1:]

    # what spectrum type ?
    spectrum_type = self._get_spectrum_type(x, y)

    # find the element with the smallest deviation from the given value
    diff_freqs = abs(ar - freq)

    min_el = min(diff_freqs)
    p = 1 + diff_freqs.tolist().index(min_el)

    if thr is not None :
      if thr <= abs(ar[p-1] - freq) :
        return (None, None)
      else :
        return (p, spectrum_type)    
    else :
      return (p, spectrum_type)

  def _gen_help_texts(self, x, y) :
    """Generate the text for the hint and for the message bar.

    Return (hint_text, msgbar_text)
    
    """
    freq = self._x_to_freq(x)
    
    p = self._find_point_info(freq, thr=10.)[0]

    # showint just the number of the vibration
    if p is not None :
      hint_text = '%d' % p
    else :
      hint_text = ''

    # message bar text
    if p is not None :
      msgbar_text = 'Vibration %d / %.2f cm**(-1)' % (p, self._mol.freqs[p])
    else :
      msgbar_text = ''

    return (hint_text, msgbar_text)

  def _get_spectrum_type(self, x, y) :
    """Return the type of the spectrum with given mouse coordinates.

    Subclasses should implement the method.
    
    """
    return None
  

class RamanROADegcircCalcFigure(SingleMoleculeSpectraFigure) :
  """Calculated Raman/ROA/Degree of circularity spectra.

  If you want to use Arial fonts, install it : apt-get install msttcorefonts

  The following public method is exported :
      plot_spectra()            -- plot the spectra

  The following static methods are exported :
      get_scattering_as_index() -- get the scattering type
      get_tex_spectrum_label()  -- get the TeX source for labels
      get_tex_spectrum_units()  -- get the TeX source for units
      
  """

  ## Axes names
  AXES_NAMES = resources.STRINGS_VROA_SPECTRA_PREFICES[:3]

  ## TeX source pattern for a degree of circularity spectrum
  TEX_LABEL_DEGCIRC = r'$\it{^RC(%s)}$'

  ## TeX source pattern for a ROA spectrum
  TEX_LABEL_ROASPECTRUM = r'$\it{-\Delta ^{%s}d\sigma(%s)/d\Omega %s}$'

  ## TeX source pattern for a Raman spectrum
  TEX_LABEL_RAMANSPECTRUM = r'$\it{^{%s}d\sigma(%s)/d\Omega %s}$'

  ## TeX source for the axis of a raman or roa spectrum
  TEX_UNITS_RAMANROASPECTRUM = r'$%s {\angstrom}^2 %s/ sr$'
  
  
  def __init__(self, master, mol, **kw) :
    """Constructor of the class.

    Positional arguments :
    master            -- parent widget
    mol               -- molecule

    Keyword arguments :
    sync_zoom_figures -- list of figures to synchronize with (default None)
    
    """
    SingleMoleculeSpectraFigure.__init__(self, master, mol, **kw)

    #self._mol = mol
    self.__raman_roa_tensors = mol.raman_roa_tensors    

  def _init_vars(self) :
    """Initialize variables."""
    BaseSpectrumFigure._init_vars(self)
    
    # scattering type, default : Backward
    # see resources.STRINGS_SCATTERING_TYPES
    self._smartdict['scattering'] = resources.STRINGS_SCATTERING_TYPES[0]

    # Full width at half maximum for the isotropic bandwidth (a2, aG)
    self._smartdict['FWHM_is']   = 3.5

    # Full width at half maximum for the anisotropic bandwidth (b2, b2G, b2A)
    self._smartdict['FWHM_anis'] = 10.

    # Full width at half maximum for the Gaussian instrument profile
    # b = FWHM_inst / (2*sqrt(2*log(2)))
    # see the Haesler's thesis, p. 142, table 10.1
    self._smartdict['FWHM_inst']  = 7.0

    for axes_name in RamanROADegcircCalcFigure.AXES_NAMES[:2] :
      # Auto calculation of the limits
      self._smartdict['%s_limits_auto' % axes_name] = True

      # if auto is turned off
      self._smartdict['%s_from' % axes_name]       = 0.
      self._smartdict['%s_to' % axes_name]         = 1.
      self._smartdict['%s_multfactor' % axes_name] = 0

      # appearance settings : linewidth & color
      self._smartdict['%s_linewidth' % axes_name] = 1.0
      self._smartdict['%s_linecolor' % axes_name] = 'black'

      # ticks properties
      self._smartdict['%s_ticks_auto' % axes_name]           = True
      self._smartdict['%s_ticks_number' % axes_name]         = None
      self._smartdict['%s_ticks_scaling_factor' % axes_name] = None

    ## Degree of circularity axes settings
    # appearance settings : linewidth & color
    self._smartdict['degcirc_linewidth'] = 1.0
    self._smartdict['degcirc_linecolor'] = 'black'


  def _plot_raman_roa(self, axes_name, X, Y,
                      scattering, representation, lim_wavenumbers,
                      labels_fontsize) :
    """Plot a Raman or ROA spectrum.

    axes_name - see RamanROADegcircCalcFigure.AXES_NAMES
    
    """
    ax = self._varsdict['axes_%s' % axes_name]
    
    Y, y_lim, multfactor = self._adjust_axes_data(
      X, Y, representation, lim_wavenumbers,
      limits_auto=self._smartdict['%s_limits_auto' % axes_name],
      yfrom=self._smartdict['%s_from' % axes_name],
      yto=self._smartdict['%s_to' % axes_name],
      multfactor=self._smartdict['%s_multfactor' % axes_name])

    # lower limit of the raman must be 0.
    if 'raman' == axes_name :
      y_lim = (0., y_lim[1])

    # inverting ROA if requested
    if 'roa' == axes_name and self._smartdict['roa_invert'] :
      Y *= -1.
    
    if 0 == representation :
      ax.plot(X, Y,
              '-',
              color=self._smartdict['%s_linecolor' % axes_name],
              linewidth=self._smartdict['%s_linewidth' % axes_name])      
    else :
      line = Line2D(BaseSpectrumFigure.LIM_AVAIL_WAVENUMBERS,
                    (0., 0.),
                    color=RamanROADegcircCalcFigure.EDGECOLOR)
      ax.add_line(line)
      
      plot_sticks(ax, X, Y,
                  barchart=True,
                  color=self._smartdict['%s_linecolor' % axes_name],
                  width=self._smartdict['%s_linewidth' % axes_name]/2.)

    # axes settings
    ax.multfactor = multfactor
    ax.set_ylim(y_lim)

    # y ticks
    self._make_yticks(
      ax,
      ticks_auto=self._smartdict['%s_ticks_auto' % axes_name],
      ticks_number=self._smartdict['%s_ticks_number' % axes_name],
      ticks_scaling_factor=\
      self._smartdict['%s_ticks_scaling_factor' % axes_name]) 

    # units label
    ax.text(BaseSpectrumFigure.POS_AXES_UNITS[0],
            BaseSpectrumFigure.POS_AXES_UNITS[1],
            RamanROADegcircCalcFigure.get_tex_spectrum_units(
              representation, multfactor),
            rotation=90,
            fontsize=labels_fontsize,
            fontname='Arial',
            horizontalalignment='center',
            verticalalignment='center',
            transform=self._varsdict['axes_%s' % axes_name].transAxes)

    # spectrum label
    i = list(RamanROADegcircCalcFigure.AXES_NAMES).index(axes_name)
    self._varsdict['label_%s_spectrum' % axes_name].set_text(
      RamanROADegcircCalcFigure.get_tex_spectrum_label(
        i, scattering, representation))

  def _plot_degcirc(self, X, degcirc_Y, scattering, representation) :
    """Plot the degree of circularity spectrum."""
    # fitted
    if 0 == representation :
      self._varsdict['axes_degcirc'].plot(
        X, degcirc_Y,
        '-',
        color=self._smartdict['degcirc_linecolor'],
        linewidth=self._smartdict['degcirc_linewidth'])
    
    # stick
    else :
      # add a y-line
      line = Line2D(self.LIM_AVAIL_WAVENUMBERS,
                    (0., 0.),
                    color=RamanROADegcircCalcFigure.EDGECOLOR)
      self._varsdict['axes_degcirc'].add_line(line)

      if 2 > scattering :
        plot_sticks(self._varsdict['axes_degcirc'], X, degcirc_Y,
                    barchart=True,
                    color=self._smartdict['degcirc_linecolor'],
                    width=self._smartdict['degcirc_linewidth']/2.)
    
    # add a dick line separating the spectrum
    line = Line2D(self.LIM_AVAIL_WAVENUMBERS,
                  (-1., -1.),
                  color=RamanROADegcircCalcFigure.EDGECOLOR,
                  linewidth=2.)
    self._varsdict['axes_degcirc'].add_line(line)

    # axes settings
    # limits are always from -1. to 1.
    self._varsdict['axes_degcirc'].set_ylim((-1., 1.))

    # formatting
    formatter = FormatStrFormatter('%d')
    self._varsdict['axes_degcirc'].yaxis.set_major_formatter(formatter)
    
    # where are yticks located   
    major_locator = MultipleLocator(1.)
    minor_locator = MultipleLocator(0.5)

    self._varsdict['axes_degcirc'].yaxis.set_major_locator(major_locator)
    self._varsdict['axes_degcirc'].yaxis.set_minor_locator(minor_locator)

    # spectrum label
    self._varsdict['label_degcirc_spectrum'].set_text(
      RamanROADegcircCalcFigure.get_tex_spectrum_label(
        2, scattering, representation))

  def _get_spectrum_type(self, x, y) :
    """Get the type of the spectrum with given mouse coordinates.

    Return None, 'raman', 'roa_forward', 'roa_backward', 'degcirc' etc.
    
    """
    if not self._axes_contains(x, y) :
      return None

    if self._axes_contains(x, y, self._varsdict['axes_raman']) :
      return 'raman'

    elif self._axes_contains(x, y, self._varsdict['axes_degcirc']) :
      return 'degcirc'

    # different roa scattering
    elif self._axes_contains(x, y, self._varsdict['axes_roa']) :
      return 'roa_%s' % self._smartdict['scattering'].lower()

    else :
      return None

  def _gen_help_texts(self, x, y) :
    """Override the base method in order to show also Raman/ROA intensities."""
    freq = self._x_to_freq(x)
    
    p = self._find_point_info(freq, thr=10.)[0]

    # showint just the number of the vibration
    if p is not None :
      hint_text = '%d' % p
    else :
      hint_text = ''

    # message bar text
    if p is not None :
      msgbar_text = 'Vibration %d / %.2f cm**(-1)' % (p, self._mol.freqs[p])

      # intensity
      type_ = self._get_spectrum_type(x, y)
      
      if type_ is not None and 'degcirc' != type_ :
        scat = self.get_scattering_as_index(self._smartdict['scattering'])
        raman, roa = self.__raman_roa_tensors.intensities(
          self._varsdict['J_all'][p - 1], scat)
        
        if 'raman' == type_ :
          str_int = ', I(Raman) = %.2e A**2 / sr' % raman
        else :
          str_int = ', I(ROA) = %.2e A**2 / sr' % roa

        msgbar_text = ''.join((msgbar_text, str_int))
        
    else :
      msgbar_text = ''

    return (hint_text, msgbar_text)    

  def _make_axes_aliases(self) :
    """Define some aliases for axes."""
    for axes_name, id_ in zip(RamanROADegcircCalcFigure.AXES_NAMES,
                             BaseSpectrumFigure.THREE_AXES_NAMES) :
      self._varsdict['axes_%s' % axes_name]           = \
                                self._varsdict['axes_%s' % id_]
      self._varsdict['label_%s_spectrum' % axes_name] = \
                                         self._varsdict['label_%s' % id_]

  def get_scattering_as_index(scat_string) :
    """Get the scattering type as integer.

    Positional arguments :
    scat_string -- one of resources.STRINGS_SCATTERING_TYPES
    
    """
    if scat_string not in resources.STRINGS_SCATTERING_TYPES :
      raise InvalidArgumentError('Invalid scattering type : %s' % scat_string)
    
    return list(resources.STRINGS_SCATTERING_TYPES).index(scat_string)

  get_scattering_as_index = staticmethod(get_scattering_as_index)

  def get_tex_spectrum_label(type_, scattering, representation) :
    """Return the TeX source for the spectra label.

    Positional arguments :
    type_          -- type of the spectrum : 0(raman), 1(roa), 2(degcirc)
    scattering     -- scattering as integer
    representation -- representation as integer
    
    """
    # tex base string for the substituion
    if 0 == type_ :
      tex_base = RamanROADegcircCalcFigure.TEX_LABEL_RAMANSPECTRUM

    elif 1 == type_ :
      tex_base = RamanROADegcircCalcFigure.TEX_LABEL_ROASPECTRUM

    elif 2 == type_ :
      if 2 > scattering :
        tex_base = RamanROADegcircCalcFigure.TEX_LABEL_DEGCIRC
      else :
        tex_base = ''

    else :
      raise InvalidArgumentError('Invalid spectrum type : %s' % type_)

    # arguments for the extrapolation of the tex_base
    args = []
    
    # scattering
    if 0 == scattering :
      if 2 != type_ :
        args.append('n')
        
      args.append(r'\pi')

    elif 1 == scattering :
      if 2 != type_ :
        args.append('n')
        
      args.append(r'0')

    elif 2 == scattering :
      if 2 != type_ :
        args.append(r'perp')
        args.append(r'\pi/2')

    elif 3 == scattering :
      if 2 != type_ :
        args.append(r'par')
        args.append(r'\pi/2')      

    else :
      raise InvalidArgumentError('Invalid scattering type : %s' % scattering)

    # representation
    if 2 != type_ :
      if 0 == representation :
        args.append(r'/d\tilde{\nu}')

      elif 1 == representation :
        args.append('')

      else :
        raise InvalidArgumentError(
          'Invalid representation type : %s' % representation)      

    return tex_base % tuple(args)

  get_tex_spectrum_label = staticmethod(get_tex_spectrum_label)
  
  def get_tex_spectrum_units(representation, multfactor) :
    """Return the TeX source for the units.

    Positional arguments :
    representation -- representation as integer
    multfactor     -- order of magnitude
    
    """
    # units
    if 0 == representation :
      tex_units = 'cm'

    elif 1 == representation :
      tex_units = ''

    else :
      raise InvalidArgumentError(
        'Invalid representation type : %s' % representation)

    multfactor_str = BaseSpectrumFigure._get_order_string(multfactor)
 
    return RamanROADegcircCalcFigure.TEX_UNITS_RAMANROASPECTRUM % \
           (multfactor_str, tex_units)

  get_tex_spectrum_units = staticmethod(get_tex_spectrum_units)
          
  def plot_spectra(self, **kw) :
    """Plot the spectra.

    Keyword arguments :
    scattering        -- resources.STRINGS_SCATTERING_TYPES
                         (default 'Backward')
    representation    -- 'Curves' or 'Stick' (default 'Curves')
    lim_wavenumbers   -- (left_nu, right_nu) ; left_nu > right_nu
                         (default (1900., 100.))
    tick_wavenumbers  -- major tick (default 200.)
    labels_fontsize   -- font size of the axes and spectra labels
                         (default 17)
    N_G               -- number of Gauss functions for fitting
    FWHM_is           -- full width at half maximum for the
                         isotropic bandwidth (a2, aG)
                         (default 3.5)
    FWHM_anis         -- full width at half maximum for the
                         anisotropic bandwidth (b2, b2G, b2A)
                         (default 10.)
    FWHM_inst         -- full width at half maximum for the
                         Gaussian instrument profile
                         (default 7.)
    title1            -- Title at the top of the figure (default '')
    title2            -- Smaller title beneath the title1 (default '')
    
    """
    ## overriding the keywords
    self._smartdict.merge()
    self._smartdict.kw = kw

    ## go
    # rerender the axes
    self._pre_render()

    # making a cache for the invariants
    # if all invariants are null - quit
    if 'J_all' not in self._varsdict :
      self._varsdict['J_all'] = self.__raman_roa_tensors.J_all(
        units='cross-section')

    # spectra types
    scattering     = RamanROADegcircCalcFigure.get_scattering_as_index(
      self._smartdict['scattering'])
    representation = self.get_representation_as_index(
      self._smartdict['representation'])
    
    # fitted
    if 0 == representation :
      X, raman_Y, roa_Y, degcirc_Y = fit_raman_roa(
        self._mol.freqs,
        self._varsdict['J_all'],
        scattering=scattering,
        N_G=self._smartdict['N_G'],
        FWHM_is=self._smartdict['FWHM_is'],
        FWHM_anis=self._smartdict['FWHM_anis'],
        FWHM_inst=self._smartdict['FWHM_inst'])

    # stick
    else :
      X = self._mol.freqs[1:]
      raman_Y, roa_Y, degcirc_Y = stick_raman_roa(scattering,
                                                  self._varsdict['J_all'])

    ## degree of circularity
    self._plot_degcirc(X,
                       degcirc_Y,
                       scattering,
                       representation)
    ## roa spectrum
    self._plot_raman_roa('roa',
                         X,
                         roa_Y,
                         scattering,
                         representation,
                         self._smartdict['lim_wavenumbers'],
                         self._smartdict['labels_fontsize'])
    
    ## raman spectrum
    self._plot_raman_roa('raman',
                         X,
                         raman_Y,
                         scattering,
                         representation,
                         self._smartdict['lim_wavenumbers'],
                         self._smartdict['labels_fontsize'])

    ## 
    self.xlim = self._smartdict['lim_wavenumbers']
    
    ## redrawing the whole figure
    self.canvas.draw()

    ## canvas needs resaving
    self.canvas_changed = True


class RamanROADegcircCalcMixtureFigure(RamanROADegcircCalcFigure) :
  """Calculated Raman/ROA/Degree of circularity spectra of a mixture of
  molecules.

  The following read-only properties are exposed :
      XY_data        -- X and Y for the single molecules

  The following public method is exposed :
      plot_spectra() -- plot the spectra

  """

  def __init__(self, master, mols, composition, **kw) :
    """Constructor of the class.

    Positional arguments :
    master            -- parent widget
    mols              -- list of molecules
    composition       -- composition of the mixture (null-based ndarray)                

    Keyword arguments :
    sync_zoom_figures -- list of figures to synchronize with (default None)

    """
    # checking the validity
    if not isinstance(mols, (tuple, list)) :
      raise ConstructorError('mols must be a tuple or a list of molecules')

    for mol in mols :
      if mol.raman_roa_tensors is None :
        raise ConstructorError('All molecules must have the ROA data')

    if not isinstance(composition, ndarray) or \
       len(composition) != len(mols) :
      raise ConstructorError('Invalid composition array')

    if any(0. > composition) or any(1. < composition) :
      raise InvalidArgumentError(
        'Composition has to have numbers between 0. and 1. inclusively')
    
    # base class
    RamanROADegcircCalcFigure.__init__(self, master, mols[0], **kw)

    self._mols        = mols
    self.__composition = composition

  def _declare_properties(self) :
    """Declare properties."""
    RamanROADegcircCalcFigure._declare_properties(self)
    
    self.__class__.XY_data = property(fget=self._get_XY_data)

  def _gen_help_texts(self, x, y) :
    """Generate the text for the hint and for the message bar.

    Return (hint_text, msgbar_text).

    Overriding the base class function.
    
    """
    freq = self._x_to_freq(x)
    conf_no, p, dummy = self._find_point_info(freq, thr=10.)

    # text hint
    if conf_no is not None and p is not None :
      hint_text = '%d [%d]' % (p, conf_no)

    else :
      hint_text = ''

    # message bar
    if conf_no is not None and p is not None :
      msgbar_text = 'Conformer %d : vibration %d / %.2f cm**(-1)' % \
                    (conf_no, p, self._mols[conf_no-1].freqs[p])

      # intensity
      type_ = self._get_spectrum_type(x, y)
      
      if type_ is not None and 'degcirc' != type_ :
        scat = self.get_scattering_as_index(self._smartdict['scattering'])
        raman, roa = self._mols[conf_no - 1].raman_roa_tensors.intensities(
          self._varsdict['arr_J_all'][conf_no - 1][p - 1], scat)

        # taking into account the composition        
        raman *= self.__composition[conf_no - 1]
        roa *= self.__composition[conf_no - 1]
        
        if 'raman' == type_ :
          str_int = ', I(Raman) = %.2e A**2 / sr' % raman
        else :
          str_int = ', I(ROA) = %.2e A**2 / sr' % roa

        msgbar_text = ''.join((msgbar_text, str_int))
        
    else :
      msgbar_text = ''
      
    return (hint_text, msgbar_text)      

  def _find_point_info(self, freq, thr=None, where=None, x=None, y=None) :
    """Find the number of vibration & conformer which wavenumber is
    closest to a given number.

    thr     ->  if set it is the difference between the found vibration
                and freq is bigger than this threshold - return None

    where   ->  dummy parameter in the implementation of the class.
    x, y    ->  x, y in fraction units
                (dummy parameters in this implementation)

    Return conf_no, p (one-based).
    
    """
    N = len(self._mols)

    mini = zeros(N, 'l')
    minv = zeros(N, 'd')

    for i in xrange(N) :
      abs_delta = abs(self._mols[i].freqs[1:] - freq)
      
      mini[i] = abs_delta.argmin()
      minv[i] = abs_delta[mini[i]]

    conf_no = 1 + minv.argmin()
    p       = 1 + mini[conf_no - 1]

    # what spectrum type ?
    spectrum_type = self._get_spectrum_type(x, y)

    if thr is not None :
      if abs(minv[conf_no - 1]) < thr :
        return conf_no, p, spectrum_type

      else :
        return None, None, None
      
    else :
      return conf_no, p, spectrum_type

  def _calc_Y_stick(self, lim_wavenumbers, xdata, ydata, where=None) :
    """Calculate the plot data in the stick mode.

    where   ->      dummy parameter in this implementation.

    Return Y, y_lim, multfactor
    
    """
    # sorting
    sorted_indices = xdata.argsort()
    x_sorted = xdata[sorted_indices]
    y_sorted = ydata[sorted_indices]

    # interval indices
    ind = abs(x_sorted - lim_wavenumbers[0]).argmin(), \
          abs(x_sorted - lim_wavenumbers[1]).argmin()

    starti, endi = min(ind), max(ind)

    multfactor = self._multiply_factor(y_sorted[starti:1+endi])
    
    Y        = pow(10., multfactor) * ydata
    y_lim    = self._find_lim(pow(10., multfactor) * y_sorted[starti:1+endi])

    return Y, y_lim, multfactor

  def _get_XY_data(obj) :
    """Getter function for the XY_data property."""
    return obj._varsdict['XY_data']

  _get_XY_data = staticmethod(_get_XY_data)

  def plot_spectra(self, **kw) :
    """Plot the spectra of a mixture of the molecules.

    Keyword arguments :
    scattering        -- resources.STRINGS_SCATTERING_TYPES
                         (default 'Backward')
    representation    -- 'Curves' or 'Stick' (default 'Curves')
    lim_wavenumbers   -- (left_nu, right_nu) ; left_nu > right_nu
                         (default (1900., 100.))
    tick_wavenumbers  -- major tick (default 200.)
    labels_fontsize   -- font size of the axes and spectra labels
                         (default 17)
    N_G               -- number of Gauss functions for fitting
    FWHM_is           -- full width at half maximum for the
                         isotropic bandwidth (a2, aG)
                         (default 3.5)
    FWHM_anis         -- full width at half maximum for the
                         anisotropic bandwidth (b2, b2G, b2A)
                         (default 10.)
    FWHM_inst         -- full width at half maximum for the
                         Gaussian instrument profile
                         (default 7.)
    title1            -- Title at the top of the figure (default '')
    title2            -- Smaller title beneath the title1 (default '')

    """
    ## overriding the keywords
    self._smartdict.merge()
    self._smartdict.kw = kw

    ## go
    # rerender the axes
    self._pre_render()

    # spectra types
    scattering     = RamanROADegcircCalcFigure.get_scattering_as_index(
      self._smartdict['scattering'])    
    representation = self.get_representation_as_index(
      self._smartdict['representation'])    

    # calculating all invariants
    # making a cache :)
    if 'arr_J_all' not in self._varsdict :
      self._varsdict['arr_J_all'] = [ mol.raman_roa_tensors.J_all(
        units='cross-section') for mol in self._mols ]

    # XY data for the single conformers
    self._varsdict['XY_data'] = []
    
    # fitted
    if 0 == representation :

      # calculating the fitting interval
      startx = 0.      
      endx   = X_PEAK_INTERVAL + max(
        array([ ceil(mol.freqs[-1]) for mol in self._mols ]))

      X_mix = arange(startx, 1. + endx, 1.)

      raman_Y_mix   = zeros(X_mix.shape, 'd')
      roa_Y_mix     = zeros(X_mix.shape, 'd')
      degcirc_Y_mix = zeros(X_mix.shape, 'd')
      
      for i in xrange(len(self._mols)) :
        # current conformer
        X, raman_Y, roa_Y, degcirc_Y = fit_raman_roa(
          self._mols[i].raman_roa_tensors.freqs,
          self._varsdict['arr_J_all'][i],
          scattering=scattering,
          N_G=self._smartdict['N_G'],
          FWHM_is=self._smartdict['FWHM_is'],
          FWHM_anis=self._smartdict['FWHM_anis'],
          FWHM_inst=self._smartdict['FWHM_inst'],
          startx=startx,
          endx=endx)

        raman_Y_mix   += self.__composition[i] * raman_Y
        roa_Y_mix     += self.__composition[i] * roa_Y
        degcirc_Y_mix += self.__composition[i] * degcirc_Y

        # saving
        self._varsdict['XY_data'].append([X_mix, raman_Y, roa_Y, degcirc_Y])

    # stick
    else :

      # dimension of the final arrays
      N_mix = 0
      for mol in self._mols :
        N_mix += mol.NFreq

      X_mix = zeros(N_mix, 'd')

      raman_Y_mix   = zeros(X_mix.shape, 'd')
      roa_Y_mix     = zeros(X_mix.shape, 'd')
      degcirc_Y_mix = zeros(X_mix.shape, 'd')

      # making an unsorted array
      starti = 0
      for i in xrange(len(self._mols)) :
        mol = self._mols[i]
        
        # single conformer
        X                         = mol.freqs[1:]
        raman_Y, roa_Y, degcirc_Y = stick_raman_roa(
          scattering, self._varsdict['arr_J_all'][i])

        endi = starti + mol.NFreq

        # mixing
        X_mix[starti:endi] = X

        raman_Y_mix[starti:endi]   = self.__composition[i] * raman_Y
        roa_Y_mix[starti:endi]     = self.__composition[i] * roa_Y
        degcirc_Y_mix[starti:endi] = self.__composition[i] * degcirc_Y

        #
        starti += mol.NFreq

        # saving
        self._varsdict['XY_data'].append(
          [mol.freqs[1:], raman_Y, roa_Y, degcirc_Y])
      
    ## degree of circularity
    self._plot_degcirc(X_mix,
                       degcirc_Y_mix,
                       scattering,
                       representation)
    ## roa spectrum
    self._plot_raman_roa('roa',
                         X_mix,
                         roa_Y_mix,
                         scattering,
                         representation,
                         self._smartdict['lim_wavenumbers'],
                         self._smartdict['labels_fontsize'])
    
    ## raman spectrum
    self._plot_raman_roa('raman',
                         X_mix,
                         raman_Y_mix,
                         scattering,
                         representation,
                         self._smartdict['lim_wavenumbers'],
                         self._smartdict['labels_fontsize'])

    ## the axes share the x axis of the raman spectrum
    self.xlim = self._smartdict['lim_wavenumbers']
    
    ## redrawing the whole figure
    self.canvas.draw()

    ## canvas needs resaving
    self.canvas_changed = True
    

class MultipleSpectraFigure(BaseSpectrumFigure) :
  """Plotting spectra of several molecules.

  The following read-only properties are exposed :
      ylim           -- y limits
      multfactor     -- order of magnitude of the y values

  The following public method is exported :
      plot_spectra() -- plot the spectra
      
  """

  ## Upper y coordinate of a first curve in fraction units
  YUPPER_SPECTRUM = BaseSpectrumFigure.YSTART_AXES + \
                    BaseSpectrumFigure.RECT_BOUNDING[3]

  ## Distance between spectra in f.u. of the height of a single spectrum
  DISTANCE_SPECTRUM = 0.20

  ## +- for marking a peak
  X_PEAK_MARK_INTERVAL = 5


  def __init__(self, master, mols, **kw) :
    """Constructor of the class.

    Positional arguments :
    master -- parent widget
    mols   -- list of molecules

    """
    # checking the validity
    if not isinstance(mols, (tuple, list)) :
      raise ConstructorError('mols must be a tuple or a list of molecules')

    for mol in mols :
      if mol.raman_roa_tensors is None :
        raise ConstructorError('All molecules must have the ROA data')

    BaseSpectrumFigure.__init__(self, master, **kw)

    self._mols        = mols
    self.__nspectra = len(mols)

  def _init_vars(self) :
    """
    Set the default values.
    """
    BaseSpectrumFigure._init_vars(self)

    # Copied from RamanROADegcircCalcFigure
    self._smartdict['FWHM_is']   = 3.5
    self._smartdict['FWHM_anis'] = 10.
    self._smartdict['FWHM_inst']  = 7.0
    
    # how to calculare the size of a single spectrum
    self._smartdict['autoresize'] = True
    
    # size of a single spectrum in cm unless the autoresizing used
    self._smartdict['spectrum_size'] = (15.28, 3.00)

    # Automatic limits by default
    self._smartdict['limits_auto'] = True

    # line properties
    self._smartdict['linecolor'] = 'black'
    self._smartdict['linewidth'] = 1.

    # type of the spectra label : None(no label), 0(raman), 1(roa), 2(degcirc)
    self._smartdict['label_type'] = None

    # whether the data are calculated (or experimental)
    self._smartdict['data_calc']  = True

    # only for experimental Raman/ROA spectra : whether they are norm.
    self._smartdict['normalize_energy'] = False

    # conformer labels
    self._smartdict['molecule_labels'] = None

    # ticks properties
    self._smartdict['ticks_auto']           = True
    self._smartdict['ticks_number']         = None
    self._smartdict['ticks_scaling_factor'] = None

  def _declare_properties(self) :
    """Declare preperties."""
    BaseSpectrumFigure._declare_properties(self)
    
    # y limits for all the spectra
    self.__class__.ylim = property(fget=self.__get_ylim)

    # multfactor (10**(-14))
    self.__class__.multfactor = property(fget=self.__get_multfactor)    

  def _render_axes(self) :
    """Render the axes for spectra."""
    w, h = self.get_figwidth(), self.get_figheight()
    
    # the size of a single spectrum
    # depends on if the autoresizing is used
    if self._smartdict['autoresize'] :
      spectrum_width  = BaseSpectrumFigure.WIDTH_AXES
      spectrum_height = \
              (self.YUPPER_SPECTRUM - BaseSpectrumFigure.YSTART_AXES) / \
              (self.__nspectra * (1. + self.DISTANCE_SPECTRUM))
    else :
      spectrum_width  = self._smartdict['spectrum_size'][0] / (INCH2CM * w)
      spectrum_height = self._smartdict['spectrum_size'][1] / (INCH2CM * h)

    # distance between spectra in fraction units
    #dist_spectra = self.DISTANCE_SPECTRUM * spectrum_height

    # format the y axes
    formatter = FormatStrFormatter('%.2f')

    ## adding the spectra axes
    for i in xrange(self.__nspectra) :
      rect_i = self.__get_rect_spectrum(i, spectrum_width, spectrum_height)
      
      ax = self.add_axes(rect_i,
                         sharex=self._varsdict['axes_bounding'],
                         frameon=False)

      # saving the rect
      ax.rect = rect_i
      
      self._varsdict['ar_axes'].append(ax)

      # setting the properties
      ax.xaxis.set_visible(False)
      ax.yaxis.set_major_formatter(formatter)

    # label for all spectra
    kw = dict(rotation=90,
              fontsize=self._smartdict['labels_fontsize'],
              fontname='Arial',
              horizontalalignment='center', verticalalignment='center',
              transform=self._varsdict['axes_bounding'].transAxes)
    
    self._varsdict['label_spectra'] = \
      self._varsdict['axes_bounding'].text(
        BaseSpectrumFigure.POS_AXES_UNITS[0],
        BaseSpectrumFigure.POS_AXES_UNITS[1], '', **kw)

  def _gen_help_texts(self, x, y) :
    """Generate the text for the hint and for the message bar.

    Return (hint_text, msgbar_text).

    Overrides the base class method.
    
    """
    freq = self._x_to_freq(x)
    mol_no, p = self._find_point_info(freq, thr=10., x=x, y=y)

    # text hint
    # showing only the number of vibration
    # since each spectrum contains already a label :)
    if mol_no is not None and p is not None :
      hint_text = '%d' % p

    else :
      hint_text = ''

    # message bar
    # showing the label 
    if mol_no is not None and p is not None :

      # if labels are available
      if self._smartdict['molecule_labels'] is not None :
        msgbar_text = '%s : vibration %d / %.2f cm**(-1)' % \
                      (self._smartdict['molecule_labels'][mol_no-1],
                       p, self._mols[mol_no-1].freqs[p])
      # else show just the number of the spectrum
      else :
        msgbar_text = 'Molecule %d : vibration %d / %.2f cm**(-1)' % \
                      (mol_no, p, self._mols[mol_no-1].freqs[p])

      # intensity (Raman, ROA)
      if self._smartdict['label_type'] in (0, 1) :
        scat = RamanROADegcircCalcFigure.get_scattering_as_index(
          self._smartdict['scattering'])

        mol = self._mols[mol_no-1]        
        J_all = mol.raman_roa_tensors.J_all(units='cross-section')
        raman, roa = mol.raman_roa_tensors.intensities(J_all[p-1], scat)
        
        if 0 == self._smartdict['label_type'] :
          str_int = ', I(Raman) = %.2e A**2 / sr' % raman
        else :
          str_int = ', I(ROA) = %.2e A**2 / sr' % roa

        msgbar_text = ''.join((msgbar_text, str_int))
        
    else :
      msgbar_text = ''
      
    return hint_text, msgbar_text
      
  def _find_point_info(self, freq, thr=None, where=None, x=None, y=None) :
    """Find the information about a given frequency.

    thr     ->  if set it is the difference between the found vibration
                and freq is bigger than this threshold - return None

    where   ->  dummy parameter in the implementation of the class.
    x, y    ->   x and y in fraction units (used to determine the spectrum)

    Return mol_no, p (one-based).
    
    """
    mol_no = None
    
    # over which axes is the mouse pointer if x and y are given
    if x and y :
      for i in xrange(self.__nspectra) :
        if self._axes_contains(x, y, ax=self._varsdict['ar_axes'][i]) :
          mol_no = 1 + i
          break  

    # for the number of the vibration call the implementation
    # of the base class
    p = None

    if mol_no :
      p = BaseSpectrumFigure._find_point_info(
        self, freq, thr=thr, where=self._mols[mol_no-1].freqs[1:])
            
    return mol_no, p

  def _find_vibnos(self, lim_wavenumbers, where=None) :
    """Find the numbers of vibration within a lim_wavenumbers.
    carefull ! the indices returned are one-based

    return vibno1, vibno2 where vibno1 < vibno2
    
    """
    vibno1 = BaseSpectrumFigure._find_point_info(
      self, lim_wavenumbers[0], where=where)
    vibno2 = BaseSpectrumFigure._find_point_info(
      self, lim_wavenumbers[1], where=where)
    
    if vibno1 > vibno2 :
      vibno1, vibno2 = vibno2, vibno1

    return vibno1, vibno2
    
  def __get_rect_spectrum(self, no, spectrum_width, spectrum_height) :
    """Return the bounding rectangle for a spectrum"""
    y = self.YUPPER_SPECTRUM - \
        (1 + no) * spectrum_height * (1. + self.DISTANCE_SPECTRUM)
    rect = (self.XSTART_AXES, y, spectrum_width, spectrum_height)

    return rect

  def __plot_spectrum(self, no, X, Y_, representation,
                      lim_wavenumbers, yfrom, yto, multfactor,
                      label=None, mark_vib=None) :
    """Plot a spectrum with a given number.

    no - null-based index of the spectrum in the axes array.

    Used keywords :
      linecolor
      linewidth
      labels_fontsize
      
    """
    Y, y_lim, dummy = self._adjust_axes_data(
      X, Y_, representation, lim_wavenumbers,
      limits_auto=False,
      yfrom=yfrom,
      yto=yto,
      multfactor=multfactor,
      where=X)
    
    ax = self._varsdict['ar_axes'][no]

    # inverting the sign if requested
    if self._smartdict['invert'] :
      Y *= -1.
    
    if 0 == representation :
      ax.plot(X, Y,
              '-',
              color=self._smartdict['linecolor'],
              linewidth=self._smartdict['linewidth'])

      # marking the peak +- X_PEAK_MARK_INTERVAL cm**(-1)
      if mark_vib is not None :
        freq_int = int(round(self._mols[no].freqs[mark_vib]))

        i_lower = max(1,
                      freq_int - MultipleSpectraFigure.X_PEAK_MARK_INTERVAL+1)
        i_upper = min(X.shape[0],
                      freq_int + MultipleSpectraFigure.X_PEAK_MARK_INTERVAL+1)

        ax.plot(X[i_lower:i_upper], Y[i_lower:i_upper],
                '-',
                color='red',
                linewidth=2.0)
      
    else :
      # add a line
      line = Line2D(self.LIM_AVAIL_WAVENUMBERS,
                    (0., 0.),
                    color=self.EDGECOLOR)
      ax.add_line(line)
  
      plot_sticks(ax, X, Y,
                  barchart=True,
                  color=self._smartdict['linecolor'],
                  width=self._smartdict['linewidth']/2.,
                  mark_stick = mark_vib)

    # label of the spectrum in its left upper corner
    if label is not None :
      ax.text(0.02, 0.95,
              label,
              fontsize=max(12, self._smartdict['labels_fontsize'] - 6),
              fontname='Arial',
              fontweight='bold',
              transform=ax.transAxes)

    # axes settings
    #ax.multfactor = -14 - multfactor
    ax.multfactor = - multfactor
    ax.set_ylim(y_lim)

  def __find_common_limits(self, XY, representation, lim_wavenumbers) :
    """Find yfrom, yto, multfactor appropriate for all spectra.

    XY is a list (length = nspectra) : [ [X1, Y1], ... ]

    multfactor is the power of the units.

    return yfrom, yto, multfactor common for ALL the spectra.
    
    """
    # find a spectrum with the biggest y value
    # it will be used to define the required data
    data = []
    maxima = []
    for d in XY :
      rv = self._adjust_axes_data(d[0], d[1],
                                  representation, lim_wavenumbers,
                                  limits_auto=True, where=d[0])
      maxima.append(max(rv[1]) * pow(10., -rv[2]))
      data.append(rv)

    maxy_i = array(maxima).argmax()

    return data[maxy_i][1][0], data[maxy_i][1][1], -data[maxy_i][2]

  def __get_tex_spectra_label(label_type,
                              scattering, representation, multfactor,
                              data_calc, normalize_energy) :
    """Return the label for *all* the spectra."""
    if data_calc :
      label = RamanROADegcircCalcFigure.get_tex_spectrum_label(
        label_type, scattering, representation)
    else :
      label = RamanROADegcircExpFigure.get_tex_spectrum_label(
        label_type, scattering)

    # Raman and ROA have units
    if 2 != label_type :
      if data_calc :
        units = RamanROADegcircCalcFigure.get_tex_spectrum_units(
          representation, multfactor)
      else :
        units = RamanROADegcircExpFigure.get_tex_spectrum_units(
          multfactor, normalize_energy)
        
      label = ''.join((label[:-1], r',\ [\ ', units[1:-1], r'\ ]$'))

    return label

  __get_tex_spectra_label = staticmethod(__get_tex_spectra_label)

  def __make_degcirc(self) :
    """Adjust the axes for the representation of degree of circularity."""
    if 'ar_axes' in self._varsdict :
      # y ticks
      major_locator = MultipleLocator(1.)
      minor_locator = MultipleLocator(0.5)

      formatter = FormatStrFormatter('%.0f')
      
      for ax in self._varsdict['ar_axes'] :
        # y limits are always from -1. to 1.
        ax.set_ylim((-1., 1.))

        # y ticks
        ax.yaxis.set_major_locator(major_locator)
        ax.yaxis.set_minor_locator(minor_locator)

        # y formatter - no decimal digits
        ax.yaxis.set_major_formatter(formatter)

  def __get_ylim(obj) :
    """Getter function for the ylim property."""
    return obj._varsdict['ar_axes'][-1].get_ylim()

  __get_ylim = staticmethod(__get_ylim)

  def __get_multfactor(obj) :
    """Getter function for the multfactor property."""
    return obj._varsdict['ar_axes'][-1].multfactor

  __get_multfactor = staticmethod(__get_multfactor)

  def plot_spectra(self, XY, **kw) :
    """Plot the spectra.

    Positional arguments :
    XY                   -- [ [X1, Y1], ... ]

    Keyword arguments :
    autoresize       -- if True, the size of a single spectrum is
                        calculated automatically
    spectrum_size    -- (w, h) in cm, used if autoresize is set to False
    label_type       -- type of the spectra label :
                          None - no label
                          0    - raman
                          1    - roa
                          2    - degcirc
    data_calc        -- True for calculated data, False for experimental
                        (default True)
    molecule_labels  -- list of the labels of the subplots
    make_degcirc     -- apply the axis setting of a degree of circularity
                        spectrum
    mark_vibs        -- list of vibrations to be marked
                        (fit : +-5 for each peak, stick : the vibrations)
    normalize_energy -- whether to normalize exp. Raman/ROA to the laser energy
                        (default True)                       
                            
    accepts all the keyword arguments of
    RamanROADegcircCalcFigure.plot_spectra()
    
    """
    if not isinstance(XY, (list, tuple)) or \
       len(XY) != self.__nspectra :
      raise InvalidArgumentError(
        'XY_data must have a dimension of %d' % self.__nspectra)
    
    # overriding the keywords
    self._smartdict.merge()
    self._smartdict.kw = kw

    # prepering for the plotting
    self._pre_render()

    scattering     = RamanROADegcircCalcFigure.get_scattering_as_index(
      self._smartdict['scattering'])
    representation = self.get_representation_as_index(
      self._smartdict['representation'])

    # finding the common limits for all the spectra
    if self._smartdict['limits_auto'] or self._smartdict['make_degcirc'] :
      yfrom, yto, multfactor = self.__find_common_limits(
        XY, representation, self._smartdict['lim_wavenumbers'])

    else :
      yfrom, yto, multfactor = self._smartdict['from'], \
                               self._smartdict['to'], \
                               self._smartdict['multfactor']

    # plotting the spectra with the common limits
    for i in xrange(len(XY)) :
      if self._smartdict['molecule_labels'] is not None :
        label = self._smartdict['molecule_labels'][i]

      else :
        label = None

      # mark vibration ?
      if self._smartdict['mark_vibs'] is not None :
        if i < len(self._smartdict['mark_vibs']) :
          mark_vib = self._smartdict['mark_vibs'][i]

          if mark_vib not in xrange(1, 1 + self._mols[i].NFreq) :
            raise InvalidArgumentError(
              'Invalid vibration number %d for the molecule %d !' % \
              (mark_vib, 1 + i))

      else :
        mark_vib = None
      
      self.__plot_spectrum(i, XY[i][0], XY[i][1], representation,
                           self._smartdict['lim_wavenumbers'],
                           yfrom, yto, multfactor,
                           label=label,
                           mark_vib=mark_vib)

    # resetting limits if necessary
    if self._smartdict['make_degcirc'] :
      self.__make_degcirc()

    # handling the ticks
    for ax in self._varsdict['ar_axes'] :
      self._make_yticks(
        ax,
        ticks_auto=self._smartdict['ticks_auto'],
        ticks_number=self._smartdict['ticks_number'],
        ticks_scaling_factor=self._smartdict['ticks_scaling_factor'])
        
    # setting the label
    if self._smartdict['label_type'] is not None and \
       self._smartdict['render_spectra_labels'] :
      
      spectra_label = self.__get_tex_spectra_label(
        self._smartdict['label_type'],
        scattering, representation, -multfactor,
        self._smartdict['data_calc'], self._smartdict['normalize_energy'])
      
      self._varsdict['label_spectra'].set_text(spectra_label)      
    else :
      self._varsdict['label_spectra'].set_text('')

    self.xlim = self._smartdict['lim_wavenumbers']

    # redrawing the whole figure
    self.canvas.draw()

    # canvas needs resaving
    self.canvas_changed = True


class PercentageFigure(BaseFigure) :
  """Bar chart figure for representing e.g. composition of a mixture."""


  def __init__(self, master, Y, **kw) :
    """Constructor of the class.

    Positional arguments :
    master -- parent widget
    Y      -- null-based ndarray.
    """

    BaseFigure.__init__(self,
                        master,
                        figsize=(10./INCH2CM, 5./INCH2CM),
                        facecolor='white',
                        edgecolor='black',
                        frameon=True,
                        **kw)

    self.__Y = Y
    self.__plot()

  def __plot(self) :
    """Plot a bar chart."""
    # rendering a bar chart
    axes  = self.add_axes((0.1, 0.2, 0.8, 0.6), frame_on=False)
    axes.yaxis.set_visible(False)

    X = arange(1., 1. + len(self.__Y), 1.)
    width = 0.5

    axes.bar(X, self.__Y, width=width, color='k')

    # text over the bars
    y_offset = 2.
    for i in xrange(len(X)) :
      axes.text(X[i] + width/2., y_offset + self.__Y[i],
                '%.0f %%' % self.__Y[i],
                fontname='Arial',
                fontsize=10,
                va='bottom',
                ha='center')

    axes.set_xlim((width, 1. + X[-1]))
    axes.set_ylim((0., 100.))

    axes.set_xticks(X + width/2.)
    axes.set_xticklabels([ '%d' % v for v in X ])

    for tick in axes.xaxis.get_major_ticks() :
      tick.tick1On = False
      tick.tick2On = False

    for label in axes.get_xticklabels() :
      label.set_fontname('Arial')
      label.set_fontweight('bold')
      label.set_fontsize(14)

    # update
    self.canvas.draw()


class IRVCDCalcFigure(SingleMoleculeSpectraFigure) :
  """Calculated IR/VCD/g spectra."""

  ## Axes names
  AXES_NAMES = resources.STRINGS_VROA_SPECTRA_PREFICES[3:]

  ## TeX source pattern for the label of a epsilon spectrum
  TEX_LABEL_EPSILON = r'$\it{\varepsilon}$'

  ## TeX source pattern for the units of a epsilon spectrum
  TEX_UNITS_EPSILON = r'$%s m^2 / mol$'

  ## TeX source pattern for the label of a delta epsilon spectrum
  TEX_LABEL_DEPSILON = r'$\it{\Delta \varepsilon}$'

  ## TeX source pattern for the label of a g spectrum
  TEX_LABEL_G = r'$\it{g} \ \times 10^{%d}$'

  ## TeX source pattern for the label of an integrated epsilon spectrum
  TEX_LABEL_INTEPSILON = r'$\it{A}$'

  ## TeX source pattern for the label of an integrated delta epsilon spectrum
  TEX_LABEL_INTDEPSILON = r'$\it{\Delta A}$'  

  ## TeX source pattern for the units of the integrated absorption coefficients
  TEX_UNITS_INTEPSILON= r'$%s m / mol$'  

  def __init__(self, master, mol, **kw) :
    """Constructor of the class.

    Positional arguments :
    master            -- parent widget
    mol               -- molecule

    Keyword arguments :
    sync_zoom_figures -- list of figures to synchronize with (default None)

    """
    SingleMoleculeSpectraFigure.__init__(self, master, mol, **kw)

    self.__ir_vcd_tensors = mol.ir_vcd_tensors

  def _init_vars(self) :
    """Initialize variables."""
    BaseSpectrumFigure._init_vars(self)

    # Full width at half maximum for the fit
    self._smartdict['FWHM_fit']   = 8.

    # Full width at half maximum for the Gaussian instrument profile
    # b = FWHM_inst / (2*sqrt(2*log(2)))
    # see the Haesler's thesis, p. 142, table 10.1
    self._smartdict['FWHM_inst']  = 10.

    ## Axes settings
    for axes_name in IRVCDCalcFigure.AXES_NAMES :
      # Auto calculation of the limits
      self._smartdict['%s_limits_auto' % axes_name] = True

      # if auto is turned off
      self._smartdict['%s_from' % axes_name]       = 0.
      self._smartdict['%s_to' % axes_name]         = 1.
      self._smartdict['%s_multfactor' % axes_name] = 0

      # appearance settings : linewidth & color
      self._smartdict['%s_linewidth' % axes_name] = 1.0
      self._smartdict['%s_linecolor' % axes_name] = 'black'

      # ticks properties
      self._smartdict['%s_ticks_auto' % axes_name]           = True
      self._smartdict['%s_ticks_number' % axes_name]         = None
      self._smartdict['%s_ticks_scaling_factor' % axes_name] = None

  def _get_spectrum_type(self, x, y) :
    """Get the type of the spectrum with given mouse coordinates.

    Return None, 'ir', 'vcd', 'g'
    
    """
    if not self._axes_contains(x, y) :
      return None

    if self._axes_contains(x, y, self._varsdict['axes_bottom']) :
      return 'ir'

    elif self._axes_contains(x, y, self._varsdict['axes_top']) :
      return 'g'

    elif self._axes_contains(x, y, self._varsdict['axes_middle']) :
      return 'vcd'

    else :
      return None

  def _make_axes_aliases(self) :
    """Make aliases."""
    for axes_name, id_ in zip(IRVCDCalcFigure.AXES_NAMES,
                             BaseSpectrumFigure.THREE_AXES_NAMES) :
      self._varsdict['axes_%s' % axes_name]  = self._varsdict['axes_%s' % id_]
      self._varsdict['label_%s' % axes_name] = self._varsdict['label_%s' % id_]

  def __plot_spectrum(self, axes_name, label_type, X, Y, representation,
                      lim_wavenumbers, labels_fontsize) :
    """Plot the epsilon or IR spectrum.

    axes_name  - IRVCDCalcFigure.AXES_NAMES
    label_type - IRVCDCalcFigure.AXES_NAMES + (int_epsilon, int_depsilon)
    
    """
    # keywords for adjusting data
    kw = dict()

    for prop in ('limits_auto', 'from', 'to', 'multfactor') :      
      if prop in ('from', 'to') :
        id_ = 'y%s' % prop
      else :
        id_ = prop
        
      kw[id_] = self._smartdict['%s_%s' % (axes_name, prop)]
    
    Y, y_lim, multfactor = self._adjust_axes_data(
      X, Y, representation, lim_wavenumbers, **kw)
    ax = self._varsdict['axes_%s' % axes_name]

    # lower limit of the IR spectrum must be 0.
    if 'ir' == axes_name :
      y_lim = (0., y_lim[1])
    
    if 0 == representation :
      ax.plot(X, Y,
              '-',
              color=self._smartdict['%s_linecolor' % axes_name],
              linewidth=self._smartdict['%s_linewidth' % axes_name])
      
    else :
      # add a line
      line = Line2D(self.LIM_AVAIL_WAVENUMBERS,
                    (0., 0.),
                    color=RamanROADegcircCalcFigure.EDGECOLOR)
      ax.add_line(line)
      
      plot_sticks(ax, X, Y,
                  barchart=True,
                  color=self._smartdict['%s_linecolor' % axes_name],
                  width=self._smartdict['%s_linewidth' % axes_name]/2.)

    # axes settings
    # always show 2 decimal points
    formatter = FormatStrFormatter('%.2f')
    ax.yaxis.set_major_formatter(formatter)
    
    ax.multfactor = multfactor
    ax.set_xlim(lim_wavenumbers)
    ax.set_ylim(y_lim)

    # y ticks
    self._make_yticks(
      ax,
      ticks_auto=self._smartdict['%s_ticks_auto' % axes_name],
      ticks_number=self._smartdict['%s_ticks_number' % axes_name],
      ticks_scaling_factor=\
      self._smartdict['%s_ticks_scaling_factor' % axes_name]) 

    # axes labels
    self.__set_spectrum_labels(axes_name, label_type,
                               multfactor, labels_fontsize)
    
  def __set_spectrum_labels(self, axes_name, label_type,
                            multfactor, labels_fontsize) :
    """Set the units and the label for a spectrum.

    axes_name  - IRVCDCalcFigure.AXES_NAMES
    label_type - IRVCDCalcFigure.AXES_NAMES + (int_epsilon, int_depsilon)
    
    """
    multfactor_str = self._get_order_string(multfactor)
    
    if 'epsilon' == label_type :
      label = IRVCDCalcFigure.TEX_LABEL_EPSILON
      units = IRVCDCalcFigure.TEX_UNITS_EPSILON % multfactor_str

    elif 'depsilon' == label_type :
      label = IRVCDCalcFigure.TEX_LABEL_DEPSILON
      units = IRVCDCalcFigure.TEX_UNITS_EPSILON % multfactor_str

    elif 'int_epsilon' == label_type :
      label = IRVCDCalcFigure.TEX_LABEL_INTEPSILON
      units = IRVCDCalcFigure.TEX_UNITS_INTEPSILON % multfactor_str
      
    elif 'int_depsilon' == label_type :
      label = IRVCDCalcFigure.TEX_LABEL_INTDEPSILON
      units = IRVCDCalcFigure.TEX_UNITS_INTEPSILON % multfactor_str

    # g
    else :
      if 0 == multfactor :
        label = r'$\it{g}$'
      else :
        label = IRVCDCalcFigure.TEX_LABEL_G % multfactor
      units = r'$\ $'

    # label
    self._varsdict['label_%s' % axes_name].set_text(label)

    # unit
    self._varsdict['axes_%s' % axes_name].text(
      BaseSpectrumFigure.POS_AXES_UNITS[0],
      BaseSpectrumFigure.POS_AXES_UNITS[1],
      units,
      rotation=90,
      fontsize=labels_fontsize,
      fontname='Arial',
      horizontalalignment='center',
      verticalalignment='center',
      transform=self._varsdict['axes_%s' % axes_name].transAxes)
    
  def plot_spectra(self, **kw) :
    """Plot the spectra.

    Keyword arguments :
    representation    -- 'Curves' or 'Stick' (default 'Curves')
    lim_wavenumbers   -- (left_nu, right_nu) ; left_nu > right_nu
                         (default (1900., 100.))
    tick_wavenumbers  -- major tick (default 200.)
    labels_fontsize   -- font size of the axes and spectra labels
                         (default 17)
    N_G               -- number of Gauss functions for fitting
    FWHM_fit          -- full width at half maximum for the curves
                         (default 10.)
    FWHM_inst         -- full width at half maximum for the
                         Gaussian instrument profile
                         (default 10.)
    title1            -- Title at the top of the figure (default '')
    title2            -- Smaller title beneath the title1 (default '')    

    """
    ## overriding the keywords
    self._smartdict.merge()
    self._smartdict.kw = kw

    ## go
    # rerender the axes
    self._pre_render()

    # spectra types
    representation = self.get_representation_as_index(
      self._smartdict['representation'])    
    
    # fitted
    if 0 == representation :      
      X, eps_Y, deps_Y, g_Y = self.__ir_vcd_tensors.fit_spectra(
        ngauss=self._smartdict['N_G'],
        fwhm_fit=self._smartdict['FWHM_fit'],
        fwhm_inst=self._smartdict['FWHM_inst'])

    # stick (integrated absorption coefficients)
    else :
      int_coeffs = self.__ir_vcd_tensors.integrated_coeffs()
      
      X      = self._mol.freqs[1:]
      eps_Y  = int_coeffs[:, 0]
      deps_Y = int_coeffs[:, 1]
      g_Y    = int_coeffs[:, 2]

    ## bottom spectrum
    self.__plot_spectrum('ir',
                         0 == representation and 'epsilon' or 'int_epsilon',
                         X,
                         eps_Y,                         
                         representation,
                         self._smartdict['lim_wavenumbers'],
                         self._smartdict['labels_fontsize'])

    ## middle spectrum
    self.__plot_spectrum('vcd',
                         0 == representation and 'depsilon' or 'int_depsilon',
                         X,
                         deps_Y,
                         representation,
                         self._smartdict['lim_wavenumbers'],
                         self._smartdict['labels_fontsize'])

    ## top spectrum
    self.__plot_spectrum('g',
                         'g',
                         X,
                         g_Y,                         
                         representation,
                         self._smartdict['lim_wavenumbers'],
                         self._smartdict['labels_fontsize'])

    ## shared axes 
    self.xlim = self._smartdict['lim_wavenumbers'] or \
                BaseSpectrumFigure.LIM_WAVENUMBERS

    ## redrawing the whole figure
    self.canvas.draw()

    ## canvas needs resaving
    self.canvas_changed = True


class RamanROADegcircExpFigure(BaseSpectrumFigure) :
  """Experimental Raman/ROA/Degree of circularity spectra."""

  ## TeX source pattern for an experimental ROA spectrum
  TEX_LABEL_ROAEXPSPECTRUM = \
    r'$\it{^{%s}I_R(%s)_{%s}\ -\ ^{%s}I_L(%s)_{%s}\ }$'

  ## TeX source pattern for an experimental Raman spectrum
  TEX_LABEL_RAMANEXPSPECTRUM = \
    r'$\it{^{%s}I_R(%s)_{%s}\ +\ ^{%s}I_L(%s)_{%s}\ }$'

  ## TeX source for the axis of a raman or roa spectrum
  TEX_UNITS_RAMANROAEXPSPECTRUM = r'$%s\ Electrons %s$'
  
  def __init__(self, master, expdata, **kw) :
    """Constructor of the class.

    Positional arguments :
    master  -- parent widget
    expdata -- list with the experimental data

    Accepts all the keyword arguments of the base class.
    
    """
    if not isinstance(expdata, (list, tuple)) or 1 > len(expdata) :
      raise ConstructorError('Invalid expdata argument')

    self._expdata = expdata
      
    BaseSpectrumFigure.__init__(self, master, **kw)

  def _init_vars(self) :
    """Initialize variables."""
    BaseSpectrumFigure._init_vars(self)

    # default axes settings
    for axes_name in RamanROADegcircCalcFigure.AXES_NAMES[:2] :
      # Auto calculation of the limits
      self._smartdict['%s_limits_auto' % axes_name] = True

      # if auto is turned off
      self._smartdict['%s_from' % axes_name]       = 0.
      self._smartdict['%s_to' % axes_name]         = 1.
      self._smartdict['%s_multfactor' % axes_name] = 0

      # appearance settings : linewidth & color
      self._smartdict['%s_linewidth' % axes_name] = 1.0
      self._smartdict['%s_linecolor' % axes_name] = 'black'

      # ticks properties
      self._smartdict['%s_ticks_auto' % axes_name]           = True
      self._smartdict['%s_ticks_number' % axes_name]         = None
      self._smartdict['%s_ticks_scaling_factor' % axes_name] = None

    ## Degree of circularity axes settings
    # appearance settings : linewidth & color
    self._smartdict['degcirc_linewidth'] = 1.0
    self._smartdict['degcirc_linecolor'] = 'black'

    # other keywords
    self._smartdict['normalize_energy'] = True
    self._smartdict['smooth'] = True
    self._smartdict['order']  = 2
    self._smartdict['sg_npoints'] = 5

  def _render_axes(self) :
    """Always rendering three axes."""
    self._render_three_axes()

  def _make_axes_aliases(self) :
    """Define some aliases for axes."""
    for axes_name, id_ in zip(RamanROADegcircCalcFigure.AXES_NAMES,
                              BaseSpectrumFigure.THREE_AXES_NAMES) :
      self._varsdict['axes_%s' % axes_name]           = \
                                self._varsdict['axes_%s' % id_]
      self._varsdict['label_%s_spectrum' % axes_name] = \
                                         self._varsdict['label_%s' % id_]
      
  def _plot_raman_roa(self, axes_name, X, Y,
                      scattering, lim_wavenumbers,
                      labels_fontsize) :
    """Plot a Raman or ROA spectrum.

    axes_name - see BaseSpectrumFigure.THREE_AXES_NAMES
    
    """
    ax = self._varsdict['axes_%s' % axes_name]
    
    Y, y_lim, multfactor = self._adjust_axes_data(
      X, Y, 0, lim_wavenumbers,
      limits_auto=self._smartdict['%s_limits_auto' % axes_name],
      yfrom=self._smartdict['%s_from' % axes_name],
      yto=self._smartdict['%s_to' % axes_name],
      multfactor=self._smartdict['%s_multfactor' % axes_name])

    # lower limit of the raman must be 0.
    if 'raman' == axes_name :
      y_lim = (0., y_lim[1])

    # inverting ROA if requested
    if 'roa' == axes_name and self._smartdict['roa_invert'] :
      Y *= -1.
    
    ax.plot(X, Y,
            '-',
            color=self._smartdict['%s_linecolor' % axes_name],
            linewidth=self._smartdict['%s_linewidth' % axes_name])  

    # axes settings
    ax.multfactor = multfactor
    ax.set_ylim(y_lim)

    # y ticks
    self._make_yticks(
      ax,
      ticks_auto=self._smartdict['%s_ticks_auto' % axes_name],
      ticks_number=self._smartdict['%s_ticks_number' % axes_name],
      ticks_scaling_factor=\
      self._smartdict['%s_ticks_scaling_factor' % axes_name]) 

    # units label
    ax.text(BaseSpectrumFigure.POS_AXES_UNITS[0],
            BaseSpectrumFigure.POS_AXES_UNITS[1],
            RamanROADegcircExpFigure.get_tex_spectrum_units(
              multfactor, self._smartdict['normalize_energy']),
            rotation=90,
            fontsize=labels_fontsize,
            fontname='Arial',
            horizontalalignment='center',
            verticalalignment='center',
            transform=self._varsdict['axes_%s' % axes_name].transAxes)

    # spectrum label
    i = list(RamanROADegcircCalcFigure.AXES_NAMES).index(axes_name)
    self._varsdict['label_%s_spectrum' % axes_name].set_text(
      RamanROADegcircExpFigure.get_tex_spectrum_label(i, scattering))

  def _plot_degcirc(self, X, degcirc_Y, scattering) :
    """Plot the degree of circularity spectrum."""
    self._varsdict['axes_degcirc'].plot(
      X, degcirc_Y,
      '-',
      color=self._smartdict['degcirc_linecolor'],
      linewidth=self._smartdict['degcirc_linewidth'])
        
    # add a dick line separating the spectrum
    line = Line2D(self.LIM_AVAIL_WAVENUMBERS,
                  (-1., -1.),
                  color=RamanROADegcircCalcFigure.EDGECOLOR,
                  linewidth=2.)
    self._varsdict['axes_degcirc'].add_line(line)

    # axes settings
    # limits are always from -1. to 1.
    self._varsdict['axes_degcirc'].set_ylim((-1., 1.))

    # formatting
    formatter = FormatStrFormatter('%d')
    self._varsdict['axes_degcirc'].yaxis.set_major_formatter(formatter)
    
    # where are yticks located   
    major_locator = MultipleLocator(1.)
    minor_locator = MultipleLocator(0.5)

    self._varsdict['axes_degcirc'].yaxis.set_major_locator(major_locator)
    self._varsdict['axes_degcirc'].yaxis.set_minor_locator(minor_locator)

    # spectrum label
    self._varsdict['label_degcirc_spectrum'].set_text(
      RamanROADegcircExpFigure.get_tex_spectrum_label(2, scattering))

  def __calc_rawdata(self) :
    """Calculate the raw experimental data.

    Return (laser_energy, X, raw_raman_Y, raw_roa_Y, raw_degcirc_Y)
    
    """
    laser_energy   = 0.
    X              = self._expdata[0].wavenumbers
    raw_raman_Y    = zeros(X.shape, 'd')
    raw_roa_Y      = zeros(X.shape, 'd')
    raw_degcirc_Y  = zeros(X.shape, 'd')
    
    for data in self._expdata :    
      if 'Raman/ROA' == data.datatype :
        laser_energy += data.laser_power * data.exposure_time * 0.001 * 60.
        raw_raman_Y  += data.raman
        raw_roa_Y    += data.roa

      # degree of circularity
      else :
        raw_degcirc_Y = data.degcirc

    return laser_energy, X, raw_raman_Y, raw_roa_Y, raw_degcirc_Y

  def get_tex_spectrum_label(type_, scattering) :
    """Return the TeX source for the spectra label.

    Positional arguments :
    type_          -- type of the spectrum : 0(raman), 1(roa), 2(degcirc)
    scattering     -- scattering as integer
    
    """
    # tex base string for the substituion
    if 0 == type_ :
      tex_base = RamanROADegcircExpFigure.TEX_LABEL_RAMANEXPSPECTRUM

    elif 1 == type_ :
      tex_base = RamanROADegcircExpFigure.TEX_LABEL_ROAEXPSPECTRUM

    elif 2 == type_ :
      if 2 > scattering :
        tex_base = RamanROADegcircCalcFigure.TEX_LABEL_DEGCIRC
      else :
        tex_base = ''

    else :
      raise InvalidArgumentError('Invalid spectrum type : %s' % type_)

    # arguments for the extrapolation of the tex_base
    args = []
    
    # scattering
    if 0 == scattering :
      if 2 != type_ :
        args.append('n')
        
      args.append(r'\pi')

      if 2 != type_ :
        args.append(r'SCP')

    elif 1 == scattering :
      if 2 != type_ :
        args.append('n')
        
      args.append(r'0')

      if 2 != type_ :
        args.append(r'SCP')

    # no degree of circularity for ICP
    elif 2 == scattering :
      if 2 != type_ :
        args.append(r'perp')
        args.append(r'\pi/2')
        args.append(r'ICP')

    elif 3 == scattering :
      if 2 != type_ :
        args.append(r'par')
        args.append(r'\pi/2')
        args.append(r'ICP')

    else :
      raise InvalidArgumentError('Invalid scattering type : %s' % scattering)

    # double the arguments for Raman/ROA
    if 2 != type_ :
      args.extend(args)

    return tex_base % tuple(args)

  get_tex_spectrum_label = staticmethod(get_tex_spectrum_label)
  
  def get_tex_spectrum_units(multfactor, normalize_energy) :
    """Return the TeX source for the units.

    Positional arguments :
    representation   -- representation as integer
    multfactor       -- order of magnitude
    normalize_energy -- whether the 
    
    """
    # units
    if normalize_energy :
      tex_units = r'\ /\ J'

    else :
      tex_units = ''

    multfactor_str = BaseSpectrumFigure._get_order_string(multfactor)
 
    return RamanROADegcircExpFigure.TEX_UNITS_RAMANROAEXPSPECTRUM % \
           (multfactor_str, tex_units)

  get_tex_spectrum_units = staticmethod(get_tex_spectrum_units)

  def plot_spectra(self, **kw) :
    """Plot the spectra.

    Keyword arguments :
    lim_wavenumbers   -- (left_nu, right_nu) ; left_nu > right_nu
                         (default (1900., 100.))
    tick_wavenumbers  -- major tick (default 200.)
    labels_fontsize   -- font size of the axes and spectra labels
                         (default 17)
    title1            -- Title at the top of the figure (default '')
    title2            -- Smaller title beneath the title1 (default '')
    smooth            -- whether to smooth the curves with Savitzky-Golay
                         (default True)
    order             -- polynomial order for Savitzy-Golay (default 2)
    sg_npoints        -- total number of points for Savitzky-Golay (default 5)
    normalize_energy  -- whether to normalize Raman/ROA to the laser energy
                         (default True)    
    
    """
    ## overriding the keywords
    self._smartdict.merge()
    self._smartdict.kw = kw

    ## go
    # rerender the axes
    self._pre_render()

    # making a cache for the raw Y values
    if 'raw_data' not in self._varsdict :
      self._varsdict['raw_data'] = self.__calc_rawdata()

    #laser_energy, X, raman_Y, roa_Y, degcirc_Y = self._varsdict['raw_data']
    laser_energy = self._varsdict['raw_data'][0]
    X = self._varsdict['raw_data'][1]
    
    # smooth ?
    if self._smartdict['smooth'] :
      nsym = (self._smartdict['sg_npoints'] - 1) / 2
      smooth_kw = dict(order=self._smartdict['order'], nl=nsym, nr=nsym)
      
      raman_Y   = savitzky_golay(self._varsdict['raw_data'][2], **smooth_kw)
      roa_Y     = savitzky_golay(self._varsdict['raw_data'][3], **smooth_kw)
      degcirc_Y = savitzky_golay(self._varsdict['raw_data'][4], **smooth_kw)
    else :
      raman_Y   = self._varsdict['raw_data'][2].copy()
      roa_Y     = self._varsdict['raw_data'][3].copy()
      degcirc_Y = self._varsdict['raw_data'][4].copy()
      
    # normalize to the laser energy ?
    if self._smartdict['normalize_energy'] and 0. != laser_energy :      
      raman_Y /= laser_energy
      roa_Y   /= laser_energy

    # scattering : assuming that all the data have the same type
    scattering  = RamanROADegcircCalcFigure.get_scattering_as_index(
      self._expdata[0].scattering)
    
    ## raman spectrum
    self._plot_raman_roa('raman',
                         X,
                         raman_Y,
                         scattering,
                         self._smartdict['lim_wavenumbers'],
                         self._smartdict['labels_fontsize'])
    ## roa spectrum
    self._plot_raman_roa('roa',
                         X,
                         roa_Y,
                         scattering,
                         self._smartdict['lim_wavenumbers'],
                         self._smartdict['labels_fontsize'])
    ## degree of circularity
    self._plot_degcirc(X,
                       degcirc_Y,
                       scattering)
    ## 
    self.xlim = self._smartdict['lim_wavenumbers']
    
    ## redrawing the whole figure
    self.canvas.draw()

    ## canvas needs resaving
    self.canvas_changed = True

