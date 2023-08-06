import logging

from Responder import *

import zgl.zglPrimitives as PrimitivesModule

import zgl_graphdrawer.Menu as MenuModule


class Port(Responder):

    PART_BACKGROUND = "port background"

    PORT_DIRECTION_INPUT = 1
    PORT_DIRECTION_OUTPUT = 2

    @staticmethod
    def hasCustomDragReleaseCallback():
        return True


    @staticmethod
    def OnDrag(event, canvas=None,
               objects=None, 
               basePosition=None,
               resetCallback=None,
               shouldResetCallbackFunction=None):

        if shouldResetCallbackFunction(event):
            resetCallback()
            pass


        canvas.computeDynamicEdge(basePosition, event.GetPosition())

        pass


    def __init__(self, portName):
        Responder.__init__(self)
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.children = []
        self.name = portName
        self.edge = None
        self.basePosition = (0, 0)
        return

    def OnDragRelease(self, event, canvas=None, 
                      objects=None,
                      eventHandler=None):

        if canvas is None:
            raise ValueError('canvas should not be None')

        # TODO:
        # should check if released on a port
        # that can be connected to the initial port
        # and if so, create an actual edge
        releasePosition = event.GetPosition()

        contextManager = canvas.contextManager()
        if contextManager is None:
            raise ValueError('canvas should have access to the context manager')

        clickReleaseObject = canvas.getClickableObjectAtCanvasCoordinates(
            releasePosition.x, releasePosition.y)

        edge = None
        if clickReleaseObject is not None and \
           contextManager.canConnect(self, clickReleaseObject):
            edge = contextManager.connect(self, clickReleaseObject)
            pass

        # reset the dynamic edge
        # (because there won't be one anymore)
        canvas._dynamicEdge = None

        # reset the mouse moved callback
        eventHandler.resetMouseMovedCallback()

        return edge

    
    def initialSetup(self):
        """
        This is a placeholder
        that subclasses can override and 
        hook in custom configuration
        """
        return
    
    def positionIndex(self, value=None):
        if value is not None:
            self._positionIndex = value
        return self._positionIndex

    def positionCount(self, value=None):
        if value is not None:
            self._positionCount = value
        return self._positionCount


    def isClickable(self):
        return True

    def updateColours(self):

        # No color policy for Ports set up yet 
        #colours = self.parts["colours"]

        background = self.parts[Port.PART_BACKGROUND]
        if self.edge is not None:
            background.borderColour = [0.8, 0.8, 0.0, 1.0]
            # background.colour = [0.5, 0.5, 0.0, 1.0]
        else:
            background.borderColour = [0.8, 0.8, 0.0, 1.0]
            background.colour = None
            pass

        return


    def overlaps(self, point):
        """
        TODO:
        This is copied from Node.Node
        Need to remove duplication
        """

        selfX = self.x + self.node.x
        selfY = self.y + self.node.y

        if point.x < selfX:
            return False
        if point.x > selfX+self.width:
            return False
        if point.y < selfY:
            return False
        if point.y > selfY+self.height:
            return False
        return True


    def draw(self):
        glPushMatrix()
        glTranslate(self.x, self.y, 0)

        for child in self.children:
            child.draw()

        glPopMatrix()

        return

    def getSelectionContextualMenu(self, event, 
                                   eventHandler, canvas, selection):
        popupMenu = SelectionContextualMenu(
            event, eventHandler, canvas, selection)
        return popupMenu


    def createBackgroundPrimitive(self, portPolicy):
        background = PrimitivesModule.zglRect()
        background.position = [0, 0, 0]
        background.size = [self.width, self.height, 1.0]
        background.corner_mode = True
        background.colour = None
        background.borderColour = [0.5, 0.5, 0.0, 1.0]
        return background

    
    def setupPrimitives(self, portPolicy):
        
        background = self.createBackgroundPrimitive(portPolicy)
        
        self.parts = {}
        self.parts[Port.PART_BACKGROUND] = background

        self.children.append(background)

        return

    # END class Port
    pass


class SelectionContextualMenu(MenuModule.SelectionContextualMenu):

    def bindEvents(self):
        pass
    pass

