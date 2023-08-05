Buildutils Extension Guidelines
===============================

This document provides some basic guidelines for building `distutils`
extensions for inclusion in `buildutils`. Note that I do not like rules
and neither should you; use these to augment your better judgement.

The Basics
----------

Extensions are built using the extension interfaces defined by distutils
(see `Extending Distutils`_). Here's a basic template::

    from distutils.command import Command
    from distutils import log
    
    class command_name(Command):
        description = "command description (shown in --help-commands)"
        user_options = [('long-arg-name=', 'a',
                         "Description of option.")]
        
        def initialize_options(self):
            self.long_arg_name = None
        
        def finalize_options(self):
            if self.long_arg_name is None:
                self.long_arg_name = "default value"
        
        def run(self):
            log.info("hello world!")

Each command extension must be placed in a separate module under
``buildutils/command`` and must contain a class with the same name as
the module.

Once the module and class are in place, extensions must be added to the
list defined at ``buildutils.command.__all__`` in the
``buildutils/command/__init__.py`` file. Just add your command name to
the list::

    __all__ = ['etags', 'info', 'stats', 'checksum', 'command_name']

The order the names are defined here is the order they are displayed
when invoking: ``python setup.py --help-commands``. Try to group
commands if it makes sense.

.. _Extending Distutils: http://www.python.org/doc/2.4.1/dist/extending.html

.. _facades:

Command Facades
---------------

Where possible, `distutils.cmd.Command` subclasses should be lite
wrappers around normal python classes and functions. Try to write
functionality generically and then call it from the extension
class. This ensures that other extensions may use the functionality
provided by your extension without requiring the use of distutils
protocol.

Dependencies
------------

`buildutils`' only hard dependency is the `setuptools` package. All
other python dependencies should be retrievable using the `setuptools`
package. Extension classes should check for dependencies in the
extension class' `run` method, which usually looks something like this::

    def run(self):
        from pkg_resources import require
        require('my_dependency>=1.0')
        ...

**Do not...**

- ... make calls to ``require`` at the module level in an extension module.
- ... add dependencies to ``buildutils.egg-info/depends.txt``

When a dependency does not exist, the user will be notified and prompted
for whether the missing package should be installed. 

This makes it possible to include commands with heavy dependency
requirements without having to ship the dependencies to the people who
don't need it.

.. _setuptools: http://peak.telecommunity.com/DevCenter/EasyInstall

Unit Tests
----------

`py.test based unit tests`_ should be provided for extensions. This is
another reason that extension classes should be kept as `Facades`_ - it
keeps unit testing sane by not requiring tests to emulate a command
line. Tests are defined under ``buildutils.test``. Any module whose name
starts with "test\_" is picked up automatically.

.. _`py.test based unit tests`: http://codespeak.net/py/current/doc/test.html

Python Version Compatibility
----------------------------

Commands should run under python versions 2.3 and above. If a command
can not provide its functionality to an earlier version of python, it
should not add itself to the ``buildutils.command.__all__`` list. 

For example, if the `foo` extension doesn't work under Python/2.3, it
should check the version before adding "foo" in
``buildutils/command/__init__.py``::

    import sys
    __all__ = ['etags', 'info', 'stats', 'checksum']
    
    (major, minor, micro, releaselevel) = sys.versioninfo
    if (major, minor) >= (2, 4):
        __all__.append('foo')


Working with files and processes
--------------------------------

The `distutils.cmd.Command` class is treasure chest of useful
functionality - much of which is undocumented. Before writing any
commands, review the ``distutils/cmd.py`` module source.

