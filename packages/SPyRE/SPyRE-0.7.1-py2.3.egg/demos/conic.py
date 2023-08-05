#!/usr/local/bin/python
#

"""
A static view of several conic sections with varying eccentricities.
"""

import math
import sys

import pygame
import OpenGL.GL as ogl

sys.path.append('..')
import spyre
import zoe_objects as zoeobj

pygame.init()


class ConicObject(spyre.Object):

    """A conic section with eccentricity e, the focus at the origin,
    and the focus-directrix distance p."""
    
    DIVISIONS = 120
    ANGLE_INCREMENT = spyre.twoPi/DIVISIONS
    
    def __init__(self, e, p=None):
        if p is None:
            if e == 0.0:
                p = 1.0
            else:
                p = (1 + e)/e
        self.e = e
        self.p = p
        self.ep = e*p
        if self.e < 1.0:
            self.start = 0.0
            self.end = spyre.twoPi + self.ANGLE_INCREMENT
        elif self.e == 1.0:
            self.start = self.ANGLE_INCREMENT
            self.end = spyre.twoPi
        else:
            a = p
            b = math.sqrt((e*a)**2 - a**2)
            phi = math.atan(b/a)
            self.start = phi - spyre.pi
            self.end = spyre.pi - phi

    def display(self):
        ogl.glColor3d(1.0, 1.0, 1.0)
        ogl.glBegin(ogl.GL_LINE_STRIP)
        theta = self.start
        while theta < self.end:
            try:
                if self.e == 0.0:
                    r = self.p
                else:
                    r = self.ep/(1 + self.e*math.cos(theta))
                ogl.glVertex3d(r*math.cos(theta), r*math.sin(theta), 0.0)
            except (ZeroDivisionError, OverflowError):
                pass
            theta += self.ANGLE_INCREMENT
        ogl.glEnd()
        

def main():
    if len(sys.argv) > 1:
        e = float(sys.argv[1])
    else:
        e = None
    engine = spyre.Engine()
    engine.add(zoeobj.AxesObject())
    engine.add(zoeobj.GridObject())
    engine.add(zoeobj.FrameRateCounter(engine))
    if e is not None:
        engine.add(ConicObject(e))
    else:
        e = 0.0
        while e <= 2.0:
            engine.add(ConicObject(e))
            e += 0.25
    engine.go()

if __name__ == '__main__': main()
