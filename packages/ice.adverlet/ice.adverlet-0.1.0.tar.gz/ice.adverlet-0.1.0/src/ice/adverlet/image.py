### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################

__license__ = "GPL v.3"

from zope.event import notify
from zope.interface import implements
from zope.component import getUtility
from rwproperty import setproperty, getproperty
from zope.cachedescriptors.property import Lazy
from zope.lifecycleevent import ObjectCreatedEvent
from zope.app.file.image import Image, getImageInfo
from zope.dublincore.interfaces import IZopeDublinCore
from zope.app.container.interfaces import INameChooser
from interfaces import IFileStorage, IImageWrapper
from i18n import _

class ImageWrapper(object):
    implements(IImageWrapper)

    def __init__(self):
        self.contentType = None

    @Lazy
    def _storage(self):
        return getUtility(IFileStorage)

    @setproperty
    def data(self, data):
        image = Image(data)  
        notify(ObjectCreatedEvent(image))
        id = INameChooser(self._storage).chooseName(None, image)
        self.image = self._storage[id] = image
        self.contentType = getImageInfo(data)[0]
    
    @setproperty
    def description(self, text):
        IZopeDublinCore(self.image).title = text

    @getproperty
    def data(self):
        return None

    @getproperty
    def description(self):
        return None

    def getSize(self):
        return self.image.getSize()
    
    def getImageSize(self):
        return self.image.getImageSize()
