"""GLX (x-windows)-specific platform features"""
import ctypes
from OpenGL.platform import ctypesloader

assert hasattr( ctypes, 'RTLD_GLOBAL' ), """Old ctypes without ability to load .so for global resolution: Get ctypes CVS branch_1_0, not CVS HEAD or released versions!"""
__all__ = (
	'EXT_DEFINES_PROTO',
	'HAS_DYNAMIC_EXT',
	'GL', 'OpenGL',
	'GLU',
	'GLUT',
	'GLE',
	'GLX',
	'FunctionType',
	'GetCurrentContext',
	'CurrentContextIsValid',
	'getGLUTFontPointer',
	'getExtensionProcedure',
	'safeGetError',
)

# On Linux (and, I assume, most GLX platforms, we have to load 
# GL and GLU with the "global" flag to allow GLUT to resolve its
# references to GL/GLU functions).

GL = OpenGL = ctypesloader.loadLibrary(
	ctypes.cdll,
	'GL', 
	mode=ctypes.RTLD_GLOBAL 
)
GLU = ctypesloader.loadLibrary(
	ctypes.cdll,
	'GLU',
	mode=ctypes.RTLD_GLOBAL 
)
# glut shouldn't need to be global, but just in case a dependent library makes
# the same assumption GLUT does...
GLUT = ctypesloader.loadLibrary(
	ctypes.cdll,
	'glut', 
	mode=ctypes.RTLD_GLOBAL 
)
# GLX doesn't seem to have its own loadable module?
GLX = GL
try:
	GLE = ctypesloader.loadLibrary(
		ctypes.cdll,
		'gle', 
		mode=ctypes.RTLD_GLOBAL 
	)
except OSError, err:
	GLE = None

FunctionType = ctypes.CFUNCTYPE

# This loads the GLX functions from the GL .so, not sure if that's
# really kosher...
GetCurrentContext = CurrentContextIsValid = GL.glXGetCurrentContext

# These are normally looked up via a define... don't know where to get it live...
EXT_DEFINES_PROTO = True
HAS_DYNAMIC_EXT = True

glXGetProcAddressARB = GL.glXGetProcAddressARB
glXGetProcAddressARB.restype = ctypes.c_void_p

def getGLUTFontPointer( constant ):
	"""Platform specific function to retrieve a GLUT font pointer
	
	GLUTAPI void *glutBitmap9By15;
	#define GLUT_BITMAP_9_BY_15		(&glutBitmap9By15)
	
	Key here is that we want the addressof the pointer in the DLL,
	not the pointer in the DLL.  That is, our pointer is to the 
	pointer defined in the DLL, we don't want the *value* stored in
	that pointer.
	"""
	name = [ x.title() for x in constant.split( '_' )[1:] ]
	internal = 'glut' + "".join( [x.title() for x in name] )
	pointer = ctypes.c_void_p.in_dll( GLUT, internal )
	return ctypes.c_void_p(ctypes.addressof(pointer))

def getExtensionProcedure( name ):
	"""Retrieve void * to named extension procedure"""
	# XXX how do we turn this into a ctypes function object?
	return glXGetProcAddressARB(name)
	
safeGetError = OpenGL.glGetError

if __name__ == "__main__":
	print 'GL', GL
	print 'GLU', GLU 
	print 'GLUT', GLUT
	print 'FunctionType', FunctionType
	print 'CurrentContext', GetCurrentContext()
