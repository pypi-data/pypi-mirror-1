============================
Buildutils Command Reference
============================

:Editors: Ryan Tomayko <rtomayko@lesscode.org>
:Revision: $Rev$
:Date: $Date: 2005-03-09 15:26:45 -0500 (Wed, 09 Mar 2005) $
:Copyright: Copyright © 2005
:License: GNU Free Documentation License

The `Buildutils Command Reference` provides usage information for the
commands available in the buildutils project.

----

.. contents:: Table of Contents
   :backlinks: entry
   :depth: 2

----

The Commands
============

.. include:: commands/announce.rst

----

.. include:: commands/checksum.rst

----

.. include:: commands/etags.rst

----

.. include:: commands/flakes.rst

----

.. include:: commands/info.rst

----

.. include:: commands/publish.rst

----

.. include:: commands/pudge.rst

----

.. include:: commands/pytest.rst

----

.. include:: commands/stats.rst

----

.. include:: commands/svntag.rst

----

Additional Command Dependencies
===============================

Certain commands require additional packages.

============= ========================================================================
Command       Dependencies
============= ========================================================================
`checksum`_   `GnuPG`
etags         The ``etags`` command (included with Emacs)
`pudge`_      `Pudge Documentation Utility <http://lesscode.org/projects/pudge/>`_,
              `Kid Template <http://lesscode.org/projects/kid/>`_,
              `ElementTree <http://effbot.org/zone/element-index.htm>`_
flakes        `pyflakes <http://divmod.org/projects/pyflakes>`_
pytest        `py.test <http://codespeak.net/py/current/doc/test.html>`_
publish       The ``scp`` or ``sftp`` commands (included with
              OpenSSH).
svntag        Python 2.4 and the ``svn`` command
============= ========================================================================


.. `Pudge Documentation Utility`: http://lesscode.org/projects/pudge/
  
