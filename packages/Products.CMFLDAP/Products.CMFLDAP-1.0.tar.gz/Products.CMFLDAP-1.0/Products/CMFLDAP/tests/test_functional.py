##############################################################################
#
# Copyright (c) 2000-2009 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Functional tests for adding CMF members

$Id: test_functional.py 1700 2009-02-16 15:52:39Z jens $
"""

import unittest

from Testing.ZopeTestCase import ZopeLite

from Products.Five import zcml

from Products.CMFDefault.tests.test_join import MembershipTests
from Products.LDAPUserFolder.tests.base.dummy import LDAPDummyUserFolder


class LDAPMembershipTests(MembershipTests):

    def setUp(self):
        import Products.CMFLDAP
        zcml.load_config('configure.zcml', Products.CMFLDAP)

        MembershipTests.setUp(self)
        ZopeLite.installProduct('CMFLDAP')
        site = self.app.site

        profile_id = 'profile-Products.CMFLDAP:default'
        site.portal_setup.runAllImportStepsFromProfile(profile_id)
    
        # Remove the "standard" user folder and replace it with a
        # LDAPDummyUserFolder
        site.manage_delObjects(['acl_users'])
        site._setObject('acl_users', LDAPDummyUserFolder())

        # Register one new attribute for testing
        site.portal_memberdata.addMemberProperty('sn')


    def _makePortal(self):
        if getattr(self, 'app', None) is not None:
            # Running under CMF >= 2.1, this is a no-op since the portal is
            # already set up the way it is supposed to be.
            return self.app.site

        site = MembershipTests._makePortal(self)

        return self._mungeSite(site)
            

    def test_join_rdn_not_login( self ):
        # Test joing for situations where the login attribute is not the
        # same as the RDN attribute
        site = self._makePortal()
        site.acl_users._login_attr = 'sn'
        member_id = 'MyLastName'

        # If the RDN attribute is not provided, a ValueError is raised
        self.assertRaises( ValueError
                         , site.portal_registration.addMember
                         , member_id
                         , 'zzyyxx'
                         , properties={ 'username': member_id
                                      , 'email' : 'foo@bar.com'
                                      }
                         )
        u = site.acl_users.getUser(member_id)
        self.failIf(u)

        # We provide it, so this should work
        site.portal_registration.addMember( member_id
                                          , 'zzyyzz'
                                          , properties={ 'username': member_id
                                                       , 'email' : 'foo@bar.com'
                                                       , 'cn' : 'someuser'
                                                       }
                                          )
        u = site.acl_users.getUser(member_id)
        self.failUnless(u)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LDAPMembershipTests),
        ))
