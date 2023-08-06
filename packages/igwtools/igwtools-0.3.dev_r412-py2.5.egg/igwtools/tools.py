"""
tools

Support functions for analyzing Internal Gravity Waves
 extracting frames and time series
 synthetic schlieren

Conventions:

Horizontal     Vertical       Temporal
i, imin, imax, k, kmin, kmax, n, nmin, nmax  pixel coords (upper-left origin)
x, xmin, xmax, z, zmin, zmax, t, tmin, tmax  world coords (bottom-left origin)

However, earlier versions of the code used i,j to stand for row, column which
means
i <-> z
j <-> x
This needs to be changed to be consistent.
"""

from __future__ import division
from igwtools import __version__

#import matplotlib
#matplotlib.use('GTKAgg')

import numpy
from numpy import pi
import tables  # PyTables for HDF5 interface
from scipy import signal
import pylab # matplotlib interface
from optparse import OptionParser, OptionGroup
import scipy.ndimage as ndimage
from numpy import fft
import os

import schlieren

class parameters:
    # acceleration due to gravity
    g = 980.0

    # geometry
    tank = {'L': 197.01, 'W': 17.5 }

    # distance from back of tank to screen
    ls = 15.0
    # width of tank walls
    lp = 1.7
    # width of tank
    lt = 17.4
    # distance from front of tank to camera
    lc = 330.0
    
    # density of pure water 
    p0 = 0.9820

    # Index of refraction
    n = {'w' : 1.333, 'a': 1.0, 'p' : 1.49}

def import_dv(group, clipname, palette = False):
    "add digital video to an h5 db"

    import tempfile
    import shutil
    import Image
    from glob import glob

    import os.path as path

    # create a temporary directory to store video frames
    tempd = tempfile.mkdtemp(prefix = "igwimport_")

    # determine if clipname is a movie or a set of files
    root, ext = path.splitext(clipname)
    print root, ext
    if ext.lower() in ['.png', '.pgm', '.bmp', '.gif', '.tif', '.tiff']:
        print "Images to be imported"
        framelist = glob(clipname) 
    elif ext.lower() in ['.dv', '.avi', '.mpeg', '.mpg', '.mov', '.mp4']:
        if not os.path.exists(clipname):
            raise "File %s not found!" % clipname

        print "Movie to be imported"
        # need to split the movie into frames

        # convert dv to a sequence of grayscale images using ffmpeg
        # -t duration, recording time in seconds
        if palette:
            dv2pgm_cmd = "ffmpeg -i " + clipname + " " + tempd + "/frame%05d.ppm"
        else:
            dv2pgm_cmd = "ffmpeg -i " + clipname + " " + tempd + "/frame%05d.pgm"
        os.system(dv2pgm_cmd)

        # Determine the number of frames in the video
        framelist = glob(tempd + '/' + '*')
        #framelist = os.listdir(tempd)

    elif ext.lower() in ['.xyp']:
        print "XYP files to be imported"
        print "...not yet implemented"

    elif ext.lower() in ['.xyp.gz', '.xyz']:
        print "compressed XYP files to be imported"
        print "...not yet implemented"
    else:
        print "Unknown file type to be imported"
        print "Import failed!"
        return

    framelist.sort()
    numframes = len(framelist)

    # use first frame to get shape of a frame
    im = Image.open(framelist[0], "r")
    (xsize, ysize) = im.size

    # get the hdf5 file object:
    h5file = group._v_file

    if 'dv' in group:
        h5file.removeNode(group.dv)

    if palette:
        # use last frame to choose palette
        im = Image.open(framelist[-1], "r")
        im = im.convert(mode = 'P')
        palette = im.getpalette()

        # save palette
        h5file.createArray(group, 'palette', palette, 'palette')

    # atoms are images
    if tables.__version__ >= '2.0':
        atom = tables.UInt8Atom()
        earray = h5file.createEArray(group, 'dv', atom = atom, shape = (ysize, xsize, 0), title='Video Data',
                      expectedrows = numframes)
    else:
        atom = tables.UInt8Atom(shape = (ysize, xsize, 0), flavor = "numpy")
        # create an EArray to store the video data
        earray = h5file.createEArray(group, 'dv', atom, 'Video Data',
                      expectedrows = numframes)
    
    # loop through all the frames of the video
    for frame in framelist:
        print frame, '(/%s)' % numframes
        # open frame
        im = Image.open(frame, "r")
        if palette:
            im = im.convert(mode = 'P', palette = palette)
        # extract image data
        data = im.getdata()
        # create an array from the image data
        newarr = numpy.array(data, dtype = 'uint8').reshape((ysize, xsize, 1))
        # add to the EArray
        earray.append(newarr)
    print 

    # clean up the frame images and the temp directory
    shutil.rmtree(tempd)

    # add timestamp for DV import
    import time
    group.dv.attrs.date_import = time.ctime()


def import_entry():
    # look up defaults from environment
    default_database = os.getenv("IGWDB")
    default_experiment = os.getenv("IGWEXPT")

    usage = """ %prog [options] FILE(s) """
    parser = OptionParser(usage = usage,
                version = "%prog (igwtools " + str(__version__) + ")")

    parser.add_option("-D", "--database", default = default_database,
                      help = "Database name [default: %default]")
    parser.add_option("-e", "--experiment", dest = "exptname",
                      default = default_experiment,
                      help = "Experiment name [default: %default]")
    parser.add_option("-v", "--verbose", action = "store_true",
                      help = "be verbose")
    parser.add_option("--xmin", type = "float", default = 0.0,
            help = 'left edge in world coordinates [default: %default]')
    parser.add_option("--xmax", type = "float", default = 1.0,
            help = 'right edge in world coordinates [default: %default]')
    parser.add_option("--zmin", type = "float", default = 0.0,
            help = 'bottom edge in world coordinates [default: %default]')
    parser.add_option("--zmax", type = "float", default = 1.0,
            help = 'top edge in world coordinates [default: %default]')
    parser.add_option("--tmin", type = "float", default = 0.0,
            help = 'time of first frame [default: %default]')
    parser.add_option("--palette", action = "store_true",
            help = 'import images in colour using a palette')

    fps = 29.97 # NTSC framerate
    parser.add_option("--fps", type = "float", default = fps,
            help = 'set framerate [default: %default]')
    parser.add_option("--dt", type = "float", default = 1/fps,
            help = 'set time between frames [default: %default]')
    parser.add_option("-f", "--force", action = "store_true",
            help = 'force overwriting of existing data')

    (options, args) = parser.parse_args()

    if options.exptname == None and len(args) == 0:
        parser.error("no experiment or DV file specified")

    # args are a list of files to import
    if options.exptname == None:
        options.exptname = args[0].split('.')[0]
    if options.database == None:
        options.database = options.exptname + '.h5'
    if options.database.split('.')[-1] != 'h5':
        # append on .h5 to database name
        options.database = options.database + '.h5'

    if options.verbose:
        print "Opening", options.database
    # open h5 db (and create if it does not exist)
    h5file = tables.openFile(options.database, mode = 'a')

    # create a branch for this experiment off of root node
    if "/" + options.exptname in h5file:
        if options.verbose:
            print "Accessing experiment", options.exptname
        group = h5file.getNode("/" + options.exptname)
    else:
        if options.verbose:
            print "Creating experiment", options.exptname
        group = h5file.createGroup("/", options.exptname)

    if len(args) >= 1:
        print "Importing ..."
        print "  %s -> %s" % (args[0], options.exptname)
        if ('dv' in group) and not options.force:
            print 'DV already exists! (use --force to override)'
            h5file.close()
            return
        import_dv(group, args[0], options.palette)

    # close the h5file
    h5file.close()

    # set the geometry
    if options.verbose:
        print "Setting world coordinates..."

    e = Experiment(options.database, options.exptname)
    if e == None:
        return

    #tmax = options.tmin + options.dt * e.nFrames
    tmax = options.tmin + 1.0 / options.fps * e.nFrames
    if ('xmin' in e.dv.attrs) and not options.force:
            print '  world coordinates already defined! (use --force to override)'
            e.close()
            return
    e.set_worldgrid(xmin = options.xmin, xmax = options.xmax,
                    zmin = options.zmin, zmax = options.zmax,
                    tmin = options.tmin, tmax = tmax)
    e.close()

    if options.verbose:
        print "igwimport successful."

def extract_entry():

    # look up defaults from environment
    default_database = os.getenv("IGWDB")
    default_experiment = os.getenv("IGWEXPT")

    usage = """ %prog [options] """
    parser = OptionParser(usage = usage,
            version = "%prog (igwtools " + str(__version__) + ")")
    parser.add_option("-o", "--outputfile",
                      help = "Name of output file (output saved only if supplied)")
    parser.add_option("-D", "--database", default = default_database,
                      help = "Database name [default: %default]")
    parser.add_option("-e", "--experiment", dest = "exptname", 
                      default = default_experiment,
                      help = "Experiment name [default: %default]")
    parser.add_option("-l", "--list", action = "store_true",
                      help = "list all experiments")
    parser.add_option("-v", "--verbose", action = "store_true",
                      help = "be verbose")
    parser.add_option("-d", action = "store_true", dest = "display",
                      help = "displays image for debugging purposes")
    parser.add_option("-s", "--schlieren", action = "store_true",
                      help = "perform qualitative synthetic schlieren")
    parser.add_option("-S", "--save",
                      help = "save view to hdf5 database")
    parser.add_option("-L", "--load",
                      help = "load view from hdf5 database")
    parser.add_option("--cmap", default = 'jet',
                      help = "color map [default: %default]")
    parser.add_option("--palette", action = "store_true",
                      help = "use the stored colour palette")
    parser.add_option("--interpolation", default = 'bicubic',
                      help = "interpolation mode [default: %default]")
    parser.add_option("--clim", 
                      help = "color bar limits")
    parser.add_option("-f", "--force", action = "store_true",
                      help = "Force operation")

    group = OptionGroup(parser,
            "Selection based on world coordinates")

    group.add_option("-t", type = "string", help = "T = tstart:tstop:tstep")
    group.add_option("-x", type = "string", help = "X = xstart:xstop:xstep")
    group.add_option("-z", type = "string", help = "Z = zstart:zstop:zstep")

    parser.add_option_group(group)

    group = OptionGroup(parser,
            "Selection based on pixel coordinates")
    group.add_option("-n", type = "string", help = "N = nstart:nstop:nstep (frame number)")
    group.add_option("-i", type = "string", help = "I = istart:istop:istep (vertical coordinate from top)")
    group.add_option("-j", type = "string", help = "J = jstart:jstop:jstep (horiztonal coordinate from left)")

    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    if options.database == None:
        parser.error('No database specified')

    if options.list:
        # print out list of experiments in db
        if options.database[-3:] != '.h5':
            options.database = options.database + '.h5'

        try:
            h5file = tables.openFile(options.database, mode = "r")
        except IOError:
            print "Unable to open database %s" % options.database
            return
        
        print 'list of experiments and views in %s:' % options.database

        for node in h5file.walkNodes("/"):
            print node
        #for group in h5file.walkGroups("/"):
        #    print group._v_pathname
        h5file.close()
        return

    if ((options.x != None) or (options.x != None) or (options.t != None)) \
   and ((options.n != None) or (options.i != None) or (options.j != None)):
       parser.error('Use world or pixel coordinates--not both!')

    if options.exptname == None:
        parser.error('No experiment name given. Use -l option to list experiments')
    else:
        expt = Experiment(options.database, options.exptname)

    if expt == None:
        print "Try the -l option to list experiments"
        return

    if options.verbose:
        print "Identity:"
        print "  database:", expt.dbname
        print "  experiment:", expt.exptname
        print "  date imported:", expt.date_import
        print "Geometry:"
        print "  tmin = %7.03f" % expt.tmin, \
              "tmax = %7.03f" % expt.tmax, \
              "dt = %.03f" % expt.dt, \
              "(%d frames)" % expt.nFrames
        print "  xmin = %7.03f" % expt.xmin, \
              "xmax = %7.03f" % expt.xmax, \
              "dx = %.03f" % expt.dx, \
              "(%d columns)" % expt.nCols
        print "  zmin = %7.03f" % expt.zmin, \
              "zmax = %7.03f" % expt.zmax, \
              "dz = %.03f" % expt.dz, \
              "(%d rows)" % expt.nRows
        print ""

    if options.verbose:
        print "Selection window:"
        print '  t    =', options.t, '(n = %s)' % options.n
        print '  x    =', options.x, '(j = %s)' % options.j
        print '  z    =', options.z, '(i = %s)' % options.i
        print

    if options.verbose:
        print 'performing extraction...'

    def process_slice(x, num = "float"):
        def tonumber(x):
            try:
                if num == "float":
                    return float(x)
                else:
                    return int(x)
            except:
                return None
        if x == None:
            return slice(None, None, None)
        x = [tonumber(s) for s in x.split(':')]
        if len(x) == 1:
            x = x[0]
        elif len(x) == 2:
            x = slice(x[0], x[1])
        else:
            x = slice(x[0], x[1], x[2])
        return x

    # parse slices
    t = process_slice(options.t)
    x = process_slice(options.x)
    z = process_slice(options.z)
    n = process_slice(options.n, num = "int")
    i = process_slice(options.i, num = "int")
    j = process_slice(options.j, num = "int")

    if options.load != None:
        segment = expt.load_view(options.load, i, j, n)
    elif ((options.x != None) or (options.z != None) or (options.t != None)):
        # world coordinates
        segment = expt[x, z, t]
    elif ((options.n != None) or (options.i != None) or (options.j != None)):
        # pixel coordinates
        segment = expt.get(i, j, n)
    else:
        print "  No window selected. If you really want *everything*, try -n :"
        expt.close()
        return

    if options.verbose:
        "Data loaded."

    if options.schlieren:
        schlieren.schlieren_field(segment)
    
    if options.save != None:
        if options.verbose:
            print "saving view...", options.save
        expt.save_view(segment, options.save, force = options.force)
        #if options.verbose:
        #    print expt.h5file

    #save as file
    if(options.outputfile != None):
        if options.verbose:
            print 'saving file...'
        segment.save(options.outputfile)

    if options.display:
        pylab.figure()
        if options.clim:
            # parse into vmin and vmax
            # TODO
            print options.clim
            try:
                vmax = float(options.clim)
                vmin = -vmax
            except:
                vmin, vmax = eval(options.clim)

            if vmin > vmax:
                print "minvalue of clim must be less that maxvalue!"
                raise ValueError

        else:
            vmin = None
            vmax = None

        segment.plot(palette = options.palette,
                     interpolation = options.interpolation,
                     vmax = vmax, vmin = vmin,
                     cmap = pylab.cm.get_cmap(options.cmap))
        pylab.title(options.exptname)
        if segment.dim > 1:
            # add a colorbar
            c = pylab.colorbar()
            segment.colorbar = c
        pylab.show()

    expt.close()

class FieldWidgets:
    """
    Tools used to explore and interact with a Field when plotted

    Key-bindings

        'i' Toggle inspect mode. Mouse clicks give info.

        'c' Toggle a cross-hair cursor

        's' Toggle a line tool that prints out slope and length

        'a' Toggle a box tool that computes area

        'f' Toogle a rectangle tool that computes the dominant 
            frequency found in the box

        'b' Blur (low-pass filter)

        'q' Quit the plot

        'P' Print the image to the default printer
    """
    def __init__(self, ax, field):
        self.ax = ax
        self.field = field
        pylab.connect('key_press_event', self.key_press_callback)
        pylab.connect('button_press_event', self.button_press_callback)

        from matplotlib.widgets import RectangleSelector, Cursor
        rectprops = dict(facecolor = 'white', edgecolor = 'black', alpha = 0.4, fill = True)
        self.box = RectangleSelector(ax, self.box_callback, drawtype = 'box', 
                               rectprops = rectprops, useblit = False)
        self.box.visible = False

        rectprops = dict(facecolor = 'blue', edgecolor = 'black', alpha = 0.4, fill = True)
        self.freq = RectangleSelector(ax, self.freq_callback, drawtype = 'box', 
                               rectprops = rectprops, useblit = False)
        self.freq.visible = False

        self.cursor = Cursor(ax, useblit = True, 
                            color = 'white', alpha = 0.7, linewidth = 2 )
        self.cursor.visible = False

        lineprops = dict(color = 'black', linestyle = '-', linewidth = 5, alpha = 0.5)
        self.line = RectangleSelector(ax, self.line_callback,  
                           lineprops = lineprops, drawtype = 'line', useblit = False)
        self.line.visible = False

        self.investigate_mode = False

        self.manager = pylab.get_current_fig_manager()
        self.toolbar = self.manager.toolbar

        # Add to toolbar
        #import gtk
        #next = 8
        #button = gtk.Button('Frequency')
        #button.show()
#
#        toolitem = gtk.ToolItem()
#        toolitem.show()
        #toolitem.set_tooltip(
        #       self.toolbar.tooltips,
        #        'Determine the frequecy is selected region')
#        toolitem.add(button)
#        self.toolbar.insert(toolitem, next); next += 1

        self.current_cmap_number = 0
        self.cmaps = ['jet', 'gray', 'gray_r']

    def key_press_callback(self, event):
        'whenever a key is pressed'
        if event.key == 'c':
            self.cursor.visible = not self.cursor.visible
            pylab.draw()
            pylab.draw()
        if event.key == 'o':
            print 'Interactive mode is on.'
            pylab.show()
        if event.key == 'O':
            pylab.ioff()
            print 'Interactive mode is off.'
        elif event.key == 'q':
            pylab.close()
        elif event.key == 'h':
            self.print_usage()
        elif event.key == 's':
            self.line.visible = not self.line.visible
        elif event.key == 'a':
            self.box.visible = not self.box.visible
        elif event.key == 'v':
            print self.field
        elif event.key == 'i':
            if self.investigate_mode:
                self.investigate_mode = False
                print "Disable inspect mode"
            else:
                self.investigate_mode = True
                print "Enable inspect mode"
        elif event.key == 'f':
            x1, x2, y1, y2 = pylab.axis()
            print "Find Frequency Peak in (%.3f, %.3f) --> (%.3f, %.3f)" % \
                (x1, y1, x2, y2)
            freq = self.field.find_freq((x1, y1, x2, y2))
        elif event.key == 'F':
            x1, x2, y1, y2 = pylab.axis()
            print pylab.axis()
            print "Find Frequency Peak in (%.3f, %.3f) --> (%.3f, %.3f)" % \
                (x1, y1, x2, y2)
            freq = self.field.find_freq((x1, y1, x2, y2), show = True)
            pylab.axis([-2.0, 2.0, -2.0, 2.0])
        elif event.key == 'b':
            self.field.blur()
            self.field.do_plot(shift = 0, redraw =True)
            pylab.draw()
            print 'Applied low-pass filter.'
        elif event.key == 'P':
            print "Print"
            #pylab.ioff()
            #f = pylab.gcf()
            #orig_size = f.get_size_inches()
            #print orig_size
            #f.set_size_inches((3, 2))
            pylab.savefig('tmp.ps')
            #f.set_size_inches(orig_size)
            print_cmd = "lp tmp.ps" # print to default printer
            #print print_cmd
            os.system(print_cmd)
            os.remove('tmp.ps')
            #pylab.ion()
        elif event.key == 'right':
            self.field.do_plot(shift = 10)
        elif event.key == 'left':
            self.field.do_plot(shift = -10)
        elif event.key == 'up':
            self.field.do_plot(shift = 1)
        elif event.key == 'down':
            self.field.do_plot(shift = -1)
        elif event.key == 'k':
            # enlarge clim
            im = self.field.im
            if im is not None:
                clim = im.get_clim()
                im.set_clim(clim[0]/1.1, clim[1]/1.1)
            pylab.draw()
        elif event.key == 'j':
            # shrink clim
            im = self.field.im
            if im is not None:
                clim = im.get_clim()
                print clim[0], clim[1]
                im.set_clim(clim[0]*1.1, clim[1]*1.1)
            pylab.draw()
        elif event.key == 'w':
            self.field.do_plot(axis = 'frame')
        elif event.key == 'e':
            self.field.do_plot(axis = 'hts') 
        elif event.key == 'r':
            self.field.do_plot(axis = 'vts')
        elif event.key == 'p':
            im = self.field.im
            if im is not None:
                self.current_cmap_number += 1
                if self.current_cmap_number > len(self.cmaps)-1:
                    self.current_cmap_number = 0
                cm = pylab.cm.get_cmap(self.cmaps[self.current_cmap_number])
                im.set_cmap(cm)
            pylab.draw()
        elif event.key == 'C':
            self.field.do_plot(contour = True)
        else:
            pass
        pylab.draw()

    def button_press_callback(self, event):
        if self.investigate_mode:
            # if cursor is turned on
            if event.inaxes:
                x, y = event.xdata, event.ydata
                print "coords: (%.2f, %.2f)" % (x, y),
                self.field.describe_element((x, y))

    def print_usage(self):
        print """
Key-bindings
    'h' Help
    'g' Toggle grid
    'c' Toggle a cross-hair cursor.
    's' Toggle a line tool that prints out slope and length
    'a' Toogle a box tool that computes the area
    'f' Computes the dominant frequency found in current view
    'F' Computes the dominant frequency found in current view
        and show the powerspectrum
    'v' Print a description of the field
    'i' Toggle inspect mode. Mouse clicks give information.
    'p' cycle the colormap (jet, gray, gray_r)
    'P' Print the image to the default printer
    'C' Make a contour plot.
    'q' Exit the plot
"""
    def line_callback(self, event1, event2):
        'event1 and event2 are the press and release events'
        if self.line.visible:
            x1, y1 = event1.xdata, event1.ydata
            x2, y2 = event2.xdata, event2.ydata
            #print "(%.3f, %.3f) --> (%.3f, %.3f)"%(x1, y1, x2, y2),
            if x2 == x1:
                slope = numpy.nan
            else:
                slope = (y2-y1) / (x2-x1)
            length = numpy.sqrt(((x2-x1)**2 + (y2-y1)**2))
            print "length: %.3g" % length,
            print "angle: %.2g" % (numpy.arctan(slope)*360/2/pi),
            print "slope: %.3g" % slope,
            print "inv. slope: %.3g" % (1/slope)

    def box_callback(self, event1, event2):
        'event1 and event2 are the press and release events'
        if self.box.visible:
            x1, y1 = event1.xdata, event1.ydata
            x2, y2 = event2.xdata, event2.ydata
            print "(%.3f, %.3f) --> (%.3f, %.3f)"%(x1, y1, x2, y2),
            area = abs((x2-x1)*(y2-y1))
            print "Area:", area

    def freq_callback(self, event1, event2):
        'event1 and event2 are the press and release events'
        if self.freq.visible:
            x1, y1 = event1.xdata, event1.ydata
            x2, y2 = event2.xdata, event2.ydata
            print "Find Frequency Peak in (%.3f, %.3f) --> (%.3f, %.3f)" % \
                (x1, y1, x2, y2)
            freq = self.field.find_freq((x1, y1, x2, y2), show = self.showfreq)
            #print "Frequency: (%.3f, %.3f)" % freq
     
class Field(numpy.ndarray):
    """
A field is the primary data structure used in igwtools.
A 4-d array that hold gridded data.  Can hold a frame, vts, or hts.
data[i, j, k, n]
x = xmin + i*dx;
y = ymin + j*dy;
z = zmin + k*dz;
t = tmin + n*dy;
Since its superclass is ndarray, slices work as expected.
"""
    def __new__(subtype, data, expt = None, 
                xmin = 0.0, xmax = 0.0, 
                ymin = 0.0, ymax = 0.0, 
                zmin = 0.0, zmax = 0.0, 
                tmin = 0.0, tmax = 0.0, 
                dtype = None, copy = True):

        # Make sure we are working with an array
        # and copy the data by default
        subarr = numpy.array(data, 
                       dtype = dtype, copy =copy)
        # Transform 'subarr' from an ndarray to our new subclass.
        subarr = subarr.view(subtype)

        subarr.expt = expt
        subarr.orientation = None
        shape = subarr.shape
        dim = len(shape)
        subarr.dim = dim
        if dim == 0:
            subarr.nx = None
            subarr.ny = None
            subarr.nz = None
            subarr.nt = None
        elif dim == 1:
            if (xmax - xmin) == 0:
                subarr.nx = 1
            else:
                subarr.nx = shape[0]
            if (zmax - zmin) == 0:
                subarr.nz = 1
            else:
                subarr.nz = shape[0]
            if (tmax - tmin) == 0:
                subarr.nt = 1
            else:
                subarr.nt = shape[0]
        elif dim == 2:
            n1, n2 = shape

            if tmax - tmin == 0: # frame xz
                subarr.orientation = 'xz'
                subarr.nx = n1
                subarr.ny = 1
                subarr.nz = n2
                subarr.nt = 1
                subarr.t = tmin
            elif zmax - zmin == 0: # hts xt
                subarr.orientation = 'xt'
                subarr.nx = n1
                subarr.ny = 1
                subarr.nz = 1
                subarr.nt = n2
                subarr.z = zmin
            elif xmax - xmin == 0: # vts tz
                subarr.orientation = 'tz'
                subarr.nx = 1
                subarr.ny = 1
                subarr.nt = n1
                subarr.nz = n2
                subarr.x = xmin
            else:
                print "2d data with 3d bounds!"
                print "shape =", shape
        elif dim == 3:
            subarr.nx, subarr.nz, subarr.nt = shape
            subarr.ny = 1
        else:
            print "unsupported dimensions!"

        subarr.xmin = xmin
        subarr.xmax = xmax
        subarr.x = xmin
        if(xmax == None or xmin == None):
            subarr.dx = None
        elif(xmax == xmin):
            subarr.dx = 0.0
        else:
            subarr.dx = (xmax - xmin) / (subarr.nx - 1)

        subarr.ymin = ymin
        subarr.ymax = ymax
        subarr.y = ymin
        if(ymax == None or ymin == None):
            subarr.dy = None
        elif(ymax == ymin):
            subarr.dy = 0.0
        else:
            subarr.dy = (ymax - ymin) / (subarr.ny - 1)
        subarr.zmin = zmin
        subarr.zmax = zmax
        subarr.z = zmin
        if(zmax == None or zmin == None):
            subarr.dz = None
        elif(zmax == zmin):
            subarr.dz = 0.0
        else:
            subarr.dz = (zmax - zmin) / (subarr.nz - 1)
        subarr.tmin = tmin
        subarr.tmax = tmax
        subarr.t = tmin
        if(tmax == None or tmin == None):
            subarr.dt = None
        elif(tmax == tmin):
            subarr.dt = 0.0
        else:
            subarr.dt = (tmax - tmin) / (subarr.nt - 1)

        return subarr

    def __str__(self):
        "describe the Field"
        if self.nt == 1: # frame
            shape = "shape = (%d,)\n" % self.shape
            header = 'Frame:\n'
        elif self.nx == 1: # vts
            shape = "shape = (%d, %d)\n" % self.shape
            header = 'VTS:\n'
        elif self.nz == 1: # hts
            shape = "shape = (%d, %d)\n" % self.shape
            header = 'HTS:\n'
        else:
            shape = "shape = (%d, %d, %d)\n" % self.shape
            if self.last_axis == 'frame':
                header = 'Frame: t = %.2f (n = %d)\n' % \
                    (self.t, self.t_to_n(self.t))
            elif self.last_axis == 'vts':
                header = 'VTS: x = %.2f (i = %d)\n' % \
                    (self.x, self.x_to_i(self.x))
            else:
                header = 'HTS: z = %.2f (k = %d)\n' % \
                    (self.z, self.z_to_k(self.z))
        geom = "[x, z, t] =[%.2f:%.2f, %.2f:%.2f, %.2f:%.2f]\n" % (self.xmin, self.xmax, 
                     self.zmin, self.zmax, self.tmin, self.tmax)
        dim = "(nx, nz, nt) = (%d, %d, %d)\n" % (self.nx, self.nz, self.nt)
        delta = "(dx, dz, dt) = (%.3f, %.3f, %.3f)" % (self.dx, self.dz, self.dt)

        contents = numpy.asarray(self).__str__()
        contents = numpy.ndarray.__str__(self)
        return header + geom + dim + delta
    def print_contents(self):
        contents = numpy.asarray(self).__str__()
        contents = numpy.ndarray.__str__(self)
        print contents
    def __array_finalize__(self, parent):
        properties = ['xmin', 'xmax', 'dx', 'nx',
                      'ymin', 'ymax', 'yz', 'ny',
                      'zmin', 'zmax', 'dz', 'nz',
                      'tmin', 'tmax', 'dt', 'nt']
        for prop in properties:
            setattr(self, prop, getattr(parent, prop, None))

    def rectangle(self, xleft, ybottom, xright, ytop, coords = 'pixels'):
        if(coords == 'pixels'):
            return self[:]
        elif(coords == 'world'):
            return self[:]

    def pixel_to_world(self, pixel):
        A = self.transformation[0]
        b = self.transformation[1]
        pixel = numpy.array(pixel)
        world = numpy.array( A*pixel + b)
        world = world.reshape(2, )
        return world

    def world_to_pixel(self, world):
        A = self.transformation[0]
        b = self.transformation[1]
        Ainv = numpy.linalg.inv(A)
        world = numpy.array(world)
        pixel = numpy.array( Ainv*(world-b)).reshape(2, )
        return pixel

    def set_transformation(self, pixelcoords = (), worldcoords = ()):
        from scipy.linalg import lstsq

        if len(pixelcoords) != len(worldcoords):
            print "pixel and world coords must be the same length"
            return

        n = len(pixelcoords)
        # solve for transformation
        M = numpy.ones((n, 3), dtype =float)
        M[:, :2] = pixelcoords
        soln =  lstsq(M, worldcoords)[0]
        A = numpy.matrix(soln[:2, :]).T
        b = soln[2, :]
        self.transformation = (A, b)

    def plot(self, axis = None, palette = False, **kwargs):
        "one time setup for plot"
        self.kwargs = kwargs
        self.colorbar = None
        self.palette = palette

        if self.dim == 0:
            #If 0-dimensional array, easiest thing is just 
            #to spit out the value to stdout
            data = numpy.asarray(self)
            print data
            return

        #ax = pylab.subplot(111)
        ax = pylab.gca()
        from matplotlib import rcParams
        if rcParams['backend'] in ['TkAgg', 'GTKAgg']:
            FieldWidgets(ax, self)
        self.ax = ax
        self.last_axis = None
        self.last_val = None

        self.do_plot(axis = axis)

    def do_plot(self, axis = None, shift = 0, redraw = False, contour = False):

        "Make a visual rendering of the Field"
        dim = len(self.shape)
        if dim == 0:
            #If 0-dimensional array, easiest thing is just 
            #to spit out the value to stdout
            data = numpy.asarray(self)
            print data
            bounds = None
            im = None
        elif dim == 1:
            # plot a curve
            l = len(self)
            if self.nz == 1 and self.nt == 1:
                grid = numpy.mgrid[self.xmin:self.xmax:l*1j]
                xlabel = r'$x$'
            if self.nx == 1 and self.nt == 1:
                grid = numpy.mgrid[self.zmin:self.zmax:l*1j]
                xlabel = r'$z$'
            if self.nx == 1 and self.nz == 1:
                grid = numpy.mgrid[self.tmin:self.tmax:l*1j]
                extent = [self.xmin, self.xmax]
                xlabel = r'$t$'
            pylab.plot(grid, self)
            pylab.xlabel(xlabel, size = 'x-large')
            bounds = None
            im = None
        elif dim == 2:
            # determine frame, hts or vts:
            if self.nt == 1: # frame
                extent = [self.xmin-self.dx/2,
                       self.xmax+self.dx/2, 
                       self.zmin-self.dz/2, 
                       self.zmax+self.dz/2]
                bounds = [self.xmin, self.xmax, self.zmin, self.zmax]
                nx = self.nx
                ny = self.nz
                xlabel = r'$x$'
                ylabel = r'$z$'
                self.orientation = 'xz'
                self.t = self.tmin
            elif self.nx == 1: # vts
                extent = [self.tmin-self.dt/2, 
                        self.tmax+self.dt/2, 
                        self.zmin-self.dz/2, 
                        self.zmax+self.dz/2]
                bounds = [self.tmin, self.tmax, self.zmin, self.zmax]
                nx = self.nt
                ny = self.nz
                xlabel = r'$t$'
                ylabel = r'$z$'
                self.orientation = 'tz'
                self.x = self.xmin
            elif self.nz == 1: # hts
                extent = [self.xmin-self.dx/2, 
                        self.xmax+self.dx/2, 
                        self.tmin-self.dt/2, 
                        self.tmax+self.dt/2]
                bounds = [self.xmin, self.xmax, self.tmin, self.tmax]
                nx = self.nx
                ny = self.nt
                xlabel = r'$x$'
                ylabel = r'$t$'
                self.orientation = 'xt'
                self.z = self.zmin
            else:
                print "Nonstandard or non 2-d field data. I don't know how to plot this"
                print self.nx, self.ny, self.nz, self.nt
                print "shape =", self.shape
                return 

            if contour:
                #levels = 6
                vmin = self.kwargs.get('vmin')
                vmax = self.kwargs.get('vmax')
                cmap = self.kwargs.get('cmap')
                if vmin == None or vmax == None:
                    levels = None
                else:
                    levels = numpy.mgrid[vmin:vmax:7j]
                x = numpy.mgrid[bounds[0]:bounds[1]:nx*1j]
                y = numpy.mgrid[bounds[2]:bounds[3]:ny*1j]
                X, Y = numpy.meshgrid(x, y)
                if levels == None:
                    cset1 = pylab.contourf(X, Y, self.T, 
                    extend = 'both', cmap = cmap)
                else:
                    cset1 = pylab.contourf(X, Y, self.T, levels,
                    extend = 'both', cmap = cmap)
                cset2 = pylab.contour(X, Y, self.T, 
                    cset1.levels, colors = 'k', hold = 'on')
                #for c in cset2.collections:
                #    c.set_linestyle('solid')
            else:
                if self.palette:
                    import Image
                    pal_image = Image.new(size = self.T.shape, mode = 'P')
                    pal_image.putdata(self.flatten())
                    palette = self.expt.experiment.palette
                    pal_image.putpalette(palette)
                    pal_image = pal_image.transpose(Image.ROTATE_270).transpose(Image.FLIP_LEFT_RIGHT)
                    rgb_image = pal_image.convert(mode ='RGB')
                    arr = pylab.array(rgb_image)
                    im = pylab.imshow(arr, aspect = 'auto',
                         origin = 'lower',
                         extent = extent, **self.kwargs)
                else:
                    im = pylab.imshow(self.T, aspect='auto',
                         origin='lower',
                         extent = extent, **self.kwargs)
                self.im = im
            pylab.axis(bounds)
            pylab.xlabel(xlabel, size='x-large')
            pylab.ylabel(ylabel, size='x-large', rotation='horizontal')
        else:
            # 3d dataset. We want to plot to 2d. Need to choose
            # view along one axis
            shape = self.shape
            if (self.last_axis != None) and (axis == None):
                axis = self.last_axis
            if axis == None:
                # infer axis
                if numpy.argmin(shape) == 0: #vts
                    axis = 'vts'
                elif numpy.argmin(shape) == 1: #hts
                    axis = 'hts'
                else: #frame
                    axis = 'frame'
            def get_data(val):
                shape = self.shape
                i = int( round((val - slide_min) / slide_delta))
                val_at_i = slide_min + i * slide_delta
                if axis == 'vts':
                    data = self[i, :, :].T
                    self.x = val_at_i
                elif axis == 'hts':
                    data = self[:, i, :] 
                    self.z = val_at_i
                else: # argmin(shape) == 2: # frame
                    data = self[:, :, i] 
                    self.t = val_at_i
                return data, val_at_i

            if axis == 'vts':
                extent = [self.tmin-self.dt/2, 
                        self.tmax+self.dt/2, 
                        self.zmin-self.dz/2, 
                        self.zmax+self.dz/2]
                bounds = [self.tmin, self.tmax, self.zmin, self.zmax]
                title  = "x = %.2f" % self.xmin
                xlabel = r'$t$'
                ylabel = r'$z$'
                self.orientation = 'tz'
                slide_name = 'x'
                slide_min = self.xmin
                slide_max = self.xmax
                slide_delta = self.dx
                if self.x == None:
                    # set default
                    val = (self.xmin + self.xmax) / 2
                else:
                    val = self.x + slide_delta*shift
                    if val > self.xmax: val = self.xmax
                    if val < self.xmin: val = self.xmin
                self.x = val
                val = self.x
            elif axis == 'hts':
                extent = [self.xmin-self.dx/2, 
                        self.xmax+self.dx/2, 
                        self.tmin-self.dt/2, 
                        self.tmax+self.dt/2]
                bounds = [self.xmin, self.xmax, self.tmin, self.tmax]
                data = self[:, 0, :] 
                title  = "z = %.2f" % self.zmin
                xlabel = r'$x$'
                ylabel = r'$t$'
                self.orientation = 'xt'
                slide_name = 'z'
                slide_min = self.zmin
                slide_max = self.zmax
                slide_delta = self.dz
                if self.z == None:
                    # set default
                    val = (self.zmin + self.zmax) / 2
                else:
                    val = self.z + slide_delta*shift
                    if val > self.zmax: val = self.zmax
                    if val < self.zmin: val = self.zmin
                self.z = val
                val = self.z
            else: # argmin(shape) == 2: # frame
               extent = [self.xmin-self.dx/2, 
                       self.xmax+self.dx/2, 
                       self.zmin-self.dz/2, 
                       self.zmax+self.dz/2]
               bounds = [self.xmin, self.xmax, self.zmin, self.zmax]
               data = self[:, :, 0] 
               title  = "t = %.2f" % self.tmin
               xlabel = r'$x$'
               ylabel = r'$z$'
               self.orientation = 'xz'
               slide_name = 't'
               slide_min = self.tmin
               slide_max = self.tmax
               slide_delta = self.dt
               if self.t == None:
                    # set default
                    val = self.tmin
               else:
                    val = self.t + slide_delta*shift
                    if val > self.tmax: val = self.tmax
                    if val < self.tmin: val = self.tmin
               self.t = val
               val = self.t

            if val == self.last_val and axis == self.last_axis and (not redraw):
                return
                
            data, val = get_data(val)
            if self.palette:
                import Image
                pal_image = Image.new(size = data.T.shape, mode = 'P')
                pal_image.putdata(data.flatten())
                palette = self.expt.experiment.palette
                pal_image.putpalette(palette)
                pal_image = pal_image.transpose(Image.ROTATE_270).transpose(Image.FLIP_LEFT_RIGHT)
                rgb_image = pal_image.convert(mode='RGB')
                arr = pylab.array(rgb_image)
                im = pylab.imshow(arr, aspect='auto',
                     origin='lower',
                     extent = extent, **self.kwargs)
            else:
                im = pylab.imshow(data.T, aspect='auto',
                         origin='lower',
                         extent = extent, **self.kwargs)
            self.im = im
            pylab.axis(bounds)
            pylab.xlabel(xlabel, size='x-large')
            pylab.ylabel(ylabel, size='x-large', rotation='horizontal')
            print "%s: %6.2f < %6.2f < %6.2f" % (slide_name, slide_min, val, slide_max)
            self.last_val = val
            self.last_axis = axis

        self.bounds = bounds
        if self.dim > 1:
            pylab.axis(self.bounds)

        #if im is not None:
        #    if self.colorbar is not None:
        #        #TODO: fix colorbar for new plots
        #        pass
                #self.colorbar.colorbar.set(im)

    def world_to_index(self, x, xmin, xmax, nx):
        if xmax == xmin:
            i = 0
        else:
            i = (nx - 1)  * (x - xmin) / (xmax - xmin)
        return int(round(i))
    def x_to_i(self, x):
        return self.world_to_index(x, self.xmin, self.xmax, self.nx)
    def y_to_j(self, y):
        return self.world_to_index(y, self.ymin, self.ymax, self.ny)
    def z_to_k(self, z):
        return self.world_to_index(z, self.zmin, self.zmax, self.nz)
    def t_to_n(self, t):
        return self.world_to_index(t, self.tmin, self.tmax, self.nt)

    def index_to_world(self, i, xmin, xmax, nx):
        if xmax == xmin:
            x = xmin
        else:
            x = xmin + i * (xmax - xmin) / (nx - 1)
        return float(x)
    def i_to_x(self, i):
        return self.index_to_world(i, self.xmin, self.xmax, self.nx)
    def j_to_y(self, j):
        return self.index_to_world(j, self.ymin, self.ymax, self.ny)
    def k_to_y(self, k):
        return self.index_to_world(k, self.zmin, self.zmax, self.nz)
    def n_to_t(self, n):
        return self.index_to_world(n, self.tmin, self.tmax, self.nt)

    def describe_element(self, coords):
        if self.orientation == 'tz':
            t, z, = coords
            x = self.x
        elif self.orientation == 'xt':
            x, t = coords
            z = self.z
        elif self.orientation == 'xz':
            x, z = coords
            t = self.t
        else:
            return

        if (x < self.xmin-self.dx/2) or (x > self.xmax+self.dx/2) or \
           (z < self.zmin-self.dz/2) or (z > self.zmax+self.dz/2) or \
           (t < self.tmin-self.dt/2) or (t > self.tmax+self.dt/2):
           print 'Out of bounds!'
           return

        i = self.x_to_i(x)
        k = self.z_to_k(z)
        n = self.t_to_n(t)

        x = self.xmin + i*self.dx
        z = self.zmin + k*self.dz
        t = self.tmin + n*self.dt

        # extract out the data given by the bounding box
        dim = len(self.shape)
        if dim == 2:
            if self.nt == 1: # frame
                print "pixel: [%d, %d]" % (i, k),
                print "<==> world: (%.2f, %.2f)" % (x, z),
                data = self[i, k]
            elif self.nx == 1: # vts
                print "pixel: [%d, %d]" % (n, k),
                print "<==> world: (%.2f, %.2f)" % (t, z),
                data = self[n, k]
            elif self.nz == 1: # hts
                print "pixel: [%d, %d]" % (i, n),
                print "<==> world: (%.2f, %.2f)" % (x, t),
                data = self[i, n]
            else:
                return None
        elif dim == 3:
            print "pixel: [%d, %d, %d]" % (i, k, n),
            print "<==> world: (%.2f, %.2f, %.2f)" % (x, z, t),
            data = self[i, k, n]
        print "value: %.4e" % data

    def find_freq(self, coords = None, show = False, method = 'simple'):
        if self.orientation == 'tz':
            if coords == None:
                tmin, zmin, tmax, zmax = \
                        self.tmin, self.zmin, self.tmax, self.zmax
            else:
                tmin, zmin, tmax, zmax = coords
            xmin = self.x
            xmax = self.x
            xlabel = r'$\omega$'
            ylabel = r'$k_z$'
        elif self.orientation == 'xt':
            if coords == None:
                xmin, tmin, xmax, tmax = \
                        self.xmin, self.tmin, self.xmax, self.tmax
            else:
                xmin, tmin, xmax, tmax = coords
            zmin = self.z
            zmax = self.z
            xlabel = r'$k_x$'
            ylabel = r'$\omega$'
        elif self.orientation == 'xz':
            if coords == None:
                xmin, zmin, xmax, zmax = \
                        self.xmin, self.xmin, self.tmax, self.zmax
            else:
                xmin, zmin, xmax, zmax = coords
            tmin = self.t
            tmax = self.t
            xlabel = r'$k_x$'
            ylabel = r'$k_z$'
        else:
            return None

        imin = self.x_to_i(xmin)
        imax = self.x_to_i(xmax)
        if imax < imin: imin, imax = imax, imin
        kmin = self.z_to_k(zmin)
        kmax = self.z_to_k(zmax)
        if kmax < kmin: kmin, kmax = kmax, kmin
        nmin = self.t_to_n(tmin)
        nmax = self.t_to_n(tmax)
        if nmax < nmin: nmin, nmax = nmax, nmin

        #print imin, kmin, nmin, ":", imax, kmax, nmax

        # extract out the data given by the bounding box
        dim = len(self.shape)
        if dim == 2:
            if self.nt == 1: # frame xz
                data = self[imin:imax+1, kmin:kmax+1]
            elif self.nx == 1: # vts tz
                data = self[nmin:nmax+1, kmin:kmax+1]
            elif self.nz == 1: # hts xt
                data = self[imin:imax+1, nmin:nmax+1]
            else:
                return None
        elif dim == 3:
            if self.orientation == 'xz':
                data = self[imin:imax+1, kmin:kmax+1, self.t_to_n(self.t)]
            elif self.orientation == 'tz':
                data = self[self.x_to_i(self.x), kmin:kmax+1, nmin:nmax+1].T
            else:
                data = self[imin:imax+1, self.z_to_k(self.z), nmin:nmax+1]

        # substract off the average
        average = numpy.mean(data)
        data = data - average

        data = Field(data,
            tmin = tmin, tmax = tmax,
            xmin = xmin, xmax = xmax,
            zmin = zmin, zmax = zmax)

        if self.orientation == 'tz':
            if data.nt % 2 == 0:
                f_tmin = -pi/self.dt + 2*pi/self.dt/data.nt
            else:
                f_tmin = -pi/self.dt
            f_tmax = pi/self.dt
            f_xmin = 0.0
            f_xmax = 0.0
            if data.nz % 2 == 0:
                f_zmin = -pi/self.dz + 2*pi/self.dz/data.nz
            else:
                f_zmin = -pi/self.dz
            f_zmax = pi/self.dz
        elif self.orientation == 'xt':
            if data.nt % 2 == 0:
                f_tmin = -pi/self.dt + 2*pi/self.dt/data.nt
            else:
                f_tmin = -pi/self.dt
            f_tmax = pi/self.dt
            if data.nx % 2 == 0:
                f_xmin = -pi/self.dx + 2*pi/self.dx/data.nx
            else:
                f_xmin = -pi/self.dx
            f_xmax = pi/self.dx
            f_zmin = 0.0
            f_zmax = 0.0
        elif self.orientation == 'xz':
            f_tmin = 0.0
            f_tmax = 0.0
            if data.nx % 2 == 0:
                f_xmin = -pi/self.dx + 2*pi/self.dx/data.nx
            else:
                f_xmin = -pi/self.dx
            f_xmax = pi/self.dx
            if data.nz % 2 == 0:
                f_zmin = -pi/self.dz + 2*pi/self.dz/data.nz
            else:
                f_zmin = -pi/self.dz
            f_zmax = pi/self.dz
        else:
            return None


        data_fft = fft.fft2(data)
        powerspectrum = abs(data_fft)**2
        #powerspectrum = powerspectrum / powerspectrum.size**2

        # since data is real, use symmetry
        # row0, col0 contains DC
        if False:
            if len(powerspectrum.shape) == 2:
                d1, d2 = powerspectrum.shape
                powerspectrum = powerspectrum[0:(d1//2+1), 0:(d2//2+1)]
            else:
                d1, d2, d3 = powerspectrum.shape
                powerspectrum = powerspectrum[0:(d1//2+1), 0:(d2//2+1), 0:(d3//2+1)]
        else:
            if len(powerspectrum.shape) == 2:
                d1, d2 = powerspectrum.shape
                powerspectrum = numpy.vstack (( powerspectrum[d1//2+1:, :],
                                         powerspectrum[:d1//2+1, :] ))
                powerspectrum = numpy.hstack (( powerspectrum[:, d2//2+1:],
                                         powerspectrum[:, :d2//2+1] ))
            else:
                # need to rearrange for 3d
                d1, d2, d3 = powerspectrum.shape

        powerspectrum = Field(powerspectrum,
            tmin = f_tmin, tmax = f_tmax,
            xmin = f_xmin, xmax = f_xmax,
            zmin = f_zmin, zmax = f_zmax)
        
        if show:
            pylab.figure()
            powerspectrum.plot(interpolation = 'nearest')
            pylab.jet()
            pylab.title('Power spectrum')
            pylab.xlabel(xlabel, size = 'x-large')
            pylab.ylabel(ylabel, size = 'x-large', rotation = 'horizontal')

           
        index = powerspectrum.argmax()
        i, j = numpy.unravel_index(index, powerspectrum.shape)
        #print "\nMaximum at pixel: [%d, %d]"% (i, j)

        P = powerspectrum
        if P.nt == 1: # frame
            xi = P.xmin + P.dx * (i + numpy.array([-1, 0., +1]))
            eta = P.zmin + P.dz * (j + numpy.array([-1, 0., +1]))
        elif P.nx == 1: # vts
            xi = P.tmin + P.dt * (i + numpy.array([-1, 0., +1]))
            eta = P.zmin + P.dz * (j + numpy.array([-1, 0., +1]))
        elif P.nz == 1: # hts
            xi = P.xmin + P.dx * (i + numpy.array([-1, 0., +1]))
            eta = P.tmin + P.dt * (j + numpy.array([-1, 0., +1]))
        else:
            print "find_freq currently only handle 2d slices"
            return None

        deltax = xi[1] - xi[0]
        deltay = eta[1] - eta[0]
        # define plusminus symbol
        # Unicode broken on somemachines:
        #pm = u"\u00B1"
        pm = "+-"
        if method == 'simple':
            print "  Simple maximum: (%.2f %s %.2f, %.2f %s %.2f) @ [%d, %d]" % \
                (xi[1], pm, deltax/2, eta[1], pm, deltay/2 , i, j)
            return xi[1], eta[1]

        def getextremum(x1, x2, x3, y1, y2, y3):
            if (x1 == x2) or (x1 == x3) or (x2 == x3):
                return None
            m21 = (y2-y1)/(x2-x1)
            m32 = (y3-y2)/(x3-x2)
            A = (m21-m32)/(x1-x3)
            B = m21 - (x1+x2)*A
            C = y1 - (A*x1 + B)*x1

            if (A == 0):
                return None

            xm = -0.5*B/A
            ym = C-0.25*B*B/A

            # if A > 0 : minimum
            # else : maximum

            #print x1, x2, x3, y1, y2, y3
            #print m21, m32, A, B, C

            return xm, ym

        def interpolate(xval, x1, x2, x3, y1, y2, y3):
            d21 = x2-x1
            d32 = x3-x2
            d13 = x1-x3
            p11 = x1*x1
            p13 = x1*x3
            p22 = x2*x2
            p21 = x2*x1
            p33 = x3*x3
            p32 = x3*x2
            ipd123 = 1.0/(d21*d32*d13)
            A = -ipd123*(y1*d32+y2*d13+y3*d21)
            B = ipd123*(y1*(p33-p22)+y2*(p11-p33)+y3*(p22-p11))
            C = -ipd123*(y1*p32*d32+y2*p13*d13+y3*p21*d21)

            yval = (A*xval + B)*xval + C
            return yval

                #print "Searching in (%.2f, %.2f)" % (xi[0], xi[2]),  \
        #      "by (%.2f, %.2f) box" % (eta[0], eta[2])
        #print "input: %.2f, %.2f, %.2f : %.2e, %.2e, %.2e" % \
        #  (eta[0], eta[1], eta[2], P[i-1, j-1], P[i-1, j], P[i-1, j+1])
        f1, p1 = getextremum(eta[0], eta[1], eta[2],
                             P[i-1, j-1], P[i-1, j], P[i-1, j+1]) 
        #print "output: %.2f, %.2e" % (f1, p1)
        f2, p2 = getextremum(eta[0], eta[1], eta[2],
                             P[i, j-1], P[i, j], P[i, j+1]) 
        f3, p3 = getextremum(eta[0], eta[1], eta[2],
                             P[i+1, j-1], P[i+1, j], P[i+1, j+1]) 
        #print "in columns, maxes are at (%.2f, %.2f, %.2f)" %(f1, f2, f3)
        freq1, p0 = getextremum(xi[0], xi[1], xi[2], p1, p2, p3) 
        freq2 = interpolate(freq1, xi[0], xi[1], xi[2], f1, f3, f3)
        if method == 'parabolic':
            print "  Parabolic interpolation: (%.2f, %.2f)" % (freq1, freq2),
            if freq1 < xi[0] or freq1 > xi[2] or freq2 < eta[0] or freq2 > eta[2]:
                print "(invalid)",
            print
            return freq1, freq2

        # find max using gaussian fit
        from scipy import optimize

        def gaussian(height, center_x, center_y, width_x, width_y):
            """Returns a gaussian function with the given parameters"""
            width_x = float(width_x)
            width_y = float(width_y)
            return lambda x, y: height*numpy.exp(
                -(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)

        def moments(data):
            """Returns (height, x, y, width_x, width_y)
            the gaussian parameters of a 2D distribution by calculating its
            moments """
            total = data.sum()
            X, Y = numpy.indices(data.shape)
            x = (X*data).sum()/total
            y = (Y*data).sum()/total
            col = data[:, int(y)]
            width_x = numpy.sqrt(abs((numpy.arange(col.size)-y)**2*col).sum()/col.sum())
            row = data[int(x), :]
            width_y = numpy.sqrt(abs((numpy.arange(row.size)-x)**2*row).sum()/row.sum())
            height = data.max()
            return height, x, y, width_x, width_y

        def fitgaussian(data):
            """Returns (height, x, y, width_x, width_y)
            the gaussian parameters of a 2D distribution found by a fit"""
            params = moments(data)
            errorfunction = lambda p: numpy.ravel(gaussian(*p)(*numpy.indices(data.shape)) -
                                                data)
            p, success = optimize.leastsq(errorfunction, params)
            return p

        subset = numpy.asarray(powerspectrum[i-1:i+2, j-1:j+2])
        params = fitgaussian(subset)
        (height, x, y, width_x, width_y) = params
        # convert back to 'real' pixel values
        x = x + i - 1
        y = y + j - 1
        if P.orientation == 'xt':
            x = P.xmin + x*P.dx
            y = P.tmin + y*P.dt
            width_x = width_x*P.dx
            width_y = width_y*P.dt
            X = numpy.arange(P.xmin, P.xmax + P.dx, P.dx)
            Y = numpy.arange(P.tmin, P.tmax + P.dt, P.dt)
        elif P.orientation == 'tz':
            x = P.tmin + x*P.dt
            y = P.zmin + y*P.dz
            width_x = width_x*P.dt
            width_y = width_y*P.dz
            X = numpy.arange(P.tmin, P.tmax+P.dt, P.dt)
            Y = numpy.arange(P.zmin, P.zmax+P.dz, P.dz)
        elif P.orientation == 'xz':
            x = P.xmin + x*P.dx
            y = P.zmin + y*P.dz
            width_x = width_x*P.dx
            width_y = width_y*P.dz
            X = numpy.arange(P.xmin, P.xmax+P.dx, P.dx)
            Y = numpy.arange(P.zmin, P.zmax+P.dz, P.dz)
        else:
            print 'unimplemented orientation!'
        params = [height, x, y, width_x, width_y]

        #print "delta1 = %.2f, delta2 = %.2f" % (width_x, width_y)

        if show:
            X, Y = numpy.meshgrid(X, Y)
            fit = gaussian(*params)
            F = fit(X, Y)
            pylab.contour(X, Y, F, cmap = pylab.cm.copper)
            #ax = pylab.gca()
            #pylab.text(0.95, 0.05, """
            #   x : %.1f
            #   y : %.1f
            #   width_x : %.1f
            #   width_y : %.1f""" %(x, y, width_x, width_y),
            #   fontsize = 16, horizontalalignment = 'right',
            #   verticalalignment = 'bottom', transform = ax.transAxes)

        freq1 = x
        freq2 = y
        if method == 'gaussian':
        # logging
        #    print "  Gaussian fit: (%.2f, %.2f)" % (x, y),
        #    print "  dx = %.2f, dy = %.2f" % (deltax, deltay),
        #    print "  wx = %.2f, wy = %.2f" % (width_x, width_y)
             return (freq1, freq2)

    def blur(self, sigma = 0.3):
        """ Smooth the field in-place using a gaussian filter """
        if self.dim == 2:
            if self.orientation == 'tz':
                self[:] = ndimage.gaussian_filter(self,  [sigma/self.dt, sigma/self.dz])
            elif self.orientation == 'xt':
                self[:] = ndimage.gaussian_filter(self,  [sigma/self.dx, sigma/self.dt])
            else:
                self[:] = ndimage.gaussian_filter(self,  [sigma/self.dx, sigma/self.dz])
        elif self.dim == 3:
            self[:] = ndimage.gaussian_filter(self,  [sigma/self.dx, sigma/self.dz, sigma/self.dt])
        else:
            pass
        
    def filter(self):
        mask = numpy.array( [[ -1, 0, +1]] )
        filtered = ndimage.correlate(self, mask)
        filtered = ndimage.gaussian_laplace(self, 3)
        filtered = ndimage.gaussian_gradient_magnitude(self, 2)
        filtered = ndimage.correlate(self, mask)
        filtered = ndimage.gaussian_laplace(self, 3)
        filtered = ndimage.correlate(self, [[-1, 0, 1]])
        filtered = ndimage.gaussian_filter(filtered, 2)

        self[:] = filtered[:]
        
    def save(self, outfile):
        dim = len(self.shape)
        if dim == 0:
            print '0d plot'
        elif dim == 1:
            print '1d plot',
            print ' should save as xpt - to be written'
        elif dim == 2:
             # determine frame, hts or vts:
            if self.nt == 1: # frame
               extent = [self.xmin, self.xmax, self.zmin, self.zmax]
            elif self.nx == 1: # vts
               extent = [self.tmin, self.tmax, self.zmin, self.zmax]
            elif self.nz == 1: # hts
               extent = [self.xmin, self.xmax, self.tmin, self.tmax]
            else:
                print "Nonstandard 2-d field data. I don't know how to save this as an xyp file"
                return

            from xplot import writeXYplot
            writeXYplot(self, extent[0], extent[1], extent[2], extent[3], outfile)
        else: # dim == 3
            print " saving unimplemented for 3d plots"

class Experiment(object):
    "Wrapper class to examine experimental data"
    def __new__(exptcls, dbname, exptname):

        # test for existance of db
        if dbname[-3:] != '.h5':
            dbname = dbname + '.h5'

        try:
            # open for read/write
            h5file = tables.openFile(dbname, mode = "r+")
        except IOError:
            print 'Unable to open database %s' % dbname
            return None

        if h5file == None:
            return None

        # test for existance of expt
        if exptname[0] != '/':
            exptname = '/' + exptname

        if exptname in h5file:
            # create the object
            expt = object.__new__(exptcls)

            expt.h5file = h5file
            expt.dbname = dbname
            expt.experiment = h5file.getNode(exptname)
            expt.exptname = exptname
        else:
            h5file.close()
            print "Experiment %s not found in %s" % (exptname, dbname)
            return None

        try:
            expt.dv = expt.experiment.dv
        except tables.exceptions.NoSuchNodeError:
            print "Warning: invalid experiment--no DV imported"
            h5file.close()
            return None

        expt.nRows, expt.nCols, expt.nFrames = expt.dv.shape # these parameters should be in the h5 db 

        # load world grid from db (if defined)
        if 'xmin' in expt.dv.attrs:
            expt.xmin = float(expt.dv.attrs.xmin)
            expt.xmax = float(expt.dv.attrs.xmax)
            expt.zmin = float(expt.dv.attrs.zmin)
            expt.zmax = float(expt.dv.attrs.zmax)
            expt.tmin = float(expt.dv.attrs.tmin)
            expt.tmax = float(expt.dv.attrs.tmax)
            expt.dx = (expt.xmax - expt.xmin) / (expt.nCols - 1.0)
            expt.dz = (expt.zmax - expt.zmin) / (expt.nRows - 1.0)
            expt.dt = (expt.tmax - expt.tmin) / (expt.nFrames - 1.0)
        else:
            expt.xmin = 0
            expt.xmax = expt.nCols - 1
            expt.dx = 1

            expt.zmin = 0
            expt.zmax = expt.nRows - 1
            expt.dz = 1

            expt.tmin = 0
            expt.tmax = expt.nFrames - 1
            expt.dt = 1

        if 'date_import' in expt.dv.attrs:
            expt.date_import = expt.dv.attrs.date_import
        else:
            expt.date_import = "n/a"

        return expt
        
    def close(self):
        """
        Close the connection to the hdf5 database
        """
        self.h5file.close()
       
    def load_view(self, viewname, 
                  iindex = slice(None, None, None), 
                  kindex = slice(None, None, None), 
                  nindex = slice(None, None, None)):
        """
        Loads viewname from the current experiment and returns a Field.
        index(s) allow for slicing of the view.
        
        If viewname is not found, None is returned.
        """

        # extract data using pixel coords

        if viewname not in self.experiment:
            return None

        view = self.h5file.getNode(self.experiment, name = viewname)
        dim = len(view.shape)

        if dim == 1:
            print "Error: loading 1D views is not supported (yet)"
            return None
        elif dim == 2:
            #slicing only works for hts now

            xmin = view.attrs.xmin
            xmax = view.attrs.xmax
            zmin = view.attrs.zmin
            zmax = view.attrs.zmax
            tmin = view.attrs.tmin
            tmax = view.attrs.tmax

            nt, nz = view.shape

            data = view[nindex, kindex]

            kmin, kmax = self.lookup_bound(kindex, 0, nz)
            nmin, nmax = self.lookup_bound(nindex, 0, nt)

            dz = (zmax - zmin) / (nz - 1)
            dt = (tmax - tmin) / (nt - 1)

            tmin = view.attrs.tmin + dt * nmin
            tmax = view.attrs.tmin + dt * nmax
            zmin = view.attrs.zmin + dz * kmin
            zmax = view.attrs.zmin + dz * kmax
            
            data = Field(data, expt = self,
                tmin = tmin, tmax = tmax,
                xmin = xmin, xmax = xmax,
                zmin = zmin, zmax = zmax)
            return data
        elif dim == 3:
            nx, nz, nt = view.shape
            imin, imax = self.lookup_bound(iindex, 0, nx)
            kmin, kmax = self.lookup_bound(kindex, 0, nz)
            nmin, nmax = self.lookup_bound(nindex, 0, nt)

            xmin = view.attrs.xmin
            xmax = view.attrs.xmax
            zmin = view.attrs.zmin
            zmax = view.attrs.zmax
            tmin = view.attrs.tmin
            tmax = view.attrs.tmax
            dx = (xmax - xmin) / (nx - 1)
            dz = (zmax - zmin) / (nz - 1)
            dt = (tmax - tmin) / (nt - 1)

            data = view[iindex, kindex, nindex]
            tmin = view.attrs.tmin + dt * nmin
            tmax = view.attrs.tmin + dt * nmax
            xmin = view.attrs.xmin + dx * imin 
            xmax = view.attrs.xmin + dx * imax
            zmin = view.attrs.zmin + dz * kmin
            zmax = view.attrs.zmin + dz * kmax
            data = Field(data, expt = self,
                tmin = tmin, tmax = tmax,
                xmin = xmin, xmax = xmax,
                zmin = zmin, zmax = zmax)
            if data.orientation == 'tz':
                data = Field(data.T, expt = self,
                    tmin = tmin, tmax = tmax,
                    xmin = xmin, xmax = xmax,
                    zmin = zmin, zmax = zmax)

            return data
        else:
            print "unsupported dimension for view"
            return None

    def save_view(self, segment, viewname, force = False):
        """
        Store segment in the database under the current experiment
        with the name viewname.
        Existing views are not replaced unless force = True
        """
        if viewname in self.experiment:
            if force:
                print "View of the same name already exists. Replace forced."
                self.h5file.removeNode(self.experiment, name = viewname)
            else:
                print "View of the same name already exists. Not saved."
                return

        view = self.h5file.createArray(self.experiment, viewname, 
                            numpy.array(segment), "Saved View")

        view.attrs.xmin = segment.xmin
        view.attrs.xmax = segment.xmax
        view.attrs.zmin = segment.zmin
        view.attrs.zmax = segment.zmax
        view.attrs.tmin = segment.tmin
        view.attrs.tmax = segment.tmax

    def get(self, iindex = None, jindex = None, nindex = None):
        # extract data using pixel coords

        imin, imax = self.lookup_bound(iindex, 0, self.nRows)
        jmin, jmax = self.lookup_bound(jindex, 0, self.nCols)
        nmin, nmax = self.lookup_bound(nindex, 0, self.nFrames)
         
        tmin = self.tmin + self.dt * nmin
        tmax = self.tmin + self.dt * nmax
        xmin = self.xmin + self.dx * jmin 
        xmax = self.xmin + self.dx * jmax
        zmin = self.zmax - self.dz * imax
        zmax = self.zmax - self.dz * imin

        data = self.dv[iindex, jindex, nindex]

        dim = len(data.shape)
        if zmax - zmin != 0: # z data in output
            if dim == 1:
                data = data[::-1] # z should be increasing
            elif dim == 2:
                data = data.T[:, ::-1] # z, t -> t, z
            else: # dim == 3
                data = data.transpose(1, 0, 2)[:, ::-1, :]

        data = Field(data, expt = self,
                tmin = tmin, tmax = tmax,
                xmin = xmin, xmax = xmax,
                zmin = zmin, zmax = zmax)

        return data
        
    def lookup_i(self, z):
        """ determine i index associated with z coordinate """
        if z == None:
            i = None
        else:
            i = int((self.zmax - z) / self.dz)
        return i

    def lookup_j(self, x):
        """ determine j index associated with x coordinate """
        if x == None:
            j = None
        else:
            j = int((x - self.xmin) / self.dx)
        return j

    def lookup_n(self, t):
        """ determine n index associated with t coordinate """
        if t == None:
            n = None
        else:
            n = int((t - self.tmin) / self.dt)
        return n

    def lookup_bound(self, index, min, max):
        """ """
        if type(index) != slice:
            # index is just a single value?
            # min and max are the same, that is the value index
            min = index
            max = index
        else:
            # index is a slice
            if index.start != None:
                # index has a lower bound, use this as the min
                min = index.start
            if index.stop != None:
                # index has an upper bound, use this as the max
                max = index.stop
            # if index has no bounds, then use values of min, max that were passed in
        return (min, max)

    def __getitem__(self, index):
        # expt[xslice, zslice, tslice]
        # extracts a subset of the experimental data in world coords
        if len(index) != 3:
            raise "incorrect number of indicies"
            return None
        xindex = index[0]
        zindex = index[1]
        tindex = index[2]
        
        if type(xindex) is slice:
            jstart = self.lookup_j(xindex.start)
            jstop = self.lookup_j(xindex.stop)
            if xindex.step == None:
                jstep = None
            else:
                jstep = int(xindex.step / self.dx)
            jindex = slice(jstart, jstop, jstep)
        else:
            jindex = self.lookup_j(xindex)
        xmin, xmax = self.lookup_bound(xindex, self.xmin, self.xmax)
            
        if type(zindex) is slice:
            istart = self.lookup_i(zindex.stop)
            istop = self.lookup_i(zindex.start)
            if zindex.step == None:
                istep = None
            else:
                istep = int(zindex.step / self.dz)
            iindex = slice(istart, istop, istep)
        else:
            iindex = self.lookup_i(zindex)
        zmin, zmax = self.lookup_bound(zindex, self.zmin, self.zmax)

        if type(tindex) is slice:
            nstart = self.lookup_n(tindex.start)
            nstop = self.lookup_n(tindex.stop)
            if tindex.step == None:
                nstep = None
            else:
                nstep = int(tindex.step / self.dt)
            nindex = slice(nstart, nstop, nstep)
        else:
            nindex = self.lookup_n(tindex)
        tmin, tmax = self.lookup_bound(tindex, self.tmin, self.tmax)

        print "i =", iindex, "j =", jindex, "n =", nindex
        data = numpy.array(self.dv[iindex, jindex, nindex])

        dim = len(data.shape)
        if zmax - zmin != 0: # z data in output
            if dim == 1:
                data = data[::-1] # z should be increasing
            elif dim == 2:
                data = data.T[:, ::-1] # z, t -> t, z
            else: # dim == 3
                data = data.transpose(1, 0, 2)[:, ::-1, :]

        data = Field(data, expt = self, xmin = xmin, xmax = xmax, 
                           zmin = zmin, zmax = zmax,
                           tmin = tmin, tmax = tmax)
        return data

    def pixel_to_world(self, pixel):
        A = self.transformation[0]
        b = self.transformation[1]
        pixel = numpy.array(pixel)
        world = numpy.array( A*pixel + b).reshape(2, )
        return world

    def world_to_pixel(self, world):
        A = self.transformation[0]
        b = self.transformation[1]
        Ainv = numpy.linalg.inv(A)
        world = numpy.array(world)
        pixel = numpy.array( Ainv*(world-b)).reshape(2, )
        return pixel

    def set_worldgrid(self, pixelcoords = (), worldcoords = ()):
        if len(pixelcoords) != len(worldcoords):
            print "pixel and world coords must be the same length"
            return

        # solve for transformation
        M = numpy.ones((6, 3), dtype = float)
        M[:, :2] = pixels
        soln =  lstsq(M, world)[0]
        A = numpy.matrix(soln[:2, :]).T
        b = soln[2, :]
        self.transformation = (A, b)

        # determine extent

    def set_worldgrid(self,
                      xmin = 0.0, xmax = 1.0, 
                      zmin = 0.0, zmax = 1.0,
                      tmin = 0.0, tmax = None):
        """ set and save world coordinates bounds """
        self.xmin = xmin
        self.xmax = xmax
        self.dx = (xmax - xmin) / (self.nCols - 1.0)
        self.zmin = zmin
        self.zmax = zmax
        self.dz = (zmax - zmin) / (self.nRows - 1.0)
        self.tmin = tmin
        if tmax == None: #special case for time
            tmax = self.tmin + self.nFrames * self.dt
        self.tmax = tmax
        self.dt = (tmax - tmin) / (self.nFrames - 1.0)

        # save in db
        self.dv.attrs.xmin = xmin
        self.dv.attrs.xmax = xmax
        self.dv.attrs.zmin = zmin
        self.dv.attrs.zmax = zmax
        self.dv.attrs.tmin = tmin
        self.dv.attrs.tmax = tmax

    def __str__(self):
        return str(self.experiment)
