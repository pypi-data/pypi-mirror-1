.. _pytest:

``pytest`` -- Run ``py.test`` unit tests
----------------------------------------

Runs `py.test`_ based unit tests for the current project.

For more information on writing ``py.test`` based unit tests, see `The
py.test tool and library`_. Grig Gheoghiu provides a nice comparison of
``py.test`` to other unit testing frameworks in `Python unit testing
part 3 - py.test`_.

.. _The py.test tool and library:
.. _py.test: http://codespeak.net/py/current/doc/test.html
.. _Python unit testing part 3 - py.test: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-3-pytest-tool.html

Synopsis
~~~~~~~~

Test 

Options
~~~~~~~

Options for the ``pytest`` buildutils command mirror those of the
``py.test`` command line utility with some minor differences.

tests (``--tests=``, ``-t``)
  A comma separated list of test files or directories to search for test
  files. Directories are searched recursively for files named either 
  ``test_*.py`` or ``*_test.py``.

collectonly (``--collectonly``)
  Collect but do not execute tests. This is useful in determining what
  tests are available and to check that collection is working properly.

exitfirst (``--exitfirst``, ``-x``)
  Exit after the first unit test error or failure. This option is 
  recommended when developing.

fulltrace (``--fulltrace``)
  Don't cut any traceback entries. The default is to remove commonly
  useless entries.

nocapture (``--no-capture``, ``-s``)
  Don't capture ``sys.stdin``, ``sys.stdout`` for each tests. When this 
  option is enabled, printed messages are displayed immediately. With
  the option off, messages are displayed only when tests fail.

nomagic (``--no-magic``)
  Refrain from using magic as much as possible. Enable this option if
  your tests seem to be failing for odd reasons.

pdb (``--pdb``)
  Start pdb_ (The Python Debugger) when a test fails.

showlocals (``--showlocals``, ``-l``)
  Show the name/values of ``locals()`` in traceback dumps. This is
  useful for quick debugging but requires more resources.

looponfailing (``--looponfailing``, ``-f``)
  When tests fail, watch for file modifications and automatically re-run
  the test until all tests pass. This option is golden when used with
  ``-x``.

tkinter (``--tkinter``)
  Use the tkinter GUI interface for tests.


.. _pdb: http://www.python.org/doc/current/lib/module-pdb.html

Notes
~~~~~

``py.test`` has not yet been packaged into a distutils package or
released on PYPI_ and cannot be automatically installed by the dependency
resolution feature.

You will need to follow the instructions from `Getting
Started with py lib`_ to install and configure the ``py`` distribution
before this command will work properly.

.. _Getting Started with py lib: http://codespeak.net/py/current/doc/getting-started.html
.. _PYPI: http://www.python.org/pypi

The basic process is to checkout the latest sources from subversion and
then to bring the configuration into your shell. For example, to bring
the library into a ``python`` directory off of your home directory on
POSIX systems, you might run::

    $ cd ~/python
    $ svn co http://codespeak.net/svn/py/dist py-dist

You will need to setup your environment before invoking the ``pytest``
command, as follows::

    $ eval `python ~/path/to/py-dist/py/env.py`

