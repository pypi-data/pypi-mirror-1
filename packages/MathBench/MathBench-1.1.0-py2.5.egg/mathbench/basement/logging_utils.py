#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Defines a logger based on Python's logger module.
"""

# Load Python's logging utilities
import logging
import logging.handlers

import configuration

# mapping usefull to interpret the options
MB_LOGLEVEL_MAPPING = {
	
	"DEBUG"		: logging.DEBUG,
	"INFO"		: logging.INFO,
	"ERROR"		: logging.ERROR,
	"CRITICAL"	: logging.CRITICAL,
}

MB_LOGGER_NAME="mathbench"

def CreateLogger(handler):
	"""
	Create a logger object with a default verbosity corresponding to a
	given loglevel.
	"""
	# Get the options concerning the verbosity level
	__config = configuration.getConfig()
	__loglevel_str = __config.get("Development","Verbosity_Level")
	loglevel = MB_LOGLEVEL_MAPPING[__loglevel_str]

	# Create the logger
	logger = logging.getLogger(MB_LOGGER_NAME)
	# set the log level according to the app's configuration
	logger.setLevel(loglevel)

	#  set default level for the handler
	handler.setLevel(loglevel)
	# create formatter
	formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	# add the formatter to the handler
	handler.setFormatter(formatter)

	# add the handler to the logger
	logger.addHandler(handler)
	return logger
	
