"""Tests for studio classes, and for light classes. Excludes testing OpenGL dependent methods, 
which might be tested in another test module, eventually.
"""

import unittest

import spyre

FUZZ = 0.00000001

class FauxEngine(object):

    def __init__(self):
        self.width = 400
        self.height = 400
        self.objects = []


class T01_Light(unittest.TestCase):
    """Test functions for Light base class."""
    
    def setUp(self):
        self.L0 = spyre.Light()
        
    def tearDown(self):
        self.L0 = None
        
    def test001_destroy(self):
        """Check that destructor is called"""
        ct = len(spyre.Light.available_lights)
        self.assert_(ct<9)
        self.assert_(self.L0.id)
        self.L0 = None
        self.assertNotEqual(len(spyre.Light.available_lights), ct)
    
    def test002_ctLimit(self):
        """Check that light ct is limited to 8."""
        Ls = []
        for L in range(7):
            Ls.append(spyre.Light())
        Lt = spyre.Light()
        self.assertRaises(IndexError, Lt.on,)

    def test003_ctLimit(self):
        """Check that lights are freed on tearDown."""
        # tests that lights created in test002 were destroyed and
        #  light ids freed after test002
        self.assert_(len(spyre.Light.available_lights) >= 7)

    def test010_onOff(self):
        """Test on and off methods."""
        self.assertNotEqual(self.L0.id, None)
        self.L0.off()
        self.assertEqual(self.L0.id, None)
        self.L0.on()
        self.assertNotEqual(self.L0.id, None)

    def test020_setPosition(self):
        """Test setPosition methods."""
        self.assertEqual(len(self.L0.position), 4)
        

class T02_Bulb(T01_Light):
    """Test functions for Light base class."""
    
    def setUp(self):
        self.L0 = spyre.Bulb()
        
    def test100_setPosition(self):
        """Test setPosition methods."""
        self.L0.setPosition((1,2,3))
        self.assertEqual(len(self.L0.position), 4)


class T03_Sun(T01_Light):
    """Test functions for Light base class."""
    
    def setUp(self):
        self.L0 = spyre.Sun()
        
        
class T04_Spot(T01_Light):
    """Test functions for Light base class."""
    
    def setUp(self):
        cutoff = 2
        direction = (1,1,1)
        self.L0 = spyre.Spot(cutoff, direction)
        
    def test100_setDirection(self):
        """Test that direction is sized 4"""
        self.L0.setDirection((1,0,1))
        self.assertEqual(len(self.L0.direction), 4)
        

class T10_StudioCM(unittest.TestCase):
    """Test functions for Studio class."""
    
    def setUp(self):
        fe = FauxEngine()
        fe.camera = spyre.BasicCamera(fe, (1,1,1))
        self.studio = spyre.StudioColorMat(fe)
        
    def test010_fixedLight(self):
        """Test that fixed lights are added and removed."""
        self.assertEqual(len(self.studio.lightsFixed), 0)
        self.assertEqual(len(self.studio.lightsMobile), 0)
        self.assertEqual(len(self.studio.lightsMotion), 0)
        self.assertEqual(len(self.studio.lightsCam), 0)
        f0 = spyre.Bulb()
        self.studio.addFixedLight(f0)
        self.assertEqual(len(self.studio.lightsFixed), 1)
        self.assertEqual(len(self.studio.lightsMobile), 0)
        self.assertEqual(len(self.studio.lightsMotion), 0)
        self.assertEqual(len(self.studio.lightsCam), 0)
        self.studio.removeFixedLight(f0)
        self.assertEqual(len(self.studio.lightsFixed), 0)
        self.assertEqual(len(self.studio.lightsMobile), 0)
        self.assertEqual(len(self.studio.lightsMotion), 0)
        self.assertEqual(len(self.studio.lightsCam), 0)
        
    def test010_camLight(self):
        """Test that cam lights are added and removed."""
        self.assertEqual(len(self.studio.lightsCam), 0)
        self.assertEqual(len(self.studio.lightsFixed), 0)
        self.assertEqual(len(self.studio.lightsMobile), 0)
        self.assertEqual(len(self.studio.lightsMotion), 0)
        f0 = spyre.Bulb()
        self.studio.addCamLight(f0)
        self.assertEqual(len(self.studio.lightsCam), 1)
        self.assertEqual(len(self.studio.lightsFixed), 0)
        self.assertEqual(len(self.studio.lightsMobile), 0)
        self.assertEqual(len(self.studio.lightsMotion), 0)
        self.studio.removeCamLight(f0)
        self.assertEqual(len(self.studio.lightsCam), 0)
        self.assertEqual(len(self.studio.lightsFixed), 0)
        self.assertEqual(len(self.studio.lightsMobile), 0)
        self.assertEqual(len(self.studio.lightsMotion), 0)
        
    def test010_mobileLight(self):
        """Test that mobile lights are added and removed."""
        self.assertEqual(len(self.studio.lightsMobile), 0)
        self.assertEqual(len(self.studio.lightsMotion), 0)
        self.assertEqual(len(self.studio.lightsFixed), 0)
        self.assertEqual(len(self.studio.lightsCam), 0)
        f0 = spyre.Bulb()
        self.studio.addMobileLight(f0,f0)
        self.assertEqual(len(self.studio.lightsMobile), 1)
        self.assertEqual(len(self.studio.lightsMotion), 1)
        self.assertEqual(len(self.studio.lightsFixed), 0)
        self.assertEqual(len(self.studio.lightsCam), 0)
        self.studio.removeMobileLight(f0)
        self.assertEqual(len(self.studio.lightsMobile), 0)
        self.assertEqual(len(self.studio.lightsMotion), 0)
        self.assertEqual(len(self.studio.lightsFixed), 0)
        self.assertEqual(len(self.studio.lightsCam), 0)
        

    def test020_depthCue(self):
        """Test that depthCueing sets attribute."""
        self.assertEqual(self.studio.depthCue, None)
        self.studio.depthCueing(True)
        self.assertEqual(len(self.studio.depthCue), 4)
        


if __name__ == '__main__':
    unittest.main()