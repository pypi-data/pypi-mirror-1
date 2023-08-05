"""glu[Un]Project[4] convenience wrappers"""
from OpenGL.platform import GL,GLU,createBaseFunction
from OpenGL.GLU import simple
from OpenGL import GL, arrays
import ctypes 
POINTER = ctypes.POINTER

gluProjectBase = createBaseFunction( 
	'gluProject', dll=GLU, resultType=simple.GLint, 
	argTypes=[
		simple.GLdouble, simple.GLdouble, simple.GLdouble, 
		arrays.GLdoubleArray, arrays.GLdoubleArray, arrays.GLintArray, 
		POINTER( simple.GLdouble ),POINTER( simple.GLdouble ),POINTER( simple.GLdouble ), 
	],
	doc='gluProject( GLdouble(objX), GLdouble(objY), GLdouble(objZ), POINTER(GLdouble)(model), POINTER(GLdouble)(proj), POINTER(GLint)(view), POINTER(GLdouble)(winX), POINTER(GLdouble)(winY), POINTER(GLdouble)(winZ) ) -> GLint', 
	argNames=('objX', 'objY', 'objZ', 'model', 'proj', 'view', 'winX', 'winY', 'winZ'),
)
gluUnProjectBase = createBaseFunction( 
	'gluUnProject', dll=GLU, resultType=simple.GLint, 
	argTypes=[
		simple.GLdouble, simple.GLdouble, simple.GLdouble, 
		arrays.GLdoubleArray, arrays.GLdoubleArray, arrays.GLintArray, 
		POINTER( simple.GLdouble ),POINTER( simple.GLdouble ),POINTER( simple.GLdouble ), 
	],
	doc='gluUnProject( GLdouble(winX), GLdouble(winY), GLdouble(winZ), POINTER(GLdouble)(model), POINTER(GLdouble)(proj), POINTER(GLint)(view), POINTER(GLdouble)(objX), POINTER(GLdouble)(objY), POINTER(GLdouble)(objZ) ) -> GLint', 
	argNames=('winX', 'winY', 'winZ', 'model', 'proj', 'view', 'objX', 'objY', 'objZ'),
)
gluUnProject4Base = createBaseFunction( 
	'gluUnProject4', dll=GLU, resultType=simple.GLint, 
	argTypes=[
		simple.GLdouble, simple.GLdouble, simple.GLdouble, simple.GLdouble, 
		arrays.GLdoubleArray, arrays.GLdoubleArray, arrays.GLintArray, 
		simple.GLdouble, simple.GLdouble, 
		POINTER( simple.GLdouble ),POINTER( simple.GLdouble ),POINTER( simple.GLdouble ), POINTER( simple.GLdouble ), 
	],
	doc='gluUnProject4( GLdouble(winX), GLdouble(winY), GLdouble(winZ), GLdouble(clipW), POINTER(GLdouble)(model), POINTER(GLdouble)(proj), POINTER(GLint)(view), GLdouble(near), GLdouble(far), POINTER(GLdouble)(objX), POINTER(GLdouble)(objY), POINTER(GLdouble)(objZ), POINTER(GLdouble)(objW) ) -> GLint', 
	argNames=('winX', 'winY', 'winZ', 'clipW', 'model', 'proj', 'view', 'near', 'far', 'objX', 'objY', 'objZ', 'objW'),
)
def gluProject( objX, objY, objZ, model=None, proj=None, view=None ):
	"""Convenience wrapper for gluProject
	
	Automatically fills in the model, projection and viewing matrices
	if not provided.
	
	returns (winX,winY,winZ) doubles
	"""
	if model is None:
		model = GL.glGetDoublev( GL.GL_MODELVIEW_MATRIX )
	if proj is None:
		proj = GL.glGetDoublev( GL.GL_PROJECTION_MATRIX )
	if view is None:
		view = GL.glGetIntegerv( GL.GL_VIEWPORT )
	winX = simple.GLdouble( 0.0 )
	winY = simple.GLdouble( 0.0 )
	winZ = simple.GLdouble( 0.0 )
	result = gluProjectBase( 
		objX,objY,objZ,
		model,proj,view,
		ctypes.byref(winX),ctypes.byref(winY),ctypes.byref(winZ),
	)
	if not result:
		raise ValueError( """Projection failed!""" )
	return winX.value, winY.value, winZ.value 

def gluUnProject( winX, winY, winZ, model=None, proj=None, view=None ):
	"""Convenience wrapper for gluUnProject
	
	Automatically fills in the model, projection and viewing matrices
	if not provided.
	
	returns (objX,objY,objZ) doubles
	"""
	if model is None:
		model = GL.glGetDoublev( GL.GL_MODELVIEW_MATRIX )
	if proj is None:
		proj = GL.glGetDoublev( GL.GL_PROJECTION_MATRIX )
	if view is None:
		view = GL.glGetIntegerv( GL.GL_VIEWPORT )
	objX = simple.GLdouble( 0.0 )
	objY = simple.GLdouble( 0.0 )
	objZ = simple.GLdouble( 0.0 )
	result = gluUnProjectBase( 
		winX,winY,winZ,
		model,proj,view,
		ctypes.byref(objX),ctypes.byref(objY),ctypes.byref(objZ),
	)
	if not result:
		raise ValueError( """Projection failed!""" )
	return objX.value, objY.value, objZ.value 
def gluUnProject4( 
	winX, winY, winZ, clipW, 
	model=None, proj=None, view=None, 
	near=0.0, far=1.0
):
	"""Convenience wrapper for gluUnProject
	
	Automatically fills in the model, projection and viewing matrices
	if not provided.
	
	returns (objX,objY,objZ) doubles
	"""
	if model is None:
		model = GL.glGetDoublev( GL.GL_MODELVIEW_MATRIX )
	if proj is None:
		proj = GL.glGetDoublev( GL.GL_PROJECTION_MATRIX )
	if view is None:
		view = GL.glGetIntegerv( GL.GL_VIEWPORT )
	objX = simple.GLdouble( 0.0 )
	objY = simple.GLdouble( 0.0 )
	objZ = simple.GLdouble( 0.0 )
	objW = simple.GLdouble( 0.0 )
	result = gluUnProject4Base( 
		winX,winY,winZ,
		model,proj,view,
		ctypes.byref(objX),ctypes.byref(objY),ctypes.byref(objZ),ctypes.byref(objW)
	)
	if not result:
		raise ValueError( """Projection failed!""" )
	return objX.value, objY.value, objZ.value, objW.value
