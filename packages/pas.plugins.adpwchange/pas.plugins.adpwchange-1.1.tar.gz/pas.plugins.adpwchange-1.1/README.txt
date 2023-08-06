Introduction
============
`pas.plugins.adpwchange` is a `PAS`_ plugin which allows Active Directory
users to change their password.

This plugin does not offer any other Active Directory integration services:
it relies on another plugin such as `LDAPMultiPlugins`_ or `PloneLDAP`_
to expose Active Directory accounts in Zope.

The Active Direction integration is done using the `python-ad`_
package. *The python-ad package currently does not support OSX machines.*

.. _PAS: http://pypi.python.org/pypi/Products.PluggableAuthService
.. _LDAPMultiPlugins: http://pypi.python.org/pypi/Products.LDAPMultiPlugins
.. _PloneLDAP: http://pypi.python.org/pypi/Products.PloneLDAP
.. _python-ad: http://code.google.com/p/python-ad/


Configuration
=============
The plugin needs to be configured for the active directory environment.
It requires a default domain name that will be used for queries as well
as credentials for an account that is allowed to make password changes.

The user id attribute and login attribute settings have to be configured
to the same value as the `LDAPMultiPlugins` or `PloneLDAP` PAS plugin.
If they are not in sync you may can unexepcted behaviour or errors.

