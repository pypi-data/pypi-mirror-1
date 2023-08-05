"""Abstraction for the platform-specific code in PyOpenGL

Eventually there will likely be enough code here to warrant
having separate modules for each platform.  Then we may load
them using sys.platform to construct the module name in order
to allow for easy extensions for new platforms.

GLUT_GUARD_CALLBACKS -- if True, all GLUT callbacks are wrapped
	with code to check for errors and exit if there is a failure
	in the callback...
"""
import ctypes
import sys

GLUT_GUARD_CALLBACKS = False
EXTENSIONS_USE_BASE_FUNCTIONS = False

if sys.platform == 'win32':
	from OpenGL.platform.win32 import *
# Apple, DOS, symbian, or any other platform in here somewhere...
elif sys.platform == 'darwin':
	from OpenGL.platform.darwin import *
else:
	from OpenGL.platform.glx import *

def createBaseFunction( 
	functionName, dll=OpenGL, 
	resultType=ctypes.c_int, argTypes=(),
	doc = None, argNames = (),
):
	"""Create a base function for given name
	
	Normally you can just use the dll.name hook to get the object,
	but we want to be able to create different bindings for the 
	same function, so we do the work manually here to produce a
	base function from a DLL.
	"""
	from OpenGL import wrapper, error
	try:
		func = ctypesloader.buildFunction(
			FunctionType(
				resultType,
				*argTypes
			),
			functionName,
			dll,
		)
	except AttributeError, err:
		return nullFunction( 
			functionName, dll=dll,
			resultType=resultType, 
			argTypes=argTypes,
			doc = doc, argNames = argNames,
		)
	else:
		func.__doc__ = doc 
		func.argNames = list(argNames or ())
		func.__name__ = functionName
		func.DLL = dll
		func.errcheck = error.glCheckError
		return func
if EXTENSIONS_USE_BASE_FUNCTIONS:
	createExtensionFunction = createBaseFunction
else:
	def createExtensionFunction( 
		functionName, dll=OpenGL,
		resultType=ctypes.c_int, 
		argTypes=(),
		doc = None, argNames = (),
	):
		"""Create an extension function for the given name
		
		Uses the platform's getExtensionProcedure function to retrieve
		a c_void_p to the function, then wraps in a platform FunctionType
		instance with all the funky code we've come to love.
		"""
		from OpenGL import wrapper, error
		# XXX need to catch errors!
		pointer = getExtensionProcedure( functionName )
		if not pointer:
			return nullFunction( 
				functionName, dll,
				resultType, 
				argTypes,
				doc, argNames,
			)
		func = FunctionType(
			resultType,
			*argTypes
		)(
			pointer
		)
		func.__doc__ = doc 
		func.argNames = list(argNames or ())
		func.__name__ = functionName
		func.DLL = dll
		func.errcheck = error.glCheckError
		return func

def copyBaseFunction( original ):
	"""Create a new base function based on an already-created function
	
	This is normally used to provide type-specific convenience versions of
	a definition created by the automated generator.
	"""
	from OpenGL import wrapper, error
	if isinstance( original, _NullFunctionPointer ):
		return nullFunction(
			original.__name__,
			original.DLL,
			resultType = original.restype,
			argTypes= original.argtypes,
			doc = original.__doc__,
			argNames = original.argNames,
		)
	func = FunctionType(
		original.restype,
		*original.argtypes
	)(
		original.__name__,
		original.DLL,
	)
	func.__doc__ = original.__doc__
	func.argNames = original.argNames 
	func.__name__ = original.__name__
	func.errcheck = error.glCheckError
	return func

def init_extension( name ):
	"""Check whether the given extension exists"""

class _NullFunctionPointer( object ):
	"""Function-pointer-like object for undefined functions"""
	def __init__( self, name, dll, resultType, argTypes, argNames ):
		from OpenGL import error
		self.__name__ = name
		self.DLL = dll
		self.argNames = argNames
		self.argtypes = argTypes
		self.errcheck = error.glCheckError
		self.restype = resultType
	def __nonzero__( self ):
		"""Make this object appear to be NULL"""
		return False
	def __call__( self, *args, **named ):
		from OpenGL import error
		raise error.NullFunctionError(
			"""Attempt to call an undefined function %s, check for bool(%s) before calling"""%(
				self.__name__, self.__name__,
			)
		)
def nullFunction( 
	functionName, dll=OpenGL,
	resultType=ctypes.c_int, 
	argTypes=(),
	doc = None, argNames = (),
):
	"""Construct a "null" function pointer"""
	cls = type( functionName, (_NullFunctionPointer,), {
		'__doc__': doc,
	} )
	return cls(
		functionName, dll, resultType, argTypes, argNames
	)
	
