### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""CaptchaWidget class for the Zope 3 based ks.widget package

$Id: captchawidget.py 35330 2008-01-13 09:03:40Z cray $
"""

__author__  = "Anatoly Bubenkov"
__license__ = "ZPL"
__version__ = "$Revision: 35330 $"
__date__ = "$Date: 2008-01-13 12:03:40 +0300 (Вск, 13 Янв 2008) $"

import datetime

from zope.app.form.interfaces import ConversionError, InputErrors
from zope.app.form.browser.widget import renderElement
from zope.app.form.browser import IntWidget
from ks.lib.pagetemplate.viewpagetemplatestring import ViewPageTemplateString

from ks.schema.captcha import _

class CaptchaWidget(IntWidget):

    imageCssClass = u'captcha'

    noImageTemplate = u''

    @property
    def keyName(self):
        return '%s.key' % self.name

    def __call__(self):
        res = []
        key = self.context.captcha.getkey()
        kwargs = {'type': 'hidden',
                  'name': self.keyName,
                  'id': self.keyName,
                  'value': key}
        res.append(renderElement('input', **kwargs))
        kwargs = {'src': '@@captcha?key=%s' % key,
                  'alt': _('Turn on images'),
                  'cssClass': self.imageCssClass
                  }
        res.append(renderElement('img', **kwargs))
        res.append(super(CaptchaWidget, self).__call__())
        pt = ViewPageTemplateString(source=self.noImageTemplate)
        res.append(pt(self, self.context.context, self.request))
        return '\n'.join(res)

    def _toFieldValue(self, input):
        if self.convert_missing_value and input == self._missing:
            value = self.context.missing_value
        else:
            try:
                value = map(unicode, input)
            except ValueError, v:
                raise ConversionError(_('Incorrect text data'), v)
            if not value[0].isdigit():
                raise ConversionError(_(u'Random key must consist of digits!'))
            if not value[1] and not self.context.required:
                value[1] = None
                return value
            if not value[1].isdigit():
                raise ConversionError(_(u'Code must consist of digits!'))
            try:
                value = map(int, input)
            except ValueError, v:
                raise ConversionError(_(u'Data conversion error'), v)

        return value

    def _getFormInput(self):
        return (self.request.get(self.keyName), self.request.get(self.name))

    def _toFormValue(self, value):
        return self._missing
