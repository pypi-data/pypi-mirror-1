"""Tests for spyres principle component, the engine.  """

import unittest
import time

import pygame

import spyre

FUZZ = 0.00000001

clock = pygame.time.Clock()

class TestException(Exception):
    pass

def doNothing():
    pass
    
def tstRaise():
    raise TestException

class T01_Timekeeper(unittest.TestCase):
    """Test functions for TimeKeeper base class."""
    
    def setUp(self):
        self.tk = spyre.TimeKeeper()
        self.tk.display_interval = 1.0/50.0
        clock.tick(50)
            
    def test001_addDelay(self):
        """Test that addDelay changes delay list. """
        t0 = time.time()
        self.tk.addDelay(50, doNothing, ())
        self.assert_(len(self.tk.delayeds)==1)
        self.assert_(self.tk.delayeds[0][0] >= t0, self.tk.delayeds[0][0])
    
    def test011_runDelay(self):
        """Test that a 0 delay task gets called.. """
        t0 = time.time()
        self.tk.addDelay(0, tstRaise, ())
        self.assert_(len(self.tk.delayeds)==1)
        self.assert_(self.tk.delayeds[0][0] >= t0, self.tk.delayeds[0][0])
        self.assertRaises(TestException, self.tk.delayManager, )
    
    def test012_runDelay(self):
        """Test that a 15 ms delay task gets called.. """
        t0 = time.time()
        self.tk.addDelay(15, tstRaise, ())
        self.assert_(len(self.tk.delayeds)==1)
        self.assert_(self.tk.delayeds[0][0] >= t0, self.tk.delayeds[0][0])
        #self.tk.delayManager()
        clock.tick(50)
        #self.tk.delayManager()
        self.assertRaises(TestException, self.tk.delayManager, )
    
    def test013_runDelay(self):
        """Test that a 50 ms delay task gets called.. """
        t0 = time.time()
        self.tk.addDelay(50, tstRaise, ())
        self.assert_(len(self.tk.delayeds)==1)
        self.assert_(self.tk.delayeds[0][0] >= t0, self.tk.delayeds[0][0])
        self.tk.delayManager()
        clock.tick(50)
        self.tk.delayManager()
        clock.tick(50)
        self.tk.delayManager()
        clock.tick(50)
        self.assertRaises(TestException, self.tk.delayManager, )
    
if __name__ == '__main__':
    unittest.main()