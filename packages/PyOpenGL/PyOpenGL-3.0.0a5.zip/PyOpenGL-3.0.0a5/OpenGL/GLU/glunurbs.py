"""Implementation of GLU Nurbs structure and callback methods

Same basic pattern as seen with the gluTess* functions, just need to
add some bookkeeping to the structure class so that we can keep the
Python function references alive during the calling process.
"""
from OpenGL.raw import GLU as simple
from OpenGL import platform, converters, wrapper
from OpenGL.GLU import glustruct
from OpenGL import arrays
import ctypes
import weakref

__all__ = (
	'GLUnurbs',
	'gluBeginCurve',
	'gluBeginSurface',
	'gluBeginTrim',
	'gluDeleteNurbsRenderer',
	'gluEndCurve',
	'gluEndSurface',
	'gluEndTrim',
	'gluGetNurbsProperty',
	'gluLoadSamplingMatrices',
	'gluNewNurbsRenderer',
	'gluNurbsCallback',
	'gluNurbsCallbackData',
	'gluNurbsCallbackDataEXT',
	'gluNurbsCurve',
	'gluNurbsProperty',
	'gluNurbsSurface',
	'gluPwlCurve',
)

# /usr/include/GL/glu.h 242
class GLUnurbs(glustruct.GLUStruct):
	"""GLU Nurbs structure with oor and callback storage support
	
	IMPORTANT NOTE: the texture coordinate callback receives a raw ctypes 
	data-pointer, as without knowing what type of evaluation is being done 
	(1D or 2D) we cannot safely determine the size of the array to convert 
	it.  This is a limitation of the C implementation.  To convert to regular 
	data-pointer, just call yourNurb.ptrAsArray( ptr, size, arrays.GLfloatArray )
	with the size of data you expect.
	"""
	CALLBACK_TYPES = {
		# mapping from "which" GLU enumeration to a ctypes function type
		simple.GLU_NURBS_BEGIN: ctypes.CFUNCTYPE( 
			None, simple.GLenum 
		),
		simple.GLU_NURBS_BEGIN_DATA: ctypes.CFUNCTYPE( 
			None, simple.GLenum, ctypes.POINTER(simple.GLvoid) 
		),
		simple.GLU_NURBS_VERTEX: ctypes.CFUNCTYPE( 
			None, ctypes.POINTER(simple.GLfloat)
		),
		simple.GLU_NURBS_VERTEX_DATA: ctypes.CFUNCTYPE( 
			None, ctypes.POINTER(simple.GLfloat), ctypes.POINTER(simple.GLvoid) 
		),
		simple.GLU_NURBS_NORMAL: ctypes.CFUNCTYPE( 
			None, ctypes.POINTER(simple.GLfloat)
		),
		simple.GLU_NURBS_NORMAL_DATA: ctypes.CFUNCTYPE( 
			None, ctypes.POINTER(simple.GLfloat), ctypes.POINTER(simple.GLvoid) 
		),
		simple.GLU_NURBS_COLOR: ctypes.CFUNCTYPE( 
			None, ctypes.POINTER(simple.GLfloat)
		),
		simple.GLU_NURBS_COLOR_DATA: ctypes.CFUNCTYPE( 
			None, ctypes.POINTER(simple.GLfloat), ctypes.POINTER(simple.GLvoid) 
		),
		simple.GLU_NURBS_TEXTURE_COORD: ctypes.CFUNCTYPE( 
			None, ctypes.POINTER(simple.GLfloat)
		),
		simple.GLU_NURBS_TEXTURE_COORD_DATA: ctypes.CFUNCTYPE( 
			None, ctypes.POINTER(simple.GLfloat), ctypes.POINTER(simple.GLvoid) 
		),
		simple.GLU_NURBS_END:ctypes.CFUNCTYPE( 
			None
		),
		simple.GLU_NURBS_END_DATA: ctypes.CFUNCTYPE( 
			None, ctypes.POINTER(simple.GLvoid) 
		),
		simple.GLU_NURBS_ERROR:ctypes.CFUNCTYPE( 
			None, simple.GLenum, 
		),
	}
	WRAPPER_METHODS = {
		simple.GLU_NURBS_BEGIN: None,
		simple.GLU_NURBS_BEGIN_DATA: '_justOOR',
		simple.GLU_NURBS_VERTEX: '_vec3',
		simple.GLU_NURBS_VERTEX_DATA: '_vec3',
		simple.GLU_NURBS_NORMAL: '_vec3',
		simple.GLU_NURBS_NORMAL_DATA: '_vec3',
		simple.GLU_NURBS_COLOR: '_vec4',
		simple.GLU_NURBS_COLOR_DATA: '_vec4',
		simple.GLU_NURBS_TEXTURE_COORD: '_tex',
		simple.GLU_NURBS_TEXTURE_COORD_DATA: '_tex',
		simple.GLU_NURBS_END: None,
		simple.GLU_NURBS_END_DATA: '_justOOR',
		simple.GLU_NURBS_ERROR: None,
	}
	def _justOOR( self, function ):
		"""Just do OOR on the last argument..."""
		def getOOR( *args ):
			args = args[:-1] + (self.originalObject(args[-1]),)
			return function( *args )
		return getOOR
	def _vec3( self, function, size=3 ):
		"""Convert first arg to size-element array, do OOR on arg2 if present"""
		def vec( *args ):
			vec = self.ptrAsArray(args[0],size,arrays.GLfloatArray)
			if len(args) > 1:
				oor = self.originalObject(args[1])
				return function( vec, oor )
			else:
				return function( vec )
		return vec
	def _vec4( self, function ):
		"""Size-4 vector version..."""
		return self._vec3( function, 4 )
	def _tex( self, function ):
		"""Texture coordinate callback 
		
		NOTE: there is no way for *us* to tell what size the array is, you will 
		get back a raw data-point, not an array, as you do for all other callback 
		types!!!
		"""
		def oor( *args ):
			if len(args) > 1:
				oor = self.originalObject(args[1])
				return function( args[0], oor )
			else:
				return function( args[0] )
		return oor

GLUnurbs.CALLBACK_FUNCTION_REGISTRARS = dict([
	(c,platform.createBaseFunction( 
		'gluNurbsCallback', dll=platform.GLU, resultType=None, 
		argTypes=[ctypes.POINTER(GLUnurbs), simple.GLenum, funcType],
		doc='gluNurbsCallback( POINTER(GLUnurbs)(nurb), GLenum(which), _GLUfuncptr(CallBackFunc) ) -> None', 
		argNames=('nurb', 'which', 'CallBackFunc'),
	))
	for (c,funcType) in GLUnurbs.CALLBACK_TYPES.items()
])
del c, funcType


def gluNurbsCallback( nurb, which, CallBackFunc ):
	"""Dispatch to the nurb's callback operation"""
	return nurb.addCallback( which, CallBackFunc )

# /usr/include/GL/glu.h 265
gluBeginCurve = platform.createBaseFunction( 
	'gluBeginCurve', dll=platform.GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUnurbs)],
	doc='gluBeginCurve( POINTER(GLUnurbs)(nurb) ) -> None', 
	argNames=('nurb',),
)
# /usr/include/GL/glu.h 267
gluBeginSurface = platform.createBaseFunction( 
	'gluBeginSurface', dll=platform.GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUnurbs)],
	doc='gluBeginSurface( POINTER(GLUnurbs)(nurb) ) -> None', 
	argNames=('nurb',),
)

# /usr/include/GL/glu.h 268
gluBeginTrim = platform.createBaseFunction( 
	'gluBeginTrim', dll=platform.GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUnurbs)],
	doc='gluBeginTrim( POINTER(GLUnurbs)(nurb) ) -> None', 
	argNames=('nurb',),
)

# /usr/include/GL/glu.h 277
gluDeleteNurbsRenderer = platform.createBaseFunction( 
	'gluDeleteNurbsRenderer', dll=platform.GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUnurbs)],
	doc='gluDeleteNurbsRenderer( POINTER(GLUnurbs)(nurb) ) -> None', 
	argNames=('nurb',),
)
# /usr/include/GL/glu.h 281
gluEndCurve = platform.createBaseFunction( 
	'gluEndCurve', dll=platform.GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUnurbs)],
	doc='gluEndCurve( POINTER(GLUnurbs)(nurb) ) -> None', 
	argNames=('nurb',),
)
# /usr/include/GL/glu.h 283
gluEndSurface = platform.createBaseFunction( 
	'gluEndSurface', dll=platform.GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUnurbs)],
	doc='gluEndSurface( POINTER(GLUnurbs)(nurb) ) -> None', 
	argNames=('nurb',),
)

# /usr/include/GL/glu.h 284
gluEndTrim = platform.createBaseFunction( 
	'gluEndTrim', dll=platform.GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUnurbs)],
	doc='gluEndTrim( POINTER(GLUnurbs)(nurb) ) -> None', 
	argNames=('nurb',),
)
# /usr/include/GL/glu.h 286
basegluGetNurbsProperty = platform.createBaseFunction( 
	'gluGetNurbsProperty', dll=platform.GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUnurbs), simple.GLenum, arrays.GLfloatArray],
	doc='gluGetNurbsProperty( POINTER(GLUnurbs)(nurb), GLenum(property), arrays.GLfloatArray(data) ) -> None', 
	argNames=('nurb', 'property', 'data'),
)
def gluGetNurbsProperty( nurb, property ):
	"""Retrieve the indicated property for the given NURB object"""
	output = simple.GLfloat( 0.0 )
	value = basegluGetNurbsProperty( nurb, property, ctypes.byref(output) )
	return output.value

# /usr/include/GL/glu.h 289
gluLoadSamplingMatrices = platform.createBaseFunction( 
	'gluLoadSamplingMatrices', dll=platform.GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUnurbs), arrays.GLfloatArray, arrays.GLfloatArray, arrays.GLintArray],
	doc='gluLoadSamplingMatrices( POINTER(GLUnurbs)(nurb), arrays.GLfloatArray(model), arrays.GLfloatArray(perspective), arrays.GLintArray(view) ) -> None', 
	argNames=('nurb', 'model', 'perspective', 'view'),
)

gluLoadSamplingMatrices = arrays.setInputArraySizeType(
	gluLoadSamplingMatrices,
	None, # XXX Could not determine size of argument model for gluLoadSamplingMatrices arrays.GLfloatArray
	arrays.GLfloatArray, 
	'model',
)

gluLoadSamplingMatrices = arrays.setInputArraySizeType(
	gluLoadSamplingMatrices,
	None, # XXX Could not determine size of argument perspective for gluLoadSamplingMatrices arrays.GLfloatArray
	arrays.GLfloatArray, 
	'perspective',
)

gluLoadSamplingMatrices = arrays.setInputArraySizeType(
	gluLoadSamplingMatrices,
	None, # XXX Could not determine size of argument view for gluLoadSamplingMatrices arrays.GLintArray
	arrays.GLintArray, 
	'view',
)
# /usr/include/GL/glu.h 291
basegluNewNurbsRenderer = platform.createBaseFunction( 
	'gluNewNurbsRenderer', dll=platform.GLU, resultType=ctypes.POINTER(GLUnurbs), 
	argTypes=[],
	doc='gluNewNurbsRenderer(  ) -> POINTER(GLUnurbs)', 
	argNames=(),
)
def gluNewNurbsRenderer( ):
	"""Return a new nurbs renderer for the system (dereferences pointer)"""
	return basegluNewNurbsRenderer()[0]

# /usr/include/GL/glu.h 296
basegluNurbsCallbackData = platform.createBaseFunction( 
	'gluNurbsCallbackData', dll=platform.GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUnurbs), ctypes.POINTER(simple.GLvoid)],
	doc='gluNurbsCallbackData( POINTER(GLUnurbs)(nurb), POINTER(GLvoid)(userData) ) -> None', 
	argNames=('nurb', 'userData'),
)
def gluNurbsCallbackData( nurb, userData ):
	"""Note the Python object for use as userData by the nurb"""
	return basegluNurbsCallbackData( nurb, nurb.noteObject( userData ) )

# /usr/include/GL/glu.h 297
basegluNurbsCallbackDataEXT = platform.createBaseFunction( 
	'gluNurbsCallbackDataEXT', dll=platform.GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUnurbs), ctypes.POINTER(simple.GLvoid)],
	doc='gluNurbsCallbackDataEXT( POINTER(GLUnurbs)(nurb), POINTER(GLvoid)(userData) ) -> None', 
	argNames=('nurb', 'userData'),
)
def gluNurbsCallbackDataEXT( nurb, userData ):
	"""Note the Python object for use as userData by the nurb"""
	return basegluNurbsCallbackDataEXT( nurb, nurb.noteObject( userData ) )

# /usr/include/GL/glu.h 298
basegluNurbsCurve = platform.createBaseFunction( 
	'gluNurbsCurve', dll=platform.GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUnurbs), simple.GLint, arrays.GLfloatArray, simple.GLint, arrays.GLfloatArray, simple.GLint, simple.GLenum],
	doc='gluNurbsCurve( POINTER(GLUnurbs)(nurb), GLint(knotCount), arrays.GLfloatArray(knots), GLint(stride), arrays.GLfloatArray(control), GLint(order), GLenum(type) ) -> None', 
	argNames=('nurb', 'knotCount', 'knots', 'stride', 'control', 'order', 'type'),
)

def gluNurbsCurve( nurb, knots, control, type ):
	"""Pythonic version of gluNurbsCurve
	
	Calculates knotCount, stride, and order automatically
	"""
	knots = arrays.GLfloatArray.asArray( knots )
	knotCount = arrays.GLfloatArray.arraySize( knots )
	control = arrays.GLfloatArray.asArray( control )
	length,step = arrays.GLfloatArray.dimensions( control )
	order = knotCount - length
	return basegluNurbsCurve(
		nurb, knotCount, knots, step, control, order, type,
	)

# /usr/include/GL/glu.h 299
gluNurbsProperty = platform.createBaseFunction( 
	'gluNurbsProperty', dll=platform.GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUnurbs), simple.GLenum, simple.GLfloat],
	doc='gluNurbsProperty( POINTER(GLUnurbs)(nurb), GLenum(property), GLfloat(value) ) -> None', 
	argNames=('nurb', 'property', 'value'),
)

# /usr/include/GL/glu.h 300
basegluNurbsSurface = platform.createBaseFunction( 
	'gluNurbsSurface', dll=platform.GLU, resultType=None, 
	argTypes=[
		ctypes.POINTER(GLUnurbs), 
		simple.GLint, arrays.GLfloatArray, 
		simple.GLint, arrays.GLfloatArray, 
		simple.GLint, simple.GLint, arrays.GLfloatArray, 
		simple.GLint, simple.GLint, simple.GLenum
	],
	doc='gluNurbsSurface( POINTER(GLUnurbs)(nurb), GLint(sKnotCount), arrays.GLfloatArray(sKnots), GLint(tKnotCount), arrays.GLfloatArray(tKnots), GLint(sStride), GLint(tStride), arrays.GLfloatArray(control), GLint(sOrder), GLint(tOrder), GLenum(type) ) -> None', 
	argNames=('nurb', 'sKnotCount', 'sKnots', 'tKnotCount', 'tKnots', 'sStride', 'tStride', 'control', 'sOrder', 'tOrder', 'type'),
)
def gluNurbsSurface( nurb, sKnots, tKnots, control, type ):
	"""Pythonic version of gluNurbsSurface
	
	Calculates knotCount, stride, and order automatically
	"""
	sKnots = arrays.GLfloatArray.asArray( sKnots )
	sKnotCount = arrays.GLfloatArray.arraySize( sKnots )
	tKnots = arrays.GLfloatArray.asArray( tKnots )
	tKnotCount = arrays.GLfloatArray.arraySize( tKnots )
	control = arrays.GLfloatArray.asArray( control )

	length,width,step = arrays.GLfloatArray.dimensions( control )
	sOrder = sKnotCount - length 
	tOrder = tKnotCount - width 
	sStride = width*step
	tStride = step
	
	assert (sKnotCount-sOrder)*(tKnotCount-tOrder) == length*width, (
		nurb, sKnotCount, sKnots, tKnotCount, tKnots,
		sStride, tStride, control,
		sOrder,tOrder,
		type
	)

	result = basegluNurbsSurface(
		nurb, sKnotCount, sKnots, tKnotCount, tKnots,
		sStride, tStride, control,
		sOrder,tOrder,
		type
	)
	return result

# /usr/include/GL/glu.h 306
basegluPwlCurve = platform.createBaseFunction( 
	'gluPwlCurve', dll=platform.GLU, resultType=None, 
	argTypes=[ctypes.POINTER(GLUnurbs), simple.GLint, arrays.GLfloatArray, simple.GLint, simple.GLenum],
	doc='gluPwlCurve( POINTER(GLUnurbs)(nurb), GLint(count), arrays.GLfloatArray(data), GLint(stride), GLenum(type) ) -> None', 
	argNames=('nurb', 'count', 'data', 'stride', 'type'),
)
def gluPwlCurve( nurb, data, type ):
	"""gluPwlCurve -- piece-wise linear curve within GLU context
	
	data -- the data-array 
	type -- determines number of elements/data-point
	"""
	data = arrays.GLfloatArray.asArray( data )
	if type == simple.GLU_MAP1_TRIM_2:
		divisor = 2
	elif type == simple.GLU_MAP_TRIM_3:
		divisor = 3
	else:
		raise ValueError( """Unrecognised type constant: %s"""%(type))
	size = arrays.GLfloatArray.arraySize( data )
	size = int(size/divisor)
	return basegluPwlCurve( nurb, size, data, divisor, type )
