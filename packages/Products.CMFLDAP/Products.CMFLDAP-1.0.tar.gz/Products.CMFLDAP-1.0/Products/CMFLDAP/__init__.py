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
""" Products.CMFLDAP initialization code

$Id: __init__.py 1700 2009-02-16 15:52:39Z jens $
"""

import LDAPMembershipTool
import LDAPMemberDataTool

# Un-break tool instances based on Products.LDAPUserFolder
__module_aliases__ = (
    ('Products.LDAPUserFolder.LDAPMembershipTool', LDAPMembershipTool),
    ('Products.LDAPUserFolder.LDAPMemberDataTool', LDAPMemberDataTool),
    )

def initialize(context):
    context.registerHelp()
