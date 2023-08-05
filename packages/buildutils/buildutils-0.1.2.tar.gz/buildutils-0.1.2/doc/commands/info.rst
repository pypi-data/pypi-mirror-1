.. _info:

``info`` -- Dump Project Info
-----------------------------

This is a simple command that dumps project information to standard
output.

Synopsis
~~~~~~~~

Running the ``info`` command on the ``buildutils`` project::

  [ rtomayko@pips:~/devel/buildutils ]$ pbu info
  buildutils - Distutils extensions for developing Python libraries and applications.
  
  Name:       buildutils          Author:     Ryan Tomayko <rtomayko@lesscode.org>
  Version:    0.1.0
  License:    MIT
  Platforms:  All (not specified)
  
  Project URL:  <http://buildutils.lesscode.org/>
  Download URL: <http://buildutils.lesscode.org/dist/0.1.0/>
  
  Trove Classifiers:
  
      Development Status :: 4 - Beta
      Environment :: Console
      Intended Audience :: Developers
      Intended Audience :: System Administrators
      License :: OSI Approved :: MIT License
      Operating System :: OS Independent
      Programming Language :: Python
      Topic :: Software Development :: Build Tools
      Topic :: System :: Installation/Setup
      Topic :: System :: Software Distribution
      Topic :: Utilities
  
  Description:
  
      The `buildutils` package contains extensions to Python's standard
      distribution utilities (`distutils`) that are often useful during the
      development of Python projects. `buildutils` was created to scratch an
      itch: removing ``make`` from the Python development process and partially
  
  ...

Options
~~~~~~~

The ``info`` command has no options.
