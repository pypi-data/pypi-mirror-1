.. _announce:

``announce`` -- Send project announcement email
-----------------------------------------------

Sends a release announcement to python-announce-list@python.org or a
user specified list of email addresses. 

This command uses various pieces of project metadata to piece together
an announcement message. The default message is::

  ${name} ${version} is available:
  
  <${download_url}>
    
  ${long_description}
    
  For more information, visit the ${name} project site:
  <${url}>
  
  ${contact}
  <${contact_email}>

You can change the message in the project's ``setup.cfg`` using the 
``message=`` option. 

Synopsis
~~~~~~~~

Send an announcement to ``announce@example.com``::

  pbu announce --recipients=announce@example.com

Common ``setup.cfg`` options::

  [announce]
  recipients=announce@example.com, another@example.com
  reply-to=moe@stooges.com
  

Options
~~~~~~~

edit (``--edit``, ``-e``)
  Bring up an editor on the message before sending. This lets you preview the
  message and make changes before sending. If you don't want to send the
  message, you can delete all text before exiting the editor and the command
  will bail. 
  
  The editor used is based on the ``EDITOR`` environment variable. If no
  ``EDITOR`` environment variable is found, ``vi`` is attempted.

message (``--message=``, ``-m``)
  This option has varying usage depending on whether it is specified on the
  command line or in a config file. When the ``--message`` or ``-m`` argument
  is given, it is assumed to be a filename containing the message text. You
  can also pass "`-`" here to read from ``stdin``.
  
  When the ``message=`` option is pulled from a config file, it is the actual
  message.
  
  The default value is described in the command overview.
  
recipients (``--recipients=``, ``-t``)
  A comma or space seperated list of email addresses to send the 
  announcement email to.
  
  Default: ``python-announce-list@python.org``

reply-to (``--reply-to=``, ``-f``)
  The email address where replies should be sent.
  
  Default: ``${contact_name}``

subject (``--subject``, ``-s``)
  The announcement email's subject.

  Default: ``ANN: ${fullname} - ${description}``

The following options support variable expansion: ``message``, ``reply-to``,
``subject``, ``recipients``.

Notes
~~~~~

The ``announce`` command will attempt to use ``sendmail`` if found and
fallback to an SMTP server on ``localhost``. Future versions of the
command will include support for specifying the sending method, SMTP
host/auth, etc.
