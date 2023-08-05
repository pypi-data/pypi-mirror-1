"""
Sets up pylab to be loaded at mathbench init !
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
	from PylabPlugin import PylabPlugin
except Exception,e:
	print e

