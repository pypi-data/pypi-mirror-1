# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: __init__.py 28752 2008-05-20 09:45:21Z sylvain $

from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
from Products.Silva.ExtensionRegistry import extensionRegistry

from plugins import oid
import SilvaOpenIDMember

registerMultiPlugin(oid.OpenIdPlugin.meta_type)

import install

def initialize(context):
    extensionRegistry.register(
        'silva.pas.openid', 'Silva OpenID Support', context, [],
        install, depends_on=('silva.pas.base', 'silva.captcha',))

    context.registerClass(oid.OpenIdPlugin,
                          permission=ManageUsers,
                          constructors=
                          (oid.manage_addOpenIDPluginForm,
                           oid.manage_addOpenIDPlugin),
                          visibility=None,
                          icon="www/openid.png")

    context.registerClass(SilvaOpenIDMember.SilvaOpenIDMember,
                          permission=ManageUsers,
                          constructors=
                          (SilvaOpenIDMember.manage_addOpenIDMemberForm,
                           SilvaOpenIDMember.manage_addOpenIDMember),
                          icon="www/member.png")
