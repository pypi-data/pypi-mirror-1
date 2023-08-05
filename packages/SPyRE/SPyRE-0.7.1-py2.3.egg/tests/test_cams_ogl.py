"""Tests for camera methods, that involve OpenGL.  """

import unittest
import math

from pygame import locals, display, init
import OpenGL.GL as ogl
import OpenGL.GLU as oglu

import spyre

class FauxEngine(object):

    def __init__(self):
        self.width = 100
        self.height = 100
        self.objects = []


FUZZ = 0.00000001
ZERO_ZERO_ONE = None
ONE_ONE_ONE = None
ORTHO = None
FRUSTUM = None
WRENCH = [[0,1,2,3],[4,5,6,7],[8,9,10,11],[12,13,14,15]]

init()
window = display.set_mode((10,10), locals.OPENGL)

def setRefMatrices():

    global ZERO_ZERO_ONE, ONE_ONE_ONE, ORTHO, FRUSTUM
    ogl.glMatrixMode(ogl.GL_MODELVIEW)
    ogl.glLoadIdentity()
    oglu.gluLookAt(1,1,1,0,0,0,0,1,0)
    ONE_ONE_ONE = ogl.glGetFloatv(ogl.GL_MODELVIEW_MATRIX)
    ogl.glLoadIdentity()
    oglu.gluLookAt(0,0,1,0,0,0,0,1,0)
    ZERO_ZERO_ONE = ogl.glGetFloatv(ogl.GL_MODELVIEW_MATRIX)
    ogl.glLoadIdentity()

    ogl.glMatrixMode(ogl.GL_PROJECTION)
    ogl.glLoadIdentity()
    ogl.glOrtho(-1,1,-1,1,-1,1)
    ORTHO = ogl.glGetFloatv(ogl.GL_PROJECTION_MATRIX)

    ogl.glMatrixMode(ogl.GL_PROJECTION)
    ogl.glLoadIdentity()
    ogl.glFrustum(-1,1,-1,1,1,3)
    FRUSTUM = ogl.glGetFloatv(ogl.GL_PROJECTION_MATRIX)
    ogl.glLoadIdentity()


def difference(a, b):
    a2 = []
    b2 = []
    for i in a:
        a2.extend(i)
    for j in b:
        b2.extend(j)
    t = map(lambda x,y: (x-y)**2, a2, b2)
    d = reduce(lambda x,y: x+y, t, 0)
    return d**0.5

def distance(a, b):
    d = math.sqrt((b[0]-a[0])**2 + (b[1]-a[1])**2 + (b[2]-a[2])**2)
    return d


class T01_CamTestOrtho(unittest.TestCase):
    """Test Camera functionality for basic camera ortho."""
    
    def setUp(self):
        setRefMatrices()
        ogl.glMatrixMode(ogl.GL_MODELVIEW)
        ogl.glLoadIdentity()
        ogl.glMatrixMode(ogl.GL_PROJECTION)
        ogl.glLoadIdentity()
        fe = FauxEngine()
        self.cam = spyre.BasicCameraOrtho(fe, (0,0,1))
        self.cam.setup()
        
    def test001_viewMV(self):
        """Test that viewMV creates correct matrix for eye (0,0,1)."""
        global ZERO_ZERO_ONE
        self.cam.eye = (0,0,1)
        self.cam.up = (0,1,0)
        self.cam.refresh()
        self.assert_(distance(self.cam.eye, (0,0,1))<FUZZ, self.cam.eye)
        self.assert_(distance(self.cam.center, (0,0,0))<FUZZ, self.cam.center)
        self.cam.viewMV()
        self.assert_(ogl.glGetInteger(ogl.GL_MATRIX_MODE) == ogl.GL_MODELVIEW)
        mat = ogl.glGetFloatv(ogl.GL_MODELVIEW_MATRIX)
        d = difference(mat, ZERO_ZERO_ONE)
        self.assert_(d < FUZZ, mat)
        
    def test002_viewMV(self):
        """Test that viewMV creates correct matrix for eye (1,1,1)."""
        global ONE_ONE_ONE, WRENCH
        self.cam.eye = (1,1,1)
        self.cam.refresh()
        self.assert_(distance(self.cam.eye, (1,1,1))<FUZZ, self.cam.eye)
        self.assert_(distance(self.cam.center, (0,0,0))<FUZZ, self.cam.center)
        self.cam.viewMV()
        self.assert_(ogl.glGetInteger(ogl.GL_MATRIX_MODE) == ogl.GL_MODELVIEW)
        mat = ogl.glGetFloatv(ogl.GL_MODELVIEW_MATRIX)
        d = difference(mat, ONE_ONE_ONE)
        self.assert_(d<FUZZ, (mat, ONE_ONE_ONE))
        e = difference(mat, WRENCH)
        self.assert_(e>FUZZ, e)
        
    def test003_ortho(self):
        """Test that ortho creates correct matrix with (-1,1,-1,1,-1,1)."""
        global ORTHO, WRENCH
        self.cam.ortho(-1,1,-1,1,-1,1)
        self.cam.viewProj()
        self.assert_(ogl.glGetInteger(ogl.GL_MATRIX_MODE) == ogl.GL_PROJECTION)
        mat = ogl.glGetFloatv(ogl.GL_PROJECTION_MATRIX)
        d = difference(mat, ORTHO)
        self.assert_(d < FUZZ, d)
        e = difference(mat, WRENCH)
        self.assert_(e > FUZZ, e)
        

class T02_CamTestFrustum(T01_CamTestOrtho):
    """Test Camera functionality for basic camera frustum."""
    
    def setUp(self):
        setRefMatrices()
        ogl.glMatrixMode(ogl.GL_MODELVIEW)
        ogl.glLoadIdentity()
        ogl.glMatrixMode(ogl.GL_PROJECTION)
        ogl.glLoadIdentity()
        fe = FauxEngine()
        self.cam = spyre.BasicCameraFrustum(fe, (0,0,1))
        self.cam.setup()
        
    def test003_ortho(self):
        """Test that frustum creates correct matrix with (-1,1,-1,1,-1,1)."""
        global FRUSTUM, WRENCH
        self.cam.frustum(-1,1,-1,1,1,3)
        self.cam.viewProj()
        self.assert_(ogl.glGetInteger(ogl.GL_MATRIX_MODE) == ogl.GL_PROJECTION)
        mat = ogl.glGetFloatv(ogl.GL_PROJECTION_MATRIX)
        d = difference(mat, FRUSTUM)
        self.assert_(d<FUZZ, mat)
        e = difference(mat, WRENCH)
        self.assert_(e>FUZZ, e)


class T04_MobileCameraOrtho(T01_CamTestOrtho):
    """Test Mobile Camera """
    
    def setUp(self):
        setRefMatrices()
        fe = FauxEngine()
        self.cam = spyre.MobileCameraOrtho(fe, 1)
        self.cam.setup()
        self.cam.up = (0,1,0)
        self.cam.refresh()
        ogl.glMatrixMode(ogl.GL_MODELVIEW)
        ogl.glLoadIdentity()
        ogl.glMatrixMode(ogl.GL_PROJECTION)
        ogl.glLoadIdentity()
                

class T05_MobileCameraOrtho(T02_CamTestFrustum):
    """Test Mobile Camera """
    
    def setUp(self):
        setRefMatrices()
        fe = FauxEngine()
        self.cam = spyre.MobileCameraFrustum(fe, 1)
        self.cam.setup()
        self.cam.up = (0,1,0)
        self.cam.refresh()
        ogl.glMatrixMode(ogl.GL_MODELVIEW)
        ogl.glLoadIdentity()
        ogl.glMatrixMode(ogl.GL_PROJECTION)
        ogl.glLoadIdentity()
                

        
        
if __name__ == '__main__':
    unittest.main()
    
