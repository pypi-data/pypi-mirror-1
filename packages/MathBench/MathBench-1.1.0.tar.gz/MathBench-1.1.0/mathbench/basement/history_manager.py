#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Handling of command history and their saving/loading in/from files.

The history is a list of commands (one item by command) to be
compatible with the history represenation in wx.Py.shell.
"""

import os
import time

class HistoryManager(object):
	"""
	Manage the history of commands.
	"""
	
	# a separator that is a bit more that a line separator to be able
	# to locate when the line ends because the commands ends or
	# because we are writting a multiple line commands (eg class
	# definition) (idea taken from wx.py itself...)
	COMMANDS_SEPARATOR = '\x00\n'

	
	def __init__(self, shell, history_dir, extension="session", max_file_nb=10):
		"""
		Initialise the manager.
		
		``history_dir``
		  
		    the directory where history files are supposed to be saved.
		"""
		self.shell = shell
		self.history_dir = history_dir
		self.extension = extension
		self.max_file_nb = max_file_nb
		self.put_landmark()

	def get_history_files_info(self):
		"""
		Return the list of dates corresponding to the available history files.
		"""
		histo_list = []
		for root, dirs, files in os.walk(self.history_dir):		
			for filename in files:
				if filename.endswith(".%s"%self.extension):
					# then it should be a command history and the rest
					# of the file should be in the following format:
					# YYYYMMDD-hhmmss
					histo_list.append(filename.rstrip(".%s"%self.extension))
			# don't go into the hierachy of folders
			return histo_list

	def load_session_at_date(self, dateinfo):
		"""
		Iterate over the list of command corresponding to the session at a
		given date, described by a string in the following format:

		YYYYMMDD-hhmmss
		"""
		f = open(os.path.join(self.history_dir,"%s.%s"%(dateinfo,self.extension)))
		hist = f.read()
		commands = hist.split(self.COMMANDS_SEPARATOR)
		# load all the commands in the shell's history
		for c in commands:
			self.shell.history.append(c)
	
	def load_latest_session(self):
		"""
		Load the latest session.
		"""
		session_dates = self.get_history_files_info()
		# sort all
		session_dates.sort()
		if len(session_dates)>0:
			# take the latest
			self.load_session_at_date(session_dates[-1])

	def check_not_too_many_file(self):
		"""
		Check that there is not too many session file, and if there is
		remove the oldest.
		"""
		session_files = self.get_history_files_info()
		session_files.sort()
		while len(session_files)>self.max_file_nb:
			f = session_files.pop(0)
			os.remove(os.path.join(self.history_dir,"%s.%s"%(f,self.extension)))

	def save_current_session(self):
		"""
		Save the history of a given file into a shell.
		
		Save the session only after the landmark.
		"""
		lt = time.localtime()
		# create an appropriate date stamp to put in the file name
		date_stamp = "%s%#02d%#02d-%#02d%#02d%#02d" % (lt.tm_year,lt.tm_mon,lt.tm_mday,
													   lt.tm_hour,lt.tm_min,lt.tm_sec)
		# open the file and write all the commands
		filename = os.path.join(self.history_dir,"%s.%s"%(date_stamp,self.extension))
		f = open(filename,"w")
		f.write(self.COMMANDS_SEPARATOR.join(self.get_history_from_landmark()))
		f.close()
		# check that we have not exceeded the limit of such files
		self.check_not_too_many_file()
		
	def put_landmark(self):
		"""
		Record the current length of the shell's history.
		"""
		self.landmark=len(self.shell.history)

	def get_landmark(self):
		"""
		Record the length of the shell's history when the latest landmark was put.
		"""
		return self.landmark

	def get_history_from_landmark(self):
		"""
		Return the list of commands entered since the latest landmark.
		"""
# 		print self.landmark
# 		print self.shell.history
		if self.landmark==0:
			return self.shell.history[:]
		else:
			return self.shell.history[:-self.landmark]

