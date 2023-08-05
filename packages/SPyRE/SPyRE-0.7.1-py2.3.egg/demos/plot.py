#!/usr/local/bin/python
#

"""
A viewer of 3D surfaces, specified by functions of the type z = f(x, y).
"""

import math
import sys
import types

sys.path.append('..')
import spyre
import zoe_objects as zoeobj


class ParsedObject(zoeobj.ReplayingObject):

    """A parser for a priorietary and obsolete file format."""
    
    colorLookup = {0: (0.0, 0.0, 0.0),
                   1: (0.0, 0.0, 0.5),
                   2: (0.0, 0.5, 0.0),
                   3: (1.0, 1.0, 1.0), ###
                   4: (0.5, 0.0, 0.0),
                   5: (1.0, 1.0, 1.0), ###
                   6: (1.0, 1.0, 1.0), ###
                   7: (0.5, 0.5, 0.5),
                   8: (0.25, 0.25, 0.25),
                   9: (0.0, 0.0, 1.0),
                   10: (0.0, 1.0, 0.0),
                   11: (1.0, 1.0, 1.0), ##
                   12: (1.0, 0.0, 0.0),
                   13: (1.0, 1.0, 1.0), ###
                   14: (1.0, 1.0, 0.0),
                   15: (1.0, 1.0, 1.0)}
    
    def __init__(self, file):
        spyre.ReplayingObject.__init__(self)
        for line in file.readlines():
            line = line[:-1]
            line.strip()
            if not line:
                continue
            if line[0] == '#':
                continue
            words = line.split()
            if not words:
                continue
            verb, rest = words[0], words[1:]
            if verb == 'color':
                self.setColor(self.tuplize(self.colorLookup[int(rest[0])]))
            elif verb == 'point':
                self.startPath()
                self.vertex(self.tuplize(rest))
                self.endPath()
            elif verb == 'line':
                self.startPath()
                self.vertex(self.tuplize(rest[0:3]))
                self.vertex(self.tuplize(rest[3:6]))
            elif verb == 'relline':
                self.vertex(self.tuplize(rest))
            elif verb == 'circle':
                x, y, z, r = self.tuplize(rest)
                DIVISIONS = 16
                self.startPath()
                for i in range(DIVISIONS):
                    theta = 2*math.pi*i/DIVISIONS
                    self.vertex((x + r*math.cos(theta), y + r*math.sin(theta), z))
                self.closePath()
                self.startPath()
                for i in range(DIVISIONS):
                    theta = 2*math.pi*i/DIVISIONS
                    self.vertex((x, y + r*math.cos(theta), z + r*math.sin(theta)))
                self.closePath()
                self.startPath()
                for i in range(DIVISIONS):
                    theta = 2*math.pi*i/DIVISIONS
                    self.vertex((x + r*math.cos(theta), y, z + r*math.sin(theta)))
                self.closePath()
            else:
                print >> sys.stderr, "unknown verb: %s" % verb
        self.done()

    def tuplize(self, seq):
        return tuple(map(lambda x: float(x), seq))


def main():
    if len(sys.argv) == 1:
        print >> sys.stderr, "usage: %s <function of x, y>" % sys.argv[0]
        sys.exit()
    arg = sys.argv[1]
    if arg.endswith('.3d'):
        file = open(arg, 'r')
        object = ParsedObject(file)
        file.close()
    else:
        func = eval('lambda x, y: %s' % arg)
        object = zoeobj.Plotter(func)
    engine = spyre.Engine()
    engine.add(object)
    engine.go()

if __name__ == '__main__': main()
