from zglPrimitives import *

# from http://www.python.org/workshops/1997-10/proceedings/savikko.html
class zuiEvent:
    def __init__( self, name ):
        self.name = name

class zuiWidget:
    def __init__( self, parent = None ):
        self.__parent = parent
		
    def Handle( self, event ):
        handler = 'Handle_' + event.name
        if hasattr( self, handler ):
            method = getattr( self, handler )
            method( event )
        elif self.__parent:
            self.__parent.Handle( event )
        elif hasattr( self, 'HandleDefault' ):
            self.HandleDefault( event )    

# since python supports multiple inheritance, ui objects
# is implemented simply as a collection of mouse and keybaord
# 
class zuiObject:
	def __init__(self):
		self.visible = True
		self.is_focusable = False
		self.highlight = False
		self.has_focus = False
		self.mouse_hover = False
		
	def contains(self, x, y):
		return (x >= self.position[0]) and (x <= self.position[0]+self.size[0]) and (y >= self.position[1]) and (y <= self.position[1]+self.size[1])
	
	def mousePassive(self, x, y):
		return False
	
	def mouseDown(self, button, x, y):
		if self.contains(x,y):
			self.has_focus = True
			return True
		return False

	def mouseUp(self, button, x, y):
		return False
	
	def mouseMotion(self, x, y):
		return False
		


# A simple container class for UI Objects
#
class zuiContainer(zuiObject, zglObject):
	def __init__(self):
		zglObject.__init__(self)
		zuiObject.__init__(self)
		self.elements = []
		self.current_mouse_down = None	# The object that mouse was clicked on
		self.current_focus = None	# points to object that currently has focus
		self.current_mouse_hover = None	# points to object that was last mouse hovered

	def setAlpha(self, alpha):
		self.alpha = alpha
		for element in self.elements:
			element.setAlpha(alpha)

	def setCurrentFocus(self, element):
		if self.current_focus is not None:
			self.current_focus.has_focus = False
		self.current_focus = element
		self.current_focus.has_focus = True

	def draw(self):
		self.predraw()

		if self.background is not None:
			self.background.draw()

		for element in self.elements:
			if element.visible:
				element.draw()

		self.postdraw()


	def mousePassive(self, x, y):
#		print "zuiContainer mousePassive: x=%d y=%d" % (x,y)

		if self.contains(x,y):
			# First make coordinates relative to the container origin
			x = x-self.position[0]
			y = y-self.position[1]

			self.mouse_hover = True
			for element in reversed(self.elements):
#				print "zuiContainer mousePassive checking element: x=%d y=%d" % (element.position[0],element.position[1])
				if element.mousePassive(x,y):
					# Now check if there's a previous mouse hover object
					if self.current_mouse_hover is not None and self.current_mouse_hover is not element:
						self.current_mouse_hover.mousePassive(x,y)
					self.current_mouse_hover = element
			return True
		else:
			self.mouse_hover = False
			if self.current_mouse_hover is not None:
				self.current_mouse_hover.mouse_hover = False
			return False

		
	def mouseDown(self, button, x, y):
		# First make coordinates relative to the container origin
		x = x-self.position[0]
		y = y-self.position[1]

		if not self.contains(x,y): return False
		
		self.current_mouse_down = None
		mouse_down_captured = False

		for element in reversed(self.elements):
			if element.mouseDown(button, x, y):
				if element.is_focusable:
					element.has_focus = True
					self.current_focus = element
				self.current_mouse_down = element
				mouse_down_captured = True
				break

		if not mouse_down_captured and self.current_focus is not None:
			self.current_focus.has_focus = False
			self.current_focus = None

		return True


	def mouseUp(self, button, x, y):
		# No container bounds test since you can drag an object and
		# release it outside of the container
		# Instead, only check for current_focus
		if self.current_mouse_down is not None:
			# Make coordinates relative to the container origin
			x = x-self.position[0]
			y = y-self.position[1]
			self.current_mouse_down.mouseUp(button, x, y)
			return True
		return False

	
	def mouseMotion(self, x, y):
		# First make coordinates relative to the container origin
		x = x-self.x
		y = y-self.y

		# Now check to see if any of the elements responds to
		# the mouse motion
		for element in reversed(self.elements):
			if element.mouseMotion(x, y):
				return True
		return False
		
# A simple button
#
class zuiButton(zuiObject):
	def __init__(self):
		zuiObject.__init__(self)
		# Buttons have to be focusable
		self.is_focusable = True
		
		# Flag for when mouse is pressed over the button
		self.mouse_down = False

	# Function that is called when button is clicked
	def releaseAction():
		pass
	def pressAction():
		pass
	
	def mousePassive(self, x, y):
		if self.contains(x,y):
			self.mouse_hover = True
		else:
			self.mouse_hover = False
		return self.mouse_hover
	
	def mouseDown(self, button, x, y):
		if self.contains(x,y):
			print "zuiButton mouseDown"
			self.mouse_down = True
			return True
		return False

	# The mouse action is only fired when the mouse button is released
	# on top of the button
	def mouseUp(self, button, x, y):
		print "zuiButton mouseUp"
		if self.mouse_down:
			self.mouse_down = False
			if self.contains(x,y):
				# If the mouse was released on top of the button
				self.releaseAction()
				return True
		return False
	
	def mouseMotion(self, x, y):
		if self.contains(x,y):
			self.mouse_hover = True
		else:
			self.mouse_hover = False
		return False
	


#
# slider	
class zuiSlider(zuiObject):
	def __init__(self, slider_button):
		zuiObject.__init__(self)
		
		self.slider_button = slider_button
		
		# Buttons have to be focusable
		self.is_focusable = True
		
		# Flag for when mouse is pressed over the button, ie we're dragging
		self.mouse_down = False

		
	# Function that is called when button is clicked
	def callReleaseAction(self):
		self.releaseAction()
	def releaseAction(self):
		pass
	def callPressAction(self):
		self.pressAction()
	def pressAction(self):
		pass
	def callScrollAction(self, position):
		self.scrollAction(position)
	def scrollAction(self, position):	# Position is a 0 to 1 variable of the scroller's position
		pass
		
	def mousePassive(self, x, y):
		if self.slider_button.contains(x,y):
			self.slider_button.mouse_hover = True
		else:
			self.slider_button.mouse_hover = False
		return self.slider_button.mouse_hover
	
	def mouseDown(self, button, x, y):
		if self.slider_button.contains(x,y):
			self.slider_button.mouse_down = True
			self.drag_sliderstartposition = self.slider_button.position[:]
			self.drag_startposition = (x, y)
			self.mouse_down = True
			return True
		return False

	def mouseMotion(self, x, y):
		if self.mouse_down:
			delta_x = x-self.drag_startposition[0]
			delta_y = y-self.drag_startposition[1]
			
			slider_range = self.width - self.slider_button.width
			self.slider_button.position[0] = self.drag_sliderstartposition[0] + delta_x
			
			if self.slider_button.position[0] > slider_range:
				self.slider_button.position[0] = slider_range
			elif self.slider_button.position[0] < 0:
				self.slider_button.position[0]  = 0
			
			# 0-1 variable of position
			position = self.slider_button.position[0] / slider_range
			self.callScrollAction(position)
			
		return False

	# The mouse action is only fired when the mouse button is released
	# on top of the button
	def mouseUp(self, button, x, y):
		if self.mouse_down:
			self.mouse_down = False
			if self.contains(x,y):
				# If the mouse was released on top of the button
				self.releaseAction()
				return True
		return False
	
