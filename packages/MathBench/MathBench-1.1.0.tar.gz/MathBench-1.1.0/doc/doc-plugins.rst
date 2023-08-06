===========
 MathBench
===========


Not enough functionalities or documentation ? Install a plugin !
================================================================

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
.. _Python: http://www.python.org

.. _`SourceForge download page`: http://sourceforge.net/project/showfiles.php?group_id=203145



Description
-----------

For people making an extensive use of only a few Python libraries,
plugins can customize |mathbench| in order to make it even more
straightforward to use with these libraries.


List of plugin(s):

 - pylab_plugin for `matplotlib's pylab <http://matplotlib.sourceforge.net/>`_ plotting library: 

    - automatically loads pylab at shell startup

    - provide search capacity and an offline access to the code samples shown at http://matplotlib.sourceforge.net/screenshots.html

 - dummy_plugin: just a test plugin to understand how it works


.. _`development section`: ./doc-development.html

Please find instructions on how to create your own plugins in the
`development section`_.


Installation
------------

Plugins can be downloaded from `SourceForge download page`_.

Once the plugin files are downloaded, |mathbench| automatically handles
their correct installation. For more details please refer the
walkthrough below:


  - download a plugin and extract its files in a safe place (e.g. your desktop)

      .. image:: images/mathbench_lin_pluginarchive.png
         :alt: A few plugins can be donwloaded right from MathBench's website
         :align: center


  - ask MathBench for the addition of a new plugin

      .. image:: images/mathbench_lin_pluginconfig.png
         :alt: MathBench "preferences" menu makes it possible to add plugins
         :align: center

   - activate the plugin

      .. image:: images/mathbench_lin_pluginactivate.png
         :alt: Check the box next to the plugin to activate it
         :align: center



.. footer:: Return home_ | Last revision on $Date: 2008-04-09 18:28:21 +0200 (mer, 09 avr 2008) $.

            |SourceForge.net| Project hosted by `SourceForge <http://sourceforge.net>`_ || Some right reserved |CC-BYSA|.
