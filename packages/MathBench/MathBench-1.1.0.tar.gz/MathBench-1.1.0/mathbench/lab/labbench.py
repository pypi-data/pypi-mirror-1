#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Inspired by
PyAlaCarte and PyAlaMode editors from WxPython

Combines the shell and filling into one control.
"""

import wx
from wx.py.shell import Shell

# for the session's history
from mathbench.lab.logbook import LogBook
from mathbench.lab.apparatus import ApparatusTree


class LabBench(wx.SplitterWindow):
	"""LabBench based on SplitterWindow."""
	sashoffset = 300

	def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=wx.SP_3D|wx.SP_LIVE_UPDATE,
				 name='LabBench Window', rootObject=None, rootLabel=None,
				 rootIsNamespace=True, intro='', locals=None,
				 InterpClass=None,
				 startupScript=None, execStartupScript=True,
				 *args, **kwds):
		"""Create LabBench instance."""
		wx.SplitterWindow.__init__(self, parent, id, pos, size, style, name)
		self.shell = Shell(parent=self, introText=intro,
						   locals=locals, InterpClass=InterpClass,
						   startupScript=startupScript,
						   execStartupScript=execStartupScript,
						   *args, **kwds)

		self.editor = self.shell
		if rootObject is None:
			rootObject = self.shell.interp.locals

# Maybe one may this could come back ?
#		self.choicebook = wx.Choicebook(parent=self, id=-1)

		self.apparatus = ApparatusTree(parent=self,
								   rootObject=rootObject,
								   rootLabel=rootLabel,
								   rootIsNamespace=rootIsNamespace)
#		self.shell.interp.locals['apparatus'] = self.apparatus
#		self.choicebook.AddPage(page=self.apparatus, text='WorkSpace', select=True)

#		self.logBook = LogBook(parent=self.choicebook)
#		self.shell.interp.locals['history'] = self.logBook
#		self.choicebook.AddPage(page=self.logBook, text='History')
		self.SizeWindows()
		self.SplitVertically(self.apparatus, self.shell, self.sashoffset)
		self.SetMinimumPaneSize(200)

		self.Bind(wx.EVT_SIZE, self.SplitterOnSize)
		self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnChanged)

	
	def OnChanged(self, event):
		"""update sash offset from the bottom of the window"""
		self.sashoffset = self.GetSize().height - event.GetSashPosition()
		event.Skip()
		

	# Make the splitter expand the top window when resized
	def SplitterOnSize(self, event):
		splitter = event.GetEventObject()
		sz = splitter.GetSize()
#		splitter.SetSashPosition(sz.width + self.sashoffset, True)
		event.Skip()
		
	def saveHistory(self):
		"""
		Save the command history in a file.
		"""
		pass
