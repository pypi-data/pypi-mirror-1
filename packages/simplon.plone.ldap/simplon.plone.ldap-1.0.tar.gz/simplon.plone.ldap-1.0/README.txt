LDAP control panel for Plone
============================

Overview
--------

simplon.plone.ldap provides a user interface in a Plone site to manage
LDAP and Active Directory servers. 

It builds on the functionality provided by LDAPMultiPlugins_, LDAPUserFolder_
and PloneLDAP_.


Active Directory
----------------

Active Directory provides an LDAP interface to its data. Using this interface
Plone can use both users and groups from an Active Directory system. Writing
to Active Directory is not supported.

With Active Directory you can use two different properties as login name:
`userPrincipalName` and `sAMAccountName`. `sAMAccountName` is the plain account
name without any domain information and is only unique within a single domain.
If your environment only uses a single AD domain this option is the best
choice. For environments with multiple names the `userPrincipalName` attribute
can be used since this includes both account name and domain information.


Since Plone does not support binary user ids it is not possible to use the
`objectGUID` attribute as user ids. Instead you can use either `sAMAccountName`
or `userPrincipalName`. The same criteria for choosing a login name also
apply to selecting the user id attribute.

Standard LDAP
-------------

LDAP directory servers are fully supported. LDAP users and groups are usable
as standard Plone users and groups can be me managed normally. Creating and
deleting users and groups is supported.


Installing
----------

This package is made to be used as a normal python package within Zope 2.10
and needs Plone 3.0 or later. 

You need to install PloneLDAP_ and its requirements in your Zope instance
before you can use simplon.plone.ldap. This can easily be done by downloading
its product bundle and extracting that in your Products directory.

Install without buildout
~~~~~~~~~~~~~~~~~~~~~~~~

First you need to install this package in the python path for your
Zope instance. This can be done by installing it in either your system
path packages or in the lib/python directory in your Zope instance.

After installing the package it needs to be registered in your Zope instance.
This can be done by putting a simplon.plone.currency-configure.zcml file in the
etc/pakage-includes directory with this content::

  <include package="simplon.plone.currency" />

or, alternatively, you can add that line to the configure.zcml in a
package or Product that is already registered.

Installing with buildout
~~~~~~~~~~~~~~~~~~~~~~~~

If you are using `buildout`_ to manage your instance installing
simplon.plone.currency is even simpler. You can install it by adding
it to the eggs line for your instance::

  [instance]
  eggs = simplon.plone.ldap
  zcml = simplon.plone.ldap

The last line tells buildout to generate a zcml snippet that tells Zope
to configure simplon.plone.ldap.

.. _buildout: http://pypi.python.org/pypi/zc.buildout


Copyright and credits
---------------------

:

Copyright
    simplon.plone.ldap is Copyright 2007 by Simplon

Credits
     Wichert Akkerman <wicher@simplon.biz>

Funding
     CentrePoint_


.. _python-ldap: http://python-ldap.sourceforge.net/
.. _LDAPUserFolder: http://www.dataflake.org/software/ldapuserfolder/
.. _LDAPMultiPlugins: http://www.dataflake.org/software/ldapmultiplugins/
.. _PloneLDAP: http://plone.org/products/ploneldap/
.. _CentrePoint: http://centrepoint.org.uk/
