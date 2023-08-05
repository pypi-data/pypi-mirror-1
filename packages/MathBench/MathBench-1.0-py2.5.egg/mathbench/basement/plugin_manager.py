#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Create a PluginManager.

Create it as a Singleton with yapsy.
"""

import os 

import yapsy
from yapsy import PluginManager  
from yapsy import ConfigurablePluginManager 
from yapsy.IPlugin import IPlugin
	
# Make an alias to be used in the app
LabPluginManager = PluginManager.PluginManagerSingleton
# set the required behaviour
LabPluginManager.setBehaviour([
		ConfigurablePluginManager.ConfigurablePluginManager
		])








