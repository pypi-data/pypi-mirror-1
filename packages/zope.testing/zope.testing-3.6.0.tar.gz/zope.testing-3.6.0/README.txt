************
zope.testing
************

.. contents::

This package provides a number of testing frameworks.  It includes a
flexible test runner, and supports both doctest and unittest.

cleanup.py
  Provides a mixin class for cleaning up after tests that
  make global changes.

doctest.py
  Enhanced version of python's standard doctest.py.
  Better test count (one per block instead of one per docstring).

  (We need to merge this with the standard doctest module.)

formparser.py
  An HTML parser that extracts form information.

  This is intended to support functional tests that need to extract
  information from HTML forms returned by the publisher.

loggingsupport.py
  Support for testing logging code

  If you want to test that your code generates proper log output, you
  can create and install a handler that collects output.

loghandler.py
  Logging handler for tests that check logging output.

renormalizing.py
  Regular expression pattern normalizing output checker.
  Useful for doctests.

setupstack
  A simple framework for automating doctest set-up and tear-down.
  See setupstack.txt.


testrunner.py
  The test runner module.  This is typically wrapped by a test.py script that
  sets up options to run a particular set of tests.


Getting started
***************

zope.testing uses buildout.  To start, run ``python bootstrap.py``.  It will
create a number of directories and the ``bin/buildout`` script.  Next, run
``bin/buildout``.  It will create a test script for you.  Now, run ``bin/test``
to run the zope.testing test suite.


Releases
********

3.6.0 (2008/07/10)
==================

New Features
------------

- Added -j option to parallel tests run in subprocesses.

- RENormalizer accepts plain Python callables.

- Added --slow-test option.

- Added --no-progress and --auto-progress options.

- Complete refactoring of the test runner into multiple code files and a more
  modular (pipeline-like) architecture.

- Unified unit tests with the layer support by introducing a real unit test
  layer.

- Added a doctest for ``zope.testing.module``. There were several bugs
  that were fixed:

  * ``README.txt`` was a really bad default argument for the module
    name, as it is not a proper dotted name. The code would
    immediately fail as it would look for the ``txt`` module in the
    ``README`` package. The default is now ``__main__``.

  * The tearDown function did not clean up the ``__name__`` entry in the
    global dictionary.

  * Fix a bug that caused a SubprocessError to be generated if a subprocess
    sent any output to stderr.

  * Fix a bug that caused the unit tests to be skipped if run in a subprocess.


3.5.1 (2007/08/14)
==================

Bugs Fixed:
-----------

- Post-mortem debugging wasn't invoked for layer-setup failures.

3.5.0 (2007/07/19)
==================

New Features
------------

- The test runner now works on Python 2.5.

- Added support for cProfile.

- Added output colorizing (-c option).

- Added --hide-secondary-failures and --show-secondary-failures options
  (https://bugs.launchpad.net/zope3/+bug/115454).

Bugs Fixed:
-----------

- Fix some problems with Unicode in doctests.

- Fix "Error reading from subprocess" errors on Unix-like systems.

3.4 (2007/03/29)
================

New Features
------------

- Added exit-with-status support (supports use with buildbot and
  zc.recipe.testing)

- Added a small framework for automating set up and tear down of
  doctest tests. See setupstack.txt.

Bugs Fixed:
-----------

- Fix testrunner-wo-source.txt and testrunner-errors.txt to run with a
  read-only source tree.

3.0 (2006/09/20)
================

- Updated the doctest copy with text-file encoding support.

- Added logging-level support to loggingsuppport module.

- At verbosity-level 1, dots are not output continuously, without any
  line breaks.

- Improved output when the inability to tear down a layer causes tests
  to be run in a subprocess.

- Made zope.exception required only if the zope_tracebacks extra is
  requested.

2.x.y (???)
===========

- Fix the test coverage. If a module, for example `interfaces`, was in an
  ignored directory/package, then if a module of the same name existed in a
  covered directory/package, then it was also ignored there, because the
  ignore cache stored the result by module name and not the filename of the
  module.

2.0 (2006/01/05)
================

- Corresponds to the version of the zope.testing package shipped as part of
  the Zope 3.2.0 release.
