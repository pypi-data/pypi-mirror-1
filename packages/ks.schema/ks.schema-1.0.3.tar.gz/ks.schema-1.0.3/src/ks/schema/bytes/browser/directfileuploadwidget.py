### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################

from zope.app.form.browser import FileWidget
from xml.sax.saxutils import quoteattr, escape

import zope.i18nmessageid
_ = zope.i18nmessageid.MessageFactory('zope')

class DirectFileUploadWidget(FileWidget):
    """File Widget"""

    def _toFieldValue(self, input):
        if input is None or input == '':
            return self.context.missing_value
        try:
            seek = input.seek
            read = input.read
        except AttributeError, e:
            raise ConversionError(_('Form input is not a file object'), e)
        else:
            if read or getattr(input, 'filename', ''):
                return input
            else:
                return self.context.missing_value

    def _toFormValue(self, value):
        return 'File'

    def hasInput(self):
        return ((self.name+".used" in self.request.form)
                or
                (self.name in self.request.form)
                )
