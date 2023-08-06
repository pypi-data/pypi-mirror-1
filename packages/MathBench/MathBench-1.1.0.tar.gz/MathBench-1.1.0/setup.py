"""
The setup.py script needed to build a .egg for an easier distribution
and installation of MathBench.

Requires 'Easy Install' to be installed :)
see there: http://peak.telecommunity.com/DevCenter/EasyInstall#installation-instructions

Then to create a package run (or see below for 'automagical' commands):
$ python setup.py bdist_egg

To use the generated .egg file then:
$ easy_install MathBench-{mathbench version}-py{python version}.egg

Automagical stuff:


- build the packages (sources an egg) and upload all the stuff to pypi
$ python setup.py register sdist bdist_egg upload

"""

from setuptools import setup, find_packages

setup(
    name = "MathBench",
    version = "1.1.0",
    packages = find_packages(exclude=["utils","plugins"]),
#     package_data = {
#         # If any package contains *.txt or *.rst files, include them:
#         '': ['artwork/*.png','artwork/*.svg','artwork/*.icns','artwork/*.txt'],
#     },

    # metadata for upload to PyPI
    author = "Thibauld Nion",
    author_email = "tibonihoo @at@  yahoo .dot. fr",
    description = "Not a whole lab, just a small bench...",
    license = "BSD",
    keywords = "editor shell documentation math script IDE",
    url = "http://mathbench.sourceforge.net",   # project home page, if any

	# more details
	long_description = """Helps in developping small Python scripts as quickly as it should be.

MathBench is extensible by plugins that can provide facilities to easily access some external libraries (for instance pylab) and also provide documentation and code samples through MathBench's integrated documentation system (aka "LibraryDesk").

Warning: Mathbench depends heavily on wxPython(>=2.8) which must be installed before installing Mathbench.""",
	classifiers=['Development Status :: 4 - Beta',
				 'Intended Audience :: Education',
				 'Intended Audience :: End Users/Desktop',
				 'Intended Audience :: Science/Research',
				 'Intended Audience :: Developers',
				 'License :: OSI Approved :: BSD License',
				 'Operating System :: OS Independent',
				 'Programming Language :: Python',
				 'Topic :: Scientific/Engineering',
				 'Topic :: Scientific/Engineering :: Information Analysis',
				 'Topic :: Scientific/Engineering :: Mathematics',
				 'Topic :: Text Editors :: Integrated Development Environments (IDE)',
				 'Topic :: Software Development :: Libraries :: Python Modules'],
	platforms='All',
	# Adds a script to be able to launch the app from commandline
	install_requires = ["Yapsy >= 1.7"],#,"wxPython>=2.8"],
# Also depends on wxPython2.8 but it doesn't seem to be properly registered on pypi yet.
	dependency_links = ["http://www.wxpython.org/download.php"],
	# other arguments here...
	entry_points = {
		'gui_scripts': [
			'MathBench = mathbench.MathBench:main',
			]
		},
)

