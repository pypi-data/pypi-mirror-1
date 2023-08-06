# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: interfaces.py 32250 2008-11-20 14:58:02Z sylvain $

from zope.interface import Interface

class IRaduisAware(Interface):
    """Marker interface to known that the service_members is Raduis
    Aware.
    """
