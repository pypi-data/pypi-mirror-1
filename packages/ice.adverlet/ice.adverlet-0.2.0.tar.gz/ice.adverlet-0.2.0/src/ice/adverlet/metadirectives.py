### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################

__license__ = "GPL v.3"
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.schema import TextLine, Text, Bool

class IAdverletDirective(Interface):
    """ Defines adverlet """

    name = TextLine(
        title = u'Name',
        description = u'Adverlets is looked up by the name',
        required = True)

    description = Text(
        title = u'Description',
        description = u'Useful description for content manager',
        required = False)

    default = TextLine(
        title = u'Default view name',
        description = u'Default view name',
        required = False)

    wysiwyg = Bool(
        title = u'Rich-text editor by default',
        description = u'Rich-text editor not always useful',
        required = False,
        default = True)
