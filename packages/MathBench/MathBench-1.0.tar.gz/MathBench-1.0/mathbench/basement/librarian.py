#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Management of the documentation of mathbench and its plugins.
"""

import os 
import logging
import re

import wx.py.dispatcher as dispatcher

def DefangHTML(txt):
	"""
	Defang html symbols.
	
	Inspired from :
	http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81330
	"""
	symbol_dict = {
		"&"  : "&amp;",
		">"  : "&gt;",
		"<"  : "&lt;",
		"é"  : "&eacute;",
		"è"  : "&egrave;",
		"à"  : "&agrave;",
		"\n" : " \n<br>",
		}
	re_match_pattern = "(%s)" % "|".join( map(re.escape, symbol_dict.keys())  )
	return re.sub( re_match_pattern, lambda m:symbol_dict[m.group()], txt )
	

class LibrarianSingleton(object):
	"""
	A singleton class in charge of building, updating the library
	and also performing the searches.

	The librarian is in charge of creating the library desk display
	and then must be informed of which DeskFacory to use to create
	this desk.

	The display widget created must also send a 'LibraryDeskClosed'
	signal when it is closed.
	"""
		
	__instance = None
	
	def __init__(self):
		"""
		Initialisation: this class should not be initialised
		explicitly and the ``get``classmethod must be called instead.
		"""
		if self.__instance is not None:
			raise Exception("Singleton can't be created twice !")
		self.__search_methods = {}
		self.__desk_factory = None
		self.__desk = None

	def show(self,txt):
		"""
		Show the results in a frame.
		"""
		if self.__desk==None:
			self.__desk = self.__desk_factory()
			dispatcher.connect(receiver=self._desk_closed,
							   signal='LibraryDeskClosed', sender=self.__desk)

		self.__desk.showPage(txt)

	def _desk_closed(self):
		"""
		When the desk is closed
		"""
		self.__desk = None

	def compile_results(self,search_query):
		"""
		Compile the search results in a unique html page.
		"""
		# Init the html file description
		search_res = ["""\
<html>
<title>Search results</title>

<body>
<H1> Search results for "%s" </H1>
<br>""" % search_query
]
		temp_search_res = []
		# browse each context and ask for results
		for context in self.__search_methods.keys():
			res_list = self.__search_methods[context](search_query)
			if len(res_list)==0:
				continue
			else:
				# when results have been found display them as list
				temp_search_res.append("""\
<br>
<H2>From %s</H2>
<br>
<ul>""" % DefangHTML(context))
				for item in res_list:
					temp_search_res.append("""\
<li><a href='%s'>%s</a></li>
<br>""" % item)
				# finish the list
				temp_search_res.append("""\
</ul>
<br>""")
				
		if len(temp_search_res)==0:
			search_res = ["""\
<html>
<title>Search results</title>

<body>
<H1> Sorry, no result for "%s" </H1>
<br>""" % search_query
]
		else:
			search_res.extend(temp_search_res)
		
		# At the very end close the document
		search_res.append("""\
</body>
</html>
""")
		return os.linesep.join(search_res)


	def show_welcome(self):
		"""
		Display the welcome text in a widget
		"""
		welcome_txt = """\
<html>

<title>Welcome</title>

<body>

<H1> Library Desk </H1>

<H2> About this desk</H2>

If you're looking for a precise answer, you may enter a search query
in the text area of the toolbar, press "Enter" (on your keyboard) and
the available answers will be shown to you.

<br>
<br>

Please also note that this viewer is buggy with external websites,
hence you should prefer going to online websites with your own
webbrowser.


<H2> About Python </H2>

<H3> References</H3>
<ul>
  <li><a href="http://python.org">Python language</a> 
<pre>http://python.org</pre></li>
  <li><a href="http://docs.python.org/modindex.html">Modules index</a> 
<pre>http://docs.python.org/modindex.html</pre></li>
  <li><a href="http://starship.python.net/crew/theller/pyhelp.cgi">Online search</a> 
<pre>http://starship.python.net/crew/theller/pyhelp.cgi</pre></li>
</ul>

<H3>Quick introductions</H3>
<ul>
  <li><a href="http://docs.python.org/tut/tut.html">Python tutorial</a> 
<pre>http://docs.python.org/tut/tut.html</pre></li>
  <li><a href="http://wiki.python.org/moin/SimplePrograms">Simple code samples</a> 
<pre>http://wiki.python.org/moin/SimplePrograms</pre></li>
</ul>

<H2> About Mathbench</H2>

<ul>
  <li><a href="http://mathbench.sourceforge.net/mathbench/doc/presentation.html">Mathbench Project</a> 
<pre>http://mathbench.sourceforge.net</pre></li>
</ul>

</body>
 
</html>
"""
		self.show(welcome_txt)

	def setSearchMethod(self,search_method,context_name):
		"""
		Set the search method
		"""
		self.__search_methods[context_name] = search_method
		
	def record_search(self,txt):
		"""
		Record the previous search items
		"""
		self.__desk.addToHistory(txt)

	#--- CLASS METHODS

	def get(self):
		"""
		Actually create an instance
		"""
		if self.__instance is None:
			self.__instance = LibrarianSingleton()	
			logging.debug("LibrarianSingleton initialised")
		return self.__instance
	get = classmethod(get)

	def register(self,search_method,context_name):
		"""
		Register a search method for a specific context (usually the
		library imported by a precise plugin.)
		"""
		librarian = self.get()
		librarian.setSearchMethod(search_method,context_name)
		logging.debug("Adding the search method from %s to the LibrarianSingleton" % context_name)
	register = classmethod(register)

	def setDeskFactory(self,desk_factory):
		"""
		Set the factory that will be in charge of creating the desk
		(ie the widget displaying the search results)
		"""
		librarian = self.get()
		librarian.__desk_factory = desk_factory
	setDeskFactory = classmethod(setDeskFactory)


	def search(self,search_query):
		"""
		Return a HTML formated text providing links to all the search results.
		"""
		if search_query.strip() == "":
			return
		librarian = LibrarianSingleton.get()
		search_res = librarian.compile_results(search_query)
		librarian.show(search_res)
		librarian.record_search(search_query)
	search = classmethod(search)

	def welcome(self):
		"""
		Display a welome page
		"""
		librarian = LibrarianSingleton.get()
		librarian.show_welcome()
	welcome = classmethod(welcome)
	

	def popup(self):
		"""
		Put the desk on top of the other frames
		"""
		librarian = self.get()
		if librarian.__desk is None:
			self.welcome()
		else:
			librarian.__desk.Show(False)
			librarian.__desk.Show(True)
	popup = classmethod(popup)






