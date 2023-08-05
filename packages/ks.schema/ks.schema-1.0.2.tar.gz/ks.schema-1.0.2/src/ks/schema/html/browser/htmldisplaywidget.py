### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""HTMLDisplayWidget class for the Zope 3 based ks.widget package

$Id: htmldisplaywidget.py 35330 2008-01-13 09:03:40Z cray $
"""

__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35330 $"
__date__ = "$Date: 2008-01-13 12:03:40 +0300 (Вск, 13 Янв 2008) $"
__credits__ = "Based heavily on zope.app.form.browser.objectwidget.ObjectWidget"

from zope.app.form.interfaces import IDisplayWidget
from zope.app.form.browser.widget import DisplayWidget, UnicodeDisplayWidget
from zope.interface import implements

from ks.schema.html import _

class UnicodeHTMLDisplayWidget(UnicodeDisplayWidget):

    implements (IDisplayWidget)

    def __call__(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        if value == self.context.missing_value:
            return u""
        return unicode(value)

class HTMLDisplayWidget(DisplayWidget):

    implements (IDisplayWidget)

    def __call__(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        if value == self.context.missing_value:
            return ""
        return value
