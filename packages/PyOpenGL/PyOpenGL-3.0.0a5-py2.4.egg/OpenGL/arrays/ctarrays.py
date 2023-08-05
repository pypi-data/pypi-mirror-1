"""ctypes native array implementation of array interfaces"""
import operator, ctypes
from OpenGL import constants, constant
from OpenGL.arrays import formathandler

def dataPointer( ctArray ):
	"""Retrieve the data pointer for the array/pointer"""
	return ctArray
	
GL_TYPE_TO_ARRAY_MAPPING = {
	constants.GL_DOUBLE: simple.gldouble,
	constants.GL_FLOAT:simple.glfloat,
	constants.GL_INT: simple.glint,
	constants.GL_UNSIGNED_INT: simple.gluint,
	constants.GL_UNSIGNED_BYTE: simple.glubyte,
	constants.GL_SHORT: simple.glshort,
	constants.GL_UNSIGNED_SHORT: simple.glushort,
	constants.GL_BYTE: simple.glbyte,
}

class CTypesHandler( formathandler.FormatHandler ):
	"""Numeric-specific data-type handler for OpenGL"""
	from_param = staticmethod( dataPointer )
	dataPointer = staticmethod( dataPointer )
	def voidDataPointer( cls, value ):
		"""Given value in a known data-pointer type, return void_p for pointer"""
		return ctypes.c_void_p( self.dataPointer( value ))
	def zeros( self, dims, typeCode ):
		"""Return Numpy array of zeros in given size"""
		type = GL_TYPE_TO_ARRAY_MAPPING[ typeCode ]
		for d in dims:
			type *= d 
		return type() # how to init to 0?
	def ones( self, dims, typeCode='d' ):
		"""Return numpy array of ones in given size"""
		return numpy.ones( dims, GL_TYPE_TO_ARRAY_MAPPING.get(typeCode) or typeCode )
	def arrayToGLType( self, value ):
		"""Given a value, guess OpenGL type of the corresponding pointer"""
		typecode = value.dtype.char
		constant = ARRAY_TO_GL_TYPE_MAPPING.get( typecode )
		if constant is None:
			raise TypeError(
				"""Don't know GL type for array of type %r, known types: %s\nvalue:%s"""%(
					typecode, ARRAY_TO_GL_TYPE_MAPPING.keys(), value,
				)
			)
		return constant
	def arraySize( self, value, typeCode = None ):
		"""Given a data-value, calculate dimensions for the array"""
		try:
			dimValue = value.shape
		except AttributeError, err:
			# XXX it's a list or a tuple, how do we determine dimensions there???
			# for now we'll just punt and convert to an array first...
			value = self.asArray( value, typeCode )
			dimValue = value.shape 
		dims = 1
		for dim in dimValue:
			dims *= dim 
		return dims 
	def asArray( self, value, typecode=None ):
		"""Convert given value to an array value of given typecode"""
		if value is None:
			return value
		else:
			return self.contiguous( value, typecode )

	def contiguous( self, source, typecode=None ):
		"""Get contiguous array from source
		
		source -- numpy Python array (or compatible object)
			for use as the data source.  If this is not a contiguous
			array of the given typecode, a copy will be made, 
			otherwise will just be returned unchanged.
		typecode -- optional 1-character typecode specifier for
			the numpy.array function.
			
		All gl*Pointer calls should use contiguous arrays, as non-
		contiguous arrays will be re-copied on every rendering pass.
		Although this doesn't raise an error, it does tend to slow
		down rendering.
		"""
		typecode = GL_TYPE_TO_ARRAY_MAPPING[ typecode ]
		if isinstance( source, numpy.ArrayType):
			if source.flags.contiguous and (typecode is None or typecode==source.dtype.char):
				return source
			else:
				# We have to do astype to avoid errors about unsafe conversions
				# XXX Confirm that this will *always* create a new contiguous array 
				# XXX Allow a way to make this raise an error for performance reasons
				# XXX Guard against wacky conversion types like uint to float, where
				# we really don't want to have the C-level conversion occur.
				return numpy.array( source.astype( typecode ), typecode )
		elif typecode:
			return numpy.array( source, typecode )
		else:
			return numpy.array( source )
	def unitSize( self, value, typeCode=None ):
		"""Determine unit size of an array (if possible)"""
		return value.shape[1]
	def dimensions( self, value, typeCode=None ):
		"""Determine dimensions of the passed array value (if possible)"""
		return value.shape


ARRAY_TO_GL_TYPE_MAPPING = {
	'd': constants.GL_DOUBLE,
	'f': constants.GL_FLOAT,
	'i': constants.GL_INT,
	's': constants.GL_SHORT,
	'c': constants.GL_UNSIGNED_BYTE,
	'b': constants.GL_BYTE,
	'I': constants.GL_UNSIGNED_INT,
}
GL_TYPE_TO_ARRAY_MAPPING = {
	constants.GL_DOUBLE: 'd',
	constants.GL_FLOAT:'f',
	constants.GL_INT: 'i',
	constants.GL_UNSIGNED_INT: 'i',
	constants.GL_UNSIGNED_BYTE: 'b',
	constants.GL_SHORT: 's',
	constants.GL_UNSIGNED_SHORT: 's',
	constants.GL_BYTE: 'b',
}

HANDLER = NumpyHandler()
HANDLER.register( (numpy.ArrayType, list, tuple ) )
if not HANDLER.RETURN_HANDLER:
	# XXX no, do this at the top level, don't default to Numpy!
	import OpenGL
	if not OpenGL.preferredNumpy() or OpenGL.preferredNumpy() is numpy:
		OpenGL.preferredNumpy( numpy )
		HANDLER.registerReturn()
