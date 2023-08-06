"Tests for igwtools"
import igwtools

from igwtools.xplot import readXYplot, writeXYplot
from igwtools.tools import Field
from unittest import TestCase

class test_tests(TestCase):
    def testTrue(self):
        self.assert_(True)

class field_tests(TestCase):
    def testEmptyField(self):
        "Ensure a None field doesn't do any harm"
        A = Field(None)
        #A.plot()
        self.assert_(True)
    def testTiny(self):
        "Single element field"
        A = Field([3])
        #A.plot()
        self.assert_(True)
    def testFrame(self):
        "A simple frame"
        f = Field([[1,2,3,4],[2,3,4,5],[3,4,5,6]], 
            xmin = 1, xmax = 3, zmin = 1, zmax = 3)
        #f.plot(interpolation='nearest')
        self.assert_(True)
    def testVts(self):
        "A simple vts"
        f = Field([[1,2,3,4],[2,3,4,5],[3,4,5,6]], 
            tmin = 1, tmax = 3, zmin = 1, zmax = 3)
        #f.plot(interpolation='nearest')
        self.assert_(True)
    def testHts(self):
        "A simple hts"
        f = Field([[1,2,3,4],[2,3,4,5],[3,4,5,6]], 
            xmin = 1, xmax = 3, tmin = 1, tmax = 3)
        #f.plot(interpolation='nearest')
        self.assert_(True)
    def testField(self):
        "xzt field"
        import pylab
        f = Field(pylab.rand(6,5,10), 
            xmin = 1, xmax = 6, zmin = 1, zmax = 5, tmin=1, tmax=10)
        #f.plot(interpolation='nearest')
        #pylab.show()
        self.assert_(True)
    def testField2(self):
        import pylab
        def func3(x,z):
            return (1-x/2+x**5 + z**3)*pylab.exp(-x**2-z**2)
        dx, dz = 0.05, 0.05
        x = pylab.arange(-3.0, 3.0, dx)
        z = pylab.arange(-3.0, 3.0, dz)
        X,Z = pylab.meshgrid(x, z)
        xmin, xmax, zmin, zmax = min(x), max(x), min(z), max(z)
        F = func3(X,Z).T
        F = igwtools.tools.Field(F, xmin = xmin, xmax = xmax, zmin = zmin, zmax=zmax)
        #F.plot(interpolation='nearest')
        #pylab.show()
        self.assert_(True)
    def testFindFreq(self):
        import pylab
        def func(x,z):
            return pylab.sin(3*x+3*z)
        dx, dz = 0.05, 0.05
        x = pylab.arange(-3.0, 3.0, dx)
        z = pylab.arange(-3.0, 3.0, dz)
        X,Z = pylab.meshgrid(x, z)
        xmin, xmax, zmin, zmax = min(x), max(x), min(z), max(z)
        F = func(X,Z).T
        F = igwtools.tools.Field(F, xmin = xmin, xmax = xmax, zmin = zmin, zmax=zmax)
        F.plot(interpolation='nearest')
        #f1, f2 = F.find_freq((xmin, xmax, zmin, zmax),show=True)
        #print f1, f2
        #pylab.show()
        self.assert_(True)
    
class xplot_tests(TestCase):
    def testWriteRead(self):
        "Save a Field as an xyp file and read it back in"
        A = Field([[1,2,3],[2,3,4]])
        A.save('test.xyp')
        B = readXYplot('test.xyp')
        from numpy import array
        self.assert_( (A==B).all() )

class xlook_tests(TestCase):
    pass

class xylook_tests(TestCase):
    pass

class igwimport_tests(TestCase):
    def testWrongMovieName(self):
        "Try an import an invalid filename as a movie"

class igwextract_tests(TestCase):
    pass

class igwschlieren_tests(TestCase):
    pass

if __name__ == '__main__':
    import unittest
    unittest.main()
