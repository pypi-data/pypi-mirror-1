"""Test GLU quadrics operations"""
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import time

count = 0

def display( *args ):
	print 'display'
	global count
	count += 1
	glClearColor( 0,0,0, 0 )
	glClear( GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT )
	glClearColor( 1,1,1, 0 )
	glClear( GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT )
	
	glDisable( GL_LIGHTING )
	quad = gluNewQuadric()
	glColor3f( .5,.5, count/100. )
	gluSphere( quad, 1.0, 16, 16 )
	glFlush ()
	glutSwapBuffers()

if __name__ == "__main__":
	from OpenGL.tests import testing_context
	import pygame
	testing_context.createGLUTContext()
##	testing_context.createPyGameContext()
	glutDisplayFunc(display)
	glutMainLoop()

	
