
import zgl_graphdrawer.canvas.gl_canvas as CanvasModule

import wx
import wx.glcanvas 




class Canvas(wx.glcanvas.GLCanvas, CanvasModule.Canvas):

    def __init__(self, parent, *args, **kwds):

        attribList = (
            wx.glcanvas.WX_GL_DOUBLEBUFFER,
            wx.glcanvas.WX_GL_RGBA, 0
        )
        wx.glcanvas.GLCanvas.__init__(
            self, parent, -1, attribList = attribList,
            *args, **kwds)

        CanvasModule.Canvas.__init__(self, parent, *args, **kwds)

        return

    def initializeTimer(self):

        self.TIMER_ID = 100  # pick a number

        # message will be sent to the parent
        self.timer = wx.Timer(self.GetParent(), self.TIMER_ID)  
        self.timer.Start(100)  # x100 milliseconds

        # TODO:
        # figure out how to have multiple listeners for the time event
        # currently only the CanvasEventHandler is handling it

        return


    def forceRedraw(self):
        dc = wx.PaintDC(self)
        self.Render(dc)
        return

    def Render(self, dc):
        self.SetCurrent()

        self.displayFunc()

        self.SwapBuffers()
        return

    def children(self):
        for node in self.nodes:
            yield node
        for edge in self.edges:
            yield edge
        raise StopIteration

    # END class Canvas
    pass

