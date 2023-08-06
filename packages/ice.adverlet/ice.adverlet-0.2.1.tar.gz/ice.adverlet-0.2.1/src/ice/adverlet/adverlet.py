### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################

__license__ = "GPL v.3"

from zope.event import notify
from zope.interface import implements
from zope.component import queryUtility
from rwproperty import setproperty, getproperty
from zope.schema.fieldproperty import FieldProperty
from interfaces import IAdverlet, ISourceStorage
from events import SourceModifiedEvent

class Adverlet(object):
    """ See ice.adverlet.interfaces.IAdverlet """
    implements(IAdverlet)

    __name__ = __parent__ = None

    description = FieldProperty(IAdverlet['description'])
    default = FieldProperty(IAdverlet['default'])
    wysiwyg = FieldProperty(IAdverlet['wysiwyg'])
    newlines = FieldProperty(IAdverlet['newlines'])

    @setproperty
    def source(self, html):
        storage = queryUtility(ISourceStorage)

        if storage:
            storage.sources[self.__name__] = html
            notify(SourceModifiedEvent(self.__name__))

    @getproperty
    def source(self): 
        storage = queryUtility(ISourceStorage)

        if storage and self.__name__ in storage.sources:
            return storage.sources[self.__name__]

        return None
