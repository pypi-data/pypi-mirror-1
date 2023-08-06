import math

import zgl.zglPrimitives as PrimitivesModule

	
class EdgePolicy(object):
	"""
	this defines the API for EdgePolicy
	"""

	KEY_SELECTION_TRUE = 'selected'
	KEY_SELECTION_FALSE = 'not selected'
	KEY_DYNAMIC = 'dynamic'

	def visualPolicy(self, value=None):
		if value is not None:
			self._visualPolicy = value
		return self._visualPolicy


	# damn British spelling
	def lineColour(self, value=None):
		"""
		TODO: modify this to make use of ColorPolicy
		"""
		if value is not None:
			self._lineColour = value
		return self._lineColour


	"""
	def setupEdge(self, edge):
		raise NotImplementedError
	"""


	def updateEdge(self, edge):
		raise NotImplementedError

	def createPath(self, inputPoint, outputPoint, steps):
		raise NotImplementedError

	# END class EdgePolicy
	pass


class SimpleEdgePolicy(EdgePolicy):

	def __init__(self):
		self.lineColour([1.0, 1.0, 1.0, 0.3])
		return
	
	"""
	def setupEdge(self, edge):
		edge.children = []
		if edge.inputNode is None or edge.outputNode is None:
			return
		
		point1 = (edge.inputNode.x + edge.inputNode.width, edge.inputNode.y + edge.inputNode.height/2)
		point2 = (edge.outputNode.x, edge.outputNode.y + edge.outputNode.height/2)
		
		line = PrimitivesModule.zglLine()
		line.points = self.createPath(point1, point2, 30)
		line.position = (0.0, 0.0, -0.01)
		edge.children.append(line)
		return
	"""
	
	def updateEdge(self, edge):
		pass

	
	def createPath(self, inputPoint, outputPoint, steps=30):
		points = []
		delta = (outputPoint[0]-inputPoint[0], outputPoint[1]-inputPoint[1])
		for i in xrange(steps+1):
			theta = float(i)/steps
			x = inputPoint[0] + delta[0] * theta 
			y = inputPoint[1] + delta[1] * (1-math.cos(theta*math.pi))/2
			points.append( (x,y) )
		return points

	# END class SimpleEdgePolicy
	pass



class SimpleVerticalEdgePolicy(EdgePolicy):

	def __init__(self):
		self.lineColour([0.75, 0.75, 0.0, 1.0])
		return
		
	
	def updateEdge(self, edge):
		
		inputPort = edge.inputPort()
		inputPort.edge = edge
		inputPort.updateColours()
		
		outputPort = edge.outputPort()
		outputPort.edge = edge
		outputPort.updateColours()
		
		pass

	
	def createPath(self, inputPoint, outputPoint, steps=30):
		points = []
		delta = (outputPoint[0]-inputPoint[0], outputPoint[1]-inputPoint[1])
		for i in xrange(steps+1):
			theta = float(i)/steps
			x = inputPoint[0] + delta[0] * (1-math.cos(theta*math.pi))/2
			y = inputPoint[1] + delta[1] * theta
			points.append( (x,y) )
		return points
		
	# END class SimpleVerticalEdgePolicy
	pass
