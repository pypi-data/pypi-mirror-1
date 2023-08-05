#!/usr/local/bin/python
#

"""
A teapot and a sphere, demos lighting/shading peculiarity
"""

import math
import atexit
import sys

import stereoscopic

import pygame;
from pygame.locals import *
from pygame import display

import OpenGL.GL as ogl 
import OpenGL.GLU as oglu

sys.path.append('..')
import spyre
import zoe_objects as zoe
from shapes_objects import *


class Sphere(spyre.Object):
    """draws a sphere """
    def __init__(self, radius, x=0, y=0, z=0):
        spyre.Object.__init__(self)
        self.radius = radius
        self.x      = x
        self.y      = y
        self.z      = z
        self.quad   = oglu.gluNewQuadric()

    def display(self):
        ogl.glColor4f(0.7, 0.7, 0.7, 1)
        ogl.glPushMatrix()
        ogl.glTranslate( self.x, self.y, self.z )

        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_AMBIENT, [0.2, 0.0, 0.1, 0.0])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_DIFFUSE, [0.5, 0.5, 0.5, 0.1])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_SPECULAR, [0.7, 0.6, 0.8, 0.0])
        ogl.glMaterialf(ogl.GL_FRONT, ogl.GL_SHININESS, 50)

        oglu.gluSphere(  self.quad, self.radius, 60, 60 )
        ogl.glPopMatrix()


class Teapot(spyre.Object):
    """ wrapper that adds color to Teapot obj """
    def __init__(self, size):
        spyre.Object.__init__(self)
        self.size = size
        self.geo = shapeTeapot(size)

    def display(self):
        ogl.glColor4f(1, 1, 1, 1)
        ogl.glPushMatrix()
        self.geo.display()
        ogl.glPopMatrix()


def postMortem( engine ):    
    """ displays frame rate to stderr at end of run """
    print >> sys.stderr, "frame %d rate %.2f" % \
               (spyre.Object.runTurn, engine.runTimer.frameRate)
       

def main():

    pygame.init()

    # create the engine
    eng = spyre.EngineFullScreen()
    eng.studio = spyre.StudioColorMat(eng)
    eng.studio.depthCueing(True,ogl.GL_LINEAR,None,2,10)

    light0 = spyre.Bulb([0.5,0.6,0.5,1.0],  # ambient
                        [0.6,0.7,0.7,1.0],  # diffuse
                        [0.3,0.3,0.3,1.0], ) # specular
                               
    eng.studio.addFixedLight( light0, (0,5,10) )
    
    eng.add(zoe.AxesObject())
    eng.add(zoe.GridObject())
    eng.add(Teapot(1))
    eng.add(Sphere(1,0,3,0))
    eng.add(zoe.FrameRateCounter(eng))
    
    engine = stereoscopic.StereoEngineRB(eng)
    
    atexit.register( postMortem, engine ) 

    engine.go()

if __name__ == '__main__': main()
