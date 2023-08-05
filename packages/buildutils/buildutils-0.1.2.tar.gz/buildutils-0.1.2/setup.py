#!/usr/bin/env python
"""Distutils setup file, used to install or test 'buildutils'"""

# bootstrap setuptools if necessary
from ez_setup import use_setuptools
use_setuptools()

import buildutils as package
from setuptools import setup

from glob import glob

# grab stuff from package
package_name = package.__name__
package_version = package.__version__

setup(
    name=package_name,
    version=package_version,
    description="Distutils extensions for developing Python libraries and applications.",
    author="Ryan Tomayko",
    author_email="rtomayko@lesscode.org",
    license="MIT",
    long_description="""\
buildutils provides several new commands for your package ``setup.py``
file to help make development easier.  It integrates with `distutils
<http://python.org/doc/current/lib/module-distutils.html>`_ using
``--command-packages``, or automatically will add commands to all your
`setuptools <http://peak.telecommunity.com/DevCenter/setuptools>`_
projects.

``announce``
  send a release announcement to mailing lists
  like python-announce-list@python.org
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

Buildutils is only available by checkout from the `Subversion
respository
<svn://lesscode.org/buildutils/trunk#egg=buildutils-dev>`_ at
http://lesscode.org/svn/buildutils/ or ``easy_install
buildutils==dev``

""",
    keywords = "distutils development make build",
    url = "http://%s.lesscode.org/" % package_name,
    
    download_url = "http://%s.lesscode.org/dist/%s/" % \
                   (package_name, package_version),
    
    scripts=['pbu'],
    py_modules=[],
    
    packages=[package_name,
              package_name + '.command',
              package_name + '.compat',
              package_name + '.test'],
    
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
    announce = buildutils.command.announce:announce
    checksum = buildutils.command.checksum:checksum
    etags = buildutils.command.etags:etags
    flakes = buildutils.command.flakes:flakes
    info = buildutils.command.info:info
    publish = buildutils.command.publish:publish
    pudge = buildutils.command.pudge:pudge
    pytest = buildutils.command.pytest:pytest
    stats = buildutils.command.stats:stats
    svntag = buildutils.command.svntag:svntag
    """,
    )
