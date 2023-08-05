"""Distutils extensions for developing Python libraries and applications.

The `buildutils` package contains extensions to Python's standard
distribution utilities (`distutils`) that are often useful during the
development of Python projects. `buildutils` was created to scratch an
itch: removing ``make`` from the Python development process and partially
to gain a better understanding of how `distutils` works.

The following extension commands are included:

announce
  send a release announcement to mailing lists
  like python-announce-list@python.org
checksum
  generate MD5 and SHA-1 checksum files for distributables.
etags
  generate an TAGS file over all packages and module (for use in Emacs).
flakes
  find lint using the pyflakes utility.
info
  dumps information about the project.
publish
  push distributables and documentation up to a project site using
  ssh/scp/sftp.
pudge
  build Python documentation from restructured text documents and
  Python doc strings.
pytest
  run py.test unit tests.
stats
  dump statistics on the number of lines, files, modules, packages,
  etc.
svntag
  make a Subversion tag for a versioned release
use
  bring in a working version of a dependency (uses setuptools egg
  stuff).

"""

__version__ = "0.1.2"

# python version compatibility libraries
import buildutils.compat as compat
import buildutils.command as command

# the following trick taken from the setuptools.command.
# this injects our commands into the distutils.command package.
def inject_commands():
    import distutils.command
    distutils.command.__path__.extend(command.__path__)
    all = distutils.command.__all__
    commands = [c for c in command.__all__ if c not in all]
    all.extend(commands)
    all.sort()
    
inject_commands()
del inject_commands

