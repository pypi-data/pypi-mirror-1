"""Dumb script to get the bulk of the OpenGL constants from gl.h

For some silly reason this doesn't happen with the ctypes auto-generated script
"""
import re, sys, os

define = re.compile( r'^\#define\W+(\w+)\W+([x0-9A-Fa-f]+)\W*$', re.MULTILINE|re.IGNORECASE )

if __name__ == "__main__":
	file = open(sys.argv[1]).read()
	print 'from OpenGL.constant import Constant'
	for match in define.finditer( file ):
		name, value = match.group(1), match.group(2)
		value = int( value, 0 )
		print '%(name)s = Constant( %(name)r, 0x%(value)x )'%locals()
