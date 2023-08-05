"""Windows-specific platform features"""
import ctypes
from OpenGL.platform import ctypesloader
__all__ = (
	'EXT_DEFINES_PROTO',
	'HAS_DYNAMIC_EXT',
	'OpenGL',
	'GL',
	'GLU',
	'GLUT',
	'GLE',
	'WGL',
	'FunctionType',
	'GetCurrentContext',
	'CurrentContextIsValid',
	'getExtensionProcedure',
	'getGLUTFontPointer',
	'safeGetError',
	'GLUT_GUARD_CALLBACKS',
)
EXT_DEFINES_PROTO = False
HAS_DYNAMIC_EXT = True
GLUT_GUARD_CALLBACKS = True
GL = OpenGL = ctypesloader.loadLibrary( ctypes.windll, 'opengl32', mode = ctypes.RTLD_GLOBAL )
GLU = ctypesloader.loadLibrary( ctypes.windll, 'glu32', mode = ctypes.RTLD_GLOBAL )
try:
	GLUT = ctypesloader.loadLibrary( ctypes.windll, 'glut32', mode = ctypes.RTLD_GLOBAL )
except WindowsError, err:
	GLUT = None
GLE = GLUT
FunctionType = ctypes.WINFUNCTYPE
WGL = ctypes.windll.gdi32

GLUT_FONT_CONSTANTS = {
	'GLUT_STROKE_ROMAN': ctypes.c_void_p( 0),
	'GLUT_STROKE_MONO_ROMAN': ctypes.c_void_p( 1),
	'GLUT_BITMAP_9_BY_15': ctypes.c_void_p( 2),
	'GLUT_BITMAP_8_BY_13': ctypes.c_void_p( 3),
	'GLUT_BITMAP_TIMES_ROMAN_10': ctypes.c_void_p( 4),
	'GLUT_BITMAP_TIMES_ROMAN_24': ctypes.c_void_p( 5),
	'GLUT_BITMAP_HELVETICA_10': ctypes.c_void_p( 6),
	'GLUT_BITMAP_HELVETICA_12': ctypes.c_void_p( 7),
	'GLUT_BITMAP_HELVETICA_18': ctypes.c_void_p( 8),
}


def getGLUTFontPointer( constant ):
	"""Platform specific function to retrieve a GLUT font pointer
	
	GLUTAPI void *glutBitmap9By15;
	#define GLUT_BITMAP_9_BY_15		(&glutBitmap9By15)
	
	Key here is that we want the addressof the pointer in the DLL,
	not the pointer in the DLL.  That is, our pointer is to the 
	pointer defined in the DLL, we don't want the *value* stored in
	that pointer.
	"""
	return GLUT_FONT_CONSTANTS[ constant ]
def getExtensionProcedure( name ):
	"""Retrieve void * to named extension procedure"""
	return OpenGL.wglGetProcAddress(name)

GetCurrentContext = CurrentContextIsValid = GL.wglGetCurrentContext

glGetError =  OpenGL.glGetError
def safeGetError( ):
	"""Provide context-not-present-safe error-checking
	
	Under OS-X an attempt to retrieve error without checking 
	context will bus-error.  Likely Windows will see the same.
	This function checks for a valid context before running 
	glGetError
	
	Note:
		This is a likely candidate for rewriting in C, as it
		is called for every almost function in the system!
	"""
	if CurrentContextIsValid():
		return glGetError()
	return None
