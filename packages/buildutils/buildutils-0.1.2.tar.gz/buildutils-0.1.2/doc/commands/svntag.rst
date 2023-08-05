.. _svntag:

``svntag`` -- Tag Subversion project for release
------------------------------------------------

Tags a project that uses Subversion.  The project should be in
``Project/trunk`` in a repository, and it will be copied to
``Project/tags/X.Y``.

Also, if you have a ``setup.cfg`` file, and that file contains
``tag_build`` and/or ``tag_svn_revision`` in the ``[egg_info]``
section, those options will be removed.  This way you can use a
``setup.cfg`` like::

    [egg_info]
    tag_build = dev
    tag_svn_revision = true

And if you are using setuptools_ the distribution files generated from
the trunk will look like ``Package-0.5dev-r393``, so your
in-development packages are not confused with actual releases.

Synopsis
~~~~~~~~

Tag Subversion projects for release.

Options
~~~~~~~

version (``--version``, ``-v``)
  The version to be tagged, like "0.1".  This option must be given.

message (``--message``, ``-m``)
  The log message to use for commits.

build (``--build``, ``-b``)
  The location to check the new tag out to, for editing.

Notes
~~~~~

This package requires Python 2.4, as it uses the `subprocess
<http://python.org/doc/current/lib/module-subprocess.html>`_ module
for communicating with Subversion.  Also, the command-line version of
Subversion must be available as ``svn``.

It uses `setuptools`_ to edit the ``setup.cfg`` files.

.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
