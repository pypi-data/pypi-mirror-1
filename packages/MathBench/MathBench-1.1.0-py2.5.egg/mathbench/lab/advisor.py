#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
The interface to chose the user's prefereed options.
"""


import sys
import os
import logging

		
import wx
import wx.py.dispatcher as dispatcher

from mathbench.ext.pluginmanagement_widgets import PluginsConfigPanel
from mathbench.basement import plugin_manager as pman

# global variable for when we only want to test the display (see
# __main__ at the end of the file.)
ADVISOR_TEST_ONLY=False

class OptionsFrame(wx.Frame):
	
	def __init__(self,parent,config,id=-1,title="Options",size=wx.Size(-1,-1)):
		"""
		create a frame instance
		"""
		wx.Frame.__init__(self,parent=parent,id=id,title=title,size=size)
		self.config = config
		sizer = wx.BoxSizer(wx.VERTICAL)
		nb = self.createNotebook()
		sizer.Add(nb,proportion=1,flag=wx.EXPAND)
		self.SetSizer(sizer)
		self.SetIcon(wx.ArtProvider().GetIcon(wx.ART_HELP_SETTINGS))
		self.Fit()
		self.Show()
		self.Bind(wx.EVT_CLOSE,self.OnClose)

	def createNotebook(self):
		"""
		Create a notebook with all options
		"""
		nb = wx.Notebook(self, -1)
		# Create general option panel
		panel = OptionsPanel(nb,self.config)
		nb.AddPage(panel,"General")
		# Create
		pm = pman.LabPluginManager.get()
		plugpan = PluginsConfigPanel(nb, pm=pm, use_versions=False)
		nb.AddPage(plugpan,"Plugins")
		return nb
		

	def OnClose(self,event):
		"""
		When the frame must close
		"""
		if ADVISOR_TEST_ONLY:
			logging.info("Configuration saved at closing")
			dispatcher.send(signal="OptionsClosed",sender=self)
			return event.Skip()
		self.config.save()
		dispatcher.send(signal="OptionsClosed",sender=self)
		event.Skip()

class OptionsPanel(wx.Panel):
	"""
	Makes it possible to set the options
	"""
	
	def __init__(self,parent,config):
		"""
		create the panel instance
		"""
		wx.Panel.__init__(self,parent)
		self.config = config
		self.parent= parent

		if ADVISOR_TEST_ONLY:
			sizer = wx.BoxSizer(wx.VERTICAL)
			# dummy text
			sectiontitle1 = wx.StaticText(self,id=-1,label="Bla!")
			sectiontitle1.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
			sectiontitle1.SetSize(sectiontitle1.GetBestSize())
			sizer.Add(sectiontitle1)
			self.SetSizer(sizer)
			return self.Fit()

		# content design
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		
		# completion section
		sectiontitle1 = wx.StaticText(self,id=-1,label="Auto Completion")
		sectiontitle1.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		sectiontitle1.SetSize(sectiontitle1.GetBestSize())
		# -- the options
		cb1_1 = wx.CheckBox(self,-1,"Show Auto Completion")
		if self.config.get("Auto Completion","Show_Auto_Completion") == "1":
			cb1_1.SetValue(True)
		else:
			cb1_1.SetValue(False)
		
		cb1_2 = wx.CheckBox(self,-1,"Include Magic Attributes")
		if self.config.get("Auto Completion","Include_Magic_Attributes") == "1":
			cb1_2.SetValue(True)
		else:
			cb1_2.SetValue(False)

		cb1_3 = wx.CheckBox(self,-1,"Include Single Underscores")
		if self.config.get("Auto Completion","Include_Single_Underscores") == "1":
			cb1_3.SetValue(True)
		else:
			cb1_3.SetValue(False)

		cb1_4 = wx.CheckBox(self,-1,"Include Double Underscores")
		if self.config.get("Auto Completion","Include_Double_Underscores") == "1":
			cb1_4.SetValue(True)
		else:
			cb1_4.SetValue(False)


		# call tip section
		sectiontitle2 = wx.StaticText(self,id=-1,label="Call Tips")
		sectiontitle2.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		sectiontitle2.SetSize(sectiontitle2.GetBestSize())
		# -- the options
		cb2_1 = wx.CheckBox(self,-1,"Show Call Tips")
		if self.config.get("Call Tips","Show_Call_Tips") == "1":
			cb2_1.SetValue(True)
		else:
			cb2_1.SetValue(False)
		
		cb2_2 = wx.CheckBox(self,-1,"Insert_Call_Tips")
		if self.config.get("Call Tips","Insert_Call_Tips") == "1":
			cb2_2.SetValue(True)
		else:
			cb2_2.SetValue(False)


		# call tip section
		sectiontitle3 = wx.StaticText(self,id=-1,label="View")
		sectiontitle3.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		sectiontitle3.SetSize(sectiontitle3.GetBestSize())
		# -- the options
		cb3_1 = wx.CheckBox(self,-1,"Wrap Lines")
		if self.config.get("View","Wrap_Lines") == "1":
			cb3_1.SetValue(True)
		else:
			cb3_1.SetValue(False)
		
		cb3_2 = wx.CheckBox(self,-1,"Show Line Numbers")
		if self.config.get("View","Show_Line_Numbers") == "1":
			cb3_2.SetValue(True)
		else:
			cb3_2.SetValue(False)


		sizer.AddMany([sectiontitle1,
					   cb1_1,
					   cb1_2,
					   cb1_3,
					   cb1_4,
					   (20,20),
					   sectiontitle2,
					   cb2_1,
					   cb2_2,
					   (20,20),
					   sectiontitle3,
					   cb3_1,
					   cb3_2])
		self.SetSizer(sizer)
		self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox,cb1_1)
		self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox,cb1_2)
		self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox,cb1_3)
		self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox,cb1_4)
		self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox,cb2_1)
		self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox,cb2_2)
		self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox,cb3_1)
		self.Bind(wx.EVT_CHECKBOX, self.OnCheckbox,cb3_2)
		self.Fit()



	def OnCheckbox(self,event):
		"""
		When the user ticks/unticks a checkbox
		"""
		cb = event.GetEventObject()
		state_str = "0"
		if event.IsChecked():
			state_str="1"
		# now set the right options
		if cb.GetLabel()=="Show Auto Completion":
			self.config.set("Auto Completion","Show_Auto_Completion",state_str)
		elif cb.GetLabel()=="Include Magic Attributes":
			self.config.set("Auto Completion","Include_Magic_Attributes",state_str)
		elif cb.GetLabel()=="Include Single Underscores":
			self.config.set("Auto Completion","Include_Single_Underscores",state_str)
		elif cb.GetLabel()=="Include Double Underscores":
			self.config.set("Auto Completion","Include_Double_Underscores",state_str)
		elif cb.GetLabel()=="Show Call Tips":
			self.config.set("Call Tips","Show_Call_Tips",state_str)
		elif cb.GetLabel()=="Insert Call Tips":
			self.config.set("Call Tips","Insert_Call_Tips",state_str)
		elif cb.GetLabel()=="Wrap Lines":
			self.config.set("View","Wrap_Lines",state_str)
		elif cb.GetLabel()=="Show Line Numbers":
			self.config.set("View","Show_Line_Numbers",state_str)
		else:
			return
		dispatcher.send(signal='OptionsChanged', sender=self.parent.GetParent())

			
if __name__=="__main__":

	sys.path.append(os.path.expanduser("~/src/mathbench/mathbenchdir/trunk"))
	ADVISOR_TEST_ONLY=True

	import ConfigParser

	logging.basicConfig(level=logging.DEBUG)

	from mathbench.basement import plugin_manager as pman

	PLUGINS_DIR= os.path.expanduser("~/src/mathbench/mathbenchdir/trunk/plugins")
	import ConfigParser
	# create the plugin manager 
	pm = pman.LabPluginManager.get()
	conf = ConfigParser.ConfigParser()
	pm.setConfigParser(conf, lambda : True)
	pm.setCategoriesFilter({"Default":pman.IPlugin})
	pm.setPluginPlaces([PLUGINS_DIR])
	pm.setPluginInfoExtension("mathplug")
	# load the plugins
	pm.collectPlugins()

	app = wx.PySimpleApp()

	f = OptionsFrame(None,conf)
	f.Show()
	
	app.MainLoop()

	
