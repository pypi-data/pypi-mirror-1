### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################

__license__ = "GPL v.3"

import os
from zope.component import provideUtility
from interfaces import IAdverlet
from adverlet import Adverlet

def registerAdverlet(_context, name, description=None, default=None):
    adverlet = Adverlet()
    adverlet.__name__ = name
    adverlet.description = description
    adverlet.default = default
    provideUtility(adverlet, IAdverlet, name=name)
