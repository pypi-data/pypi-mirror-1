############################
FileSystemStorage unit tests
############################

Common::

  $ cd $INSTANCE_HOME
  $ # Creating default storage/backup directories
  $ mkdir var/fss_storage
  $ mkdir var/fss_backup

With Zope 2.8::

  $ bin/zopectl test [-v] [-p] [--nowarnings] iw.fss

With Zope 2.9::

  $ bin/zopectl test [-v] [-p] [--nowarnings] -s iw.fss

Run "zopectl help test" for other Zope versions.

Please keep `FileSystemStorage/etc/plone-filesystemstorage.conf.in` as
is and do not override (see `FileSystemStorage/README.txt`) for
running unit tests.

--------

.. $Id: README.txt 69081 2008-07-28 13:39:24Z b_mathieu $
