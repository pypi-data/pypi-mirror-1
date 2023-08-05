.. _checksum:

``checksum`` -- Build SHA-1/MD5 Checksum Files
----------------------------------------------

The ``checksum`` command generates SHA-1 and/or MD5 checksum files
containing hashes for all distributables under the ``dist``
directory. It can generate a single checksum file for all distributables
or one checksum file per distributable. Checksum files may optionally be
signed using GPG.

Synopsis
~~~~~~~~

Build a source distribution and create a single SHA-1 checksum file
containing the hashes for all distributable files under the ``dist``
directory::

  pbu sdist checksum --sha

Common ``setup.cfg`` options::

  [checksum]
  per-file=1
  md5=0
  sha=1
  sign=1

Options
~~~~~~~

dist-dist (``--dist-dir=``, ``-d``)
  The directory containing distributables that should be signed. This 
  directory is also where ``.sha`` and/or ``.md5`` files are generated.

force (``--force``, ``-f``)
  Force generation of checksum files even if they exist and are up to date.

md5 (``--md5``, ``-m``)
  Generate `MD5`_ checksums. 

per-file (``--per-file``, ``-p``)
  When specified, multiple checksum files are generated - one for each 
  distributable in ``dist-dir``. The checksum file names will be equivelant
  to the original distribution with an additional ``sha`` or ``md5`` 
  extension. 

  When this option is not specified, checksums for all distributables
  are placed in a single file named ``name-version.sha`` or
  ``name-version.md5``, where ``name`` and ``version`` correspond to the
  values specified in ``setup.py``.

sha (``--sha``)
  Generate `SHA-1`_ checksums. This is the default. The ``--no-sha`` or ``-s``
  options can be used to turn of SHA-1 checksums.

sign (``--sign``)
  Sign all checksum files using `GnuPG`_. Note that this requires ``gpg``
  and a secret key.

.. _SHA-1: http://en.wikipedia.org/wiki/SHA-1
.. _MD5: http://en.wikipedia.org/wiki/MD5
.. _GnuPG: http://www.gnupg.org/

