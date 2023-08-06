#! /usr/bin/python

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy


class Bug(object):
    def __init__(self):        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutCreateWindow("Bug")
        
        glutDisplayFunc(self.on_display)
        glutReshapeFunc(self.on_reshape)

        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glShadeModel(GL_FLAT)

        glMatrixMode(GL_MODELVIEW)
        glLightfv(GL_LIGHT0, GL_POSITION,  (40.0, 40, 100.0, 0.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.99, 0.99, 0.99, 1.0))
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glColorMaterial(GL_FRONT_AND_BACK, GL_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
        
        self.quad = gluNewQuadric()

    def on_reshape(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        a = 9.0/min(width, height)
        clipping_planes = (a*width, a*height)
        glFrustum(-clipping_planes[0], clipping_planes[0], -clipping_planes[1], clipping_planes[1], 50.0, 150.0)


    def on_display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # BEGIN INTERESTING PART
        # Set up the model view matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        transf = numpy.identity(4, dtype=numpy.float32)
        s = numpy.sin(0.1)
        c = numpy.cos(0.1)
        # A Given's rotation about the z-axis
        transf[0,0] = c
        transf[0,1] = s
        transf[1,0] = -s
        transf[1,1] = c
        # A translation
        transf[0,3] = 2.5
        transf[2,3] = -80
        print glGetFloatv(GL_MODELVIEW_MATRIX)
        print transf.transpose()
        # This doesn't work:
        glMultMatrixf(transf.transpose())
        # This does work:
        #glMultMatrixf(transf.transpose().copy())
        print glGetFloatv(GL_MODELVIEW_MATRIX)
        # END INTERESTING PART

        glColor3f(0.6, 0.8, 0.3)
        gluSphere(self.quad, 10, 8, 8)
        glutSwapBuffers()



if __name__ == '__main__':
    glutInit(sys.argv)
    Bug()
    glutMainLoop ()
