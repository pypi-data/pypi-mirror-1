#####################################################################
#
# test_LDAPMultiPlugins.py
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
#####################################################################
""" Unit tests for LDAPMultiPlugin and ActiveDirectoryMultiPlugin

$Id: test_LDAPMultiPlugins.py 1404 2007-03-15 10:41:23Z jens $
"""

from unittest import main
from unittest import makeSuite
from unittest import TestSuite
from unittest import TestCase

from Products.PluggableAuthService.interfaces.plugins import \
     IUserEnumerationPlugin, IGroupsPlugin, IGroupEnumerationPlugin, \
     IRoleEnumerationPlugin


class LMPBaseTests(TestCase):

    def _getTargetClass(self):
        from Products.LDAPMultiPlugins.LDAPPluginBase import LDAPPluginBase
        return LDAPPluginBase
    

    def test_interfaces(self):
        from zope.interface.verify import verifyClass

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
    return TestSuite((
        makeSuite( ADMPTests ),
        makeSuite( LMPTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite') 
