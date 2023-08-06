import os
import sys
import unittest

APP_ROOT = os.getenv('ZGL_HOME')
sys.path.insert(0, '%s/src' % APP_ROOT)

import wx

import zgl_graphdrawer.Application as ApplicationModule
import zgl_graphdrawer.canvas.wx_canvas as CanvasModule
import zgl_graphdrawer.Frame as FrameModule
import zgl_graphdrawer.GraphDrawerManager as ContextManagerModule
import zgl_graphdrawer.utils as UtilsModule

import MockData as DataModule

class TestCase(unittest.TestCase):

    def setUp(self):
        print "setUp"
        pass

    def tearDown(self):
        print "tearDown"
        pass

    def _testApplication1(self):
        app = wx.PySimpleApp()
        frame = wx.Frame(None, title='Hello World')
        frame.Show()
        app.MainLoop()


    def testApplication2(self):
        print "starting"

        app = ApplicationModule.wxApplication()
        app.setResourcePath(
            os.path.sep.join([os.getenv('ZGL_HOME'), 'resources']))


        frame = FrameModule.wxFrame(
            None, title='foo',
            size=wx.Size(ApplicationModule.DEFAULT_WIDTH,
                         ApplicationModule.DEFAULT_HEIGHT))
        frame.app(app)
        canvas = CanvasModule.Canvas(frame, 
                                     ApplicationModule.DEFAULT_WIDTH,
                                     ApplicationModule.DEFAULT_HEIGHT)

        contextManager = ContextManagerModule.GraphDrawerManager()	
        contextManager.initialize(canvas=canvas)

        app.contextManager(contextManager)
        contextManager.app(app)

        # TODO:
        # this needs to be specified elsewhere
        contextManager.commandPath('dot', '/sw/bin/dot')
        
        app.initializePolicies()

        (mockNodes, mockEdges) = DataModule.createMockData()
        contextManager.setDataContext(mockNodes, mockEdges)

        canvas.computeLayout()

        frame.Show()
        app.MainLoop()

        print "ending"
        pass

    # END class TestApplication1
    pass



def main():
    UtilsModule.configLogging()

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCase, 'test'))

    runner = unittest.TextTestRunner()
    runner.run(suite)
    return

if __name__=="__main__":
    main()

