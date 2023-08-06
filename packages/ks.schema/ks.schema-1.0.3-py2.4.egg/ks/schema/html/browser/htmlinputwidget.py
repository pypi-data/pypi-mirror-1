### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""HTMLInputWidget class for the Zope 3 based ks.widget package

$Id: htmlinputwidget.py 35335 2008-05-27 16:02:13Z anatoly $
"""

__author__  = "Anatoly Zaretsky"
__license__ = "ZPL"
__version__ = "$Revision: 35335 $"
__date__ = "$Date: 2008-05-27 19:02:13 +0300 (Tue, 27 May 2008) $"

import demjson

from zope.component import queryMultiAdapter
from zope.app.container.interfaces import IAdding

import z3c.widget.tiny.widget

from interfaces import IHTMLImageListProvider

from ks.schema.html import _

class HTMLInputWidget(z3c.widget.tiny.widget.TinyWidget):

    height = 30
    mce_theme = "advanced"
    mce_theme_advanced_toolbar_location = "top"
    mce_theme_advanced_toolbar_align = "left"
    mce_theme_advanced_statusbar_location = "bottom"
    mce_entity_encoding = "raw"
    mce_convert_newlines_to_brs = "true"
    mce_external_image_list_url = "htmlimagelist.js"
    mce_relative_urls = "false"
    mce_plugins = "style,layer,table,save,advhr,advimage,advlink,emotions,iespell,insertdatetime,preview,zoom,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras"
    mce_theme_advanced_buttons1 = "save,newdocument,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,styleselect,formatselect,fontselect,fontsizeselect"
    mce_theme_advanced_buttons2 = "cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,|,undo,redo,|,link,unlink,anchor,image,cleanup,code,|,insertdate,inserttime,preview,|,forecolor,backcolor"
    mce_theme_advanced_buttons3 = "tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,media,advhr,|,print,|,ltr,rtl,|,fullscreen"
    mce_theme_advanced_buttons4 = "insertlayer,moveforward,movebackward,absolute,|,styleprops,|,cite,abbr,acronym,del,ins,attribs,|,visualchars,nonbreaking"
    mce_extended_valid_elements = "a[name|href|target|title|onclick],img[class|src|border=0|alt|title|hspace|vspace|width|height|align|onmouseover|onmouseout|name],hr[class|width|size|noshade],font[face|size|color|style],span[class|align|style]"


class HTMLImageListJS(object):

    def __call__(self, *kv, **kw):
        context = self.context
        if IAdding.providedBy(context):
            context = context.context
        images = getattr(
            queryMultiAdapter(
                (context, self.request),
                interface=IHTMLImageListProvider,
                context=context),
            'images',
            None)
        self.request.response.setHeader('Content-Type', 'text/javascript; charset=utf-8')
        if images:
            return u'var tinyMCEImageList = %s;\n' % demjson.encode(images)
        return u''
