import logging

from Responder import *
	
import zgl.zglPrimitives as PrimitivesModule




# An Edge defines a connection between 
#			
class Edge(Responder):
	def __init__(self, edgeData):
		Responder.__init__(self)
		self.edgeData = edgeData
		self._inputNode = None
		self._outputNode = None
		
		return
	
	def sourceNode(self, *args, **kwds):
		return self.inputNode(*args, **kwds)

	def targetNode(self, *args, **kwds):
		return self.outputNode(*args, **kwds)

	def outputNode(self, value=None):
		if value is not None:
			self._outputNode = value
		return self._outputNode

	def inputNode(self, value=None):
		if value is not None:
			self._inputNode = value
		return self._inputNode


	def inputPort(self):
		if self.inputNode() is None:
			raise AttributeError('no attribute "inputNode" found')
		return self.inputNode().getOutputPort(self.edgeData.inputPort)
	
	
	def outputPort(self):
		if self.outputNode() is None:
			raise AttributeError('no attribute "outputNode" found')
		return self.outputNode().getInputPort(self.edgeData.outputPort)

	def setupPrimitives(self, edgePolicy):
		self.children = []
					
		try:
			inputPort = self.inputPort()
			outputPort = self.outputPort()
			
			point1 = (self.inputNode().x + inputPort.x + inputPort.width/2, 
				  self.inputNode().y + inputPort.y + inputPort.height/2)
			point2 = (self.outputNode().x + outputPort.x + outputPort.width/2, 
				  self.outputNode().y + outputPort.y + outputPort.height/2)
		except AttributeError, e:
			logging.error(e)
			return
		
		line = PrimitivesModule.zglLine()
		points = edgePolicy.createPath(point1, point2, 30)
		line.points= points
		self.points = points
		self.children.append(line)
		edgePolicy.updateEdge(self)

		self.setupColors(edgePolicy)
		return

	def setupColors(self, edgePolicy):
		line.colour = edgePolicy._lineColour
		return
	
	def draw(self):
		for child in self.children:
			child.draw()


	# Override hit detection
	# Do not allow edges to be selected for now
	def isInside(self, x, y):
		return False


	def intersectsRect(self, rect):
		return False
		

	# END class Edge
	pass
