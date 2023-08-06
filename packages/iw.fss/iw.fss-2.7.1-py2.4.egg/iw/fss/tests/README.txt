############################
FileSystemStorage unit tests
############################

Common::

  Be careful: unit tests need ZOPE_TESTCASE environ variable to be set.

  $ cd $INSTANCE_HOME
  $ # Creating default storage/backup directories
  $ mkdir var/fss_storage
  $ mkdir var/fss_backup
  $ export ZOPE_TESTCASE="y"

With Zope 2.8::

  $ bin/zopectl test [-v] [-p] [--nowarnings] iw.fss

With Zope 2.9::

  $ bin/zopectl test [-v] [-p] [--nowarnings] -s iw.fss

Run "zopectl help test" for other Zope versions.

Please keep `FileSystemStorage/etc/plone-filesystemstorage.conf.in` as
is and do not override (see `FileSystemStorage/README.txt`) for
running unit tests.

--------

.. $Id: README.txt 59136 2008-02-21 13:53:55Z tarek $
