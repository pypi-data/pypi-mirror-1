### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################

__license__ = "GPL v.3"

from BTrees.OOBTree import OOBTree
from persistent import Persistent
from zope.interface import implements
from zope.app.container.contained import Contained
from zope.app.container.btree import BTreeContainer
from zope.schema.fieldproperty import FieldProperty
from interfaces import ISourceStorage, IFileStorage

class SourceStorage(Persistent, Contained):
    implements(ISourceStorage)

    mceplugins = FieldProperty(ISourceStorage['mceplugins'])

    def __init__(self):
        self.sources = OOBTree()

class FileStorage(BTreeContainer):
    implements(IFileStorage)
