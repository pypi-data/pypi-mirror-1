#!/usr/bin/env python
import sys, os
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *



DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600

class zglApplication(object):

	def __init__(self, 
		     width=DEFAULT_WIDTH, 
		     height=DEFAULT_HEIGHT, 
		     app_name=""):
		"""initialize"""

		self.width = width
		self.height = height
		self.app_name = app_name
		self.path = os.getcwd()
		self.initGL()
		self.initLighting()
		self.initViewport()

		
	def initGL(self):
		glutInit(sys.argv)
		# reset the path here because GLUT will change paths to its own path
		os.chdir(self.path)
	
		glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
		glutInitWindowSize(self.width, self.height)
		glutInitWindowPosition(0, 0)
	
		# Okay, like the C version we retain the window id to use when closing, but for those of you new
		# to Python (like myself), remember this assignment would make the variable local and not global
		# if it weren't for the global declaration at the start of main.
		self.window = glutCreateWindow(self.app_name)
		
		glClearDepth (1.0)
		glEnable (GL_DEPTH_TEST)
		glClearColor (0.0, 0.0, 0.0, 0.0)
		glShadeModel (GL_SMOOTH)
		glMatrixMode (GL_PROJECTION)
		
	
	def initLighting(self):
		# initialize lighting */
		lightOnePosition = (40.0, 40, 100.0, 0.0)
		lightOneColor = (0.99, 0.99, 0.99, 1.0) 
		lightTwoPosition = (-40.0, 40, 100.0, 0.0)
		lightTwoColor = (0.99, 0.99, 0.99, 1.0) 

		glLightfv (GL_LIGHT0, GL_POSITION, lightOnePosition)
		glLightfv (GL_LIGHT0, GL_DIFFUSE, lightOneColor)
		glEnable (GL_LIGHT0)
		glLightfv (GL_LIGHT1, GL_POSITION, lightTwoPosition)
		glLightfv (GL_LIGHT1, GL_DIFFUSE, lightTwoColor)
		glEnable (GL_LIGHT1)
		glEnable (GL_LIGHTING)
		glColorMaterial (GL_FRONT_AND_BACK, GL_DIFFUSE)
		glEnable (GL_COLOR_MATERIAL)
	
	def initViewport(self):
		# roughly, measured in centimeters */
		glViewport(0, 0, self.width, self.height)		# Reset The Current Viewport And Perspective Transformation
		self.updateProjection()
		
	def mousePassiveFunc(self, x, y):
		self.last_mouse_x = x
		self.last_mouse_y = y
		glutPostRedisplay()		
	
	def mouseFunc(self, button, state, x, y):
		""" mouseFunc """
	
	def mouseMotionFunc(self, x, y):
		self.last_mouse_x = x
		self.last_mouse_y = y
		glutPostRedisplay()
		
	def keyboardFunc(self, key, x, y):
		# If escape is pressed, kill everything.
		if key == ESCAPE:
			sys.exit()
			
	def keyboardUpFunc(self, key, x, y):
		pass
			
	def specialFunc(self, *args):
		pass
			
	def displayFunc(self):
		self.updateProjection()
		self.updateLighting()
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glDrawBuffer(GL_BACK)
		glutSwapBuffers()
	
	
	def reshapeFunc(self, width, height):
#		print "Reshaping Window "+str(width)+","+str(height)
		if width == 0:
			width = 1
		self.width = width
		self.height = height
		glViewport(0, 0, self.width, self.height)		# Reset The Current Viewport And Perspective Transformation
		self.updateProjection()
	
	
	def idleFunc(self):
		glutPostRedisplay()
		return

	def updateProjection(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(45.0, 1.0*self.width/self.height, 0.1, 100.0)
		glMatrixMode(GL_MODELVIEW)

	#----------------------------------------------
	#	Make a 2D Ortho view for this window size.
	#	Used for 2D drawing (UI, for example)
	def updateProjection2DOrtho(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0.0, self.width, 0.0, self.height)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		
	
	def updateLighting(self):
		""" update lighting """

	
	def run(self):
		glutDisplayFunc(self.displayFunc)
		glutReshapeFunc(self.reshapeFunc)
		glutIdleFunc(self.idleFunc)
		glutMotionFunc(self.mouseMotionFunc)
		glutKeyboardFunc(self.keyboardFunc)
		glutKeyboardUpFunc(self.keyboardUpFunc)
		glutSpecialFunc(self.specialFunc)
		glutPassiveMotionFunc(self.mousePassiveFunc)
		glutMouseFunc(self.mouseFunc)
		glutMotionFunc(self.mouseMotionFunc)
		glutMainLoop()

		
	# END class zglApplication
	pass


if __name__ == "__main__":
	# execution stuff
	app = zglApplication(width, height, "PyOpenGLApplication")
	app.run()


