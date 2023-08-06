Paver: Build, Distribute and Deploy Python Projects
===================================================

.. image:: _static/paver_banner.jpg

Paver is a Python-based build/distribution/deployment scripting tool along the
lines of Make or Rake. What makes Paver unique is its integration with 
commonly used Python libraries. Common tasks that were easy before remain 
easy. More importantly, dealing with *your* applications specific needs and 
requirements is also easy.

* Build files are :ref:`just Python <justpython>`
* :ref:`One file with one syntax <onefile>`, pavement.py, knows how to manage
  your project
* :ref:`File operations <pathmodule>` are unbelievably easy, thanks to the 
  built-in version of Jason Orendorff's path.py.
* Need to do something that takes 5 lines of code? 
  :ref:`It'll only take 5 lines of code. <fivelines>`.
* Wraps :ref:`setuptools <setuptools>` so that you can customize behavior
* Wraps :ref:`Sphinx <sphinx>` for generating documentation.
* Wraps :ref:`Subversion <svn>` for working with code that is checked out.
* Can use all of these other libraries, but :ref:`requires none of them <nodeps>`

Paver was created by `Kevin Dangoor <blueskyonmars.com>`_ of `SitePen <sitepen.com>`_.

Status
======

Paver is currently alpha release software. It's easy enough to use and works for
what it does, but does not have robust error handling and is likely missing
some of the bits you'd like to have. More importantly, there's no guarantee that
the :ref:`pavement` syntax will remain unchanged. Luckily, pavement files are
standard Python. That means that odds are good that changes within Paver would
only require changes to a few lines of your pavements.

See the :ref:`changelog <changelog>` for more information about recent improvements.

Installation
============

The easiest way to get Paver is if you have setuptools_ installed.

``easy_install Paver``

Without setuptools, it's still pretty easy. Download the Paver .tgz file from 
`Paver's Cheeseshop page`_, untar it and run:

``python setup.py install``

.. _Paver's Cheeseshop page: http://pypi.python.org/pypi/Paver/
.. _setuptools: http://peak.telecommunity.com/DevCenter/EasyInstall

Help and Development
====================

You can get help from the `mailing list`_.

If you'd like to help out with Paver, you can check the code out from Launchpad:

``bzr branch http://bazaar.launchpad.net/~dangoor/paver/main``

You can also take a look at `Paver's project page on Launchpad <https://launchpad.net/paver/>`_.

.. _mailing list: http://groups.google.com/group/paver

License
=======

Paver is licensed under a BSD license. See the LICENSE.txt file in the 
distribution.


Contents:

.. toctree::
   :maxdepth: 2
   
   features
   pavement
   paverstdlib
   cmdline
   changelog
   todo
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

