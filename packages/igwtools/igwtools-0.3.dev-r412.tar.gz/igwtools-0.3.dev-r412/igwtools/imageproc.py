import sys
import pylab
import Image
import numpy
from math import log

def justshowit():
    filename = sys.argv[1]
    im = Image.open(filename,'r')
    xsize,ysize = im.size
    data = im.getdata()
    newarr = numpy.array(data,dtype='uint8')
    if im.mode == 'RGB':
      newarr = newarr.reshape((ysize,xsize,3))
    else:
      pylab.gray()
      newarr = newarr.reshape((ysize,xsize))
    pylab.imshow(newarr)
    pylab.show()

