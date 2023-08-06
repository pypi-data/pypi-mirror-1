from OpenGL.GL import *
from zglFreeType import *
from zglPrimitives import *

import FTGL


ALIGN_LEFT = 'left'
ALIGN_RIGHT = 'right'
ALIGN_CENTER = 'center'

ALIGN_TOP = 'top'
ALIGN_MIDDLE = 'middle'
ALIGN_BOTTOM = 'bottom'


class zglText(zglObject):
		
	def __init__(self):
		zglObject.__init__(self)
		self.font = None
		self.text = ""
		self.horizontal_align = ALIGN_LEFT
		self.vertical_align = ALIGN_TOP
		return
	
	# update uses current font and text to calculate width and height
	def sizeToFit(self):
		width = 0
		height = 0
		if self.font is not None:
			if self.text is not "":
				width, height = self.font.getSize(self.text)
			else:
				height = self.font.m_font_height
		self.size[0] = width
		self.size[1] = height
	
	def getDrawingOffset(self):
		fontSize = self.font.getSize(self.text)
		xx = 0
		if self.horizontal_align is ALIGN_CENTER:		# CENTER ALIGN
			xx = (self.size[0]-fontSize[0])/2
		elif self.horizontal_align is ALIGN_RIGHT:	# RIGHT ALIGN
			xx = (self.size[0]-fontSize[0])
			
		yy = 0
		if self.vertical_align is ALIGN_MIDDLE:		# MIDDLE ALIGN
			yy = (self.size[1]-fontSize[1])/2
		elif self.vertical_align is ALIGN_BOTTOM:		# BOTTOM ALIGN
			yy = (self.size[1]-fontSize[1])

		return xx, yy

	def draw(self):
		if self.font is None: return
		
		self.predraw()
		

		xx, yy = self.getDrawingOffset()
		
		self.useColourWithAlpha(self.colour, self.alpha)
		
		glPushMatrix()
		glTranslate(xx, yy, 0)
		self.font.draw(self.text)
		glPopMatrix()
		
		self.postdraw()


# simple text box containing a single line of text with a desired background colour
#
class zglTextBox(zglText):
	def __init__(self):
		zglText.__init__(self)
		self.inner_margin = (2,5,2,5)	# top, right, down, left

		self.background = zglRect()
		self.background.corner_mode = True
		self.background.size = self.size	# Link the background's size to the overall size
		self.autoresize_x = True

	def sizeToFit(self):
		if self.autoresize_x:
			# If the textbox is autoresizing based on the text, adjust the background
			zglText.sizeToFit(self)
			self.size[0] += self.inner_margin[1] + self.inner_margin[3]
			self.size[1] += self.inner_margin[0] + self.inner_margin[2]

			# Now adjust the background position based on text alignment
			# Remember: zglRect's position is based on the center of the rect
			if self.horizontal_align is ALIGN_CENTER:
				self.background.position[0] = -self.size[0]/2-self.inner_margin[3]
			elif self.horizontal_align is ALIGN_RIGHT:
				self.background.position[0] = -self.size[0]-self.inner_margin[3]-self.inner_margin[1]
			else:
				self.background.position[0] = 0
				
			if self.vertical_align is ALIGN_TOP:
				self.background.position[1] = 0			
			elif self.vertical_align is ALIGN_MIDDLE:
				self.background.position[1] = -self.size[1]/2
			else:
				self.background.position[1] = -self.size[1]
	
		else:
			# Otherwise, we need to enforce the width/height on the 
			# NOT YET IMPLEMENTED
			pass
	
	def setAlpha(self, alpha):
		self.alpha = alpha
		self.background.alpha = alpha

	def draw(self):
		self.predraw()
		self.background.draw()
	
		# Now since this is now an extension of a zglObject
		# if we change x and y based on text alignment, that would
		# move the object errornously. So instead we calculate, 
		xx = 0
		yy = 0
		
		if self.horizontal_align is ALIGN_CENTER:
			xx = (self.size[0]-self.font.getSize(self.text)[0])/2
		elif self.horizontal_align is ALIGN_RIGHT:
			xx = (self.size[0]-self.font.getSize(self.text)[0])
			
			
		if self.vertical_align is ALIGN_BOTTOM:
			yy = -self.size[1]
		elif self.vertical_align is ALIGN_MIDDLE:
			yy = -self.size[1]/2

		glTranslatef(xx, yy, 0)

		self.useColourWithAlpha()
		self.font.draw(self.text)

		self.postdraw()
		
# NOT DONE!
#
class zglTextArea(zglObject):
	def __init__(self):
		self.font = None
		self.text = ""
		self.lines = []
		self.horizontal_align = ALIGN_LEFT
		self.vertical_align = ALIGN_TOP
		self.line_spacing = 12
	
	# Separate self.text into lines
# NOT DONE!
	def sizeToFit(self):
		self.lines = []
		current_word = ""
		current_line = ""
		newline = False
		for c in self.text:
			if c is '\n':
				
				newline = True
			else:
				current_word += c
		

	def draw(self):
		if self.font is None or len(self.lines) is 0: return
		
		self.predraw()
		
		yy = -(len(self.lines)-1) * self.line_spacing
		for line in self.lines:
			self.font.draw(0, yy, line)
			yy = yy + self.line_spacing
		
		self.postdraw()
		



# Support class that defines functions to deal with keypresses
# and mouse clicks
class zglTextInput:
	def keyPressed(self, key):
#		print "zglTextInput has entry: %s %d" % (key, ord(key))
#		if key is '\x0D':			# Enter
		if ord(key) is 13:
			self.actionEnter(self)
			self.text = ""
#		elif key is '\b':			# Backspace
		elif ord(key) is 8:
			self.text = self.text[:-1]
		elif key is '\033':		# ESC Key
			self.text = ""
		else:
			self.text += key
		self.sizeToFit()

	# When enter is pressed
	# override this for desired functionality
	def actionEnter(self):
		pass



class zglInputTextBox(zglTextBox, zglTextInput):
	def __init__(self):
		zglTextBox.__init__(self)

	def actionEnter(self):
		pass


class zglFTGLFont(FTGL.TextureFont):

	# Note: scale is here to render a sharper font than the
	# font size implies, such that when you zoom in it is still
	# sharp-looking
	
	def __init__(self, typeface, size, scale=2):
		FTGL.TextureFont.__init__(self, typeface)
		self.fontSize = size
		self.scale = scale
		self.FaceSize(size*scale, 288)
		
	def getSize(self, string):
		bbox = self.BBox(string)
		return ((bbox[3]-bbox[0])/self.scale, (bbox[4]-bbox[1])/self.scale)

	def draw(self, string):
		glPushMatrix()
		glScalef(1.0/self.scale, 1.0/self.scale, 1.0)
		self.Render(string)
		glPopMatrix()


class zglFontManager:

	USE_FTGL = 0
	USE_ZGLFREETYPE = 1
	
	mode = USE_FTGL
	library = dict()
	
	@staticmethod
	def getKey(typeface, size):
		return typeface+"_"+str(size)
		
	@staticmethod
	def createItem(typeface, size):
		if  zglFontManager.mode == zglFontManager.USE_FTGL:
			return zglFTGLFont(typeface, size)
		elif zglFontManager.mode == zglFontManager.USE_ZGLFREETYPE:
			return zglFreeType(typeface, size)
	
	@staticmethod
	def getFont(typeface, size):
		"""Gets a font from the existing created objects
		if it doesn't exist, it'll be created"""
		key = zglFontManager.getKey(typeface, size)
		if zglFontManager.library.has_key(key):
#			print "Font "+key+" found in library"
			return zglFontManager.library[key]
		else:
#			print "Font "+key+" not found in library, creating it"
			new_font = zglFontManager.createItem(typeface, size)
			if new_font is not None:
				zglFontManager.library[key] = new_font
				return zglFontManager.library[key]
			else:
				print "Cannot create font: %d" % (key)
		
		
