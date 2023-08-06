import Image
from numpy import *
from OpenGL.GL import *
from zglUtils import *
from zglDrawer import *


#==============================================================
#
#	An Object that's based on an array of vertices
#
#
class zglVertexObject(zglObject):
	def __init__(self, vertices, colors, faces, normals):
		zglObject.__init__(self)
		self.size = 1.0;
		
		self.vertices = vertices[:]
		
		if colors is not None:
			self.colors = colors[:]
		else:
			self.colors = None
			
		if faces is not None:
			self.faces = faces[:]
		else:
			self.faces = None
			
		if normals is not None:
			self.normals = normals[:]
		else:
			self.normals = None

#		self.lines = []			#
		
	
	def getVertexArray(self):
		a = []
		for face_index in range(0,len(self.faces)):
			face = self.faces[face_index]
			for vertex_index in face:
				a.extend( [self.vertices[vertex_index][0], self.vertices[vertex_index][1], self.vertices[vertex_index][2]] )
		return a
	
	def getColorArray(self):
		if self.colors is None: return None
		
		a = []
		for face_index in range(0,len(self.faces)):
			face = self.faces[face_index]
			for vertex_index in face:
				a.extend( [self.colors[vertex_index][0], self.colors[vertex_index][1], self.colors[vertex_index][2], self.alpha] )
		return a


	# Assume the that vertices never exceed -1 or 1 in any direction
	# in that case the object should be completely enclosed in a -1 to 1 box
	# which in turn is completely encased by a sphere of size sqrt(3)
	#
	def getBoundingRadius(self):
		return SQRT_3 * self.size


	def maindraw(self):
		glBegin(GL_QUADS)
		for face_index in range(0,len(self.faces)):
			face = self.faces[face_index]
			
			if self.normals is not None:
				glNormal3f(self.normals[face_index][0], self.normals[face_index][1], self.normals[face_index][2])
			
			for vertex_index in face:
				if self.colors is not None:
					glColor4f(self.colors[vertex_index][0], self.colors[vertex_index][1], self.colors[vertex_index][2], self.alpha)
					
				glVertex3f(self.vertices[vertex_index][0] * self.size, self.vertices[vertex_index][1] * self.size, self.vertices[vertex_index][2] * self.size)
				
		glEnd()
		
	
	def drawStroke(self):
		self.predraw()
		glColor4f(self.colour[0], self.colour[1], self.colour[2], self.colour[3]*self.alpha)
		for face in self.faces:
			glBegin(GL_LINE_LOOP)
			for vertex_index in face:
				glVertex3f(self.vertices[vertex_index][0] * self.size, self.vertices[vertex_index][1] * self.size, self.vertices[vertex_index][2] * self.size)
			glEnd()
		self.postdraw()




class zglVertexRect(zglVertexObject):
	vertices = ( (1.0, 1.0, 0.0), (1.0, -1.0, 1.0), (-1.0, -1.0, 1.0), (-1.0, 1.0, 1.0) )
	faces = ( (3, 2, 1, 0) )
	normals = ( (0, 0, 1) )

	

class zglCube(zglVertexObject):
	# Cube Vertices: 8 vertex, 3 coords each
	vertices = (
	(1.0, 1.0, 1.0), (1.0, -1.0, 1.0), (-1.0, -1.0, 1.0), (-1.0, 1.0, 1.0),
	(1.0, 1.0, -1.0), (1.0, -1.0, -1.0), (-1.0, -1.0, -1.0), (-1.0, 1.0, -1.0) )
	
	# Cube Colour Vertices: 8 vertex, 3 colour coords each
	colors = (
	(1.0, 1.0, 1.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 1.0, 1.0),
	(1.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 1.0) )
	
	# Cube Faces: 6 faces, 4 vertex each
	faces = ( (3, 2, 1, 0), (2, 3, 7, 6), (0, 1, 5, 4), (3, 0, 4, 7), (1, 2, 6, 5), (4, 5, 6, 7) )
	
	# Cube Normals
	normals = ( (0, 0, 1), (-1, 0, 0), (1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, -1) )
	
	def __init__(self):
		zglVertexObject.__init__(self, 	zglCube.vertices, 
										zglCube.colors, 
										zglCube.faces, 
										zglCube.normals )


#==============================================================
#
#	An vertex array object that's drawn using GL's vertex array
#
#	COMBINE WITH VERTEX OBJECT< SUBCLASS???
#
class zglVertexArray(zglObject):
	def __init__(self, vertices, colors=None, mode=GL_TRIANGLES):
		zglObject.__init__(self)
		self.vertices = vertices
		self.colors = colors
		self.mode = mode
		
		if self.colors is None:
			self.use_colour_array = False
		else:
			self.use_colour_array = True
		
		self.length = int( len(self.vertices)/3 )
		

	# MAKE SURE THE MODE IS THE SAME	
	def addVertices(self, vertices, colors=None):
		pass
	
	def addVertexObject(self, vertex_object):
		pass
	

		
	def maindraw(self):
		glEnableClientState(GL_VERTEX_ARRAY)
		
		if self.use_colour_array:
			glEnableClientState(GL_COLOR_ARRAY)
		
		self.predraw()
		
		if self.use_colour_array:
			glColorPointer(	4, 				# coordinates per vertex. We want alpha, so 4
							GL_FLOAT, 		# array data type
							0, 				# stride. 0 means no space between vertex data
							self.colors)	# The array
		glVertexPointer(3, 
						GL_FLOAT, 
						0, 
						self.vertices)
		glDrawArrays(	self.mode,		# render mode
						0, 				# Starting vertex 
						self.length)	# number of vertices to be rendered
		
		self.postdraw()
		
		glDisableClientState(GL_VERTEX_ARRAY)
		
		if self.use_colour_array:
			glDisableClientState(GL_COLOR_ARRAY)

