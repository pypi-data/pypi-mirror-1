#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Inspired by
PyAlaCarte and PyAlaMode editors from wxPython

Combines the lab_bench and offers the possibility to transform the
current work into script files.
"""
import sys

import wx
import wx.lib.dialogs

import wx.py
import wx.py.frame as PyFrame 
import wx.py.dispatcher as dispatcher

from wx.py.editor import *

from labbench import LabBench
import advisor

from mathbench.basement.librarian import LibrarianSingleton

class LabEditorNotebook(EditorNotebook):
	"""
	Very light customisation of the base class
	"""
	def __init__(self,parent,config):
		"""
		Create the instance
		"""
		EditorNotebook.__init__(self,parent)
		self.config = config
		self.parent = parent

	def AddPage(self,page,text="Page",select=False):
		"""
		Also enforce the configuration options for each new element.
		"""
		EditorNotebook.AddPage(self,page,text=text,select=select)
		dispatcher.send(signal='NewPageOnNotebook', sender=self)
	
	
class LabBook(EditorNotebookFrame):
	"""
	LabBook instance that manage all the sutff displayed on screen
	(editors and shells).

	To add the singleton behaviour to a LabBench instance.
	
	implemented in a similar way as in :
	http://www.haypocalc.com/blog/index.php/2006/05/12/3-motifs-de-conception-et-python
	"""	

	# storage for the instance reference
	__instance = None

	# the commant to be executed when the shell starts
	_init_shell_session = []


	def __init__(self, parent=None, id=-1, title='Math Bench', config=None,
				 pos=wx.DefaultPosition, size=(800, 600), 
				 style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE,
				 filename=None):
		"""Create LabBookFrame instance."""
		self.config = config
		EditorNotebookFrame.__init__(self, parent, id, title, pos,
									 size, style, filename)
		self._modify_menus()
		# keep track of the option frame to avoir having two of them
		self.options_frame = None
		# keep track of the shells opened for the exectution of a spectific file
		self.execution_shells = {}
		

	def __new__(cls,parent=None, id=-1, title='Math Bench', config=None,
				 pos=wx.DefaultPosition, size=(800, 600), 
				 style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE,
				 filename=None):
		"""
		Make sure only one instance is ever created
		"""
		if cls.__instance is None:
			cls.__instance = object.__new__(cls)
		return cls.__instance
	
	# now the implementation

	def _init_notebook(self):
		"""
		Create the top level widgets contained by the frame
		"""
		# create the notebook that will hold the shell and editors
		self.notebook = LabEditorNotebook(parent=self,config=self.config)
		dispatcher.connect(receiver=self._newPageOnNotebook,
						   signal='NewPageOnNotebook', sender=self.notebook)
		
	def _init_helpbar(self):
		"""
		Create a toolbar showing some helping options
		"""
		self.helpbar = wx.Panel( self,-1, size=wx.Size(-1,20))
		help_sizer = wx.BoxSizer(wx.HORIZONTAL)
		tb_img_size = (16,16)
		bt_size = (20,20)
		# show library
		img = wx.ArtProvider_GetBitmap(wx.ART_HELP, 
									   wx.ART_TOOLBAR, 
									   tb_img_size)
		btn = wx.BitmapButton(self.helpbar, 50, img)
		btn.SetToolTipString("Show the library desk.")
		self.Bind(wx.EVT_BUTTON, self.OnHelpToolClick, id=50)
		help_sizer.Add(btn,proportion=0,border=3,flag=wx.ALL)

		# search query widget
		dummylongtext = wx.StaticText(self.helpbar,-1,"mathbench.basement.configuration.py")
		dummylongtext.Fit()
		nice_width = dummylongtext.GetBestSize().width
		dummylongtext.Hide()
		self.query_widget = wx.TextCtrl(name='query', 
										parent=self.helpbar, 
										size=wx.Size(nice_width,-1))
		self.query_widget.SetToolTipString("Press 'Enter' to launch the search")
		self.query_widget.Bind(wx.EVT_KEY_DOWN,self.OnQueryKeyDown)
		help_sizer.Add(self.query_widget,proportion=1,flag=wx.EXPAND | wx.ALL, border=3)

		# delete button
		img = wx.ArtProvider_GetBitmap(wx.ART_DELETE, 
									   wx.ART_TOOLBAR, 
									   tb_img_size)
		btn = wx.BitmapButton(self.helpbar, 30, img)
		btn.SetToolTipString("Clear the search form.")
		self.Bind(wx.EVT_BUTTON, self.OnHelpToolClick, id=30)
		help_sizer.Add(btn,proportion=0,border=3,flag=wx.ALL)
		self.helpbar.SetSizer(help_sizer)

		# search button
		img = wx.ArtProvider_GetBitmap(wx.ART_FIND, 
									   wx.ART_TOOLBAR, 
									   tb_img_size)
		btn = wx.BitmapButton(self.helpbar,35, img)
		btn.SetToolTipString("Search the documentation.")
		self.Bind(wx.EVT_BUTTON, self.OnHelpToolClick, id=35)
		help_sizer.Add(btn,proportion=0,border=3,flag=wx.ALL)

		self.helpbar.SetSizer(help_sizer)

	def _init_shell_widget(self):
		"""
		Create the widget that will be used as the main shell
		"""
		import imp
		module = imp.new_module('__main__')
		import __builtin__
		module.__dict__['__builtins__'] = __builtin__
		namespace = module.__dict__.copy()
		intro = "Welcome in MathBench"
		self.labBench = LabBench(parent=self.notebook, intro=intro, locals=namespace)
		self.shell = self.labBench.shell
		
		
	def _setup(self):
		"""
		Setup prior to first buffer creation.

		Called automatically by base class during init.
		"""
		sizer = wx.BoxSizer(wx.VERTICAL)
		# create the base widgets
		self._init_notebook()
		sizer.Add(self.notebook,proportion=1,flag=wx.EXPAND)
		# create the help bar
		self._init_helpbar()
		sizer.Add(self.helpbar,proportion=0,flag=wx.EXPAND)
		self.SetSizer(sizer)
		# create the shell
		self._init_shell_widget()
		# Override the logBook so that status messages go to the status bar.
		self.labBench.logBook.setStatusText = self.SetStatusText
		# And tell the logBook to use our sink when the user wants to extract the log
		self.labBench.logBook.log_sink = self.log_sink_to_file
		# Override the shell so that status messages go to the status bar.
		self.shell.setStatusText = self.SetStatusText
		# make sure the std::cout & co are shown in the shell
		self.shell.redirectStdout(True)
		self.shell.redirectStderr(True)
		# Fix a problem with the sash shrinking to nothing.
		self.notebook.AddPage(page=self.labBench, text='*Shell*', select=True)
		self.setEditor(self.labBench.editor)
		# make sure the shell gets the focus
		wx.CallAfter(self.shell.SetFocus)
		# launch session initialisation
		self.init_worksession()

	def _newPageOnNotebook(self,):
		"""
		When a new page is added perform some necessary checking and
		settings.
		"""
		page_nb = self.notebook.GetPageCount()
		if page_nb>1:
			self.enforce_options(self.notebook.GetPage(page_nb-1).editor.window)
		else:
			# this is the shell 
			self.enforce_options(self.shell)

	def init_worksession(self):
		"""
		Put here the functions to call at the begining of the working
		session of the shell.
		
		This is separated from the init function, so that anybody can
		overwrite the content of this function.
		"""
		for cmd_str in LabBook._init_shell_session:
			self.shell.run(cmd_str)

	def enforce_options(self,window):
		"""
		Enforce the choices the user made with the options.
		"""
		if self.config is None:
			return
		# set the options relative to autocompletion
		section_name = "Auto Completion"
		if self.config.has_section(section_name):
			window.autoComplete = (self.config.get(section_name,"Show_Auto_Completion")=="1")
			window.autoCompleteIncludeMagic = (self.config.get(section_name,"Include_Magic_Attributes")=="1")
			window.autoCompleteIncludeSingle = (self.config.get(section_name,"Include_Single_Underscores")=="1")
			window.autoCompleteIncludeDouble = (self.config.get(section_name,"Include_Double_Underscores")=="1")
		# set the options relative to autocompletion
		section_name = "Call Tips"
		if self.config.has_section(section_name):
			window.autoCallTip = (self.config.get(section_name,"Show_Call_Tips")=="1")
			window.callTipInsert = (self.config.get(section_name,"Insert_Call_Tips")=="1")
		# set the options relative to the view
		section_name = "View"
		if self.config.has_section(section_name):
			window.SetWrapMode((self.config.get(section_name,"Wrap_Lines")=="1"))
			wx.FutureCall(1, self.shell.EnsureCaretVisible)
			window.lineNumbers = (self.config.get(section_name,"Show_Line_Numbers")=="1")
			window.setDisplayLineNumbers(window.lineNumbers)

	def _modify_menus(self):
		"""
		Change a little the menus
		"""
		# File Menu
		m = self.fileMenu
		m.SetTitle("Script")
		ID_EXECUTE = wx.NewId()
		m.Append(ID_EXECUTE, '&Execute \tCtrl+e',
				 'Execute the script in a new shell')
		ID_EXECUTE_MAIN = wx.NewId()
		m.Append(ID_EXECUTE_MAIN, '&Execute in main shell \tShift+Ctrl+e',
				 'Execute the script in the main shell')

		# Options Menu
		m = self.optionsMenu
		m.SetTitle("Tools")
		if wx.Platform == "__WXMAC__":
			m.Remove(PyFrame.ID_USEAA)
		# remove Py stuff that we don't want
		m.Remove(m.FindItem("History"))
		m.Remove(m.FindItem("Startup"))
		m.Remove(m.FindItem("Settings"))
		# add preference menu
		ID_PREFERENCE = wx.NewId()
		if wx.Platform == "__WXMAC__":
			wx.App.SetMacPreferencesMenuItemId(ID_PREFERENCE)
		else:
			m.AppendSeparator()
		m.Append(ID_PREFERENCE,"&Preferences", 
				 "Open the preference panel")

		# Help menu
		m = self.helpMenu
		ID_LIBRARY = wx.NewId()
		m.Append(ID_LIBRARY,"&Library desk",
				 "Show the library desk and its useful pointers")
# 		ID_ABOUT = wx.NewId()
# 		m.Append(ID_ABOUT,"&About", 
# 				 "About this software")
# 		if wx.Platform == "__WXMAC__":
# 			wx.App.SetMacAboutMenuItemId(ID_ABOUT)

		# Bindings
		self.Bind(wx.EVT_MENU, self.OnExecute, id=ID_EXECUTE)
		self.Bind(wx.EVT_MENU, self.OnExecuteInMainShell, id=ID_EXECUTE_MAIN)
		self.Bind(wx.EVT_MENU, self.OnPreference, id=ID_PREFERENCE)
#   		self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_ABOUT)
		self.Bind(wx.EVT_MENU, self.OnLibrary, id=ID_LIBRARY)
		self.Bind(wx.EVT_CLOSE, self.OnClose)

	def log_sink_to_file(self, text):
		"""
		Create a new file from the given text
		"""
		self.bufferNew()		
		self.editor.setText(text)

	def OnClose(self,event):
		"""
		Close everything and don't let a creepy plugin hold the end of the app.
		"""
		sys.exit(0)

	def OnHelp(self,event):
		"""
		Display a small helpign text
		"""
		msg = """Code samples and documentation are available at the library desk
(accessible at the bottom of the application's window).

Shortcut keys for the shell are listed below: 
(also accessible by typing shell.help())

%s
""" % wx.py.shell.HELP_TEXT
		dlg =wx.lib.dialogs.ScrolledMessageDialog(self, msg, "Help about Mathbench")
		dlg.Show()

	def OnAbout(self, event):
		"""Display an About window."""
		title = 'MathBench'
		text = """
Not a whole laboratory, just a small bench'

That is: another fine, flaky program for lazy  scientists :)

Written by Thibauld Nion
And heavily based on wxPython's py library.
"""
		dialog = wx.MessageDialog(self, text, title,
								  wx.OK | wx.ICON_INFORMATION)
		dialog.ShowModal()
		dialog.Destroy()

	def OnLibrary(self,event):
		"""
		Show the library desk
		"""
		LibrarianSingleton.popup()


	def OnExecute(self,event):
		"""
		Execute the script in a new shell frame.
		"""
		script_filepath = self.editor.buffer.doc.filepath
		if self.execution_shells.has_key(script_filepath):
			execframe = self.execution_shells[script_filepath]
		else:
			# create a new shell
			execframe = wx.py.shell.ShellFrame()
			self.execution_shells[script_filepath] = execframe
			def OnCloseExecShell(event):
				"""
				remove any reference to this shell
				"""
				self.execution_shells.pop(script_filepath)
				event.Skip()
			execframe.Bind(wx.EVT_CLOSE,OnCloseExecShell)
			# don't want the history of this new shell to be recorded 
			execframe.shell.addHistory = lambda x: None
		# amke sure the window is visible
		execframe.Hide()
		execframe.Show()
		# exec the file (maybe there is a cleaner way to do this ?)
		execframe.shell.run("execfile('%s')" % script_filepath)

	def OnExecuteInMainShell(self,event):
		"""
		Execute the script in the main shell.
		"""
		filepath = self.editor.buffer.doc.filepath
		self.notebook.SetSelection(0)
		# exec the file (maybe there is a cleaner way to do this ?)
		self.shell.run("execfile('%s')" % filepath)

	def OnPreference(self,event):
		"""
		Show the preference panel
		"""
		if self.options_frame is None:
			self.options_frame = advisor.OptionsFrame(self,self.config)
			dispatcher.connect(signal='OptionsChanged',
							   receiver=self._onOptionsChanged,sender=self.options_frame)
			dispatcher.connect(signal="OptionsClosed", 
							   receiver=self._onOptionsClosed,sender=self.options_frame)
		else:
			self.options_frame.Hide()
			self.options_frame.Show()
		
	def _onOptionsChanged(self):
		"""
		Take into accout a change in the options
		"""
		# this is the shell 
		self.enforce_options(self.shell)
		for page_id in range(1,self.notebook.GetPageCount()):
			self.enforce_options(self.notebook.GetPage(page_id).editor.window)

	def _onOptionsClosed(self):
		"""
		Remove the reference to the options frame
		"""
		self.options_frame = None

	def OnHelpToolClick(self,event):
		"""
		When the user clicks on the helpbar, find which button has
		been clicked and act !
		"""
		eid = event.GetId()
		if eid==30: #< Clear
			self.query_widget.Clear()
		elif eid==35: #< Search
			LibrarianSingleton.search(self.query_widget.GetValue())
		elif eid==50: #< Desk
			LibrarianSingleton.popup()
		else:
			raise Exception("Event from unknown source!")


	def OnQueryKeyDown(self,event):	
		"""
		When user clicks on enter while typing in the query widget,
		then launch the search !
		"""
		if event.GetKeyCode() == wx.WXK_RETURN:
			LibrarianSingleton.search(self.query_widget.GetValue())
		event.Skip()

	# --- Static interface
	# class/static methods easily accessible by the plugins for
	# instance

	def initShellSessionAppend(self,cmd_str):
		"""
		Add a command to be executed at session init.
		"""
		self._init_shell_session.append(cmd_str)
	initShellSessionAppend = classmethod(initShellSessionAppend)

	
