.. _publish:

``publish`` -- Push distributables and documentation to remote site
-------------------------------------------------------------------

The publish command can be used to transfer distributables and
documentation files to a remote site using a variety of transport
protocols. 

Currently, only SSH/SCP or SFTP are supported and require external ``ssh``, 
``scp``, and ``sftp`` system commands.

Synopsis
~~~~~~~~

Publishing distributables after building and generating checksum_ files::

  pbu sdist bdist_egg checksum publish --dist-dest=scp://stooges.com/project/

The ``setup.cfg`` file is an excellent place to put remote locations::

  [publish]
  dist-dest=scp://curly@stooges.com/projects/$name/
  make-dirs=1

Options
~~~~~~~

dist-dir (``--dist-dir=``, ``-d``)
  Directory containing distributables to transfer. It should be rare that
  the default value needs overridden.

dist-dest (``--dist-dest=``, ``-t``)
  The destination URL where distributables should be transfered.

doc-dir (``--doc-dir=``)
  Directory containing documentation.

doc-dest (``--doc-dest=``)
  The destination URL where documentation files should be transfered.

make-dirs (``--make-dirs=``, ``-m``)
  Try to create the dest directories if they do not exist on the remote
  site.

protocol-list (``--protocol-list``)
  Display a list of available protocols / URL schemes that can be used
  to transfer files.

