
import spyre

import sys
import math

import OpenGL.GL as ogl

tp_patchdata = (
  (102, 103, 104, 105, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15),
  (12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27),
  (24, 25, 26, 27, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40),
  (96, 96, 96, 96, 97, 98, 99, 100, 101, 101, 101, 101, 0, 1, 2, 3,),
  (0, 1, 2, 3, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117),
  (118, 118, 118, 118, 124, 122, 119, 121, 123, 126, 125, 120, 40, 39, 38, 37),
  (41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56),
  (53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 28, 65, 66, 67),
  (68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83),
  (80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95)
)

tp_cpdata = (
    (0.2, 0, 2.7), (0.2, -0.112, 2.7), (0.112, -0.2, 2.7), 
    (0, -0.2, 2.7), (1.3375, 0, 2.53125), (1.3375, -0.749, 2.53125),
    (0.749, -1.3375, 2.53125), (0, -1.3375, 2.53125), (1.4375, 0, 2.53125), 
    (1.4375, -0.805, 2.53125), (0.805, -1.4375, 2.53125), (0, -1.4375, 2.53125), 
    (1.5, 0, 2.4), (1.5, -0.84, 2.4), (0.84, -1.5, 2.4), 
    (0, -1.5, 2.4), (1.75, 0, 1.875), (1.75, -0.98, 1.875), 
    (0.98, -1.75, 1.875), (0, -1.75, 1.875), (2, 0, 1.35), 
    (2, -1.12, 1.35), (1.12, -2, 1.35), (0, -2, 1.35), 
    (2, 0, 0.9), (2, -1.12, 0.9), (1.12, -2, 0.9), 
    (0, -2, 0.9), (-2, 0, 0.9), (2, 0, 0.45), 
    (2, -1.12, 0.45), (1.12, -2, 0.45), (0, -2, 0.45), 
    (1.5, 0, 0.225), (1.5, -0.84, 0.225), (0.84, -1.5, 0.225), 
    (0, -1.5, 0.225), (1.5, 0, 0.15), (1.5, -0.84, 0.15), 
    (0.84, -1.5, 0.15), (0, -1.5, 0.15), (-1.6, 0, 2.025), 
    (-1.6, -0.3, 2.025), (-1.5, -0.3, 2.25), (-1.5, 0, 2.25), 
    (-2.3, 0, 2.025), (-2.3, -0.3, 2.025), (-2.5, -0.3, 2.25), 
    (-2.5, 0, 2.25), (-2.7, 0, 2.025), (-2.7, -0.3, 2.025), 
    (-3, -0.3, 2.25), (-3, 0, 2.25), (-2.7, 0, 1.8), 
    (-2.7, -0.3, 1.8), (-3, -0.3, 1.8), (-3, 0, 1.8), 
    (-2.7, 0, 1.575), (-2.7, -0.3, 1.575), (-3, -0.3, 1.35), 
    (-3, 0, 1.35), (-2.5, 0, 1.125), (-2.5, -0.3, 1.125), 
    (-2.65, -0.3, 0.9375), (-2.65, 0, 0.9375), (-2, -0.3, 0.9), 
    (-1.9, -0.3, 0.6), (-1.9, 0, 0.6), (1.7, 0, 1.425), 
    (1.7, -0.66, 1.425), (1.7, -0.66, 0.6), (1.7, 0, 0.6), 
    (2.6, 0, 1.425), (2.6, -0.66, 1.425), (3.1, -0.66, 0.825), 
    (3.1, 0, 0.825), (2.3, 0, 2.1), (2.3, -0.25, 2.1),
    (2.4, -0.25, 2.025), (2.4, 0, 2.025), (2.7, 0, 2.4), 
    (2.7, -0.25, 2.4), (3.3, -0.25, 2.4), (3.3, 0, 2.4), 
    (2.8, 0, 2.475), (2.8, -0.25, 2.475), (3.525, -0.25, 2.49375),
    (3.525, 0, 2.49375), (2.9, 0, 2.475), (2.9, -0.15, 2.475),
    (3.45, -0.15, 2.5125), (3.45, 0, 2.5125), (2.8, 0, 2.4),
    (2.8, -0.15, 2.4), (3.2, -0.15, 2.4), (3.2, 0, 2.4), 
    (0, 0, 3.15), (0.8, 0, 3.15), (0.8, -0.45, 3.15), 
    (0.45, -0.8, 3.15), (0, -0.8, 3.15), (0, 0, 2.85), 
    (1.4, 0, 2.4), (1.4, -0.784, 2.4), (0.784, -1.4, 2.4), 
    (0, -1.4, 2.4), (0.4, 0, 2.55), (0.4, -0.224, 2.55), 
    (0.224, -0.4, 2.55), (0, -0.4, 2.55), (1.3, 0, 2.55), 
    (1.3, -0.728, 2.55), (0.728, -1.3, 2.55), (0, -1.3, 2.55), 
    (1.3, 0, 2.4), (1.3, -0.728, 2.4), (0.728, -1.3, 2.4), 
    (0, -1.3, 2.4), (0, 0, 0), (1.425, -0.798, 0), 
    (1.5, 0, 0.075), (1.425, 0, 0), (0.798, -1.425, 0), 
    (0, -1.5, 0.075), (0, -1.425, 0), (1.5, -0.84, 0.075),
    (0.84, -1.5, 0.075)
)

tp_tex  = ( ( (0, 0), (1, 0)), ( (0, 1), (1, 1)) )





class shapeTeapot(spyre.Object):
    """draws a teapot, bottom in xy plane.
       init with ( size, type ) where type is 'GL_FILL' (default)
       or 'GL_LINE'
    """
    def __init__(self, size, type=ogl.GL_FILL):
        spyre.Object.__init__(self)
        self.size = size
        self.type = type

    def display(self):

        grid = 14

        ogl.glPushAttrib(ogl.GL_ENABLE_BIT | ogl.GL_EVAL_BIT);
        ogl.glEnable(ogl.GL_AUTO_NORMAL);
        ogl.glEnable(ogl.GL_NORMALIZE);
        ogl.glEnable(ogl.GL_MAP2_VERTEX_3);
        ogl.glEnable(ogl.GL_MAP2_TEXTURE_COORD_2);

        ogl.glPushMatrix()

        ogl.glMaterialfv( ogl.GL_FRONT, ogl.GL_AMBIENT, [0.25,0.25,0.25,1] )
        ogl.glMaterialfv( ogl.GL_FRONT, ogl.GL_DIFFUSE, [0.4,0.4,0.4,1] )
        ogl.glMaterialfv( ogl.GL_FRONT, ogl.GL_SPECULAR, [0.4,0.4,0.4,1] )

        ogl.glScalef(0.5*self.size, 0.5*self.size, 0.5*self.size);
        ogl.glTranslatef(0.0, 0.0, -1.5);

        p = []; q = []; r=[]; s=[]
        for j in range(4):
            p.append([])
            q.append([])
            r.append([])
            s.append([])
            for k in range(4):
                p[j].append([])
                q[j].append([])
                r[j].append([])
                s[j].append([])
                for l in range(3):
                    p[j][k].append([])
                    q[j][k].append([])
                    r[j][k].append([])
                    s[j][k].append([])


        for i in range(10):
            for j in range(4):
                for k in range(4):
                    for l in range(3):
                        p[j][k][l] = tp_cpdata[tp_patchdata[i][j * 4 + k]][l]
                        q[j][k][l] = tp_cpdata[tp_patchdata[i][j * 4 + (3 - k)]][l]
                        if (l == 1):
                            q[j][k][l] *= -1.0
                        if (i < 6):
                            r[j][k][l] = tp_cpdata[tp_patchdata[i][j * 4 + (3 - k)]][l]
                            if (l == 0):
                                r[j][k][l] *= -1.0
                            s[j][k][l] = tp_cpdata[tp_patchdata[i][j * 4 + k]][l]
                            if (l == 0):
                                s[j][k][l] *= -1.0
                            if (l == 1):
                                s[j][k][l] *= -1.0

            ogl.glMap2f(ogl.GL_MAP2_TEXTURE_COORD_2, 0, 1, 0, 1, tp_tex)
            ogl.glMap2f(ogl.GL_MAP2_VERTEX_3, 0, 1, 0, 1, p)
            ogl.glMapGrid2f(grid, 0.0, 1.0, grid, 0.0, 1.0)
            ogl.glEvalMesh2(self.type, 0, grid, 0, grid)
            ogl.glMap2f(ogl.GL_MAP2_VERTEX_3, 0, 1, 0, 1, q)
            ogl.glEvalMesh2(self.type, 0, grid, 0, grid)
            if i < 6 :
                ogl.glMap2f(ogl.GL_MAP2_VERTEX_3, 0, 1, 0, 1, r)
                ogl.glEvalMesh2(self.type, 0, grid, 0, grid)
                ogl.glMap2f(ogl.GL_MAP2_VERTEX_3, 0, 1, 0, 1, s)
                ogl.glEvalMesh2(self.type, 0, grid, 0, grid)
                  
        ogl.glPopMatrix()
        ogl.glPopAttrib()
    


cu_n = (
    (-1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (1.0, 0.0, 0.0),
    (0.0, -1.0, 0.0),
    (0.0, 0.0, 1.0),
    (0.0, 0.0, -1.0)
)
cu_faces = (
    (0, 1, 2, 3),
    (3, 2, 6, 7),
    (7, 6, 5, 4),
    (4, 5, 1, 0),
    (5, 6, 2, 1),
    (7, 4, 0, 3)
)


class shapeCube(spyre.Object):
    """draws a cube, 
       init with ( size, type ) where type is 'GL_LINE_LOOP' (default)
       or 'GL_QUADS'
    """
    def __init__(self, size, type=ogl.GL_LINE_LOOP):
        spyre.Object.__init__(self)
        self.size = size
        self.type = type

    def display(self):
                
        v = []
        for i in range(8):
            v.append([])
            for j in range(3):
                v[i].append([])

        v[0][0] = v[1][0] = v[2][0] = v[3][0] = -self.size / 2
        v[4][0] = v[5][0] = v[6][0] = v[7][0] = self.size / 2
        v[0][1] = v[1][1] = v[4][1] = v[5][1] = -self.size / 2
        v[2][1] = v[3][1] = v[6][1] = v[7][1] = self.size / 2
        v[0][2] = v[3][2] = v[4][2] = v[7][2] = -self.size / 2
        v[1][2] = v[2][2] = v[5][2] = v[6][2] = self.size / 2

        for i in range(5):
            j = 5-i
            ogl.glBegin(self.type)
            ogl.glNormal3fv(cu_n[j])
            ogl.glVertex3fv(v[cu_faces[j][0]])
            ogl.glVertex3fv(v[cu_faces[j][1]])
            ogl.glVertex3fv(v[cu_faces[j][2]])
            ogl.glVertex3fv(v[cu_faces[j][3]])
            ogl.glEnd()


def pentagon( a, b, c, d, e, Type):
    """ draws a pentagram using 5 vectors in dodec """
    ogl.glBegin(Type)
    ogl.glVertex3fv(a)
    ogl.glVertex3fv(b)
    ogl.glVertex3fv(c)
    ogl.glVertex3fv(d)
    ogl.glVertex3fv(e)
    ogl.glEnd()


class shapeDodecahedron(spyre.Object):
    """draws a dodecahedron, 
       init with ( type ) where type is 'GL_LINE_LOOP' (default)
       or 'GL_QUADS'
    """
    def __init__(self, type=ogl.GL_LINE_LOOP):
        spyre.Object.__init__(self)
        self.type = type
        self.dodec = []

        alpha = math.sqrt(2.0 / (3.0 + math.sqrt(5.0)))
        beta = 1.0 + math.sqrt(6.0 / (3.0 + math.sqrt(5.0)) -
            2.0 + 2.0 * math.sqrt(2.0 / (3.0 + math.sqrt(5.0))))
            
        self.dodec.append( [ -alpha, 0, beta ] )
        self.dodec.append( [ alpha, 0, beta ] )
        self.dodec.append( [ -1, -1, -1 ] )
        self.dodec.append( [ -1, -1, 1 ] )
        self.dodec.append( [ -1, 1, -1 ] )
        self.dodec.append( [ -1, 1, 1 ] )
        self.dodec.append( [ 1, -1, -1 ] )
        self.dodec.append( [ 1, -1, 1 ] )
        self.dodec.append( [ 1, 1, -1 ] )
        self.dodec.append( [ 1, 1, 1 ] )
        self.dodec.append( [ beta, alpha, 0 ] )
        self.dodec.append( [ beta, -alpha, 0 ] )
        self.dodec.append( [ -beta, alpha, 0 ] )
        self.dodec.append( [ -beta, -alpha, 0 ] )
        self.dodec.append( [ -alpha, 0, -beta ] )
        self.dodec.append( [ alpha, 0, -beta ] )
        self.dodec.append( [ 0, beta, alpha ] )
        self.dodec.append( [ 0, beta, -alpha ] )
        self.dodec.append( [ 0, -beta, alpha ] )
        self.dodec.append( [ 0, -beta, -alpha ] )


    def Spentagon(self,a,b,c,d,e):
    
        pentagon(self.dodec[a], self.dodec[b], self.dodec[c], self.dodec[d], self.dodec[e], self.type);


    def display(self):
        """ display nothing """
        self.Spentagon(0, 1, 9, 16, 5);
        self.Spentagon(1, 0, 3, 18, 7);
        self.Spentagon(1, 7, 11, 10, 9);
        self.Spentagon(11, 7, 18, 19, 6);
        self.Spentagon(8, 17, 16, 9, 10);
        self.Spentagon(2, 14, 15, 6, 19);
        self.Spentagon(2, 13, 12, 4, 14);
        self.Spentagon(2, 19, 18, 3, 13);
        self.Spentagon(3, 0, 5, 12, 13);
        self.Spentagon(6, 15, 8, 10, 11);
        self.Spentagon(4, 17, 8, 15, 14);
        self.Spentagon(4, 12, 5, 16, 17);



def drawTriangle( v0, v1, v2, Type ):
    """ draws a triangle using three provided points """
    ogl.glBegin(Type);
    ogl.glVertex3fv(v0) # order 1,0.2
    ogl.glVertex3fv(v1)
    ogl.glVertex3fv(v2)
    ogl.glEnd();



T = 1.73205080756887729 / 2

tet_data = (
  (T, T, T),
  (T, -T, -T),
  (-T, T, -T),
  (-T, -T, T)
)

tet_ndex = (
  (0, 1, 3),
  (2, 1, 0),
  (3, 2, 0),
  (1, 2, 3)
)


class shapeTetrahedron(spyre.Object):
    """draws a tetrahedron, 
       init with ( type ) where type is 'GL_LINE_LOOP' (default)
       or 'GL_QUADS'
    """
    def __init__(self, type=ogl.GL_LINE_LOOP):
        spyre.Object.__init__(self)
        self.type = type

    def display(self):
                
        for i in range(4):
            
            drawTriangle(   tet_data[tet_ndex[i][0]], 
                            tet_data[tet_ndex[i][1]],
                            tet_data[tet_ndex[i][2]],
                            self.type                )



