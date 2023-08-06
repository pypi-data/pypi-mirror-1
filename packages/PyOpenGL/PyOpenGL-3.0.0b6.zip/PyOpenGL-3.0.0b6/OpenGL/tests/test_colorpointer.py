import sys, time, math
import pygame

from OpenGL.GL import *
from OpenGL.GLU import *

FRAME_TIME = 0.02
colors = []
vertexes = []

def setup_scene(screen):
	glViewport(0, 0, screen.get_width(), screen.get_height())
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluOrtho2D(-4, 4, -3, 3)
	
	glEnableClientState(GL_COLOR_ARRAY)
	glEnableClientState(GL_VERTEX_ARRAY)
	
	radius = 2.0
	
	for i in range(10):
		angle1 = math.pi* i/ 5.0 
		angle2 = math.pi* (i+ 1)/ 5.0
		
		vertexes.append([radius* math.cos(angle1), radius* math.sin(angle1), 0.0])
		vertexes.append([radius* math.cos(angle2), radius* math.sin(angle2), 0.0])
		vertexes.append([0.0, 0.0, 0.0])
		
		colors.append([1.0, 0.0, 0.0, 1.0])
		colors.append([1.0, 0.0, 0.0, 1.0])
		colors.append([0.5, 0.0, 0.0, 1.0])
		
	print len(vertexes), vertexes
	print len(colors), colors
		
	glVertexPointerf(vertexes)
	glColorPointerf(colors)
	
def render_scene():
	glClear(GL_COLOR_BUFFER_BIT)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	
	t = time.time()/ 4
	subtime = t- math.floor(t) 
	glRotatef(subtime* 360, 0, 0, 1)
	
	glDrawArrays(GL_TRIANGLES, 0, 30)

if __name__ == "__main__":
	pygame.init()

	screen = pygame.display.set_mode([800, 600], pygame.OPENGL | pygame.DOUBLEBUF)
	pygame.display.set_caption('Python OpenGL test', 'pygame')

	setup_scene(screen)

	while True:
		starttime = time.time()
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					sys.exit()
		
		render_scene()
		pygame.display.flip()
		
		timeleft = FRAME_TIME- (time.time()- starttime)
		if (timeleft > 0):
			time.sleep(timeleft)
