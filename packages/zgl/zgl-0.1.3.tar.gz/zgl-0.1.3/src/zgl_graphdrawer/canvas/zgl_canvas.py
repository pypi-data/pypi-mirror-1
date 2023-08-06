import logging
import sys
import time

from zgl_graphdrawer.Edge import *
from zgl_graphdrawer.Node import *
from zgl_graphdrawer.MouseHandlers import *
import zgl_graphdrawer.Event as EventModule
import zgl_graphdrawer.canvas as CanvasModule
import zgl_graphdrawer.GraphDrawerManager as ContextManagerModule

from zgl.zglUtils import zglUtils


import OpenGL
from OpenGL.GL import *

import numpy



class Canvas(CanvasModule.Canvas):


    def __init__(self):
        CanvasModule.Canvas.__init__(self)
        self.frame = (0.0, 0.0, 0.0, 0.0)	# x_min, y_min, x_max, y_max of the layout
        self.scroll_bounds = (0.0, 0.0)

        self.resetDrawables()


        # self.currentMouseHandler = None
        self.mouseHandlers = {}
        self.defaultMouseHandler = None
        self.activeMouseMode = None

        self.is_dragging = False
        self.is_zooming = False

        return


    def activeMouseHandler(self):
        return self.mouseHandlers.get(
            self.activeMouseMode, 
            self.defaultMouseHandler)


    def draw(self):
        CanvasModule.Canvas.draw(self)
        return

    def updateFrame(self, frame):
        self.frame = frame
        self.validateScrollPosition()


    def children(self):
        for node in self.nodes:
            yield node
        for edge in self.edges:
            yield edge
        raise StopIteration



    def mouseMoved(self, x, y):
        self.activeMouseHandler().mouseMoved(x, y)


    def mouseButtonDown(self, button, x, y):
        # Check if any of the child has buttons that
        # consumed this event 
        for child in self.children():
            if child.mouseButtonDown(button, x, y):
                return True

        result = self.activeMouseHandler().mouseButtonDown(button, x, y)
        if result is not None and result != False:
            return result

        return

    def mouseDragged(self, x, y):

        self.activeMouseHandler().mouseDragged(x, y)

        return

    def mouseButtonUp(self, button, x, y):
        for child in self.children():
            if child.mouseButtonUp(button, x, y):
                return True

        self.activeMouseHandler().mouseButtonUp(button, x, y)
        return


    def initializeEventHandlers(self, contextManager=None):

        self.activeMouseMode = ContextManagerModule.GraphDrawerManager.MOUSEMODE_SELECT

        # Mouse Handlers
        scrollMouseHandler = CanvasScrollMouseHandler(self)
        zoomMouseHandler = CanvasZoomMouseHandler(self)
        selectionMouseHandler = CanvasSelectionMouseHandler(
            self, contextManager.selection)

        mouseHandlers = {
            ContextManagerModule.GraphDrawerManager.MOUSEMODE_SELECT:selectionMouseHandler,
            ContextManagerModule.GraphDrawerManager.MOUSEMODE_CANVAS_PAN:scrollMouseHandler,
            ContextManagerModule.GraphDrawerManager.MOUSEMODE_CANVAS_ZOOM:zoomMouseHandler
        }

        # Default Mouse Handler
        self.defaultMouseHandler = selectionMouseHandler
        self.mouseHandlers = mouseHandlers
        return


    def getObjectAtViewCoordinates(self, x, y):
        (canvas_x, canvas_y) = self.getCanvasCoordinatesFromViewCoordinates(x, y)
        for child in self.children():
            if child.isInside(x, y):
                return child

        return None


    def getViewCoordinatesFromCanvasCoordinates(self, x, y):
        view_x = x/self.zoom - self.scroll_position[0];
        view_y = y/self.zoom - self.scroll_position[1];
        return (view_x, view_y)

    def getCanvasCoordinatesFromViewCoordinates(self, x, y):
        canvas_x = int( (self.scroll_position[0] + x)*self.zoom )
        canvas_y = int( (self.scroll_position[1] + y)*self.zoom )
        return (canvas_x, canvas_y)

    def validateScrollPosition(self):
        if self.scroll_position[0] + self.frame[0] > self.scroll_bounds[0]:
            self.scroll_position[0] = self.scroll_bounds[0] - self.frame[0]
        elif self.scroll_position[1] > self.scroll_bounds[1]:
            pass


    '''
    def displayFunc(self):
            glDrawBuffer(GL_BACK)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glDisable(GL_LIGHTING)
            glColor3f(1.0, 1.0, 1.0)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            """main drawing stuff goes here"""
            glPushMatrix()
            self.graphDrawerManager.step()
            self.graphDrawerManager.draw()
            glPopMatrix()

            x = 30
            y = 30
            glColor3f(1.0, 1.0, 1.0)
            zglUtils.zglUtils.drawBitmapText("Hello World", x, y, )
            self.drawFPS()

            glutSwapBuffers()

    def drawFPS(self):
            if hasattr(self, "last_t"):
                    self.fps = 1.0/float(time.time()-self.last_t)
                    glColor3f(1.0, 1.0, 1.0)
                    zglUtils.zglUtils.drawBitmapText("FPS: %f" % (self.fps), 30, self.height-30, font=GLUT_BITMAP_HELVETICA_10)
            self.last_t = time.time()

    '''

    # END class zglCanvas
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
