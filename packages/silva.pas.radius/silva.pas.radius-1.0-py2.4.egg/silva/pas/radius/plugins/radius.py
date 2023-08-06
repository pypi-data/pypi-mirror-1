##############################################################################
#
# PASRadius - Radius authentication plugin for PluggableAuthService
# Copyright (C) 2007 Shimizukawa Takayuki
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: radius.py 32253 2008-11-20 15:48:38Z sylvain $
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from zope.interface import implementedBy

try:
    from zope.interface import Interface
except ImportError:
    from Products.PluggableAuthService.utils import Interface

from Products.PluggableAuthService.interfaces import plugins
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.permissions import ManageUsers
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin

from silva.pas.radius import radius

class IRadiusPlugin(Interface):
    """ Marker interface.
    """

def manage_addRadiusPlugin(self, id, title='', RESPONSE=None ):
    """
    add radius plugin
    """
    plugin = RadiusPlugin(id, title)
    self._setObject(id, plugin)

    if RESPONSE is not None:
        RESPONSE.redirect('manage_workspace')


manage_addRadiusPluginForm = PageTemplateFile('../www/radiusAddForm',
                globals(), __name__="manage_addRadiusPluginForm")

class RadiusPlugin(BasePlugin):
    """PAS plugin for radius users.
    """

    meta_type = "Silva Radius Plugin"
    security = ClassSecurityInfo()

    manage_options = ( ( { 'label': 'Radius',
                           'action': 'manage_editRadiusPluginForm', }
                         ,
                       )
                       + BasePlugin.manage_options[:]
                     )

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title
        self.setRadius('localhost',1812,'testing123')

    security.declarePrivate('setRadius')
    def setRadius(self, host, port, password):
        """why need doc string??"""
        self.host = host
        self.port = port
        self.password = password

    def authenticateCredentials(self, credentials):
        r = radius.Radius(self.password, self.host, self.port)
        login = credentials.get('login', '')
        password = credentials.get('password', '')
        try:
            if r.authenticate(login, password):
                return (login, login) # shuld return user name ?
        except:
            pass
        return (None, None)

    manage_editRadiusPluginForm = PageTemplateFile('../www/radiusEditForm',
                 globals(), __name__="manage_editRadiusPluginForm")

    security.declareProtected(ManageUsers, 'manage_editRadiusPlugin')
    def manage_editRadiusPlugin(self, host, port, password, RESPONSE=None):
        """why need doc string??"""
        error_message = ''
        try:
            port = int(port)
            self.setRadius(host, port, password)
            r = radius.Radius(self.password, self.host, self.port)
            r.authenticate('dummyloginuser','dummypassword')
        except radius.Error:
            error_message = 'cannot connet to radius server'
        except:
            error_message = 'invalid value'

        if RESPONSE is not None:
            if error_message:
                self.REQUEST.form['manage_tabs_message'] = error_message
                return self.manage_editRadiusPluginForm(RESPONSE)
            else:
                message = 'host+updated'
                RESPONSE.redirect( '%s/manage_editRadiusPluginForm'
                                   '?manage_tabs_message=%s'
                                 % ( self.absolute_url(), message )
                                 )


classImplements(RadiusPlugin,
                IRadiusPlugin,
                plugins.IAuthenticationPlugin,
                *implementedBy(BasePlugin))

InitializeClass(RadiusPlugin)
