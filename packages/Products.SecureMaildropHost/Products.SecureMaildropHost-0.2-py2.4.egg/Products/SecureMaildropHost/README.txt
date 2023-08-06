------------------
SecureMaildropHost
------------------

Introduction
------------

SecureMaildropHost marries SecureMailHost_ and MaildropHost_, making this a
drop-in replacement for SecureMailHost.

SecureMaildropHost uses both SecureMailHost and MaildropHost to do it's work,
so both must be installed.

.. _SecureMailHost: http://plone.org/products/securemailhost
.. _MaildropHost: http://www.dataflake.org/software/maildrophost/

Installation
------------

- Install and configure MaildropHost first!
- Unpack this Product into your instance Products directory
- Restart Zope, navigate to your SecureMailHost instance (usually named
  ``MailHost``), note it's settings. Make sure you configure your MaildropHost
  queue to use the same settings.
- Delete the SecureMailHost, and create a SecureMaildropHost with the same id
  in it's place

License
-------

ZPL 2.1, see LICENSE.txt

Credits
-------

SecureMaildropHost was developed by Plone Solutions for internal use, Dec 2006

Design and development::
  `Plone Solutions <http://plonesolutions.com>`__ (Martijn Pieters)
