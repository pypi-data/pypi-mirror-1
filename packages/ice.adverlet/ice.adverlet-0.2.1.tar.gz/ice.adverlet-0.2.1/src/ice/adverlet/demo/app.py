### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################
""" Demo site
"""

__license__ = "GPL v.3"

from zope import event
from zope.app.folder import Folder
from zope.interface import Interface, implements
from zope.app.component.site import LocalSiteManager        
from ice.adverlet.interfaces import ISourceStorage, IFileStorage
from ice.adverlet.storage import SourceStorage, FileStorage

class ISite(Interface):
    """ Demo site """

class Site(Folder):
    implements(ISite)

    def __init__(self):
        super(Site, self).__init__()
        sm = LocalSiteManager(self)
        self.setSiteManager(sm)        
        sm = self.getSiteManager()
        event.notify(SiteCreatedEvent(self))

class ISiteCreatedEvent(Interface):
    """ event """

class SiteCreatedEvent:
    implements(ISiteCreatedEvent)
    
    def __init__(self, site):
        self.site = site                

def installs(e):
    site = e.site
    sm = site.getSiteManager()

    storage = SourceStorage()
    sm['adverlets_sources'] = storage
    sm.registerUtility(storage, ISourceStorage)
    
    storage = FileStorage()
    site['images'] = storage
    sm.registerUtility(storage, IFileStorage)
    
