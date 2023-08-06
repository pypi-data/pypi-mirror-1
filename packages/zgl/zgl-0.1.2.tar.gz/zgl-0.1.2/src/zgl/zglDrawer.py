import os, string, Image
import math, operator		# For vector stuff

from OpenGL.GL import *
from OpenGL.GLUT import *
from zglUtils import zglVector


class zglDrawer:
	@staticmethod
	def drawRectangle(x, y, width, height, colour):
		glPushMatrix()
		glTranslatef(x, y, 0)
		glColor4f(colour[0], colour[1], colour[2], colour[3])
		glBegin(GL_QUADS)
		glVertex2f(0, height)
		glVertex2f(width, height)
		glVertex2f(width, 0)
		glVertex2f(0, 0)
		glEnd()
		glPopMatrix()

	@staticmethod
	def drawRectangleWithGradient(x, y, width, height, colour1, colour2, angle):
		glPushMatrix()
		glTranslatef(x, y, 0)
		glColor4f(colour[0], colour[1], colour[2], colour[3])
		glBegin(GL_QUADS)
		glVertex2f(0, height)
		glVertex2f(width, height)
		glVertex2f(width, 0)
		glVertex2f(0, 0)
		glEnd()
		glPopMatrix()

	# radius is a 4-tuple for topleft, topright, bottomleft, bottomright radius'
	@staticmethod
	def drawRoundedRectangle(x, y, width, height, radius, colour):
		glPushMatrix()
		glTranslatef(x, y, 0)
		glColor4f(colour[0], colour[1], colour[2], colour[3])
		glBegin(GL_QUADS)
		glVertex2f(0, height)
		glVertex2f(width, height)
		glVertex2f(width, 0)
		glVertex2f(0, 0)
		glEnd()
		glPopMatrix()
		
	
	@staticmethod
	def drawLine(points):
		l = len(points[0])
		if l == 2:
			zglDrawer.drawLine2(points)
		elif l > 2:
			zglDrawer.drawLine3(points)
	
	@staticmethod
	def drawLine2(points):
		glBegin(GL_LINE_STRIP)
		for point in points:
			glVertex2f(point[0], point[1])
		glEnd()
	
	@staticmethod
	def drawLine3(points):
		#point1 = zglVector.lengthen(point1, 3)
		#point2 = zglVector.lengthen(point2, 3)
		
		glBegin(GL_LINE_STRIP)
		for point in points:
			glVertex3f(point[0], point[1], point[2])
		glEnd()

	@staticmethod
	def drawCircularArc(center, startAngle, endAngle):
		
		glBegin(GL_LINE_STRIP)
		
		glEnd()

	@staticmethod
	def drawBezierArc(point1, point2, controlPoint):
		pass
	
	
	