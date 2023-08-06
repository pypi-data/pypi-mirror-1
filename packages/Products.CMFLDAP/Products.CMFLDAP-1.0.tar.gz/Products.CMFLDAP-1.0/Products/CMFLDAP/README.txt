==================
 Products.CMFLDAP
==================

.. contents::

NOTE: Do not install the CMFLDAP GenericSetup extension profile into a Plone 
site. They are meant for pure CMF sites only and will break Plone.

Bug tracker
===========
Please post questions, bug reports or feature requests to the bug tracker
at http://www.dataflake.org/tracker/

SVN version
===========
You can retrieve the latest code from Subversion using setuptools or
zc.buildout via this URL:

http://svn.dataflake.org/svn/Products.CMFLDAP/trunk#egg=Products.CMFLDAP

Debugging problems
==================
All log messages are sent to the standard Zope event log 'event.log'. In 
order to see more verbose logging output you need to increase the log level 
in your Zope instance's zope.conf. See the 'eventlog' directive. Setting 
the 'level' key to 'debug' will maximize log output and may help pinpoint 
problems during setup and testing.

LDAP Schema considerations when used with the CMF
=================================================
The CMF (and by extension, Plone) expect that every user has an email
address. In order to make everything work correctly your LDAP user
records must have a "mail" attribute or similar, and this attribute must 
be set up in the "LDAP Schema" tab of your LDAPUserFolder. When you add the
email schema item make sure you set the "Map to Name" field to "email". 

The attributes that show up on the join form and the personalize view
are governed by the properties you 'register' using the 'Member Properties' 
tab in the portal_memberdata tool ZMI view, which in turn is sourced from 
the 'LDAP Schema' tab in the LDAPUserFolder ZMI view. Attributes you would 
like to enable for portal members must be set up on the LDAPUserFolder 
'LDAP Schema' tab first, and then registered using the 'Member properties' 
screen in the Member data tool ZMI view.
