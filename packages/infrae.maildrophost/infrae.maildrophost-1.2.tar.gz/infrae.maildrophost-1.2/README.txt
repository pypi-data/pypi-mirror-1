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
  version = 1.22

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
directory, so data is preserved when update (if there is any data).

You can use the ``target`` option to specify a different folder to
install the product, for instance if you already have a part called
``dist-products`` for your Zope products::

  target = ${dist-products:location}

The version option will be used to generate the download url::

  http://www.dataflake.org/software/maildrophost/maildrophost_<version>/MaildropHost-<version>.tgz

In recent versions of `MaildropHost`_ (>= 1.22) the config file has
changed name, setting the ``version`` option will make the recipe
choose the right name.

It is also possible to override the download url by setting a ``url``
option.

Settings
--------

You can customize some of settings of `MaildropHost`_:

``mail_dir``
  Directory to use as *home directory* for the deamon. By default it's
  ``${buildout:directory}/var/maildrop`` It will be created if it
  doesn't exists.

``spool_dir``
  Directory to use as a spool. By default it will be
  ``${mail_dir}/spool``. The directory will be created if it doesn't
  exist already.

``pid_file``
  PID file to use for the daemon. By default it will be
  ``${mail_dir}/maildrop.pid``.

``smtp_host``
  SMTP server to use. Default to localhost.

``smtp_port``
  Port to use. Default to default SMTP port, 25.

``login``
  If the SMTP server require authentication, login to use.

``password``
  If the SMTP server require authentication, password to use.

``tls``
  If 1, `MaildropHost`_ will be speaking to a TLS enabled SMTP server.

``batch``
  Set ``MAILDROP_BATCH``.

``add_messageid``
  Add a message id to the sent mail.

``pool_interval``
  Must be an integer which define the interval in seconds between two
  check for new mail in the spool directory. Default is 120 seconds.

``wait_interval``
  Must be an interger or float which say how much time the daemon
  should wait between sending two mails to the mail server.


Latest version
--------------

The latest version is available in a `Subversion repository
<https://svn.infrae.com/buildout/infrae.maildrophost/trunk>`_.

.. _MaildropHost: http://www.dataflake.org/software/maildrophost
