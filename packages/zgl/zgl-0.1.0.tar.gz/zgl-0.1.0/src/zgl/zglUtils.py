import os, string, sys

#print sys.path
#import Image
from PIL import Image

import math, operator		# For vector stuff

from OpenGL.GL import *
from OpenGL.GLUT import *


# Some useful constants
PI_OVER_180 = math.pi/180.0

SQRT_2 = math.sqrt(2.0)
SQRT_3 = math.sqrt(3.0)


# For conversion of row/col to matrix index, assuming OpenGL column-major 4x4 matrices
#
# utility function to get index of matrix
# row and col start at 1
#
#	0	4	8	12
#	1	5	9	13
#	2	6	10	14
#	3	7	11	15
#
#
#def rowcol(row,col):
#	return col*4 + row - 5
# prepare index
#def indexFromRowCol(row, col):
#	return row_col_index[row][col]


# A support class for vector manipulation and calculations
# There functions are all based on all vectors being an
# iterable sequence, like a list or numpy array
#
class zglVector:
	@staticmethod
	def lengthen(vector, desiredLength):
		length = len(vector)
		if length < desiredLength:
			return vector + [0]*(desiredLength-length)
		return vector[:desiredLength]
	
	@staticmethod
	def add(v1, v2):
		return map(operator.add, v1, v2)
	@staticmethod
	def subtract(v1, v2):
		return map(operator.sub, v1, v2)
	@staticmethod
	def multiply(v1, v2):
		return map(operator.mul, v1, v2)
	@staticmethod
	def divide(v1, v2):
		return map(operator.div, v1, v2)
	
	@staticmethod
	def multiplyConstant(v, c):
		return map(lambda i: i*c, v)


	@staticmethod
	def norm(v):
		return math.sqrt( reduce( lambda i,j: i + j*j, v, 0 ) )

	@staticmethod
	def normalize(v):
		v_norm = zglVector.norm(v)
		return map( lambda i: i/v_norm, v )
		
	@staticmethod
	def dotProduct(v1, v2):
		temp = map(operator.mul, v1, v2)
		return sum(temp)
	
	@staticmethod
	def crossProduct(v1, v2):
		result = [0.0, 0.0, 0.0]
		result[0] = v1[1] * v2[2] - v1[2] * v2[1];
		result[1] = v1[2] * v2[0] - v1[0] * v2[2];
		result[2] = v1[0] * v2[1] - v1[1] * v2[0];
		return result


class zglUtils:
	LEFT = 0
	CENTER = 1
	RIGHT = 2

	@staticmethod
	def pathGoUp(levels=1):
		index = path.rindex(path, delimiter)
		return path[:i], path[i+1:]
		

	@staticmethod
	def drawRect(x, y, width, height, colour):
		glPushMatrix()
		glTranslatef(x, y, 0)
		glColor4f(colour[0], colour[1], colour[2], colour[3])
		glBegin(GL_QUADS)
		glVertex2f(0, 0)
		glVertex2f(width, 0)
		glVertex2f(width, height)
		glVertex2f(0, height)
		glEnd()
		glPopMatrix()
		
	
	@staticmethod
	def drawRoundedRect( x, y, width, height, radius, colour):
		pass


	@staticmethod
	def strokeRect(x, y, width, height, colour):
		pass


	@staticmethod
	def drawBitmapText(text, x, y, align=LEFT, 
			   font=GLUT_BITMAP_HELVETICA_10, line_spacing=18):
		"""Draw the given text at given 2D position in window"""
		# Available Fonts:
		#	GLUT_BITMAP_8_BY_13
		#	GLUT_BITMAP_9_BY_15
		#	GLUT_BITMAP_TIMES_ROMAN_10
		#	GLUT_BITMAP_TIMES_ROMAN_24
		#	GLUT_BITMAP_HELVETICA_10
		#	GLUT_BITMAP_HELVETICA_12
		#	GLUT_BITMAP_HELVETICA_18
		glRasterPos2i(x, y)
		lines = 0
		for character in text:
			if character == '\n':
				glRasterPos2i(x, y-(lines*line_spacing))
			else:
				glutBitmapCharacter(font, ord(character));

	# Helper function used by multiple chart types to normalize its data
	@staticmethod
	def normalizeChartData(data, min_value, max_value):
		spread = max_value-min_value
		if spread == 0: return

		# normalize according to the min and max
		# could use list comprehension form, but some people say its slower
		# normalized_data = [float(x)/max_value for x in data]
		def normalize(x): return float(x-min_value)/spread
		normalized_data = map(normalize, data[0])
		return normalized_data

	@staticmethod
	def drawBarChart(data, x, y, width, height, colour):
		""" Draws a barchart at x,y 
		    data is assumed to be an array or tuple consisting of the following:
		    (data_array, data_min, data_max) """
		if len(data) is 0: return

		normalized_data = zglUtils.normalizeChartData(data, data[1], data[2])
		if normalized_data:
			bar_width = float(width)/float(len(normalized_data))
			xx = x
			for i in range(len(normalized_data)):
#				print "hello x=%d y=%d" % (xx, y)
				zglUtils.drawRect(xx,y, bar_width, height*normalized_data[i], colour)
				xx = xx + bar_width

	@staticmethod
	def drawBarChartWithBackground(data, x, y, width, height, colour, background_colour):
		zglUtils.drawRect(x,y,width,height,background_colour)
		glPushMatrix()
		glTranslatef(0.0, 0.0, 0.1)
		zglUtils.drawBarChart(data, x, y, width, height, colour)
		glPopMatrix()

	
	@staticmethod
	def drawLineChart(data, x, y, width, height, colour):
		""" Draws a line chart at x,y 
		    data is assumed to be an array or tuple consisting of the following:
		    (data_array, data_min, data_max) """
		if len(data) is 0: return
		elif len(data) is 1: data = data.extend(data)

		normalized_data = zglUtils.normalizeChartData(data, data[1], data[2])
		if normalized_data:
			x_increment = float(width)/float(len(normalized_data)-1)
			xx = 0
			glPushMatrix()
			glTranslatef(x,y,0)
			glColor4f(colour[0], colour[1], colour[2], colour[3])
			glBegin(GL_POLYGON)
#			glVertex2f(0,width)
#			glVertex2f(0,0)
			glVertex2f(width, 0)
			glVertex2f(0,0)
			for i in range(len(normalized_data)):
				glVertex2f(xx, height*normalized_data[i])
				xx += x_increment
			glEnd()
			glPopMatrix()
			
	
	@staticmethod
	def drawLineChartWithBackground(data, x, y, width, height, colour, background_colour):
		zglUtils.drawRect(x,y,width,height,background_colour)
		zglUtils.drawLineChart(data, x, y, width, height, colour)

	

	@staticmethod
	def getNextPowerOfTwo(num):
		""" If num isn't a power of 2, will return the next higher power of two """
		rval = 1
		while (rval<num):
			rval <<= 1
		return rval
		
	
	@staticmethod
	def loadTextureImage(path):
		# From NeHe lesson41
		
		# Load Image And Convert To A Texture
		# path can be a relative path, or a fully qualified path.
		# returns False if the requested image couldn't loaded as a texture
		# returns True and the texture ID if image was loaded
		# Catch exception here if image file couldn't be loaded
		try:
			# Note, NYI, path specified as URL's could be access using python url lib
			# OleLoadPicturePath () supports url paths, but that capability isn't critcial to this tutorial.
			Picture = Image.open(path)
		except:
			print os.getcwd()
			print "Unable to open image file '%s'." % (path)
			return 0
	
		glMaxTexDim = glGetIntegerv (GL_MAX_TEXTURE_SIZE)
	
		WidthPixels = Picture.size [0]
		HeightPixels = Picture.size [1]
	
		if ((WidthPixels > glMaxTexDim) or (HeightPixels > glMaxTexDim)):
			# The image file is too large. Shrink it to fit within the texture dimensions
			# support by our rendering context for a GL texture.
			# Note, Feel free to experiemnt and force a resize by placing a small val into
			# glMaxTexDim (e.g. 32,64,128).
			if (WidthPixels > HeightPixels):
				# Width is the domainant dimension.
				resizeWidthPixels = glMaxTexDim
				squash = float (resizeWidthPixels) / float (WidthPixels)
				resizeHeightPixels = int (HeighPixels * squash)
			else:
				resizeHeightPixels = glMaxTexDim
				squash = float (resizeHeightPixels) / float (HeightPixels)
				resizeWidthPixels = int (WidthPixels * squash)
		else:
			# // Resize Image To Closest Power Of Two
			if (WidthPixels > HeightPixels):
				# Width is the domainant dimension.
				resizeWidthPixels = zglUtils.getNextPowerOfTwo (WidthPixels)
				squash = float (resizeWidthPixels) / float (WidthPixels)
				resizeHeightPixels = int (HeightPixels * squash)
			else:
				resizeHeightPixels = zglUtils.getNextPowerOfTwo (HeightPixels)
				squash = float (resizeHeightPixels) / float (HeightPixels)
				resizeWidthPixels = int (WidthPixels * squash)
			# 
		# Resize the image to be used as a texture.
		# The Python image library provides a handy method resize (). 
		# Several filtering options are available.
		# If you don't specify a filtering option will default NEAREST
		Picture = Picture.resize((resizeWidthPixels, resizeHeightPixels), Image.BICUBIC)
		lWidthPixels = zglUtils.getNextPowerOfTwo(resizeWidthPixels)
		lHeightPixels = zglUtils.getNextPowerOfTwo(resizeWidthPixels)
		# Now we create an image that has the padding needed
		newpicture = Image.new ("RGB", (lWidthPixels, lHeightPixels), (0, 0, 0))
		
		print "picture: "+str(Picture.size[0])+","+str(Picture.size[1])+" mode="+Picture.mode
		print "new_picture: "+str(newpicture.size[0])+","+str(newpicture.size[1])+" mode="+newpicture.mode
		newpicture.paste(Picture)
	
		# Create a raw string from the image data - data will be unsigned bytes
		# RGBpad, no stride (0), and first line is top of image (-1)
		pBits = newpicture.tostring("raw", "RGBX", 0, -1)
	
		# // Typical Texture Generation Using Data From The Bitmap
		texid = glGenTextures(1);											# // Create The Texture
		glBindTexture(GL_TEXTURE_2D, texid);								# // Bind To The Texture ID
		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);		# // (Modify This For The Type Of Filtering You Want)
		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);     # // (Modify This For The Type Of Filtering You Want)
	
		# // (Modify This If You Want Mipmaps)
		glTexImage2D(GL_TEXTURE_2D, 0, 3, lWidthPixels, lHeightPixels, 0, GL_RGBA, GL_UNSIGNED_BYTE, pBits);
		return texid					# // Return True (All Good)


