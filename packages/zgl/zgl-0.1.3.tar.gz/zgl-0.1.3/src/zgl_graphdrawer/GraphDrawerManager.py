import logging
import sys

import zgl_graphdrawer.Edge as EdgeModule
import zgl_graphdrawer.Node as NodeModule


class ContextManager(object):

    def __init__(self):

        # initialize the dictionry that holds
        # the locations of the commands that may be called
        self._commands = {}
        return

    def app(self, value=None):
        if value is not None:
            self._app = value
        return self._app


    def initializeCanvas(self, canvas):

        self.canvas = canvas
        return

    def initializeEventHandlers(self):

        self.canvas.initializeEventHandlers(contextManager=self)

        pass


    def resourcePath(self, value=None):
        """
        this sets the path from which the resources should be loaded
        """

        if value is not None:
            self._resourcePath = value
        if not hasattr(self, '_resourcePath'):
            self._resourcePath = '.'
        return self._resourcePath

    
    def commandPath(self, key, value=None):
        """
        this sets the path of a command
        """

        if value is not None:
            self._commands[key] = value
        return self._commands[key]






    def objectsMoved(self, objects):
        for edge in self.edges.values():
            if edge.inputNode in objects or \
               edge.outputNode in objects:
                edge.setupPrimitives(self.canvas.edgePolicy())
                pass
            pass
        return


    def draw(self):
        """
        TODO: move out of context manager class
        """
        try:
            self.canvas.draw()
        except Exception, e:
            logging.error(e)
            sys.exit(1)
        return


    def canConnect(self, port1Data, port2Data):
        print "need to determine if can actually connect ports"
        return True


    def connect(self, event, port1Data, port2Data):
        print "should connect %s -> %s" % (
            port1Data[0].getInputPort(port1Data[1]),
            port2Data[0].getOutputPort(port2Data[1])
        )
        return


    # END class ContextManager
    pass


class GraphDrawerManager(ContextManager):

    MOUSEMODE_SELECT = 0
    MOUSEMODE_CANVAS_PAN = 1
    MOUSEMODE_CANVAS_ZOOM = 2
    MOUSEMODE_DRAG_OBJECT = 3

    MOUSEMODE_HOTKEYS = {
        ' ':MOUSEMODE_CANVAS_PAN,
        'z':MOUSEMODE_CANVAS_ZOOM
    }



    def initialize(self, canvas=None):

        if canvas is None:
            import zgl_graphdrawer.canvas.zgl_canvas as CanvasModule
            canvas = CanvasModule.Canvas()

        # Selection Service
        self.selection = NodeSelection(self)

        self.initializeCanvas(canvas)

        pass



    def updateFrame(self, frame):
        self.canvas.updateFrame(frame)




    def step(self):
        """ called every frame. For animation purposes. """
        return


    def keyDown(self, key):
        mouseHandler = self.canvas.activeMouseHandler()
        if not mouseHandler.isActive():
            self.canvas.activeMouseMode = GraphDrawerManager.MOUSEMODE_HOTKEYS.get(key, None)
            pass
        return


    def keyUp(self, key):
        """
        default to selection
        """
        self.canvas.activeMouseMode = GraphDrawerManager.MOUSEMODE_SELECT
        return


    def mouseMoved(self, x, y):
        self.canvas.mouseMoved(x, y)


    def mouseButtonDown(self, button, x, y):


        result = self.canvas.mouseButtonDown(button, x, y)

        if result is not None and result != True:
            # selection clicked on an object
            self.canvas.mouseHandlers[GraphDrawerManager.MOUSEMODE_DRAG_OBJECT] = \
                ObjectDragMoveMouseHandler(self.selection.selection, self.canvas, self)

            # need to cache the previous mouse mode
            self.prevMouseMode = self.canvas.activeMouseMode
            self.canvas.activeMouseMode = GraphDrawerManager.MOUSEMODE_DRAG_OBJECT
            self.canvas.mouseButtonDown(button, x, y)

        return

    def mouseDragged(self, x, y):
        self.canvas.mouseDragged(x, y)

    def mouseButtonUp(self, button, x, y):

        self.canvas.mouseButtonUp(button, x, y)

        # if the mousedown had changed the mouse mode
        # we restore it here
        if self.prevMouseMode is not None:
            self.canvas.activeMouseMode = self.prevMouseMode
            self.prevMouseMode = None
        return

    def setDataContext(self, nodes, edges):
        """
        This is only used by the zglCanvas side
        """
        self.nodes = {}
        self.edges = {}

        for nodeData in nodes:
            uiNode = NodeModule.Node(nodeData)
            self.nodes[nodeData] = uiNode

        for edgeData in edges:
            uiEdge = EdgeModule.Edge(edgeData)
            if edgeData.inputNode() is not None:
                uiEdge.inputNode(self.nodes[edgeData.inputNode()])


            if edgeData.outputNode() is not None:

                uiEdge.outputNode(self.nodes[edgeData.outputNode()])

            self.edges[edgeData] = uiEdge
            pass

        self.canvas.resetDrawables()
        map(self.canvas.addDrawable, self.nodes.itervalues())
        map(self.canvas.addDrawable, self.edges.itervalues())

        logging.debug("GraphDrawer setup %d nodes and %d edges" % 
                      (len(self.nodes), len(self.edges)))
        return


    # END class GraphDrawerManager
    pass



class NodeSelection:
    def __init__(self, delegate):
        self.selection = []
        self.delegate = delegate

    def count(self):
        return len(self.selection)

    def setSelection(self, newSelection):
        oldSelection = self.selection
        self.selection = newSelection
        self.delegate.selectionChanged(oldSelection, newSelection)

        return
