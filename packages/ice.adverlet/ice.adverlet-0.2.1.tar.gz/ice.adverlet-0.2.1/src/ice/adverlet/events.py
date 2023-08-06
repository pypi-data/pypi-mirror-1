### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################

__license__ = "GPL v.3"

from zope import event
from zope.interface import implements
from interfaces import ISourceModifiedEvent

class SourceModifiedEvent:
    implements(ISourceModifiedEvent)
    
    def __init__(self, name):
        self.name = name
