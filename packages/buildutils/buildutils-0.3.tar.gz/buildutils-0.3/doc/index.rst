======================
Python Build Utilities
======================

`Python Build Utilities` (``buildutils``) is a set of extension commands
to python's standard distutils_ that are often useful during development
and deployment of python projects. `buildutils` was created with the
desire of removing ``make`` and other external build tools from the
python development process.

Because buildutils is integrated with distutils, information about a
project can be obtained from the project's ``setup.py`` and
``setup.cfg`` files. This allows commands to provide smart defaults when
invoking external tools and utilities. 

Installing
~~~~~~~~~~

The quickest method of installation is through `EasyInstall`_::

  easy_install -fhttp://lesscode.org/eggs/ buildutils

You can also grab a distributable of the latest version from `this
directory`_ and install old school by extracting the files from the 
distribution and running ``python setup.py install``.

.. _this directory: http://lesscode.org/dist/buildutils/

Documentation
~~~~~~~~~~~~~

- The `User's Guide`_ contains information on using buildutils with
  python projects and customizing build process.
- The `Command Reference`_ provides reference text for each of the
  commands included with buildutils.
- See `Extension Guidelines`_ for information on building commands for
  buildutils.
- There is generated python documentation available for the
  `buildutils`_ package.

Hacking
~~~~~~~

The subversion repository is at

|  http://lesscode.org/svn/buildutils/

You can grab the latest unstable sources with something like::

  svn co http://lesscode.org/svn/buildutils/trunk buildutils

Community
~~~~~~~~~

I'd prefer to discuss buildutils on the `distutils-sig mailing list`_
until we get kicked off :)

I'm extremely liberal with subversion access and love getting
patches. If you would like to contribute code or documentation contact
me at <rtomayko@lesscode.org> or drop by ``irc.freenode.net`` - my nick
is ``rtomayko`` and I can usually be found lurking in ``#python``.

Back Matter
~~~~~~~~~~~

Buildutils is `Free Software`_ by `Ryan Tomayko`_ and is licensed under 
`The MIT License`_.


.. _distutils: http://www.python.org/doc/current/lib/module-distutils.html
.. _User's Guide: guide.html
.. _Command Reference: commands.html
.. _Extension Guidelines: extensions.html
.. _buildutils: module-buildutils.html
.. _EasyInstall: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _distutils-sig mailing list: http://mail.python.org/mailman/listinfo/distutils-sig
.. _browsable here: http://lesscode.org/projects/buildutils/browse/
.. _Free Software: http://www.gnu.org/philosophy/free-sw.html
.. _Ryan Tomayko: http://naeblis.cx/rtomayko/
.. _The MIT License: http://opensource.org/licenses/mit-license.php
