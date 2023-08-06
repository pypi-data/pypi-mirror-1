from OpenGL.GL import *
from OpenGL.GLUT import *


class zglConsole:
	def __init__(self):
		"""init"""
		self.lines = []		# array to store the lines
		self.line_spacing = 18
		self.font = GLUT_BITMAP_HELVETICA_10
		
	def setFont(self, _font):
		self.font = _font
		
	def draw(self):
		""" """
		xx = x
		yy = self.y
		for line in lines:
			zglUtils.drawBitmapText(line, xx, yy, self.font, self.line_spacing)
			
			yy = yy + 18