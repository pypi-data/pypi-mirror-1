#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Define configuration options and panel for the Pylab plugin
"""

PYLAB_DEFAULT_OPTIONS="""
text.usetex: 0
text.latex.unicode: 0
"""

import wx
from matplotlib import rc


class PylabConfigurator(object):
	"""
	Class handling pylab's configuration
	"""
	
	def __init__(self,parent_plugin):
		"""
		Save parent plugin object to acess its configuration i/o methods
		"""
		self.parent_plugin =  parent_plugin
		# check that the options are already there
		if not self.parent_plugin.hasConfigOption("text.usetex"):
			self.parent_plugin.setConfigOption("text.usetex","0")
		if not self.parent_plugin.hasConfigOption("text.latex.unicode"):
			self.parent_plugin.setConfigOption("text.latex.unicode","0")
		# now apply the configuration options
		opt = self.parent_plugin.getConfigOption("text.usetex")
		rc('text', usetex=(opt=="1"))
		opt = self.parent_plugin.getConfigOption("text.latex.unicode")
		rc('text',**{'latex.unicode':(opt=="1")})
		self.opt_dict = {"Use LaTeX for all text":"text.usetex",
						 "Ask LaTeX to handle unicode strings":"text.latex.unicode"}
		# remember the config frame
		self._cframe = None

	def show_config_widget(self,parent):
		"""
		Show a configuration widget
		"""
		if self._cframe is not None:
			self._cframe.Show(False)
			self._cframe.Show(True)

		
		f = wx.Frame(parent,-1,"Pylab configuration")
		sizer = wx.BoxSizer(wx.VERTICAL)
		txt = wx.StaticText(f,-1,"""Please check your prefered options.
They will be taken into account for next session""")
		sizer.Add(txt,proportion=0,flag=wx.EXPAND|wx.ALL,border=3)
		
		opt_list = self.opt_dict.keys()
		f.lb = wx.CheckListBox(f, -1,choices=opt_list)
		for i in range(len(opt_list)):
			option_name = self.opt_dict[opt_list[i]]
			f.lb.Check(i,check=(self.parent_plugin.getConfigOption(option_name)=="1"))
		sizer.Add(f.lb,proportion=1,flag=wx.EXPAND,border=3)
		f.SetSizer(sizer)
		f.Bind(wx.EVT_CLOSE,self.OnFrameClose)
		self._cframe=f
		f.Show()

	def OnFrameClose(self,event):
		"""
		When the config frame is closed
		"""
		nb_items = self._cframe.lb.GetCount()
		for i in range(nb_items):
			option_label = self._cframe.lb.GetString(i)
			if self._cframe.lb.IsChecked(i):
				self.parent_plugin.setConfigOption(self.opt_dict[option_label],"1")
			else:
				self.parent_plugin.setConfigOption(self.opt_dict[option_label],"0")
		# delete ref to the frame
		self._cframe = None
		event.Skip()
