#-----------------------------------------------------------------------------
# Name:		pluginmanager_widgets.py
# Purpose:	 global plugin management and dialog to control them
#
# Author:	  Rob McMullen
# Comments:	   Modified for mathbench by Thibauld Nion
# Created:	 2007
# RCS-ID:	  $Id: $
# Copyright:   (c) 2007 Rob McMullen
# License:	 wxWidgets
#-----------------------------------------------------------------------------
"""
Widget for plugin management configurations

This module provides plugin management for yapsy plugins.
"""

import os, sys
#from cStringIO import StringIO

import wx
# import wx.stc
# from wx.lib.pubsub import Publisher
# from wx.lib.evtmgr import eventManager
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import wx.lib.hyperlink as hlk


import logging

from columnsizer import *


class PluginList(wx.ListCtrl, CheckListCtrlMixin, ColumnSizerMixin):
	"""
	Display the list of plugins with check boxes to see which ones are
	activated.
	
	Collaborates with a plugin manager.
	"""

	def __init__(self, parent, pm, use_versions = True):
		wx.ListCtrl.__init__(self, parent, size=(200,100), style=wx.LC_REPORT)
		CheckListCtrlMixin.__init__(self)
		ColumnSizerMixin.__init__(self)

		self.plugin_manager = pm
		self.recuperatePlugins()
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

		self.skip_verify = False
		self.show_versions = use_versions

		self.createColumns()
		self.reset()
		self.resizeColumns()


	def recuperatePlugins(self):
		"""
		Recuperate all plugins
		"""
		cats = self.plugin_manager.getCategories()
		self.plugins = []
		for cat in cats:
			plugins = self.plugin_manager.getPluginsOfCategory(cat)
#			print plugins
			self.plugins.extend(plugins)
		logging.debug("Recuperated plugins %s" % self.plugins)

		# Sort first by name, then by version number
		self.plugins.sort(key=lambda s:(s.name, s.version))


	def createColumns(self):
		self.InsertColumn(0, "Name")
		self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		if self.show_versions:
			self.InsertColumn(1, "Version")
			self.SetColumnWidth(1, wx.LIST_AUTOSIZE)

	def getPlugin(self, index):
		if len(self.plugins)==0:
			return None
		else:
			return self.plugins[index]

	def OnItemActivated(self, evt):
		index = evt.GetIndex()
		logging.debug("selected plugin %d: %s" % (index, self.plugins[index]))
		evt.Skip()

	def reset(self):
		index = 0
		list_count = self.GetItemCount()
		for plugin in self.plugins:
			logging.debug("Reset info for plugin: %s" % plugin.name)
			if index >= list_count:
				self.InsertStringItem(sys.maxint, plugin.name)
			else:
				self.SetStringItem(index, 0, plugin.name)
			if self.show_versions:
				self.SetStringItem(index, 1, str(plugin.version))
			self.CheckItem(index, plugin.is_activated)

			index += 1

		if index < list_count:
			for i in range(index, list_count):
				# always delete the first item because the list gets
				# shorter by one each time.
				self.DeleteItem(index)

	def OnCheckItem(self, index, flag):
		"""
		When an item "checked state" change, apply the change to the
		corresponding plugin by activating/deactivating it.
		"""
		if flag:
			what = "checked"
		else:
			what = "unchecked"
		logging.debug("toggling plugin %d: %s = %s" % (index, self.plugins[index],
													   what))
		if not self.skip_verify:
			# If we aren't currently verifying another item, verify
			# that only one plugin of the same name is active
			self.verify(index)
		plugin = self.plugins[index]

	def verify(self, selected_index):
		"""
		Check two things:

		  - make sure a plugin that is currently in use isn't deactivated

		  - When multiple versions of the same plugin exist, verify
		    that only the selected version is active and all other
		    versions are deactivated.
		"""
		# CheckItem always calls OnCheckItem, so setting the checked
		# state within this method would cause in infinite loop
		# without this skip_verify flag
		self.skip_verify = True
		selected = self.plugins[selected_index]

		# If the user tried to disable an in-use plugin, don't allow it
		if hasattr(selected.plugin_object, 'isInUse'):
			if not self.IsChecked(selected_index) and selected.plugin_object.isInUse():
				self.CheckItem(selected_index, True)
				self.skip_verify = False
				dlg = wx.MessageDialog(self, "Plugin %s in use.\n\nCan't deactivate a running plugin." % selected.name, "Plugin in use", wx.OK | wx.ICON_EXCLAMATION )
				dlg.ShowModal()
				return

		# otherwise, make sure the selected plugin doesn't have any
		# other versions active
		index = 0
		for plugin in self.plugins:
			if plugin.name == selected.name and plugin != selected:
					self.CheckItem(index, False)
			index += 1
		self.skip_verify = False

	def update(self):
		index = 0
		for plugin in self.plugins:
			activated = self.IsChecked(index)
			if activated != plugin.plugin_object.is_activated:
				if activated:
					logging.debug("Activating %s" % plugin.plugin_object)
					self.plugin_manager.activatePluginByName(plugin.name,plugin.category)
				else:
					logging.debug("Deactivating %s" % plugin.plugin_object)
					self.plugin_manager.deactivatePluginByName(plugin.name,plugin.category)
			index += 1


class SimplePluginPanel(wx.Panel):
	"""
	A simple panel that shows basic info about the plugin and display
	a 'Configure' button if the current plugin is configurable.
	"""

	def __init__(self, parent, plugin_info):
		"""
		plugin_info: instance holding the plugin object and its metadata.
		"""
		self.plugin_info = plugin_info
		wx.Panel.__init__(self, parent)
		self.sizer = wx.GridBagSizer()
		self.create()
		self.SetSizer(self.sizer)
		
	def create(self):
		row = 0
		# set the main title
		txt = wx.StaticText(self,-1,"Description")
		font = txt.GetFont()
		font.SetWeight(wx.FONTWEIGHT_BOLD)
		txt.SetFont(font)
		self.sizer.Add(txt,(row,1))
		row += 1
		# kind of separator
		sep0 = wx.StaticText(self, -1, "")
		self.sizer.Add(sep0,(row,1),flag=wx.EXPAND)
		row += 1
		order = ['author', 'version', 'copyright']
		for info in order:
			if (hasattr(self.plugin_info,info)):
				title = wx.StaticText(self, -1, info+": ")
				self.sizer.Add(title, (row,0))		
				value = wx.StaticText(self, -1, str(getattr(self.plugin_info, info)))
				self.sizer.Add(value, (row,1), flag=wx.EXPAND)
				row += 1
		# kind of separator
		sep = wx.StaticText(self, -1, "")
		self.sizer.Add(sep,(row,1),flag=wx.EXPAND)
		row += 1
		# Display the web link separately:
		if (hasattr(self.plugin_info,'website')):
			hyper1 = hlk.HyperLinkCtrl(self, wx.ID_ANY, "Website",
									   URL=self.plugin_info.website)
			self.sizer.Add(hyper1, (row,1), flag=wx.EXPAND)
			row += 1
		# kind of separator
		sep2 = wx.StaticText(self, -1, "")
		self.sizer.Add(sep2,(row,1),flag=wx.EXPAND)
		row += 1
		# create a button that will show the plugin's files
		if (hasattr(self.plugin_info,'path')):
			def on_reveal(event):
				"""
				Reveal the plugin files in a file dialog
				"""
				dlg = wx.FileDialog(
					self, message="Plugin's files", defaultDir=self.plugin_info.path, 
					defaultFile="", style=wx.FD_CHANGE_DIR
					)
				dlg.ShowModal()
				dlg.Destroy()
			btn = wx.Button(self,-1,"Reveal files")
			btn.Bind(wx.EVT_BUTTON,on_reveal)
			self.sizer.Add(btn,(row,0),flag=wx.ALL,border=3)
		# when the plugin provides a widget for its configuration, display it !
		if hasattr(self.plugin_info.plugin_object,"showConfigurationWidget"):
			def on_click(event):
				self.plugin_info.plugin_object.showConfigurationWidget(self)
			btn = wx.Button(self,-1,"Configure")
			btn.Bind(wx.EVT_BUTTON,on_click)
			self.sizer.Add(btn,(row,1),flag=wx.ALL,border=3)		

	def update(self):
		# update preferences here
		pass

class NoPluginPanel(wx.Panel):
	"""
	A simple panel to be displayed when there is no plugin at all !
	"""

	def __init__(self, parent, pm):
		"""
		pm: plugin manager
		"""
		self.pm = pm
		wx.Panel.__init__(self, parent)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.create()
		self.SetSizer(self.sizer)


	def create(self):
		txt = wx.StaticText(self, -1, """

No plugin found or selected !

""")
		self.sizer.Add(txt)
		
	def update(self):
		"""
		dummy function to comply with the required interface;
		"""
		pass

class PluginsConfigPanel(wx.Panel):
	"""
	Holds a list of plugins 
	"""

	def __init__(self, parent, pm, use_versions=True):
		"""
		pm: the plugin manager instance.
		"""
		
		wx.Panel.__init__(self, parent, -1)

		self.plugin_manager = pm
		
		self.show_versions = use_versions

		sizer = wx.BoxSizer(wx.VERTICAL)
		txt = wx.StaticText(self,-1,"""
Check/uncheck the plugins to ask to their activation/deactivation.

Press the 'Apply' button to enforce these choices.  
""")
		sizer.Add(txt,flag=wx.ALL|wx.EXPAND,border=3)
		
		self.splitter = wx.SplitterWindow(self)
		self.splitter.SetMinimumPaneSize(150)
		listpanel = self.createListPanel(self.splitter)
		self.list = listpanel.list
		
		self.panels = {}
		pref = self.createPanel(self.list.getPlugin(0))

		self.splitter.SplitVertically(listpanel, pref, 0)
#		self.splitter.SetSashGravity(0.4)
		sizer.Add(self.splitter, 1, wx.EXPAND)

		self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		self.SetSizer(sizer)
		self.Fit()

	def createListPanel(self, parent):
		"""
		Create a panel containing a list and an 'Apply' button.
		"""
		panel = wx.Panel(parent,-1)
		sizer = wx.BoxSizer(wx.VERTICAL)
		panel.list = self.createList(panel)
		sizer.Add(panel.list,proportion=1,flag=wx.ALL|wx.EXPAND,border=3)
		botpanel = wx.Panel(panel,-1)
		botsizer = wx.BoxSizer(wx.HORIZONTAL)
		btn = wx.Button(botpanel,-1,"Apply")
		btn.Bind(wx.EVT_BUTTON,self.OnApply)
		btn2 = wx.Button(botpanel,-1,"Add")
		btn2.Bind(wx.EVT_BUTTON,self.OnAdd)
		botsizer.Add(btn,flag=wx.ALL|wx.EXPAND,border=3)
		botsizer.Add(btn2,flag=wx.ALL|wx.EXPAND,border=3)
		botpanel.SetSizer(botsizer)
		sizer.Add(botpanel,flag=wx.ALL|wx.EXPAND,border=3)
		panel.SetSizer(sizer)
		return panel

	def createList(self, parent):
		"""
		Create a list-display of all plugins.
		"""
		list = PluginList(parent, self.plugin_manager, use_versions=self.show_versions)
		if len(list.plugins)!=0:
			list.SetItemState(0, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
		return list
		
	def createPanel(self, plugin_info):
		if plugin_info is None:
			pref = NoPluginPanel(self.splitter,self.plugin_manager)
		else:
			pref = SimplePluginPanel(self.splitter, plugin_info)
		self.panels[None] = pref
		return pref

	def OnItemSelected(self, evt):
		index = evt.GetIndex()
		plugin_info = self.list.getPlugin(index)
		if plugin_info:
			if plugin_info in self.panels:
				pref = self.panels[plugin_info]
			else:
				pref = self.createPanel(plugin_info)
			old = self.splitter.GetWindow2()
			self.splitter.ReplaceWindow(old, pref)
			old.Hide()
			pref.Show()
			pref.Layout()
		evt.Skip()

	def OnItemActivated(self, evt):
		evt.Skip()

	def OnApply(self,event):
		"""
		Apply the activation/deactivation preferences
		"""
		self.applyPreferences()

	def OnAdd(self,event):
		"""
		Start the plugin addition procedure.
		"""
		self.install_a_plugin()
		
	def applyPreferences(self):
		# Look at all the panels that have been created: this gives us
		# an upper bound on what preferences may have changed.
		for plugin, pref in self.panels.iteritems():
			pref.update()

		# After the preferences have been changed, activate or
		# deactivate plugins as required
		self.list.update()
		d = wx.MessageDialog(self,
							 """Changes have been applied.

Please restart for them to take effect.""",
							 "Plugin [de]activations",
							 style=wx.OK | wx.ICON_INFORMATION)
		d.ShowModal()
		d.Destroy()
		

	def install_a_plugin(self):
		"""
		Show dialog to help the user installing new plugins.
		"""
		d = wx.FileDialog(self, 
						  message="Select the plugin to install",
						  wildcard="*.%s" % self.plugin_manager.plugin_info_ext, 
						  style=wx.FD_OPEN)
		ok_cancel = d.ShowModal()
		current_directory = d.Directory
		plugin_info_filename = d.Filename
		d.Destroy()
		if ok_cancel==wx.ID_OK and os.path.isfile(os.path.join(current_directory,plugin_info_filename)):
			install_ok = self.plugin_manager.install(current_directory,plugin_info_filename)
			if not install_ok:
				d = wx.MessageDialog(self,
									 "Sorry, the required plugin could not be installed !",
									 "Plugin installation",
									 style=wx.OK | wx.ICON_ERROR)
				d.ShowModal()
				d.Destroy()
			else:
				self.plugin_manager.collectPlugins()
				self.list.recuperatePlugins()
				self.list.reset()

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)

	sys.path.append(os.path.expanduser("~/src/mathbench/mathbenchdir/trunk"))
	from mathbench.basement import plugin_manager as pman

	PLUGINS_DIR= os.path.expanduser("~/src/mathbench/mathbenchdir/trunk/plugins")
	import ConfigParser
	# create the plugin manager 
	pm = pman.LabPluginManager.get()
	pm.setConfigParser(ConfigParser.ConfigParser(), lambda : True)
	pm.setCategoriesFilter({"Default":pman.IPlugin})
	pm.setPluginPlaces([PLUGINS_DIR])
	pm.setPluginInfoExtension("mathplug")
	# load the plugins
	pm.collectPlugins()

	app = wx.PySimpleApp()

	f = wx.Frame(None,title="Test plugin configuration",size=wx.Size(500,300))
	p = PluginsConfigPanel(parent=f, pm=pm, use_versions=False)
	f.Show(True)

	app.MainLoop()
