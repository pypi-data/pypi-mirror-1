#!/usr/local/bin/python
#

"""
A sample of a fountain effect, with perspective projection
"""

import random
import sys

import pygame

sys.path.append('..')
import la
import spyre 
import zoe_objects as zoeobj 

pygame.init()


PARTICLES = 100

class FountainParticle(zoeobj.NewtonianParticle):

    """Each particle is pulled down by a gravitational force, and is
    reset when it hits the x-y plane."""
    
    G = -0.002*la.Vector.K # 
    Z_MIN = 0.0 # 

    trailLength = 5

    def update(self):
        self.impulse(self.G)
        zoeobj.NewtonianParticle.update(self)

    def ok(self):
        return self.pos[2] >= self.Z_MIN


class FountainSystem(zoeobj.System):

    """Manage the fountain particles, creating them at the origin with some
    random upward velocity."""
    
    V0_MAX = 0.1 # maximum initial speed
    
    def new(self):
        theta = random.uniform(0, spyre.twoPi)
        phi = random.uniform(0, spyre.pi)
        vel = la.PolarVector(self.V0_MAX, theta, phi)
        return FountainParticle(la.Vector.ZERO, vel)


def main():
    engine = spyre.Engine()
    engine.camera = spyre.MobileCameraFrustum( engine, 5.0 )
    
    engine.add(zoeobj.AxesObject())
    engine.add(zoeobj.GridObject())
    engine.add(FountainSystem(PARTICLES))
    engine.add(zoeobj.FrameRateCounter(engine))
    engine.go()

if __name__ == '__main__': main()
