infrae.maildrophost
===================

``infrae.maildrophost`` is used to download and install `MaildropHost`_
for Zope, and configure a maildrophost server using the same
configuration than the Zope product. 

Example in buildout::

  [buildout]
  parts = 
      maildrophost
      instance
  
  [maildrophost]
  recipe = infrae.maildrophost
  smtp_host = localhost
  smtp_port = 25
  url = http://www.dataflake.org/software/maildrophost/maildrophost_1.20/MaildropHost-1.20.tgz

  [instance]
  ...
  products =
       ...
       ${maildrophost:location}
       ...
  ...

This will install `MaildropHost`_, create configuration files for the
daemon, and put a start/stop script in the ``bin`` directory of the
buildout tree.

Spool and PID files are put by default in the ``var/maildrop``
directory, so data is preserved when update (if there is any
data). This setting can be overrided with the ``mail-dir`` option.

You can use the ``target`` option to specify a different folder to
install the product, for instance if you already have a part called
``dist-products`` for your Zope products::
        
  target = ${dist-products:location}

As well, you can use ``login`` and ``password`` to define an
authentication against the SMTP server. 

``poll_interval`` must be an integer which define the interval in
seconds between two check for new mail in the spool directory. Default
is 120 seconds.

Latest version
--------------

The latest version is available in a `Subversion repository
<https://svn.infrae.com/buildout/infrae.maildrophost/trunk>`_.

.. _MaildropHost: http://www.dataflake.org/software/maildrophost
