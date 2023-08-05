"""Tests for spyres principle component, the engine.  """

import unittest
import time
import math

import pdb

import spyre
import stereoscopic


FUZZ = 0.001

def distance(a, b):
    d = math.sqrt((b[0]-a[0])**2 + (b[1]-a[1])**2 + (b[2]-a[2])**2)
    return d

def doNothing():
    pass


class T01_CamTest(unittest.TestCase):
    """Test Camera functionality for basic camera."""
    
    def setUp(self):
        fe = stereoscopic.StereoEngine(spyre.Engine())
        fe.tb_offset=19
        cam = spyre.BasicCameraFrustum(fe, (0,1,0), (0,0,0), (0,0,1), -1,1,-1,1,0,1 )
        self.cam = stereoscopic.StereoTopBottomCamera(cam)
        fe.addCamera(self.cam)
        self.cam.setup()
        
    def test001_center(self):
        """Set center and check that was set."""
        self.assert_(distance(self.cam.center, (1,1,1))>FUZZ)
        self.cam.center = (1,1,1)
        self.cam.refresh()
        self.assert_(distance(self.cam.center, (1,1,1))<FUZZ, self.cam.center)
        self.assert_(distance(self.cam.cam.center, (1,1,1))<FUZZ, self.cam.cam.center)
        self.assert_(self.cam.dirty)
        
    def test010_eye(self):
        """Set eye and check that was set."""
        self.assert_(distance(self.cam.eye, (1,1,1))>FUZZ)
        self.cam.eye = (1,1,1)
        self.cam.refresh()
        self.assert_(distance(self.cam.eye, (1,1,1))<FUZZ, self.cam.eye)
        self.assert_(distance(self.cam.cam.eye, (1,1,1))<FUZZ, self.cam.cam.eye)
        self.assert_(self.cam.dirty)
        
    def test020_subEye(self):
        """Check that subEye exists."""
        self.assert_(self.cam.subEye)
        self.assert_(hasattr(self.cam.subEye, 'up'))
        
    def test030_addcams(self):
        """Check that cams are being added to engine."""
        self.assert_(self.cam.engine.cameras)
        self.assertEqual(len(self.cam.engine.cameras), 2)
        self.assert_(self.cam.engine.camera)

        
class T02_Interface(unittest.TestCase):
    """Test functions for StereoInterface."""
    
    def setUp(self):
        fe = spyre.Engine()
        fe.tb_offset=19
        cam = spyre.BasicCameraFrustum(fe, (0,1,0), (0,0,0), (0,0,1), -1, 1, -1, 1, 0, 1)
        fe.addCamera(cam)
        iface = spyre.BareBonesInterface(fe) 
        self.interface = stereoscopic.StereoInterface(iface)
        self.engine = stereoscopic.StereoEngine(fe)
        self.interface.setup()
        
    def test001_camSetup(self):
        """Check that both cameras are in engine. """
        self.assertEqual(len(self.engine.cameras), 2)
    
    def test002_camSetup(self):
        """Check that camera was setup. """
        self.assert_(self.engine.camera)
        self.assert_(self.engine.camera.subEye)
    
    def test003_camSetup(self):
        """Check that up vectors match. """
        cam = self.engine.camera
        sub = self.engine.camera.subEye
        self.assertEqual(cam.up, sub.up, "%s %s" % (cam.up, sub.up))
    
    def test020_quit(self):
        """Interface Quit raises ShutdownException. """
        self.assertRaises(spyre.EngineShutdownException, self.interface.quit,)
        

class UpdateOnly(spyre.Object):

    def __init__(self):
        self.displayCount = 0
        self.updateCount = 0

    def display(self):
        self.displayCount += 1
        
    def update(self):
        self.updateCount += 1


class UpdateList(spyre.Object):

    def __init__(self):
        self.displayCount = 0
        self.updateCount = 0
        self.updateList = []

    def display(self):
        self.displayCount += 1
        
    def update(self):
        self.updateCount += 1
        self.updateList.append(time.time())


class UpdateCommit(UpdateOnly):
    
    def __init__(self):
        self.displayCount = 0
        self.updateCount = 0
        self.commitCount = 0        

    def commit(self):
        self.commitCount += 1


class CommitQuits(UpdateCommit):

    def __init__(self, lim=1):
        self.displayCount = 0
        self.updateCount = 0
        self.commitCount = 0        
        self.limCount = lim

    def commit(self):
        self.commitCount += 1
        if self.commitCount >= self.limCount:
            raise spyre.EngineShutdownException
    

class CommitQuitsSafety(CommitQuits):
    
    def commit(self):
        self.commitCount += 1
        if self.commitCount >= self.limCount:
            print 'DIE_IN_COMMIT'
            raise spyre.EngineShutdownException
        
    
class T02_Engine(unittest.TestCase):
    """Test functions for StereoTopBottomEngine base class."""
    
    def setUp(self):
        eng = spyre.EngineFullScreen()
        tk = spyre.TimeKeeper()
        tk.display_interval = 1.0/50.0
        eng.runTimer = tk
        iface = spyre.BasicInterface(eng)
        eng.interface = stereoscopic.StereoInterface(iface)
        self.eng = stereoscopic.StereoEngineED(eng)
        
    def test001_commitquit(self):
        """Test that an engine.quit raises shutdown exception. """
        self.assertRaises(spyre.EngineShutdownException, self.eng.quit, )        
    
    def test002_commitquit(self):
        """Test that a display object can shutdown engine. """
        cq = CommitQuits()
        self.eng.add(cq)
        self.eng.go()        
    
    def test081_reshape(self):
        """Test that reshape raises no exception."""
        self.eng.reshape(10,10)


if __name__ == '__main__':
    unittest.main()