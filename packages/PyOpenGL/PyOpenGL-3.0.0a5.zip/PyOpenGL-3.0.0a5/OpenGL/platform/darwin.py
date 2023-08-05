"""Darwin (MacOSX)-specific platform features

This was implemented with the help of the following links:
[1] Apple's Mac OS X OpenGL interfaces: http://developer.apple.com/qa/qa2001/qa1269.html
[2] As above, but updated: http://developer.apple.com/documentation/GraphicsImaging/Conceptual/OpenGL-MacProgGuide/opengl_pg_concepts/chapter_2_section_3.html
[3] CGL reference: http://developer.apple.com/documentation/GraphicsImaging/Reference/CGL_OpenGL/index.html#//apple_ref/doc/uid/TP40001186
[4] Intro to OpenGL on Mac OS X: http://developer.apple.com/documentation/GraphicsImaging/Conceptual/OpenGL-MacProgGuide/opengl_intro/chapter_1_section_1.html#//apple_ref/doc/uid/TP40001987-CH207-TP9

About the  CGL API, (from [1]):
CGL or Core OpenGL is the lowest accessible interface API for OpenGL. 
It knows nothing about windowing systems but can be used directly to 
find both renderer information and as a full screen or off screen 
interface. It is accessible from both Cocoa and Carbon and is what both 
NSGL and AGL are built on. A complete Pbuffer interface is also provided. 
Functionality is provided in via the OpenGL framework and applications 
can include the OpenGL.h header to access CGL's functionality. Developers
can see an example of using CGL with Carbon in the Carbon CGL code sample.

Documentation and header files are found in:
/System/Library/Frameworks/OpenGL.framework
/System/Library/Frameworks/GLUT.framework

"""
import ctypes, ctypes.util
from OpenGL.platform import ctypesloader

__all__ = (
	'EXT_DEFINES_PROTO',
	'HAS_DYNAMIC_EXT',
	'GL', 'OpenGL',
	'CGL',
	'GLE',
	'GLU',
	'GLUT',
	'FunctionType',
	'GetCurrentContext',
	'CurrentContextIsValid',
	'getGLUTFontPointer',
	'getExtensionProcedure',
	'safeGetError',
	'EXTENSIONS_USE_BASE_FUNCTIONS',
)

FunctionType = ctypes.CFUNCTYPE

OpenGL = ctypesloader.loadLibrary(
	ctypes.cdll,
	'OpenGL', 
	mode=ctypes.RTLD_GLOBAL 
)

# CGL provides the windowing environment functionality
# but it is built into the GL libs.
GL = GLU = CGL = OpenGL

# glut shouldn't need to be global, but just in case a dependent library makes
# the same assumption GLUT does...
GLUT = ctypesloader.loadLibrary(
	ctypes.cdll,
	'glut', 
	mode=ctypes.RTLD_GLOBAL 
)

# GLE is handled by GLUT under OS X
GLE = GLUT

GetCurrentContext = CurrentContextIsValid = CGL.CGLGetCurrentContext

# These are normally looked up via a define... don't know where to get it live...
EXT_DEFINES_PROTO = True
HAS_DYNAMIC_EXT = True
EXTENSIONS_USE_BASE_FUNCTIONS = True

def getGLUTFontPointer( constant ):
	"""Platform specific function to retrieve a GLUT font pointer
	
	GLUTAPI void *glutBitmap9By15;
	#define GLUT_BITMAP_9_BY_15     (&glutBitmap9By15)
	
	Key here is that we want the addressof the pointer in the DLL,
	not the pointer in the DLL.  That is, our pointer is to the 
	pointer defined in the DLL, we don't want the *value* stored in
	that pointer.
	"""
	name = [ x.title() for x in constant.split( '_' )[1:] ]
	internal = 'glut' + "".join( [x.title() for x in name] )
	pointer = ctypes.c_void_p.in_dll( GLUT, internal )
	return ctypes.c_void_p(ctypes.addressof(pointer))

syslib = ctypes.CDLL(ctypes.util.find_library('System'))

def getExtensionProcedure( name ):
	"""Retrieve void * to named extension procedure.
	Under OS X these functions are defining in the main GL library.
	This function is empty since in __init__.py we override it anyway"""
	pass

glGetError =  OpenGL.glGetError
def safeGetError( ):
	"""Provide context-not-present-safe error-checking
	
	Under OS-X an attempt to retrieve error without checking 
	context will bus-error.  This function checks for a valid
	context before running glGetError
	
	Note:
		This is a likely candidate for rewriting in C, as it
		is called for every almost function in the system!
	"""
	if CurrentContextIsValid():
		return glGetError()
	return None


if __name__ == "__main__":
	print 'GL', GL
	print 'GLU', GLU 
	print 'GLUT', GLUT
	print 'FunctionType', FunctionType
	print 'CurrentContext', GetCurrentContext()
