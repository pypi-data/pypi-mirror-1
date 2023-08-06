import copy
import math

import VisualPolicy as VisualPolicyModule

import zgl.zglPrimitives as PrimitivesModule
import zgl.zglText as TextModule
import zgl.zglUtils as zglUtils

import zgl_graphdrawer.Port as PortModule

class NodePolicy(object):

    KEY_BORDER_SELECTION_TRUE = "selected border"
    KEY_BORDER_SELECTION_FALSE = "not selected border"
    KEY_BACKGROUND_SELECTION_TRUE = "selected background"
    KEY_BACKGROUND_SELECTION_FALSE = "not selected background"
    KEY_TEXT_SELECTION_TRUE = "selected text"
    KEY_TEXT_SELECTION_FALSE = "not selected text"

    @staticmethod
    def constructDefaultColours(nodePolicy):
        
        import Node as NodeModule
        
        visualPolicy = nodePolicy.visualPolicy()

        colourBorderSelectionTrue = visualPolicy.colour(
            "%s, %s" % (
                NodeModule.Node.PART_BORDER,
                VisualPolicyModule.VisualPolicy.KEY_SELECTION_TRUE
            )
        )
        colourBorderSelectionFalse = visualPolicy.colour(
            "%s, %s" % (
                NodeModule.Node.PART_BORDER,
                VisualPolicyModule.VisualPolicy.KEY_SELECTION_FALSE
            )
        )
        colourBackgroundSelectionTrue = visualPolicy.colour(
            "%s, %s" % (
                NodeModule.Node.PART_BACKGROUND,
                VisualPolicyModule.VisualPolicy.KEY_SELECTION_TRUE
            )
        )
        colourBackgroundSelectionFalse = visualPolicy.colour(
            "%s, %s" % (
                NodeModule.Node.PART_BACKGROUND,
                VisualPolicyModule.VisualPolicy.KEY_SELECTION_FALSE
            )
        )
        colourTextSelectionTrue = visualPolicy.colour(
            "%s, %s" % (
                NodeModule.Node.PART_LABEL,
                VisualPolicyModule.VisualPolicy.KEY_SELECTION_TRUE
            )
        )
        colourTextSelectionFalse = visualPolicy.colour(
            "%s, %s" % (
                NodeModule.Node.PART_LABEL,
                VisualPolicyModule.VisualPolicy.KEY_SELECTION_FALSE
            )
        )


        colours =  {
            NodePolicy.KEY_BORDER_SELECTION_TRUE:colourBorderSelectionTrue,
            NodePolicy.KEY_BORDER_SELECTION_FALSE:colourBorderSelectionFalse,
            NodePolicy.KEY_BACKGROUND_SELECTION_TRUE:colourBackgroundSelectionTrue,
            NodePolicy.KEY_BACKGROUND_SELECTION_FALSE:colourBackgroundSelectionFalse,
            NodePolicy.KEY_TEXT_SELECTION_TRUE:colourTextSelectionTrue,
            NodePolicy.KEY_TEXT_SELECTION_FALSE:colourTextSelectionFalse
        }

        return colours


    def __init__(self, contextManager):
        self.contextManager(contextManager)
        return

    def contextManager(self, value=None):
        if value is not None:
            self._manager = value
        return self._manager

    def initializeColours(self):
        self.resetColours()
        return
    
    
    def resetColours(self):
        self._colours = NodePolicy.constructDefaultColours(self)
        return

    def colour(self, key, value=None):
        if value is not None:
            self._colours[key] = value
        return self._colours[key]


    def visualPolicy(self, value=None):
        if value is not None:
            self._visualPolicy = value
        return self._visualPolicy

    def portPolicy(self, value=None):
        if value is not None:
            self._portPolicy = value
        return self._portPolicy

    
    def getHorizontalAlignmentOfLabel(self):
        return TextModule.ALIGN_CENTER
        
    def getVerticalAlignmentOfLabel(self):
        return TextModule.ALIGN_MIDDLE
    
    def getPositionForNameLabel(self):
        return [0, 0, 0]


    def setupDimensions(self, node):
        node.width=100
        node.height=50
        return

    
    # END class NodePolicy
    pass


class SimpleNodePolicy(NodePolicy):

    def __init__(self, contextManager):
        NodePolicy.__init__(self, contextManager)
        return



    def boundsCheck(self, node_x, node_y, node_width, node_height, x, y):
        if x < node_x or x > node_width:
            return False
        if y < node_y or y > node_height:
            return False
        return True

    
    def updateNode(self, node):

        node.shouldUpdateDisplay(True)

        return

    def setPortPosition(self, node, port):

        # TODO:
        # some of the values in this function
        # are calculated multiple times
        # because this function is called once per port
        # but some of the values, 
        # e.g. minimumPortAreaWidth
        # is constant


        portDirection = port.direction

        yOffset = 0
        if (portDirection == PortModule.Port.PORT_DIRECTION_INPUT):
            yOffset = node.height + 5
        elif (portDirection == PortModule.Port.PORT_DIRECTION_OUTPUT):
            yOffset = -1*(port.height+5)

        port.y = yOffset

        minimumPortMargin = 5
        portCount = port.positionCount()
        minimumPortAreaWidth = \
            port.width * portCount + minimumPortMargin * (portCount-1)

        portIndex = port.positionIndex()

        xOffset = 0
        if minimumPortAreaWidth > node.width:
            # Ports have to extend beyond the limit of the node
            # because of size constraint
            startLocation = (node.width-minimumPortAreaWidth)/2
            xOffset = startLocation + portIndex*(portWidth + minimumPortMargin) - portWidth/2
        else:
            xOffset = node.width/portCount * (portIndex+0.5) - port.width/2
        port.x = xOffset


        return 

    # END class SimpleNodePolicy
    pass
