from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame, time

if __name__ == "__main__":
	from OpenGL.tests import testing_context
	#testing_context.createPyGameContext()
	window = testing_context.createGLUTContext()
	glDisable( GL_LIGHTING )
	glColor3f( 1,1,1 )
	glNormal3f( 0,0,1 )
	def begin( *args ):
		print 'begin', args
		return glBegin( *args )
	def vertex( *args ):
		print 'vertex', args
		return glVertex3dv( *args )
	def end( *args ):
		print 'end', args 
		return glEnd( *args )
	for x in range( 100 ):
		tobj = gluNewTess()
		gluTessCallback(tobj, GLU_TESS_BEGIN, begin);
		gluTessCallback(tobj, GLU_TESS_VERTEX, vertex); 
		gluTessCallback(tobj, GLU_TESS_END, end); 
		gluTessBeginPolygon(tobj, None); 
		gluTessBeginContour(tobj);
		for vert in [
			(0,0,0),
			(1,0,0),
			(1,1,0),
##			(1,0,0),
##			(-1,0,0),
		]:
			gluTessVertex(tobj, vert, vert);
		gluTessEndContour(tobj); 
		gluTessEndPolygon(tobj);
		print 'finished end polygon'
		glFlush()
		# glut equivalent of flip..
		glutSetWindow(window);
		glClearColor (0.0, 0.0, (time.time()%1.0)/1.0, 0.0)
		glClear (GL_COLOR_BUFFER_BIT)
		glutSwapBuffers()
		#pygame.display.flip()
		time.sleep( .01 )

