"""Test loading and use of a simple extension"""
from OpenGL.GL import *
from OpenGL.GL.ARB.window_pos import *
from OpenGL import platform
import ctypes

if __name__ == "__main__":
	#from OpenGL.tests import testing_context
	#testing_context.createPyGameContext()
	
	print 'glWindowPos2dARB', glWindowPos2dARB
	glWindowPos2dARB( 0.0, 3.0 )
	glWindowPos2dARB( 0.0, 3.0 )
	
##	glClearColor( 0,0,0, 0 )
##	glClear( GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT )
##	glDisable( GL_LIGHTING )
	
##	function = platform.getExtensionProcedure( 'glWindowPos2dARB' )
##	FTYPE = platform.FunctionType(
##		ctypes.c_void_p,
##		ctypes.c_double,
##		ctypes.c_double,
##	)
##	function2 = FTYPE( function )
##	print function, function2
##	function2( 0.0, 3.0 )
	
