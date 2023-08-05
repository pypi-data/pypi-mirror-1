"""Implementation of OpenGL constant objects"""
import sys

class Constant( object ):
	"""OpenGL constant that displays itself as a name rather than a value
	
	The purpose of this class is to make debugging OpenGL code easier,
	as you recieve messages that say what value you passed in in a 
	human-readable form, rather than as a bald number that requires
	lookup and disambiguation in the header file.
	"""
	def __new__( cls, name, value ):
		"""Initialise the constant with the given name and value"""
		if isinstance( value, float ) and cls is not FloatConstant:
			return FloatConstant( name, value )
		elif isinstance( value, (int,long) ) and cls is not IntConstant:
			return IntConstant( name, value )
		elif isinstance( value, (str,unicode) ) and cls is not StringConstant:
			return StringConstant( name, str(value) )
		if isinstance( value, long ):
			if value > sys.maxint:
				value = - (value & sys.maxint)
		base = super(Constant,cls).__new__( cls, value )
		base.name = name 
		return base
	def __repr__( self ):
		"""Return the name, rather than the bald value"""
		return self.name 
	def __str__( self ):
		"""Return the value as a human-friendly string"""
		return '%s (%s)'%(self.name,super(Constant,self).__str__())

class IntConstant( Constant, int ):
	"""Integer constant sub-class"""
	__slots__ = ('name',)
class FloatConstant( Constant, float ):
	"""Float constant sub-class"""
	__slots__ = ('name',)
class StringConstant( Constant, str ):
	"""Float constant sub-class"""
