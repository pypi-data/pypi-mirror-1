### -*- coding: utf-8 -*- ####################################################
#
# Author: Ilshad Habibullin, 2008 <astoon.net at gmail.com>
#
##############################################################################

__license__ = "GPL v.3"

from zope.formlib import form
from zope.event import notify
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.app.file.interfaces import IImage
from zope.cachedescriptors.property import Lazy
from zope.lifecycleevent import ObjectModifiedEvent
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.dublincore.interfaces import IZopeDublinCore
from zope.contentprovider.interfaces import IContentProvider
from zope.component import getUtilitiesFor, queryUtility, getUtility
from ice.adverlet.interfaces import IFileStorage, IImageWrapper
from ice.adverlet.interfaces import IAdverlet, ISourceStorage
from ice.adverlet.image import ImageWrapper
from interfaces import IManageUITemplate
from widget import RichTextWidget
from ice.adverlet.i18n import _

class ManageForm(form.FormBase):
    implements(IContentProvider)

    primary_actions = form.Actions()
    secondary_actions = form.Actions()
    preview = None
    info = None
    no_changes = False
    
    def __init__(self, context, request, view):
        self.__parent__ = view
        self.request = request
        self.context = self.getContext()
        self.default_css = self._sources.defaultCSS

        # customizable template
        self.template = getMultiAdapter((self, self.request),
                                        IManageUITemplate,
                                        name='ice.adverlet.ManageTemplate')

        # edit adverlet
        if IAdverlet(self.context, None):
            self.title = _(u'Edit HTML')
            self.form_fields = form.Fields(IAdverlet)
            if IAdverlet(self.context).wysiwyg:
                self.form_fields['source'].custom_widget = RichTextWidget 
                self.form_fields = self.form_fields.omit('newlines')
                IAdverlet(self.context).newlines = False
            self.form_fields = self.form_fields.omit(
                '__name__', 'description', 'default')

        # edit settings
        elif ISourceStorage(self.context, None):
            self.title = _(u'Edit settings')
            self.form_fields = form.Fields(ISourceStorage)
            self.form_fields = self.form_fields.omit('defaultCSS')

        # upload file
        elif IImageWrapper(self.context, None):
            self.title = _(u'Upload File')
            self.form_fields = form.Fields(IImageWrapper)

        # for all forms
        if self.context:
            super(ManageForm, self).__init__(self.context, request)

    @Lazy
    def _sources(self):
        return getUtility(ISourceStorage)

    @Lazy
    def _files(self):
        return getUtility(IFileStorage)

    def getContext(self):
        request = self.request

        custom = request.get('custom')
        settings = request.get('settings')
        upload = request.get('images')

        # select type of form
        if custom:
            return queryUtility(IAdverlet, custom)
        elif settings:
            return self._sources
        elif upload:
            return ImageWrapper()
        else:
            return None

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}     
        # context may be empty
        if self.context:
            self.widgets = form.setUpEditWidgets(
                self.form_fields, self.prefix, self.context, self.request,
                adapters=self.adapters, ignore_request=ignore_request
                )
        else:
            self.widgets = ()

    def update(self):
        request = self.request

        # for table with listing of all registered adverlets
        self.adverlets = [i[1] for i in getUtilitiesFor(IAdverlet)]

        # preview mode
        preview_name = request.get('preview')
        if preview_name:
            adv = queryUtility(IAdverlet, preview_name)
            self.adverlet_name = adv.__name__
            self.preview = adv and adv.source

        # delete image
        file_key = request.get('delete')
        if file_key:
            del self._files[file_key]
            self.redirect('?images=yes')

        # update form
        self.setUpWidgets()
        self.form_reset = False
        data = {}

        # for `cancel` action
        if form.handleSubmit(self.secondary_actions, data)[1]:
            self.redirect()

        # for `apply` action
        errors, action = form.handleSubmit(
            self.primary_actions, data, self.validate)

        # form result
        if errors:
            self.status = u'There were errors'
            result = action.failure(data, errors)
        elif errors is not None:
            self.form_reset = True
            result = action.success(data)
        else:
            result = None

        self.form_result = result
        
        # redirect
        if action and not errors and not self.no_changes:
            custom = request.get('custom')
            
            self.redirect(
                (request.get('images') and '?images=yes') or
                (request.get('settings') and '?settings=yes') or
                (custom and '?custom=%s' % custom) or ''
                )

    @Lazy
    def actions(self):
        return list(self.primary_actions) + list(
            self.secondary_actions)

    @form.action(_(u'Apply'), primary_actions)
    def handle_apply_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields,
                             data, self.adapters):
            notify(ObjectModifiedEvent(self.context))
            self.status = _(u'Updated')
        else:
            self.status = _(u'No changes')
            self.no_changes = True

    @form.action(_(u'Close'), secondary_actions)
    def handle_close_action(self, *argv):
        pass

    def redirect(self, query=''):
        self.request.response.redirect(
            str(self.request.URL) + query)

    @property
    def info(self):
        """ Some information """
        sources_size = sum(
            [len(source) for source in self._sources.sources.values()
             if source]
            )

        images_size = sum(
            [f.getSize() for f in self._files.values()
             if IImage(f, None)]
            )

        return {'sources_size':sources_size,
                'images_size':images_size}
 
    def getFiles(self):
        """ Listing of images """
        for id, ob in self._files.items():
            if IImage(ob, None):
                yield {'id':id, 'ob':ob, 'dc':IZopeDublinCore(ob)}

    def render(self):
        if self.form_result is None:
            if self.form_reset:
                self.resetForm()
                self.form_reset = False
            self.form_result = self.template(self)

        return self.form_result
