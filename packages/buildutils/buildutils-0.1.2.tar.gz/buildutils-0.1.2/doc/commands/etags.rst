.. _etags:

``etags`` -- Generate Emacs TAGS file
-------------------------------------

Generates an Emacs ``TAGS`` file for all packages and modules in the 
current project.  

Emacs Tags_ provide an indexing mechanism for various types source files
that allows Emacs to provide such cool features as auto-complete and
go-to-definition.

Once the ``TAGS`` file is generated, you can bring it into Emacs by
invoking ``M-x visit-tags-table`` and then entering the path to the 
TAGS file (the project root directory).

Some of the useful Tags functions are:

======================= ============================================
Keystroke               Description
======================= ============================================
``M-.``                 Find first definition of a tag.
``M-x tags-search``     Search for a specified regular expression
                        through the files in the selected tag table.
``M-,``                 Find next definition of previous tag, next
                        occurrence of specified regular expression.
======================= ============================================

More information on Emacs Tags can be found under the `Tags Node`_ of the
GNU Emacs Manual.

.. _Tags Node:
.. _Tags: http://www.gnu.org/software/emacs/manual/html_node/Tags.html#Tags

Synopsis
~~~~~~~~

Running the ``etags`` command::

  pbu etags

Options
~~~~~~~

command (``--command=``, ``-c``)
  Specify the location of the ``etags`` executable. The default is to search
  along the ``$PATH`` looking for a command named ``etags``.

tags-file (``--tags-file=``, ``-t``)
  Where to write the TAGS file. Default is a file named ``TAGS`` in the
  project's directory (i.e. right next to ``setup.py``).

force (``--force``, ``-f``)
  For creation of the ``TAGS`` file even if a ``TAGS`` file exists that
  is newer than all of the source files.

