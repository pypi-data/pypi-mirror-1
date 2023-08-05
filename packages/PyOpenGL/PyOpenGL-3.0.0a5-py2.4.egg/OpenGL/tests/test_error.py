"""Test Error-object display"""
from OpenGL.GL import *
import traceback

if __name__ == "__main__":
	from OpenGL.tests import testing_context
	testing_context.createPyGameContext()
	try:
		glClear( GL_INVALID_VALUE )
	except Exception, err:
		traceback.print_exc()
		print err
		print repr(err)
	try:
		glColorPointer(GL_INVALID_VALUE,GL_BYTE,0,None)
	except Exception, err:
		traceback.print_exc()
		print err
		print repr(err)
	try:
		glBitmap(-1,-1,0,0,0,0,"")
	except Exception, err:
		traceback.print_exc()
		print err
		print repr(err)
