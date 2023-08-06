##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: $
"""

from zope import interface
from zope.component.interfaces import IObjectEvent

class IApplication( interface.Interface ):
    """
    Application Root to publish
    """

class IWSGIApplicationCreatedEvent( IObjectEvent ):
    
    app = interface.Attribute(u"Published Application")

class WSGIApplicationCreatedEvent( object ):
    
    interface.implements( IWSGIApplicationCreatedEvent )
    
    def __init__( self, object ):
        self.object = object