#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Inspired by PyAlaMode (a programmer's editor from wxPython code)

'Math bench: not a whole laboratory, just a small bench'
"""

import os
import sys
import logging

#sys.path.append(os.path.expanduser("~/src/mathbench/mathbenchdir/trunk"))

# use latest dev version of yapsy
#sys.path.insert(0,os.path.expanduser("~/src/yapsy/yapsydir/trunk"))

import wx
from mathbench.lab.notebook import LabBook
from mathbench.basement.configuration import MathBenchConfig as mbconfig
import mathbench.basement.plugin_manager as pm

from mathbench.basement.librarian import LibrarianSingleton
from mathbench.lab.library import LibraryDeskHTML
 
# Sets some basic paths.
CONFIG_DIR= os.path.expanduser("~/.mathbench")

PLUGINS_DIR= os.path.join(CONFIG_DIR,"plugins")

if not os.path.isdir(CONFIG_DIR):	
	os.mkdir(CONFIG_DIR)

if not os.path.isdir(PLUGINS_DIR):	
	os.mkdir(PLUGINS_DIR)


# Create the app

class MathBenchApp(wx.App):
	"""MathBench as a standalone application."""

	def __init__(self, filename=None):
		self.filename = filename
		wx.App.__init__(self, redirect=False)

	def OnInit(self):
		"""
		Create the main frame and load the config
		"""

		# create the configuration manager
		mbconfig.setFilePath(os.path.join(CONFIG_DIR,"config.txt"))
		self.config = mbconfig.getConfig()

		# create the plugin manager 
		self.pm = pm.LabPluginManager.get()
		self.pm.setConfigParser(self.config, lambda : self.config.save())
		self.pm.setCategoriesFilter({"Default":pm.IPlugin})
		self.pm.setPluginPlaces([PLUGINS_DIR])
		self.pm.setPluginInfoExtension("mathplug")
		# load the plugins
		self.pm.collectPlugins()

		def createSimpleLibraryDesk():
			"""
			Just create a simple frame
			"""
			return LibraryDeskHTML("Mathbench's Library Desk")

		# set the correct class for the help display (library desk)
		LibrarianSingleton.setDeskFactory(createSimpleLibraryDesk)

		# show the main frame
		self.frame = LabBook(filename=self.filename,config=self.config)
		self.frame.Show()
		self.SetTopWindow(self.frame)
		return True

def main(filename=None):
	if not filename and len(sys.argv) > 1:
		filename = sys.argv[1]
	if filename:
		filename = os.path.realpath(filename)
	app = MathBenchApp(filename)
	app.MainLoop()

if __name__ == '__main__':
	main()
