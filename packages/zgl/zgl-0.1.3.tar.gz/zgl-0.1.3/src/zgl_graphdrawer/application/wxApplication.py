import wx
import wx.glcanvas 

import zgl.zgl_graphdrawer.application as ApplicationModule

class wxApplication(ApplicationModule.Application, wx.PySimpleApp):

    def __init__(self):
        wx.PySimpleApp.__init__(self)
        Application.__init__(self)
        return
        
    def OnInit(self):
        print "init now"
        return True

    # END class wxApplication
    pass
