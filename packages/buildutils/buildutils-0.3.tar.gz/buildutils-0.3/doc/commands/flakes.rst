.. _flakes:

``flakes`` -- Find Lint
-----------------------

From the pyflakes_ project page: 

    Pyflakes is a simple program which checks Python source files for
    errors. It is similar to PyChecker in scope, but differs in that it
    does not execute the modules to check them. This is both safer and
    faster, although it does not perform as many checks. Unlike PyLint,
    Pyflakes checks only for logical errors in programs; it does not
    perform any checks on style.

Synopsis
~~~~~~~~

Running the ``flakes`` command on the ``buildutils`` project::

  [ rtomayko@pips:~/devel/buildutils ]$ pbu flakes
  warning: flakes: buildutils/__init__.py:23: 'compat' imported but unused
  warning: flakes: buildutils/command/pudge.py:68: 'isdir' imported but unused
  warning: flakes: buildutils/command/pudge.py:83: 'normpath' imported but unused
  warning: flakes: buildutils/command/use.py:98: undefined name 'egg'

Options
~~~~~~~

There are no options for the ``flakes`` command.

.. _pyflakes: http://divmod.org/projects/pyflakes
