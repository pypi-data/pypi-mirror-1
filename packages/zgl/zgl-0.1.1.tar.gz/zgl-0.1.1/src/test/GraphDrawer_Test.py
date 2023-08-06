#!/usr/bin/python

import logging
import math, sys, os, time

APP_ROOT = os.getenv('ZGL_HOME')
sys.path.insert(0, '%s/src' % APP_ROOT)


import zgl_graphdrawer.Application as ApplicationModule
import zgl_graphdrawer.GraphDrawerManager as ContextManagerModule
import zgl_graphdrawer.utils as CanvasUtils

import MockData as DataModule


	
if __name__ == "__main__":
	# setup logging
	CanvasUtils.configLogging()

	# execution stuff
	(mockNodes, mockEdges) = DataModule.createMockData()
	
	app = ApplicationModule.zglApplication()
	app.setDefaultResourcePath()
	# app.initializeContextManager()
	# contextManager = app.contextManager()
	contextManager = ContextManagerModule.GraphDrawerManager()
	app.contextManager(contextManager)
	contextManager.app(app)
	contextManager.initialize()

	# TODO:
	# this needs to be specified elsewhere
	contextManager.commandPath('dot', '/sw/bin/dot')

	app.initializePolicies()

	# some of us have different paths for dot
	if len(sys.argv) > 1:
		import getopt
		try:
			options, args = getopt.getopt(sys.argv[1:], "d:", ["dot="])
			for option, argument in options:
				if option in ("-d","--dot"):
					app.graphDrawerManager.commandPath('dot', argument)
		finally:
			pass
	
	contextManager.setDataContext(mockNodes, mockEdges)

	canvas = contextManager.canvas
	canvas.computeLayout()


	app.run()
