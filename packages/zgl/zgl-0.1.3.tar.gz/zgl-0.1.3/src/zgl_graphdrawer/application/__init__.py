import logging
import math, sys, os, time


import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


import zgl.zglUtils as zglUtilsModule
import zgl.zglApplication as ZglApplicationModule
from zgl.zglPrimitives import zglMouse




from zgl_graphdrawer.EdgePolicy import *
from zgl_graphdrawer.GraphDrawerManager import GraphDrawerManager
from zgl_graphdrawer.LayoutPolicy import *
from zgl_graphdrawer.NodePolicy import *
from zgl_graphdrawer.PortPolicy import *
from zgl_graphdrawer.VisualPolicy import *

DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600



class Application(object):
    
    def __init__(self):
        self._resourceValues = {}
        return



    def setResourceValue(self, key, value):
        self._resourceValues[key] = value
        return

    def getResourceValue(self, key, default=None):
        if not key in self._resourceValues:
            return default
        return self._resourceValues[key]

    def setDefaultResourcePath(self):
        cwd = os.getcwd()
        resourcePath = os.path.sep.join(
            os.getenv('ZGL_HOME').split('/')+['resources'])
        self.setResourcePath(resourcePath)
        return

    def setResourcePath(self, resourcePath):
        if not os.path.exists(resourcePath):
            raise IOError('resource path %s does not exist' % resourcePath)
        self._resourcePath = resourcePath
        return

    def contextManager(self, value=None):
        if value is not None:
            self.graphDrawerManager = value
        return self.graphDrawerManager


    def initializePolicies(self):

        contextManager = self.contextManager()

        visualPolicy = self.initializeVisualPolicy(contextManager)
        nodePolicy = self.initializeNodePolicy(contextManager)
        edgePolicy = self.initializeEdgePolicy(contextManager)
        layoutPolicy = self.initializeLayoutPolicy(contextManager)
        portPolicy = self.initializePortPolicy(contextManager)
        nodePolicy.portPolicy(portPolicy)
        return
        
        
    def initializeEdgePolicy(self, contextManager):
        canvas = contextManager.canvas
        
        # create and set the edge policy
        key = 'edge policy'
        classObject = self.getResourceValue(
            "%s class" % key, default=SimpleVerticalEdgePolicy)
        edgePolicy = classObject()
        canvas.edgePolicy(edgePolicy)

        visualPolicy = canvas.visualPolicy()
        edgePolicy.visualPolicy(visualPolicy)


        # set the colors for the node policy
        # we can instead set it on the visual policy first
        for key, value in [
            (EdgePolicy.KEY_DYNAMIC,  [0.85, 0.85, 0.85, 1.0]),
            (EdgePolicy.KEY_SELECTION_TRUE, [0.85, 0.85, 0.0, 1.0]),
            (EdgePolicy.KEY_SELECTION_FALSE, [0.7, 0.7, 0.0, 1.0])]:

            visualPolicy.colour(key, value)
            pass


        return edgePolicy
    

    def initializeLayoutPolicy(self, contextManager):
        canvas = contextManager.canvas
        
        # create and set the layout policy
        key = 'layout policy'
        classObject = self.getResourceValue(
            "%s class" % key, default=GraphVizLayoutPolicy)
        layoutPolicy = classObject(contextManager)
        canvas.layoutPolicy(layoutPolicy)

        return layoutPolicy
    
    def initializeNodePolicy(self, contextManager):
        canvas = contextManager.canvas

        # create the node policy for this application
        key = 'node policy'
        classObject = self.getResourceValue(
            "%s class" % key, default=SimpleNodePolicy)
        nodePolicy = classObject(contextManager)

        # set the visual policy
        visualPolicy = canvas.visualPolicy()
        nodePolicy.visualPolicy(visualPolicy)

        # set the colors for the node policy
        # we can instead set it on the visual policy first
        nodePolicy.initializeColours()
        for key, value in [
            (NodePolicy.KEY_BORDER_SELECTION_TRUE,  [1.0, 1.0, 1.0, 1.0]),
            (NodePolicy.KEY_BORDER_SELECTION_FALSE,  [0.6, 0.6, 0.6, 1.0]),
            (NodePolicy.KEY_BACKGROUND_SELECTION_TRUE,  [0.4, 0.4, 0.6, 1.0]),
            (NodePolicy.KEY_BACKGROUND_SELECTION_FALSE,  [0.3, 0.3, 0.5, 0.8]),
            (NodePolicy.KEY_TEXT_SELECTION_TRUE, [1.0, 1.0, 1.0, 1.0]),
            (NodePolicy.KEY_TEXT_SELECTION_FALSE, [0.8, 0.8, 0.8, 1.0])]:

            nodePolicy.colour(key, value)
            pass

        # set the node policy
        canvas.nodePolicy(nodePolicy)
        return nodePolicy
    
    
    
    def initializeVisualPolicy(self, contextManager):

        # create the visual policy
        key = 'visual policy'
        classObject = self.getResourceValue(
            "%s class" % key, default=VisualPolicy)
        visualPolicy = classObject(contextManager)
            
        # seupt the default font
        pathForDefaultFont = visualPolicy.getPathForDefaultFont()
        font = TextModule.zglFontManager.getFont(pathForDefaultFont, 16)
        visualPolicy.font(VisualPolicy.KEY_FONT_DEFAULT, font)
        
        canvas = contextManager.canvas

        # set the visual policy
        canvas.visualPolicy(visualPolicy)
        
        return visualPolicy
    

    def initializePortPolicy(self, contextManager):

        key = 'port policy'
        classObject = self.getResourceValue(
            "%s class" % key, default=PortPolicy)
        portPolicy = classObject(contextManager)

        canvas = contextManager.canvas
        canvas.portPolicy(portPolicy)
        return portPolicy

    
    # END class Application
    pass




class zglApplication(Application, ZglApplicationModule.zglApplication):
    mouse_drag = False
    last_mouse_x = 0
    last_mouse_y = 0

    def __init__(self, name=None, 
                 width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):

        if name is None:
            name = 'Application'

        ZglApplicationModule.zglApplication.__init__(
            self, width=width, height=height, app_name=name)
        Application.__init__(self)

        glClearColor(0.1, 0.1, 0.2, 0.5)

        return

    def initGL(self):
        ZglApplicationModule.zglApplication.initGL(self)

        # Enable blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST) # Really Nice Perspective Calculations

        glShadeModel(GL_SMOOTH)				# Enables Smooth Color Shading
        glClearDepth(1.0)					# Enables Clearing Of The Depth Buffer

        glEnable(GL_DEPTH_TEST)				# Enables Depth Testing
        glDepthFunc(GL_LEQUAL)				# The Type Of Depth Test To Do

        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)

        self.updateProjection()
        return

    
    def updateProjection(self):
        """ Called by reshapeFunc when window size has changed """
        self.updateProjection2DOrtho()

    def reshapeFunc(self, width, height):
        ZglApplicationModule.zglApplication.reshapeFunc(self, width, height)
        self.contextManager().updateFrame((0.0, 0.0, self.width, self.height))


    def displayFunc(self):
        glDrawBuffer(GL_BACK)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        """main drawing stuff goes here"""
        glPushMatrix()
        self.contextManager().step()
        self.contextManager().draw()
        glPopMatrix()

        x = 30
        y = 30
        glColor3f(1.0, 1.0, 1.0)
        self.drawFPS()

        glutSwapBuffers()

        return

    
    def drawFPS(self):
        if hasattr(self, "last_t"):
            # self.fps = 1.0/float(time.time()-self.last_t)
            self.fps = float(time.time()-self.last_t)
            
            glColor3f(1.0, 1.0, 1.0)
            zglUtilsModule.zglUtils.drawBitmapText(
                "FPS: %f" % (self.fps), 
                # x, y
                30, self.height-30, 
                font=GLUT_BITMAP_HELVETICA_10)
        self.last_t = time.time()

        return


    def keyboardFunc(self, key, x, y):
        # If escape is pressed, kill everything.
        if key == '\033':
            logging.debug("Quitting!")
            sys.exit()
        else:
            self.contextManager().keyDown(key)

    def keyboardUpFunc(self, key, x, y):
        self.contextManager().keyUp(key)

    def specialFunc(self, *args):
        key = args[0]
        if key == GLUT_KEY_UP:
            logging.debug("Up!   GLUT_KEY_UP=" + str(GLUT_KEY_UP))
        elif key == GLUT_KEY_DOWN:
            logging.debug("Down!   GLUT_KEY_DOWN=" + str(GLUT_KEY_DOWN))
        elif key == GLUT_KEY_LEFT:
            logging.debug("Left!   GLUT_KEY_LEFT=" + str(GLUT_KEY_LEFT))
        elif key == GLUT_KEY_RIGHT:
            logging.debug("Right!   GLUT_KEY_RIGHT=" + str(GLUT_KEY_RIGHT))

    def mousePassiveFunc(self, x, y):
        zglMouse.setPosition(x, y)

        self.last_mouse_x = x
        self.last_mouse_y = y
        self.contextManager().mouseMoved(x, self.height-y)

    def mouseFunc(self, button, state, x, y):
        if state == GLUT_DOWN:
            self.contextManager().mouseButtonDown(button, x, self.height-y)
        elif state == GLUT_UP:
            self.contextManager().mouseButtonUp(button, x, self.height-y)

    def mouseMotionFunc(self, x, y):
        self.contextManager().mouseDragged(x, self.height-y)

        return

    # END class Application
    pass
