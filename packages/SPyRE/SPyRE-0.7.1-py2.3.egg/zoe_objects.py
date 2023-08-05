"""
Specialized objects for SPyRE.

these classes have been moved out of the zoe.py 
"""

__author__ = 'Erik Max Francis <max@alcyone.com>'
__copyright__ = 'Copyright (C) 2000-2002 Erik Max Francis,  2004 David Keeney'
__license__ = 'LGPL'


import OpenGL.GL as ogl

import spyre
import pygame
import types

class AxesObject(spyre.Object):
    """Shows a set of axes, with stippling in the negative direction."""
    
    xColor = 1.0, 0.0, 0.0
    yColor = 0.0, 1.0, 0.0
    zColor = 0.0, 0.0, 1.0
    stipple = 0x0f0f

    def __init__(self, expanse=20):
        spyre.Object.__init__(self)
        self.expanse = expanse

    def display(self):
        """ draw the object """
        ogl.glLineStipple(1, self.stipple)
        ogl.glDisable(ogl.GL_LINE_STIPPLE)
        ogl.glBegin(ogl.GL_LINES)
        ogl.glColor3d(*self.xColor)
        ogl.glVertex3d(0, 0, 0)
        ogl.glVertex3d(self.expanse, 0, 0)
        ogl.glEnd()
        ogl.glEnable(ogl.GL_LINE_STIPPLE)
        ogl.glBegin(ogl.GL_LINES)
        ogl.glVertex3d(0, 0, 0)
        ogl.glVertex3d(-self.expanse, 0, 0)
        ogl.glEnd()
        ogl.glDisable(ogl.GL_LINE_STIPPLE)
        ogl.glBegin(ogl.GL_LINES)
        ogl.glColor3d(*self.yColor)
        ogl.glVertex3d(0, 0, 0)
        ogl.glVertex3d(0, self.expanse, 0)
        ogl.glEnd()
        ogl.glEnable(ogl.GL_LINE_STIPPLE)
        ogl.glBegin(ogl.GL_LINES)
        ogl.glVertex3d(0, 0, 0)
        ogl.glVertex3d(0, -self.expanse, 0)
        ogl.glEnd()
        ogl.glDisable(ogl.GL_LINE_STIPPLE)
        ogl.glBegin(ogl.GL_LINES)
        ogl.glColor3d(*self.zColor)
        ogl.glVertex3d(0, 0, 0)
        ogl.glVertex3d(0, 0, self.expanse)
        ogl.glEnd()
        ogl.glEnable(ogl.GL_LINE_STIPPLE)
        ogl.glBegin(ogl.GL_LINES)
        ogl.glVertex3d(0, 0, 0)
        ogl.glVertex3d(0, 0, -self.expanse)
        ogl.glEnd()
        ogl.glDisable(ogl.GL_LINE_STIPPLE)

class GridObject(spyre.Object):
    """Shows a grid on the x-y plane."""

    gridColor = 0.25, 0.25, 0.25
    
    def __init__(self, resolution=1, expanse=20, skipZero=1):
        spyre.Object.__init__(self)
        self.resolution = resolution
        self.expanse = expanse
        self.skipZero = skipZero

    def display(self):
        """ draw the object """
        ogl.glColor3d(*self.gridColor)
        ogl.glBegin(ogl.GL_LINES)
        i = -self.expanse
        while i <= +self.expanse:
            if i == 0 and self.skipZero:
                i += self.resolution
                continue
            ogl.glVertex3d(i, -self.expanse, 0)
            ogl.glVertex3d(i, +self.expanse, 0)
            ogl.glVertex3d(-self.expanse, i, 0)
            ogl.glVertex3d(+self.expanse, i, 0)
            i += self.resolution
        ogl.glEnd()


class ReplayingObject(spyre.Object):
    """An object which can be given a series of PostScript-like
    commands, finished with the 'done' method, and then can replay
    them back."""
    
    def __init__(self):
        self.paths = []
        self.current = None

    def setColor(self, triple):
        """ adds a color to 'paths' """
        self.endPath()
        self.paths.append(tuple(triple))

    def startPath(self):
        """ create a path """
        if self.current is not None:
            self.endPath()
        self.current = []

    def vertex(self, point):
        """ add a vertex """
        assert self.current is not None
        self.current.append(point)

    def endPath(self):
        """ end the path, put it on 'paths' """
        if self.current is not None:
            self.paths.append(self.current)
            self.current = None

    def closePath(self):
        """ make Path closed loop """
        assert self.current is not None
        self.current.append(self.current[0])
        self.endPath()

    def done(self):
        """ alias for endpath """
        self.endPath()

    def display(self):
        """ draw the objects """
        for path in self.paths:
            if type(path) is types.TupleType:
                ogl.glColor3d(*path)
            else:
                if len(path) == 1:
                    ogl.glBegin(ogl.GL_POINTS)
                elif len(path) == 2:
                    ogl.glBegin(ogl.GL_LINES)
                else:
                    ogl.glBegin(ogl.GL_LINE_STRIP)
                for point in path:
                    ogl.glVertex3d(*point)
                ogl.glEnd()


class Plotter(ReplayingObject):
    """A plotter which, given a function taking two arguments, will
    play out its behavior drawing a surface."""
    
    def __init__(self, func, startT=-10.0, deltaT=0.2, endT=+10.0):
        ReplayingObject.__init__(self)
        x = startT
        while x <= endT:
            self.startPath()
            y = startT
            while y <= endT:
                try:
                    z = func(x, y)
                except (ZeroDivisionError, OverflowError):
                    y += deltaT
                    continue
                self.vertex((x, y, z))
                y += deltaT
            self.endPath()
            x += deltaT
        y = startT
        while y <= endT:
            self.startPath()
            x = startT
            while x <= endT:
                try:
                    z = func(x, y)
                except (ZeroDivisionError, OverflowError):
                    x += deltaT
                    continue
                self.vertex((x, y, z))
                x += deltaT
            self.endPath()
            y += deltaT


class StatusObject(spyre.Object):
    """A status object is one that can render itself as text on the
    main screen."""

    textColor = 1.0, 1.0, 1.0
    
    def __init__(self, engine):
        spyre.Object.__init__(self)
        self.engine = engine

    def displayText(self, x, y, style, message):
        """ draw some text at spec loc """
        ogl.glMatrixMode(ogl.GL_PROJECTION)
        ogl.glPushMatrix()
        ogl.glLoadIdentity()
        ogl.glOrtho(0, self.engine.width, 0, self.engine.height, -1, 1)
        ogl.glMatrixMode(ogl.GL_MODELVIEW)
        ogl.glPushMatrix()
        ogl.glLoadIdentity()
        ogl.glColor3d(*self.textColor)
        ogl.glRasterPos2i(x, y)
        self.drawText(message)
        ogl.glPopMatrix()
        ogl.glMatrixMode(ogl.GL_PROJECTION)
        ogl.glPopMatrix()
        ogl.glMatrixMode(ogl.GL_MODELVIEW)

    def drawText(self,textString):
        """ draw text """

        font = pygame.font.Font(None, 16) # 64
        textSurface = font.render(textString, True,
                               (255, 255, 255, 255),
                               (0, 0, 0, 255))
        textData = pygame.image.tostring(textSurface,
                                      "RGBA", True)
        #glRasterPos3d(*position)
        ogl.glDrawPixels(textSurface.get_width(),
                      textSurface.get_height(),
                      ogl.GL_RGBA, ogl.GL_UNSIGNED_BYTE, textData)


class FrameRateCounter(StatusObject):
    """A frame rate counter, which displays the current frame number
    and the current frame rate."""
    
    def __init__(self, engine, x=10, y=10, style=0 ): #ogl.GLUT_BITMAP_HELVETICA_12):
        StatusObject.__init__(self, engine)
        self.x, self.y = x, y
        self.style = style

    def display(self):
        """ draw the object """
        self.displayText(self.x, self.y, self.style, "frame %d rate %.2f" % \
                (spyre.Object.runTurn, self.engine.runTimer.frameRate))



# Transform ================================================================

class Transform:

    """An encapsulation of a transformation."""
    
    def __init__(self):
        pass

    def apply(self):
        """Apply the transformation."""
        pass


class TranslateTransform(Transform):

    """A translation transformation."""
    
    def __init__(self, vec):
        self.vec = vec

    def apply(self):
        ogl.glTranslated(self.vec[0], self.vec[1], self.vec[2])


class RotateTransform(Transform):

    """A rotation transformation."""
    
    def __init__(self, angle, ray=(0, 0, 1)):
        self.angle = angle
        self.ray = ray

    def apply(self):
        ogl.glRotated(self.angle*spyre.radiansToDegrees, \
                  self.ray[0], self.ray[1], self.ray[2])


class ScaleTransform(Transform):

    """A scale transformation."""
    
    def __init__(self, vecOrScalar):
        if type(vecOrScalar) is types.FloatType:
            self.vec = (vecOrScalar,) * 3
        else:
            self.vec = vecOrScalar

    def apply(self):
        ogl.glScaled(self.vec[0], self.vec[1], self.vec[2])



# Group =====================================================================


class Group2(spyre.Group):
    """Group with 'before' and 'after' methods. """
    
    def before(self):
        pass

    def after(self):
        pass

    def display(self):
        """ draw the objects in the group """
        self.before()
        for obj in self.objects:
            obj.display()
        self.after()


class TransformGroup(Group2):

    """A group that implements a series of transforms."""
    
    def __init__(self, transforms, objects=None):
        Group2.__init__(self, objects)
        self.transforms = transforms

    def before(self):
        ogl.glPushMatrix()
        for transform in self.transforms:
            transform.apply()

    def after(self):
        ogl.glPopMatrix()


class RotatingGroup(TransformGroup):

    """A group that slowly rotates."""
    
    def __init__(self, angularSpeed, ray=(0, 0, 1), objects=None):
        self.transform = RotateTransform(0.0, ray)
        TransformGroup.__init__(self, [self.transform], objects)
        self.angularSpeed = angularSpeed

    def update(self):
        self.transform.angle += self.angularSpeed
        if self.transform.angle >= spyre.twoPi:
            self.transform.angle -= spyre.twoPi



# Particle, System #===========================================================

class Particle(spyre.Object):

    """A particle is an object with a position, and an optional
    trail."""

    trailLength = 0
    particleColor = 1.0, 1.0, 1.0
    trailColor = 0.5, 0.5, 0.5
    
    def __init__(self, pos=(0, 0, 0)):
        spyre.Object.__init__(self)
        self.pos = pos
        self.trail = []

    def display(self):
        """ draw the object """
        if self.trailLength:
            ogl.glColor3d(*self.trailColor)
            ogl.glBegin(ogl.GL_LINE_STRIP)
            for point in self.trail:
                ogl.glVertex3d(*point)
            ogl.glVertex3d(*self.pos)
            ogl.glEnd()
        ogl.glColor3d(*self.particleColor)
        ogl.glBegin(ogl.GL_POINTS)
        ogl.glVertex3d(*self.pos)
        ogl.glEnd()

    def update(self):
        if self.trailLength:
            self.trail.append(self.pos)
            if len(self.trail) > self.trailLength:
                self.trail = self.trail[-self.trailLength:]

    def ok(self):
        """Does this particle need to be reclaimed?  Only applicable for
        particles in systems."""
        return 1


class NewtonianParticle(Particle):

    """A Newtonian particle has a position and a velocity, and every
    turn updates its position according to the velocity (which
    actually acts as a change in position."""
    
    def __init__(self, pos=(0, 0, 0), vel=(0, 0, 0)):
        Particle.__init__(self, pos)
        self.vel = vel

    def update(self):
        Particle.update(self)
        self.pos = self.pos[0] + self.vel[0], \
                   self.pos[1] + self.vel[1], \
                   self.pos[2] + self.vel[2]

    def impulse(self, deltavee):
        """Apply an impulse to the particle, with the change in velocity."""
        self.vel = self.vel[0] + deltavee[0], \
                   self.vel[1] + deltavee[1], \
                   self.vel[2] + deltavee[2]


class System(Group2):

    """A system is a group that maintains a list of objects with a
    maximum number, all of the same type.  Each object is excepted to
    have an 'ok' method that returns whether or not it should be
    reclaimed."""

    def __init__(self, max):
        Group2.__init__(self)
        self.max = max

    def new(self):
        """Construct a new particle."""
        raise NotImplementedError

    def reset(self, index):
        """Reset the nth particle."""
        self.remove(self.objects[index])
        self.append(self.new())

    def update(self):
        Group2.update(self)
        # Look for expired particles.
        objs = self.objects[:]
        for obj in objs:
            if not obj.ok():
                self.remove(obj)
                self.append(self.new())
        # Inject new particles.
        if len(self.objects) < self.max:
            self.append(self.new())



