infrae.maildrophost
===================

``infrae.maildrophost`` is used to download and install MaildropHost
for Zope, and configure a maildrophost server using the same
configuration than the Zope product. 

Example in buildout::

  [buildout]
  parts = maildrophost
  

  [maildrophost]
  recipe = infrae.maildrophost
  smtp_host = localhost
  smtp_port = 25
  url = http://www.dataflake.org/software/maildrophost/maildrophost_1.20/MaildropHost-1.20.tgz

This will install MaildropHost, create configuration files for the
daemon, and put a start/stop script named in the ``bin`` directory of
the buildout tree.

Spool and PID files are put by default in the ``var/maildrop``
directory, so data is preserved when update (if there is any
data). This setting can be overrided with the ``mail-dir`` option.

Latest version
--------------

The latest version is available in a `Subversion repository
<https://svn.infrae.com/buildout/infrae.maildrophost/trunk>`_.

