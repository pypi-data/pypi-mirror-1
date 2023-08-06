### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################

__license__ = "GPL v.3"

from zope.interface import implements
from zope.cachedescriptors.property import Lazy
from zope.app.undo.interfaces import IUndoManager
from zope.component import getUtility, getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
from zope.app.security.interfaces import IAuthentication
from zope.app.pagetemplate import ViewPageTemplateFile
from ice.adverlet.interfaces import ISourceStorage
from interfaces import IUndoTemplate
from ice.adverlet.i18n import _

class Undo(object):
    implements(IContentProvider)
    
    def __init__(self, context, request, view):
        self.__parent__ = view
        self.request = request
        self.context = context

        # customizable template
        self.template = getMultiAdapter(
            (self, self.request), IUndoTemplate,
            name='ice.adverlet.UndoTemplate')

    @Lazy
    def _manager(self):
        return getUtility(IUndoManager)

    def update(self):
        request = self.request
        self.transactions = self._manager.getPrincipalTransactions(
            request.principal, self.context, 0, -10)

        id = request.get('id')
        if id:
            self._manager.undoPrincipalTransactions(
                request.principal, ids=[id,])

            request.response.redirect(str(request.URL) + '?undo=yes')

    def render(self):
        return self.template(self)
