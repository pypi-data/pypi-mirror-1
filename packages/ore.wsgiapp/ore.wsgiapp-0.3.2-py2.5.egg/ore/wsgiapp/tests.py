##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import re, unittest, os

from zope.testing import doctest, renormalizing
from zope.app.testing import placelesssetup, ztapi

from ore.wsgiapp.app import Application

test_zcml_contents = open( os.path.join( os.path.dirname(__file__), 'test.zcml'  ) )

class TestApplication( Application ):
    """ a really simple containerish application """
    
class AppView( object ):
    """ a simple view we register for the application """
    def __init__( self,context, request):
        self.context = context 
        self.request = request
        
    def __call__( self ):
        return "Hello World"
    
def test_suite():
    
    ns = dict(
        component = ztapi,
        test_zcml_contents = test_zcml_contents 
        )
        
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'readme.txt',
            checker = renormalizing.RENormalizing([
                (re.compile('at 0x[0-9a-f]+'), 'at <SOME ADDRESS>'),
                ]),
            ),
        ))    
