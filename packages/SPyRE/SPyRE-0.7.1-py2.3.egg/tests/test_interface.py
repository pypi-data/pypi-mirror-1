"""Tests for interface methods. Excludes testing pygame dependent methods, which might 
be tested in another test module, eventually.

for now, only tests camera control functions.

"""

import unittest
import math
import la

from pygame import init, event, locals

import spyre

def makeKeyEvent(ch):
    """Create a pygame event for keystroke. """
    ev = event.Event(locals.KEYDOWN, key=ch)
    return ev

def makeMouseButtonDownEvent(loc=(1,1,1)):
    """Create a pygame event for keystroke. """
    ev = event.Event(locals.MOUSEBUTTONDOWN, pos=loc, button=1)
    assert(ev.button)
    return ev

def makeMouseMotionEvent(loc=(1,1,1)):
    """Create a pygame event for keystroke. """
    ev = event.Event(locals.MOUSEMOTION, pos=loc)
    return ev


class FauxEngine(object):
    pass

FUZZ = 0.00000001
init()

class T01_BareBones(unittest.TestCase):
    """Test functions for BareBonesInterface."""
    
    def setUp(self):
        fe = spyre.Engine()
        fe.camera = spyre.BasicCameraOrtho(fe, (0,0,1), (0,0,0), (0,0,1), -1, 1, -1, 1, 0, 1)
        self.interface = spyre.BareBonesInterface(fe) 
        self.engine = fe
        self.interface.setup()
        
    def test001_reset(self):
        """Interface reset resets camera. """
        left = self.engine.camera.left
        self.engine.camera.zoomOut(3.0)
        self.interface.reset()
        self.assert_(self.engine.camera.left == left, (self.engine.camera.left, left))
        self.assert_(self.engine.camera.dirty)
    
    def test002_quit(self):
        """Interface Quit raises ShutdownException. """
        self.assertRaises(spyre.EngineShutdownException, self.interface.quit,)
        
    def test003_sizeUp(self):
        """Test that resize raises reinit exception, and sets params. """
        width = self.engine.width
        self.assertRaises(spyre.EngineReInitException, self.interface.sizeUp, 2)
        self.assertEqual(self.engine.width, width*2)

    def test004_sizeDown(self):
        """Test that resize raises reinit exception."""
        width = self.engine.width
        self.assertRaises(spyre.EngineReInitException, self.interface.sizeDown, 2)        
        self.assertEqual(self.engine.width, width/2)

    def test005_keyPressed(self):
        """Reset engine with keystroke through keyPressed() """
        left = self.engine.camera.left
        ev = event.Event(locals.KEYDOWN, key='r')
        self.engine.camera.zoomOut(3.0)
        self.interface.keyPressed(ev.key)
        self.assertEqual(self.engine.camera.left, left)
        self.assert_(self.engine.camera.dirty)
        
    def test006_eventKey(self):
        """Reset engine with keystroke through event() """
        left = self.engine.camera.left
        ev = makeKeyEvent('r')
        self.engine.camera.zoomOut(3.0)
        self.interface.event(ev)
        self.assertEqual(self.engine.camera.left, left)
        self.assert_(self.engine.camera.dirty)

    def test007_mouse(self):
        """Test mouse motion handler"""
        c = self.engine.camera.center
        e = self.engine.camera.eye
        evB = makeMouseButtonDownEvent()
        self.assertNotEqual(self.interface.lastButton, evB.button)
        self.assertNotEqual(self.interface.mouseMark, evB.pos)
        self.interface.event(evB)
        self.assertEqual(self.interface.lastButton, evB.button)
        self.assertEqual(self.interface.mouseMark, evB.pos)

    
class T02_Basic(T01_BareBones):
    """Test functions for BasicInterface."""
    
    def setUp(self):
        fe = spyre.Engine()
        fe.camera = spyre.BasicCameraOrtho(fe, (0,0,1), (0,0,0), (0,0,1), -1, 1, -1, 1, 0, 1)
        self.interface = spyre.BasicInterface(fe) 
        self.engine = fe
        self.interface.setup()
        
    def test101_zoom(self):
        """Test that zoomIN changes frustum/ortho bounds."""
        left = self.engine.camera.left
        self.engine.camera.zoomIn(3.0)
        self.assert_(self.engine.camera.left == left/3.0)

    def test102_zoom(self):
        """Test that zoomOUT changes frustum/ortho bounds."""
        left = self.engine.camera.left
        self.engine.camera.zoomOut(3.0)
        self.assert_(self.engine.camera.left == left*3.0)

    def test103_toggle(self):
        """No test for toggle in interface."""
        pass #####
        
    def test104_step(self):
        """No test for step in interface."""
        pass #####
        
    
class T03_Pivoting(T02_Basic):
    """Test functions for PivotingInterface."""
    
    def setUp(self):
        fe = spyre.Engine()
        fe.camera = spyre.MobileCameraOrtho(fe, 5)
        self.interface = spyre.PivotingInterface(fe) 
        self.engine = fe
        self.interface.setup()
        
    def test201_mouse(self):
        """Test mouse motion handler"""
        cam = self.engine.camera
        intf = self.interface
        cam.eye = (1,0,0)
        cam.center = (0,0,0)
        c = cam.center
        e = cam.eye
        evB = makeMouseButtonDownEvent((0,1,0))
        evM = makeMouseMotionEvent((0,10,0))
        self.assertNotEqual(intf.lastButton, evB.button)
        self.assertNotEqual(intf.mouseMark, evM.pos)
        self.interface.event(evB)
        self.assertEqual(intf.lastButton, evB.button)
        self.interface.event(evM)
        self.assertEqual(intf.mouseMark, evM.pos)
        self.assertNotEqual(cam.eye, e)
        self.assertEqual(cam.center, c)
        v0 = la.Vector(e[0]-c[0],e[1]-c[1],e[2]-c[2])
        v1 = la.Vector(cam.eye[0]-cam.center[0],
                       cam.eye[1]-cam.center[1],
                       cam.eye[2]-cam.center[2])
        vD = v1-v0
        self.assertNotEqual(vD[0], 0)
        self.assertEqual(vD[1], 0)
        self.assertNotEqual(vD[2], 0)

    def test202_mouse(self):
        """Test mouse motion handler via event() """
        cam = self.engine.camera
        intf = self.interface
        cam.eye = (0,1,0)
        cam.center = (0,0,0)
        cam.up = (0,0,1)
        c = cam.center
        e = cam.eye
        evB = makeMouseButtonDownEvent((0,1,0))
        evM = makeMouseMotionEvent((0,10,0))
        self.assertNotEqual(intf.lastButton, evB.button)
        self.assertNotEqual(intf.mouseMark, evM.pos)
        self.interface.event(evB)
        self.assertEqual(intf.lastButton, evB.button)
        self.interface.event(evM)
        self.assertEqual(intf.mouseMark, evM.pos)
        self.assertNotEqual(cam.eye, e)
        self.assertEqual(cam.center, c)
        v0 = la.Vector(e[0]-c[0],e[1]-c[1],e[2]-c[2])
        v1 = la.Vector(cam.eye[0]-cam.center[0],
                       cam.eye[1]-cam.center[1],
                       cam.eye[2]-cam.center[2])
        vD = v1-v0
        self.assert_(abs(vD[0]) < FUZZ, vD)
        self.assert_(abs(vD[1]) > FUZZ, vD)
        self.assert_(abs(vD[2]) > FUZZ, vD)


class T04_Panning(T03_Pivoting):
    """Test functions for PanningInterface."""
    
    def setUp(self):
        fe = spyre.Engine()
        fe.camera = spyre.MobileCameraOrtho(fe, 5)
        self.interface = spyre.PanningInterface(fe) 
        self.engine = fe
        self.interface.setup()
        
    def test301_pan(self):
        """Test that pan +x moves center"""
        ctr0 = self.engine.camera.center
        self.interface.panPositiveX()
        self.assertNotEqual(ctr0, self.engine.camera.center)

    def test302_pan(self):
        """Test that pan -x moves center"""
        ctr0 = self.engine.camera.center
        self.interface.panNegativeX()
        self.assertNotEqual(ctr0, self.engine.camera.center)

    def test303_pan(self):
        """Test that pan +y moves center"""
        ctr0 = self.engine.camera.center
        self.interface.panPositiveY()
        self.assertNotEqual(ctr0, self.engine.camera.center)

    def test304_pan(self):
        """Test that pan -y moves center"""
        ctr0 = self.engine.camera.center
        self.interface.panNegativeY()
        self.assertNotEqual(ctr0, self.engine.camera.center)

    def test305_pan(self):
        """Test that pan +z moves center"""
        ctr0 = self.engine.camera.center
        self.interface.panPositiveZ()
        self.assertNotEqual(ctr0, self.engine.camera.center)

    def test306_pan(self):
        """Test that pan -z moves center"""
        ctr0 = self.engine.camera.center
        self.interface.panNegativeZ()
        self.assertNotEqual(ctr0, self.engine.camera.center)

    def test307_reset(self):
        """Test that panReset restores center to (0,0,0)"""
        self.engine.camera.center = (0,0,0)
        self.interface.panNegativeZ()
        self.interface.resetPan()
        self.assertEqual((0,0,0), self.engine.camera.center)


def distance(a, b):
    d = math.sqrt((b[0]-a[0])**2 + (b[1]-a[1])**2 + (b[2]-a[2])**2)
    return d


class T05_Pedestrian(T02_Basic):
    """Test functions for PedestrianInterface."""
    
    def setUp(self):
        fe = spyre.Engine()
        fe.camera = spyre.RovingCameraOrtho(fe)
        self.interface = spyre.PedestrianInterface(fe) 
        self.engine = fe
        self.interface.setup()
        
    def test006_eventKey(self):
        """Override eventKey test for Pedestrian, since key assignments changed"""
        pass 

    def test005_keyPressed(self):
        """Override keyPressed test for Pedestrian, since key assignments changed"""
        pass

    def test401_forward(self):
        """Test that forward moves both eye and center."""
        eye0 = self.engine.camera.eye
        ctr0 = self.engine.camera.center
        self.interface.forward()
        self.assertNotEqual(eye0, self.engine.camera.eye)
        self.assertNotEqual(ctr0, self.engine.camera.center)

    def test402_backward(self):
        """Test that backward moves both eye and center."""
        eye0 = self.engine.camera.eye
        ctr0 = self.engine.camera.center
        self.interface.backward()
        self.assertNotEqual(eye0, self.engine.camera.eye)
        self.assertNotEqual(ctr0, self.engine.camera.center)

    def test403_moveCam(self):
        """moveCam is basis for forward, backward. redundant test"""
        eye0 = self.engine.camera.eye
        ctr0 = self.engine.camera.center
        self.interface.moveCam(1)
        self.assertNotEqual(eye0, self.engine.camera.eye)
        self.assertNotEqual(ctr0, self.engine.camera.center)

    def test404_left(self):
        """Check that left moves center, not eye."""
        eye0 = self.engine.camera.eye
        ctr0 = self.engine.camera.center
        self.interface.left()
        self.assertEqual(eye0, self.engine.camera.eye)
        self.assertNotEqual(ctr0, self.engine.camera.center)

    def test405_right(self):
        """Check that right moves center, not eye."""
        eye0 = self.engine.camera.eye
        ctr0 = self.engine.camera.center
        self.interface.right()
        self.assertEqual(eye0, self.engine.camera.eye)
        self.assertNotEqual(ctr0, self.engine.camera.center)


class T06_PedestrianY(T05_Pedestrian):
    """Test functions for PedestrianInterface."""
    
    def setUp(self):
        fe = spyre.Engine()
        fe.camera = spyre.RovingCameraOrthoY(fe)
        self.interface = spyre.PedestrianInterfaceY(fe) 
        self.engine = fe
        self.interface.setup()
        

class T07_CursorKey(T04_Panning):
    """Test CursorKeyInterface.  Needs tests, but ....
    it is so ugly, I may eliminate it from module altogether.
    """
    
    def setUp(self):
        fe = spyre.Engine()
        fe.camera = spyre.MobileCameraOrtho(fe, 5)
        self.interface = spyre.CursorKeyInterface(fe) 
        self.engine = fe
        self.interface.setup()


if __name__ == '__main__':
    unittest.main()