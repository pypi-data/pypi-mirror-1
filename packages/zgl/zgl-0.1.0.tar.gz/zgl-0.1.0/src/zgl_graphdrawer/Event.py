#import currypy
import functools
import logging
import sys
import time

import wx
import numpy
import Menu as MenuModule

MODIFIERS = {
    'alt':'AltDown',
    'cmd':'CmdDown',
    'ctrl':'ControlDown',
    'meta':'MetaDown',
    'shift':'ShiftDown'
}
def getModifiers(wxEvent):
    # alt, cmd, ctrl, meta, shift
    modifiers = {}
    for key, attr in MODIFIERS.iteritems():
        modifiers[key] = getattr(wxEvent, attr)()
        pass
    return modifiers

def shouldResetMouseDownCallback(event, modifiers=None):
    if modifiers is not None:
        import Event as EventModule
        newModifiers = EventModule.getModifiers(event)
        if not newModifiers == modifiers:
            return True
    return False


class EventHandler(object):

    def eventSource(self, value=None):
        if value is not None:
            self._eventSource = value
        return self._eventSource

    def OnTimerFraction(self, event):
        # default do nothing
        return


    # END class EventHandler
    pass



class CanvasEventHandler(wx.EvtHandler, EventHandler):

    def __init__(self, eventSource):
        wx.EvtHandler.__init__(self)
        self.eventSource(eventSource)
        pass

    def bindEvents(self):
        self.Bind(wx.EVT_SIZE, self.OnSize, source=self.eventSource())
        self.Bind(wx.EVT_PAINT, self.OnPaint, source=self.eventSource())

        # call the on_timer function
        wx.EVT_TIMER(self.eventSource().GetParent(),
                     self.eventSource().TIMER_ID, 
                     self.OnTimerFraction)

        return

    def OnSize(self, evt):
        eventSource=self.eventSource()

        w,h = eventSource.GetClientSize()
        eventSource.width = w
        eventSource.height = h
        dc = wx.ClientDC(eventSource)
        eventSource.Render(dc)
        return

    def OnPaint(self, evt):
        dc = wx.PaintDC(self.eventSource())
        self.eventSource().Render(dc)
        return

    def OnTimerFraction(self, event):
        self.eventSource().forceRedraw()
        return

    # END class CanvasEventHandler
    pass


class MouseEventHandler(wx.EvtHandler, EventHandler):

    def __init__(self, eventSource):
        wx.EvtHandler.__init__(self)
        self.eventSource(eventSource)
        pass

    def bindEvents(self):
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftMouseButtonDown, source=self.eventSource())
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftMouseButtonUpDefault, source=self.eventSource())
        self.Bind(wx.EVT_MOTION, self.OnMouseMovedDefault, source=self.eventSource())
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightMouseButtonDown, source=self.eventSource())
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightMouseButtonUp, source=self.eventSource())
        return



    def computeRawMouseMove(self, initialPosition, finalPosition):

        initialMatrix = numpy.matrix('0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' % 
                                     (initialPosition.x, initialPosition.y))
        finalMatrix = numpy.matrix('0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' % 
                                   (finalPosition.x, finalPosition.y))

        return finalMatrix - initialMatrix

    def OnMouseMovedDefault(self, event):
        return




    def OnPanViewport(self, event, 
                      basePosition=None,
                      resetCallback=None,
                      shouldResetCallbackFunction=None):
        if shouldResetCallbackFunction(event):
            resetCallback()

        baseCanvasMatrix = numpy.matrix('0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' %
                                        (basePosition.x, basePosition.y))
        baseWorldMatrix = self.eventSource().getWorldCoordinatesFromCanvasCoordinates(baseCanvasMatrix)

        newCanvasMatrix = numpy.matrix('0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' %
                                       (event.GetX(), event.GetY()))
        newWorldMatrix = self.eventSource().getWorldCoordinatesFromCanvasCoordinates(newCanvasMatrix)

        deltaMatrix = newWorldMatrix - baseWorldMatrix

        self.eventSource().panMatrix = deltaMatrix + self.eventSource().initialPanMatrix

        return


    def OnZoomViewport(self, event, 
                       basePosition=None,
                       resetCallback=None,
                       shouldResetCallbackFunction=None):

        if shouldResetCallbackFunction(event):
            resetCallback()

        delta = self.computeRawMouseMove(basePosition, event.GetPosition())
        delta_zoom = -0.005 * delta[3,0]

        newZoomFactor = min(max(self.eventSource().initialZoomMatrix[0,0]+delta_zoom,0.5),10.0)

        newZoomMatrix = numpy.matrix('%s 0 0 0; 0 %s 0 0; 0 0 %s 0; 0 0 0 %s' %
                                     (newZoomFactor, newZoomFactor, newZoomFactor, newZoomFactor))

        self.eventSource().zoomMatrix = newZoomMatrix
        return

    def OnBoundingBoxSelection(self, event, 
                               basePosition=None,
                               resetCallback=None,
                               shouldResetCallbackFunction=None):

        baseCanvasMatrix = numpy.matrix('0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' %
                                        (basePosition.x, basePosition.y))
        baseWorldMatrix = self.eventSource().getWorldCoordinatesFromCanvasCoordinates(baseCanvasMatrix)

        newCanvasMatrix = numpy.matrix('0 0 0 0; 0 0 0 0; 0 0 0 0; %s %s 0 0' %
                                       (event.GetX(), event.GetY()))
        newWorldMatrix = self.eventSource().getWorldCoordinatesFromCanvasCoordinates(newCanvasMatrix)

        deltaMatrix = newWorldMatrix - baseWorldMatrix

        self.eventSource().selection_rectangle = (
            baseWorldMatrix[3,0], baseWorldMatrix[3,1],
            deltaMatrix[3,0], deltaMatrix[3,1]
        )


        #if self.eventSource().selection_rectangle is not None:
        #    # select the objects under the selection_rectagle
        #    pass
        objectsInBoundBox = self.eventSource().getObjectsIntersectingRect(self.eventSource().selection_rectangle)
        self.eventSource().setSelection(self.eventSource().initialSelection + objectsInBoundBox)

        return


    def OnLeftMouseButtonDown(self, event):
        point = event.GetPosition()

        # alt, cmd, ctrl, meta, shift
        modifiers = getModifiers(event)
        shouldResetCallbackFunction = functools.partial(
            shouldResetMouseDownCallback,
            modifiers=modifiers)


        mouseMoveCallback = None
        mouseUpCallback=self.OnLeftMouseButtonUpDefault

        if modifiers['alt']:
            mouseMoveCallback = self.OnPanViewport
            self.eventSource().initialPanMatrix = self.eventSource().panMatrix
            self.eventSource()
        elif modifiers['shift']:
            mouseMoveCallback = self.OnZoomViewport
            self.eventSource().initialZoomMatrix = self.eventSource().zoomMatrix
        else:
            clickedObject = self.eventSource().getClickableObjectAtCanvasCoordinates(point.x, point.y)

            if clickedObject is not None:
                # every clickable object needs to have a OnDrag callback
                mouseMoveCallback = functools.partial(
                    clickedObject.OnDrag,
                    canvas=self.eventSource())
                if clickedObject.hasCustomDragReleaseCallback():
                    mouseUpCallback = functools.partial(
                        clickedObject.OnDragRelease,
                        canvas=self.eventSource(),
                        eventHandler=self)
                    pass

                if (modifiers['ctrl'] or modifiers['cmd']) and \
                   clickedObject.isSelectable():
                    self.eventSource().addToSelection([clickedObject])
                else:
                    self.eventSource().setSelection([clickedObject])
                pass

                objects = self.eventSource().getSelection()
                mouseMoveCallback = functools.partial(
                    mouseMoveCallback,
                    objects=objects)
                for object in objects:
                    object.initialX = object.x
                    object.initialY = object.y
                pass
            else:
                if modifiers['ctrl'] or modifiers['cmd']:
                    # because the "add to" meta key is still active
                    # we don't want to reset the selection
                    pass
                else:
                    self.eventSource().setSelection([])
                self.eventSource().initialSelection = self.eventSource().getSelection()
                mouseMoveCallback = self.OnBoundingBoxSelection
                mouseUpCallback = self.resetSelectionBoundingBox
                pass


        mouseMoveCallback = functools.partial(
            mouseMoveCallback,
            basePosition=event.GetPosition(),
            resetCallback=self.resetMouseCallbacks,
            shouldResetCallbackFunction=shouldResetCallbackFunction)

        self.Bind(wx.EVT_MOTION, mouseMoveCallback, source=self.eventSource())
        self.Bind(wx.EVT_LEFT_UP, mouseUpCallback, source=self.eventSource())

        return

    def OnLeftMouseButtonUpDefault(self, event):
        self.resetMouseMovedCallback()
        return


    def resetSelectionBoundingBox(self, event):
        self.resetMouseCallbacks()
        self.eventSource().selection_rectangle=None
        return

    def resetMouseCallbacks(self):
        self.resetMouseMovedCallback()
        self.resetMouseUpCallback()
        return
    
    def resetMouseUpCallback(self):
        self.Bind(wx.EVT_MOTION, self.OnLeftMouseButtonUpDefault, source=self.eventSource())
        return

    def resetMouseMovedCallback(self):
        self.Bind(wx.EVT_MOTION, self.OnMouseMovedDefault, source=self.eventSource())
        return


    def OnRightMouseButtonDown(self, event):
        point = event.GetPosition()

        clickedObject = self.eventSource().getClickableObjectAtCanvasCoordinates(point.x, point.y)
        selection = self.eventSource().getSelection()[:]

        if clickedObject is None:
            pass
        elif len(selection) is 0 or not clickedObject in selection:
            selection = [clickedObject]

        popupMenu = None

        # create a new popup menu
        if len(selection) is 0:
            menuClass = self.eventSource().app().getResourceValue('canvas contextual menu class', MenuModule.CanvasContextualMenu)
            popupMenu = menuClass(event, self, self.eventSource())
            pass
        else:
            # get the contextual menu
            # from the most recent item selected
            popupMenu = selection[-1].getSelectionContextualMenu(
                event, self, self.eventSource(), selection)
            pass

        popupMenu.bindEvents()
        self.eventSource().PopupMenu(
            popupMenu, event.GetPosition())

        # according to http://wiki.wxpython.org/PopupMenuOnRightClick
        # need to call destroy
        popupMenu.Destroy()

        return

    def OnRightMouseButtonUp(self, event):
        point = event.GetPosition()
        print "right up at (%s,%s)" % (point.x, point.y)


        return



    # END class CanvasEventHandler
    pass




class KeyEventHandler(wx.EvtHandler, EventHandler):

    def __init__(self, eventSource):
        wx.EvtHandler.__init__(self)
        self.eventSource(eventSource)
        pass

    def bindEvents(self):
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPressed)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyReleased)
        return

    def OnKeyPressed(self, event):
        modifiers = getModifiers(event)
        return

    def OnKeyReleased(self, event):
        modifiers = getModifiers(event)
        return

    # END class KeyEventHandler
    pass


class MyPopupMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)

        self.parent = parent

        minimize = wx.MenuItem(self, wx.NewId(), 'Minimize')
        self.AppendItem(minimize)
        self.Bind(wx.EVT_MENU, self.OnMinimize, id=minimize.GetId())

        close = wx.MenuItem(self, wx.NewId(), 'Close')
        self.AppendItem(close)
        self.Bind(wx.EVT_MENU, self.OnClose, id=close.GetId())


    def OnMinimize(self, event):
        self.parent.Iconize()

    def OnClose(self, event):
        self.parent.Close()


