.. _stats:

``stats`` -- Dump Code Statistics
---------------------------------

The ``stats`` command shows high level source code statistics about a
project including the number of files, modules, packages, and
lines. 

The following line statistics are provided for each file and in
aggregate:

lines
  The total number of lines in the file.
code
  The number of lines that contain python code (excludes comments, doc 
  strings, and blank lines)
doc
  The number of doc string lines.
comment
  The number of comment lines.
blank
  The number of blank lines.

Finally a ratio of test code to other code is provided.  Tests are
code in any module that starts with ``test_`` or in a package named
``test`` or ``tests``.

Synopsis
~~~~~~~~

Dump stats for the buildutils project::

  buildutils$ python setup.py stats
  running stats
     lines    code     doc comment   blank  file
   ------- ------- ------- ------- -------  -----------------------------------
	57      12      37       3       5  buildutils/__init__.py
       123      92      18       2      11  buildutils/cmd.py
	 6       2       3       0       1  buildutils/command/__init__.py
       188     159       4       4      21  buildutils/command/announce.py
       130     111       3       2      14  buildutils/command/checksum.py
	47      29       6       4       8  buildutils/command/etags.py
	57      29      15       1      12  buildutils/command/flakes.py
       109      90       1       6      12  buildutils/command/info.py
       144     119       3       5      17  buildutils/command/publish.py
       131     116       3       4       8  buildutils/command/pudge.py
       120     104       3       4       9  buildutils/command/pytest.py
       129     105       9       5      10  buildutils/command/stats.py
	98      79       3       3      13  buildutils/command/use.py
	25      18       1       3       3  buildutils/compat/__init__.py
       125      96       7       8      14  buildutils/compat/string_template.py
	58      27      25       0       6  buildutils/editor.py
       393     196     103      37      57  buildutils/pycount.py
       180     156      10       3      11  buildutils/pysetup.py
	 3       0       3       0       0  buildutils/test/__init__.py *
	 7       5       1       0       1  buildutils/test/test_compat.py *
	10       7       0       0       3  buildutils/test/test_publish.py *
      2140    1552     258      94     236  [total]
  Test code: 12  other code: 1540  ratio: 1:0.01 code to tests

  1552 lines of code, 21 modules, 4 packages.

Options
~~~~~~~

exclude-tests (``--exclude-tests``, ``-t``)
  Exclude any module identified as a test

totals (``--totals``)
  Show only the totals, not the file-by-file counts

extra-packages (``--extra-packages``, ``-p``)
  Any packages that wouldn't be installed (testing packages, for 
  instance) can be loaded with this option

Notes
~~~~~

The ``stats`` command is based on `pycount.py`_, by
Dinu C. Gherman, which is included in the ``buildutils`` distribution.

.. _pycount.py: http://starship.python.net/crew/gherman/playground/pycount/pycount.py
