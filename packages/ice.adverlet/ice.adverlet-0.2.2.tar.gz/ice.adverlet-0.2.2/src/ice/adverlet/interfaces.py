### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################

__license__ = "GPL v.3"
__docformat__ = 'restructuredtext'

from zope.interface import Interface, Attribute
from zope.tales.interfaces import ITALESExpression
from zope.schema import Text, TextLine, List, Choice, Bool
from zope.location.interfaces import ILocation
from zope.app.file.interfaces import IImage
from i18n import _

class IAdverlet(ILocation):
    """ Adverlet """

    description = Text(title=_(u'Description'), required=False)

    default = TextLine(title=_(u'Default view name'), required=False)

    source = Text(title=_(u'HTML Source'), required=False)

    wysiwyg = Bool(title=_(u'Rich-text editor'), default=True)

    newlines = Bool(title=_(u'Render newlines'), default=False)

class ISourceStorage(Interface):
    """ Storage for HTML sources """

    sources = Attribute('HTML sources')

    mceplugins = List(
        title=_(u'TinyMCE Plugins'),
        default=[],
        value_type=Choice(vocabulary='ice.adverlet.mceplugins'))
    
    defaultCSS = Bool(
        title=_(u'Include default css-styles for management UI'),
        default=True)

class IFileStorage(Interface):
    """ Files storage """

class IImageWrapper(IImage):
    """ Image wrapper """

    description = TextLine(title=_(u'Description'))

class ISourceModifiedEvent(Interface):
    """ Event """

class ITALESAdverletExpression(ITALESExpression):
    """ Returns a HTML content of the adverlet.
    To call a adverlet in a view use the follow syntax
    in a page template::

      <tal:block content="structure adverlet:adverlet_name" />

    Thus, adverlet is looked up only by the name.
    """
