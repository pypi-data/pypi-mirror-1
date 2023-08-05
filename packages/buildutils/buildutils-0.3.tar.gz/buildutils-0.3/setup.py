#!/usr/bin/env python
"""Distutils setup file, used to install or test 'buildutils'"""

# bootstrap setuptools if necessary
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name='buildutils',
    version="0.3",
    description="Distutils extensions for developing Python libraries and applications.",
    author="Ian Bicking, Ryan Tomayko",
    author_email="ianb@colorstudy.com",
    license="MIT",
    long_description="""\
buildutils provides several new commands for your package ``setup.py``
file to help make development easier.  It integrates with `distutils
<http://python.org/doc/current/lib/module-distutils.html>`_ using
``--command-packages``, or automatically will add commands to all your
`setuptools <http://peak.telecommunity.com/DevCenter/setuptools>`_
projects.

``addcommand``
  add a custom distutils command to a package/setup.cfg file
``announce``
  send a release announcement to mailing lists
  like python-announce-list@python.org
``bundle``
  create a bundle of a package plus all its dependencies
``checksum``
  generate MD5 and SHA-1 checksum files for distributables.
``etags``
  generate an TAGS file over all packages and module (for use in Emacs).
``flakes``
  find lint using the pyflakes utility.
``info``
  dumps information about the project.
``publish``
  push distributables and documentation up to a project site using
  ssh/scp/sftp.
``pudge``
  build Python documentation from restructured text documents and
  Python doc strings, using `Pudge <http://pudge.lesscode.org>`.
``pytest``
  run `py.test <http://codespeak.net/py/current/doc/test.html>`_ unit
  tests.
``stats``
  dump statistics on the number of lines, files, modules, packages,
  etc.
``svntag``
  make a Subversion tag for a versioned release
``use``
  bring in a working version of a dependency (uses setuptools egg
  stuff).

Buildutils is available in a `Mercurial repository
<https://www.knowledgetap.com/hg/buildutils>`_.
""",
    keywords="distutils development make build",
    #url="http://buildutils.lesscode.org/",    
    packages=find_packages(),
    include_package_data=True,
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'Intended Audience :: System Administrators',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Build Tools',
                 'Topic :: System :: Installation/Setup',
                 'Topic :: System :: Software Distribution',
                 'Topic :: Utilities'],
    entry_points="""
    [distutils.commands]
    checksum = buildutils.command.checksum:checksum
    etags = buildutils.command.etags:etags
    flakes = buildutils.command.flakes:flakes
    info = buildutils.command.info:info
    stats = buildutils.command.stats:stats
    # global?
    svntag = buildutils.command.svntag:svntag
    addcommand = buildutils.command.addcommand:addcommand
    customcommand = buildutils.command.customcommand:customcommand
    bundle = buildutils.command.bundle:bundle
    
    [console_scripts]
    pbu = buildutils.pysetup:main

    [buildutils.optional_commands]
    announce = buildutils.announce_command
    publish = buildutils.publish_command
    pudge = buildutils.pudge_command
    pytest = buildutils.pytest_command
    """,
    )
