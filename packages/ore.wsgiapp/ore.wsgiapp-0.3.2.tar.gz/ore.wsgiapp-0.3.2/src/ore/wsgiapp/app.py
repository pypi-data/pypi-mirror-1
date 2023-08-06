
from zope import interface
from zope.app.component import site
from zope.app.container.sample import SampleContainer
from zope.traversing.interfaces import IContainmentRoot

import interfaces

class BaseApplication( site.SiteManagerContainer ):

    interface.implements( interfaces.IApplication, IContainmentRoot )
    
class Application( SampleContainer, BaseApplication ):
    pass
