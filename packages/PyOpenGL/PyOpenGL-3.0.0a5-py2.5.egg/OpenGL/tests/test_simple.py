"""Test simple functions (i.e. no pointers involved)"""
from OpenGL.GL import *
import traceback

if __name__ == "__main__":
	from OpenGL.tests import testing_context
##	testing_context.createPyGameContext()
	testing_context.createGLUTContext()
	
	glClearColor( 0,0,0, 0 )
	glClear( GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT )
	glClearColor( 1,1,1, 0 )
	glClear( GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT )
	
	glDisable( GL_LIGHTING )
##	import pdb
##	pdb.set_trace()
	glBegin( GL_TRIANGLES )
	try:
		try:
			glVertex3f( 0.,1.,0. )
		except Exception, err:
			traceback.print_exc()
		glVertex3fv( [-1,0,0] )
		glVertex3dv( [1,0,0] )
		try:
			glVertex3dv( [1,0] )
		except ValueError, err:
			#Got expected value error (good)
			pass
		else:
			raise RuntimeError(
				"""Should have raised a value error on passing 2-element array to 3-element function!""",
			)
	finally:
		glEnd()
	a = glGenTextures( 1 )
	assert a
	b = glGenTextures( 2 )
	assert len(b) == 2
	
