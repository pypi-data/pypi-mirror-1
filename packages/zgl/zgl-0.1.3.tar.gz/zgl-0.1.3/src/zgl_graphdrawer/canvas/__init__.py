import logging
import sys
import time

from zgl_graphdrawer.Edge import *
from zgl_graphdrawer.Node import *
from zgl_graphdrawer.MouseHandlers import *
import zgl_graphdrawer.Event as EventModule

from zgl.zglUtils import zglUtils


import OpenGL
from OpenGL.GL import *

import numpy



class Canvas(object):

    def __init__(self):
        self.scroll_position = [0.0, 0.0]

        # set up the zoom and pan matrices
        self.zoomMatrix = numpy.matrix('1 0 0 0; 0 1 0 0; 0 0 1 0; 0 0 0 1')
        self.panMatrix = numpy.matrix('0 0 0 0; 0 0 0 0; 0 0 0 0; 0 0 0 0')

        self.selection_rectangle = None

        self.resetDrawables()
        return

    def contextManager(self, value=None):
        if value is not None:
            self._contextManager = value
        return self._contextManager


    def nodePolicy(self, value=None):
        if value is not None:
            self._nodePolicy = value
        return self._nodePolicy

    def edgePolicy(self, value=None):
        if value is not None:
            self._edgePolicy = value
        return self._edgePolicy

    def layoutPolicy(self, value=None):
        if value is not None:
            self._layoutPolicy = value
        return self._layoutPolicy

    def visualPolicy(self, value=None):
        if value is not None:
            self._visualPolicy = value
        return self._visualPolicy

    def portPolicy(self, value=None):
        if value is not None:
            self._portPolicy = value
        return self._portPolicy

    def resetDrawables(self):
        self._dynamicEdge = None
        self.nodes = []
        self.edges = []
        self.selectables = set([])
        self.clickables = set([])
        self.layers = {}
        for layerName in ['edges', 'nodes']:
            layer = CanvasLayer(layerName)
            self.layers[layerName] = layer
            pass
        return


    def addDrawable(self, drawable):
        if isinstance(drawable, Node):
            self.nodes.append(drawable)
            self.layers['nodes'].addChild(drawable)

            ports = drawable.inputPorts.values() + drawable.outputPorts.values()
            for port in ports:
                self.determineSelectable(port)
                self.determineClickable(port)

        if isinstance(drawable, Edge):
            self.edges.append(drawable)
            self.layers['edges'].addChild(drawable)

        self.determineSelectable(drawable)
        self.determineClickable(drawable)
        return


    def determineSelectable(self, object):
        if object.isSelectable():
            self.selectables.add(object)
        return

    def determineClickable(self, object):
        if object.isClickable():
            self.clickables.add(object)

        return

    def removeDrawable(self, drawable):
        return self.removeChild(drawable)
    
    def removeChild(self, drawable):
        # remove from layers
        for layer in self.layers.values():
            layer.removeChild(drawable)

        if isinstance(drawable, Node):
            ports = drawable.inputPorts.values() + drawable.outputPorts.values()
            for port in ports:
                self.selectables.discard(port)
                self.clickables.discard(port)

        self.selectables.discard(drawable)
        self.clickables.discard(drawable)
        return

    def getSelectables(self):
        return self.selectables

    def getClickables(self):
        return self.clickables

    def computeLayout(self):

        if not len(self.nodes):
            # no need to compute layout if self has no nodes
            return

        (x_max, y_max) = self.layoutPolicy().layoutNodes(
            self.nodes, self.edges)
        self.scroll_bounds = (x_max, y_max)

        self.updateLayout()
        return


    def updateLayout(self):

        map(lambda x: x.setupPrimitives(self.nodePolicy()), self.nodes)
        map(lambda x: x.setupPrimitives(self.edgePolicy()), self.edges)

        return


    def setScrollPosition(self, new_scroll_position):
        self.scroll_position = new_scroll_position
        self.validateScrollPosition()


    def validateScrollPosition(self):
        # this is really only used by zglCanvas
        # need to refactor to reflect that
        pass


    def computeDynamicEdge(self, initialPosition, finalPosition):

        line = PrimitivesModule.zglLine()
        edgePolicy = self.edgePolicy()

        initialCanvasMatrix = numpy.matrix('1 0 0 0; 0 1 0 0; 0 0 1 0; %s %s 0 1' % (initialPosition.x, initialPosition.y))
        finalCanvasMatrix = numpy.matrix('1 0 0 0; 0 1 0 0; 0 0 1 0; %s %s 0 1' % (finalPosition.x, finalPosition.y))

        initialWorldMatrix = self.getWorldCoordinatesFromCanvasCoordinates(initialCanvasMatrix)
        finalWorldMatrix = self.getWorldCoordinatesFromCanvasCoordinates(finalCanvasMatrix)

        point1 = (initialWorldMatrix[3,0], initialWorldMatrix[3,1])
        point2 = (finalWorldMatrix[3,0], finalWorldMatrix[3,1])

        line.points = edgePolicy.createPath(point1, point2)
        line.position = (0.0, 0.0, 0.01)
        line.colour = [0.7, 0.7, 1.0, 0.3]
        
        edgeClass = self.contextManager().app().getResourceValue(
            'gui edge class', default=Edge)
        self._dynamicEdge = edgeClass()
        self._dynamicEdge.children = [line]
        self._dynamicEdge.setupColors(self.edgePolicy())
        self.points = line.points

        pass


    def drawLayers(self):
        # Draw nodes
        for layerName, layer in self.layers.iteritems():
            for child in layer.getChildren():
                child.draw()
        return

    def drawDynamicEdge(self):
        if self._dynamicEdge is not None:
            self._dynamicEdge.draw()
        return

    def draw(self):
        glPushMatrix()

        glTranslate(self.panMatrix[3,0], self.panMatrix[3,1], self.panMatrix[3,2])
        glScale(1.0/self.zoomMatrix[0,0], 1.0/self.zoomMatrix[1,1], 1.0/self.zoomMatrix[2,2])

        self.drawLayers()

        self.drawDynamicEdge()

        # Draw selection rectangle
        if self.selection_rectangle is not None:
            zglUtils.drawRect(
                self.selection_rectangle[0], 
                self.selection_rectangle[1], 
                self.selection_rectangle[2], 
                self.selection_rectangle[3], (0.8, 0.5, 0.2, 0.2)
            )

        glPopMatrix()
        return


    def getObjectsIntersectingRect(self, rect):
        objects = []

        # recalculate the rect so that its in the form 
        # where width and height are both positive
        baseX = rect[0]
        baseY = rect[1]
        diffX = baseX + rect[2]
        diffY = baseY + rect[3]

        minX = min(baseX, diffX)
        minY = min(baseY, diffY)
        maxX = max(baseX, diffX)
        maxY = max(baseY, diffY)
        rect = (minX, minY, maxX-minX, maxY-minY)

        for child in self.nodes + self.edges:
            if child.intersectsRect(rect):
                objects.append(child)
        return objects


    # END class Canvas
    pass






class CanvasLayer(object):

    def __init__(self, name):
        self.name = name
        self._children = []
        return

    def addChild(self, child):
        self.getChildren().append(child)
        return

    def removeChild(self, child):
        while child in self.getChildren():
            self.getChildren().remove(child)
        return

    def getChildren(self):
        return self._children


    # END class CanvasLayer
    pass
