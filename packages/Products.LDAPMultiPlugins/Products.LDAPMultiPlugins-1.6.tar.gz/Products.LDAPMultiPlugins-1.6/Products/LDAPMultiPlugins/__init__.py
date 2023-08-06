##############################################################################
#
# __init__.py	Initialization code for the LDAP Multi Plugins
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
##############################################################################

__doc__     = """ LDAPUserFolder shims initialization module """
__version__ = '$Revision: 1403 $'[11:-2]

from AccessControl.Permissions import add_user_folders
from Products.PluggableAuthService.PluggableAuthService import \
        registerMultiPlugin
from LDAPMultiPlugin import LDAPMultiPlugin, \
                            manage_addLDAPMultiPlugin, \
                            addLDAPMultiPluginForm
from ActiveDirectoryMultiPlugin import ActiveDirectoryMultiPlugin, \
                            manage_addActiveDirectoryMultiPlugin, \
                            addActiveDirectoryMultiPluginForm

def initialize(context):
    """ Initialize the LDAPMultiPlugin """
    registerMultiPlugin(LDAPMultiPlugin.meta_type)
    registerMultiPlugin(ActiveDirectoryMultiPlugin.meta_type)

    context.registerClass( LDAPMultiPlugin
                         , permission=add_user_folders
                         , constructors=( addLDAPMultiPluginForm
                                        , manage_addLDAPMultiPlugin
                                        )
                         , icon='www/ldapmultiplugin.png'
                         , visibility=None
                         )

    context.registerClass( ActiveDirectoryMultiPlugin
                         , permission=add_user_folders
                         , constructors=( addActiveDirectoryMultiPluginForm
                                     , manage_addActiveDirectoryMultiPlugin
                                     )
                         , icon='www/admultiplugin.png'
                         , visibility=None
                         )
