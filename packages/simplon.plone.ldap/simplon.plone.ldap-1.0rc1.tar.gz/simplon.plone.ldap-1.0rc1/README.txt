simplon.plone.ldap
==================

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
