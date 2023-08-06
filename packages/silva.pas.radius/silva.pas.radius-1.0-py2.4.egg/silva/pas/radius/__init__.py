# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: __init__.py 32250 2008-11-20 14:58:02Z sylvain $

from AccessControl.Permissions import manage_users as ManageUsers
from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.PluggableAuthService import registerMultiPlugin

from plugins import radius
import install

registerMultiPlugin(radius.RadiusPlugin.meta_type)

def initialize(context):
    extensionRegistry.register(
        'silva.pas.radius', 'Silva Radius Support', context, [],
        install, depends_on=('silva.pas.base',))

    context.registerClass(radius.RadiusPlugin,
                          permission=ManageUsers,
                          constructors=
                          (radius.manage_addRadiusPluginForm,
                           radius.manage_addRadiusPlugin),
                          visibility=None,
                          icon="www/radius.png")
