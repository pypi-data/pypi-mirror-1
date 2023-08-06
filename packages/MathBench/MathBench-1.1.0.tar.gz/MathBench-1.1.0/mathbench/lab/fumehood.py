#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Define a nice way to show the messages sent to be logged.

NOTE: not used yet
"""

import wx

# Load Python's logging utilities
import logging
import logging.handlers

from mathbench.basement.logging_utils import CreateLogger


class FumeHoodLogHandler(logging.StreamHandler):
	"""
	A log handler that will display the logged messages (above a
	certain priprity level) in GUI windows.
	"""

	def __init__(self) :
		"""
		Initialisation
		"""
		logging.StreamHandler.__init__(self)
		# Associate a loglevel to a certain kind of window
		self.handle_mapping = {
			logging.CRITICAL: self.TriggerCritical,
			logging.ERROR	: self.TriggerError,
			logging.WARNING	: self.TriggerWarning,
			logging.INFO	: self.TriggerInfo,
			}

	def handle(self, record):
		"""
		React to the record according to its priority level.
		"""
		if self.handle_mapping.has_key(record.levelno):
			self.handle_mapping[record.levelno](record)
		logging.StreamHandler.handle(self,record)
			
	def TriggerWarning(self,record):
		"""
		mouf
		"""
		dialog = wx.MessageBox(record.getMessage(), caption = "Warning", style = wx.OK | wx.ICON_WARNING)

	def TriggerError(self,record):
		"""
		Trigger the info contained in a record of level ERROR.
		"""
		dialog = wx.MessageBox(record.getMessage(), caption = "Error !", style = wx.OK | wx.ICON_ERROR)

	def TriggerInfo(self,record):
		"""
		Trigger the info contained in a record of level INFO.
		"""
		dialog = wx.MessageBox(record.getMessage(), caption = "Information...", style = wx.OK | wx.ICON_INFORMATION)

	def TriggerCritical(self,record):
		"""
		Trigger the info contained in a record of level CRITICAL.
		"""
		dialog = wx.MessageBox(record.getMessage(), caption = "Critical Error !", style = wx.OK | wx.ICON_STOP)



# The global variables should only be defined when the module is
# loaded/executed for the first time
if "fumehood" in __name__ or __name__ == "__main__":

	# Create a GUI enabled logger
	__log_handler = FumeHoodLogHandler()
	__MB_LOGGER = CreateLogger(__log_handler)

	# (re)define the global functions through which the messages are sent
	def debug(text) :
		return __MB_LOGGER.debug(text)

	def info(text) :
		return __MB_LOGGER.info(text)

	def warn(text) :
		return __MB_LOGGER.warn(text)

	def critical(text) :
		return __MB_LOGGER.critical(text)

	def log(text) :
		return __MB_LOGGER.log(text)

	def error(text) :
		return __MB_LOGGER.error(text)


def log_function_call(func):
	"""
	Send a message each time the decorated function is called.

	This nifty decorator is very usefull to trace the function calls
	"""
	def wrapper(*args, **kwargs):
		debug("Called func.: %s (defined in %s)" % (func.__name__,func.code.co_filename))
		return func(*args, **kwargs)
	# usefull for automatic doc generation/introspection
	wrapper.__name__	= func.__name__
	wrapper.__doc__		= func.__doc__
	wrapper.__dict__.update(func.__dict__)
	return wrapper

 	
#--- TEST ---------------------------------------------------------------------------------

if  __name__ == "__main__":
	app = wx.PySimpleApp()
	debug("debug message")
	info("info message")
	warn("warn message")
	error("error message")
	critical("critical message")
	app.MainLoop()
	
