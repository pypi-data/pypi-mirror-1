.. _cmdline:

Paver Command Line
==================

The paver command line tool is very simple::

  paver [-q] [-n] [-v] [task] [task...]

The command line options are:

-q
  quiet... don't display much info (info and debug messages are not shown)

-n
  dry run... don't actually run destructive commands

-v
  verbose... display debug level output


If you run paver without a task, it will default to the "help" task which 
lists the available tasks.
