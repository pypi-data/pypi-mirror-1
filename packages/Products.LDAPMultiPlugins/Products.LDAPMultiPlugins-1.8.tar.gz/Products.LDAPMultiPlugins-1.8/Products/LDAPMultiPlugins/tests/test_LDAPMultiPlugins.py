##############################################################################
#
# Copyright (c) 2005-2009 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" LDAPMultiPlugin and ActiveDirectoryMultiPlugin unit tests

$Id: test_LDAPMultiPlugins.py 1694 2009-02-08 08:21:45Z jens $
"""

import unittest

from Products.PluggableAuthService.interfaces.plugins import \
     IUserEnumerationPlugin
from Products.PluggableAuthService.interfaces.plugins import \
    IGroupsPlugin
from Products.PluggableAuthService.interfaces.plugins import \
    IGroupEnumerationPlugin
from Products.PluggableAuthService.interfaces.plugins import \
    IRoleEnumerationPlugin

from Products.LDAPMultiPlugins.interfaces import ILDAPMultiPlugin


class LMPBaseTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.LDAPMultiPlugins.LDAPPluginBase import LDAPPluginBase
        return LDAPPluginBase

    def test_interfaces(self):
        from zope.interface.verify import verifyClass

        verifyClass(ILDAPMultiPlugin, self._getTargetClass())

        verifyClass(IUserEnumerationPlugin, self._getTargetClass())
        verifyClass(IGroupsPlugin, self._getTargetClass())
        verifyClass(IGroupEnumerationPlugin, self._getTargetClass())
        verifyClass(IRoleEnumerationPlugin, self._getTargetClass())


class ADMPTests(LMPBaseTests):

    def _getTargetClass(self):
        from Products.LDAPMultiPlugins.ActiveDirectoryMultiPlugin import \
             ActiveDirectoryMultiPlugin       
        return ActiveDirectoryMultiPlugin


class LMPTests(LMPBaseTests):

    def _getTargetClass(self):
        from Products.LDAPMultiPlugins.LDAPMultiPlugin import LDAPMultiPlugin
        return LDAPMultiPlugin


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ADMPTests),
        unittest.makeSuite(LMPTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite') 

