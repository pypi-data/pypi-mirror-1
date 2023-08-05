#!/usr/local/bin/python
#

"""
A demonstration of chaos theory (namely sensitivity to initial
conditions) with a Lorenz system.

"""
import sys

import pygame

sys.path.append('..')
import spyre 
import zoe_objects as zoeobj 

pygame.init()


# The Lorenz differential equations:
#
#     dx/dt = sigma (y - x)
#     dy/dt = rho x - y - x z
#     dz/dt = -B z + x y

PARTICLES = 10 # the number of particles


class LorenzParticle(zoeobj.Particle):

    """A Lorenz particle simply moves according to the Lorenz
    differential equations described above.
    """

    SIGMA = 10.0
    RHO = 28.0
    B = 8.0/3.0
    DELTA_T = 0.01
    
    trailLength = 100

    def __init__(self, start):
        zoeobj.Particle.__init__(self, start)
        self.t = 0.0

    def update(self):
        x, y, z = [10*x for x in self.pos]
        zoeobj.Particle.update(self)
        deltaX = (self.SIGMA*(y - x))*self.DELTA_T
        deltaY = (self.RHO*x - y - x*z)*self.DELTA_T
        deltaZ = (-self.B*z + x*y)*self.DELTA_T
        x += deltaX
        y += deltaY
        z += deltaZ
        self.pos = [0.1*x for x in (x,y,z)]
        self.t += self.DELTA_T


class LorenzGroup(spyre.Group):

    """A Lorenz group creates a collection of particles that all have
    very nearly the same position, differing only by a very small
    amount."""

    BASE = 0.001 # the starting position
    VARIANCE = 0.000001 # the variance of all particles

    def __init__(self, count):
        spyre.Group.__init__(self)
        for i in range(1, count + 1):
            xyz = self.BASE + i*self.VARIANCE/count
            self.append(LorenzParticle((xyz,)*3))


def main():
    engine = spyre.Engine()
    engine.setup()
    engine.add(zoeobj.AxesObject(50.0))
    engine.add(LorenzGroup(PARTICLES))
    engine.add(zoeobj.FrameRateCounter(engine))
    engine.go()

if __name__ == '__main__': main()
