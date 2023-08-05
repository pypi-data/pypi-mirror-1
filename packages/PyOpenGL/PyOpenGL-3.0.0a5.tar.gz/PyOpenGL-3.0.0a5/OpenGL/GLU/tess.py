"""Wrapper/Implementation of the GLU tessellator objects for PyOpenGL"""
from OpenGL.raw import GLU as simple
from OpenGL.platform import GLU,createBaseFunction
from OpenGL.GLU import glustruct
from OpenGL import arrays, constants
import ctypes

class GLUtesselator( glustruct.GLUStruct ):
	"""Implementation class for GLUTessellator structures in OpenGL-ctypes"""
	CALLBACK_TYPES = {
		# mapping from "which" GLU enumeration to a ctypes function type
		simple.GLU_TESS_BEGIN: ctypes.CFUNCTYPE( None, simple.GLenum ),
		simple.GLU_TESS_BEGIN_DATA: ctypes.CFUNCTYPE( 
			None, simple.GLenum, ctypes.c_void_p 
		),
		simple.GLU_TESS_EDGE_FLAG: ctypes.CFUNCTYPE( None, simple.GLboolean),
		simple.GLU_TESS_EDGE_FLAG_DATA: ctypes.CFUNCTYPE( 
			None, simple.GLboolean, ctypes.c_void_p 
		),
		simple.GLU_TESS_VERTEX: ctypes.CFUNCTYPE( None, ctypes.c_void_p ),
		simple.GLU_TESS_VERTEX_DATA: ctypes.CFUNCTYPE( 
			None, ctypes.c_void_p, ctypes.c_void_p
		),
		simple.GLU_TESS_END: ctypes.CFUNCTYPE( None ),
		simple.GLU_TESS_END_DATA: ctypes.CFUNCTYPE( None, ctypes.c_void_p), 
		simple.GLU_TESS_COMBINE: ctypes.CFUNCTYPE( 
			None, 
			ctypes.POINTER(simple.GLdouble), 
			ctypes.POINTER(ctypes.c_void_p), 
			ctypes.POINTER(simple.GLfloat),
			ctypes.POINTER(ctypes.c_void_p)
		),
		simple.GLU_TESS_COMBINE_DATA: ctypes.CFUNCTYPE( 
			None, 
			ctypes.POINTER(simple.GLdouble), 
			ctypes.POINTER(ctypes.c_void_p), 
			ctypes.POINTER(simple.GLfloat),
			ctypes.POINTER(ctypes.c_void_p),
			ctypes.c_void_p,
		),
		simple.GLU_TESS_ERROR: ctypes.CFUNCTYPE( None, simple.GLenum), 
		simple.GLU_TESS_ERROR_DATA: ctypes.CFUNCTYPE( 
			None, simple.GLenum, ctypes.c_void_p
		), 
		simple.GLU_ERROR : ctypes.CFUNCTYPE( None, simple.GLenum )
	}
	WRAPPER_METHODS = {
		simple.GLU_TESS_BEGIN_DATA: 'dataWrapper',
		simple.GLU_TESS_EDGE_FLAG_DATA: 'dataWrapper',
		simple.GLU_TESS_VERTEX: 'vertexWrapper',
		simple.GLU_TESS_VERTEX_DATA: 'vertexWrapper',
		simple.GLU_TESS_END_DATA: 'dataWrapper', 
		simple.GLU_TESS_COMBINE: 'combineWrapper',
		simple.GLU_TESS_COMBINE_DATA: 'combineWrapper',
		simple.GLU_TESS_ERROR_DATA: 'dataWrapper', 
	}
	def gluTessVertex( self, location, data=None ):
		"""Add a vertex to this tessellator, storing data for later lookup"""
		vertexCache = getattr( self, 'vertexCache', None )
		if vertexCache is None:
			self.vertexCache = []
			vertexCache = self.vertexCache
		location = arrays.GLdoubleArray.asArray( location, constants.GL_DOUBLE )
		if arrays.GLdoubleArray.arraySize( location ) != 3:
			raise ValueError( """Require 3 doubles for array location, got: %s"""%(location,))
		oorValue = self.noteObject(data)
		vp = ctypes.c_void_p( oorValue )
		self.vertexCache.append( location )
		return gluTessVertexBase( self, location, vp )
	def gluTessBeginPolygon( self, data ):
		"""Note the object pointer to return it as a Python object"""
		return gluTessBeginPolygonBase( 
			self, ctypes.c_void_p(self.noteObject( data ))
		)
	def combineWrapper( self, function ):
		"""Wrap a Python function with ctypes-compatible wrapper for combine callback
		
		For a Python combine callback, the signature looks like this:
			def combine(
				GLdouble coords[3], 
				void *vertex_data[4], 
				GLfloat weight[4]
			):
				return data
		While the C signature looks like this:
			void combine( 
				GLdouble coords[3], 
				void *vertex_data[4], 
				GLfloat weight[4], 
				void **outData 
			)
		"""
		if (function is not None) and (not callable( function )):
			raise TypeError( """Require a callable callback, got:  %s"""%(function,))
		def wrap( coords, vertex_data, weight, outData, *args ):
			"""The run-time wrapper around the function"""
			coords = self.ptrAsArray( coords, 3, arrays.GLdoubleArray )
			weight = self.ptrAsArray( weight, 4, arrays.GLfloatArray )
			# find the original python objects for vertex data
			vertex_data = [ self.originalObject( vertex_data[i] ) for i in range(4) ]
			args = tuple( [ self.originalObject( x ) for x in args ] )
			try:
				result = function( coords, vertex_data, weight, *args )
			except Exception, err:
				raise err.__class__(
					"""Failure during combine callback %r with args( %s,%s,%s,*%s):\n%s"""%(
						function, coords, vertex_data, weight, args, str(err),
					)
				)
			outP = ctypes.c_void_p(self.noteObject(result))
			outData.contents = outP 
			return None
		return wrap
	def dataWrapper( self, function ):
		"""Wrap a function which only has the one data-pointer as last arg"""
		if (function is not None) and (not callable( function )):
			raise TypeError( """Require a callable callback, got:  %s"""%(function,))
		def wrap( *args ):
			"""Just return the original object for polygon_data"""
			args = args[:-1] + ( self.originalObject(args[-1]), )
			try:
				return function( *args )
			except Exception, err:
				err.args += (function,args)
				raise
		return wrap
	def dataWrapper2( self, function ):
		"""Wrap a function which has two data-pointers as last args"""
		if (function is not None) and (not callable( function )):
			raise TypeError( """Require a callable callback, got:  %s"""%(function,))
		def wrap( *args ):
			"""Just return the original object for polygon_data"""
			args = args[:-2] + ( self.originalObject(args[-2]), self.originalObject(args[-1]), )
			try:
				return function( *args )
			except Exception, err:
				err.args += (function,args)
				raise
		return wrap
	def vertexWrapper( self, function ):
		"""Converts a vertex-pointer into an OOR vertex for processing"""
		if (callable is not None) and (not callable( function )):
			raise TypeError( """Require a callable callback, got:  %s"""%(function,))
		def wrap( vertex, data=None ):
			"""Just return the original object for polygon_data"""
			vertex = self.originalObject(vertex)
			try:
				if data is not None:
					data = self.originalObject(data)
					return function( vertex, data )
				else:
					return function( vertex )
			except Exception, err:
				err.args += (function,(vertex,data))
				raise
		return wrap

GLUtesselator.CALLBACK_FUNCTION_REGISTRARS = dict([
	(c,createBaseFunction( 
		'gluTessCallback', dll=GLU, resultType=None, 
		argTypes=[ctypes.POINTER(GLUtesselator), simple.GLenum,funcType],
		doc='gluTessCallback( POINTER(GLUtesselator)(tess), GLenum(which), _GLUfuncptr(CallBackFunc) ) -> None', 
		argNames=('tess', 'which', 'CallBackFunc'),
	))
	for (c,funcType) in GLUtesselator.CALLBACK_TYPES.items()
])
del c, funcType

def gluTessCallback( tess, which, function ):
	"""Set a given gluTessellator callback for the given tessellator"""
	return tess.addCallback( which, function )
def gluTessBeginPolygon( tess, data ):
	"""Start definition of polygon in the tessellator"""
	return tess.gluTessBeginPolygon( data )
def gluTessVertex( tess, location, data=None ):
	"""Add a vertex to the tessellator's current polygon"""
	return tess.gluTessVertex( location, data )



# /usr/include/GL/glu.h 316
##gluTessCallbackBase = createBaseFunction( 
##	'gluTessCallback', dll=GLU, resultType=None, 
##	argTypes=[ctypes.POINTER(GLUtesselator), simple.GLenum,ctypes.CFUNCTYPE],
##	doc='gluTessCallback( POINTER(GLUtesselator)(tess), GLenum(which), _GLUfuncptr(CallBackFunc) ) -> None', 
##	argNames=('tess', 'which', 'CallBackFunc'),
##)
##gluTessBeginPolygonBase = createBaseFunction( 
##	'gluTessBeginPolygon', dll=GLU, resultType=None, 
##	argTypes=[ctypes.POINTER(GLUtesselator), ctypes.c_void_p],
##	doc='gluTessBeginPolygon( POINTER(GLUtesselator)(tess), _GLUfuncptr(CallBackFunc) ) -> None', 
##	argNames=('tess', 'CallBackFunc'),
##)

# /usr/include/GL/glu.h 294
gluNextContour = createBaseFunction( 
	'gluNextContour', dll=GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUtesselator), simple.GLenum],
	doc='gluNextContour( POINTER(GLUtesselator)(tess), GLenum(type) ) -> None', 
	argNames=('tess', 'type'),
)

# /usr/include/GL/glu.h 293
gluNewTessBase = createBaseFunction( 
	'gluNewTess', dll=GLU, resultType=ctypes.POINTER(GLUtesselator), 
	doc='gluNewTess(  ) -> POINTER(GLUtesselator)', 
)
def gluNewTess( ):
	"""Get a new tessellator object (just unpacks the pointer for you)"""
	return gluNewTessBase()[0]


# /usr/include/GL/glu.h 288
gluGetTessPropertyBase = createBaseFunction( 
	'gluGetTessProperty', dll=GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUtesselator), simple.GLenum, ctypes.POINTER(simple.GLdouble)],
	doc='gluGetTessProperty( POINTER(GLUtesselator)(tess), GLenum(which), POINTER(GLdouble)(data) ) -> None', 
	argNames=('tess', 'which', 'data'),
)
def gluGetTessProperty( tess, which, data=None ):
	"""Retrieve single double for a tessellator property"""
	if data is None:
		data = simple.GLdouble( 0.0 )
		gluGetTessPropertyBase( tess, which, data )
		return data.value 
	else:
		return gluGetTessPropertyBase( tess, which, data )

# /usr/include/GL/glu.h 282
gluEndPolygon = createBaseFunction( 
	'gluEndPolygon', dll=GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUtesselator)],
	doc='gluEndPolygon( POINTER(GLUtesselator)(tess) ) -> None (OBSOLETE see gluTessEndPolygon)', 
	argNames=('tess',),
)

# /usr/include/GL/glu.h 279
gluDeleteTess = createBaseFunction( 
	'gluDeleteTess', dll=GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUtesselator)],
	doc='gluDeleteTess( POINTER(GLUtesselator)(tess) ) -> None', 
	argNames=('tess',),
)


# /usr/include/GL/glu.h 321
gluTessVertexBase = createBaseFunction( 
	'gluTessVertex', dll=GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUtesselator), arrays.GLdoubleArray, ctypes.c_void_p],
	doc='gluTessVertex( POINTER(GLUtesselator)(tess), POINTER(GLdouble)(location), POINTER(GLvoid)(data) ) -> None', 
	argNames=('tess', 'location', 'data'),
)
gluTessVertexBase = arrays.setInputArraySizeType(
	gluTessVertexBase,
	3,
	arrays.GLdoubleArray,
	'location',
)

# /usr/include/GL/glu.h 266
gluBeginPolygon = createBaseFunction( 
	'gluBeginPolygon', dll=GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUtesselator)],
	doc='gluBeginPolygon( POINTER(GLUtesselator)(tess) ) -> None (OBSOLETE see gluTessBeginPolygon)', 
	argNames=('tess',),
)
# /usr/include/GL/glu.h 320
gluTessProperty = createBaseFunction( 
	'gluTessProperty', dll=GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUtesselator), simple.GLenum, simple.GLdouble],
	doc='gluTessProperty( POINTER(GLUtesselator)(tess), GLenum(which), GLdouble(data) ) -> None', 
	argNames=('tess', 'which', 'data'),
)
# /usr/include/GL/glu.h 319
gluTessNormal = createBaseFunction( 
	'gluTessNormal', dll=GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUtesselator), simple.GLdouble, simple.GLdouble, simple.GLdouble],
	doc='gluTessNormal( POINTER(GLUtesselator)(tess), GLdouble(valueX), GLdouble(valueY), GLdouble(valueZ) ) -> None', 
	argNames=('tess', 'valueX', 'valueY', 'valueZ'),
)

# /usr/include/GL/glu.h 318
gluTessEndPolygon = createBaseFunction( 
	'gluTessEndPolygon', dll=GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUtesselator)],
	doc='gluTessEndPolygon( POINTER(GLUtesselator)(tess) ) -> None', 
	argNames=('tess',),
)

# /usr/include/GL/glu.h 317
gluTessEndContour = createBaseFunction( 
	'gluTessEndContour', dll=GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUtesselator)],
	doc='gluTessEndContour( POINTER(GLUtesselator)(tess) ) -> None', 
	argNames=('tess',),
)

# /usr/include/GL/glu.h 315
gluTessBeginPolygonBase = createBaseFunction( 
	'gluTessBeginPolygon', dll=GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUtesselator), ctypes.c_void_p],
	doc='gluTessBeginPolygon( POINTER(GLUtesselator)(tess), POINTER(GLvoid)(data) ) -> None', 
	argNames=('tess', 'data'),
)

# /usr/include/GL/glu.h 314
gluTessBeginContour = createBaseFunction( 
	'gluTessBeginContour', dll=GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUtesselator)],
	doc='gluTessBeginContour( POINTER(GLUtesselator)(tess) ) -> None', 
	argNames=('tess',),
)
