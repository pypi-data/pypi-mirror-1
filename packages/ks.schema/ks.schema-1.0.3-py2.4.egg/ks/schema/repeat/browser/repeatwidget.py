### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""The widget for repeated fields.

$Id: repeatwidget.py 23861 2007-11-25 00:13:00Z xen $
"""
__author__  = "Arvid"
__license__ = "ZPL"
__version__ = "$Revision: 23861 $"
__date__ = "$Date: 2007-11-25 02:13:00 +0200 (Sun, 25 Nov 2007) $"

from zope.interface import implements
from zope.schema.interfaces import ValidationError
from zope.app.form.interfaces import WidgetInputError
from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.form.browser.textwidgets import TextWidget, PasswordWidget
from zope.schema.fieldproperty import FieldProperty

from interfaces import IRepeatWidget

from ks.schema.repeat import _

class NotRepeated(ValidationError):
    __doc__ = _(u"""Incorrect Repeat""")

class RepeatWidget(SimpleInputWidget):
    """base widget to repeat another fields"""
    implements(IRepeatWidget)

    checkfield = FieldProperty(IRepeatWidget['checkfield'])

    def getInputValue(self):
        value = super(RepeatWidget, self).getInputValue()

        try:
            if self.request.get(self.checkfield) != value:
                raise NotRepeated
        except NotRepeated, v:
            self._error = WidgetInputError(self.context.__name__, self.label, v)
            raise self._error

        return value

class PasswordRepeatWidget(PasswordWidget, RepeatWidget):
    """password repeat widget"""
    pass
