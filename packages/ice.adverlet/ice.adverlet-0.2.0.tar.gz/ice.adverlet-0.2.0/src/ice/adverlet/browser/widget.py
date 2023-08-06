### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################

__license__ = "GPL v.3"

from z3c.widget.tiny.widget import TinyWidget
from zope.component import getUtility
from ice.adverlet.interfaces import ISourceStorage

class RichTextWidget(TinyWidget):

    height = 25
    mce_theme = "advanced"
    mce_theme_advanced_toolbar_location = "top"
    mce_theme_advanced_toolbar_align="left"
    mce_theme_advanced_statusbar_location = "bottom"
    width = "100%"
    mce_entity_encoding = "raw"
    mce_convert_newlines_to_brs = "false"
    mce_relative_urls = "false"
    mce_theme_advanced_buttons1 = "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,bullist,numlist,|,outdent,indent,|,formatselect,fontselect,fontsizeselect"
    mce_theme_advanced_buttons2 = "cut,copy,paste,pastetext,pasteword,|,undo,redo,|,link,unlink,anchor,image,cleanup,code,|,insertdate,inserttime,|,forecolor,backcolor"
    mce_theme_advanced_buttons3 = "tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,iespell,media,advhr,|,ltr,rtl,|,preview,fullscreen"
    mce_extended_valid_elements = "a[name|href|target|title|onclick],img[class|src|border=0|alt|title|hspace|vspace|width|height|align|onmouseover|onmouseout|name],hr[class|width|size|noshade],font[face|size|color|style],span[class|align|style]"

    @property
    def mce_plugins(self):
        tool = getUtility(ISourceStorage)
        return ','.join(tool.mceplugins)
