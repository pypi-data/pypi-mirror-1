### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################

__license__ = "GPL v.3"

from zope.interface import implements
from zope.app.component.hooks import setSite
from zope.component import queryUtility, provideUtility
from z3c.sampledata.interfaces import ISampleDataPlugin
from ice.adverlet.interfaces import ISourceStorage, IFileStorage
from ice.adverlet.storage import SourceStorage, FileStorage

class SampleSourceStorage(object):
    implements(ISampleDataPlugin)
    name = 'ice.adverlet.sample.sourcestorage'
    dependencies = []
    schema = None

    def generate(self, context, param={}, dataSource=None, seed=None):
        setSite(context)
        storage = queryUtility(ISourceStorage)
        if storage is None:
            storage = SourceStorage()
            sm = context.getSiteManager()
            sm['source_storage'] = storage
            provideUtility(storage, ISourceStorage)
        return storage

class SampleFileStorage(object):
    implements(ISampleDataPlugin)
    name = 'ice.adverlet.sample.filestorage'
    dependencies = []
    schema = None

    def generate(self, context, param={}, dataSource=None, seed=None):
        setSite(context)
        storage = queryUtility(IFileStorage)
        if storage is None:
            storage = FileStorage()
            sm = context.getSiteManager()
            sm['file_storage'] = storage
            provideUtility(storage, IFileStorage)
        return storage
