### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""ImageDisplayWidget class for the Zope 3 based ks.widget package

$Id: imagedisplaywidget.py 35321 2008-01-07 22:03:46Z cray $
"""

__author__  = "Anatoly Zaretsky"
__license__ = "ZPL"
__version__ = "$Revision: 35321 $"
__date__ = "$Date: 2008-01-08 00:03:46 +0200 (Tue, 08 Jan 2008) $"

from zope.interface import implements
from zope.traversing.browser import absoluteURL

from zope.app.form.interfaces import IDisplayWidget
from zope.app.form.browser.widget import DisplayWidget, renderElement


# from ks.widget import _ не используется

class ImageDisplayWidget(DisplayWidget):

    implements (IDisplayWidget)

    cssClass = u''
    extra = u''

    def __call__(self):
        src = '%s/++attribute++%s/++attribute++__call__' % (absoluteURL(self.context.context, self.request), self.context.__name__)
        return renderElement('img', src=src, cssClass=self.cssClass, extra=self.extra)
