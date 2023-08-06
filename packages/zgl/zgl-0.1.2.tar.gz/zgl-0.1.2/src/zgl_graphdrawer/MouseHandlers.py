import math

class MouseHandler(object):
    def __init__(self, target):
        self.target = target
        self.isActive(False)
        return

    def isActive(self, value=None):
        if value is not None:
            self._isActive = value
        return self._isActive

    def updateLatestMousePosition(self, x, y):
        self.last_mouse_x = x
        self.last_mouse_y = y
        return

    def mouseButtonDown(self, button, x, y):
        self.updateLatestMousePosition(x, y)
        self.isActive(True)


    def mouseMoved(self, x, y):
        self.updateLatestMousePosition(x, y)


    def mouseButtonUp(self, button, x, y):
        self.isActive(False)


    def mouseDragged(self, x, y):
        pass



class CanvasSelectionMouseHandler (MouseHandler):
    def __init__(self, target, selection):
        MouseHandler.__init__(self,target)
        self.selection = selection
        self.is_drawing_selection_rect = False

    def mouseButtonDown(self, button, x, y):
        MouseHandler.mouseButtonDown(self, button, x, y)
        clickedObject = self.target.getObjectAtViewCoordinates(x,y)
        if clickedObject is not None:
            if not clickedObject.isSelected():
                self.selection.setSelection([clickedObject])
            return clickedObject
        else:
            self.selection.setSelection([])
            self.is_drawing_selection_rect = True
            self.selection_rect_origin = self.target.getCanvasCoordinatesFromViewCoordinates(x,y)
            return True

    def mouseDragged(self, x, y):
        if self.is_drawing_selection_rect:
            self.selection_rect_endpoint = self.target.getCanvasCoordinatesFromViewCoordinates(x,y)

            if self.hasSelectionRect():
                self.target.selection_rectangle = self.getSelectionRect()
                selectedObjects = self.target.getObjectsIntersectingRect(self.target.selection_rectangle)
                self.selection.setSelection(selectedObjects)

        self.updateLatestMousePosition(x, y)


    def mouseButtonUp(self, button, x, y):
        self.selection_rect_origin = None
        self.selection_rect_endpoint = None
        self.target.selection_rectangle = None
        MouseHandler.mouseButtonUp(self, button, x, y)

    def hasSelectionRect(self):
        return self.selection_rect_endpoint is not None and \
               self.selection_rect_origin is not None

    def getSelectionRect(self):
        if not self.hasSelectionRect():
            raise NotImplementedError('selection rect is undefined')

        x = min(self.selection_rect_endpoint[0], 
                self.selection_rect_origin[0])
        y = min(self.selection_rect_endpoint[1], 
                self.selection_rect_origin[1])
        width = max(self.selection_rect_endpoint[0], 
                    self.selection_rect_origin[0]) - x
        height = max(self.selection_rect_endpoint[1], 
                     self.selection_rect_origin[1]) - y
        return (x,y,width,height)


class CanvasScrollMouseHandler (MouseHandler):
    # For Canvas MouseHandlers, the target is the canvas itself
    def mouseDragged(self, x, y):
        delta = (x - self.last_mouse_x, y - self.last_mouse_y)
        if self.isActive():
            self.target.scroll_position[0] = self.target.scroll_position[0] - delta[0]
            self.target.scroll_position[1] = self.target.scroll_position[1] - delta[1]	
        self.updateLatestMousePosition(x, y)


class CanvasZoomMouseHandler (MouseHandler):

    def mouseButtonDown(self, button, x, y):
        MouseHandler.mouseButtonDown(self, button, x, y)
        self.mouseDownX = x
        self.mouseDownY = y
        self.originalZoom = self.target.zoom
        self.originalScroll = self.target.scroll_position[:]
        self.zoom_center = self.target.getCanvasCoordinatesFromViewCoordinates(x,y)

    def mouseDragged(self, x, y):
        delta = (x - self.last_mouse_x, y - self.last_mouse_y)
        if self.isActive() and math.fabs(delta[0]) > 0:
            delta_zoom = -0.005 * delta[0]
            newZoom = min(max(self.target.zoom + delta_zoom, 0.5), 2.0)
            self.target.zoom = newZoom

            new_zoom_center = self.target.getCanvasCoordinatesFromViewCoordinates(x, y)
            delta_scroll = (self.zoom_center[0]-new_zoom_center[0], self.zoom_center[1]-new_zoom_center[1])
            self.target.scroll_position = [self.target.scroll_position[0] + delta_scroll[0], self.target.scroll_position[1] + delta_scroll[1]]


        self.updateLatestMousePosition(x, y)


class ObjectDragMoveMouseHandler (MouseHandler):
    # Target is a list of objects being moved
    # Canvas is the canvas containing the object (needed in case of zoom)
    def __init__(self, target, canvas, delegate):
        MouseHandler.__init__(self, target)
        self.canvas = canvas
        self.delegate = delegate

    def mouseDragged(self, x, y):
        delta = (x - self.last_mouse_x, y - self.last_mouse_y)
        for object in self.target:
            object.x += delta[0] * self.canvas.zoom
            object.y += delta[1] * self.canvas.zoom

        if self.delegate is not None:
            self.delegate.objectsMoved(self.target)

        self.updateLatestMousePosition(x, y)

