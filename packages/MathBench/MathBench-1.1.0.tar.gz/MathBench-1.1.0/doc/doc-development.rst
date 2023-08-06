===========
 MathBench
===========


Technologies and development
============================

.. _home: ./index.html
.. image:: artwork/mathbench-big.png
   :alt: mathbench-icon
   :class: logo-img


.. |mathbench| replace:: **MathBench**
.. |mathbench-icon| image:: artwork/mathbench.png 
.. |SourceForge.net| image:: http://sflogo.sourceforge.net/sflogo.php?group_id=203145&type=3
                     :alt: Sourceforge.net
.. |CC-BYSA| image:: http://i.creativecommons.org/l/by-sa/3.0/88x31.png
             :alt: Creative Commons License

.. _dev: ./doc-development.html
.. _install: ./doc-install.html


Trivia
------

The development takes place on Sourceforge at `this place
<http://sourceforge.net/projects/mathbench/>`_.

The documentation is accessible at `this address
<http://mathbench.sourceforge.net/epydoc/>`_.


GUI
---

MathBench's GUI is based on `wxPython <http://www.wxpython.org/>`_ and
intensively uses its ``wx.py`` library. 

This makes it **portable** accross many platforms
(Linux/MacOSX/Windows) and gives us a reasonable freedom concerning
the licensing of the project.



Plugin Creation
---------------

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


.. footer:: Return home_ | Last revision on $Date: 2008-04-09 18:28:21 +0200 (mer, 09 avr 2008) $.

            |SourceForge.net| Project hosted by `SourceForge <http://sourceforge.net>`_ || Some right reserved |CC-BYSA|.
