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

from zope.app.publication.browser import BrowserPublication
from zope.app.publication.interfaces import IRequestPublicationFactory, IBrowserRequestFactory

from zope.publisher.browser import BrowserRequest
from zope import component, interface

import interfaces

class Publication( BrowserPublication ):

    def getApplication( self, request ):
        app = component.getUtility( interfaces.IApplication )
        return app

class BrowserFactory( object ):

    interface.implements( IRequestPublicationFactory )

    def canHandle( self, environment ):
        return True

    def __call__(self):
        request_class = component.queryUtility(
            IBrowserRequestFactory, default=BrowserRequest)
        return request_class, Publication
    
