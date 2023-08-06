### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################

__license__ = "GPL v.3"

from zope.component import getUtilitiesFor
from zope.schema.vocabulary import SimpleVocabulary

def tinyMcePluginsVocabulary(context):
    plugins = [
        'style', 'layer', 'table', 'save', 'advhr', 'advimage',
        'advlink', 'emotions' , 'iespell', 'insertdatetime',
        'preview', 'zoom', 'media', 'searchreplace', 'print',
        'contextmenu', 'paste', 'directionality', 'fullscreen',
        'noneditable', 'visualchars', 'nonbreaking', 'xhtmlxtras'
        ]

    return SimpleVocabulary.fromValues(plugins)
