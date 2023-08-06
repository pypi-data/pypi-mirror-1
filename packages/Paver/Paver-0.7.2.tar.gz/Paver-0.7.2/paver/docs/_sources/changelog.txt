.. _changelog:

Paver Changelog
===============

0.7.2 (May 8, 2008)
-------------------

* Fixed Python 2.4 compatibility. The paver-minilib.zip file contained 2.5 
  .pyc files. .pyc files are not compatible between major Python versions.
  The new version contains .py files.

0.7.1 (May 8, 2008)
-------------------

* 0.7 had a broken paver-minilib.zip (missing misctasks.py, which is now part of the
  standard minilib)

0.7 (May 7, 2008)
----------------------

Breaking changes:

* "targets" have become "tasks", because that name is a clearer description.
* paver.sphinxdoc has been renamed paver.doctools

New features and changes:

* runtime.OPTIONS is gone now. The old voodoo surrounding the options() function
  has been replaced with a distinctly non-magical __call__ = update in the
  Namespace class.
* distutils.core.setup is now the command line driver
* distutils/setuptools commands can be seamlessly intermingled with Tasks
* tasks can have command line settable options via the cmdopts decorator.
  Additionally, they can use the consume_args decorator to collect up
  all command line arguments that come after the task name.
* Two new tasks: cog and uncog. These run Ned Batchelder's Cog code
  generator (included in the Paver package), by default against your
  Sphinx documentation. The idea is that you can keep your code samples
  in separate files (with unit tests and all) and incorporate them
  into your documentation files. Unlike the Sphinx include directives,
  using Cog lets you work on your documentation with the code samples
  in place.
* paver.doctools.SectionedFile provides a convenient way to mark off sections
  of a file, usually for documentation purposes, so that those sections can
  be included in another documentation file.
* paver.doctools.Includer knows how to look up SectionedFiles underneath
  a directory and to cache their sections.
* options are now a "Namespace" object that will search the sections for
  values. By default, the namespace is searched starting with top-level
  items (preserving current behavior) followed by a section named the same
  as the task, followed by all of the other sections. The order can
  be changed by calling options.order.
* option values that are callable will be called and that value returned.
  This is a simple way to provide lazy evaluation of options.
* Added minilib task that creates a paver-minilib.zip file that can be
  used to distribute programs that use Paver for their builds so that
  setup.py will run even without Paver fully installed.
* Added generate_setup task that creates a setup.py file that will
  actually run Paver. This will detect paver-minilib.zip if it's
  present.
* The "help" task has been greatly improved to provide a clearer picture
  of the tasks, options and commands available.
* Add the ability to create virtualenv bootstrap scripts
* The "help" property on tasks has changed to "description"
* output is now directed through distutils.log
* Ever improving docs, including a new Getting Started guide.
* Changes to Paver's bootstrap setup so that Paver no longer uses
  distutils for its bootstrapping.


There were no versions 0.5 and 0.6.

0.4 (April 22, 2008)
--------------------

* First public release.
* Removes setuptools dependency
* More docs
* Paver can now be run even without a pavement.py file for commands like
  help and paverdocs
