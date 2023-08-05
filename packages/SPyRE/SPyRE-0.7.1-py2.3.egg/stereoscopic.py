"""
An extension to B{SPyRE} to add B{stereoscopic} viewing.  Works with Red/Blue
glasses or the eDimensional LCD glasses.

example usage::

    from spyre import EngineFullScreen
    from stereoscopic import StereoEngineRB

    eng = EngineFullScreen()
    eng.add(...)
    
    engine = StereoEngineRB(eng)
    engine.go()

The StereoEngine setup code will insert StereoCameras and 
StereoInterfaces code where necessary.  The displayable objects
are unchanged.

The two modes of stereoscopic visuals supported here are B{LCD glasses}
and B{Red/Blue glasses}.

The eDimensional LCD glasses use the L{StereoEngineED}, the 
L{StereoTopBottomInterface}, and the L{StereoTopBottomCamera}.

The Red/Blue mode uses L{StereoEngineRB}, the L{StereoRedBlueInterface},
and the L{StereoRedBlueCamera}.

@group Red/Blue: SubordinateEyeCameraRB, SubordinateEyeCamFrustumRB, SubordinateEyeCamOrthoRB, 
    StereoRedBlueCamera, StereoRedBlueInterface, StereoEngineRB
@group eDimensional LCD: SubordinateEyeCamera, SubordinateEyeCamFrustum, SubordinateEyeCamOrtho, 
    StereoTopBottomCamera, StereoTopBottomInterface, StereoEngineED
@group abstract: StereoBaseCamera, StereoCamera, StereoInterface, StereoEngine

"""

__program__ = 'SPyRE'
__version__ = '0.7.1'
__author__ = 'David Keeney <dkeeney@travelbyroad.net>'
__copyright__ = 'Copyright (C) 2005, 2006 David Keeney'
__license__ = 'LGPL'


import math
import sys
import time
import types
import time
import atexit

import pdb

import pygame
from pygame.locals import FULLSCREEN
import OpenGL.GL as ogl
import OpenGL.GLU as oglu

import spyre
import la


# StereoCamera ==============================

class StereoBaseCamera(object):
    """Abstract base class for all Stereo cameras."""
    pass

class SubordinateEyeCamera(spyre.BasicCamera, StereoBaseCamera):
    """Camera for other eye. This is a basic camera, controlled by a 
    StereoCamera. Should be subclassed to add ortho or frustum projection.
    """
    pass

class SubordinateEyeCamOrtho(spyre.OrthoCam, SubordinateEyeCamera):
    """Camera for other eye, with ortho projection. """
    pass

class SubordinateEyeCamFrustum(spyre.FrustumCam, SubordinateEyeCamera):
    """Camera for other eye, with frustum projection. """
    pass

class SubordinateEyeCameraRB(SubordinateEyeCamera):
    """Camera for other eye, only shows red component.  Should be 
    subclassed to add frustum or ortho projection.
    """
    
    def displayBackground(self):
        """Clear openGL depth buffer and setup color blending."""
        bits = ogl.GL_DEPTH_BUFFER_BIT
        ogl.glClear(bits)
        ogl.glEnable(ogl.GL_BLEND)
        ogl.glBlendFunc(ogl.GL_SRC_ALPHA, ogl.GL_ONE_MINUS_SRC_ALPHA)
        ogl.glColorMask(True, False, False, True) # block blue/green

class SubordinateEyeCamFrustumRB(spyre.FrustumCam, SubordinateEyeCameraRB):
    """Camera for sub eye, frustum proj, that shows red only."""
    pass

class SubordinateEyeCamOrthoRB(spyre.OrthoCam, SubordinateEyeCameraRB):
    """Camera for sub eye, ortho proj, that shows red only."""
    pass


class StereoCamera(StereoBaseCamera):
    """Camera for stereo camera functionality.  Initialize with a 
    non-stereo camera.
    
    This class wraps the original (non-stereo) camera instance, 
    passing most method calls through to it.  It implicitly creates
    a second camera for second eye, using a L{SubordinateEyeCamera} and
    installs that camera in the engine.
    
    The and L{calc} methods maintain the position of this
    camera and also of the subordinate camera.
    """ 

    def __init__(self, camera, interOc=None):
        """Initialize newly constructed camera.

        @param camera: a non-stereo camera instance.
        @param interOc: the distance between the eyes.  if omitted, defaults
          to 1/30th of near distance.
        @type interOc: float
        """
        self.cam = camera
        self.frViewport = camera.fractViewport
        self.interOc = interOc
        self.subEye = None

    def calcEyes(self):
        """Calculate the two eye pos's. 
        @return: eye tuple (x,y,z), center tuple (x,y,z)
        """
        eye = self.cam.eye
        ctr = self.cam.center
        up = self.cam.up
        assert(eye is not None)
        assert(ctr is not None)
        eVec = la.Vector( eye[0]-ctr[0], eye[1]-ctr[1], eye[2]-ctr[2] )
        upVec = la.Vector(*up)
        eyeVec = upVec.cross(eVec).unit() * -self.interOc
        oEye = eye[0]-eyeVec[0], eye[1]-eyeVec[1], eye[2]-eyeVec[2]
        oCenter = ctr[0]-eyeVec[0], ctr[1]-eyeVec[1], ctr[2]-eyeVec[2]
        return oEye, oCenter

    def calc(self):
        """Recalc position, and pass on to subordinate camera. 
        @return: None
        """
        self.cam.calc()
        oEye, oCenter = self.calcEyes()
        self.subEye.eye = oEye
        self.subEye.center = oCenter
        self.subEye.up = self.cam.up

    def refresh(self): self.calc()

    def __getattr__(self, attname):
        """Delegate most attribute lookups."""
        return getattr(self.cam, attname)

    def __setattr__(self, attname, val):
        """Delegate most attribute lookups."""
        if attname == 'cam':
            self.__dict__['cam'] = val
        elif attname == 'subEye':
            self.__dict__['subEye'] = val
        elif attname == 'interOc':
            self.__dict__['interOc'] = val
        elif attname == 'frViewport':
            self.__dict__['frViewport'] = val
        else:
            object.__setattr__(self.__dict__['cam'], attname, val)


class StereoTopBottomCamera(StereoCamera):
    """Stereo camera to support LCD glasses video in top/bottom mode. 
    @see: L{StereoCamera} for description.
    """
    
    def setup(self):
        """Create controlled subordinate eye for displaying other eye view,
        and partition viewports for dual views.
        """
        self.cam.setup()
        if not self.subEye:
            if not self.interOc:
                self.interOc = self.cam.near/30.0
                if not self.interOc: self.interOc = 0.1
            oEye, oCenter = self.calcEyes()
            c = self.cam
            parms = c.left, c.right, c.bottom, c.top, c.near, c.far
            if isinstance(self.cam, spyre.OrthoCam):
                subEye = SubordinateEyeCamOrtho(self.cam.engine, oEye, oCenter, self.cam.up)
                subEye.ortho(*parms)
            elif isinstance(self.cam, spyre.FrustumCam):
                subEye = SubordinateEyeCamFrustum(self.cam.engine, oEye, oCenter, self.cam.up)
                subEye.frustum(*parms)
            else:
                raise Exception('camera is neither ortho nor frustum')
            subEye.background = c.background
            self.subEye = subEye
            self.subEye.setup()
            self.cam.engine.addCamera(self.subEye)

        # tune viewports to suit engine
        halfPorch = self.cam.engine.tb_offset*0.5/self.cam.engine.height
        halfLessHP = 0.5-halfPorch
        lowerBase = halfLessHP + 2.0*halfPorch
        vp0 = self.frViewport
        vp1_top = vp0[0], vp0[1]*halfLessHP, vp0[2], vp0[3]*halfLessHP
        vp1_bottom = vp0[0], vp0[1]*halfLessHP+lowerBase, vp0[2], vp0[3]*halfLessHP+lowerBase
        self.cam.setViewport(*vp1_top)
        self.subEye.setViewport(*vp1_bottom)


class StereoRedBlueCamera(StereoCamera):
    """Stereo camera to support stereo vision via red/blue glasses.    
    @see: L{StereoCamera} for description.
    """
 
    def setup(self):
        """Create controlled subordinate eye for displaying other eye view."""
        self.cam.setup()
        if not self.subEye:
            if not self.interOc:
                self.interOc = self.cam.near/30.0
                if not self.interOc: self.interOc = 0.1
            oEye, oCenter = self.calcEyes()
            c = self.cam
            parms = c.left, c.right, c.bottom, c.top, c.near, c.far
            if isinstance(self.cam, spyre.OrthoCam):
                subEye = SubordinateEyeCamOrthoRB(self.cam.engine, oEye, oCenter, self.cam.up)
                subEye.ortho(*parms)
            elif isinstance(self.cam, spyre.FrustumCam):
                subEye = SubordinateEyeCamFrustumRB(self.cam.engine, oEye, oCenter, self.cam.up)
                subEye.frustum(*parms)
            else:
                raise Exception('camera must be ortho or frustum')
            subEye.background = c.background
            self.subEye = subEye
            self.subEye.setup()
            self.cam.engine.addCamera(self.subEye)

            self.cam.setViewport(*self.frViewport)
            self.subEye.setViewport(*self.frViewport)
            
    def displayBackground(self):
        """Set openGL params to filter red out of display. """
        bits = ogl.GL_DEPTH_BUFFER_BIT
        ogl.glClear(bits)
        ogl.glColorMask(False, True, True, True) # block red
        
    
# StereoInterface =============================

class StereoInterface(spyre.Object):
    """The interface for stereo renderers. Initialize with a non-stereo
    interface, such as PanningInterface, and that interface provides 
    the interface behavior.

    The setup method replaces non-stereo cameras in the engine wiht
    stereo cameras (and paired subordinate cameras).  
    
    This class is typically not used directly, though it can be,
    and will work with regular engines, if care is taken to install 
    stereo interface in the engine.  More typically, the engine 
    will be wrapped by a stereo engine and that stereo engine wil
    handle setting up stereo interfaces and stereo cameras.
    
    @cvar defaultStereoCamera: designated camera for this interface.  
       non-stereo cameras are wrapped using this camera.
    """
    defaultStereoCamera = StereoTopBottomCamera

    def __init__(self, interface):
        """Initialize new instance. """
        self.iface = interface
            
    def setup(self):
        """Setup interface after all components exist."""
        self.iface.setup()
        eng = self.iface.engine
        cams = []
        for c in eng.cameras:
            if isinstance(c, StereoBaseCamera): 
                continue
            cams.append(c)
        for c in cams:
            eng.removeCamera(c)
        for c in cams:
            cs = self.defaultStereoCamera(c)
            eng.addCamera(cs)
        for cs in eng.cameras:
            cs.setup()
    
    def __getattr__(self, attname):
        """Delegate most attribute lookups."""
        return getattr(self.iface, attname)

    def __setattr__(self, attname, val):
        """Delegate most attribute lookups."""
        if attname == 'iface':
            self.__dict__['iface'] = val
        else:
            object.__setattr__(self.__dict__['iface'], attname, val)


class StereoTopBottomInterface(StereoInterface):
    """Stereo Interface for LCD glasses in top/bottom mode. 

    @cvar defaultStereoCamera: designated camera for this stereo mode
      is the StereoTopBottomCamera.
    @see: StereoInterface
    """

    defaultStereoCamera = StereoTopBottomCamera

    def __init__(self, interface):
        StereoInterface.__init__(self, interface)
        interface.keyMap['+'] = self.stereoRightUp # tweak left/right eye
        interface.keyMap['-'] = self.stereoRightDown # alignment
            
    def stereoRightUp(self, empty=None):
        """Adjust vertical alignment of left/right views."""
        self.engine.tb_offset += 1
        raise spyre.EngineReSetupException

    def stereoRightDown(self, empty=None):
        """Adjust vertical alignment of left/right views."""
        self.engine.tb_offset -= 1
        if self.engine.tb_offset < 0: 
            self.engine.tb_offset = 0
        raise spyre.EngineReSetupException

    def __setattr__(self, attname, val):
        """Delegate most attribute lookups."""
        if attname == 'iface':
            self.__dict__['iface'] = val
        else:
            object.__setattr__(self.__dict__['iface'], attname, val)


class StereoRedBlueInterface(StereoInterface):
    """Stereo interface for red/blue glasses. 

    @cvar defaultStereoCamera: designated camera for this stereo mode
      is the StereoRedBlueCamera.
    @see: StereoInterface
    """
    defaultStereoCamera = StereoRedBlueCamera
    

# StereoEngineED  ==============================

class StereoEngine(spyre.Object):
    """Abstract class for Engine.  This class (or its subclass) 
    wraps a non-stereo engine, 
    
    A StereoEngine subclass will typically be the only 
    class you use directly from this module.
    
    A StereoEngine will set up all the code necessary to
    maintain the stereo visuals.
    
    The behavior of your program will depend on the selection
    of non-stereo cameras, interfaces, engine (and timekeeper 
    and studio) you set up before wrapping the engine with 
    StereoEngine.
    """
    
    defaultStereoInterface = None
    
    def __init__(self, engine):
        """Initialize new instance.     
        @param engine: a non-stereo engine
        """
        engine.title += 'Stereo3dSpyre'
        self.engine = engine
        self.inited = False
        
    def setup(self):
        """Do setup after all components are initialized. """
        self.engine.setup()
        self.engine.interface = self.defaultStereoInterface(self.engine.interface)
    
    def go(self):
        """Main loop."""
        self.setup()
        self.engine.go()
    
    def __getattr__(self, attname):
        """Pass attribute requests through to engine component."""
        return getattr(self.engine, attname)

    def __setattr__(self, attname, val):
        """Pass attribute assignments through to engine component."""
        if attname == 'engine':
            self.__dict__['engine'] = val
        elif attname == 'inited':
            self.__dict__['inited'] = val
        else:
            object.__setattr__(self.__dict__['engine'], attname, val)


class StereoEngineED(StereoEngine):
    """The engine manages the window, handles high-level displaying
    and updating, for eDimensional LCD glasses.
    
    The L{stereo} and L{noStereo} methods display the graphic
    patterns necessary to put the edimensional dongle into or out off
    stereoscopic display mode, to be viewed via LCD goggles.
    
    These will be invoked before the first engine display, and on
    program exit.
    """

    defaultStereoInterface = StereoTopBottomInterface

    def __init__(self, engine):
        """Initialize engine instance. 
        @param engine: non-stereo engine instance, must be fullscreen.
        """
        StereoEngine.__init__(self, engine)
        engine.tb_offset = 19
        if not self.engine.mode & FULLSCREEN:
            raise Exception('edimensional mode requires fullscreen engine')
        if not self.inited:
            self.init()
            self.inited = True
            atexit.register(self.unInit)
    
    def stereo(self):
        """Put display in stereo 3D mode. Display signal image for 
        edimensional glasses 3D ON.
        """
        surface = pygame.display.set_mode((self.width, self.height), FULLSCREEN) 
        pygame.draw.line(surface, (255,0,0),   (0,1), (self.width-1,1), 2)
        pygame.draw.line(surface, (0,255,0),   (0,3), (self.width-1,3), 2)
        pygame.draw.line(surface, (255,255,0), (0,5), (self.width-1,5), 2)
        pygame.draw.line(surface, (255,255,0), (0,7), (self.width-1,7), 2)
        pygame.draw.line(surface, (255,255,0), (0,9), (self.width-1,9), 2)
        pygame.display.flip()
        time.sleep(0.6)
        pygame.display.quit()

    def noStereo(self):
        """Put display in non-stereo mode. Display signal image for 
        edimensional glasses 3D OFF.
        """
        surface = pygame.display.set_mode((self.width, self.height), FULLSCREEN) 
        pygame.draw.line(surface, (255,0,0),   (0,1), (self.width-1,1), 2)
        pygame.draw.line(surface, (0,255,0),   (0,3), (self.width-1,3), 2)
        pygame.draw.line(surface, (255,255,0), (0,5), (self.width-1,5), 2)
        pygame.draw.line(surface, (255,255,0), (0,7), (self.width-1,7), 2)
        pygame.draw.line(surface, (0,0,0),     (0,9), (self.width-1,9), 2)
        pygame.display.flip()
        time.sleep(0.6)
        pygame.display.quit()

    def init(self):
        """Initialize stereo mode via stereo method. """
        self.stereo()
        
    def unInit(self):
        """Uninitialize stereo mode for normal video viewing. """
        self.noStereo()


class StereoEngineRB(StereoEngine):
    """The engine manages the window, handles high-level displaying
    and updating, for red/blue glasses.
    """

    defaultStereoInterface = StereoRedBlueInterface

    
