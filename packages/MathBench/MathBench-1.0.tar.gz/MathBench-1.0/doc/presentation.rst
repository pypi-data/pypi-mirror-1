===========
 MathBench
===========


Not a whole lab, just a small bench
===================================


.. image:: ../artwork/mathbench-big.png
   :alt: mathbench-icon
   :class: logo-img


.. |mathbench| replace:: **MathBench**
.. |mathbench-icon| image:: ../artwork/mathbench.png 
.. |SourceForge.net| image:: http://sflogo.sourceforge.net/sflogo.php?group_id=203145&type=3
                     :alt: Sourceforge.net
.. |CC-BYSA| image:: http://i.creativecommons.org/l/by-sa/3.0/88x31.png
             :alt: Creative Commons License

.. warning:: 

   MathBench is still in heavy development and any help is
   appreciated.


Overview
--------

MathBench is a Python IDE targetting at people usually writing small
scripts or execute a few commands in a handy shell. MathBench is thus
optimised for activies like:

 - algorithms or numerical scheme prototyping
 - use of data display tools (ala gnuplot)
 - need of executing a few lines of code to test an idea


MathBench is designed to be as **intuitive** and **useful** as
possible.


Features
--------

GUI shell and script editors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
 - Auto-completion

 - Call tips

 - Command history for the shell

 - Script generation with the shell's history


Documentation system
~~~~~~~~~~~~~~~~~~~~

 - Simple interface to documentation  (aka "LibraryDesk") 

 - Extensible search engine to search among code samples and
   documentation provided by plugins.


Plugins
~~~~~~~

For people making an extensive use of a few Python libraries, plugins
can customize MathBench in order to make it even more straightforward
to use these libraries.

Additionaly a plugin can extend the documentation system with some
offline *and* online references which might save a lot more time
(avoiding to browse the whole web for a usefull code sample for
instance).

List of plugin(s):

 - pylab_plugin for `matplotlib's pylab <http://matplotlib.sourceforge.net/>`_ plotting library: 

    - automatically loads pylab at shell startup

    - provide search capacity and an offline access to the code samples shown at http://matplotlib.sourceforge.net/screenshots.html


Installation of a plugin is performed by copying its files in the
``.mathbench/plugins`` directory. Then the user can activate or
deactivate plugins through the ``Tools->Preferences`` menu options.


Technologies and development
----------------------------

GUI
~~~

MathBench's GUI is based on `wxPython <http://www.wxpython.org/>`_ and
intensively uses its ``wx.py`` library. 

This makes it **portable** accross many platforms
(Linux/MacOSX/Windows) and gives us a reasonable freedom concerning
the licensing of the project.

The development takes place on Sourceforge at `this place
<http://sourceforge.net/projects/mathbench/>`_.

Plugin Creation
~~~~~~~~~~~~~~~

As soon as a plugin is loaded it can access all the classes and
objects of MathBench and by leveraging the flexibility of Python, it
can modify nearly anthing in the app.

However a few facilities are provided to ease plugins' development:

 - A static method makes it possible to add a new instrution to be
   executed at shell start-up:
   
   ::

      from mathbench.lab.notebook import LabBook
      
      # here some code and the plugin class definition
      # ...
        def activate(self)
	  """
	  Plugin activation method
          """
	  # ...
          LabBook.initShellSessionAppend("import mypreferedlib as mpl #< load my prefered library")
      

 - Another static method makes it possible to add a new search engine
   that will be used by the internal documentation system as soon as
   the user makes a query (results from search engines provided by all
   the plugins are then agregated in a html page filled with links)
   
   ::

      from mathbench.basement.librarian import LibrarianSingleton

      # here some code and the plugin class definition
      # ...

        def activate(self)
	  """
	  Plugin activation method
          """
	  # ... 
          LibrarianSingleton.register(my_search_method,"my_plugin_name")


.. hint::
   
   MathBench's plugin system is built on `Yapsy
   <http://yapsy.sourceforge.net>`_ which is a lightweight and quite
   flexible plugin framework.


License
-------

This software is open source with all the source code being licensed
under the "new" BSD license.

The only exception to this BSD license is the license for the icons
that are under the Creative Common Attribution-ShareAlike License.


.. footer:: Last revision on $Date: 2007-11-10 18:17:35 +0100 (Sat, 10 Nov 2007) $.

            |CC-BYSA| Some right reserved.

            |SourceForge.net| Project hosted by `SourceForge <http://sourceforge.net>`_  

            
 