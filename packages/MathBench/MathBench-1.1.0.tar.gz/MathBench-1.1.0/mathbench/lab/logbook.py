#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Defines widget that helps you keep a log of what you're experimenting.

"""

import wx
from wx.py.crust import SessionListing


class LogBook(wx.Panel):
	"""
	A facade for the SessionListing widget defined in wx.py
	"""
	
	def __init__(self, parent=None, id=-1):
		"""
		Create a SessionListing widget and wrap it among nice buttons.
		"""
		wx.Panel.__init__(self,parent,id)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.listing = SessionListing(self)
		sizer.Add(self.listing, proportion=1, flag=wx.EXPAND)
		
		button  = wx.Button(self, label="Get into a script")
		self.Bind(wx.EVT_BUTTON, self.OnCreateScript, button)
		sizer.Add(button, proportion=0, border=3, flag= wx.TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER)
		self.SetSizer(sizer)

	def OnCreateScript(self,event):
		"""
		Put the content of the log into a new script.
		"""
		self.log_sink(self.listing.GetString(0,-1))

	def log_sink(self,txt):
		"""
		Print the text on standard output.

		This method here to be overwrittent by external classes that
		want for instance to transform the log into a new file.
		"""
		print txt

	def loadHistory(self, history):
		self.listing.loadHistory(history)

	def addHistory(self, command):
		self.listing.addHistory(command)

	def clearHistory(self):
		self.listing.clearHistory()
