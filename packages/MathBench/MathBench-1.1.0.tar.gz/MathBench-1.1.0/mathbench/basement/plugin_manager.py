#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Create a PluginManager.

Create it as a Singleton with yapsy.
"""

import os 

import yapsy
from yapsy.PluginManager import PluginManagerSingleton  
from yapsy.ConfigurablePluginManager import ConfigurablePluginManager 
from yapsy.AutoInstallPluginManager import  AutoInstallPluginManager
from yapsy.IPlugin import IPlugin
	
# Make an alias to be used in the app
LabPluginManager = PluginManagerSingleton
# set the required behaviour
LabPluginManager.setBehaviour([
		ConfigurablePluginManager,
		AutoInstallPluginManager
		])








