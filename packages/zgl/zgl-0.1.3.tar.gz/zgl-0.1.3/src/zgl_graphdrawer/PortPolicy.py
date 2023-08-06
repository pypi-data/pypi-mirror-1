import copy
import math

from Port import *

import zgl.zglPrimitives as PrimitivesModule
import zgl.zglText as TextModule
import zgl.zglUtils as zglUtils


# TODO:
# the following should be configurable
# port size, currently (8,8)
# min port margin, currently 5
# port spacing, currently dynamically spaced out

class PortPolicy(object):

    def __init__(self, contextManager):
        self.contextManager(contextManager)
        return

    def contextManager(self, value=None):
        if value is not None:
            self._manager = value
        return self._manager


    def setupDimensions(self, port):
        port.width = 8
        port.height = 8
        return



    # END class PortPolicy
    pass


