# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: install.py 32250 2008-11-20 14:58:02Z sylvain $

from zope.interface import alsoProvides, noLongerProvides

from Products.PluggableAuthService.interfaces.plugins import *
from silva.pas.base.interfaces import IPASMemberService

from interfaces import IRaduisAware

def install(root):
    """Installation method for OpenID support
    """
    assert IPASMemberService.providedBy(root.service_members)

    # Register PAS plugins
    registerPASPlugins(root.acl_users)

    alsoProvides(root.service_members, IRaduisAware)


def uninstall(root):
    """Uninstall OpenID support
    """
    assert IPASMemberService.providedBy(root.service_members)
    # FIXME: We should restore the previous login page

    unregisterPASPlugins(root.acl_users)

    # We remove the registration page.
    noLongerProvides(root.service_members, IRaduisAware)

def is_installed(root):
    return IRaduisAware.providedBy(root.service_members)


def registerPASPlugins(pas):
    """Register new PAS plugins.
    """
    pas.manage_addProduct['plone.session'].manage_addSessionPlugin('session')
    pas.manage_addProduct['silva.pas.membership'].manage_addMembershipPlugin('members')
    if getattr(pas, 'raduis', None) is None:
        pas.manage_addProduct['silva.pas.radius'].manage_addRadiusPlugin('radius')

    plugins = pas.plugins
    plugins.activatePlugin(IExtractionPlugin, 'session')
    plugins.movePluginsUp(IExtractionPlugin, ['session',])
    plugins.activatePlugin(IAuthenticationPlugin, 'session')
    plugins.movePluginsUp(IAuthenticationPlugin, ['session',])
    plugins.movePluginsUp(IAuthenticationPlugin, ['session',])
    plugins.deactivatePlugin(ICredentialsResetPlugin, 'cookie_auth')
    plugins.activatePlugin(ICredentialsResetPlugin, 'session')
    plugins.deactivatePlugin(ICredentialsUpdatePlugin, 'cookie_auth')
    plugins.activatePlugin(ICredentialsUpdatePlugin, 'session')

    plugins.activatePlugin(IAuthenticationPlugin, 'radius')
    plugins.movePluginsUp(IAuthenticationPlugin, ['radius',])
    plugins.movePluginsUp(IAuthenticationPlugin, ['radius',])

    plugins.activatePlugin(IUserEnumerationPlugin, 'members')
    plugins.movePluginsUp(IUserEnumerationPlugin, ['members',])
    plugins.movePluginsUp(IUserEnumerationPlugin, ['members',])


def unregisterPASPlugins(pas):
    """Remove PAS plugins.
    """
    pas.manage_delObjects(['session', 'members',])
    plugins = pas.plugins
    plugins.deactivatePlugin(IAuthenticationPlugin, 'radius')
    plugins.activatePlugin(ICredentialsResetPlugin, 'cookie_auth')
    plugins.activatePlugin(ICredentialsUpdatePlugin, 'cookie_auth')



if __name__ == '__main__':
    print """This module is not an installer. You don't have to run it."""
