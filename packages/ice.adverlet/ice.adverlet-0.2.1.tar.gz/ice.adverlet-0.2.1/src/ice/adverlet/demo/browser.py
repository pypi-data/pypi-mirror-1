### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################
""" Demo site, simple browser classes
"""

__license__ = "GPL v.3"

from zope.app.pagetemplate import ViewPageTemplateFile

class Frontpage(object):

    __call__ = ViewPageTemplateFile('layout.pt')
    render = ViewPageTemplateFile('frontpage.pt')

class Manage(object):

    __call__ = ViewPageTemplateFile('layout.pt')
    render = ViewPageTemplateFile('manage.pt')

class HeaderView(object):

    def __call__(self):
        return u'DEFAULT HEADER'

class MainView(object):

    def __call__(self):
        return u'DEFAULT MAIN'

class SidebarView(object):
    
    def __call__(self):
        return u'DEFAULT SIDEBAR'
