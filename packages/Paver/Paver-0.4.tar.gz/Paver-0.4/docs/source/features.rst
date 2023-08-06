Paver's Features
================

.. _justpython:

Files Are Just Python
---------------------

Python has a very concise, readable syntax. There's no need to create some
mini-language for describing your builds. Quite often it seems like these
mini-languages are missing features that you need. By using Python as its
syntax, you can always be sure that you can express whatever it is you
need to do easily.

.. _onefile:

One File with One Syntax
------------------------

When putting together a Python project today, you get into a collection of
tools to get the job done. distutils and setuptools are the standards for
getting packages put together. zc.buildout and virtualenv are used for
installation into isolated deployment environments. Sphinx provides
a great way to document Python projects.

To put together a total system, you need each of these parts. But they
each have their own way of working. The goal with the 
:ref:`Paver Standard Library <stdlib>`
is to make the common tools have a more integrated feel, so you don't
have to guess as much about how to get something done.

.. _pathmodule:

Easy file operations
--------------------

Paver includes a customized version of Jason Orendorff's awesome path.py
module. Operations on files and directories could hardly be easier,
and the methods have been modified to support "dry run" behavior.

.. _fivelines:

Small bits of behavior take small amounts of work
-------------------------------------------------

Imagine you need to do something that will take you 5 lines of Python code.
With some of the tools that Paver augments, it'll take you a lot more
effort than those 5 lines of code. You have to read about the API for
making new commands or recipes or otherwise extending the package.
The goal when using Paver is to have a five line change take about five
lines to make.

.. _nodeps:

Can Take Advantage of Libraries But Doesn't Require Them
--------------------------------------------------------

The Paver Standard Library includes support for a lot of the common tools,
but you don't necessarily need all of those tools, and certainly not on
every project. Paver is designed to have no other requirements but to
automatically take advantage of other tools when they're available.
