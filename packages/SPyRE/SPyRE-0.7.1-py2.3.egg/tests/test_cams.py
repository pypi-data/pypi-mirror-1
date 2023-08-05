"""Tests for camera methods. Excludes testing OpenGL methods, which are tested in another test
module.

"""

import unittest
import math

import spyre

class FauxEngine(object):

    def __init__(self):
        self.width = 400
        self.height = 400
        self.objects = []


FUZZ = 0.001

def distance(a, b):
    d = math.sqrt((b[0]-a[0])**2 + (b[1]-a[1])**2 + (b[2]-a[2])**2)
    return d

    
class T01_Functions(unittest.TestCase):
    """Test functions for conversions."""
    
    def test001_backAndForth(self):
        """Convert cartesian to sphere, and then back to cartesian """
        d = (1, 2, 3)
        self.backAndForth(d)
        
    def test002_backAndForth(self):
        """Convert cartesian to sphere, and then back to cartesian """
        d = (25, 25, 35)
        self.backAndForth(d)

    def test003_oneOneOne(self):
        """Convert (1,1,1) to () """
        sph = spyre.cartesianToSpherical(1,1,1)
        self.assert_(distance(sph, (1.7320, 0.78540, 0.61550))< FUZZ, sph)

    def test010_forthAndBack(self):
        """Convert cartesian to sphere, and then back to sphere """
        d = (25, 25, 28)
        self.assertRaises(ValueError, self.forthAndBack, d)
        
    def test011_forthAndBack(self):
        """Convert cartesian to sphere, and then back to sphere """
        d = (1, 2, 3)
        self.assertRaises(ValueError, self.forthAndBack, d)
        
    def test012_forthAndBack(self):
        """Convert cartesian to sphere, and then back to sphere """
        d = (10, 2, 1.2)
        self.forthAndBack(d)
        
    def backAndForth(self, data):
        s = spyre.cartesianToSpherical(*data)
        self.assert_(s != data)
        c = spyre.sphericalToCartesian(*s)
        self.assert_(abs(c[0]-data[0])<FUZZ, "%s | %s" % (c, data))
        self.assert_(abs(c[1]-data[1])<FUZZ, "%s | %s" % (c, data))
        self.assert_(abs(c[2]-data[2])<FUZZ, "%s | %s" % (c, data))
        
    def forthAndBack(self, data):
        c = spyre.sphericalToCartesian(*data)
        self.assert_(c != data)
        s = spyre.cartesianToSpherical(*c)
        self.assert_(abs(s[0]-data[0])<FUZZ, "%s | %s" % (s, data))
        self.assert_(abs(s[1]-data[1])<FUZZ, "%s | %s" % (s, data))
        self.assert_(abs(s[2]-data[2])<FUZZ, "%s | %s" % (s, data))
        

class T02_CamTest(unittest.TestCase):
    """Test Camera functionality for basic camera."""
    
    def setUp(self):
        fe = FauxEngine()
        self.cam = spyre.Camera(fe, (0,0,1), (0,0,0), (0,0,1), -1, 1, -1, 1, 0, 1 )
        self.cam.setup()
        
    def test001_center(self):
        """Set center and check that was set."""
        self.assert_(distance(self.cam.center, (1,1,1))>FUZZ)
        self.cam.center = (1, 1, 1)
        self.cam.refresh()
        self.assert_(distance(self.cam.center, (1,1,1))<FUZZ, self.cam.center)
        self.assert_(self.cam.dirty)
        
    def test002_center(self):
        """Set center and check that was set."""
        self.assert_(distance(self.cam.center, (-1,-1,-1))>FUZZ)
        self.cam.center = (-1, -1, -1)
        self.cam.refresh()
        self.assert_(distance(self.cam.center, (-1,-1,-1))<FUZZ, self.cam.center)
        self.assert_(self.cam.dirty)

    def test003_center(self):
        """Set center and check that was set."""
        ref = (1, -1, 1)
        self.assert_(distance(self.cam.center, ref)>FUZZ)
        self.cam.center = ref
        self.cam.refresh()
        self.assert_(distance(self.cam.center, ref)<FUZZ, self.cam.center)
        self.assert_(self.cam.dirty)

    def test004_center(self):
        """Set center and check that was set."""
        ref = (-1, 1, -1)
        self.assert_(distance(self.cam.center, ref)>FUZZ)
        self.cam.center = ref
        self.cam.refresh()
        self.assert_(distance(self.cam.center, ref)<FUZZ, self.cam.center)
        self.assert_(self.cam.dirty)
        
    def test010_eye(self):
        """Set eye and check that was set.(1/4)"""
        self.assert_(distance(self.cam.eye, (1,1,1))>FUZZ)
        self.cam.eye = (1, 1, 1)
        self.assert_(distance(self.cam.eye, (1,1,1))<FUZZ, self.cam.eye)
        self.cam.refresh()
        self.assert_(distance(self.cam.eye, (1,1,1))<FUZZ, self.cam.eye)
        self.assert_(self.cam.dirty)
        
    def test011_eye(self):
        """Set eye and check that was set. (2/4)"""
        ref = (-1, -1, -1)
        self.assert_(distance(self.cam.eye, ref)>FUZZ)
        self.cam.eye = ref
        self.cam.refresh()
        self.assert_(distance(self.cam.eye, ref)<FUZZ, self.cam.eye)
        self.assert_(self.cam.dirty)
        
    def test012_eye(self):
        """Set eye and check that was set. (3/4)"""
        ref = (-1, 1, -1)
        self.assert_(distance(self.cam.eye, ref)>FUZZ)
        self.cam.eye = ref
        self.cam.refresh()
        self.assert_(distance(self.cam.eye, ref)<FUZZ, self.cam.eye)
        self.assert_(self.cam.dirty)
        
    def test013_eye(self):
        """Set eye and check that was set. (4/4)"""
        ref = (-1, 1, 1)
        self.assert_(distance(self.cam.eye, ref)>FUZZ)
        self.cam.eye = ref
        self.cam.refresh()
        self.assert_(distance(self.cam.eye, ref)<FUZZ, self.cam.eye)
        self.assert_(self.cam.dirty)
        
    def test020_zoom(self):
        """Check zoom. """
        left = self.cam.left
        self.cam.zoomIn(3.0)
        self.assert_(self.cam.left == left/3.0)
        self.assert_(self.cam.dirty)
        
    def test021_zoom(self):
        """Check zoom. """
        left = self.cam.left
        self.cam.zoomOut(3.0)
        self.assert_(self.cam.left == left*3.0)
        self.assert_(self.cam.dirty)
        
    def test030_saveRestore(self):
        """Check saveInit and restoreInit. """
        left = self.cam.left
        self.cam.saveInit()
        self.cam.zoomOut(3.0)
        self.assert_(self.cam.left != left)
        self.cam.restoreInit()
        self.assert_(self.cam.left == left)
        self.assert_(self.cam.dirty)

    def test031_saveRestore(self):
        """Check restoreInit """
        left = self.cam.left
        self.cam.zoomOut(3.0)
        self.assert_(self.cam.left != left)
        self.cam.restoreInit()
        self.assert_(self.cam.left == left)
        self.assert_(self.cam.dirty)
    
    def test041_setup(self):
        """Test that setup creates viewport correctly."""
        self.assertEqual(self.cam.viewport[0], self.cam.viewport[0])
        self.assertEqual(self.cam.viewport[1], self.cam.viewport[1])
        self.assert_(self.cam.viewport[2] == 400, self.cam.viewport[2])
        self.assert_(self.cam.viewport[3] == 400, self.cam.viewport[3])

    def test051_viewport(self):
        """Test that setViewport sets viewport correctly."""
        self.cam.setViewport(0.1, 0.2, 0.5, 0.6)
        self.assertEqual(self.cam.viewport[0], 40, self.cam.viewport)
        self.assertEqual(self.cam.viewport[1], 80, self.cam.viewport)
        self.assertEqual(self.cam.viewport[2], 160, self.cam.viewport)
        self.assertEqual(self.cam.viewport[3], 160, self.cam.viewport)

            
class T03_BasicCam(T02_CamTest):
    """Test BasicCam. """

    def setUp(self):
        fe = FauxEngine()
        self.cam = spyre.BasicCamera(fe, (0,0,1))
        self.cam.setup()
        

class T04_BasicCamOrtho(T03_BasicCam):
    """Test BasicCameraFrustum """
    
    def setUp(self):
        fe = FauxEngine()
        self.cam = spyre.BasicCameraOrtho(fe, (0,0,1))
        self.cam.setup()

    def test100_ortho(self):
        """Confirm ortho setting """
        self.assert_(self.cam.right != 3.5)
        right = self.cam.right
        self.cam.ortho(-3.5, 3.5, -2.8, 2.7, 0.1, 10)
        self.assert_(self.cam.right == 3.5)
        self.assert_(self.cam.far == 10)
        

class T05_BasicCamFrustum(T03_BasicCam):
    """Test BasicCameraFrustum """
    
    def setUp(self):
        fe = FauxEngine()
        self.cam = spyre.BasicCameraFrustum(fe, (0,0,1))
        self.cam.setup()

    def test100_frustum(self):
        """Confirm frustum setting. """
        self.assert_(self.cam.right != 3.5)
        right = self.cam.right
        self.cam.frustum(-3.5, 3.5, -2.8, 2.7, 0.1, 10)
        self.assert_(self.cam.right == 3.5)
        self.assert_(self.cam.far == 10)
        
    def test101_frustum(self):
        """Confirm perspective setting. """
        self.assert_(self.cam.right != 3.5)
        self.cam.frustum(-1, 1, -1, 1, 0.1, 10)
        right = self.cam.right
        top = self.cam.top
        self.cam.perspective(20, 1, 0.1, 10)
        self.assert_(self.cam.right != right)
        self.assert_(self.cam.top != top)
        self.assert_(self.cam.far == 10)


class T06_PrecessingCamera(T03_BasicCam):
    """Test Precessing Camera"""
    
    def setUp(self):
        fe = FauxEngine()
        self.cam = spyre.PrecessingCamera(fe, 5, 2, 1)
        self.cam.setup()
        
    def test010_eye(self):
        """neutered inherited test"""
        pass
        
    def test011_eye(self):
        """neutered inherited test"""
        pass
        
    def test012_eye(self):
        """neutered inherited test"""
        pass
        
    def test013_eye(self):
        """neutered inherited test"""
        pass
        
    def test200_calc(self):
        """Check calc method """
        self.cam.refresh()
        z = [self.cam.eye[0], self.cam.eye[1], self.cam.eye[2]]
        z[2] = 0
        d = distance(z, (0,0,0))
        self.assert_(d==self.cam.distance)
    
    def test201_calc(self):
        """Check calc method """
        self.cam.refresh()
        self.cam.refresh()
        self.cam.refresh()
        z = [self.cam.eye[0], self.cam.eye[1], self.cam.eye[2]]
        z[2] = 0
        d = distance(z, (0,0,0))
        self.assert_(d==self.cam.distance)


class T07_PrecessingCameraOrtho(T06_PrecessingCamera):

    def setUp(self):
        fe = FauxEngine()
        self.cam = spyre.PrecessingCameraOrtho(fe, 5, 2, 1)
        self.cam.setup()
        

class T09_MobileCamera(T03_BasicCam):
    """Test Mobile Camera """
    
    def setUp(self):
        fe = FauxEngine()
        self.cam = spyre.MobileCamera(fe, 5)
        self.cam.setup()
        
    def test220_calc(self):
        """Check calc """
        self.cam.rho = 1
        self.cam.theta = 0
        self.cam.phi = spyre.piOverTwo
        self.cam.calc()
        self.assert_(distance(self.cam.eye, (0,0,1))<FUZZ, self.cam.eye)

    def test221_calc(self):
        """Check calc """
        self.cam.rho = 2
        self.cam.theta = 0
        self.cam.phi = spyre.pi/4.0
        self.cam.calc()
        ref = (2*math.sin(spyre.pi/4.0), 0, 2*math.cos(spyre.pi/4.0))
        self.assert_(distance(self.cam.eye, ref)<FUZZ, self.cam.eye)

    def test222_calc(self):
        """Check calc """
        self.cam.rho = 1
        self.cam.theta = spyre.pi
        self.cam.phi = 0
        self.cam.calc()
        ref = (-1, 0, 0)
        self.assert_(distance(self.cam.eye, ref)<FUZZ, self.cam.eye)

    def test223_calc(self):
        """Check calc """
        self.cam.rho = 2
        self.cam.theta = spyre.pi
        self.cam.phi = spyre.pi/4.0
        self.cam.calc()
        ref = (-2*math.sin(spyre.pi/4.0), 0, 2*math.cos(spyre.pi/4.0))
        self.assert_(distance(self.cam.eye, ref)<FUZZ, self.cam.eye)


class T10_MobileCamOrtho(T09_MobileCamera):
    """Test Mobile Camera. """
    
    def setUp(self):
        fe = FauxEngine()
        self.cam = spyre.MobileCameraOrtho(fe, 5)
        self.cam.setup()
    

class T11_MobileCamFrustum(T09_MobileCamera):
    """Test Mobile Camera. """
    
    def setUp(self):
        fe = FauxEngine()
        self.cam = spyre.MobileCameraFrustum(fe, 5)
        self.cam.setup()
    

class T12_RovingCam(T03_BasicCam):
    """Test Roving Camera """
    
    def setUp(self):
        fe = FauxEngine()
        self.cam = spyre.RovingCamera(fe, (10,0,10), (0,0,10))
        self.cam.setup()
        
    def test001_center(self):
        """neutered inherited test"""
        pass
        
    def test002_center(self):
        """neutered inherited test"""
        pass
        
    def test003_center(self):
        """neutered inherited test"""
        pass
        
    def test004_center(self):
        """neutered inherited test"""
        pass
        
    def test200_calc(self):
        """Check calc """
        self.cam.eye = (20,10,10)
        self.cam.calc()
        e = (self.cam.eye[0], self.cam.eye[1], 0)
        c = (self.cam.center[0], self.cam.center[1], 0)
        self.assert_(distance(e, c)-10<FUZZ, c)
        
    def test201_calc(self):
        """Check calc """
        self.cam.eye = (30,10,10)
        self.cam.calc()
        e = (self.cam.eye[0], self.cam.eye[1], 0)
        c = (self.cam.center[0], self.cam.center[1], 0)
        self.assert_(distance(e, c)-10<FUZZ, c)
        
    def test202_calc(self):
        """Check calc """
        self.cam.eye = (40,10,10)
        self.cam.calc()
        e = (self.cam.eye[0], self.cam.eye[1], 0)
        c = (self.cam.center[0], self.cam.center[1], 0)
        self.assert_(distance(e, c)-10<FUZZ, c)
            
           
class T13_RovingCamFrustum(T12_RovingCam):
    """Test Roving Camera Frustum. """
    
    def setUp(self):
        fe = FauxEngine()
        self.cam = spyre.RovingCameraFrustum(fe, (10,0,10), (0,0,10))
        self.cam.setup()
    
        
class T14_RovingCamOrtho(T12_RovingCam):
    """Test Roving Camera Ortho. """
    
    def setUp(self):
        fe = FauxEngine()
        self.cam = spyre.RovingCameraOrtho(fe, (10,0,10), (0,0,10))
        self.cam.setup()
    
        
class T15_RovingCamY(T03_BasicCam):
    """Test Roving Camera """
    
    def setUp(self):
        fe = FauxEngine()
        fe.debug = 0
        self.cam = spyre.RovingCameraY(fe, (10,0,0), (0,0,0))
        self.cam.setup()
        
    def test001_center(self):
        """neutered inherited test"""
        pass
        
    def test002_center(self):
        """neutered inherited test"""
        pass
        
    def test003_center(self):
        """neutered inherited test"""
        pass
        
    def test004_center(self):
        """neutered inherited test"""
        pass
        
    def test200_eye(self):
        """Check eye """
        self.cam.eye=(20,0,0)
        self.cam.calc()
        self.assert_(self.cam.theta==spyre.pi, self.cam.theta)
        
    def test201_calc(self):
        """Check calc """
        self.cam.eye = (20,10,10)
        self.cam.calc()
        e = (self.cam.eye[0], 0, self.cam.eye[2])
        c = (self.cam.center[0], 0, self.cam.center[2])
        self.assert_(distance(e, c)-10<FUZZ, "%s | %s" % (e,c))
        
    def test202_calc(self):
        """Check calc """
        self.cam.eye = (30,10,10)
        self.cam.calc()
        e = (self.cam.eye[0], 0, self.cam.eye[2])
        c = (self.cam.center[0], 0, self.cam.center[2])
        self.assert_(distance(e, c)-10<FUZZ, c)
        
    def test203_calc(self):
        """Check calc """
        self.cam.eye = (40,10,10)
        self.cam.calc()
        e = (self.cam.eye[0], 0, self.cam.eye[2])
        c = (self.cam.center[0], 0, self.cam.center[2])
        self.assert_(distance(e, c)-10<FUZZ, c)


class T16_RovingCamFrustumY(T15_RovingCamY):
    """Test Roving Camera Frustum. """
    
    def setUp(self):
        fe = FauxEngine()
        fe.debug = 0
        self.cam = spyre.RovingCameraFrustumY(fe, (10,0,0), (0,0,0))
        self.cam.setup()
    
        
class T17_RovingCamOrthoY(T15_RovingCamY):
    """Test Roving Camera Ortho. """
    
    def setUp(self):
        fe = FauxEngine()
        fe.debug = 0
        self.cam = spyre.RovingCameraOrthoY(fe, (10,0,0), (0,0,0))
        self.cam.setup()


        
if __name__ == '__main__':
    unittest.main()