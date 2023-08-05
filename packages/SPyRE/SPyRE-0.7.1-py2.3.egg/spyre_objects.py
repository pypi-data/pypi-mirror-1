#!/usr/local/bin/python

""" Object classes for spyre engines
"""

__program__ = 'stereo_zoe_objects'
__author__ = 'David Keeney <dkeeney@travelbyroad.net>'
__copyright__ = 'Copyright (C) 2004 David Keeney'
__license__ = 'Python '


import spyre
import sys

import OpenGL.GL as ogl

# Object #==================================================

class DisplayListObject (spyre.Object):

    """Object that stores graphic elements as OpenGL Display
    Lists for quicker display
    """
    
    def __init__(self):
        """Initialize new instance. """
        spyre.Object.__init__(self)
        self.DLId = 0
        spyre.Object.opengl_state_dependent.append(self)


    def display(self):
        """Compiles display into display list and displays it"""
        if self.DLId > 0:
            # display list
            ogl.glCallList( self.DLId ) 
        else:
            # generate and display list
            if self.DLId == 0:
                self.DLId = ogl.glGenLists(1) # get one number 
            else: # DLId < 0
                self.DLId = -self.DLId
                
            ogl.glNewList( self.DLId, ogl.GL_COMPILE_AND_EXECUTE ) 
            self._display()
            ogl.glEndList()    
    
    def _display(self):
        """Display the object.  This method must be overridden."""
        raise NotImplementedError
    
    
    def regenerate(self):
        """Regenerate display list """
        self.DLId = -self.DLId
        