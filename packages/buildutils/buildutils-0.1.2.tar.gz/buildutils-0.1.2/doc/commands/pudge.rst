.. _pudge:

``pudge`` -- Generate Documentation
-----------------------------------

The ``pudge`` command is used to generate documentation in either HTML
4.01 or XHTML 1.0 format. `pudge` can extract documentation strings from
python objects and has support for restructured text. It's also possible
to generate documentation from restructured text documents.

Synopsis
~~~~~~~~

Generate documentation for all modules and packages, include
a GNU Free Documentation License, and open the documentation in a web
browser after it has been generated::

  pbu pudge --license=gnu -o

Common ``setup.cfg`` options::

  [pudge]
  docs=doc/index.rst doc/users-guide.rst
  title=Some Package
  license=cc
  xhtml=1

Options
~~~~~~~

dest (``--dest=``, ``-d``)
  The directory where documentation should be generated. If this option
  isn't specified, ``build/doc`` is assumed.

docs (``--docs=``, ``-i``)
  List of restructured text documents to include in generated
  documentation.

license (``--license=``)
  Include a standard license document. Current options are 'gnu' for the 
  GNU Free Documentation License and 'cc' for a Creative Commands 
  Attribution, NonCommercial, copyleft license.

modules (``--modules=``, ``-m``)
  List of module or package names that should be documented. This argument
  defaults to all modules and packages specified in the projects ``setup.py``
  file using the ``py_modules`` and ``packages`` arguments to ``setup()``. 
  In most cases, this option should not need to be customized.

open (``--open``, ``-o``)
  Open generated documentation in a web browser. Handy when testing generated
  documentation.

pages (``--pages=``, ``-p``)
  Specify the list of pages that should be opened when the ``--open``
  option is provided. Separate page file names by commas::
  
    pbu pudge -o --pages=index.html,mydoc.html,module-foo.bar.html

stages (``--stages=``, ``-s``)
  A comma separated list of documentation generation stages that should
  be performed. This can speed the generation process during testing by 
  omitting steps that are not needed. Available stages are as follows:
  
  - `docs` - generate documentation from restructured text documents 
    specified by the ``--docs`` option.
  - `index` - generate the index document.
  - `reference` - generate module reference documentation.
  - `copy` - copy other files (CSS, images, etc.)
  - `source` - generate syntax colored source files.

title (``--title=``)
  The title of the documentation set.

xhtml (``--xhtml=``, ``-x``)
  Output documentation as XHTML 1.0 instead of HTML 4.01. HTML
  4.01 is recommended due to browser compatibility issues with
  XHTML 1.0.
