================
Using Buildutils
================

This document describes how to use Buildutils with Python projects.

.. contents:: Contents
   :backlinks: entry
.. sectnum::

An Introduction to Buildutils
=============================

Who should use Buildutils?
--------------------------

People who are developing Python projects and want a smart and unified
build environment. The goal of Buildutils is to distil various
development procedures into a set of simple commands under a single
environment. All commands are invoked_ and configured_ using standard
Python techniques.

.. _invoked: `Invoking Buildutils`_
.. _configured: `Configuring Buildutils Commands`_

Requirements
------------

Buildutils currently requires Python 2.3 or greater and the `setuptools
package`_ (included in distribution). The plan is to support 2.2 but it
has not been tested.

Certain commands may include additional requirements. In most cases,
``buildutils`` can obtain and install command dependencies when the
command is invoked.

.. _setuptools package: http://peak.telecommunity.com/DevCenter/EasyInstall

Invoking Buildutils
===================

This section describes various methods of invoking `buildutils
commands`_ on a project. In most cases, the `pbu command`_ should be
used. Other methods are provided for scenarios where using the ``pbu``
command is either not possible or not desirable.

If your project uses the `setuptools package`_, then the buildutils
commands will be automatically available, and you will not have to use
``pbu``.

.. note::

   To enable setuptools in your package, all you have to do is use
   ``from setuptools import setup`` instead of ``from distutils.core
   import setup``, or if you want to support either::

     try:
         from setuptools import setup
     except ImportError:
         from distutils.core import setup

.. _pbu command:

With the ``pbu`` command
------------------------

The ``pbu`` command is included with ``buildutils`` and is a simple
wrapper roughly equivalent to calling ``python setup.py`` from a project
directory. It provides a few additional features that make it the
preferred method of invoking ``buildutils``:

* Reduces potential for `carpal tunnel syndrome`_.

* Makes the ``buildutils`` commands available without having to specify
  the ``--command-packages`` option.

* Can be invoked from a sub directory of the project. The pbu script
  will search for the closest ``setup.py`` file and change into the
  containing directory before invoking the setup script.

* Can be used to invoke multiple versions of python (useful for running
  tests, building version specific distributables, etc.)

.. _carpal tunnel syndrome: http://en.wikipedia.org/wiki/Carpal_tunnel_syndrome

Python Interpreter Selection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``pbu`` usage is like that of ``python setup.py`` with an additional global
option for specifying a set of python interpreters. The ``-i`` or 
``--interpreter=`` argument has a few variations on usage:

To run the `pytest` command using Python 2.3::

    pbu -i2.3 pytest

To run the `pytest` command using specific interpreter that is in a
"non-standard" location::

   pbu -i/opt/python2.3/bin/python pytest

To run the `bdist_egg` command with Python 2.2 followed by Python 2.4::

   pbu -i2.2,2.4 bdist_egg

To run the `bdist_egg` command with Python 2.2, 2.3, and then 2.4::

   pbu -i2.2-2.4 bdist_egg

If a command fails, ``pbu`` prints a message, continues to the next
interpreter, and will exit with a non-zero result code. If all interpreters
succeed, ``pbu`` exits with result code 0.

With ``python setup.py``
------------------------

If you prefer not to use the `pbu command`_, the buildutils commands can
be used with the normal ``distutils`` idiom::

  python setup.py [command]

However, ``buildutils`` commands are not automatically available. There
are two methods of enabling the ``buildutils`` commands in existing
projects, detailed in the following sections.

Enabling ``buildutils`` in ``setup.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can enable ``buildutils`` commands by importing the ``buildutils``
package in a project's ``setup.py`` file::

    # an example setup.py file that enables buildutils commands
    
    try:
        import buildutils
    except ImportError:
        pass
    
    setup(
        name='someproject',
        version='1.0',
        description='Some Project that uses Buildutils',
        py_modules = []
    )

Note that the ``buildutils`` package is imported conditionally. This is
a good idea as it ensures that the base set of ``distutils`` commands
can be invoked even when ``buildutils`` is not available.


Enabling ``buildutils`` with the ``--command-packages`` option
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are unable to use the `pbu command`_ and are also not able to add
``buildutils`` to the projects ``setup.py`` file, you can still get at
Buildutils' commands by specifying the ``--command-packages`` option
(Python 2.4 only)::

    python setup.py --command-packages=buildutils.command stats


Configuring Buildutils Commands
===============================

Buildutils commands can be configured using `distutils configuration
files`_. The normal search path is to look for a ``setup.cfg`` file
sitting next to a project's ``setup.py`` file, followed by a user
configuration located at ``$HOME/.pydistutils.cfg`` (POSIX) or 
``$HOME/pydistutils.cfg`` (WINDOWS). 

Configuration Example
---------------------

The `Syntax of Config Files`_ section of the Distutils documentation
provides an overview of config file syntax. The following example is from
Buildutils' own ``setup.cfg``::

    [announce]
    recipients=python-announce-list@python.org
               distutils-sig@python.org
    
    [publish]
    dist-dest=scp://lesscode.org/var/projects/pub/${name}/dist/${version}
    doc-dir=doc/html
    doc-dest=scp://lesscode.org/var/projects/pub/${name}
    make-dirs=1
    
    [checksum]
    sign=1
    
    [pytest]
    tests=buildutils/test
    
    [pudge]
    docs=doc/index.rst doc/guide.rst doc/commands.rst doc/extensions.rst 
         doc/TODO.rst
    dest=doc/html
    pages=index.html
    theme=lesscode.org
    license=gnu
    modules=buildutils
    title=Python Build Utilities
    mailing_list_url=http://mail.python.org/mailman/listinfo/distutils-sig/
    blog-url=http://lesscode.org/blog/category/${name}/
    syndication-url=http://lesscode.org/blog/category/projects/${name}/feed/
    organization=lesscode.org
    organization-url=http://lesscode.org/blog/

Each ``[section]`` corresponds to a command, with options corresponding
to those described in the `Command Reference`_. Options specified in
config files can be overridden on the command line.

Option Expansion
----------------

Some options support variable expansion. For instance, the following
section of the `configuration example`_ uses ``${name}`` and ``${version}``
in option values to bring in project metadata::

    [publish]
    dist-dest=scp://lesscode.org/var/projects/pub/${name}/dist/${version}
    doc-dir=doc/html
    doc-dest=scp://lesscode.org/var/projects/pub/${name}
    make-dirs=1

At present, variables are available for the `base set of metadata`_ specified
by distutils:

name	
  name of the package
version	
  version of this release
author
  package author's name
author_email
  email address of the package author
maintainer
  package maintainer's name
maintainer_email
  email address of the package maintainer
contact
  maintainer's or author's name (whichever comes first)
contact_email
  email address of maintainer or author (whichever comes first)
url
  home page for the package	URL
description
  short, summary description of the package.
long_description
  longer description of the package
download_url
  location where the package may be downloaded

Individual commands can add additional pieces of metadata for their options.
Commands that support additional expansion values should provide details
in their reference documentation.



.. _base set of metadata: http://www.python.org/doc/current/dist/meta-data.html
.. _Syntax of config files: http://www.python.org/doc/current/inst/config-syntax.html#SECTION000520000000000000000
.. _distutils configuration files: http://www.python.org/doc/current/inst/config-syntax.html
.. _buildutils commands: commands.html
.. _command reference: commands.html
