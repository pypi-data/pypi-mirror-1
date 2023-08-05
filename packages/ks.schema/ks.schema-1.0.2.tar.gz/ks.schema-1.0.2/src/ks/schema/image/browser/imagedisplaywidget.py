### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""ImageDisplayWidget class for the Zope 3 based ks.widget package

$Id: imagedisplaywidget.py 35330 2008-01-13 09:03:40Z cray $
"""

__author__  = "Anatoly Zaretsky"
__license__ = "ZPL"
__version__ = "$Revision: 35330 $"
__date__ = "$Date: 2008-01-13 12:03:40 +0300 (Вск, 13 Янв 2008) $"

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
