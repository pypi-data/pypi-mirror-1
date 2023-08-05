### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""HMTMLDisplayWidget class for the Zope 3 based ks.widget package

$Id: smarturiwidget.py 35330 2008-01-13 09:03:40Z cray $
"""

__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35330 $"
__date__ = "$Date: 2008-01-13 12:03:40 +0300 (Вск, 13 Янв 2008) $"
__credits__ = "Based heavily on zope.app.form.browser.objectwidget.ObjectWidget"

from ks.schema.smarturi.smarturi import URI

from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import ObjectWidget, DisplayWidget
from zope.app.form.browser.widget import renderElement
from zope.interface import implements
from interfaces import ISmartURIDisplayWidget

from interfaces import _

SmartURIWidget = CustomWidgetFactory(ObjectWidget, URI)

class SmartURIDisplayWidget(DisplayWidget):

    implements(ISmartURIDisplayWidget)

    tag = 'a'

    cssClass = u''

    extra = u''

    _missing = u''

    def __call__(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        if value == self.context.missing_value:
            value = self._missing
        return renderElement(self.tag,
                             id=self.name,
                             contents=value.title,
                             href=value.uri,
                             cssClass=self.cssClass,
                             extra=self.extra)
