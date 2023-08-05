""" 
py2app/py2exe build script for MathBench

Bundle nearly all that is neede by MathBench in a single standalone
application.

Usage (Mac OS X): 
	python setupbundle.py py2app 

Usage (Windows):
	python setupbundle.py py2exe
""" 

import sys

from setuptools import setup

if sys.platform == 'darwin':

	APP = ['mathbench/MathBench.py']
	DATA_FILES = []
	OPTIONS = {
		# Cross-platform applications generally expect sys.argv to
		# be used for opening files.
		'argv_emulation': True,
		# Because they are among matplotlib's dependencies we have to
		# exclude these libraries (we d'ont use the tk backend)
		'dylib_excludes': 'Tk,Tcl',
		# Don't bundle python
		'semi_standalone': True,
		# include the system and user site-packages into sys.path
		'site_packages': True,
		# Allow PYTHONPATH to effect the interpreter's environment
		'use_pythonpath': True,
		# Artwork
		'iconfile': '/Users/thibauldnion/src/mathbench/mathbenchdir/trunk/artwork/mathbench.icns',
		# Mac info
		'plist': {'CFBundleIdentifier': "net.sourceforge.mathbench",
				  'CFBundleGetInfoString':"Helps in developping small Python scripts as quickly as it should be."},
		# There is a problem when including wx (one of the .so libs is missing)
		'excludes': 'wx',
		}
	
	setup(
		name="MathBench",
		app=APP,
		data_files=DATA_FILES,
		options={'py2app': OPTIONS},
		setup_requires=['py2app'],
		)

elif sys.platform == 'win32':
	setup(
		name="MathBench",
		setup_requires=['py2exe'],
		app=['mathbench/MathBench.py'],
		)

else: # unix ?
	raise Exception("No bundle for this plateform: please consider using the setup.py script and create an .egg")

		
