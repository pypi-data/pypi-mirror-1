import copy
import os

class VisualPolicy(object):

    KEY_SELECTION_TRUE = "selected"
    KEY_SELECTION_FALSE = "not selected"


    COLOUR_DEFAULT = [1.0, 1.0, 1.0, 1.0]

    FONT_DEFAULT = "FreeUniversal-Regular"
    FONT_DEFAULT_FILE = "%s.ttf" % FONT_DEFAULT

    KEY_FONT_DEFAULT = "default font"    



    def __init__(self, contextManager):
        self.contextManager(contextManager)
        self._backgroundMap = {}
        self._textMap = {}
        self._colourMap = {}
        self._fontMap = {}
        return

    def contextManager(self, value=None):
        if value is not None:
            self._contextManager = value
        # being set in the constructor
        # so no need to verify if there's a context manager
        return self._contextManager


    def colour(self, key, value=None):
        if value is not None:
            self._colourMap[key] = value
        if not key in self._colourMap:
            self._colourMap[key] = copy.copy(VisualPolicy.COLOUR_DEFAULT)
        return self._colourMap[key]

    def color(self, *args, **kwds):
        """
        alias the British spelling
        """
        return self.colour(*args, **kwds)

    def getFontPath(self):
        return self.contextManager().resourcePath()


    def getPathForDefaultFont(self):
        fontPath = os.sep.join([self.getFontPath(),
                                VisualPolicy.FONT_DEFAULT_FILE])
        return fontPath


    def font(self, key, value=None):
        if value is not None:
            self._fontMap[key] = value
        if not key in self._fontMap:
            self._fontMap[key] = copy.copy(VisualPolicy.FONT_DEFAULT)
        return self._fontMap[key]


    # END class VisualPolicy
    pass
