#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Sets up pylab to be loaded at mathbench init !
"""

import sys
import os

# Set up matplotlib for a nice and interactive usage/display in the wx
# shell.
from matplotlib import rc
import matplotlib
matplotlib.interactive(True) 
matplotlib.use('WX')

import wx

from mathbench.basement.plugin_manager import IPlugin
from mathbench.lab.notebook import LabBook
from mathbench.basement.librarian import LibrarianSingleton

from pylab_configuration import PylabConfigurator
import pylab_search_engine

class PylabPlugin(IPlugin):
	"""
	Try to use the methods with which it has been decorated.
	"""

	def __init__(self):
		"""
		init
		"""
		# initialise parent class
		IPlugin.__init__(self)


	def activate(self):
		"""
		Call the parent class's acivation method
		"""
		IPlugin.activate(self)
		LabBook.initShellSessionAppend("import pylab as pl #< load a plotting library")
		LibrarianSingleton.register(pylab_search_engine.search,"pylab")
		self.configurator = PylabConfigurator(self)
		return


	def deactivate(self):
		"""
		Just call the parent class's method
		"""
		IPlugin.deactivate(self)

	def showConfigurationWidget(self,parent):
		"""
		Create a panel where the user can make some configurations
		"""
		self.configurator.show_config_widget(parent)
