#!/usr/local/bin/python
#

"""
A demonstration of the pedestrian interface with a forest scene.
"""

import math
import random
import sys

import OpenGL.GL as ogl
import OpenGL.GLU as oglu
import pygame

sys.path.append('..')
import la
import spyre 
pygame.init()

# the location of the hill in the scene (z is height)
hillLoc = ( -10, 75, 10 )

class terrain(spyre.Object):
    """draws the ground """
    def __init__(self, width=2000, depth=2000, x=0, y=0, z=0):
        spyre.Object.__init__(self)
        self.width  = width
        self.depth  = depth
        self.x      = x
        self.y      = y
        self.z      = z
        self.quad   = oglu.gluNewQuadric()

    def display(self):
        ogl.glPushMatrix()
        ogl.glTranslate( self.x, self.y, self.z )
        ogl.glColor4f(0.4, 0.5, 0.4, 1)
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_AMBIENT,  [0.17, 0.2, 0.2, 0.0])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_DIFFUSE,  [0.5,  0.5, 0.5, 0.1])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_SPECULAR, [0.7,  0.6, 0.8, 0.0])    

        oglu.gluDisk( self.quad, 0, self.width, 60, 70 ) 
        ogl.glTranslate( hillLoc[0], hillLoc[1], 0 )
        oglu.gluCylinder( self.quad, 50, 25, hillLoc[2], 50, 50 )  # hill
        ogl.glTranslate( 0, 0, hillLoc[2] )
        oglu.gluDisk( self.quad, 0, 25, 60, 70 ) 
        
        ogl.glPopMatrix()

class deciduous(spyre.Object):
    """draws a deciduous tree"""
    def __init__(self, height, radius, x=0, y=0, z=0):
        spyre.Object.__init__(self)
        self.height = height
        self.radius = radius
        self.x      = x
        self.y      = y
        self.z      = z
        self.quad   = oglu.gluNewQuadric()

    def display(self):
        ogl.glPushMatrix()

        # trunk
        ogl.glTranslate( self.x, self.y, self.z )
        ogl.glColor4f(0.5, 0.6, 0.6, 1)
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_AMBIENT,  [0.17, 0.2, 0.2, 0.0])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_DIFFUSE,  [0.5,  0.5, 0.5, 0.1])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_SPECULAR, [0.7,  0.6, 0.8, 0.0])
        ogl.glMaterialf(ogl.GL_FRONT, ogl.GL_SHININESS, 50)
        oglu.gluCylinder( self.quad, self.radius/20.0, self.radius/20.0, self.height*0.66, 60, 60 ) 

        # crown
        ogl.glColor4f(0.0, 0.9, 0.4, 1)
        ogl.glTranslate( 0, 0, self.height-self.radius )
        oglu.gluSphere( self.quad, self.radius, 60, 60 )

        ogl.glPopMatrix()


class conifer(spyre.Object):
    """draws a conifer (conical) tree"""
    def __init__(self, height, radius, x=0, y=0, z=0):
        spyre.Object.__init__(self)
        self.height = height
        self.radius = radius
        self.x      = x
        self.y      = y
        self.z      = z
        self.quad   = oglu.gluNewQuadric()

    def display(self):
        ogl.glPushMatrix()
        # trunk
        ogl.glTranslate( self.x, self.y, self.z )
        ogl.glColor4f(0.4, 0.6, 0.6, 1)
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_AMBIENT,  [0.17, 0.2, 0.2, 0.0])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_DIFFUSE,  [0.5,  0.5, 0.5, 0.1])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_SPECULAR, [0.6,  0.5, 0.7, 0.0])
        ogl.glMaterialf(ogl.GL_FRONT, ogl.GL_SHININESS, 50)
        oglu.gluCylinder( self.quad , self.radius/20.0, self.radius/20.0, 
                     self.height*0.25, 60, 70 ) 
        # crown
        ogl.glColor4f(0.2, 0.9, 0.4, 1)
        ogl.glTranslate( 0, 0, self.height*0.25 )
        oglu.gluCylinder( self.quad, self.radius, 0, self.height*0.75, 60, 60 )
        ogl.glPopMatrix()


class triConifer(spyre.Object):
    """draws a conifer with three frond levels"""
    def __init__(self, height, radius, x=0, y=0, z=0):
        spyre.Object.__init__(self)
        self.height = height
        self.radius = radius
        self.x      = x
        self.y      = y
        self.z      = z
        self.quad   = oglu.gluNewQuadric()

    def display(self):
        ogl.glPushMatrix()
        # trunk
        ogl.glTranslate( self.x, self.y, self.z )
        ogl.glColor4f(0.4, 0.4, 0.5, 1)
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_AMBIENT,  [0.17, 0.2, 0.2, 0.0])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_DIFFUSE,  [0.5,  0.5, 0.5, 0.1])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_SPECULAR, [0.7,  0.6, 0.8, 0.0])
        ogl.glMaterialf(ogl.GL_FRONT, ogl.GL_SHININESS, 50)
        oglu.gluCylinder( self.quad , self.radius/20.0, self.radius/20.0, 
                     self.height*0.25, 60, 70 ) 
        # crown
        ogl.glColor4f(0.2, 0.9, 0.6, 1)
        ogl.glTranslate( 0, 0, self.height*0.25 )
        oglu.gluCylinder( self.quad, self.radius*0.9, 0, self.height*0.50, 60, 60 )

        ogl.glTranslate( 0, 0, self.height*0.25 )
        oglu.gluCylinder( self.quad, self.radius, 0, self.height*0.50, 60, 60 )

        ogl.glTranslate( 0, 0, self.height*0.25 )
        oglu.gluCylinder( self.quad, self.radius*0.8, 0, self.height*0.50, 60, 60 )
        ogl.glPopMatrix()


class poplar(spyre.Object):
    """draws a poplar tree"""
    def __init__(self, height, radius, x=0, y=0, z=0):
        spyre.Object.__init__(self)
        self.height = height
        self.radius = radius
        self.x      = x
        self.y      = y
        self.z      = z
        self.quad   = oglu.gluNewQuadric()

    def display(self):
        ogl.glPushMatrix()
        # trunk
        ogl.glTranslate( self.x, self.y, self.z )
        ogl.glColor4f(0.6, 0.5, 0.6, 1)
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_AMBIENT,  [0.17, 0.2, 0.2, 0.0])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_DIFFUSE,  [0.5,  0.5, 0.5, 0.1])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_SPECULAR, [0.5,  0.5, 0.5, 0.0])
        ogl.glMaterialf(ogl.GL_FRONT, ogl.GL_SHININESS, 50)
        oglu.gluCylinder( self.quad , self.radius/10.0, self.radius/10.0, 
                     self.height*0.1, 60, 70 ) 
        # crown
        ogl.glColor4f(0.3, 0.8, 0.1, 1)
        ogl.glTranslate( 0, 0, self.height*0.1+self.radius )
        oglu.gluSphere( self.quad, self.radius, 20, 20 )

        oglu.gluCylinder( self.quad, self.radius, self.radius, self.height*0.50-self.radius, 60, 60 )

        ogl.glTranslate( 0, 0, self.height*0.50-self.radius )
        oglu.gluCylinder( self.quad, self.radius, 0, self.height*0.40, 60, 60 )
        ogl.glPopMatrix()


class rock(spyre.Object):
    """draws a round rock"""
    def __init__(self, radius, x=0, y=0, z=0):
        spyre.Object.__init__(self)
        self.radius = radius
        self.x      = x
        self.y      = y
        self.z      = z
        self.quad   = oglu.gluNewQuadric()

    def display(self):
        ogl.glPushMatrix()
        # trunk
        ogl.glTranslate( self.x, self.y, self.z )
        ogl.glColor4f(0.3, 0.3, 0.32, 1)
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_AMBIENT,  [0.17, 0.2, 0.2, 0.0])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_DIFFUSE,  [0.5,  0.5, 0.5, 0.1])
        ogl.glMaterialfv(ogl.GL_FRONT, ogl.GL_SPECULAR, [0.8,  0.8, 0.8, 0.0])
        ogl.glMaterialf(ogl.GL_FRONT, ogl.GL_SHININESS, 50)
        oglu.gluSphere( self.quad, self.radius, 20, 20 )
        ogl.glPopMatrix()


def elev(x,y):
    dist = math.sqrt( (hillLoc[0]-x)**2 + (hillLoc[1]-y)**2 )
    if dist < 50:
        if dist < 25:
            return hillLoc[2]
        else:
            return hillLoc[2] - hillLoc[2] * (dist-25)/25
    else:
        return 0;

def main():
    engine = spyre.Engine()
    engine.addCamera(spyre.RovingCameraFrustum(engine,(10,-95,8),(10,-10,6),(0,0,1),elev))
    engine.camera.perspective(20, 1, 5, 500)
    engine.interface = spyre.PedestrianInterface(engine)
    engine.studio = spyre.StudioColorMat(engine)
    engine.studio.depthCueing(True,ogl.GL_LINEAR)

    #engine.debug = 7

    light0 = spyre.Bulb([0.5,0.6,0.5,1.0],  # ambient
                        [0.6,0.7,0.7,1.0],  # diffuse
                        [0.3,0.3,0.3,1.0], ) # specular
    engine.studio.addCamLight( light0, (0,0,10) )

    solar  = spyre.Sun( [0.4,0.4,0.4,1.0],  # ambient
                        [0.9,1.0,0.1,1.0],  # diffuse
                        [0.3,0.3,0.3,1.0] ) # specular
    engine.studio.addFixedLight( solar, (0,100,100) )

    engine.add(terrain())
    
    engine.add(poplar(40,2,   -75,-10,0))
    engine.add(poplar(42,2,   -79,-14,0))
    engine.add(poplar(43,2.2, -85,-19,0))
    engine.add(poplar(38,2,   -95,-25,0))
    
    engine.add(conifer(15,7, -20,-10,0))
    engine.add(conifer(15,3, -30,-15,0))
    
    engine.add(deciduous(25,10,-22,35,5))

    engine.add(conifer(12,5,-10,90,hillLoc[2]))
    engine.add(conifer(13,5,  0,85,hillLoc[2]))
    engine.add(conifer(11,4,  5,75,hillLoc[2]))

    engine.add(triConifer(15,10, 70,100,0))
    engine.add(triConifer(15,10, 70,70,0))

    engine.add(poplar(25,2, 73,-30,0))

    engine.add(rock(2,   28,-40,0))
    engine.add(rock(1.5, 20,-25,0))
    engine.add(rock(2,   15,-13,0))
    engine.add(rock(2.2, 20, 0,0))
    engine.add(rock(1.7, 20,45,3))
    engine.add(rock(2,   24, 60,0))

    engine.go()

if __name__ == '__main__': main()
