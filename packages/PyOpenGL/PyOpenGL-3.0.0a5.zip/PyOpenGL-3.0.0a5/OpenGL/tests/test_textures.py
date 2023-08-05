"""Test GLU quadrics operations"""
from OpenGL.GL import *
from OpenGL.GLU import *
import time
from OpenGLContext import texture
import Image
ourTexture = None

def display( count ):
	global ourTexture
	if ourTexture is None:
		ourTexture = texture.Texture(
			Image.open( 'lightmap.png' )
		)
	glClearColor( 0,0,0, 0 )
	glClear( GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT )
	glClearColor( 1,1,1, 0 )
	glClear( GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT )
	ourTexture()
	
	glDisable( GL_LIGHTING )
	quad = gluNewQuadric()
	glColor3f( .5,.5, count/100. )
	gluSphere( quad, 1.0, 16, 16 )

if __name__ == "__main__":
	from OpenGL.tests import testing_context
	import pygame
	testing_context.createPyGameContext()
	
	for x in range( 1000 ):
		display(x)
		pygame.display.flip()
