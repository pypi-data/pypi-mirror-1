#!/usr/local/bin/python
"""
SPyRE -> Simple Pythonic Rendering Engine.
A simple OpenGL rendering engine 

Spyre has five types of objects which together make up the engine.

Engine::
    Includes main loop, handles event queue, passing input data to 
    interface, maintaining viewport and tracking and displaying 
    objects.
    
Interface::
    Controls the primary camera, the engine, and the timekeeper in 
    response to user input.
    
Camera::
    Maintains eye position and direction of view, as well as projection
    config (frustum or ortho).   Different cameras are suited to different
    interfaces, but MobileCamera is common.
    
Studio::
    Maintains lights, including fixed, mobile, and camera-mounted types; 
    and depth-cueing (fog) and some materials details.
    
TimeKeeper::
    Controls pace of engine run, can switch engine advancement on and
    off.  Also controls and monitors framerate.
    
Object::
    In addition to the above five elements of the engine assembly, there are 
    displayable objects.  These all descend from the Object class.

An ultra-simple example::
    This is not tested. See scripts in demos directory for
    tested code.
    =========================
    import spyre
    import OpenGL.GLU as oglu

    # create displayable object, subclassing Object
    def Sphere(spyre.Object):
        def __init__(self, diameter): self.rad = diameter/2.0 
        def display(self):
            quad   = oglu.gluNewQuadric()
            oglu.gluSphere(quad, self.rad, 60, 60)

    sph = Sphere()
        
    engine = Engine()
    engine.add(sph)

    engine.go()
    ===========================
@group Engine: Engine, EngineFullScreen
@group Timekeeper: TimeKeeper
@group Studios: StudioColorMat, Light, Sun, Bulb, Spot, NullStudio
@group Interfaces: Interface, BareBonesInterface, BasicInterface, PivotingInterface,
  PanningInterface, PedestrianInterface, PedestrianInterfaceY, CursorKeyInterface
@group Camera: Camera, MobileCamera, MobileCameraFrustum, MobileCameraOrtho, BasicCamera,
  BasicCameraOrtho, BasicCameraFrustum, PrecessingCamera, PrecessingCameraOrtho,
  RovingCamera, RovingCameraFrustum, RovingCameraFrustumY, RovingCameraOrtho,
  RovingCameraOrthoY, RovingCameraY, FrustumCam, OrthoCam
@group others: Object, Group
@undocumented: Rect
"""

__program__ = 'SPyRE'
__version__ = '0.7.1'
__url__ = 'http://pduel.sourceforge.net/'
__author__ = 'David Keeney <dkeeney@travelbyroad.net>'
__copyright__ = 'Copyright (C) 2000-2006 Erik Max Francis, 2004-2005 David Keeney'
__license__ = 'LGPL'


import math
import sys
import types
import time

import la

from pygame import display, key, init, event
from pygame import time as pytime
from pygame.locals import *
import OpenGL.GL as ogl
import OpenGL.GLU as oglu

# Some mathematical constants for convenience.
pi = math.pi
twoPi = 2*pi
piOverTwo = pi/2
piOverOneEighty = pi/180
radiansToDegrees = 1/piOverOneEighty
degreesToRadians = piOverOneEighty
sqrtTwo = math.sqrt(2)

# events
REDRAW_TIMER = USEREVENT +1

def cartesianToSpherical (x, y, z):
    """Convert cartesion coords (x,y,z) to spherical (rho,theta,phi)."""

    rho = math.sqrt(x*x + y*y + z*z)
    phi = math.asin(z/rho)
    r = rho*math.cos(phi)
    if r < abs(y): r = abs(y)
    assert(y/r <= 1)
    assert(y/r >= -1)
    if x == 0:
        theta = math.asin(y/r)
    else:
        theta = math.atan(y/x)
        if (x < 0):
            theta += pi
    return rho, theta, phi

def sphericalToCartesian (rho, theta, phi):
    """Convert spherical (rho,theta,phi) to cartesion coords (x,y,z)."""
    if abs(phi) > piOverTwo:
        raise ValueError, phi
    if abs(theta) > twoPi:
        raise ValueError, theta
    x = rho * math.cos(phi) * math.cos(theta)
    y = rho * math.cos(phi) * math.sin(theta)
    z = rho * math.sin(phi)
    return x, y, z


# Object #=====================================================================

class Object(object):  # making class 'new-style' 

    """The fundamental object. Contains class variables for run time 
    and run (turn) counter.
    
    All displayable objects should subclass from this.  In addition to the 
    inherited method 'display', a displayable object may have an 'update' and
    'commit' methods.
    
    The class vars runTime and runTurn are maintained by the TimeKeeper instance.
   
    @cvar runTime: how long has engine been running?
    @cvar runTurn: how many frames have elapsed?
    @cvar engine: makes engine accessible to displayable objects.
    """
    
    # reference to current engine
    engine = None
    
    # list of opengl state dependant objects
    opengl_state_dependent = []
    
    # these class vars track engine runtime (fictional)
    #   and turn counts
    #  these are typically maintained/manipulated by a runTimer object
    #
    runTime = 0.0
    runTurn = 0

    def __init__(self):
        """Abstract initializer."""
        if self.__class__ is Object:
            raise NotImplementedError
    
    def display(self):
        """Display the object using OpenGL  This method must be overridden."""
        raise NotImplementedError
    

## various Object descendants from zoe are now in the zoeobj.py file

# Camera =====================================================================

## ------ these are mixins to provide ortho/perspective to -------
## ------ various cameras ----------------------------------------

class OrthoCam(object):
    """An OrthoCam is a mixin that provides for ortho mode 
    in descendant cameras. 
      
    Each camera installed in an engine must inherit from either
    FrustumCam or OrthoCam.
    """
    def viewProj(self):
        """Pushes ortho params/settings through to OpenGL """
        ogl.glMatrixMode(ogl.GL_PROJECTION)
        ogl.glLoadIdentity()
        ogl.glOrtho(self.left, self.right, 
                self.bottom, self.top, 
                self.near, self.far)
                
    def viewMV(self):
        """Sets eye and center position in OpenGL """
        ogl.glMatrixMode(ogl.GL_MODELVIEW)
        ogl.glLoadIdentity()
        oglu.gluLookAt(self.eye[0], self.eye[1], self.eye[2],
                  self.center[0], self.center[1], self.center[2],
                  self.up[0], self.up[1], self.up[2])

    def shape(self, left, right, bottom, top, near=None, far=None):
        """Sets frustum shape members.
        (left, top, near) and (right, bottom, near) map to the diametrical
        opposite corners of the viewport, in x,y,z coords, modelview space.
        
        near and far params are optional, and if ommitted, prior attribute
        values remain.  all params are floats.
        """
        if near != None:
            self.near = near
        if far != None:
            self.far = far
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        
    ortho = shape


class FrustumCam(OrthoCam):
    """A FrustumCam is a mixin that provides for frustum (perspective) mode 
    in descendant cameras.    
      
    Each camera installed in an engine must inherit from either
    FrustumCam or OrthoCam.
    """
    def viewProj(self):
        """Pushes frustum params/settings through to OpenGL """
        ogl.glMatrixMode(ogl.GL_PROJECTION)
        ogl.glLoadIdentity()
        ogl.glFrustum(self.left, self.right, 
                      self.bottom, self.top, 
                      self.near, self.far)
                
    frustum = OrthoCam.shape
        
    def perspective(self, fovy, aspect, near, far):
        """Alternate way to specify frustum.
        @param fovy: field of view angle, degrees
        @param aspect: height/width (float)
        @param near: near side of viewing box (float)
        @param far: far side of viewing box (float)
        """
        # from Mesa source, Brian Paul
        ymax = near * math.tan(fovy * pi / 360.0)
        ymin = -ymax
        xmin = ymin * aspect
        xmax = ymax * aspect

        self.frustum(xmin, xmax, ymin, ymax, near, far)


## -- the cameras -------------------

class Camera(object):
    """Abstract camera base class.  A usable camera would inherit from
    this, and from FrustumCam or OrthoCam. 
    
    Each engine must have at least one camera.  If none are provided
    by programmer, the interface will install its preferred camera.
    
    Each camera tracks its own viewport, which is by default the
    size of the window.
    
    @ivar objects:  Each camera keeps a list of displayable objects. 
        By default this is a reference to the engines list, and all
        objects are displayed for each camera.  This behavior can
        be overriden such that each camera displays a subset of 
        displayable objects.
    @sort: __init__, setup, eye, center, zoomIn, zoomOut, setViewport, 
      displayViewport, displayBackground
    @undocumented: object
    """
    
    def __init__(self, engine, eye, center, up,
                  left, right, bottom, top, near, far):
        """Initialize new camera.
        @param engine: the engine
        @param eye: x,y,z tuple with eye position
        @param center: x,y,z tuple with center of view
        @param up: x,y,z tuple pointing up
        @param left: left edge of viewing box, in eyespace (float)
        @param right: right edge of viewing box, in eyespace (float)
        @param bottom: bottom edge of viewing box, in eyespace (float)
        @param top: top edge of viewing box, in eyespace (float)
        @param near: near edge of viewing box, in eyespace (float)
        @param far: far edge of viewing box, in eyespace (float)"""
        self.engine = engine        
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.near = near
        self.far = far
        self._eye = eye
        self._center = center
        self.up = up
        self.background = (0,0,0,0)
        self.fractViewport = (0,0,1,1)
        self.viewport = (0, 0, self.engine.width, self.engine.height) 
        self.objects = engine.objects
        self.saveInit()
        self.dirty = True

    def setup(self):
        """Overridable for things to be done before use, but after engine
        and interface are initialized.
        """
        self.setViewport(*self.fractViewport)

    def saveInit(self):
        """Save state of initialization internally for later restoration."""
        self.__saveinit = (self._eye, self._center, 
                           self.left, self.right, 
                           self.bottom, self.top,
                           self.near, self.far)

    def restoreInit(self):
        """Restore previously saved initialization state."""
        stuff = self.__saveinit
        self._eye = stuff[0]
        self._center = stuff[1]
        self.left, self.right, self.bottom, self.top, self.near, \
            self.far = stuff[2:]

    def _getCtr(self):
        """ methods to access center position property """
        return self._center
        
    def _setCtr(self, cntr):
        self._center = cntr
        self.dirty = True

    center = property(_getCtr, _setCtr, None, "Track center position")

    def _getEye(self):
        """ methods to access eye position property """
        return self._eye
        
    def _setEye(self, eye):
        self._eye = eye
        self.dirty = True

    eye = property(_getEye, _setEye, None, "Track eye position")

    def zoomIn(self, factor=sqrtTwo):
        """Zoom in. Narrows the viewing box.  
        
        @param factor: ratio of old width to new width.
        """
        self.left /= factor
        self.right /= factor
        self.top /= factor
        self.bottom /= factor
        self.dirty = True

    def zoomOut(self, factor=sqrtTwo):
        """Zoom out. Widens the viewing box.
        
        @param factor: ratio of new width to old width.
        """
        self.left *= factor
        self.right *= factor
        self.top *= factor
        self.bottom *= factor
        self.dirty = True

    def refresh(self):
        """Refresh the position of the camera."""
        pass

    def displayBackground(self):
        """Clear the display, or alternate prelim treatment.
        Always clears depth buffer, clears color if background
        attribute is set.  This method can be overridden for
        multiviewport effects.
        """
        bits = ogl.GL_DEPTH_BUFFER_BIT
        if self.background:
            ogl.glClearColor(*self.background)
            bits |= ogl.GL_COLOR_BUFFER_BIT
        ogl.glClear(bits)

    def displayViewport(self):
        """Push the viewport params to OpenGL."""
        ogl.glViewport(*self.viewport)
        ogl.glScissor(*self.viewport)

    def setViewport(self, left, top, right, bottom):
        """Record desired viewport (left, top, right, bottom). Each value 
        is in range 0-1, representing fraction of window. The default 
        (0,0,1,1) is entire window.
        """
        self.fractViewport = (left, top, right, bottom)
        assert(max(self.fractViewport)<=1)
        assert(min(self.fractViewport)>=0)
        w, h = self.engine.width, self.engine.height
        self.viewport = (int(left*w), int(top*h), 
          int((right-left)*w), int((bottom-top)*h))


class BasicCamera(Camera):
    """A basic camera views a center point from an eye position, with
    a reference up vector that points to the top of the screen.
    """
    
    def __init__( self, engine, eye,
                  center = (0,0,0), up = (0,1,0),
                  left=None, right=None, 
                  bottom=None, top=None, 
                  near=None, far=None):
        if left is None: left = -5
        if right is None: right = 5
        if top is None: top = 5
        if bottom is None: bottom = -5
        if near is None: near = 1
        if far is None: far = 11
        Camera.__init__(self, engine, eye, center, up,
                        left, right, bottom, top, near, far)
        self.saveInit()


class BasicCameraFrustum(FrustumCam, BasicCamera):
    pass


class BasicCameraOrtho(OrthoCam, BasicCamera):
    pass


class PrecessingCamera(BasicCamera):
    """A precessing camera orbits around the z axis at a given
    distance from it and height above the x-y plane."""
    
    def __init__(self, engine, distance, height, rate, \
                 center=(0, 0, 0), up=(0, 0, 1)):
        BasicCamera.__init__(self, engine, None, center, up)
        self.distance = distance
        self.height = height
        self.rate = rate
        self.angle = 0.0
        self.calc()

    def calc(self):
        """Recalculate postion of eye """
        self.eye = self.distance*math.cos(self.angle), \
                   self.distance*math.sin(self.angle), \
                   self.height

    def refresh(self):
        """Update calculated position """
        self.angle += self.rate
        if self.angle < 0:
            self.angle += twoPi
        elif self.angle >= twoPi:
            self.angle -= twoPi
        self.calc()


class PrecessingCameraOrtho(OrthoCam, PrecessingCamera):
    """ A precessing camera with Orthographic viewing projection """
    pass


class MobileCamera(BasicCamera):
    """A mobile camera maintains a certain distance (rho) from the
    origin, but is user controllable.
    """
    
    def __init__(self, engine, eyeRho, center=(0, 0, 0), up=(0, 0, 1)):
        """Initialize new camera.
        @param engine: the engine
        @param eyeRho: either a constant radius (float), or an eye position
          tuple (x,y,z)
        @param center: center of view tuple (x,y,z)
        """
        BasicCamera.__init__(self, engine, None, center, up)
        if type(eyeRho) == type((0,)):
            eyeVec = la.Vector(eyeRho[0]-center[0], \
                               eyeRho[1]-center[1], \
                               eyeRho[2]-center[2])
            rho = eyeVec.norm()
            phi = math.asin(eyeVec[2]/rho)
            r = rho * math.cos(phi)
            theta = math.acos(eyeVec[0]/r)
        else:
            rho = eyeRho
            theta = 0
            phi = 0
        self.rho = rho
        self.theta = theta
        self.phi = phi
        self.center = center
        self.calc()
        self.saveInit()

    def _getEye(self):
        return self._eye
        
    def _setEye(self, eye):
        """ methods to set eye position property. """
        ctr = self.center
        if type(eye) == type((1,)):
            self.rho, self.theta, self.phi = \
                cartesianToSpherical(eye[0]-ctr[0], 
                                     eye[1]-ctr[1],
                                     eye[2]-ctr[2],)
            self.calc()
            self.dirty = True

    eye = property(_getEye, _setEye, "Maintain eye position, converting to spherical coords.")

    def calc(self): 
        ctr = self.center
        there = sphericalToCartesian(self.rho, self.theta, self.phi)
        self._eye = (there[0]+ctr[0], 
                     there[1]+ctr[1], 
                     there[2]+ctr[2])
    
    def refresh(self):
        self.calc()


class MobileCameraOrtho(OrthoCam, MobileCamera):
    """ A mobile camera with Orthographic viewing projection """
    pass


class MobileCameraFrustum(FrustumCam, MobileCamera):
    """ A mobile camera with Frustum viewing projection """
    pass


class RovingCamera(BasicCamera):
    """A roving camera moves around the scene. Used with pedestrian interface. """
    
    def __init__(self, engine, eye=(2,2,2), center=(0,0,0), up=(0,0,1), elev=None):
        """Initialize new camera.
        @param engine: the engine
        @param eye: eye position tuple (x,y,z)
        @param center: center of view type (x,y,z)
        @param up: up vector tuple (x,y,z)
        @param elev: (optional) function to give elevation z 
          for any x,y pair. defaults to 0
        """
        self.saveEye = eye
        self.saveCenter = center
        BasicCamera.__init__(self, engine, eye, center, up)
        if elev == None: 
            elev = lambda x,y: 0
        self.rho = math.sqrt((center[0]-eye[0])**2 + 
                             (center[1]-eye[1])**2)
        self.theta = math.acos((center[0]-eye[0])/self.rho)
        if eye[1] > center[1]:
            self.theta = twoPi -self.theta
        self.camHeight = eye[2] - elev(eye[0], eye[1])
        self.ctrHeight = center[2] - elev(*center[0:2])
        self.elev = elev
        self.calc()
        self.saveInit()

    def calc(self):
        """calculate center position from eye pos """
        ex, ey, ez = self.eye
        cx = self.rho * math.cos(self.theta) + ex
        cy = self.rho * math.sin(self.theta) + ey
        cz = self.elev(cx, cy) + self.ctrHeight
        self.center = (cx, cy, cz)

    def refresh(self):
        self.calc()


class RovingCameraFrustum(FrustumCam, RovingCamera):
    """ a roving camera with frustum projection """
    pass


class RovingCameraOrtho(OrthoCam, RovingCamera):
    """ a roving camera with ortho projection """
    pass


class RovingCameraY(BasicCamera):
    """ A roving camera moves around the scene, panning on xz plane. Used with 
    PedestrianInterfaceY. 
    """
    
    def __init__(self, engine, eye=(2,2,2), center=(0,0,0), up=(0,0,1), elev=None):
        self.saveEye = eye
        self.saveCenter = center
        BasicCamera.__init__(self, engine, eye, center, up)
        if elev == None: 
            elev = lambda x,y: 0
        self.rho = math.sqrt((center[0]-eye[0])**2 + 
                             (center[2]-eye[2])**2)
        self.theta = math.acos((center[0]-eye[0])/self.rho)
        if eye[2] < center[2]:
            self.theta = twoPi - self.theta
        self.camHeight = eye[1] - elev(eye[0], eye[2])
        self.ctrHeight = center[1] - elev(center[0], center[2])
        self.elev = elev
        self.calc()
        self.saveInit()

    def calc(self):
        """calculate center position from eye pos """
        ex, ey, ez = self.eye
        cx = self.rho * math.cos(self.theta) + ex
        cz = self.rho * math.sin(self.theta) + ez
        cy = self.elev(cx, cz) + self.ctrHeight
        self.center = (cx, cy, cz)

    def refresh(self):
        self.calc()


class RovingCameraFrustumY(FrustumCam, RovingCameraY):
    """RovingCameraY with Frustum """
    pass


class RovingCameraOrthoY(OrthoCam, RovingCameraY):
    """RovingCameraY with Frustum """
    pass


# Interface ================================================================

class Interface(object):
    """The interface encapsulates all the user interface behavior that
    an engine can exhibit.
    
    @cvar defaultCamera: preferred camera class and default __init__ params
    """
    
    defaultCamera = BasicCameraOrtho, ((5,5,5),)

    def __init__(self, engine):
        """Initialize new instance.
        @param engine: the engine
        """
        self.engine = engine
        engine.interface = self
        self.keyMap = {} # mapping for keys and special keys
        self.buttons = [] # list of buttons currently pressed
        self.lastButton = None # last button pressed
        self.mouseMark = None # last mouse down location
        self.visible = 0 # is window currently visible

    def setup(self):
        """Setup interface after components all exist. """
        if self.engine.camera and not self.engine.cameras:
            self.engine.addCamera(self.engine.camera)
        if not self.engine.cameras:
            functor, args = self.defaultCamera
            cam = functor(*((self.engine,) + args))
            self.engine.addCamera(cam)
        for c in self.engine.cameras:
            c.setup()

    def _mouse(self, button, state, loc):
        """The mouse event wrapper. Private method: Override
        mouseDown or mouseUp rather than this.
        """
        if state:
            self.buttons.append(button)
            self.lastButton = button
            self.mouseMark = loc
            self.mouseDown(button, loc)
        else:
            self.buttons.remove(button)
            self.lastButton = None
            self.mouseMark = None
            self.mouseUp(button, loc)

    def _motion(self, loc):
        """The mouse motion wrapper.  Private method: Override
        mouseDrag or MouseMove rather than this.
        """
        if self.lastButton:
            self.mouseDrag(self.lastButton, loc)
        else:
            self.mouseMove(loc)

    def _visibility(self, visible):
        """The visibility wrapper."""
        if visible != self.visible:
            self.visibilityChange(visible)
            self.visible = visible

    def _entry(self, entry):
        """The window entry wrapper."""
        pass

    # The following should be overridden by subclasses.

    def keyPressed(self, key):
        """A key was pressed.
        @param key: ascii value.
        """
        loc = self.mouseMark
        if self.keyMap.has_key(key):
            self.keyMap[key](loc)

    def mouseDown(self, button, loc):
        """The specified mouse button was clicked while the mouse was at
        the given location.
        @param button: which button was pressed
        @param loc: x,y tuple with mouse position
        """
        self.lastButton = button
        self.mouseMark = loc
    
    def mouseUp(self, button, loc):
        """The specified mouse button was released while the mouse was at
        the given location.
        @param button: which button was pressed
        @param loc: x,y tuple with mouse position
        """
        self.lastButton = None
        self.mouseMark = None

    def mouseMove(self, loc):
        """The mouse moved with no buttons pressed."""
        raise NotImplementedError('mouseMove')
        
    def mouseDrag(self, button, loc):
        """The mouse was dragged to the specified location while the given
        mouse button was held down.
        """
        raise NotImplementedError('mouseDrag')

    def entryChange(self, entered):
        """The mouse moved into or out of the window."""
        raise NotImplementedError('entryChange');

    def visibilityChange(self, visible):
        """The window had a visibility chnage."""
        raise NotImplementedError('visibilityChange');


class BareBonesInterface(Interface):
    """A bare-bones interface supports quitting, and resizing."""
    
    def __init__(self, engine):
        Interface.__init__(self, engine)
        self.keyMap['q'] = self.quit
        self.keyMap['\033'] = self.quit
        self.keyMap[K_F12] = self.engine.dumpStats
        self.keyMap['>'] = self.sizeUp
        self.keyMap['<'] = self.sizeDown
        self.keyMap['r'] = self.reset
 
    def event(self, ev):
        """Handle all interface events (from Pygame events)
        @param ev: pygame event 
        """
        if ev.type == VIDEORESIZE:
            pass
        elif ev.type == KEYDOWN:
            if ev.key < 256:
                key = ev.unicode.encode('ascii') 
            else:
                key = ev.key
            self.keyPressed(key)
        elif ev.type == KEYUP:
            pass
        elif ev.type == MOUSEMOTION:
            self._motion(ev.pos)
        elif ev.type == MOUSEBUTTONUP:
            self.mouseUp(ev.button, ev.pos)
        elif ev.type == MOUSEBUTTONDOWN:
            self.mouseDown(ev.button, ev.pos)
        elif ev.type == QUIT:
            self.quit()

    def quit(self, empty=None): self.engine.quit()
    def reset(self, empty=None): 
        """Resets all cameras."""
        for c in self.engine.cameras:
            c.restoreInit()
    
    def sizeUp(self, empty):
        """Increase window size."""
        self.engine.reshape(self.engine.width*2, self.engine.height*2)

    def sizeDown(self, empty):
        """Decrease window size."""
        self.engine.reshape(self.engine.width/2, self.engine.height/2)

    def mouseMove(self, loc):
        """The mouse moved with no buttons pressed."""
        pass
        
    def mouseDrag(self, button, loc):
        """The mouse was dragged to the specified location while the given
        mouse button was held down."""
        pass
        
    def entryChange(self, entered):
        """The mouse moved into or out of the window."""
        pass

    def visibilityChange(self, visible):
        """The window had a visibility chnage."""
        pass


class BasicInterface(BareBonesInterface):
    """A basic interface supports quitting, pausing, stepping,
    zooming, and resizing.
    """
    
    def __init__(self, engine):
        BareBonesInterface.__init__(self, engine)
        self.keyMap[' '] = self.toggle
        self.keyMap['z'] = self.zoomIn
        self.keyMap['Z'] = self.zoomOut
        self.keyMap['\r'] = self.step
                             
    def toggle(self, empty): 
        """Toggle engine progress on/off. """
        self.engine.runTimer.toggle()
        
    def step(self, empty): 
        """Advance engine one step only. """
        self.engine.runTimer.step()
    
    def zoomIn(self, empty):
        """Zoom in on principle camera."""
        self.engine.camera.zoomIn()
        self.engine.redisplay()
        
    def zoomOut(self, empty):
        """Zoom out on principle camera. """
        self.engine.camera.zoomOut()
        self.engine.redisplay()


class PivotingInterface(BasicInterface):
    """A pivoting interface supports the basic interfaces and can be
    pivoted around the center point with the mouse.
    
    @cvar sensitivity: how sensitive is view to mouse motion
    """
    
    defaultCamera = MobileCameraOrtho, (5.0,)
    sensitivity = 2
    
    def __init__(self, engine):
        BasicInterface.__init__(self, engine)

    def mouseDrag(self, button, loc):
        """Process mouse drag event.
        @param loc: x,y tuple for new mouse loc
        """
        cam = self.engine.camera
        abT = (1.0*loc[0]/self.engine.width)*cam.right, \
              (-1.0*loc[1]/self.engine.height)*cam.top
        abS = (1.0*self.mouseMark[0]/self.engine.width)*cam.right, \
              (-1.0*self.mouseMark[1]/self.engine.height)*cam.top
        deltaX = -self.sensitivity*(abT[0]-abS[0])
        deltaY = -self.sensitivity*(abT[1]-abS[1])
        eyeVec = la.Vector(cam.eye[0]-cam.center[0], \
                            cam.eye[1]-cam.center[1], \
                            cam.eye[2]-cam.center[2])
        upVec = la.Vector(*cam.up).unit()
        leftVec = eyeVec.cross(upVec).unit()
        assert(leftVec.dot(upVec) < 0.0001)
        assert(leftVec.dot(eyeVec) < 0.0001)
        if deltaX:
            lVec = leftVec * deltaX
            eyeVec = eyeVec + lVec
        upVec = leftVec.cross(eyeVec).unit()
        assert(upVec.dot(leftVec) < 0.0001)
        assert(upVec.dot(eyeVec) < 0.0001)
        if deltaY:
            uVec = upVec * deltaY
            eyeVec = eyeVec + uVec
        eyeVec = eyeVec.unit() * cam.rho
        cam.up = (upVec.x, upVec.y, upVec.z)

        # calculate spherical coords
        cam.rho, cam.theta, cam.phi = \
            cartesianToSpherical(eyeVec.x, eyeVec.y, eyeVec.z)
        self.mouseMark = loc
        cam.refresh()
        self.engine.redisplay()


class PanningInterface(PivotingInterface):
    """ A panning interface supports all the pivoting and basic
    behavior, but the pivoting point can be moved with the keyboard.
    
    @cvar increment: how far to move center per keystroke
    """
    
    increment = 0.1
    
    def __init__(self, engine):
        PivotingInterface.__init__(self, engine)
        self.keyMap['d'] = self.panPositiveX
        self.keyMap['a'] = self.panNegativeX
        self.keyMap['w'] = self.panPositiveY
        self.keyMap['x'] = self.panNegativeY
        self.keyMap['e'] = self.panPositiveZ
        self.keyMap['c'] = self.panNegativeZ
  #      self.keyMap['s'] = self.resetPan

    def panPositiveX(self, empty=None):
        cam = self.engine.camera
        x = cam.center[0] + self.increment
        cam.center = x, cam.center[1], cam.center[2]
        
    def panNegativeX(self, empty=None):
        cam = self.engine.camera
        x = cam.center[0] - self.increment
        cam.center = x, cam.center[1], cam.center[2]
        
    def panPositiveY(self, empty=None): 
        cam = self.engine.camera
        y = cam.center[1] + self.increment
        cam.center = cam.center[0], y, cam.center[2]
        
    def panNegativeY(self, empty=None):
        cam = self.engine.camera
        y = cam.center[1] - self.increment
        cam.center = cam.center[0], y, cam.center[2]
        
    def panPositiveZ(self, empty=None): 
        cam = self.engine.camera
        z = cam.center[2] + self.increment
        cam.center = cam.center[0], cam.center[1], z
        
    def panNegativeZ(self, empty=None): 
        cam = self.engine.camera
        z = cam.center[2] - self.increment
        cam.center = cam.center[0], cam.center[1], z
        
    def resetPan(self, empty=None):
        self.engine.camera.center = 0.0, 0.0, 0.0


class PedestrianInterface(BasicInterface):
    """A pedestrian interface moves the camera on a roughly horizontal plane.
    (constant z).  The cursor keys move the viewpoint directly, and the camera
    indirectly.

    @cvar rotate_inc: how far to rotate camera per keystroke.
    """
    
    defaultCamera = RovingCameraOrtho, ()

    increment = 0.05
    rotate_inc = 0.02
    
    def __init__(self, engine):
        BasicInterface.__init__(self, engine)
        self.stepSize = self.engine.camera.rho * self.increment
        self.keyMap[' '] = self.forward
        self.keyMap['\b'] = self.backward
        self.keyMap['l'] = self.left
        self.keyMap['r'] = self.right
        self.keyMap[K_UP] = self.forward
        self.keyMap[K_DOWN] = self.backward
        self.keyMap[K_LEFT] = self.left
        self.keyMap[K_RIGHT] = self.right
        key.set_repeat(500, 30)

    def forward(self, empty=None):
        """Move camera forward."""
        self.moveCam(self.stepSize)
        self.engine.camera.calc()
    
    def backward(self, empty=None):
        """Move camera backward."""
        self.moveCam(-self.stepSize)
        self.engine.camera.calc()

    def moveCam(self, inc):
        cam = self.engine.camera
        x = cam.eye[0] + inc * math.cos(cam.theta)
        y = cam.eye[1] + inc * math.sin(cam.theta)
        cam.eye = x, y, cam.elev(x, y)+cam.camHeight
        cam.calc()
  
    def left(self, empty=None):
        """Rotate camera left."""
        cam = self.engine.camera
        cam.theta += self.rotate_inc
        if cam.theta > twoPi:
            cam.theta = twoPi - cam.theta
        cam.calc()

    def right(self, empty=None):
        """Rotate camera right."""
        cam = self.engine.camera
        cam.theta -= self.rotate_inc
        if cam.theta < 0:
            cam.theta = twoPi + cam.theta
        cam.calc()


class PedestrianInterfaceY(PedestrianInterface):
    """ PedestrianInterface for xz plane panning """

    def moveCam(self, inc):
        """Override moveCam to change plane of motion to x,z """
        cam = self.engine.camera
        x = cam.eye[0] + inc * math.cos(cam.theta)
        z = cam.eye[2] - inc * math.sin(cam.theta)
        cam.eye = x, cam.elev(x, z)+cam.camHeight, z
        cam.calc()


class CursorKeyInterface(PanningInterface):

    """ A cursorkey interface supports all the pivoting and basic
        behavior, but the pivoting is done by cursor keys rather than
        by mouse.
    """
    
    increment = 10
    
    def __init__(self, engine):
        PanningInterface.__init__(self, engine)
        self.keyMap[K_UP] = self.pivotUp
        self.keyMap[K_DOWN] = self.pivotDown
        self.keyMap[K_LEFT] = self.pivotLeft
        self.keyMap[K_RIGHT] = self.pivotRight
        self.mouseLoc = (0,0)
        key.set_repeat(500, 50) 

    def pivotUp(self, empty=None): 
        ev = event.Event(MOUSEBUTTONDOWN, pos=(0,0), button=1) 
        event.post(ev)
        ev = event.Event(MOUSEMOTION,     
                            pos=(self.mouseLoc[0],self.mouseLoc[1]+self.increment),   
                            rel=(0,0), 
                            buttons=(1)) 
        event.post(ev)
        ev = event.Event(MOUSEBUTTONUP,   pos=(0,0), button=1) 
        event.post(ev)
        
    def pivotDown(self, empty=None):
        ev = event.Event(MOUSEBUTTONDOWN, pos=(0,0), button=1) 
        event.post(ev)
        ev = event.Event(MOUSEMOTION,     
                            pos=(self.mouseLoc[0],self.mouseLoc[1]-self.increment),   
                            rel=(0,0), 
                            buttons=(1)) 
        event.post(ev)
        ev = event.Event(MOUSEBUTTONUP,   pos=(0,0), button=1) 
        event.post(ev)
        
    def pivotLeft(self, empty=None): 
        ev = event.Event(MOUSEBUTTONDOWN, pos=(0,0), button=1) 
        event.post(ev)
        ev = event.Event(MOUSEMOTION,     
                            pos=(self.mouseLoc[0]-self.increment,self.mouseLoc[1]),   
                            rel=(0,0), 
                            buttons=(1)) 
        event.post(ev)
        ev = event.Event(MOUSEBUTTONUP,   pos=(0,0), button=1) 
        event.post(ev)
        
    def pivotRight(self, empty=None):
        ev = event.Event(MOUSEBUTTONDOWN, pos=(0,0), button=1) 
        event.post(ev)
        ev = event.Event(MOUSEMOTION,     
                            pos=(self.mouseLoc[0]+self.increment,self.mouseLoc[1]),   
                            rel=(0,0), 
                            buttons=(1)) 
        event.post(ev)
        ev = event.Event(MOUSEBUTTONUP,   pos=(0,0), button=1) 
        event.post(ev)
        

# Light ======================================

class Light(object):
    
    """Implements each light. This class is concrete, so can be used
    to create light instances, but the subclasses may be more intuitive.
    
    You can create any number of lights, but only 8 can be on at a time.
    
    @cvar available_lights: keeps track of which light ids are available
      for use.
      
    @sort: on, off, display, setPosition
    """
    
    available_lights = [ ogl.GL_LIGHT7, ogl.GL_LIGHT6, ogl.GL_LIGHT5, ogl.GL_LIGHT4, 
                         ogl.GL_LIGHT3, ogl.GL_LIGHT2, ogl.GL_LIGHT1, ogl.GL_LIGHT0 ]
    
    def __init__(self, ambient=None, diffuse=None, specular=None, position=None,):  
        """Initialize new instance.
        @param ambient: 4 tuple rgba for 'ambient' light
        @param diffuse: 4 tuple rgba for 'diffuse' light
        @param specular: 4 tuple rgba for 'specular' (imaged) light
        @param position: 4 tuple, x,y,z and opengl-peculiar 4th value
        """
        self.id = None
        if not ambient: ambient = (0.2, 0.2, 0.2, 1.0)
        if not diffuse: diffuse = (0.6, 0.6, 0.6, 1.0)
        if not specular: specular = (1.0, 1.0, 1.0, 1.0)
        if not position: position = (0.0, 0.0, 0.0, 0.0)
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        ## attenuation?
        Light.setPosition(self, position)
        self.dirty = False
        if len(self.available_lights) > 0:
            self.on()
    
    def __del__(self):
        """Turn light off on destruction."""
        self.off()
    
    def on(self):
        """Turn light on """
        if not self.id:
            self.id = self.available_lights.pop()
            self.dirty = True
    
    def off(self):
        """Turn light off """
        if self.id:
            ogl.glDisable(self.id)
            self.available_lights.append(self.id)
            self.id = None
        self.dirty = False
    
    def setPosition(self, position):
        """Change position value. 
        @param position: 4 tuple with x,y,z,?
        """
        assert(len(position) == 4)
        self.position = position
    
    def display(self):
        """Push light params through to OpenGL """
        if self.id:
            ogl.glLightfv(self.id, ogl.GL_POSITION, self.position) 
            if self.dirty:
                ogl.glEnable(self.id)
                ogl.glLightfv(self.id, ogl.GL_AMBIENT, self.ambient) 
                ogl.glLightfv(self.id, ogl.GL_DIFFUSE, self.diffuse)
                ogl.glLightfv(self.id, ogl.GL_SPECULAR, self.specular)         
                # attenuation ?
                self.dirty = False

    def update(self):
        """ updates light """
        pass
        

class Sun(Light):
    """Implements light that stays at infinite distance """
    
    def __init__(self, ambient=None, diffuse=None, specular=None, direction=None):
        """Initialize new instance. 
        @param ambient: 4 tuple rgba for 'ambient' light
        @param diffuse: 4 tuple rgba for 'diffuse' light
        @param specular: 4 tuple rgba for 'specular' (imaged) light
        @param direction: 3 tuple, x,y,z direction light points
        """
        Light.__init__(self, ambient, diffuse, specular, None)
        if not direction:
            direction = (0.0, 1.0, 0.0)
        self.setDirection(direction)

    def setPosition(self, position):
        """Disable setPosition. """
        pass
        
    def setDirection(self, direction):
        """Sets direction light shines. """
        assert(len(direction) == 3)
        pos = [ -1*x for x in direction ]
        pos.append(1.0)
        self.position = pos


class Bulb(Light):
    """Implements point light """
    
    def __init__(self, ambient=None, diffuse=None, specular=None, position=None,):
        """Initialize new instance. 
        @param ambient: 4 tuple rgba for 'ambient' light
        @param diffuse: 4 tuple rgba for 'diffuse' light
        @param specular: 4 tuple rgba for 'specular' (imaged) light
        @param position: 3 tuple, x,y,z for location of light
        """
        Light.__init__(self, ambient, diffuse, specular, None)
        if not position:
            position = (0.0, 0.0, 0.0) 
        self.setPosition(position)

    def setPosition(self,position):
        """Set position of light. """
        pos = [ x for x in position ]
        pos.append(0.0)
        self.position = pos


class Spot(Bulb):
    """Implements a spotlight, with beam. """
    
    def __init__(self, cutoff, direction, ambient=None, diffuse=None, 
                    specular=None, position=None,):
        """Initialize new instance. 
        @param cutoff: angle in degrees for 'spot'
        @param direction: 3 tuple, x,y,z for direction light points
        @param ambient: 4 tuple rgba for 'ambient' light
        @param diffuse: 4 tuple rgba for 'diffuse' light
        @param specular: 4 tuple rgba for 'specular' (imaged) light
        @param position: 3 tuple, x,y,z for location of light
        """
        Bulb.__init__(self, ambient, diffuse, specular, position)
        self.cutoff = cutoff
        self.setDirection(direction)

    def display(self):
        """Pushes light params through to OpenGL """
        if self.id:
           ogl.glLightf (self.id, ogl.GL_SPOT_CUTOFF, self.cutoff);
           ogl.glLightf (self.id, ogl.GL_SPOT_DIRECTION, self.direction);
        Bulb.display(self)

    def setDirection(self, direction):
        """Set Direction light points """
        di = [ x for x in direction[0:4] ]
        di.append(1.0)
        self.direction = di


# Studio ======================================

class NullStudio(object):
    """Manage environmental effects such as lights and fog. """
    def __init__(self, engine):
        pass

    def setup(self):
        pass

    def lightsOut(self):
        """Disable all lighting """
        pass
        
    def lightsOK(self):
        """Enable lighting """
        pass

    def init(self):
        """Prep scene for lighting, set light models, colormaterial, etc... """
        pass

    def displayFixedLights(self):
        """Push all light params through to OpenGL """
        pass
                
    def addFixedLight(self,light,position=None):
        """Add a light to fixed lights array """
        pass

    def removeFixedLight(self,light):
        """Removes light from fixed lights array """
        pass

    def displayCamLights(self):
        """Push all light params through to OpenGL """
        pass
                
    def addCamLight(self,light,position=None):
        """Add a light to camera lights array """
        pass

    def removeCamLight(self,light):
        """Removes light from camera lights array """
        pass

    def displayMobileLights(self):
        """Push all light params through to OpenGL """
        pass
                
    def addMobileLight(self, light, mover=None, position=None):
        """Add a light to mobile lights array.  If mover 
        provided, studio will call update method of mover 
        periodically.  Same light can be passed as both.
        @param light: light to be added
        @param mover: typically a 'group' that moves, and contains
          the light. Can be same as light.
        @param position: x,y,z tuple with initial light position
        """
        pass

    def removeMobileLight(self,light):
        """Removes light from mobile lights array """
        pass

    def depthCueing(self,status=True,fmode=None,
                    density=None,near=None,far=None):
        """Initialize depth cueing.
        @param status: is depth cueing enabled?
        @param fmode: GL_LINEAR, GL_EXP, or GL_EXP2
        @param density: float > 0, ignored for GL_LINEAR mode
        @param near: how near the camera does fog start?
        @param far: how far from the camera does fog extend?
        """
        pass
        
    def display(self):
        pass
        
    def update(self):
        """Update the Mobile Lights (and whatever else) """
        pass

    def commit(self):
        """Commits the Mobile Lights (and whatever else) """
        pass


class StudioColorMat(NullStudio):
    """Manage environmental effects such as lights and fog """

    def __init__(self, engine, ambient= (0.15, 0.15, 0.15, 1.0)):
        """Initialize new instance.
        @param engine: the engine
        @param ambient: 4 tuple, rgba for ambient light color
        """
        self.lightsFixed = []
        self.lightsCam = []
        self.lightsMobile = []
        self.lightsMotion = []
        self.depthCue = None
        self.engine = engine
        self.ambient = ambient
        self.dirtyfog = True

    def init(self):
        pass

    def lightsOut(self):
        """Disable all lighting """
        ogl.glDisable(ogl.GL_LIGHTING)
        
    def lightsOK(self):
        """Enable lighting """
        ogl.glEnable(ogl.GL_LIGHTING)

    def setup(self):
        """Prep scene for lighting, set light models, colormaterial, etc... """
        if self.lightsFixed or self.lightsCam or self.lightsMobile:
            ogl.glEnable(ogl.GL_LIGHTING)
            ogl.glLightModelfv(ogl.GL_LIGHT_MODEL_AMBIENT, self.ambient) 
            ogl.glClearColor(0.0, 0.1, 0.1, 0.0)
            ogl.glEnable(ogl.GL_DEPTH_TEST)
            ogl.glShadeModel(ogl.GL_SMOOTH)
            ogl.glEnable(ogl.GL_COLOR_MATERIAL)
            ogl.glColorMaterial(ogl.GL_FRONT_AND_BACK, ogl.GL_AMBIENT_AND_DIFFUSE)
            if self.lightsFixed:   # reset all lights to be refreshed
                for l in self.lightsFixed:
                    if l.id: l.dirty = True
            if self.lightsCam:
                for l in self.lightsCam:
                    if l.id: l.dirty = True
            if self.lightsMobile:
                for l in self.lightsMobile:
                    if l.id: l.dirty = True
        self.displayFog();

    def displayFog(self):
        """Initialize depth cueing. """
        if self.depthCue:
            ogl.glFog(ogl.GL_FOG_MODE, self.depthCue[0])
            ogl.glFog(ogl.GL_FOG_DENSITY, self.depthCue[1])
            ogl.glFog(ogl.GL_FOG_START, self.depthCue[2])
            ogl.glFog(ogl.GL_FOG_END, self.depthCue[3])
            ogl.glEnable(ogl.GL_FOG)
        else:
            ogl.glDisable(ogl.GL_FOG)
        self.dirtyfog = False

    def displayFixedLights(self):
        """Push all light params through to OpenGL """

        if self.lightsFixed:
            ogl.glMatrixMode(ogl.GL_MODELVIEW)
            for light in self.lightsFixed:        
                light.display()
                
    def addFixedLight(self,light,position=None):
        """Add a light to fixed lights array """
        self.lightsFixed.append(light)
        if position:  light.setPosition(position)

    def removeFixedLight(self,light):
        """Removes light from fixed lights array """
        light.off()
        self.lightsFixed.remove(light)

    def displayCamLights(self):
        """Push all light params through to OpenGL """
        if self.lightsCam:
            ogl.glMatrixMode(ogl.GL_MODELVIEW)
            ogl.glLoadIdentity()
            for light in self.lightsCam:        
                light.display()
                
    def addCamLight(self,light,position=None):
        """Add a light to camera lights array """
        self.lightsCam.append(light)
        if position: light.setPosition(position)

    def removeCamLight(self,light):
        """Removes light from camera lights array """
        light.off()
        self.lightsCam.remove(light)

    def displayMobileLights(self):
        """Push all light params through to OpenGL. """
        if self.lightsMotion:
            ogl.glMatrixMode(ogl.GL_MODELVIEW)
            ogl.glPushMatrix()
            for mover in self.lightsMotion:
                mover.display()
            ogl.glPopMatrix()
                
    def addMobileLight(self,light,mover=None,position=None):
        """Add a light to mobile lights array.  If mover 
        provided, studio will call update method of mover 
        periodically.  Same light can be passed as both.
        @param light: light to be added
        @param mover: typically a 'group' that moves, and contains
          the light. Can be same as light.
        @param position: x,y,z tuple with initial light position
        """
        self.lightsMobile.append(light)
        self.lightsMotion.append(mover)
        if position: light.setPosition(position)

    def removeMobileLight(self,light):
        """Removes light from mobile lights array. Removes
        light and its mover.
        @param light: light to be removed
        """
        i = self.lightsMobile.index(light);
        del self.lightsMobile[i]
        del self.lightsMotion[i]

    def depthCueing(self,status=True,fmode=None,
                    density=None,near=None,far=None):
        """Initialize depth cueing.
        @param status: is depth cueing enabled?
        @param fmode: GL_LINEAR, GL_EXP, or GL_EXP2
        @param density: float > 0, ignored for GL_LINEAR mode
        @param near: how near the camera does fog start?
        @param far: how far from the camera does fog extend?
        """
        if status:
            if not self.depthCue:
                if near == None:
                    near = self.engine.camera.near
                if far == None:
                    far = self.engine.camera.far
                if fmode == None:
                    fmode = ogl.GL_LINEAR
                if density == None:
                    density = 1
                self.depthCue = (fmode,density,near,far)
        else:
            self.depthCue = None
        self.dirtyfog = True

    def update(self):
        """Updates the Mobile Lights (and whatever else). """
        if self.lightsMotion:
            for li in self.lightsMotion:
                if li:
                    li.update()
        if self.dirtyfog:
            self.displayFog()

    def display(self):
        """Push settings to OpenGL."""
        self.displayMobileLights()
        self.displayCamLights()
        self.displayFixedLights()
        self.dirty = False
    
    
# Group #==========================================================================

class Group(Object):

    """A group is an object which holds a collection of other objects.
    It displays, updates, and commits all its contained objects in
    sequence."""
    
    def __init__(self, objects=None):
        """Initialize new instance.
        @param objects: list of objects to be contained
        """
        Object.__init__(self)
        self.objects = [] # list of objects
        self.commitableObjects = [] # objects with commit method
        self.updateableObjects = [] # objects with update
        if objects:
            self.extend(objects)

    def append(self, obj):
        """Add an object."""
        self.objects.append(obj)
        if hasattr(obj,'commit'):
            self.commitableObjects.append(obj)
        if hasattr(obj,'update'):
            self.updateableObjects.append(obj)
            
    def extend(self, objects):
        """Add a sequence of objects."""
        for obj in objects:
            self.append(obj)

    def remove(self, obj):
        """Remove an object."""
        if self.objects.count(obj):
            self.objects.remove(obj)
        if self.commitableObjects.count(obj):
            self.commitableObjects.remove(obj)
        if self.updateableObjects.count(obj):
            self.updateableObjects.remove(obj)

    def display(self):
        """Draw the objects in the group """
        for obj in self.objects:
            obj.display()

    def update(self):
        """Update each object in group."""
        for obj in self.updateableObjects:
            obj.update()

    def commit(self):
        """Commit each object in group. """
        for obj in self.commitableObjects:
            obj.commit()


# TimeKeeper #=====================================================================

class TimeKeeper(Object):
    """Keeps track of time and engine progress.
    Also has provisions for calling callback functions/bound-methods
    after predetermined delays. see addDelay()
    
    Does not have reference to engine, so same timekeeper class
    can track time for entire program, from engine to engine.
    
    @sort: iterate, addDelay, setup, step, toggle
    @ivar play: indicates whether update should run this frame,
        whether interface hasn't paused engine.
    """

    def __init__(self, fps=24):
        """Initialize new instance. 
        @param fps: frames per second, defaults to 24
        """
        self.delayeds = []
        self.createTime = time.time()
        self.startTime = None
        self.display_interval = 1.0/fps # how many seconds between frames
        self.play = 1 # positive = play, 0 = paused, negative = update count
        self.timePeriod = 2 # period (s) to update frame rate
        self.frameMark, self.timeMark = 0l, time.time() # marks for updating
        self.frameRate = 0.0 # current frame rate
        self.timerEventID = None

    def setup(self, tid):
        """Startup code to run after other objects are all constructed. 
        @param tid: pygame event id for timer event.
        """
        # adjust delayed timing to correct for engine setup delays
        self.timerEventID = tid
        if self.createTime:
            diff = time.time() - self.createTime
            assert(diff>=0)
            for i in range(len(self.delayeds)):
                d0 = self.delayeds[i]
                d1 = (d0[0]+diff, d0[1], d0[2])
                self.delayeds[i] = d1
            self.createTime = None
        self.set_timer()
        self.startTime = time.time()
        
    def shutdown(self):
        """Turn timer off."""
        pytime.set_timer(self.timerEventID, 0) # off
        
    def set_timer(self):
        """Enable timekeeper."""
        pytime.set_timer(self.timerEventID, int(self.display_interval*1000)) # 1/24

    def iterate(self):
        """Update frame measure.  Called by engine once per frame."""
        if self.play < 0:
            self.play += 1
        if self.delayeds:
            self.delayManager()
        if self.play:
            Object.runTurn += 1
        now = time.time()
        elapsed = now - self.timeMark
        Object.runTime = now - self.startTime
        if elapsed >= self.timePeriod:
            self.frameRate = (Object.runTurn - self.frameMark)/elapsed
            self.frameMark = Object.runTurn
            self.timeMark = now
          
    def step(self, count=2):
        """Set to only step the engine one frame."""
        self.play = -count

    def toggle(self):
        """Toggle the engine between playing and pausing."""
        self.play = not self.play

    def delayManager(self):
        """Exec delayed tasks whose time has arrived, and maintain queue. """
        now = time.time()
        while len(self.delayeds) and self.delayeds[0] and self.delayeds[0][0] <= now:
            temp = self.delayeds.pop(0)
            func, args = temp[1:]
            func(*args)
            now = time.time()

    def addDelay(self, delay, func, args):
        """Adds a function to be be executed 'delay' ms later, with 
        arguments 'args'. These callbacks are synchronized with the
        framerate, so that each is called at the first frame after delay
        is complete; Timing granularity depends on frame rate.
        
        @param delay: how many milliseconds to delay execution
        @param func: function to be called
        @param args: tuple of args to be passed to func when called
        """
        tgt_time = time.time() + delay/1000.0
        self.delayeds.append(tuple([tgt_time,func,args]))
        self.delayeds.sort(lambda x,y: cmp(x[0],y[0]))


# Engine #=====================================================================

class EngineShutdownException(Exception):
    """Exception can be raised anywhere to end engine immediately. """
    pass

class EngineReSetupException(Exception):
    """Exception can be raised anywhere to rerun engine setup code.
    raise whenever a new camera, studio or interface is installed while engine
    is running.
    """
    pass

class EngineReInitException(Exception):
    """Exception can be raised anywhere to rerun engine initialization and setup code.
    raise whenever basic video config options change (basically window size) while 
    engine is running.
    """
    pass


class Engine(object):

    """The engine manages the window, handles high-level displaying
    and updating."""

    defaultInterface = PanningInterface, ()
    defaultStudio = NullStudio, ()

    def __init__(self, video=(320,320)):
        self.title = 'spyre'
        self.width, self.height = video
        self.mode = OPENGL | DOUBLEBUF 
        self.background = (0,0,0,0)
        
        self.runTimer = None
        self.objects = Group()
        self.add = self.objects.append
        self.remove = self.objects.remove
        self.extend = self.objects.extend
        self.cameras = []
        self.camera = None
        self.interface = None
        self.studio = None        
        self.dirty = True
        Object.engine = self
        
    def init(self):
        """Initialize video and other systems """
        self.window = \
            display.set_mode((self.width, self.height), self.mode)
        # regenerate objects that depend on opengl internal state
        for obj in Object.opengl_state_dependent: 
            obj.regenerate() 
        if self.studio:
            self.studio.init()
        
    def unInit(self):
        """After all engines are done, call this. """
        pass
        
    def setup(self):
        """Setup the camera and interface if they're unspecified. """
        if self.interface is None:
            functor, args = self.defaultInterface
            self.interface = functor(*((self,) + args))
        self.interface.setup()
        if self.studio is None:
            functor, args = self.defaultStudio
            self.studio = functor(*((self,) + args))
        self.studio.setup()
        self.studio.displayCamLights()
        if self.runTimer is None:
            self.runTimer = TimeKeeper()
        self.runTimer.setup(REDRAW_TIMER)
        Object.engine = self

    def shutdown(self):
        """Handle termination chores. """
        self.runTimer.shutdown()

    def addCamera(self, cam):
        """Add a camera (and viewport) to engine. """
        while self.cameras.count(cam):
            self.cameras.remove(cam)
        self.cameras.append(cam)
        if not self.camera:
            self.camera = cam
            
    def removeCamera(self, cam):
        """Remove a camera (and viewport) from engine. """
        while self.cameras.count(cam):
            self.cameras.remove(cam)
        if self.camera == cam:
            if self.cameras:
                self.camera = self.cameras[0]
            else:
                self.camera = None

    def update(self):
        """Update all objects, both studio and display."""
        self.studio.update()
        self.objects.update()

    def commit(self):
        """Commit all objects, both studio and display."""
        self.studio.commit()
        self.objects.commit()

    def display(self):
        """Display."""
        # enable scissor testing if multiple viewports
        self.clear()
        if len(self.cameras) > 1:
            ogl.glEnable(ogl.GL_SCISSOR_TEST)
        else:
            ogl.glDisable(ogl.GL_SCISSOR_TEST)
        # for each camera, clear background and draw
        for cam in self.cameras:
            cam.displayViewport()
            cam.displayBackground()
            cam.viewProj()
            cam.viewMV()
            if cam.dirty:
                self.studio.displayFixedLights()
                cam.dirty = False
            self.studio.displayMobileLights()
            cam.objects.display()
        # flush all pending drawing 
        ogl.glFlush()
        display.flip()
        self.dirty = False
        
    def redisplay(self):
        """Register a redisplay."""
        self.dirty = True

    def clear(self):
        """Clear the display."""
        ogl.glViewport(0, 0, self.width, self.height)
        ogl.glDisable(ogl.GL_SCISSOR_TEST)
        ogl.glDisable(ogl.GL_BLEND)
        bits = ogl.GL_DEPTH_BUFFER_BIT
        if self.background:
            ogl.glClearColor(*self.background)
            bits |= ogl.GL_COLOR_BUFFER_BIT
        ogl.glClear(bits)

    def maintain(self):
        """Run update as apropos."""
        self.redisplay()  # default behaviour - necessary?
        if self.runTimer.play:
            self.update()
            self.commit()

    def idle(self):
        """Runs when the engine is idle."""
        while 1:
            pytime.wait(10)
            yield None
        
    def reshape(self, width, height):
        """Resize the window."""
        self.width, self.height = width, height
        self.redisplay()
        raise EngineReInitException

    def event(self, ev):
        """Handles all user defined events"""
        pass
  
    def quit(self, *args):
        """ Mark the engine as shutting down. """
        raise EngineShutdownException

    def getAbsPos(self, pos):
        """Return absolute position of relative position 'pos'."""
        assert(ogl.glGetIntegerv(ogl.GL_MATRIX_MODE) == ogl.GL_MODELVIEW)
        winPos = oglu.gluProject(*pos)
        assert type(winPos) is types.TupleType, type(winPos)
        ogl.glPushMatrix()
        ogl.glLoadIdentity()
        self.camera.viewMV()
        absPos = oglu.gluUnProject(*winPos)
        assert type(absPos) is types.TupleType, type(absPos)
        ogl.glPopMatrix()
        return absPos

    def go(self):
        """Set everything up and then execute the main loop."""        
        try:
            while 1:
                if not hasattr(self, 'window'):
                    init()
                self.init()

                try:
                    while 1:
                        # run setup, then start main event loop    
                        #  typically, this loop never repeats, but
                        #  is exited on first pass by EngineShutdownException
                        self.setup()
                        self.update()
                        self.commit()
                        self.studio.display()
                        self.display()

                        try:
                            idler = self.idle().next
                        except AttributeError:
                            idler = self.idle

                        # optimization
                        engevent = self.event
                        maintainer = self.maintain
                        displayer = self.display
                        timer = self.runTimer.iterate
                        iface = self.interface
                        ifevent = iface.event

                        try:
                            # main event loop
                            while 1:
                                ev = event.poll()
                                if ev.type == NOEVENT:   
                                    #self.idle()
                                    idler()
                                elif ev.type == ACTIVEEVENT:
                                    if (ev.state):
                                        #self.redisplay()
                                        self.dirty = True
                                elif ev.type == REDRAW_TIMER:
                                    event.get(REDRAW_TIMER) # clear queue
                                    #self.runTimer.iterate()
                                    timer()
                                    #self.maintain()
                                    maintainer()
                                    if self.dirty:
                                    #    self.display()
                                        displayer()
                                elif ev.type < USEREVENT:
                                    #self.interface.event(ev)
                                    ifevent(ev)
                                else:
                                    #self.event(ev)
                                    engevent(ev)

                        # if reSetup exception thrown, exit event loop
                        #   to setup loop
                        except EngineReSetupException:
                            pass

                # if reInit exception is thrown, return to top of go()
                #  and reinitialize and resetup everything
                except EngineReInitException:
                    pass

        # if shutdown exception thrown, run shutdown code, and
        #   exit runloop
        except EngineShutdownException:
            self.shutdown()


    def dumpStats(self, empty=None):
        """Dump engine statistics. """
        cam = self.cameras[0]
        print 'engine status '
        print '---------------'
        print '  camera eye   '
        print '  ( %.4f %.4f %.4f ) ' % cam.eye
        print '  camera center '
        print '  ( %.4f %.4f %.4f ) ' % cam.center
        print '  camera viewbox bounds  (l/r) '
        print '  ( %.4f %.4f ) ' % (cam.left, cam.right)
        print '  camera viewbox bounds  (t/b) '
        print '  ( %.4f %.4f ) ' % (cam.top, cam.bottom)
        print '  camera viewbox bounds  (n/f) '
        print '  ( %.4f %.4f ) ' % (cam.near, cam.far)
        
        
class EngineFullScreen(Engine):
    """Generic engine, but full screen. """
    
    defaultInterface = PanningInterface, ()
    defaultStudio = NullStudio, ()

    def __init__(self, video=(800, 600)):
        Engine.__init__(self, video)
        self.mode = self.mode | FULLSCREEN

    def reshape(self, width, height):
        """Disable reshape method. """
        pass