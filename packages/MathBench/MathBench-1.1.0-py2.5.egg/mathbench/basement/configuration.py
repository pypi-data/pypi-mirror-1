#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
The tools to save/load/use the user's customisations.
"""
import sys
import os
from ConfigParser import SafeConfigParser
		
import wx
import wx.py.dispatcher as dispatcher

MB_DEFAULT_OPTIONS="""
[Auto Completion]
Show_Auto_Completion = 1
Include_Magic_Attributes = 1
Include_Single_Underscores = 1
Include_Double_Underscores = 0

[Call Tips]
Show_Call_Tips = 1
Insert_Call_Tips = 1

[View]
Wrap_Lines = 1
Show_Line_Numbers = 1

[Development]
Verbosity_Level = INFO
"""

class MathBenchConfig(SafeConfigParser):
	"""
	Hold the configuration for the whole application and makes it
	possible to save the default and prefered options of the users.

	It is implemented as a singleton.
	"""

	__instance = None

	_filepath = ".config"

	def __init__(self):
		"""
		Save the default if the file does not exists, else just read it.
		filepath should the the full path to the file (base + name)
		"""
		if self.__instance is not None:
			raise Exception("Instanciating a second singleton... arg !")
		# make sure the config file exists
		if not os.path.isfile(self._filepath):	
			config_file = open(self._filepath,'w')
			config_file.write(MB_DEFAULT_OPTIONS)
			config_file.close()
		# load the file
		SafeConfigParser.__init__(self)
		self.read(self._filepath)

	def save(self):
		"""
		Write the config in the file
		"""
		config_file = open(self._filepath,'w')
		self.write(config_file)
		config_file.close()

	@staticmethod
	def setFilePath(filepath):
		"""
		Set the config file's path.
		To be called before any initialisation.
		"""
		MathBenchConfig._filepath = filepath

	@staticmethod
	def getConfig():
		"""
		Return the singleton's instance
		"""
		if MathBenchConfig.__instance is None:
			MathBenchConfig.__instance = MathBenchConfig()
#		print MathBenchConfig.__instance
		return MathBenchConfig.__instance




# # This should make it possible to have the whole file behave like a
# # singleton
# if "configuration" in __name__:
	

# 	def GetConfig():
# 		"""
# 		Return the *unique* config parser object.
# 		"""
# 		return MathBenchConfig.getConfig()

# 	def SetFilePath():
# 		"""
# 		Return the *unique* config parser object.
# 		"""
# 		return MathBenchConfig.getConfig()
