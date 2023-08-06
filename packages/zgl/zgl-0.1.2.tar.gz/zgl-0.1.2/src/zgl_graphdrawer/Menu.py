import logging
import sys
import time

import wx

class Menu(object):
    
    def __init__(self, event=None, parent=None, canvas=None):

        self.parent = parent
        self.canvas = canvas
        self.event = event
        return
    
    def addMenuItem(self, label, callback):
        menuitem = wx.MenuItem(self, wx.NewId(), label)
        self.AppendItem(menuitem)
        self.Bind(wx.EVT_MENU, callback, id=menuitem.GetId())
        return
    
    def bindEvents(self):
        raise NotImplementedError

    pass


class SelectionContextualMenu(wx.Menu, Menu):
    
    def __init__(self, event, parent, canvas, objects):
        wx.Menu.__init__(self)
        Menu.__init__(self, event, parent, canvas)
        self.objects = objects
        return

    # END class SelectionContextualMenu
    pass


class CanvasContextualMenu(wx.Menu, Menu):
    
    def __init__(self, *args, **kwds):
        wx.Menu.__init__(self)

        Menu.__init__(self, *args, **kwds)
        return

    def bindEvents(self):
        self.addMenuItem('Create node', self.OnCreateNode)
        return
    
    def OnCreateNode(self, event):
        print "should create node"
        return

    # END class CanvasContextualMenu
    pass

