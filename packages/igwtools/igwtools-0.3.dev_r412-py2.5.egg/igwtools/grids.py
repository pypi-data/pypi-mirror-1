"""
This tool registers a world grid with an image, movie, or array.
It is interactive and requires the user's guidance.
It determines a set of 'map points' and a 'transformation'.
The tool can also be used to verify or modify a set of map points.

keypress events control the program

h - display help; list of keys
a - add a point at the current location of the mouse;
    control points are guessed as the nearest to nearest 1cm
    if a coordintate systems is already well defined
    else the coordinates of 0,0 are supposed.
d - delete the point closest to the mouse pointer
e - open up dialogue box to change the coordinates of a point


Wheel mouse zooms in and out.
Use pan/zoom tool

"""

from matplotlib.artist import Artist
from matplotlib.patches import Polygon, CirclePolygon
from matplotlib.numerix import sqrt, nonzero, equal, asarray, dot, Float
from matplotlib.numerix.mlab import amin
from matplotlib.mlab import dist_point_to_segment
from matplotlib.lines import Line2D
from matplotlib.backends.backend_gtk import error_msg_gtk

from igwtools import __version__
import gtk
import sys, os
import pylab
import Image
import numpy
from numpy.linalg import lstsq

class CoordsCollection():
    """
    A collection of pixel and world coordinates.
    Each pixel_coord is mapped to a corresponding
    set of world_coord.
    """
    def __init__(self, pixel_coords = [(0,0)], world_coords = [(0,0)]):
        self.pixel_coords = pixel_coords
        self.world_coords = world_coords
        self.compute_transform()

    def add_coord(self, pixel_coord, world_coord = None):
        if world_coord == None:
            # if transform is well defined, guess world coord:
            if len(self.pixel_coords) >= 3:
                world_coord = self.pixel_to_world(pixel_coord)
                # set world to nearest integer
                world_coord = (round(world_coord[0]), round(world_coord[1]))
            else: 
                # ask for advice from user
                world_coord = (0.,0.)
                dlg = CoordsDialog( pixel_coord = pixel_coord,
                                    world_coord = world_coord)
                response = dlg.run()
                if response==gtk.RESPONSE_OK:
                    pixel_coord = dlg.pixel_coord
                    world_coord = dlg.world_coord
                    dlg.destroy()
                else:
                    # don't add coord
                    dlg.destroy()
                    return

        self.pixel_coords.append(pixel_coord)
        self.world_coords.append(world_coord)
            
        # Assert len(pixel_coords) == len(world_coords)
        self.compute_transform()

    def del_coord(self, ind):
        self.pixel_coords = [tup for i,tup in \
                enumerate(self.pixel_coords) if i!=ind]
        self.world_coords = [tup for i,tup in \
                enumerate(self.world_coords) if i!=ind]
        self.compute_transform()

    def compute_transform(self):
        N = len(self.pixel_coords)
        if N < 3:
            # need a at least three coord pairs for this to work
            A = numpy.matrix(numpy.eye(2, dtype=float))
            b = numpy.array([0., 0.])
        else:
            M = numpy.ones((N,3),dtype=float)
            M[:,:2] = numpy.array(self.pixel_coords)

            soln =  lstsq(M,self.world_coords)[0]
            A = numpy.matrix(soln[:2,:]).T
            b = soln[2,:]
        self.transformation = (A,b)

    def pixel_to_world(self, pixel):
        A = self.transformation[0];
        b = self.transformation[1];
        pixel = numpy.array(pixel)
        world = numpy.array( A*pixel + b).reshape(2,)
        world = (world[0], world[1])
        return world

    def world_to_pixel(self, world):
        A = self.transformation[0];
        b = self.transformation[1];
        try: 
            Ainv = numpy.linalg.inv(A);
        except numpy.linalg.linalg.LinAlgError:
            print "Singular transformation matrix"
            return (numpy.nan, numpy.nan)

        world = numpy.array(world)
        pixel = numpy.array( Ainv*(world-b)).reshape(2,)
        return pixel

class CoordsInteractor:
    """
    An editor for coordinate markers

    Key-bindings

      'h' display a list of key-bindings

      'a' add a coordinate marker at point

      'd' delete the coordinate marker under point
    
      'e' edit the coordinates of the coordinate marker under point

      't' toggle coordinate markers on and off. When markers are on,
          you can move, edit, and delete them
    """

    showverts = True
    epsilon = 5  # max pixel distance to count as a vertex hit

    def __init__(self, ax, coords):
        self.ax = ax
        canvas = ax.get_figure().canvas
        self.coords = coords
        self.coords.pixel_coords = list(self.coords.pixel_coords)
        x, y = zip(*self.coords.pixel_coords)
        self.line = Line2D(x, y, linestyle='', marker='D', 
                           markerfacecolor='r', animated=True)
        
        self._ind = None # the active vert

        canvas.mpl_connect('draw_event', self.draw_callback)
        canvas.mpl_connect('button_press_event', self.button_press_callback)
        canvas.mpl_connect('key_press_event', self.key_press_callback)        
        canvas.mpl_connect('button_release_event', self.button_release_callback)
        canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)                
        self.canvas = canvas
        
        manager = pylab.get_current_fig_manager()
        label = gtk.Label()
        label.set_markup('Drag mouse over axes for position')
        label.show()
        vbox = manager.vbox
        vbox.pack_start(label, False, False)
        vbox.reorder_child(manager.toolbar, -1)
        self.coordinateslabel = label

    def draw_callback(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)
        
    def get_ind_under_point(self, event):
        'get the index of the vertex under point if within epsilon tolerance'
        x, y = zip(*self.coords.pixel_coords)
        
        # display coords        
        xt, yt = self.line.get_transform().numerix_x_y(x, y)
        d = sqrt((xt-event.x)**2 + (yt-event.y)**2)
        indseq = nonzero(equal(d, amin(d)))
        ind = indseq[0]

        if d[ind]>=self.epsilon:
            ind = None

        return ind
        
    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        if not self.showverts: return 
        if event.inaxes==None: return
        if event.button != 1: return
        self._ind = self.get_ind_under_point(event)

    def button_release_callback(self, event):
        'whenever a mouse button is released'
        self.coords.compute_transform()
        if not self.showverts: return
        if event.button != 1: return
        self._ind = None

    def key_press_callback(self, event):
        'whenever a key is pressed'
        if not event.inaxes: return
        if event.key=='t':
            self.showverts = not self.showverts
            self.line.set_visible(self.showverts)
            if not self.showverts: self._ind = None
        elif event.key=='a':
            if not self.showverts: return
            self.coords.add_coord((event.xdata, event.ydata))
            self.line.set_data(zip(*self.coords.pixel_coords))
        elif event.key=='d':
            if not self.showverts: return
            ind = self.get_ind_under_point(event)
            if ind is not None:
                if len(self.coords.pixel_coords)==1:
                    print "Warning: must have at least one coordinate marker"
                else:
                    self.coords.del_coord(ind)
                    self.line.set_data(zip(*self.coords.pixel_coords))
        elif event.key=='e':
            if not self.showverts: return
            ind = self.get_ind_under_point(event)
            if ind is not None:
                dlg = CoordsDialog( pixel_coord = self.coords.pixel_coords[ind],
                                    world_coord = self.coords.world_coords[ind]
                                  )
                response = dlg.run()
                if response==gtk.RESPONSE_OK:
                    self.coords.pixel_coords[ind] = dlg.pixel_coord
                    self.coords.world_coords[ind] = dlg.world_coord
                    self.coords.compute_transform()
                    self.line.set_data(zip(*self.coords.pixel_coords))
                dlg.destroy()
        elif event.key=='h':
            print self.__doc__

        self.canvas.draw()

    def motion_notify_callback(self, event):
        'on mouse movement'

        if event.inaxes is None:
            self.coordinateslabel.set_markup('Drag mouse over axes for coordinates')
        else:
            pixel = (event.xdata, event.ydata)
            world = self.coords.pixel_to_world(pixel)
            #pixel = self.coords.world_to_pixel(world)
        
            #self.coordinateslabel.set_markup('World: x,y=(%.1f, %.1f)'%(world[0],world[1]) +\
            #         ' Pixel: x,y=(%.1f,%.1f)'%(pixel[0], pixel[1]))
            self.coordinateslabel.set_markup('World Coordinates: (%.1f, %.1f)'%(world[0],world[1]))

        if not self.showverts: return 
        if self._ind is None: return
        if event.inaxes is None: return
        if event.button != 1: return
        x,y = event.xdata, event.ydata
        self.coords.pixel_coords[self._ind] = x,y
        self.line.set_data(zip(*self.coords.pixel_coords))

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

class SaveQueryDialog(gtk.Dialog):
    def __init__(self):
        gtk.Dialog.__init__(self, 'Save changes?')
        self.add_button(gtk.STOCK_YES, gtk.RESPONSE_YES)
        self.add_button(gtk.STOCK_NO, gtk.RESPONSE_NO)

class CoordsDialog(gtk.Dialog):
    def __init__(self, pixel_coord, world_coord):
        gtk.Dialog.__init__(self, 'Coordinates')
        
        self.pixel_coord = pixel_coord
        self.world_coord = world_coord

        table = gtk.Table(3,3)
        table.show()
        table.set_row_spacings(4)
        table.set_col_spacings(4)
        self.vbox.pack_start(table, True, True)
        
        # Labels
        label = gtk.Label('Pixel')
        label.show()
        table.attach(label, 0,1,1,2)
        label = gtk.Label('World')
        label.show()
        table.attach(label, 0,1,2,3)
        label = gtk.Label('x')
        label.show()
        table.attach(label, 1,2,0,1)
        label = gtk.Label('y')
        label.show()
        table.attach(label, 2,3,0,1)

        # text boxes
        entry = gtk.Entry()
        entry.show()
        entry.set_text(str(pixel_coord[0]))
        self.entryPixel0 = entry
        table.attach(entry, 1,2,1,2)
        entry = gtk.Entry()
        entry.show()
        entry.set_text(str(pixel_coord[1]))
        self.entryPixel1 = entry
        table.attach(entry, 2,3,1,2)

        entry = gtk.Entry()
        entry.show()
        entry.set_text(str(world_coord[0]))
        self.entryWorld0 = entry
        table.attach(entry, 1,2,2,3)
        entry = gtk.Entry()
        entry.show()
        entry.set_text(str(world_coord[1]))
        self.entryWorld1 = entry
        table.attach(entry, 2,3,2,3)

        self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
    def update_coords(self):

        # yes, this can be combined into a loop...

        s = self.entryPixel0.get_text()
        try: pixel0 = float(s)
        except ValueError:
            error_msg_gtk('Coordinates must be floats.')
            return False

        s = self.entryPixel1.get_text()
        try: pixel1 = float(s)
        except ValueError:
            error_msg_gtk('Coordinates must be floats.')
            return False

        s = self.entryWorld0.get_text()
        try: world0 = float(s)
        except ValueError:
            error_msg_gtk('Coordinates must be floats.')
            return False
         
        s = self.entryWorld1.get_text()
        try: world1 = float(s)
        except ValueError:
            error_msg_gtk('Coordinates must be floats.')
            return False
            
        self.pixel_coord = (pixel0, pixel1)
        self.world_coord = (world0, world1)

        return True

    def run(self):
        while 1:
            response = gtk.Dialog.run(self)
            if response==gtk.RESPONSE_OK:
                success = self.update_coords()
                if success:
                    break
            elif response==gtk.RESPONSE_CANCEL:
                break
        return response

def coords_editor(imagefilename, coords, **kwargs):
    fig = pylab.figure()

    ax = pylab.subplot(111)

    # add background image
    im = Image.open(imagefilename,'r')
    ar = numpy.array(im)

    pylab.imshow(ar,
                 aspect='auto',
                 interpolation='nearest',
                 **kwargs)
    pylab.axis('tight')


    c = CoordsInteractor(ax, coords)
    ax.add_line(c.line)

    ax.set_title('Coordinate Editor')
    ax.set_autoscale_on(False)

    pylab.show()

def grid_entry():
    """
    This is the entry point for the command line tool igwgrid.
    This function parses the command line arguments then calls
    the other functions in this module.
    """
    # define a parser
    from optparse import OptionParser
    usage = """ %prog [options] FILE """
    parser = OptionParser(usage=usage,
               version = "%prog (igwtools " + __version__ + ")")

    parser.add_option("--cmap", default = 'jet',
            help = "color map [default: %default]")
    parser.add_option("--worldgrid",
            help = "name of world grid file")
    parser.add_option("-t", "--timeoffset",
            help = "start time offset")
    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error("no image or movie file specified")

    # determine file type
    root, ext = os.path.splitext(args[0])
    ext = ext.lower()

    # TODO: generalize image, movie detection
    # TODO: support .xyp files
    if ext in ['.mov', '.avi', '.dv']:
        # movie format - need to extract out frame 0
        
        # create tempfile 
        import tempfile
        fd, tempname = tempfile.mkstemp(suffix = '.png')
        os.close(fd)

        if options.timeoffset is None:
            options.timeoffset = "0"

        # extract out frame 0 to tempfile
        cmd = "ffmpeg -ss %s " % options.timeoffset +\
              "-i %s -vcodec png " % args[0] +\
              "-vframes 1 -an -f rawvideo -y %s" % tempname
        os.system(cmd)
        imagefile = tempname
    else:
        tempname = None
        imagefile = args[0]

    # Create a default world grid
    coords = CoordsCollection(pixel_coords = [(100,100)])

    if options.worldgrid != None:
        # Load coords from file
        try:
            ar = pylab.load(options.worldgrid)
            if ar.size == 4:
                ar = ar.reshape(1,4)
            pixel_coords = [tuple(x) for x in list(ar[:,:2])]
            world_coords = [tuple(x) for x in list(ar[:,2:])]
            
            coords = CoordsCollection(pixel_coords = pixel_coords,
                                      world_coords = world_coords)
        except IOError:
            # file does not exist
            pass

    coords_editor(imagefile, coords = coords,
                  cmap = pylab.cm.get_cmap(options.cmap))

    # determine bounding box
    # how big is the image?
    size = Image.open(imagefile,'r').size
    # what are the coordinates of the corners?
    xmin1, zmin1 = coords.pixel_to_world((0, 0))
    xmax1, zmin2 = coords.pixel_to_world((size[0]-1, 0))
    xmin2, zmax1 = coords.pixel_to_world((0, size[1]-1))
    xmax2, zmax2 = coords.pixel_to_world((size[0]-1, size[1]-1))

    xmin = ((xmin1 + xmin2) / 2) 
    xmax = ((xmax1 + xmax2) / 2) 
    zmin = ((zmin1 + zmin2) / 2) 
    zmax = ((zmax1 + zmax2) / 2) 
    dx = (xmax - xmin) / size[0]
    dz = (zmax - zmin) / size[1]
    print "xmin = %.1f" % xmin
    print "xmax = %.1f" % xmax
    print "zmin = %.1f" % zmin
    print "zmax = %.1f" % zmax
    print "dx = %.3f" % dx
    print "dz = %.3f" % dz

    if options.worldgrid == None:
        #print to stdout
        for pixel, world in zip(coords.pixel_coords, coords.world_coords):
            print pixel[0], pixel[1], world[0], world[1]
        # open a filesave dialog box?
    else:
        # save coords to file
        dlg = SaveQueryDialog()
        response = dlg.run()
        if response==gtk.RESPONSE_YES:
            coords_array = numpy.hstack((numpy.array(coords.pixel_coords),
                                         numpy.array(coords.world_coords)))
            pylab.save(options.worldgrid, coords_array)
        dlg.destroy()

    if tempname != None:
        # remove temp file (if any)
        os.remove(tempname)

