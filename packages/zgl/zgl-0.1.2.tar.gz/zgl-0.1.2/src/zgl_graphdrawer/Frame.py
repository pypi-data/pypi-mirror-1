import logging
import math, sys, os, time

import wx
import wx.glcanvas 

import Event as EventModule

class wxFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        self.canvas = None

        return



    def bindEvents(self):
        self.Bind(wx.EVT_SHOW, self.OnShowFrame)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        return
    
    def OnResize(self, event):
        self.Skip()
        return
    
    def OnShowFrame(self, event):
        self.canvas.displayFunc()
        self.Skip()
        return

    
    
    # END wxFrame
    pass

