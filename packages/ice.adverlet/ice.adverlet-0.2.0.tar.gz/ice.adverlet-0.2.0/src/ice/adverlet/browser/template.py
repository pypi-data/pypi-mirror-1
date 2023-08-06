### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################

__license__ = "GPL v.3"

from zope.component import adapter
from zope.interface import implementer
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.contentprovider.interfaces import IContentProvider
from interfaces import IManageUITemplate, IUndoTemplate

@implementer(IManageUITemplate)
@adapter(IContentProvider, IDefaultBrowserLayer)
def manageUITemplate(*argv):
    return ViewPageTemplateFile('manage.pt')

@implementer(IUndoTemplate)
@adapter(IContentProvider, IDefaultBrowserLayer)
def undoTemplate(*argv):
    return ViewPageTemplateFile('undo.pt')
