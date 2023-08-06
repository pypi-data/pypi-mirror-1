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

import os
import sys
import code
import zope.app.wsgi
import zope.app.debug

import wsgi

def application_factory(global_conf, zcml='site.zcml', devmode='off'):
    zcml_conf = os.path.join(global_conf['here'], zcml)
    devmode = ( devmode.lower() in ('true', 'True', 'on') and True) or False
    return wsgi.getWSGIApplication(zcml_conf, devmode)

