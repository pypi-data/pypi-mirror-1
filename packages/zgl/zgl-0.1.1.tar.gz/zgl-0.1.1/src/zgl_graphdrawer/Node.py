import logging


import numpy

import zgl.zglPrimitives as PrimitivesModule
import zgl.zglText as TextModule

import zgl_graphdrawer.Menu as MenuModule
from zgl_graphdrawer.NodePolicy import *
import zgl_graphdrawer.Port as PortModule
from zgl_graphdrawer.Responder import *


class Node(Responder):

    PART_BORDER = "node border"
    PART_BACKGROUND = "node background"
    PART_LABEL = "node label"


    @staticmethod
    def hasCustomDragReleaseCallback():
        return False

    @staticmethod
    def OnDrag(event, canvas=None,
               objects=None, 
               basePosition=None,
               resetCallback=None,
               shouldResetCallbackFunction=None):

        if objects is None:
            raise NotImplementedError('should not happen')
        
        if shouldResetCallbackFunction(event):
            resetCallback()

        originalCanvasMatrix = numpy.matrix(
            '0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' %
            (basePosition.x, basePosition.y))

        eventPosition = event.GetPosition()
        eventCanvasMatrix = numpy.matrix(
            '0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' %
            (eventPosition.x, eventPosition.y))

        originalWorldMatrix = canvas.getWorldCoordinatesFromCanvasCoordinates(originalCanvasMatrix)
        eventWorldMatrix = canvas.getWorldCoordinatesFromCanvasCoordinates(eventCanvasMatrix)
        worldDeltaMatrix = eventWorldMatrix - originalWorldMatrix

        delta = (worldDeltaMatrix[3,0], worldDeltaMatrix[3,1])

        for object in objects:
            object.setPosition(object.initialX + delta[0],
                               object.initialY + delta[1])
            pass

        edgesToProcess = filter(
            lambda x: x.inputNode() in objects or x.outputNode() in objects,
            canvas.edges
        )
        map(lambda x: x.setupPrimitives(canvas.edgePolicy()), edgesToProcess)

        return



    def __init__(self, nodeData):
        
        Responder.__init__(self)
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.inputPorts = {}
        self.outputPorts = {}
        self.parts = {
            "inputPorts":self.inputPorts,
            "outputPorts":self.outputPorts
            }

        
        self.nodeData = nodeData
        
        self.shouldUpdateDisplay(True)
        self.shouldUpdateImage(False)
        self.shouldUpdateColours(True)

        return


    def contextManager(self, value=None):
        if value is not None:
            self._contextManager = value
        if not hasattr(self, '_contextManager'):
            self._contextManager = None
        return self._contextManager
 
    
    def canvas(self):
        return self.contextManager.canvas

    
    def shouldUpdateDisplay(self, value=None):
        if value is not None:
            self._shouldUpdateDisplay = value
        if not hasattr(self, "_shouldUpdateDisplay"):
            self._shouldUpdateDisplay = False
        return self._shouldUpdateDisplay

    def shouldUpdateImage(self, value=None):
        if value is not None:
            self._shouldUpdateImage = value
        if not hasattr(self, "_shouldUpdateImage"):
            self._shouldUpdateImage = False
        return self._shouldUpdateImage


    def shouldUpdateColours(self, value=None):
        if value is not None:
            self._shouldUpdateColours = value
        if not hasattr(self, "_shouldUpdateColours"):
            self._shouldUpdateColours = False
        return self._shouldUpdateColours


    def isInside(self, x, y):
        if x < self.x or x > self.x+self.width:
            return False
        if y < self.y or y > self.y+self.height:
            return False
        return True

    def overlaps(self, point):
        if point.x < self.x:
            return False
        if point.x > self.x+self.width:
            return False
        if point.y < self.y:
            return False
        if point.y > self.y+self.height:
            return False
        return True


    def intersectsRect(self, rect):
        if (rect[0]+rect[2] > self.x) and \
           (rect[0] < self.x+self.width) and \
           (rect[1]+rect[3] > self.y) and \
           (rect[1] < self.y+self.height):
            return True 

        return False


    def isSelectable(self):
        return True

    def isClickable(self):
        return True

    def updateDisplay(self):
        if self.shouldUpdateColours():
            self.updateColours()

        if self.shouldUpdateImage():
            self.updateImage()
        return

    def updateImage(self):
        """
        The generic version does nothing
        """
        return

    def updateColours(self):

        colours = self.parts["colours"]
        background = self.parts[Node.PART_BACKGROUND]
        text = self.parts[Node.PART_LABEL]
        if self.isSelected():
            logging.debug("updating for selected node")
            background.borderColour = colours[NodePolicy.KEY_BORDER_SELECTION_TRUE]
            background.colour = colours[NodePolicy.KEY_BACKGROUND_SELECTION_TRUE]
            text.colour = colours[NodePolicy.KEY_TEXT_SELECTION_TRUE]
        else:
            logging.debug("updating for unselected node")
            background.borderColour = colours[NodePolicy.KEY_BORDER_SELECTION_FALSE]
            background.colour = colours[NodePolicy.KEY_BACKGROUND_SELECTION_FALSE]
            text.colour = colours[NodePolicy.KEY_TEXT_SELECTION_FALSE]
            pass

        return


    def createBackgroundPrimitive(self, size=None):
        background = PrimitivesModule.zglRect()
        background.position = [0, 0, 0]

        if size is None:
            size = self.getBounds()
        background.size = size

        background.corner_mode = True
        return background



    def getBounds(self):
        return (self.width, self.height)


    def createNamePrimitive(self, nodePolicy):
        # Fit node to text size or simply to
        # what graphviz gives us, which may not look good
        # depending on the NodePolicy
        #stringBounds = font.getSize(node.nodeData.name)
        #nodeSize = (stringBounds[0] + 2*10, stringBounds[1] + 2*10)
        nodeSize = self.getBounds()


        # initialize the name label
        nameLabel = TextModule.zglText()
        nameLabel.position = nodePolicy.getPositionForNameLabel()
        nameLabel.size = [nodeSize[0], nodeSize[1], 0]
        nameLabel.horizontal_align = nodePolicy.getHorizontalAlignmentOfLabel()
        nameLabel.vertical_align = nodePolicy.getVerticalAlignmentOfLabel()
        nameLabel.font = self.font
        nameLabel.text = self.nodeData.name()
        return nameLabel


    def setupPrimitives(self, nodePolicy):

        # self.setupDimensions()
        nodePolicy.setupDimensions(self)

        font = nodePolicy.visualPolicy().font(
            VisualPolicyModule.VisualPolicy.KEY_FONT_DEFAULT)
        self.font = font

        background = self.createBackgroundPrimitive()

        nameLabel = self.createNamePrimitive(nodePolicy)

        self.parts[Node.PART_BACKGROUND] = background
        self.parts[Node.PART_LABEL] = nameLabel
        self.parts["colours"] = nodePolicy._colours

        self.setupPorts(nodePolicy)

        self.shouldUpdateDisplay(True)

        return


    def retrieveInputPortNamesFromDataObject(self):
        if not hasattr(self.nodeData, 'inputPorts'):
            return []
        return self.nodeData.inputPorts


    def retrieveOutputPortNamesFromDataObject(self):
        if not hasattr(self.nodeData, 'outputPorts'):
            return []
        return self.nodeData.outputPorts


    def getResourceKeyForPort(self, portName):
        return 'gui port class'

    
    def setupPorts(self, nodePolicy):

        portPolicy = nodePolicy.portPolicy()

        inputPortNames = self.retrieveInputPortNamesFromDataObject()
        outputPortNames = self.retrieveOutputPortNamesFromDataObject()

        for portDirection, portNames, portMap in [
            (PortModule.Port.PORT_DIRECTION_INPUT, inputPortNames, self.inputPorts),
            (PortModule.Port.PORT_DIRECTION_OUTPUT, outputPortNames, self.outputPorts)]:

            positionCount = len(portNames)
            for index, portName in enumerate(portNames):

                resourceKey = self.getResourceKeyForPort(portName)
                portClass = self.contextManager().app().getResourceValue(
                    resourceKey, PortModule.Port)
                port = portClass(portName)
                port.node = self
                port.direction = portDirection
                port.positionIndex(index)
                port.positionCount(positionCount)

                port.initialSetup()

                portPolicy.setupDimensions(port)

                # we need to first know the port's dimensions
                # beefore we can set its position
                nodePolicy.setPortPosition(self, port)

                port.setupPrimitives(portPolicy)

                portMap[portName] = port
                pass
            pass

        return

    def getPosition(self):
        return (self.x, self.y)

    def setPosition(self, x, y):
        self.x = x
        self.y = y
        return


    def _buildChildren(self):
        return [
            self.parts[Node.PART_BACKGROUND],
            self.parts[Node.PART_LABEL]
            ] + self.inputPorts.values() + self.outputPorts.values()    


    def children(self):
        """
        A subclass can override this
        """
        if not hasattr(self, '_children'):
            # cache this so that we dont have to recompute 
            # for every redraw
            self._children = self._buildChildren()
            pass
        return self._children


    def draw(self):

        if self.shouldUpdateDisplay():
            logging.debug("updating node")
            self.updateDisplay()
            self.shouldUpdateDisplay(False)

        glPushMatrix()
        glTranslate(self.x, self.y, 0)

        for child in self.children():
            child.draw()

        glPopMatrix()

        return


    def getInputPort(self, id):
        return self.inputPorts[id]

    def getOutputPort(self, id):
        return self.outputPorts[id]

    def getSelectionContextualMenu(self, event, eventHandler, canvas, selection):

        popupMenu = SelectionContextualMenu(
            event, eventHandler, canvas, selection)
        return popupMenu


    # END class Node
    pass


class SelectionContextualMenu(MenuModule.SelectionContextualMenu):


    def bindEvents(self):

        self.addMenuItem('Edit', self.OnEdit)
        self.addMenuItem('Delete', self.OnDelete)
        return


    def OnDelete(self, event):

        # first remove all the node's incoming and outgoing edges
        objectsToRemove = []
        for edge in self.canvas.edges:
            if edge.outputNode in self.objects or \
               edge.inputNode in self.objects:
                objectsToRemove.append(edge)

        objectsToRemove.extend(self.objects)

        # remove the objects
        map(self.canvas.removeChild, objectsToRemove)

        return


    def OnEdit(self, event):
        print "%s should display editor for nodes" % self.__class
        return


    # END class SelectionContextualMenu
    pass
