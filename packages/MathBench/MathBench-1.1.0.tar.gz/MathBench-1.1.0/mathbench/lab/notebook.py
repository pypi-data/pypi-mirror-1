#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Inspired by
PyAlaCarte and PyAlaMode editors from wxPython

Combines the lab_bench and offers the possibility to transform the
current work into script files.
"""

import sys
import os

import wx
import wx.lib.dialogs

import wx.py
import wx.py.frame as PyFrame 
import wx.py.dispatcher as dispatcher

from wx.py.editor import *

from mathbench.basement.history_manager import HistoryManager

from mathbench.lab.labbench import LabBench
import mathbench.lab.advisor as advisor

from mathbench.basement.librarian import LibrarianSingleton

ID_EXECUTE = wx.NewId()
ID_EXECUTE_MAIN = wx.NewId()
ID_PREFERENCE = wx.NewId()
ID_LIBRARY = wx.NewId()
ID_HISTORY_TO_SCRIPT = wx.NewId()
ID_LOAD_OLD_SESSION = wx.NewId()


from wx.html import HtmlEasyPrinting

class Printer(HtmlEasyPrinting):
	"""
	Small printing class taken from: http://wiki.wxpython.org/Printing
	"""
	def __init__(self):
		HtmlEasyPrinting.__init__(self)

	def GetHtmlText(self,text):
		"Simple conversion of text.	 Use a more powerful version"
		html_text = text.replace('\n', '<BR>')
		return html_text

	def Print(self, text, doc_name):
		self.SetHeader(doc_name)
		self.PrintText(self.GetHtmlText(text),doc_name)

	def PreviewText(self, text, doc_name):
		self.SetHeader(doc_name)
		HtmlEasyPrinting.PreviewText(self, self.GetHtmlText(text))

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


	def __init__(self, parent=None, id=-1, title='MathBench', 
				 config=None,
				 pos=wx.DefaultPosition, size=(800, 600), 
				 style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE,
				 filename=None, history_dir=None):
		"""Create LabBookFrame instance."""
		self.config = config
		self.history_dir = history_dir
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
				 filename=None, history_dir=None):
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
		art_prov = wx.ArtProvider()
		# show library
		img = art_prov.GetBitmap(wx.ART_HELP_BOOK, 
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
		img = art_prov.GetBitmap(wx.ART_DELETE, 
								 wx.ART_TOOLBAR, 
								 tb_img_size)
		btn = wx.BitmapButton(self.helpbar, 30, img)
		btn.SetToolTipString("Clear the search form.")
		self.Bind(wx.EVT_BUTTON, self.OnHelpToolClick, id=30)
		help_sizer.Add(btn,proportion=0,border=3,flag=wx.ALL)
		self.helpbar.SetSizer(help_sizer)

		# search button
		img = art_prov.GetBitmap(wx.ART_FIND, 
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
		# if a directory to put the session files in is provided, then
		# instanciate a History manager.
		if self.history_dir is not None:
			self.historyman = HistoryManager(self.shell, self.history_dir)	
			dispatcher.connect(receiver=self.historyman.save_current_session, signal='LabBook.close')
			self.historyman.load_latest_session()
			self.historyman.put_landmark()
		
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
# 		# Override the logBook so that status messages go to the status bar.
# 		self.labBench.logBook.setStatusText = self.SetStatusText
# 		# And tell the logBook to use our sink when the user wants to extract the log
# 		self.labBench.logBook.log_sink = self.log_sink_to_file
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
		Recreate the menus, overwritting what has been done in the
		wx/py/frame.py
		"""
		art_prov = wx.ArtProvider()
		# Remove predefined menus
		for i in reversed(range(self.menuBar.GetMenuCount())):
			self.menuBar.Remove(i)
		# File Menu
		m = self.fileMenu = wx.Menu()
		m.Append(PyFrame.ID_NEW, '&New \tCtrl+N',
				 'New file')
		m.Append(PyFrame.ID_OPEN, '&Open... \tCtrl+O',
				 'Open file')
		m.AppendSeparator()
		m.Append(PyFrame.ID_REVERT, '&Revert \tCtrl+R',
				 'Revert to last saved version')
		m.Append(PyFrame.ID_CLOSE, '&Close \tCtrl+W',
				 'Close file')
		m.AppendSeparator()
		m.Append(PyFrame.ID_SAVE, '&Save... \tCtrl+S',
				 'Save file')
		m.Append(PyFrame.ID_SAVEAS, 'Save &As \tCtrl+Shift+S',
				 'Save file with new name')
		m.AppendSeparator()
		m.Append(PyFrame.ID_PRINT, '&Print... \tCtrl+P',
				 'Print file')
		m.AppendSeparator()
		m.Append(ID_HISTORY_TO_SCRIPT, 'Session &To Script',
				 "Create a script from the session's history")
		m.Append(ID_LOAD_OLD_SESSION, "Recover &Older Session",
				 'Load (and exectute) the history of a previous session')		
		m.AppendSeparator()
		m.Append(ID_EXECUTE, '&Execute \tF9',
				 'Execute the script in a new shell')
		m.Append(ID_EXECUTE_MAIN, 'Execute in &main shell \tShift+F9',
				 'Execute the script in the main shell')
		m.Append(PyFrame.ID_NAMESPACE, '&Update Namespace \tCtrl+Shift+N',
				 'Update namespace for autocompletion and calltips')
		m.AppendSeparator()
		m.Append(PyFrame.ID_EXIT, 'E&xit\tCtrl+Q', 'Exit Program')

		# Edit
		m = self.editMenu = wx.Menu()
		m.Append(PyFrame.ID_UNDO, '&Undo \tCtrl+Z',
				 'Undo the last action')
		m.Append(PyFrame.ID_REDO, '&Redo \tCtrl+Y',
				 'Redo the last undone action')
		m.AppendSeparator()
		m.Append(PyFrame.ID_CUT, 'Cu&t \tCtrl+X',
				 'Cut the selection')
		m.Append(PyFrame.ID_COPY, '&Copy \tCtrl+C',
				 'Copy the selection')
		m.Append(PyFrame.ID_COPY_PLUS, 'Cop&y Plus \tCtrl+Shift+C',
				 'Copy the selection - retaining prompts')
		m.Append(PyFrame.ID_PASTE, '&Paste \tCtrl+V', 'Paste from clipboard')
		m.Append(PyFrame.ID_PASTE_PLUS, "Past&e'n'run \tCtrl+Shift+V",
				 'Paste and run commands')
		m.AppendSeparator()
		m.Append(PyFrame.ID_EMPTYBUFFER, 'E&mpty Buffer...',
				 'Delete all the contents of the edit buffer')
		m.Append(PyFrame.ID_SELECTALL, 'Select A&ll \tCtrl+A',
				 'Select all text')
		if wx.Platform == '__WXGTK__':
			m.AppendSeparator()
			m.Append(ID_PREFERENCE,"&Preferences", 
					 "Open the preference panel")

		# View
		m = self.autocompMenu = wx.Menu()
		m.Append(PyFrame.ID_AUTOCOMP_SHOW, 'Show &Auto Completion\tCtrl+Shift+A',
				 'Show auto completion list', wx.ITEM_CHECK)
		m.Append(PyFrame.ID_AUTOCOMP_MAGIC, 'Include &Magic Attributes\tCtrl+Shift+M',
				 'Include attributes visible to __getattr__ and __setattr__',
				 wx.ITEM_CHECK)
		m.Append(PyFrame.ID_AUTOCOMP_SINGLE, 'Include Single &Underscores\tCtrl+Shift+U',
				 'Include attibutes prefixed by a single underscore', wx.ITEM_CHECK)
		m.Append(PyFrame.ID_AUTOCOMP_DOUBLE, 'Include &Double Underscores\tCtrl+Shift+D',
				 'Include attibutes prefixed by a double underscore', wx.ITEM_CHECK)
		m = self.calltipsMenu = wx.Menu()
		m.Append(PyFrame.ID_CALLTIPS_SHOW, 'Show Call &Tips\tCtrl+Shift+T',
				 'Show call tips with argument signature and docstring', wx.ITEM_CHECK)
		m.Append(PyFrame.ID_CALLTIPS_INSERT, '&Insert Call Tips\tCtrl+Shift+I',
				 '&Insert Call Tips', wx.ITEM_CHECK)

		m = self.viewMenu = wx.Menu()
		m.AppendMenu(PyFrame.ID_AUTOCOMP, '&Auto Completion', self.autocompMenu,
					 'Auto Completion Options')
		m.AppendMenu(PyFrame.ID_CALLTIPS, '&Call Tips', self.calltipsMenu,
					 'Call Tip Options')
		m.Append(PyFrame.ID_WRAP, '&Wrap Lines\tCtrl+Shift+W',
				 'Wrap lines at right edge', wx.ITEM_CHECK)
		m.Append(PyFrame.ID_SHOW_LINENUMBERS, '&Show Line Numbers\tCtrl+Shift+L', 'Show Line Numbers', wx.ITEM_CHECK)
		m.AppendSeparator()
		m.Append(PyFrame.ID_TOGGLE_MAXIMIZE, '&Toggle Maximize\tF11', 'Maximize/Restore Application')
		# add library menu
		if wx.Platform == '__WXMAC__':
			m.AppendSeparator()
			m.Append(ID_LIBRARY,"&Library desk",
					 "Show the library desk and its useful pointers")
			m.Append(PyFrame.ID_HELP, '&Help\tF1', 'Help!')
        		m.Append(PyFrame.ID_ABOUT, '&About...', 'About this program')
		if wx.Platform != '__WXGTK__':
			if wx.Platform == '__WXMAC__':
				wx.App.SetMacPreferencesMenuItemId(ID_PREFERENCE)
			m.Append(ID_PREFERENCE,"&Preferences", 
					 "Open the preference panel")

		# Search
		m = self.searchMenu = wx.Menu()
		m.Append(PyFrame.ID_FIND, '&Find Text... \tCtrl+F',
				 'Search for text in the edit buffer')
		m.Append(PyFrame.ID_FINDNEXT, 'Find &Next \tF3',
				 'Find next/previous instance of the search text')

		# Help menu (with a workaround for mac...)
		m = self.helpMenu = wx.Menu()
		m.Append(PyFrame.ID_HELP, '&Help\tF1', 'Help!')
		if wx.Platform != "__WXMAC__":
			m.AppendSeparator()
			m.Append(ID_LIBRARY,"&Library desk",
					 "Show the library desk and its useful pointers")
			m.AppendSeparator()
        		m.Append(PyFrame.ID_ABOUT, '&About...', 'About this program')

		b = self.menuBar
		b.Append(self.fileMenu, '&Script')
		b.Append(self.editMenu, '&Edit')
		b.Append(self.viewMenu, '&View')
		b.Append(self.searchMenu, '&Search')
		if wx.Platform != "__WXMAC__":
			b.Append(self.helpMenu, '&Help')

		# Bindings
		self.Bind(wx.EVT_MENU, self.OnExecute, id=ID_EXECUTE)
		self.Bind(wx.EVT_MENU, self.OnExecuteInMainShell, id=ID_EXECUTE_MAIN)
		self.Bind(wx.EVT_MENU, self.OnPreference, id=ID_PREFERENCE)
		self.Bind(wx.EVT_MENU, self.OnLibrary, id=ID_LIBRARY)
		self.Bind(wx.EVT_MENU, self.OnHistoryToScript, id=ID_HISTORY_TO_SCRIPT)		
 		self.Bind(wx.EVT_MENU, self.OnLoadOldSession, id=ID_LOAD_OLD_SESSION)		
		self.shell.Bind(wx.EVT_CLOSE, self.OnClose)		

	def _checkCurrentBufferSaved(self,title="Savind required"):
		"""
		Check is the content of the current buffer has been saved (at
		its latest version).
		"""
		if not self.bufferHasChanged():
			return True
		else:
			d = wx.MessageDialog(self,u'You need to save the script first.\nDo you want to do is now ?',u'%s'%title, wx.YES_NO | wx.ICON_WARNING)
			yes_no = d.ShowModal()
			if yes_no != wx.ID_YES:
				return False
			cancel = self.bufferSave()
			return not cancel

	def _editorChange(self, editor):
		"""
		When the editor change, update the menu options.
		"""
		EditorNotebookFrame._editorChange(self,editor)
		# enable/disable menu items that make sense
		if isinstance(editor,wx.py.shell.Shell):
			self.fileMenu.Enable(ID_EXECUTE,False)
			self.fileMenu.Enable(ID_EXECUTE_MAIN,False)
			self.fileMenu.Enable(ID_HISTORY_TO_SCRIPT,True)
			self.fileMenu.Enable(ID_LOAD_OLD_SESSION,True)
		else:
			self.fileMenu.Enable(ID_EXECUTE,True)
			self.fileMenu.Enable(ID_EXECUTE_MAIN,True)		
			self.fileMenu.Enable(ID_HISTORY_TO_SCRIPT,False)
			self.fileMenu.Enable(ID_LOAD_OLD_SESSION,False)
	
	def log_sink_to_file(self, text):
		"""
		Create a new file from the given text
		"""
		self.bufferNew()		
		self.editor.setText(text)

	def bufferNew(self):
		"""
		Create new buffer.
		
		This method is redefined only to include a workaround for 
		bug#1752674
		"""
		cancel = EditorNotebookFrame.bufferNew(self)
		if not cancel:
			self.editor.buffer.overwriteConfirm = lambda s,filepath=None: True
			self.editor.buffer.confirmed = False
		return cancel

	def bufferPrint(self):
		"""
		printing ability
		"""
		printer = Printer()
		if isinstance(self.editor,wx.py.shell.Shell):
			printer.Print(self.editor.GetText(),
						  "*Shell*")
		else:
			printer.Print(self.editor.getText(),
						  self.editor.buffer.name)
			
	
	def OnClose(self,event):
		"""
		Close everything and don't let a creepy plugin hold the end of the app.
		"""
		dispatcher.send(signal="LabBook.close")
		sys.exit(0)

	def OnHelp(self,event):
		"""
		Display a small helpign text
		"""
		msg = """\
Basic usage
-----------

  1) type and execute a few commands in the shell

  2) ask for this commands to be transformed into a plain script file
    (via the menu "Script"->"Session To script")

  3) edit the script

  4) execute it with Script->Execute

  5) save it when you're done !

and later on...

  - open an existing script and edit it

  - restart an old shell session (see "Script"->"Recover Old Session")

Search for documentation
------------------------

Code samples and documentation are available at the library desk:

  - type a query at the bottom of the application's window

or

  - launch the desk via the menu "Help"->"Library Desk"


Shortcut keys
-------------

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
		if not self._checkCurrentBufferSaved():
			return
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
		# exec the file
#		execframe.shell.run("execfile('%s')" % script_filepath)
		execframe.shell.runfile(script_filepath)

	def OnExecuteInMainShell(self,event):
		"""
		Execute the script in the main shell.
		"""
		if not self._checkCurrentBufferSaved():
			return
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


	def OnHistoryToScript(self,event):
		"""
		Pass the shell's history to a new script.
		"""
		txtL = self.historyman.get_history_from_landmark()
		txtL.reverse()
		script = os.linesep.join(txtL)
		return self.log_sink_to_file(script)
		
		
	def OnLoadOldSession(self,event):
		"""
		Load an older session from its history file.
		"""
		d = wx.FileDialog(self,"Please chose a session to load",self.history_dir,
						  wildcard="*.session", style=wx.FD_OPEN)
		ok_cancel = d.ShowModal()
		path = d.GetPath()
		d.Destroy()
		if ok_cancel==wx.ID_OK and os.path.isfile(path):
			f = open(path)
			txt = f.read()
			txtL = txt.split(self.historyman.COMMANDS_SEPARATOR)
			txtL.reverse()
# 			print txtL
			sesname = os.path.splitext(os.path.basename(path))[0]
			self.shell.run("# Recovering session: %s" % sesname)
#   			for c in txtL:
#  				self.shell.run(c)
  			self.shell.Execute("\n\n".join(txtL))


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

	
