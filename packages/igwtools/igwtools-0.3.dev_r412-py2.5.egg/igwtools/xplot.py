"""
Utilities for reading and writing XYP and XPT files.

XYP and XPT are file formats developed by Bruce Sutherland.

xpt file format:

      data.xpt    <filename>
      xmin
      xmax
      ymin
      ymax
      nc          <number of curves>
      np1         <number of points for curve 1>
      x_1       y_1
      x_2       y_2
      ..    ..
      x_np1     y_np1
      np2         <number of points for curve 2>
      ...etc

xyp file format:

      data.xyp    <filename>
      xmin        <span and range of plot>
      xmax
      ymin
      ymax
      nc          <number of contour plots>
      nx1         <number of x and y points for 1st contour plot>
      ny1         
      cllow       <contour intervals>
      clhigh
      clint
      f1_x1_y1    <data>
      f1_x2_y1
      ..
      f1_xnx1_y1
      f1_x1_y2
      ..
      nx2         <number of x and y points for 2nd contour plot>
      ny2         
      c2low       <contour intervals>
      c2high
      c2int
      f2_x1_y1
      ...etc

   Note that if cint<0.0 then the following data is taken to represent
   header information for the plot.
"""

import numpy
import pylab
import string
import sys
from optparse import OptionParser
from igwtools import __version__
from tools import Field

class xpt:
    def __init__(self, header, dataset):
        self.header = header
        self.dataset = dataset
    def __str__(self):
        return self.header['title']
    def __repr__(self):
        return self.header['title']
    def write(self, filename):
        outfile = open(filename,'wt')
        outfile.write(self.header['title'] + '\n')
        for i in ('xmin','xmax','ymin','ymax'):
            outfile.write(str(self.header[i]) + '\n')
        for (np, x, y) in self.dataset:
            outfile.write(str(np) + '\n')
            for i in range(np):
                outfile.write("%s %s\n" % x[i], y[i])
        outfile.close()
    def plot(self):
        for (np, x, y) in self.dataset:
           pylab.plot(x, y)
        pylab.axis('tight')

        title_str = self.header['title'].replace('_', '\_')
        print self.header['title']
        print title_str

        pylab.title(title_str)
 
class xyp:
    def __init__(self, header, dataset):
        self.header = header
        self.dataset = dataset
        self.title = header['title']
        self.xmin = header['xmin']
        self.xmax = header['xmax']
        self.ymin = header['ymin']
        self.ymax = header['ymax']
        self.nc = header['nc']
    def __str__(self):
        return self.header['title']
    def __repr__(self):
        return self.header['title']
    def write(self, filename):
        outfile = open(filename,'wt')
        # write out header
        for i in ('title','xmin','xmax','ymin','ymax','nc'):
           outfile.write(str(getattr(self,i)) + '\n')
        for (hdr, data) in self.dataset:
           for i in ('nx','ny','cllow','clhigh','clinc'):
               outfile.write(str(hdr[i]) + '\n')
           for x in data:
               outfile.write(str(x) + '\n')
        outfile.close()
    def plot_contours(self):
        "Plot the first xyp of the dataset as an image" 
        hdr, data = self.dataset[0]
        dx = (self.header['xmax'] - self.header['xmin']) / (hdr['nx'] - 1.0)
        dy = (self.header['ymax'] - self.header['ymin']) / (hdr['ny'] - 1.0)
        A = numpy.array(data).reshape((hdr['nx'],hdr['ny']))
        pylab.transpose(A)
        x = [self.header['xmin'] + i*dx for i in range(hdr['nx'])]
        y = [self.header['ymin'] + i*dy for i in range(hdr['ny'])]
        X, Y = pylab.meshgrid(x,y)
        
        pylab.contour(X, Y, A)
        #pylab.pcolor(X, Y, A, shading='flat')

        pylab.axis('tight')
        pylab.xlabel('x')
        pylab.ylabel('y')

        title_str = self.header['title'].replace('_', '\_')
        pylab.title(title_str)

        pylab.colorbar()
    def data(self):
        hdr, data = self.dataset[0]
        A = numpy.array(data).reshape(hdr['ny'],hdr['nx'])
        return A.T, self.header['xmin'], self.header['xmax'], self.header['ymin'], self.header['ymax']
    def plot(self, **kwargs):
        "Plot the first xyp of the dataset as an image" 
        hdr, data = self.dataset[0]
        A = numpy.array(data).reshape(hdr['ny'],hdr['nx'])
        pylab.imshow(A, aspect='auto',
                    origin = 'lower',
                    extent = [self.header['xmin'], self.header['xmax'],
                              self.header['ymin'], self.header['ymax']],
                    **kwargs)
        pylab.xlabel('x')
        pylab.ylabel('y')
        title_str = self.header['title'].replace('_', '\_')
        pylab.title(title_str)
        pylab.colorbar()
    
def readXplot_new(filename):
    "Returns a Field object"
    infile = open(filename,'r')
    input = infile.readlines()
    infile.close()

    # strip off eol using [:-1]
    title = input[0][:-1] # read in title
    xmin = float(input[1][:-1])
    xmax = float(input[2][:-1])
    ymin = float(input[3][:-1])
    ymax = float(input[4][:-1])
    nc = int(input[5][:-1])
        
    for c in range(nc):
        np = int(input[6][:-1])
        #convert list of strings pairs to list of float pairs
        print  np, nc, xmin, xmax, ymin, ymax
        data = [x.split() for x in input[c+7:c+7+np]]
        data = [(float(x[0]), float(x[1])) for x in data]
        data = numpy.array(data)
        data = data[:,0]
        print data
        print data.shape
        
    #return Field(data[1], xmin = xmin, xmax = xmax)
    print ymin, ymax
    return Field(data, xmin = ymin, xmax = ymax)

def readXplot(filename):
    "Returns a xpt object"
    infile = open(filename)

    # strip off eol using [:-1]
    header = {}
    header['title'] = infile.readline()[:-1]
    for i in ('xmin','xmax','ymin','ymax'):
        header[i]  = float(infile.readline()[:-1])
    header['nc']  = int(infile.readline()[:-1])
    dataset = []
    for c in range(header['nc']):
        np = int(infile.readline()[:-1])
        x = []
        y = []
        for i in range(np):
           xypair = string.split(infile.readline())
           x.append(float(xypair[0]))
           y.append(float(xypair[1]))
        dataset.append((np,x,y))

    infile.close()
    return xpt(header,dataset)

def writeXYplot(x, xmin, xmax, ymin, ymax, title):
    header = {}
    header['title'] = title
    header['xmin'] = xmin
    header['xmax'] = xmax
    header['ymin'] = ymin
    header['ymax'] = ymax
    header['nc']  = 1

    hdr = {}
    nrows, ncols = x.shape 
    hdr['nx'] = nrows
    hdr['ny'] = ncols
    hdr['cllow'] = 1
    hdr['clhigh'] = 1
    hdr['clinc'] = 1

    data = x.T.reshape(ncols*nrows,).tolist()

    dataset = [(hdr, data)]

    xyp(header,dataset).write(title)

def readXYplot(filename, orientation = 'xz'):
    "returns a Field from an .xyp file"
    "need to add option which determines frames vs hts vs vts"
    "currently, it assumes xz data"

    infile = open(filename,'r')
    input = infile.readlines()
    infile.close()

    # read in title
    # strip off eol using [:-1]
    title = input[0][:-1]

    # read in bounds of data
    if orientation == 'xz':
        xmin = float(input[1])
        xmax = float(input[2])
        zmin = float(input[3])
        zmax = float(input[4])
        tmin = 0.0
        tmax = 0.0
    elif orientation == 'tz':
        xmin = 0.0
        xmax = 0.0
        tmin = float(input[1])
        tmax = float(input[2])
        zmin = float(input[3])
        zmax = float(input[4])
    elif orientation == 'xt':
        xmin = float(input[1])
        xmax = float(input[2])
        tmin = float(input[3])
        tmax = float(input[4])
        zmin = 0.0
        zmax = 0.0
    else:
        print "invalid orientation"
        return None

    nc = int(input[5])
    if nc != 1:
        print "Warning! readXYplot currently only support one xyp per file."
        print "  reading last plot only out of", nc

    # currently assuming nc = 1
    for c in range(nc):
        nx = int(input[c+6])
        ny = int(input[c+7])
        cllow = float(input[c+8])
        clhigh = float(input[c+9])
        clinc = float(input[c+10])
        #convert list of strings to list of floats
        data = [float(x) for x in input[c+11:c+11+nx*ny]]
        data = numpy.array(data).reshape(ny,nx).T
        # should append this data to a master data array here!

    f = Field(data, xmin = xmin, xmax = xmax, zmin = zmin, zmax = zmax, tmin=tmin, tmax=tmax)
    f.title = title
    return f


# entry point
def xlook():
    usage = "%prog [options] xptfile"
    parser = OptionParser(usage=usage, version="%prog (igwtools " +
            __version__+ ")")
    parser.add_option("-s", "--save",
                      help="save the image (fileformat determined by extension)")
    parser.add_option("--xlabel",
                      help="x-axis label")
    parser.add_option("--ylabel",
                      help="y-axis label")
    
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("needs one argument")

    xpt = readXplot(args[0])

    xpt.plot()

    if options.xlabel != None:
        pylab.xlabel(options.xlabel)
    if options.ylabel != None:
        pylab.ylabel(options.ylabel)

    if options.save:
        pylab.savefig(options.save)
    else:
        pylab.show()

# entry point
def xylook():
    usage = """%prog [options] <xypfile>

This tool is useful for data exploration of .xyp files.  Currently,
it only support one plot per .xyp file. The -h option gives the full usage."""
    parser = OptionParser(usage=usage, version="%prog (igwtools " + __version__
            + ")")
    parser.add_option("-s", "--save",
                      help="save the image (fileformat determined by extension)")
    parser.add_option("--vmin", type="float", dest="vmin",
                      help="colourbar minimum" )
    parser.add_option("--vmax", type="float", dest="vmax",
                      help="colourbar maximum" )
    parser.add_option("--cmap",
                      help="select a colour map" )
    parser.add_option("--list_cmaps", action="store_true",
                      help="print a list of available colour maps" )
    parser.add_option("--mask",
                      help="MASK is an .xyp file  of the same dimensions as the target xypfile which is shown behind in grayscale")
    parser.add_option("-i", 
                      "--interpolation", dest="interpolation", default='bicubic',

                      help="interpolation mode: nearest, bicubic [default: %default]")
    parser.add_option("--xlabel",
                      help="x-axis label")
    parser.add_option("--ylabel",
                      help="y-axis label")

    (options, args) = parser.parse_args()

    if options.list_cmaps:
        print "Available colormaps are:"
        print pylab.cm.cmapnames

    numplots = len(args)
    if numplots != 1:
        parser.error("needs one argument")

    xyp = readXYplot(args[0])
    if options.mask:
        mask = readXYplot(options.mask)
        mask.plot(interpolation = options.interpolation, cmap=pylab.cm.gray)
        pylab.hold(True)
        xyp.plot(interpolation = options.interpolation,
             vmin = options.vmin, vmax = options.vmax,
             cmap = pylab.cm.get_cmap(options.cmap), alpha=0.6)
    else:
        xyp.plot(interpolation = options.interpolation,
             vmin = options.vmin, vmax = options.vmax,
             cmap = pylab.cm.get_cmap(options.cmap))

    pylab.title(xyp.title)
    pylab.colorbar()
    if options.xlabel != None:
        pylab.xlabel(options.xlabel)
    if options.ylabel != None:
        pylab.ylabel(options.ylabel)

    if options.save:
        pylab.savefig(options.save)
    else:
        pylab.show()

# entry point
def xydiff():
    usage = """%prog [options] <xypfile1> <xypfile2>

This tool works like diff for .xyp files.
The -h option gives the full usage."""
    parser = OptionParser(usage=usage, version="%prog (igwtools " + __version__
            + ")")
    parser.add_option("-s", "--save",
                      help="save the image (fileformat determined by extension)")
    parser.add_option("--vmin", type="float", dest="vmin",
                      help="colourbar minimum" )
    parser.add_option("--vmax", type="float", dest="vmax",
                      help="colourbar maximum" )
    parser.add_option("--cmap",
                      help="select a colour map" )
    parser.add_option("--list_cmaps", action="store_true",
                      help="print a list of available colour maps" )
    parser.add_option("-i", 
                      "--interpolation", dest="interpolation", default='nearest',

                      help="interpolation mode: nearest, bicubic [default: %default]")
    parser.add_option("--xlabel",
                      help="x-axis label")
    parser.add_option("--ylabel",
                      help="y-axis label")

    (options, args) = parser.parse_args()

    if options.list_cmaps:
        print "Available colormaps are:"
        print pylab.cm.cmapnames

    numplots = len(args)
    if numplots != 2:
        parser.error("needs two arguments")

    #assume both xyp files have the same dimensions and sizes
    file1 = args[0]
    file2 = args[1]

    xyp1 = readXYplot(file1)
    xyp2 = readXYplot(file2)

    pylab.figure(figsize=(15,5))

    NUM_STD_DEVS = 4
    if options.vmax == None:
        options.vmax = xyp1.std() * NUM_STD_DEVS
    if options.vmin == None:
        options.vmin = -options.vmax

    pylab.subplot(131)
    xyp1.plot(interpolation = options.interpolation, 
              vmin = options.vmin, vmax = options.vmax,
              cmap = pylab.cm.get_cmap(options.cmap))
    pylab.title(file1)
    pylab.colorbar()
    if options.xlabel != None:
        pylab.xlabel(options.xlabel)
    if options.ylabel != None:
        pylab.ylabel(options.ylabel)


    pylab.subplot(132)
    xyp2.plot(interpolation = options.interpolation, 
              vmin = options.vmin, vmax = options.vmax,
              cmap = pylab.cm.get_cmap(options.cmap))
    pylab.title(file2)
    pylab.colorbar()
    if options.xlabel != None:
        pylab.xlabel(options.xlabel)
    if options.ylabel != None:
        pylab.ylabel(options.ylabel)


    pylab.subplot(133)
    diff = xyp1 - xyp2

    vmax = diff.std() * NUM_STD_DEVS
    vmin = -vmax

    # hack to get diff to be a well defined field again
    diff = Field(diff, xmin = xyp1.xmin, xmax = xyp1.xmax,
                       zmin = xyp1.zmin, zmax = xyp1.zmax)

    diff.plot(interpolation = options.interpolation, 
              vmin = vmin, vmax = vmax,
              cmap = pylab.cm.get_cmap(options.cmap))
    pylab.title('%s - %s' % (file1, file2))
    pylab.colorbar()
    if options.xlabel != None:
        pylab.xlabel(options.xlabel)
    if options.ylabel != None:
        pylab.ylabel(options.ylabel)

    # compute relative difference
    norm1 = pylab.sqrt((xyp1**2).sum())
    norm2 = pylab.sqrt((xyp2**2).sum())
    normdiff = pylab.sqrt((diff**2).sum())
    print "norm of %s = %f" % (file1, norm1)
    print "norm of %s = %f" % (file2, norm2)
    print "norm of difference = %f" % normdiff
    reldifference = normdiff / norm1
    print "relative difference = %f" % reldifference

    if options.save:
        pylab.savefig(options.save)
    else:
        pylab.show()


def testcases():
    # Test cases

    filename = 'xypfile.xyp'
    header = {'title':'Test XYP file', 'xmin':0.0,'xmax':1.0,'ymin':0.0,'ymax':1.0}
    dataset = [ {'nc':0}, [] ]
    data = xyp(header,dataset)
    data.write(filename)

    #data2 = readXYplot(filename)
    #data2.write(filename + '2')
    #print 'Write/Read test',
    #if data == data2:
    #   print 'passed.'
    #else:
    #   print 'failed.'
    global xyp1, xyp2, xyp3, xyp4 

    xyp1 = readXYplot('h-16dnt.xyp')
    xyp2 = readXYplot('nwt_h-16dnt.xyp')
    xyp3 = readXYplot('Fnwt_h-16dnt.xyp')
    xyp4 = readXYplot('PFnwt_h-16dnt.xyp')

    print xyp1

    xpt1 = readXplot('trav1.xpt')
    xpt2 = readXplot('trav2.xpt')
    xpt3 = readXplot('trms_nwt_h-16dnt.xpt')

if __name__ == "__main__":
    testcases()
