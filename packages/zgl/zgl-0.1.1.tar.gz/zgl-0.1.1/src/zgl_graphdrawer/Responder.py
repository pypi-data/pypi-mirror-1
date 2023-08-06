from zgl.zglUtils import *
from zgl.zglText import *

from MouseHandlers import MouseHandler



class Responder(object):
	def __init__(self):
		self.is_mouseover = False
		self.isSelected(False)
		return

	def visible(self, value=None):
		if value is not None:
			self._visible = value
		if not hasattr(self, '_visible'):
			self._visible = True
		return self._visible

	def isSelected(self, value=None):
		if not self.isSelectable():
			return False
		if value is not None:
			self._isSelected = value
		return self._isSelected
		
	def isSelectable(self):
		return False

	def isClickable(self):
		return False
	
	def overlaps(self, point):
		return False
		
	def mouseMoved(self, x, y):
		if self.isInside(x,y):
			self.is_mouseover = True
		return False
	
	def mouseButtonDown(self, button, x, y):
		return False
	
	def mouseButtonUp(self, button, x, y):
		return False
	
	def mouseDragged(self, x, y):
		return False
	
