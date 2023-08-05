#!/usr/local/bin/python
#

"""
A sample of a number of particles engaging in a random walk.
"""

import random
import sys

import pygame

sys.path.append('..')
import la
import spyre 
import zoe_objects as zoeobj 


PARTICLES = 100


class WalkParticle(zoeobj.NewtonianParticle):

    """A particle gets successive random nudges applied to its
    velocity.  It is recycled when it wanders too far."""
    
    EPSILON = 0.01 # the velocity nudge factor
    R_MAX_SQUARED = 10.0**2 # the maximum distance before recycling

    trailLength = 10

    def update(self):
        epsilon = la.Vector(random.uniform(-self.EPSILON, self.EPSILON), \
                            random.uniform(-self.EPSILON, self.EPSILON), \
                            random.uniform(-self.EPSILON, self.EPSILON))
        self.impulse(epsilon)
        zoeobj.NewtonianParticle.update(self)

    def ok(self):
        return la.Vector(*self.pos).normSquared() <= self.R_MAX_SQUARED


class WalkSystem(zoeobj.System):

    """Manage the walk system.  All particles start out at rest, at
    the origin."""
    
    def new(self):
        return WalkParticle(la.Vector.ZERO, la.Vector.ZERO)


def main():
    engine = spyre.Engine()
    engine.add(zoeobj.AxesObject())
    engine.add(zoeobj.GridObject())
    engine.add(WalkSystem(100))
    engine.add(zoeobj.FrameRateCounter(engine))
    engine.go()

if __name__ == '__main__': main()
