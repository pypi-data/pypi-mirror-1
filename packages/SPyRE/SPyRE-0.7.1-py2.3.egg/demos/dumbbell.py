#!/usr/local/bin/python
#

"""Draws a dumbbell, (two spheres and a connecting cylinder) fixed in space, 
but with an orbiting light source.
"""

import math
import sys
import atexit

import pygame
import OpenGL.GL as ogl
import OpenGL.GLU as oglu

sys.path.append('..')
import spyre
import zoe_objects as zoeobj


class DumbBell(spyre.Object):
    """draws a dumbbell object """
    def __init__(self, height, radius, x=0, y=0, z=0):
        spyre.Object.__init__(self)
        self.height = height
        self.radius = radius
        self.x      = x
        self.y      = y
        self.z      = z
        self.quad   = oglu.gluNewQuadric()

    def display(self):
        ogl.glColor4f(0.5, 0.5, 0.5, 1)
        ogl.glPushMatrix()
        ogl.glTranslate(self.x, self.y, self.z-self.height/2.0)

        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_AMBIENT, [0.1745, 0.0, 0.1, 0.0])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_DIFFUSE, [0.5, 0.5, 0.5, 0.1])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_SPECULAR, [0.7, 0.6, 0.8, 0.0])
        ogl.glMaterialf(ogl.GL_FRONT, ogl.GL_SHININESS, 50)

        oglu.gluCylinder(self.quad , self.radius/2.0, self.radius/2.0, 
                     self.height, 60, 70) 

        ogl.glTranslate(0, 0, self.height+self.radius/2.0)
        oglu.gluSphere(self.quad, self.radius, 60, 60)

        ogl.glTranslate(0, 0, -self.height-self.radius)
        oglu.gluSphere(self.quad, self.radius, 60, 60)

        ogl.glPopMatrix()


def postMortem(engine):    
    """ displays frame rate to stderr at end of run """
    print >> sys.stderr, "frame %d rate %.2f" % \
               (spyre.Object.runTurn, engine.runTimer.frameRate)
    print >> sys.stderr, "ortho %d, %d, %d, %d, %d, %d" % \
                (engine.camera.left, engine.camera.right, 
                 engine.camera.top, engine.camera.bottom, 
                 engine.camera.near, engine.camera.far)
    print >> sys.stderr, "eye <%f %f %f> " % engine.camera.eye


def main():
    """ main block """
    pygame.init()

    # create the engine
    engine = spyre.Engine()
    engine.studio = spyre.StudioColorMat(engine)

    light0 = spyre.Bulb([0.5,0.6,0.5,1.0],  # ambient
                        [0.6,0.7,0.7,1.0],  # diffuse
                        [0.3,0.3,0.3,1.0], ) # specular
                               
    orbiter = zoeobj.RotatingGroup(0.03, objects=[light0], ray=(1,0,0))
    engine.studio.addMobileLight(light0, orbiter, (0,10,10))

    # add the various objects to the engine
    engine.add(zoeobj.AxesObject())
    engine.add(zoeobj.GridObject())

    engine.add(DumbBell(2,1))
    
    atexit.register(postMortem, engine) 

    # run the event loop
    engine.go()

if __name__ == '__main__': 
    main()
