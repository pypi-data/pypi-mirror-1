import logging
import sys
import time

from zgl_graphdrawer.Edge import *
from zgl_graphdrawer.Node import *
from zgl_graphdrawer.MouseHandlers import *

import zgl_graphdrawer.canvas as CanvasModule
import zgl_graphdrawer.Event as EventModule
import zgl_graphdrawer.GraphDrawerManager as ContextManagerModule

from zgl.zglUtils import zglUtils

import OpenGL
from OpenGL.GL import *

import numpy

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        return

class Canvas(CanvasModule.Canvas):

    def __init__(self, parent, width, height, *args, **kwds):

        CanvasModule.Canvas.__init__(self)

        self.width = width
        self.height = height
        self.initGL()
        self.initLighting()
        self.initViewport()

        self._selected = []

        return

    def resetDrawables(self):
        CanvasModule.Canvas.resetDrawables(self)
        self.resetDataToGuiObjectMapping()
        return

    def resetDataToGuiObjectMapping(self):
        self._dataToGuiObjectMapping = {}
        return

    def addDataToGuiObjectMapping(self, dataObject, guiObject):
        self._dataToGuiObjectMapping[dataObject] = guiObject
        return

    def getGuiObjectForDataObject(self, dataObject):
        return self._dataToGuiObjectMapping[dataObject]
 

    def initializeEventHandlers(self, contextManager=None):
        self.contextManager(contextManager)

        for key, default in [
            ('mouse event handler', EventModule.MouseEventHandler),
            ('key event handler', EventModule.KeyEventHandler),
            ('canvas event handler', EventModule.CanvasEventHandler),
            ]:

            classObject = contextManager.app().getResourceValue(
                "%s class" % key, default=default)

            eventHandler = classObject(self)
            eventHandler.bindEvents()
            self.PushEventHandler(eventHandler)

            # TODO:
            # remove this once the event handler mechanism works
            contextManager.app().setResourceValue(
                key, eventHandler)

            pass

        return

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.setViewport(width, height)
        return
    
    def initViewport(self):
        return self._initViewport(self.getWidth(), self.getHeight())

    def _initViewport(self, width, height):

        self.setViewport(width, height)
        self.panMatrix = numpy.matrix('0 0 0 0; 0 0 0 0; 0 0 0 0; 0 0 0 0')

        return

    def setViewport(self, width, height):
        # Reset The Current Viewport And Perspective Transformation
        glViewport(0, 0, width, height)		
        self._updateProjection(width, height)
        return

    def initLighting(self):
        return self._initLighting()

    def _initLighting(self):
        return

    def initGL(self):
        return self._initGL()

    def _initGL(self):

        glClearDepth (1.0)
        glEnable (GL_DEPTH_TEST)
        # glClearColor (0.0, 0.0, 0.0, 0.0)
        glClearColor (0.6, 0.6, 0.6, 1.0)
        
        glShadeModel (GL_SMOOTH)
        glMatrixMode (GL_PROJECTION)

        # Enable blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Really Nice Perspective Calculations
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST) 

        # Enables Smooth Color Shading
        glShadeModel(GL_SMOOTH)
        # Enables Clearing Of The Depth Buffer
        glClearDepth(1.0)

        # Enables Depth Testing
        glEnable(GL_DEPTH_TEST)

        # The Type Of Depth Test To Do	
        glDepthFunc(GL_LEQUAL)

        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)

        self.updateProjection()

        return


    def Render(self, dc):
        self.SetCurrent()

        self.displayFunc()

        self.SwapBuffers()
        return

    def displayFunc(self):
        return self._displayFunc()

    def _displayFunc(self):
        glDrawBuffer(GL_BACK)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        """main drawing stuff goes here"""
        self.draw()

        self.drawMetaInfo()
        return


    def drawMetaInfo(self):

        x = 30
        y = self.getHeight() - 30
        self.drawFPS(x, y)

        return


    def updateProjection(self):
        return self._updateProjection(self.getWidth(), self.getHeight())


    def _updateProjection(self, width, height):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0.0, width, 0.0, height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        return


    def drawFPS(self, x, y):
        if hasattr(self, "last_t"):
            self.fps = 1.0/float(time.time()-self.last_t)
            glColor3f(1.0, 1.0, 1.0)

            zglUtils.drawBitmapText(
                "FPS: %f" % (self.fps), 
                x, y,
                font=GLUT_BITMAP_HELVETICA_10)
        self.last_t = time.time()

        return



    def getClickableObjectAtCanvasCoordinates(self, x, y):
        canvasMatrix = numpy.matrix('0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' % (x, y))
        worldMatrix = self.getWorldCoordinatesFromCanvasCoordinates(canvasMatrix)
        world_x = worldMatrix[3,0]
        world_y = worldMatrix[3,1]

        point = Point(world_x, world_y)

        for clickable in self.getClickables():
            if clickable.overlaps(point):
                return clickable

        return None

    def getSelectableObjectAtCanvasCoordinates(self, x, y):

        """
        this should instead be a composite filter
        # object is selectable
        # object contains point
        """

        canvasMatrix = numpy.matrix(
            '0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' % (x, y))
        worldMatrix = self.getWorldCoordinatesFromCanvasCoordinates(canvasMatrix)
        world_x = worldMatrix[3,0]
        world_y = worldMatrix[3,1]

        point = Point(world_x, world_y)

        for selectable in self.getSelectables():
            if selectable.overlaps(point):
                return selectable

        return None

    def getViewportCoordinatesFromCanvasCoordinates(self, canvasMatrix):
        rotationMatrix = numpy.matrix(
            '1 0 0 0; 0 -1 0 0; 0 0 -1 0; 0 0 0 1')
        translationMatrix = numpy.matrix(
            '0 0 0 0; 0 0 0 0; 0 0 0 0; 0 %s 0 0' % self.getHeight())

        viewportMatrix = (canvasMatrix*rotationMatrix) +translationMatrix
        return viewportMatrix


    def getWorldCoordinatesFromViewportCoordinates(self, viewportMatrix):

        worldMatrix = self.zoomMatrix * (viewportMatrix - self.panMatrix)

        return worldMatrix


    def getWorldCoordinatesFromCanvasCoordinates(self, canvasMatrix):
        viewportMatrix = self.getViewportCoordinatesFromCanvasCoordinates(canvasMatrix)
        worldMatrix = self.getWorldCoordinatesFromViewportCoordinates(viewportMatrix)

        return worldMatrix


    def setSelection(self, selected):

        oldSelection = self._selected
        self._selected = selected

        self.contextManager().selectionChanged(oldSelection, self._selected)

        return

    def addToSelection(self, selected):

        self._selected.extend(selected)

        self.contextManager().selectionChanged([], self._selected)
        pass


    def getSelection(self):
        return self._selected


    def getResourceKeyForNode(self, dataNode):
        return 'gui node class'


    def addNode(self, dataNode, worldMatrix=None):

        resourceKey = self.getResourceKeyForNode(dataNode)
        nodeClass = self.contextManager().app().getResourceValue(
            resourceKey, default=Node)
        
        uiNode = nodeClass(dataNode)
        # need to do this so that the node
        # will have access to app contextual information
        uiNode.contextManager(self.contextManager())
        
        uiNode.setupPrimitives(self.nodePolicy())

        self.addDrawable(uiNode)

        if worldMatrix is None:
            worldMatrix = numpy.matrix('1 0 0 0; 0 1 0 0; 0 0 1 0; 0 0 0 1')

        uiNode.setPosition(worldMatrix[3,0], worldMatrix[3,1])

        dataObjectFunction = self.addDataToGuiObjectMapping

        dataObjectFunction(dataNode, uiNode)
        ports = uiNode.inputPorts.values()+uiNode.outputPorts.values()
        for port in ports:
            portName = port.name

            # parameters have __eq__ defined
            # such that they are equivalent if their ids are equivalent
            # and since the ids are not unique (and are contextualized)
            # we need to include the context, ie the data node
            dataObjectFunction((dataNode, portName), port)

            pass

        return uiNode


    def addEdge(self, dataPath):
        # find the gui objects
        # for the outputNode, outputPort, inputPort, inputNode

        dataObjectFunction = self.getGuiObjectForDataObject

        guiPath = map(
            dataObjectFunction,
            [
                dataPath[0], # source node
                (dataPath[0], dataPath[1]), # source port
                (dataPath[-1], dataPath[-2]), # target port
                dataPath[-1] # target node
            ]
        )

        edgeClass = self.contextManager().app().getResourceValue(
            'gui edge class', default=Edge)

        edge = edgeClass(dataPath, guiPath)
        edge.setupPrimitives(self.edgePolicy())
        self.addDrawable(edge)

        return


    # END class Canvas
    pass

