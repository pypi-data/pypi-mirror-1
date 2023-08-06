#!/usr/bin/python

import logging
import math, sys, os, time


import zgl_graphdrawer.Application as ApplicationModule

def createMockData():
	mockNodes = []
	for i in range(8):
		nodeData = MockNodeData()
		nodeData.name("Job %d" % (i))
		if i < 4:
			nodeData.inputPorts = ['input1', 'input2', 'input3']
		else:
			nodeData.inputPorts = ['input1']
		nodeData.outputPorts = ['result']
		mockNodes.append(nodeData) 

	mockEdges = []
	mockEdge = MockEdgeData()
	mockEdge.inputNode = lambda: mockNodes[0]
	mockEdge.inputPort = 'result'
	mockEdge.outputNode = lambda: mockNodes[1]
	mockEdge.outputPort = 'input1'
	mockEdges.append(mockEdge)

	mockEdge = MockEdgeData()
	mockEdge.inputNode = lambda: mockNodes[0]
	mockEdge.inputPort = 'result'
	mockEdge.outputNode = lambda: mockNodes[2]
	mockEdge.outputPort = 'input2'
	mockEdges.append(mockEdge)

	mockEdge = MockEdgeData()
	mockEdge.inputNode = lambda: mockNodes[0]
	mockEdge.inputPort = 'result'
	mockEdge.outputNode = lambda: mockNodes[3]
	mockEdge.outputPort = 'input3'
	mockEdges.append(mockEdge)

	mockEdge = MockEdgeData()
	mockEdge.inputNode = lambda: mockNodes[0]
	mockEdge.inputPort = 'result'
	mockEdge.outputNode = lambda: mockNodes[4]
	mockEdge.outputPort = 'input1'
	mockEdges.append(mockEdge)

	for source, target in zip(mockNodes[4:-1], mockNodes[5:]):
		mockEdge = MockEdgeData()
		mockEdge.inputNode = lambda: source
		mockEdge.inputPort = 'result'
		mockEdge.outputNode = lambda: target
		mockEdge.outputPort = 'input1'
		mockEdges.append(mockEdge)

	return (mockNodes, mockEdges)

	
# Mock Data Model for node
class MockNodeData(object):
	def __init__(self):
		self.name("Node")

	def name(self, value=None):
		if value is not None:
			self._name = value
		return self._name
		
# Mock Data Model for edge
class MockEdgeData(object):
	def __init__(self):
		self.inputNode = None
		self.outputNode = None

	def name(self, value=None):
		if value is not None:
			self._name = value
		if not hasattr(self, '_name'):
			return "%s.%s->%s.%s" % (self.inputNode().name(),
						 self.inputPort,
						 self.outputNode().name(),
						 self.outputPort)
		return self._name
