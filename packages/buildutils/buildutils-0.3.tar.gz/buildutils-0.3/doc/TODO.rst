Open Issues
===========

* ``python-buildutils.el``: adds support for buildutils to emacs. Some of
  the things I'd like to do here:

  - ``py-buildutils-testfile``: locate the unit test for the module we're
    currently editing and run it.

  - ``py-buildutils-build``: prompts for target(s), locates closest
    ``setup.py`` and runs buildutils.

  - support for moving around in error messages from build, pytest, flakes,
    etc. (e.g. normal emacs ``C-x-``` stuff). 

* `pychecker` and/or `pylint` commands. (pyflakes was added and works
  fairly well).

* `announce` needs a lot of work in general.

* `announce` should have an option that brings up an editor on the message
  before sending. Note sure what the best way of accomplishing this is
  but I'm sure there are recipe's out there.

* Need some way of providing a SMTP password for `announce`. I left the
  command line option out because of the security issues with passing
  passwords on the command line. The password could be specified using
  distutils config files or we could prompt before sending (when we
  determine a password is needed?)

* I don't like how the `checksum` ``--md5`` and ``--sha`` options are
  working at present. ``--sha`` is on by default and ``--md5`` is
  off. If you do this...
  
  ::
  
      $ python setup.py checksums --md5
  
  ... both SHA and MD5 checksums are generated. I think it would be better
  to default to SHA but allow ``--md5`` to override that (or something).

* The `stats` command should show totals for each package. Right now
  stats are file based but I'd like them to be package / module based.

