#! /usr/bin/env python
"""OpenGL-ctypes setup script (setuptools-based)
"""
from setuptools import setup, find_packages
import sys, os
sys.path.insert(0, '.' )
import metadata

requirements = []
if sys.hexversion < 0x2050000:
	requirements.append( 'ctypes' )

if __name__ == "__main__":
	setup(
		name = "PyOpenGL",
		packages = find_packages(),
		
		description = 'Standard OpenGL bindings for Python',
		include_package_data = True,
		zip_safe = False,
		
		install_requires = requirements,
		entry_points = {
			'OpenGL.arrays.formathandler':[
				'numpy = OpenGL.arrays.numpymodule:NumpyHandler',
##				'numarray = OpenGL.arrays.numarrays.NumarrayHandler',
##				'numeric = OpenGL.arrays.numeric.NumericHandler',
				'lists = OpenGL.arrays.lists:ListHandler',
				'nones = OpenGL.arrays.nones:NoneHandler',
				'strings = OpenGL.arrays.strings:StringHandler',
				'numbers = OpenGL.arrays.numbers:NumberHandler',
				'ctypesarrays = OpenGL.arrays.ctypesarrays:CtypesArrayHandler',
				'ctypespointers = OpenGL.arrays.ctypespointers:CtypesPointerHandler',
			],
		},
		**metadata.metadata
	)
