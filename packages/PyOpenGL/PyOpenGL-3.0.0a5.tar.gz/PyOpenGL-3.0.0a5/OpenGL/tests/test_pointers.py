from OpenGL import GL, arrays, constants
import OpenGL, numpy
import ctypes
from OpenGL.arrays import formathandler
#formathandler.FormatHandler.chooseOutput( 'numpy' )

vertex = constants.GLdouble * 3
vArray =  vertex * 2




if __name__ == "__main__":
	from OpenGL.tests import testing_context
	testing_context.createPyGameContext()
	print GL.glVertexPointerd( [[2,3,4,5],[2,3,4,5]] )
	print GL.glVertexPointeri( ([2,3,4,5],[2,3,4,5]) )
	print GL.glVertexPointers( [[2,3,4,5],[2,3,4,5]] )
	print GL.glVertexPointerd( vArray( vertex(2,3,4),vertex(2,3,4) ) )
	myVector = vArray( vertex(2,3,4),vertex(2,3,4) )
	print GL.glVertexPointer(
		3,
		GL.GL_DOUBLE,
		0,
		ctypes.cast( myVector, ctypes.POINTER(constants.GLdouble)) 
	)
		
	
	#print GL.glVertexPointerd( numpy.array([[2,3,4,5],[2,3,4,5]],'d') )
	print repr(GL.glVertexPointerb( [[2,3],[4,5]] ))
	print GL.glVertexPointerf( [[2,3],[4,5]] )
	assert arrays.ArrayDatatype.dataPointer( None ) == None
	print GL.glVertexPointerf( None )
	
	print GL.glNormalPointerd( [[2,3,4],[2,3,4]] )
	print GL.glNormalPointerd( None )

	print GL.glTexCoordPointerd( [[2,3,4],[2,3,4]] )
	print GL.glTexCoordPointerd( None )

	print GL.glColorPointerd( [[2,3,4],[2,3,4]] )
	print GL.glColorPointerd( None )

	print GL.glEdgeFlagPointerb( [0,1,0,0,1,0] )
	print GL.glEdgeFlagPointerb( None )

	print GL.glIndexPointerd( [0,1,0,0,1,0] )
	print GL.glIndexPointerd( None )
	
	print GL.glColor4fv( [0,0,0,1] )
	a =  GL.glColor4fv( [0,0,0,1] )
	print 'Array type', type(a) 

	# string data-types...
	import struct
	s = struct.pack( '>iiii', 2,3,4,5 ) * 2
	print GL.glVertexPointer( 4,GL.GL_INT,0,s )

